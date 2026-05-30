from workers.datasource.synthetic_source import SyntheticBLESource
from workers.dsp import DSPThread, DSPState
from workers.writer import WAVWriter
from buffers.raw_buffer import CircularBuffer
from buffers.proc_buffer import ProcessedBuffer
from core.pipeline import Pipeline
from settings.settings import REAL_DATA
from workers.datasource.ble_source import BLESource
from settings.settings import BLE_ADDRESS, CMD_UUID, DATA_UUID


class RecordingEngine:

    def __init__(self, sample_rate=12000, REAL_DATA=REAL_DATA):

        self.sample_rate = sample_rate
        self.channels = 2
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

        # create SOURCE (BLE or synthetic)
        self._init_source()

        self._running = False

    # ============================================================
    # SOURCE FACTORY (CLEAN SEPARATION)
    # ============================================================
    def _init_source(self):

        if self.REAL_DATA:


            self.source = BLESource(
                ring_buffer=self.raw_buffer,
                address=BLE_ADDRESS,
                cmd_uuid=CMD_UUID,
                data_uuid=DATA_UUID,
                channels=2
            )

        else:
            self.source = SyntheticBLESource(self.raw_buffer)

    # ============================================================
    # START ENGINE (DSP + WRITER ONLY)
    # ============================================================
    def start(self):

        if self._running:
            return

        self._running = True

        self.dsp = DSPThread(
            ring_buffer=self.raw_buffer,
            processed_buffer=self.proc_buffer,
            dsp_state=self.dsp_state
        )

        self.writer = WAVWriter(
            ring_buffer=self.raw_buffer,
            sample_rate=self.sample_rate,
            consumer_name="logger",
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

    def get_pipeline(self):
        return self.pipeline