# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QBrush
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QSizePolicy, QGridLayout, QLabel, QSlider, \
    QComboBox, QColorDialog, QCheckBox, QGroupBox, QVBoxLayout, QListWidget, QListWidgetItem, QScrollArea, \
    QDialog, QSpinBox, QLineEdit

from editor.basic_editor import BasicEditor
from widgets.clickable_label import ClickableLabel
from util import tr
from vial_device import VialKeyboard
import themes


class QmkRgblightEffect:

    def __init__(self, idx, name, color_picker):
        self.idx = idx
        self.name = name
        self.color_picker = color_picker


QMK_RGBLIGHT_EFFECTS = [
    QmkRgblightEffect(0, "All Off", False),
    QmkRgblightEffect(1, "Solid Color", True),
    QmkRgblightEffect(2, "Breathing 1", True),
    QmkRgblightEffect(3, "Breathing 2", True),
    QmkRgblightEffect(4, "Breathing 3", True),
    QmkRgblightEffect(5, "Breathing 4", True),
    QmkRgblightEffect(6, "Rainbow Mood 1", False),
    QmkRgblightEffect(7, "Rainbow Mood 2", False),
    QmkRgblightEffect(8, "Rainbow Mood 3", False),
    QmkRgblightEffect(9, "Rainbow Swirl 1", False),
    QmkRgblightEffect(10, "Rainbow Swirl 2", False),
    QmkRgblightEffect(11, "Rainbow Swirl 3", False),
    QmkRgblightEffect(12, "Rainbow Swirl 4", False),
    QmkRgblightEffect(13, "Rainbow Swirl 5", False),
    QmkRgblightEffect(14, "Rainbow Swirl 6", False),
    QmkRgblightEffect(15, "Snake 1", True),
    QmkRgblightEffect(16, "Snake 2", True),
    QmkRgblightEffect(17, "Snake 3", True),
    QmkRgblightEffect(18, "Snake 4", True),
    QmkRgblightEffect(19, "Snake 5", True),
    QmkRgblightEffect(20, "Snake 6", True),
    QmkRgblightEffect(21, "Knight 1", True),
    QmkRgblightEffect(22, "Knight 2", True),
    QmkRgblightEffect(23, "Knight 3", True),
    QmkRgblightEffect(24, "Christmas", True),
    QmkRgblightEffect(25, "Gradient 1", True),
    QmkRgblightEffect(26, "Gradient 2", True),
    QmkRgblightEffect(27, "Gradient 3", True),
    QmkRgblightEffect(28, "Gradient 4", True),
    QmkRgblightEffect(29, "Gradient 5", True),
    QmkRgblightEffect(30, "Gradient 6", True),
    QmkRgblightEffect(31, "Gradient 7", True),
    QmkRgblightEffect(32, "Gradient 8", True),
    QmkRgblightEffect(33, "Gradient 9", True),
    QmkRgblightEffect(34, "Gradient 10", True),
    QmkRgblightEffect(35, "RGB Test", True),
    QmkRgblightEffect(36, "Alternating", True),
]


class VialRGBEffect:

    def __init__(self, idx, name):
        self.idx = idx
        self.name = name


VIALRGB_EFFECTS = [
    VialRGBEffect(0, "Disable"),
    VialRGBEffect(1, "Direct Control"),
    VialRGBEffect(2, "Solid Color"),
    VialRGBEffect(3, "Alphas Mods"),
    VialRGBEffect(4, "Gradient Up Down"),
    VialRGBEffect(5, "Gradient Left Right"),
    VialRGBEffect(6, "Breathing"),
    VialRGBEffect(7, "Band Sat"),
    VialRGBEffect(8, "Band Val"),
    VialRGBEffect(9, "Band Pinwheel Sat"),
    VialRGBEffect(10, "Band Pinwheel Val"),
    VialRGBEffect(11, "Band Spiral Sat"),
    VialRGBEffect(12, "Band Spiral Val"),
    VialRGBEffect(13, "Cycle All"),
    VialRGBEffect(14, "Cycle Left Right"),
    VialRGBEffect(15, "Cycle Up Down"),
    VialRGBEffect(16, "Rainbow Moving Chevron"),
    VialRGBEffect(17, "Cycle Out In"),
    VialRGBEffect(18, "Cycle Out In Dual"),
    VialRGBEffect(19, "Cycle Pinwheel"),
    VialRGBEffect(20, "Cycle Spiral"),
    VialRGBEffect(21, "Dual Beacon"),
    VialRGBEffect(22, "Rainbow Beacon"),
    VialRGBEffect(23, "Rainbow Pinwheels"),
    VialRGBEffect(24, "Raindrops"),
    VialRGBEffect(25, "Jellybean Raindrops"),
    VialRGBEffect(26, "Hue Breathing"),
    VialRGBEffect(27, "Hue Pendulum"),
    VialRGBEffect(28, "Hue Wave"),
    VialRGBEffect(29, "Typing Heatmap"),
    VialRGBEffect(30, "Digital Rain"),
    VialRGBEffect(31, "Solid Reactive Simple"),
    VialRGBEffect(32, "Solid Reactive"),
    VialRGBEffect(33, "Solid Reactive Wide"),
    VialRGBEffect(34, "Solid Reactive Multiwide"),
    VialRGBEffect(35, "Solid Reactive Cross"),
    VialRGBEffect(36, "Solid Reactive Multicross"),
    VialRGBEffect(37, "Solid Reactive Nexus"),
    VialRGBEffect(38, "Solid Reactive Multinexus"),
    VialRGBEffect(39, "Splash"),
    VialRGBEffect(40, "Multisplash"),
    VialRGBEffect(41, "Solid Splash"),
    VialRGBEffect(42, "Solid Multisplash"),
    VialRGBEffect(43, "Pixel Rain"),
    VialRGBEffect(44, "Pixel Fractal"),
]


