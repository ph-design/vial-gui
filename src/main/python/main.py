# SPDX-License-Identifier: GPL-2.0-or-later
import ssl
import certifi
import os

if ssl.get_default_verify_paths().cafile is None:
    os.environ['SSL_CERT_FILE'] = certifi.where()

import traceback
import sys

from hidpi import setup_hidpi
setup_hidpi()

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QLabel, QProgressBar, QVBoxLayout
from PyQt6.QtGui import QPixmap
import json
from pathlib import Path


class LocalAppCtx:
    def __init__(self):
        # load build settings from src/build/settings/base.json
        root = Path(__file__).resolve().parents[2]
        settings_path = root / 'build' / 'settings' / 'base.json'
        try:
            with open(settings_path, 'r', encoding='utf-8') as inf:
                self.build_settings = json.load(inf)
        except Exception:
            self.build_settings = {"app_name": "Vial-Next", "version": "0.0.1"}

        self._app = None

    @property
    def app(self):
        if self._app is None:
            self._app = QtWidgets.QApplication(sys.argv)
            HiDPIInit.initialize()
            self._app.setApplicationName(self.build_settings.get("app_name", "Vial-Next"))
            self._app.setOrganizationDomain("phdesign.cc")
            self._app.setApplicationVersion(self.build_settings.get("version", "0.0.1"))
        return self._app

    def get_resource(self, name):
        # map resource requests to one of several locations so it works
        # both in development and in various frozen layouts (Nuitka).
        root = Path(__file__).resolve().parents[1]

        candidates = [
            root / 'resources' / 'base' / name,
            root / 'main.dist' / 'resources' / 'base' / name,
            root.parent / 'resources' / 'base' / name,
            root.parent / 'main.dist' / 'resources' / 'base' / name,
            Path.cwd() / 'resources' / 'base' / name,
        ]

        for p in candidates:
            try:
                if p.exists():
                    return str(p)
            except Exception:
                continue

        # fallback to the original expected location
        return str(root / 'resources' / 'base' / name)

import sys

from main_window import MainWindow
from hidpi import HiDPIInit


# http://timlehr.com/python-exception-hooks-with-qt-message-box/
from util import init_logger


def show_exception_box(log_msg):
    if QtWidgets.QApplication.instance() is not None:
        errorbox = QtWidgets.QMessageBox()
        errorbox.setText(log_msg)
        errorbox.exec()


