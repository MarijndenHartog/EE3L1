
import asyncio
import struct
import sys
import threading
import time
from typing import Callable
 
from bleak import BleakClient, BleakScanner
 
# ── Constanten ───────────────────────────────────────────────────────────────
DEVICE_NAME        = "grompack"
NUS_SERVICE_UUID   = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
NUS_TX_CHAR_UUID   = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"  # device → host
NUS_RX_CHAR_UUID   = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # host → device
 
PACKED_BUFFER_SIZE = 240
PACKET_FORMAT      = f"<I{PACKED_BUFFER_SIZE}s"
PACKET_SIZE        = struct.calcsize(PACKET_FORMAT)
 
MAX_POINTS         = 10000
SAMPLE_RATE        = 12500
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Async kern
# ─────────────────────────────────────────────────────────────────────────────
 
class GrompackBLE:
    """
    Pure async BLE client voor de Grompack microcontroller.
 
    Gebruik:
        grom = GrompackBLE(on_data=mijn_callback)
        await grom.connect()
        await grom.start_stream()   # stuurt 0x01
        ...
        await grom.stop_stream()    # stuurt 0x02
        await grom.disconnect()
 
    on_data(counter: int, raw: bytes) wordt aangeroepen voor elk ontvangen pakket.
    """
 
    def __init__(self, on_data: Callable[[int, bytes], None] | None = None) -> None:
        self._client: BleakClient | None = None
        self._tx_handle: int | None = None
        self._rx_handle: int | None = None
        self._disconnected = asyncio.Event()
        self._on_data = on_data
 
        self.packet_count: int = 0
        self.samples: list[int] = []
 
    # ── Verbinding ────────────────────────────────────────────────────────────
 
    async def connect(self, retries: int = 3) -> None:
        """Scan naar het apparaat en verbind met retry-logica."""
        device = await self._scan()
 
        for attempt in range(1, retries + 1):
            print(f"Verbindingspoging {attempt}/{retries}…")
            client = BleakClient(
                device.address,
                timeout=20.0,
                disconnected_callback=self._on_disconnect,
                winrt={"use_cached_services": False},
            )
            try:
                await client.connect()
                if client.is_connected:
                    self._client = client
                    print(f"Verbonden met {device.name}  [{device.address}]")
                    await asyncio.sleep(2.0)        # Windows BLE-stack stabiliseren
                    await self._resolve_characteristics()
                    return
            except Exception as e:
                print(f"[WARN] Poging {attempt} mislukt: {e}")
                try:
                    await client.disconnect()
                except Exception:
                    pass
            await asyncio.sleep(2.0)
 
        raise RuntimeError(f"Kon niet verbinden met '{DEVICE_NAME}' na {retries} pogingen.")
 
    async def disconnect(self) -> None:
        """Verbreek de BLE-verbinding netjes."""
        if self._client and self._client.is_connected:
            try:
                await self._client.disconnect()
                print("Verbinding verbroken.")
            except Exception as e:
                print(f"[WARN] Fout bij verbreken: {e}")
        self._client = None
 
    # ── Commando's ────────────────────────────────────────────────────────────
 
    async def start_stream(self) -> None:
        """Notificaties inschakelen + 0x01 sturen → microcontroller start streaming."""
        await self._enable_notifications()
        await self._write(bytes([0x01]))
        print("Start-commando (0x01) verstuurd.")
 
    async def stop_stream(self) -> None:
        """0x02 sturen → microcontroller stopt streaming + notificaties uit."""
        await self._write(bytes([0x02]))
        print("Stop-commando (0x02) verstuurd.")
        await self._disable_notifications()
 
    async def send_command(self, cmd: bytes) -> None:
        """Stuur een willekeurig commando naar de microcontroller."""
        await self._write(cmd)
        print(f"Commando verstuurd: {cmd.hex()}")
 
    async def cmd_burst(self, duration_ms: int, frequency_hz: float) -> None:
        """
        Stuur een stimulatieburst naar de microcontroller.
        Pakketformaat: [0x03, duration_lo, duration_hi, freq_lo, freq_hi]
        Pas dit aan op het werkelijke firmware-protocol.
        """
        dur  = int(duration_ms)  & 0xFFFF
        freq = int(frequency_hz) & 0xFFFF
        payload = bytes([
            0x03,
            dur  & 0xFF, (dur  >> 8) & 0xFF,
            freq & 0xFF, (freq >> 8) & 0xFF,
        ])
        await self._write(payload)
        print(f"Burst-commando verstuurd: {duration_ms}ms @ {frequency_hz}Hz")
 
    # ── Wachten op data ───────────────────────────────────────────────────────
 
    async def receive(self) -> None:
        """Wacht tot de verbinding wegvalt of de taak geannuleerd wordt."""
        print("Ontvangen… (Ctrl+C om te stoppen)\n")
        try:
            await self._disconnected.wait()
        except asyncio.CancelledError:
            pass
 
    # ── Privé hulpfuncties ────────────────────────────────────────────────────
 
    async def _scan(self, timeout: float = 60.0):
        """Scan met callback zodat ook apparaten met lange advertentie-interval gevonden worden."""
        print(f"Scannen naar '{DEVICE_NAME}' (timeout {timeout}s)…")
        found = asyncio.Event()
        result = {}
 
        def on_device(device, adv):
            if device.name and DEVICE_NAME.lower() in device.name.lower():
                if not found.is_set():
                    result["device"] = device
                    found.set()
 
        scanner = BleakScanner(detection_callback=on_device)
        await scanner.start()
        try:
            await asyncio.wait_for(found.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            raise RuntimeError(f"Apparaat '{DEVICE_NAME}' niet gevonden binnen {timeout}s.")
        finally:
            await scanner.stop()
 
        device = result["device"]
        print(f"Gevonden: {device.name}  [{device.address}]")
        return device
 
    async def _resolve_characteristics(self) -> None:
        assert self._client is not None
        nus = next(
            (s for s in self._client.services
             if s.uuid.lower() == NUS_SERVICE_UUID.lower()),
            None,
        )
        if nus is None:
            available = [s.uuid for s in self._client.services]
            raise RuntimeError(f"NUS-service niet gevonden. Beschikbaar: {available}")
 
        tx = next((c for c in nus.characteristics
                   if c.uuid.lower() == NUS_TX_CHAR_UUID.lower()), None)
        rx = next((c for c in nus.characteristics
                   if c.uuid.lower() == NUS_RX_CHAR_UUID.lower()), None)
 
        if tx is None or rx is None:
            raise RuntimeError("TX of RX characteristic niet gevonden in NUS-service.")
 
        self._tx_handle = tx.handle
        self._rx_handle = rx.handle
        print(f"TX handle: {self._tx_handle}  RX handle: {self._rx_handle}")
 
    async def _enable_notifications(self) -> None:
        assert self._client and self._tx_handle is not None
        for attempt in range(1, 4):
            try:
                await self._client.start_notify(self._tx_handle, self._on_notification)
                print("Notificaties ingeschakeld.")
                return
            except Exception as e:
                print(f"[WARN] start_notify poging {attempt} mislukt: {e}")
                if attempt == 3:
                    raise RuntimeError("Kon notificaties niet inschakelen na 3 pogingen.")
                await asyncio.sleep(1.5)
 
    async def _disable_notifications(self) -> None:
        if self._client and self._client.is_connected and self._tx_handle is not None:
            try:
                await self._client.stop_notify(self._tx_handle)
            except Exception:
                pass
 
    async def _write(self, data: bytes) -> None:
        if not self._client or not self._client.is_connected:
            raise RuntimeError("Niet verbonden.")
        await self._client.write_gatt_char(self._rx_handle, data, response=False)
 
    def _on_disconnect(self, _client: BleakClient) -> None:
        print("[WARN] BLE verbinding verbroken!")
        self._disconnected.set()
 
    def _on_notification(self, _sender, data: bytearray) -> None:
        if len(data) < PACKET_SIZE:
            print(f"[WARN] Kort pakket: {len(data)} bytes (verwacht {PACKET_SIZE})")
            return
 
        counter, raw_buffer = struct.unpack_from(PACKET_FORMAT, data)
        self.packet_count += 1
 
        print(
            f"[PKT #{self.packet_count:>6}]  counter={counter:>10}  "
            f"buffer={raw_buffer[:8].hex()}…  ({len(raw_buffer)} bytes)"
        )
 
        if self._on_data:
            self._on_data(counter, raw_buffer)
 
        self.samples.extend(raw_buffer)
        if len(self.samples) > MAX_POINTS:
            del self.samples[: len(self.samples) - MAX_POINTS]
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Synchrone wrapper — vervangt workers/datasource/ble_source.py
# ─────────────────────────────────────────────────────────────────────────────
 
class BLESource:
    """
    Synchrone wrapper om GrompackBLE.
    Draait de async BLE-loop in een eigen achtergrondthread zodat de
    RecordingEngine er gewone (niet-async) methoden op kan aanroepen.
 
    Interface die RecordingEngine verwacht:
        source.start()
        source.stop()
        source.cmd_burst(duration_ms, frequency_hz)
    """
 
    def __init__(self, pipeline) -> None:
        self._pipeline = pipeline
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._ble: GrompackBLE | None = None
        self._ready = threading.Event()
        self._stop_flag = threading.Event()
 
    # ── Publieke interface (synchroon) ────────────────────────────────────────
 
    def start(self) -> None:
        """Verbind met de microcontroller en start streaming (blokkeert tot verbonden)."""
        self._stop_flag.clear()
        self._ready.clear()
        self._error: Exception | None = None
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="BLEThread")
        self._thread.start()
        if not self._ready.wait(timeout=90):
            # Haal eventuele exception op uit de achtergrondthread
            if self._error:
                raise RuntimeError(f"BLE verbinding mislukt: {self._error}") from self._error
            raise RuntimeError("BLE: verbinding niet tijdig tot stand gebracht (timeout 90s).")
 
    def stop(self) -> None:
        """Stop streaming en verbreek de verbinding."""
        self._stop_flag.set()
        if self._loop and self._ble:
            asyncio.run_coroutine_threadsafe(self._async_stop(), self._loop).result(timeout=5)
        if self._thread:
            self._thread.join(timeout=5)
 
    def cmd_burst(self, duration_ms: int, frequency_hz: float) -> None:
        """Stuur een stimulatieburst (thread-safe)."""
        if self._loop and self._ble:
            asyncio.run_coroutine_threadsafe(
                self._ble.cmd_burst(duration_ms, frequency_hz), self._loop
            )
 
    # ── Intern ────────────────────────────────────────────────────────────────
 
    def _run_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._async_run())
        except Exception as e:
            self._error = e
            self._ready.set()   # deblokkeer start() zodat die de fout kan ophalen
            print(f"[BLEThread] Fout: {e}")
        finally:
            self._loop.close()
 
    async def _async_run(self) -> None:
        self._ble = GrompackBLE(on_data=self._on_data)
        await self._ble.connect()
        await self._ble.start_stream()
        self._ready.set()
 
        while not self._stop_flag.is_set():
            await asyncio.sleep(0.1)
 
    async def _async_stop(self) -> None:
        if self._ble:
            await self._ble.stop_stream()
            await self._ble.disconnect()
 
    def _on_data(self, counter: int, raw: bytes) -> None:
        self._pipeline.push_raw(counter, raw)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Standalone tests
