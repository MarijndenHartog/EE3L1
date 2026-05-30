import numpy as np
import threading


class ProcessedBuffer:
    """
    High-performance ring buffer for real-time DSP + GUI plotting.

    Design:
    - Single producer (DSP write in batches)
    - Single consumer (GUI read)
    - No read pointer (only write pointer)
    - Always returns "last N samples"
    """

    def __init__(self, capacity: int, channels: int = 2, dtype=np.int16):
        self.capacity = int(capacity)
        self.channels = int(channels)
        self.dtype = dtype

        self.buffer = np.zeros((self.capacity, self.channels), dtype=self.dtype)

        self.write_idx = 0
        self.filled = 0

        self.lock = threading.Lock()

    # ============================================================
    # DSP WRITE (batch safe)
    # ============================================================
    def write(self, samples: np.ndarray):
        """
        Write a batch of samples (N x channels).
        """

        if samples.ndim != 2 or samples.shape[1] != self.channels:
            raise ValueError(
                f"Expected shape (N, {self.channels}), got {samples.shape}"
            )

        n = len(samples)

        with self.lock:
            first_part = min(self.capacity - self.write_idx, n)

            # 1. write first segment
            self.buffer[self.write_idx:self.write_idx + first_part] = samples[:first_part]

            # 2. wrap-around write if needed
            remaining = n - first_part
            if remaining > 0:
                self.buffer[:remaining] = samples[first_part:]

            # 3. update write pointer
            self.write_idx = (self.write_idx + n) % self.capacity

            # 4. track valid fill level (important early startup)
            self.filled = min(self.capacity, self.filled + n)

    # ============================================================
    # GUI READ (last N samples)
    # ============================================================
    def read(self, max_samples: int):
        """
        Return last N samples in correct time order.
        Always returns contiguous time-ordered array.
        """

        with self.lock:
            if self.filled == 0:
                return np.empty((0, self.channels), dtype=self.dtype)

            n = min(max_samples, self.filled)

            end = self.write_idx
            start = (end - n) % self.capacity

            # case 1: no wrap
            if start < end:
                out = self.buffer[start:end]

            # case 2: wrap-around
            else:
                out = np.vstack((
                    self.buffer[start:],
                    self.buffer[:end]
                ))

            return out.copy()