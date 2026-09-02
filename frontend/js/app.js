/**
 * PulseStream - Universal Social Media Music & Video Downloader
 * Client Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const urlInput = document.getElementById("url-input");
  const btnClearUrl = document.getElementById("btn-clear-url");
  const btnPasteUrl = document.getElementById("btn-paste-url");
  const btnFetchInfo = document.getElementById("btn-fetch-info");
  const detectedPlatformBadge = document.getElementById("detected-platform-badge");
  const platformIconWrapper = document.getElementById("platform-icon-wrapper");

  const loadingState = document.getElementById("loading-state");
  const mediaCard = document.getElementById("media-card");
  const mediaThumbnail = document.getElementById("media-thumbnail");
  const mediaDuration = document.getElementById("media-duration");
  const thumbPlatformBadge = document.getElementById("thumb-platform-badge");
  const mediaTitle = document.getElementById("media-title");
  const mediaUploader = document.getElementById("media-uploader");
  const mediaViews = document.getElementById("media-views");

  const modeTabs = document.querySelectorAll(".mode-tab");
  const audioFormatsSection = document.getElementById("audio-formats-section");
  const videoFormatsSection = document.getElementById("video-formats-section");
  const btnStartDownload = document.getElementById("btn-start-download");
  const btnDownloadLabel = document.getElementById("btn-download-label");

  const progressCard = document.getElementById("progress-card");
  const progressMediaTitle = document.getElementById("progress-media-title");
  const progressStatusBadge = document.getElementById("progress-status-badge");
  const progressBarFill = document.getElementById("progress-bar-fill");
  const progressSpeed = document.getElementById("progress-speed");
  const progressEta = document.getElementById("progress-eta");
  const progressBytes = document.getElementById("progress-bytes");
  const progressStageNote = document.getElementById("progress-stage-note");
  const finishedActions = document.getElementById("finished-actions");
  const btnDirectDownload = document.getElementById("btn-direct-download");
  const btnPlayPreview = document.getElementById("btn-play-preview");

  // History & Batch Modals
  const btnOpenHistory = document.getElementById("btn-open-history");
  const historyModal = document.getElementById("history-modal");
  const btnCloseHistoryModal = document.getElementById("btn-close-history-modal");
  const historyItemsList = document.getElementById("history-items-list");
  const historyEmpty = document.getElementById("history-empty");
  const historyCounter = document.getElementById("history-counter");

  const btnBatchMode = document.getElementById("btn-batch-mode");
  const batchModal = document.getElementById("batch-modal");
  const btnCloseBatchModal = document.getElementById("btn-close-batch-modal");
  const btnStartBatch = document.getElementById("btn-start-batch");
  const batchUrlsInput = document.getElementById("batch-urls-input");
  const batchDefaultMode = document.getElementById("batch-default-mode");
  const batchQueueContainer = document.getElementById("batch-queue-container");
  const batchItemsList = document.getElementById("batch-items-list");

  // Floating Player
  const floatingAudioPlayer = document.getElementById("floating-audio-player");
  const globalAudio = document.getElementById("global-audio-element");
  const playerThumb = document.getElementById("player-thumb");
  const playerTitle = document.getElementById("player-title");
  const playerArtist = document.getElementById("player-artist");
  const playerBtnPlay = document.getElementById("player-btn-play");
  const iconPlay = document.getElementById("icon-play");
  const iconPause = document.getElementById("icon-pause");
  const playerSeekbar = document.getElementById("player-seekbar");
  const playerCurrentTime = document.getElementById("player-current-time");
  const playerTotalTime = document.getElementById("player-total-time");
  const playerVolume = document.getElementById("player-volume");
  const playerBtnClose = document.getElementById("player-btn-close");

  // Video Modal
  const videoModal = document.getElementById("video-modal");
  const btnCloseVideoModal = document.getElementById("btn-close-video-modal");
  const modalVideoElement = document.getElementById("modal-video-element");
  const videoModalTitle = document.getElementById("video-modal-title");

  // Toast Container
  const toastContainer = document.getElementById("toast-container");

  // Application State
  let currentMediaData = null;
  let activeMediaType = "audio"; // 'audio' or 'video'
  let selectedQuality = "mp3-320";
  let selectedExt = "mp3";
  let activeTaskId = null;
  let progressPollTimer = null;

  // Platform Definitions & Detection
  const platforms = [
    { key: "youtube", name: "YouTube", match: ["youtube.com", "youtu.be"], color: "#FF0000" },
    { key: "instagram", name: "Instagram", match: ["instagram.com"], color: "#E1306C" },
    { key: "facebook", name: "Facebook", match: ["facebook.com", "fb.watch"], color: "#1877F2" },
    { key: "tiktok", name: "TikTok", match: ["tiktok.com"], color: "#00F2FE" },
    { key: "twitter", name: "Twitter / X", match: ["twitter.com", "x.com"], color: "#1DA1F2" },
    { key: "soundcloud", name: "SoundCloud", match: ["soundcloud.com"], color: "#FF5500" },
    { key: "reddit", name: "Reddit", match: ["reddit.com", "redd.it"], color: "#FF4500" },
    { key: "vimeo", name: "Vimeo", match: ["vimeo.com"], color: "#1AB7EA" },
    { key: "pinterest", name: "Pinterest", match: ["pinterest.com", "pin.it"], color: "#BD081C" },
    { key: "twitch", name: "Twitch", match: ["twitch.tv"], color: "#9146FF" },
    { key: "spotify", name: "Spotify", match: ["spotify.com"], color: "#1DB954" },
  ];

  function detectPlatformFromUrl(url) {
    if (!url) return null;
    const lower = url.toLowerCase();
    return platforms.find(p => p.match.some(m => lower.includes(m))) || null;
  }

  function updatePlatformUI(platform) {
    if (platform) {
      detectedPlatformBadge.textContent = platform.name;
      detectedPlatformBadge.style.display = "inline-block";
      detectedPlatformBadge.style.borderColor = platform.color;
      detectedPlatformBadge.style.color = "#fff";
      detectedPlatformBadge.style.background = platform.color + "33";
    } else {
      detectedPlatformBadge.style.display = "none";
    }
  }

  // Input Events
  urlInput.addEventListener("input", () => {
    const val = urlInput.value.trim();
    btnClearUrl.style.display = val ? "flex" : "none";
    const detected = detectPlatformFromUrl(val);
    updatePlatformUI(detected);
  });

  urlInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      fetchMediaInfo();
    }
  });

  btnClearUrl.addEventListener("click", () => {
    urlInput.value = "";
    btnClearUrl.style.display = "none";
    detectedPlatformBadge.style.display = "none";
    mediaCard.style.display = "none";
    urlInput.focus();
  });

  btnPasteUrl.addEventListener("click", async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        urlInput.value = text.trim();
        btnClearUrl.style.display = "flex";
        const detected = detectPlatformFromUrl(text);
        updatePlatformUI(detected);
        showToast("Link pasted from clipboard", "info");
        fetchMediaInfo();
      }
    } catch (err) {
      showToast("Unable to read clipboard. Please paste manually (Ctrl+V).", "error");
      urlInput.focus();
    }
  });

  btnFetchInfo.addEventListener("click", fetchMediaInfo);

  // Platform chip click helpers
  document.querySelectorAll(".platform-chips .chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const platformKey = chip.getAttribute("data-platform");
      if (platformKey === "youtube") {
        urlInput.value = "https://www.youtube.com/watch?v=kJQP7kiw5Fk";
      } else if (platformKey === "instagram") {
        urlInput.value = "https://www.instagram.com/reel/C3_example";
      } else if (platformKey === "soundcloud") {
        urlInput.value = "https://soundcloud.com/artist/track";
      }
      urlInput.dispatchEvent(new Event("input"));
    });
  });

  // Fetch Media Information from Backend
  async function fetchMediaInfo() {
    const url = urlInput.value.trim();
    if (!url) {
      showToast("Please enter or paste a valid link first.", "error");
      urlInput.focus();
      return;
    }

    // Update button loading state
    btnFetchInfo.disabled = true;
    btnFetchInfo.querySelector(".btn-text").textContent = "Analyzing...";
    btnFetchInfo.querySelector(".btn-arrow").style.display = "none";
    btnFetchInfo.querySelector(".loader-spinner").style.display = "inline-block";

    mediaCard.style.display = "none";
    progressCard.style.display = "none";
    loadingState.style.display = "block";

    try {
      const response = await fetch("/api/info", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url })
      });

      let data;
      const rawText = await response.text();
      try {
        data = JSON.parse(rawText);
      } catch (_) {
        throw new Error(response.status === 404 ? "Server API endpoint not found. Please verify backend is running." : (rawText || `Server returned error (${response.status})`));
      }

      if (!response.ok || !data.success) {
        throw new Error(data.detail || data.error || "Failed to analyze link.");
      }

      currentMediaData = data;
      renderMediaCard(data);
      showToast("Media details extracted successfully!", "success");
    } catch (err) {
      console.error(err);
      showToast(err.message || "Could not read media link.", "error");
    } finally {
      loadingState.style.display = "none";
      btnFetchInfo.disabled = false;
      btnFetchInfo.querySelector(".btn-text").textContent = "Analyze Link";
      btnFetchInfo.querySelector(".btn-arrow").style.display = "inline-block";
      btnFetchInfo.querySelector(".loader-spinner").style.display = "none";
    }
  }

  // Render Extracted Media Details into Card
  function renderMediaCard(data) {
    mediaThumbnail.src = data.thumbnail || "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='320' height='180' fill='%231e293b'></svg>";
    mediaDuration.textContent = data.duration_formatted || "00:00";
    mediaTitle.textContent = data.title || "Media Stream";
    mediaUploader.textContent = data.uploader || "Universal Stream";
    mediaViews.textContent = data.view_count ? `${data.view_count} views` : data.platform.name;

    thumbPlatformBadge.textContent = data.platform.badge || data.platform.name;
    thumbPlatformBadge.style.borderColor = data.platform.color;

    // Render Audio Formats
    audioFormatsSection.innerHTML = "";
    (data.audio_options || []).forEach(opt => {
      const pill = document.createElement("div");
      pill.className = `format-pill ${opt.recommended ? "selected" : ""}`;
      pill.setAttribute("data-id", opt.id);
      pill.setAttribute("data-ext", opt.ext);
      pill.setAttribute("data-type", "audio");

      pill.innerHTML = `
        ${opt.recommended ? '<span class="rec-badge">BEST</span>' : ""}
        <span class="format-name">${opt.label.split(" ")[0]}</span>
        <span class="format-desc">${opt.label.replace(opt.label.split(" ")[0], "").trim()}</span>
      `;

      pill.addEventListener("click", () => selectFormatOption(pill, "audio", opt.id, opt.ext, opt.label));
      audioFormatsSection.appendChild(pill);

      if (opt.recommended && activeMediaType === "audio") {
        selectedQuality = opt.id;
        selectedExt = opt.ext;
        updateDownloadButtonLabel(opt.label);
      }
    });

    // Render Video Formats
    videoFormatsSection.innerHTML = "";
    (data.video_options || []).forEach(opt => {
      const pill = document.createElement("div");
      pill.className = `format-pill ${opt.recommended ? "selected" : ""}`;
      pill.setAttribute("data-id", opt.id);
      pill.setAttribute("data-ext", opt.ext);
      pill.setAttribute("data-type", "video");

      pill.innerHTML = `
        ${opt.recommended ? '<span class="rec-badge">POPULAR</span>' : ""}
        <span class="format-name">${opt.resolution}</span>
        <span class="format-desc">${opt.label}</span>
      `;

      pill.addEventListener("click", () => selectFormatOption(pill, "video", opt.id, opt.ext, opt.label));
      videoFormatsSection.appendChild(pill);
    });

    // Reset to current active tab
    setActiveTab(activeMediaType);
    mediaCard.style.display = "block";
    mediaCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  // Format selection handler
  function selectFormatOption(element, type, qualityId, ext, label) {
    const parent = type === "audio" ? audioFormatsSection : videoFormatsSection;
    parent.querySelectorAll(".format-pill").forEach(p => p.classList.remove("selected"));
    element.classList.add("selected");
    selectedQuality = qualityId;
    selectedExt = ext;
    updateDownloadButtonLabel(label);
  }

  function updateDownloadButtonLabel(label) {
    if (activeMediaType === "audio") {
      btnDownloadLabel.textContent = `⚡ Download Music (${label.split("(")[0].trim()})`;
    } else {
      btnDownloadLabel.textContent = `⚡ Download Video (${label.split("(")[0].trim()})`;
    }
  }

  // Mode Tabs Click (Audio vs Video)
  modeTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const type = tab.getAttribute("data-type");
      setActiveTab(type);
    });
  });

  function setActiveTab(type) {
    activeMediaType = type;
    modeTabs.forEach(t => {
      if (t.getAttribute("data-type") === type) {
        t.classList.add("active");
      } else {
        t.classList.remove("active");
      }
    });

    if (type === "audio") {
      audioFormatsSection.style.display = "grid";
      videoFormatsSection.style.display = "none";
      const selectedAudio = audioFormatsSection.querySelector(".format-pill.selected");
      if (selectedAudio) selectedAudio.click();
    } else {
      audioFormatsSection.style.display = "none";
      videoFormatsSection.style.display = "grid";
      const selectedVideo = videoFormatsSection.querySelector(".format-pill.selected");
      if (selectedVideo) selectedVideo.click();
    }
  }

  // Start Download Action
  btnStartDownload.addEventListener("click", async () => {
    if (!currentMediaData) return;

    btnStartDownload.disabled = true;
    showToast(`Starting ${activeMediaType} extraction...`, "info");

    try {
      const payload = {
        url: currentMediaData.url,
        media_type: activeMediaType,
        quality: selectedQuality,
        format_ext: selectedExt,
        title: currentMediaData.title,
        thumbnail: currentMediaData.thumbnail,
      };

      const res = await fetch("/api/download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok || !data.task_id) {
        throw new Error(data.detail || "Failed to start download task.");
      }

      activeTaskId = data.task_id;
      showProgressView(currentMediaData.title);
      startProgressPolling(activeTaskId);
    } catch (err) {
      showToast(err.message || "Failed to initiate download.", "error");
      btnStartDownload.disabled = false;
    }
  });

  // Show and Track Progress
  function showProgressView(title) {
    progressMediaTitle.textContent = title;
    progressStatusBadge.textContent = "Connecting...";
    progressBarFill.style.width = "5%";
    progressSpeed.textContent = "0 KB/s";
    progressEta.textContent = "ETA: --:--";
    progressBytes.textContent = "Initiating stream...";
    progressStageNote.textContent = "Contacting media servers...";
    finishedActions.style.display = "none";
    progressCard.style.display = "block";
    progressCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function startProgressPolling(taskId) {
    if (progressPollTimer) clearInterval(progressPollTimer);

    progressPollTimer = setInterval(async () => {
      try {
        const res = await fetch(`/api/progress/${taskId}`);
        if (!res.ok) return;
        const task = await res.json();

        updateProgressUI(task);

        if (task.status === "completed") {
          clearInterval(progressPollTimer);
          handleDownloadCompleted(task);
        } else if (task.status === "error") {
          clearInterval(progressPollTimer);
          handleDownloadError(task);
        }
      } catch (err) {
        console.error("Progress poll error:", err);
      }
    }, 600);
  }

  function updateProgressUI(task) {
    const pct = Math.min(Math.max(task.progress || 0, 0), 100);
    progressBarFill.style.width = `${pct}%`;

    if (task.status === "downloading") {
      progressStatusBadge.textContent = `Downloading ${pct}%`;
      progressSpeed.textContent = task.speed || "Downloading...";
      progressEta.textContent = `ETA: ${task.eta || "--:--"}`;
      progressBytes.textContent = `${task.downloaded_str || "0 MB"} / ${task.total_str || "--"}`;
      progressStageNote.textContent = "Extracting highest quality media stream...";
    } else if (task.status === "converting") {
      progressStatusBadge.textContent = "Processing & Converting...";
      progressSpeed.textContent = "FFmpeg Active";
      progressEta.textContent = "Finalizing";
      progressBytes.textContent = "Embedding tags & artwork...";
      progressStageNote.textContent = activeMediaType === "audio" 
        ? "Encoding high-fidelity 320kbps MP3 with album artwork..." 
        : "Multiplexing video and audio streams...";
    }
  }

  function handleDownloadCompleted(task) {
    progressBarFill.style.width = "100%";
    progressStatusBadge.textContent = "Ready!";
    progressSpeed.textContent = task.file_size_str || "Done";
    progressEta.textContent = "Complete";
    progressBytes.textContent = `File: ${task.filename}`;
    progressStageNote.textContent = "Conversion finished successfully!";

    btnDirectDownload.href = `/api/file/${task.task_id}`;
    btnDirectDownload.setAttribute("download", task.filename || "media_download");

    finishedActions.style.display = "block";
    btnStartDownload.disabled = false;

    // Trigger auto-download via virtual anchor
    triggerAutoDownload(`/api/file/${task.task_id}`, task.filename);

    showToast("🎉 Download completed successfully!", "success");
    updateHistoryCount();
  }

  function handleDownloadError(task) {
    progressBarFill.style.width = "100%";
    progressBarFill.style.background = "#f43f5e";
    progressStatusBadge.textContent = "Failed";
    progressStatusBadge.style.color = "#f43f5e";
    progressSpeed.textContent = "Error";
    progressEta.textContent = "--";
    progressStageNote.textContent = task.error || "An error occurred during extraction.";
    btnStartDownload.disabled = false;
    showToast("Download failed. Link may be restricted or private.", "error");
  }

  function triggerAutoDownload(url, filename) {
    const a = document.createElement("a");
    a.href = url;
    if (filename) a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  // Play Preview Button
  btnPlayPreview.addEventListener("click", () => {
    if (!activeTaskId) return;
    if (activeMediaType === "audio") {
      playInAudioPlayer(
        `/api/preview/${activeTaskId}`,
        currentMediaData?.title || "Audio Track",
        currentMediaData?.uploader || "Universal Media",
        currentMediaData?.thumbnail
      );
    } else {
      openVideoModal(
        `/api/preview/${activeTaskId}`,
        currentMediaData?.title || "Video Preview"
      );
    }
  });

  // Floating In-App Audio Player Logic
  function playInAudioPlayer(streamUrl, title, artist, thumb) {
    playerTitle.textContent = title || "Audio Track";
    playerArtist.textContent = artist || "Artist";
    playerThumb.src = thumb || "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='44' height='44' fill='%231e293b'></svg>";

    globalAudio.src = streamUrl;
    globalAudio.play();
    floatingAudioPlayer.style.display = "flex";
    setPlayerPlayingState(true);
  }

  function setPlayerPlayingState(isPlaying) {
    iconPlay.style.display = isPlaying ? "none" : "block";
    iconPause.style.display = isPlaying ? "block" : "none";
  }

  playerBtnPlay.addEventListener("click", () => {
    if (globalAudio.paused) {
      globalAudio.play();
      setPlayerPlayingState(true);
    } else {
      globalAudio.pause();
      setPlayerPlayingState(false);
    }
  });

  globalAudio.addEventListener("timeupdate", () => {
    if (!isNaN(globalAudio.duration)) {
      const pct = (globalAudio.currentTime / globalAudio.duration) * 100;
      playerSeekbar.value = pct;
      playerCurrentTime.textContent = formatSec(globalAudio.currentTime);
      playerTotalTime.textContent = formatSec(globalAudio.duration);
    }
  });

  playerSeekbar.addEventListener("input", () => {
    if (!isNaN(globalAudio.duration)) {
      globalAudio.currentTime = (playerSeekbar.value / 100) * globalAudio.duration;
    }
  });

  playerVolume.addEventListener("input", () => {
    globalAudio.volume = playerVolume.value;
  });

  playerBtnClose.addEventListener("click", () => {
    globalAudio.pause();
    floatingAudioPlayer.style.display = "none";
  });

  function formatSec(s) {
    if (isNaN(s)) return "00:00";
    const mins = Math.floor(s / 60);
    const secs = Math.floor(s % 60);
    return `${mins < 10 ? "0" : ""}${mins}:${secs < 10 ? "0" : ""}${secs}`;
  }

  // Video Preview Modal Logic
  function openVideoModal(videoUrl, title) {
    videoModalTitle.textContent = title;
    modalVideoElement.src = videoUrl;
    videoModal.style.display = "flex";
    modalVideoElement.play();
  }

  btnCloseVideoModal.addEventListener("click", () => {
    modalVideoElement.pause();
    modalVideoElement.src = "";
    videoModal.style.display = "none";
  });

  // History Drawer Logic
  btnOpenHistory.addEventListener("click", loadHistory);
  btnCloseHistoryModal.addEventListener("click", () => historyModal.style.display = "none");

  async function loadHistory() {
    try {
      const res = await fetch("/api/history");
      const data = await res.json();
      renderHistory(data.history || []);
      historyModal.style.display = "flex";
    } catch (err) {
      showToast("Could not load history.", "error");
    }
  }

  function renderHistory(items) {
    historyItemsList.innerHTML = "";
    historyCounter.textContent = items.length;

    if (items.length === 0) {
      historyEmpty.style.display = "block";
      return;
    }
    historyEmpty.style.display = "none";

    items.forEach(item => {
      const row = document.createElement("div");
      row.className = "history-item-row";
      row.innerHTML = `
        <img class="history-thumb" src="${item.thumbnail || ''}" alt="thumb" />
        <div class="history-item-details">
          <div class="history-item-title">${item.title}</div>
          <div class="history-item-meta">${item.format_ext.toUpperCase()} • ${item.file_size_str} • ${item.platform.name}</div>
        </div>
        <div class="history-item-actions">
          <a class="btn btn-secondary" href="/api/file/${item.task_id}" download title="Download again" style="padding: 6px 10px;">💾</a>
          <button class="btn btn-secondary btn-history-play" data-task="${item.task_id}" data-title="${encodeURIComponent(item.title)}" data-type="${item.media_type}" data-thumb="${encodeURIComponent(item.thumbnail || '')}" title="Play preview" style="padding: 6px 10px;">▶</button>
          <button class="btn btn-ghost btn-history-del" data-task="${item.task_id}" title="Delete file" style="padding: 6px 10px; color: #f43f5e;">✕</button>
        </div>
      `;

      row.querySelector(".btn-history-play").addEventListener("click", (e) => {
        const btn = e.currentTarget;
        const tid = btn.getAttribute("data-task");
        const title = decodeURIComponent(btn.getAttribute("data-title"));
        const type = btn.getAttribute("data-type");
        const thumb = decodeURIComponent(btn.getAttribute("data-thumb"));
        historyModal.style.display = "none";

        if (type === "audio") {
          playInAudioPlayer(`/api/preview/${tid}`, title, "Saved Track", thumb);
        } else {
          openVideoModal(`/api/preview/${tid}`, title);
        }
      });

      row.querySelector(".btn-history-del").addEventListener("click", async (e) => {
        const tid = e.currentTarget.getAttribute("data-task");
        await fetch(`/api/history/${tid}`, { method: "DELETE" });
        row.remove();
        updateHistoryCount();
      });

      historyItemsList.appendChild(row);
    });
  }

  async function updateHistoryCount() {
    try {
      const res = await fetch("/api/history");
      const data = await res.json();
      historyCounter.textContent = (data.history || []).length;
    } catch (_) {}
  }
  updateHistoryCount();

  // Batch Mode Logic
  btnBatchMode.addEventListener("click", () => {
    batchModal.style.display = "flex";
  });
  btnCloseBatchModal.addEventListener("click", () => {
    batchModal.style.display = "none";
  });

  btnStartBatch.addEventListener("click", async () => {
    const raw = batchUrlsInput.value.trim();
    if (!raw) {
      showToast("Please paste at least one URL.", "error");
      return;
    }

    const urls = raw.split("\n").map(u => u.trim()).filter(u => u.length > 5);
    if (urls.length === 0) {
      showToast("No valid links found.", "error");
      return;
    }

    batchQueueContainer.style.display = "block";
    batchItemsList.innerHTML = "";
    btnStartBatch.disabled = true;

    const mode = batchDefaultMode.value; // e.g. 'audio-320', 'video-best'
    const isAudio = mode.startsWith("audio");
    const quality = isAudio ? (mode === "audio-320" ? "mp3-320" : "mp3-192") : (mode === "video-best" ? "best" : "res_720");
    const format_ext = isAudio ? "mp3" : "mp4";

    for (let i = 0; i < urls.length; i++) {
      const u = urls[i];
      const itemRow = document.createElement("div");
      itemRow.className = "batch-item-row";
      itemRow.innerHTML = `
        <div style="flex: 1; overflow: hidden;">
          <div style="font-size: 0.85rem; font-weight: 600; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${u}</div>
          <div class="batch-item-status" style="font-size: 0.75rem; color: #a5b4fc;">Analyzing link...</div>
        </div>
      `;
      batchItemsList.appendChild(itemRow);
      const statusEl = itemRow.querySelector(".batch-item-status");

      try {
        // Step 1: Info
        const infoRes = await fetch("/api/info", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: u })
        });
        const infoData = await infoRes.json();
        if (!infoRes.ok || !infoData.success) {
          statusEl.textContent = `❌ Failed: ${infoData.detail || "Unable to extract"}`;
          statusEl.style.color = "#f43f5e";
          continue;
        }

        statusEl.textContent = `⏳ Downloading ${infoData.title.slice(0, 40)}...`;

        // Step 2: Download
        const dlRes = await fetch("/api/download", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            url: u,
            media_type: isAudio ? "audio" : "video",
            quality: quality,
            format_ext: format_ext,
            title: infoData.title,
            thumbnail: infoData.thumbnail,
          })
        });
        const dlData = await dlRes.json();

        // Polling until finished
        await new Promise((resolve) => {
          const poll = setInterval(async () => {
            const pRes = await fetch(`/api/progress/${dlData.task_id}`);
            if (pRes.ok) {
              const pData = await pRes.json();
              if (pData.status === "downloading") {
                statusEl.textContent = `⬇️ Downloading (${pData.progress}% - ${pData.speed})`;
              } else if (pData.status === "converting") {
                statusEl.textContent = `⚙️ Converting to ${format_ext.toUpperCase()}...`;
              } else if (pData.status === "completed") {
                clearInterval(poll);
                statusEl.innerHTML = `✅ Complete! <a href="/api/file/${dlData.task_id}" download style="color: #34d399; font-weight: 700; margin-left: 8px;">[Save File]</a>`;
                triggerAutoDownload(`/api/file/${dlData.task_id}`, pData.filename);
                resolve();
              } else if (pData.status === "error") {
                clearInterval(poll);
                statusEl.textContent = `❌ Error: ${pData.error}`;
                statusEl.style.color = "#f43f5e";
                resolve();
              }
            }
          }, 1000);
        });
      } catch (err) {
        statusEl.textContent = `❌ Error: ${err.message}`;
        statusEl.style.color = "#f43f5e";
      }
    }

    btnStartBatch.disabled = false;
    showToast("Batch processing finished!", "success");
    updateHistoryCount();
  });

  // Modal Backdrop Click Dismissal
  [historyModal, batchModal, videoModal].forEach(modal => {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) modal.style.display = "none";
    });
  });

  // Toast Notification Helper
  function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(50px)";
      setTimeout(() => toast.remove(), 300);
    }, 3800);
  }
});
