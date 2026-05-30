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

        # queue for thread-safe logging
        self.q = queue.Queue()

        # rate limiting
        self.min_interval = min_interval
        self._last_time = 0.0

        # flush control
        self.flush_interval = flush_interval
        self._stop = threading.Event()

        self._init_file()

        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    # ------------------------------------------------------------
    def _init_file(self):
        with open(self.filepath, "w") as f:
            f.write("# Marker ID,\tTime (s)\n")

    # ------------------------------------------------------------
    # FAST NON-BLOCKING CALL (UI THREAD SAFE)
    # ------------------------------------------------------------
    def add(self, marker_id: int, t: float):

        now = time.perf_counter()

        # rate limit (prevents spam)
        if now - self._last_time < self.min_interval:
            return

        self._last_time = now

        self.q.put((marker_id, t))

    # ------------------------------------------------------------
    # BACKGROUND WRITER THREAD
    # ------------------------------------------------------------
    def _run(self):

        buffer = []

        while not self._stop.is_set():

            try:
                item = self.q.get(timeout=self.flush_interval)
                buffer.append(item)
            except queue.Empty:
                pass

            # flush batch
            if buffer:

                with open(self.filepath, "a") as f:
                    for m, t in buffer:
                        f.write(f"{m},\t{t:.4f}\n")

                    f.flush()
                    os.fsync(f.fileno())

                buffer.clear()

        # final flush on exit
        if buffer:
            with open(self.filepath, "a") as f:
                for m, t in buffer:
                    f.write(f"{m},\t{t:.4f}\n")

                f.flush()
                os.fsync(f.fileno())

    # ------------------------------------------------------------
    def stop(self):
        self._stop.set()
        self.thread.join(timeout=2.0)