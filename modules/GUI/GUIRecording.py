from PyQt5 import QtWidgets, QtCore
import numpy as np
import pyqtgraph as pg

from settings.settings import SAMPLE_RATE, TRIGGER_WINDOW_MS, NORMAL_WINDOW_MS, UPPER_THRESHOLD, LOWER_THRESHOLD


class RecordingTab(QtWidgets.QWidget):

    def __init__(self, controller, parent=None):
        super().__init__(parent)

        self.controller = controller
        self.pipeline = controller.get_pipeline()

        self.sample_rate = SAMPLE_RATE

        self.running = False
        self.trigger_mode = False

        self.upper_threshold = UPPER_THRESHOLD
        self.lower_threshold = LOWER_THRESHOLD

        # trigger memory
        self.last_trigger_index = -1
        
        self.NORMAL_VISIBLE_SAMPLES = int(
            self.sample_rate * NORMAL_WINDOW_MS / 1000
        )
        
        self.TRIGGER_VISIBLE_SAMPLES = int(
            self.sample_rate * TRIGGER_WINDOW_MS / 1000
        )

        self.init_ui()
        self.update_thresholds()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(30)

    # ============================================================
    # UI
    # ============================================================
    def init_ui(self):

        pg.setConfigOptions(antialias=False)

        layout = QtWidgets.QHBoxLayout(self)

        # ---------------- CONTROLS ----------------
        controls = QtWidgets.QVBoxLayout()

        self.btn = QtWidgets.QPushButton("Start")
        self.btn.setCheckable(True)
        self.btn.clicked.connect(self.toggle)

        self.trigger_btn = QtWidgets.QPushButton("Trigger Mode: OFF")
        self.trigger_btn.setCheckable(True)
        self.trigger_btn.clicked.connect(self.toggle_trigger_mode)

        self.upper_box = QtWidgets.QSpinBox()
        self.upper_box.setRange(-100000, 100000)
        self.upper_box.setValue(self.upper_threshold)
        self.upper_box.valueChanged.connect(self.update_thresholds)

        self.lower_box = QtWidgets.QSpinBox()
        self.lower_box.setRange(-100000, 100000)
        self.lower_box.setValue(self.lower_threshold)
        self.lower_box.valueChanged.connect(self.update_thresholds)

        controls.addWidget(self.btn)
        controls.addWidget(self.trigger_btn)
        controls.addWidget(QtWidgets.QLabel("Upper threshold"))
        controls.addWidget(self.upper_box)
        controls.addWidget(QtWidgets.QLabel("Lower threshold"))
        controls.addWidget(self.lower_box)
        controls.addStretch()

        # ---------------- PLOTS ----------------
        pg_layout = QtWidgets.QVBoxLayout()

        self.plot1 = pg.PlotWidget(title="Channel 1")
        self.plot2 = pg.PlotWidget(title="Channel 2")

        self.curve1 = self.plot1.plot(pen='y')
        self.curve2 = self.plot2.plot(pen='c')

        # stable y-axis (IMPORTANT)
        for p in (self.plot1, self.plot2):
            p.setYRange(-1000, 2000)
            p.showGrid(x=True, y=True)

        # trigger lines
        self.upper_line1 = pg.InfiniteLine(angle=0, pen='r')
        self.lower_line1 = pg.InfiniteLine(angle=0, pen='b')

        self.upper_line2 = pg.InfiniteLine(angle=0, pen='r')
        self.lower_line2 = pg.InfiniteLine(angle=0, pen='b')

        self.plot1.addItem(self.upper_line1)
        self.plot1.addItem(self.lower_line1)

        self.plot2.addItem(self.upper_line2)
        self.plot2.addItem(self.lower_line2)

        pg_layout.addWidget(self.plot1)
        pg_layout.addWidget(self.plot2)

        layout.addLayout(controls, 0)
        layout.addLayout(pg_layout, 1)

    # ============================================================
    # CONTROL
    # ============================================================
    def toggle(self):
        self.running = self.btn.isChecked()

        if self.running:
            self.btn.setText("Stop")
            self.controller.start()
        else:
            self.btn.setText("Start")
            self.controller.stop()

    def toggle_trigger_mode(self):
        self.trigger_mode = self.trigger_btn.isChecked()
        self.trigger_btn.setText(
            "Trigger Mode: ON" if self.trigger_mode else "Trigger Mode: OFF"
        )

    def update_thresholds(self):
        self.upper_threshold = self.upper_box.value()
        self.lower_threshold = self.lower_box.value()

        self.upper_line1.setValue(self.upper_threshold)
        self.lower_line1.setValue(self.lower_threshold)

        self.upper_line2.setValue(self.upper_threshold)
        self.lower_line2.setValue(self.lower_threshold)

    # ============================================================
    # PLOT UPDATE
    # ============================================================
    def update_plot(self):

        data = self.pipeline.get_processed_latest(self.NORMAL_VISIBLE_SAMPLES) 
        data = np.asarray(data)

        if data.size == 0:
            return

        if data.ndim != 2 or data.shape[1] < 2:
            return

        ch1 = data[:, 0]
        ch2 = data[:, 1]

        # ========================================================
        # NORMAL MODE
        # ========================================================
        if not self.trigger_mode:

            # take last N samples based on window
            ch1_view = ch1[-self.NORMAL_VISIBLE_SAMPLES:]
            ch2_view = ch2[-self.NORMAL_VISIBLE_SAMPLES:]

            x = np.arange(len(ch1_view)) * 1000 / self.sample_rate  # ms axis

            self.curve1.setData(x, ch1_view)
            self.curve2.setData(x, ch2_view)

            self.plot1.setXRange(0, NORMAL_WINDOW_MS)
            self.plot2.setXRange(0, NORMAL_WINDOW_MS)

            return
        
        # ========================================================
        # TRIGGER MODE (spike detection on CH1)
        # ========================================================
        spike_indices = np.where(
            (ch1 > self.upper_threshold) |
            (ch1 < self.lower_threshold)
        )[0]

        if len(spike_indices) == 0:
            return

        trigger_idx = spike_indices[0]

        # avoid duplicate trigger spam
        if trigger_idx == self.last_trigger_index:
            return

        self.last_trigger_index = trigger_idx

        pre = self.TRIGGER_VISIBLE_SAMPLES // 2
        post = self.TRIGGER_VISIBLE_SAMPLES - pre

        start_i = max(0, trigger_idx - pre)
        end_i = min(len(ch1), trigger_idx + post)

        seg1 = ch1[start_i:end_i]
        seg2 = ch2[start_i:end_i]

        # pad if needed
        if len(seg1) < self.TRIGGER_VISIBLE_SAMPLES:
            pad_len = self.TRIGGER_VISIBLE_SAMPLES - len(seg1)

            seg1 = np.pad(seg1, (0, pad_len), mode='edge')
            seg2 = np.pad(seg2, (0, pad_len), mode='edge')

        t = np.arange(len(seg1)) * 1000 / self.sample_rate

        self.curve1.setData(t, seg1)
        self.curve2.setData(t, seg2)

        self.plot1.setXRange(0, TRIGGER_WINDOW_MS)
        self.plot2.setXRange(0, TRIGGER_WINDOW_MS)