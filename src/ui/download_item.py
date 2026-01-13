"""
Download item widget - displays a single download in the list
"""

from PyQt6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QProgressBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..models.download import Download
from ..utils.constants import DownloadStatus
from ..utils.helpers import format_size, format_speed, format_time
from .styles import get_status_color


class DownloadItemWidget(QFrame):
    """Widget representing a single download item"""
    
    # Signals
    pause_clicked = pyqtSignal(str)    # download_id
    resume_clicked = pyqtSignal(str)   # download_id
    cancel_clicked = pyqtSignal(str)   # download_id
    open_file_clicked = pyqtSignal(str)  # download_id
    open_folder_clicked = pyqtSignal(str)  # download_id
    
    def __init__(self, download: Download, parent=None):
        super().__init__(parent)
        self.download = download
        self.setObjectName("downloadItemFrame")
        self._setup_ui()
        self._update_display()
    
    def _setup_ui(self):
        """Set up the user interface"""
        self.setFixedHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(15)
        
        # Left section - File info
        left_layout = QVBoxLayout()
        left_layout.setSpacing(5)
        
        # Filename
        self.filename_label = QLabel(self.download.filename)
        self.filename_label.setObjectName("filenameLabel")
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        self.filename_label.setFont(font)
        left_layout.addWidget(self.filename_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(18)
        left_layout.addWidget(self.progress_bar)
        
        # Status info (size, speed, ETA)
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        left_layout.addWidget(self.status_label)
        
        main_layout.addLayout(left_layout, 1)
        
        # Right section - Buttons
        right_layout = QVBoxLayout()
        right_layout.setSpacing(5)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Button container
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        # Pause/Resume button
        self.pause_resume_btn = QPushButton("⏸ Pause")
        self.pause_resume_btn.setFixedWidth(90)
        self.pause_resume_btn.clicked.connect(self._on_pause_resume_click)
        button_layout.addWidget(self.pause_resume_btn)
        
        # Cancel/Open button
        self.action_btn = QPushButton("✕ Cancel")
        self.action_btn.setFixedWidth(90)
        self.action_btn.clicked.connect(self._on_action_click)
        button_layout.addWidget(self.action_btn)
        
        right_layout.addLayout(button_layout)
        
        # Open folder button (shown when completed)
        self.open_folder_btn = QPushButton("📁 Open Folder")
        self.open_folder_btn.setFixedWidth(190)
        self.open_folder_btn.clicked.connect(self._on_open_folder_click)
        self.open_folder_btn.hide()
        right_layout.addWidget(self.open_folder_btn)
        
        main_layout.addLayout(right_layout)
    
    def update_download(self, download: Download):
        """Update the download data and refresh display"""
        self.download = download
        self._update_display()
    
    def _update_display(self):
        """Update all display elements based on current download state"""
        # Update filename
        self.filename_label.setText(self.download.filename)
        
        # Update progress bar
        progress = int(self.download.progress)
        self.progress_bar.setValue(progress)
        
        # Set progress bar color based on status
        status_color = get_status_color(self.download.status)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #16213e;
                border: none;
                border-radius: 8px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {status_color};
                border-radius: 8px;
            }}
        """)
        
        # Update status label
        self._update_status_label()
        
        # Update buttons based on status
        self._update_buttons()
    
    def _update_status_label(self):
        """Update the status label text"""
        status = self.download.status
        
        if status == DownloadStatus.DOWNLOADING:
            size_text = f"{format_size(self.download.downloaded_size)} / {format_size(self.download.total_size)}"
            speed_text = format_speed(self.download.speed) if self.download.speed > 0 else "calculating..."
            eta_text = format_time(self.download.eta) if self.download.eta >= 0 else "∞"
            self.status_label.setText(f"{size_text}  •  {speed_text}  •  ETA: {eta_text}")
            
        elif status == DownloadStatus.COMPLETED:
            self.status_label.setText(f"✓ Completed  •  {format_size(self.download.total_size)}")
            
        elif status == DownloadStatus.PAUSED:
            size_text = f"{format_size(self.download.downloaded_size)} / {format_size(self.download.total_size)}"
            self.status_label.setText(f"⏸ Paused  •  {size_text}")
            
        elif status == DownloadStatus.QUEUED:
            self.status_label.setText("⏳ Waiting in queue...")
            
        elif status == DownloadStatus.FAILED:
            error = self.download.error_message or "Unknown error"
            self.status_label.setText(f"✕ Failed: {error}")
            
        else:
            self.status_label.setText(status.capitalize())
    
    def _update_buttons(self):
        """Update button states based on download status"""
        status = self.download.status
        
        if status == DownloadStatus.DOWNLOADING:
            self.pause_resume_btn.setText("⏸ Pause")
            self.pause_resume_btn.show()
            self.action_btn.setText("✕ Cancel")
            self.action_btn.show()
            self.open_folder_btn.hide()
            
        elif status == DownloadStatus.PAUSED:
            self.pause_resume_btn.setText("▶ Resume")
            self.pause_resume_btn.show()
            self.action_btn.setText("✕ Cancel")
            self.action_btn.show()
            self.open_folder_btn.hide()
            
        elif status == DownloadStatus.COMPLETED:
            self.pause_resume_btn.setText("📄 Open")
            self.pause_resume_btn.show()
            self.action_btn.hide()
            self.open_folder_btn.show()
            
        elif status == DownloadStatus.QUEUED:
            self.pause_resume_btn.setText("▶ Start")
            self.pause_resume_btn.show()
            self.action_btn.setText("✕ Remove")
            self.action_btn.show()
            self.open_folder_btn.hide()
            
        elif status == DownloadStatus.FAILED:
            self.pause_resume_btn.setText("🔄 Retry")
            self.pause_resume_btn.show()
            self.action_btn.setText("✕ Remove")
            self.action_btn.show()
            self.open_folder_btn.hide()
    
    def _on_pause_resume_click(self):
        """Handle pause/resume button click"""
        status = self.download.status
        
        if status == DownloadStatus.DOWNLOADING:
            self.pause_clicked.emit(self.download.id)
        elif status in (DownloadStatus.PAUSED, DownloadStatus.QUEUED, DownloadStatus.FAILED):
            self.resume_clicked.emit(self.download.id)
        elif status == DownloadStatus.COMPLETED:
            self.open_file_clicked.emit(self.download.id)
    
    def _on_action_click(self):
        """Handle action button click"""
        self.cancel_clicked.emit(self.download.id)
    
    def _on_open_folder_click(self):
        """Handle open folder button click"""
        self.open_folder_clicked.emit(self.download.id)
