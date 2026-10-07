"""
Download item widget - displays a single download in the list
"""

from PyQt6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QProgressBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

try:
    import qtawesome as qta
    HAS_QTAWESOME = True
except ImportError:
    HAS_QTAWESOME = False

from ..models.download import Download
from ..utils.constants import DownloadStatus
from ..utils.helpers import format_size, format_speed, format_time
from .styles import get_status_color


# Exact RGBA color configurations for high-DPI crisp rendering
STATUS_BADGE_CONFIG = {
    DownloadStatus.DOWNLOADING: {
        'bg': 'rgba(59, 130, 246, 0.16)',
        'text': '#60a5fa',
        'border': 'rgba(59, 130, 246, 0.35)',
    },
    DownloadStatus.COMPLETED: {
        'bg': 'rgba(16, 185, 129, 0.16)',
        'text': '#34d399',
        'border': 'rgba(16, 185, 129, 0.35)',
    },
    DownloadStatus.PAUSED: {
        'bg': 'rgba(245, 158, 11, 0.16)',
        'text': '#fbbf24',
        'border': 'rgba(245, 158, 11, 0.35)',
    },
    DownloadStatus.QUEUED: {
        'bg': 'rgba(100, 116, 139, 0.16)',
        'text': '#94a3b8',
        'border': 'rgba(100, 116, 139, 0.35)',
    },
    DownloadStatus.FAILED: {
        'bg': 'rgba(239, 68, 68, 0.16)',
        'text': '#f87171',
        'border': 'rgba(239, 68, 68, 0.35)',
    },
    DownloadStatus.CANCELLED: {
        'bg': 'rgba(100, 116, 139, 0.16)',
        'text': '#94a3b8',
        'border': 'rgba(100, 116, 139, 0.35)',
    },
}


