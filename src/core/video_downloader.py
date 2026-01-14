"""
Video downloader using yt-dlp
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Callable, Optional, Any

try:
    import yt_dlp
    HAS_YTDLP = True
except ImportError:
    HAS_YTDLP = False


logger = logging.getLogger(__name__)


class VideoDownloader:
    """
    Video downloader using yt-dlp library.

    Handles video info extraction and downloading with progress tracking.
    Supports all sites that yt-dlp supports (100+ sites).
    """

    def __init__(self):
        """Initialize video downloader"""
        if not HAS_YTDLP:
            raise RuntimeError("yt-dlp is not installed. Install it with: pip install yt-dlp")

    async def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Extract video information from URL.

        Args:
            url: Video URL

        Returns:
            Dict containing:
                - title: Video title
                - thumbnail: Thumbnail URL
                - duration: Duration in seconds
                - formats: List of available formats
                - is_playlist: Boolean indicating if URL is a playlist
                - playlist_count: Number of videos in playlist (if applicable)
                - uploader: Channel/uploader name
                - upload_date: Upload date
                - description: Video description
                - view_count: View count

        Raises:
            Exception: If URL is invalid or video not found
        """
        def _extract_info():
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,  # Get full format info
                'ignoreerrors': False,  # Raise errors for invalid URLs
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)

                    # Check if it's a playlist
                    if 'entries' in info:
                        # It's a playlist
                        return {
                            'title': info.get('title', 'Playlist'),
                            'thumbnail': info.get('thumbnail', ''),
                            'duration': 0,  # Playlists don't have single duration
                            'formats': [],  # Formats fetched per video
                            'is_playlist': True,
                            'playlist_count': len(info.get('entries', [])),
                            'uploader': info.get('uploader', 'Unknown'),
                            'upload_date': info.get('upload_date', ''),
                            'description': info.get('description', ''),
                            'view_count': info.get('view_count', 0),
                            'entries': info.get('entries', []),
                        }
                    else:
                        # Single video
                        formats = self._parse_formats(info.get('formats', []))

                        return {
                            'title': info.get('title', 'Unknown'),
                            'thumbnail': info.get('thumbnail', ''),
                            'duration': info.get('duration', 0),
                            'formats': formats,
                            'is_playlist': False,
                            'playlist_count': 0,
                            'uploader': info.get('uploader', 'Unknown'),
                            'upload_date': info.get('upload_date', ''),
                            'description': info.get('description', ''),
                            'view_count': info.get('view_count', 0),
                            'webpage_url': info.get('webpage_url', url),
                            'video_id': info.get('id', ''),
                        }

                except Exception as e:
                    logger.error(f"Error extracting video info: {e}")
                    raise

        # Run yt-dlp in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _extract_info)

    def _parse_formats(self, formats: List[Dict]) -> List[Dict]:
        """
        Parse and format video formats for UI display.

        Args:
            formats: Raw formats from yt-dlp

        Returns:
            List of formatted format dictionaries
        """
        parsed = []
        seen = set()  # Avoid duplicate formats

        for fmt in formats:
            # Skip formats without video (audio-only is handled separately)
            if fmt.get('vcodec') == 'none':
                continue

            format_id = fmt.get('format_id', '')
            if format_id in seen:
                continue

            seen.add(format_id)

            # Extract format info
            height = fmt.get('height', 0)
            width = fmt.get('width', 0)
            fps = fmt.get('fps', 0)
            filesize = fmt.get('filesize') or fmt.get('filesize_approx', 0)
            ext = fmt.get('ext', 'mp4')
            vcodec = fmt.get('vcodec', 'unknown')
            acodec = fmt.get('acodec', 'unknown')

            # Create quality label
            if height:
                quality = f"{height}p"
                if fps:
                    quality += f"{fps}"
            else:
                quality = "Unknown"

            parsed.append({
                'format_id': format_id,
                'quality': quality,
                'height': height,
                'width': width,
                'fps': fps,
                'filesize': filesize,
                'ext': ext,
                'vcodec': vcodec,
                'acodec': acodec,
                'note': fmt.get('format_note', ''),
            })

        # Sort by quality (height) descending
        parsed.sort(key=lambda x: (x['height'], x['fps']), reverse=True)

        return parsed

    async def download_video(
        self,
        url: str,
        save_path: str,
        format_id: str,
        progress_callback: Optional[Callable[[float, int, int, float], None]] = None,
        start_fresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Download video with progress tracking.

        Args:
            url: Video URL
            save_path: Directory to save video
            format_id: Format ID from get_video_info()
            progress_callback: Callback function(progress, downloaded_bytes, total_bytes, speed)
            start_fresh: If True, download from scratch even if partial file exists

        Returns:
            Dict containing:
                - success: Boolean
                - filepath: Path to downloaded file
                - filesize: Size of downloaded file
                - error: Error message if failed

        Raises:
            Exception: If download fails
        """
        def _download():
            Path(save_path).mkdir(parents=True, exist_ok=True)

            # Progress hook variables
            progress_data = {'downloaded': 0, 'total': 0}

            def progress_hook(d):
                """Internal yt-dlp progress hook"""
                if d['status'] == 'downloading':
                    downloaded = d.get('downloaded_bytes', 0)
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)

                    progress_data['downloaded'] = downloaded
                    progress_data['total'] = total

                    if total > 0:
                        progress = (downloaded / total) * 100
                        speed = d.get('speed', 0)

                        if progress_callback:
                            # Call callback on main thread
                            try:
                                progress_callback(progress, downloaded, total, speed)
                            except Exception as e:
                                logger.error(f"Error in progress callback: {e}")

                elif d['status'] == 'finished':
                    logger.info(f"Download finished: {d.get('filename')}")

            # Configure yt-dlp options
            ydl_opts = {
                'format': format_id,
                'outtmpl': str(Path(save_path) / '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': False,
                'overwrites': True,  # Overwrite if file exists
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=True)
                    filepath = ydl.prepare_filename(info)

                    return {
                        'success': True,
                        'filepath': filepath,
                        'filesize': progress_data.get('total', 0),
                        'error': None,
                    }

                except Exception as e:
                    logger.error(f"Error downloading video: {e}")
                    return {
                        'success': False,
                        'filepath': None,
                        'filesize': 0,
                        'error': str(e),
                    }

        # Run yt-dlp in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _download)

    async def get_playlist_videos(self, url: str) -> List[Dict[str, Any]]:
        """
        Get list of videos in a playlist.

        Args:
            url: Playlist URL

        Returns:
            List of video info dicts, each containing:
                - title: Video title
                - url: Video URL
                - duration: Duration in seconds
                - thumbnail: Thumbnail URL
                - video_id: Video ID

        Raises:
            Exception: If playlist is invalid or not found
        """
        def _extract_playlist():
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # Faster, don't extract full info for each video
                'ignoreerrors': True,  # Skip unavailable videos
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)

                    if 'entries' not in info:
                        raise Exception("URL is not a playlist")

                    videos = []
                    for entry in info.get('entries', []):
                        if entry is None:
                            continue

                        videos.append({
                            'title': entry.get('title', 'Unknown'),
                            'url': entry.get('url', entry.get('webpage_url', '')),
                            'duration': entry.get('duration', 0),
                            'thumbnail': entry.get('thumbnail', ''),
                            'video_id': entry.get('id', ''),
                        })

                    return videos

                except Exception as e:
                    logger.error(f"Error extracting playlist: {e}")
                    raise

        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _extract_playlist)

    async def get_audio_only_format(self, url: str) -> str:
        """
        Get the best audio-only format ID for a video.

        Args:
            url: Video URL

        Returns:
            Format ID for best audio quality
        """
        def _get_audio_format():
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'format': 'bestaudio/best',  # Select best audio
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                    # Return format ID of best audio
                    return info.get('format_id', 'bestaudio')
                except Exception:
                    return 'bestaudio'

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get_audio_format)


# Convenience functions for quick access

async def get_video_info_quick(url: str) -> Dict[str, Any]:
    """Quick wrapper for get_video_info"""
    downloader = VideoDownloader()
    return await downloader.get_video_info(url)


async def download_video_quick(
    url: str,
    save_path: str,
    format_id: str,
    progress_callback: Optional[Callable] = None,
) -> Dict[str, Any]:
    """Quick wrapper for download_video"""
    downloader = VideoDownloader()
    return await downloader.download_video(url, save_path, format_id, progress_callback)
