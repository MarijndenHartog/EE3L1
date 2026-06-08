import sys
from PyQt5 import QtWidgets

from core.engine import RecordingEngine
from modules.GUI.GUIRecording import RecordingTab
from simulations.stress_config import BLEStressConfig

def run():

    app = QtWidgets.QApplication(sys.argv)

    # 1. engine (real or simulated)
    configuration = BLEStressConfig(
        enable_jitter=True,
        jitter_ms_std=10,

        # =========================
        # PACKET LOSS
        # =========================
        enable_packet_loss=False,
        packet_loss_prob=0.01,

        # =========================
        # BURST (micro congestion)
        # =========================
        enable_burst=True,
        burst_prob=0.02,
        burst_delay_ms=(5, 30),

        # =========================
        # STALL (BLE freeze events)
        # =========================
        enable_stall=True,
        stall_prob=0.01,
        stall_ms=(50, 200),

        # =========================
        # QUEUE / CONGESTION
        # =========================
        enable_congestion=True,
        max_queue_size=10,
        flush_threshold=3,
        
        )  # clean config for testing
    
    engine = RecordingEngine(REAL_DATA=False, config=configuration)   
    
    # 2. your existing plotting widget
    widget = RecordingTab(engine)

    # 3. wrap it in a window
    window = QtWidgets.QMainWindow()
    window.setCentralWidget(widget)
    window.resize(1200, 600)
    window.setWindowTitle("Recording Plot (Standalone)")

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run()