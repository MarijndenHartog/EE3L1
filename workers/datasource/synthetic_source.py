import threading
import time
import numpy as np
from settings.settings import SAMPLE_RATE, CHANNELS, PACKET_SIZE

from workers.datasource.source_abstraction import (
    DataSource,
    SourceState
)


class SyntheticBLESource(threading.Thread, DataSource):

    def __init__(
        self,
        ring_buffer,
        sample_rate=SAMPLE_RATE,
        channels=CHANNELS,
        packet_size=PACKET_SIZE,
        noise_level=300,
    ):
        super().__init__(daemon=True)

        self.ring = ring_buffer

        self.sample_rate = sample_rate
        self.channels = channels
        self.packet_size = packet_size
        self.noise_level = noise_level

        self._running = False
        self._streaming = False

        self.state = SourceState.DISCONNECTED

    # ============================================================
    # CONTROL
    # ============================================================
    def cmd_start(self):

        self._streaming = True
        self.state = SourceState.STREAMING

    def cmd_stop(self):

        self._streaming = False
        self.state = SourceState.READY

    def is_streaming(self):
        return self.state == SourceState.STREAMING
    

    # ============================================================
    # SIGNAL GENERATION
    # ============================================================
    def generate(self, n):

        noise = np.random.randn(n)
        noise = np.convolve(
            noise,
            np.ones(5) / 5,
            mode='same'
        ) * self.noise_level

        spikes = np.zeros(n)

        i = 0

        while i < n:

            if np.random.rand() < 0.0002:

                amp = np.random.choice(
                    [2000, 3000, 4000, 5000]
                )

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

        return np.clip(
            signal,
            -8192,
            8191
        ).astype(np.int16)

    # ============================================================
    # THREAD LOOP
    # ============================================================
    def run(self):

        dt = self.packet_size / self.sample_rate

        self._running = True
        self.state = SourceState.READY

        while self._running:

            if not self._streaming:
                time.sleep(0.01)
                continue

            packet_loss_prob = 0.001

            if np.random.rand() < packet_loss_prob:
                time.sleep(dt)
                continue

            ch1 = self.generate(self.packet_size)

            ch2 = (
                ch1 * 0.8 +
                np.random.randn(self.packet_size) * 50
            ).astype(np.int16)

            packet = np.stack(
                [ch1, ch2],
                axis=1
            )

            self.ring.write(packet)

            jitter = np.random.uniform(
                -0.002,
                0.002
            )

            sleep_time = max(
                0,
                dt + jitter
            )

            time.sleep(sleep_time)

        self.state = SourceState.DISCONNECTED

    # ============================================================
    # THREAD CONTROL
    # ============================================================
    def start(self):

        if self.is_alive():
            return

        super().start()

    def stop(self):

        self._streaming = False
        self._running = False
        self.state = SourceState.DISCONNECTED