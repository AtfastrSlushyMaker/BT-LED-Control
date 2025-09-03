# bt_led_control/screen_capture.py

from typing import Tuple, List, Dict, Optional
from PIL import ImageGrab
import numpy as np


def get_available_monitors() -> List[Dict]:
    """Get information about all available monitors."""
    try:
        import tkinter as tk

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


def display_available_monitors():
    """Display all available monitors for user selection."""
    monitors = get_available_monitors()

    print("\n🖥️  Available Monitors:")
    print("=" * 40)

    for monitor in monitors:
        primary_str = " (PRIMARY)" if monitor.get("primary", False) else ""
        print(f"  {monitor['id']}: {monitor['name']}{primary_str}")
        print(f"      Resolution: {monitor['width']}x{monitor['height']}")
        if monitor.get("bbox"):
            bbox = monitor["bbox"]
            print(f"      Position: ({bbox[0]}, {bbox[1]}) to ({bbox[2]}, {bbox[3]})")
        print()

    return monitors


def _capture_monitor_win32(bbox: Tuple[int, int, int, int]):
    """Capture screen using Win32 API for multi-monitor support with negative coordinates."""
    try:
        import win32gui
        import win32ui
        import win32con
        from PIL import Image

        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1

        # Get device contexts
        hdesktop = win32gui.GetDesktopWindow()
        hdc = win32gui.GetWindowDC(hdesktop)
        hdcmem = win32ui.CreateDCFromHandle(hdc)
        hdcmem2 = hdcmem.CreateCompatibleDC()

        # Create bitmap
        hbitmap = win32ui.CreateBitmap()
        hbitmap.CreateCompatibleBitmap(hdcmem, width, height)
        hdcmem2.SelectObject(hbitmap)

        # Copy screen area
        hdcmem2.BitBlt((0, 0), (width, height), hdcmem, (x1, y1), win32con.SRCCOPY)

        # Convert to PIL Image
        bmpinfo = hbitmap.GetInfo()
        bmpstr = hbitmap.GetBitmapBits(True)
        img = Image.frombuffer(
            "RGB",
            (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
            bmpstr,
            "raw",
            "BGRX",
            0,
            1,
        )

        # Cleanup
        hdcmem2.DeleteDC()
        hdcmem.DeleteDC()
        win32gui.ReleaseDC(hdesktop, hdc)
        win32gui.DeleteObject(hbitmap.GetHandle())

        return img

    except ImportError:
        raise ImportError(
            "Win32 capture requires pywin32. Install with: pip install pywin32"
        )
    except Exception as e:
        raise Exception(f"Win32 screen capture failed: {e}")


def get_screen_average_color(
    monitor_bbox: Optional[Tuple[int, int, int, int]] = None,
) -> Tuple[int, int, int]:
    """Capture screen and return average RGB color across entire screen or specified monitor."""
    try:
        if monitor_bbox and (monitor_bbox[0] < 0 or monitor_bbox[1] < 0):
            # Use Win32 for monitors with negative coordinates
            screenshot = _capture_monitor_win32(monitor_bbox)
        elif monitor_bbox:
            screenshot = ImageGrab.grab(bbox=monitor_bbox)
        else:
            screenshot = ImageGrab.grab()

        # Use moderate resize for speed while keeping color accuracy
        screenshot = screenshot.resize((640, 360))  # Smaller but not too small
        img_array = np.array(screenshot)
        avg_color = np.mean(img_array, axis=(0, 1))
        return tuple(map(int, avg_color))

    except Exception as e:
        print(f"Warning: Screen capture error: {e}")
        # Fallback to basic capture
        screenshot = ImageGrab.grab()
        screenshot = screenshot.resize((640, 360))
        img_array = np.array(screenshot)
        avg_color = np.mean(img_array, axis=(0, 1))
        return tuple(map(int, avg_color))


def get_screen_edge_color(
    edge_width: int = 50, monitor_bbox: Optional[Tuple[int, int, int, int]] = None
) -> Tuple[int, int, int]:
    """Capture screen and return average color from edges (Ambilight-style)."""
    try:
        if monitor_bbox and (monitor_bbox[0] < 0 or monitor_bbox[1] < 0):
            # Use Win32 for monitors with negative coordinates
            screenshot = _capture_monitor_win32(monitor_bbox)
        elif monitor_bbox:
            screenshot = ImageGrab.grab(bbox=monitor_bbox)
        else:
            screenshot = ImageGrab.grab()

        img_array = np.array(screenshot)
        height, width = img_array.shape[:2]

        # Sample larger edge areas for better color detection
        edge_pixels = []

        # Top edge - larger sample
        top_edge = img_array[:edge_width, :]
        edge_pixels.append(top_edge)

        # Bottom edge - larger sample
        bottom_edge = img_array[-edge_width:, :]
        edge_pixels.append(bottom_edge)

        # Left edge - full height for better sampling
        left_edge = img_array[:, :edge_width]
        edge_pixels.append(left_edge)

        # Right edge - full height for better sampling
        right_edge = img_array[:, -edge_width:]
        edge_pixels.append(right_edge)

        all_edge_pixels = np.concatenate(
            [pixels.reshape(-1, 3) for pixels in edge_pixels]
        )
        avg_color = np.mean(all_edge_pixels, axis=0)
        return tuple(map(int, avg_color))

    except Exception as e:
        print(f"Warning: Screen edge capture error: {e}")
        # Fallback to basic capture
        screenshot = ImageGrab.grab()
        img_array = np.array(screenshot)
        height, width = img_array.shape[:2]

        edge_pixels = []
        top_edge = img_array[:edge_width, :]
        edge_pixels.append(top_edge)
        bottom_edge = img_array[-edge_width:, :]
        edge_pixels.append(bottom_edge)
        left_edge = img_array[:, :edge_width]
        edge_pixels.append(left_edge)
        right_edge = img_array[:, -edge_width:]
        edge_pixels.append(right_edge)

        all_edge_pixels = np.concatenate(
            [pixels.reshape(-1, 3) for pixels in edge_pixels]
        )
        avg_color = np.mean(all_edge_pixels, axis=0)
        return tuple(map(int, avg_color))


def smooth_color_transition(
    current_color: Tuple[int, int, int],
    target_color: Tuple[int, int, int],
    smoothing_factor: float = 0.1,
) -> Tuple[int, int, int]:
    """Apply smoothing between current and target colors to prevent jarring changes."""
    r_current, g_current, b_current = current_color
    r_target, g_target, b_target = target_color

    r_smooth = int(r_current + (r_target - r_current) * smoothing_factor)
    g_smooth = int(g_current + (g_target - g_current) * smoothing_factor)
    b_smooth = int(b_current + (b_target - b_current) * smoothing_factor)

    return (r_smooth, g_smooth, b_smooth)


class ScreenColorCapture:
    """Class for managing continuous screen color capture with smoothing and monitor selection."""

    def __init__(
        self,
        edge_width: int = 50,
        smoothing_factor: float = 0.2,
        monitor_id: Optional[int] = None,
    ):
        self.edge_width = edge_width
        self.smoothing_factor = smoothing_factor
        self.current_color = (0, 0, 0)
        self.use_edge_sampling = True
        self.monitor_id = monitor_id
        self.monitor_bbox = None

        # Get monitor info if specific monitor requested
        if monitor_id is not None:
            self.set_monitor(monitor_id)

    def set_monitor(self, monitor_id: int) -> bool:
        """Set which monitor to capture from."""
        try:
            monitors = get_available_monitors()
            if 0 <= monitor_id < len(monitors):
                self.monitor_id = monitor_id
                selected_monitor = monitors[monitor_id]
                self.monitor_bbox = selected_monitor.get("bbox")
                print(
                    f"✅ Monitor set to: {selected_monitor['name']} ({selected_monitor['width']}x{selected_monitor['height']})"
                )
                return True
            else:
                print(
                    f"❌ Invalid monitor ID {monitor_id}. Available: 0-{len(monitors)-1}"
                )
                return False
        except Exception as e:
            print(f"❌ Error setting monitor: {e}")
            return False

    def get_monitor_info(self) -> Optional[Dict]:
        """Get information about the currently selected monitor."""
        if self.monitor_id is not None:
            monitors = get_available_monitors()
            if 0 <= self.monitor_id < len(monitors):
                return monitors[self.monitor_id]
        return None

    def get_next_color(self) -> Tuple[int, int, int]:
        """Get the next smoothed color from screen capture."""
        try:
            if self.use_edge_sampling:
                raw_color = get_screen_edge_color(self.edge_width, self.monitor_bbox)
            else:
                raw_color = get_screen_average_color(self.monitor_bbox)

            # If smoothing is 0 (instant), return raw color directly
            if self.smoothing_factor == 0.0:
                self.current_color = raw_color
            else:
                self.current_color = smooth_color_transition(
                    self.current_color, raw_color, self.smoothing_factor
                )

            return self.current_color

        except Exception as e:
            print(f"Warning: Screen capture error: {e}")
            return self.current_color  # Return last known color

    def set_edge_sampling(self, enabled: bool):
        """Enable or disable edge-based sampling."""
        self.use_edge_sampling = enabled

    def set_smoothing(self, factor: float):
        """Set the smoothing factor (0.0 = very smooth, 1.0 = instant)."""
        self.smoothing_factor = max(0.0, min(1.0, factor))

    def list_monitors(self) -> List[Dict]:
        """List all available monitors."""
        return get_available_monitors()
