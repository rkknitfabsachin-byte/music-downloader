# Production Dockerfile for PulseStream with YouTube PO Token Bot Bypass
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8000 \
    HOME=/root

# Install system dependencies: FFmpeg, git, curl, aria2
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    aria2 \
    curl \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20.x (with npm) for BotGuard challenge solving
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Clone and build bgutil POT (Proof of Origin Token) server scripts
# This solves YouTube's BotGuard challenge to generate tokens that bypass datacenter IP blocks
RUN git clone --depth 1 https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git /root/bgutil-ytdlp-pot-provider && \
    cd /root/bgutil-ytdlp-pot-provider/server && \
    npm install && \
    npx tsc

WORKDIR /app

# Copy requirements and install Python dependencies (including POT plugins)
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy application source files
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY start.py ./
COPY cookies.txt* ./

# Create downloads directory
RUN mkdir -p downloads && chmod 777 downloads

EXPOSE 8000

# Start FastAPI application
CMD ["sh", "-c", "python -m uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