# ─────────────────────────────────────────────────────────────────────────────
 
async def _test_async() -> None:
    """Test GrompackBLE direct (async)."""
    grom = GrompackBLE()
    await grom.connect()
    await grom.start_stream()
    await grom.receive()
    await grom.stop_stream()
    await grom.disconnect()
    print(f"\nKlaar. Pakketten: {grom.packet_count}  Samples: {len(grom.samples)}")
 
 
class _FakePipeline:
    """Nep-pipeline: vangt push_raw() op en print elk pakket."""
 
    def __init__(self):
        self.packet_count = 0
        self.byte_count = 0
 
    def push_raw(self, counter: int, raw: bytes) -> None:
        self.packet_count += 1
        self.byte_count += len(raw)
        print(
            f"[PIPELINE] pkt={self.packet_count:>5}  "
            f"counter={counter:>10}  "
            f"bytes={len(raw)}  "
            f"totaal={self.byte_count}  "
            f"eerste4={raw[:4].hex()}"
        )
 
 
def _test_wrapper(test_seconds: int = 5) -> None:
    """Test de synchrone BLESource wrapper met een nep-pipeline."""
    print("=== BLESource wrapper test ===\n")
 
    pipeline = _FakePipeline()
    source = BLESource(pipeline)
 
    print("[TEST] start()…")
    source.start()
    print("[TEST] Verbonden en streaming gestart.\n")
 
    print(f"[TEST] {test_seconds}s data ontvangen…")
    time.sleep(test_seconds)
 
    print("\n[TEST] cmd_burst(50ms, 20Hz)…")
    source.cmd_burst(duration_ms=50, frequency_hz=20)
    time.sleep(1)
 
    print("\n[TEST] stop()…")
    source.stop()
 
    print("\n=== Resultaat ===")
    print(f"Ontvangen pakketten : {pipeline.packet_count}")
    print(f"Ontvangen bytes     : {pipeline.byte_count}")
    expected = int(test_seconds * SAMPLE_RATE / PACKED_BUFFER_SIZE)
    print(f"Verwacht (circa)    : {expected} pakketten")
 
