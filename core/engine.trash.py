import threading
from workers.datasource.synthetic_source import SyntheticBLESource
from workers.dsp import DSPThread, DSPState
from workers.writer import WAVWriter
from buffers.raw_buffer import CircularBuffer
from buffers.proc_buffer import ProcessedBuffer
from core.pipeline import Pipeline
from settings.settings import CHANNELS, SAMPLE_RATE, STIMULATION_TIME_MAX
from workers.datasource.ble_source import BLESource
from core.marker_logger import MarkerLogger
import time
from simulations.stress_config import BLEStressConfig          ########################Remove later
import asyncio 
import struct
import numpy as np
from bleak import BleakClient, BleakScanner


DEVICE_NAME       = "grompack"
NUS_TX_CHAR_UUID  = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
NUS_SERVICE_UUID  = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
NUS_RX_CHAR_UUID  = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
PACKED_BUFFER_SIZE = 240
PACKET_FORMAT      = f"<I{PACKED_BUFFER_SIZE}s"
PACKET_SIZE        = struct.calcsize(PACKET_FORMAT)


class RecordingEngine:

    def __init__(
        self,
        sample_rate=SAMPLE_RATE,
        REAL_DATA=True,                           #########################Remove later, replace with real source
        channels=CHANNELS,
        config=BLEStressConfig()                      ########################Remove later
    ):
            
        self.sample_rate = sample_rate
        self.REAL_DATA = REAL_DATA                  #########################Remove later
        self.config = config                        ########################Remove later

        self.raw_buffer = CircularBuffer(sample_rate * 5, channels)
        self.proc_buffer = ProcessedBuffer(sample_rate * 15, channels)  
        self.pipeline = Pipeline(self.raw_buffer, self.proc_buffer)

        self.dsp_state = DSPState()
        self.dsp_state.update(-500, 500)

        self.source = None
        self.dsp = None
        self.writer = None

        self._running = False
        self._connected = False
        self._init_source()
        self.last_stim_time = 0.0


    def _init_source(self):   #########################Remove later

        if self.REAL_DATA:
            self.source = None
        else:
            self.source = SyntheticBLESource(self.pipeline, config=self.config)  

    # =========================================================
    # START SESSION
    # =========================================================
    def start(self, device):

        if self._running:
            return
        
        self.session_id = time.strftime("%Y%m%d_%H%M%S")
        self._running = True

        self.marker_logger = MarkerLogger(
            output_prefix="session",
            session_id=self.session_id
        )

        self.dsp = DSPThread(
            ring_buffer=self.raw_buffer,
            pipeline=self.pipeline,
            dsp_state=self.dsp_state
        )

        self.writer = WAVWriter(
            ring_buffer=self.raw_buffer,
            sample_rate=self.sample_rate,
            session_id=self.session_id,
            consumer_name="writer",
            flush_interval_seconds=5.0,
            output_prefix="session"
        )

        # start other components
        self.dsp.start()
        self.writer.start()
        self.marker_logger.start()
        

            
        if self.REAL_DATA: 
            self._ble_thread = threading.Thread(
                target=self._start_ble_background,
                daemon=True
                )
            self._ble_thread.start()
        else: 
            self.source.cmd_start()
        
    def stop(self):

        if not self._running:
            return
        
        if self.REAL_DATA: 
            self.source.stop_stream()
        else: 
            self.source.cmd_stop()


        # STOP WRITER
        if self.writer:
            self.writer.stop()
            self.writer.join(timeout=2.0)
            self.writer = None

        # STOP MARKERS
        if self.marker_logger:
            self.marker_logger.stop()
            self.marker_logger = None

        # STOP DSP
        if self.dsp:
            self.dsp.stop()
            self.dsp.join(timeout=2.0)
            self.dsp = None


        self.pipeline.reset()

        self._running = False
            
        
    # ============================================================
    # ACCESSORS
    # ============================================================
    def get_pipeline(self):
        return self.pipeline

    # ============================================================
    # MARKERS
    # ============================================================
    def add_marker(self, marker_id):

        if self.marker_logger is None:
            return

        sample_idx = self.pipeline.get_sample_index()

        t = sample_idx / self.sample_rate

        self.marker_logger.add(
            marker_id,
            t
        )
        
    # ============================================================
    # Stimulation
    # ============================================================
    def send_stimulation_burst(self, duration_ms, frequency_hz):

        if not self._running or self.source is None:
            return
        
        #debounce
        if time.perf_counter() - self.last_stim_time < 2*(STIMULATION_TIME_MAX / 1000):
            print("[WARNING] Stimulation command ignored due to debounce. Please wait before sending another stimulation.")
            return
        
        self.source.cmd_burst(duration_ms, frequency_hz)
        self.last_stim_time = time.perf_counter()
        
    def _start_ble_background(self):
        asyncio.run(self._ble_task())
        
    async def _ble_task(self):

        print(f"Scanning for '{DEVICE_NAME}' …")

        device = await BleakScanner.find_device_by_name(
            DEVICE_NAME,
            timeout=30.0
        )
        await asyncio.sleep(5)

        if device is None:
            print("[ERROR] device not found")
            return

        async with BleakClient(device) as client:

            self._client = client
            await client.get_services()
            await asyncio.sleep(0.2)

            nus_service = next(
                (s for s in client.services
                if s.uuid.lower() == NUS_SERVICE_UUID.lower()),
                None
            )

            tx_char = next(
                (c for c in nus_service.characteristics
                if c.uuid.lower() == NUS_TX_CHAR_UUID.lower()),
                None
            )
            print(tx_char.properties)

            rx_char = next(
                (c for c in nus_service.characteristics
                if c.uuid.lower() == NUS_RX_CHAR_UUID.lower()),
                None
            )

            await client.start_notify(tx_char, self._on_notify)
            await client.write_gatt_char(rx_char, b'\x01')

            while self._running:
                await asyncio.sleep(0.05)

            await client.stop_notify(tx_char)
                

    
    def _decode_packet(self, data):

        try:
            header, packed = struct.unpack_from(PACKET_FORMAT, data)
        except Exception as e:
            return None

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

        return samples
    
    def _on_notify(self, _handle: int, data: bytearray):

        if len(data) < PACKET_SIZE:
            return

        samples = self._decode_packet(data)

        if samples is None:
            return

        self.pipeline.push_raw(samples)
    
    