import os
import re
import sys
import time
import uuid
import shutil
import logging
import threading
from typing import Dict, Any, Optional, Tuple, List
import yt_dlp

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Ensure static-ffmpeg is initialized if available
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
    logger.info("static-ffmpeg initialized successfully.")
except Exception as e:
    logger.warning(f"Could not initialize static-ffmpeg: {e}. Falling back to system ffmpeg.")

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Datacenter & Browser Headers
DEFAULT_HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Mode": "navigate",
}


def get_cookie_file() -> Optional[str]:
    """Retrieve cookies file path from disk or environment variable."""
    cookies_file = os.path.join(BASE_DIR, "cookies.txt")
    
    env_cookies = os.environ.get("YTDL_COOKIES")
    if env_cookies:
        try:
            with open(cookies_file, "w", encoding="utf-8") as f:
                f.write(env_cookies.strip())
            logger.info("Wrote cookies from YTDL_COOKIES environment variable.")
        except Exception as e:
            logger.warning(f"Could not write YTDL_COOKIES: {e}")

    if os.path.exists(cookies_file) and os.path.getsize(cookies_file) > 10:
        return cookies_file
    return None


def detect_platform(url: str) -> Dict[str, str]:
    """Detect platform name and brand styling from URL."""
    url_lower = url.lower()
    
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return {"name": "YouTube", "icon": "youtube", "color": "#FF0000", "badge": "YouTube"}
    elif "instagram.com" in url_lower:
        return {"name": "Instagram", "icon": "instagram", "color": "#E1306C", "badge": "Instagram"}
    elif "facebook.com" in url_lower or "fb.watch" in url_lower:
        return {"name": "Facebook", "icon": "facebook", "color": "#1877F2", "badge": "Facebook"}
    elif "tiktok.com" in url_lower:
        return {"name": "TikTok", "icon": "tiktok", "color": "#00F2FE", "badge": "TikTok"}
    elif "twitter.com" in url_lower or "x.com" in url_lower:
        return {"name": "Twitter / X", "icon": "twitter", "color": "#1DA1F2", "badge": "X (Twitter)"}
    elif "soundcloud.com" in url_lower:
        return {"name": "SoundCloud", "icon": "soundcloud", "color": "#FF5500", "badge": "SoundCloud"}
    elif "reddit.com" in url_lower or "redd.it" in url_lower:
        return {"name": "Reddit", "icon": "reddit", "color": "#FF4500", "badge": "Reddit"}
    elif "pinterest.com" in url_lower or "pin.it" in url_lower:
        return {"name": "Pinterest", "icon": "pinterest", "color": "#BD081C", "badge": "Pinterest"}
    elif "vimeo.com" in url_lower:
        return {"name": "Vimeo", "icon": "vimeo", "color": "#1AB7EA", "badge": "Vimeo"}
    elif "twitch.tv" in url_lower:
        return {"name": "Twitch", "icon": "twitch", "color": "#9146FF", "badge": "Twitch"}
    elif "spotify.com" in url_lower:
        return {"name": "Spotify", "icon": "spotify", "color": "#1DB954", "badge": "Spotify"}
    elif "bandcamp.com" in url_lower:
        return {"name": "Bandcamp", "icon": "bandcamp", "color": "#629AA9", "badge": "Bandcamp"}
    else:
        return {"name": "Web Media", "icon": "globe", "color": "#6366F1", "badge": "Universal"}


def format_bytes(size: Optional[int]) -> str:
    """Format bytes to human readable string."""
    if not size or size <= 0:
        return "Unknown size"
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def format_duration(seconds: Optional[float]) -> str:
    """Format duration seconds to HH:MM:SS or MM:SS."""
    if not seconds:
        return "00:00"
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def sanitize_filename(name: str) -> str:
    """Sanitize string to be safe for filenames."""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:120] if name else "media_download"


