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
import os
import numpy as np
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from PyQt5.QtWidgets import (QMainWindow, QApplication, QSpinBox, QFileDialog,
                             QCheckBox, QLabel, QDoubleSpinBox, QMessageBox)
from modules.GUI.Ui_SpikeAnalysis import Ui_MainWindow
from modules.GUI import GUIFunctions
from core.pipeline import Pipeline
from core.engine import RecordingEngine
from core.controller import RecordingController
from modules.GUI.GUIRecording import RecordingTab
from settings.settings import SAMPLE_RATE, CHANNELS

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)
        #exit code, if set to one will restart the program
        self.exitcode=0
        #File name
        self.filename=""
        #Filters
        self.filt_highpass=1
        self.filt_lowpass=500
        self.filt_notch=50
        self.order=2
        self.quality=30
        #Time frames
        self.dsps_starttimes=[]
        self.dsps_stoptimes=[]
        self.lbls_timeto=[]
        self.lbls_timesec=[]
        #Channels
        self.cbs_channels=[]
        #Thresholds
        self.sps_thresholds=[self.sps_thresholds]
        #Threshold recurrence
        self.thr_recurrence=0.80
        #Auto-correlation time window
        self.autocorr_pretime=2.0
        self.autocorr_posttime=2.0
        #Cross-correlation time window and clusters
        self.crosscorr_pretime=2.0
        self.crosscorr_posttime=2.0
        self.crosscorr_clus1=[]
        self.crosscorr_clus2=[]
        
        #binsizes
        self.isi_bincount = 50
        self.ampdis_bincount = 50
        self.autocorr_bincount = 50
        self.crosscorr_bincount = 50
        
        #Data
        self.datatype=""
        self.data=[]
        self.time=[]
        self.clusters=[]
        self.markers=defaultdict(list)
        self.framerate=0
        self.history=[]
        self.identifier="001"
        self.channels=[]
        #All data
        self.SetFulldata()
        
        self.engine = RecordingEngine()
        self.controller = RecordingController(self.engine)
        self.recording_tab = RecordingTab(self.controller)
        self.tabWidget.insertTab(0, self.recording_tab, "Recording")
        
        #Plot canvasses
        self.cnvs_rawrecording=self.plt_container_raw.canvas
        self.cnvs_unfiltrecording=self.plt_container_unfilt.canvas
        self.cnvs_filtrecording=self.plt_container_filt.canvas
        self.cnvs_unfiltfft=self.plt_fft.canvas
        self.cnvs_filtfft=self.plt_fftfilt.canvas
        self.cnvs_datasel=self.plt_container_datasel.canvas
        self.cnvs_spikesort=self.plt_container_spike.canvas
        self.cnvs_spikesortpre=self.plt_sortingpreview.canvas

        self.Btn_Next.clicked.connect(self.NextTab)
        self.Btn_Previous.clicked.connect(self.PreviousTab)
        self.btn_import.clicked.connect(lambda: self.LoadData(True))
        self.actionImport_file.triggered.connect(lambda: self.LoadData(False))      
        self.plt_container_averagewaves=[]
        self.cnvss_averagewave=[]
        self.cnvs_isi=self.plt_container_isi.canvas
        self.cnvs_amplitudedis=self.plt_container_amplitude.canvas
        self.plt_container_autocorrs=[]
        self.cnvss_autocorr=[]
        self.cnvs_crosscorr=self.plt_container_crosscorr.canvas
        
        #Attach functions
        self.Btn_Next.clicked.connect(self.NextTab)
        self.Btn_Previous.clicked.connect(self.PreviousTab)
        self.btn_import.clicked.connect(lambda: self.LoadData(True))
        self.actionImport_file.triggered.connect(lambda: self.LoadData(False))
        self.btn_savefilt.clicked.connect(lambda: self.SaveData("filt"))
        self.btn_setfilters.clicked.connect(lambda: GUIFunctions.ViewFilter(self))
        self.btn_applyfilt.clicked.connect(self.ApplyFilters)
        self.btn_savedatasel.clicked.connect(lambda: self.SaveData("datasel"))
        self.btn_viewdatasel.clicked.connect(lambda: GUIFunctions.ViewDataSel(self))
        self.btn_applydatasel.clicked.connect(self.ApplyDataSel)
        self.btn_savespikes.clicked.connect(lambda: self.SaveData("spikesort"))
        self.btn_exportcsv.clicked.connect(self.ExportAsCSV)
        self.btn_spikesort.clicked.connect(self.SortSpikes)
        self.btn_addtime.clicked.connect(self.AddTimeFrame)
        self.btn_removetime.clicked.connect(self.RemoveTimeFrame)
        self.btn_addthreshold.clicked.connect(self.AddThreshold)
        self.btn_removethreshold.clicked.connect(self.RemoveThreshold)
        self.btn_loadmarkers.clicked.connect(self.LoadMarkers)
        self.btn_loadmarkers_2.clicked.connect(self.LoadMarkers)
        self.sp_framerate.valueChanged.connect(self.FramerateChange)
        self.sp_bandpasshigh.valueChanged.connect(self.HighpassChange)
        self.sp_bandpasslow.valueChanged.connect(self.LowpassChange)
        self.btn_getwaveforms.clicked.connect(lambda: GUIFunctions.AverageWaveform(self))
        self.btn_getisi.clicked.connect(lambda: GUIFunctions.InterSpikeInterval(self))
        self.btn_getamplitude.clicked.connect(lambda: GUIFunctions.AmplitudeDistribution(self))
        self.btn_getautocorr.clicked.connect(lambda: GUIFunctions.AutoCorrelation(self))
        self.btn_getcrosscorr.clicked.connect(lambda: GUIFunctions.CrossCorrelation(self))
        self.cb_crossch1.currentTextChanged.connect(self.CrosscorrSelectChange1)
        self.cb_crossch2.currentTextChanged.connect(self.CrosscorrSelectChange2)
        self.actionFile_history.triggered.connect(lambda: self.InfoMsg("History", "\n".join(self.history)))
        self.actionBatch_analysis.triggered.connect(self.BatchWindow)
        self.Btn_Exit.clicked.connect(self.close)
        self.actionReset.triggered.connect(self.Reset)
        
        #Set labels
        self.lbl_order.setText(str(self.order))
        self.lbl_quality.setText(str(self.quality))
        
        #Disable buttons that require data to be ran
        self.btn_loadmarkers.setEnabled(False)
        self.btn_loadmarkers_2.setEnabled(False)
        self.btn_savefilt.setEnabled(False)
        self.btn_savedatasel.setEnabled(False)
        self.btn_savespikes.setEnabled(False)
        self.btn_exportcsv.setEnabled(False)
        self.btn_getwaveforms.setEnabled(False)
        self.btn_getisi.setEnabled(False)
        self.btn_getamplitude.setEnabled(False)
        self.btn_getautocorr.setEnabled(False)
        self.btn_getcrosscorr.setEnabled(False)
        #Disable batch action, since that is not implemented by default
        self.actionBatch_analysis.setEnabled(False)
    
    def SetFulldata(self):
        self.fulldata={"Datatype": self.datatype,
                       "Data": self.data,
                       "Framerate": self.framerate,
                       "Time": self.time,
                       "Markers": dict(self.markers),
                       "Clusters": self.clusters,
                       "History": self.history,
                       "Channels": self.channels,
                       "Identifier": self.identifier}
    
    def NextTab(self):
        """Method to advance the displayed tab to the next one."""
        indx=self.tabWidget.currentIndex()
        self.tabWidget.setCurrentIndex(indx+1)
    def PreviousTab(self):
        """Method to advance the displayed tab to the previous one."""
        indx=self.tabWidget.currentIndex()
        self.tabWidget.setCurrentIndex(indx-1)
        
    def AddTimeFrame(self):
        """Method to add a timeframe to the Data selection tab."""
        self.gridLayout_4.removeItem(self.verticalSpacer_9)
        self.dsps_starttimes.append(QDoubleSpinBox(self.scrollAreaWidgetContents))
        self.dsps_stoptimes.append(QDoubleSpinBox(self.scrollAreaWidgetContents))
        self.lbls_timeto.append(QLabel(self.scrollAreaWidgetContents))
        self.lbls_timesec.append(QLabel(self.scrollAreaWidgetContents))
        self.dsps_starttimes[-1].setDecimals(3)
        self.dsps_starttimes[-1].setMaximum(999999999)
        self.dsps_stoptimes[-1].setDecimals(3)
        self.dsps_stoptimes[-1].setMaximum(999999999)
        self.gridLayout_4.addWidget(self.dsps_starttimes[-1], len(self.dsps_starttimes)+1, 0, 1, 1)
        self.gridLayout_4.addWidget(self.lbls_timeto[-1], len(self.dsps_starttimes)+1, 1, 1 ,1)
        self.gridLayout_4.addWidget(self.dsps_stoptimes[-1], len(self.dsps_starttimes)+1, 2, 1, 1)
        self.gridLayout_4.addWidget(self.lbls_timesec[-1], len(self.dsps_starttimes)+1, 3, 1, 1)
        self.gridLayout_4.addItem(self.verticalSpacer_9, len(self.dsps_starttimes)+2, 2, 1, 1)
        self.lbls_timeto[-1].setText("to")
        self.lbls_timesec[-1].setText("seconds")
    def RemoveTimeFrame(self):
        """Method to remove the last timeframe from the Data selection tab."""
        if len(self.dsps_starttimes):
            self.gridLayout_4.removeItem(self.verticalSpacer_9)
            self.gridLayout_4.removeWidget(self.dsps_starttimes[-1])
            self.gridLayout_4.removeWidget(self.lbls_timeto[-1])
            self.gridLayout_4.removeWidget(self.dsps_stoptimes[-1])
            self.gridLayout_4.removeWidget(self.lbls_timesec[-1])
            self.dsps_starttimes=self.dsps_starttimes[:-1]
            self.dsps_stoptimes=self.dsps_stoptimes[:-1]
            self.lbls_timesec=self.lbls_timesec[:-1]
            self.lbls_timeto=self.lbls_timeto[:-1]
            self.gridLayout_4.addItem(self.verticalSpacer_9, len(self.dsps_starttimes)+2, 2, 1, 1)
        
    def AddThreshold(self):
        """Method to add a threshold to the Spike sorting tab."""
        self.gridLayout_6.removeItem(self.verticalSpacer_3)
        self.sps_thresholds.append(QSpinBox(self.scrollAreaWidgetContents_2))
        self.gridLayout_6.addWidget(self.sps_thresholds[-1], len(self.sps_thresholds)+2, 0, 1, 1)
        self.sps_thresholds[-1].setSuffix(" A.U.")
        self.sps_thresholds[-1].setMaximum(999999999)
        self.sps_thresholds[-1].setMinimum(-999999999)
        self.gridLayout_6.addItem(self.verticalSpacer_3, len(self.sps_thresholds)+3, 1, 1, 1)
    def RemoveThreshold(self):
        """Method to remove the last threshold from the Spike sorting tab."""
        if len(self.sps_thresholds):
            self.gridLayout_6.removeItem(self.verticalSpacer_3)
            self.gridLayout_6.removeWidget(self.sps_thresholds[-1])
            self.sps_thresholds=self.sps_thresholds[:-1]
            self.gridLayout_6.addItem(self.verticalSpacer_3, len(self.sps_thresholds)+3, 1, 1, 1)
        
    def BatchWindow(self):
        """
        Method for batch analysis, not implemented by default.
        See the wiki for how to implement this.
            https://github.com/LukSullock/SpikeAnalysis/wiki/Adding-functionalities-to-the-Spike-Analysis-Tool
        """
    
    def LoadData(self, plotloadeddata=True):
        """
        Method to load in data. Imported file is chosen within the method.
        Prints the history to the console of the loaded data.

        Parameters
        ----------
        plotloadeddata : bool, optional
            Boolean to denote if the data should be immediately plotted, or only imported. The default is True.

        """
        #Pre-disable all buttons that are meant to be disabled when the required data isn't loaded
        self.btn_loadmarkers.setEnabled(False)
        self.btn_loadmarkers_2.setEnabled(False)
        self.btn_savefilt.setEnabled(False)
        self.btn_savedatasel.setEnabled(False)
        self.btn_savespikes.setEnabled(False)
        self.btn_exportcsv.setEnabled(False)
        self.btn_getwaveforms.setEnabled(False)
        self.btn_getisi.setEnabled(False)
        self.btn_getamplitude.setEnabled(False)
        self.btn_getautocorr.setEnabled(False)
        self.btn_getcrosscorr.setEnabled(False)
        
        self.btn_import.setEnabled(False)
        self.btn_import.setStyleSheet(u"background-color: rgb(93, 93, 93);")
        self.btn_import.repaint()
        filedialog=QFileDialog(self)
        filedialog.setWindowTitle("Open file...")
        filedialog.setNameFilters(["All (*.ssa *.wav)","Numpy archive (*.ssa)", "Audio file (*.wav)"])
        if filedialog.exec():
            self.btn_loadmarkers.setEnabled(True)
            self.btn_loadmarkers_2.setEnabled(True)
            file=filedialog.selectedFiles()[0]
            self.filename=file.split("/")[-1]
            direc=os.path.dirname(file)
            #filename is called in GUIFunctions, and data is set within GUIFunctions as well
            nomarker=GUIFunctions.ImportData(self, direc)
            self.history=list(self.history)
            if nomarker:
                self.lbl_markersloaded.setText("No markers")            
            else:
                self.lbl_markersloaded.setText("Markers loaded, see Data selection.")
            shape=self.data.shape
            self.lbl_filename.setText(str(self.filename))
            self.lbl_fileshape.setText(str(shape))
            self.sp_framerate.setValue(int(self.framerate))
            self.lbl_datatype.setText(str(self.datatype))
            self.le_identifier.setText(str(self.identifier))
            self.cb_channelsnr.clear()
            for ii,ch in enumerate(self.data):
                m = ch.mean(0)
                sd = ch.std(axis=0, ddof=0)
                SNR=abs(np.where(sd == 0, 0, m/sd))
                SNRtxt=Decimal(str(SNR))
                SNRtxt=SNRtxt.quantize(Decimal('0.0001'), ROUND_HALF_UP) #Proper rounding
                self.cb_channelsnr.addItem(f'Channel {ii+1}: {SNRtxt}')
            self.SetFulldata()
            #Add new channels in data selection tab
            for ii in reversed(range(len(self.cbs_channels))):
                self.cbs_channels[ii].setParent(None)
            self.cbs_channels=[QCheckBox(f'{self.channels[ii]}', self.scrollAreaWidgetContents_3) for ii in range(self.data.shape[0])]
            [cb.setChecked(True) for cb in self.cbs_channels]
            [self.verticalLayout.insertWidget(len(self.verticalLayout)-1, cb) for cb in self.cbs_channels]
            #Clear thresholds
            while self.sps_thresholds:
                self.RemoveThreshold()
            #Plot raw data in open recording tab, filters tab, and data selection tab
            if plotloadeddata:
                GUIFunctions.ViewRaw(self)
                GUIFunctions.ViewUnfilter(self)
                GUIFunctions.ViewDataSel(self)
                GUIFunctions.SpikeSortingNoThr(self)
                if len(self.clusters)!=0:
                    cutoff_thresh=False
                    recurrence=0.80
                    for his in self.history:
                        if "cut-off" in his:
                            cutoff_thresh=int(his.split(": ")[-1])
                            self.ch_cutoff.setChecked(True)
                            self.sp_cutoff.setValue(cutoff_thresh)
                        elif "thresholds" in his:
                            #Clear the thresholds in the GUI
                            while self.sps_thresholds:
                                self.RemoveThreshold()
                            thrstring=his.split(": ")[-1]
                            thresholds=[int(float(val)) for val in thrstring.split(", ")]
                            [self.AddThreshold() for _ in range(len(thresholds))]
                            [self.sps_thresholds[ii].setValue(val) for ii, val in enumerate(thresholds)]
                        elif "recurrence" in his:
                            recurrence=float(his.split(": ")[-1])
                            self.dsp_recurrence.setValue(recurrence)
                    GUIFunctions.SpikeSort(self, cutoff_thresh, recurrence)
                    self.btn_savespikes.setEnabled(True)
                    self.btn_exportcsv.setEnabled(True)
                    self.btn_getwaveforms.setEnabled(True)
                    self.btn_getisi.setEnabled(True)
                    self.btn_getamplitude.setEnabled(True)
                    self.btn_getautocorr.setEnabled(True)
                    self.btn_getcrosscorr.setEnabled(True)
                else:
                    [axis.remove() for axis in self.cnvs_spikesortpre.axs]
                    self.cnvs_spikesortpre.axs=[]
            else:
                [axis.remove() for axis in self.cnvs_rawrecording.axs]
                self.cnvs_rawrecording.axs=[]
                [axis.remove() for axis in self.cnvs_unfiltrecording.axs]
                self.cnvs_unfiltrecording.axs=[]
                [axis.remove() for axis in self.cnvs_unfiltfft.axs]
                self.cnvs_unfiltfft.axs=[]
                [axis.remove() for axis in self.cnvs_datasel.axs]
                self.cnvs_datasel.axs=[]
                [axis.remove() for axis in self.cnvs_spikesort.axs]
                self.cnvs_spikesort.axs=[]
                [axis.remove() for axis in self.cnvs_spikesortpre.axs]
                self.cnvs_spikesortpre.axs=[]
            #Clean all other plots
            [canvas.setParent(None) for canvas in self.cnvss_averagewave]
            self.cnvss_averagewave=[]
            self.plt_container_waveforms.clear()
            [axis.remove() for axis in self.cnvs_amplitudedis.axs]
            self.cnvs_amplitudedis.axs=[]
            [axis.remove() for axis in self.cnvs_crosscorr.axs]
            self.cnvs_crosscorr.axs=[]
            [axis.remove() for axis in self.cnvs_filtfft.axs]
            self.cnvs_filtfft.axs=[]
            [axis.remove() for axis in self.cnvs_filtrecording.axs]
            self.cnvs_filtrecording.axs=[]
            [axis.remove() for axis in self.cnvs_isi.axs]
            self.cnvs_isi.axs=[]
            #Add markers and channels to cross-correlation tab
            self.cb_crossch1.clear()
            self.cb_crossch2.clear()
            self.cb_crossch1.addItems(self.channels)
            self.cb_crossch1.addItems([f'Marker {key}' for key in self.markers.keys()])
            self.cb_crossch2.addItems(self.channels)
            self.cnvs_amplitudedis.draw()
            self.cnvs_crosscorr.draw()
            self.cnvs_filtfft.draw()
            self.cnvs_filtrecording.draw()
            self.cnvs_isi.draw()
            self.cnvs_spikesort.draw()
            self.cnvs_spikesortpre.draw()
            self.cnvs_rawrecording.draw()
            self.cnvs_unfiltrecording.draw()
            self.cnvs_unfiltfft.draw()
            self.cnvs_datasel.draw()
            print('Data history:')
            [print(his) for his in self.history]
            print()
        #Enable all buttons
        self.btn_import.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_import.setEnabled(True)
        self.btn_setfilters.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_setfilters.setEnabled(True)
        self.btn_applyfilt.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_applyfilt.setEnabled(True)
        self.btn_viewdatasel.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_viewdatasel.setEnabled(True)
        self.btn_applydatasel.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_applydatasel.setEnabled(True)
        self.btn_spikesort.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_spikesort.setEnabled(True)
        #Only reset the colour of the buttons that require specific data to be loaded
        self.btn_savefilt.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_savedatasel.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_savespikes.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_exportcsv.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_getwaveforms.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_getisi.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_getamplitude.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_getautocorr.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_getcrosscorr.setStyleSheet(u"background-color: rgb(0, 255, 0);")
    def LoadMarkers(self):
        """Method to load a marker file. Marker file to be imported is chosen within the method."""
        filedialog=QFileDialog(self)
        filedialog.setWindowTitle("Open file...")
        filedialog.setNameFilters(["Text file (*.txt)"])
        if filedialog.exec():
            file=filedialog.selectedFiles()[0]
            with open(file, encoding="utf8") as csvfile:
                markersCSV=np.genfromtxt(csvfile, delimiter=',')
            self.markers=defaultdict(list)
            for key in markersCSV:
                self.markers[key[0]].append(key[1])
            starttimes=[]
            stoptimes=[]
            for his in self.history:
                if "Data selection" in his:
                    starttimesstr=his.split(";")[-2]
                    stoptimesstr=his.split(";")[-1]
                    for start in starttimesstr.split(", "):
                        starttimes.append(float(start))
                    for stop in stoptimesstr.split(", "):
                        stoptimes.append(float(stop))
            _, self.markers=GUIFunctions.UpdateMarkers(self, starttimes, stoptimes, self.data)
            self.fulldata["Markers"]=self.markers
            GUIFunctions.ViewDataSel(self)
            self.cb_crossch1.clear()
            self.cb_crossch1.addItems(self.channels)
            self.cb_crossch1.addItems([f'Marker {key}' for key in self.markers.keys()])
            self.cb_crossch2.clear()
            self.cb_crossch2.addItems(self.channels)
    
    def ApplyFilters(self):
        """Method to call the function required to apply filters to the stored data."""
        self.btn_applyfilt.setEnabled(False)
        self.btn_applyfilt.setStyleSheet(u"background-color: rgb(93, 93, 93);")
        self.btn_applyfilt.repaint()
        GUIFunctions.ApplyFilter(self)
        self.btn_savefilt.setEnabled(True)
        self.btn_applyfilt.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_applyfilt.setEnabled(True)
    def ApplyDataSel(self):
        """Method to call the functions required to apply data selection to the stored data."""
        self.btn_applydatasel.setEnabled(False)
        self.btn_applydatasel.setStyleSheet(u"background-color: rgb(93, 93, 93);")
        self.btn_applydatasel.repaint()
        GUIFunctions.ApplyDataSel(self)
        self.cb_crossch1.clear()
        self.cb_crossch1.addItems(self.channels)
        self.cb_crossch1.addItems([f'Marker {key}' for key in self.markers.keys()])
        self.cb_crossch2.clear()
        self.cb_crossch2.addItems(self.channels)
        GUIFunctions.SpikeSortingNoThr(self)
        self.btn_savedatasel.setEnabled(True)
        self.btn_applydatasel.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_applydatasel.setEnabled(True)
    def SortSpikes(self):
        """Method to sort the spikes into clusters."""
        self.btn_spikesort.setEnabled(False)
        self.btn_spikesort.setStyleSheet(u"background-color: rgb(93, 93, 93);")
        self.btn_spikesort.repaint()
        #Get thresholds
        thresholds=[spbox.value() for spbox in self.sps_thresholds]
        #Raise warning if there are no thresholds selected
        if len(thresholds)==0:
            self.WarningMsg("Please select atleast 1 threshold.")
            self.btn_spikesort.setStyleSheet(u"background-color: rgb(0, 255, 0);")
            self.btn_spikesort.setEnabled(True)
            return
        #Remove duplicates
        thresholds=list(set(thresholds))
        #Sort the list from largest to smallest
        thresholds=sorted(thresholds, key=abs)
        thresholds=thresholds[::-1]
        #Get the cut off threshold if applicable
        if self.ch_cutoff.isChecked():
            cutoff_thresh=self.sp_cutoff.value()
        else:
            cutoff_thresh=False
        #Get spike data and sort into clusters
        GUIFunctions.SpikeData(self, thresholds, cutoff_thresh)
        #Plot spike sorting
        GUIFunctions.SpikeSort(self, cutoff_thresh, self.dsp_recurrence.value())
        self.CrosscorrSelectChange1()
        self.CrosscorrSelectChange2()
        #Update history
        thresholds=[str(clus[4][0]) for clus in self.clusters[0]]
        if cutoff_thresh:
            self.history.append(f'Spike sorting cut-off: {cutoff_thresh}')
        self.history.append(f'Spike sorting thresholds: {", ".join(thresholds)}')
        self.history.append(f'Spike sorting recurrence: {self.dsp_recurrence.value()}')
        #Enable save buttons
        self.btn_savespikes.setEnabled(True)
        self.btn_exportcsv.setEnabled(True)
        self.btn_getwaveforms.setEnabled(True)
        self.btn_getisi.setEnabled(True)
        #Enable buttons with functions dependent on cluster data
        self.btn_getamplitude.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_getamplitude.setEnabled(True)
        self.btn_getautocorr.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_getautocorr.setEnabled(True)
        self.btn_getcrosscorr.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_getcrosscorr.setEnabled(True)
        self.btn_spikesort.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_spikesort.setEnabled(True)
        
    def SaveData(self, extension):
        """
        Method to save the stored data.

        Parameters
        ----------
        extension : str
            String that will be appended to the output file by default as an identifier.

        """
        self.btn_savefilt.setEnabled(False)
        self.btn_savefilt.setStyleSheet(u"background-color: rgb(93, 93, 93);")
        self.btn_savefilt.repaint()
        self.btn_savedatasel.setEnabled(False)
        self.btn_savedatasel.setStyleSheet(u"background-color: rgb(93, 93, 93);")
        self.btn_savedatasel.repaint()
        self.btn_savespikes.setEnabled(False)
        self.btn_savespikes.setStyleSheet(u"background-color: rgb(93, 93, 93);")
        self.btn_savespikes.repaint()
        filedialog=QFileDialog(self)
        filedialog.setWindowTitle("Save file as...")
        filedialog.setNameFilter("Numpy archive (*.ssa)")
        filedialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        filedialog.selectFile(f'{self.filename[:-4]}_{extension}')
        if filedialog.exec():
            file=filedialog.selectedFiles()[0]
            GUIFunctions.SaveData(self, file)
        self.btn_savefilt.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_savefilt.setEnabled(True)
        self.btn_savedatasel.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_savedatasel.setEnabled(True)
        self.btn_savespikes.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_savespikes.setEnabled(True)
    def ExportAsCSV(self):
        """Method to export cluster data to a .csv file."""
        self.btn_exportcsv.setEnabled(False)
        self.btn_exportcsv.setStyleSheet(u"background-color: rgb(93, 93, 93);")
        self.btn_exportcsv.repaint()
        filedialog=QFileDialog(self)
        filedialog.setWindowTitle("Save file as...")
        filedialog.setNameFilter("Comma seperated file (*.csv)")
        filedialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        filedialog.selectFile(f'{self.filename[:-4]}_spikesorted')
        if filedialog.exec():
            file=filedialog.selectedFiles()[0]
            GUIFunctions.ExportAsCSV(self, file)
        self.btn_exportcsv.setStyleSheet(u"background-color: rgb(0, 255, 0);")
        self.btn_exportcsv.setEnabled(True)
    
    def FramerateChange(self):
        """Method to update the framerate."""
        self.framerate=self.sp_framerate.value()
        
    def HighpassChange(self):
        """Method to update the high-pass filter"""
        self.filt_highpass=self.sp_bandpasshigh.value()
    def LowpassChange(self):
        """Method to update the low-pass filter"""
        self.filt_lowpass=self.sp_bandpasslow.value()
    
    def CrosscorrSelectChange1(self):
        """Method to update the selectable clusters based on the selected channel of the first cluster."""
        if len(self.clusters)==0:
            return
        self.cb_crossch1.currentTextChanged.disconnect()
        self.cb_crosscl1.clear()
        if "Marker" not in self.cb_crossch1.currentText():
            self.cb_crosscl1.addItems([f'Cluster {clus[4][0]}' for clus in self.clusters[0]])
        self.cb_crossch1.currentTextChanged.connect(self.CrosscorrSelectChange1)
    def CrosscorrSelectChange2(self):
        """Method to update the selectable clusters based on the selected channel of the second cluster."""
        if len(self.clusters)==0:
            return
        self.cb_crossch2.currentTextChanged.disconnect()
        self.cb_crosscl2.clear()
        self.cb_crosscl2.addItems([f'Cluster {clus[4][0]}' for clus in self.clusters[0]])
        self.cb_crossch2.currentTextChanged.connect(self.CrosscorrSelectChange2)
    
    def WarningMsg(self, text, subtext=""):
        """
        QMessageBox to display a warning.

        Parameters
        ----------
        text : string
            Text to be displayed.
        subtext : string, optional
            Subtext to be displayed. The default is "".

        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(text)
        msg.setInformativeText(subtext)
        msg.setWindowTitle("Warning")
        msg.exec_()
    def InfoMsg(self, text, subtext=""):
        """
        QMessageBox to display some information

        Parameters
        ----------
        text : string
            Text to be displayed.
        subtext : string, optional
            Subtext to be displayed. The default is "".

        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setInformativeText(subtext)
        msg.setWindowTitle("Information")
        msg.exec_()
    
    def Reset(self):
        """Method to reset the GUI"""
        self.exitcode=1
        self.close()
    