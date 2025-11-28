# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import Qt

import platform


class HiDPIInit:
    """Helper class for managing HiDPI scaling and font sizes."""

    _instance = None
    _dpi_scale = 1.0
    _base_font_size = 10

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HiDPIInit, cls).__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls):
        """Initialize HiDPI settings based on primary screen."""
        helper = cls()
        screen = QApplication.primaryScreen()
        
        if screen:
            # Get logical DPI and physical DPI
            logical_dpi = screen.logicalDotsPerInch()
            physical_dpi = screen.physicalDotsPerInch()
            device_pixel_ratio = screen.devicePixelRatio()
            
            # Standard DPI is 96 on Windows/Linux, 72 on macOS
            system = platform.system()
            if system == "Darwin":
                standard_dpi = 72
            else:
                standard_dpi = 96
            
            # Calculate scale based on logical DPI
            helper._dpi_scale = max(1.0, logical_dpi / standard_dpi)
            
            # Ensure minimum scale of 1.0 and cap at 3.0
            helper._dpi_scale = min(3.0, max(1.0, helper._dpi_scale))
            
            return {
                'logical_dpi': logical_dpi,
                'physical_dpi': physical_dpi,
                'device_pixel_ratio': device_pixel_ratio,
                'dpi_scale': helper._dpi_scale,
                'system': system
            }
        
        return None

    @classmethod
    def get_scale(cls):
        """Get the current DPI scale factor."""
        return cls()._dpi_scale

    @classmethod
    def scale(cls, value):
        """Scale a value based on DPI."""
        return int(value * cls()._dpi_scale)

    @classmethod
    def scale_float(cls, value):
        """Scale a float value based on DPI."""
        return value * cls()._dpi_scale

    @classmethod
    def get_font_size(cls, size=None):
        """Get a DPI-scaled font size."""
        if size is None:
            size = cls()._base_font_size
        return cls.scale_float(size)

    @classmethod
    def get_window_size(cls, width=None, height=None):
        """Calculate scaled window size based on DPI and screen geometry."""
        from constants import (
            WINDOW_WIDTH, WINDOW_HEIGHT,
            MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT,
            PREFERRED_WINDOW_WIDTH, PREFERRED_WINDOW_HEIGHT
        )
        
        if width is None:
            width = WINDOW_WIDTH
        if height is None:
            height = WINDOW_HEIGHT
        
        scale = cls.get_scale()
        
        # Apply scale
        scaled_width = int(width * scale)
        scaled_height = int(height * scale)
        
        # Ensure minimum size
        scaled_width = max(scaled_width, cls.scale(MIN_WINDOW_WIDTH))
        scaled_height = max(scaled_height, cls.scale(MIN_WINDOW_HEIGHT))
        
        # Get available screen geometry
        screen = QApplication.primaryScreen()
        if screen:
            available_geom = screen.availableGeometry()
            screen_width = available_geom.width()
            screen_height = available_geom.height()
            
            # Leave some margin from screen edges (5% on each side)
            max_width = int(screen_width * 0.95)
            max_height = int(screen_height * 0.95)
            
            scaled_width = min(scaled_width, max_width)
            scaled_height = min(scaled_height, max_height)
        
        return scaled_width, scaled_height

    @classmethod
    def get_layout_spacing(cls):
        """Get DPI-scaled layout spacing."""
        return cls.scale(4)

    @classmethod
    def get_button_size(cls):
        """Get DPI-scaled button size."""
        return cls.scale(24)

    @classmethod
    def get_icon_size(cls):
        """Get DPI-scaled icon size."""
        return cls.scale(16)


def setup_hidpi():
    """Setup HiDPI support. PyQt6 handles HiDPI automatically."""
    # PyQt6 automatically enables HiDPI scaling
    pass