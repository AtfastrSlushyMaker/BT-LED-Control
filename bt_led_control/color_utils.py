# bt_led_control/color_utils.py

import numpy as np
from PIL import Image
from typing import Tuple, Optional


class ColorTransitioner:
    """Handles smooth color transitions between frames for LED lamps."""

    def __init__(self, transition_speed: float = 0.15):
        """
        Initialize the color transitioner.

        Args:
            transition_speed: How fast to transition (0.1 = slow, 0.3 = medium, 0.5+ = fast)
        """
        self.current_left = (0, 0, 0)
        self.current_right = (0, 0, 0)
        self.target_left = (0, 0, 0)
        self.target_right = (0, 0, 0)
        self.transition_speed = transition_speed

    def set_targets(
        self, left_color: Tuple[int, int, int], right_color: Tuple[int, int, int]
    ):
        """Set the target colors for smooth transition."""
        self.target_left = left_color
        self.target_right = right_color

    def update_smooth_colors(self) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """Update current colors towards targets with smooth interpolation."""
        # Smooth interpolation using exponential decay for natural motion
        self.current_left = self._interpolate_color(self.current_left, self.target_left)
        self.current_right = self._interpolate_color(
            self.current_right, self.target_right
        )

        return self.current_left, self.current_right

    def _interpolate_color(
        self, current: Tuple[int, int, int], target: Tuple[int, int, int]
    ) -> Tuple[int, int, int]:
        """Smoothly interpolate between current and target color using exponential decay."""
        factor = self.transition_speed

        r = int(current[0] + (target[0] - current[0]) * factor)
        g = int(current[1] + (target[1] - current[1]) * factor)
        b = int(current[2] + (target[2] - current[2]) * factor)

        return (r, g, b)

    def is_close_to_target(self, threshold: int = 5) -> bool:
        """Check if current colors are close enough to targets."""
        left_diff = sum(abs(c - t) for c, t in zip(self.current_left, self.target_left))
        right_diff = sum(
            abs(c - t) for c, t in zip(self.current_right, self.target_right)
        )

        return left_diff < threshold and right_diff < threshold

    def reset(
        self,
        left_color: Tuple[int, int, int] = (0, 0, 0),
        right_color: Tuple[int, int, int] = (0, 0, 0),
    ):
        """Reset the transitioner to specific colors."""
        self.current_left = left_color
        self.current_right = right_color
        self.target_left = left_color
        self.target_right = right_color


def enhance_color_saturation(
    r: int, g: int, b: int, saturation_factor: float = 1.5
) -> Tuple[int, int, int]:
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

    # Pink/Magenta: high red + high blue, low green
    if r > 200 and b > 200 and g < 100:
        return (r, g, b)  # Keep pink as-is

    # If the color is already quite saturated, don't over-enhance
    if color_range > 150:
        saturation_factor = min(saturation_factor, 1.2)

    # Pure white or near-white should stay as-is
    if min_val > 220 and color_range < 35:
        return (r, g, b)

    # Convert to HSV-like manipulation
    # Find which color is dominant
    if max_val == r:
        dominant = "red"
    elif max_val == g:
        dominant = "green"
    else:
        dominant = "blue"

    # Apply saturation enhancement
    if color_range > 20:  # Only enhance if there's some color difference
        # Calculate enhancement amount based on how much color difference exists
        enhancement = min(saturation_factor, 1.0 + (color_range / 255.0))

        # Reduce non-dominant colors more aggressively
        if dominant == "red":
            g = max(0, int(g / enhancement))
            b = max(0, int(b / enhancement))
        elif dominant == "green":
            r = max(0, int(r / enhancement))
            b = max(0, int(b / enhancement))
        else:  # blue
            r = max(0, int(r / enhancement))
            g = max(0, int(g / enhancement))

        # Slight boost to the dominant color if it's not too bright
        if max_val < 220:
            boost_factor = min(1.1, 1.0 + (255 - max_val) / 500.0)
            if dominant == "red":
                r = min(255, int(r * boost_factor))
            elif dominant == "green":
                g = min(255, int(g * boost_factor))
            else:  # blue
                b = min(255, int(b * boost_factor))

    return (r, g, b)


def smooth_color_transition(
    current_color: Optional[Tuple[int, int, int]],
    target_color: Tuple[int, int, int],
    smoothing_factor: float = 0.3,
) -> Tuple[int, int, int]:
    """
    Apply smooth transition between current and target colors.

    Args:
        current_color: Current RGB color tuple (or None for first frame)
        target_color: Target RGB color tuple
        smoothing_factor: Transition speed (0.1 = slow, 0.5 = fast)

    Returns:
        New RGB color tuple transitioning towards target
    """
    if current_color is None:
        return target_color

    cr, cg, cb = current_color
    tr, tg, tb = target_color

    # Exponential decay interpolation for natural motion
    new_r = int(cr + (tr - cr) * smoothing_factor)
    new_g = int(cg + (tg - cg) * smoothing_factor)
    new_b = int(cb + (tb - cb) * smoothing_factor)

    # Ensure values stay in valid range
    new_r = max(0, min(255, new_r))
    new_g = max(0, min(255, new_g))
    new_b = max(0, min(255, new_b))

    return (new_r, new_g, new_b)


def get_edge_colors_from_image(
    img, edge: str, sample_size: int = 50
) -> Tuple[int, int, int]:
    """Extract average color from a specific edge of an image."""
    width, height = img.size

    if edge == "left":
        crop_box = (0, 0, sample_size, height)
    elif edge == "right":
        crop_box = (width - sample_size, 0, width, height)
    elif edge == "top":
        crop_box = (0, 0, width, sample_size)
    elif edge == "bottom":
        crop_box = (0, height - sample_size, width, height)
    else:
        # Full screen fallback
        crop_box = (0, 0, width, height)

    # Crop and get average color
    edge_img = img.crop(crop_box)
    edge_array = np.array(edge_img)

    # Calculate average RGB
    avg_color = edge_array.mean(axis=(0, 1))

    return tuple(int(c) for c in avg_color)


def calculate_screen_average_color(
    img, sample_ratio: float = 0.1
) -> Tuple[int, int, int]:
    """Calculate the average color of a screen capture with downsampling for performance."""
    # Resize image for faster processing
    original_size = img.size
    sample_width = max(50, int(original_size[0] * sample_ratio))
    sample_height = max(50, int(original_size[1] * sample_ratio))

    # Resize with high-quality resampling
    img_small = img.resize((sample_width, sample_height), Image.Resampling.LANCZOS)

    # Convert to numpy array for fast calculation
    img_array = np.array(img_small)

    # Calculate average RGB
    avg_color = img_array.mean(axis=(0, 1))

    return tuple(int(c) for c in avg_color)