class BasicHandler(QObject):

    update = pyqtSignal()

    def __init__(self, container):
        super().__init__()
        self.device = self.keyboard = None
        self.widgets = []

    def set_device(self, device):
        self.device = device
        if self.valid():
            self.keyboard = self.device.keyboard
            self.show()
        else:
            self.hide()

    def show(self):
        for w in self.widgets:
            w.show()

    def hide(self):
        for w in self.widgets:
            w.hide()

    def block_signals(self):
        for w in self.widgets:
            w.blockSignals(True)

    def unblock_signals(self):
        for w in self.widgets:
            w.blockSignals(False)

    def update_from_keyboard(self):
        raise NotImplementedError

    def valid(self):
        raise NotImplementedError


class QmkRgblightHandler(BasicHandler):

    def __init__(self, container):
        super().__init__(container)

        row = container.rowCount()

        # Create a group for underglow controls
        self.group_underglow = QGroupBox(tr("RGBConfigurator", "Underglow (QMK RGB Light)"))
        underglow_font = self.group_underglow.font()
        underglow_font.setPointSize(11)
        self.group_underglow.setFont(underglow_font)
        underglow_layout = QVBoxLayout()
        underglow_layout.setSpacing(10)
        underglow_layout.setContentsMargins(12, 10, 12, 10)

        self.lbl_underglow_effect = QLabel(tr("RGBConfigurator", "Effect:"))
        lbl_font = self.lbl_underglow_effect.font()
        lbl_font.setPointSize(11)
        self.lbl_underglow_effect.setFont(lbl_font)
        underglow_layout.addWidget(self.lbl_underglow_effect)
        
        # Create scroll area for effect buttons
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(180)
        
        effect_widget = QWidget()
        self.effect_buttons_layout = QGridLayout()
        self.effect_buttons_layout.setSpacing(8)
        self.effect_buttons_layout.setContentsMargins(5, 5, 5, 5)
        effect_widget.setLayout(self.effect_buttons_layout)
        scroll.setWidget(effect_widget)
        underglow_layout.addWidget(scroll)

        # Other controls in a grid
        controls_layout = QGridLayout()
        controls_layout.setSpacing(10)

        self.lbl_underglow_brightness = QLabel(tr("RGBConfigurator", "Brightness:"))
        self.lbl_underglow_brightness.setMinimumWidth(140)
        self.lbl_underglow_brightness.setFont(lbl_font)
        controls_layout.addWidget(self.lbl_underglow_brightness, 0, 0)
        self.underglow_brightness = QSlider(QtCore.Qt.Orientation.Horizontal)
        self.underglow_brightness.setMinimum(0)
        self.underglow_brightness.setMaximum(255)
        self.underglow_brightness.setMinimumHeight(28)
        self.underglow_brightness.valueChanged.connect(self.on_underglow_brightness_changed)
        controls_layout.addWidget(self.underglow_brightness, 0, 1)

        self.lbl_underglow_color = QLabel(tr("RGBConfigurator", "Color:"))
        self.lbl_underglow_color.setMinimumWidth(140)
        self.lbl_underglow_color.setFont(lbl_font)
        controls_layout.addWidget(self.lbl_underglow_color, 1, 0)
        self.underglow_color = ClickableLabel(" ")
        self.underglow_color.setMinimumHeight(44)
        border = themes.Theme.border_color()
        self.underglow_color.setStyleSheet(f"QLabel {{ border-radius: 8px; border: 2px solid {border}; }}")
        self.underglow_color.clicked.connect(self.on_underglow_color)
        controls_layout.addWidget(self.underglow_color, 1, 1)

        underglow_layout.addLayout(controls_layout)
        self.group_underglow.setLayout(underglow_layout)
        container.addWidget(self.group_underglow, row, 0, 1, 2)

        self.widgets = [self.group_underglow]
        self.effect_buttons = []

    def update_from_keyboard(self):
        if not self.valid():
            return

        self.underglow_brightness.setValue(self.device.keyboard.underglow_brightness)
        self.build_effect_buttons(self.device.keyboard.underglow_effect)
        color = self.current_color()
        border = themes.Theme.border_color()
        self.underglow_color.setStyleSheet(f"QLabel {{ background-color: {color.name()}; border-radius: 8px; border: 2px solid {border}; }}")

    def build_effect_buttons(self, current_effect_idx):
        """Build the effect button grid"""
        # Clear old buttons
        for btn in self.effect_buttons:
            btn.deleteLater()
        self.effect_buttons.clear()
        
        # Create new button grid (4 columns for better layout)
        for idx, effect in enumerate(QMK_RGBLIGHT_EFFECTS):
            btn = QPushButton(f"{idx}: {effect.name}")
            btn.setMinimumHeight(36)
            btn.setCheckable(True)
            btn.setChecked(idx == current_effect_idx)
            btn_font = btn.font()
            btn_font.setPointSize(9)
            btn.setFont(btn_font)
            
            row = idx // 4
            col = idx % 4
            
            def make_callback(effect_idx):
                def callback():
                    self.device.keyboard.set_qmk_rgblight_effect(effect_idx)
                    self.lbl_underglow_color.setVisible(QMK_RGBLIGHT_EFFECTS[effect_idx].color_picker)
                    self.underglow_color.setVisible(QMK_RGBLIGHT_EFFECTS[effect_idx].color_picker)
                    self.build_effect_buttons(effect_idx)
                    self.update.emit()
                return callback
            
            btn.clicked.connect(make_callback(idx))
            self.effect_buttons.append(btn)
            self.effect_buttons_layout.addWidget(btn, row, col)

    def valid(self):
        return isinstance(self.device, VialKeyboard) and self.device.keyboard.lighting_qmk_rgblight

    def on_underglow_brightness_changed(self, value):
        self.device.keyboard.set_qmk_rgblight_brightness(value)
        self.update.emit()

    def on_underglow_effect_changed(self):
        # This method is no longer used since we handle clicks in build_effect_buttons
        pass

    def on_underglow_color(self):
        parent = self.underglow_color.window() if hasattr(self.underglow_color, 'window') else None
        dlg = ModernColorPickerDialog(self.current_color(), parent)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.on_underglow_color_finished(dlg.selectedColor())

    def on_underglow_color_finished(self, color):
        if not color or not color.isValid():
            return
        border = themes.Theme.border_color()
        self.underglow_color.setStyleSheet(f"QLabel {{ background-color: {color.name()}; border-radius: 8px; border: 2px solid {border}; }}")
        h, s, v, a = color.getHsvF()
        if h < 0:
            h = 0
        self.device.keyboard.set_qmk_rgblight_color(int(255 * h), int(255 * s), int(255 * v))
        self.update.emit()

    def current_color(self):
        return QColor.fromHsvF(self.device.keyboard.underglow_color[0] / 255.0,
                               self.device.keyboard.underglow_color[1] / 255.0,
                               self.device.keyboard.underglow_brightness / 255.0)


