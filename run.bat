@echo off
title PulseStream - Universal Media Downloader
echo =========================================================================
echo  Starting PulseStream - Universal Social Media Music and Video Downloader
echo =========================================================================
echo.

python start.py

if errorlevel 1 (
    echo.
    echo [ERROR] An error occurred while running the application.
    pause
)
