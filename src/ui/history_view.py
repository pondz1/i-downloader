"""
Download history view widget
"""

from typing import Optional, List
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..models.download import Download
from ..utils.helpers import format_size
from ..utils.constants import DownloadStatus


class HistoryViewWidget(QWidget):
    """Widget for displaying download history"""

    # Signals
    open_file_requested = pyqtSignal(str)  # download_id
    open_folder_requested = pyqtSignal(str)  # download_id
    delete_requested = pyqtSignal(str)  # download_id
    retry_requested = pyqtSignal(str)  # download_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._downloads: List[Download] = []
        self._filtered_downloads: List[Download] = []
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Search and filter bar
        filter_layout = QHBoxLayout()

        # Search input
        search_label = QLabel("Search:")
        filter_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by filename or URL...")
        self.search_input.textChanged.connect(self._on_search_changed)
        filter_layout.addWidget(self.search_input)

        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Status", "all")
        self.status_filter.addItem("Completed", DownloadStatus.COMPLETED)
        self.status_filter.addItem("Failed", DownloadStatus.FAILED)
        self.status_filter.addItem("Cancelled", DownloadStatus.CANCELLED)
        self.status_filter.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.status_filter)

        # Clear button
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self._on_clear_history)
        filter_layout.addWidget(clear_btn)

        layout.addLayout(filter_layout)

        # History table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Filename", "Status", "Size", "Date", "Speed", "Error", "Checksum"
        ])

        # Configure table
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Filename
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Date
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Speed
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Error
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Checksum

        self.table.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self.table)

        # Status label
        self.status_label = QLabel("No downloads in history")
        self.status_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self.status_label)

    def set_downloads(self, downloads: List[Download]):
        """Set the downloads to display"""
        self._downloads = downloads
        self._apply_filters()

    def _apply_filters(self):
        """Apply search and status filters"""
        search_text = self.search_input.text().strip().lower()
        status_filter = self.status_filter.currentData()

        # Filter downloads
        filtered = []
        for download in self._downloads:
            # Status filter
            if status_filter != "all" and download.status != status_filter:
                continue

            # Search filter
            if search_text:
                if (search_text not in download.filename.lower() and
                    search_text not in download.url.lower()):
                    continue

            filtered.append(download)

        self._filtered_downloads = filtered
        self._update_table()

    def _update_table(self):
        """Update the table with filtered downloads"""
        self.table.setRowCount(len(self._filtered_downloads))

        for row, download in enumerate(self._filtered_downloads):
            # Filename
            filename_item = QTableWidgetItem(download.filename)
            self.table.setItem(row, 0, filename_item)

            # Status
            status_item = QTableWidgetItem(download.status.capitalize())
            if download.status == DownloadStatus.COMPLETED:
                status_item.setForeground(Qt.GlobalColor.green)
            elif download.status == DownloadStatus.FAILED:
                status_item.setForeground(Qt.GlobalColor.red)
            elif download.status == DownloadStatus.CANCELLED:
                status_item.setForeground(Qt.GlobalColor.gray)
            self.table.setItem(row, 1, status_item)

            # Size
            size_text = format_size(download.total_size) if download.total_size > 0 else "N/A"
            size_item = QTableWidgetItem(size_text)
            self.table.setItem(row, 2, size_item)

            # Date
            date_text = download.created_at.strftime("%Y-%m-%d %H:%M")
            date_item = QTableWidgetItem(date_text)
            self.table.setItem(row, 3, date_item)

            # Speed (for completed downloads)
            if download.status == DownloadStatus.COMPLETED and download.speed > 0:
                speed_text = f"{download.speed / 1024 / 1024:.1f} MB/s"
            else:
                speed_text = "N/A"
            speed_item = QTableWidgetItem(speed_text)
            self.table.setItem(row, 4, speed_item)

            # Error message (for failed downloads)
            error_text = download.error_message[:50] + "..." if len(download.error_message) > 50 else download.error_message
            error_item = QTableWidgetItem(error_text if download.error_message else "")
            if download.error_message:
                error_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 5, error_item)

            # Checksum status
            if download.checksum:
                checksum_text = f"✓ {download.checksum_algorithm.upper()}"
                checksum_item = QTableWidgetItem(checksum_text)
                checksum_item.setForeground(Qt.GlobalColor.green)
            elif download.expected_checksum:
                checksum_text = f"✗ Failed"
                checksum_item = QTableWidgetItem(checksum_text)
                checksum_item.setForeground(Qt.GlobalColor.red)
            else:
                checksum_item = QTableWidgetItem("")
            self.table.setItem(row, 6, checksum_item)

        # Update status label
        count = len(self._filtered_downloads)
        if count == 0:
            self.status_label.setText("No downloads match the current filters")
        else:
            self.status_label.setText(f"Showing {count} download{'s' if count != 1 else ''}")

    def _on_search_changed(self):
        """Handle search text change"""
        self._apply_filters()

    def _on_filter_changed(self):
        """Handle status filter change"""
        self._apply_filters()

    def _on_clear_history(self):
        """Handle clear history button"""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all download history? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Emit delete signal for all downloads
            for download in self._downloads:
                self.delete_requested.emit(download.id)

    def _show_context_menu(self, position):
        """Show right-click context menu"""
        item = self.table.itemAt(position)
        if not item:
            return

        row = item.row()
        download = self._filtered_downloads[row]

        menu = QMenu(self)

        # Open file (only if completed and file exists)
        if download.status == DownloadStatus.COMPLETED:
            open_file_action = menu.addAction("Open File")
            open_file_action.triggered.connect(lambda: self.open_file_requested.emit(download.id))

            open_folder_action = menu.addAction("Open Folder")
            open_folder_action.triggered.connect(lambda: self.open_folder_requested.emit(download.id))

        # Retry failed downloads
        if download.status == DownloadStatus.FAILED:
            retry_action = menu.addAction("Retry Download")
            retry_action.triggered.connect(lambda: self.retry_requested.emit(download.id))

        menu.addSeparator()

        # Delete
        delete_action = menu.addAction("Delete from History")
        delete_action.triggered.connect(lambda: self.delete_requested.emit(download.id))

        menu.exec(self.table.mapToGlobal(position))

    def refresh(self):
        """Refresh the display"""
        self._apply_filters()
