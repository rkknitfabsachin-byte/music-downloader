# 🌐 Cloudflare & Cloud Hosting Guide for PulseStream

This guide walks you through hosting **PulseStream** using **Cloudflare** for maximum speed, global DDoS protection, and SSL.

---

## 🎯 Architecture Options

```
Option 1 (100% Free - Cloudflare Tunnel):
[Users Worldwide] --> [Cloudflare CDN + SSL] --> [Cloudflare Tunnel] --> [Your Local PC / Server (Port 8000)]

Option 2 (24/7 Always-On Cloud):
[Users Worldwide] --> [Cloudflare Pages (Frontend)] --> [Cloud Backend (Railway/Render/Hetzner)]
```

---

## 🚀 Option 1: 100% Free Hosting via Cloudflare Tunnel

Cloudflare Tunnel lets you securely expose the web app running on your computer to any custom domain (or a free `trycloudflare.com` URL) without port-forwarding and without exposing your IP address.

### Step 1: Install Cloudflare Tunnel Client (`cloudflared`)
On Windows, open PowerShell / Terminal and run:

```powershell
winget install Cloudflare.cloudflared
```

### Step 2: Start the Web App
Double click `run.bat` or run:
```bash
python start.py
```

### Step 3: Launch the Cloudflare Tunnel
In a new terminal window:
```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

Cloudflare will give you a public HTTPS URL (e.g. `https://random-name.trycloudflare.com`) that anyone in the world can access!

### Step 4: (Optional) Connect Your Own Custom Domain
If you have a domain on Cloudflare (e.g., `mydownloader.com`):
1. Log into your [Cloudflare Dashboard](https://dash.cloudflare.com/) -> **Zero Trust** -> **Networks** -> **Tunnels**.
2. Click **Create a Tunnel** and copy the command to run on your machine.
3. Route `https://download.mydownloader.com` to `http://localhost:8000`.

---

## ☁️ Option 2: 24/7 Cloud Hosting (Railway / Render / VPS)

### Method A: Deploy on Railway (Recommended)
1. Push this project folder to your GitHub account (`git init`, `git add .`, `git commit -m "init"`, `git push`).
2. Go to [Railway.app](https://railway.app/) and click **New Project** -> **Deploy from GitHub repo**.
3. Railway automatically detects the `Dockerfile` and builds the Python + FFmpeg container.
4. Add your custom domain in Railway settings, or link it to Cloudflare DNS with CNAME.

### Method B: Deploy on Render.com
1. Go to [Render.com](https://render.com/) -> **New Web Service**.
2. Connect your GitHub repository.
3. Environment: **Docker**.
4. Port: `8000`.
5. Click **Deploy**.

### Method C: Deploy on a Linux VPS (Hetzner / DigitalOcean / Ubuntu)
1. Clone your repo onto the server:
   ```bash
   git clone <your-repo-url> && cd music-downloader
   ```
2. Build and run with Docker Compose:
   ```bash
   docker compose up -d --build
   ```
3. Your app is now live on `http://YOUR_SERVER_IP:8000`!
