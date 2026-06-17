
import asyncio
import struct
import threading
import numpy as np
from bleak import BleakClient, BleakScanner
from buffers.raw_buffer import raw_buf
from settings.states import command_queue
from settings.settings import (
    DEVICE_NAME,
    NUS_SERVICE_UUID,
    NUS_TX_CHAR_UUID,
    NUS_RX_CHAR_UUID,
    PACKED_BUFFER_SIZE
    )

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

    data = np.asarray(samples, dtype=np.int16)
    raw_buf.write(data)

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
        
        while True:
            cmd_msg = command_queue.get()
            cmd = cmd_msg["cmd"]

            if cmd == 0x01:
                await client.write_gatt_char(rx, b'\x01')

            elif cmd == 0x02:
                await client.write_gatt_char(rx, b'\x02')

            elif cmd == 0x03:
                dur = cmd_msg.get("time")
                freq = cmd_msg.get("freq")
                print("STIMULATE", dur, freq)
                
                payload = bytes([
                    0x03,
                    dur  & 0xFF, (dur  >> 8) & 0xFF,
                    freq & 0xFF, (freq >> 8) & 0xFF,
                ])
                await client.write_gatt_char(rx, payload)
                           
async def test():
    while True:
        cmd_msg = command_queue.get()
        cmd = cmd_msg["cmd"]

        if cmd == 0x01:
            print("START")

        elif cmd == 0x02:
            print("STOP")

        elif cmd == 0x03:
            dur = cmd_msg.get("time")
            freq = cmd_msg.get("freq")
            print("STIMULATE", dur, freq)
    

def start_ble_background(): 
    #asyncio.run(ble_task())
    asyncio.run(test())


# ── Entry point ───────────────────────────────────────────────────────────────

def ble_fix():
    ble_thread = threading.Thread(target=start_ble_background, daemon=True)
    ble_thread.start()