class QmkBacklightHandler(BasicHandler):

    def __init__(self, container):
        super().__init__(container)

        row = container.rowCount()

        # Create a group for backlight controls
        self.group_backlight = QGroupBox(tr("RGBConfigurator", "Backlight (QMK)"))
        backlight_font = self.group_backlight.font()
        backlight_font.setPointSize(11)
        self.group_backlight.setFont(backlight_font)
        backlight_layout = QGridLayout()
        backlight_layout.setSpacing(10)
        backlight_layout.setContentsMargins(12, 10, 12, 10)

        self.lbl_backlight_brightness = QLabel(tr("RGBConfigurator", "Brightness:"))
        self.lbl_backlight_brightness.setMinimumWidth(140)
        lbl_font = self.lbl_backlight_brightness.font()
        lbl_font.setPointSize(11)
        self.lbl_backlight_brightness.setFont(lbl_font)
        backlight_layout.addWidget(self.lbl_backlight_brightness, 0, 0)
        self.backlight_brightness = QSlider(QtCore.Qt.Orientation.Horizontal)
        self.backlight_brightness.setMinimum(0)
        self.backlight_brightness.setMaximum(255)
        self.backlight_brightness.setMinimumHeight(28)
        self.backlight_brightness.valueChanged.connect(self.on_backlight_brightness_changed)
        backlight_layout.addWidget(self.backlight_brightness, 0, 1)

        self.lbl_backlight_breathing = QLabel(tr("RGBConfigurator", "Breathing:"))
        self.lbl_backlight_breathing.setMinimumWidth(140)
        self.lbl_backlight_breathing.setFont(lbl_font)
        backlight_layout.addWidget(self.lbl_backlight_breathing, 1, 0)
        self.backlight_breathing = QCheckBox()
        self.backlight_breathing.setMinimumHeight(28)
        self.backlight_breathing.stateChanged.connect(self.on_backlight_breathing_changed)
        backlight_layout.addWidget(self.backlight_breathing, 1, 1)

        self.group_backlight.setLayout(backlight_layout)
        container.addWidget(self.group_backlight, row, 0, 1, 2)

        self.widgets = [self.group_backlight]

    def update_from_keyboard(self):
        if not self.valid():
            return

        self.backlight_brightness.setValue(self.device.keyboard.backlight_brightness)
        self.backlight_breathing.setChecked(self.device.keyboard.backlight_effect == 1)

    def valid(self):
        return isinstance(self.device, VialKeyboard) and self.device.keyboard.lighting_qmk_backlight

    def on_backlight_brightness_changed(self, value):
        self.device.keyboard.set_qmk_backlight_brightness(value)

    def on_backlight_breathing_changed(self, checked):
        self.device.keyboard.set_qmk_backlight_effect(int(checked))


