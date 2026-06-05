import struct
import threading

import numpy as np
from bleak import BleakClient, BleakScanner

import asyncio
import threading

import asyncio
import threading


class BLEThreadWrapper:
    def __init__(self, ble_source):
        self.ble = ble_source
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start(self):
        self.thread.start()

    def run(self, coro):
        """Submit coroutine to BLE asyncio loop"""
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

class BLESource:
    NUS_RX_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
    NUS_TX_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

    CMD_START = 0x01
    CMD_STOP = 0x02
    CMD_BURST = 0x03

    PACKED_BUFFER_SIZE = 240
    PACKET_FORMAT = f"<I{PACKED_BUFFER_SIZE}s"
    PACKET_SIZE = struct.calcsize(PACKET_FORMAT)

    def __init__(self, pipeline=None):
        self.pipeline = pipeline

        self.client = None
        self.device = None

        self._streaming = False
        self._lock = threading.Lock()

    async def connect(self, device):
        """
        Connect to a BLE device.

        Parameters
        ----------
        device : str | BLEDevice
            Address or Bleak BLEDevice.
        """
        self.device = device
        self.client = BleakClient(device)

        await self.client.connect()

        print(f"[BLE] Connected to {device}")

    async def disconnect(self):
        """
        Stop streaming and disconnect.
        """
        if self.client is None:
            return

        try:
            await self.cmd_stop()
        except Exception:
            pass

        if self.client.is_connected:
            await self.client.disconnect()

        print("[BLE] Disconnected")

    async def cmd_start(self):
        """
        Send start streaming command (0x01).
        """
        if self.client is None:
            raise RuntimeError("BLE device not connected")

        if not self._streaming:
            await self.client.start_notify(
                self.NUS_TX_CHAR_UUID,
                self._notification_handler,
            )
            self._streaming = True

        await self.client.write_gatt_char(
            self.NUS_RX_CHAR_UUID,
            bytes([self.CMD_START]),
        )

        print("[BLE] Streaming started")

    async def cmd_stop(self):
        """
        Send stop streaming command (0x02).
        """
        if self.client is None:
            return

        await self.client.write_gatt_char(
            self.NUS_RX_CHAR_UUID,
            bytes([self.CMD_STOP]),
        )

        with self._lock:
            if self._streaming:
                try:
                    await self.client.stop_notify(self.NUS_TX_CHAR_UUID)
                except Exception:
                    pass

                self._streaming = False

        print("[BLE] Streaming stopped")

    async def cmd_burst(self, duration_ms, frequency_hz):
        """
        Send burst command (0x03).

        Payload:
            [0x03][duration_ms:uint16][frequency_hz:uint16]
        """
        if self.client is None:
            raise RuntimeError("BLE device not connected")

        payload = struct.pack(
            "<BHH",
            self.CMD_BURST,
            int(duration_ms),
            int(frequency_hz),
        )

        await self.client.write_gatt_char(
            self.NUS_RX_CHAR_UUID,
            payload,
        )

        print(
            f"[BLE] Burst command: duration={duration_ms} ms, "
            f"frequency={frequency_hz} Hz"
        )

    def _notification_handler(self, sender, data):
        """
        Called by Bleak whenever a packet is received.
        """
        if not self._streaming:
            return

        packet = self._decode_packet(data)

        if packet is not None:
            #self.pipeline.push_raw(packet)
            print(packet)

    def _decode_packet(self, data):

        if len(data) < self.PACKET_SIZE:
            return None

        try:
            _, packed = struct.unpack_from(self.PACKET_FORMAT, data)
        except Exception as e:
            print("[BLE] unpack error:", e)
            return None

        samples = []

        for i in range(0, min(len(packed), self.PACKED_BUFFER_SIZE), 3):
            b0 = packed[i]
            b1 = packed[i + 1]
            b2 = packed[i + 2]

            s1 = b0 | ((b1 & 0x0F) << 8)
            s2 = (b1 >> 4) | (b2 << 4)
            s2 &= 0x0FFF

            samples.append((s1, s2))

        out = np.asarray(samples, dtype=np.int16)

        print(f"[BLE] decoded samples: {len(out)}")
        return out
    
    async def find_device(self, name: str):
        return await BleakScanner.find_device_by_name(name, timeout=10.0)
    
    



    
    