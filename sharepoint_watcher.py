"""
OneDrive/SharePoint Sync Watcher for GNOC Issue Tracker Dashboard

Watches the OneDrive-synced SharePoint folder for changes to the
Issue Tracker Excel files and auto-copies them to the dashboard
directory so Streamlit always has fresh data.

Usage:
    # Start watcher + dashboard together:
    python sharepoint_watcher.py

    # Watch only (dashboard already running):
    python sharepoint_watcher.py --watch-only

    # One-shot copy (no watching):
    python sharepoint_watcher.py --once
"""

import os
import sys
import time
import shutil
import argparse
import subprocess
from datetime import datetime

try:
    from watchdog.observers.polling import PollingObserver as Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("❌ watchdog not installed. Run: pip install watchdog")
    sys.exit(1)

# === CONFIGURATION ===

# OneDrive synced SharePoint folder (source)
SYNC_FOLDER = "/mnt/c/Users/eknriis/Ericsson/Airtel Africa DL - Documents"

# Dashboard directory (destination)
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_SCRIPT = os.path.join(DASHBOARD_DIR, "issue_tracker_dashboard.py")

# Files to sync — maps source filename → destination filename
FILES_TO_SYNC = {
    "Issue Tracker  MTN.xlsx": "Issue Tracker  MTN.xlsx",
    "Issue Tracker AA_OBF.xlsx": "Issue Tracker AA_OBF.xlsx",
}


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def copy_file(src_name, dst_name):
    """Copy a file from sync folder to dashboard folder if it changed."""
    src = os.path.join(SYNC_FOLDER, src_name)
    dst = os.path.join(DASHBOARD_DIR, dst_name)

    if not os.path.exists(src):
        log(f"   ⚠️  Source not found: {src_name}")
        return False

    src_mtime = os.path.getmtime(src)
    dst_mtime = os.path.getmtime(dst) if os.path.exists(dst) else 0

    if src_mtime > dst_mtime:
        shutil.copy2(src, dst)
        size_kb = os.path.getsize(dst) / 1024
        log(f"   ✅ Copied: {src_name} ({size_kb:.1f} KB)")
        return True
    else:
        log(f"   ⏭️  {src_name} — unchanged")
        return False


def sync_all():
    """Copy all watched files from sync folder to dashboard folder."""
    log("🔄 Syncing files from SharePoint/OneDrive...")
    updated = 0
    for src_name, dst_name in FILES_TO_SYNC.items():
        try:
            if copy_file(src_name, dst_name):
                updated += 1
        except Exception as e:
            log(f"   ❌ Error copying {src_name}: {e}")

    if updated:
        log(f"📥 {updated} file(s) updated.")
        # Touch dashboard script to invalidate Streamlit cache
        if os.path.exists(DASHBOARD_SCRIPT):
            os.utime(DASHBOARD_SCRIPT, None)
            log("🔄 Dashboard cache invalidated.")
    else:
        log("✅ All files up to date.")
    return updated


class SyncHandler(FileSystemEventHandler):
    """Watches the OneDrive sync folder and copies changed files."""

    def __init__(self):
        super().__init__()
        self.last_event_time = 0
        self.debounce_seconds = 5

    def on_modified(self, event):
        self._handle(event)

    def on_created(self, event):
        self._handle(event)

    def _handle(self, event):
        if event.is_directory:
            return

        filename = os.path.basename(event.src_path)
        if filename not in FILES_TO_SYNC:
            return

        now = time.time()
        if now - self.last_event_time < self.debounce_seconds:
            return
        self.last_event_time = now

        log(f"📄 Change detected: {filename}")
        # Small delay to let OneDrive finish writing
        time.sleep(2)
        sync_all()


def start_dashboard():
    """Start the Streamlit dashboard as a subprocess."""
    log("🚀 Starting Streamlit dashboard...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", DASHBOARD_SCRIPT,
         "--server.fileWatcherType", "poll"],
        cwd=DASHBOARD_DIR,
    )
    log(f"   Dashboard PID: {proc.pid}")
    return proc


def main():
    parser = argparse.ArgumentParser(description="OneDrive Sync Watcher for GNOC Issue Tracker")
    parser.add_argument("--watch-only", action="store_true",
                        help="Only watch files, don't start dashboard")
    parser.add_argument("--once", action="store_true",
                        help="Copy files once and exit")
    args = parser.parse_args()

    print("=" * 60)
    print("  👁️  SharePoint/OneDrive Watcher — GNOC Issue Tracker")
    print("=" * 60)
    print(f"  Source:  {SYNC_FOLDER}")
    print(f"  Dest:    {DASHBOARD_DIR}")
    print(f"  Files:   {', '.join(FILES_TO_SYNC.keys())}")
    print("=" * 60)

    # Initial sync
    sync_all()

    if args.once:
        log("Done (one-shot mode).")
        return

    dashboard_proc = None
    if not args.watch_only:
        dashboard_proc = start_dashboard()

    # Set up file watcher (using PollingObserver for cross-filesystem /mnt/c)
    handler = SyncHandler()
    observer = Observer(timeout=5)
    observer.schedule(handler, SYNC_FOLDER, recursive=False)
    observer.start()

    log("👁️  Watching for SharePoint changes... (Ctrl+C to stop)")
    log("💡 Any edits in SharePoint will auto-sync via OneDrive → dashboard.")

    try:
        while True:
            time.sleep(1)
            if dashboard_proc and dashboard_proc.poll() is not None:
                log("⚠️  Dashboard exited. Restarting...")
                dashboard_proc = start_dashboard()
    except KeyboardInterrupt:
        print()
        log("🛑 Stopping watcher...")
        observer.stop()
        if dashboard_proc and dashboard_proc.poll() is None:
            log("🛑 Stopping dashboard...")
            dashboard_proc.terminate()
            dashboard_proc.wait(timeout=5)
    finally:
        observer.join()

    log("👋 Done.")


if __name__ == "__main__":
    main()
