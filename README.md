# i-Downloader

A fast, multi-threaded download manager built with Python and PyQt6.

## Features

- 🚀 **Multi-threaded Downloads** - Split files into segments for faster downloads
- ⏸️ **Pause/Resume** - Resume interrupted downloads
- 📋 **Download Queue** - Manage multiple downloads
- 📊 **Progress Tracking** - Real-time speed and ETA
- 🌙 **Dark Theme** - Modern, eye-friendly interface

## Requirements

- Python 3.11+
- Windows/Linux/macOS

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Usage

1. Click **"+ Add"** to add a new download
2. Paste the URL and choose save location
3. Click **"Download"** to start

## Roadmap

### ✅ Completed

- [x] **Multi-threaded Downloads** - Split files into segments for faster downloads
- [x] **Pause/Resume** - Resume interrupted downloads
- [x] **Download Queue** - Manage multiple downloads with priority system
- [x] **Progress Tracking** - Real-time speed and ETA display
- [x] **Dark Theme** - Modern, eye-friendly interface
- [x] **System Tray** - Minimize to tray with quick actions
- [x] **Settings Dialog** - Configure download preferences

### 🎯 High Priority

- [ ] **Watch Clipboard** - Auto-detect copied URLs and prompt to download
- [ ] **Download Categories** - Auto-organize files by type (Videos, Images, Documents, etc.)
- [ ] **Download Scheduler** - Schedule downloads for specific times
- [ ] **Bandwidth Limiter** - Limit download speed to preserve bandwidth
- [ ] **Batch URL Import** - Import multiple URLs from text or file

### 🔧 Medium Priority

- [ ] **Auto-retry on Failure** - Automatically retry failed downloads
- [ ] **Download History** - Complete history with search and filter
- [ ] **Notifications** - Windows toast notifications on completion
- [ ] **Checksum Verification** - Verify MD5/SHA256 after download
- [ ] **Proxy Support** - HTTP/SOCKS proxy configuration

### 🚀 Advanced Features

- [ ] **Video Site Integration** - YouTube, TikTok, Twitter support via yt-dlp
- [ ] **Torrent Support** - Magnet links and .torrent files
- [ ] **Cloud Integration** - Direct upload to Google Drive, OneDrive
- [ ] **Keyboard Shortcuts** - Global hotkeys for quick actions
- [ ] **Plugin System** - Extensible architecture for custom plugins

## License

MIT License
