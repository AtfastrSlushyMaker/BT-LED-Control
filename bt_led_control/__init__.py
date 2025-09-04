"""
BT-LED-Control: Python library for controlling Magic Lantern LED devices via BLE.

This package provides easy-to-use interfaces for controlling LED lights over
Bluetooth Low Energy, including color control and device management.
"""

__version__ = "1.0.0"
__author__ = "Malek Bsaissa"
__description__ = "Control Magic Lantern LED lights via Bluetooth Low Energy"

# Import main classes for easy access (only import what doesn't require extra dependencies)
from .commands import rgb_command, red, green, blue, white, off
from .monitor import get_available_monitors, get_monitor_with_scaling_info
from .color_utils import enhance_color_saturation, smooth_color_transition
from .ui_utils import display_available_monitors, choose_monitor_interactive
from .utils import check_for_exit_key

# Import screen capture (might need PIL)
try:
    from .screen_capture import (
        ScreenColorCapture,
        get_screen_average_color,
        get_screen_edge_color,
    )
except ImportError:
    # PIL not available
    pass

# Import device classes only if bluetooth dependencies are available
try:
    from .device import LT22Lamp
    from .bluetooth import BLEManager
except ImportError:
    # BLE dependencies not available
    pass

# Define what gets imported with "from bt_led_control import *"
__all__ = [
    "LT22Lamp",
    "BLEManager",
    "rgb_command",
    "red",
    "green",
    "blue",
    "white",
    "off",
    "ScreenColorCapture",
    "get_screen_average_color",
    "get_screen_edge_color",
    "get_available_monitors",
    "get_monitor_with_scaling_info",
    "enhance_color_saturation",
    "smooth_color_transition",
    "display_available_monitors",
    "choose_monitor_interactive",
    "check_for_exit_key",
]
