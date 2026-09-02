@echo off
title PulseStream - Cloudflare Online Sharing
echo =========================================================================
echo  Starting PulseStream with Free Cloudflare Public Link
echo =========================================================================
echo.

python share_online.py

if errorlevel 1 (
    echo.
    echo [ERROR] Could not start Cloudflare tunnel.
    pause
)
