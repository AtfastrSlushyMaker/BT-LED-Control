import asyncio
from typing import Optional, List
from bleak import BleakClient, BleakScanner, BLEDevice


class BLEManager:
    """Manages BLE connections for Magic Lantern LED devices."""

    # Magic Lantern command characteristic UUID
    COMMAND_CHAR_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"

    def __init__(self, device_address: str = "BE:28:72:00:39:FD"):
        self.device_address = device_address
        self.client: Optional[BleakClient] = None

    async def scan_for_devices(
        self, timeout: float = 1.0, display: bool = False
    ) -> List[BLEDevice]:
        """Scan for nearby BLE devices."""
        devices = await BleakScanner.discover(timeout=timeout)
        if display:
            for device in devices:
                print(
                    f"Found device: {device.name or 'Unknown Device'} ({device.address})"
                )
        return devices

    async def find_device(self, timeout: float = 5.0) -> Optional[BLEDevice]:
        """Find the target device by address."""
        devices = await self.scan_for_devices(timeout=timeout)

        for device in devices:
            if device.address == self.device_address:
                return device
        return None

    async def connect(self) -> bool:
        """Connect to the target device."""
        if self.is_connected():
            return True

        device = await self.find_device()
        if not device:
            return False

        try:
            self.client = BleakClient(device.address)
            await self.client.connect()
            return self.client.is_connected
        except Exception:
            self.client = None
            return False

    async def disconnect(self) -> bool:
        """Disconnect from device."""
        if not self.is_connected():
            return True

        try:
            await self.client.disconnect()
            self.client = None
            return True
        except Exception:
            return False

    def is_connected(self) -> bool:
        """Check if connected to device."""
        return self.client is not None and self.client.is_connected

    async def send_command(self, command: List[int]) -> bool:
        """Send command to LED device."""
        if not self.is_connected():
            return False

        try:
            await self.client.write_gatt_char(self.COMMAND_CHAR_UUID, bytes(command))
            return True
        except Exception:
            return False
