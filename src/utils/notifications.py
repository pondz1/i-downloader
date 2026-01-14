"""
Cross-platform notification manager for download events
"""

import platform
import subprocess
from typing import Optional


class NotificationManager:
    """
    Cross-platform notification manager.

    Supports:
    - Windows: Toast notifications via win10toast
    - Linux: Desktop notifications via notify-send
    - macOS: Notifications via osascript
    """

    def __init__(self):
        self.system = platform.system()
        self._windows_toaster = None

        # Initialize Windows toast notifier if available
        if self.system == "Windows":
            try:
                from win10toast import ToastNotifier
                self._windows_toaster = ToastNotifier()
            except ImportError:
                self._windows_toaster = None

    def show_completion(self, filename: str, size: str, speed: str = ""):
        """
        Show notification when download completes.

        Args:
            filename: Name of the downloaded file
            size: Formatted file size
            speed: Average download speed (optional)
        """
        title = "Download Complete"
        message = f"{filename}\n{size}"
        if speed:
            message += f"\nSpeed: {speed}"

        self._show_notification(title, message)

    def show_failure(self, filename: str, error: str):
        """
        Show notification when download fails.

        Args:
            filename: Name of the file that failed
            error: Error message
        """
        title = "Download Failed"
        message = f"{filename}\nError: {error}"

        self._show_notification(title, message)

    def show_batch_complete(self, count: int):
        """
        Show notification when multiple downloads complete.

        Args:
            count: Number of downloads completed
        """
        title = "Downloads Complete"
        message = f"{count} download{'s' if count > 1 else ''} completed"

        self._show_notification(title, message)

    def _show_notification(self, title: str, message: str):
        """Show notification using platform-specific method"""
        try:
            if self.system == "Windows":
                self._show_windows(title, message)
            elif self.system == "Darwin":  # macOS
                self._show_macos(title, message)
            elif self.system == "Linux":
                self._show_linux(title, message)
        except Exception as e:
            print(f"Failed to show notification: {e}")

    def _show_windows(self, title: str, message: str):
        """Show Windows toast notification"""
        if self._windows_toaster:
            # win10toast shows blocking notifications
            # Use threaded=False for non-blocking
            self._windows_toaster.show_toast(
                title,
                message,
                duration=5,
                threaded=True
            )
        else:
            # Fallback: Try using PowerShell
            try:
                ps_command = f'''
                Add-Type -AssemblyName System.Windows.Forms
                $balloon = New-Object System.Windows.Forms.NotifyIcon
                $balloon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
                $balloon.BalloonTipText = "{message}"
                $balloon.BalloonTipTitle = "{title}"
                $balloon.Visible = $true
                $balloon.ShowBalloonTip(5000)
                Start-Sleep -Seconds 5
                $balloon.Dispose()
                '''
                subprocess.Popen(
                    ["powershell", "-Command", ps_command],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except:
                pass

    def _show_macos(self, title: str, message: str):
        """Show macOS notification using osascript"""
        script = f'''
        display notification "{message}" with title "{title}" sound name "default"
        '''
        subprocess.run(["osascript", "-e", script], check=False)

    def _show_linux(self, title: str, message: str):
        """Show Linux notification using notify-send"""
        # Check if notify-send is available
        try:
            subprocess.run(
                ["notify-send", title, message],
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            # notify-send not available, try zenity
            try:
                subprocess.run(
                    ["zenity", "--notification", "--text", f"{title}\n{message}"],
                    check=False
                )
            except:
                pass
