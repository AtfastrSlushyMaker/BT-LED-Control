# bt_led_control/dual_lamp.py

import asyncio
from typing import Tuple, Optional, Dict, Any
from .device import LT22Lamp
from .screen_capture import get_screen_edge_color
from .color_utils import enhance_color_saturation, get_edge_colors_from_image
from .utils import check_for_exit_key
from .monitor import get_available_monitors, get_monitor_with_scaling_info
from PIL import ImageGrab
import numpy as np


class DualLampManager:
    """Manager for controlling two Magic Lantern lamps for professional Ambilight effect."""

    # Device addresses for the dual-lamp setup
    LEFT_LAMP_ADDRESS = "BE:28:72:00:37:C8"  # New lamp (left side)
    RIGHT_LAMP_ADDRESS = "BE:28:72:00:39:FD"  # Original lamp (right side)

    def __init__(self):
        self.left_lamp = LT22Lamp(self.LEFT_LAMP_ADDRESS)
        self.right_lamp = LT22Lamp(self.RIGHT_LAMP_ADDRESS)
        self.connected = {"left": False, "right": False}

    async def connect_both(self) -> Dict[str, bool]:
        """Connect to both lamps with retry logic."""
        print("🔗 Connecting to dual-lamp setup...")

        # Connect to left lamp with retry
        print("   Left lamp (BE:28:72:00:37:C8)...", end=" ")
        for attempt in range(3):
            self.connected["left"] = await self.left_lamp.connect()
            if self.connected["left"]:
                break
            if attempt < 2:
                await asyncio.sleep(1)
        print("✅ Connected!" if self.connected["left"] else "❌ Failed!")

        # Connect to right lamp with retry
        print("   Right lamp (BE:28:72:00:39:FD)...", end=" ")
        for attempt in range(3):
            self.connected["right"] = await self.right_lamp.connect()
            if self.connected["right"]:
                break
            if attempt < 2:
                await asyncio.sleep(1)
        print("✅ Connected!" if self.connected["right"] else "❌ Failed!")

        if self.connected["left"] and self.connected["right"]:
            print("🎉 Both lamps connected successfully!")
        elif self.connected["left"] or self.connected["right"]:
            print("⚠️  Only one lamp connected. Dual-lamp mode will be limited.")
        else:
            print("❌ No lamps connected!")

        return self.connected

    async def disconnect_both(self) -> Dict[str, bool]:
        """Disconnect from both lamps."""
        print("📴 Disconnecting from dual-lamp setup...")

        results = {}
        if self.connected["left"]:
            results["left"] = await self.left_lamp.disconnect()
            self.connected["left"] = False
        else:
            results["left"] = True

        if self.connected["right"]:
            results["right"] = await self.right_lamp.disconnect()
            self.connected["right"] = False
        else:
            results["right"] = True

        print("👋 Dual-lamp setup disconnected!")
        return results

    async def set_both_color(self, red: int, green: int, blue: int) -> Dict[str, bool]:
        """Set both lamps to the same color."""
        results = {}

        if self.connected["left"]:
            results["left"] = await self.left_lamp.set_color(red, green, blue)

        if self.connected["right"]:
            results["right"] = await self.right_lamp.set_color(red, green, blue)

        return results

    async def _check_connections(self):
        """Check and update connection status."""
        if self.connected["left"]:
            self.connected["left"] = self.left_lamp.ble.is_connected()
        if self.connected["right"]:
            self.connected["right"] = self.right_lamp.ble.is_connected()

    async def set_left_color(self, red: int, green: int, blue: int) -> bool:
        """Set only the left lamp color."""
        if self.connected["left"]:
            try:
                result = await self.left_lamp.set_color(red, green, blue)
                return result
            except Exception as e:
                print(f"Left lamp error: {e}")
                return False
        return False

    async def set_right_color(self, red: int, green: int, blue: int) -> bool:
        """Set only the right lamp color."""
        if self.connected["right"]:
            try:
                result = await self.right_lamp.set_color(red, green, blue)
                return result
            except Exception as e:
                print(f"Right lamp error: {e}")
                return False
        return False

    async def turn_off_both(self) -> Dict[str, bool]:
        """Turn off both lamps."""
        results = {}

        if self.connected["left"]:
            results["left"] = await self.left_lamp.turn_off()

        if self.connected["right"]:
            results["right"] = await self.right_lamp.turn_off()

        return results

    def _capture_screen_with_zones(self, monitor_id: Optional[int] = None):
        """Capture screen and extract left/right zone colors with 4K support."""
        try:
            # Use 4K-aware capture like the single lamp version
            if monitor_id is not None:
                monitor_info = get_monitor_with_scaling_info(monitor_id)

                # Check if it's a 4K monitor that needs special handling
                if (monitor_info.get("is_4k") and monitor_info.get("is_scaled")) or (
                    monitor_info.get("actual_resolution", (0, 0))[0] >= 3840
                ):
                    try:
                        from .screen_capture import _capture_4k_scaled_monitor

                        screenshot = _capture_4k_scaled_monitor(monitor_info)
                    except Exception as e:
                        print(f"Warning: 4K capture failed, using standard method: {e}")
                        monitors = get_available_monitors()
                        if monitor_id < len(monitors):
                            monitor = monitors[monitor_id]
                            bbox = monitor.get("bbox")
                            if bbox and (bbox[0] < 0 or bbox[1] < 0):
                                # Use Win32 for negative coordinates
                                from .screen_capture import _capture_monitor_win32

                                screenshot = _capture_monitor_win32(bbox)
                            else:
                                screenshot = (
                                    ImageGrab.grab(bbox=bbox)
                                    if bbox
                                    else ImageGrab.grab()
                                )
                        else:
                            screenshot = ImageGrab.grab()
                else:
                    # Standard monitor capture
                    monitors = get_available_monitors()
                    if monitor_id < len(monitors):
                        monitor = monitors[monitor_id]
                        bbox = monitor.get("bbox")
                        if bbox and (bbox[0] < 0 or bbox[1] < 0):
                            # Use Win32 for negative coordinates
                            from .screen_capture import _capture_monitor_win32

                            screenshot = _capture_monitor_win32(bbox)
                        else:
                            screenshot = (
                                ImageGrab.grab(bbox=bbox) if bbox else ImageGrab.grab()
                            )
                    else:
                        screenshot = ImageGrab.grab()
            else:
                screenshot = ImageGrab.grab()

            if screenshot is None:
                screenshot = ImageGrab.grab()  # Final fallback

            width, height = screenshot.size

            # Define zones for professional Ambilight
            edge_width = 80  # Wider sampling for better color representation

            # LEFT ZONE: Left edge + left half of top/bottom
            left_samples = []

            # Left edge (full height)
            left_edge = screenshot.crop((0, 0, edge_width, height))
            left_samples.append(np.array(left_edge))

            # Left half of top edge
            top_left = screenshot.crop((0, 0, width // 2, edge_width))
            left_samples.append(np.array(top_left))

            # Left half of bottom edge
            bottom_left = screenshot.crop((0, height - edge_width, width // 2, height))
            left_samples.append(np.array(bottom_left))

            # RIGHT ZONE: Right edge + right half of top/bottom
            right_samples = []

            # Right edge (full height)
            right_edge = screenshot.crop((width - edge_width, 0, width, height))
            right_samples.append(np.array(right_edge))

            # Right half of top edge
            top_right = screenshot.crop((width // 2, 0, width, edge_width))
            right_samples.append(np.array(top_right))

            # Right half of bottom edge
            bottom_right = screenshot.crop(
                (width // 2, height - edge_width, width, height)
            )
            right_samples.append(np.array(bottom_right))

            # Calculate average colors for each zone
            left_pixels = np.concatenate(
                [sample.reshape(-1, 3) for sample in left_samples]
            )
            right_pixels = np.concatenate(
                [sample.reshape(-1, 3) for sample in right_samples]
            )

            left_color = tuple(map(int, np.mean(left_pixels, axis=0)))
            right_color = tuple(map(int, np.mean(right_pixels, axis=0)))

            return left_color, right_color

        except Exception as e:
            print(f"Warning: Screen zone capture error: {e}")
            return (50, 50, 50), (50, 50, 50)  # Fallback colors

    async def start_dual_ambilight(
        self,
        fps: int = 60,
        brightness_boost: int = 40,
        saturation_factor: float = 2.0,
        monitor_id: Optional[int] = None,
    ):
        """Start professional dual-lamp Ambilight system."""
        if not any(self.connected.values()):
            print("❌ No lamps connected! Please connect first.")
            return False

        connected_lamps = [name for name, status in self.connected.items() if status]
        print(f"🌈 Starting Dual-Lamp Professional Ambilight!")
        print(f"   Connected lamps: {', '.join(connected_lamps)}")
        print(
            f"   FPS: {fps} | Brightness: +{brightness_boost} | Saturation: {saturation_factor}x"
        )
        print("   Left lamp = Left screen zone | Right lamp = Right screen zone")
        print("   Press 'END' key to stop")

        delay = 1.0 / fps

        try:
            while True:
                # Check for exit
                if check_for_exit_key():
                    break

                # Capture and process screen zones
                left_color, right_color = self._capture_screen_with_zones(monitor_id)

                # Apply brightness boost (more gentle approach)
                left_color = tuple(min(255, c + brightness_boost) for c in left_color)
                right_color = tuple(min(255, c + brightness_boost) for c in right_color)

                # Apply saturation enhancement
                left_color = enhance_color_saturation(*left_color, saturation_factor)
                right_color = enhance_color_saturation(*right_color, saturation_factor)

                # Send colors to respective lamps
                tasks = []
                if self.connected["left"]:
                    tasks.append(self.set_left_color(*left_color))
                if self.connected["right"]:
                    tasks.append(self.set_right_color(*right_color))

                # Execute both lamp updates simultaneously
                if tasks:
                    await asyncio.gather(*tasks)

                # Frame rate control
                await asyncio.sleep(max(0.001, delay))

        except KeyboardInterrupt:
            pass

        print("\n🎉 Dual-lamp Ambilight stopped!")
        await self.turn_off_both()
        return True

    async def test_lamps(self):
        """Test both lamps with different colors (gentle on connections)."""
        print("🧪 Testing dual-lamp setup...")

        if not any(self.connected.values()):
            print("❌ No lamps connected! Please connect first.")
            return

        # Check connection status first
        await self._check_connections()

        colors = [
            ("Red", 255, 0, 0),
            ("Green", 0, 255, 0),
            ("Blue", 0, 0, 255),
            ("Yellow", 255, 255, 0),
            ("Purple", 255, 0, 255),
            ("Cyan", 0, 255, 255),
            ("White", 255, 255, 255),
        ]

        for color_name, r, g, b in colors:
            print(f"   Testing {color_name} on both lamps...")
            await self.set_both_color(r, g, b)
            await asyncio.sleep(1.5)  # Longer delay to be gentler on BLE

        print("   Testing different colors on each lamp...")
        if self.connected["left"] and self.connected["right"]:
            await self.set_left_color(255, 0, 0)  # Left = Red
            await asyncio.sleep(0.5)  # Small delay between commands
            await self.set_right_color(0, 0, 255)  # Right = Blue
            await asyncio.sleep(2)

        print("   Turning off lamps...")
        await self.turn_off_both()
        print("✅ Lamp test complete!")

        # Final connection check
        await self._check_connections()
        if not all(self.connected.values()):
            print(
                "⚠️  Note: Some connections may need refreshing after intensive testing."
            )
