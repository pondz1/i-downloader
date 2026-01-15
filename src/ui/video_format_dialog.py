"""
Video format selection dialog
"""

import asyncio
from typing import Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QWidget, QMessageBox, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QPixmap, QFont

try:
    import qtawesome as qta
    HAS_QTAWESOME = True
except ImportError:
    HAS_QTAWESOME = False


class VideoInfoFetcher(QThread):
    """
    Thread for fetching video info asynchronously.
    """

    info_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self._should_stop = False

    def stop(self):
        """Signal the thread to stop"""
        self._should_stop = True

    def run(self):
        """Fetch video info in background thread"""
        loop = None
        try:
            from ..core.video_downloader import VideoDownloader

            # Create asyncio event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                if not self._should_stop:
                    downloader = VideoDownloader()
                    info = loop.run_until_complete(downloader.get_video_info(self.url))
                    if not self._should_stop:
                        self.info_ready.emit(info)
            except asyncio.CancelledError:
                pass  # Task was cancelled, normal shutdown
            except Exception as e:
                if not self._should_stop:
                    self.error_occurred.emit(str(e))

        except Exception as e:
            if not self._should_stop:
                self.error_occurred.emit(str(e))
        finally:
            # Clean up the event loop properly
            if loop:
                try:
                    # Cancel all pending tasks
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()
                    # Wait for tasks to be cancelled
                    if pending:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                except Exception:
                    pass

                try:
                    loop.close()
                except Exception:
                    pass


