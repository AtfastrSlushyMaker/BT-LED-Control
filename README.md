# BT-LED-Control 🎨

Control **Magic Lantern LED lights** via **Bluetooth Low Energy (BLE)** directly from Python.  
This project is an open-source alternative to the official *Magic Lantern* app, providing full programmatic control over your LED devices with **professional dual-lamp Ambilight support**.

---

## ✨ Features

### Single Lamp Control

- 🔗 **Easy BLE Connection** - Automatic device discovery and connection
- 🎨 **Full Color Control** - Set any RGB color (0-255 values)
- 🌈 **Preset Colors** - Red, Green, Blue, White, Purple, Orange, Yellow, Cyan
- 🖥️ **Ambient Screen Lighting** - Real-time screen color matching with advanced color enhancement

### Dual-Lamp Ambilight System

- 🚀 **Dual-Lamp Setup** - Control two lamps simultaneously for left/right screen zones
- 🎯 **Professional Ambilight** - Left lamp matches left screen zone, right lamp matches right zone
- ⚡ **High Performance** - 60 FPS and 120 FPS ultra-smooth modes
- 🎨 **Enhanced Color Saturation** - Vibrant 2.2x-2.5x saturation boost for immersive lighting
- 🔄 **Intelligent Connection Management** - Automatic reconnection and robust error handling
- 🖥️ **4K Display Support** - Full 4K capture with automatic scaling detection (100%, 150%, 200%)

### Advanced Features

- 🖥️ **Multi-Monitor Support** - Choose which monitor to capture for ambient lighting  
- 🔍 **Advanced Screen Detection** - Automatic detection of all connected monitors with 4K support
- 🔧 **Win32 Integration** - Proper capture from monitors with negative coordinates
- 🎯 **Smart Color Enhancement** - Intelligent saturation boost while preserving natural color mixes
- ⚡ **Simple API** - Clean, async Python interface
- 🎮 **Interactive Menu** - Command-line interface with dual-lamp mode switching
- 🔧 **Extensible** - Easy to add new features and effects

---

## 🚀 Quick Start

### Installation

1. **Clone the repository:**

```bash
git clone https://github.com/AtfastrSlushyMaker/BT-LED-Control.git
cd BT-LED-Control
```

2. **Set up virtual environment:**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

### Interactive Menu (Easiest Way)

Run the interactive LED control menu:

```bash
python led_menu.py
```

This provides a user-friendly interface with:

- **Single Lamp Mode** - Control one LED lamp with ambient lighting
- **Dual-Lamp Mode** - Professional Ambilight with two lamps for left/right screen zones
- **Mode Switching** - Press 'M' to switch between Single and Dual-Lamp modes
- **Monitor Selection** - Choose which monitor to capture for ambient lighting
- **4K Support** - Automatic detection and proper capture of 4K displays at any scaling

---

## 🔥 Dual-Lamp Professional Ambilight

Experience true cinematic lighting with our professional dual-lamp Ambilight system!

### Quick Start

1. **Connect two Magic Lantern lamps** to your system
2. **Run the menu**: `python led_menu.py`
3. **Switch to Dual-Lamp mode**: Press 'M'
4. **Connect both lamps**: Choose option 1
5. **Select your monitor**: Choose option 12 (supports 4K at any scaling)
6. **Start Ambilight**: Choose option 10 (60 FPS) or 11 (120 FPS)
7. **Enjoy immersive lighting**: Left lamp = left screen zone, right lamp = right screen zone

### Dual-Lamp Features

- **🎯 Professional Zone Mapping**: Left lamp mirrors left screen zone, right lamp mirrors right zone
- **⚡ High Performance**: 60 FPS (smooth) or 120 FPS (ultra-smooth) modes  
- **🎨 Enhanced Saturation**: 2.2x-2.5x color boost for vibrant, cinematic lighting
- **🖥️ 4K Display Support**: Full 4K capture at 100%, 150%, or 200% scaling
- **🔄 Robust Connections**: Automatic reconnection and error recovery
- **🎮 Easy Controls**: Test lamps, reconnect, monitor selection, and more

### Supported Configurations

- **Left Lamp**: `BE:28:72:00:37:C8` (matches left screen zone)
- **Right Lamp**: `BE:28:72:00:39:FD` (matches right screen zone)
- **Any Monitor**: Primary, secondary, 4K TVs, gaming monitors
- **Any Resolution**: 1080p, 1440p, 4K, ultrawide, mixed setups
- **Any Scaling**: 100%, 125%, 150%, 200% Windows scaling

---

## 💻 Python API Usage

### Basic Usage

