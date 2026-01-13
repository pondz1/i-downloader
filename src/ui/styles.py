"""
Application styling - Dark theme QSS
"""

DARK_THEME = """
/* Global Styles */
QWidget {
    background-color: #1a1a2e;
    color: #eaeaea;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
}

/* Main Window */
QMainWindow {
    background-color: #1a1a2e;
}

/* Menu Bar */
QMenuBar {
    background-color: #16213e;
    border-bottom: 1px solid #0f3460;
    padding: 5px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 8px 15px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #0f3460;
}

QMenu {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 8px;
    padding: 5px;
}

QMenu::item {
    padding: 8px 30px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #0f3460;
}

/* Tool Bar */
QToolBar {
    background-color: #16213e;
    border: none;
    padding: 8px;
    spacing: 8px;
}

QToolButton {
    background-color: #0f3460;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    color: #eaeaea;
    font-weight: 500;
}

QToolButton:hover {
    background-color: #e94560;
}

QToolButton:pressed {
    background-color: #c73e54;
}

QToolButton:disabled {
    background-color: #2a2a4a;
    color: #666;
}

/* Push Buttons */
QPushButton {
    background-color: #0f3460;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    color: #eaeaea;
    font-weight: 500;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #e94560;
}

QPushButton:pressed {
    background-color: #c73e54;
}

QPushButton:disabled {
    background-color: #2a2a4a;
    color: #666;
}

QPushButton#primaryButton {
    background-color: #e94560;
}

QPushButton#primaryButton:hover {
    background-color: #ff6b8a;
}

QPushButton#dangerButton {
    background-color: #dc3545;
}

QPushButton#dangerButton:hover {
    background-color: #ff4757;
}

/* Line Edit */
QLineEdit {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 8px;
    padding: 10px 15px;
    color: #eaeaea;
    selection-background-color: #e94560;
}

QLineEdit:focus {
    border-color: #e94560;
}

QLineEdit:disabled {
    background-color: #2a2a4a;
    color: #666;
}

/* Scroll Area */
QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollBar:vertical {
    background-color: #16213e;
    width: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #0f3460;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #e94560;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #16213e;
    height: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #0f3460;
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #e94560;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* Progress Bar */
QProgressBar {
    background-color: #16213e;
    border: none;
    border-radius: 8px;
    height: 20px;
    text-align: center;
    color: #eaeaea;
    font-weight: bold;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #e94560,
        stop:0.5 #ff6b8a,
        stop:1 #e94560);
    border-radius: 8px;
}

/* Table Widget */
QTableWidget {
    background-color: #16213e;
    gridline-color: #0f3460;
    border: none;
    border-radius: 8px;
}

QTableWidget::item {
    padding: 10px;
    border-bottom: 1px solid #0f3460;
}

QTableWidget::item:selected {
    background-color: #0f3460;
}

QHeaderView::section {
    background-color: #0f3460;
    padding: 12px;
    border: none;
    font-weight: bold;
}

/* Labels */
QLabel {
    color: #eaeaea;
    background-color: transparent;
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #e94560;
}

QLabel#subtitleLabel {
    font-size: 14px;
    color: #aaa;
}

QLabel#filenameLabel {
    font-size: 14px;
    font-weight: bold;
}

QLabel#statusLabel {
    font-size: 12px;
    color: #888;
}

/* Group Box */
QGroupBox {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 10px;
    margin-top: 15px;
    padding-top: 15px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px 15px;
    color: #e94560;
}

/* Combo Box */
QComboBox {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 8px;
    padding: 8px 15px;
    color: #eaeaea;
    min-width: 150px;
}

QComboBox:hover {
    border-color: #e94560;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 8px solid #e94560;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 8px;
    selection-background-color: #0f3460;
}

/* Spin Box */
QSpinBox {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 8px;
    padding: 8px 15px;
    color: #eaeaea;
}

QSpinBox:focus {
    border-color: #e94560;
}

/* Dialog */
QDialog {
    background-color: #1a1a2e;
}

/* Status Bar */
QStatusBar {
    background-color: #16213e;
    border-top: 1px solid #0f3460;
    padding: 5px;
}

QStatusBar::item {
    border: none;
}

/* Tooltips */
QToolTip {
    background-color: #0f3460;
    color: #eaeaea;
    border: none;
    border-radius: 4px;
    padding: 8px;
}

/* Frame for download items */
QFrame#downloadItemFrame {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 12px;
    padding: 15px;
    margin: 5px;
}

QFrame#downloadItemFrame:hover {
    border-color: #e94560;
    background-color: #1e2a4a;
}

/* System Tray */
QMenu#trayMenu {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 10px;
    padding: 8px;
}
"""

# Colors for status indicators
STATUS_COLORS = {
    'downloading': '#4CAF50',  # Green
    'paused': '#FFC107',       # Yellow
    'queued': '#2196F3',       # Blue
    'completed': '#9C27B0',    # Purple
    'failed': '#F44336',       # Red
    'cancelled': '#9E9E9E'     # Gray
}

def get_status_color(status: str) -> str:
    """Get the color for a download status"""
    return STATUS_COLORS.get(status, '#eaeaea')
