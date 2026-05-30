import numpy as np

class Pipeline:
    """
    Pure data pipeline:
    - geen GUI
    - geen start/stop
    - alleen data toegang
    """

    def __init__(self, raw_buffer, proc_buffer):
        self.raw = raw_buffer
        self.proc = proc_buffer

    # -------------------------
    # RAW (optioneel)
    # -------------------------
    def get_raw_latest(self, n):
        return self.raw.read_latest(n)

    # -------------------------
    # PROCESSED (GUI used)
    # -------------------------
    def get_processed_latest(self, n):
        return self.proc.read_latest(n)