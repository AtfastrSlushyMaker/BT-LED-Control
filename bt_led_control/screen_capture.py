# bt_led_control/screen_capture.py

from typing import Tuple, List, Dict, Optional
from PIL import ImageGrab, Image
import numpy as np
from .monitor import get_monitor_with_scaling_info


def _capture_monitor_win32(bbox: Tuple[int, int, int, int]) -> Image.Image:
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


def _capture_4k_monitor_direct(monitor_info: Dict) -> Image.Image:
    """Capture a 4K monitor at full resolution using Win32 API directly."""
    try:
        import win32gui
        import win32ui
        import win32con

        # Get actual monitor device info
        device_name = monitor_info.get("device_name", "")
        actual_width = monitor_info.get("actual_width", 3840)
        actual_height = monitor_info.get("actual_height", 2160)

        print(
            f"🎯 Capturing 4K monitor {device_name} at {actual_width}x{actual_height}"
        )

        # Get the device context for the specific monitor
        hdc_screen = win32gui.CreateDC(device_name, None, None)
        hdc_mem = win32ui.CreateDCFromHandle(hdc_screen)
        hdc_mem2 = hdc_mem.CreateCompatibleDC()

        # Create bitmap at full resolution
        hbitmap = win32ui.CreateBitmap()
        hbitmap.CreateCompatibleBitmap(hdc_mem, actual_width, actual_height)
        hdc_mem2.SelectObject(hbitmap)

        # Copy the entire monitor content at full resolution
        hdc_mem2.BitBlt(
            (0, 0), (actual_width, actual_height), hdc_mem, (0, 0), win32con.SRCCOPY
        )

        # Convert to PIL Image
        bmpinfo = hbitmap.GetInfo()
        bmpstr = hbitmap.GetBitmapBits(True)
        screenshot = Image.frombuffer(
            "RGB",
            (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
            bmpstr,
            "raw",
            "BGRX",
            0,
            1,
        )

        # Cleanup
        hdc_mem2.DeleteDC()
        hdc_mem.DeleteDC()
        win32gui.DeleteDC(hdc_screen)

        print(f"✅ Captured 4K at full resolution: {screenshot.size}")
        return screenshot

    except Exception as e:
        print(f"❌ 4K direct capture failed: {e}")
        raise e


def _capture_with_bbox(monitor_bbox: Tuple[int, int, int, int]) -> Image.Image:
    """Helper function to capture using bbox with proper coordinate handling."""
    if monitor_bbox[0] < 0 or monitor_bbox[1] < 0:
        # Get full virtual desktop first
        screenshot = ImageGrab.grab(all_screens=True)

        # Get virtual desktop coordinates
        import win32api
        import win32con

        virt_left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        virt_top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

        # Convert monitor coordinates to crop coordinates
        x1, y1, x2, y2 = monitor_bbox
        crop_x1 = x1 - virt_left
        crop_y1 = y1 - virt_top
        crop_x2 = x2 - virt_left
        crop_y2 = y2 - virt_top

        # Crop to the specific monitor
        screenshot = screenshot.crop((crop_x1, crop_y1, crop_x2, crop_y2))
    else:
        # Positive coordinates - use regular grab
        screenshot = ImageGrab.grab(bbox=monitor_bbox)

    return screenshot


def _capture_4k_scaled_monitor(monitor_info: Dict) -> Image.Image:
    """Capture a scaled 4K monitor at full resolution using virtual desktop method."""
    try:
        import win32api
        import win32con

        # Get virtual desktop coordinates
        virt_left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        virt_top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

        # Capture full virtual desktop (this gets the actual high-res content)
        screenshot = ImageGrab.grab(all_screens=True)

        # For a scaled 4K display, the actual 4K content is at full resolution
        # Calculate where the 4K content should be in the captured image
        x1, y1, x2, y2 = monitor_info["windows_rect"]

        # Convert to virtual desktop coordinates
        crop_x1 = x1 - virt_left
        crop_y1 = y1 - virt_top

        # For 4K scaled displays, use the actual resolution instead of Windows scaled size
        actual_width = monitor_info["actual_width"]
        actual_height = monitor_info["actual_height"]

        # Calculate the 4K crop area
        # Based on our discovery: 4K content is at full resolution in the captured area
        if crop_x1 == 0 and crop_y1 == 0:
            # TV is at the leftmost position - use full 4K dimensions
            crop_x2 = actual_width
            crop_y2 = actual_height
        else:
            # Calculate scaled coordinates for other positions
            scaling_x = monitor_info["scaling_x"]
            scaling_y = monitor_info["scaling_y"]
            crop_x1 = int(crop_x1 * scaling_x)
            crop_y1 = int(crop_y1 * scaling_y)
            crop_x2 = crop_x1 + actual_width
            crop_y2 = crop_y1 + actual_height

        # Ensure coordinates are within bounds
        max_x, max_y = screenshot.size
        crop_x1 = max(0, min(crop_x1, max_x))
        crop_y1 = max(0, min(crop_y1, max_y))
        crop_x2 = max(crop_x1, min(crop_x2, max_x))
        crop_y2 = max(crop_y1, min(crop_y2, max_y))

        # Crop to get the full 4K content
        screenshot = screenshot.crop((crop_x1, crop_y1, crop_x2, crop_y2))

        return screenshot

    except Exception as e:
        print(f"4K scaled capture failed: {e}")
        # Fall back to standard method
        return _capture_with_bbox(monitor_info["windows_rect"])


def get_screen_average_color(
    monitor_bbox: Optional[Tuple[int, int, int, int]] = None,
    monitor_id: Optional[int] = None,
) -> Tuple[int, int, int]:
    """Capture screen and return average RGB color across entire screen or specified monitor."""
    try:
        # If monitor_id is provided, check if it's a scaled 4K display
        if monitor_id is not None:
            monitor_info = get_monitor_with_scaling_info(monitor_id)
            if monitor_info and monitor_info["is_4k"] and monitor_info["is_scaled"]:
                try:
                    # Use 4K scaled capture for scaled 4K displays
                    screenshot = _capture_4k_scaled_monitor(monitor_info)
                except Exception as e:
                    print(f"4K scaled capture failed, falling back: {e}")
                    # Fall back to bbox method
                    if monitor_bbox:
                        screenshot = _capture_with_bbox(monitor_bbox)
                    else:
                        screenshot = ImageGrab.grab()
            else:
                # Use bbox method for non-4K or non-scaled displays
                if monitor_bbox:
                    screenshot = _capture_with_bbox(monitor_bbox)
                else:
                    screenshot = ImageGrab.grab()
        else:
            # Legacy behavior - use bbox if provided
            if monitor_bbox:
                screenshot = _capture_with_bbox(monitor_bbox)
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
        try:
            screenshot = ImageGrab.grab()
            screenshot = screenshot.resize((640, 360))
            img_array = np.array(screenshot)
            avg_color = np.mean(img_array, axis=(0, 1))
            return tuple(map(int, avg_color))
        except:
            return (0, 0, 0)


def get_screen_edge_color(
    edge_width: int = 50,
    monitor_bbox: Optional[Tuple[int, int, int, int]] = None,
    monitor_id: Optional[int] = None,
) -> Tuple[int, int, int]:
    """Capture screen and return average color from edges (Ambilight-style)."""
    try:
        # Use 4K-aware capture if monitor_id is provided and it's a scaled 4K display
        if monitor_id is not None:
            monitor_info = get_monitor_with_scaling_info(monitor_id)
            if monitor_info and monitor_info["is_4k"] and monitor_info["is_scaled"]:
                try:
                    screenshot = _capture_4k_scaled_monitor(monitor_info)
                except Exception as e:
                    print(f"4K edge capture failed, falling back: {e}")
                    screenshot = (
                        _capture_with_bbox(monitor_bbox)
                        if monitor_bbox
                        else ImageGrab.grab()
                    )
            else:
                screenshot = (
                    _capture_with_bbox(monitor_bbox)
                    if monitor_bbox
                    else ImageGrab.grab()
                )
        elif monitor_bbox and (monitor_bbox[0] < 0 or monitor_bbox[1] < 0):
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
            from .monitor import get_available_monitors

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
            from .monitor import get_available_monitors

            monitors = get_available_monitors()
            if 0 <= self.monitor_id < len(monitors):
                return monitors[self.monitor_id]
        return None

    def get_next_color(self) -> Tuple[int, int, int]:
        """Get the next smoothed color from screen capture."""
        try:
            from .color_utils import smooth_color_transition

            if self.use_edge_sampling:
                raw_color = get_screen_edge_color(
                    self.edge_width, self.monitor_bbox, self.monitor_id
                )
            else:
                # Pass monitor_id for better 4K support
                raw_color = get_screen_average_color(self.monitor_bbox, self.monitor_id)

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
