import os
import numpy as np
import wave
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg


class MakeRecordingTab(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # ============================================================
        # CONFIGURATION
        # ============================================================
        self.SAMPLE_RATE = 10000

        self.NORMAL_WINDOW_MS = 1000
        self.TRIGGER_WINDOW_MS = 10

        self.REFRESH_FPS = 30

        self.BUFFER_SECONDS = 5
        self.PACKET_SAMPLES = 100

        self.VISIBLE_SAMPLES = int(
            self.SAMPLE_RATE * self.NORMAL_WINDOW_MS / 1000
        )

        self.TRIGGER_VISIBLE_SAMPLES = int(
            self.SAMPLE_RATE * self.TRIGGER_WINDOW_MS / 1000
        )

        self.BUFFER_SIZE = (
            self.SAMPLE_RATE * self.BUFFER_SECONDS
        )

        # ============================================================
        # STATE
        # ============================================================
        self.phase = 0

        self.running = False
        self.trigger_mode = False
        self.append_mode = False
        self.unsaved_changes = False

        self.upper_threshold = 1000
        self.lower_threshold = -1000

        self.buffer = np.zeros(
            self.BUFFER_SIZE,
            dtype=np.int16
        )

        self.write_index = 0

        self.last_trigger_write_index = -1

        # Recording buffers
        self.current_recording = []
        self.full_recording = []

        # ============================================================
        # UI
        # ============================================================
        self.init_ui()

        # ============================================================
        # TIMERS
        # ============================================================
        self.packet_timer = QtCore.QTimer()
        self.packet_timer.timeout.connect(
            self.receive_fake_packet
        )

        self.packet_timer.start(
            int(
                1000
                * self.PACKET_SAMPLES
                / self.SAMPLE_RATE
            )
        )

        self.gui_timer = QtCore.QTimer()
        self.gui_timer.timeout.connect(
            self.update_plot
        )

        self.gui_timer.start(
            int(1000 / self.REFRESH_FPS)
        )

    # ============================================================
    # UI SETUP
    # ============================================================
    def init_ui(self):

        pg.setConfigOptions(antialias=False)

        main_layout = QtWidgets.QHBoxLayout(self)

        # ------------------------------------------------------------
        # LEFT CONTROL PANEL
        # ------------------------------------------------------------
        controls = QtWidgets.QVBoxLayout()

        # START / STOP BUTTON
        self.button_run = QtWidgets.QPushButton("Start")

        self.button_run.setCheckable(True)
        self.button_run.setChecked(False)

        self.button_run.clicked.connect(
            self.toggle_running
        )

        # TRIGGER MODE BUTTON
        self.button_trigger = QtWidgets.QPushButton(
            "Trigger Mode: OFF"
        )

        self.button_trigger.setCheckable(True)

        self.button_trigger.clicked.connect(
            self.toggle_trigger_mode
        )

        # APPEND MODE BUTTON
        self.button_append = QtWidgets.QPushButton(
            "Append Mode: OFF"
        )

        self.button_append.setCheckable(True)

        self.button_append.clicked.connect(
            self.toggle_append_mode
        )

        # UPPER THRESHOLD
        upper_label = QtWidgets.QLabel(
            "Upper Threshold"
        )

        self.upper_box = QtWidgets.QSpinBox()

        self.upper_box.setRange(
            -100000,
            100000
        )

        self.upper_box.setValue(
            self.upper_threshold
        )

        self.upper_box.valueChanged.connect(
            self.update_thresholds
        )

        # LOWER THRESHOLD
        lower_label = QtWidgets.QLabel(
            "Lower Threshold"
        )

        self.lower_box = QtWidgets.QSpinBox()

        self.lower_box.setRange(
            -100000,
            100000
        )

        self.lower_box.setValue(
            self.lower_threshold
        )

        self.lower_box.valueChanged.connect(
            self.update_thresholds
        )

        # RECORDING NAME
        name_label = QtWidgets.QLabel(
            "Recording Name"
        )

        self.name_box = QtWidgets.QLineEdit()

        self.name_box.setText(
            self.get_default_filename()
        )

        # SAVE BUTTON
        self.button_save = QtWidgets.QPushButton(
            "Save WAV"
        )

        self.button_save.clicked.connect(
            self.save_to_wav
        )

        # Layout
        controls.addWidget(self.button_run)
        controls.addWidget(self.button_trigger)
        controls.addWidget(self.button_append)

        controls.addSpacing(20)

        controls.addWidget(upper_label)
        controls.addWidget(self.upper_box)

        controls.addSpacing(10)

        controls.addWidget(lower_label)
        controls.addWidget(self.lower_box)

        controls.addSpacing(20)

        controls.addWidget(name_label)
        controls.addWidget(self.name_box)

        controls.addSpacing(20)

        controls.addWidget(self.button_save)

        controls.addStretch()

        # ------------------------------------------------------------
        # PLOT
        # ------------------------------------------------------------
        self.plot_widget = pg.PlotWidget()

        self.plot = self.plot_widget.getPlotItem()

        self.plot.setLabel(
            'left',
            'Amplitude'
        )

        self.plot.showGrid(
            x=True,
            y=True
        )

        self.plot.setYRange(
            -5000,
            5000
        )

        self.curve = self.plot.plot(
            pen='y'
        )

        # THRESHOLD LINES
        self.upper_line = pg.InfiniteLine(
            angle=0,
            pen=pg.mkPen(
                'r',
                width=1,
                style=QtCore.Qt.DashLine
            )
        )

        self.lower_line = pg.InfiniteLine(
            angle=0,
            pen=pg.mkPen(
                'c',
                width=1,
                style=QtCore.Qt.DashLine
            )
        )

        self.plot.addItem(self.upper_line)
        self.plot.addItem(self.lower_line)

        self.update_threshold_lines()

        # ------------------------------------------------------------
        # MAIN LAYOUT
        # ------------------------------------------------------------
        main_layout.addLayout(
            controls,
            0
        )

        main_layout.addWidget(
            self.plot_widget,
            1
        )

    # ============================================================
    # DEFAULT FILENAME
    # ============================================================
    def get_default_filename(self):

        index = 1

        while True:

            name = f"Recording_{index}"

            filename = f"{name}.wav"

            if not os.path.exists(filename):
                return name

            index += 1

    # ============================================================
    # SIGNAL GENERATION
    # ============================================================
    def generate_samples(self, num_samples):

        noise = np.random.randn(num_samples)

        noise = np.convolve(
            noise,
            np.ones(5) / 5,
            mode='same'
        ) * 300

        spikes = np.zeros(num_samples)

        i = 0

        while i < num_samples:

            if np.random.rand() < 0.0002:

                amp = np.random.choice(
                    [2000, 3000, 4000, 5000]
                )

                width = np.random.randint(
                    5,
                    12
                )

                for w in range(width):

                    if i + w < num_samples:

                        rise = (
                            1 - np.exp(-w / 2.0)
                        )

                        decay = np.exp(-w / 3.0)

                        spikes[i + w] += (
                            amp
                            * rise
                            * decay
                        )

                i += np.random.randint(
                    25,
                    80
                )

            else:
                i += 1

        self.phase += num_samples

        signal = noise + spikes

        return np.clip(
            signal,
            -8192,
            8191
        ).astype(np.int16)

    # ============================================================
    # DATA INPUT
    # ============================================================
    def receive_fake_packet(self):

        if not self.running:
            return

        samples = self.generate_samples(
            self.PACKET_SAMPLES
        )

        # CURRENT SESSION
        self.current_recording.append(
            samples.copy()
        )
        self.unsaved_changes = True

        # APPEND RECORDING
        if self.append_mode:

            self.full_recording.append(
                samples.copy()
            )

        # RING BUFFER
        end = (
            self.write_index
            + self.PACKET_SAMPLES
        )

        if end < self.BUFFER_SIZE:

            self.buffer[
                self.write_index:end
            ] = samples

        else:

            split = (
                self.BUFFER_SIZE
                - self.write_index
            )

            self.buffer[
                self.write_index:
            ] = samples[:split]

            self.buffer[
                :self.PACKET_SAMPLES - split
            ] = samples[split:]

        self.write_index = (
            self.write_index
            + self.PACKET_SAMPLES
        ) % self.BUFFER_SIZE

    # ============================================================
    # BUTTON CALLBACKS
    # ============================================================
    def toggle_running(self):

        self.running = self.button_run.isChecked()

        if self.running:

            self.button_run.setText("Stop")

            # fresh session
            self.current_recording = []

        else:

            self.button_run.setText("Start")

    def toggle_trigger_mode(self):

        self.trigger_mode = (
            self.button_trigger.isChecked()
        )

        if self.trigger_mode:

            self.button_trigger.setText(
                "Trigger Mode: ON"
            )

        else:

            self.button_trigger.setText(
                "Trigger Mode: OFF"
            )

    def toggle_append_mode(self):

        self.append_mode = (
            self.button_append.isChecked()
        )

        if self.append_mode:

            self.button_append.setText(
                "Append Mode: ON"
            )

        else:

            self.button_append.setText(
                "Append Mode: OFF"
            )

    def update_thresholds(self):

        self.upper_threshold = (
            self.upper_box.value()
        )

        self.lower_threshold = (
            self.lower_box.value()
        )

        self.update_threshold_lines()

    def update_threshold_lines(self):

        self.upper_line.setValue(
            self.upper_threshold
        )

        self.lower_line.setValue(
            self.lower_threshold
        )

    # ============================================================
    # SAVE WAV
    # ============================================================
    def save_to_wav(self):

        name = self.name_box.text().strip()

        if name == "":
            print("Invalid filename")
            return

        filename = f"{name}.wav"

        # Prevent overwrite
        if os.path.exists(filename):

            print(
                f"File already exists: {filename}"
            )

            return

        if self.append_mode:

            source = self.full_recording

        else:

            source = self.current_recording

        if len(source) == 0:

            print("No data recorded")
            return

        audio = np.concatenate(
            source
        ).astype(np.int16)

        with wave.open(filename, "w") as wf:

            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(
                self.SAMPLE_RATE
            )

            wf.writeframes(
                audio.tobytes()
            )

        print(
            f"Saved recording: {filename}"
        )
        self.unsaved_changes = False

        # Auto increment next filename
        self.name_box.setText(
            self.get_default_filename()
        )
        
        
    # ============================================================
    # CLOSE EVENT
    # ============================================================
    def closeEvent(self, event):

        if self.unsaved_changes:

            reply = QtWidgets.QMessageBox.warning(
                self,
                "Unsaved Recording",
                (
                    "There are unsaved recordings.\n\n"
                    "Are you sure you want to quit?"
                ),
                QtWidgets.QMessageBox.Yes
                | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )

            if reply == QtWidgets.QMessageBox.No:

                event.ignore()
                return

        event.accept()
        

    # ============================================================
    # PLOT UPDATE
    # ============================================================
    def update_plot(self):

        if self.write_index < self.VISIBLE_SAMPLES:
            return

        start = (
            self.write_index
            - self.VISIBLE_SAMPLES
        ) % self.BUFFER_SIZE

        if start < self.write_index:

            data = self.buffer[
                start:self.write_index
            ]

        else:

            data = np.concatenate((
                self.buffer[start:],
                self.buffer[:self.write_index]
            ))

        # ------------------------------------------------------------
        # NORMAL MODE
        # ------------------------------------------------------------
        if not self.trigger_mode:

            t = (
                np.arange(len(data))
                / self.SAMPLE_RATE
            )

            self.curve.setData(t, data)

            self.plot.setLabel(
                'bottom',
                'Time',
                units='s'
            )

            self.plot.setXRange(
                0,
                self.NORMAL_WINDOW_MS / 1000
            )

            return

        # ------------------------------------------------------------
        # TRIGGER MODE
        # ------------------------------------------------------------
        spike_indices = np.where(
            (data > self.upper_threshold)
            |
            (data < self.lower_threshold)
        )[0]

        if len(spike_indices) == 0:
            return

        trigger_idx = spike_indices[0]

        trigger_global_index = (
            self.write_index
            - len(data)
            + trigger_idx
        ) % self.BUFFER_SIZE

        if (
            trigger_global_index
            == self.last_trigger_write_index
        ):
            return

        self.last_trigger_write_index = (
            trigger_global_index
        )

        pre = (
            self.TRIGGER_VISIBLE_SAMPLES // 2
        )

        post = (
            self.TRIGGER_VISIBLE_SAMPLES
            - pre
        )

        start_i = max(
            0,
            trigger_idx - pre
        )

        end_i = min(
            len(data),
            trigger_idx + post
        )

        segment = data[start_i:end_i]

        if len(segment) < self.TRIGGER_VISIBLE_SAMPLES:

            segment = np.pad(
                segment,
                (
                    0,
                    self.TRIGGER_VISIBLE_SAMPLES
                    - len(segment)
                ),
                mode='edge'
            )

        t = (
            np.arange(len(segment))
            * 1000
            / self.SAMPLE_RATE
        )

        self.curve.setData(
            t,
            segment
        )

        self.plot.setLabel(
            'bottom',
            'Time',
            units='ms'
        )

        self.plot.setXRange(
            0,
            self.TRIGGER_WINDOW_MS
        )


if __name__ == "__main__":

    app = QtWidgets.QApplication([])

    w = MakeRecordingTab()

    w.resize(1200, 600)

    w.show()

    app.exec_()