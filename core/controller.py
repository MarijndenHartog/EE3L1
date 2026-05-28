import time

class DeviceController:
    """
    Owns:
    - handshake state (future BLE)
    - streaming state
    - gating for all data sources
    """

    def __init__(self, pipeline):
        self.pipeline = pipeline

        self.connected = False
        self.streaming = False
        self.handshake_done = False

    # -------------------------
    # CONNECTION LAYER
    # -------------------------
    def connect(self):
        if self.connected:
            return

        print("Connecting to device... (handshake)")

        # placeholder for BLE discovery + GATT setup
        time.sleep(0.5)

        self.handshake_done = True
        self.connected = True

        print("Device connected + handshake complete")

    def disconnect(self):
        self.connected = False
        self.handshake_done = False
        self.streaming = False

        self.pipeline.streaming_enabled = False

        print("Device disconnected")

    # -------------------------
    # STREAM CONTROL
    # -------------------------
    def start_stream(self):
        if not self.handshake_done:
            print("Cannot start: device not connected")
            return

        self.streaming = True
        self.pipeline.streaming_enabled = True

    def stop_stream(self):
        self.streaming = False
        self.pipeline.streaming_enabled = False