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
        
        # Get virtual desktop resolution (what Python sees)
        virtual_width = win32api.GetSystemMetrics(0)  # SM_CXSCREEN
        virtual_height = win32api.GetSystemMetrics(1)  # SM_CYSCREEN
        
        # Get actual desktop resolution
        hdc = win32gui.GetDC(0)
        actual_width = win32gui.GetDeviceCaps(hdc, 8)   # HORZRES
        actual_height = win32gui.GetDeviceCaps(hdc, 10)  # VERTRES
        win32gui.ReleaseDC(0, hdc)
        
        # Detect 4K scaling
        is_4k_scaled = (
            actual_width == 3840 and actual_height == 2160 and
            virtual_width != actual_width
        )
        
        monitor["is_4k_scaled"] = is_4k_scaled
        monitor["virtual_resolution"] = (virtual_width, virtual_height)
        monitor["actual_resolution"] = (actual_width, actual_height)
        
    except ImportError:
        monitor["is_4k_scaled"] = False
        monitor["virtual_resolution"] = (monitor["width"], monitor["height"])
        monitor["actual_resolution"] = (monitor["width"], monitor["height"])
    except Exception:
        monitor["is_4k_scaled"] = False
        monitor["virtual_resolution"] = (monitor["width"], monitor["height"])
        monitor["actual_resolution"] = (monitor["width"], monitor["height"])
    
    return monitor
