from workers.datasource.synthetic_source import SyntheticBLESource
from workers.dsp import DSPThread, DSPState
from workers.writer import WAVWriter
from buffers.raw_buffer import CircularBuffer
from buffers.proc_buffer import ProcessedBuffer
from core.pipeline import Pipeline
from settings.settings import REAL_DATA, CHANNELS, SAMPLE_RATE, BLE_ADDRESS, CMD_UUID, DATA_UUID
from workers.datasource.ble_source import BLESource
from core.marker_logger import MarkerLogger
import time


class RecordingEngine:

    def __init__(self, sample_rate=SAMPLE_RATE, REAL_DATA=REAL_DATA, channels=CHANNELS):

        self.sample_rate = sample_rate
        self.channels = channels
        self.REAL_DATA = REAL_DATA

        # -------------------------
        # BUFFERS
        # -------------------------
        self.raw_buffer = CircularBuffer(sample_rate * 5, self.channels)
        self.proc_buffer = ProcessedBuffer(sample_rate * 2, self.channels)

        # -------------------------
        # PIPELINE
        # -------------------------
        self.pipeline = Pipeline(self.raw_buffer, self.proc_buffer)

        # -------------------------
        # DSP STATE
        # -------------------------
        self.dsp_state = DSPState()
        self.dsp_state.update(-500, 500)

        # -------------------------
        # COMPONENTS
        # -------------------------
        self.dsp = None
        self.writer = None
        self.source = None
        
        # -------------------------
        # SESSION 
        # -------------------------       
        self.session_id = None
        self.marker_logger = None
        self.global_sample_index = 0
        
        self._init_source()
        self._running = False
        
    # ============================================================
    # SESSION INIT
    # ============================================================
    def start_session(self):

        self.session_id = time.strftime("%Y%m%d_%H%M%S")

        self.marker_logger = MarkerLogger(
            output_prefix="session",
            session_id=self.session_id
        )

        return self.session_id

    # ============================================================
    # SOURCE FACTORY 
    # ============================================================
    def _init_source(self):

        if self.REAL_DATA:


            self.source = BLESource(
                pipeline=self.pipeline,
                address=BLE_ADDRESS,
                cmd_uuid=CMD_UUID,
                data_uuid=DATA_UUID,
                channels=self.channels
            )

        else:
            self.source = SyntheticBLESource(self.pipeline)

    # ============================================================
    # START ENGINE 
    # ============================================================
    def start(self):

        if self._running:
            return

        self._running = True
        
        if self.session_id is None:
            self.start_session()

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

        self.dsp.start()
        self.writer.start()

    def stop(self):

        if not self._running:
            return

        self._running = False

        if self.dsp:
            self.dsp.stop()

        if self.writer:
            self.writer.stop()

        if self.dsp:
            self.dsp.join(timeout=2)

        if self.writer and self.writer.is_alive():
            self.writer.join(timeout=2)
            
        if self.marker_logger:
            self.marker_logger.stop()

    def get_pipeline(self):
        return self.pipeline
    
    def add_marker(self, marker_id):

        if self.marker_logger is None:
            return

        sample_idx = self.pipeline.get_sample_index()
        t = sample_idx / self.sample_rate

        self.marker_logger.add(marker_id, t)