```python
import asyncio
from bt_led_control.device import LT22Lamp

async def control_led():
    # Create lamp instance
    lamp = LT22Lamp()
    
    # Connect to device
    await lamp.connect()
    
    # Control the LED
    await lamp.turn_red()
    await lamp.turn_green()
    await lamp.turn_blue()
    await lamp.turn_white()
    
    # Custom colors (RGB 0-255)
    await lamp.set_color(255, 128, 0)  # Orange
    await lamp.set_color(128, 0, 128)  # Purple
    
    # Turn off
    await lamp.turn_off()
    
    # Disconnect
    await lamp.disconnect()

# Run it
asyncio.run(control_led())
```

### Advanced Usage

```python
import asyncio
from bt_led_control.device import LT22Lamp

async def color_cycle():
    lamp = LT22Lamp()
    await lamp.connect()
    
    colors = [
        (255, 0, 0),    # Red
        (255, 165, 0),  # Orange  
        (255, 255, 0),  # Yellow
        (0, 255, 0),    # Green
        (0, 255, 255),  # Cyan
        (0, 0, 255),    # Blue
        (128, 0, 128),  # Purple
    ]
    
    for r, g, b in colors:
        await lamp.set_color(r, g, b)
        await asyncio.sleep(1)  # Wait 1 second
    
    await lamp.turn_off()
    await lamp.disconnect()

asyncio.run(color_cycle())
```

---

## 🖥️ Ambient Screen Lighting

Experience immersive lighting that matches your screen content in real-time!

### Quick Start

Use the interactive menu for the easiest setup:

```bash
python led_menu.py
# Select option 11 for 120 FPS ambient lighting
# Select option 12 for ultra-smooth unlimited FPS mode
# Press 'END' key to exit ambient lighting
```

### API Usage

```python
import asyncio
from bt_led_control.device import LT22Lamp

async def ambient_lighting():
    lamp = LT22Lamp()
    await lamp.connect()
    
    # Start 120 FPS ambient lighting
    await lamp.start_ambient_lighting(fps=120)
    
    # Or start ultra-smooth mode (unlimited FPS)
    await lamp.start_ultra_smooth_ambient()
    
    await lamp.disconnect()

asyncio.run(ambient_lighting())
```

### Features

- **🚀 High Performance**: 120+ FPS for ultra-smooth color transitions
- **🎨 Smart Color Enhancement**: Intelligently boosts washed-out colors while preserving natural mixes
- **🖱️ Easy Control**: Press 'END' key to exit ambient mode
- **⚡ Optimized Capture**: Fast screen sampling with edge detection for better color accuracy
- **🎯 Color Accuracy**: Special handling for whites, cyans, yellows, and magentas
- **🖥️ Multi-Monitor Support**: Select any connected monitor for ambient lighting capture

### Multi-Monitor Support

Perfect for multi-screen setups! The system can:

- **🔍 Auto-Detect**: Automatically discover all connected monitors
- **📺 Monitor Selection**: Choose which screen to capture via menu option 13
- **🔧 Advanced Capture**: Uses Win32 API for proper multi-monitor support
- **🎮 Gaming Setup**: Capture from your gaming monitor while using other screens
- **⚡ Performance**: Same high-speed capture regardless of monitor choice

**Supported Configurations:**

- Single monitor setups (automatic)
- Multi-monitor with positive coordinates  
- Multi-monitor with negative coordinates (left-positioned screens)
- Mixed resolution setups (e.g., 4K primary + 1080p secondary)

### How It Works

1. **Screen Capture**: Captures your selected screen at high speed with optimized resolution
2. **Color Analysis**: Samples screen edges and calculates average color
3. **Smart Enhancement**: Applies intelligent saturation boost:
   - Preserves natural color combinations (white, cyan, yellow, magenta)
   - Enhances single-color dominance for vivid ambient lighting
   - Maintains color accuracy for mixed content
4. **LED Update**: Sends color commands to your LED strip in real-time

---

## 🛠️ API Reference

### Single Lamp - LT22Lamp Class

| Method | Description | Returns |
|--------|-------------|---------|
| `connect()` | Connect to LED device | `bool` - Success status |
| `disconnect()` | Disconnect from device | `bool` - Success status |
| `set_color(r, g, b)` | Set RGB color (0-255 each) | `bool` - Success status |
| `turn_red()` | Turn LED red | `bool` - Success status |
| `turn_green()` | Turn LED green | `bool` - Success status |
| `turn_blue()` | Turn LED blue | `bool` - Success status |
| `turn_white()` | Turn LED white | `bool` - Success status |
| `turn_off()` | Turn LED off | `bool` - Success status |
| `start_ambient_lighting(fps=120)` | Start screen-matching ambient lighting | `None` |
| `start_ultra_smooth_ambient()` | Start unlimited FPS ambient lighting | `None` |

### Dual-Lamp - DualLampManager Class

