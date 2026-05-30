from workers.datasource.synthetic_source import SyntheticBLESource
from workers.dsp import DSPThread, DSPState
from workers.writer import WAVWriter
from buffers.raw_buffer import CircularBuffer
from buffers.proc_buffer import ProcessedBuffer
from core.pipeline import Pipeline


class RecordingEngine:

    def __init__(self, sample_rate=12000):

        self.sample_rate = sample_rate
        self.channels = 2

        # -------------------------
        # BUFFERS
        # -------------------------
        self.raw_buffer = CircularBuffer(sample_rate * 5, self.channels)
        self.proc_buffer = ProcessedBuffer(sample_rate * 2, self.channels)

        # -------------------------
        # PIPELINE (read-only layer)
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
        self.source = SyntheticBLESource(self.raw_buffer)

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

        self._running = False

    # -------------------------
    # START ALL
    # -------------------------
    def start(self):
        if self._running:
            return

        self._running = True
        self.source = SyntheticBLESource(self.raw_buffer)

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

        self.source.start()
        self.dsp.start()
        self.writer.start()

    # -------------------------
    # STOP ALL
    # -------------------------
    def stop(self):
        if not self._running:
            return

        self._running = False

        self.source.stop()
        self.dsp.stop()
        self.writer.stop()

        self.source.join(timeout=2.0)
        self.dsp.join(timeout=2.0)

        if self.writer.is_alive():
            self.writer.join(timeout=2.0)

    # -------------------------
    # GUI ACCESS POINT
    # -------------------------
    def get_pipeline(self):
        return self.pipeline