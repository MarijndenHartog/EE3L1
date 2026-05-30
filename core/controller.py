class RecordingController:

    def __init__(self, engine):
        self.engine = engine
        self.recording = False

    # -------------------------
    # GUI CALLS THIS
    # -------------------------
    def start(self):
        if self.recording:
            return

        self.recording = True
        self.engine.start()

    def stop(self):
        if not self.recording:
            return

        self.recording = False
        self.engine.stop()

    def get_pipeline(self):
        return self.engine.get_pipeline()