| Method | Description | Returns |
|--------|-------------|---------|
| `connect_both()` | Connect to both left and right lamps | `Dict[str, bool]` |
| `disconnect_both()` | Disconnect from both lamps | `Dict[str, bool]` |
| `reconnect_both()` | Reconnect both lamps with retry logic | `bool` |
| `set_both_color(r, g, b)` | Set same RGB color on both lamps | `Dict[str, bool]` |
| `set_left_color(r, g, b)` | Set RGB color on left lamp only | `bool` |
| `set_right_color(r, g, b)` | Set RGB color on right lamp only | `bool` |
| `turn_off_both()` | Turn off both lamps | `Dict[str, bool]` |
| `start_dual_ambilight(fps, brightness_boost, saturation_factor, monitor_id)` | Start professional dual-lamp Ambilight | `bool` |
| `test_lamps()` | Test both lamps with different colors | `None` |

---

## 📁 Project Structure

```text
BT-LED-Control/
├── bt_led_control/          # Main package
│   ├── __init__.py         # Package initialization & exports
│   ├── bluetooth.py         # BLE connection management
│   ├── commands.py          # LED command protocols
│   ├── device.py           # Single lamp interface (includes ambient lighting)
│   ├── dual_lamp.py        # Dual-lamp Ambilight system
│   ├── screen_capture.py   # Screen color capture and analysis (4K support)
│   ├── color_utils.py      # Color enhancement and processing
│   ├── monitor.py          # Multi-monitor detection with 4K scaling
│   ├── ui_utils.py         # User interface utilities
│   └── utils.py            # Utility functions
├── led_menu.py             # Interactive control menu (single & dual-lamp modes)
├── requirements.txt        # Project dependencies
├── .gitignore             # Git ignore rules
└── README.md              # Project documentation
```

---

## 🔧 Technical Details

### Protocol Information

- **Target Device**: Magic Lantern MELK-OF10 LED lights
- **Connection**: Bluetooth Low Energy (BLE)
- **Service UUID**: `0000fff0-0000-1000-8000-00805f9b34fb`
- **Command UUID**: `0000fff3-0000-1000-8000-00805f9b34fb`
- **Protocol**: `[0x7E, 0x00, 0x05, 0x03, G, R, B, 0x00, 0xEF]`

### Requirements

- **Python**: 3.8+
- **OS**: Windows, macOS, Linux
- **Hardware**: Bluetooth adapter
- **Dependencies**: `bleak`, `asyncio`, `Pillow` (PIL), `numpy`, `msvcrt` (Windows)

**For Ambient Lighting:**

- Screen access permissions may be required on some systems
- Windows: Built-in screen capture support
- macOS/Linux: May require additional permissions for screen access

---

## 🎯 Examples

### Example Scripts

Check out these example files:

- `led_menu.py` - Interactive command-line interface with single and dual-lamp modes, full Ambilight support
- `debug_ambilight.py` - Dual-lamp color testing and debugging utilities

### Single Lamp Ambient Lighting

```python
import asyncio
from bt_led_control.device import LT22Lamp

async def smart_ambient_lighting():
    """Example of single lamp ambient lighting with custom settings."""
    lamp = LT22Lamp()
    
    if await lamp.connect():
        print("🚀 Starting ambient lighting!")
        print("Press 'END' key to exit")
        
        # Start high-performance ambient lighting
        await lamp.start_ambient_lighting(fps=120)
        
        await lamp.disconnect()
    else:
        print("❌ Could not connect to LED")

asyncio.run(smart_ambient_lighting())
```

### Dual-Lamp Professional Ambilight

```python
import asyncio
from bt_led_control.dual_lamp import DualLampManager

async def professional_ambilight():
    """Example of dual-lamp Ambilight system."""
    dual_lamps = DualLampManager()
    
    # Connect to both lamps
    connections = await dual_lamps.connect_both()
    
    if connections["left"] and connections["right"]:
        print("🔥 Starting Professional Dual-Lamp Ambilight!")
        print("Left lamp = left screen zone | Right lamp = right screen zone")
        print("Press 'END' key to exit")
        
        # Start professional Ambilight (60 FPS, enhanced saturation)
        await dual_lamps.start_dual_ambilight(
            fps=60,
            brightness_boost=25,
            saturation_factor=2.2,
            monitor_id=0  # Use primary monitor
        )
        
        await dual_lamps.disconnect_both()
    else:
        print("❌ Could not connect to both lamps")
        print(f"Left: {'✅' if connections['left'] else '❌'}")
        print(f"Right: {'✅' if connections['right'] else '❌'}")

asyncio.run(professional_ambilight())
```

### Custom Dual Colors

