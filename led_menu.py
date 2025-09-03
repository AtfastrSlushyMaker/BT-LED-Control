"""
Interactive LED Control Menu
Simple command-line interface for controlling Magic Lantern LED devices.
"""

import asyncio
import sys
from bt_led_control.device import LT22Lamp


class LEDMenu:
    def __init__(self):
        self.lamp = LT22Lamp()
        self.connected = False
        self.selected_monitor = None  # Track selected monitor for ambient lighting

    def show_menu(self):
        """Display the main menu options."""
        print("\n" + "=" * 50)
        print("🎨 Magic Lantern LED Control Menu")
        print("=" * 50)

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

        print("-" * 50)

    async def connect_led(self):
        """Connect to the LED device."""
        print("🔍 Connecting to LED device...")
        if await self.lamp.connect():
            print("✅ Connected successfully!")
            self.connected = True
        else:
            print("❌ Failed to connect. Make sure the LED is on and nearby.")

    async def disconnect_led(self):
        """Disconnect from the LED device."""
        print("🔌 Disconnecting...")
        await self.lamp.disconnect()
        self.connected = False
        print("✅ Disconnected")

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

    async def handle_choice(self, choice):
        """Handle user menu choice."""
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
                monitor_id = self.lamp.choose_monitor_interactive()
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
