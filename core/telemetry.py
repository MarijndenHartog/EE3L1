import time
import threading


class Telemetry:

    def __init__(self):
        self.lock = threading.Lock()

        # -------------------------
        # pipeline state
        # -------------------------
        self.source_queue = 0
        self.raw_fill = 0
        self.proc_fill = 0

        # -------------------------
        # counters
        # -------------------------
        self.dropped_packets = 0
        self.total_packets = 0

        # -------------------------
        # timing
        # -------------------------
        self.last_push_time = 0.0
        self.last_gui_time = 0.0

        # -------------------------
        # optional external sync values
        # -------------------------
        self.source_sample_index = 0
        self.gui_sample_index = 0

    # ============================================================
    # UPDATES FROM SYSTEM
    # ============================================================
    def update_source(self, queue_len):
        with self.lock:
            self.source_queue = queue_len

    def update_pipeline(self, raw_fill, proc_fill):
        with self.lock:
            self.raw_fill = raw_fill
            self.proc_fill = proc_fill

    def set_sample_indices(self, source_idx, gui_idx):
        with self.lock:
            self.source_sample_index = source_idx
            self.gui_sample_index = gui_idx

    # ============================================================
    # EVENTS
    # ============================================================
    def mark_push(self):
        with self.lock:
            self.last_push_time = time.perf_counter()

    def mark_gui(self):
        with self.lock:
            self.last_gui_time = time.perf_counter()

    def packet_drop(self):
        with self.lock:
            self.dropped_packets += 1

    def packet_in(self):
        with self.lock:
            self.total_packets += 1

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def get(self):
        with self.lock:
            now = time.perf_counter()

            sample_lag = self.source_sample_index - self.gui_sample_index

            return {
                "source_queue": self.source_queue,
                "raw_fill": self.raw_fill,
                "proc_fill": self.proc_fill,

                "dropped": self.dropped_packets,
                "total": self.total_packets,

                # timing (real-time latency)
                "source_age_ms": (
                    (now - self.last_push_time) * 1000
                    if self.last_push_time else 0
                ),

                "gui_lag_ms": (
                    (now - self.last_gui_time) * 1000
                    if self.last_gui_time else 0
                ),

                # structural lag (pipeline lag indicator)
                "sample_lag": sample_lag,
            }

    # ============================================================
    # RESET (important for sessions)
    # ============================================================
    def reset(self):
        with self.lock:
            self.source_queue = 0
            self.raw_fill = 0
            self.proc_fill = 0

            self.dropped_packets = 0
            self.total_packets = 0

            self.last_push_time = 0.0
            self.last_gui_time = 0.0

            self.source_sample_index = 0
            self.gui_sample_index = 0