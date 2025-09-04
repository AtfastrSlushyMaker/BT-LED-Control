# bt_led_control/ui_utils.py

from typing import List, Dict
from .monitor import get_available_monitors


def display_available_monitors() -> List[Dict]:
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


def choose_monitor_interactive() -> int:
    """Interactive monitor selection."""
    monitors = display_available_monitors()
    
    if len(monitors) == 1:
        print("Only one monitor detected. Using it automatically.")
        return 0
    
    while True:
        try:
            choice = input(f"Choose monitor (0-{len(monitors)-1}): ").strip()
            monitor_id = int(choice)
            if 0 <= monitor_id < len(monitors):
                return monitor_id
            else:
                print(f"Please enter a number between 0 and {len(monitors)-1}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nExiting...")
            return 0


def list_monitors():
    """List all available monitors."""
    display_available_monitors()
