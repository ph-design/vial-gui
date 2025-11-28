# SPDX-License-Identifier: GPL-2.0-or-later
import logging
import platform
from json import JSONDecodeError

from PyQt6.QtCore import Qt, QSettings, QStandardPaths, QTimer, QRect, QT_VERSION_STR
from PyQt6.QtGui import QAction, QActionGroup, QMovie
from PyQt6.QtWidgets import QWidget, QComboBox, QToolButton, QHBoxLayout, QVBoxLayout, QMainWindow, QApplication, \
    QFileDialog, QDialog, QTabWidget, QMessageBox, QLabel, QProgressBar

import os
import sys

from about_keyboard import AboutKeyboard
from autorefresh.autorefresh import Autorefresh
from editor.alt_repeat_key import AltRepeatKey
from editor.combos import Combos
from constants import WINDOW_WIDTH, WINDOW_HEIGHT
from widgets.editor_container import EditorContainer
from editor.firmware_flasher import FirmwareFlasher
from editor.key_override import KeyOverride
from protocol.keyboard_comm import ProtocolError
from editor.keymap_editor import KeymapEditor
from keymaps import KEYMAPS
from editor.layout_editor import LayoutEditor
from editor.macro_recorder import MacroRecorder
from editor.qmk_settings import QmkSettings
from editor.rgb_configurator import RGBConfigurator
from tabbed_keycodes import TabbedKeycodes
from editor.tap_dance import TapDance
from unlocker import Unlocker
from util import tr, EXAMPLE_KEYBOARDS, KeycodeDisplay, EXAMPLE_KEYBOARD_PREFIX
from vial_device import VialKeyboard
from editor.matrix_test import MatrixTest
from i18n import I18n

import themes

#splash scren
class LoadingDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("LoadingDialog", "Loading"))
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.label = QLabel(tr("LoadingDialog", "Connecting to keyboard..."))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.label.font()
        font.setPointSize(11)
        font.setBold(True)
        self.label.setFont(font)
        layout.addWidget(self.label)
        
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(0)
        self.progress.setTextVisible(False)
        self.progress.setMinimumHeight(8)
        layout.addWidget(self.progress)
        
        self.hint_label = QLabel(tr("LoadingDialog", "Please wait..."))
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_font = self.hint_label.font()
        hint_font.setPointSize(9)
        self.hint_label.setFont(hint_font)
        layout.addWidget(self.hint_label)
        
        self.setLayout(layout)
        self.setFixedSize(350, 140)
        
        self.apply_style()

    def apply_style(self):
        window_bg = themes.Theme.window_color()
        text_color = themes.Theme.text_color()
        highlight = themes.Theme.highlight_color()
        border = themes.Theme.border_color()
        
        style = f"""
        QDialog {{
            background-color: {window_bg};
            border: 1px solid {border};
            border-radius: 8px;
        }}
        QLabel {{
            color: {text_color};
            background-color: transparent;
        }}
        QProgressBar {{
            background-color: {border};
            border: none;
            border-radius: 4px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {highlight};
            border-radius: 4px;
        }}
        """
        self.setStyleSheet(style)

    def keyPressEvent(self, ev):
        pass


