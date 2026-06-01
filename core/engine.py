from workers.datasource.synthetic_source import SyntheticBLESource
from workers.dsp import DSPThread, DSPState
from workers.writer import WAVWriter
from buffers.raw_buffer import CircularBuffer
from buffers.proc_buffer import ProcessedBuffer
from core.pipeline import Pipeline
from settings.settings import REAL_DATA, CHANNELS, SAMPLE_RATE
from workers.datasource.ble_source import BLESource
from core.marker_logger import MarkerLogger
import time
from simulations.stress_config import BLEStressConfig          ########################Remove later


class RecordingEngine:

    def __init__(
        self,
        sample_rate=SAMPLE_RATE,
        REAL_DATA=REAL_DATA,
        channels=CHANNELS,
        config=BLEStressConfig()                      ########################Remove later
    ):

        self.sample_rate = sample_rate
        self.channels = channels
        self.REAL_DATA = REAL_DATA
        self.config = config                          ########################Remove later

        # -------------------------
        # BUFFERS
        # -------------------------
        self.raw_buffer = CircularBuffer(
            sample_rate * 5,
            channels
        )

        self.proc_buffer = ProcessedBuffer(
            sample_rate * 15,
            channels
        )

        # -------------------------
        # PIPELINE
        # -------------------------
        self.pipeline = Pipeline(
            self.raw_buffer,
            self.proc_buffer
        )

        # -------------------------
        # DSP STATE
        # -------------------------
        self.dsp_state = DSPState()
        self.dsp_state.update(-500, 500)

        # -------------------------
        # COMPONENTS
        # -------------------------
        self.source = None
        self.dsp = None
        self.writer = None

        # -------------------------
        # SESSION
        # -------------------------
        self.session_id = None
        self.marker_logger = None

        self._running = False

        self._init_source()

    # ============================================================
    # SOURCE
    # ============================================================
    def _init_source(self):

        if self.REAL_DATA:

            self.source = BLESource(
                pipeline=self.pipeline,
                channels=self.channels
            )

        else:                                       ########################Remove later

            self.source = SyntheticBLESource(
                self.pipeline, config=self.config       ########################Remove later
            )

    # ============================================================
    # SESSION
    # ============================================================
    def start_session(self):

        self.session_id = time.strftime("%Y%m%d_%H%M%S")

        self.marker_logger = MarkerLogger(
            output_prefix="session",
            session_id=self.session_id
        )

    # ============================================================
    # START
    # ============================================================
    def start(self):

        if self._running:
            return

        # -------------------------
        # Source thread lives forever
        # -------------------------
        if not self.source.is_alive():
            self.source.start()

        # -------------------------
        # New session every recording
        # -------------------------
        self.start_session()

        # -------------------------
        # New workers every recording
        # -------------------------
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

        # -------------------------
        # Start source streaming
        # -------------------------
        self.source.ack_start.clear()

        self.source.cmd_start()

        if not self.source.ack_start.wait(timeout=3.0):
            raise TimeoutError(
                "START ACK not received"
            )

        # -------------------------
        # Start workers
        # -------------------------
        self.dsp.start()
        self.writer.start()

        self._running = True

    # ============================================================
    # STOP
    # ============================================================
    def stop(self):

        if not self._running:
            return

        # -------------------------
        # Stop source streaming
        # -------------------------
        self.source.ack_stop.clear()

        self.source.cmd_stop()

        if not self.source.ack_stop.wait(timeout=3.0):
            print("WARNING: STOP ACK timeout")

        # -------------------------
        # Stop workers
        # -------------------------
        if self.dsp:
            self.dsp.stop()

        if self.writer:
            self.writer.stop()

        # -------------------------
        # Join workers
        # -------------------------
        if self.dsp and self.dsp.is_alive():
            self.dsp.join(timeout=2)

        if self.writer and self.writer.is_alive():
            self.writer.join(timeout=2)

        # -------------------------
        # Finalize session
        # -------------------------
        if self.marker_logger:
            self.marker_logger.stop()

        # -------------------------
        # IMPORTANT:
        # prepare for next session
        # -------------------------
        self.dsp = None
        self.writer = None

        self.marker_logger = None
        self.session_id = None

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