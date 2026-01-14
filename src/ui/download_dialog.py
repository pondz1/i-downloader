"""
New download dialog - for adding new downloads
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QSpinBox, QGroupBox, QFormLayout,
    QMessageBox, QCheckBox, QDateTimeEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime
from PyQt6.QtGui import QFont

from ..utils.constants import DEFAULT_DOWNLOAD_DIR, DEFAULT_SEGMENTS
from ..utils.helpers import is_valid_url
from ..utils.categories import get_all_categories, get_category_save_path, get_category_name, get_category_from_filename
from .settings_dialog import StyledSpinBox


class DownloadDialog(QDialog):
    """Dialog for adding a new download"""

    # Signal emitted when download is confirmed
    download_requested = pyqtSignal(str, str, int, str, object)  # url, save_dir, num_segments, category, scheduled_time

    def __init__(self, parent=None, url: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Add New Download")
        self.setMinimumWidth(550)
        self.setModal(True)
        
        self._initial_url = url
        self._setup_ui()
        
        if url:
            self.url_input.setText(url)
    
    def _setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel("Add New Download")
        title.setObjectName("titleLabel")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # URL Section
        url_group = QGroupBox("Download URL")
        url_layout = QVBoxLayout(url_group)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter or paste download URL here...")
        self.url_input.textChanged.connect(self._on_url_changed)
        url_layout.addWidget(self.url_input)
        
        self.url_status = QLabel()
        self.url_status.setStyleSheet("color: #888; font-size: 11px;")
        url_layout.addWidget(self.url_status)
        
        layout.addWidget(url_group)
        
        # Save Location Section
        save_group = QGroupBox("Save Location")
        save_layout = QVBoxLayout(save_group)

        # Category row
        category_row = QHBoxLayout()
        category_label = QLabel("Category:")
        category_row.addWidget(category_label)

        from PyQt6.QtWidgets import QComboBox
        self.category_combo = QComboBox()
        for key, category in get_all_categories().items():
            self.category_combo.addItem(category.name, key)
        # Set "Auto" as default (first item)
        self.category_combo.setCurrentIndex(0)
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        category_row.addWidget(self.category_combo)
        category_row.addStretch()
        save_layout.addLayout(category_row)

        # Folder path row
        path_row = QHBoxLayout()
        self.save_path_input = QLineEdit()
        self.save_path_input.setText(DEFAULT_DOWNLOAD_DIR)
        self.save_path_input.setReadOnly(True)
        path_row.addWidget(self.save_path_input)

        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self._browse_folder)
        path_row.addWidget(browse_btn)

        save_layout.addLayout(path_row)

        layout.addWidget(save_group)
        
        # Advanced Options Section
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QFormLayout(advanced_group)

        # Number of segments - using custom SpinBox
        self.segments_spin = StyledSpinBox(min_val=1, max_val=32, value=DEFAULT_SEGMENTS)
        self.segments_spin.setToolTip("More segments can increase download speed, but too many may cause issues")
        advanced_layout.addRow("Download Segments:", self.segments_spin)

        # Schedule download option
        schedule_row = QHBoxLayout()
        self.schedule_cb = QCheckBox("Schedule this download for later")
        self.schedule_cb.toggled.connect(self._on_schedule_toggled)
        schedule_row.addWidget(self.schedule_cb)
        advanced_layout.addRow(schedule_row)

        # Schedule datetime picker
        self.schedule_datetime = QDateTimeEdit()
        self.schedule_datetime.setDateTime(QDateTime.currentDateTime().addSecs(3600))  # Default: 1 hour from now
        self.schedule_datetime.setCalendarPopup(True)
        self.schedule_datetime.setEnabled(False)
        self.schedule_datetime.setMinimumDateTime(QDateTime.currentDateTime())
        advanced_layout.addRow("Start Time:", self.schedule_datetime)

        layout.addWidget(advanced_group)

        # Spacer
        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.download_btn = QPushButton("Download")
        self.download_btn.setObjectName("primaryButton")
        self.download_btn.clicked.connect(self._on_download_click)
        self.download_btn.setEnabled(False)
        button_layout.addWidget(self.download_btn)

        layout.addLayout(button_layout)

        # Initial validation
        self._on_url_changed()

    def _on_url_changed(self):
        """Handle URL text change - validate and auto-detect category"""
        url = self.url_input.text().strip()

        if not url:
            self.url_status.setText("Enter a download URL")
            self.url_status.setStyleSheet("color: #888; font-size: 11px;")
            self.download_btn.setEnabled(False)
        elif is_valid_url(url):
            self.url_status.setText("✓ Valid URL")
            self.url_status.setStyleSheet("color: #4CAF50; font-size: 11px;")
            self.download_btn.setEnabled(True)

            # Auto-detect category from URL
            self._auto_detect_category(url)
        else:
            self.url_status.setText("✕ Invalid URL (must start with http:// or https://)")
            self.url_status.setStyleSheet("color: #F44336; font-size: 11px;")
            self.download_btn.setEnabled(False)

    def _auto_detect_category(self, url: str):
        """Auto-detect category from URL and update dropdown"""
        from urllib.parse import unquote
        import re

        # Extract filename from URL
        filename = ""
        path = url.split('?')[0]  # Remove query string
        if '/' in path:
            filename = unquote(path.split('/')[-1])

        # If no filename in URL, try to extract from Content-Disposition hint in URL
        if not filename or '.' not in filename:
            # Try to find filename in common URL patterns
            match = re.search(r'/([^/]+\.\w+)(?:\?|$)', url)
            if match:
                filename = unquote(match.group(1))

        # Detect category
        detected_category = get_category_from_filename(filename) if filename else "all"

        # Update category dropdown
        for i in range(self.category_combo.count()):
            if self.category_combo.itemData(i) == detected_category:
                self.category_combo.setCurrentIndex(i)
                break

    def _on_schedule_toggled(self, checked: bool):
        """Handle schedule checkbox toggle"""
        self.schedule_datetime.setEnabled(checked)
        if checked:
            self.download_btn.setText("Schedule")
        else:
            self.download_btn.setText("Download")

    def _on_category_changed(self):
        """Handle category change"""
        category_key = self.category_combo.currentData()
        current_path = self.save_path_input.text()

        # Update path to include category subfolder
        # Get base path (remove existing category folder if any)
        base_path = current_path
        for category in get_all_categories().values():
            if category.folder_name and base_path.endswith(category.folder_name):
                base_path = str(Path(base_path).parent.parent)
                break

        new_path = get_category_save_path(base_path, category_key)
        self.save_path_input.setText(new_path)
    
    def _browse_folder(self):
        """Open folder browser dialog"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Download Folder",
            self.save_path_input.text()
        )
        if folder:
            self.save_path_input.setText(folder)
    
    def _on_download_click(self):
        """Handle download button click"""
        url = self.url_input.text().strip()
        save_dir = self.save_path_input.text().strip()
        num_segments = self.segments_spin.value()
        category = self.category_combo.currentData()

        # Validate
        if not is_valid_url(url):
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid download URL.")
            return

        if not os.path.isdir(save_dir):
            QMessageBox.warning(self, "Invalid Path", "The save location does not exist.")
            return

        # Get scheduled time if scheduling is enabled
        scheduled_time = None
        if self.schedule_cb.isChecked():
            scheduled_time = self.schedule_datetime.dateTime().toPyDateTime()

        # Emit signal and close
        self.download_requested.emit(url, save_dir, num_segments, category, scheduled_time)
        self.accept()
    
    def get_download_info(self) -> tuple:
        """Get the download information"""
        return (
            self.url_input.text().strip(),
            self.save_path_input.text().strip(),
            self.segments_spin.value()
        )
