import threading
import time
import numpy as np


class SyntheticBLESource(threading.Thread):

    def __init__(
        self,
        ring_buffer,
        sample_rate=12000,
        channels=2,
        packet_size=96,
        noise_level=300,
    ):
        super().__init__(daemon=True)

        self.ring = ring_buffer
        self.sample_rate = sample_rate
        self.channels = channels
        self.packet_size = packet_size

        self.noise_level = noise_level

        self._running = True
        self.phase = 0

    # -------------------------
    # SPIKE SIGNAL GENERATOR
    # -------------------------
    def generate_samples(self, num_samples):

        # 1. noise (smoothed)
        noise = np.random.randn(num_samples)
        noise = np.convolve(noise, np.ones(5) / 5, mode='same') * self.noise_level

        # 2. spikes
        spikes = np.zeros(num_samples)

        i = 0
        while i < num_samples:

            if np.random.rand() < 0.0002:

                amp = np.random.choice([2000, 3000, 4000, 5000])
                width = np.random.randint(5, 12)

                for w in range(width):
                    if i + w < num_samples:
                        rise = (1 - np.exp(-w / 2.0))
                        decay = np.exp(-w / 3.0)
                        spikes[i + w] += amp * rise * decay

                i += np.random.randint(25, 80)

            else:
                i += 1

        signal = noise + spikes

        return np.clip(signal, -8192, 8191).astype(np.int16)

    # -------------------------
    # THREAD LOOP
    # -------------------------
    def run(self):

        dt = 1.0 / self.sample_rate

        while self._running:

            # generate block
            ch1 = self.generate_samples(self.packet_size)
            ch2 = (ch1 * 0.8 + np.random.randn(self.packet_size) * 50).astype(np.int16)

            packet = np.stack([ch1, ch2], axis=1)

            # write to buffer
            self.ring.write(packet)

            time.sleep(self.packet_size / self.sample_rate)

    # -------------------------
    # STOP
    #--------------------------
    def stop(self):
        self._running = False