import asyncio
import struct
import threading
import numpy as np
from bleak import BleakClient, BleakScanner
from workers.datasource.source_abstraction import DataSource, SourceState


class BLESource(threading.Thread, DataSource):

    DEVICE_NAME = "grompack"

    NUS_TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
    NUS_RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
    NUS_SERVICE_UUID  = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"

    PACKED_BUFFER_SIZE = 240
    PACKET_FORMAT = f"<I{PACKED_BUFFER_SIZE}s"
    PACKET_SIZE = struct.calcsize(PACKET_FORMAT)

    def __init__(self, pipeline, channels=2):
        super().__init__(daemon=True)

        self.pipeline = pipeline

        # lifecycle (thread NEVER stops)
        self._running = True

        # streaming control (toggle only)
        self._streaming = False

        # asyncio runtime
        self.loop = None
        self.client = None

        # sync
        self.ack_start = threading.Event()
        self.ack_stop = threading.Event()
        self.connected = threading.Event()

        self.state = SourceState.DISCONNECTED

        print("BLESource (persistent) initialized")

    # =========================================================
    # COMMANDS
    # =========================================================
    def cmd_start(self):
        print("BLESource: START")

        self.connected.wait(timeout=10.0)

        self._streaming = True
        self.state = SourceState.STREAMING

        if self.loop and self.client:
            future = asyncio.run_coroutine_threadsafe(
                self.client.write_gatt_char(self.rx_char, b"\x01"),
                self.loop
            )
            try:
                # 2 second timeout to catch immediate write errors without freezing the thread
                future.result(timeout=2.0) 
            except Exception as e:
                print(f"[ERROR] Failed to send START command: {e}")

        self.ack_start.set()

    def cmd_stop(self):
        print("BLESource: STOP")

        self._streaming = False
        self.state = SourceState.READY

        if self.loop and self.client:
            future = asyncio.run_coroutine_threadsafe(
                self.client.write_gatt_char(self.rx_char, b"\x02"),
                self.loop
            )
            try:
                future.result(timeout=2.0)
            except Exception as e:
                print(f"[ERROR] Failed to send STOP command: {e}")

        self.ack_stop.set()

    def cmd_burst(self, duration_ms, frequency_hz):
        print("BLESource: STIMULATE BURST")

        self._streaming = False
        self.state = SourceState.READY

        payload = struct.pack("<BII", 0x05, duration_ms, frequency_hz)

        if self.loop and self.client:
            future = asyncio.run_coroutine_threadsafe(
                self.client.write_gatt_char(self.rx_char, payload),
                self.loop
            )
            try:
                future.result(timeout=2.0)
            except Exception as e:
                print(f"[ERROR] Failed to send STIMULATE BURST command: {e}")

        self.ack_stop.set()
        
    def cmd_stimulate_start(self):
        print("BLESource: STIMULATE START")

        self._streaming = False
        self.state = SourceState.READY

        if self.loop and self.client:
            future = asyncio.run_coroutine_threadsafe(
                self.client.write_gatt_char(self.rx_char, b"\x03"),
                self.loop
            )
            try:
                future.result(timeout=2.0)
            except Exception as e:
                print(f"[ERROR] Failed to send STIMULATE START command: {e}")

        self.ack_stop.set()
        
    def cmd_stimulate_stop(self):
        print("BLESource: STIMULATE STOP")

        self._streaming = False
        self.state = SourceState.READY

        if self.loop and self.client:
            future = asyncio.run_coroutine_threadsafe(
                self.client.write_gatt_char(self.rx_char, b"\x04"),
                self.loop
            )
            try:
                future.result(timeout=2.0)
            except Exception as e:
                print(f"[ERROR] Failed to send STIMULATE STOP command: {e}")

        self.ack_stop.set()
        
    # =========================================================
    # DECODER
    # =========================================================
    def _decode_packet(self, data):
        if len(data) < self.PACKET_SIZE:
            return None

        _, packed = struct.unpack_from(self.PACKET_FORMAT, data)

        samples = []
        for i in range(0, self.PACKED_BUFFER_SIZE, 3):
            b0 = packed[i]
            b1 = packed[i + 1]
            b2 = packed[i + 2]

            s1 = b0 | ((b1 & 0x0F) << 8)
            s2 = (b1 >> 4) | (b2 << 4)
            s2 &= 0x0FFF

            samples.append((s1, s2))

        return np.asarray(samples, dtype=np.int16)

    # =========================================================
    # CALLBACK
    # =========================================================
    def _on_notify(self, handle, data):

        if not self._streaming:
            print("Received BLE packet while not streaming, ignoring")
            return

        packet = self._decode_packet(data)

        if packet is None:
            return

        self.pipeline.push_raw(packet)

    # =========================================================
    # BLE LIFECYCLE (RUNS ONCE, FOREVER)
    # =========================================================
    async def _ble_loop(self):

        self.state = SourceState.CONNECTING
        print("Scanning BLE devices...")

        device = await BleakScanner.find_device_by_name(
            self.DEVICE_NAME,
            timeout=10.0
        )

        if device is None:
            self.state = SourceState.ERROR
            raise RuntimeError("BLE device not found")

        print(f"Found {device.name}")
        self.state = SourceState.CONNECTING

        # FIX 1: Pass the device object, not device.address
        async with BleakClient(device) as client:

            self.client = client
            print("BLE connected")

            # FIX 2: Do NOT set self.connected.set() here yet!
            # await client.get_services()

            nus_service = next(
                (s for s in client.services if s.uuid.lower() == self.NUS_SERVICE_UUID.lower()),
                None
            )

            if not nus_service:
                self.state = SourceState.ERROR
                print("[ERROR] NUS service not found")
                return

            tx_char = next(
                (c for c in nus_service.characteristics
                if c.uuid.lower() == self.NUS_TX_UUID.lower()),
                None
            )

            # FIX 3: Explicitly resolve and save the RX characteristic 
            self.rx_char = next(
                (c for c in nus_service.characteristics
                if c.uuid.lower() == self.NUS_RX_UUID.lower()),
                None
            )

            if not tx_char or not self.rx_char:
                self.state = SourceState.ERROR
                print("[ERROR] TX or RX characteristic not found")
                return

            print(f"Using TX char at handle {tx_char.handle}")
            await client.start_notify(tx_char, self._on_notify)
            print("Subscribed. Streaming ...\n")
            
            # FIX 4: Set the connected flag ONLY when everything is truly ready
            self.state = SourceState.READY
            self.connected.set()

            try:
                while self._running:
                    await asyncio.sleep(0.1)
            finally:
                print("Stopping BLE...")
                try:
                    await client.stop_notify(tx_char)
                except Exception:
                    pass
                self.state = SourceState.DISCONNECTED

    # =========================================================
    # THREAD ENTRY (RUN ONCE ONLY)
    # =========================================================
    def run(self):

        print("BLESource thread started")

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.loop.run_until_complete(self._ble_loop())

    # =========================================================
    # THREAD START (ONLY ONCE EVER)
    # =========================================================
    def start(self):
        if self.is_alive():
            return
        super().start()

    # =========================================================
    # STOP = ONLY STOPS STREAM, NOT THREAD
    # =========================================================
    def stop(self):
        print("BLESource STOP (soft)")

        self.cmd_stop()

        self._running = False
        self.state = SourceState.DISCONNECTED
        
        
        
