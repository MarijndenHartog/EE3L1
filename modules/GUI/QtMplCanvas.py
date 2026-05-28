# -*- coding: utf-8 -*-
"""
SpikeAnalysis tool. A tool to analyse neuronal spike activity.

Copyright (C) 2024 Luk Sullock Enzlin

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QWidget, QVBoxLayout


class MplCanvas(FigureCanvas):
    #Derived from: https://www.pythonguis.com/tutorials/plotting-matplotlib/
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axs=[]
        super(MplCanvas, self).__init__(self.fig)
        
class QtCanvas(QWidget):
    def __init__(self, parent=None):
        super(QtCanvas, self).__init__(parent)
        self.canvas=MplCanvas()
        self.toolbar=NavigationToolbar(self.canvas)
        self.boxlay=QVBoxLayout()
        self.boxlay.addWidget(self.toolbar)
        self.boxlay.addWidget(self.canvas)
        self.setLayout(self.boxlay)
