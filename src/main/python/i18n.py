# SPDX-License-Identifier: GPL-2.0-or-later
"""
Internationalization (i18n) module for Vial GUI.
"""

import locale
import sys
from PyQt6.QtCore import QSettings


class I18n:
    """Internationalization manager with hot-switch support."""
    
    # Supported languages
    LANGUAGES = {
        "en": "English",
        "zh_CN": "简体中文",
    }
    
    # Current language code
    _current_lang = "en"
    
    # List of widgets that need to be updated on language change
    _observers = []
    
    # Translation dictionaries
    _translations = {
        "en": {},  # English is the default, no translation needed
        "zh_CN": {
            # Menu
            "File": "文件",
            "Keyboard layout": "键盘布局",
            "Security": "安全",
            "Theme": "主题",
            "Language": "语言",
            "About": "关于",
            
            # Menu File
            "Load saved layout...": "加载已保存的布局...",
            "Save current layout...": "保存当前布局...",
            "Sideload VIA JSON...": "侧载 VIA JSON...",
            "Download VIA definitions": "下载 VIA 定义",
            "Load dummy JSON...": "加载虚拟 JSON...",
            "Exit": "退出",
            
            # Menu Security
            "Unlock": "解锁",
            "Lock": "锁定",
            "Reboot to bootloader": "重启到引导程序",
            
            # Menu Theme
            "System": "跟随系统",
            
            # Menu About
            "About Vial...": "关于 Vial...",
            
            # MainWindow
            "Refresh": "刷新",
            "Keymap": "键位映射",
            "Layout": "布局",
            "Macros": "宏",
            "Lighting": "灯光",
            "Tap Dance": "多击触发",
            "Combos": "组合键",
            "Key Overrides": "按键覆盖",
            "Alt Repeat Key": "备选重复键",
            "QMK Settings": "QMK 设置",
            "Matrix tester": "矩阵测试",
            "Firmware updater": "固件更新",
            "In order to fully apply the theme you should restart the application.": 
                "为了完全应用主题，您需要重启应用程序。",
            "In order to fully apply the language you should restart the application.":
                "为了完全应用语言设置，您需要重启应用程序。",
            
            # No devices message
            'No devices detected. Connect a Vial-compatible device and press "Refresh"<br>or select "File" → "Download VIA definitions" in order to enable support for VIA keyboards.':
                '未检测到设备。请连接 Vial 兼容设备并点击"刷新"<br>或选择"文件" → "下载 VIA 定义"以启用 VIA 键盘支持。',
            
            # Linux udev message
            '<br><br>On Linux you need to set up a custom udev rule for keyboards to be detected. Follow the instructions linked below:<br><a href="https://get.vial.today/manual/linux-udev.html">https://get.vial.today/manual/linux-udev.html</a>':
                '<br><br>在 Linux 上，您需要设置自定义 udev 规则才能检测到键盘。请按照以下链接的说明操作：<br><a href="https://get.vial.today/manual/linux-udev.html">https://get.vial.today/manual/linux-udev.html</a>',
            
            # RGBConfigurator
            "Underglow (QMK RGB Light)": "底部灯光",
            "Effect:": "效果:",
            "Brightness:": "亮度:",
            "Color:": "颜色:",
            "Speed:": "速度:",
            "Backlight (QMK)": "背光",
            "Breathing:": "呼吸效果:",
            "Save": "保存",
            "Undo": "撤销",
            "Revert": "还原",
            
            # Unlocker
            "In order to proceed, the keyboard must be set into unlocked mode.\n":
                "要继续操作，必须将键盘设置为解锁模式。\n",
            "To exit this mode, you will need to replug the keyboard\n":
                "要退出此模式，您需要重新插拔键盘\n",
            "Press and hold the following keys until the progress bar ":
                "按住以下按键直到进度条",
            
            # TextboxWindow
            "Apply": "应用",
            "Cancel": "取消",
            "Copy": "复制",
            "Paste": "粘贴",
            
            # TabbedKeycodes
            "Basic": "基础键",
            "ISO/JIS": "ISO/JIS 键",
            "Layers": "层切换",
            "Quantum": "高级功能",
            "Backlight": "背光控制",
            "App, Media and Mouse": "应用、媒体和鼠标",
            "MIDI": "MIDI 控制",
            "User": "用户自定义",
            "Macro": "宏",
            
            # Editor tabs and common
            "Enabled": "已启用",
            "Disabled": "已禁用",
            "On": "开",
            "Off": "关",
            "Yes": "是",
            "No": "否",
            "OK": "确定",
            "Reset": "重置",
            "Clear": "清除",
            "Add": "添加",
            "Remove": "移除",
            "Delete": "删除",
            "Edit": "编辑",
            "Import": "导入",
            "Export": "导出",
            "Record": "录制",
            "Stop": "停止",
            "Play": "播放",
            "Test": "测试",
            "Enable": "启用",
            
            # Combos editor
            "Key 1": "按键 1",
            "Key 2": "按键 2",
            "Key 3": "按键 3",
            "Key 4": "按键 4",
            "Output key": "输出键",
            
            # Tap Dance editor
            "On tap": "单击时",
            "On hold": "长按时",
            "On double tap": "双击时",
            "On tap + hold": "单击后长按时",
            "Tapping term (ms)": "触发时间 (毫秒)",
            
            # Key Override editor
            "Enable on layers": "在以下层启用",
            "Trigger": "触发键",
            "Trigger mods": "触发修饰键",
            "Negative mods": "排除修饰键",
            "Suppressed mods": "抑制修饰键",
            "Replacement": "替换键",
            "Options": "选项",
            "Enable all": "全部启用",
            "Disable all": "全部禁用",
            "Activate when the trigger key is pressed down": "当触发键按下时激活",
            "Activate when a necessary modifier is pressed down": "当必要的修饰键按下时激活",
            "Activate when a negative modifier is released": "当排除修饰键释放时激活",
            "Activate on one modifier": "单个修饰键时激活",
            "Don't deactivate when another key is pressed down": "当其他键按下时不停用",
            "Don't register the trigger key again after the override is deactivated": "覆盖停用后不再注册触发键",
            
            # Macro recorder
            "Record macro": "录制宏",
            "Stop recording": "停止录制",
            "Add action": "添加动作",
            "Tap Enter": "点击回车",
            "Open Text Editor...": "打开文本编辑器...",
            "Append to current": "追加到当前",
            "Replace everything": "替换全部",
            "Memory used by macros: {}/{}": "宏使用的内存: {}/{}",
            
            # Macro action types
            "Text": "文本",
            "Down": "按下",
            "Up": "抬起",
            "Tap": "点击",
            "Delay (ms)": "延迟 (毫秒)",
            
            # Firmware flasher
            "Select file...": "选择文件...",
            "Flash": "刷写",
            "Restore current layout after flashing": "刷写后恢复当前布局",
            "Valid Vial Bootloader device at {}": "在 {} 发现有效的 Vial 引导程序设备",
            "Vial keyboard detected": "检测到 Vial 键盘",
            "Firmware update package: {}": "固件更新包: {}",
            "Error: Please select a firmware update package": "错误: 请选择固件更新包",
            "Error: Firmware is too large. Check you've selected the correct file": "错误: 固件过大。请检查是否选择了正确的文件",
            "Preparing to flash...": "准备刷写...",
            "Backing up current layout...": "正在备份当前布局...",
            "Error: Firmware UID does not match keyboard UID. Check that you have the correct file": "错误: 固件 UID 与键盘 UID 不匹配。请检查是否选择了正确的文件",
            "Restarting in bootloader mode...": "正在重启到引导程序模式...",
            "Looking for devices...": "正在查找设备...",
            "Found Vial Bootloader device at {}": "在 {} 发现 Vial 引导程序设备",
            "Found Vial keyboard at {}": "在 {} 发现 Vial 键盘",
            "Restoring saved layout...": "正在恢复已保存的布局...",
            "Done!": "完成!",
            
            # Matrix tester
            "Unlock the keyboard before testing:": "测试前请先解锁键盘:",
            
            # QMK Settings tabs
            "Magic": "魔术键",
            "Grave Escape": "Grave Escape",
            "Tap-Hold": "点按-长按",
            "Auto Shift": "自动上档",
            "Combo": "组合键",
            "One Shot Keys": "一次性按键",
            "Mouse keys": "鼠标键",
            "Reset all settings to default values?": "重置所有设置为默认值？",
            
            # QMK Settings - Magic
            "Swap Caps Lock and Left Control": "交换大写锁定和左Control",
            "Treat Caps Lock as Control": "将大写锁定视为Control",
            "Swap Left Alt and GUI": "交换左Alt和GUI",
            "Swap Right Alt and GUI": "交换右Alt和GUI",
            "Disable the GUI keys": "禁用GUI键",
            "Swap ` and Escape": "交换 ` 和 Escape",
            "Swap \\ and Backspace": "交换 \\ 和 Backspace",
            "Enable N-key rollover": "启用全键无冲",
            "Swap Left Control and GUI": "交换左Control和GUI",
            "Swap Right Control and GUI": "交换右Control和GUI",
            
            # QMK Settings - Grave Escape
            "Always send Escape if Alt is pressed": "如果按下Alt则始终发送Escape",
            "Always send Escape if Control is pressed": "如果按下Control则始终发送Escape",
            "Always send Escape if GUI is pressed": "如果按下GUI则始终发送Escape",
            "Always send Escape if Shift is pressed": "如果按下Shift则始终发送Escape",
            
            # QMK Settings - Tap-Hold
            "Tapping Term": "点按时间",
            "Permissive Hold": "宽容长按",
            "Ignore Mod Tap Interrupt": "忽略Mod-Tap中断",
            "Tapping Force Hold": "强制长按",
            "Retro Tapping": "回溯点按",
            "Hold On Other Key Press": "其他键按下时长按",
            "Quick Tap Term": "快速点按时间",
            "Tap Code Delay": "点按码延迟",
            "Tap Hold Caps Delay": "点按长按大写锁定延迟",
            "Tapping Toggle": "点按切换次数",
            "Chordal Hold": "和弦长按",
            "Flow Tap": "流动点按",
            
            # QMK Settings - Auto Shift
            "Enable for modifiers": "对修饰键启用",
            "Timeout": "超时时间",
            "Do not Auto Shift special keys": "不自动上档特殊键",
            "Do not Auto Shift numeric keys": "不自动上档数字键",
            "Do not Auto Shift alpha characters": "不自动上档字母",
            "Enable keyrepeat": "启用按键重复",
            "Disable keyrepeat when timeout is exceeded": "超时后禁用按键重复",
            
            # QMK Settings - Combo
            "Time out period for combos": "组合键超时时间",
            
            # QMK Settings - One Shot Keys
            "Tapping this number of times holds the key until tapped once again": "点按此次数后保持按键直到再次点按",
            "Time (in ms) before the one shot key is released": "一次性按键释放前的时间 (毫秒)",
            
            # QMK Settings - Mouse keys
            "Delay between pressing a movement key and cursor movement": "按下移动键到光标移动的延迟",
            "Time between cursor movements in milliseconds": "光标移动间隔时间 (毫秒)",
            "Step size": "步进大小",
            "Maximum cursor speed at which acceleration stops": "加速停止时的最大光标速度",
            "Time until maximum cursor speed is reached": "达到最大光标速度的时间",
            "Delay between pressing a wheel key and wheel movement": "按下滚轮键到滚轮移动的延迟",
            "Time between wheel movements": "滚轮移动间隔时间",
            "Maximum number of scroll steps per scroll action": "每次滚动的最大步数",
            "Time until maximum scroll speed is reached": "达到最大滚动速度的时间",
            
            # RGB Effects
            "All Off": "全部关闭",
            "Solid Color": "纯色",
            "Breathing": "呼吸",
            "Band Sat.": "饱和度渐变带",
            "Band Val.": "亮度渐变带",
            "Band Spiral Sat.": "螺旋饱和度渐变",
            "Band Spiral Val.": "螺旋亮度渐变",
            "Cycle All": "全键循环",
            "Cycle Hor.": "水平循环",
            "Cycle Vert.": "垂直循环",
            "Rainbow Chevron": "彩虹 V 形",
            "Cycle Out-In": "由外向内循环",
            "Cycle Spiral": "螺旋循环",
            "Rainbow Beacon": "彩虹灯塔",
            "Rainbow Pinwheel": "彩虹风车",
            "Raindrops": "雨滴",
            "Jellybean": "果冻豆",
            "Hue Breath.": "色相呼吸",
            "Hue Pend.": "色相摆动",
            "Hue Wave": "色相波浪",
            "Typing Heatmap": "打字热力图",
            "Digital Rain": "数字雨",
            "React Simple": "简单响应",
            "React Solid": "纯色响应",
            "React Multi Wide": "宽范围多色响应",
            "React Multi Nexus": "连接点多色响应",
            "Splash": "水花",
            "Multi Splash": "多重水花",
            "Solid Splash": "纯色水花",
            "Solid Multi Splash": "纯色多重水花",
            "Starlight": "星光",
            "Starlight Dual Hue": "双色星光",
            "Starlight Dual Sat.": "双饱和度星光",
            "Riverflow": "流水",
            "Effect": "效果",
            
            # RGB Underglow Effects
            "Static": "静态",
            "Breathing 1": "呼吸 1",
            "Breathing 2": "呼吸 2",
            "Breathing 3": "呼吸 3",
            "Breathing 4": "呼吸 4",
            "Rainbow Mood 1": "彩虹情绪 1",
            "Rainbow Mood 2": "彩虹情绪 2",
            "Rainbow Mood 3": "彩虹情绪 3",
            "Rainbow Swirl 1": "彩虹漩涡 1",
            "Rainbow Swirl 2": "彩虹漩涡 2",
            "Rainbow Swirl 3": "彩虹漩涡 3",
            "Rainbow Swirl 4": "彩虹漩涡 4",
            "Rainbow Swirl 5": "彩虹漩涡 5",
            "Rainbow Swirl 6": "彩虹漩涡 6",
            "Snake 1": "蛇形 1",
            "Snake 2": "蛇形 2",
            "Snake 3": "蛇形 3",
            "Snake 4": "蛇形 4",
            "Snake 5": "蛇形 5",
            "Snake 6": "蛇形 6",
            "Knight 1": "骑士 1",
            "Knight 2": "骑士 2",
            "Knight 3": "骑士 3",
            "Christmas": "圣诞",
            "Static Gradient 1": "静态渐变 1",
            "Static Gradient 2": "静态渐变 2",
            "Static Gradient 3": "静态渐变 3",
            "Static Gradient 4": "静态渐变 4",
            "Static Gradient 5": "静态渐变 5",
            "Static Gradient 6": "静态渐变 6",
            "Static Gradient 7": "静态渐变 7",
            "Static Gradient 8": "静态渐变 8",
            "Static Gradient 9": "静态渐变 9",
            "Static Gradient 10": "静态渐变 10",
            "Alternating": "交替",
            "Twinkle 1": "闪烁 1",
            "Twinkle 2": "闪烁 2",
            "Twinkle 3": "闪烁 3",
            "Twinkle 4": "闪烁 4",
            "Twinkle 5": "闪烁 5",
            "Twinkle 6": "闪烁 6",
            
            # About keyboard dialog
            "Manufacturer": "制造商",
            "Product": "产品",
            "Device": "设备",
            "VIA protocol": "VIA 协议",
            "Vial protocol": "Vial 协议",
            "Vial keyboard ID": "Vial 键盘 ID",
            "Macro entries": "宏条目",
            "Macro memory": "宏内存",
            "Macro delays": "宏延迟",
            "Complex (2-byte) macro keycodes": "复杂 (2字节) 宏键码",
            "Tap Dance entries": "多击触发条目",
            "Combo entries": "组合键条目",
            "Key Override entries": "按键覆盖条目",
            "Alt Repeat Key entries": "备选重复键条目",
            "Caps Word": "大写锁定词",
            "Layer Lock": "层锁定",
            "unsupported - sideloaded keyboard": "不支持 - 侧载的键盘",
            "unsupported - VIA keyboard": "不支持 - VIA 键盘",
            "unsupported - Vial firmware too old": "不支持 - Vial 固件版本过旧",
            "unsupported - disabled in firmware": "不支持 - 固件中已禁用",
            "disabled in firmware": "固件中已禁用",
            "yes": "是",
            "bytes": "字节",
            "Sideloaded JSON, Vial functionality is disabled": "侧载的 JSON，Vial 功能已禁用",
            "VIA keyboard, Vial functionality is disabled": "VIA 键盘，Vial 功能已禁用",
            
            # Any keycode dialog
            "Enter the QMK keycode:": "输入 QMK 键码:",
            "Any keycode": "任意键码",
            
            # Error messages
            "Unsupported protocol version!": "不支持的协议版本！",
            "Please download latest Vial from https://get.vial.today/": "请从 https://get.vial.today/ 下载最新版 Vial",
            "An example keyboard UID was detected.": "检测到示例键盘 UID。",
            "Please change your keyboard UID to be unique before you ship!": "请在发货前将键盘 UID 更改为唯一值！",
        },
    }
    
    @classmethod
    def get_system_language(cls):
        """Detect system language and return the best matching language code."""
        try:
            # Get system locale
            if sys.platform == "win32":
                import ctypes
                windll = ctypes.windll.kernel32
                lang_id = windll.GetUserDefaultUILanguage()
                # Chinese (Simplified)
                if lang_id in (0x0804, 0x1004):  # zh-CN, zh-SG
                    return "zh_CN"
            else:
                lang, _ = locale.getdefaultlocale()
                if lang:
                    if lang.startswith("zh"):
                        return "zh_CN"
        except Exception:
            pass
        return "en"
    
    @classmethod
    def set_language(cls, lang_code):
        if lang_code not in cls.LANGUAGES:
            lang_code = "en"
        cls._current_lang = lang_code
        
        # Save to settings
        settings = QSettings("Vial", "Vial")
        settings.setValue("language", lang_code)
        
        # Notify all observers
        cls._notify_observers()
    
    @classmethod
    def get_language(cls):
        """Get the current language code."""
        return cls._current_lang
    
    @classmethod
    def get_language_name(cls, lang_code=None):
        if lang_code is None:
            lang_code = cls._current_lang
        return cls.LANGUAGES.get(lang_code, "English")
    
    @classmethod
    def load_language(cls):
        settings = QSettings("Vial", "Vial")
        saved_lang = settings.value("language", None)
        
        if saved_lang and saved_lang in cls.LANGUAGES:
            cls._current_lang = saved_lang
        else:
            # Auto-detect from system
            cls._current_lang = cls.get_system_language()
    
    @classmethod
    def translate(cls, context, text):
        if cls._current_lang == "en":
            return text
        
        translations = cls._translations.get(cls._current_lang, {})
        return translations.get(text, text)
    
    @classmethod
    def register_observer(cls, observer):
        if observer not in cls._observers:
            cls._observers.append(observer)
    
    @classmethod
    def unregister_observer(cls, observer):
        if observer in cls._observers:
            cls._observers.remove(observer)
    
    @classmethod
    def _notify_observers(cls):
        for observer in cls._observers[:]:  # Copy list to avoid modification during iteration
            try:
                if hasattr(observer, 'retranslate_ui'):
                    observer.retranslate_ui()
            except RuntimeError:
                # Widget has been deleted
                cls._observers.remove(observer)


# Convenience function for translation
def tr(context, text):

    return I18n.translate(context, text)
