"""
Main download manager - orchestrates all downloads
"""

import asyncio
import aiohttp
import os
import ssl
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional, Callable, List
from datetime import datetime

from .segment import SegmentDownloader
from .file_utils import merge_segments, create_segment_files, cleanup_temp_files
from .checksum import ChecksumVerifier
from ..models.download import Download, SegmentInfo
from ..models.database import Database
from ..utils.constants import (
    DEFAULT_SEGMENTS,
    DEFAULT_MAX_CONCURRENT,
    DEFAULT_TIMEOUT,
    USER_AGENT,
    APP_DATA_DIR,
    DownloadStatus,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_RETRY_BACKOFF
)
from ..utils.helpers import (
    extract_filename_from_url, 
    extract_filename_from_header,
    get_unique_filename
)


class DownloadManager:
    """
    Main download manager that handles all download operations.
    Supports multi-threaded downloads, pause/resume, and queue management.
    """
    
    def __init__(
        self,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT,
        default_segments: int = DEFAULT_SEGMENTS,
        progress_callback: Optional[Callable[[Download], None]] = None,
        status_callback: Optional[Callable[[Download], None]] = None,
        rate_limit: Optional[float] = None,  # bytes per second (None = unlimited)
        proxy_url: Optional[str] = None,
        enable_retry: bool = True,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF
    ):
        self.max_concurrent = max_concurrent
        self.default_segments = default_segments
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.rate_limit = rate_limit
        self.proxy_url = proxy_url
        self.enable_retry = enable_retry
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff

        self.downloads: Dict[str, Download] = {}
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.segment_downloaders: Dict[str, List[SegmentDownloader]] = {}

        self.db = Database()
        self.temp_dir = APP_DATA_DIR / "temp"
        self.temp_dir.mkdir(exist_ok=True)

        self._session: Optional[aiohttp.ClientSession] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._running = False
        self._speed_tracker: Dict[str, List[tuple]] = {}  # download_id -> [(time, bytes)]
    
    async def initialize(self):
        """Initialize the download manager"""
        # SECURITY: Explicitly configure SSL/TLS certificate validation
        # This ensures we verify SSL certificates and prevent MITM attacks
        ssl_context = ssl.create_default_context()
        ssl_context.verify_mode = ssl.CERT_REQUIRED

        # Create connector with SSL validation
        connector = aiohttp.TCPConnector(ssl=ssl_context)

        # Create session with proxy if configured
        self._session = aiohttp.ClientSession(
            connector=connector,
            trust_env=True  # Respect system proxy env vars
        )
        self._running = True

        # Load ALL downloads from database (including completed)
        all_downloads = self.db.get_all_downloads()
        for download in all_downloads:
            # Set incomplete downloads to paused
            if download.status == DownloadStatus.DOWNLOADING:
                download.status = DownloadStatus.PAUSED
            self.downloads[download.id] = download
    
    async def shutdown(self):
        """Shutdown the download manager"""
        self._running = False
        
        # Cancel all active downloads
        for download_id in list(self.active_tasks.keys()):
            await self.pause_download(download_id)
        
        # Save all downloads to database
        for download in self.downloads.values():
            self.db.save_download(download)
        
        if self._session:
            await self._session.close()
    
    async def add_download(
        self,
        url: str,
        save_dir: str,
        filename: Optional[str] = None,
        num_segments: Optional[int] = None
    ) -> Download:
        """
        Add a new download.
        
        Args:
            url: Download URL
            save_dir: Directory to save the file
            filename: Optional filename (auto-detected if not provided)
            num_segments: Number of segments to use
            
        Returns:
            Download object
        """
        # Get file info from server
        file_info = await self._get_file_info(url)
        
        # Determine filename
        if not filename:
            filename = file_info.get('filename') or extract_filename_from_url(url)
        
        # Ensure unique filename
        filename = get_unique_filename(save_dir, filename)
        
        # Create download object
        download = Download(
            url=url,
            filename=filename,
            save_path=os.path.join(save_dir, filename),
            total_size=file_info.get('size', 0),
            num_segments=num_segments or self.default_segments,
            supports_resume=file_info.get('supports_resume', False),
            content_type=file_info.get('content_type', '')
        )
        
        # If server doesn't support resume or file is small, use single segment
        if not download.supports_resume or download.total_size < 1024 * 1024:  # < 1MB
            download.num_segments = 1
        
        # Create segments
        download.segments = self._create_segments(download)
        
        # Save to database and memory
        self.downloads[download.id] = download
        self.db.save_download(download)
        
        # Notify status change
        self._notify_status(download)
        
        return download
    
    async def start_download(self, download_id: str) -> bool:
        """Start or resume a download"""
        download = self.downloads.get(download_id)
        if not download:
            return False
        
        if download.status == DownloadStatus.DOWNLOADING:
            return True  # Already downloading
        
        # Check concurrent limit
        active_count = sum(1 for d in self.downloads.values() if d.is_active)
        if active_count >= self.max_concurrent:
            download.status = DownloadStatus.QUEUED
            self._notify_status(download)
            return True
        
        # Start download task
        download.status = DownloadStatus.DOWNLOADING
        self._notify_status(download)
        
        task = asyncio.create_task(self._download_task(download))
        self.active_tasks[download_id] = task
        
        return True
    
    async def pause_download(self, download_id: str) -> bool:
        """Pause a download"""
        download = self.downloads.get(download_id)
        if not download or not download.is_active:
            return False
        
        # Stop segment downloaders
        if download_id in self.segment_downloaders:
            for downloader in self.segment_downloaders[download_id]:
                downloader.pause()
        
        # Cancel task
        if download_id in self.active_tasks:
            self.active_tasks[download_id].cancel()
            try:
                await self.active_tasks[download_id]
            except asyncio.CancelledError:
                pass
            del self.active_tasks[download_id]
        
        download.status = DownloadStatus.PAUSED
        self.db.save_download(download)
        self._notify_status(download)
        
        # Start next queued download
        await self._start_next_queued()
        
        return True
    
    async def cancel_download(self, download_id: str) -> bool:
        """Cancel and remove a download"""
        download = self.downloads.get(download_id)
        if not download:
            return False
        
        # Stop if active
        if download.is_active:
            if download_id in self.segment_downloaders:
                for downloader in self.segment_downloaders[download_id]:
                    downloader.cancel()
            
            if download_id in self.active_tasks:
                self.active_tasks[download_id].cancel()
                try:
                    await self.active_tasks[download_id]
                except asyncio.CancelledError:
                    pass
                del self.active_tasks[download_id]
        
        download.status = DownloadStatus.CANCELLED
        
        # Cleanup temp files
        cleanup_temp_files(download_id, self.temp_dir)
        
        # Remove from memory and database
        del self.downloads[download_id]
        self.db.delete_download(download_id)
        
        # Start next queued download
        await self._start_next_queued()
        
        return True
    
    async def _download_task(self, download: Download):
        """Main download task for a single download"""
        try:
            self._speed_tracker[download.id] = []

            # Create segment temp files if needed
            for segment in download.segments:
                if not segment.temp_file:
                    # SECURITY: Use tempfile.mkstemp() for atomic, secure file creation
                    # This prevents TOCTOU (Time-of-Check-Time-of-Use) race conditions
                    # and symlink attacks
                    try:
                        fd, temp_path = tempfile.mkstemp(
                            suffix=f"_seg{segment.index}.tmp",
                            dir=self.temp_dir,
                            prefix=f"{download.id}_"
                        )
                        os.close(fd)  # Close the file descriptor, we'll reopen later
                        segment.temp_file = temp_path
                    except (OSError, IOError) as e:
                        download.status = DownloadStatus.FAILED
                        download.error_message = f"Failed to create temp file: {str(e)}"
                        self.db.save_download(download)
                        self._notify_status(download)
                        return

                # Ensure file exists (might have been cleaned up)
                if not os.path.exists(segment.temp_file):
                    Path(segment.temp_file).touch()

            # Create segment downloaders
            def progress_callback(segment_index: int, bytes_downloaded: int):
                self._on_segment_progress(download, segment_index, bytes_downloaded)

            downloaders = [
                SegmentDownloader(
                    url=download.url,
                    segment=segment,
                    session=self._session,
                    progress_callback=progress_callback,
                    rate_limit=self.rate_limit,
                    proxy_url=self.proxy_url
                )
                for segment in download.segments
                if not segment.completed
            ]

            self.segment_downloaders[download.id] = downloaders

            # Download all segments concurrently
            tasks = [asyncio.create_task(d.download()) for d in downloaders]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check if all segments completed
            all_completed = all(s.completed for s in download.segments)

            if all_completed:
                # Merge segments into final file
                segment_files = [s.temp_file for s in sorted(download.segments, key=lambda x: x.index)]
                await merge_segments(segment_files, download.save_path)

                # Verify checksum if expected checksum is set
                if download.expected_checksum:
                    try:
                        verified = ChecksumVerifier.verify_checksum(
                            download.save_path,
                            download.expected_checksum,
                            download.checksum_algorithm or 'sha256'
                        )

                        if verified:
                            # Calculate and store the actual checksum
                            download.checksum = ChecksumVerifier.calculate_file_hash(
                                download.save_path,
                                download.checksum_algorithm or 'sha256'
                            )
                            download.checksum_algorithm = download.checksum_algorithm or 'sha256'
                            download.status = DownloadStatus.COMPLETED
                            download.completed_at = datetime.now()
                            download.downloaded_size = download.total_size
                        else:
                            download.status = DownloadStatus.FAILED
                            download.error_message = f"Checksum verification failed. Expected {download.checksum_algorithm.upper()}: {download.expected_checksum[:12]}..."
                            # Don't delete the file so user can manually verify
                    except Exception as e:
                        download.status = DownloadStatus.FAILED
                        download.error_message = f"Checksum verification error: {str(e)}"
                else:
                    # No checksum verification required
                    download.status = DownloadStatus.COMPLETED
                    download.completed_at = datetime.now()
                    download.downloaded_size = download.total_size
            else:
                # Some segments failed - check if we should retry
                if self.enable_retry and download.retry_count < self.max_retries:
                    download.retry_count += 1
                    download.status = DownloadStatus.PAUSED  # Temporarily pause for retry
                    download.error_message = f"Download failed. Retry {download.retry_count}/{self.max_retries} in {self._calculate_retry_delay(download.retry_count):.1f}s..."
                    self.db.save_download(download)
                    self._notify_status(download)

                    # Calculate delay with exponential backoff
                    delay = self._calculate_retry_delay(download.retry_count)
                    await asyncio.sleep(delay)

                    # Retry download
                    await self.start_download(download.id)
                    return
                else:
                    download.status = DownloadStatus.FAILED
                    if download.retry_count > 0:
                        download.error_message = f"Download failed after {download.retry_count} retry attempts"
                    else:
                        download.error_message = "One or more segments failed to download"

            # Cleanup
            if download.id in self.segment_downloaders:
                del self.segment_downloaders[download.id]
            if download.id in self._speed_tracker:
                del self._speed_tracker[download.id]

            self.db.save_download(download)
            self._notify_status(download)

            # Start next queued download
            await self._start_next_queued()

        except asyncio.CancelledError:
            # Download was paused or cancelled
            self.db.save_download(download)
            raise
        except Exception as e:
            # Check if we should retry on exception
            if self.enable_retry and download.retry_count < self.max_retries:
                download.retry_count += 1
                download.status = DownloadStatus.PAUSED
                download.error_message = f"Error: {str(e)}. Retry {download.retry_count}/{self.max_retries} in {self._calculate_retry_delay(download.retry_count):.1f}s..."
                self.db.save_download(download)
                self._notify_status(download)

                # Calculate delay with exponential backoff
                delay = self._calculate_retry_delay(download.retry_count)
                await asyncio.sleep(delay)

                # Retry download
                await self.start_download(download.id)
                return
            else:
                download.status = DownloadStatus.FAILED
                download.error_message = str(e)
                self.db.save_download(download)
                self._notify_status(download)

            await self._start_next_queued()
        finally:
            if download.id in self.active_tasks:
                del self.active_tasks[download.id]

    def _calculate_retry_delay(self, retry_count: int) -> float:
        """
        Calculate retry delay with exponential backoff.

        Args:
            retry_count: Current retry attempt number (1-based)

        Returns:
            Delay in seconds
        """
        return self.retry_delay * (self.retry_backoff ** (retry_count - 1))
    
    def _on_segment_progress(self, download: Download, segment_index: int, bytes_downloaded: int):
        """Called when segment downloads some bytes"""
        download.downloaded_size += bytes_downloaded
        
        # Track speed
        now = time.time()
        tracker = self._speed_tracker.get(download.id, [])
        tracker.append((now, bytes_downloaded))
        
        # Keep only last 3 seconds for speed calculation
        tracker = [(t, b) for t, b in tracker if now - t < 3]
        self._speed_tracker[download.id] = tracker
        
        # Calculate speed
        if len(tracker) >= 2:
            total_bytes = sum(b for _, b in tracker)
            time_span = tracker[-1][0] - tracker[0][0]
            if time_span > 0:
                download.speed = total_bytes / time_span
            
            # Calculate ETA
            if download.speed > 0:
                remaining = download.total_size - download.downloaded_size
                download.eta = int(remaining / download.speed)
        
        # Notify progress
        self._notify_progress(download)
        
        # Save periodically (every 5%)
        if download.progress % 5 < 0.1:
            self.db.save_download(download)
    
    async def _get_file_info(self, url: str) -> dict:
        """
        Get file information from server.

        SECURITY: Limited redirects to prevent:
        - Infinite redirect loops (DoS)
        - SSRF (Server-Side Request Forgery)
        - Redirect-based data exfiltration
        """
        try:
            headers = {'User-Agent': USER_AGENT}
            timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)

            # SECURITY: Limit redirects to 10 to prevent redirect-based attacks
            async with self._session.head(
                url,
                headers=headers,
                timeout=timeout,
                allow_redirects=True,
                max_redirects=10,  # Prevent infinite redirects and SSRF
                proxy=self.proxy_url
            ) as response:
                content_length = response.headers.get('Content-Length')
                content_disposition = response.headers.get('Content-Disposition')
                accept_ranges = response.headers.get('Accept-Ranges')
                content_type = response.headers.get('Content-Type', '')

                return {
                    'size': int(content_length) if content_length else 0,
                    'filename': extract_filename_from_header(content_disposition),
                    'supports_resume': accept_ranges == 'bytes',
                    'content_type': content_type
                }
        except Exception as e:
            print(f"Error getting file info: {e}")
            return {}
    
    def _create_segments(self, download: Download) -> List[SegmentInfo]:
        """Create download segments"""
        if download.total_size == 0 or download.num_segments == 1:
            return [SegmentInfo(
                index=0,
                start_byte=0,
                end_byte=download.total_size - 1 if download.total_size > 0 else 0
            )]
        
        segment_size = download.total_size // download.num_segments
        segments = []
        
        for i in range(download.num_segments):
            start = i * segment_size
            end = (i + 1) * segment_size - 1 if i < download.num_segments - 1 else download.total_size - 1
            
            segments.append(SegmentInfo(
                index=i,
                start_byte=start,
                end_byte=end
            ))
        
        return segments
    
    async def _start_next_queued(self):
        """Start the next queued download if possible"""
        active_count = sum(1 for d in self.downloads.values() if d.is_active)
        
        if active_count >= self.max_concurrent:
            return
        
        for download in self.downloads.values():
            if download.status == DownloadStatus.QUEUED:
                await self.start_download(download.id)
                break
    
    def _notify_progress(self, download: Download):
        """Notify progress callback"""
        if self.progress_callback:
            self.progress_callback(download)
    
    def _notify_status(self, download: Download):
        """Notify status callback"""
        if self.status_callback:
            self.status_callback(download)
    
    def get_download(self, download_id: str) -> Optional[Download]:
        """Get a download by ID"""
        return self.downloads.get(download_id)
    
    def get_all_downloads(self) -> List[Download]:
        """Get all downloads"""
        return list(self.downloads.values())
