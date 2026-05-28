import threading
import time
import numpy as np


class SyntheticDataSource:
    def __init__(self, pipeline, controller, sample_rate=12000, chunk_size=256):
        self.pipeline = pipeline
        self.controller = controller

        self.sample_rate = sample_rate
        self.chunk_size = chunk_size

        self.running = False
        self.thread = None
        self.phase = 0

    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        dt = self.chunk_size / self.sample_rate

        while self.running:
            if not self.controller.streaming:
                time.sleep(0.05)
                continue

            samples = self.generate_samples(self.chunk_size)
            self.pipeline.push_data(samples)

            time.sleep(dt)

    def generate_samples(self, num_samples):
        noise = np.random.randn(num_samples)

        noise = np.convolve(noise, np.ones(5) / 5, mode='same') * 300

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

        self.phase += num_samples
        signal = noise + spikes

        return np.clip(signal, -8192, 8191).astype(np.int16)