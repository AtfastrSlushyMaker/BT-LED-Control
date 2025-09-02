"""
BT-LED-Control: Python library for controlling Magic Lantern LED devices via BLE.

This package provides easy-to-use interfaces for controlling LED lights over
Bluetooth Low Energy, including color control and device management.
"""

__version__ = "1.0.0"
__author__ = "Malek Bsaissa"
__description__ = "Control Magic Lantern LED lights via Bluetooth Low Energy"

# Import main classes for easy access
from .device import LT22Lamp
from .bluetooth import BLEManager
from .commands import rgb_command, red, green, blue, white, off

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
]
