# i-Downloader

A fast, multi-threaded download manager built with Python and PyQt6.

## Features

- 🚀 **Multi-threaded Downloads** - Split files into segments for faster downloads
- ⏸️ **Pause/Resume** - Resume interrupted downloads
- 📋 **Download Queue** - Manage multiple downloads with priority ordering
- 📊 **Progress Tracking** - Real-time speed and ETA
- 🌙 **Dark Theme** - Modern, eye-friendly interface
- 📑 **Auto-Categorization** - Organize files by type (Videos, Images, Documents, etc.)
- 📋 **Clipboard Monitoring** - Auto-detect URLs and prompt to download
- ⏰ **Scheduler** - Schedule downloads for specific times
- 📦 **Batch Import** - Import multiple URLs at once
- 🔒 **Checksum Verification** - Verify file integrity with MD5/SHA256
- 🔔 **Notifications** - Desktop alerts on completion/failure
- 📜 **Download History** - Search and filter past downloads
- 🔄 **Auto-Retry** - Automatically retry failed downloads
- 🚦 **Bandwidth Limiter** - Control download speeds
- 🌐 **Proxy Support** - HTTP/SOCKS proxy configuration
- 🎬 **Video Downloads** - Download from 100+ sites (YouTube, TikTok, Twitter, etc.) with format selection

## Requirements

- Python 3.11+
- Windows/Linux/macOS

## Installation

```bash
# Install Env
python -m venv .venv

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Usage

1. Click **"+ Add"** to add a new download
2. Paste the URL and choose save location
3. Click **"Download"** to start

## Advanced Features

### 📑 Auto-Categorization
Downloads are automatically organized into categories based on file type:
- **Videos** (mp4, mkv, avi, webm, etc.)
- **Images** (jpg, png, gif, webp, etc.)
- **Audio** (mp3, flac, wav, m4a, etc.)
- **Documents** (pdf, doc, txt, epub, etc.)
- **Archives** (zip, rar, 7z, tar, etc.)
- **Programs** (exe, appimage, dmg, deb, etc.)

Configure category paths in Settings → Categories.

### 📋 Clipboard Monitoring
When enabled, i-Downloader automatically detects URLs copied to your clipboard and prompts you to download. Enable/disable in Settings → General.

### ⏰ Scheduler
Schedule downloads to start at specific times:
1. Add a download normally
2. Right-click the download → "Schedule"
3. Set the date and time
4. The download will start automatically at the scheduled time

### 📦 Batch Import
Import multiple URLs at once:
1. Click **"Batch Import"** in the toolbar
2. Paste URLs (one per line) or load from a text file
3. Configure common settings (save location, category, etc.)
4. Click **"Import"** to add all to the queue

### 🔒 Checksum Verification
Verify downloaded file integrity:
- Supports MD5, SHA1, and SHA256
- View checksums in Download History
- Automatically verifies after download if checksum provided

### 🔔 Notifications
Receive desktop notifications when:
- Downloads complete
- Downloads fail
- Batch operations finish

Configure notification preferences in Settings.

### 📜 Download History
Access complete download history:
- View all past downloads (completed, failed, cancelled)
- Search by filename or URL
- Filter by status
- Open file/folder, retry, or delete entries

### 🔄 Auto-Retry
Failed downloads automatically retry with:
- Exponential backoff (delays increase between retries)
- Configurable max retry count
- Smart segment-level retry for partial failures

### 🚦 Bandwidth Limiter
Control download speeds to preserve bandwidth:
- Set global speed limit in Settings → Network
- Apply to individual downloads in the download context menu

### 🌐 Proxy Support
Route downloads through proxy servers:
- HTTP/HTTPS/SOCKS4/SOCKS5 protocols
- Authentication support (username/password)
- Configure in Settings → Network

### 🎬 Video Downloads
Download videos from 100+ supported sites:
- **Supported Sites**: YouTube, TikTok, Twitter/X, Instagram, Vimeo, Twitch, Facebook, Reddit, and many more
- **Format Selection**: Choose video quality (1080p, 720p, 480p, etc.) and format (MP4, WebM)
- **Audio Only**: Download audio track separately (requires FFmpeg)
- **Playlists**: Download entire playlists with one click
- **Progress Tracking**: Real-time download progress with speed and ETA

**How to Use**:
1. Paste a video URL (e.g., YouTube link)
2. The app will detect it's a video and show "Video detected on [Site Name]"
3. Click "Download" to see format options
4. Select your preferred quality and format
5. For playlists, confirm to download all videos

**FFmpeg Requirement**:
Audio-only downloads require FFmpeg to be installed on your system:
- **Ubuntu/Debian**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

If FFmpeg is not installed, the app will warn you when selecting audio-only formats.

Videos are automatically saved to the "Videos" category.

## Roadmap

### ✅ Completed

Core download management functionality is fully implemented, including:
- Multi-threaded downloads with pause/resume
- Download queue with priority management
- Progress tracking with real-time speed and ETA
- System tray integration
- Settings management
- Clipboard monitoring
- Download categories with auto-organization
- Download scheduler
- Bandwidth limiting
- Batch URL import
- Auto-retry on failure
- Download history with search and filter
- Desktop notifications
- Checksum verification (MD5/SHA256)
- Proxy support (HTTP/HTTPS/SOCKS)
- **Video site integration** - Support for 100+ video sites including YouTube, TikTok, Twitter, Instagram, Vimeo, and more

### 🚀 Planned Features

Future enhancements planned for development:

- [ ] **Torrent Support** - Magnet links and .torrent files with full P2P functionality
- [ ] **Cloud Integration** - Direct upload to Google Drive, OneDrive, Dropbox
- [ ] **Keyboard Shortcuts** - Global hotkeys for quick actions
- [ ] **Plugin System** - Extensible architecture for custom plugins and integrations

## License

MIT License
