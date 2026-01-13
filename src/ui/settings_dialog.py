"""
Settings dialog - application settings
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QSpinBox, QGroupBox, QFormLayout,
    QLineEdit, QCheckBox, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

try:
    import qtawesome as qta
    HAS_QTAWESOME = True
except ImportError:
    HAS_QTAWESOME = False

from ..utils.constants import DEFAULT_DOWNLOAD_DIR, DEFAULT_SEGMENTS, DEFAULT_MAX_CONCURRENT


class StyledSpinBox(QWidget):
    """Custom SpinBox with visible +/- buttons"""
    
    valueChanged = pyqtSignal(int)
    
    def __init__(self, min_val=1, max_val=100, value=1, parent=None):
        super().__init__(parent)
        self._min = min_val
        self._max = max_val
        self._value = value
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Minus button
        self.minus_btn = QPushButton("-")
        self.minus_btn.setFixedSize(32, 32)
        self.minus_btn.clicked.connect(self._decrement)
        if HAS_QTAWESOME:
            self.minus_btn.setIcon(qta.icon('fa5s.minus', color='#eaeaea'))
            self.minus_btn.setText("")
        layout.addWidget(self.minus_btn)
        
        # Value display
        self.value_label = QLineEdit(str(self._value))
        self.value_label.setFixedWidth(60)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setReadOnly(True)
        self.value_label.setStyleSheet("""
            QLineEdit {
                background-color: #16213e;
                border: 2px solid #0f3460;
                border-radius: 6px;
                padding: 5px;
                color: #eaeaea;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.value_label)
        
        # Plus button
        self.plus_btn = QPushButton("+")
        self.plus_btn.setFixedSize(32, 32)
        self.plus_btn.clicked.connect(self._increment)
        if HAS_QTAWESOME:
            self.plus_btn.setIcon(qta.icon('fa5s.plus', color='#eaeaea'))
            self.plus_btn.setText("")
        layout.addWidget(self.plus_btn)
    
    def _increment(self):
        if self._value < self._max:
            self._value += 1
            self.value_label.setText(str(self._value))
            self.valueChanged.emit(self._value)
    
    def _decrement(self):
        if self._value > self._min:
            self._value -= 1
            self.value_label.setText(str(self._value))
            self.valueChanged.emit(self._value)
    
    def value(self):
        return self._value
    
    def setValue(self, val):
        self._value = max(self._min, min(self._max, val))
        self.value_label.setText(str(self._value))
    
    def setMinimum(self, val):
        self._min = val
    
    def setMaximum(self, val):
        self._max = val


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
        
        # Default segments - using custom SpinBox
        self.segments_spin = StyledSpinBox(min_val=1, max_val=32, value=DEFAULT_SEGMENTS)
        download_layout.addRow("Default Segments:", self.segments_spin)
        
        # Max concurrent downloads - using custom SpinBox
        self.concurrent_spin = StyledSpinBox(min_val=1, max_val=10, value=DEFAULT_MAX_CONCURRENT)
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
