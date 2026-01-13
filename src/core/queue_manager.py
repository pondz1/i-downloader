"""
Download queue manager
"""

from typing import List, Optional, Callable
from ..models.download import Download
from ..utils.constants import DownloadStatus


class QueueManager:
    """Manages download queue and priorities"""
    
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self._queue: List[str] = []  # List of download IDs in order
        self._priorities: dict[str, int] = {}  # download_id -> priority (higher = more important)
    
    def add_to_queue(self, download_id: str, priority: int = 0):
        """Add a download to the queue"""
        if download_id not in self._queue:
            self._queue.append(download_id)
            self._priorities[download_id] = priority
            self._sort_queue()
    
    def remove_from_queue(self, download_id: str):
        """Remove a download from the queue"""
        if download_id in self._queue:
            self._queue.remove(download_id)
        if download_id in self._priorities:
            del self._priorities[download_id]
    
    def set_priority(self, download_id: str, priority: int):
        """Set the priority of a download"""
        if download_id in self._queue:
            self._priorities[download_id] = priority
            self._sort_queue()
    
    def move_up(self, download_id: str):
        """Move a download up in the queue"""
        if download_id in self._queue:
            idx = self._queue.index(download_id)
            if idx > 0:
                self._queue[idx], self._queue[idx - 1] = self._queue[idx - 1], self._queue[idx]
    
    def move_down(self, download_id: str):
        """Move a download down in the queue"""
        if download_id in self._queue:
            idx = self._queue.index(download_id)
            if idx < len(self._queue) - 1:
                self._queue[idx], self._queue[idx + 1] = self._queue[idx + 1], self._queue[idx]
    
    def move_to_top(self, download_id: str):
        """Move a download to the top of the queue"""
        if download_id in self._queue:
            self._queue.remove(download_id)
            self._queue.insert(0, download_id)
    
    def move_to_bottom(self, download_id: str):
        """Move a download to the bottom of the queue"""
        if download_id in self._queue:
            self._queue.remove(download_id)
            self._queue.append(download_id)
    
    def get_next(self) -> Optional[str]:
        """Get the next download ID in the queue"""
        return self._queue[0] if self._queue else None
    
    def get_queue(self) -> List[str]:
        """Get the current queue order"""
        return self._queue.copy()
    
    def get_position(self, download_id: str) -> int:
        """Get the position of a download in the queue (0-indexed)"""
        return self._queue.index(download_id) if download_id in self._queue else -1
    
    def _sort_queue(self):
        """Sort queue by priority (higher first)"""
        self._queue.sort(key=lambda x: self._priorities.get(x, 0), reverse=True)
    
    def clear(self):
        """Clear the queue"""
        self._queue.clear()
        self._priorities.clear()
    
    @property
    def size(self) -> int:
        """Get the queue size"""
        return len(self._queue)
    
    @property
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self._queue) == 0