class VideoFormatDialog(QDialog):
    """
    Dialog for selecting video format before download.

    Shows video thumbnail, title, and available formats in a table.
    """

    format_selected = pyqtSignal(list, dict)  # format_ids list, video_info

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url
        self.video_info = {}
        self.fetcher = None

        self._setup_ui()
        self._fetch_video_info()

    def _setup_ui(self):
        """Set up the dialog UI"""
        self.setWindowTitle("Select Video Format")
        self.setMinimumSize(700, 550)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Video info section
        info_widget = QWidget()
        info_layout = QHBoxLayout(info_widget)
        info_layout.setSpacing(15)

        # Thumbnail
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(160, 120)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                background-color: #16213e;
                border: 2px solid #0f3460;
                border-radius: 8px;
            }
        """)
        self.thumbnail_label.setText("Loading...")
        info_layout.addWidget(self.thumbnail_label)

        # Video details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(8)

        self.title_label = QLabel("Fetching video info...")
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #eaeaea;")
        details_layout.addWidget(self.title_label)

        self.meta_label = QLabel("")
        self.meta_label.setStyleSheet("color: #888; font-size: 12px;")
        details_layout.addWidget(self.meta_label)

        details_layout.addStretch()
        info_layout.addLayout(details_layout)

        layout.addWidget(info_widget)

        # Format filter
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet("color: #eaeaea;")
        filter_layout.addWidget(filter_label)

        self.quality_filter = QComboBox()
        self.quality_filter.addItem("All Formats", "all")
        self.quality_filter.addItem("1080p+", "1080")
        self.quality_filter.addItem("720p", "720")
        self.quality_filter.addItem("480p", "480")
        self.quality_filter.addItem("Audio Only", "audio")
        self.quality_filter.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.quality_filter)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Formats table
        self.formats_table = QTableWidget()
        self.formats_table.setColumnCount(5)
        self.formats_table.setHorizontalHeaderLabels([
            "Download", "Quality", "Format", "Size", "Codec"
        ])

        # Style the table
        self.formats_table.setStyleSheet("""
            QTableWidget {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 6px;
                gridline-color: #0f3460;
            }
            QTableWidget::item {
                padding: 8px;
                color: #eaeaea;
            }
            QTableWidget::item:selected {
                background-color: #0f3460;
                color: #4cc9f0;
            }
            QHeaderView::section {
                background-color: #1a1a2e;
                color: #eaeaea;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #0f3460;
                font-weight: bold;
            }
        """)

        # Set column widths
        header = self.formats_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # Set row height
        self.formats_table.verticalHeader().setVisible(False)
        self.formats_table.setShowGrid(False)

        layout.addWidget(self.formats_table)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.select_btn = QPushButton("Download Selected Format")
        self.select_btn.setObjectName("primaryButton")
        self.select_btn.setEnabled(False)
        self.select_btn.clicked.connect(self._on_select_format)
        button_layout.addWidget(self.select_btn)

        layout.addLayout(button_layout)

        # Loading indicator
        self.loading_label = QLabel("Fetching video information...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("color: #4cc9f0; font-size: 14px; padding: 20px;")
        layout.addWidget(self.loading_label)

        self.formats_table.setVisible(False)

    def _fetch_video_info(self):
        """Start fetching video info in background"""
        self.fetcher = VideoInfoFetcher(self.url)
        self.fetcher.info_ready.connect(self._on_info_ready)
        self.fetcher.error_occurred.connect(self._on_fetch_error)
        self.fetcher.start()

    def _on_info_ready(self, info: Dict[str, Any]):
        """Handle fetched video info"""
        self.video_info = info
        self.loading_label.setVisible(False)
        self.formats_table.setVisible(True)

        # Enable the download button now that formats are loaded
        self.select_btn.setEnabled(True)

        # Update video details
        self.title_label.setText(info.get('title', 'Unknown'))

        duration = info.get('duration', 0)
        uploader = info.get('uploader', 'Unknown')
        views = info.get('view_count', 0)

        if duration:
            minutes = duration // 60
            seconds = duration % 60
            duration_str = f"{minutes}:{seconds:02d}"
        else:
            duration_str = "Unknown"

        meta_text = f"Duration: {duration_str} | From: {uploader}"
        if views:
            views_str = f"{views:,}" if views >= 1000 else str(views)
            meta_text += f" | {views_str} views"

        self.meta_label.setText(meta_text)

        # Load thumbnail
        thumbnail_url = info.get('thumbnail', '')
        if thumbnail_url:
            self._load_thumbnail(thumbnail_url)

        # Populate formats table
        self._populate_formats(info.get('formats', []))

    def _on_fetch_error(self, error_msg: str):
        """Handle fetch error"""
        self.loading_label.setText(f"Error: {error_msg}")
        self.loading_label.setStyleSheet("color: #e63946; font-size: 14px; padding: 20px;")

        QMessageBox.critical(
            self,
            "Error",
            f"Failed to fetch video information:\n\n{error_msg}"
        )
        self.reject()

    def _load_thumbnail(self, url: str):
        """Load video thumbnail"""
        try:
            from ..core.downloader import DownloadManager
            import aiohttp

            async def fetch_thumbnail():
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                            if response.status == 200:
                                data = await response.read()

                                # Load pixmap on main thread
                                QTimer.singleShot(0, lambda: self._display_thumbnail(data))
                except Exception as e:
                    print(f"Error loading thumbnail: {e}")

            # Run in existing event loop
            from PyQt6.QtWidgets import QApplication
            window = QApplication.activeWindow()
            if hasattr(window, '_loop'):
                asyncio.run_coroutine_threadsafe(
                    fetch_thumbnail(),
                    window._loop
                )

        except Exception as e:
            print(f"Error loading thumbnail: {e}")
            self.thumbnail_label.setText("No Image")

    def _display_thumbnail(self, data: bytes):
        """Display thumbnail image"""
        try:
            pixmap = QPixmap()
            if pixmap.loadFromData(data):
                scaled = pixmap.scaled(
                    160, 120,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.thumbnail_label.setPixmap(scaled)
            else:
                self.thumbnail_label.setText("No Image")
        except Exception:
            self.thumbnail_label.setText("No Image")

    def _populate_formats(self, formats: list):
        """Populate formats table"""
        self.formats_table.setRowCount(0)

        if not formats:
            self.formats_table.setRowCount(1)
            item = QTableWidgetItem("No formats available")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.formats_table.setItem(0, 0, item)
            self.formats_table.setSpan(0, 0, 1, 5)
            return

        # Add "Best Quality" option
        self.formats_table.insertRow(0)
        self._add_format_row(0, {
            'format_id': 'best',
            'quality': 'Best Quality',
            'ext': 'mp4',
            'filesize': 0,
            'vcodec': 'best',
            'acodec': 'best',
        }, is_best=True)

        # Add audio-only option
        self.formats_table.insertRow(1)
        self._add_format_row(1, {
            'format_id': 'bestaudio/best',  # Use format string for audio-only
            'quality': 'Audio Only',
            'ext': 'm4a',
            'filesize': 0,
            'vcodec': 'none',
            'acodec': 'best',
        }, is_audio=True)

        # Add actual formats
        for i, fmt in enumerate(formats, start=2):
            self._add_format_row(i, fmt)

        # Store all formats for filtering
        self.all_formats = formats

    def _add_format_row(self, row: int, fmt: dict, is_best: bool = False, is_audio: bool = False):
        """Add a format row to the table"""
        # Checkbox for download
        checkbox = QWidget()
        checkbox_layout = QHBoxLayout(checkbox)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        chk = QCheckBox()
        chk.setProperty("format_id", fmt.get('format_id', 'best'))
        if is_best:
            chk.setChecked(True)  # Default check best quality
            chk.setToolTip("Best quality video + audio")
        elif is_audio:
            chk.setToolTip("Audio only (no video)")
        checkbox_layout.addWidget(chk)
        self.formats_table.setCellWidget(row, 0, checkbox)

        # Quality
        quality_item = QTableWidgetItem(fmt.get('quality', 'Unknown'))
        if is_best:
            quality_item.setForeground(Qt.GlobalColor.cyan)
        self.formats_table.setItem(row, 1, quality_item)

        # Format (extension)
        format_item = QTableWidgetItem(fmt.get('ext', 'mp4').upper())
        self.formats_table.setItem(row, 2, format_item)

        # Size
        filesize = fmt.get('filesize', 0)
        if filesize and filesize > 0:
            size_mb = filesize / (1024 * 1024)
            size_str = f"{size_mb:.1f} MB"
        else:
            size_str = "Unknown"
        size_item = QTableWidgetItem(size_str)
        self.formats_table.setItem(row, 3, size_item)

        # Codec
        vcodec = fmt.get('vcodec', 'unknown')
        acodec = fmt.get('acodec', 'unknown')
        if is_best:
            codec_str = "Best Available"
        elif is_audio:
            codec_str = "Audio Only"
        else:
            codec_str = f"{vcodec} / {acodec}"
        codec_item = QTableWidgetItem(codec_str)
        self.formats_table.setItem(row, 4, codec_item)

    def _on_format_selected(self, format_id: str):
        """Handle format selection (deprecated - now uses checkboxes)"""
        pass

    def _on_filter_changed(self, index: int):
        """Handle quality filter change"""
        filter_type = self.quality_filter.currentData()

        # Show/hide rows based on filter
        for row in range(self.formats_table.rowCount()):
            should_show = False

            if row == 0:  # Best Quality
                should_show = filter_type in ['all', '1080']
            elif row == 1:  # Audio Only
                should_show = filter_type in ['all', 'audio']
            else:
                # Get quality from column 0
                quality_item = self.formats_table.item(row, 0)
                if quality_item:
                    quality_text = quality_item.text()

                    if filter_type == 'all':
                        should_show = True
                    elif filter_type == '1080':
                        should_show = '1080' in quality_text or '1440' in quality_text or '2160' in quality_text
                    elif filter_type == '720':
                        should_show = '720' in quality_text
                    elif filter_type == '480':
                        should_show = '480' in quality_text or '360' in quality_text

            self.formats_table.setRowHidden(row, not should_show)

    def _on_select_format(self):
        """Handle download button click"""
        # Collect all checked formats
        selected_formats = []

        for row in range(self.formats_table.rowCount()):
            checkbox_widget = self.formats_table.cellWidget(row, 0)
            if checkbox_widget:
                chk = checkbox_widget.findChild(QCheckBox)
                if chk and chk.isChecked():
                    format_id = chk.property("format_id")
                    if format_id:
                        selected_formats.append(format_id)

        if not selected_formats:
            QMessageBox.warning(self, "No Selection", "Please select at least one format to download.")
            return

        self.format_selected.emit(selected_formats, self.video_info)
        self.accept()

    def get_selected_formats(self) -> tuple[list, Dict[str, Any]]:
        """Get selected format IDs and video info"""
        selected_formats = []

        for row in range(self.formats_table.rowCount()):
            checkbox_widget = self.formats_table.cellWidget(row, 0)
            if checkbox_widget:
                chk = checkbox_widget.findChild(QCheckBox)
                if chk and chk.isChecked():
                    format_id = chk.property("format_id")
                    if format_id:
                        selected_formats.append(format_id)

        return selected_formats if selected_formats else ['best'], self.video_info

    def closeEvent(self, event):
        """Clean up on close"""
        if self.fetcher and self.fetcher.isRunning():
            # Signal the thread to stop gracefully
            self.fetcher.stop()

            # Wait a bit for graceful shutdown
            if not self.fetcher.wait(500):  # Wait 500ms
                # If still running, force terminate
                self.fetcher.terminate()
                self.fetcher.wait(1000)  # Wait another 1 second for termination
        event.accept()
