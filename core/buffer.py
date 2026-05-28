import numpy as np
from threading import Lock
from settings import BUFFER_SIZE

class CircularBuffer:
    def __init__(self, size=BUFFER_SIZE):
        self.size = size
        self.buffer = np.zeros(size, dtype=np.int16)

        self.write_index = 0
        self.filled = 0

        self.lock = Lock()

    def write(self, samples):
        samples = np.asarray(samples, dtype=np.int16)
        n = len(samples)

        with self.lock:
            end = self.write_index + n

            if end <= self.size:
                self.buffer[self.write_index:end] = samples
            else:
                split = self.size - self.write_index
                self.buffer[self.write_index:] = samples[:split]
                self.buffer[:end % self.size] = samples[split:]

            self.write_index = end % self.size
            self.filled = min(self.size, self.filled + n)
            
    def read_last(self, n):
        with self.lock:
            n = min(n, self.filled)

            if n == 0:
                return np.array([], dtype=np.int16), self.write_index

            start = (self.write_index - n) % self.size

            if start < self.write_index:
                return self.buffer[start:self.write_index].copy(), start
            else:
                return np.concatenate([
                    self.buffer[start:].copy(),
                    self.buffer[:self.write_index].copy()
                ]), start