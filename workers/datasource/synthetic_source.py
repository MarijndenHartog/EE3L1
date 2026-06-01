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

        self._running = False
        self._streaming = False

        self.ack_start = threading.Event()
        self.ack_stop = threading.Event()

        self.state = SourceState.DISCONNECTED

        # congestion simulation buffer
        self._queue = []

        # timing
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

        self._running = True

        while self._running:

            if not self._streaming:
                time.sleep(0.01)
                self._next_t = time.perf_counter()
                continue

            # =====================================================
            # PACKET GENERATION
            # =====================================================
            packet = np.stack([
                self._generate(self.packet_size),
                self._generate(self.packet_size)
            ], axis=1)

            # =====================================================
            # PACKET LOSS
            # =====================================================
            if self.config.enable_packet_loss:
                if np.random.rand() < self.config.packet_loss_prob:
                    continue

            # =====================================================
            # CONGESTION (QUEUE LIMIT)
            # =====================================================
            if self.config.enable_congestion:
                if len(self._queue) >= self.config.max_queue_size:
                    self._queue.pop(0)  # drop oldest (real BLE behavior)

            self._queue.append(packet)

            # =====================================================
            # BURST DELAY
            # =====================================================
            if self.config.enable_burst and np.random.rand() < self.config.burst_prob:
                time.sleep(np.random.uniform(*self.config.burst_delay_ms) / 1000)

            # =====================================================
            # STALL EVENT
            # =====================================================
            if self.config.enable_stall and np.random.rand() < self.config.stall_prob:
                time.sleep(np.random.uniform(*self.config.stall_ms) / 1000)

            # =====================================================
            # FLUSH BEHAVIOR (BLE batching)
            # =====================================================
            if len(self._queue) >= self.config.flush_threshold:

                while self._queue:
                    self.pipeline.push_raw(self._queue.pop(0))

            else:
                self.pipeline.push_raw(packet)

            # =====================================================
            # JITTER (TIME DOMAIN)
            # =====================================================
            self._next_t += dt

            if self.config.enable_jitter:
                jitter = np.random.normal(0, self.config.jitter_ms_std) / 1000
                self._next_t += jitter

            sleep_time = self._next_t - time.perf_counter()

            if sleep_time > 0:
                time.sleep(sleep_time)

            # recovery if system stalls
            if time.perf_counter() - self._next_t > 1.0:
                self._next_t = time.perf_counter()

    # =========================================================
    # THREAD CONTROL
    # =========================================================
    def start(self):
        if self.is_alive():
            return
        super().start()

    def stop(self):
        self._streaming = False
        self._running = False
        self.state = SourceState.DISCONNECTED