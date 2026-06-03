import threading
import time
from core.pipeline import Pipeline

class DSPState:
    """
    Placeholder voor GUI-controlled parameters.
    Nog niet gebruikt in dummy DSP.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.low = 0
        self.high = 0

    def update(self, low, high):
        with self.lock:
            self.low = low
            self.high = high

    def get(self):
        with self.lock:
            return self.low, self.high


class DSPThread(threading.Thread):

    def __init__(
        self,
        ring_buffer,
        pipeline: Pipeline,
        dsp_state,
        consumer_name="dsp",
        block_size=256
    ):
        super().__init__(daemon=True)

        self.ring = ring_buffer
        self.pipeline = pipeline
        self.state = dsp_state

        self.consumer_name = consumer_name
        self.block_size = block_size

        self._running = True

        self.ring.register_consumer(
            consumer_name,
            start_latest=True
        )

    def run(self):
        while self._running:
            try:
                chunk = self.ring.read(self.consumer_name, self.block_size)

                if len(chunk) == 0:
                    time.sleep(0.001)
                    continue

                self.pipeline.push_processed(chunk)

                time.sleep(0.001)

            except Exception as e:
                print(f"[DSPThread error] {e}")
                break

    def stop(self):
        self._running = False