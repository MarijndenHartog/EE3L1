import threading
import time
import numpy as np
from scipy.signal import butter, sosfilt, sosfilt_zi
from core.pipeline import Pipeline
from settings.settings import SAMPLE_RATE


class DSPState:
    """
    GUI-controlled DSP parameters.
    """

    def __init__(self):
        self.lock = threading.Lock()

        self.low = 300.0
        self.high = 3000.0

        self.enabled = False

        self._dirty = False

    def update(self, low, high):
        with self.lock:
            self.low = float(low)
            self.high = float(high)
            self._dirty = True

    def set_enabled(self, enabled: bool):
        with self.lock:
            self.enabled = bool(enabled)
            self._dirty = True   # force rebuild / re-eval

    def is_enabled(self):
        with self.lock:
            return self.enabled

    def get(self):
        with self.lock:
            return self.low, self.high

    def consume_dirty(self):
        with self.lock:
            dirty = self._dirty
            self._dirty = False
            return dirty


class DSPThread(threading.Thread):

    def __init__(
        self,
        ring_buffer,
        pipeline: Pipeline,
        dsp_state,
        fs=SAMPLE_RATE,
        consumer_name="dsp",
        block_size=256
    ):
        super().__init__(daemon=True)

        self.ring = ring_buffer
        self.pipeline = pipeline
        self.state = dsp_state

        self.fs = fs
        self.consumer_name = consumer_name
        self.block_size = block_size

        self._running = True

        self.sos = None
        self.zi = None
        self.n_channels = None

        self.ring.register_consumer(
            consumer_name,
            start_latest=True
        )

        self._rebuild_filter()

    def _build_zi(self, sos, n_channels):
        zi_1d = sosfilt_zi(sos)
        return np.repeat(
            zi_1d[:, None, :],
            n_channels,
            axis=1
        )

    def _rebuild_filter(self):
        if not self.state.is_enabled():
            self.sos = None
            self.zi = None
            #print("[DSP] Filter DISABLED")
            return

        low, high = self.state.get()
        nyquist = self.fs / 2.0

        valid = (
            low > 0 and
            high > 0 and
            low < high and
            high < nyquist
        )

        if not valid:
            print(f"[DSP] Invalid bandpass: {low}-{high}")
            self.sos = None
            self.zi = None
            return

        try:
            self.sos = butter(
                N=4,
                Wn=[low, high],
                btype="bandpass",
                fs=self.fs,
                output="sos"
            )

            self.zi = None  # reset state

            #print(f"[DSP] Filter ENABLED: {low:.1f}-{high:.1f} Hz")

        except Exception as e:
            print(f"[DSP] Filter creation failed: {e}")
            self.sos = None
            self.zi = None

    def run(self):
        while self._running:
            try:

                if self.state.consume_dirty():
                    self._rebuild_filter()

                chunk = self.ring.read(
                    self.consumer_name,
                    self.block_size
                )

                if len(chunk) == 0:
                    time.sleep(0.001)
                    continue

                chunk = np.asarray(chunk, dtype=np.float32)

                if chunk.ndim == 1:
                    chunk = chunk[:, None]

                if self.n_channels is None:
                    self.n_channels = chunk.shape[1]


                # ── FILTER OFF ─────────────────────────────
                if not self.state.is_enabled():
                    self.pipeline.push_processed(chunk)
                    continue

                # ── INIT FILTER STATE ──────────────────────
                if self.sos is not None and self.zi is None:
                    self.zi = self._build_zi(self.sos, self.n_channels)

                # ── FILTER ON ──────────────────────────────
                if self.sos is not None and self.zi is not None:
                    filtered, self.zi = sosfilt(
                        self.sos,
                        chunk,
                        axis=0,
                        zi=self.zi
                    )
                    self.pipeline.push_processed(filtered)
                else:
                    self.pipeline.push_processed(chunk)

            except Exception as e:
                print(f"[DSPThread error] {e}")
                break

    def stop(self):
        self._running = False