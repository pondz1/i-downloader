"""
Main application window
"""

import os
import sys
import asyncio
import json
import platform
import subprocess
from pathlib import Path
from typing import Dict, Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QToolBar, QStatusBar,
    QSystemTrayIcon, QMenu, QMessageBox, QApplication, QTabWidget, QDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QSize
from PyQt6.QtGui import QIcon, QAction, QCloseEvent

try:
    import qtawesome as qta
    HAS_QTAWESOME = True
except ImportError:
    HAS_QTAWESOME = False

from .styles import DARK_THEME
from .download_item import DownloadItemWidget
from .download_dialog import DownloadDialog
from .settings_dialog import SettingsDialog
from .clipboard_monitor import ClipboardMonitor
from .batch_dialog import BatchImportDialog
from .history_view import HistoryViewWidget
from ..core.downloader import DownloadManager
from ..core.scheduler import DownloadScheduler
from ..models.download import Download
from ..utils.constants import (
    APP_NAME, APP_VERSION, APP_DATA_DIR,
    DEFAULT_DOWNLOAD_DIR, DEFAULT_SEGMENTS, DEFAULT_MAX_CONCURRENT,
    DownloadStatus
)
from ..utils.helpers import format_size, format_speed


def get_icon(icon_name: str, color: str = '#eaeaea'):
    """Get icon from QtAwesome or return None"""
    if HAS_QTAWESOME:
        return qta.icon(icon_name, color=color)
    return None


