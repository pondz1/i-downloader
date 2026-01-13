"""
Helper utility functions
"""

import os
import re
from urllib.parse import urlparse, unquote
from typing import Optional

from .constants import SIZE_UNITS


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable string"""
    if size_bytes == 0:
        return "0 B"
    
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(SIZE_UNITS) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {SIZE_UNITS[unit_index]}"


def format_speed(bytes_per_second: float) -> str:
    """Format download speed to human readable string"""
    return f"{format_size(int(bytes_per_second))}/s"


def format_time(seconds: int) -> str:
    """Format seconds to human readable time string"""
    if seconds < 0:
        return "∞"
    
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:02d}"


def extract_filename_from_url(url: str) -> str:
    """Extract filename from URL"""
    parsed = urlparse(url)
    path = unquote(parsed.path)
    filename = os.path.basename(path)
    
    if not filename:
        filename = "download"
    
    # Clean filename
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    return filename


def extract_filename_from_header(content_disposition: str) -> Optional[str]:
    """Extract filename from Content-Disposition header"""
    if not content_disposition:
        return None
    
    # Try to find filename*= (RFC 5987)
    match = re.search(r"filename\*=(?:UTF-8'')?([^;]+)", content_disposition, re.IGNORECASE)
    if match:
        return unquote(match.group(1).strip('"'))
    
    # Try to find filename=
    match = re.search(r'filename[^;=\n]*=(["\']?)([^"\';]+)\1', content_disposition)
    if match:
        return match.group(2).strip()
    
    return None


def get_unique_filename(directory: str, filename: str) -> str:
    """Get a unique filename in the directory by appending number if needed"""
    filepath = os.path.join(directory, filename)
    
    if not os.path.exists(filepath):
        return filename
    
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while os.path.exists(filepath):
        new_filename = f"{name} ({counter}){ext}"
        filepath = os.path.join(directory, new_filename)
        counter += 1
    
    return os.path.basename(filepath)


def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except:
        return False


def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename"""
    # Remove invalid characters for Windows
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove control characters
    filename = ''.join(char for char in filename if ord(char) >= 32)
    
    return filename.strip()
