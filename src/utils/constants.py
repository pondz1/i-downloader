"""
Application constants and configuration
"""

import os
import uuid
from pathlib import Path

# Application info
APP_NAME = "i-Downloader"
APP_VERSION = "1.0.0"

# Default settings
DEFAULT_DOWNLOAD_DIR = str(Path.home() / "Downloads")
DEFAULT_SEGMENTS = 8
DEFAULT_MAX_CONCURRENT = 3
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_CHUNK_SIZE = 1024 * 64  # 64KB

# Retry settings
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 5.0  # seconds
DEFAULT_RETRY_BACKOFF = 2.0  # multiplier

# Download status
class DownloadStatus:
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# File size units
SIZE_UNITS = ["B", "KB", "MB", "GB", "TB"]

# Database
DB_NAME = "i_downloader.db"
DB_PATH = Path.home() / ".i-downloader" / DB_NAME

# Ensure app directory exists
APP_DATA_DIR = Path.home() / ".i-downloader"
APP_DATA_DIR.mkdir(exist_ok=True)

# User agent for HTTP requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def generate_id() -> str:
    """
    Generate a unique ID for downloads.

    Returns:
        A unique identifier string
    """
    return str(uuid.uuid4())
