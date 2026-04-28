# main.pyw — Entry point for Claude Settings Manager
# Use .pyw extension to avoid console window on Windows

import sys
import os
import msvcrt
import webview
from app.api import Api

LOCK_PATH = os.path.join(os.path.expanduser("~"), ".claude", ".settings-manager.lock")
_lock_file = None


def is_already_running():
    """Check if another instance is running using a file lock.
    Uses msvcrt.locking for an exclusive lock on Windows.
    The lock is automatically released when the process exits."""
    global _lock_file
    try:
        os.makedirs(os.path.dirname(LOCK_PATH), exist_ok=True)
        _lock_file = open(LOCK_PATH, "w")
        # Try to acquire an exclusive (non-blocking) lock
        msvcrt.locking(_lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        _lock_file.write(str(os.getpid()))
        _lock_file.flush()
        return False
    except (OSError, IOError):
        # Lock is held by another instance
        if _lock_file:
            _lock_file.close()
            _lock_file = None
        return True


def release_lock():
    """Release the file lock on exit."""
    global _lock_file
    if _lock_file:
        try:
            msvcrt.locking(_lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            _lock_file.close()
        except (OSError, IOError):
            pass
        _lock_file = None
    try:
        os.remove(LOCK_PATH)
    except OSError:
        pass


def main():
    if is_already_running():
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
        release_lock()


if __name__ == "__main__":
    main()