"""
async def _ble_loop(self):

        self.state = SourceState.CONNECTING
        print("Scanning BLE devices...")

        device = await BleakScanner.find_device_by_name(
            self.DEVICE_NAME,
            timeout=10.0
        )

        if device is None:
            self.state = SourceState.ERROR
            raise RuntimeError("BLE device not found")

        print(f"Found {device.name}")
        self.state = SourceState.CONNECTING

        # FIX 1: Pass the device object, not device.address
        async with BleakClient(device) as client:

            self.client = client
            print("BLE connected")

            # FIX 2: Do NOT set self.connected.set() here yet!
            # await client.get_services()

            nus_service = next(
                (s for s in client.services if s.uuid.lower() == self.NUS_SERVICE_UUID.lower()),
                None
            )

            if not nus_service:
                self.state = SourceState.ERROR
                print("[ERROR] NUS service not found")
                return

            tx_char = next(
                (c for c in nus_service.characteristics
                if c.uuid.lower() == self.NUS_TX_UUID.lower()),
                None
            )

            # FIX 3: Explicitly resolve and save the RX characteristic 
            self.rx_char = next(
                (c for c in nus_service.characteristics
                if c.uuid.lower() == self.NUS_RX_UUID.lower()),
                None
            )

            if not tx_char or not self.rx_char:
                self.state = SourceState.ERROR
                print("[ERROR] TX or RX characteristic not found")
                return

            print(f"Using TX char at handle {tx_char.handle}")
            await client.start_notify(tx_char, self._on_notify)
            print("Subscribed. Streaming ...\n")
            
            # FIX 4: Set the connected flag ONLY when everything is truly ready
            self.state = SourceState.READY
            self.connected.set()

            try:
                while self._running:
                    await asyncio.sleep(0.1)
            finally:
                print("Stopping BLE...")
                try:
                    await client.stop_notify(tx_char)
                except Exception:
                    pass
                self.state = SourceState.DISCONNECTED

    # =========================================================
    # THREAD ENTRY (RUN ONCE ONLY)
    # =========================================================
    def run(self):

        print("BLESource thread started")

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.loop.run_until_complete(self._ble_loop())

"""