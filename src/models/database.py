"""
SQLite database operations for download history and resume data
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .download import Download, SegmentInfo
from ..utils.constants import DB_PATH, DownloadStatus


class Database:
    """SQLite database handler for downloads"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """Initialize database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                filename TEXT NOT NULL,
                save_path TEXT NOT NULL,
                total_size INTEGER DEFAULT 0,
                downloaded_size INTEGER DEFAULT 0,
                status TEXT DEFAULT 'queued',
                num_segments INTEGER DEFAULT 8,
                error_message TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                completed_at TEXT,
                supports_resume INTEGER DEFAULT 0,
                content_type TEXT DEFAULT '',
                segments_json TEXT DEFAULT '[]',
                retry_count INTEGER DEFAULT 0,
                checksum TEXT DEFAULT '',
                checksum_algorithm TEXT DEFAULT '',
                expected_checksum TEXT DEFAULT ''
            )
        ''')

        # Migrate: Add new columns if they don't exist (for existing databases)
        self._migrate_database(cursor)

        conn.commit()
        conn.close()

    def _migrate_database(self, cursor):
        """Migrate existing database to add new columns"""
        # Get existing columns
        cursor.execute("PRAGMA table_info(downloads)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        # Add new columns if they don't exist
        new_columns = {
            'retry_count': 'INTEGER DEFAULT 0',
            'checksum': "TEXT DEFAULT ''",
            'checksum_algorithm': "TEXT DEFAULT ''",
            'expected_checksum': "TEXT DEFAULT ''"
        }

        for column, definition in new_columns.items():
            if column not in existing_columns:
                try:
                    cursor.execute(f'ALTER TABLE downloads ADD COLUMN {column} {definition}')
                except Exception as e:
                    print(f"Migration warning: Could not add column {column}: {e}")

    def save_download(self, download: Download):
        """Save or update a download in the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        segments_json = json.dumps([
            {
                'index': s.index,
                'start_byte': s.start_byte,
                'end_byte': s.end_byte,
                'downloaded': s.downloaded,
                'completed': s.completed,
                'temp_file': s.temp_file
            }
            for s in download.segments
        ])
        
        cursor.execute('''
            INSERT OR REPLACE INTO downloads
            (id, url, filename, save_path, total_size, downloaded_size, status,
             num_segments, error_message, created_at, completed_at, supports_resume,
             content_type, segments_json, retry_count, checksum, checksum_algorithm, expected_checksum)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            download.id,
            download.url,
            download.filename,
            download.save_path,
            download.total_size,
            download.downloaded_size,
            download.status,
            download.num_segments,
            download.error_message,
            download.created_at.isoformat(),
            download.completed_at.isoformat() if download.completed_at else None,
            1 if download.supports_resume else 0,
            download.content_type,
            segments_json,
            download.retry_count,
            download.checksum,
            download.checksum_algorithm,
            download.expected_checksum
        ))
        
        conn.commit()
        conn.close()
    
    def get_download(self, download_id: str) -> Optional[Download]:
        """Get a download by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM downloads WHERE id = ?', (download_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_download(row)
        return None
    
    def get_all_downloads(self) -> List[Download]:
        """Get all downloads from database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM downloads ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_download(row) for row in rows]
    
    def get_incomplete_downloads(self) -> List[Download]:
        """Get all incomplete downloads (for resume on startup)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM downloads 
            WHERE status IN (?, ?, ?)
            ORDER BY created_at DESC
        ''', (DownloadStatus.DOWNLOADING, DownloadStatus.PAUSED, DownloadStatus.QUEUED))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_download(row) for row in rows]
    
    def delete_download(self, download_id: str):
        """Delete a download from database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM downloads WHERE id = ?', (download_id,))
        
        conn.commit()
        conn.close()
    
    def clear_completed(self):
        """Clear all completed downloads from database"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM downloads WHERE status = ?', (DownloadStatus.COMPLETED,))

        conn.commit()
        conn.close()

    def get_completed_downloads(self) -> List[Download]:
        """Get all completed, failed, or cancelled downloads (for history view)"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM downloads
            WHERE status IN (?, ?, ?)
            ORDER BY created_at DESC
        ''', (DownloadStatus.COMPLETED, DownloadStatus.FAILED, DownloadStatus.CANCELLED))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_download(row) for row in rows]

    def search_downloads(self, query: str, status_filter: Optional[str] = None) -> List[Download]:
        """
        Search downloads by filename or URL.

        Args:
            query: Search query string
            status_filter: Optional status filter (completed, failed, cancelled, etc.)

        Returns:
            List of matching downloads
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        sql = 'SELECT * FROM downloads WHERE (filename LIKE ? OR url LIKE ?)'
        params = (f'%{query}%', f'%{query}%')

        if status_filter:
            sql += ' AND status = ?'
            params = (f'%{query}%', f'%{query}%', status_filter)

        sql += ' ORDER BY created_at DESC'

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_download(row) for row in rows]

    def filter_by_status(self, statuses: List[str]) -> List[Download]:
        """
        Filter downloads by status.

        Args:
            statuses: List of status values to filter by

        Returns:
            List of downloads with matching status
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        placeholders = ','.join('?' * len(statuses))
        cursor.execute(f'''
            SELECT * FROM downloads
            WHERE status IN ({placeholders})
            ORDER BY created_at DESC
        ''', statuses)

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_download(row) for row in rows]

    def filter_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Download]:
        """
        Filter downloads by date range.

        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)

        Returns:
            List of downloads in the date range
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM downloads
            WHERE created_at >= ? AND created_at <= ?
            ORDER BY created_at DESC
        ''', (start_date.isoformat(), end_date.isoformat()))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_download(row) for row in rows]

    def _row_to_download(self, row: sqlite3.Row) -> Download:
        """Convert database row to Download object"""
        segments_data = json.loads(row['segments_json'])
        segments = [
            SegmentInfo(
                index=s['index'],
                start_byte=s['start_byte'],
                end_byte=s['end_byte'],
                downloaded=s['downloaded'],
                completed=s['completed'],
                temp_file=s['temp_file']
            )
            for s in segments_data
        ]
        
        return Download(
            id=row['id'],
            url=row['url'],
            filename=row['filename'],
            save_path=row['save_path'],
            total_size=row['total_size'],
            downloaded_size=row['downloaded_size'],
            status=row['status'],
            segments=segments,
            num_segments=row['num_segments'],
            error_message=row['error_message'],
            created_at=datetime.fromisoformat(row['created_at']),
            completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
            supports_resume=bool(row['supports_resume']),
            content_type=row['content_type'],
            retry_count=row.get('retry_count', 0),
            checksum=row.get('checksum', ''),
            checksum_algorithm=row.get('checksum_algorithm', ''),
            expected_checksum=row.get('expected_checksum', '')
        )