class VialRGBHandler(BasicHandler):

    def __init__(self, container):
        super().__init__(container)

        row = container.rowCount()

        # Effect selection label
        self.lbl_rgb_effect = QLabel(tr("RGBConfigurator", "Effect:"))
        lbl_font = self.lbl_rgb_effect.font()
        lbl_font.setPointSize(11)
        self.lbl_rgb_effect.setFont(lbl_font)
        container.addWidget(self.lbl_rgb_effect, row, 0)
        row += 1

        # Create scroll area for effect buttons
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(180)
        
        effect_widget = QWidget()
        self.effect_buttons_layout = QGridLayout()
        self.effect_buttons_layout.setSpacing(8)
        self.effect_buttons_layout.setContentsMargins(5, 5, 5, 5)
        effect_widget.setLayout(self.effect_buttons_layout)
        scroll.setWidget(effect_widget)
        container.addWidget(scroll, row, 0, 1, 2)
        row += 1

        # Color label
        self.lbl_rgb_color = QLabel(tr("RGBConfigurator", "Color:"))
        self.lbl_rgb_color.setMinimumWidth(140)
        self.lbl_rgb_color.setFont(lbl_font)
        container.addWidget(self.lbl_rgb_color, row, 0)
        
        # Modern color selector with gradient effect
        color_container = QHBoxLayout()
        self.rgb_color = ClickableLabel(" ")
        self.rgb_color.setMinimumHeight(48)
        self.rgb_color.setMinimumWidth(200)
        self.rgb_color.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        border = themes.Theme.border_color()
        link = themes.Theme.link_color()
        highlight = themes.Theme.highlight_color()
        window_bg = themes.Theme.window_color()
        self.rgb_color.setStyleSheet(f"""
            QLabel {{
                border-radius: 8px;
                border: 2px solid {border};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {highlight}, stop:1 {window_bg});
                padding: 4px;
            }}
            QLabel:hover {{
                border: 2px solid {link};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {link}, stop:1 {highlight});
            }}
        """)
        self.rgb_color.clicked.connect(self.on_rgb_color)
        color_container.addWidget(self.rgb_color)
        
        container.addLayout(color_container, row, 1)
        row += 1

        # Brightness label and slider
        self.lbl_rgb_brightness = QLabel(tr("RGBConfigurator", "Brightness:"))
        self.lbl_rgb_brightness.setMinimumWidth(140)
        self.lbl_rgb_brightness.setFont(lbl_font)
        container.addWidget(self.lbl_rgb_brightness, row, 0)
        self.rgb_brightness = QSlider(QtCore.Qt.Orientation.Horizontal)
        self.rgb_brightness.setMinimum(0)
        self.rgb_brightness.setMaximum(255)
        self.rgb_brightness.setMinimumHeight(28)
        self.rgb_brightness.valueChanged.connect(self.on_rgb_brightness_changed)
        container.addWidget(self.rgb_brightness, row, 1)
        row += 1

        # Speed label and slider
        self.lbl_rgb_speed = QLabel(tr("RGBConfigurator", "Speed:"))
        self.lbl_rgb_speed.setMinimumWidth(140)
        self.lbl_rgb_speed.setFont(lbl_font)
        container.addWidget(self.lbl_rgb_speed, row, 0)
        self.rgb_speed = QSlider(QtCore.Qt.Orientation.Horizontal)
        self.rgb_speed.setMinimum(0)
        self.rgb_speed.setMaximum(255)
        self.rgb_speed.setMinimumHeight(28)
        self.rgb_speed.valueChanged.connect(self.on_rgb_speed_changed)
        container.addWidget(self.rgb_speed, row, 1)

        self.widgets = [self.lbl_rgb_effect, scroll, self.lbl_rgb_color, self.rgb_color, 
                        self.lbl_rgb_brightness, self.rgb_brightness, self.lbl_rgb_speed, self.rgb_speed]

        self.effects = []
        self.effect_buttons = []
        self.current_effect_idx = 0

    def on_rgb_brightness_changed(self, value):
        self.keyboard.set_vialrgb_brightness(value)

    def on_rgb_speed_changed(self, value):
        self.keyboard.set_vialrgb_speed(value)

    def on_rgb_color(self):
        parent = self.rgb_color.window() if hasattr(self.rgb_color, 'window') else None
        dlg = ModernColorPickerDialog(self.current_color(), parent)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.on_rgb_color_finished(dlg.selectedColor())

    def on_rgb_color_finished(self, color):
        if not color or not color.isValid():
            return
        border = themes.Theme.border_color()
        link = themes.Theme.link_color()
        highlight = themes.Theme.highlight_color()
        window_bg = themes.Theme.window_color()
        self.rgb_color.setStyleSheet(f"""
            QLabel {{
                border-radius: 8px;
                border: 2px solid {border};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color.name()}, stop:1 {window_bg});
                padding: 4px;
            }}
            QLabel:hover {{
                border: 2px solid {link};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color.name()}, stop:1 {highlight});
            }}
        """)
        
        h, s, v, a = color.getHsvF()
        if h < 0:
            h = 0
        self.keyboard.set_vialrgb_color(int(255 * h), int(255 * s), self.keyboard.rgb_hsv[2])
        self.update.emit()

    def current_color(self):
        return QColor.fromHsvF(self.keyboard.rgb_hsv[0] / 255.0,
                               self.keyboard.rgb_hsv[1] / 255.0,
                               1.0)

    def rebuild_effects(self):
        self.effects = []
        for effect in VIALRGB_EFFECTS:
            if effect.idx in self.keyboard.rgb_supported_effects:
                self.effects.append(effect)

        # Clear old buttons
        for btn in self.effect_buttons:
            btn.deleteLater()
        self.effect_buttons.clear()
        
        # Create new button grid (4 columns for better layout)
        for idx, effect in enumerate(self.effects):
            btn = QPushButton(effect.name)
            btn.setMinimumHeight(36)
            btn.setCheckable(True)
            btn_font = btn.font()
            btn_font.setPointSize(10)
            btn.setFont(btn_font)
            
            row = idx // 4
            col = idx % 4
            
            def make_callback(effect_obj):
                def callback():
                    self.keyboard.set_vialrgb_mode(effect_obj.idx)
                    self.update_effect_buttons()
                return callback
            
            btn.clicked.connect(make_callback(effect))
            self.effect_buttons.append(btn)
            self.effect_buttons_layout.addWidget(btn, row, col)

    def update_effect_buttons(self):
        """Update button states to show which effect is currently selected"""
        for idx, btn in enumerate(self.effect_buttons):
            if idx < len(self.effects):
                is_selected = self.effects[idx].idx == self.keyboard.rgb_mode
                btn.setChecked(is_selected)

    def update_from_keyboard(self):
        if not self.valid():
            return

        self.rebuild_effects()
        self.update_effect_buttons()
        self.rgb_brightness.setMaximum(self.keyboard.rgb_maximum_brightness)
        self.rgb_brightness.setValue(self.keyboard.rgb_hsv[2])
        self.rgb_speed.setValue(self.keyboard.rgb_speed)
        
        color = self.current_color()
        color_name = color.name()
        border = themes.Theme.border_color()
        link = themes.Theme.link_color()
        highlight = themes.Theme.highlight_color()
        window_bg = themes.Theme.window_color()
        self.rgb_color.setStyleSheet(f"""
            QLabel {{
                border-radius: 8px;
                border: 2px solid {border};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color_name}, stop:1 {window_bg});
                padding: 4px;
            }}
            QLabel:hover {{
                border: 2px solid {link};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color_name}, stop:1 {highlight});
            }}
        """)


    def valid(self):
        return isinstance(self.device, VialKeyboard) and self.device.keyboard.lighting_vialrgb


