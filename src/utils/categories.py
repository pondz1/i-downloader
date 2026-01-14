"""
Download categories - auto-organize files by type
"""

from pathlib import Path
from typing import Optional, Dict
from mimetypes import guess_type


class Category:
    """Download category configuration"""

    def __init__(self, name: str, folder_name: str, extensions: list, icon: str = ""):
        self.name = name
        self.folder_name = folder_name
        self.extensions = extensions
        self.icon = icon


# Default categories
CATEGORIES: Dict[str, Category] = {
    "auto": Category("Auto (Detect from file)", "", [], 'fa5s.magic'),
    "all": Category("All Files", "", [], ""),
    "videos": Category(
        "Videos",
        "Videos",
        ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp'],
        'fa5s.video'
    ),
    "images": Category(
        "Images",
        "Images",
        ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', '.psd', '.raw'],
        'fa5s.image'
    ),
    "audio": Category(
        "Audio",
        "Audio",
        ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus', '.aiff'],
        'fa5s.music'
    ),
    "documents": Category(
        "Documents",
        "Documents",
        ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf', '.odt', '.ods', '.odp'],
        'fa5s.file-alt'
    ),
    "archives": Category(
        "Archives",
        "Archives",
        ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.tar.gz', '.tar.bz2'],
        'fa5s.file-archive'
    ),
    "programs": Category(
        "Programs",
        "Programs",
        ['.exe', '.msi', '.app', '.dmg', '.deb', '.rpm', '.apk', '.appimage', '.flatpak'],
        'fa5s.cog'
    ),
    "torrents": Category(
        "Torrents",
        "Torrents",
        ['.torrent'],
        'fa5s.download'
    ),
}


def get_category_from_filename(filename: str) -> str:
    """
    Determine category from filename extension.

    Args:
        filename: The filename to check

    Returns:
        Category key (e.g., 'videos', 'images', 'all')
    """
    ext = Path(filename).suffix.lower()

    for category_key, category in CATEGORIES.items():
        if category_key == "all":
            continue
        if ext in category.extensions:
            return category_key

    return "all"


def get_category_from_content_type(content_type: str) -> str:
    """
    Determine category from HTTP Content-Type header.

    Args:
        content_type: The content type string (e.g., 'video/mp4')

    Returns:
        Category key (e.g., 'videos', 'images', 'all')
    """
    if not content_type:
        return "all"

    content_type = content_type.lower()

    if content_type.startswith('video/'):
        return "videos"
    elif content_type.startswith('image/'):
        return "images"
    elif content_type.startswith('audio/'):
        return "audio"
    elif content_type.startswith('text/') or 'document' in content_type or 'pdf' in content_type:
        return "documents"
    elif content_type.startswith('application/zip') or 'archive' in content_type or 'compressed' in content_type:
        return "archives"
    elif content_type in ['application/x-bittorrent', 'application/x-torrent']:
        return "torrents"
    elif content_type in ['application/x-msdownload', 'application/x-msdos-program',
                          'application/x-executable', 'application/x-apple-diskimage']:
        return "programs"

    return "all"


def get_category_save_path(base_path: str, category_key: str) -> str:
    """
    Get the save path for a category.

    Args:
        base_path: Base download directory
        category_key: Category key

    Returns:
        Full path to category folder
    """
    if category_key == "all" or category_key not in CATEGORIES:
        return base_path

    category = CATEGORIES[category_key]
    if not category.folder_name:
        return base_path

    category_path = Path(base_path) / category.folder_name
    return str(category_path)


def get_all_categories() -> Dict[str, Category]:
    """Get all available categories"""
    return CATEGORIES


def get_category_name(category_key: str) -> str:
    """Get the display name for a category"""
    if category_key in CATEGORIES:
        return CATEGORIES[category_key].name
    return "All Files"


def get_category_icon(category_key: str) -> str:
    """Get the icon name for a category"""
    if category_key in CATEGORIES:
        return CATEGORIES[category_key].icon
    return ""
