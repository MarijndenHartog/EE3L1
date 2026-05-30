import asyncio
import threading
from settings.settings import SAMPLE_RATE, CHANNELS, PACKET_SIZE, BLE_ADDRESS
from workers.datasource.source_abstraction import SourceState

class BLESource(threading.Thread):
    def __init__(self, 
        pipeline, 
        address, 
        sample_rate=SAMPLE_RATE, 
        channels=CHANNELS, 
        packet_size=PACKET_SIZE
    ):
        super().__init__()
        
        self.pipeline = pipeline
        self.address = address
        self.sample_rate = sample_rate
        self.channels = channels
        self.packet_size = packet_size
        
        self._state = SourceState.DISCONNECTED
        
        # Control events
        self._running = False
        self._streaming = False
        
        self.ack_start = threading.Event()
        self.ack_stop = threading.Event()


    def run(self):
        # Format np.int16 data into (packet_size, channels) and write to ring buffer
        #packet = np.stack([ch1, ch2], axis=1)
        #self.pipeline.push_raw(packet)
        return
    
    # ============================================================
    # Commands
    # ============================================================   
    def cmd_start(self):
        self._state = SourceState.STARTING

        #... send start command to BLE device ...
        
        # Wait for BLE device to acknowledge start
        self.ack_start.set() 

    def cmd_stop(self):
        self._state = SourceState.STOPPING
        
        #... send stop command to BLE device ...
        
        # Wait for BLE device to acknowledge stop
        self.ack_stop.set() 

    # ============================================================
    # THREAD CONTROL
    # ============================================================
    def start(self):

        if self.is_alive():
            return

        super().start()

    def stop(self):
        self._streaming = False
        self._running = False
        self.state = SourceState.DISCONNECTED


   
        
        