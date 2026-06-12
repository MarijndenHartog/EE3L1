"""
BLE client voor de Grompack microcontroller.
Stuurt 0x01 om streaming te starten en print ontvangen datapakketten.

Vereisten:
    pip install bleak
"""

import asyncio
import struct
import sys

from bleak import BleakClient, BleakScanner

# ── Constanten ──────────────────────────────────────────────────────────────
DEVICE_NAME        = "grompack"
NUS_SERVICE_UUID   = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
NUS_TX_CHAR_UUID   = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"  # device → host
NUS_RX_CHAR_UUID   = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # host → device

PACKED_BUFFER_SIZE = 240
PACKET_FORMAT      = f"<I{PACKED_BUFFER_SIZE}s"
PACKET_SIZE        = struct.calcsize(PACKET_FORMAT)

MAX_POINTS         = 10000   # rolling window (samples)
SAMPLE_RATE        = 12500   # Hz
MAX_REC_SECONDS    = 100     # harde grens opname

# ── Globale toestand ─────────────────────────────────────────────────────────
received_samples: list[bytes] = []
packet_count = 0
disconnected_event = asyncio.Event()


def on_disconnect(client: BleakClient) -> None:
    print("[WARN] BLE verbinding verbroken!")
    disconnected_event.set()


def handle_notification(sender, data: bytearray) -> None:
    """Callback voor elk BLE-notificatiepakket van de microcontroller."""
    global packet_count

    if len(data) < PACKET_SIZE:
        print(f"[WARN] Kort pakket ontvangen: {len(data)} bytes (verwacht {PACKET_SIZE})")
        return

    # Uitpakken: uint32 teller + 240 bytes ruwe buffer
    counter, raw_buffer = struct.unpack_from(PACKET_FORMAT, data)
    packet_count += 1

    print(
        f"[PKT #{packet_count:>6}]  counter={counter:>10}  "
        f"buffer={raw_buffer[:8].hex()}…  ({len(raw_buffer)} bytes)"
    )

    received_samples.extend(raw_buffer)
    if len(received_samples) > MAX_POINTS:
        del received_samples[: len(received_samples) - MAX_POINTS]


async def scan_for_device(timeout: float = 10.0):
    """Scan naar het Grompack-apparaat en geef het BLE-apparaat terug."""
    print(f"Scannen naar '{DEVICE_NAME}' (timeout {timeout}s)…")
    device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=timeout)
    if device is None:
        print(f"[ERROR] Apparaat '{DEVICE_NAME}' niet gevonden.")
        sys.exit(1)
    print(f"Gevonden: {device.name}  [{device.address}]")
    return device


async def connect_with_retry(address: str, retries: int = 3) -> BleakClient:
    """Maak een BleakClient aan en verbind, met retry bij mislukking."""
    for attempt in range(1, retries + 1):
        print(f"Verbindingspoging {attempt}/{retries}…")
        client = BleakClient(
            address,
            timeout=20.0,                          # langere GATT-timeout
            disconnected_callback=on_disconnect,
            winrt={"use_cached_services": False},  # forceer verse service discovery op Windows
        )
        try:
            await client.connect()
            if client.is_connected:
                print(f"Verbonden! (poging {attempt})")
                return client
        except Exception as e:
            print(f"[WARN] Poging {attempt} mislukt: {e}")
            try:
                await client.disconnect()
            except Exception:
                pass
        await asyncio.sleep(2.0)

    print("[ERROR] Kon niet verbinden na alle pogingen.")
    sys.exit(1)


async def run() -> None:
    global disconnected_event
    disconnected_event = asyncio.Event()

    device = await scan_for_device()
    client = await connect_with_retry(device.address)

    try:
        # Geef Windows BLE-stack tijd om services volledig te resolven
        await asyncio.sleep(2.0)

        if not client.is_connected:
            print("[ERROR] Verbinding verloren na sleep.")
            return

        # Zoek de NUS-service op
        nus_service = next(
            (s for s in client.services if s.uuid.lower() == NUS_SERVICE_UUID.lower()),
            None,
        )
        if nus_service is None:
            print("[ERROR] NUS-service niet gevonden op dit apparaat.")
            print("Beschikbare services:")
            for s in client.services:
                print(f"  {s.uuid}")
            return

        # Haal TX en RX characteristics op via de service
        tx_char = next(
            (c for c in nus_service.characteristics if c.uuid.lower() == NUS_TX_CHAR_UUID.lower()),
            None,
        )
        rx_char = next(
            (c for c in nus_service.characteristics if c.uuid.lower() == NUS_RX_CHAR_UUID.lower()),
            None,
        )

        if tx_char is None or rx_char is None:
            print("[ERROR] TX of RX characteristic niet gevonden in de NUS-service.")
            return

        print(f"TX handle: {tx_char.handle}  RX handle: {rx_char.handle}")

        # Notificaties inschakelen met retry
        for attempt in range(1, 4):
            try:
                await client.start_notify(tx_char.handle, handle_notification)
                print("Notificaties ingeschakeld.")
                break
            except Exception as e:
                print(f"[WARN] start_notify poging {attempt} mislukt: {e}")
                if attempt == 3:
                    print("[ERROR] Kon notificaties niet inschakelen.")
                    return
                await asyncio.sleep(1.5)

        # Stuur 0x01 → start streaming
        await client.write_gatt_char(rx_char.handle, bytes([0x01]), response=False)
        print("Start-commando (0x01) verstuurd. Wachten op data…\n")

        # Wacht tot tijdslimiet OF verbindingsverlies
        try:
            done, _ = await asyncio.wait(
                [
                    asyncio.create_task(asyncio.sleep(MAX_REC_SECONDS)),
                    asyncio.create_task(disconnected_event.wait()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
        except asyncio.CancelledError:
            pass

        # Stop streaming
        if client.is_connected:
            try:
                await client.write_gatt_char(rx_char.handle, bytes([0x00]), response=False)
                print("\nStop-commando (0x00) verstuurd.")
            except Exception:
                pass
            try:
                await client.stop_notify(tx_char.handle)
            except Exception:
                pass

    finally:
        try:
            await client.disconnect()
        except Exception:
            pass

    print(f"\nKlaar. Totaal ontvangen pakketten : {packet_count}")
    print(f"Samples in rollend venster       : {len(received_samples)}")


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nAfgebroken door gebruiker.")