def open_path(path: str):
    """
    Open a file or folder using the system's default application.
    Cross-platform implementation supporting Windows, macOS, and Linux.
    """
    try:
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', path], check=True)
        else:  # Linux and others
            subprocess.run(['xdg-open', path], check=True)
    except Exception as e:
        print(f"Failed to open {path}: {e}")


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Settings
        self._settings = self._load_settings()
        
        # Download manager
        self._download_manager: Optional[DownloadManager] = None
        self._download_widgets: Dict[str, DownloadItemWidget] = {}

        # Async event loop
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # Clipboard monitor
        self._clipboard_monitor = None
        self._clipboard_dialog_shown = False

        # Scheduler
        self._scheduler: Optional[DownloadScheduler] = None

        # Notification manager
        self._notification_manager = None

        # Setup UI
        self._setup_window()
        self._setup_toolbar()
        self._setup_central_widget()
        self._setup_status_bar()
        self._setup_system_tray()
        
        # Apply theme
        self.setStyleSheet(DARK_THEME)
        
        # Update timer for progress refresh
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._refresh_downloads)
        self._update_timer.start(500)  # Update every 500ms
    
    def _setup_window(self):
        """Setup main window properties"""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(800, 600)
        self.resize(900, 650)
        
        # Set window icon
        if HAS_QTAWESOME:
            self.setWindowIcon(qta.icon('fa5s.download', color='#e94560'))
        
        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _setup_toolbar(self):
        """Setup the toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)
        
        # Add download button
        self.add_btn = QPushButton(" Add Download")
        if HAS_QTAWESOME:
            self.add_btn.setIcon(qta.icon('fa5s.plus', color='#eaeaea'))
        self.add_btn.clicked.connect(self._on_add_download)
        toolbar.addWidget(self.add_btn)

        # Batch import button
        self.batch_btn = QPushButton(" Batch Import")
        if HAS_QTAWESOME:
            self.batch_btn.setIcon(qta.icon('fa5s.list', color='#eaeaea'))
        self.batch_btn.clicked.connect(self._on_batch_import)
        toolbar.addWidget(self.batch_btn)

        toolbar.addSeparator()
        
        # Resume all button
        self.resume_all_btn = QPushButton(" Resume All")
        if HAS_QTAWESOME:
            self.resume_all_btn.setIcon(qta.icon('fa5s.play', color='#eaeaea'))
        self.resume_all_btn.clicked.connect(self._on_resume_all)
        toolbar.addWidget(self.resume_all_btn)
        
        # Pause all button
        self.pause_all_btn = QPushButton(" Pause All")
        if HAS_QTAWESOME:
            self.pause_all_btn.setIcon(qta.icon('fa5s.pause', color='#eaeaea'))
        self.pause_all_btn.clicked.connect(self._on_pause_all)
        toolbar.addWidget(self.pause_all_btn)
        
        toolbar.addSeparator()
        
        # Clear completed button
        self.clear_btn = QPushButton(" Clear Completed")
        if HAS_QTAWESOME:
            self.clear_btn.setIcon(qta.icon('fa5s.trash-alt', color='#eaeaea'))
        self.clear_btn.clicked.connect(self._on_clear_completed)
        toolbar.addWidget(self.clear_btn)
        
        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(spacer.sizePolicy().Policy.Expanding, spacer.sizePolicy().Policy.Preferred)
        toolbar.addWidget(spacer)
        
        # Settings button
        self.settings_btn = QPushButton(" Settings")
        if HAS_QTAWESOME:
            self.settings_btn.setIcon(qta.icon('fa5s.cog', color='#eaeaea'))
        self.settings_btn.clicked.connect(self._on_settings)
        toolbar.addWidget(self.settings_btn)
    
    def _setup_central_widget(self):
        """Setup the central widget with tabs"""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("mainTabWidget")

        # Downloads tab
        downloads_tab = QWidget()
        downloads_layout = QVBoxLayout(downloads_tab)
        downloads_layout.setContentsMargins(0, 0, 0, 0)
        downloads_layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Downloads")
        title.setObjectName("titleLabel")
        header_layout.addWidget(title)
        header_layout.addStretch()
        self.download_count_label = QLabel("0 downloads")
        self.download_count_label.setObjectName("subtitleLabel")
        header_layout.addWidget(self.download_count_label)
        downloads_layout.addLayout(header_layout)

        # Scroll area for downloads
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.downloads_container = QWidget()
        self.downloads_layout = QVBoxLayout(self.downloads_container)
        self.downloads_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.downloads_layout.setSpacing(10)
        self.downloads_layout.setContentsMargins(0, 0, 0, 0)

        scroll.setWidget(self.downloads_container)
        downloads_layout.addWidget(scroll)

        # Empty state
        self.empty_label = QLabel("No downloads yet. Click '+ Add Download' to start.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setObjectName("subtitleLabel")
        self.empty_label.setStyleSheet("padding: 50px; color: #666;")
        self.downloads_layout.addWidget(self.empty_label)

        # Add downloads tab
        self.tab_widget.addTab(downloads_tab, "Downloads")

        # History tab
        self.history_view = HistoryViewWidget()
        self.history_view.open_file_requested.connect(self._on_open_file)
        self.history_view.open_folder_requested.connect(self._on_open_folder)
        self.history_view.delete_requested.connect(self._on_history_delete)
        self.history_view.retry_requested.connect(self._on_history_retry)
        self.tab_widget.addTab(self.history_view, "History")

        layout.addWidget(self.tab_widget)

        # Connect tab change to refresh history
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
    def _setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Download stats
        self.stats_label = QLabel("Ready")
        self.status_bar.addPermanentWidget(self.stats_label)
    
    def _setup_system_tray(self):
        """Setup system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Set tray icon
        if HAS_QTAWESOME:
            self.tray_icon.setIcon(qta.icon('fa5s.download', color='#e94560'))
        else:
            # Use default Qt icon as fallback
            self.tray_icon.setIcon(self.style().standardIcon(
                self.style().StandardPixmap.SP_ArrowDown
            ))
        
        # Create tray menu
        tray_menu = QMenu()
        tray_menu.setObjectName("trayMenu")
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._on_quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()
    
    async def initialize(self):
        """Initialize async components"""
        self._loop = asyncio.get_event_loop()

        # Initialize download manager
        rate_limit = self._settings.get('rate_limit', 0)

        # Build proxy URL if enabled
        proxy_url = None
        if self._settings.get('proxy_enabled', False):
            proxy_type = self._settings.get('proxy_type', 'http')
            proxy_host = self._settings.get('proxy_host', '')
            proxy_port = self._settings.get('proxy_port', '')
            proxy_username = self._settings.get('proxy_username', '')
            proxy_password = self._settings.get('proxy_password', '')

            if proxy_host and proxy_port:
                if proxy_username:
                    proxy_url = f"{proxy_type}://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
                else:
                    proxy_url = f"{proxy_type}://{proxy_host}:{proxy_port}"

        self._download_manager = DownloadManager(
            max_concurrent=self._settings.get('max_concurrent', DEFAULT_MAX_CONCURRENT),
            default_segments=self._settings.get('default_segments', DEFAULT_SEGMENTS),
            progress_callback=self._on_download_progress,
            status_callback=self._on_download_status_changed,
            rate_limit=rate_limit if rate_limit > 0 else None,
            proxy_url=proxy_url,
            enable_retry=self._settings.get('enable_retry', True),
            max_retries=self._settings.get('max_retries', 3),
            retry_delay=self._settings.get('retry_delay', 5.0),
            retry_backoff=self._settings.get('retry_backoff', 2.0)
        )
        await self._download_manager.initialize()

        # Initialize scheduler
        self._scheduler = DownloadScheduler(self._start_scheduled_download)
        await self._scheduler.start()

        # Initialize notification manager
        from ..utils.notifications import NotificationManager
        self._notification_manager = NotificationManager()

        # Initialize clipboard monitor
        self._clipboard_monitor = ClipboardMonitor(self)
        self._clipboard_monitor.url_detected.connect(self._on_url_detected)
        self._clipboard_monitor.set_enabled(self._settings.get('watch_clipboard', False))

        # Load existing downloads into UI
        for download in self._download_manager.get_all_downloads():
            self._add_download_widget(download)

        self._update_empty_state()
        self._update_stats()
    
    async def shutdown(self):
        """Shutdown async components"""
        if self._scheduler:
            await self._scheduler.stop()
        if self._download_manager:
            await self._download_manager.shutdown()
    
    def _on_add_download(self):
        """Handle add download button click"""
        dialog = DownloadDialog(self)
        dialog.download_requested.connect(self._start_new_download)
        dialog.video_download_requested.connect(self._on_video_download_requested)
        dialog.exec()

    def _on_batch_import(self):
        """Handle batch import button click"""
        dialog = BatchImportDialog(self)
        dialog.downloads_requested.connect(self._start_batch_downloads)
        dialog.exec()

    def _start_batch_downloads(self, downloads: list):
        """Start multiple downloads from batch import"""
        for url, save_dir, num_segments, category in downloads:
            QTimer.singleShot(0, lambda u=url, d=save_dir, s=num_segments, c=category:
                self._start_new_download(u, d, s, c))

    def _start_scheduled_download(self, url: str, save_dir: str, num_segments: int, category: str = "all"):
        """Callback for starting a scheduled download"""
        QTimer.singleShot(0, lambda: self._start_new_download(url, save_dir, num_segments, category))

    def _on_url_detected(self, url: str):
        """Handle URL detected in clipboard"""
        # Prevent showing multiple dialogs in quick succession
        if self._clipboard_dialog_shown:
            return

        self._clipboard_dialog_shown = True

        reply = QMessageBox.question(
            self,
            "URL Detected in Clipboard",
            f"A URL was detected in your clipboard:\n\n{url}\n\nDo you want to download it?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Show download dialog with the URL
            dialog = DownloadDialog(self, url=url)
            dialog.download_requested.connect(self._start_new_download)
            dialog.video_download_requested.connect(self._on_video_download_requested)
            dialog.exec()

        self._clipboard_dialog_shown = False

    def _start_new_download(self, url: str, save_dir: str, num_segments: int, category: str = "all", scheduled_time=None, expected_checksum: str = "", checksum_algorithm: str = ""):
        """Start a new download"""
        if scheduled_time and self._scheduler:
            # Schedule the download
            self._scheduler.schedule_download(url, save_dir, num_segments, scheduled_time, category)
            QMessageBox.information(
                self,
                "Download Scheduled",
                f"Download has been scheduled for:\n{scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        elif self._loop and self._download_manager:
            asyncio.run_coroutine_threadsafe(
                self._add_and_start_download(url, save_dir, num_segments, category, expected_checksum, checksum_algorithm),
                self._loop
            )

    def _on_video_download_requested(self, url: str, save_dir: str, category: str):
        """Handle video download request - show format selection dialog"""
        from .video_format_dialog import VideoFormatDialog

        # Show format selection dialog
        dialog = VideoFormatDialog(url, self)
        dialog.format_selected.connect(lambda format_ids, video_info: self._start_video_download(url, save_dir, format_ids, category))
        result = dialog.exec()

        if result != QDialog.DialogCode.Accepted:
            # User cancelled
            pass

    def _start_video_download(self, url: str, save_dir: str, format_ids: list, category: str):
        """Start video downloads with selected format(s)"""
        if self._loop and self._download_manager:
            for format_id in format_ids:
                asyncio.run_coroutine_threadsafe(
                    self._add_and_start_video_download(url, save_dir, format_id, category),
                    self._loop
                )

    async def _add_and_start_video_download(self, url: str, save_dir: str, format_id: str, category: str):
        """Add and start a video download (async)"""
        try:
            from ..core.video_downloader import VideoDownloader
            from ..models.download import DownloadStatus
            import os

            # Ensure save directory exists
            os.makedirs(save_dir, exist_ok=True)

            # Create video downloader
            video_downloader = VideoDownloader()

            # Get video info first
            info = await video_downloader.get_video_info(url)

            # Check if it's a playlist
            if info.get('is_playlist'):
                # Handle playlist download
                await self._handle_playlist_download(url, save_dir, format_id, category, info)
                return

            # Create a download object for the video
            # Determine the correct file extension based on format
            is_audio = format_id.startswith('bestaudio') or 'audio' in format_id
            if is_audio:
                extension = 'm4a'  # Audio files are converted to m4a
            else:
                extension = 'mp4'  # Default video extension

            filename = f"{info['title']}.{extension}"

            # Import Download model
            from ..models.download import Download
            from ..utils.constants import generate_id

            download_id = generate_id()

            download = Download(
                id=download_id,
                url=url,
                save_path=os.path.join(save_dir, filename),
                filename=filename,
                total_size=info.get('filesize', 0) or 0,
                num_segments=1,  # Video downloads don't use segments
                status=DownloadStatus.DOWNLOADING,  # Set to downloading immediately
            )

            # Store video-specific info
            download.format_id = format_id
            download.is_video = True
            download.video_title = info.get('title', 'Unknown')
            download.thumbnail_url = info.get('thumbnail', '')

            # Add to download manager tracking
            self._download_manager.downloads[download_id] = download

            # Add widget on main thread AFTER setting status to DOWNLOADING
            QTimer.singleShot(0, lambda: self._add_download_widget(download))

            # Start the download
            await self._download_video_with_progress(download, video_downloader)

        except Exception as e:
            error_msg = str(e)
            QTimer.singleShot(0, lambda msg=error_msg: QMessageBox.critical(
                self,
                "Error",
                f"Failed to start video download:\n\n{msg}"
            ))

    async def _download_video_with_progress(self, download, video_downloader):
        """Download video with progress tracking"""
        try:
            from ..models.download import DownloadStatus
            import os

            save_dir = os.path.dirname(download.save_path)

            def progress_callback(progress, downloaded, total, speed):
                """Progress callback from video downloader"""
                # Update download progress - progress is calculated from downloaded_size / total_size
                download.downloaded_size = downloaded
                download.total_size = total
                download.speed = speed

                # Notify progress
                self._download_manager._notify_progress(download)

            # Start download
            result = await video_downloader.download_video(
                url=download.url,
                save_path=save_dir,
                format_id=download.format_id,
                progress_callback=progress_callback
            )

            if result.get('success'):
                download.status = DownloadStatus.COMPLETED
                download.downloaded_size = download.total_size  # Ensure 100% progress

                # Update actual filepath if different
                if result.get('filepath'):
                    download.save_path = result['filepath']
                    # Also update filename to match actual file
                    download.filename = os.path.basename(result['filepath'])

                # Notify status change
                self._download_manager._notify_status(download)
            else:
                from ..models.download import DownloadStatus
                download.status = DownloadStatus.FAILED
                download.error_message = result.get('error', 'Unknown error')
                self._download_manager._notify_status(download)

        except Exception as e:
            from ..models.download import DownloadStatus
            download.status = DownloadStatus.FAILED
            download.error_message = str(e)
            self._download_manager._notify_status(download)

    async def _handle_playlist_download(self, url: str, save_dir: str, format_id: str, category: str, info: dict):
        """Handle playlist download - add all videos to queue"""
        try:
            from ..core.video_downloader import VideoDownloader

            video_downloader = VideoDownloader()

            # Get playlist videos
            playlist_videos = await video_downloader.get_playlist_videos(url)

            # Confirm with user
            reply = QMessageBox.question(
                self,
                "Playlist Detected",
                f"This URL contains {len(playlist_videos)} videos.\n\nDo you want to download all of them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Add each video to download queue
            for i, video in enumerate(playlist_videos):
                try:
                    # Recursively call _add_and_start_video_download for each video
                    await self._add_and_start_video_download(
                        url=video['url'],
                        save_dir=save_dir,
                        format_id=format_id,
                        category=category
                    )

                    # Small delay between adding to avoid overwhelming
                    await asyncio.sleep(0.5)

                except Exception as e:
                    print(f"Error adding video {i+1} from playlist from playlist: {e}")

            QMessageBox.information(
                self,
                "Playlist Queued",
                f"Added {len(playlist_videos)} videos to the download queue."
            )

        except Exception as e:
            error_msg = str(e)
            QTimer.singleShot(0, lambda msg=error_msg: QMessageBox.critical(
                self,
                "Playlist Error",
                f"Failed to process playlist:\n\n{msg}"
            ))

    async def _add_and_start_download(self, url: str, save_dir: str, num_segments: int, category: str = "all", expected_checksum: str = "", checksum_algorithm: str = ""):
        """Add and start a download (async)"""
        try:
            import os
            from ..utils.categories import get_category_from_filename, get_category_save_path

            # Ensure save directory exists
            os.makedirs(save_dir, exist_ok=True)

            download = await self._download_manager.add_download(
                url=url,
                save_dir=save_dir,
                num_segments=num_segments
            )

            # Set checksum information if provided
            if expected_checksum:
                download.expected_checksum = expected_checksum
                download.checksum_algorithm = checksum_algorithm

            # Handle auto category detection
            if category == "auto":
                detected_category = get_category_from_filename(download.filename)

                # Update save path if category detected and not "all"
                if detected_category != "all":
                    new_save_dir = get_category_save_path(save_dir, detected_category)
                    if new_save_dir != save_dir:
                        os.makedirs(new_save_dir, exist_ok=True)
                        download.save_path = os.path.join(new_save_dir, download.filename)

            # Add widget on main thread
            QTimer.singleShot(0, lambda: self._add_download_widget(download))

            # Start if auto-start is enabled
            if self._settings.get('auto_start', True):
                await self._download_manager.start_download(download.id)
        except Exception as e:
            error_msg = str(e)
            QTimer.singleShot(0, lambda msg=error_msg: QMessageBox.critical(
                self, "Error", f"Failed to add download: {msg}"
            ))
    
    def _add_download_widget(self, download: Download):
        """Add a download widget to the list"""
        # Hide empty label
        self.empty_label.hide()
        
        # Create widget
        widget = DownloadItemWidget(download)
        widget.pause_clicked.connect(self._on_pause_download)
        widget.resume_clicked.connect(self._on_resume_download)
        widget.cancel_clicked.connect(self._on_cancel_download)
        widget.open_file_clicked.connect(self._on_open_file)
        widget.open_folder_clicked.connect(self._on_open_folder)
        
        # Add to layout
        self.downloads_layout.insertWidget(0, widget)
        self._download_widgets[download.id] = widget
        
        # Update count
        self._update_download_count()
    
    def _remove_download_widget(self, download_id: str):
        """Remove a download widget from the list"""
        if download_id in self._download_widgets:
            widget = self._download_widgets[download_id]
            self.downloads_layout.removeWidget(widget)
            widget.deleteLater()
            del self._download_widgets[download_id]
            
            self._update_empty_state()
            self._update_download_count()
    
    def _update_empty_state(self):
        """Update empty state visibility"""
        if not self._download_widgets:
            self.empty_label.show()
        else:
            self.empty_label.hide()
    
    def _update_download_count(self):
        """Update download count label"""
        count = len(self._download_widgets)
        self.download_count_label.setText(f"{count} download{'s' if count != 1 else ''}")
    
    def _on_download_progress(self, download: Download):
        """Callback for download progress updates"""
        # Update is handled by the timer for batching
        pass
    
    def _on_download_status_changed(self, download: Download):
        """Callback for download status changes"""
        # Show notification if enabled and download completed or failed
        if self._notification_manager and self._settings.get('notify_complete', True):
            if download.status == DownloadStatus.COMPLETED:
                self._notification_manager.show_completion(
                    download.filename,
                    format_size(download.total_size),
                    format_speed(download.speed)
                )
            elif download.status == DownloadStatus.FAILED:
                self._notification_manager.show_failure(
                    download.filename,
                    download.error_message or "Unknown error"
                )

        QTimer.singleShot(0, lambda: self._update_download_widget(download))
    
    def _update_download_widget(self, download: Download):
        """Update a download widget"""
        if download.id in self._download_widgets:
            self._download_widgets[download.id].update_download(download)
        self._update_stats()
    
    def _refresh_downloads(self):
        """Refresh all download displays"""
        if not self._download_manager:
            return
        
        for download in self._download_manager.get_all_downloads():
            if download.id in self._download_widgets:
                self._download_widgets[download.id].update_download(download)
        
        self._update_stats()
    
    def _update_stats(self):
        """Update status bar stats"""
        if not self._download_manager:
            return
        
        downloads = self._download_manager.get_all_downloads()
        active = sum(1 for d in downloads if d.is_active)
        total_speed = sum(d.speed for d in downloads if d.is_active)
        
        if active > 0:
            self.stats_label.setText(
                f"Active: {active}  •  Speed: {format_speed(total_speed)}"
            )
        else:
            self.stats_label.setText("Ready")
    
    @pyqtSlot(str)
    def _on_pause_download(self, download_id: str):
        """Handle pause download"""
        if self._loop and self._download_manager:
            asyncio.run_coroutine_threadsafe(
                self._download_manager.pause_download(download_id),
                self._loop
            )
    
    @pyqtSlot(str)
    def _on_resume_download(self, download_id: str):
        """Handle resume download"""
        if self._loop and self._download_manager:
            asyncio.run_coroutine_threadsafe(
                self._download_manager.start_download(download_id),
                self._loop
            )
    
    @pyqtSlot(str)
    def _on_cancel_download(self, download_id: str):
        """Handle cancel download"""
        reply = QMessageBox.question(
            self, "Cancel Download",
            "Are you sure you want to cancel this download?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self._loop and self._download_manager:
                asyncio.run_coroutine_threadsafe(
                    self._download_manager.cancel_download(download_id),
                    self._loop
                )
            self._remove_download_widget(download_id)
    
    @pyqtSlot(str)
    def _on_open_file(self, download_id: str):
        """Handle open file"""
        if self._download_manager:
            download = self._download_manager.get_download(download_id)
            if download and os.path.exists(download.save_path):
                open_path(download.save_path)

    @pyqtSlot(str)
    def _on_open_folder(self, download_id: str):
        """Handle open folder"""
        if self._download_manager:
            download = self._download_manager.get_download(download_id)
            if download:
                folder = os.path.dirname(download.save_path)
                if os.path.exists(folder):
                    open_path(folder)
    
    def _on_resume_all(self):
        """Resume all paused downloads"""
        if self._loop and self._download_manager:
            for download in self._download_manager.get_all_downloads():
                if download.status in (DownloadStatus.PAUSED, DownloadStatus.QUEUED):
                    asyncio.run_coroutine_threadsafe(
                        self._download_manager.start_download(download.id),
                        self._loop
                    )
    
    def _on_pause_all(self):
        """Pause all active downloads"""
        if self._loop and self._download_manager:
            for download in self._download_manager.get_all_downloads():
                if download.is_active:
                    asyncio.run_coroutine_threadsafe(
                        self._download_manager.pause_download(download.id),
                        self._loop
                    )
    
    def _on_clear_completed(self):
        """Clear completed downloads"""
        if self._download_manager:
            completed_ids = [
                d.id for d in self._download_manager.get_all_downloads()
                if d.is_complete
            ]
            
            for download_id in completed_ids:
                self._remove_download_widget(download_id)
                self._download_manager.db.delete_download(download_id)
                if download_id in self._download_manager.downloads:
                    del self._download_manager.downloads[download_id]
    
    def _on_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self._settings, self)
        dialog.settings_changed.connect(self._apply_settings)
        dialog.exec()
    
    def _apply_settings(self, settings: dict):
        """Apply new settings"""
        self._settings = settings
        self._save_settings()

        # Apply to download manager
        if self._download_manager:
            self._download_manager.max_concurrent = settings.get('max_concurrent', DEFAULT_MAX_CONCURRENT)
            self._download_manager.default_segments = settings.get('default_segments', DEFAULT_SEGMENTS)
            rate_limit = settings.get('rate_limit', 0)
            self._download_manager.rate_limit = rate_limit if rate_limit > 0 else None

            # Apply retry settings
            self._download_manager.enable_retry = settings.get('enable_retry', True)
            self._download_manager.max_retries = settings.get('max_retries', 3)
            self._download_manager.retry_delay = settings.get('retry_delay', 5.0)
            self._download_manager.retry_backoff = settings.get('retry_backoff', 2.0)

            # Apply proxy settings - requires rebuilding session
            proxy_url = None
            if settings.get('proxy_enabled', False):
                proxy_type = settings.get('proxy_type', 'http')
                proxy_host = settings.get('proxy_host', '')
                proxy_port = settings.get('proxy_port', '')
                proxy_username = settings.get('proxy_username', '')
                proxy_password = settings.get('proxy_password', '')

                if proxy_host and proxy_port:
                    if proxy_username:
                        proxy_url = f"{proxy_type}://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
                    else:
                        proxy_url = f"{proxy_type}://{proxy_host}:{proxy_port}"

            self._download_manager.proxy_url = proxy_url
            # Note: Proxy changes require restarting the download manager for active downloads
            # This is a limitation of aiohttp's session architecture

        # Apply to clipboard monitor
        if self._clipboard_monitor:
            self._clipboard_monitor.set_enabled(settings.get('watch_clipboard', False))
    
    def _load_settings(self) -> dict:
        """Load settings from file"""
        settings_path = APP_DATA_DIR / "settings.json"
        if settings_path.exists():
            try:
                with open(settings_path) as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_settings(self):
        """Save settings to file"""
        settings_path = APP_DATA_DIR / "settings.json"
        try:
            with open(settings_path, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.activateWindow()
    
    def _on_quit(self):
        """Handle quit action"""
        self._force_quit = True
        self.close()
    
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event"""
        if self._settings.get('close_to_tray', False) and not getattr(self, '_force_quit', False):
            event.ignore()
            self.hide()
        else:
            # Stop the update timer first
            self._update_timer.stop()

            # Save all downloads synchronously
            if self._download_manager:
                for download in self._download_manager.get_all_downloads():
                    self._download_manager.db.save_download(download)

            # Close tray icon
            if hasattr(self, 'tray_icon'):
                self.tray_icon.hide()

            event.accept()

    def _on_tab_changed(self, index: int):
        """Handle tab change"""
        if index == 1:  # History tab
            self._refresh_history()

    def _refresh_history(self):
        """Refresh the history view"""
        if hasattr(self, 'history_view') and self._download_manager:
            completed_downloads = self._download_manager.db.get_completed_downloads()
            self.history_view.set_downloads(completed_downloads)

    def _on_history_delete(self, download_id: str):
        """Handle delete from history"""
        if self._download_manager:
            self._download_manager.db.delete_download(download_id)
            if download_id in self._download_manager.downloads:
                del self._download_manager.downloads[download_id]
            self._refresh_history()

    def _on_history_retry(self, download_id: str):
        """Handle retry from history"""
        if self._loop and self._download_manager:
            download = self._download_manager.get_download(download_id)
            if download:
                # Reset download for retry
                download.status = DownloadStatus.QUEUED
                download.downloaded_size = 0
                download.retry_count = 0
                download.error_message = ""
                for segment in download.segments:
                    segment.downloaded = 0
                    segment.completed = False

                # Remove from history and add back to active downloads
                self._download_manager.db.save_download(download)
                self._add_download_widget(download)

                # Start the download
                asyncio.run_coroutine_threadsafe(
                    self._download_manager.start_download(download_id),
                    self._loop
                )

                # Refresh history
                self._refresh_history()
