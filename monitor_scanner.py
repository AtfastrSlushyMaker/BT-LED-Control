#!/usr/bin/env python3
"""
Monitor detection and selection utility for screen capture.
Scans available monitors and allows user to choose which one to capture.
"""

import tkinter as tk
from PIL import ImageGrab
import sys


def get_all_monitors():
    """Get information about all available monitors."""
    try:
        # Try to get monitor information using tkinter
        root = tk.Tk()
        root.withdraw()  # Hide the window

        monitors = []

        # Get primary monitor
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        monitors.append(
            {
                "id": 0,
                "name": "Primary Monitor",
                "width": width,
                "height": height,
                "bbox": (0, 0, width, height),
                "primary": True,
            }
        )

        root.destroy()

        # Try to get additional monitor info using Windows-specific methods
        try:
            import win32api
            import win32con
            from win32api import EnumDisplayMonitors, GetMonitorInfo

            # Clear the basic monitor and get detailed info
            monitors.clear()

            monitor_handles = EnumDisplayMonitors()

            for i, (hmon, hdc, rect) in enumerate(monitor_handles):
                try:
                    monitor_info = GetMonitorInfo(hmon)
                    device_name = monitor_info.get("Device", f"Monitor {i+1}")
                    monitor_rect = monitor_info["Monitor"]  # (left, top, right, bottom)
                    work_area = monitor_info.get("Work", monitor_rect)

                    is_primary = monitor_info["Flags"] & win32con.MONITORINFOF_PRIMARY

                    monitor_data = {
                        "id": i,
                        "name": device_name,
                        "width": monitor_rect[2] - monitor_rect[0],
                        "height": monitor_rect[3] - monitor_rect[1],
                        "bbox": monitor_rect,
                        "work_area": work_area,
                        "primary": bool(is_primary),
                        "device": device_name,
                    }

                    monitors.append(monitor_data)

                except Exception as e:
                    print(f"Error getting monitor {i} info: {e}")
                    continue

        except ImportError:
            print("Warning: win32api not available. Using basic monitor detection.")
            print("Install pywin32 for full multi-monitor support: pip install pywin32")

        return monitors

    except Exception as e:
        print(f"Error detecting monitors: {e}")
        return [
            {
                "id": 0,
                "name": "Default Monitor",
                "width": 1920,
                "height": 1080,
                "bbox": None,
                "primary": True,
            }
        ]


def display_monitor_info(monitors):
    """Display information about available monitors."""
    print("🖥️  Available Monitors:")
    print("=" * 50)

    for i, monitor in enumerate(monitors):
        primary_str = " (PRIMARY)" if monitor.get("primary", False) else ""
        print(f"{i}: {monitor['name']}{primary_str}")
        print(f"   Resolution: {monitor['width']}x{monitor['height']}")
        if monitor.get("bbox"):
            bbox = monitor["bbox"]
            print(f"   Position: ({bbox[0]}, {bbox[1]}) to ({bbox[2]}, {bbox[3]})")
        if monitor.get("device"):
            print(f"   Device: {monitor['device']}")
        print()


def choose_monitor(monitors):
    """Let user choose which monitor to use."""
    if len(monitors) == 1:
        print(f"Only one monitor detected: {monitors[0]['name']}")
        return monitors[0]

    display_monitor_info(monitors)

    while True:
        try:
            choice = input(f"Choose monitor (0-{len(monitors)-1}): ").strip()
            monitor_id = int(choice)

            if 0 <= monitor_id < len(monitors):
                selected = monitors[monitor_id]
                print(
                    f"✅ Selected: {selected['name']} ({selected['width']}x{selected['height']})"
                )
                return selected
            else:
                print(f"❌ Invalid choice. Please enter 0-{len(monitors)-1}")

        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n👋 Cancelled by user")
            sys.exit(0)


def test_screenshot(monitor):
    """Test taking a screenshot of the selected monitor."""
    try:
        print(f"\n📸 Testing screenshot of {monitor['name']}...")

        if monitor.get("bbox"):
            # Capture specific monitor
            screenshot = ImageGrab.grab(bbox=monitor["bbox"])
        else:
            # Capture primary/default
            screenshot = ImageGrab.grab()

        # Save test screenshot
        test_filename = f"test_monitor_{monitor['id']}.png"
        screenshot.save(test_filename)
        print(f"✅ Test screenshot saved as: {test_filename}")
        print(f"   Size: {screenshot.size}")

        # Get average color as a test
        import numpy as np

        img_array = np.array(screenshot.resize((100, 100)))
        avg_color = np.mean(img_array, axis=(0, 1))
        print(
            f"   Average color: RGB({int(avg_color[0])}, {int(avg_color[1])}, {int(avg_color[2])})"
        )

        return True

    except Exception as e:
        print(f"❌ Error taking screenshot: {e}")
        return False


if __name__ == "__main__":
    print("🔍 Multi-Monitor Detection Tool")
    print("=" * 40)

    # Detect monitors
    monitors = get_all_monitors()

    if not monitors:
        print("❌ No monitors detected!")
        sys.exit(1)

    # Let user choose
    selected_monitor = choose_monitor(monitors)

    # Test screenshot
    if test_screenshot(selected_monitor):
        print(f"\n🎉 Monitor selection successful!")
        print(f"Selected monitor info:")
        print(f"  ID: {selected_monitor['id']}")
        print(f"  Name: {selected_monitor['name']}")
        print(f"  Resolution: {selected_monitor['width']}x{selected_monitor['height']}")
        if selected_monitor.get("bbox"):
            print(f"  Bounds: {selected_monitor['bbox']}")
    else:
        print("❌ Screenshot test failed")
