import threading
import time


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
    """
    Dummy DSP:
    - leest uit CircularBuffer
    - doet GEEN filtering
    - schrijft direct door naar ProcessedBuffer
    """

    def __init__(
        self,
        ring_buffer,
        processed_buffer,
        dsp_state: DSPState,
        consumer_name="dsp",
        block_size=256
    ):
        super().__init__(daemon=True)

        self.ring = ring_buffer
        self.out = processed_buffer
        self.state = dsp_state

        self.consumer_name = consumer_name
        self.block_size = block_size

        self._running = True

        # register in circular buffer
        self.ring.register_consumer(consumer_name, start_latest=True)

    # -------------------------
    # THREAD LOOP
    # -------------------------
    def run(self):
        while self._running:

            # 1. read raw audio
            chunk = self.ring.read(self.consumer_name, self.block_size)

            if len(chunk) == 0:
                time.sleep(0.001)
                continue

            # 2. DUMMY DSP (no processing)
            processed = chunk

            # 3. forward to GUI buffer
            self.out.write(processed)

            # small sleep to avoid 100% CPU spin
            time.sleep(0.001)

    # -------------------------
    # STOP
    # -------------------------
    def stop(self):
        self._running = False