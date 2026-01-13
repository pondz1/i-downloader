"""
Settings dialog - application settings
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QSpinBox, QGroupBox, QFormLayout,
    QLineEdit, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..utils.constants import DEFAULT_DOWNLOAD_DIR, DEFAULT_SEGMENTS, DEFAULT_MAX_CONCURRENT


class SettingsDialog(QDialog):
    """Settings dialog for application configuration"""
    
    settings_changed = pyqtSignal(dict)  # Emitted when settings are saved
    
    def __init__(self, settings: dict = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        self._settings = settings or {}
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel("Settings")
        title.setObjectName("titleLabel")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # Download Settings
        download_group = QGroupBox("Download Settings")
        download_layout = QFormLayout(download_group)
        
        # Default download directory
        dir_layout = QHBoxLayout()
        self.download_dir_input = QLineEdit()
        self.download_dir_input.setReadOnly(True)
        dir_layout.addWidget(self.download_dir_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self._browse_folder)
        dir_layout.addWidget(browse_btn)
        
        download_layout.addRow("Default Save Location:", dir_layout)
        
        # Default segments
        self.segments_spin = QSpinBox()
        self.segments_spin.setMinimum(1)
        self.segments_spin.setMaximum(32)
        self.segments_spin.setValue(DEFAULT_SEGMENTS)
        download_layout.addRow("Default Segments:", self.segments_spin)
        
        # Max concurrent downloads
        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setMinimum(1)
        self.concurrent_spin.setMaximum(10)
        self.concurrent_spin.setValue(DEFAULT_MAX_CONCURRENT)
        download_layout.addRow("Max Concurrent Downloads:", self.concurrent_spin)
        
        layout.addWidget(download_group)
        
        # Behavior Settings
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QFormLayout(behavior_group)
        
        self.start_minimized_cb = QCheckBox("Start minimized to system tray")
        behavior_layout.addRow(self.start_minimized_cb)
        
        self.close_to_tray_cb = QCheckBox("Close to system tray instead of exiting")
        behavior_layout.addRow(self.close_to_tray_cb)
        
        self.notify_complete_cb = QCheckBox("Show notification when download completes")
        self.notify_complete_cb.setChecked(True)
        behavior_layout.addRow(self.notify_complete_cb)
        
        self.auto_start_cb = QCheckBox("Start downloads automatically when added")
        self.auto_start_cb.setChecked(True)
        behavior_layout.addRow(self.auto_start_cb)
        
        layout.addWidget(behavior_group)
        
        # Spacer
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._on_save_click)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _browse_folder(self):
        """Open folder browser dialog"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Default Download Folder",
            self.download_dir_input.text()
        )
        if folder:
            self.download_dir_input.setText(folder)
    
    def _load_settings(self):
        """Load settings into UI"""
        self.download_dir_input.setText(
            self._settings.get('download_dir', DEFAULT_DOWNLOAD_DIR)
        )
        self.segments_spin.setValue(
            self._settings.get('default_segments', DEFAULT_SEGMENTS)
        )
        self.concurrent_spin.setValue(
            self._settings.get('max_concurrent', DEFAULT_MAX_CONCURRENT)
        )
        self.start_minimized_cb.setChecked(
            self._settings.get('start_minimized', False)
        )
        self.close_to_tray_cb.setChecked(
            self._settings.get('close_to_tray', False)
        )
        self.notify_complete_cb.setChecked(
            self._settings.get('notify_complete', True)
        )
        self.auto_start_cb.setChecked(
            self._settings.get('auto_start', True)
        )
    
    def _on_save_click(self):
        """Handle save button click"""
        settings = {
            'download_dir': self.download_dir_input.text(),
            'default_segments': self.segments_spin.value(),
            'max_concurrent': self.concurrent_spin.value(),
            'start_minimized': self.start_minimized_cb.isChecked(),
            'close_to_tray': self.close_to_tray_cb.isChecked(),
            'notify_complete': self.notify_complete_cb.isChecked(),
            'auto_start': self.auto_start_cb.isChecked()
        }
        
        self.settings_changed.emit(settings)
        self.accept()
    
    def get_settings(self) -> dict:
        """Get current settings from UI"""
        return {
            'download_dir': self.download_dir_input.text(),
            'default_segments': self.segments_spin.value(),
            'max_concurrent': self.concurrent_spin.value(),
            'start_minimized': self.start_minimized_cb.isChecked(),
            'close_to_tray': self.close_to_tray_cb.isChecked(),
            'notify_complete': self.notify_complete_cb.isChecked(),
            'auto_start': self.auto_start_cb.isChecked()
        }
