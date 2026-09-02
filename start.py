import os
import sys
import socket
import webbrowser
import subprocess
import time

# Set current directory to script root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def find_available_port(preferred_port: int = 8000, host: str = "127.0.0.1") -> int:
    for port in [preferred_port, 8001, 8080, 5000, 3000]:
        if not is_port_in_use(port, host):
            return port
    return preferred_port

def ensure_dependencies():
    """Ensure all required Python packages and static-ffmpeg are installed."""
    try:
        import fastapi
        import uvicorn
        import yt_dlp
        import static_ffmpeg
        static_ffmpeg.add_paths()
        print("✓ Core dependencies and FFmpeg initialized successfully.")
    except ImportError as e:
        print(f"[!] Missing dependency: {e}. Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", os.path.join(BACKEND_DIR, "requirements.txt")])
        import static_ffmpeg
        static_ffmpeg.add_paths()
        print("✓ Dependencies installed.")

def main():
    print("=" * 60)
    print("  PulseStream - Universal Social Media Music & Video Downloader")
    print("=" * 60)
    ensure_dependencies()

    host = "127.0.0.1"
    port = find_available_port(8000, host)
    url = f"http://{host}:{port}"
    print(f"\n🚀 Launching Web Application on {url}")
    print("💡 Paste links from YouTube, Instagram, Facebook, TikTok, Twitter/X, SoundCloud and more!\n")

    def open_browser():
        time.sleep(1.2)
        webbrowser.open(url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    import uvicorn
    from app import app
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    main()
