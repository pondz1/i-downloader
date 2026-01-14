"""
Download data model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import uuid

from ..utils.constants import DownloadStatus


@dataclass
class SegmentInfo:
    """Information about a download segment"""
    index: int
    start_byte: int
    end_byte: int
    downloaded: int = 0
    completed: bool = False
    temp_file: str = ""


@dataclass
class Download:
    """Download item data model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    url: str = ""
    filename: str = ""
    save_path: str = ""
    total_size: int = 0
    downloaded_size: int = 0
    status: str = DownloadStatus.QUEUED
    segments: List[SegmentInfo] = field(default_factory=list)
    num_segments: int = 8
    speed: float = 0.0  # bytes per second
    eta: int = -1  # seconds remaining
    error_message: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    supports_resume: bool = False
    content_type: str = ""
    retry_count: int = 0  # Number of retry attempts
    checksum: str = ""  # Calculated checksum after download
    checksum_algorithm: str = ""  # Algorithm used (md5, sha1, sha256)
    expected_checksum: str = ""  # User-provided checksum for verification
    
    @property
    def progress(self) -> float:
        """Calculate download progress as percentage"""
        if self.total_size == 0:
            return 0.0
        return (self.downloaded_size / self.total_size) * 100
    
    @property
    def is_active(self) -> bool:
        """Check if download is currently active"""
        return self.status == DownloadStatus.DOWNLOADING
    
    @property
    def is_complete(self) -> bool:
        """Check if download is completed"""
        return self.status == DownloadStatus.COMPLETED
    
    @property
    def is_paused(self) -> bool:
        """Check if download is paused"""
        return self.status == DownloadStatus.PAUSED
    
    @property
    def can_resume(self) -> bool:
        """Check if download can be resumed"""
        return self.status in (DownloadStatus.PAUSED, DownloadStatus.FAILED) and self.supports_resume
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'url': self.url,
            'filename': self.filename,
            'save_path': self.save_path,
            'total_size': self.total_size,
            'downloaded_size': self.downloaded_size,
            'status': self.status,
            'num_segments': self.num_segments,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'supports_resume': self.supports_resume,
            'content_type': self.content_type,
            'retry_count': self.retry_count,
            'checksum': self.checksum,
            'checksum_algorithm': self.checksum_algorithm,
            'expected_checksum': self.expected_checksum,
            'segments': [
                {
                    'index': s.index,
                    'start_byte': s.start_byte,
                    'end_byte': s.end_byte,
                    'downloaded': s.downloaded,
                    'completed': s.completed,
                    'temp_file': s.temp_file
                }
                for s in self.segments
            ]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Download':
        """Create Download from dictionary"""
        segments = [
            SegmentInfo(
                index=s['index'],
                start_byte=s['start_byte'],
                end_byte=s['end_byte'],
                downloaded=s['downloaded'],
                completed=s['completed'],
                temp_file=s['temp_file']
            )
            for s in data.get('segments', [])
        ]

        return cls(
            id=data['id'],
            url=data['url'],
            filename=data['filename'],
            save_path=data['save_path'],
            total_size=data['total_size'],
            downloaded_size=data['downloaded_size'],
            status=data['status'],
            segments=segments,
            num_segments=data.get('num_segments', 8),
            error_message=data.get('error_message', ''),
            created_at=datetime.fromisoformat(data['created_at']),
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            supports_resume=data.get('supports_resume', False),
            content_type=data.get('content_type', ''),
            retry_count=data.get('retry_count', 0),
            checksum=data.get('checksum', ''),
            checksum_algorithm=data.get('checksum_algorithm', ''),
            expected_checksum=data.get('expected_checksum', '')
        )
