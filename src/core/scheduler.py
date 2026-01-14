"""
Download scheduler - schedule downloads for specific times
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable, List
from ..models.download import Download


class ScheduledDownload:
    """Represents a scheduled download"""

    def __init__(
        self,
        download_id: str,
        scheduled_time: datetime,
        url: str,
        save_dir: str,
        num_segments: int,
        category: str = "all"
    ):
        self.download_id = download_id
        self.scheduled_time = scheduled_time
        self.url = url
        self.save_dir = save_dir
        self.num_segments = num_segments
        self.category = category
        self.completed = False


class DownloadScheduler:
    """Scheduler for delayed downloads"""

    def __init__(self, start_callback: Callable):
        """
        Initialize the scheduler.

        Args:
            start_callback: Function to call when a scheduled download should start
                           Callback signature: (url, save_dir, num_segments, category) -> None
        """
        self.start_callback = start_callback
        self.scheduled: Dict[str, ScheduledDownload] = {}
        self._running = False
        self._check_interval = 5  # Check every 5 seconds
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the scheduler"""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())

    async def stop(self):
        """Stop the scheduler"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self._running:
            try:
                await self._check_and_start_due()
                await asyncio.sleep(self._check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Scheduler error: {e}")
                await asyncio.sleep(self._check_interval)

    async def _check_and_start_due(self):
        """Check for due downloads and start them"""
        now = datetime.now()

        # Find due downloads
        due_downloads = [
            (download_id, scheduled)
            for download_id, scheduled in self.scheduled.items()
            if not scheduled.completed and scheduled.scheduled_time <= now
        ]

        # Start due downloads
        for download_id, scheduled in due_downloads:
            try:
                # Call the start callback
                self.start_callback(
                    scheduled.url,
                    scheduled.save_dir,
                    scheduled.num_segments,
                    scheduled.category
                )
                scheduled.completed = True

                # Remove from scheduled after a short delay
                asyncio.create_task(self._remove_scheduled(download_id))
            except Exception as e:
                print(f"Failed to start scheduled download {download_id}: {e}")

    async def _remove_scheduled(self, download_id: str, delay: float = 5.0):
        """Remove a scheduled download after a delay"""
        await asyncio.sleep(delay)
        if download_id in self.scheduled:
            del self.scheduled[download_id]

    def schedule_download(
        self,
        url: str,
        save_dir: str,
        num_segments: int,
        scheduled_time: datetime,
        category: str = "all"
    ) -> str:
        """
        Schedule a new download.

        Args:
            url: Download URL
            save_dir: Save directory
            num_segments: Number of segments
            scheduled_time: When to start the download
            category: Download category

        Returns:
            Scheduled download ID
        """
        import uuid
        download_id = str(uuid.uuid4())

        scheduled = ScheduledDownload(
            download_id=download_id,
            scheduled_time=scheduled_time,
            url=url,
            save_dir=save_dir,
            num_segments=num_segments,
            category=category
        )

        self.scheduled[download_id] = scheduled
        return download_id

    def cancel_scheduled(self, download_id: str) -> bool:
        """Cancel a scheduled download"""
        if download_id in self.scheduled:
            del self.scheduled[download_id]
            return True
        return False

    def get_scheduled_downloads(self) -> List[ScheduledDownload]:
        """Get all scheduled downloads"""
        return list(self.scheduled.values())

    def get_scheduled_download(self, download_id: str) -> Optional[ScheduledDownload]:
        """Get a specific scheduled download"""
        return self.scheduled.get(download_id)

    def get_next_due_time(self) -> Optional[datetime]:
        """Get the time of the next due download"""
        if not self.scheduled:
            return None

        incomplete = [s for s in self.scheduled.values() if not s.completed]
        if not incomplete:
            return None

        return min(s.scheduled_time for s in incomplete)
