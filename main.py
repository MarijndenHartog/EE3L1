# -*- coding: utf-8 -*-
"""
SpikeAnalysis tool. A tool to analyse neuronal spike activity.

Copyright (C) 2024 Luk Sullock Enzlin

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import sys
from PyQt5.QtWidgets import QApplication
from modules.GUI.GUIMain import Main

#!/usr/bin/env python3
"""
BLE real-time visualiser — pyqtgraph edition
• Shows CH1 or CH2 (Togglable via UI Button)
• Records the active channel to a WAV file (16-bit PCM, mono)
"""

import sys
import asyncio
import struct
import threading
import numpy as np
from bleak import BleakClient, BleakScanner
from buffers.raw_buffer import CircularBuffer
from buffers.proc_buffer import ProcessedBuffer
from core.pipeline import Pipeline
from functools import partial
from settings.settings import CHANNELS, SAMPLE_RATE


# ── Config ────────────────────────────────────────────────────────────────────
DEVICE_NAME        = "grompack"
NUS_SERVICE_UUID   = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
NUS_TX_CHAR_UUID   = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
NUS_RX_CHAR_UUID   = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"

PACKED_BUFFER_SIZE = 80
PACKET_FORMAT      = f"<I{PACKED_BUFFER_SIZE}s"
PACKET_SIZE        = struct.calcsize(PACKET_FORMAT)


# ── BLE callback / async task ─────────────────────────────────────────────────

def on_notify(_handle: int, data: bytearray) -> None:
    if len(data) < PACKET_SIZE:
        return

    _index, packed = struct.unpack_from(PACKET_FORMAT, data)

    samples = []
    for i in range(0, PACKED_BUFFER_SIZE, 3):
        b0 = packed[i]
        b1 = packed[i + 1]
        b2 = packed[i + 2]

        s1 = b0 | ((b1 & 0x0F) << 8)
        s2 = (b1 >> 4) | (b2 << 4)
        s2 &= 0x0FFF

        samples.append((s1, s2))
        
    print(samples)
    pipeline.push_raw(np.asarray(samples, dtype=np.int16))
    
    

async def ble_task() -> None:
    print(f"Scanning for '{DEVICE_NAME}' …")
    device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=10.0)

    if device is None:
        print("[ERROR] device not found")
        return

    print(f"Found {device.name} [{device.address}] — connecting …")

    async with BleakClient(device) as client:
        nus = next((s for s in client.services if s.uuid.lower() == NUS_SERVICE_UUID.lower()), None)
        if not nus:
            print("[ERROR] NUS service not found"); return

        tx = next((c for c in nus.characteristics if c.uuid.lower() == NUS_TX_CHAR_UUID.lower()), None)
        rx = next((c for c in nus.characteristics if c.uuid.lower() == NUS_RX_CHAR_UUID.lower()), None)

        if not tx or not rx:
            print("[ERROR] TX/RX characteristic not found"); return

        print(f"Using TX char at handle {tx.handle}")
        await client.start_notify(tx, on_notify)
        await client.write_gatt_char(rx, b'\x01')

        while True:
            await asyncio.sleep(0.05)

        print("Stopping BLE notifications …")
        await client.stop_notify(tx)

def start_ble_background():
    asyncio.run(ble_task())


def start():
    ble_thread = threading.Thread(target=start_ble_background, daemon=True)
    ble_thread.start()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    ui = Main(pipeline, raw_buffer)
    ui.show()

    app.exec()

    return ui.exitcode


if __name__ == "__main__":
    launch = 1
    raw_buffer = CircularBuffer(SAMPLE_RATE * 5, CHANNELS)
    proc_buffer = ProcessedBuffer(SAMPLE_RATE * 15, CHANNELS)  
    pipeline = Pipeline(raw_buffer, proc_buffer)

    while launch:
        launch = start()
