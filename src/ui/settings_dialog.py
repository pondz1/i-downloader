"""
Settings dialog - application settings
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QSpinBox, QGroupBox, QFormLayout,
    QLineEdit, QCheckBox, QWidget, QComboBox, QTabWidget, QScrollArea
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
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Settings")
        title.setObjectName("titleLabel")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #0f3460;
                border-radius: 8px;
                background-color: #1a1a2e;
            }
            QTabBar::tab {
                background-color: #16213e;
                color: #eaeaea;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #0f3460;
                color: #4cc9f0;
            }
            QTabBar::tab:hover {
                background-color: #1a1a2e;
            }
        """)
        layout.addWidget(self.tab_widget)

        # Create tabs
        self._create_general_tab()
        self._create_network_tab()
        self._create_advanced_tab()

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

    def _create_general_tab(self):
        """Create General settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

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

        self.watch_clipboard_cb = QCheckBox("Watch clipboard for download URLs")
        behavior_layout.addRow(self.watch_clipboard_cb)

        layout.addWidget(behavior_group)

        layout.addStretch()

        self.tab_widget.addTab(tab, "General")

    def _create_network_tab(self):
        """Create Network settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Bandwidth Settings
        bandwidth_group = QGroupBox("Bandwidth")
        bandwidth_layout = QFormLayout(bandwidth_group)

        self.limit_speed_cb = QCheckBox("Limit download speed")
        self.limit_speed_cb.toggled.connect(self._on_limit_speed_toggled)
        bandwidth_layout.addRow(self.limit_speed_cb)

        # Speed limit input
        speed_limit_layout = QHBoxLayout()
        self.speed_limit_input = QLineEdit()
        self.speed_limit_input.setText("0")
        self.speed_limit_input.setEnabled(False)
        speed_limit_layout.addWidget(self.speed_limit_input)

        self.speed_limit_unit = QComboBox()
        self.speed_limit_unit.addItem("KB/s", 1024)
        self.speed_limit_unit.addItem("MB/s", 1024 * 1024)
        self.speed_limit_unit.setEnabled(False)
        speed_limit_layout.addWidget(self.speed_limit_unit)

        self.speed_limit_unlimited = QLabel("(0 = unlimited)")
        self.speed_limit_unlimited.setStyleSheet("color: #888; font-size: 11px;")
        speed_limit_layout.addWidget(self.speed_limit_unlimited)

        bandwidth_layout.addRow("Speed Limit:", speed_limit_layout)

        layout.addWidget(bandwidth_group)

        # Proxy Settings
        proxy_group = QGroupBox("Proxy")
        proxy_layout = QFormLayout(proxy_group)

        self.proxy_enabled_cb = QCheckBox("Enable proxy")
        self.proxy_enabled_cb.toggled.connect(self._on_proxy_enabled_toggled)
        proxy_layout.addRow(self.proxy_enabled_cb)

        # Proxy type
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItem("HTTP", "http")
        self.proxy_type_combo.addItem("HTTPS", "https")
        self.proxy_type_combo.addItem("SOCKS4", "socks4")
        self.proxy_type_combo.addItem("SOCKS5", "socks5")
        self.proxy_type_combo.setEnabled(False)
        proxy_layout.addRow("Proxy Type:", self.proxy_type_combo)

        # Proxy host
        self.proxy_host_input = QLineEdit()
        self.proxy_host_input.setPlaceholderText("proxy.example.com")
        self.proxy_host_input.setEnabled(False)
        proxy_layout.addRow("Proxy Host:", self.proxy_host_input)

        # Proxy port
        self.proxy_port_input = QLineEdit()
        self.proxy_port_input.setPlaceholderText("8080")
        self.proxy_port_input.setEnabled(False)
        proxy_layout.addRow("Proxy Port:", self.proxy_port_input)

        # Proxy username (optional)
        self.proxy_username_input = QLineEdit()
        self.proxy_username_input.setPlaceholderText("(optional)")
        self.proxy_username_input.setEnabled(False)
        proxy_layout.addRow("Username:", self.proxy_username_input)

        # Proxy password (optional)
        self.proxy_password_input = QLineEdit()
        self.proxy_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.proxy_password_input.setPlaceholderText("(optional)")
        self.proxy_password_input.setEnabled(False)
        proxy_layout.addRow("Password:", self.proxy_password_input)

        layout.addWidget(proxy_group)

        layout.addStretch()

        self.tab_widget.addTab(tab, "Network")

    def _create_advanced_tab(self):
        """Create Advanced settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Retry Settings
        retry_group = QGroupBox("Auto-Retry")
        retry_layout = QFormLayout(retry_group)

        self.enable_retry_cb = QCheckBox("Enable auto-retry on failure")
        retry_layout.addRow(self.enable_retry_cb)

        # Max retries - using custom SpinBox
        self.max_retries_spin = StyledSpinBox(min_val=0, max_val=10, value=3)
        self.max_retries_spin.setToolTip("Number of times to retry a failed download (0 = no retry)")
        retry_layout.addRow("Max Retries:", self.max_retries_spin)

        # Retry delay input
        retry_delay_layout = QHBoxLayout()
        self.retry_delay_input = QLineEdit()
        self.retry_delay_input.setText("5")
        retry_delay_layout.addWidget(self.retry_delay_input)

        self.retry_delay_unit = QLabel("seconds")
        retry_delay_layout.addWidget(self.retry_delay_unit)

        self.retry_delay_hint = QLabel("(before first retry)")
        self.retry_delay_hint.setStyleSheet("color: #888; font-size: 11px;")
        retry_delay_layout.addWidget(self.retry_delay_hint)

        retry_layout.addRow("Retry Delay:", retry_delay_layout)

        # Retry backoff input
        backoff_layout = QHBoxLayout()
        self.retry_backoff_input = QLineEdit()
        self.retry_backoff_input.setText("2")
        backoff_layout.addWidget(self.retry_backoff_input)

        self.retry_backoff_unit = QLabel("x (multiplier)")
        self.retry_backoff_unit.setStyleSheet("color: #888; font-size: 11px;")
        backoff_layout.addWidget(self.retry_backoff_unit)

        retry_layout.addRow("Backoff:", backoff_layout)

        layout.addWidget(retry_group)

        layout.addStretch()

        self.tab_widget.addTab(tab, "Advanced")
    
    def _browse_folder(self):
        """Open folder browser dialog"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Default Download Folder",
            self.download_dir_input.text()
        )
        if folder:
            self.download_dir_input.setText(folder)

    def _on_limit_speed_toggled(self, checked: bool):
        """Handle limit speed checkbox toggle"""
        self.speed_limit_input.setEnabled(checked)
        self.speed_limit_unit.setEnabled(checked)

    def _on_proxy_enabled_toggled(self, checked: bool):
        """Handle proxy enabled checkbox toggle"""
        self.proxy_type_combo.setEnabled(checked)
        self.proxy_host_input.setEnabled(checked)
        self.proxy_port_input.setEnabled(checked)
        self.proxy_username_input.setEnabled(checked)
        self.proxy_password_input.setEnabled(checked)

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

        # Load bandwidth limit settings
        rate_limit = self._settings.get('rate_limit', 0)  # 0 = unlimited
        if rate_limit > 0:
            self.limit_speed_cb.setChecked(True)
            # Determine unit (KB or MB)
            if rate_limit >= 1024 * 1024:
                self.speed_limit_unit.setCurrentIndex(1)  # MB/s
                self.speed_limit_input.setText(str(rate_limit // (1024 * 1024)))
            else:
                self.speed_limit_unit.setCurrentIndex(0)  # KB/s
                self.speed_limit_input.setText(str(rate_limit // 1024))
        else:
            self.limit_speed_cb.setChecked(False)
            self.speed_limit_input.setText("0")

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
        self.watch_clipboard_cb.setChecked(
            self._settings.get('watch_clipboard', False)
        )

        # Load retry settings
        self.enable_retry_cb.setChecked(
            self._settings.get('enable_retry', True)
        )
        self.max_retries_spin.setValue(
            self._settings.get('max_retries', 3)
        )
        self.retry_delay_input.setText(
            str(self._settings.get('retry_delay', 5))
        )
        self.retry_backoff_input.setText(
            str(self._settings.get('retry_backoff', 2.0))
        )

        # Load proxy settings
        self.proxy_enabled_cb.setChecked(
            self._settings.get('proxy_enabled', False)
        )
        self.proxy_type_combo.setCurrentIndex(
            0 if self._settings.get('proxy_type', 'http') == 'http' else
            1 if self._settings.get('proxy_type', 'http') == 'https' else
            2 if self._settings.get('proxy_type', 'http') == 'socks4' else 3
        )
        self.proxy_host_input.setText(
            self._settings.get('proxy_host', '')
        )
        self.proxy_port_input.setText(
            str(self._settings.get('proxy_port', ''))
        )
        self.proxy_username_input.setText(
            self._settings.get('proxy_username', '')
        )
        self.proxy_password_input.setText(
            self._settings.get('proxy_password', '')
        )

    def _on_save_click(self):
        """Handle save button click"""
        # Calculate rate limit in bytes per second
        if self.limit_speed_cb.isChecked():
            try:
                value = float(self.speed_limit_input.text())
                unit_multiplier = self.speed_limit_unit.currentData()
                rate_limit = int(value * unit_multiplier)
            except ValueError:
                rate_limit = 0
        else:
            rate_limit = 0

        settings = {
            'download_dir': self.download_dir_input.text(),
            'default_segments': self.segments_spin.value(),
            'max_concurrent': self.concurrent_spin.value(),
            'rate_limit': rate_limit,
            'start_minimized': self.start_minimized_cb.isChecked(),
            'close_to_tray': self.close_to_tray_cb.isChecked(),
            'notify_complete': self.notify_complete_cb.isChecked(),
            'auto_start': self.auto_start_cb.isChecked(),
            'watch_clipboard': self.watch_clipboard_cb.isChecked(),
            # Retry settings
            'enable_retry': self.enable_retry_cb.isChecked(),
            'max_retries': self.max_retries_spin.value(),
            'retry_delay': float(self.retry_delay_input.text()),
            'retry_backoff': float(self.retry_backoff_input.text()),
            # Proxy settings
            'proxy_enabled': self.proxy_enabled_cb.isChecked(),
            'proxy_type': self.proxy_type_combo.currentData(),
            'proxy_host': self.proxy_host_input.text().strip(),
            'proxy_port': self.proxy_port_input.text().strip(),
            'proxy_username': self.proxy_username_input.text().strip(),
            'proxy_password': self.proxy_password_input.text()
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
            'auto_start': self.auto_start_cb.isChecked(),
            'watch_clipboard': self.watch_clipboard_cb.isChecked()
        }
