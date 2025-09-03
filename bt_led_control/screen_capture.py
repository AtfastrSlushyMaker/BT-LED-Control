# bt_led_control/screen_capture.py

from typing import Tuple
from PIL import ImageGrab
import numpy as np


def get_screen_average_color() -> Tuple[int, int, int]:
    """Capture screen and return average RGB color across entire screen."""
    screenshot = ImageGrab.grab()
    # Use moderate resize for speed while keeping color accuracy
    screenshot = screenshot.resize((640, 360))  # Smaller but not too small
    img_array = np.array(screenshot)
    avg_color = np.mean(img_array, axis=(0, 1))
    return tuple(map(int, avg_color))


def get_screen_edge_color(edge_width: int = 50) -> Tuple[int, int, int]:
    """Capture screen and return average color from edges (Ambilight-style)."""
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

    all_edge_pixels = np.concatenate([pixels.reshape(-1, 3) for pixels in edge_pixels])
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
    """Class for managing continuous screen color capture with smoothing."""

    def __init__(self, edge_width: int = 50, smoothing_factor: float = 0.2):
        self.edge_width = edge_width
        self.smoothing_factor = smoothing_factor
        self.current_color = (0, 0, 0)
        self.use_edge_sampling = True

    def get_next_color(self) -> Tuple[int, int, int]:
        """Get the next smoothed color from screen capture."""
        if self.use_edge_sampling:
            raw_color = get_screen_edge_color(self.edge_width)
        else:
            raw_color = get_screen_average_color()

        # If smoothing is 0 (instant), return raw color directly
        if self.smoothing_factor == 0.0:
            self.current_color = raw_color
        else:
            self.current_color = smooth_color_transition(
                self.current_color, raw_color, self.smoothing_factor
            )

        return self.current_color

    def set_edge_sampling(self, enabled: bool):
        """Enable or disable edge-based sampling."""
        self.use_edge_sampling = enabled

    def set_smoothing(self, factor: float):
        """Set the smoothing factor (0.0 = very smooth, 1.0 = instant)."""
        self.smoothing_factor = max(0.0, min(1.0, factor))
