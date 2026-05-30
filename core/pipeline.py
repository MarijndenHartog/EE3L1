class Pipeline:

    def __init__(self, raw_buffer, proc_buffer):
        self.raw = raw_buffer
        self.proc = proc_buffer

    def get_raw_latest(self, n):
        return self.raw.read_latest(n)

    def get_processed_latest(self, n):
        return self.proc.read_latest(n)