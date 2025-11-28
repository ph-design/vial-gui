import sys

from PyQt6.QtCore import QObject, pyqtSignal
import threading
import logging


class AutorefreshLocker:

    def __init__(self, autorefresh):
        self.autorefresh = autorefresh

    def __enter__(self):
        self.autorefresh._lock()

    def __exit__(self):
        self.autorefresh._unlock()


class Autorefresh(QObject):

    instance = None
    devices_updated = pyqtSignal(object, bool)
    # Emitted when a device has been opened asynchronously (device instance or None)
    device_opened = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self.devices = []
        self.current_device = None

        Autorefresh.instance = self

        if sys.platform == "emscripten":
            from autorefresh.autorefresh_thread_web import AutorefreshThreadWeb

            self.thread = AutorefreshThreadWeb()
        elif sys.platform.startswith("win"):
            from autorefresh.autorefresh_thread_win import AutorefreshThreadWin

            self.thread = AutorefreshThreadWin()
        else:
            from autorefresh.autorefresh_thread import AutorefreshThread

            self.thread = AutorefreshThread()

        self.thread.devices_updated.connect(self.on_devices_updated)
        self.thread.start()

    def _lock(self):
        self.thread.lock()

    def _unlock(self):
        self.thread.unlock()

    @classmethod
    def lock(cls):
        return AutorefreshLocker(cls.instance)

    def load_dummy(self, data):
        self.thread.load_dummy(data)

    def sideload_via_json(self, data):
        self.thread.sideload_via_json(data)

    def load_via_stack(self, data):
        self.thread.load_via_stack(data)

    def select_device(self, idx):
        if self.current_device is not None:
            self.current_device.close()
        self.current_device = None
        if idx >= 0:
            self.current_device = self.devices[idx]

        if self.current_device is not None:
            if self.current_device.sideload:
                self.current_device.open(self.thread.sideload_json)
            elif self.current_device.via_stack:
                self.current_device.open(self.thread.via_stack_json["definitions"][self.current_device.via_id])
            else:
                self.current_device.open(None)
        self.thread.set_device(self.current_device)

    def select_device_async(self, idx):
        """Select device by index but open it asynchronously to avoid blocking UI."""
        if self.current_device is not None:
            try:
                self.current_device.close()
            except Exception:
                logging.exception("Error closing current device")
        self.current_device = None
        if idx < 0:
            # clear device in thread
            self.thread.set_device(None)
            self.device_opened.emit(None)
            return

        if idx >= len(self.devices):
            self.device_opened.emit(None)
            return

        dev = self.devices[idx]
        self.current_device = dev

        def _open_worker(d):
            try:
                if d.sideload:
                    d.open(self.thread.sideload_json)
                elif d.via_stack:
                    d.open(self.thread.via_stack_json["definitions"][d.via_id])
                else:
                    d.open(None)
                # let autorefresh thread know about current device
                self.thread.set_device(d)
                # notify listeners on the main thread
                self.device_opened.emit(d)
            except Exception:
                logging.exception("Failed to open device asynchronously")
                # still set device in thread as None
                self.thread.set_device(None)
                self.device_opened.emit(None)

        t = threading.Thread(target=_open_worker, args=(dev,), daemon=True)
        t.start()

    def on_devices_updated(self, devices, changed):
        self.devices = devices
        self.devices_updated.emit(devices, changed)

    def update(self, quiet=True, hard=False):
        self.thread.update(quiet, hard)
