class RecordingController:

    def __init__(self, engine):
        self.engine = engine

    # ============================================================
    # START SYSTEM
    # ============================================================
    def start(self):

        source = self.engine.source

        if not source.is_alive():
            source.start()

        self.engine.start()

        source.ack_start.clear()

        source.cmd_start()

        # WAIT FOR ACK (BLE OR SYNTH)
        if not source.ack_start.wait(timeout=3.0):
            raise TimeoutError("START ACK not received")

    # ============================================================
    # STOP SYSTEM
    # ============================================================
    def stop(self):

        source = self.engine.source

        source.ack_stop.clear()

        source.cmd_stop()

        if not source.ack_stop.wait(timeout=3.0):
            print("WARNING: STOP ACK timeout")

        self.engine.stop()

    # ============================================================
    # PIPELINE ACCESS
    # ============================================================
    def get_pipeline(self):
        return self.engine.get_pipeline()