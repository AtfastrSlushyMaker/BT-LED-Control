# BT-LED-Control 🎨

Control **Magic Lantern LED lights** via **Bluetooth Low Energy (BLE)** directly from Python.  
This project is an open-source alternative to the official *Magic Lantern* app, providing full programmatic control over your LED devices.

---

## ✨ Features

- 🔗 **Easy BLE Connection** - Automatic device discovery and connection
- 🎨 **Full Color Control** - Set any RGB color (0-255 values)
- 🌈 **Preset Colors** - Red, Green, Blue, White, Purple, Orange, Yellow, Cyan
- 🖥️ **Ambient Screen Lighting** - Real-time screen color matching with advanced color enhancement
- 🖥️ **Multi-Monitor Support** - Choose which monitor to capture for ambient lighting
- 🔍 **Advanced Screen Detection** - Automatic detection of all connected monitors
- 🔧 **Win32 Integration** - Proper capture from monitors with negative coordinates
- ⚡ **High-Performance** - 120+ FPS ambient lighting with ultra-smooth updates
- 🎯 **Smart Color Enhancement** - Intelligent saturation boost while preserving natural color mixes
- ⚡ **Simple API** - Clean, async Python interface
- 🎮 **Interactive Menu** - Command-line interface for manual control
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

This provides a user-friendly interface with all features!

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

### LT22Lamp Class

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

---

## 📁 Project Structure

```
BT-LED-Control/
├── bt_led_control/          # Main package
│   ├── __init__.py         # Package initialization & exports
│   ├── bluetooth.py         # BLE connection management
│   ├── commands.py          # LED command protocols
│   ├── device.py           # High-level device interface (includes ambient lighting)
│   ├── screen_capture.py   # Screen color capture and analysis
│   └── utils.py            # Utility functions
├── led_menu.py             # Interactive control menu
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

- `led_menu.py` - Interactive command-line interface with all features including ambient lighting
- `color_debug_test.py` - Color testing and debugging utilities

### Ambient Lighting Example

```python
import asyncio
from bt_led_control.device import LT22Lamp

async def smart_ambient_lighting():
    """Example of ambient lighting with custom settings."""
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

- Support for more LED models
- Color effects (fade, flash, rainbow)
- Brightness control
- Timer functions
- GUI interface
- Multi-zone ambient lighting
- Custom screen capture regions
- Audio-reactive lighting modes

---

## � License

This project is open source. Feel free to use, modify, and distribute.

---

## 🔍 Troubleshooting

### Connection Issues

1. Make sure LED device is powered on
2. Ensure Bluetooth is enabled on your computer
3. Check that device is in pairing mode
4. Try running as administrator (Windows)

### Device Not Found

1. Verify the device address in `bluetooth.py`
2. Use the built-in scanner to discover available devices:

   ```python
   from bt_led_control.bluetooth import BLEManager
   import asyncio
   
   async def scan():
       ble = BLEManager()
       devices = await ble.scan_for_devices(display=True)  # Shows all discovered devices
   
   asyncio.run(scan())
   ```

3. Update the device address if needed

### Ambient Lighting Issues

1. **Screen capture not working:**
   - On Windows: May require running as administrator
   - On macOS: Grant screen recording permissions in System Preferences > Security & Privacy
   - On Linux: Ensure X11 or Wayland screen access

2. **Performance issues:**
   - Lower FPS if experiencing lag: `await lamp.start_ambient_lighting(fps=60)`
   - Close unnecessary applications to free up system resources
   - Ensure stable Bluetooth connection

3. **Colors appear washed out:**
   - The system automatically enhances colors for better ambient lighting
   - Colors are preserved for natural mixes (whites, cyans, yellows)
   - Single-color dominance is enhanced for vivid lighting

4. **Exit ambient lighting:**
   - Press 'END' key to gracefully exit ambient mode
   - The LED will retain the last color displayed

---

## 🎉 Acknowledgments

Built with reverse engineering of the Magic Lantern BLE protocol.  
Uses the excellent [bleak](https://github.com/hbldh/bleak) library for BLE communication.
