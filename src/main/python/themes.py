# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor

themes = [
    ("Photon-light", {
    QPalette.ColorRole.Window: "#ffffff",
    QPalette.ColorRole.WindowText: "#1a1a1a",
    QPalette.ColorRole.Base: "#fafafa",
    QPalette.ColorRole.AlternateBase: "#f5f5f5",
    QPalette.ColorRole.ToolTipBase: "#f0f0f0",
    QPalette.ColorRole.ToolTipText: "#1a1a1a",
    QPalette.ColorRole.Text: "#1a1a1a",
    QPalette.ColorRole.Button: "#f5f5f5",
    QPalette.ColorRole.ButtonText: "#1a1a1a",
    QPalette.ColorRole.BrightText: "#0052cc",
    QPalette.ColorRole.Link: "#0052cc",
    QPalette.ColorRole.Highlight: "#0052cc",
    QPalette.ColorRole.HighlightedText: "#ffffff",
    QPalette.ColorRole.Light: "#e0e0e0",
    QPalette.ColorRole.Midlight: "#d5d5d5",
    QPalette.ColorRole.Dark: "#f5f5f5",
    QPalette.ColorRole.Mid: "#e8e8e8",
    QPalette.ColorRole.Shadow: "#ffffff",
    (QPalette.ColorGroup.Active, QPalette.ColorRole.Button): "#e8e8e8",
    (QPalette.ColorGroup.Active, QPalette.ColorRole.Window): "#ffffff",
    (QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText): "#999999",
    (QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText): "#999999",
    (QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text): "#999999",
    (QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light): "#e0e0e0",
    (QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight): "#0052cc",
    }),

    ("Phantom-dark", {
    QPalette.ColorRole.Window: "#0d1117",
    QPalette.ColorRole.WindowText: "#e6edf3",
    QPalette.ColorRole.Base: "#161b22",
    QPalette.ColorRole.AlternateBase: "#1c2128",
    QPalette.ColorRole.ToolTipBase: "#1c2128",
    QPalette.ColorRole.ToolTipText: "#e6edf3",
    QPalette.ColorRole.Text: "#e6edf3",
    QPalette.ColorRole.Button: "#21262d",
    QPalette.ColorRole.ButtonText: "#c9d1d9",
    QPalette.ColorRole.BrightText: "#79c0ff",
    QPalette.ColorRole.Link: "#58a6ff",
    QPalette.ColorRole.Highlight: "#1f6feb",
    QPalette.ColorRole.HighlightedText: "#ffffff",
    QPalette.ColorRole.Light: "#30363d",
    QPalette.ColorRole.Midlight: "#484f58",
    QPalette.ColorRole.Dark: "#0d1117",
    QPalette.ColorRole.Mid: "#21262d",
    QPalette.ColorRole.Shadow: "#000000",
    (QPalette.ColorGroup.Active, QPalette.ColorRole.Button): "#30363d",
    (QPalette.ColorGroup.Active, QPalette.ColorRole.Window): "#0d1117",
    (QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText): "#6e7681",
    (QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText): "#6e7681",
    (QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text): "#6e7681",
    (QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light): "#21262d",
    (QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight): "#1f6feb",
    }),
]

palettes = dict()

for name, colors in themes:
    palette = QPalette()
    for role, color in colors.items():
        if not isinstance(role, (tuple, list)):
            role = (role,)
        palette.setColor(*role, QColor(color))
    palettes[name] = palette


class Theme:

    theme = ""
    # 缓存当前主题的颜色
    _colors = {}

    @classmethod
    def set_theme(cls, theme):
        cls.theme = theme
        cls._colors = {}  # 清空颜色缓存
        if theme in palettes:
            QApplication.setPalette(palettes[theme])
            QApplication.setStyle("Fusion")
            # 缓存颜色便于访问
            for name, colors in themes:
                if name == theme:
                    for role, color in colors.items():
                        if not isinstance(role, (tuple, list)):
                            cls._colors[role] = color
                    break

    @classmethod
    def get_theme(cls):
        return cls.theme

    @classmethod
    def is_light_theme(cls):
        """判断是否为浅色主题"""
        return cls.theme in ("Photon-light", "Light")
    
    @classmethod
    def is_dark_theme(cls):
        """判断是否为深色主题"""
        return not cls.is_light_theme()

    @classmethod
    def get_color(cls, role):
        """获取指定角色的颜色值（十六进制字符串）"""
        return cls._colors.get(role, "#ffffff")
    
    @classmethod
    def window_color(cls):
        """主窗口背景色"""
        return cls.get_color(QPalette.ColorRole.Window)
    
    @classmethod
    def base_color(cls):
        """基础背景色"""
        return cls.get_color(QPalette.ColorRole.Base)
    
    @classmethod
    def button_color(cls):
        """按钮背景色"""
        return cls.get_color(QPalette.ColorRole.Button)
    
    @classmethod
    def text_color(cls):
        """文本颜色"""
        return cls.get_color(QPalette.ColorRole.Text)
    
    @classmethod
    def highlight_color(cls):
        """高亮/选中颜色"""
        return cls.get_color(QPalette.ColorRole.Highlight)
    
    @classmethod
    def link_color(cls):
        """链接颜色"""
        return cls.get_color(QPalette.ColorRole.Link)
    
    @classmethod
    def border_color(cls):
        """边框颜色 - 使用 Light 角色"""
        return cls.get_color(QPalette.ColorRole.Light)
    
    @classmethod
    def alternate_base_color(cls):
        """交替背景色"""
        return cls.get_color(QPalette.ColorRole.AlternateBase)
    
    @classmethod
    def button_text_color(cls):
        """按钮文本颜色"""
        return cls.get_color(QPalette.ColorRole.ButtonText)
    
    @classmethod
    def mid_color(cls):
        """中间色调"""
        return cls.get_color(QPalette.ColorRole.Mid)
    
    @classmethod  
    def midlight_color(cls):
        """中亮色调"""
        return cls.get_color(QPalette.ColorRole.Midlight)
    
    @classmethod
    def dark_color(cls):
        """深色调"""
        return cls.get_color(QPalette.ColorRole.Dark)

    @classmethod
    def mask_light_factor(cls):
        if cls.theme in ("Light", "Phantom-light"):
            return 103
        return 150