class RGBConfigurator(BasicEditor):

    def __init__(self):
        super().__init__()

        self.addStretch()

        w = QWidget()
        w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.container = QGridLayout()
        self.container.setSpacing(16)
        self.container.setContentsMargins(15, 15, 15, 15)
        w.setLayout(self.container)
        self.addWidget(w, 0)
        self.setAlignment(w, QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignTop)

        self.handler_backlight = QmkBacklightHandler(self.container)
        self.handler_backlight.update.connect(self.update_from_keyboard)
        self.handler_rgblight = QmkRgblightHandler(self.container)
        self.handler_rgblight.update.connect(self.update_from_keyboard)
        self.handler_vialrgb = VialRGBHandler(self.container)
        self.handler_vialrgb.update.connect(self.update_from_keyboard)
        self.handlers = [self.handler_backlight, self.handler_rgblight, self.handler_vialrgb]

        self.addStretch()
        buttons = QHBoxLayout()
        buttons.addStretch()
        save_btn = QPushButton(tr("RGBConfigurator", "Save"))
        save_btn.setMinimumSize(120, 40)
        btn_font = save_btn.font()
        btn_font.setPointSize(11)
        save_btn.setFont(btn_font)
        buttons.addWidget(save_btn)
        save_btn.clicked.connect(self.on_save)
        self.addLayout(buttons)

    def on_save(self):
        self.device.keyboard.save_rgb()

    def valid(self):
        return isinstance(self.device, VialKeyboard) and \
               (self.device.keyboard.lighting_qmk_rgblight or self.device.keyboard.lighting_qmk_backlight
                or self.device.keyboard.lighting_vialrgb)

    def block_signals(self):
        for h in self.handlers:
            h.block_signals()

    def unblock_signals(self):
        for h in self.handlers:
            h.unblock_signals()

    def update_from_keyboard(self):
        self.device.keyboard.reload_rgb()

        self.block_signals()

        for h in self.handlers:
            h.update_from_keyboard()

        self.unblock_signals()

    def rebuild(self, device):
        super().rebuild(device)

        for h in self.handlers:
            h.set_device(device)

        if not self.valid():
            return

        self.update_from_keyboard()


