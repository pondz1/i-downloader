"""
i-Downloader - Main Entry Point
A fast, multi-threaded download manager
"""

import sys
import asyncio
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from src.ui.main_window import MainWindow


class AsyncRunner:
    """Helper class to run async code with Qt"""
    
    def __init__(self, app: QApplication, window: MainWindow):
        self.app = app
        self.window = window
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def run(self):
        """Run the application with async support"""
        # Initialize async components
        self.loop.run_until_complete(self.window.initialize())
        
        # Store loop in window for async operations
        self.window._loop = self.loop
        
        # Run Qt event loop with async integration
        timer = QTimer()
        timer.timeout.connect(self._run_pending)
        timer.start(10)  # Process async tasks every 10ms
        
        try:
            exit_code = self.app.exec()
        finally:
            # Cleanup
            try:
                self.loop.run_until_complete(self.window.shutdown())
            except:
                pass
            self.loop.close()
        
        return exit_code
    
    def _run_pending(self):
        """Run pending async tasks"""
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()


def main():
    """Main entry point"""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("i-Downloader")
    app.setApplicationVersion("1.0.0")
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Run with async support
    runner = AsyncRunner(app, window)
    sys.exit(runner.run())


if __name__ == "__main__":
    main()
