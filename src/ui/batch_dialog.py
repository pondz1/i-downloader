"""
Batch import dialog - for importing multiple URLs
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QPlainTextEdit, QGroupBox, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from pathlib import Path

from ..utils.constants import DEFAULT_DOWNLOAD_DIR, DEFAULT_SEGMENTS
from ..utils.helpers import is_valid_url
from ..utils.categories import get_all_categories, get_category_from_filename


class BatchImportDialog(QDialog):
    """Dialog for batch importing multiple downloads"""

    # Signal emitted with list of (url, save_dir, num_segments, category)
    downloads_requested = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Batch Import URLs")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setModal(True)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)

        # Title
        title = QLabel("Batch Import URLs")
        title.setObjectName("titleLabel")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        # Description
        desc = QLabel("Enter one URL per line. All URLs will use the same settings.")
        desc.setStyleSheet("color: #888;")
        layout.addWidget(desc)

        # URLs Section
        urls_group = QGroupBox("Download URLs")
        urls_layout = QVBoxLayout(urls_group)

        self.urls_text = QPlainTextEdit()
        self.urls_text.setPlaceholderText(
            "https://example.com/file1.zip\n"
            "https://example.com/file2.mp4\n"
            "https://example.com/file3.pdf\n\n"
            "One URL per line..."
        )
        urls_layout.addWidget(self.urls_text)

        # Button row for URLs
        urls_btn_row = QHBoxLayout()

        import_file_btn = QPushButton("Import from File")
        import_file_btn.clicked.connect(self._import_from_file)
        urls_btn_row.addWidget(import_file_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.urls_text.clear)
        urls_btn_row.addWidget(clear_btn)

        urls_btn_row.addStretch()

        self.url_count_label = QLabel("0 URLs")
        self.url_count_label.setStyleSheet("color: #888;")
        urls_btn_row.addWidget(self.url_count_label)

        urls_layout.addLayout(urls_btn_row)

        layout.addWidget(urls_group)

        # Connect text change to update count
        self.urls_text.textChanged.connect(self._update_url_count)

        # Common Settings Section
        settings_group = QGroupBox("Common Settings for All Downloads")
        settings_layout = QVBoxLayout(settings_group)

        # Save location
        save_row = QHBoxLayout()
        save_label = QLabel("Save Location:")
        save_label.setFixedWidth(100)
        save_row.addWidget(save_label)

        from PyQt6.QtWidgets import QLineEdit, QComboBox
        self.save_path_input = QLineEdit()
        self.save_path_input.setText(DEFAULT_DOWNLOAD_DIR)
        self.save_path_input.setReadOnly(True)
        save_row.addWidget(self.save_path_input)

        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self._browse_folder)
        save_row.addWidget(browse_btn)

        settings_layout.addLayout(save_row)

        # Category row
        category_row = QHBoxLayout()
        category_label = QLabel("Category:")
        category_label.setFixedWidth(100)
        category_row.addWidget(category_label)

        self.category_combo = QComboBox()
        for key, category in get_all_categories().items():
            self.category_combo.addItem(category.name, key)
        # Set "Auto" as default (first item)
        self.category_combo.setCurrentIndex(0)
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        category_row.addWidget(self.category_combo)
        category_row.addStretch()
        settings_layout.addLayout(category_row)

        # Segments row
        segments_row = QHBoxLayout()
        segments_label = QLabel("Segments:")
        segments_label.setFixedWidth(100)
        segments_row.addWidget(segments_label)

        from .settings_dialog import StyledSpinBox
        self.segments_spin = StyledSpinBox(min_val=1, max_val=32, value=DEFAULT_SEGMENTS)
        segments_row.addWidget(self.segments_spin)
        segments_row.addStretch()
        settings_layout.addLayout(segments_row)

        layout.addWidget(settings_group)

        # Spacer
        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.import_btn = QPushButton("Import All")
        self.import_btn.setObjectName("primaryButton")
        self.import_btn.clicked.connect(self._on_import_click)
        self.import_btn.setEnabled(False)
        button_layout.addWidget(self.import_btn)

        layout.addLayout(button_layout)

    def _update_url_count(self):
        """Update the URL count label"""
        text = self.urls_text.toPlainText().strip()
        urls = [line.strip() for line in text.split('\n') if line.strip() and is_valid_url(line.strip())]
        self.url_count_label.setText(f"{len(urls)} URL{'s' if len(urls) != 1 else ''}")
        self.import_btn.setEnabled(len(urls) > 0)

    def _on_category_changed(self):
        """Handle category change"""
        from ..utils.categories import get_category_save_path
        category_key = self.category_combo.currentData()
        current_path = self.save_path_input.text()

        # Update path to include category subfolder
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

    def _import_from_file(self):
        """Import URLs from a text file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select URL List File",
            "",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.urls_text.setPlainText(content)
            except Exception as e:
                QMessageBox.warning(self, "Import Failed", f"Failed to read file:\n{str(e)}")

    def _on_import_click(self):
        """Handle import button click"""
        text = self.urls_text.toPlainText().strip()

        if not text:
            QMessageBox.warning(self, "No URLs", "Please enter at least one URL.")
            return

        # Parse URLs
        urls = [line.strip() for line in text.split('\n') if line.strip()]

        # Validate URLs
        valid_urls = []
        invalid_urls = []

        for url in urls:
            if is_valid_url(url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)

        # Show warning if there are invalid URLs
        if invalid_urls:
            reply = QMessageBox.question(
                self,
                "Invalid URLs Detected",
                f"{len(invalid_urls)} URL(s) are invalid and will be skipped.\n\nDo you want to continue with the {len(valid_urls)} valid URL(s)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                return

        if not valid_urls:
            QMessageBox.warning(self, "No Valid URLs", "No valid URLs found to import.")
            return

        # Prepare download info
        save_dir = self.save_path_input.text()
        num_segments = self.segments_spin.value()
        category = self.category_combo.currentData()

        # Ensure directory exists
        os.makedirs(save_dir, exist_ok=True)

        # Create download list
        downloads = [(url, save_dir, num_segments, category) for url in valid_urls]

        # Emit signal
        self.downloads_requested.emit(downloads)
        self.accept()
