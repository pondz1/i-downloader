# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

i-Downloader is a **desktop download manager** built with Python 3.11+ and PyQt6. It features multi-threaded downloads, pause/resume capability, queue management, and a modern dark-themed GUI.

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

No build process is required. The app runs directly from source.

## Architecture

The application uses a **layered architecture** with clear separation between UI, business logic, and data:

```
src/
├── ui/              # PyQt6 GUI components
├── core/            # Download engine and file operations
├── models/          # Data models and database persistence
└── utils/           # Constants and helper functions
```

### Key Architectural Patterns

**Async/Qt Integration**: The app bridges Qt's event loop with asyncio using `AsyncRunner` (main.py:15). This allows blocking download operations to run without freezing the UI. When working with async code from Qt signals, use `asyncio.run_coroutine_threadsafe()`.

**Multi-Segment Downloads**: Files are split into segments (default: 8) that download concurrently via HTTP Range requests. Each segment is handled by a `SegmentDownloader` (src/core/segment.py). After completion, segments are merged into the final file.

**Download Flow**:
1. `DownloadManager.add_download()` - Fetches file info (HEAD request), creates segments
2. `DownloadManager.start_download()` - Creates async task, respects concurrent limit
3. `_download_task()` - Spawns SegmentDownloader instances for each incomplete segment
4. Segments download concurrently, progress tracked via callbacks
5. On completion, `merge_segments()` combines temp files

**State Management**: Downloads transition through states: QUEUED → DOWNLOADING → (PAUSED|COMPLETED|FAILED|CANCELLED). Active downloads are tracked in `active_tasks`, segment downloaders in `segment_downloaders`.

**Persistence**: Downloads are saved to SQLite (src/models/database.py) on:
- Initial creation
- Every ~5% progress (downloader.py:342-343)
- Status changes
- Shutdown/app close

The database is loaded at startup, and incomplete downloads (status=DOWNLOADING) are set to PAUSED.

### Important Classes

- **DownloadManager** (src/core/downloader.py) - Core orchestrator, handles all download operations
- **SegmentDownloader** (src/core/segment.py) - Downloads a single file segment with pause/resume
- **Download** (src/models/download.py) - Data model with properties for progress, is_active, is_complete
- **MainWindow** (src/ui/main_window.py) - Primary UI, bridges Qt signals to async operations

## Configuration

Settings are stored in `~/.i-downloader/settings.json`. Key settings:
- `max_concurrent` - Maximum simultaneous downloads (default: 3)
- `default_segments` - Number of segments per file (default: 8)
- `auto_start` - Automatically start downloads when added
- `close_to_tray` - Minimize to system tray instead of quitting

## Development Notes

- **Platform-specific code**: `os.startfile()` is used for opening files/folders (Windows only). For cross-platform compatibility, use `subprocess` with platform checks.
- **Temp files**: Stored in `~/.i-downloader/temp/` as `{download_id}_segment_{index}.tmp`
- **Speed calculation**: Uses a rolling 3-second window (downloader.py:318-332)
- **Qt threading**: UI updates from async context must use `QTimer.singleShot(0, lambda: ...)` to execute on main thread
- **Icons**: Uses qtawesome for FontAwesome icons. Falls back to Qt standard icons if unavailable.
