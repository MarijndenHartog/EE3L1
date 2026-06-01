import asyncio
import struct
import threading

import numpy as np
from bleak import BleakClient, BleakScanner

from workers.datasource.source_abstraction import (
    DataSource,
    SourceState
)


class BLESource(threading.Thread, DataSource):

    DEVICE_NAME = "grompack"

    NUS_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
    NUS_RX_UUID      = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
    NUS_TX_UUID      = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

    PACKED_BUFFER_SIZE = 240

    PACKET_FORMAT = f"<I{PACKED_BUFFER_SIZE}s"
    PACKET_SIZE = struct.calcsize(PACKET_FORMAT)
    
    def __init__(
        self,
        pipeline,
        channels=2
    ):
        super().__init__(daemon=True)

        self.pipeline = pipeline

        self.channels = channels

        self._running = False
        self._streaming = False

        self.ack_start = threading.Event()
        self.ack_stop = threading.Event()

        self.state = SourceState.DISCONNECTED

        self.client = None
        
        
    def cmd_start(self):

        self._streaming = True
        self.state = SourceState.STREAMING

        if self.client and self.client.is_connected:
            asyncio.run_coroutine_threadsafe(
                self.client.write_gatt_char(self.NUS_RX_UUID, b'\x01'),
                asyncio.get_event_loop()
            )

        self.ack_start.set()


    def cmd_stop(self):

        self._streaming = False
        self.state = SourceState.READY

        if self.client and self.client.is_connected:
            asyncio.run_coroutine_threadsafe(
                self.client.write_gatt_char(self.NUS_RX_UUID, b'\x02'),
                asyncio.get_event_loop()
            )

        self.ack_stop.set()
        
        
    def _decode_packet(self, data):

        if len(data) < self.PACKET_SIZE:
            return None

        _, packed = struct.unpack_from(
            self.PACKET_FORMAT,
            data
        )

        samples = []
        for i in range(0, self.PACKED_BUFFER_SIZE, 3):
            b0, b1, b2 = packed[i], packed[i+1], packed[i+2]

            sample1 = b0 | ((b1 & 0x0F) << 8)
            sample2 = (b1 >> 4) | (b2 << 4)
            sample2 &= 0x0FFF

            samples.append((sample1, sample2))

        return np.asarray(samples, dtype=np.int16)
    
    def _on_notify(self, handle, data):

        if not self._streaming:
            return

        packet = self._decode_packet(data)

        if packet is None:
            return

        self.pipeline.push_raw(packet)
        
    async def _ble_loop(self):

        self.state = SourceState.CONNECTING

        device = await BleakScanner.find_device_by_name(
            self.DEVICE_NAME,
            timeout=10.0
        )

        if device is None:
            raise RuntimeError(
                "BLE device not found"
            )

        self.client = BleakClient(device)

        await self.client.connect()

        self.state = SourceState.READY

        await self.client.start_notify(
            self.NUS_TX_UUID,
            self._on_notify
        )

        while self._running:
            await asyncio.sleep(0.1)

        await self.client.stop_notify(
            self.NUS_TX_UUID
        )

        await self.client.disconnect()
        
        
    # =========================================================
    # THREAD CONTROL
    # =========================================================
    def start(self):

        if self.is_alive():
            return

        super().start()

    def stop(self):

        self._streaming = False
        self._running = False

        self.state = SourceState.DISCONNECTED