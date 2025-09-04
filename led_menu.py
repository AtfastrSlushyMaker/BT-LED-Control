"""
Interactive LED Control Menu
Simple command-line interface for controlling Magic Lantern LED devices.
"""

import asyncio
import sys
from bt_led_control.device import LT22Lamp
from bt_led_control.dual_lamp import DualLampManager


class LEDMenu:
    def __init__(self):
        self.lamp = LT22Lamp()
        self.dual_lamps = DualLampManager()
        self.connected = False
        self.dual_connected = False
        self.selected_monitor = None  # Track selected monitor for ambient lighting
        self.mode = "single"  # "single" or "dual"

    def show_menu(self):
        """Display the main menu options."""
        print("\n" + "=" * 60)
        print("🎨 Magic Lantern LED Control Menu")
        print("=" * 60)

        # Mode selection
        print(
            f"Current Mode: {'🔥 DUAL-LAMP AMBILIGHT' if self.mode == 'dual' else '💡 Single Lamp'}"
        )
        print("M. Switch Mode (Single ↔ Dual-Lamp)")

        if self.mode == "single":
            self._show_single_lamp_menu()
        else:
            self._show_dual_lamp_menu()

    def _show_single_lamp_menu(self):
        """Show single lamp menu options."""
        if not self.connected:
            print("❌ Not connected to LED device")
            print("1. Connect to LED")
            print("0. Exit")
        else:
            print("✅ Connected to LED device")
            print("\n🎯 Basic Colors:")
            print("1. Red")
            print("2. Green")
            print("3. Blue")
            print("4. White")
            print("5. Turn Off")

            print("\n🌈 Custom Colors:")
            print("6. Set Custom RGB")
            print("7. Purple")
            print("8. Orange")
            print("9. Yellow")
            print("10. Cyan")

            print("\n✨ Special Effects:")
            print("11. Ambient Screen Lighting")
            print("12. Ultra-Smooth Ambient Lighting")
            print("13. Select Monitor for Ambient Lighting")

            print("\n⚙️ Connection:")
            print("14. Disconnect")
            print("0. Exit")

    def _show_dual_lamp_menu(self):
        """Show dual lamp menu options."""
        if not self.dual_connected:
            print("❌ Not connected to dual-lamp setup")
            print("1. Connect to Dual-Lamp Setup")
            print("0. Exit")
        else:
            print("🔥 Connected to DUAL-LAMP setup")
            print("   Left Lamp (37:C8) + Right Lamp (39:FD)")

            print("\n🎯 Basic Colors:")
            print("1. Both Red")
            print("2. Both Green")
            print("3. Both Blue")
            print("4. Both White")
            print("5. Turn Off Both")

            print("\n🌈 Dual Colors:")
            print("6. Left Red, Right Blue")
            print("7. Left Green, Right Purple")
            print("8. Left Yellow, Right Cyan")
            print("9. Custom Dual Colors")

            print("\n🔥 PROFESSIONAL AMBILIGHT:")
            print("10. 🌈 Dual-Lamp Ambilight (60 FPS)")
            print("11. 🚀 Ultra-Smooth Dual Ambilight (120 FPS)")
            print("12. Select Monitor for Ambilight")
            print("13. Test Both Lamps")

            print("\n⚙️ Settings & Connection:")
            print("14. 🌊 Adjust Color Transition Smoothness")
            print("15. Reconnect Lamps")
            print("16. 🔧 Diagnose Lamp Issues")
            print("17. Disconnect Dual Setup")
            print("0. Exit")

        print("-" * 60)

    async def connect_led(self):
        """Connect to the LED device."""
        print("🔍 Connecting to LED device...")
        if await self.lamp.connect():
            print("✅ Connected successfully!")
            self.connected = True
        else:
            print("❌ Failed to connect. Make sure the LED is on and nearby.")

    async def connect_dual_lamps(self):
        """Connect to both lamps in dual setup."""
        print("🔍 Connecting to dual-lamp setup...")
        connections = await self.dual_lamps.connect_both()
        self.dual_connected = any(connections.values())

    async def disconnect_led(self):
        """Disconnect from the LED device."""
        print("🔌 Disconnecting...")
        await self.lamp.disconnect()
        self.connected = False
        print("✅ Disconnected")

    async def disconnect_dual_lamps(self):
        """Disconnect from dual-lamp setup."""
        print("🔌 Disconnecting dual setup...")
        await self.dual_lamps.disconnect_both()
        self.dual_connected = False

    async def diagnose_lamp_issues(self):
        """Diagnose connection and communication issues with lamps."""
        if not self.dual_lamps:
            print("❌ Dual lamp system not initialized")
            return

        print("🔧 Starting lamp diagnostics...")
        print("-" * 50)

        # Check current connection status
        print("📡 Connection Status:")
        left_connected = self.dual_lamps.connected["left"]
        right_connected = self.dual_lamps.connected["right"]
        print(
            f"   Left Lamp:  {'✅ Connected' if left_connected else '❌ Disconnected'}"
        )
        print(
            f"   Right Lamp: {'✅ Connected' if right_connected else '❌ Disconnected'}"
        )

        if not (left_connected or right_connected):
            print("⚠️ Both lamps disconnected. Try reconnecting first.")
            return

        # Test individual lamp responses
        print("\n🧪 Testing Individual Lamp Responses:")

        test_colors = [
            ("Red", 255, 0, 0),
            ("Green", 0, 255, 0),
            ("Blue", 0, 0, 255),
        ]

        for color_name, r, g, b in test_colors:
            print(f"\n   Testing {color_name}...")

            if left_connected:
                try:
                    left_result = await self.dual_lamps.set_left_color(r, g, b)
                    print(
                        f"   Left Lamp {color_name}: {'✅ Success' if left_result else '❌ Failed'}"
                    )
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"   Left Lamp {color_name}: ❌ Exception: {e}")

            if right_connected:
                try:
                    right_result = await self.dual_lamps.set_right_color(r, g, b)
                    print(
                        f"   Right Lamp {color_name}: {'✅ Success' if right_result else '❌ Failed'}"
                    )
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"   Right Lamp {color_name}: ❌ Exception: {e}")

        # Check BLE connection health
        print("\n🔍 BLE Connection Health:")
        try:
            if left_connected and hasattr(
                self.dual_lamps.left_lamp.ble, "is_connected"
            ):
                ble_left = self.dual_lamps.left_lamp.ble.is_connected()
                print(
                    f"   Left BLE Status: {'✅ Active' if ble_left else '❌ Inactive'}"
                )
                if not ble_left:
                    print("   ⚠️ Left lamp marked connected but BLE shows inactive!")

        except Exception as e:
            print(f"   Left BLE Check: ❌ Error: {e}")

        try:
            if right_connected and hasattr(
                self.dual_lamps.right_lamp.ble, "is_connected"
            ):
                ble_right = self.dual_lamps.right_lamp.ble.is_connected()
                print(
                    f"   Right BLE Status: {'✅ Active' if ble_right else '❌ Inactive'}"
                )
                if not ble_right:
                    print("   ⚠️ Right lamp marked connected but BLE shows inactive!")

        except Exception as e:
            print(f"   Right BLE Check: ❌ Error: {e}")

        # Recommendations
        print("\n💡 Recommendations:")
        if not left_connected and not right_connected:
            print("   • Use option 14 to reconnect both lamps")
        elif not left_connected or not right_connected:
            print("   • Use option 14 to reconnect the disconnected lamp")
            print("   • Check power to the problematic lamp")
            print("   • If using USB hub, try connecting directly to TV USB port")
        else:
            print("   • Both lamps appear connected")
            print(
                "   • If one lamp gets stuck, it may be a power or interference issue"
            )
            print("   • Try using the 30 FPS power-saving mode")

        print("-" * 50)

    def adjust_transition_smoothness(self):
        """Allow user to adjust color transition smoothness."""
        print("🌊 Color Transition Smoothness Settings")
        print("-" * 40)
        print(
            "Current setting: {:.2f}".format(
                self.dual_lamps.color_transitioner.transition_speed
            )
        )
        print("\nPresets:")
        print("1. 🐢 Very Smooth (0.10) - Slow, buttery transitions")
        print("2. 🌊 Smooth (0.15) - Gentle, natural transitions")
        print("3. ⚡ Balanced (0.25) - Good speed with smoothness")
        print("4. 🚀 Fast (0.40) - Quick response")
        print("5. ⚡ Instant (1.00) - No smoothing")
        print("6. 🎛️ Custom Value")

        try:
            choice = input("\nChoose setting (1-6): ").strip()

            speed_map = {"1": 0.10, "2": 0.15, "3": 0.25, "4": 0.40, "5": 1.00}

            if choice in speed_map:
                speed = speed_map[choice]
                self.dual_lamps.set_transition_speed(speed)
                print(f"✅ Transition speed set to {speed:.2f}")
            elif choice == "6":
                try:
                    speed = float(input("Enter custom speed (0.01-1.00): "))
                    if 0.01 <= speed <= 1.0:
                        self.dual_lamps.set_transition_speed(speed)
                        print(f"✅ Custom transition speed set to {speed:.2f}")
                    else:
                        print("❌ Speed must be between 0.01 and 1.00")
                except ValueError:
                    print("❌ Invalid number format")
            else:
                print("❌ Invalid choice")

        except Exception as e:
            print(f"❌ Error adjusting smoothness: {e}")

    def get_custom_rgb(self):
        """Get RGB values from user input."""
        try:
            print("\nEnter RGB values (0-255):")
            red = int(input("Red: "))
            green = int(input("Green: "))
            blue = int(input("Blue: "))

            if not all(0 <= val <= 255 for val in [red, green, blue]):
                print("❌ RGB values must be between 0 and 255")
                return None

            return red, green, blue
        except ValueError:
            print("❌ Invalid input. Please enter numbers only.")
            return None

    def get_dual_custom_colors(self):
        """Get RGB values for both lamps."""
        print("\n🔵 Left Lamp Color:")
        left_color = self.get_custom_rgb()
        if not left_color:
            return None, None

        print("\n🔴 Right Lamp Color:")
        right_color = self.get_custom_rgb()
        if not right_color:
            return None, None

        return left_color, right_color

    async def handle_choice(self, choice):
        """Handle user menu choice."""
        # Handle mode switching
        if choice.upper() == "M":
            self.mode = "dual" if self.mode == "single" else "single"
            print(
                f"🔄 Switched to {'DUAL-LAMP' if self.mode == 'dual' else 'SINGLE-LAMP'} mode!"
            )
            return True

        if self.mode == "single":
            return await self._handle_single_choice(choice)
        else:
            return await self._handle_dual_choice(choice)

    async def _handle_single_choice(self, choice):
        """Handle single lamp menu choices."""
        if not self.connected and choice != "1" and choice != "0":
            print("❌ Please connect to LED first!")
            return True

        try:
            if choice == "0":
                if self.connected:
                    await self.disconnect_led()
                print("👋 Goodbye!")
                return False

            elif choice == "1":
                if not self.connected:
                    await self.connect_led()
                else:
                    print("🔴 Setting LED to Red...")
                    await self.lamp.turn_red()
                    print("✅ Done!")

            # Continue with existing single lamp choices...
            elif choice == "2":
                print("🟢 Setting LED to Green...")
                await self.lamp.turn_green()
                print("✅ Done!")

            elif choice == "3":
                print("🔵 Setting LED to Blue...")
                await self.lamp.turn_blue()
                print("✅ Done!")

            elif choice == "4":
                print("⚪ Setting LED to White...")
                await self.lamp.turn_white()
                print("✅ Done!")

            elif choice == "5":
                print("⚫ Turning LED Off...")
                await self.lamp.turn_off()
                print("✅ Done!")

            elif choice == "6":
                rgb = self.get_custom_rgb()
                if rgb:
                    red, green, blue = rgb
                    print(f"🎨 Setting LED to RGB({red}, {green}, {blue})...")
                    await self.lamp.set_color(red, green, blue)
                    print("✅ Done!")

            elif choice == "7":
                print("🟣 Setting LED to Purple...")
                await self.lamp.set_color(128, 0, 128)
                print("✅ Done!")

            elif choice == "8":
                print("🟠 Setting LED to Orange...")
                await self.lamp.set_color(255, 165, 0)
                print("✅ Done!")

            elif choice == "9":
                print("🟡 Setting LED to Yellow...")
                await self.lamp.set_color(255, 255, 0)
                print("✅ Done!")

            elif choice == "10":
                print("🩵 Setting LED to Cyan...")
                await self.lamp.set_color(0, 255, 255)
                print("✅ Done!")

            elif choice == "11":
                print("✨ Starting Ambient Screen Lighting...")
                print("This will make your LED match your screen colors!")
                print("Tip: Play a colorful video or game to see the effect")
                print("📋 Press 'END' key to exit ambient mode")

                # Use selected monitor if available
                if (
                    hasattr(self, "selected_monitor")
                    and self.selected_monitor is not None
                ):
                    print(f"🖥️  Using selected monitor {self.selected_monitor}")
                    await self.lamp.start_ambient_lighting(
                        monitor_id=self.selected_monitor
                    )
                else:
                    await self.lamp.start_ambient_lighting()

            elif choice == "12":
                print("🚀 Starting ULTRA-SMOOTH Ambient Lighting...")
                print("Maximum FPS for the smoothest experience!")
                print("Warning: This will use more CPU and BLE bandwidth")
                print("📋 Press 'END' key to exit ambient mode")

                # Use selected monitor if available
                if (
                    hasattr(self, "selected_monitor")
                    and self.selected_monitor is not None
                ):
                    print(f"🖥️  Using selected monitor {self.selected_monitor}")
                    await self.lamp.start_ultra_smooth_ambient(
                        monitor_id=self.selected_monitor
                    )
                else:
                    await self.lamp.start_ultra_smooth_ambient()

            elif choice == "13":
                print("🖥️  Monitor Selection for Ambient Lighting")
                from bt_led_control.ui_utils import choose_monitor_interactive

                monitor_id = choose_monitor_interactive()
                if monitor_id is not None:
                    print(
                        f"✅ Monitor {monitor_id} will be used for future ambient lighting"
                    )
                    # Store the selected monitor for future use
                    self.selected_monitor = monitor_id
                else:
                    print("❌ Monitor selection cancelled")

            elif choice == "14":
                await self.disconnect_led()

            else:
                print("❌ Invalid choice. Please try again.")

        except Exception as e:
            print(f"❌ Error: {e}")

        return True

    async def _handle_dual_choice(self, choice):
        """Handle dual lamp menu choices."""
        if not self.dual_connected and choice != "1" and choice != "0":
            print("❌ Please connect to dual-lamp setup first!")
            return True

        try:
            if choice == "0":
                if self.dual_connected:
                    await self.disconnect_dual_lamps()
                print("👋 Goodbye!")
                return False

            elif choice == "1":
                if not self.dual_connected:
                    await self.connect_dual_lamps()
                else:
                    print("🔴 Setting both lamps to Red...")
                    await self.dual_lamps.set_both_color(255, 0, 0)
                    print("✅ Done!")

            elif choice == "2":
                print("🟢 Setting both lamps to Green...")
                await self.dual_lamps.set_both_color(0, 255, 0)
                print("✅ Done!")

            elif choice == "3":
                print("🔵 Setting both lamps to Blue...")
                await self.dual_lamps.set_both_color(0, 0, 255)
                print("✅ Done!")

            elif choice == "4":
                print("⚪ Setting both lamps to White...")
                await self.dual_lamps.set_both_color(255, 255, 255)
                print("✅ Done!")

            elif choice == "5":
                print("🔌 Turning off both lamps...")
                await self.dual_lamps.turn_off_both()
                print("✅ Done!")

            elif choice == "6":
                print("🔴🔵 Left Red, Right Blue...")
                await self.dual_lamps.set_left_color(255, 0, 0)
                await self.dual_lamps.set_right_color(0, 0, 255)
                print("✅ Done!")

            elif choice == "7":
                print("🟢🟣 Left Green, Right Purple...")
                await self.dual_lamps.set_left_color(0, 255, 0)
                await self.dual_lamps.set_right_color(128, 0, 128)
                print("✅ Done!")

            elif choice == "8":
                print("🟡🔷 Left Yellow, Right Cyan...")
                await self.dual_lamps.set_left_color(255, 255, 0)
                await self.dual_lamps.set_right_color(0, 255, 255)
                print("✅ Done!")

            elif choice == "9":
                left_color, right_color = self.get_dual_custom_colors()
                if left_color and right_color:
                    print(f"🎨 Setting Left: RGB{left_color}, Right: RGB{right_color}")
                    await self.dual_lamps.set_left_color(*left_color)
                    await self.dual_lamps.set_right_color(*right_color)
                    print("✅ Done!")

            elif choice == "10":
                print("🌈 Starting Professional Dual-Lamp Ambilight (60 FPS)!")
                monitor_id = (
                    self.selected_monitor if self.selected_monitor is not None else 0
                )
                await self.dual_lamps.start_dual_ambilight(
                    fps=60,
                    brightness_boost=25,
                    saturation_factor=2.2,
                    monitor_id=monitor_id,
                )

            elif choice == "11":
                print("🚀 Starting ULTRA-SMOOTH Dual-Lamp Ambilight (120 FPS)!")
                monitor_id = (
                    self.selected_monitor if self.selected_monitor is not None else 0
                )
                await self.dual_lamps.start_dual_ambilight(
                    fps=120,
                    brightness_boost=30,
                    saturation_factor=2.5,
                    monitor_id=monitor_id,
                )

            elif choice == "12":
                print("🖥️  Monitor Selection for Dual Ambilight")
                from bt_led_control.ui_utils import choose_monitor_interactive

                monitor_id = choose_monitor_interactive()
                if monitor_id is not None:
                    print(f"✅ Monitor {monitor_id} will be used for dual ambilight")
                    self.selected_monitor = monitor_id
                else:
                    print("❌ Monitor selection cancelled")

            elif choice == "13":
                print("🧪 Testing both lamps...")
                await self.dual_lamps.test_lamps()

            elif choice == "14":
                print("🌊 Adjusting color transition smoothness...")
                self.adjust_transition_smoothness()

            elif choice == "15":
                print("🔄 Reconnecting both lamps...")
                if self.dual_lamps:
                    success = await self.dual_lamps.reconnect_both()
                    if success:
                        print("✅ Both lamps reconnected successfully!")
                    else:
                        print("❌ Failed to reconnect one or both lamps")
                else:
                    print("❌ Dual lamp system not initialized")

            elif choice == "16":
                print("🔧 Diagnosing lamp connection issues...")
                await self.diagnose_lamp_issues()

            elif choice == "17":
                await self.disconnect_dual_lamps()

            else:
                print("❌ Invalid choice. Please try again.")

        except Exception as e:
            print(f"❌ Error: {e}")

        return True

    async def run(self):
        """Run the interactive menu."""
        print("🚀 Starting LED Control Menu...")

        try:
            while True:
                self.show_menu()
                choice = input("\nEnter your choice: ").strip()

                if not await self.handle_choice(choice):
                    break

                # Small delay to see the result
                await asyncio.sleep(0.5)

        except KeyboardInterrupt:
            print("\n\n⚡ Interrupted by user")
            if self.connected:
                await self.disconnect_led()

        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            if self.connected:
                await self.disconnect_led()


async def main():
    """Main function to run the LED menu."""
    menu = LEDMenu()
    await menu.run()


if __name__ == "__main__":
    asyncio.run(main())
