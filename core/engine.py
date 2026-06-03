import threading

from workers.datasource.synthetic_source import SyntheticBLESource
from workers.dsp import DSPThread, DSPState
from workers.writer import WAVWriter
from buffers.raw_buffer import CircularBuffer
from buffers.proc_buffer import ProcessedBuffer
from core.pipeline import Pipeline
from settings.settings import REAL_DATA, CHANNELS, SAMPLE_RATE, STIMULATION_TIME_MAX
from workers.datasource.ble_source import BLESource
from core.marker_logger import MarkerLogger
import time
from simulations.stress_config import BLEStressConfig          ########################Remove later


class RecordingEngine:

    def __init__(
        self,
        sample_rate=SAMPLE_RATE,
        REAL_DATA=REAL_DATA,                           #########################Remove later, replace with real source
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
        self.last_stim_time = 0.0


    def _init_source(self):   #########################Remove later

        if self.REAL_DATA:
            self.source = BLESource(self.pipeline)
        else:
            self.source = SyntheticBLESource(self.pipeline, config=self.config)  




    # =========================================================
    # START SESSION
    # =========================================================
    def start(self):

        if self._running:
            return

        self.session_id = time.strftime("%Y%m%d_%H%M%S")

        self.marker_logger = MarkerLogger(
            output_prefix="session",
            session_id=self.session_id
        )

        # NEW DSP per session
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
        
        self._init_source()   ##########################Remove later recplace with real source 

        self.source.ack_start.clear()
        self.source.cmd_start()

        self.source.ack_start.wait(timeout=3.0)

        self.dsp.start()
        self.source.start()
        self.writer.start()
        self.marker_logger.start()

        self._running = True
    
    # =========================================================
    # STOP SESSION
    # =========================================================
    def stop(self):

        if not self._running:
            return

        # STOP WRITER
        if self.writer:
            self.writer.stop()
            self.writer.join(timeout=2.0)
            self.writer = None

        # STOP MARKERS
        if self.marker_logger:
            self.marker_logger.stop()
            self.marker_logger = None
            
        # STOP SOURCE
        if self.source:
            self.source.cmd_stop()
            self.source.stop()
            self.source.join(timeout=2.0)
            
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
        