class UncaughtHook(QtCore.QObject):
    _exception_caught = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super(UncaughtHook, self).__init__(*args, **kwargs)

        # this registers the exception_hook() function as hook with the Python interpreter
        sys._excepthook = sys.excepthook
        sys.excepthook = self.exception_hook

        # connect signal to execute the message box function always on main thread
        self._exception_caught.connect(show_exception_box)

    def exception_hook(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # ignore keyboard interrupt to support console applications
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        else:
            log_msg = '\n'.join([''.join(traceback.format_tb(exc_traceback)),
                                 '{0}: {1}'.format(exc_type.__name__, exc_value)])

            # trigger message box show
            self._exception_caught.emit(log_msg)
        sys._excepthook(exc_type, exc_value, exc_traceback)


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == "--linux-recorder":
        from linux_keystroke_recorder import linux_keystroke_recorder

        linux_keystroke_recorder()
    else:
        appctxt = LocalAppCtx()
        init_logger()

        # Ensure QApplication exists before showing a splash
        app = appctxt.app

        # Simple splash dialog shown during startup
        class SplashDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
                self.setModal(False)
                layout = QVBoxLayout()
                layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                # try to load an icon for splash
                try:
                    # Prefer resources provided via LocalAppCtx.get_resource() so
                    # packaged builds (Nuitka/etc.) can include the icon and
                    # return a usable path. Fall back to source-tree locations.
                    root = Path(__file__).resolve().parents[1]
                    icon_candidates = []
                    try:
                        candidate = Path(appctxt.get_resource('Icon.ico'))
                        if candidate.exists():
                            icon_candidates.append(candidate)
                    except Exception:
                        pass
                    try:
                        candidate = Path(appctxt.get_resource('vial.ico'))
                        if candidate.exists():
                            icon_candidates.append(candidate)
                    except Exception:
                        pass
                    # fallback to repository locations for development runs
                    icon_candidates += [
                        root / 'icons' / 'Icon.ico',
                        root / 'icons' / 'base' / 'vial.ico',
                    ]
                    icon_pix = None
                    for p in icon_candidates:
                        try:
                            if p.exists():
                                pix = QPixmap(str(p))
                                if not pix.isNull():
                                    icon_pix = pix
                                    break
                        except Exception:
                            continue
                    if icon_pix is not None:
                        icon_label = QLabel()
                        # increase icon size so it's clearly visible
                        ICON_SIZE = 96
                        icon_label.setFixedSize(ICON_SIZE, ICON_SIZE)
                        pix = icon_pix.scaled(ICON_SIZE, ICON_SIZE, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
                        icon_label.setPixmap(pix)
                        icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                        # add with explicit horizontal centering
                        layout.addWidget(icon_label, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
                except Exception:
                    pass

                self.label = QLabel("Starting vial-next...")
                self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.progress = QProgressBar()
                self.progress.setMinimum(0)
                self.progress.setMaximum(0)
                self.progress.setTextVisible(False)
                layout.addWidget(self.label)
                layout.addWidget(self.progress)
                self.setLayout(layout)
                # increase size so icon + label + progress fit without clipping
                self.setFixedSize(380, 200)

            def message(self, text):
                self.label.setText(text)

        # show splash early
        splash = SplashDialog()
        splash.show()
        app.processEvents()
        # attach splash to application so other modules can update it
        try:
            app.splash = splash
        except Exception:
            pass

        # Load language settings before creating the main window
        from i18n import I18n
        splash.message("Loading language...")
        app.processEvents()
        I18n.load_language()
        # Try to set application/window icon. Prefer the running exe's embedded
        # icon when this is a bundled executable; otherwise fall back to project
        # icon files. Using the exe icon ensures taskbar and explorer show the
        # embedded icon correctly.
        try:
            from PyQt6.QtGui import QIcon
            exe_path = None
            try:
                exe_path = Path(sys.argv[0])
            except Exception:
                exe_path = None
            # Prefer using an explicit icon file bundled in resources if present
            # (this works reliably both in development and in packaged builds).
            try:
                try:
                    icon_path = appctxt.get_resource('Icon.ico')
                except Exception:
                    icon_path = None

                if icon_path and Path(icon_path).exists():
                    appctxt.app.setWindowIcon(QIcon(str(icon_path)))
                elif exe_path and exe_path.suffix.lower() == '.exe' and exe_path.exists():
                    # Fallback: use the running exe's embedded icon if available
                    appctxt.app.setWindowIcon(QIcon(str(exe_path)))
                else:
                    # Last-resort fallback: repository icon locations
                    root = Path(__file__).resolve().parents[1]
                    for name in ('icons/Icon.ico', 'icons/base/vial.ico'):
                        p = root / name
                        try:
                            if p.exists():
                                appctxt.app.setWindowIcon(QIcon(str(p)))
                                break
                        except Exception:
                            continue
            except Exception:
                # ignore icon errors
                pass
        except Exception:
            pass
        # Defer main window creation so the event loop can run and the
        # splash progress bar can animate without being blocked.
        def start_main():
            try:
                qt_exception_hook = UncaughtHook()
                splash.message("Initializing main window...")
                app.processEvents()
                window = MainWindow(appctxt)
                splash.message("Finalizing...")
                app.processEvents()
                window.show()
                # close splash after main window is visible
                try:
                    splash.close()
                except Exception:
                    pass
            except Exception:
                import traceback
                traceback.print_exc()

        QtCore.QTimer.singleShot(50, start_main)
        exit_code = appctxt.app.exec()
        sys.exit(exit_code)
