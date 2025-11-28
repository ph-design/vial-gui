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
            self.build_settings = {"app_name": "Vial", "version": "0.0.0"}

        self._app = None

    @property
    def app(self):
        if self._app is None:
            self._app = QtWidgets.QApplication(sys.argv)
            HiDPIInit.initialize()
            self._app.setApplicationName(self.build_settings.get("app_name", "Vial"))
            self._app.setOrganizationDomain("vial.today")
            self._app.setApplicationVersion(self.build_settings.get("version", "0.0.0"))
        return self._app

    def get_resource(self, name):
        # map resource requests to src/main/resources/base/<name>
        root = Path(__file__).resolve().parents[1]
        res = root / 'resources' / 'base' / name
        return str(res)

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
        
        # Load language settings before creating the main window
        from i18n import I18n
        I18n.load_language()
        
        app = appctxt.app
        qt_exception_hook = UncaughtHook()
        window = MainWindow(appctxt)
        window.show()
        exit_code = appctxt.app.exec()
        sys.exit(exit_code)
