import os
import re
import shutil
import logging
import urllib.parse
from typing import Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from downloader import downloader_instance, BASE_DIR, DOWNLOADS_DIR, detect_platform

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("api")

app = FastAPI(
    title="Universal Social Media Media Downloader",
    description="Download high-quality audio and video from YouTube, Instagram, Facebook, TikTok, Twitter/X, SoundCloud and 1000+ sites.",
    version="1.0.0"
)

# Enable full CORS for cross-origin and Cloudflare Tunnel support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Length", "Content-Type"],
)

# Request Models
class InfoRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    media_type: str = "audio"
    quality: str = "mp3-320"
    format_ext: str = "mp3"
    title: Optional[str] = None
    thumbnail: Optional[str] = None

class BatchInfoRequest(BaseModel):
    urls: List[str]


# API Endpoints
@app.get("/api/health")
def health_check():
    """Check backend status and health."""
    return {
        "status": "online",
        "service": "Universal Media Downloader",
        "downloads_dir": DOWNLOADS_DIR,
    }


@app.post("/api/info")
def extract_media_info(payload: InfoRequest):
    """Fetch video/audio metadata without downloading."""
    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="Please provide a valid URL.")
    
    logger.info(f"Extracting info for URL: {url}")
    result = downloader_instance.extract_info(url)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400, 
            detail=result.get("error", "Could not extract media info. Please check the URL.")
        )
    
    return result


@app.post("/api/batch-info")
def extract_batch_info(payload: BatchInfoRequest):
    """Extract metadata for multiple URLs."""
    results = []
    for url in payload.urls[:20]:
        url_clean = url.strip()
        if not url_clean:
            continue
        info = downloader_instance.extract_info(url_clean)
        results.append(info)
    return {"items": results}


@app.post("/api/download")
def start_download(payload: DownloadRequest):
    """Initiate a download/conversion task."""
    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required.")

    task_id = downloader_instance.start_download(
        url=url,
        media_type=payload.media_type,
        quality=payload.quality,
        format_ext=payload.format_ext,
        title=payload.title,
        thumbnail=payload.thumbnail,
    )

    return {
        "task_id": task_id,
        "status": "queued",
        "message": "Download task started."
    }


@app.get("/api/progress/{task_id}")
def get_progress(task_id: str):
    """Get live download progress."""
    task = downloader_instance.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    return {
        "task_id": task["task_id"],
        "status": task["status"],
        "progress": task["progress"],
        "speed": task["speed"],
        "eta": task["eta"],
        "downloaded_str": task["downloaded_str"],
        "total_str": task["total_str"],
        "title": task["title"],
        "thumbnail": task.get("thumbnail"),
        "filename": task.get("filename"),
        "file_size_str": task.get("file_size_str"),
        "error": task.get("error"),
    }


@app.get("/api/file/{task_id}")
def download_file(task_id: str):
    """Download the completed media file with RFC 6266 UTF-8 header compliance."""
    task = downloader_instance.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    if task["status"] != "completed" or not task.get("file_path"):
        raise HTTPException(status_code=400, detail="File is not ready yet.")
    
    file_path = task["file_path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File no longer exists on server.")
    
    raw_filename = task.get("filename") or os.path.basename(file_path)
    
    # RFC 6266 & Cloudflare header safety:
    # 1. ASCII fallback with non-ascii and quotes stripped
    ascii_filename = re.sub(r'[^\x20-\x7E]', '_', raw_filename).replace('"', '').replace(';', '')
    # 2. URL-encoded UTF-8 filename for full international characters
    encoded_filename = urllib.parse.quote(raw_filename)
    
    # Determine MIME media type
    ext = os.path.splitext(raw_filename)[1].lower()
    media_type = "application/octet-stream"
    if ext == ".mp3":
        media_type = "audio/mpeg"
    elif ext == ".m4a":
        media_type = "audio/mp4"
    elif ext == ".wav":
        media_type = "audio/wav"
    elif ext == ".flac":
        media_type = "audio/flac"
    elif ext in [".mp4", ".m4v"]:
        media_type = "video/mp4"
    elif ext == ".webm":
        media_type = "video/webm"

    headers = {
        "Content-Disposition": f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}',
        "Cache-Control": "no-cache",
        "Accept-Ranges": "bytes",
    }

    return FileResponse(
        path=file_path,
        media_type=media_type,
        headers=headers
    )


@app.get("/api/preview/{task_id}")
def preview_stream(task_id: str):
    """Stream media file directly for in-browser playback."""
    task = downloader_instance.get_task(task_id)
    if not task or task["status"] != "completed" or not task.get("file_path"):
        raise HTTPException(status_code=404, detail="Media not ready.")

    file_path = task["file_path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    ext = os.path.splitext(file_path)[1].lower()
    media_type = "audio/mpeg" if ext == ".mp3" else ("video/mp4" if ext == ".mp4" else "application/octet-stream")

    return FileResponse(path=file_path, media_type=media_type)


@app.get("/api/history")
def get_history():
    """Get list of downloaded files in current session."""
    items = downloader_instance.list_history()
    return {
        "count": len(items),
        "history": [
            {
                "task_id": item["task_id"],
                "title": item["title"],
                "media_type": item["media_type"],
                "format_ext": item["format_ext"],
                "quality": item["quality"],
                "filename": item["filename"],
                "file_size_str": item["file_size_str"],
                "platform": item["platform"],
                "thumbnail": item.get("thumbnail"),
                "created_at": item["created_at"],
            }
            for item in items
        ]
    }


@app.delete("/api/history/{task_id}")
def delete_download(task_id: str):
    """Delete a downloaded task and clean disk space."""
    task_dir = os.path.join(DOWNLOADS_DIR, task_id)
    if os.path.exists(task_dir):
        shutil.rmtree(task_dir, ignore_errors=True)
    
    with downloader_instance.lock:
        if task_id in downloader_instance.tasks:
            del downloader_instance.tasks[task_id]
            
    return {"success": True, "message": f"Deleted task {task_id}"}


# Serve Frontend static assets
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
