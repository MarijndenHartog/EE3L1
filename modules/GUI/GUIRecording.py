from PyQt5 import QtWidgets, QtCore
import numpy as np
import pyqtgraph as pg

from settings.settings import (
    UPDATE_TIME,
    SAMPLE_RATE,
    TRIGGER_WINDOW_MS,
    NORMAL_WINDOW_MS,
    UPPER_THRESHOLD,
    LOWER_THRESHOLD,
    STIMULATION_TIME_MS,
    STIMULATION_FREQUENCY_HZ,
    STIMULATION_TIME_MAX,
    STIMULATION_FREQUENCY_MAX,
    REFRESH_FPS
)


class RecordingTab(QtWidgets.QWidget):

    def __init__(self, engine, parent=None):
        super().__init__(parent)

        # Access engine and pipeline
        self.engine = engine  
        self.pipeline = self.engine.get_pipeline()

        # State variables
        self.running = False
        self.trigger_mode = False

        # Thresholds and trigger state
        self.upper_threshold = UPPER_THRESHOLD
        self.lower_threshold = LOWER_THRESHOLD
        self.last_trigger_index_ch1 = -1
        self.last_trigger_index_ch2 = -1
        
        # Stimulation parameters
        self.stim_time_max = STIMULATION_TIME_MAX
        self.stim_freq_max = STIMULATION_FREQUENCY_MAX
        self.stim_time = STIMULATION_TIME_MS
        self.stim_freq = STIMULATION_FREQUENCY_HZ

        # Set visible window sizes in samples
        self.sample_rate = SAMPLE_RATE
        self.NORMAL_VISIBLE_SAMPLES = int(
            self.sample_rate * NORMAL_WINDOW_MS / 1000
        )

        self.TRIGGER_VISIBLE_SAMPLES = int(
            self.sample_rate * TRIGGER_WINDOW_MS / 1000
        )

        # Markers: list of tuples (marker_id, sample_index, line_item)
        self.markers = []

        # Initialize UI
        self.init_ui()
        self.update_thresholds()

        # Start update timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(UPDATE_TIME)
        
        self.plot_counter = 0 ##################Remove later
        

    # ============================================================
    # UI
    # ============================================================
    def init_ui(self):

        pg.setConfigOptions(antialias=False)

        layout = QtWidgets.QHBoxLayout(self)

        controls = QtWidgets.QVBoxLayout()

        ## Control buttons
        # Start/Stop button
        self.btn = QtWidgets.QPushButton("Start")
        self.btn.setCheckable(True)
        self.btn.clicked.connect(self.toggle)

        # Trigger mode toggle button
        self.trigger_btn = QtWidgets.QPushButton("Trigger Mode: OFF")
        self.trigger_btn.setCheckable(True)
        self.trigger_btn.clicked.connect(self.toggle_trigger_mode)

        # Trigger threshold controls
        self.upper_box = QtWidgets.QSpinBox()
        self.upper_box.setRange(-100000, 100000)
        self.upper_box.setValue(self.upper_threshold)
        self.upper_box.valueChanged.connect(self.update_thresholds)

        self.lower_box = QtWidgets.QSpinBox()
        self.lower_box.setRange(-100000, 100000)
        self.lower_box.setValue(self.lower_threshold)
        self.lower_box.valueChanged.connect(self.update_thresholds)
        
        # Stimulation time and frequency controls 
        self.stim_time_box = QtWidgets.QSpinBox()
        self.stim_time_box.setRange(0, self.stim_time_max)
        self.stim_time_box.setValue(self.stim_time)
        self.stim_time_box.valueChanged.connect(self.update_stimulation)
        self.stim_button = QtWidgets.QPushButton("Send Stimulation")
        self.stim_button.clicked.connect(lambda: self.engine.send_stimulation_burst(self.stim_time, self.stim_freq))
        
        self.stim_freq_box = QtWidgets.QSpinBox()
        self.stim_freq_box.setRange(0, self.stim_freq_max)
        self.stim_freq_box.setValue(self.stim_freq)
        self.stim_freq_box.valueChanged.connect(self.update_stimulation)
        
        # BLE device
        self.ble_device_input = QtWidgets.QLineEdit()
        self.ble_device_input.setPlaceholderText("Enter BLE device name")

        self.ble_connect_btn = QtWidgets.QPushButton("Connect BLE")
        self.ble_connect_btn.clicked.connect(self.connect_ble_device)

        self.ble_status = QtWidgets.QLabel("Status: DISCONNECTED")
        self.ble_status.setStyleSheet("color: red;")
        
        
        # Add controls to layout
        controls.addWidget(self.btn)
        controls.addWidget(self.trigger_btn)
        controls.addWidget(QtWidgets.QLabel("Upper threshold"))
        controls.addWidget(self.upper_box)
        controls.addWidget(QtWidgets.QLabel("Lower threshold"))
        controls.addWidget(self.lower_box)
        controls.addWidget(QtWidgets.QLabel("Stimulation Time"))
        controls.addWidget(self.stim_time_box)
        controls.addWidget(QtWidgets.QLabel("Stimulation Frequency"))
        controls.addWidget(self.stim_freq_box)
        controls.addWidget(self.stim_button)
        controls.addWidget(self.ble_device_input)
        controls.addWidget(self.ble_connect_btn)
        controls.addWidget(self.ble_status)
        controls.addStretch()

        # Add plots
        pg_layout = QtWidgets.QVBoxLayout()
        self.plot1 = pg.PlotWidget(title="Channel 1")
        self.plot2 = pg.PlotWidget(title="Channel 2")

        self.curve1 = self.plot1.plot(pen='y')
        self.curve2 = self.plot2.plot(pen='c')

        for p in (self.plot1, self.plot2):
            p.setYRange(-1000, 2000)
            p.showGrid(x=True, y=True)

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
            self.engine.start(device="grompack")
        else:
            self.btn.setText("Start")
            self.engine.stop()

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
        
    def update_stimulation(self):
        self.stim_time = self.stim_time_box.value()
        self.stim_freq = self.stim_freq_box.value()
        return

    # ============================================================
    # MARKERS
    # ============================================================
    def set_markers_visible(self, visible: bool):
        for _, _, line in self.markers:
            line.setVisible(visible)

    def add_marker(self, marker_id, idx):

        colors = {
            1: 'r', 2: 'g', 3: 'b', 4: 'y', 5: 'm',
            6: 'c', 7: 'w', 8: (255, 165, 0), 9: (128, 0, 128)
        }

        line = pg.InfiniteLine(
            angle=90,
            pen=pg.mkPen(colors.get(marker_id, 'r'), width=2)
        )

        self.plot1.addItem(line)

        # Marker start aan rechterkant van het zichtbare venster
        pos = float(self.NORMAL_VISIBLE_SAMPLES)

        self.markers.append((marker_id, pos, line))

    def update_marker_positions(self, step):

        alive = []

        for marker_id, pos, line in self.markers:

            # schuif marker mee met de plot
            pos -= step

            # marker is uit beeld
            if pos < 0:
                self.plot1.removeItem(line)
                continue

            x_ms = (pos / self.sample_rate) * 1000

            line.setVisible(True)
            line.setPos(x_ms)

            alive.append((marker_id, pos, line))

        self.markers = alive

    # ============================================================
    # TRIGGER DRAW
    # ============================================================
    def _draw_trigger_segment(self, trigger_idx, ch, curve, plot):

        half = self.TRIGGER_VISIBLE_SAMPLES // 2

        start_i = trigger_idx - half
        end_i = trigger_idx + half

        seg = np.zeros(self.TRIGGER_VISIBLE_SAMPLES, dtype=ch.dtype)

        seg_start = max(0, -start_i)
        data_start = max(0, start_i)
        data_end = min(len(ch), end_i)

        seg[seg_start:seg_start + (data_end - data_start)] = ch[data_start:data_end]

        t = np.arange(self.TRIGGER_VISIBLE_SAMPLES) * 1000 / self.sample_rate


        curve.setData(t, seg)

        plot.setXRange(0, self.TRIGGER_VISIBLE_SAMPLES * 1000 / self.sample_rate)

    # ============================================================
    # UPDATE LOOP
    # ============================================================
    def update_plot(self):
        
        n = int(self.NORMAL_VISIBLE_SAMPLES)
        data, step = self.pipeline.get_processed(n = n)
        data = np.asarray(data)
        
        if data.size == 0 or data.ndim != 2 or data.shape[1] < 2:
            return
        
        self.plot_counter += step    ################Remove later
        live_lag = np.round((self.pipeline.live_idx - self.plot_counter) / SAMPLE_RATE, 3)
        buffer_lag = np.round((self.pipeline.get_sample_index() - self.plot_counter) / SAMPLE_RATE, 3)
        #print(live_lag, buffer_lag, step, self.pipeline.proc.write_idx, self.pipeline.proc.read_idx + 36000)

        ch1 = data[:, 0]
        ch2 = data[:, 1]

        # ========================================================
        # NORMAL MODE
        # ========================================================
        if not self.trigger_mode:

            self.set_markers_visible(True)

            ch1_view = ch1[-self.NORMAL_VISIBLE_SAMPLES:]
            ch2_view = ch2[-self.NORMAL_VISIBLE_SAMPLES:]

            x = np.arange(len(ch1_view)) * 1000 / self.sample_rate

            self.curve1.setData(x, ch1_view)
            self.curve2.setData(x, ch2_view)

            self.plot1.setXRange(0, NORMAL_WINDOW_MS)
            self.plot2.setXRange(0, NORMAL_WINDOW_MS)

            self.update_marker_positions(step)
            return

        # ========================================================
        # TRIGGER MODE (INDEPENDENT CHANNELS)
        # ========================================================

        self.set_markers_visible(False)

        # CH1 trigger → Plot 1
        spike_ch1 = np.where(
            (ch1 > self.upper_threshold) |
            (ch1 < self.lower_threshold)
        )[0]

        if len(spike_ch1) > 0:
            idx = spike_ch1[0]

            if idx != self.last_trigger_index_ch1:
                self.last_trigger_index_ch1 = idx
                self._draw_trigger_segment(idx, ch1, self.curve1, self.plot1)

        # CH2 trigger → Plot 2
        spike_ch2 = np.where(
            (ch2 > self.upper_threshold) |
            (ch2 < self.lower_threshold)
        )[0]

        if len(spike_ch2) > 0:
            idx = spike_ch2[0]

            if idx != self.last_trigger_index_ch2:
                self.last_trigger_index_ch2 = idx
                self._draw_trigger_segment(idx, ch2, self.curve2, self.plot2)

    # ============================================================
    # KEY INPUT
    # ============================================================
    def keyPressEvent(self, event):

        if not self.running:
            return

        key = event.key()

        if QtCore.Qt.Key_1 <= key <= QtCore.Qt.Key_9:

            marker_id = key - QtCore.Qt.Key_0
            self.engine.add_marker(marker_id)
            self.add_marker(marker_id, None)
            
    def connect_ble_device(self):
        return