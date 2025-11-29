# SPDX-License-Identifier: GPL-2.0-or-later
import sys
import time

from PyQt6.QtCore import Qt, QTimer, QCoreApplication, QByteArray, QBuffer, QIODevice
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QProgressBar, QDialog, QApplication, QPushButton, QHBoxLayout

from widgets.keyboard_widget import KeyboardWidget
from util import tr
import themes


class Unlocker(QDialog):

    def __init__(self, layout_editor, keyboard):
        super().__init__()

        self.setStyleSheet("background-color: {}".format(
            QApplication.palette().color(QPalette.ColorRole.Button).lighter(130).name()))

        self.keyboard = keyboard

        layout = QVBoxLayout()

        self.progress = QProgressBar()

        # Texts (i18n)
        lbl_intro = QLabel(tr("Unlocker", "In order to proceed, the keyboard must be set into unlocked mode.\n"
                              "You should only perform this operation on computers that you trust."))
        lbl_hint = QLabel(tr("Unlocker", "To exit this mode, you will need to replug the keyboard\n"
                              "or select Security->Lock from the menu."))
        lbl_instructions = QLabel(tr("Unlocker", "Press and hold the following keys until the progress bar "
                                        "below fills up:"))

        for lbl in (lbl_intro, lbl_hint, lbl_instructions):
            lbl.setWordWrap(True)

        self.keyboard_reference = KeyboardWidget(layout_editor)
        self.keyboard_reference.set_enabled(False)
        self.keyboard_reference.set_scale(0.7)
        self.keyboard_reference.setObjectName("unlock_keyboard_ref")

        # info label for dynamic messages (e.g. unplug notice)
        self.info_label = QLabel("")
        self.info_label.setObjectName("unlock_info")
        self.info_label.setWordWrap(True)

        layout.addWidget(lbl_intro)
        layout.addWidget(lbl_hint)
        layout.addWidget(lbl_instructions)
        layout.addWidget(self.keyboard_reference)
        layout.setAlignment(self.keyboard_reference, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.progress)
        layout.addWidget(self.info_label)

        # action row
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.btn_cancel = QPushButton(tr("Unlocker", "Cancel"))
        self.btn_cancel.clicked.connect(self._on_cancel)
        btn_row.addWidget(self.btn_cancel)
        layout.addLayout(btn_row)

        self.setLayout(layout)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint)

        self.progress.setMinimumHeight(20)

        self.update_reference()
        self.timer = QTimer()
        self.timer.timeout.connect(self.unlock_poller)
        self.perform_unlock()

        # apply theme-aware styling
        try:
            bg = themes.Theme.window_color()
            text = themes.Theme.text_color()
            accent = themes.Theme.highlight_color()
            border = themes.Theme.border_color()
            btn_bg = themes.Theme.button_color()
            btn_text = themes.Theme.button_text_color()
            style = f"""
            QDialog {{
                background-color: {bg};
                color: {text};
                border-radius: 10px;
            }}
            QLabel {{
                font-size: 13px;
            }}
            QLabel#unlock_info {{
                color: {text};
                font-size: 12px;
            }}
            QPushButton {{
                background-color: {btn_bg};
                color: {btn_text};
                border: 1px solid {border};
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 13px;
            }}
            QProgressBar {{
                min-height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {accent};
            }}
            """
            self.setStyleSheet(style)
        except Exception:
            pass

    def update_reference(self):
        """ Updates keycap reference image """
        try:
            keys = getattr(self.keyboard, 'keys', []) or []
            encoders = getattr(self.keyboard, 'encoders', []) or []
            self.keyboard_reference.set_keys(keys, encoders)

            # use "active" background to indicate keys to hold
            try:
                lock_keys = self.keyboard.get_unlock_keys()
            except Exception:
                lock_keys = []

            for w in self.keyboard_reference.widgets:
                try:
                    if (w.desc.row, w.desc.col) in lock_keys:
                        w.setOn(True)
                    else:
                        w.setOn(False)
                except Exception:
                    continue

            self.keyboard_reference.update_layout()
            self.keyboard_reference.update()
            self.keyboard_reference.updateGeometry()
        except Exception:
            return

    def unlock_poller(self):
        try:
            data = self.keyboard.unlock_poll()
        except Exception:
            # communication error (device may have been unplugged)
            try:
                self.timer.stop()
            except Exception:
                pass
            try:
                self.info_label.setText(tr("Unlocker", "Device disconnected. The dialog will close."))
            except Exception:
                pass
            try:
                self.reject()
            except Exception:
                try:
                    self.close()
                except Exception:
                    pass
            return

        unlocked = data[0]
        unlock_counter = data[2]

        self.progress.setMaximum(max(self.progress.maximum(), unlock_counter))
        self.progress.setValue(self.progress.maximum() - unlock_counter)

        if sys.platform == "emscripten":
            import vialglue
            vialglue.unlock_status(unlock_counter)

        if unlocked == 1:
            if sys.platform == "emscripten":
                import vialglue
                vialglue.unlock_done()

            self.accept()

    def perform_unlock(self):
        self.progress.setMaximum(1)
        self.progress.setValue(0)

        self.keyboard.unlock_start()
        self.timer.start(200)

        if sys.platform == "emscripten":
            import vialglue

            pixmap = self.keyboard_reference.grab()

            # convert QPixmap to bytes
            ba = QByteArray()
            buff = QBuffer(ba)
            buff.open(QIODevice.WriteOnly)
            pixmap.save(buff, "PNG")
            pixmap_bytes = ba.data()

            vialglue.unlock_start(pixmap_bytes, pixmap.width(), pixmap.height())

    @classmethod
    def on_dialog_finished(cls, retval):
        cls.dlg_retval = retval

    @classmethod
    def unlock(cls, keyboard):
        if keyboard.get_unlock_status() == 1:
            return True

        cls.dlg_retval = None
        dlg = cls(cls.global_layout_editor, keyboard)
        dlg.finished.connect(cls.on_dialog_finished)
        cls.global_main_window.lock_ui()
        dlg.setModal(True)
        dlg.show()
        while cls.dlg_retval is None:
            time.sleep(0.05)
            QCoreApplication.processEvents()
        ret = cls.dlg_retval
        cls.global_main_window.unlock_ui()
        return ret

    def keyPressEvent(self, ev):
        """ Ignore all key presses, e.g. Esc should not close the window """
        pass

    def _on_cancel(self):
        try:
            self.timer.stop()
        except Exception:
            pass
        try:
            self.reject()
        except Exception:
            try:
                self.close()
            except Exception:
                pass