import asyncio
from bleak import BleakScanner
from bleak.backends.winrt.scanner import BleakScannerWinRT
import platform
 
 
async def check():
    print(f"Python platform : {platform.platform()}")
    print(f"Bleak backend   : WinRT (Windows)\n")
 
    # Scan met verhoogde logging
    print("Scanning met cb voor elk advertisement pakket (20s)…")
    count = 0
 
    def cb(device, adv):
        nonlocal count
        count += 1
        print(f"  [{count:>3}] {device.address}  rssi={adv.rssi:>4}  naam={device.name!r}")
 
    scanner = BleakScanner(detection_callback=cb)
    await scanner.start()
    await asyncio.sleep(20)
    await scanner.stop()
 
    print(f"\nTotaal advertisement-paketten ontvangen: {count}")
    if count == 0:
        print("\n[!] Geen enkel BLE-apparaat gevonden.")
        print("    Mogelijke oorzaken:")
        print("    1. BLE adapter ondersteunt passive scan niet goed op Windows 11")
        print("    2. Probeer een USB BLE dongle (CSR 4.0 / 5.0)")
        print("    3. Zet Bluetooth uit en weer aan in Windows instellingen")
    else:
        print("\n[!] Adapter werkt wel, maar Grompack staat er niet bij.")
        print("    → Controleer of de firmware actief adverteert (herstart het apparaat)")
 
