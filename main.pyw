# main.pyw — Entry point for Claude Settings Manager
# Use .pyw extension to avoid console window on Windows

import sys
import os
import webview
from app.api import Api


def is_already_running():
    """Check if another instance is running using a lock file."""
    lock_path = os.path.join(os.path.expanduser("~"), ".claude", ".settings-manager.lock")
    try:
        # Try to create lock file exclusively
        if os.path.exists(lock_path):
            # Check if the PID in the lock file is still alive
            with open(lock_path, "r") as f:
                old_pid = f.read().strip()
            if old_pid:
                try:
                    os.kill(int(old_pid), 0)  # Signal 0 = check existence
                    return True  # Process exists
                except (OSError, ValueError):
                    pass  # Stale lock file
            os.remove(lock_path)
        # Write our PID
        with open(lock_path, "w") as f:
            f.write(str(os.getpid()))
        return False
    except OSError:
        return False


def remove_lock():
    """Remove the lock file on exit."""
    lock_path = os.path.join(os.path.expanduser("~"), ".claude", ".settings-manager.lock")
    try:
        os.remove(lock_path)
    except OSError:
        pass


def main():
    if is_already_running():
        print("Another instance is already running.")
        sys.exit(0)

    try:
        api = Api()
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "index.html")
        window = webview.create_window(
            title="Claude Settings Manager",
            url=ui_path,
            js_api=api,
            width=800,
            height=600,
            resizable=True,
            min_size=(600, 450),
        )
        webview.start()
    finally:
        remove_lock()


if __name__ == "__main__":
    main()