class DownloadManager:
    """Manages background downloads, speed optimizations, and cache."""

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.metadata_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
        self.cache_ttl = 600
        self.lock = threading.Lock()
        self._start_cleanup_worker()

    def _start_cleanup_worker(self):
        """Periodically cleans up old files (>2 hours) from downloads directory."""
        def cleanup_loop():
            while True:
                time.sleep(1800)
                try:
                    now = time.time()
                    with self.lock:
                        expired_keys = [
                            k for k, (ts, _) in self.metadata_cache.items()
                            if now - ts > self.cache_ttl
                        ]
                        for k in expired_keys:
                            del self.metadata_cache[k]

                    for folder in os.listdir(DOWNLOADS_DIR):
                        fpath = os.path.join(DOWNLOADS_DIR, folder)
                        if os.path.isdir(fpath):
                            mtime = os.path.getmtime(fpath)
                            if now - mtime > 7200:
                                shutil.rmtree(fpath, ignore_errors=True)
                except Exception as e:
                    logger.debug(f"Cleanup error: {e}")

        t = threading.Thread(target=cleanup_loop, daemon=True)
        t.start()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self.lock:
            return self.tasks.get(task_id)

    def list_history(self) -> list:
        with self.lock:
            completed = [
                task for task in self.tasks.values()
                if task.get("status") == "completed" and os.path.exists(task.get("file_path", ""))
            ]
            return sorted(completed, key=lambda x: x.get("created_at", 0), reverse=True)

    def extract_info(self, url: str) -> Dict[str, Any]:
        """Extract metadata from media URL with multi-strategy fallback."""
        clean_url = url.strip()

        # Check Cache
        with self.lock:
            if clean_url in self.metadata_cache:
                ts, cached_data = self.metadata_cache[clean_url]
                if time.time() - ts < self.cache_ttl:
                    logger.info(f"Serving metadata from cache for {clean_url}")
                    return cached_data

        cookie_path = get_cookie_file()

        # Multiple fallback strategies to guarantee extraction on datacenter IPs
        strategies: List[Dict[str, Any]] = [
            # Strategy 1: Standard with Node.js and cookies if available
            {
                "js_runtimes": {"node": {}},
                **({"cookiefile": cookie_path} if cookie_path else {})
            },
            # Strategy 2: Mobile client emulation (Android & iOS)
            {
                "js_runtimes": {"node": {}},
                "extractor_args": {"youtube": {"player_client": ["android", "ios"]}},
            },
            # Strategy 3: Web creator / mweb fallback
            {
                "js_runtimes": {"node": {}},
                "extractor_args": {"youtube": {"player_client": ["web_creator", "mweb"]}},
            },
            # Strategy 4: TV client fallback
            {
                "js_runtimes": {"node": {}},
                "extractor_args": {"youtube": {"player_client": ["tvhtml5", "tv"]}},
            }
        ]

        last_error = None
        info = None

        for strategy in strategies:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
                "skip_download": True,
                "socket_timeout": 15,
                "retries": 3,
                "http_headers": DEFAULT_HTTP_HEADERS,
                **strategy
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(clean_url, download=False)
                    if info:
                        break
            except Exception as e:
                last_error = e
                logger.warning(f"Extraction strategy failed ({strategy}): {e}. Retrying with next fallback...")

        if not info:
            logger.error(f"All extraction strategies failed for {clean_url}: {last_error}")
            return {
                "success": False,
                "error": str(last_error),
                "url": clean_url,
                "platform": detect_platform(clean_url)
            }

        try:
            if "entries" in info and info["entries"]:
                entries = list(info["entries"])
                if entries and entries[0]:
                    entry_info = entries[0]
                    entry_info["playlist_count"] = len(entries)
                    info = entry_info

            title = info.get("title", "Untitled Media")
            duration = info.get("duration", 0)
            thumbnail = info.get("thumbnail")
            uploader = info.get("uploader") or info.get("channel") or info.get("creator") or "Unknown Creator"
            view_count = info.get("view_count")
            platform_meta = detect_platform(clean_url)

            formats = info.get("formats", [])
            resolutions_found = set()
            video_options = []

            standard_resolutions = [
                ("4K (2160p)", 2160),
                ("1440p (2K)", 1440),
                ("1080p (Full HD)", 1080),
                ("720p (HD)", 720),
                ("480p (SD)", 480),
                ("360p", 360),
            ]

            for f in formats:
                height = f.get("height")
                if height:
                    resolutions_found.add(height)

            video_options.append({
                "id": "best",
                "label": "Best Available Quality (Max)",
                "resolution": "Best",
                "ext": "mp4",
                "recommended": True
            })

            for label, res in standard_resolutions:
                if any(h >= res for h in resolutions_found) or not resolutions_found:
                    video_options.append({
                        "id": f"res_{res}",
                        "label": label,
                        "resolution": f"{res}p",
                        "ext": "mp4",
                        "height": res,
                        "recommended": res == 1080
                    })

            audio_options = [
                {"id": "mp3-320", "label": "MP3 - 320 kbps (High Fidelity)", "bitrate": "320", "ext": "mp3", "recommended": True},
                {"id": "mp3-256", "label": "MP3 - 256 kbps (Studio Quality)", "bitrate": "256", "ext": "mp3", "recommended": False},
                {"id": "mp3-192", "label": "MP3 - 192 kbps (Standard)", "bitrate": "192", "ext": "mp3", "recommended": False},
                {"id": "mp3-128", "label": "MP3 - 128 kbps (Compact)", "bitrate": "128", "ext": "mp3", "recommended": False},
                {"id": "m4a", "label": "M4A / AAC (Lossless Stream)", "bitrate": "best", "ext": "m4a", "recommended": False},
                {"id": "wav", "label": "WAV (Uncompressed Audio)", "bitrate": "best", "ext": "wav", "recommended": False},
                {"id": "flac", "label": "FLAC (High-Res Lossless)", "bitrate": "best", "ext": "flac", "recommended": False},
            ]

            result = {
                "success": True,
                "url": clean_url,
                "title": title,
                "uploader": uploader,
                "duration": duration,
                "duration_formatted": format_duration(duration),
                "thumbnail": thumbnail,
                "view_count": f"{view_count:,}" if view_count else None,
                "platform": platform_meta,
                "video_options": video_options,
                "audio_options": audio_options,
            }

            with self.lock:
                self.metadata_cache[clean_url] = (time.time(), result)

            return result

        except Exception as e:
            logger.error(f"Formatting error for {clean_url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": clean_url,
                "platform": detect_platform(clean_url)
            }

    def start_download(
        self,
        url: str,
        media_type: str = "audio",
        quality: str = "mp3-320",
        format_ext: str = "mp3",
        title: Optional[str] = None,
        thumbnail: Optional[str] = None,
    ) -> str:
        """Start an asynchronous download task with multi-threaded optimizations."""
        task_id = str(uuid.uuid4())
        
        with self.lock:
            self.tasks[task_id] = {
                "task_id": task_id,
                "url": url,
                "media_type": media_type,
                "quality": quality,
                "format_ext": format_ext,
                "title": title or "Media Download",
                "thumbnail": thumbnail,
                "platform": detect_platform(url),
                "status": "queued",
                "progress": 0.0,
                "speed": "0 KB/s",
                "eta": "--:--",
                "downloaded_bytes": 0,
                "total_bytes": 0,
                "downloaded_str": "0 MB",
                "total_str": "--",
                "file_path": None,
                "filename": None,
                "file_size": 0,
                "file_size_str": "0 MB",
                "error": None,
                "created_at": time.time(),
            }

        thread = threading.Thread(
            target=self._download_worker,
            args=(task_id, url, media_type, quality, format_ext, title),
            daemon=True
        )
        thread.start()
        return task_id

    def _progress_hook(self, task_id: str, d: dict):
        """Callback for yt-dlp download progress."""
        status = d.get("status")
        with self.lock:
            if task_id not in self.tasks:
                return
            task = self.tasks[task_id]

            if status == "downloading":
                task["status"] = "downloading"
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes") or 0
                
                if total > 0:
                    task["progress"] = round((downloaded / total) * 100, 1)
                    task["total_bytes"] = total
                    task["total_str"] = format_bytes(total)
                else:
                    _percent_str = d.get("_percent_str", "0%").replace("%", "").strip()
                    try:
                        task["progress"] = round(float(_percent_str), 1)
                    except ValueError:
                        pass

                task["downloaded_bytes"] = downloaded
                task["downloaded_str"] = format_bytes(downloaded)

                speed = d.get("speed")
                if speed:
                    task["speed"] = f"{format_bytes(speed)}/s"
                elif "_speed_str" in d:
                    task["speed"] = d["_speed_str"].strip()

                eta = d.get("eta")
                if eta is not None:
                    task["eta"] = format_duration(eta)
                elif "_eta_str" in d:
                    task["eta"] = d["_eta_str"].strip()

            elif status == "finished":
                task["status"] = "converting"
                task["progress"] = 98.0
                task["speed"] = "Processing..."
                task["eta"] = "A few seconds..."

    def _download_worker(
        self,
        task_id: str,
        url: str,
        media_type: str,
        quality: str,
        format_ext: str,
        initial_title: Optional[str]
    ):
        """Optimized worker executing multi-threaded fragment downloads and fast transcoding."""
        task_dir = os.path.join(DOWNLOADS_DIR, task_id)
        os.makedirs(task_dir, exist_ok=True)

        outtmpl = os.path.join(task_dir, "%(title).100s [%(id)s].%(ext)s")

        cookie_path = get_cookie_file()

        # Build format and postprocessor configs
        postprocessors = []
        format_spec = "bestaudio/best"
        postprocessor_args = {"ffmpeg": ["-threads", "0"]}

        if media_type == "audio":
            audio_codec = format_ext.lower()
            if audio_codec not in ["mp3", "m4a", "wav", "flac"]:
                audio_codec = "mp3"

            bitrate = "320"
            if quality.startswith("mp3-"):
                bitrate = quality.split("-")[1]

            format_spec = "bestaudio/best"
            postprocessors = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_codec,
                    "preferredquality": bitrate if audio_codec == "mp3" else "0",
                    "nopostoverwrites": False,
                },
                {
                    "key": "FFmpegMetadata",
                    "add_metadata": True,
                }
            ]

            if audio_codec in ["mp3", "m4a"]:
                postprocessors.append({"key": "EmbedThumbnail"})

        else:
            height_limit = None
            if quality.startswith("res_"):
                try:
                    height_limit = int(quality.replace("res_", ""))
                except ValueError:
                    pass

            if height_limit:
                format_spec = f"bestvideo[height<={height_limit}]+bestaudio/best[height<={height_limit}]/best"
            else:
                format_spec = "bestvideo+bestaudio/best"

            postprocessor_args = {"ffmpeg": ["-c:v", "copy", "-threads", "0"]}
            postprocessors = [
                {
                    "key": "FFmpegMetadata",
                    "add_metadata": True,
                }
            ]

        # Download strategies
        strategies = [
            {"js_runtimes": {"node": {}}, **({"cookiefile": cookie_path} if cookie_path else {})},
            {"js_runtimes": {"node": {}}, "extractor_args": {"youtube": {"player_client": ["android", "ios"]}}},
            {"js_runtimes": {"node": {}}, "extractor_args": {"youtube": {"player_client": ["web_creator", "mweb"]}}},
        ]

        last_error = None
        info = None

        for strategy in strategies:
            ydl_opts: Dict[str, Any] = {
                "outtmpl": outtmpl,
                "quiet": True,
                "no_warnings": True,
                "progress_hooks": [lambda d: self._progress_hook(task_id, d)],
                "noplaylist": True,
                "windowsfilenames": True,
                "restrictfilenames": False,
                "http_headers": DEFAULT_HTTP_HEADERS,
                "format": format_spec,
                "writethumbnail": media_type == "audio" and format_ext in ["mp3", "m4a"],
                "merge_output_format": "mp4" if media_type == "video" else None,
                "postprocessors": postprocessors,
                "postprocessor_args": postprocessor_args,
                "concurrent_fragment_downloads": 8,
                "buffersize": 1048576,
                "http_chunk_size": 10485760,
                "socket_timeout": 15,
                "retries": 5,
                "fragment_retries": 10,
                **strategy
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if info:
                        break
            except Exception as e:
                last_error = e
                logger.warning(f"Download strategy failed ({strategy}): {e}")

        if not info:
            with self.lock:
                task = self.tasks[task_id]
                task["status"] = "error"
                task["error"] = str(last_error)
                task["speed"] = "Failed"
                task["eta"] = "--"
            return

        try:
            if "entries" in info and info["entries"]:
                info = info["entries"][0]

            real_title = info.get("title") or initial_title or "media"
            thumbnail = info.get("thumbnail")

            downloaded_files = [
                os.path.join(task_dir, f)
                for f in os.listdir(task_dir)
                if not f.endswith(".temp") and not f.endswith(".part") and not f.endswith(".ytdl")
            ]

            if not downloaded_files:
                raise Exception("Media file could not be generated. Please check link accessibility.")

            media_files = [
                f for f in downloaded_files 
                if not f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
            ]
            final_file_path = media_files[0] if media_files else downloaded_files[0]
            
            file_name = os.path.basename(final_file_path)
            file_size = os.path.getsize(final_file_path)

            with self.lock:
                task = self.tasks[task_id]
                task["status"] = "completed"
                task["progress"] = 100.0
                task["speed"] = "Completed"
                task["eta"] = "00:00"
                task["title"] = real_title
                if thumbnail and not task.get("thumbnail"):
                    task["thumbnail"] = thumbnail
                task["file_path"] = final_file_path
                task["filename"] = file_name
                task["file_size"] = file_size
                task["file_size_str"] = format_bytes(file_size)
                logger.info(f"Task {task_id} completed: {file_name} ({task['file_size_str']})")

        except Exception as e:
            logger.error(f"Finalization failed for task {task_id}: {e}", exc_info=True)
            with self.lock:
                task = self.tasks[task_id]
                task["status"] = "error"
                task["error"] = str(e)
                task["speed"] = "Failed"
                task["eta"] = "--"


# Global singleton instance
downloader_instance = DownloadManager()
