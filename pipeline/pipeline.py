from pipeline.buffer import CircularBuffer


class SignalPipeline:
    def __init__(self, buffer_size=100000):
        self.buffer = CircularBuffer(buffer_size)
        self.streaming_enabled = False

    def push_data(self, samples):
        if not self.streaming_enabled:
            return  

        self.buffer.write(samples)

    def get_view(self, n):
        return self.buffer.read_last(n)