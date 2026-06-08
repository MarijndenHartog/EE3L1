import numpy as np
import threading


class CircularBuffer:
    def __init__(self, capacity, channels=2):
        self.capacity = capacity
        self.channels = channels

        self.buffer = np.zeros((capacity, channels), dtype=np.int16)

        self.write_idx = 0
        self.lock = threading.Lock()

        # per consumer read pointer
        self.read_ptrs = {}

        # optional: detect overruns per consumer
        self.overruns = {}

    # -------------------------
    # consumer registration
    # -------------------------
    def register_consumer(self, name, start_latest=True):
        with self.lock:
            if start_latest:
                self.read_ptrs[name] = self.write_idx
            else:
                self.read_ptrs[name] = 0

            self.overruns[name] = 0

    # -------------------------
    # VECTORISED WRITE
    # -------------------------
    def write(self, samples: np.ndarray):
        if samples.ndim != 2 or samples.shape[1] != self.channels:
            raise ValueError("Invalid shape: expected (N, channels)")

        n = len(samples)

        with self.lock:
            wp = self.write_idx
            end = wp + n
            self.write_idx = end % self.capacity

            if end <= self.capacity:
                self.buffer[wp:end] = samples
            else:
                first = self.capacity - wp
                self.buffer[wp:] = samples[:first]
                self.buffer[:self.write_idx] = samples[first:]

            for name in self.read_ptrs:
                rp = self.read_ptrs[name]

                # if writer laps reader → mark overrun
                distance = (self.write_idx - rp) % self.capacity
                if distance > self.capacity * 0.8:
                    self.overruns[name] += 1

    # -------------------------
    # VECTORISED READ
    # -------------------------
    def read(self, name, max_samples=1024):
        with self.lock:
            if name not in self.read_ptrs:
                self.read_ptrs[name] = self.write_idx
                self.overruns[name] = 0

            rp = self.read_ptrs[name]
            wp = self.write_idx
            cap = self.capacity

        if rp == wp:
            return np.empty((0, self.channels), dtype=np.int16)

        # compute available samples
        if wp > rp:
            available = wp - rp
        else:
            available = cap - rp + wp

        n = min(available, max_samples)

        if n <= 0:
            return np.empty((0, self.channels), dtype=np.int16)

        # -------- vectorized read (NO LOOP) --------
        if rp + n <= cap:
            out = self.buffer[rp:rp + n]
            new_rp = rp + n
        else:
            first = cap - rp
            second = n - first

            out = np.vstack((
                self.buffer[rp:],
                self.buffer[:second]
            ))

            new_rp = second

        with self.lock:
            self.read_ptrs[name] = new_rp

        return out.copy()

    # -------------------------
    # utility: lag detection
    # -------------------------
    def get_lag(self, name):
        with self.lock:
            rp = self.read_ptrs.get(name, self.write_idx)
            wp = self.write_idx

        return (wp - rp) % self.capacity

    def get_overruns(self, name):
        return self.overruns.get(name, 0)
    
    
    def reset(self):
        with self.lock:
            self.buffer.fill(0)
            self.write_idx = 0
            self.read_ptrs.clear()
            self.overruns.clear()
            
        
            
    