class MainWindow(QMainWindow):

    def __init__(self, appctx):
        super().__init__()
        self.appctx = appctx
        try:
            app = QApplication.instance()
            splash = getattr(app, 'splash', None)
            if splash:
                splash.message(tr("MainWindow", "Initializing UI..."))
                app.processEvents()
        except Exception:
            splash = None

        self.ui_lock_count = 0

        self.settings = QSettings("vial-next", "vial-next")
        if self.settings.value("size", None):
            self.resize(self.settings.value("size"))
        else:
            self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        _pos = self.settings.value("pos", None)
        # In PyQt6, qApp.desktop() is replaced with screen handling
        if _pos:
            screen_rect = QApplication.instance().primaryScreen().geometry()
            if screen_rect.contains(QRect(_pos, self.size())):
                self.move(self.settings.value("pos"))

        if self.settings.value("maximized", False, bool):
            self.showMaximized()

        themes.Theme.set_theme(self.get_theme())

        self.combobox_devices = QComboBox()
        self.combobox_devices.currentIndexChanged.connect(self.on_device_selected)

        self.btn_refresh_devices = QToolButton()
        self.btn_refresh_devices.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.btn_refresh_devices.setText(tr("MainWindow", "Refresh"))
        self.btn_refresh_devices.clicked.connect(self.on_click_refresh)

        layout_combobox = QHBoxLayout()
        layout_combobox.addWidget(self.combobox_devices)
        if sys.platform != "emscripten":
            layout_combobox.addWidget(self.btn_refresh_devices)

        try:
            if splash:
                splash.message(tr("MainWindow", "Creating editors..."))
                app.processEvents()
        except Exception:
            pass

        self.layout_editor = LayoutEditor()
        self.keymap_editor = KeymapEditor(self.layout_editor)
        self.firmware_flasher = FirmwareFlasher(self)
        self.macro_recorder = MacroRecorder()
        self.tap_dance = TapDance()
        self.combos = Combos()
        self.key_override = KeyOverride()
        self.alt_repeat_key = AltRepeatKey()
        QmkSettings.initialize(appctx)
        self.qmk_settings = QmkSettings()
        self.matrix_tester = MatrixTest(self.layout_editor)
        self.rgb_configurator = RGBConfigurator()

        self.editors = [(self.keymap_editor, "Keymap"), (self.layout_editor, "Layout"), (self.macro_recorder, "Macros"),
                        (self.rgb_configurator, "Lighting"), (self.tap_dance, "Tap Dance"), (self.combos, "Combos"),
                        (self.key_override, "Key Overrides"), (self.alt_repeat_key, "Alt Repeat Key"),
                        (self.qmk_settings, "QMK Settings"), (self.matrix_tester, "Matrix tester"),
                        (self.firmware_flasher, "Firmware updater")]

        Unlocker.global_layout_editor = self.layout_editor
        Unlocker.global_main_window = self

        self.current_tab = None
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.refresh_tabs()
        try:
            if splash:
                splash.message(tr("MainWindow", "Building tabs..."))
                app.processEvents()
        except Exception:
            pass

        self.loading_dialog = None

        no_devices = 'No devices detected. Connect a Vial-compatible device and press "Refresh"<br>' \
                     'or select "File" → "Download VIA definitions" in order to enable support for VIA keyboards.'
        if sys.platform.startswith("linux"):
            no_devices += '<br><br>On Linux you need to set up a custom udev rule for keyboards to be detected. ' \
                          'Follow the instructions linked below:<br>' \
                          '<a href="https://get.vial.today/manual/linux-udev.html">https://get.vial.today/manual/linux-udev.html</a>'
        self.lbl_no_devices = QLabel(tr("MainWindow", no_devices))
        self.lbl_no_devices.setTextFormat(Qt.TextFormat.RichText)
        self.lbl_no_devices.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addLayout(layout_combobox)
        layout.addWidget(self.tabs, 1)
        layout.addWidget(self.lbl_no_devices)
        layout.setAlignment(self.lbl_no_devices, Qt.AlignmentFlag.AlignHCenter)
        self.tray_keycodes = TabbedKeycodes()
        self.tray_keycodes.make_tray()
        layout.addWidget(self.tray_keycodes, 1)
        self.tray_keycodes.hide()
        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        self.init_menu()
        self.apply_stylesheet()

        # Do not start device autorefresh thread immediately to avoid blocking
        # UI startup. Start it shortly after the window is shown.
        try:
            if splash:
                splash.message(tr("MainWindow", "Starting device backend..."))
                app.processEvents()
        except Exception:
            pass
        self.autorefresh = None

        # cache for via definition files
        self.cache_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)

        # check if the via defitions already exist (cache the data; will be
        # loaded into the autorefresh thread when it starts)
        self._cached_via_stack = None
        if os.path.isfile(os.path.join(self.cache_path, "via_keyboards.json")):
            with open(os.path.join(self.cache_path, "via_keyboards.json")) as vf:
                data = vf.read()
            try:
                # store for later loading when autorefresh starts
                self._cached_via_stack = data
            except Exception as e:
                logging.warning("Failed to read stored via_keyboards.json: {}".format(e))

        # Delay starting autorefresh until after main window is shown to avoid
        # blocking the UI during heavy device enumeration and initial updates.
        QTimer.singleShot(100, self.start_autorefresh)

    def start_autorefresh(self):
        try:
            self.autorefresh = Autorefresh()
            self.autorefresh.devices_updated.connect(self.on_devices_updated)
            # handle asynchronous device opens
            if hasattr(self.autorefresh, 'device_opened'):
                self.autorefresh.device_opened.connect(self.on_device_opened)

            # If we cached VIA definitions, load them into the autorefresh thread
            if self._cached_via_stack:
                try:
                    self.autorefresh.load_via_stack(self._cached_via_stack)
                except JSONDecodeError as e:
                    logging.warning("Failed to parse stored via_keyboards.json: {}".format(e))

            # perform an initial refresh once autorefresh thread is running
            self.on_click_refresh()
        except Exception:
            logging.exception("Failed to start autorefresh")

        if sys.platform == "emscripten":
            import vialglue
            QTimer.singleShot(100, vialglue.notify_ready)

    def init_menu(self):
        layout_load_act = QAction(tr("MenuFile", "Load saved layout..."), self)
        layout_load_act.setShortcut("Ctrl+O")
        layout_load_act.triggered.connect(self.on_layout_load)

        layout_save_act = QAction(tr("MenuFile", "Save current layout..."), self)
        layout_save_act.setShortcut("Ctrl+S")
        layout_save_act.triggered.connect(self.on_layout_save)

        sideload_json_act = QAction(tr("MenuFile", "Sideload VIA JSON..."), self)
        sideload_json_act.triggered.connect(self.on_sideload_json)

        download_via_stack_act = QAction(tr("MenuFile", "Download VIA definitions"), self)
        download_via_stack_act.triggered.connect(self.load_via_stack_json)

        load_dummy_act = QAction(tr("MenuFile", "Load dummy JSON..."), self)
        load_dummy_act.triggered.connect(self.on_load_dummy)

        exit_act = QAction(tr("MenuFile", "Exit"), self)
        exit_act.setShortcut("Ctrl+Q")
        exit_act.triggered.connect(self.close)

        file_menu = self.menuBar().addMenu(tr("Menu", "File"))
        file_menu.addAction(layout_load_act)
        file_menu.addAction(layout_save_act)

        if sys.platform != "emscripten":
            file_menu.addSeparator()
            file_menu.addAction(sideload_json_act)
            file_menu.addAction(download_via_stack_act)
            file_menu.addAction(load_dummy_act)
            file_menu.addSeparator()
            file_menu.addAction(exit_act)

        keyboard_unlock_act = QAction(tr("MenuSecurity", "Unlock"), self)
        keyboard_unlock_act.setShortcut("Ctrl+U")
        keyboard_unlock_act.triggered.connect(self.unlock_keyboard)

        keyboard_lock_act = QAction(tr("MenuSecurity", "Lock"), self)
        keyboard_lock_act.setShortcut("Ctrl+L")
        keyboard_lock_act.triggered.connect(self.lock_keyboard)

        keyboard_reset_act = QAction(tr("MenuSecurity", "Reboot to bootloader"), self)
        keyboard_reset_act.setShortcut("Ctrl+B")
        keyboard_reset_act.triggered.connect(self.reboot_to_bootloader)

        keyboard_layout_menu = self.menuBar().addMenu(tr("Menu", "Keyboard layout"))
        keymap_group = QActionGroup(self)
        selected_keymap = self.settings.value("keymap")
        for idx, keymap in enumerate(KEYMAPS):
            act = QAction(tr("KeyboardLayout", keymap[0]), self)
            act.triggered.connect(lambda checked, x=idx: self.change_keyboard_layout(x))
            act.setCheckable(True)
            if selected_keymap == keymap[0]:
                self.change_keyboard_layout(idx)
                act.setChecked(True)
            keymap_group.addAction(act)
            keyboard_layout_menu.addAction(act)
        # check "QWERTY" if nothing else is selected
        if keymap_group.checkedAction() is None:
            keymap_group.actions()[0].setChecked(True)

        self.security_menu = self.menuBar().addMenu(tr("Menu", "Security"))
        self.security_menu.addAction(keyboard_unlock_act)
        self.security_menu.addAction(keyboard_lock_act)
        self.security_menu.addSeparator()
        self.security_menu.addAction(keyboard_reset_act)

        if sys.platform != "emscripten":
            self.theme_menu = self.menuBar().addMenu(tr("Menu", "Theme"))
            theme_group = QActionGroup(self)
            selected_theme = self.get_theme()
            for name, _ in [("System", None)] + themes.themes:
                act = QAction(tr("MenuTheme", name), self)
                act.triggered.connect(lambda x,name=name: self.set_theme(name))
                act.setCheckable(True)
                act.setChecked(selected_theme == name)
                theme_group.addAction(act)
                self.theme_menu.addAction(act)
            # check "System" if nothing else is selected
            if theme_group.checkedAction() is None:
                theme_group.actions()[0].setChecked(True)

            # Language menu
            self.language_menu = self.menuBar().addMenu(tr("Menu", "Language"))
            self.language_group = QActionGroup(self)
            current_lang = I18n.get_language()
            for lang_code, lang_name in I18n.LANGUAGES.items():
                act = QAction(lang_name, self)
                act.triggered.connect(lambda x, code=lang_code: self.set_language(code))
                act.setCheckable(True)
                act.setChecked(current_lang == lang_code)
                self.language_group.addAction(act)
                self.language_menu.addAction(act)

        about_vial_act = QAction(tr("MenuAbout", "About vial-next..."), self)
        about_vial_act.triggered.connect(self.about_vial)
        self.about_keyboard_act = QAction("", self)
        self.about_keyboard_act.triggered.connect(self.about_keyboard)
        self.about_menu = self.menuBar().addMenu(tr("Menu", "About"))
        self.about_menu.addAction(self.about_keyboard_act)
        self.about_menu.addAction(about_vial_act)

    def on_layout_loaded(self, layout):
        """
        Receives a message from the JS bridge when a layout has
        been loaded via the JS File System API.
        """
        self.keymap_editor.restore_layout(layout)
        self.rebuild()

    def on_layout_load(self):
        if sys.platform == "emscripten":
            import vialglue
            # Tells the JS bridge to open a file selection dialog
            # so the user can load a layout.
            vialglue.load_layout()
        else:
            dialog = QFileDialog()
            dialog.setDefaultSuffix("vil")
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
            dialog.setNameFilters(["Vial layout (*.vil)"])
            if dialog.exec() == QDialog.DialogCode.Accepted:
                with open(dialog.selectedFiles()[0], "rb") as inf:
                    data = inf.read()
                self.keymap_editor.restore_layout(data)
                self.rebuild()

    def on_layout_save(self):
        if sys.platform == "emscripten":
            import vialglue
            layout = self.keymap_editor.save_layout()
            # Passes the current layout to the JS bridge so it can
            # open a file dialog and allow the user to save it to disk.
            vialglue.save_layout(layout)
        else:
            dialog = QFileDialog()
            dialog.setDefaultSuffix("vil")
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            dialog.setNameFilters(["Vial layout (*.vil)"])
            if dialog.exec() == QDialog.DialogCode.Accepted:
                with open(dialog.selectedFiles()[0], "wb") as outf:
                    outf.write(self.keymap_editor.save_layout())

    def on_click_refresh(self):
        self.autorefresh.update(quiet=False, hard=True)

    def on_devices_updated(self, devices, hard_refresh):
        self.combobox_devices.blockSignals(True)

        self.combobox_devices.clear()
        for dev in devices:
            self.combobox_devices.addItem(dev.title())
            if self.autorefresh.current_device and dev.desc["path"] == self.autorefresh.current_device.desc["path"]:
                self.combobox_devices.setCurrentIndex(self.combobox_devices.count() - 1)

        self.combobox_devices.blockSignals(False)

        if devices:
            self.lbl_no_devices.hide()
            self.tabs.show()
        else:
            self.lbl_no_devices.show()
            self.tabs.hide()

        if hard_refresh:
            self.on_device_selected()

    def on_device_selected(self):
        # Use async selection to avoid blocking UI while opening the device
        if not self.autorefresh:
            return
        try:
            self.lock_ui()
            # 显示加载对话框
            self.loading_dialog = LoadingDialog(self)
            self.loading_dialog.show()
            QApplication.processEvents()  # 确保对话框立即显示
            
            # call async selection; result will be handled in on_device_opened
            self.autorefresh.select_device_async(self.combobox_devices.currentIndex())
        except Exception:
            logging.exception("Failed to select device asynchronously")
            # 关闭加载对话框
            if self.loading_dialog:
                self.loading_dialog.close()
                self.loading_dialog = None
            QMessageBox.warning(self, "", "Unsupported protocol version!\n"
                                          "Please download latest Vial from https://get.vial.today/")
            try:
                self.unlock_ui()
            except Exception:
                pass

    def on_device_opened(self, device):
        """Called when an async device open completes."""
        try:
            if device is None:
                # failed to open or cleared
                return

            # post-open checks and UI refresh
            if isinstance(device, VialKeyboard):
                keyboard_id = device.keyboard.keyboard_id
                if (keyboard_id in EXAMPLE_KEYBOARDS) or ((keyboard_id & 0xFFFFFFFFFFFFFF) == EXAMPLE_KEYBOARD_PREFIX):
                    QMessageBox.warning(self, "", "An example keyboard UID was detected.\n"
                                              "Please change your keyboard UID to be unique before you ship!")

            # 保持加载对话框显示，更新提示信息
            if self.loading_dialog:
                self.loading_dialog.label.setText(tr("LoadingDialog", "Loading keyboard layout..."))
                QApplication.processEvents()
            
            self.rebuild()
            self.refresh_tabs()
        finally:
            try:
                # 在所有操作完成后才关闭加载对话框
                if self.loading_dialog:
                    self.loading_dialog.close()
                    self.loading_dialog = None
                
                self.unlock_ui()
            except Exception:
                pass

    def rebuild(self):
        # don't show "Security" menu for bootloader mode, as the bootloader is inherently insecure
        self.security_menu.menuAction().setVisible(isinstance(self.autorefresh.current_device, VialKeyboard))

        self.about_keyboard_act.setVisible(False)
        if isinstance(self.autorefresh.current_device, VialKeyboard):
            self.about_keyboard_act.setText("About {}...".format(self.autorefresh.current_device.title()))
            self.about_keyboard_act.setVisible(True)

        # if unlock process was interrupted, we must finish it first
        if isinstance(self.autorefresh.current_device, VialKeyboard) and self.autorefresh.current_device.keyboard.get_unlock_in_progress():
            Unlocker.unlock(self.autorefresh.current_device.keyboard)
            self.autorefresh.current_device.keyboard.reload()

        for e in [self.layout_editor, self.keymap_editor, self.firmware_flasher, self.macro_recorder,
                  self.tap_dance, self.combos, self.key_override, self.alt_repeat_key,
                  self.qmk_settings, self.matrix_tester, self.rgb_configurator]:
            e.rebuild(self.autorefresh.current_device)

    def refresh_tabs(self):
        self.tabs.clear()
        for container, lbl in self.editors:
            if not container.valid():
                continue

            c = EditorContainer(container)
            self.tabs.addTab(c, tr("MainWindow", lbl))

    def load_via_stack_json(self):
        from urllib.request import urlopen

        with urlopen("https://github.com/vial-kb/via-keymap-precompiled/raw/main/via_keyboard_stack.json") as resp:
            data = resp.read()
        self.autorefresh.load_via_stack(data)
        # write to cache
        with open(os.path.join(self.cache_path, "via_keyboards.json"), "wb") as cf:
            cf.write(data)

    def on_sideload_json(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix("json")
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dialog.setNameFilters(["VIA layout JSON (*.json)"])
        if dialog.exec() == QDialog.DialogCode.Accepted:
            with open(dialog.selectedFiles()[0], "rb") as inf:
                data = inf.read()
            self.autorefresh.sideload_via_json(data)

    def on_load_dummy(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix("json")
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dialog.setNameFilters(["VIA layout JSON (*.json)"])
        if dialog.exec() == QDialog.DialogCode.Accepted:
            with open(dialog.selectedFiles()[0], "rb") as inf:
                data = inf.read()
            self.autorefresh.load_dummy(data)

    def lock_ui(self):
        self.ui_lock_count += 1
        if self.ui_lock_count == 1:
            self.autorefresh._lock()
            self.tabs.setEnabled(False)
            self.combobox_devices.setEnabled(False)
            self.btn_refresh_devices.setEnabled(False)

    def unlock_ui(self):
        self.ui_lock_count -= 1
        if self.ui_lock_count == 0:
            self.autorefresh._unlock()
            self.tabs.setEnabled(True)
            self.combobox_devices.setEnabled(True)
            self.btn_refresh_devices.setEnabled(True)

    def unlock_keyboard(self):
        if isinstance(self.autorefresh.current_device, VialKeyboard):
            Unlocker.unlock(self.autorefresh.current_device.keyboard)

    def lock_keyboard(self):
        if isinstance(self.autorefresh.current_device, VialKeyboard):
            self.autorefresh.current_device.keyboard.lock()

    def reboot_to_bootloader(self):
        if isinstance(self.autorefresh.current_device, VialKeyboard):
            Unlocker.unlock(self.autorefresh.current_device.keyboard)
            self.autorefresh.current_device.keyboard.reset()

    def change_keyboard_layout(self, index):
        self.settings.setValue("keymap", KEYMAPS[index][0])
        KeycodeDisplay.set_keymap_override(KEYMAPS[index][1])

    def get_theme(self):
        return self.settings.value("theme", "Phantom-dark")

    def set_theme(self, theme):
        themes.Theme.set_theme(theme)
        self.settings.setValue("theme", theme)
        msg = QMessageBox()
        msg.setText(tr("MainWindow", "In order to fully apply the theme you should restart the application."))
        msg.exec()

    def set_language(self, lang_code):
        I18n.set_language(lang_code)
        msg = QMessageBox()
        msg.setText(tr("MainWindow", "In order to fully apply the language you should restart the application."))
        msg.exec()

    def on_tab_changed(self, index):
        TabbedKeycodes.close_tray()
        old_tab = self.current_tab
        new_tab = None
        if index >= 0:
            new_tab = self.tabs.widget(index)

        if old_tab is not None:
            old_tab.editor.deactivate()
        if new_tab is not None:
            new_tab.editor.activate()

        self.current_tab = new_tab

    def about_vial(self):
        title = "About vial-next"
        # 说明与原项目（Vial）的关系，并提供本仓库地址
        text = 'vial-next {}<br><br>Python {}<br>Qt {}<br><br>' \
               'This project is a fork/derivative of the original Vial GUI. ' \
               'It contains local modifications and changes made under the terms of the original license.<br><br>' \
               'Original project: <a href="https://get.vial.today/">https://get.vial.today/</a><br>' \
               'This repository (vial-next): <a href="https://github.com/ph-design/vial-gui">https://github.com/ph-design/vial-gui</a><br><br>' \
               'Licensed under the terms of the<br>GNU General Public License (version 2 or later)<br><br>' \
               .format(QApplication.instance().applicationVersion(),
                       platform.python_version(), QT_VERSION_STR)

        if sys.platform == "emscripten":
            self.msg_about = QMessageBox()
            self.msg_about.setWindowTitle(title)
            self.msg_about.setText(text)
            self.msg_about.setModal(True)
            self.msg_about.show()
        else:
            QMessageBox.about(self, title, text)

    def about_keyboard(self):
        self.about_dialog = AboutKeyboard(self.autorefresh.current_device)
        self.about_dialog.setModal(True)
        self.about_dialog.show()

    def apply_stylesheet(self):
        window_bg = themes.Theme.window_color()
        base_bg = themes.Theme.base_color()
        button_bg = themes.Theme.button_color()
        text_color = themes.Theme.text_color()
        button_text = themes.Theme.button_text_color()
        highlight = themes.Theme.highlight_color()
        link = themes.Theme.link_color()
        border = themes.Theme.border_color()
        alt_base = themes.Theme.alternate_base_color()
        mid = themes.Theme.mid_color()
        midlight = themes.Theme.midlight_color()
        
        # 根据主题类型调整一些特殊颜色
        if themes.Theme.is_dark_theme():
            hover_bg = "#30363d"
            hover_border = "#58a6ff"
            focus_bg = "#1c2128"
            disabled_text = "#6e7681"
            separator_color = "#30363d"
            tab_text_inactive = "#8b949e"
        else:
            hover_bg = "#e8e8e8"
            hover_border = "#0052cc"
            focus_bg = "#f0f0f0"
            disabled_text = "#999999"
            separator_color = "#d5d5d5"
            tab_text_inactive = "#666666"
        
        # 启用平滑滚动
        from PyQt6.QtWidgets import QScrollArea
        
        scroll_style = f"""
            QScrollArea {{
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {window_bg};
                width: 12px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {border};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {midlight};
            }}
            QScrollBar:horizontal {{
                background-color: {window_bg};
                height: 12px;
                border: none;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {border};
                border-radius: 6px;
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {midlight};
            }}
        """
        
        # QScrollArea/QScrollBar rules are included in the stylesheet below
        # (avoid per-widget setStyleSheet calls which are expensive)
        
        stylesheet = f"""
        QMainWindow {{
            background-color: {window_bg};
        }}
        
        QComboBox {{
            background-color: {base_bg};
            color: {text_color};
            border: 1px solid {border};
            border-radius: 4px;
            padding: 5px;
            font-size: 11px;
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QToolButton {{
            background-color: {button_bg};
            color: {button_text};
            border: 1px solid {border};
            border-radius: 4px;
            padding: 5px 10px;
            font-size: 11px;
            font-weight: 500;
        }}
        
        QToolButton:hover {{
            background-color: {hover_bg};
            border: 1px solid {hover_border};
        }}
        
        QToolButton:pressed {{
            background-color: {highlight};
            color: #ffffff;
        }}
        
        QPushButton {{
            background-color: {button_bg};
            color: {button_text};
            border: 1px solid {border};
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {hover_bg};
            color: {button_text};
            border: 1px solid {hover_border};
        }}
        
        QPushButton:pressed {{
            background-color: {highlight};
            color: #ffffff;
        }}
        
        QPushButton:focus {{
            color: {button_text};
            border: 2px solid {link};
        }}
        
        QPushButton:disabled {{
            color: {disabled_text};
        }}
        
        QLabel {{
            color: {text_color};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {border};
            background-color: {window_bg};
        }}
        
        QTabBar::tab {{
            background-color: {button_bg};
            color: {tab_text_inactive};
            border: 1px solid {border};
            padding: 4px 12px;
            border-radius: 4px 4px 0px 0px;
            margin-right: 2px;
            min-height: 24px;
            font-size: 14px;
            font-weight: 500;
        }}
        
        QTabBar::tab:hover {{
            background-color: {hover_bg};
            color: {button_text};
            border: 1px solid {midlight};
        }}
        
        QTabBar::tab:selected {{
            background-color: {alt_base};
            color: {link};
            border: 1px solid {border};
            border-bottom: 2px solid {link};
        }}
        
        QTabBar::scroller {{
            width: 60px;
            height: 24px;
        }}
        
        QTabBar::left-arrow {{
            background-color: {link};
            width: 18px;
            height: 18px;
            margin: 0px 2px;
        }}
        
        QTabBar::right-arrow {{
            background-color: {link};
            width: 18px;
            height: 18px;
            margin: 0px 2px;
        }}
        
        QLineEdit {{
            background-color: {base_bg};
            color: {text_color};
            border: 1px solid {border};
            border-radius: 4px;
            padding: 5px;
            font-size: 11px;
            selection-background-color: {highlight};
        }}
        
        QLineEdit:focus {{
            border: 2px solid {link};
            background-color: {focus_bg};
        }}
        
        QTextEdit {{
            background-color: {base_bg};
            color: {text_color};
            border: 1px solid {border};
            border-radius: 4px;
            padding: 5px;
            font-size: 11px;
            selection-background-color: {highlight};
        }}
        
        QTextEdit:focus {{
            border: 2px solid {link};
            background-color: {focus_bg};
        }}
        
        QPlainTextEdit {{
            background-color: {base_bg};
            color: {text_color};
            border: 1px solid {border};
            border-radius: 4px;
            padding: 5px;
            font-size: 11px;
            selection-background-color: {highlight};
        }}
        
        QPlainTextEdit:focus {{
            border: 2px solid {link};
            background-color: {focus_bg};
        }}
        
        QScrollBar:vertical {{
            background-color: {window_bg};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {border};
            border-radius: 6px;
            min-height: 20px;
            margin: 0px 2px 0px 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {midlight};
        }}
        
        QScrollBar:horizontal {{
            background-color: {window_bg};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {border};
            border-radius: 6px;
            min-width: 20px;
            margin: 2px 0px 2px 0px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {midlight};
        }}
        
        QScrollBar::add-line, QScrollBar::sub-line {{
            background: none;
            border: none;
        }}
        
        QMenuBar {{
            background-color: {base_bg};
            color: {button_text};
            border-bottom: 1px solid {border};
            padding: 4px 0px;
        }}
        
        QMenuBar::item {{
            padding: 4px 12px;
            margin: 2px 0px;
            border-radius: 4px;
            border: 1px solid transparent;
            background-color: transparent;
        }}
        
        QMenuBar::item:selected {{
            background-color: {hover_bg};
            padding: 4px 12px;
            margin: 2px 0px;
            border-radius: 4px;
            border: 1px solid transparent;
            font-size: 11px;
        }}
        
        QMenu {{
            background-color: {base_bg};
            color: {button_text};
            border: 1px solid {border};
            border-radius: 4px;
        }}
        
        QMenu::item {{
            padding: 4px 8px;
            margin: 1px 0px;
            border-radius: 2px;
            border: 1px solid transparent;
            background-color: transparent;
        }}
        
        QMenu::item:selected {{
            background-color: {highlight};
            color: #ffffff;
            border-radius: 2px;
            padding: 4px 8px;
            margin: 1px 0px;
            border: 1px solid transparent;
        }}
        
        QMenu::separator {{
            background-color: {separator_color};
            height: 1px;
            margin: 4px 0px;
        }}
        
        QMessageBox QLabel {{
            color: {text_color};
        }}
        
        QMessageBox QDialogButtonBox QPushButton {{
            min-width: 70px;
        }}
        
        QCheckBox {{
            color: {button_text};
            spacing: 5px;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
        }}
        
        QCheckBox::indicator:unchecked {{
            background-color: {base_bg};
            border: 1px solid {border};
            border-radius: 3px;
        }}
        
        QCheckBox::indicator:unchecked:hover {{
            border: 1px solid {link};
            background-color: {focus_bg};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {highlight};
            border: 1px solid {highlight};
            border-radius: 3px;
        }}
        
        QCheckBox::indicator:checked:hover {{
            background-color: {link};
            border: 1px solid {link};
        }}
        
        QRadioButton {{
            color: {button_text};
            spacing: 5px;
        }}
        
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
        }}
        
        QRadioButton::indicator:unchecked {{
            background-color: {base_bg};
            border: 1px solid {border};
            border-radius: 8px;
        }}
        
        QRadioButton::indicator:unchecked:hover {{
            border: 1px solid {link};
            background-color: {focus_bg};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {highlight};
            border: 1px solid {highlight};
            border-radius: 8px;
        }}
        
        QGroupBox {{
            color: {button_text};
            border: 1px solid {border};
            border-radius: 4px;
            margin-top: 12px;
            padding-top: 12px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }}
        
        QSpinBox, QDoubleSpinBox {{
            background-color: {base_bg};
            color: {text_color};
            border: 1px solid {border};
            border-radius: 4px;
            padding: 5px;
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {link};
            background-color: {focus_bg};
        }}
        
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 16px;
            border-left: 1px solid {border};
            background-color: {button_bg};
        }}
        
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
            background-color: {hover_bg};
        }}
        
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 16px;
            border-left: 1px solid {border};
            border-top: 1px solid {border};
            background-color: {button_bg};
        }}
        
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: {hover_bg};
        }}
        
        QSlider::groove:horizontal {{
            background-color: {border};
            height: 4px;
            border-radius: 2px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {link};
            width: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: {hover_border};
        }}
        
        QSlider::groove:vertical {{
            background-color: {border};
            width: 4px;
            border-radius: 2px;
        }}
        
        QSlider::handle:vertical {{
            background-color: {link};
            height: 16px;
            margin: 0 -6px;
            border-radius: 8px;
        }}
        
        QSlider::handle:vertical:hover {{
            background-color: {hover_border};
        }}
        
        QProgressBar {{
            background-color: {base_bg};
            border: 1px solid {border};
            border-radius: 4px;
            padding: 2px;
            height: 20px;
        }}
        
        QProgressBar::chunk {{
            background-color: {highlight};
            border-radius: 2px;
        }}
        
        QHeaderView::section {{
            background-color: {button_bg};
            color: {button_text};
            padding: 5px;
            border: 1px solid {border};
            font-weight: 500;
        }}
        
        QTableWidget, QTableView {{
            background-color: {base_bg};
            alternate-background-color: {alt_base};
            gridline-color: {border};
            border: 1px solid {border};
        }}
        
        QTableWidget::item:selected {{
            background-color: {highlight};
            color: #ffffff;
        }}
        
        QListWidget, QListView {{
            background-color: {base_bg};
            border: 1px solid {border};
            outline: none;
        }}
        
        QListWidget::item:hover, QListView::item:hover {{
            background-color: {button_bg};
        }}
        
        QListWidget::item:selected, QListView::item:selected {{
            background-color: {highlight};
            color: #ffffff;
        }}
        
        QTreeWidget, QTreeView {{
            background-color: {base_bg};
            border: 1px solid {border};
            outline: none;
        }}
        
        QTreeView::item:hover {{
            background-color: {button_bg};
        }}
        
        QTreeView::item:selected {{
            background-color: {highlight};
            color: #ffffff;
        }}
        
        QDockWidget {{
            background-color: {window_bg};
            color: {button_text};
        }}
        
        QDockWidget::title {{
            background-color: {button_bg};
            border: 1px solid {border};
            padding: 5px;
            border-radius: 4px;
        }}
        
        QStatusBar {{
            background-color: {base_bg};
            color: {button_text};
            border-top: 1px solid {border};
        }}
        
        QToolBar {{
            background-color: {window_bg};
            border: none;
            spacing: 5px;
            padding: 5px;
        }}
        
        QToolBar::separator {{
            background-color: {separator_color};
            width: 1px;
            margin: 0 5px;
        }}
        """
        QApplication.instance().setStyleSheet(stylesheet)

        # Enable smoother/per-pixel scrolling on item views and improve scroll step
        try:
            from PyQt6.QtWidgets import QAbstractItemView, QListWidget, QListView, QTreeView, QTreeWidget, QTableView, QTableWidget, QScrollArea
            for w in QApplication.instance().allWidgets():
                try:
                    # item views: use per-pixel scrolling where supported
                    if isinstance(w, (QListWidget, QListView, QTreeView, QTreeWidget, QTableView, QTableWidget)):
                        try:
                            w.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
                            w.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
                        except Exception:
                            pass
                        # increase single-step to make wheel/keyboard scrolling feel smoother
                        try:
                            v = w.verticalScrollBar()
                            h = w.horizontalScrollBar()
                            if v is not None:
                                v.setSingleStep(8)
                            if h is not None:
                                h.setSingleStep(8)
                        except Exception:
                            pass
                    # QScrollArea: tweak scrollbar single step to reduce jumpiness
                    elif isinstance(w, QScrollArea):
                        try:
                            v = w.verticalScrollBar()
                            h = w.horizontalScrollBar()
                            if v is not None:
                                v.setSingleStep(8)
                            if h is not None:
                                h.setSingleStep(8)
                        except Exception:
                            pass
                    # enable QScroller on widgets with a viewport for kinetic/touch-style scrolling
                    try:
                        from PyQt6.QtWidgets import QScroller
                        if hasattr(w, 'viewport'):
                            try:
                                vp = w.viewport()
                                if vp is not None:
                                    QScroller.grabGesture(vp, QScroller.GestureType.LeftMouseButtonGesture)
                            except Exception:
                                pass
                    except Exception:
                        # QScroller may not be available on all builds; ignore silently
                        pass
                except Exception:
                    continue
        except Exception:
            pass

    def closeEvent(self, e):
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        self.settings.setValue("maximized", self.isMaximized())

        e.accept()
