import threading
import time
import numpy as np

from settings.settings import SAMPLE_RATE, PACKET_SIZE
from workers.datasource.source_abstraction import DataSource, SourceState
from simulations.stress_config import BLEStressConfig

        
class SyntheticBLESource(threading.Thread, DataSource):

    def __init__(self, pipeline, config=BLEStressConfig()):
        super().__init__(daemon=True)

        self.pipeline = pipeline
        self.config = config

        self.sample_rate = SAMPLE_RATE
        self.packet_size = PACKET_SIZE

        self._stop_event = threading.Event()
        self._streaming = False

        self.ack_start = threading.Event()
        self.ack_stop = threading.Event()

        self.state = SourceState.DISCONNECTED

        self._queue = []
        self._next_t = time.perf_counter()

    # =========================================================
    # CONTROL
    # =========================================================
    def cmd_start(self):
        self._streaming = True
        self.state = SourceState.STREAMING
        self.ack_start.set()


    def cmd_stop(self):
        self._streaming = False
        self.state = SourceState.READY
        self.ack_stop.set()

    # =========================================================
    # SIGNAL
    # =========================================================
    def _generate(self, n):
        noise = np.random.randn(n)
        noise = np.convolve(noise, np.ones(5) / 5, mode='same') * self.config.noise_level

        spikes = np.zeros(n)
        i = 0

        while i < n:
            if np.random.rand() < 0.0002:
                amp = np.random.choice([2000, 3000, 4000, 5000])
                width = np.random.randint(5, 12)

                for w in range(width):
                    if i + w < n:
                        spikes[i + w] += (
                            amp *
                            (1 - np.exp(-w / 2)) *
                            np.exp(-w / 3)
                        )

                i += np.random.randint(25, 80)
            else:
                i += 1

        signal = noise + spikes
        return np.clip(signal, -8192, 8191).astype(np.int16)
    
    # =========================================================
    # RUN LOOP
    # =========================================================
    def run(self):

        dt = self.packet_size / self.sample_rate
        self._next_t = time.perf_counter()

        try:
            while not self._stop_event.is_set():

                if not self._streaming:
                    time.sleep(0.01)
                    self._next_t = time.perf_counter()
                    continue

                packet = np.stack([
                    self._generate(self.packet_size),
                    self._generate(self.packet_size)
                ], axis=1)

                if self.config.enable_packet_loss:
                    if np.random.rand() < self.config.packet_loss_prob:
                        continue

                if self.config.enable_congestion:
                    if len(self._queue) >= self.config.max_queue_size:
                        self._queue.pop(0)

                self._queue.append(packet)

                if self.config.enable_burst and np.random.rand() < self.config.burst_prob:
                    time.sleep(np.random.uniform(*self.config.burst_delay_ms) / 1000)

                if self.config.enable_stall and np.random.rand() < self.config.stall_prob:
                    time.sleep(np.random.uniform(*self.config.stall_ms) / 1000)

                # flush
                if len(self._queue) >= self.config.flush_threshold:
                    while self._queue and not self._stop_event.is_set():
                        self.pipeline.push_raw(self._queue.pop(0))
                else:
                    self.pipeline.push_raw(packet)

                # timing
                self._next_t += dt

                if self.config.enable_jitter:
                    self._next_t += np.random.normal(0, self.config.jitter_ms_std) / 1000

                sleep_time = self._next_t - time.perf_counter()

                if sleep_time > 0:
                    time.sleep(sleep_time)

                if time.perf_counter() - self._next_t > 1.0:
                    self._next_t = time.perf_counter()

        finally:
            self._queue.clear()
            self.state = SourceState.DISCONNECTED
            self._streaming = False

    # =========================================================
    # THREAD CONTROL
    # =========================================================
    def start(self):
        if self.is_alive():
            return
        super().start()

    def stop(self):
        self._streaming = False
        self._stop_event.set()

        # wake sleeping loop instantly
        self._next_t = time.perf_counter()