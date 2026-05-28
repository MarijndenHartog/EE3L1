import os
import numpy as np
import wave
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from settings import SAMPLE_RATE, NORMAL_WINDOW_MS, TRIGGER_WINDOW_MS, REFRESH_FPS


class MakeRecordingTab(QtWidgets.QWidget):

    def __init__(self, pipeline, controller, parent=None):
        super().__init__(parent)

        self.pipeline = pipeline
        self.controller = controller

        self.SAMPLE_RATE = SAMPLE_RATE
        self.NORMAL_WINDOW_MS = NORMAL_WINDOW_MS
        self.TRIGGER_WINDOW_MS = TRIGGER_WINDOW_MS
        self.REFRESH_FPS = REFRESH_FPS

        self.VISIBLE_SAMPLES = int(self.SAMPLE_RATE * self.NORMAL_WINDOW_MS / 1000)
        self.TRIGGER_VISIBLE_SAMPLES = int(self.SAMPLE_RATE * self.TRIGGER_WINDOW_MS / 1000)

        self.running = False
        self.trigger_mode = False
        self.append_mode = False

        self.upper_threshold = 1000
        self.lower_threshold = -1000

        self.last_trigger_index = -1
        self.cooldown_samples = 500

        # -------------------------
        # RECORDING STATE
        # -------------------------
        self.recording = False
        self.session_buffer = []

        self.init_ui()

        self.gui_timer = QtCore.QTimer()
        self.gui_timer.timeout.connect(self.update_plot)
        self.gui_timer.start(int(1000 / self.REFRESH_FPS))

    # -------------------------
    # DATA ACCESS
    # -------------------------
    def get_data(self):
        return self.pipeline.get_view(self.VISIBLE_SAMPLES)

    # -------------------------
    # UI
    # -------------------------
    def init_ui(self):
        pg.setConfigOptions(antialias=False)

        main_layout = QtWidgets.QHBoxLayout(self)
        controls = QtWidgets.QVBoxLayout()

        self.button_run = QtWidgets.QPushButton("Start")
        self.button_run.setCheckable(True)
        self.button_run.clicked.connect(self.toggle_running)

        self.button_trigger = QtWidgets.QPushButton("Trigger Mode: OFF")
        self.button_trigger.setCheckable(True)
        self.button_trigger.clicked.connect(self.toggle_trigger_mode)

        self.button_append = QtWidgets.QPushButton("Append Mode: OFF")
        self.button_append.setCheckable(True)
        self.button_append.clicked.connect(self.toggle_append_mode)

        self.upper_box = QtWidgets.QSpinBox()
        self.upper_box.setRange(-100000, 100000)
        self.upper_box.setValue(self.upper_threshold)
        self.upper_box.valueChanged.connect(self.update_thresholds)

        self.lower_box = QtWidgets.QSpinBox()
        self.lower_box.setRange(-100000, 100000)
        self.lower_box.setValue(self.lower_threshold)
        self.lower_box.valueChanged.connect(self.update_thresholds)

        self.name_box = QtWidgets.QLineEdit("Recording")

        controls.addWidget(self.button_run)
        controls.addWidget(self.button_trigger)
        controls.addWidget(self.button_append)
        controls.addWidget(self.upper_box)
        controls.addWidget(self.lower_box)
        controls.addWidget(self.name_box)
        controls.addStretch()

        self.plot_widget = pg.PlotWidget()
        self.plot = self.plot_widget.getPlotItem()
        self.plot.setYRange(-1000, 2000)
        self.curve = self.plot.plot(pen='y')

        self.upper_line = pg.InfiniteLine(angle=0, pen='r')
        self.lower_line = pg.InfiniteLine(angle=0, pen='c')

        self.plot.addItem(self.upper_line)
        self.plot.addItem(self.lower_line)

        main_layout.addLayout(controls)
        main_layout.addWidget(self.plot_widget, 1)

    # -------------------------
    # START / STOP (SESSION CONTROL)
    # -------------------------
    def toggle_running(self):
        self.running = self.button_run.isChecked()
        self.button_run.setText("Stop" if self.running else "Start")

        if self.running:
            # reset session
            self.session_buffer = []

            # connect + start streaming
            self.controller.connect()
            self.controller.start_stream()

            self.recording = True

        else:
            # stop streaming first
            self.controller.stop_stream()

            self.recording = False

            # auto-save session
            self.save_to_wav()

    # -------------------------
    # MODE TOGGLES
    # -------------------------
    def toggle_trigger_mode(self):
        self.trigger_mode = self.button_trigger.isChecked()
        self.button_trigger.setText(
            "Trigger Mode: ON" if self.trigger_mode else "Trigger Mode: OFF"
        )

    def toggle_append_mode(self):
        self.append_mode = self.button_append.isChecked()
        self.button_append.setText(
            "Append Mode: ON" if self.append_mode else "Append Mode: OFF"
        )

    def update_thresholds(self):
        self.upper_threshold = self.upper_box.value()
        self.lower_threshold = self.lower_box.value()

    # -------------------------
    # MAIN PLOT LOOP
    # -------------------------
    def update_plot(self):
        if not self.running:
            return

        data, _ = self.get_data()

        if len(data) < self.VISIBLE_SAMPLES:
            return

        window = data[-self.VISIBLE_SAMPLES:]

        # -------------------------
        # RECORDING (SESSION BUFFER)
        # -------------------------
        if self.recording and len(data) > 0:
            # append latest chunk (simple + safe)
            self.session_buffer.append(data[-256:].copy())

        # -------------------------
        # NORMAL DISPLAY MODE
        # -------------------------
        if not self.trigger_mode:
            t = np.arange(len(window)) / self.SAMPLE_RATE
            self.curve.setData(t, window)
            self.plot.setLabel('bottom', 'Time', units='s')
            return

        # -------------------------
        # TRIGGER MODE
        # -------------------------
        recent = window[-self.cooldown_samples:]

        spikes = np.flatnonzero(
            (recent > self.upper_threshold) |
            (recent < self.lower_threshold)
        )

        if len(spikes) == 0:
            return

        idx = len(window) - self.cooldown_samples + spikes[0]

        if idx <= self.last_trigger_index:
            return

        if idx < self.last_trigger_index + self.cooldown_samples:
            return

        self.last_trigger_index = idx

        pre = self.TRIGGER_VISIBLE_SAMPLES // 2
        post = self.TRIGGER_VISIBLE_SAMPLES - pre

        segment = window[max(0, idx - pre): idx + post]

        if len(segment) < self.TRIGGER_VISIBLE_SAMPLES:
            segment = np.pad(
                segment,
                (0, self.TRIGGER_VISIBLE_SAMPLES - len(segment)),
                mode='edge'
            )

        t = np.arange(len(segment)) * 1000 / self.SAMPLE_RATE

        self.curve.setData(t, segment)
        self.plot.setLabel('bottom', 'Time', units='ms')

    # -------------------------
    # WAV EXPORT (SESSION BUFFER)
    # -------------------------
    def save_to_wav(self):

        if not self.session_buffer:
            return

        name = self.name_box.text().strip()
        if not name:
            name = "Recording"

        filename = f"{name}.wav"

        # merge session
        audio = np.concatenate(self.session_buffer).astype(np.int16)

        # avoid overwrite
        if os.path.exists(filename):
            base, ext = os.path.splitext(filename)
            i = 1
            while os.path.exists(f"{base}_{i}{ext}"):
                i += 1
            filename = f"{base}_{i}{ext}"

        with wave.open(filename, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.SAMPLE_RATE)
            wf.writeframes(audio.tobytes())