def on_device(device, adv):
    naam = device.name or "(geen naam)"
    uuids = [str(u).lower() for u in adv.service_uuids]
    nus = "✓ NUS" if NUS_SERVICE_UUID in uuids else ""
    print(f"  {naam:<30} {device.address:<20} {adv.rssi:>4} dBm  {nus}")
 
 
async def scan(duration: float = 15.0) -> None:
    print(f"Scannen voor {duration}s — verbreek eventuele andere verbindingen…\n")
    print(f"  {'Naam':<30} {'Adres':<20} {'RSSI'}  NUS")
    print("  " + "-" * 65)
 
    scanner = BleakScanner(detection_callback=on_device)
    await scanner.start()
    await asyncio.sleep(duration)
    await scanner.stop()
    print("\nKlaar.")
 
 


# ── Keuzemenu ─────────────────────────────────────────────────────────────────
#
#   python ble_grompack.py             → async GrompackBLE test
#   python ble_grompack.py wrapper     → synchrone BLESource test (5s)
if __name__ == "__main__":
    mode = "wrapper"

    if mode == "wrapper":
        try:
            print("wrapper")
            _test_wrapper()
        except KeyboardInterrupt:
            print("\nAfgebroken door gebruiker.")
            
    if mode == "scan":
        asyncio.run(check())
    
    else:
        try:
            asyncio.run(_test_async())
        except KeyboardInterrupt:
            print("\nAfgebroken door gebruiker.")