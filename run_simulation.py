import sys
from PyQt5 import QtWidgets

from core.engine import RecordingEngine
from modules.GUI.GUIRecording import RecordingTab
from simulations.stress_config import BLEStressConfig

def run():

    app = QtWidgets.QApplication(sys.argv)

    # 1. engine (real or simulated)
    configuration = BLEStressConfig()  # clean config for testing
    
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