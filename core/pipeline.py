class Pipeline:

    def __init__(self, raw_buffer, proc_buffer):
        self.raw = raw_buffer
        self.proc = proc_buffer
        self.sample_index = 0

    def get_raw(self, n):
        return self.raw.read(n)

    def get_processed(self, n):
        return self.proc.read(n)
    
    def push_raw(self, data):
        self.raw.write(data)
        self.sample_index += len(data)
        
    def push_processed(self, data):
        self.proc.write(data)
    
    def get_sample_index(self):
        return self.sample_index
    
    def reset(self):
        self.raw.reset()
        self.proc.reset()
        self.sample_index = 0