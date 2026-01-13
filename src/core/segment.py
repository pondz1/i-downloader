"""
Segment downloader - handles downloading a single segment of a file
"""

import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import Callable, Optional

from ..utils.constants import DEFAULT_CHUNK_SIZE, DEFAULT_TIMEOUT, USER_AGENT
from ..models.download import SegmentInfo


class SegmentDownloader:
    """Downloads a single segment of a file using HTTP Range requests"""
    
    def __init__(
        self,
        url: str,
        segment: SegmentInfo,
        session: aiohttp.ClientSession,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE
    ):
        self.url = url
        self.segment = segment
        self.session = session
        self.progress_callback = progress_callback
        self.chunk_size = chunk_size
        self._cancelled = False
        self._paused = False
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Not paused initially
    
    async def download(self) -> bool:
        """
        Download the segment.
        Returns True if completed successfully.
        """
        try:
            # Calculate range to download
            start = self.segment.start_byte + self.segment.downloaded
            end = self.segment.end_byte
            
            if start > end:
                # Already completed
                self.segment.completed = True
                return True
            
            headers = {
                'User-Agent': USER_AGENT,
                'Range': f'bytes={start}-{end}'
            }
            
            timeout = aiohttp.ClientTimeout(total=None, connect=DEFAULT_TIMEOUT)
            
            async with self.session.get(
                self.url,
                headers=headers,
                timeout=timeout
            ) as response:
                if response.status not in (200, 206):
                    return False
                
                # Open file in append mode
                async with aiofiles.open(self.segment.temp_file, 'ab') as f:
                    async for chunk in response.content.iter_chunked(self.chunk_size):
                        # Check for pause
                        await self._pause_event.wait()
                        
                        # Check for cancellation
                        if self._cancelled:
                            return False
                        
                        await f.write(chunk)
                        self.segment.downloaded += len(chunk)
                        
                        if self.progress_callback:
                            self.progress_callback(self.segment.index, len(chunk))
            
            self.segment.completed = True
            return True
            
        except asyncio.CancelledError:
            return False
        except Exception as e:
            print(f"Segment {self.segment.index} error: {e}")
            return False
    
    def pause(self):
        """Pause the download"""
        self._paused = True
        self._pause_event.clear()
    
    def resume(self):
        """Resume the download"""
        self._paused = False
        self._pause_event.set()
    
    def cancel(self):
        """Cancel the download"""
        self._cancelled = True
        self._pause_event.set()  # Unblock if paused
    
    @property
    def is_paused(self) -> bool:
        return self._paused
