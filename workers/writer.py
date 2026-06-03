import threading
import numpy as np
import time
import wave



class WAVWriter(threading.Thread):

    def __init__(self, ring_buffer, sample_rate, session_id=None, **kwargs):
        super().__init__(daemon=True)

        self.ring = ring_buffer
        self.sample_rate = sample_rate
        self.session_id = session_id

        self.consumer_name = kwargs.get("consumer_name", "writer")
        self.output_prefix = kwargs.get("output_prefix", "session")
        self.max_chunk = kwargs.get("max_chunk", 2048)

        self._stop_event = threading.Event()

        self._file = None
        self._filename = None

        self.ring.register_consumer(
            self.consumer_name,
            start_latest=True
        )

    # -------------------------
    # START
    # -------------------------
    def start_writer(self):
        if self.is_alive():
            return

        self._stop_event.clear()
        super().start()

    # -------------------------
    # STOP
    # -------------------------
    def stop(self):
        self._stop_event.set()

        if self.is_alive():
            self.join(timeout=2.0)

        # close file safely
        if self._file:
            self._file.close()
            self._file = None

    # -------------------------
    # THREAD LOOP
    # -------------------------
    def run(self):

        try:
            self._filename = f"{self.output_prefix}_{self.session_id}.wav"

            self._file = wave.open(self._filename, "wb")
            self._file.setnchannels(2)
            self._file.setsampwidth(2)
            self._file.setframerate(self.sample_rate)

            print(f"[WAV WRITER] recording to {self._filename}")

            while not self._stop_event.is_set():

                chunk = self.ring.read(self.consumer_name, self.max_chunk)

                if len(chunk) > 0:
                    audio = np.asarray(chunk)

                    if audio.ndim == 2:
                        self._file.writeframes(
                            audio.astype(np.int16).tobytes()
                        )

                time.sleep(0.005)

        finally:
            if self._file:
                self._file.close()
                self._file = None