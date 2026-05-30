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
        source.cmd_start()
        
    def stop(self):
        source = self.engine.source
        source.cmd_stop()
        self.engine.stop()

    # ============================================================
    # PIPELINE ACCESS
    # ============================================================
    def get_pipeline(self):
        return self.engine.get_pipeline()

    # ============================================================
    # STATUS
    # ============================================================
    def is_recording(self):
        return self.engine.source.is_streaming()