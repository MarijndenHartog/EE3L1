# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'UiSeperatedToolsgQoatx.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

#Imports have been edited. UI now uses Qt5 instead of Qt6, path to QtMplCanvas has been updated to import from main directory with a reletive path.
#At the end and in between imports, a bit of code has been included to let this file run standalone for testing purposes.

from PyQt5.QtCore import (QCoreApplication, QMetaObject, QRect)
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QGridLayout, QLabel, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QSpinBox,
    QTabWidget, QVBoxLayout, QWidget, QAction)
if __name__=="__main__":
    import os
    import sys
    curdir=os.path.dirname(os.path.abspath(__file__))
    pardir=os.path.dirname(os.path.dirname(curdir))
    sys.path.append(pardir)
from modules.GUI.QtMplCanvas import QtCanvas

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.actionImport_file = QAction(MainWindow)
        self.actionImport_file.setObjectName(u"actionImport_file")
        self.actionBatch_analysis = QAction(MainWindow)
        self.actionBatch_analysis.setObjectName(u"actionBatch_analysis")
        self.actionFile_history = QAction(MainWindow)
        self.actionFile_history.setObjectName(u"actionFile_history")
        self.actionReset = QAction(MainWindow)
        self.actionReset.setObjectName(u"actionReset")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_13 = QGridLayout(self.centralwidget)
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.Tab_Recording = QWidget()
        self.Tab_Recording.setObjectName(u"Tab_Recording")
        self.gridLayout_2 = QGridLayout(self.Tab_Recording)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.lbl_markersloaded = QLabel(self.Tab_Recording)
        self.lbl_markersloaded.setObjectName(u"lbl_markersloaded")

        self.gridLayout_2.addWidget(self.lbl_markersloaded, 5, 7, 1, 1)

        self.btn_import = QPushButton(self.Tab_Recording)
        self.btn_import.setObjectName(u"btn_import")
        self.btn_import.setStyleSheet(u"background-color: rgb(0, 255, 0);")

        self.gridLayout_2.addWidget(self.btn_import, 8, 8, 1, 1)

        self.le_identifier = QLineEdit(self.Tab_Recording)
        self.le_identifier.setObjectName(u"le_identifier")

        self.gridLayout_2.addWidget(self.le_identifier, 6, 7, 1, 2)

        self.label_14 = QLabel(self.Tab_Recording)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_2.addWidget(self.label_14, 6, 6, 1, 1)

        self.label_15 = QLabel(self.Tab_Recording)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_2.addWidget(self.label_15, 3, 6, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_2, 8, 4, 1, 1)

        self.lbl_datatype = QLabel(self.Tab_Recording)
        self.lbl_datatype.setObjectName(u"lbl_datatype")

        self.gridLayout_2.addWidget(self.lbl_datatype, 3, 7, 1, 2)

        self.verticalSpacer_12 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_12, 7, 7, 1, 1)

        self.btn_loadmarkers = QPushButton(self.Tab_Recording)
        self.btn_loadmarkers.setObjectName(u"btn_loadmarkers")

        self.gridLayout_2.addWidget(self.btn_loadmarkers, 5, 8, 1, 1)

        self.label_13 = QLabel(self.Tab_Recording)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_2.addWidget(self.label_13, 5, 6, 1, 1)

        self.label_12 = QLabel(self.Tab_Recording)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_2.addWidget(self.label_12, 2, 6, 1, 1)

        self.lbl_filesnr = QLabel(self.Tab_Recording)
        self.lbl_filesnr.setObjectName(u"lbl_filesnr")

        self.gridLayout_2.addWidget(self.lbl_filesnr, 4, 6, 1, 1)

        self.label_10 = QLabel(self.Tab_Recording)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_2.addWidget(self.label_10, 0, 6, 1, 1)

        self.lbl_filename = QLabel(self.Tab_Recording)
        self.lbl_filename.setObjectName(u"lbl_filename")

        self.gridLayout_2.addWidget(self.lbl_filename, 0, 7, 1, 2)

        self.label_16 = QLabel(self.Tab_Recording)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_2.addWidget(self.label_16, 1, 6, 1, 1)

        self.lbl_fileshape = QLabel(self.Tab_Recording)
        self.lbl_fileshape.setObjectName(u"lbl_fileshape")

        self.gridLayout_2.addWidget(self.lbl_fileshape, 1, 7, 1, 2)

        self.cb_channelsnr = QComboBox(self.Tab_Recording)
        self.cb_channelsnr.setObjectName(u"cb_channelsnr")

        self.gridLayout_2.addWidget(self.cb_channelsnr, 4, 7, 1, 2)

        self.plt_container_raw = QtCanvas(self.Tab_Recording)
        self.plt_container_raw.setObjectName(u"plt_container_raw")

        self.gridLayout_2.addWidget(self.plt_container_raw, 0, 0, 8, 6)

        self.sp_framerate = QSpinBox(self.Tab_Recording)
        self.sp_framerate.setObjectName(u"sp_framerate")
        self.sp_framerate.setMaximum(999999999)

        self.gridLayout_2.addWidget(self.sp_framerate, 2, 7, 1, 2)

        self.tabWidget.addTab(self.Tab_Recording, "")
        self.Tab_Raw = QWidget()
        self.Tab_Raw.setObjectName(u"Tab_Raw")
        self.gridLayout_3 = QGridLayout(self.Tab_Raw)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalSpacer_11 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_11, 2, 4, 1, 1)

        self.btn_setfilters = QPushButton(self.Tab_Raw)
        self.btn_setfilters.setObjectName(u"btn_setfilters")
        self.btn_setfilters.setStyleSheet(u"background-color: rgb(0, 255, 0);")

        self.gridLayout_3.addWidget(self.btn_setfilters, 4, 6, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_4, 0, 4, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_4, 4, 2, 1, 1)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_10, 4, 3, 1, 1)

        self.verticalSpacer_10 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_10, 1, 4, 1, 1)

        self.btn_savefilt = QPushButton(self.Tab_Raw)
        self.btn_savefilt.setObjectName(u"btn_savefilt")
        self.btn_savefilt.setStyleSheet(u"background-color: rgb(0, 255, 0);")

        self.gridLayout_3.addWidget(self.btn_savefilt, 4, 8, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_2, 3, 4, 1, 1)

        self.widget = QWidget(self.Tab_Raw)
        self.widget.setObjectName(u"widget")
        self.formLayout = QFormLayout(self.widget)
        self.formLayout.setObjectName(u"formLayout")
        self.ch_notch = QCheckBox(self.widget)
        self.ch_notch.setObjectName(u"ch_notch")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.ch_notch)

        self.sp_notch = QSpinBox(self.widget)
        self.sp_notch.setObjectName(u"sp_notch")
        self.sp_notch.setMinimum(1)
        self.sp_notch.setMaximum(99999)
        self.sp_notch.setValue(50)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.sp_notch)

        self.ch_highpass = QCheckBox(self.widget)
        self.ch_highpass.setObjectName(u"ch_highpass")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.ch_highpass)

        self.ch_lowpass = QCheckBox(self.widget)
        self.ch_lowpass.setObjectName(u"ch_lowpass")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.ch_lowpass)

        self.sp_bandpasslow = QSpinBox(self.widget)
        self.sp_bandpasslow.setObjectName(u"sp_bandpasslow")
        self.sp_bandpasslow.setMinimum(1)
        self.sp_bandpasslow.setMaximum(99999)
        self.sp_bandpasslow.setValue(500)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.sp_bandpasslow)

        self.sp_bandpasshigh = QSpinBox(self.widget)
        self.sp_bandpasshigh.setObjectName(u"sp_bandpasshigh")
        self.sp_bandpasshigh.setMinimum(1)
        self.sp_bandpasshigh.setMaximum(99999)
        self.sp_bandpasshigh.setValue(1)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.sp_bandpasshigh)

        self.label_17 = QLabel(self.widget)
        self.label_17.setObjectName(u"label_17")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_17)

        self.lbl_order = QLabel(self.widget)
        self.lbl_order.setObjectName(u"lbl_order")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.lbl_order)

        self.label_19 = QLabel(self.widget)
        self.label_19.setObjectName(u"label_19")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_19)

        self.lbl_quality = QLabel(self.widget)
        self.lbl_quality.setObjectName(u"lbl_quality")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.lbl_quality)


        self.gridLayout_3.addWidget(self.widget, 0, 0, 1, 1)

        self.btn_applyfilt = QPushButton(self.Tab_Raw)
        self.btn_applyfilt.setObjectName(u"btn_applyfilt")
        self.btn_applyfilt.setStyleSheet(u"background-color: rgb(0, 255, 0);")

        self.gridLayout_3.addWidget(self.btn_applyfilt, 4, 7, 1, 1)

        self.plt_fftfilt = QtCanvas(self.Tab_Raw)
        self.plt_fftfilt.setObjectName(u"plt_fftfilt")

        self.gridLayout_3.addWidget(self.plt_fftfilt, 2, 5, 2, 4)

        self.plt_container_filt = QtCanvas(self.Tab_Raw)
        self.plt_container_filt.setObjectName(u"plt_container_filt")

        self.gridLayout_3.addWidget(self.plt_container_filt, 2, 2, 2, 2)

        self.plt_container_unfilt = QtCanvas(self.Tab_Raw)
        self.plt_container_unfilt.setObjectName(u"plt_container_unfilt")

        self.gridLayout_3.addWidget(self.plt_container_unfilt, 0, 2, 2, 2)

        self.plt_fft = QtCanvas(self.Tab_Raw)
        self.plt_fft.setObjectName(u"plt_fft")

        self.gridLayout_3.addWidget(self.plt_fft, 0, 5, 2, 4)

        self.horizontalSpacer_16 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_16, 4, 5, 1, 1)

        self.tabWidget.addTab(self.Tab_Raw, "")
        self.Tab_DataSel = QWidget()
        self.Tab_DataSel.setObjectName(u"Tab_DataSel")
        self.gridLayout_5 = QGridLayout(self.Tab_DataSel)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.btn_viewdatasel = QPushButton(self.Tab_DataSel)
        self.btn_viewdatasel.setObjectName(u"btn_viewdatasel")
        self.btn_viewdatasel.setStyleSheet(u"background-color: rgb(0, 255, 0);")

        self.gridLayout_5.addWidget(self.btn_viewdatasel, 3, 3, 1, 1)

        self.plt_container_datasel = QtCanvas(self.Tab_DataSel)
        self.plt_container_datasel.setObjectName(u"plt_container_datasel")

        self.gridLayout_5.addWidget(self.plt_container_datasel, 0, 0, 1, 6)

        self.btn_applydatasel = QPushButton(self.Tab_DataSel)
        self.btn_applydatasel.setObjectName(u"btn_applydatasel")
        self.btn_applydatasel.setStyleSheet(u"background-color: rgb(0, 255, 0);")

        self.gridLayout_5.addWidget(self.btn_applydatasel, 3, 4, 1, 1)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_5.addItem(self.verticalSpacer_5, 0, 6, 1, 1)

        self.sa_timeframes = QScrollArea(self.Tab_DataSel)
        self.sa_timeframes.setObjectName(u"sa_timeframes")
        self.sa_timeframes.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 251, 218))
        self.gridLayout_4 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.btn_removetime = QPushButton(self.scrollAreaWidgetContents)
        self.btn_removetime.setObjectName(u"btn_removetime")

        self.gridLayout_4.addWidget(self.btn_removetime, 0, 1, 1, 1)

        self.label = QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(u"label")

        self.gridLayout_4.addWidget(self.label, 0, 0, 1, 1)

        self.btn_addtime = QPushButton(self.scrollAreaWidgetContents)
        self.btn_addtime.setObjectName(u"btn_addtime")

        self.gridLayout_4.addWidget(self.btn_addtime, 0, 2, 1, 1)

        self.verticalSpacer_9 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer_9, 1, 1, 1, 1)

        self.horizontalSpacer_14 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_14, 0, 3, 1, 1)

        self.sa_timeframes.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_5.addWidget(self.sa_timeframes, 2, 0, 2, 1)

        self.btn_savedatasel = QPushButton(self.Tab_DataSel)
        self.btn_savedatasel.setObjectName(u"btn_savedatasel")
        self.btn_savedatasel.setStyleSheet(u"background-color: rgb(0, 255, 0);")

        self.gridLayout_5.addWidget(self.btn_savedatasel, 3, 5, 1, 1)

        self.sa_channels = QScrollArea(self.Tab_DataSel)
        self.sa_channels.setObjectName(u"sa_channels")
        self.sa_channels.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 69, 235))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_5 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout.addWidget(self.label_5)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_7)

        self.sa_channels.setWidget(self.scrollAreaWidgetContents_3)

        self.gridLayout_5.addWidget(self.sa_channels, 2, 1, 2, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_5.addItem(self.verticalSpacer, 2, 4, 1, 1)

        self.lbl_markers = QLabel(self.Tab_DataSel)
        self.lbl_markers.setObjectName(u"lbl_markers")

        self.gridLayout_5.addWidget(self.lbl_markers, 2, 2, 1, 1)

        self.btn_loadmarkers_2 = QPushButton(self.Tab_DataSel)
        self.btn_loadmarkers_2.setObjectName(u"btn_loadmarkers_2")

        self.gridLayout_5.addWidget(self.btn_loadmarkers_2, 3, 2, 1, 1)

        self.tabWidget.addTab(self.Tab_DataSel, "")
        self.Tab_SpikeSorting = QWidget()
        self.Tab_SpikeSorting.setObjectName(u"Tab_SpikeSorting")
        self.gridLayout_7 = QGridLayout(self.Tab_SpikeSorting)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.btn_savespikes = QPushButton(self.Tab_SpikeSorting)
        self.btn_savespikes.setObjectName(u"btn_savespikes")
        self.btn_savespikes.setStyleSheet(u"background-color: rgb(0, 255, 0);")

        self.gridLayout_7.addWidget(self.btn_savespikes, 2, 5, 1, 1)

        self.plt_container_spike = QtCanvas(self.Tab_SpikeSorting)
        self.plt_container_spike.setObjectName(u"plt_container_spike")

        self.gridLayout_7.addWidget(self.plt_container_spike, 0, 0, 1, 3)

        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_11, 2, 3, 1, 1)

        self.plt_sortingpreview = QtCanvas(self.Tab_SpikeSorting)
        self.plt_sortingpreview.setObjectName(u"plt_sortingpreview")

        self.gridLayout_7.addWidget(self.plt_sortingpreview, 0, 3, 2, 4)

        self.btn_spikesort = QPushButton(self.Tab_SpikeSorting)
        self.btn_spikesort.setObjectName(u"btn_spikesort")
        self.btn_spikesort.setStyleSheet(u"background-color: rgb(0, 255, 0);")

        self.gridLayout_7.addWidget(self.btn_spikesort, 2, 4, 1, 1)

        self.sa_thresholds = QScrollArea(self.Tab_SpikeSorting)
        self.sa_thresholds.setObjectName(u"sa_thresholds")
        self.sa_thresholds.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 369, 205))
        self.gridLayout_6 = QGridLayout(self.scrollAreaWidgetContents_2)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.btn_removethreshold = QPushButton(self.scrollAreaWidgetContents_2)
        self.btn_removethreshold.setObjectName(u"btn_removethreshold")

        self.gridLayout_6.addWidget(self.btn_removethreshold, 2, 1, 1, 1)

        self.btn_addthreshold = QPushButton(self.scrollAreaWidgetContents_2)
        self.btn_addthreshold.setObjectName(u"btn_addthreshold")

        self.gridLayout_6.addWidget(self.btn_addthreshold, 2, 2, 1, 1)

        self.horizontalSpacer_15 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_6.addItem(self.horizontalSpacer_15, 0, 3, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_6.addItem(self.verticalSpacer_3, 4, 1, 1, 1)

        self.dsp_recurrence = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.dsp_recurrence.setObjectName(u"dsp_recurrence")
        self.dsp_recurrence.setMaximum(1.000000000000000)
        self.dsp_recurrence.setSingleStep(0.100000000000000)
        self.dsp_recurrence.setValue(0.800000000000000)

        self.gridLayout_6.addWidget(self.dsp_recurrence, 0, 2, 1, 1)

        self.label_2 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_6.addWidget(self.label_2, 2, 0, 1, 1)

        self.sps_thresholds = QSpinBox(self.scrollAreaWidgetContents_2)
        self.sps_thresholds.setObjectName(u"sps_thresholds")
        self.sps_thresholds.setMinimum(-999999999)
        self.sps_thresholds.setMaximum(999999999)

        self.gridLayout_6.addWidget(self.sps_thresholds, 3, 0, 1, 1)

        self.sp_cutoff = QSpinBox(self.scrollAreaWidgetContents_2)
        self.sp_cutoff.setObjectName(u"sp_cutoff")
        self.sp_cutoff.setMinimum(-999999999)
        self.sp_cutoff.setMaximum(999999999)

        self.gridLayout_6.addWidget(self.sp_cutoff, 1, 2, 1, 1)

        self.ch_cutoff = QCheckBox(self.scrollAreaWidgetContents_2)
        self.ch_cutoff.setObjectName(u"ch_cutoff")

        self.gridLayout_6.addWidget(self.ch_cutoff, 1, 0, 1, 2)

        self.label_6 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_6.addWidget(self.label_6, 0, 0, 1, 2)

        self.sa_thresholds.setWidget(self.scrollAreaWidgetContents_2)

        self.gridLayout_7.addWidget(self.sa_thresholds, 1, 0, 1, 3)

        self.btn_exportcsv = QPushButton(self.Tab_SpikeSorting)
        self.btn_exportcsv.setObjectName(u"btn_exportcsv")
        self.btn_exportcsv.setStyleSheet(u"background-color: rgb(0, 255, 0);")

        self.gridLayout_7.addWidget(self.btn_exportcsv, 2, 6, 1, 1)

        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_13, 2, 2, 1, 1)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_12, 2, 0, 1, 1)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_7.addItem(self.verticalSpacer_6, 0, 7, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_3, 2, 1, 1, 1)

        self.tabWidget.addTab(self.Tab_SpikeSorting, "")
        self.Tab_AverageWaveform = QWidget()
        self.Tab_AverageWaveform.setObjectName(u"Tab_AverageWaveform")
        self.gridLayout_8 = QGridLayout(self.Tab_AverageWaveform)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.btn_getwaveforms = QPushButton(self.Tab_AverageWaveform)
        self.btn_getwaveforms.setObjectName(u"btn_getwaveforms")
        self.btn_getwaveforms.setStyleSheet(u"background-color: rgb(0, 255, 0);")

        self.gridLayout_8.addWidget(self.btn_getwaveforms, 1, 1, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_8.addItem(self.horizontalSpacer_5, 1, 0, 1, 1)

        self.plt_container_waveforms = QTabWidget(self.Tab_AverageWaveform)
        self.plt_container_waveforms.setObjectName(u"plt_container_waveforms")

        self.gridLayout_8.addWidget(self.plt_container_waveforms, 0, 0, 1, 2)

        self.tabWidget.addTab(self.Tab_AverageWaveform, "")
        self.Tab_ISI = QWidget()
        self.Tab_ISI.setObjectName(u"Tab_ISI")
        self.gridLayout_9 = QGridLayout(self.Tab_ISI)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.horizontalSpacer_6 = QSpacerItem(647, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_9.addItem(self.horizontalSpacer_6, 1, 0, 1, 1)

        self.btn_getisi = QPushButton(self.Tab_ISI)
        self.btn_getisi.setObjectName(u"btn_getisi")
        self.btn_getisi.setStyleSheet(u"background-color: rgb(0, 255, 0);")

        self.gridLayout_9.addWidget(self.btn_getisi, 1, 1, 1, 1)

        self.plt_container_isi = QtCanvas(self.Tab_ISI)
        self.plt_container_isi.setObjectName(u"plt_container_isi")

        self.gridLayout_9.addWidget(self.plt_container_isi, 0, 0, 1, 2)

        self.tabWidget.addTab(self.Tab_ISI, "")
        self.Tab_Amplitude = QWidget()
        self.Tab_Amplitude.setObjectName(u"Tab_Amplitude")
        self.gridLayout_10 = QGridLayout(self.Tab_Amplitude)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.horizontalSpacer_7 = QSpacerItem(621, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_10.addItem(self.horizontalSpacer_7, 1, 0, 1, 1)

        self.btn_getamplitude = QPushButton(self.Tab_Amplitude)
        self.btn_getamplitude.setObjectName(u"btn_getamplitude")
        self.btn_getamplitude.setStyleSheet(u"background-color: rgb(0, 255, 0);")

        self.gridLayout_10.addWidget(self.btn_getamplitude, 1, 1, 1, 1)

        self.plt_container_amplitude = QtCanvas(self.Tab_Amplitude)
        self.plt_container_amplitude.setObjectName(u"plt_container_amplitude")

        self.gridLayout_10.addWidget(self.plt_container_amplitude, 0, 0, 1, 2)

        self.tabWidget.addTab(self.Tab_Amplitude, "")
        self.Tab_Autocorr = QWidget()
        self.Tab_Autocorr.setObjectName(u"Tab_Autocorr")
        self.gridLayout_11 = QGridLayout(self.Tab_Autocorr)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.horizontalSpacer_8 = QSpacerItem(653, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_11.addItem(self.horizontalSpacer_8, 1, 3, 1, 1)

        self.btn_getautocorr = QPushButton(self.Tab_Autocorr)
        self.btn_getautocorr.setObjectName(u"btn_getautocorr")
        self.btn_getautocorr.setStyleSheet(u"background-color: rgb(0, 255, 0);")

        self.gridLayout_11.addWidget(self.btn_getautocorr, 1, 4, 1, 1)

        self.label_8 = QLabel(self.Tab_Autocorr)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_11.addWidget(self.label_8, 1, 0, 1, 1)

        self.plt_container_autocorr = QTabWidget(self.Tab_Autocorr)
        self.plt_container_autocorr.setObjectName(u"plt_container_autocorr")

        self.gridLayout_11.addWidget(self.plt_container_autocorr, 0, 0, 1, 5)

        self.dsp_autotime = QDoubleSpinBox(self.Tab_Autocorr)
        self.dsp_autotime.setObjectName(u"dsp_autotime")
        self.dsp_autotime.setDecimals(3)
        self.dsp_autotime.setValue(2.000000000000000)

        self.gridLayout_11.addWidget(self.dsp_autotime, 1, 1, 1, 1)

        self.tabWidget.addTab(self.Tab_Autocorr, "")
        self.Tab_Crosscorr = QWidget()
        self.Tab_Crosscorr.setObjectName(u"Tab_Crosscorr")
        self.gridLayout_12 = QGridLayout(self.Tab_Crosscorr)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.label_9 = QLabel(self.Tab_Crosscorr)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_12.addWidget(self.label_9, 2, 2, 1, 1)

        self.cb_crossch2 = QComboBox(self.Tab_Crosscorr)
        self.cb_crossch2.setObjectName(u"cb_crossch2")

        self.gridLayout_12.addWidget(self.cb_crossch2, 3, 0, 1, 1)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_12.addItem(self.verticalSpacer_8, 0, 7, 1, 1)

        self.cb_crossch1 = QComboBox(self.Tab_Crosscorr)
        self.cb_crossch1.setObjectName(u"cb_crossch1")

        self.gridLayout_12.addWidget(self.cb_crossch1, 2, 0, 1, 1)

        self.label_4 = QLabel(self.Tab_Crosscorr)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_12.addWidget(self.label_4, 1, 1, 1, 1)

        self.btn_getcrosscorr = QPushButton(self.Tab_Crosscorr)
        self.btn_getcrosscorr.setObjectName(u"btn_getcrosscorr")
        self.btn_getcrosscorr.setStyleSheet(u"background-color: rgb(0, 255, 0);")

        self.gridLayout_12.addWidget(self.btn_getcrosscorr, 3, 6, 1, 1)

        self.cb_crosscl2 = QComboBox(self.Tab_Crosscorr)
        self.cb_crosscl2.setObjectName(u"cb_crosscl2")

        self.gridLayout_12.addWidget(self.cb_crosscl2, 3, 1, 1, 1)

        self.dsp_crosstime = QDoubleSpinBox(self.Tab_Crosscorr)
        self.dsp_crosstime.setObjectName(u"dsp_crosstime")
        self.dsp_crosstime.setDecimals(3)
        self.dsp_crosstime.setValue(2.000000000000000)

        self.gridLayout_12.addWidget(self.dsp_crosstime, 2, 3, 1, 1)

        self.cb_crosscl1 = QComboBox(self.Tab_Crosscorr)
        self.cb_crosscl1.setObjectName(u"cb_crosscl1")

        self.gridLayout_12.addWidget(self.cb_crosscl1, 2, 1, 1, 1)

        self.label_3 = QLabel(self.Tab_Crosscorr)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_12.addWidget(self.label_3, 1, 0, 1, 1)

        self.horizontalSpacer_9 = QSpacerItem(483, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_12.addItem(self.horizontalSpacer_9, 1, 2, 1, 4)

        self.plt_container_crosscorr = QtCanvas(self.Tab_Crosscorr)
        self.plt_container_crosscorr.setObjectName(u"plt_container_crosscorr")

        self.gridLayout_12.addWidget(self.plt_container_crosscorr, 0, 0, 1, 7)

        self.tabWidget.addTab(self.Tab_Crosscorr, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 3)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 0, 1, 1)

        self.Btn_Previous = QPushButton(self.centralwidget)
        self.Btn_Previous.setObjectName(u"Btn_Previous")

        self.gridLayout.addWidget(self.Btn_Previous, 1, 1, 1, 1)

        self.Btn_Next = QPushButton(self.centralwidget)
        self.Btn_Next.setObjectName(u"Btn_Next")

        self.gridLayout.addWidget(self.Btn_Next, 1, 2, 1, 1)

        self.Btn_Exit = QPushButton(self.centralwidget)
        self.Btn_Exit.setObjectName(u"Btn_Exit")

        self.gridLayout.addWidget(self.Btn_Exit, 2, 2, 1, 1)


        self.gridLayout_13.addLayout(self.gridLayout, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        self.menuMenu = QMenu(self.menubar)
        self.menuMenu.setObjectName(u"menuMenu")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuMenu.menuAction())
        self.menuMenu.addAction(self.actionImport_file)
        self.menuMenu.addAction(self.actionBatch_analysis)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.actionFile_history)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.actionReset)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)
        self.plt_container_waveforms.setCurrentIndex(-1)
        self.plt_container_autocorr.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionImport_file.setText(QCoreApplication.translate("MainWindow", u"Import file...", None))
        self.actionBatch_analysis.setText(QCoreApplication.translate("MainWindow", u"Batch analysis", None))
        self.actionFile_history.setText(QCoreApplication.translate("MainWindow", u"File history", None))
        self.actionReset.setText(QCoreApplication.translate("MainWindow", u"Reset", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.lbl_markersloaded.setText(QCoreApplication.translate("MainWindow", u"No markers", None))
        self.btn_import.setText(QCoreApplication.translate("MainWindow", u"Import data", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Identifier: ", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Data type: ", None))
        self.lbl_datatype.setText("")
        self.btn_loadmarkers.setText(QCoreApplication.translate("MainWindow", u"Load from file", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Markers: ", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Framerate: ", None))
#if QT_CONFIG(tooltip)
        self.lbl_filesnr.setToolTip(QCoreApplication.translate("MainWindow", u"Signal to Noise Ratio (SNR) of the signal.\n"
"SNR denotes the ratio between the average and the average plus the standard deviation, giving a proportion that can be used as a guidance in how noisy the signal appears to be.", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_filesnr.setText(QCoreApplication.translate("MainWindow", u"SNR: ", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"File:", None))
#if QT_CONFIG(tooltip)
        self.lbl_filename.setToolTip(QCoreApplication.translate("MainWindow", u"Name of the imported file.", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_filename.setText("")
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Shape: ", None))
#if QT_CONFIG(tooltip)
        self.lbl_fileshape.setToolTip(QCoreApplication.translate("MainWindow", u"Shape of the imported file (rows, columns).\n"
"The rows should be the amount of channels and the columns the amount of datapoints per channel.", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_fileshape.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_Recording), QCoreApplication.translate("MainWindow", u"Open recording", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.Tab_Recording), QCoreApplication.translate("MainWindow", u"Open recording.\n"
"Used to import and view the raw signal data.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btn_setfilters.setToolTip(QCoreApplication.translate("MainWindow", u"Show the selected filters in the plots, but do not apply them to the stored data.\n"
"Note that after time frames have been applied in data selection, filters are no longer applicable.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_setfilters.setText(QCoreApplication.translate("MainWindow", u"View filtered data", None))
#if QT_CONFIG(tooltip)
        self.btn_savefilt.setToolTip(QCoreApplication.translate("MainWindow", u"Save the stored data.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_savefilt.setText(QCoreApplication.translate("MainWindow", u"Save data", None))
#if QT_CONFIG(tooltip)
        self.widget.setToolTip(QCoreApplication.translate("MainWindow", u"Determines how narrow the desired frequency is filtered.\n"
"Default is 30.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.ch_notch.setToolTip(QCoreApplication.translate("MainWindow", u"Filter out a single frequency", None))
#endif // QT_CONFIG(tooltip)
        self.ch_notch.setText(QCoreApplication.translate("MainWindow", u"Notch", None))
        self.sp_notch.setSuffix(QCoreApplication.translate("MainWindow", u" Hz", None))
#if QT_CONFIG(tooltip)
        self.ch_highpass.setToolTip(QCoreApplication.translate("MainWindow", u"Everything below this frequency will be filtered out.", None))
#endif // QT_CONFIG(tooltip)
        self.ch_highpass.setText(QCoreApplication.translate("MainWindow", u"High pass", None))
#if QT_CONFIG(tooltip)
        self.ch_lowpass.setToolTip(QCoreApplication.translate("MainWindow", u"Everything above this frequency will be filtered out.", None))
#endif // QT_CONFIG(tooltip)
        self.ch_lowpass.setText(QCoreApplication.translate("MainWindow", u"Low pass", None))
        self.sp_bandpasslow.setSuffix(QCoreApplication.translate("MainWindow", u" Hz", None))
        self.sp_bandpasshigh.setSuffix(QCoreApplication.translate("MainWindow", u" Hz", None))
#if QT_CONFIG(tooltip)
        self.label_17.setToolTip(QCoreApplication.translate("MainWindow", u"Determines steepness of the filter. Higher value can filter unwanted signals better, but requires more computation and can cause phase shifts.\n"
"Default is 2.", None))
#endif // QT_CONFIG(tooltip)
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Order (bandpass)", None))
        self.lbl_order.setText("")
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"Quality (notch)", None))
        self.lbl_quality.setText("")
#if QT_CONFIG(tooltip)
        self.btn_applyfilt.setToolTip(QCoreApplication.translate("MainWindow", u"Apply the filters to the stored data.\n"
"Note that after time frames have been applied in data selection, filters are no longer applicable.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_applyfilt.setText(QCoreApplication.translate("MainWindow", u"Apply filters", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_Raw), QCoreApplication.translate("MainWindow", u"Filters", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.Tab_Raw), QCoreApplication.translate("MainWindow", u"Filters.\n"
"Used for filtering your signal.\n"
"In the rightside plots, the fourier transform is displayed, this can be used as a guideline to filtering your signal.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btn_viewdatasel.setToolTip(QCoreApplication.translate("MainWindow", u"Show the selected data in the plot, but don't apply it to the stored data.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_viewdatasel.setText(QCoreApplication.translate("MainWindow", u"View data selection", None))
#if QT_CONFIG(tooltip)
        self.btn_applydatasel.setToolTip(QCoreApplication.translate("MainWindow", u"Apply the data selection to the stored data.\n"
"Note that after applying with time frames selected, filters can no longer be applied.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_applydatasel.setText(QCoreApplication.translate("MainWindow", u"Apply data selection", None))
#if QT_CONFIG(tooltip)
        self.btn_removetime.setToolTip(QCoreApplication.translate("MainWindow", u"Remove the last time frame", None))
#endif // QT_CONFIG(tooltip)
        self.btn_removetime.setText(QCoreApplication.translate("MainWindow", u"-", None))
#if QT_CONFIG(tooltip)
        self.label.setToolTip(QCoreApplication.translate("MainWindow", u"Fill in the time frames", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("MainWindow", u"Time frames", None))
#if QT_CONFIG(tooltip)
        self.btn_addtime.setToolTip(QCoreApplication.translate("MainWindow", u"Add another time frame.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_addtime.setText(QCoreApplication.translate("MainWindow", u"+", None))
#if QT_CONFIG(tooltip)
        self.btn_savedatasel.setToolTip(QCoreApplication.translate("MainWindow", u"Save the stored data.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_savedatasel.setText(QCoreApplication.translate("MainWindow", u"Save data", None))
#if QT_CONFIG(tooltip)
        self.label_5.setToolTip(QCoreApplication.translate("MainWindow", u"Select the channels.", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Channels", None))
        self.lbl_markers.setText(QCoreApplication.translate("MainWindow", u"Markers:", None))
        self.btn_loadmarkers_2.setText(QCoreApplication.translate("MainWindow", u"Load markers", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_DataSel), QCoreApplication.translate("MainWindow", u"Data selection", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.Tab_DataSel), QCoreApplication.translate("MainWindow", u"Data selection.\n"
"Used for selecting parts of your data to analyse, this can be done on a time and/or channel basis.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btn_savespikes.setToolTip(QCoreApplication.translate("MainWindow", u"Save the stored data.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_savespikes.setText(QCoreApplication.translate("MainWindow", u"Save data", None))
#if QT_CONFIG(tooltip)
        self.btn_spikesort.setToolTip(QCoreApplication.translate("MainWindow", u"Detect and sort spikes based on amplitude.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_spikesort.setText(QCoreApplication.translate("MainWindow", u"Sort spikes", None))
#if QT_CONFIG(tooltip)
        self.btn_removethreshold.setToolTip(QCoreApplication.translate("MainWindow", u"Remove the last threshold.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_removethreshold.setText(QCoreApplication.translate("MainWindow", u"-", None))
#if QT_CONFIG(tooltip)
        self.btn_addthreshold.setToolTip(QCoreApplication.translate("MainWindow", u"Add another threshold.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_addthreshold.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Thresholds", None))
        self.sps_thresholds.setSuffix(QCoreApplication.translate("MainWindow", u" A.U.", None))
        self.sp_cutoff.setSuffix(QCoreApplication.translate("MainWindow", u" A.U.", None))
        self.ch_cutoff.setText(QCoreApplication.translate("MainWindow", u"Cut-off threshold", None))
#if QT_CONFIG(tooltip)
        self.label_6.setToolTip(QCoreApplication.translate("MainWindow", u"Recurrence denotes the proportion of the thresholds the signal has to go below before searching for a new spike.", None))
#endif // QT_CONFIG(tooltip)
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Threshold recurrence", None))
#if QT_CONFIG(tooltip)
        self.btn_exportcsv.setToolTip(QCoreApplication.translate("MainWindow", u"Export cluster spike times as csv file.\n"
"Requires spike sorting data.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_exportcsv.setText(QCoreApplication.translate("MainWindow", u"Export as .csv", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_SpikeSorting), QCoreApplication.translate("MainWindow", u"Spike sorting", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.Tab_SpikeSorting), QCoreApplication.translate("MainWindow", u"Spike sorting.\n"
"Used for detecting and clustering of spikes.\n"
"Spikes can be detected and sorted on the basis of thresholds with a recurrence value.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btn_getwaveforms.setToolTip(QCoreApplication.translate("MainWindow", u"Show the average waveform plot per clusters.\n"
"Requires spike sorting data.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_getwaveforms.setText(QCoreApplication.translate("MainWindow", u"Average waveforms", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_AverageWaveform), QCoreApplication.translate("MainWindow", u"Average waveform", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.Tab_AverageWaveform), QCoreApplication.translate("MainWindow", u"Average waveform.\n"
"Used for viewing the average waveform of the clusters, which can be helpful in cluster evaluation.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btn_getisi.setToolTip(QCoreApplication.translate("MainWindow", u"Show the interspike interval.\n"
"Requires spikes sorting data.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_getisi.setText(QCoreApplication.translate("MainWindow", u"Interspike interval", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_ISI), QCoreApplication.translate("MainWindow", u"Interspike interval", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.Tab_ISI), QCoreApplication.translate("MainWindow", u"Interspike interval.\n"
"Used for checking the duration between spikes, which can be used for cluster evaluation.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btn_getamplitude.setToolTip(QCoreApplication.translate("MainWindow", u"Show the amplitude distribution.\n"
"Requires spike sorting data.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_getamplitude.setText(QCoreApplication.translate("MainWindow", u"Amplitude distribution", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_Amplitude), QCoreApplication.translate("MainWindow", u"Amplitude distribution", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.Tab_Amplitude), QCoreApplication.translate("MainWindow", u"Amplitude distribution.\n"
"Used for checking the distribution of the amplitudes per cluster, which can be used for cluster evalution.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btn_getautocorr.setToolTip(QCoreApplication.translate("MainWindow", u"Show the auto-correlation plot per clusters.\n"
"Requires spikes to be sorted.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_getautocorr.setText(QCoreApplication.translate("MainWindow", u"Auto-correlation", None))
#if QT_CONFIG(tooltip)
        self.label_8.setToolTip(QCoreApplication.translate("MainWindow", u"The time window in seconds after each spike in which other spikes are searched for.", None))
#endif // QT_CONFIG(tooltip)
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Timeframe after each spike", None))
        self.dsp_autotime.setSuffix(QCoreApplication.translate("MainWindow", u"s", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_Autocorr), QCoreApplication.translate("MainWindow", u"Auto-correlation", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.Tab_Autocorr), QCoreApplication.translate("MainWindow", u"Auto-correlation.\n"
"Used for spiketrain detection.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.label_9.setToolTip(QCoreApplication.translate("MainWindow", u"The time window in seconds before each spike in which other spikes are searched for.", None))
#endif // QT_CONFIG(tooltip)
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Time before and after each spike", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Cluster", None))
#if QT_CONFIG(tooltip)
        self.btn_getcrosscorr.setToolTip(QCoreApplication.translate("MainWindow", u"Show the cross-correlation plot between selected clusters/marker.\n"
"Requires spikes to be sorted.", None))
#endif // QT_CONFIG(tooltip)
        self.btn_getcrosscorr.setText(QCoreApplication.translate("MainWindow", u"Cross-correlation", None))
        self.dsp_crosstime.setSuffix(QCoreApplication.translate("MainWindow", u"s", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Channel/Marker", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_Crosscorr), QCoreApplication.translate("MainWindow", u"Cross-correlation", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.Tab_Crosscorr), QCoreApplication.translate("MainWindow", u"Cross-correlation.\n"
"Used for spiketrain detection between clusters.", None))
#endif // QT_CONFIG(tooltip)
        self.Btn_Previous.setText(QCoreApplication.translate("MainWindow", u"Previous", None))
        self.Btn_Next.setText(QCoreApplication.translate("MainWindow", u"Next", None))
        self.Btn_Exit.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
        self.menuMenu.setTitle(QCoreApplication.translate("MainWindow", u"Menu", None))
    # retranslateUi


if __name__=="__main__":
    app=QApplication(sys.argv)
    Main=QMainWindow()
    ui=Ui_MainWindow()
    ui.setupUi(Main)
    Main.show()
    sys.exit(app.exec())