class DownloadItemWidget(QFrame):
    """Widget representing a single download item"""

    # Signals
    pause_clicked = pyqtSignal(str)       # download_id
    resume_clicked = pyqtSignal(str)      # download_id
    cancel_clicked = pyqtSignal(str)      # download_id
    open_file_clicked = pyqtSignal(str)   # download_id
    open_folder_clicked = pyqtSignal(str) # download_id

    def __init__(self, download: Download, parent=None):
        super().__init__(parent)
        self.download = download
        self.setObjectName("downloadItemFrame")
        self._setup_ui()
        self._update_display()

    def _setup_ui(self):
        """Set up the user interface with generous vertical hierarchy"""
        self.setFixedHeight(94)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(16)

        # Left section - File info
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        # Top row: Filename + Status Badge placed together on the left
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(10)
        top_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.filename_label = QLabel(self.download.filename)
        self.filename_label.setObjectName("filenameLabel")
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.filename_label.setFont(font)
        top_row.addWidget(self.filename_label, 0, Qt.AlignmentFlag.AlignVCenter)

        self.badge_label = QLabel()
        self.badge_label.setObjectName("badgeLabel")
        self.badge_label.setFixedHeight(20)
        self.badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_row.addWidget(self.badge_label, 0, Qt.AlignmentFlag.AlignVCenter)

        top_row.addStretch(1)
        left_layout.addLayout(top_row)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        left_layout.addWidget(self.progress_bar)

        # Status info (size, speed, ETA)
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        self.status_label.setFixedHeight(18)
        left_layout.addWidget(self.status_label)

        main_layout.addLayout(left_layout, 1)

        # Right section - Action Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Pause/Resume/Open button
        self.pause_resume_btn = QPushButton("Pause")
        self.pause_resume_btn.setFixedSize(84, 32)
        self.pause_resume_btn.clicked.connect(self._on_pause_resume_click)
        button_layout.addWidget(self.pause_resume_btn)

        # Cancel button
        self.action_btn = QPushButton("Cancel")
        self.action_btn.setFixedSize(84, 32)
        self.action_btn.clicked.connect(self._on_action_click)
        button_layout.addWidget(self.action_btn)

        # Open folder button
        self.open_folder_btn = QPushButton("Folder")
        self.open_folder_btn.setFixedSize(84, 32)
        self.open_folder_btn.clicked.connect(self._on_open_folder_click)
        self.open_folder_btn.hide()
        button_layout.addWidget(self.open_folder_btn)

        # Set icons if QtAwesome is available
        self._update_button_icons()

        main_layout.addLayout(button_layout)

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

        status_color = get_status_color(self.download.status)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #1e293b;
                border: none;
                border-radius: 3px;
                height: 6px;
            }}
            QProgressBar::chunk {{
                background-color: {status_color};
                border-radius: 3px;
            }}
        """)

        # Update badge styling with RGBA
        cfg = STATUS_BADGE_CONFIG.get(self.download.status, STATUS_BADGE_CONFIG[DownloadStatus.QUEUED])
        badge_text = f"{progress}%" if self.download.status == DownloadStatus.DOWNLOADING else self.download.status.capitalize()
        self.badge_label.setText(badge_text)
        self.badge_label.setStyleSheet(f"""
            QLabel {{
                background-color: {cfg['bg']};
                color: {cfg['text']};
                border: 1px solid {cfg['border']};
                border-radius: 4px;
                padding: 1px 7px;
                font-size: 11px;
                font-weight: 600;
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
            eta_text = format_time(self.download.eta) if self.download.eta >= 0 else "--"
            self.status_label.setText(f"{size_text}  |  {speed_text}  |  ETA: {eta_text}")

        elif status == DownloadStatus.COMPLETED:
            self.status_label.setText(f"Completed  |  {format_size(self.download.total_size)}")

        elif status == DownloadStatus.PAUSED:
            size_text = f"{format_size(self.download.downloaded_size)} / {format_size(self.download.total_size)}"
            self.status_label.setText(f"Paused  |  {size_text}")

        elif status == DownloadStatus.QUEUED:
            self.status_label.setText("Waiting in queue...")

        elif status == DownloadStatus.FAILED:
            error = self.download.error_message or "Unknown error"
            if len(error) > 90:
                short_error = error[:87] + "..."
                self.status_label.setText(f"Failed: {short_error}")
                self.status_label.setToolTip(f"Failed: {error}")
            else:
                self.status_label.setText(f"Failed: {error}")
                self.status_label.setToolTip("")

        else:
            self.status_label.setText(status.capitalize())

    def _update_buttons(self):
        """Update button states based on download status"""
        status = self.download.status

        if status == DownloadStatus.DOWNLOADING:
            self.pause_resume_btn.setText("Pause")
            if HAS_QTAWESOME:
                self.pause_resume_btn.setIcon(qta.icon('fa5s.pause', color='#e2e8f0'))
            self.pause_resume_btn.show()
            self.action_btn.setText("Cancel")
            if HAS_QTAWESOME:
                self.action_btn.setIcon(qta.icon('fa5s.times', color='#e2e8f0'))
            self.action_btn.show()
            self.open_folder_btn.hide()

        elif status == DownloadStatus.PAUSED:
            self.pause_resume_btn.setText("Resume")
            if HAS_QTAWESOME:
                self.pause_resume_btn.setIcon(qta.icon('fa5s.play', color='#e2e8f0'))
            self.pause_resume_btn.show()
            self.action_btn.setText("Cancel")
            if HAS_QTAWESOME:
                self.action_btn.setIcon(qta.icon('fa5s.times', color='#e2e8f0'))
            self.action_btn.show()
            self.open_folder_btn.hide()

        elif status == DownloadStatus.COMPLETED:
            self.pause_resume_btn.setText("Open")
            if HAS_QTAWESOME:
                self.pause_resume_btn.setIcon(qta.icon('fa5s.file', color='#e2e8f0'))
            self.pause_resume_btn.show()
            self.action_btn.hide()
            self.open_folder_btn.setText("Folder")
            if HAS_QTAWESOME:
                self.open_folder_btn.setIcon(qta.icon('fa5s.folder-open', color='#e2e8f0'))
            self.open_folder_btn.show()

        elif status == DownloadStatus.QUEUED:
            self.pause_resume_btn.setText("Start")
            if HAS_QTAWESOME:
                self.pause_resume_btn.setIcon(qta.icon('fa5s.play', color='#e2e8f0'))
            self.pause_resume_btn.show()
            self.action_btn.setText("Remove")
            if HAS_QTAWESOME:
                self.action_btn.setIcon(qta.icon('fa5s.trash-alt', color='#e2e8f0'))
            self.action_btn.show()
            self.open_folder_btn.hide()

        elif status == DownloadStatus.FAILED:
            self.pause_resume_btn.setText("Retry")
            if HAS_QTAWESOME:
                self.pause_resume_btn.setIcon(qta.icon('fa5s.redo', color='#e2e8f0'))
            self.pause_resume_btn.show()
            self.action_btn.setText("Remove")
            if HAS_QTAWESOME:
                self.action_btn.setIcon(qta.icon('fa5s.trash-alt', color='#e2e8f0'))
            self.action_btn.show()
            self.open_folder_btn.hide()

    def _update_button_icons(self):
        """Set initial button icons"""
        if HAS_QTAWESOME:
            self.pause_resume_btn.setIcon(qta.icon('fa5s.pause', color='#e2e8f0'))
            self.action_btn.setIcon(qta.icon('fa5s.times', color='#e2e8f0'))
            self.open_folder_btn.setIcon(qta.icon('fa5s.folder-open', color='#e2e8f0'))

    def _on_pause_resume_click(self):
        """Handle pause/resume button click"""
        status = self.download.status
        if status == DownloadStatus.DOWNLOADING:
            self.pause_clicked.emit(self.download.id)
        elif status == DownloadStatus.PAUSED:
            self.resume_clicked.emit(self.download.id)
        elif status == DownloadStatus.COMPLETED:
            self.open_file_clicked.emit(self.download.id)
        elif status in (DownloadStatus.FAILED, DownloadStatus.QUEUED):
            self.resume_clicked.emit(self.download.id)

    def _on_action_click(self):
        """Handle cancel/remove button click"""
        self.cancel_clicked.emit(self.download.id)

    def _on_open_folder_click(self):
        """Handle open folder button click"""
        self.open_folder_clicked.emit(self.download.id)
