import asyncio
import threading
from settings.settings import SAMPLE_RATE, CHANNELS, PACKET_SIZE, BLE_ADDRESS
from workers.datasource.source_abstraction import SourceState

class BLESource(threading.Thread):
    def __init__(self, 
        ring_buffer, 
        address, 
        sample_rate=SAMPLE_RATE, 
        channels=CHANNELS, 
        packet_size=PACKET_SIZE
    ):
        super().__init__()
        
        self.ring = ring_buffer
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
        packet = np.stack([ch1, ch2], axis=1)
        self.ring.write(packet)
        return
    
    # ============================================================
    # Commands
    # ============================================================   
    def cmd_start(self):
        self._state = SourceState.STARTING
        self.ack_start.clear()
        ... send start command to BLE device ...

    def cmd_stop(self):
        self._state = SourceState.STOPPING
        self.ack_stop.clear()
        ... send stop command to BLE device ...

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
        

   
        
        