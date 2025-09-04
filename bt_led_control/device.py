# bt_led_control/device.py

import asyncio
import time
from .bluetooth import BLEManager
from .commands import rgb_command, red, green, blue, white, off
from .screen_capture import ScreenColorCapture
from .color_utils import enhance_color_saturation
from .utils import check_for_exit_key


class LT22Lamp:
    """High-level interface for controlling Magic Lantern LED devices."""

    def __init__(self, device_address: str = "BE:28:72:00:39:FD"):
        self.ble = BLEManager(device_address)

    async def connect(self) -> bool:
        """Connect to the LED device."""
        return await self.ble.connect()

    async def disconnect(self) -> bool:
        """Disconnect from the LED device."""
        return await self.ble.disconnect()

    async def set_color(self, red: int, green: int, blue: int) -> bool:
        """Set the LED to a specific RGB color."""
        command = rgb_command(red, green, blue)
        return await self.ble.send_command(command)

    async def turn_red(self) -> bool:
        command = red()
        return await self.ble.send_command(command)

    async def turn_green(self) -> bool:
        command = green()
        return await self.ble.send_command(command)

    async def turn_blue(self) -> bool:
        command = blue()
        return await self.ble.send_command(command)

    async def turn_white(self) -> bool:
        command = white()
        return await self.ble.send_command(command)

    async def turn_off(self) -> bool:
        command = off()
        return await self.ble.send_command(command)

    async def start_ambient_lighting(
        self,
        fps: int = 120,
        edge_width: int = 100,
        smoothing: float = 0.0,
        brightness_boost: int = 30,
        monitor_id: int = None,
    ):
        """Start ambient lighting that matches screen colors."""
        print(f"Starting ambient lighting at {fps} FPS (ULTRA-RESPONSIVE MODE)...")
        print(f"Brightness boost: {brightness_boost} + COLOR SATURATION BOOST")
        print("Press 'END' key to stop and return to menu")

        capture = ScreenColorCapture(
            edge_width=edge_width, smoothing_factor=smoothing, monitor_id=monitor_id
        )
        capture.set_edge_sampling(False)  # Full screen for better color detection
        delay = 1.0 / fps

        try:
            while True:
                # Check if user wants to exit
                if check_for_exit_key():
                    break

                r, g, b = capture.get_next_color()

                # Apply brightness boost to keep LED visible
                r = max(brightness_boost, r)
                g = max(brightness_boost, g)
                b = max(brightness_boost, b)

                # Enhance color saturation for more vibrant colors
                r, g, b = enhance_color_saturation(r, g, b, 1.8)

                await self.set_color(r, g, b)
                # Minimal delay for maximum speed
                await asyncio.sleep(max(0.001, delay))  # 1ms minimum delay

        except KeyboardInterrupt:
            pass  # Handle Ctrl+C gracefully too

        print("\nAmbient lighting stopped! Returning to menu...")
        await self.turn_off()
        return True

    async def start_ultra_smooth_ambient(
        self, brightness_boost: int = 40, monitor_id: int = None
    ):
        """Ultra-smooth ambient lighting - maximum FPS, no smoothing, optimized capture."""
        print("Starting ULTRA-SMOOTH ambient lighting at MAXIMUM FPS...")
        print(f"Brightness boost: {brightness_boost} + MAXIMUM SATURATION BOOST")
        print("Press 'END' key to stop and return to menu")

        capture = ScreenColorCapture(
            smoothing_factor=0.0, monitor_id=monitor_id
        )  # No smoothing = instant response
        capture.set_edge_sampling(False)

        try:
            while True:
                # Check if user wants to exit
                if check_for_exit_key():
                    break

                r, g, b = capture.get_next_color()

                # Apply brightness boost to keep LED bright and visible
                r = max(brightness_boost, r)
                g = max(brightness_boost, g)
                b = max(brightness_boost, b)

                # Maximum saturation boost for ultra-vibrant colors
                r, g, b = enhance_color_saturation(r, g, b, 2.0)

                await self.set_color(r, g, b)
                # No sleep = maximum possible FPS limited only by BLE speed

        except KeyboardInterrupt:
            pass  # Handle Ctrl+C gracefully too

        print("\nUltra-smooth ambient lighting stopped! Returning to menu...")
        await self.turn_off()
        return True
