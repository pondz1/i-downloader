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

- [x] **Watch Clipboard** - Auto-detect copied URLs and prompt to download
- [x] **Download Categories** - Auto-organize files by type (Videos, Images, Documents, etc.)
- [x] **Download Scheduler** - Schedule downloads for specific times
- [x] **Bandwidth Limiter** - Limit download speed to preserve bandwidth
- [x] **Batch URL Import** - Import multiple URLs from text or file

### 🔧 Medium Priority

- [x] **Auto-retry on Failure** - Automatically retry failed downloads
- [x] **Download History** - Complete history with search and filter
- [x] **Notifications** - Windows toast notifications on completion
- [x] **Checksum Verification** - Verify MD5/SHA256 after download
- [x] **Proxy Support** - HTTP/SOCKS proxy configuration

### 🚀 Advanced Features

- [ ] **Video Site Integration** - YouTube, TikTok, Twitter support via yt-dlp
- [ ] **Torrent Support** - Magnet links and .torrent files
- [ ] **Cloud Integration** - Direct upload to Google Drive, OneDrive
- [ ] **Keyboard Shortcuts** - Global hotkeys for quick actions
- [ ] **Plugin System** - Extensible architecture for custom plugins

## License

MIT License
