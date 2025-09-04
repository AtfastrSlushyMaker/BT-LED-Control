# bt_led_control/monitor.py

from typing import List, Dict
import tkinter as tk


def get_available_monitors() -> List[Dict]:
    """Get information about all available monitors."""
    try:
        # Basic fallback monitor info
        root = tk.Tk()
        root.withdraw()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()

        monitors = [
            {
                "id": 0,
                "name": "Primary Monitor",
                "width": width,
                "height": height,
                "bbox": (0, 0, width, height),
                "primary": True,
            }
        ]

        # Try to get detailed monitor info using Windows API
        try:
            import win32api
            import win32con
            from win32api import EnumDisplayMonitors, GetMonitorInfo

            monitors.clear()
            monitor_handles = EnumDisplayMonitors()

            for i, (hmon, hdc, rect) in enumerate(monitor_handles):
                try:
                    monitor_info = GetMonitorInfo(hmon)
                    device_name = monitor_info.get("Device", f"Monitor {i+1}")
                    monitor_rect = monitor_info["Monitor"]
                    is_primary = monitor_info["Flags"] & win32con.MONITORINFOF_PRIMARY

                    monitors.append(
                        {
                            "id": i,
                            "name": device_name,
                            "width": monitor_rect[2] - monitor_rect[0],
                            "height": monitor_rect[3] - monitor_rect[1],
                            "bbox": monitor_rect,
                            "primary": bool(is_primary),
                            "device": device_name,
                        }
                    )
                except Exception as e:
                    print(f"Warning: Could not get info for monitor {i}: {e}")
                    continue

        except ImportError:
            print("Info: Advanced multi-monitor support requires pywin32")
            print("Install with: pip install pywin32")
        except Exception as e:
            print(f"Warning: Could not detect all monitors: {e}")

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


def get_monitor_with_scaling_info(monitor_id: int) -> Dict:
    """Get detailed monitor information including 4K scaling detection."""
    monitors = get_available_monitors()

    if monitor_id >= len(monitors):
        return monitors[0]  # Fallback to primary

    monitor = monitors[monitor_id]

    # Check for 4K scaling using Win32 API
    try:
        import win32api
        import win32gui
        import win32con

        # Get the monitor's device context to check its actual capabilities
        bbox = monitor["bbox"]
        if bbox:
            # Try to get the actual monitor resolution using device caps
            try:
                # Get device context for this specific monitor
                hmonitor = win32api.MonitorFromPoint(
                    (bbox[0] + 100, bbox[1] + 100), win32con.MONITOR_DEFAULTTONEAREST
                )
                monitor_info_raw = win32api.GetMonitorInfo(hmonitor)

                # Get the device name for this monitor
                device_name = monitor_info_raw.get("Device", "")

                if device_name:
                    # Create device context for this specific monitor - fix the API call
                    try:
                        hdc = win32gui.CreateDC(device_name, device_name, None, None)
                        if hdc:
                            # Get actual monitor resolution
                            actual_width = win32gui.GetDeviceCaps(hdc, 8)  # HORZRES
                            actual_height = win32gui.GetDeviceCaps(hdc, 10)  # VERTRES

                            # Get virtual resolution (what Windows reports)
                            virtual_width = bbox[2] - bbox[0]
                            virtual_height = bbox[3] - bbox[1]

                            win32gui.DeleteDC(hdc)
                        else:
                            raise Exception("Could not create device context")
                    except Exception:
                        # Fallback to global desktop if monitor-specific DC fails
                        hdc = win32gui.GetDC(0)
                        actual_width = win32gui.GetDeviceCaps(hdc, 8)
                        actual_height = win32gui.GetDeviceCaps(hdc, 10)
                        virtual_width = bbox[2] - bbox[0]
                        virtual_height = bbox[3] - bbox[1]
                        win32gui.ReleaseDC(0, hdc)
                else:
                    # Use bbox dimensions as both virtual and actual
                    virtual_width = bbox[2] - bbox[0]
                    virtual_height = bbox[3] - bbox[1]
                    actual_width = virtual_width
                    actual_height = virtual_height

            except Exception:
                # Use the dimensions from bbox as both virtual and actual
                virtual_width = bbox[2] - bbox[0]
                virtual_height = bbox[3] - bbox[1]
                actual_width = virtual_width
                actual_height = virtual_height
        else:
            # No bbox, use basic detection
            virtual_width = monitor["width"]
            virtual_height = monitor["height"]
            actual_width = virtual_width
            actual_height = virtual_height

        # Conservative 4K detection - only flag as 4K if we have strong evidence
        is_4k = False
        is_scaled = False

        # Method 1: Detected actual 4K resolution
        if actual_width >= 3840 and actual_height >= 2160:
            is_4k = True
            is_scaled = virtual_width != actual_width or virtual_height != actual_height
        # Method 2: Only apply scaling detection to your known 4K TV (DISPLAY8)
        elif (
            virtual_width == 1920
            and virtual_height == 1080
            and monitor["name"] == r"\\.\DISPLAY8"
        ):
            # This is specifically your 4K TV scaled to 200%
            is_4k = True
            is_scaled = True
            actual_width = 3840
            actual_height = 2160
        else:
            # For all other monitors, assume no scaling
            actual_width = virtual_width
            actual_height = virtual_height
            is_scaled = False

        is_4k_scaled = is_4k and is_scaled

        # Calculate scaling factors
        scaling_x = actual_width / virtual_width if virtual_width > 0 else 1.0
        scaling_y = actual_height / virtual_height if virtual_height > 0 else 1.0

        monitor["is_4k"] = is_4k
        monitor["is_scaled"] = is_scaled
        monitor["is_4k_scaled"] = is_4k_scaled
        monitor["virtual_resolution"] = (virtual_width, virtual_height)
        monitor["actual_resolution"] = (actual_width, actual_height)
        monitor["actual_width"] = actual_width
        monitor["actual_height"] = actual_height
        monitor["scaling_x"] = scaling_x
        monitor["scaling_y"] = scaling_y
        monitor["windows_rect"] = monitor["bbox"]  # Use the bbox as windows_rect

    except ImportError:
        monitor["is_4k"] = False
        monitor["is_scaled"] = False
        monitor["is_4k_scaled"] = False
        monitor["virtual_resolution"] = (monitor["width"], monitor["height"])
        monitor["actual_resolution"] = (monitor["width"], monitor["height"])
        monitor["actual_width"] = monitor["width"]
        monitor["actual_height"] = monitor["height"]
        monitor["scaling_x"] = 1.0
        monitor["scaling_y"] = 1.0
        monitor["windows_rect"] = monitor["bbox"]
    except Exception:
        monitor["is_4k"] = False
        monitor["is_scaled"] = False
        monitor["is_4k_scaled"] = False
        monitor["virtual_resolution"] = (monitor["width"], monitor["height"])
        monitor["actual_resolution"] = (monitor["width"], monitor["height"])
        monitor["actual_width"] = monitor["width"]
        monitor["actual_height"] = monitor["height"]
        monitor["scaling_x"] = 1.0
        monitor["scaling_y"] = 1.0
        monitor["windows_rect"] = monitor["bbox"]

    return monitor
