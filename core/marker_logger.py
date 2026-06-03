import time
import threading
import queue
import os


import time
import threading
import queue
import os


import time
import threading
import queue
import os


class MarkerLogger:

    def __init__(self, output_prefix="session", session_id=None,
                 min_interval=0.05, flush_interval=0.5):

        self.output_prefix = output_prefix
        self.session_id = session_id or time.strftime("%Y%m%d_%H%M%S")

        self.filepath = f"{self.output_prefix}_{self.session_id}_markers.txt"

        self.q = queue.Queue()

        self.min_interval = min_interval
        self._last_time = 0.0

        self.flush_interval = flush_interval

        self._stop_event = threading.Event()
        self._thread = None

        self._init_file()

    # ------------------------------------------------------------
    def _init_file(self):
        with open(self.filepath, "w") as f:
            f.write("# Marker ID,\tTime (s)\n")

    # ------------------------------------------------------------
    # FAST NON-BLOCKING CALL (UI THREAD SAFE)
    # ------------------------------------------------------------
    def add(self, marker_id: int, t: float):

        now = time.perf_counter()

        if now - self._last_time < self.min_interval:
            return

        self._last_time = now

        self.q.put((marker_id, t))

    # ------------------------------------------------------------
    # BACKGROUND WRITER THREAD
    # ------------------------------------------------------------
    def _run(self):

        buffer = []

        try:
            while not self._stop_event.is_set():

                try:
                    item = self.q.get(timeout=self.flush_interval)
                    buffer.append(item)
                except queue.Empty:
                    pass

                if buffer:
                    with open(self.filepath, "a") as f:
                        for m, t in buffer:
                            f.write(f"{m},\t{t:.4f}\n")

                        f.flush()
                        os.fsync(f.fileno())

                    buffer.clear()

        finally:
            # final flush on exit
            if buffer:
                with open(self.filepath, "a") as f:
                    for m, t in buffer:
                        f.write(f"{m},\t{t:.4f}\n")
                    f.flush()
                    os.fsync(f.fileno())

    # ------------------------------------------------------------
    def stop(self):
        self._stop_event.set()

        if self._thread:
            self._thread.join()  
            self._thread = None
            
            
    def start(self):

        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name=f"MarkerLogger-{self.session_id}"
        )

        self._thread.start()