# bt_led_control/device.py

import asyncio
import time
import msvcrt
from .bluetooth import BLEManager
from .commands import rgb_command, red, green, blue, white, off
from .screen_capture import ScreenColorCapture


class LT22Lamp:
    """High-level interface for controlling Magic Lantern LED devices."""

    def __init__(self, device_address: str = "BE:28:72:00:39:FD"):
        self.ble = BLEManager(device_address)

    def _check_for_exit_key(self):
        """Check if user pressed End key to exit ambient mode."""
        if msvcrt.kbhit():
            key = msvcrt.getch()
            # Handle special keys (2-byte sequences)
            if ord(key) == 224:  # Special key prefix
                key2 = msvcrt.getch()
                # Check for End key (79)
                return ord(key2) == 79
            return False
        return False

    def _enhance_color_saturation(
        self, r: int, g: int, b: int, saturation_factor: float = 1.5
    ):
        """Enhance color saturation by making dominant colors more pure."""
        # Find the dominant color and color differences
        max_val = max(r, g, b)
        min_val = min(r, g, b)

        # If the color is too dark overall, don't process it
        if max_val < 40:
            return (r, g, b)

        # Calculate how "gray" or washed out the color is
        color_range = max_val - min_val

        # Detect special color combinations that should be preserved
        # Cyan: high blue + high green, low red
        if b > 200 and g > 200 and r < 100:
            return (r, g, b)  # Keep cyan as-is

        # Yellow: high red + high green, low blue
        if r > 200 and g > 200 and b < 100:
            return (r, g, b)  # Keep yellow as-is

        # Magenta: high red + high blue, low green
        if r > 200 and b > 200 and g < 100:
            return (r, g, b)  # Keep magenta as-is

        # White/Light gray: all channels high and similar
        if color_range < 30:  # Very similar values = white/gray
            boost = 1.05  # Very gentle boost for whites/grays
            return (
                min(255, int(r * boost)),
                min(255, int(g * boost)),
                min(255, int(b * boost)),
            )

        # For truly washed out single colors, enhance more
        elif color_range > 60:  # Clear dominant color
            if r >= g and r >= b:  # Red dominant
                new_r = min(255, int(r * 1.1))
                new_g = max(0, int(g * 0.6))
                new_b = max(0, int(b * 0.6))
                return (new_r, new_g, new_b)
            elif g >= r and g >= b:  # Green dominant
                new_r = max(0, int(r * 0.6))
                new_g = min(255, int(g * 1.1))
                new_b = max(0, int(b * 0.6))
                return (new_r, new_g, new_b)
            else:  # Blue dominant
                new_r = max(0, int(r * 0.6))
                new_g = max(0, int(g * 0.6))
                new_b = min(255, int(b * 1.1))
                return (new_r, new_g, new_b)

        # For moderately mixed colors, gentle enhancement
        else:
            boost = 1.05  # Very gentle enhancement
            return (
                min(255, int(r * boost)),
                min(255, int(g * boost)),
                min(255, int(b * boost)),
            )

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
    ):
        """Start ambient lighting that matches screen colors.

        Args:
            fps: Updates per second (higher = smoother, more CPU)
            edge_width: Pixels from screen edge to sample
            smoothing: Color transition smoothing (0.0=instant, 1.0=gradual)
            brightness_boost: Minimum brightness level (0-255) to keep LED visible
        """
        print(f"Starting ambient lighting at {fps} FPS (ULTRA-RESPONSIVE MODE)...")
        print(f"Brightness boost: {brightness_boost} + COLOR SATURATION BOOST")
        print("Press 'END' key to stop and return to menu")

        capture = ScreenColorCapture(edge_width=edge_width, smoothing_factor=smoothing)
        capture.set_edge_sampling(False)  # Full screen for better color detection
        delay = 1.0 / fps

        try:
            while True:
                # Check if user wants to exit
                if self._check_for_exit_key():
                    break

                r, g, b = capture.get_next_color()

                # Apply brightness boost to keep LED visible
                r = max(brightness_boost, r)
                g = max(brightness_boost, g)
                b = max(brightness_boost, b)

                # Enhance color saturation for more vibrant colors
                r, g, b = self._enhance_color_saturation(r, g, b, 1.8)

                await self.set_color(r, g, b)
                # Minimal delay for maximum speed
                await asyncio.sleep(max(0.001, delay))  # 1ms minimum delay

        except KeyboardInterrupt:
            pass  # Handle Ctrl+C gracefully too

        print("\nAmbient lighting stopped! Returning to menu...")
        await self.turn_off()
        return True

    async def start_ultra_smooth_ambient(self, brightness_boost: int = 40):
        """Ultra-smooth ambient lighting - maximum FPS, no smoothing, optimized capture."""
        print("Starting ULTRA-SMOOTH ambient lighting at MAXIMUM FPS...")
        print(f"Brightness boost: {brightness_boost} + MAXIMUM SATURATION BOOST")
        print("Press 'END' key to stop and return to menu")

        capture = ScreenColorCapture(
            smoothing_factor=0.0
        )  # No smoothing = instant response
        capture.set_edge_sampling(False)

        try:
            while True:
                # Check if user wants to exit
                if self._check_for_exit_key():
                    break

                r, g, b = capture.get_next_color()

                # Apply brightness boost to keep LED bright and visible
                r = max(brightness_boost, r)
                g = max(brightness_boost, g)
                b = max(brightness_boost, b)

                # Maximum saturation boost for ultra-vibrant colors
                r, g, b = self._enhance_color_saturation(r, g, b, 2.0)

                await self.set_color(r, g, b)
                # No sleep = maximum possible FPS limited only by BLE speed

        except KeyboardInterrupt:
            pass  # Handle Ctrl+C gracefully too

        print("\nUltra-smooth ambient lighting stopped! Returning to menu...")
        await self.turn_off()
        return True
