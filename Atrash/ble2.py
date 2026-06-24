import asyncio
import threading
import struct
import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Optional, List

from bleak import BleakClient, BleakScanner


# =========================
# BLE UUIDs (Nordic UART Service)
# =========================
NUS_RX_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
NUS_TX_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
NUS_SERVICE_UUID  = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"


# =========================
# Packet configuration
# =========================
PACKED_BUFFER_SIZE = 240
PACKET_FORMAT = f"<I{PACKED_BUFFER_SIZE}s"


# =========================
# Device state
# =========================
class DeviceState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    STREAMING = "streaming"


# =========================
# BLE device model
# =========================
@dataclass
class BLEDeviceInfo:
    name: str
    address: str


# =========================
# BLE Client
# =========================
class BLESource:
    def __init__(self, pipeline, debug: bool = False):
        self.pipeline = pipeline
        self.debug = debug

        self._client: Optional[BleakClient] = None
        self._device = None

        self.state = DeviceState.DISCONNECTED

        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)

        self._data_callback: Optional[Callable[[np.ndarray], None]] = None
        self._state_callback: Optional[Callable[[DeviceState], None]] = None

        self._lock = threading.Lock()

        self.last_packet_header = None

        self._thread.start()

    # =========================
    # Public callbacks
    # =========================
    def set_data_callback(self, callback: Callable[[np.ndarray], None]):
        self._data_callback = callback

    def set_state_callback(self, callback: Callable[[DeviceState], None]):
        self._state_callback = callback

    # =========================
    # Async loop
    # =========================
    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    # =========================
    # DEVICE SCANNING (GUI)
    # =========================
    async def scan_devices(self, timeout: float = 3.0) -> List[BLEDeviceInfo]:
        devices = await BleakScanner.discover(timeout=timeout)

        results = []
        for d in devices:
            if d.name:
                results.append(BLEDeviceInfo(
                    name=d.name,
                    address=d.address
                ))

        return results

    def scan_devices_sync(self, timeout: float = 3.0):
        return asyncio.run_coroutine_threadsafe(
            self.scan_devices(timeout),
            self._loop
        ).result()

    # =========================
    # CONNECTION (by address)
    # =========================
    def connect_to_address(self, address: str):
        asyncio.run_coroutine_threadsafe(
            self._connect_by_address(address),
            self._loop
        )


    async def _connect_by_address(self, address: str):
        self._set_state(DeviceState.CONNECTING)

        try:
            # Direct verbinden op adres — geen scan nodig, stabieler op Windows
            self._client = BleakClient(address)
            await self._client.connect()

            if not self._client.is_connected:
                if self.debug:
                    print("[BLE] Failed to connect")
                self._set_state(DeviceState.DISCONNECTED)
                return

            # Zoek de NUS service
            nus_service = next(
                (s for s in self._client.services if s.uuid.lower() == NUS_SERVICE_UUID.lower()),
                None
            )
            if not nus_service:
                if self.debug:
                    print("[BLE] NUS service not found")
                await self._client.disconnect()
                self._set_state(DeviceState.DISCONNECTED)
                return

            # Zoek TX en RX characteristics
            self.tx_char = next(
                (c for c in nus_service.characteristics if c.uuid.lower() == NUS_TX_CHAR_UUID.lower()),
                None
            )
            self.rx_char = next(
                (c for c in nus_service.characteristics if c.uuid.lower() == NUS_RX_CHAR_UUID.lower()),
                None
            )

            if not self.tx_char or not self.rx_char:
                if self.debug:
                    print("[BLE] TX or RX characteristic not found")
                await self._client.disconnect()
                self._set_state(DeviceState.DISCONNECTED)
                return

            await self._client.start_notify(self.tx_char, self._notification_handler)

            self._set_state(DeviceState.CONNECTED)

            if self.debug:
                print(f"[BLE] Connected to {address}")

        except Exception as e:
            if self.debug:
                print(f"[BLE] Connection error: {e}")
            self._set_state(DeviceState.DISCONNECTED)

    # =========================
    # DISCONNECT
    # =========================
    def disconnect(self):
        asyncio.run_coroutine_threadsafe(
            self._disconnect(),
            self._loop
        )

    async def _disconnect(self):
        if self._client and self._client.is_connected:
            try:
                await self._client.stop_notify(self.tx_char)
                await self._client.disconnect()
            except Exception as e:
                if self.debug:
                    print("[BLE] disconnect error:", e)

        self._set_state(DeviceState.DISCONNECTED)

    # =========================
    # SWITCH DEVICE
    # =========================
    def switch_device(self, address: str):
        asyncio.run_coroutine_threadsafe(
            self._switch_device(address),
            self._loop
        )

    async def _switch_device(self, address: str):
        await self._disconnect()
        await self._connect_by_address(address)

    # =========================
    # COMMANDS
    # =========================
    def start_stream(self):
        self._write_cmd(b"\x01")

    def stop_stream(self):
        self._write_cmd(b"\x02")

    def stimulate(self, frequency_hz: float, duration_ms: int):
        cmd = bytes([
            0x03,
            int(frequency_hz) & 0xFF,
            (int(frequency_hz) >> 8) & 0xFF,
            duration_ms & 0xFF,
            (duration_ms >> 8) & 0xFF
        ])
        self._write_cmd(cmd)

    def _write_cmd(self, data: bytes):
        asyncio.run_coroutine_threadsafe(
            self._write(data),
            self._loop
        )

    async def _write(self, data: bytes):
        if not self._client or not self._client.is_connected:
            return

        try:
            await self._client.write_gatt_char(self.rx_char.uuid, data)
        except Exception as e:
            if self.debug:
                print("[BLE] write error:", e)

    # =========================
    # NOTIFICATIONS
    # =========================
    def _notification_handler(self, handle: int, data: bytes):
        print("not")
        try:
            decoded = self._decode_packet(data)

            if decoded is not None:
                if self.debug:
                    print(decoded)
                else: 
                    self.pipeline.push_raw(decoded)

                if self._data_callback:
                    self._data_callback(decoded)

        except Exception as e:
            if self.debug:
                print("[BLE] notification error:", e)

    # =========================
    # PACKET DECODER
    # =========================
    def _decode_packet(self, data):
        expected_size = struct.calcsize(PACKET_FORMAT)

        if data is None or len(data) < expected_size:
            return None

        try:
            header, packed = struct.unpack_from(PACKET_FORMAT, data)
        except Exception as e:
            if self.debug:
                print("[BLE] unpack error:", e)
            return None

        self.last_packet_header = header

        max_len = (len(packed) // 3) * 3
        if max_len == 0:
            return None

        samples = np.empty((max_len // 3, 2), dtype=np.int16)

        idx = 0
        for i in range(0, max_len, 3):
            b0 = packed[i]
            b1 = packed[i + 1]
            b2 = packed[i + 2]

            s1 = b0 | ((b1 & 0x0F) << 8)
            s2 = (b1 >> 4) | (b2 << 4)
            s2 &= 0x0FFF

            samples[idx, 0] = s1
            samples[idx, 1] = s2
            idx += 1

        if self.debug:
            print(f"[BLE] header={header}, samples={len(samples)}")

        return samples

    # =========================
    # STATE MANAGEMENT
    # =========================
    def get_state(self) -> DeviceState:
        return self.state

    def _set_state(self, new_state: DeviceState):
        with self._lock:
            self.state = new_state

        if self._state_callback:
            self._state_callback(new_state)
            
            
if __name__ == "__main__":
    import time

    ble = BLESource(pipeline="pipeline", debug=True)

    # 1. scan devices
    devices = ble.scan_devices_sync()

    for d in devices:
        print(d.name, d.address)
    
    target = next(
    (d for d in devices if d.name == "grompack" and d.address == "E1:66:FD:A9:7F:D8"),
    None
)

    # 2. connect to first device
    ble.connect_to_address(target.address)

    time.sleep(5)

    # 3. start streaming
    ble.start_stream()

    time.sleep(5)

    # 4. stimulation command
    ble.stimulate(20, 500)

    time.sleep(2)

    # 5. stop streaming
    ble.stop_stream()

    # 6. disconnect
    ble.disconnect()
    
