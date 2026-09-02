import os
import re
import sys
import time
import shutil
import subprocess
import threading
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def find_cloudflared():
    """Find cloudflared executable."""
    exe = shutil.which("cloudflared")
    if exe:
        return exe
    
    # Common winget / program files install paths
    possible_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages"),
        r"C:\Program Files\Cloudflare\cloudflared",
        r"C:\Program Files (x86)\Cloudflare\cloudflared",
    ]
    for p in possible_paths:
        if os.path.exists(p):
            for root, _, files in os.walk(p):
                if "cloudflared.exe" in files:
                    return os.path.join(root, "cloudflared.exe")
    return "cloudflared"

def main():
    print("=" * 65)
    print("  PulseStream - Launching Cloudflare Tunnel & Public Link")
    print("=" * 65)

    # 1. Start App backend if not already running
    import socket
    def is_port_in_use(port=8000):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) == 0

    if not is_port_in_use(8000):
        print("[*] Starting local PulseStream server...")
        subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "start.py")], cwd=BASE_DIR)
        time.sleep(2)
    else:
        print("[✓] PulseStream server is already running on http://127.0.0.1:8000")

    cloudflared_bin = find_cloudflared()
    print(f"[*] Starting Cloudflare Tunnel via: {cloudflared_bin}...")
    
    try:
        proc = subprocess.Popen(
            [cloudflared_bin, "tunnel", "--url", "http://127.0.0.1:8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
    except FileNotFoundError:
        print("\n[ERROR] 'cloudflared' command not found.")
        print("Please install it by running: winget install Cloudflare.cloudflared")
        input("\nPress Enter to exit...")
        return

    url_found = False
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    for line in iter(proc.stdout.readline, ''):
        match = url_pattern.search(line)
        if match and not url_found:
            public_url = match.group(0)
            url_found = True
            print("\n" + "=" * 65)
            print("  🎉 YOUR PUBLIC CLOUDFLARE LINK IS READY!")
            print("=" * 65)
            print(f"\n  👉  {public_url}  👈\n")
            print("=" * 65)
            print("  • Share this link with anyone to let them download music & videos!")
            print("  • Keep this window OPEN while you want the link active.")
            print("=" * 65 + "\n")
            
            # Open the URL in default browser
            try:
                webbrowser.open(public_url)
            except Exception:
                pass
        
        # Also print important errors or logs if needed
        if "ERR" in line or "error" in line.lower():
            print(line.strip())

    proc.stdout.close()
    proc.wait()

if __name__ == "__main__":
    main()