class ModernColorPickerDialog(QDialog):
    """现代化的颜色选择器对话框"""
    
    def __init__(self, initial_color=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Color Picker")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.selected_color = initial_color if initial_color and initial_color.isValid() else QColor(31, 111, 235)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 颜色预览 - 大色块
        preview_container = QHBoxLayout()
        preview_label = QLabel("Color Preview:")
        preview_label.setMinimumWidth(100)
        self.color_preview = QLabel()
        self.color_preview.setMinimumHeight(80)
        border = themes.Theme.border_color()
        self.color_preview.setStyleSheet(f"""
            QLabel {{
                border-radius: 10px;
                border: 2px solid {border};
                background-color: {self.selected_color.name()};
            }}
        """)
        preview_container.addWidget(preview_label)
        preview_container.addWidget(self.color_preview, 1)
        layout.addLayout(preview_container)
        
        # 滑块样式
        link = themes.Theme.link_color()
        slider_groove_style = f"""
            QSlider::groove:horizontal {{
                border: 1px solid {border};
                height: 8px;
                background-color: {border};
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                border: 2px solid {link};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
        """
        
        # Hue 滑块
        hue_layout = QHBoxLayout()
        hue_label = QLabel("Hue:")
        hue_label.setMinimumWidth(100)
        self.hue_slider = QSlider(Qt.Orientation.Horizontal)
        self.hue_slider.setMinimum(0)
        self.hue_slider.setMaximum(359)
        h, s, v = self.selected_color.getHsv()[:3]
        self.hue_slider.setValue(h if h >= 0 else 0)
        self.hue_slider.setMinimumHeight(24)
        self.hue_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {border};
                height: 8px;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, 
                    stop:0 #ff0000, stop:0.17 #ffff00, stop:0.33 #00ff00, 
                    stop:0.5 #00ffff, stop:0.67 #0000ff, stop:0.83 #ff00ff, stop:1 #ff0000);
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                border: 2px solid {link};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
        """)
        self.hue_slider.valueChanged.connect(self.on_hue_changed)
        hue_layout.addWidget(hue_label)
        hue_layout.addWidget(self.hue_slider, 1)
        hue_layout.addWidget(QLabel(str(self.hue_slider.value()) + "°"), 0)
        self.hue_value_label = hue_layout.itemAt(hue_layout.count() - 1).widget()
        layout.addLayout(hue_layout)
        
        # Saturation 滑块
        sat_layout = QHBoxLayout()
        sat_label = QLabel("Saturation:")
        sat_label.setMinimumWidth(100)
        self.sat_slider = QSlider(Qt.Orientation.Horizontal)
        self.sat_slider.setMinimum(0)
        self.sat_slider.setMaximum(100)
        self.sat_slider.setValue(s)
        self.sat_slider.setMinimumHeight(24)
        self.sat_slider.setStyleSheet(slider_groove_style)
        self.sat_slider.valueChanged.connect(self.on_saturation_changed)
        sat_layout.addWidget(sat_label)
        sat_layout.addWidget(self.sat_slider, 1)
        sat_layout.addWidget(QLabel(str(self.sat_slider.value()) + "%"), 0)
        self.sat_value_label = sat_layout.itemAt(sat_layout.count() - 1).widget()
        layout.addLayout(sat_layout)
        
        # Value/Brightness 滑块
        val_layout = QHBoxLayout()
        val_label = QLabel("Brightness:")
        val_label.setMinimumWidth(100)
        self.val_slider = QSlider(Qt.Orientation.Horizontal)
        self.val_slider.setMinimum(0)
        self.val_slider.setMaximum(100)
        self.val_slider.setValue(v)
        self.val_slider.setMinimumHeight(24)
        self.val_slider.setStyleSheet(slider_groove_style)
        self.val_slider.valueChanged.connect(self.on_value_changed)
        val_layout.addWidget(val_label)
        val_layout.addWidget(self.val_slider, 1)
        val_layout.addWidget(QLabel(str(self.val_slider.value()) + "%"), 0)
        self.val_value_label = val_layout.itemAt(val_layout.count() - 1).widget()
        layout.addLayout(val_layout)
        
        # RGB 和 HEX 输入框
        info_layout = QHBoxLayout()
        info_layout.setSpacing(12)
        
        # RGB 输入区域
        rgb_container = QHBoxLayout()
        rgb_label = QLabel("RGB:")
        rgb_label.setMinimumWidth(50)
        self.rgb_r_input = QSpinBox()
        self.rgb_r_input.setMinimum(0)
        self.rgb_r_input.setMaximum(255)
        self.rgb_r_input.setMinimumWidth(50)
        self.rgb_r_input.setValue(self.selected_color.getRgb()[0])
        self.rgb_r_input.valueChanged.connect(self.on_rgb_input_changed)
        
        self.rgb_g_input = QSpinBox()
        self.rgb_g_input.setMinimum(0)
        self.rgb_g_input.setMaximum(255)
        self.rgb_g_input.setMinimumWidth(50)
        self.rgb_g_input.setValue(self.selected_color.getRgb()[1])
        self.rgb_g_input.valueChanged.connect(self.on_rgb_input_changed)
        
        self.rgb_b_input = QSpinBox()
        self.rgb_b_input.setMinimum(0)
        self.rgb_b_input.setMaximum(255)
        self.rgb_b_input.setMinimumWidth(50)
        self.rgb_b_input.setValue(self.selected_color.getRgb()[2])
        self.rgb_b_input.valueChanged.connect(self.on_rgb_input_changed)
        
        rgb_container.addWidget(rgb_label)
        rgb_container.addWidget(self.rgb_r_input)
        rgb_container.addWidget(self.rgb_g_input)
        rgb_container.addWidget(self.rgb_b_input)
        info_layout.addLayout(rgb_container)
        
        # HEX 输入框
        hex_label = QLabel("HEX:")
        hex_label.setMinimumWidth(50)
        self.hex_input = QLineEdit()
        self.hex_input.setText(self.selected_color.name().upper())
        self.hex_input.setMinimumWidth(100)
        self.hex_input.setMaxLength(7)
        self.hex_input.textChanged.connect(self.on_hex_input_changed)
        info_layout.addWidget(hex_label)
        info_layout.addWidget(self.hex_input)
        
        layout.addLayout(info_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setMinimumSize(100, 36)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumSize(100, 36)
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.apply_theme()
    
    def apply_theme(self):
        """应用主题样式"""
        # 从主题获取颜色
        window_bg = themes.Theme.window_color()
        base_bg = themes.Theme.base_color()
        button_bg = themes.Theme.button_color()
        text_color = themes.Theme.text_color()
        button_text = themes.Theme.button_text_color()
        highlight = themes.Theme.highlight_color()
        link = themes.Theme.link_color()
        border = themes.Theme.border_color()
        
        # 根据主题类型调整一些特殊颜色
        if themes.Theme.is_dark_theme():
            hover_bg = "#30363d"
            focus_bg = "#0d1117"
        else:
            hover_bg = "#e8e8e8"
            focus_bg = "#ffffff"
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {window_bg};
                color: {button_text};
            }}
            QLabel {{
                color: {button_text};
                font-size: 11px;
            }}
            QSpinBox, QLineEdit {{
                background-color: {base_bg};
                color: {button_text};
                border: 1px solid {border};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }}
            QSpinBox:focus, QLineEdit:focus {{
                border: 1px solid {link};
                background-color: {focus_bg};
            }}
            QPushButton {{
                background-color: {button_bg};
                color: {button_text};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
                border: 1px solid {link};
            }}
            QSlider {{
                background-color: transparent;
            }}
        """)
    
    def on_hue_changed(self, value):
        self.update_color_from_sliders()
        self.hue_value_label.setText(f"{value}°")
    
    def on_saturation_changed(self, value):
        self.update_color_from_sliders()
        self.sat_value_label.setText(f"{value}%")
    
    def on_value_changed(self, value):
        self.update_color_from_sliders()
        self.val_value_label.setText(f"{value}%")
    
    def update_color_from_sliders(self):
        """从滑块更新颜色"""
        h = self.hue_slider.value()
        s = self.sat_slider.value()
        v = self.val_slider.value()
        
        self.selected_color.setHsv(h, int(s * 255 / 100), int(v * 255 / 100))
        
        # 获取主题边框颜色
        border = themes.Theme.border_color()
        
        # 更新预览
        self.color_preview.setStyleSheet(f"""
            QLabel {{
                border-radius: 10px;
                border: 2px solid {border};
                background-color: {self.selected_color.name()};
            }}
        """)
        
        # 更新输入框（阻止信号避免死循环）
        self.rgb_r_input.blockSignals(True)
        self.rgb_g_input.blockSignals(True)
        self.rgb_b_input.blockSignals(True)
        self.hex_input.blockSignals(True)
        
        r, g, b = self.selected_color.getRgb()[:3]
        self.rgb_r_input.setValue(r)
        self.rgb_g_input.setValue(g)
        self.rgb_b_input.setValue(b)
        self.hex_input.setText(self.selected_color.name().upper())
        
        self.rgb_r_input.blockSignals(False)
        self.rgb_g_input.blockSignals(False)
        self.rgb_b_input.blockSignals(False)
        self.hex_input.blockSignals(False)
    
    def on_rgb_input_changed(self):
        """处理 RGB 输入框变化"""
        r = self.rgb_r_input.value()
        g = self.rgb_g_input.value()
        b = self.rgb_b_input.value()
        
        self.selected_color.setRgb(r, g, b)
        self.update_color_display()
    
    def on_hex_input_changed(self):
        """处理 HEX 输入框变化"""
        hex_text = self.hex_input.text().strip()
        
        # 确保以 # 开头
        if not hex_text.startswith('#'):
            hex_text = '#' + hex_text
        
        # 验证 HEX 格式
        if len(hex_text) == 7 and all(c in '0123456789ABCDEFabcdef#' for c in hex_text):
            color = QColor(hex_text)
            if color.isValid():
                self.selected_color = color
                self.update_color_display()
    
    def update_color_display(self):
        """更新颜色显示和滑块"""
        # 获取主题边框颜色
        border = themes.Theme.border_color()
        
        # 更新预览
        self.color_preview.setStyleSheet(f"""
            QLabel {{
                border-radius: 10px;
                border: 2px solid {border};
                background-color: {self.selected_color.name()};
            }}
        """)
        
        # 更新 HSV 滑块（阻止信号避免死循环）
        self.hue_slider.blockSignals(True)
        self.sat_slider.blockSignals(True)
        self.val_slider.blockSignals(True)
        
        h, s, v = self.selected_color.getHsv()[:3]
        if h >= 0:
            self.hue_slider.setValue(h)
        self.sat_slider.setValue(int(s * 100 / 255))
        self.val_slider.setValue(int(v * 100 / 255))
        
        self.hue_slider.blockSignals(False)
        self.sat_slider.blockSignals(False)
        self.val_slider.blockSignals(False)
        
        # 更新输入框（阻止信号避免死循环）
        self.rgb_r_input.blockSignals(True)
        self.rgb_g_input.blockSignals(True)
        self.rgb_b_input.blockSignals(True)
        self.hex_input.blockSignals(True)
        
        r, g, b = self.selected_color.getRgb()[:3]
        self.rgb_r_input.setValue(r)
        self.rgb_g_input.setValue(g)
        self.rgb_b_input.setValue(b)
        self.hex_input.setText(self.selected_color.name().upper())
        
        self.rgb_r_input.blockSignals(False)
        self.rgb_g_input.blockSignals(False)
        self.rgb_b_input.blockSignals(False)
        self.hex_input.blockSignals(False)
        
        # 更新标签显示
        self.hue_value_label.setText(f"{self.hue_slider.value()}°")
        self.sat_value_label.setText(f"{self.sat_slider.value()}%")
        self.val_value_label.setText(f"{self.val_slider.value()}%")
    
    def selectedColor(self):
        return self.selected_color
