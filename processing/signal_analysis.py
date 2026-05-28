import numpy as np


class SignalAnalyzer:
    def __init__(self):
        self.alpha = 0.1
        self.previous = 0

    def filter_signal(self, samples):
        """
        Vectorized low-pass filter.
        """

        samples = np.asarray(samples, dtype=np.float32)

        output = np.empty_like(samples)

        prev = self.previous

        for i, sample in enumerate(samples):
            prev = self.alpha * sample + (1 - self.alpha) * prev
            output[i] = prev

        self.previous = prev

        return output

    def rms(self, signal):
        signal = np.asarray(signal)

        return np.sqrt(np.mean(signal ** 2))