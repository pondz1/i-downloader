"""
Application styling - Modern Slate Dark theme QSS
"""

DARK_THEME = """
/* Global Styles */
QWidget {
    background-color: #0f172a;
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
}

/* Main Window */
QMainWindow {
    background-color: #0f172a;
}

/* Menu Bar */
QMenuBar {
    background-color: #090d16;
    border-bottom: 1px solid #1e293b;
    padding: 4px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
    color: #94a3b8;
}

QMenuBar::item:selected {
    background-color: #1e293b;
    color: #f8fafc;
}

QMenu {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 6px;
}

QMenu::item {
    padding: 7px 24px;
    border-radius: 4px;
    color: #cbd5e1;
}

QMenu::item:selected {
    background-color: #1e293b;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: #1e293b;
    margin: 4px 8px;
}

/* Tool Bar */
QToolBar {
    background-color: #0c1322;
    border-bottom: 1px solid #1e293b;
    padding: 8px 12px;
    spacing: 8px;
}

QToolButton {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 14px;
    color: #e2e8f0;
    font-weight: 500;
}

QToolButton:hover {
    background-color: #27354f;
    border-color: #475569;
    color: #ffffff;
}

QToolButton:pressed {
    background-color: #172033;
}

QToolButton:disabled {
    background-color: #111827;
    border-color: #1f2937;
    color: #4b5563;
}

/* Push Buttons */
QPushButton {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 14px;
    color: #e2e8f0;
    font-weight: 500;
    min-width: 72px;
}

QPushButton:hover {
    background-color: #27354f;
    border-color: #475569;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #172033;
}

QPushButton:disabled {
    background-color: #111827;
    border-color: #1f2937;
    color: #4b5563;
}

QPushButton#primaryButton {
    background-color: #2563eb;
    border: 1px solid #3b82f6;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background-color: #1d4ed8;
    border-color: #60a5fa;
}

QPushButton#primaryButton:pressed {
    background-color: #1e40af;
}

QPushButton#dangerButton {
    background-color: #dc2626;
    border: 1px solid #ef4444;
    color: #ffffff;
}

QPushButton#dangerButton:hover {
    background-color: #b91c1c;
    border-color: #f87171;
}

/* Line Edit */
QLineEdit {
    background-color: #090d16;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 12px;
    color: #f8fafc;
    selection-background-color: #2563eb;
}

QLineEdit:focus {
    border-color: #3b82f6;
    background-color: #0c1322;
}

QLineEdit:disabled {
    background-color: #111827;
    border-color: #1f2937;
    color: #4b5563;
}

/* Scroll Area */
QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    border-radius: 4px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: #475569;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: transparent;
    height: 8px;
    border-radius: 4px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #334155;
    border-radius: 4px;
    min-width: 24px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #475569;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* Progress Bar */
QProgressBar {
    background-color: #1e293b;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    font-size: 10px;
    color: transparent;
}

QProgressBar::chunk {
    background-color: #3b82f6;
    border-radius: 4px;
}

/* Tabs */
QTabWidget::pane {
    border: none;
    background-color: #0f172a;
}

QTabBar::tab {
    background-color: transparent;
    color: #94a3b8;
    padding: 8px 16px;
    border-bottom: 2px solid transparent;
    font-weight: 500;
}

QTabBar::tab:selected {
    color: #3b82f6;
    border-bottom: 2px solid #3b82f6;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    color: #f1f5f9;
}

/* Table Widget */
QTableWidget {
    background-color: #0f172a;
    gridline-color: #1e293b;
    border: 1px solid #1e293b;
    border-radius: 8px;
}

QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #1e293b;
}

QTableWidget::item:selected {
    background-color: #1e293b;
    color: #38bdf8;
}

QHeaderView::section {
    background-color: #0c1322;
    color: #94a3b8;
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid #1e293b;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 11px;
}

/* Labels */
QLabel {
    color: #f1f5f9;
    background-color: transparent;
}

QLabel#titleLabel {
    font-size: 16px;
    font-weight: 700;
    color: #f8fafc;
}

QLabel#subtitleLabel {
    font-size: 13px;
    color: #94a3b8;
}

QLabel#filenameLabel {
    font-size: 13px;
    font-weight: 600;
    color: #f1f5f9;
}

QLabel#statusLabel {
    font-size: 12px;
    color: #94a3b8;
}

QLabel#badgeLabel {
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
}

/* Group Box */
QGroupBox {
    background-color: #0c1322;
    border: 1px solid #1e293b;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 14px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    color: #38bdf8;
}

/* Combo Box */
QComboBox {
    background-color: #090d16;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 12px;
    color: #f8fafc;
    min-width: 140px;
}

QComboBox:hover {
    border-color: #3b82f6;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #94a3b8;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 6px;
    selection-background-color: #1e293b;
    selection-color: #38bdf8;
}

/* Spin Box */
QSpinBox {
    background-color: #090d16;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 12px;
    color: #f8fafc;
    min-width: 70px;
    selection-background-color: #2563eb;
}

QSpinBox:focus {
    border-color: #3b82f6;
}

QSpinBox::up-button, QSpinBox::down-button {
    width: 0;
    height: 0;
    border: none;
}

/* Dialog */
QDialog {
    background-color: #0f172a;
}

/* Status Bar */
QStatusBar {
    background-color: #090d16;
    border-top: 1px solid #1e293b;
    padding: 4px 10px;
    color: #94a3b8;
    font-size: 12px;
}

QStatusBar::item {
    border: none;
}

/* Tooltips */
QToolTip {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}

/* Frame for download items */
QFrame#downloadItemFrame {
    background-color: #162137;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 12px 16px;
}

QFrame#downloadItemFrame:hover {
    border-color: #3b82f6;
    background-color: #1a2742;
}

/* Empty State Widget */
QWidget#emptyStateWidget {
    background-color: transparent;
}

/* System Tray */
QMenu#trayMenu {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 6px;
}
"""

# Colors for status indicators
STATUS_COLORS = {
    'downloading': '#3b82f6',  # Blue
    'paused': '#f59e0b',       # Amber
    'queued': '#64748b',       # Slate
    'completed': '#10b981',    # Emerald green
    'failed': '#ef4444',       # Red
    'cancelled': '#64748b'     # Slate gray
}

def get_status_color(status: str) -> str:
    """Get the color for a download status"""
    return STATUS_COLORS.get(status, '#94a3b8')
