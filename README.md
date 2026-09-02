# PulseStream — Universal Social Media Music & Video Downloader

PulseStream is a modern, full-featured web application designed to download high-quality **music** (MP3, M4A, WAV, FLAC) and **videos** (MP4 up to 4K/1080p) from almost any social media platform.

---

## 🌟 Key Features

- **Universal Multi-Platform Support**:
  - **YouTube**: Videos, Shorts, Playlists, YouTube Music.
  - **Instagram**: Reels, Posts, IGTV, Audio tracks.
  - **Facebook**: Public Videos, Reels, Watch clips.
  - **TikTok**: High-res video with watermark-free audio extraction.
  - **Twitter / X**: Video clips and audio tweets.
  - **SoundCloud & Bandcamp**: Studio-quality music streams.
  - **Reddit, Pinterest, Vimeo, Twitch**: Clips and media.
  - Plus 1,000+ additional platforms supported via `yt-dlp`.

- **Studio-Grade Audio Extraction**:
  - Convert any video or stream to **MP3 (320kbps High Fidelity, 256kbps, 192kbps, 128kbps)**.
  - Formats: **MP3, M4A (AAC), WAV, FLAC**.
  - **Automatic ID3 Tagging & Album Cover Embedding**: Original track title, creator/artist, and HD cover artwork are embedded directly into the downloaded audio files.

- **High-Definition Video Downloads**:
  - Download in **4K (2160p), 1440p (2K), 1080p (Full HD), 720p (HD), 480p, 360p**.
  - Seamlessly multiplexes separate video and audio streams into clean universal **MP4** files.

- **Interactive Cyber Obsidian & Glassmorphism UI**:
  - **Auto Platform Recognition**: Detects the platform in real time as you paste or type links and displays the official platform badge.
  - **1-Click Clipboard Paste**: Instant reading from clipboard with auto-inspection.
  - **Live Download Progress Tracker**: Shows real-time percentage, download speed (MB/s), ETA (seconds), and conversion state.
  - **Built-in Audio & Video Player**: Preview and play downloaded tracks or video clips directly inside the app before or after saving.
  - **Batch Downloader**: Paste multiple URLs (one per line) to analyze and download in bulk.
  - **Download History**: Session history with 1-click re-download and playback.

---

## 🚀 Quick Start

### 1. Launch with One Click (Windows)
Double-click `run.bat` or run in terminal:

```bash
python start.py
```

This will:
1. Verify all dependencies and initialize FFmpeg automatically.
2. Start the FastAPI backend server on `http://127.0.0.1:8000`.
3. Open your default web browser automatically to the PulseStream web app.

---

## 🛠 Project Structure

```
music downloader/
├── backend/
│   ├── app.py             # FastAPI REST endpoints & static file server
│   ├── downloader.py      # yt-dlp extraction engine, FFmpeg pipeline, & progress tracker
│   └── requirements.txt   # Python dependencies (FastAPI, yt-dlp, static-ffmpeg, mutagen, etc.)
├── frontend/
│   ├── css/
│   │   └── style.css      # Cyber Obsidian glassmorphism stylesheet & responsive layout
│   ├── js/
│   │   └── app.js         # Client-side platform detection, format manager, & player logic
│   └── index.html         # Modern web application interface
├── downloads/             # Temp and completed media storage (auto-created)
├── run.bat                # 1-click Windows starter
├── start.py               # Cross-platform Python launcher
└── README.md
```

---

## 🎧 Supported Audio & Video Formats

| Format | Quality / Bitrate | Description |
|---|---|---|
| **MP3** | 320 kbps (High Fidelity) | Maximum audio quality with embedded HD album cover art |
| **MP3** | 256 kbps (Studio Quality) | High audio clarity with low file size |
| **MP3** | 192 kbps (Standard) | Balanced everyday quality |
| **MP3** | 128 kbps (Compact) | Lightweight audio file |
| **M4A** | Best AAC Stream | Native Apple / iOS audio container |
| **FLAC** | Lossless | Studio-grade uncompressed audio |
| **WAV** | Uncompressed PCM | Lossless standard audio format |
| **MP4** | 4K / 1440p / 1080p / 720p | Multiplexed MP4 video with full stereo audio |

---

## 🔒 Privacy & Local Processing
All downloads and conversions are processed directly on your local machine. No external tracking, rate limits, or intermediate third-party servers.
