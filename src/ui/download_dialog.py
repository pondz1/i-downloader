"""
New download dialog - for adding new downloads
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QSpinBox, QGroupBox, QFormLayout,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..utils.constants import DEFAULT_DOWNLOAD_DIR, DEFAULT_SEGMENTS
from ..utils.helpers import is_valid_url


class DownloadDialog(QDialog):
    """Dialog for adding a new download"""
    
    # Signal emitted when download is confirmed
    download_requested = pyqtSignal(str, str, int)  # url, save_dir, num_segments
    
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
        self.url_input.textChanged.connect(self._validate_url)
        url_layout.addWidget(self.url_input)
        
        self.url_status = QLabel()
        self.url_status.setStyleSheet("color: #888; font-size: 11px;")
        url_layout.addWidget(self.url_status)
        
        layout.addWidget(url_group)
        
        # Save Location Section
        save_group = QGroupBox("Save Location")
        save_layout = QHBoxLayout(save_group)
        
        self.save_path_input = QLineEdit()
        self.save_path_input.setText(DEFAULT_DOWNLOAD_DIR)
        self.save_path_input.setReadOnly(True)
        save_layout.addWidget(self.save_path_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self._browse_folder)
        save_layout.addWidget(browse_btn)
        
        layout.addWidget(save_group)
        
        # Advanced Options Section
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QFormLayout(advanced_group)
        
        # Number of segments
        self.segments_spin = QSpinBox()
        self.segments_spin.setMinimum(1)
        self.segments_spin.setMaximum(32)
        self.segments_spin.setValue(DEFAULT_SEGMENTS)
        self.segments_spin.setToolTip("More segments can increase download speed, but too many may cause issues")
        advanced_layout.addRow("Download Segments:", self.segments_spin)
        
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
        self._validate_url()
    
    def _validate_url(self):
        """Validate the URL input"""
        url = self.url_input.text().strip()
        
        if not url:
            self.url_status.setText("Enter a download URL")
            self.url_status.setStyleSheet("color: #888; font-size: 11px;")
            self.download_btn.setEnabled(False)
        elif is_valid_url(url):
            self.url_status.setText("✓ Valid URL")
            self.url_status.setStyleSheet("color: #4CAF50; font-size: 11px;")
            self.download_btn.setEnabled(True)
        else:
            self.url_status.setText("✕ Invalid URL (must start with http:// or https://)")
            self.url_status.setStyleSheet("color: #F44336; font-size: 11px;")
            self.download_btn.setEnabled(False)
    
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
        
        # Validate
        if not is_valid_url(url):
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid download URL.")
            return
        
        if not os.path.isdir(save_dir):
            QMessageBox.warning(self, "Invalid Path", "The save location does not exist.")
            return
        
        # Emit signal and close
        self.download_requested.emit(url, save_dir, num_segments)
        self.accept()
    
    def get_download_info(self) -> tuple:
        """Get the download information"""
        return (
            self.url_input.text().strip(),
            self.save_path_input.text().strip(),
            self.segments_spin.value()
        )
