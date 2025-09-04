# bt_led_control/utils.py

import msvcrt


def check_for_exit_key() -> bool:
    """Check if user pressed End key to exit ambient mode."""
    if msvcrt.kbhit():
        key = msvcrt.getch()
        # Handle special keys (2-byte sequences)
        if ord(key) == 224:  # Special key prefix
            key2 = msvcrt.getch()
            # Check for End key (79)
            return ord(key2) == 79
        return False
    return False
