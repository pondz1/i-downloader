"""
Video site URL detection and utilities
"""

import re
from urllib.parse import urlparse


# Common video site URL patterns
VIDEO_SITE_PATTERNS = {
    'YouTube': [
        r'youtube\.com/watch',
        r'youtu\.be/',
        r'youtube\.com/shorts/',
        r'youtube\.com/embed/',
    ],
    'TikTok': [
        r'tiktok\.com/@',
        r'vm\.tiktok\.com',
        r'vt\.tiktok\.com',
    ],
    'Twitter/X': [
        r'twitter\.com/.*/status/',
        r'x\.com/.*/status/',
    ],
    'Instagram': [
        r'instagram\.com/p/',
        r'instagram\.com/reel/',
        r'instagram\.com/tv/',
    ],
    'Vimeo': [
        r'vimeo\.com/\d+',
    ],
    'Twitch': [
        r'twitch\.tv/videos/',
        r'twitch\.tv/.*?/video/',
    ],
    'Facebook': [
        r'facebook\.com/.*/videos/',
        r'fb\.watch/',
    ],
    'Reddit': [
        r'reddit\.com/r/.*?/comments/',
    ],
    'Dailymotion': [
        r'dailymotion\.com/video/',
    ],
}


def is_video_url(url: str) -> bool:
    """
    Check if URL is from a known video site.

    This is a quick check using URL patterns. For comprehensive detection,
    yt-dlp should be used as it supports 100+ sites.

    Args:
        url: URL to check

    Returns:
        True if URL matches a known video site pattern
    """
    if not url:
        return False

    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return False

        domain = parsed.netloc.lower()

        # Check against known patterns
        for site_name, patterns in VIDEO_SITE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return True

        # Additional check: if it's a well-known domain but we don't have a pattern
        # Let yt-dlp determine if it can extract it
        return _might_be_video(url)

    except Exception:
        return False


def _might_be_video(url: str) -> bool:
    """
    Check if URL might be a video based on heuristics.
    This catches video URLs that don't match our known patterns.

    Args:
        url: URL to check

    Returns:
        True if URL might be video content
    """
    try:
        parsed = urlparse(url)

        # Common video file extensions
        video_extensions = ('.mp4', '.webm', '.mkv', '.avi', '.mov', '.flv', '.wmv')
        if parsed.path.lower().endswith(video_extensions):
            return True

        # Known video hosting domains (even without specific patterns)
        known_video_domains = [
            'youtu.be', 'youtube.com', 'youtube-nocookie.com',
            'tiktok.com', 'vm.tiktok.com',
            'twitter.com', 'x.com', 't.co',
            'instagram.com',
            'vimeo.com',
            'twitch.tv', 'clips.twitch.tv',
            'facebook.com', 'fb.watch',
            'dailymotion.com',
            'vid.me', 'vine.co',  # defunct but might have archived links
            'streamable.com',
            'gfycat.com',
            'imgur.com',  # some videos
            'reddit.com', 'redd.it',
            'soundcloud.com',  # audio but often grouped with videos
            'mixcloud.com',
            'bandcamp.com',
        ]

        domain = parsed.netloc.lower()
        for known_domain in known_video_domains:
            if known_domain in domain:
                return True

        return False

    except Exception:
        return False


def get_video_site_name(url: str) -> str:
    """
    Get the name of the video site for a URL.

    Args:
        url: Video URL

    Returns:
        Site name (e.g., "YouTube", "TikTok") or "Unknown"
    """
    if not url:
        return "Unknown"

    try:
        for site_name, patterns in VIDEO_SITE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return site_name

        # Check domain-based detection
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        domain_to_name = {
            'youtu.be': 'YouTube',
            'youtube.com': 'YouTube',
            'tiktok.com': 'TikTok',
            'vm.tiktok.com': 'TikTok',
            'twitter.com': 'Twitter',
            'x.com': 'X',
            'instagram.com': 'Instagram',
            'vimeo.com': 'Vimeo',
            'twitch.tv': 'Twitch',
            'facebook.com': 'Facebook',
            'fb.watch': 'Facebook',
            'reddit.com': 'Reddit',
            'dailymotion.com': 'Dailymotion',
        }

        for known_domain, name in domain_to_name.items():
            if known_domain in domain:
                return name

        return "Unknown"

    except Exception:
        return "Unknown"


def is_playlist_url(url: str) -> bool:
    """
    Check if URL appears to be a playlist.

    Note: This is a basic heuristic. For accurate detection,
    yt-dlp should be used to extract playlist info.

    Args:
        url: URL to check

    Returns:
        True if URL appears to be a playlist
    """
    if not url:
        return False

    playlist_indicators = [
        'playlist',
        'list=',
        '/album/',
        '/set/',
        '/collection/',
    ]

    url_lower = url.lower()
    return any(indicator in url_lower for indicator in playlist_indicators)


def extract_video_id(url: str) -> str | None:
    """
    Extract video ID from common video site URLs.

    Args:
        url: Video URL

    Returns:
        Video ID or None if not found
    """
    if not url:
        return None

    try:
        # YouTube
        if 'youtube.com' in url or 'youtu.be' in url:
            # youtu.be/VIDEO_ID
            match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url)
            if match:
                return match.group(1)

            # youtube.com/watch?v=VIDEO_ID
            match = re.search(r'[?&]v=([a-zA-Z0-9_-]+)', url)
            if match:
                return match.group(1)

            # youtube.com/shorts/VIDEO_ID
            match = re.search(r'shorts/([a-zA-Z0-9_-]+)', url)
            if match:
                return match.group(1)

        # TikTok
        if 'tiktok.com' in url:
            # Try to extract video ID from path
            match = re.search(r'/video/(\d+)', url)
            if match:
                return match.group(1)

            # Alternative pattern
            match = re.search(r'/v/(\d+)', url)
            if match:
                return match.group(1)

        # Vimeo
        if 'vimeo.com' in url:
            match = re.search(r'vimeo\.com/(\d+)', url)
            if match:
                return match.group(1)

        # Twitter/X
        if 'twitter.com' in url or 'x.com' in url:
            match = re.search(r'/status/(\d+)', url)
            if match:
                return match.group(1)

        return None

    except Exception:
        return None
