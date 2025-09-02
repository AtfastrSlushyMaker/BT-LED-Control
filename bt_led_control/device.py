# bt_led_control/device.py

import asyncio
from .bluetooth import BLEManager
from .commands import rgb_command, red, green, blue, white, off


class LT22Lamp:
    """High-level interface for controlling Magic Lantern LED devices."""

    def __init__(self, device_address: str = "BE:28:72:00:39:FD"):
        self.ble = BLEManager(device_address)

    async def connect(self) -> bool:
        """Connect to the LED device."""
        return await self.ble.connect()

    async def disconnect(self) -> bool:
        """Disconnect from the LED device."""
        return await self.ble.disconnect()

    async def set_color(self, red: int, green: int, blue: int) -> bool:
        """Set the LED to a specific RGB color."""
        command = rgb_command(red, green, blue)
        return await self.ble.send_command(command)

    async def turn_red(self) -> bool:
        command = red()
        return await self.ble.send_command(command)

    async def turn_green(self) -> bool:
        command = green()
        return await self.ble.send_command(command)

    async def turn_blue(self) -> bool:
        command = blue()
        return await self.ble.send_command(command)

    async def turn_white(self) -> bool:
        command = white()
        return await self.ble.send_command(command)

    async def turn_off(self) -> bool:
        command = off()
        return await self.ble.send_command(command)
