"""
Clipboard monitor - watches for URLs in clipboard
"""

import re
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal
from ..utils.helpers import is_valid_url


class ClipboardMonitor(QObject):
    """Monitors clipboard for URLs and emits signals when detected"""

    url_detected = pyqtSignal(str)  # Emitted when a URL is detected

    def __init__(self, parent=None):
        super().__init__(parent)
        self._enabled = False
        self._last_clipboard_text = ""
        self._clipboard = QApplication.clipboard()
        if self._clipboard:
            self._clipboard.dataChanged.connect(self._on_clipboard_changed)

    def set_enabled(self, enabled: bool):
        """Enable or disable clipboard monitoring"""
        self._enabled = enabled
        if enabled:
            # Initialize with current clipboard content
            self._last_clipboard_text = self._clipboard.text() if self._clipboard else ""

    def is_enabled(self) -> bool:
        """Check if monitoring is enabled"""
        return self._enabled

    def _on_clipboard_changed(self):
        """Handle clipboard change"""
        if not self._enabled or not self._clipboard:
            return

        text = self._clipboard.text().strip()

        # Skip if empty or same as last
        if not text or text == self._last_clipboard_text:
            return

        # Check if it's a valid URL
        if is_valid_url(text):
            self._last_clipboard_text = text
            self.url_detected.emit(text)

    def set_last_text(self, text: str):
        """Manually set the last clipboard text (to avoid immediate re-detection)"""
        self._last_clipboard_text = text