```python
import asyncio
from bt_led_control.dual_lamp import DualLampManager

async def custom_dual_colors():
    """Example of setting different colors on each lamp."""
    dual_lamps = DualLampManager()
    
    await dual_lamps.connect_both()
    
    # Set different colors
    await dual_lamps.set_left_color(255, 0, 0)    # Red on left
    await dual_lamps.set_right_color(0, 0, 255)   # Blue on right
    
    await asyncio.sleep(2)
    
    # Test sequence
    await dual_lamps.test_lamps()
    
    await dual_lamps.turn_off_both()
    await dual_lamps.disconnect_both()

asyncio.run(custom_dual_colors())
```

### Create Your Own Script

```python
import asyncio
from bt_led_control.device import LT22Lamp

async def my_led_script():
    lamp = LT22Lamp()
    
    if await lamp.connect():
        # Your custom LED control here!
        await lamp.set_color(255, 192, 203)  # Pink
        await asyncio.sleep(2)
        await lamp.turn_off()
        await lamp.disconnect()
    else:
        print("Could not connect to LED")

asyncio.run(my_led_script())
```

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Support for more LED models and protocols
- Additional dual-lamp effects (synchronized patterns, color waves)
- Brightness control per lamp
- Timer and scheduling functions
- GUI interface for dual-lamp setup
- Multi-zone ambient lighting (more than 2 lamps)
- Custom screen capture regions
- Audio-reactive lighting modes
- Integration with streaming software (OBS, etc.)
- Gaming integration (match in-game events)

---

## � License

This project is open source. Feel free to use, modify, and distribute.

---

## 🔍 Troubleshooting

### Connection Issues

1. Make sure LED device(s) are powered on
2. Ensure Bluetooth is enabled on your computer
3. Check that devices are in pairing mode
4. Try running as administrator (Windows)
5. For dual-lamp setup, ensure both lamps are discoverable

### Device Not Found

1. Verify the device addresses in the code:
   - Single lamp: Check `bluetooth.py`
   - Dual-lamp: Left `BE:28:72:00:37:C8`, Right `BE:28:72:00:39:FD`

2. Use the built-in device scanner:

   ```python
   from bt_led_control.bluetooth import BLEManager
   import asyncio
   
   async def scan():
       ble = BLEManager()
       devices = await ble.scan_for_devices(display=True)
   
   asyncio.run(scan())
   ```

3. Update device addresses if needed for your specific lamps

### Dual-Lamp Specific Issues

1. **Only one lamp connecting:**
   - Check both lamps are powered and in range
   - Verify device addresses are correct
   - Use menu option 14 to reconnect both lamps
   - Try the test function (option 13) to identify which lamp has issues

2. **Connection lost during Ambilight:**
   - The system includes automatic retry logic
   - Use reconnect option if needed
   - Ensure stable power to both lamps
   - Check Bluetooth adapter range and interference

3. **Colors not synchronized:**
   - This is normal - left lamp shows left screen zone, right shows right zone
   - Use "Both Red/Green/Blue" options to test synchronized colors
   - Check monitor selection (option 12) for proper screen capture

### Monitor and Display Issues

1. **4K Display not detected properly:**
   - The system auto-detects 4K scaling (100%, 150%, 200%)
   - Only actual 4K displays are flagged as 4K
   - Check monitor selection menu for proper resolution display

2. **Screen capture not working:**
   - On Windows: May require running as administrator
   - On macOS: Grant screen recording permissions in System Preferences > Security & Privacy
   - On Linux: Ensure X11 or Wayland screen access
   - For multiple monitors: Use monitor selection (option 12)

3. **Colors appear wrong:**
   - Check which monitor is selected for capture
   - Ensure the correct screen content is being captured
   - The system enhances colors for better ambient lighting effect
   - Try different saturation levels (60 FPS vs 120 FPS modes)

### Performance Issues

1. **Ambient lighting lag:**
   - Lower FPS if experiencing lag: Use 60 FPS mode instead of 120 FPS
   - Close unnecessary applications to free up system resources
   - Ensure stable Bluetooth connection to both lamps
   - Check system resources during operation

2. **Exit ambient lighting:**
   - Press 'END' key to gracefully exit ambient mode
   - The LEDs will retain the last color displayed
   - Use turn off options to completely disable lamps

### Advanced Debugging

For dual-lamp development and debugging:

```python
# Test dual-lamp screen capture
python debug_ambilight.py

# Check individual lamp connections
from bt_led_control.dual_lamp import DualLampManager
dual_lamps = DualLampManager()
# ... test individual lamp methods
```

---

## 🎉 Acknowledgments

Built with reverse engineering of the Magic Lantern BLE protocol.  
Uses the excellent [bleak](https://github.com/hbldh/bleak) library for BLE communication.
