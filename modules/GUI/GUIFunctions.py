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
import scipy as sp
import numpy as np
import pandas as pd
import itertools
import math
from copy import deepcopy
from PyQt5.QtWidgets import QCheckBox
from collections import defaultdict
from matplotlib.colors import TABLEAU_COLORS
from modules.GUI.QtMplCanvas import QtCanvas
from modules.analysis import SpikeFunctions

def ImportData(self, directory):
    self.data, self.clusters, self.markers, self.time, self.framerate, self.datatype, self.history, self.identifier, self.channels, nomarker=SpikeFunctions.OpenRecording(directory, self.filename)
    return nomarker

def ViewRaw(self):
    """Function to plot the raw data in the Import recording tab."""
    size=self.data.shape[0]
    #Plot raw data in the Import recording tab
    [axis.remove() for axis in self.cnvs_rawrecording.axs]
    self.cnvs_rawrecording.axs=[]
    self.cnvs_rawrecording.axs=[self.cnvs_rawrecording.fig.add_subplot(size,1,1)]
    [self.cnvs_rawrecording.axs.append(self.cnvs_rawrecording.fig.add_subplot(size,1,ii+2,sharex=self.cnvs_rawrecording.axs[0],sharey=self.cnvs_rawrecording.axs[0])) for ii in range(size-1)]
    [self.cnvs_rawrecording.axs[ii].plot(self.time, chdata, color="k") for ii,chdata in enumerate(self.data)]
    self.cnvs_rawrecording.fig.text(0.01, 0.5, "Amplitude (A.U.)", va="center", rotation="vertical")
    self.cnvs_rawrecording.fig.text(0.5, 0.02, "Time (s)", ha="center")
    self.cnvs_rawrecording.draw()

def ViewUnfilter(self):
    """Function to plot the unfiltered data and unfiltered FFT in the Filter data tab."""
    size=self.data.shape[0]
    #Plot unfiltered data in filters tab
    [axis.remove() for axis in self.cnvs_unfiltrecording.axs]
    self.cnvs_unfiltrecording.axs=[]
    self.cnvs_unfiltrecording.axs=[self.cnvs_unfiltrecording.fig.add_subplot(size,1,1)]
    [self.cnvs_unfiltrecording.axs.append(self.cnvs_unfiltrecording.fig.add_subplot(size,1,ii+2,sharex=self.cnvs_unfiltrecording.axs[0],sharey=self.cnvs_unfiltrecording.axs[0])) for ii in range(size-1)]
    [self.cnvs_unfiltrecording.axs[ii].plot(self.time, chdata, color="k") for ii,chdata in enumerate(self.data)]
    self.cnvs_unfiltrecording.fig.text(0.01, 0.5, "Amplitude (A.U.)", va="center", rotation="vertical")
    self.cnvs_unfiltrecording.fig.text(0.5, 0.02, "Time (s)", ha="center")
    #Plot unfiltered data fft in filters tab
    [axis.remove() for axis in self.cnvs_unfiltfft.axs]
    self.cnvs_unfiltfft.axs=[]
    self.cnvs_unfiltfft.axs=[self.cnvs_unfiltfft.fig.add_subplot(size,1,1)]
    [self.cnvs_unfiltfft.axs.append(self.cnvs_unfiltfft.fig.add_subplot(size,1,ii+2,sharex=self.cnvs_unfiltfft.axs[0],sharey=self.cnvs_unfiltfft.axs[0])) for ii in range(size-1)]
    for ii,chdata in enumerate(self.data):
        ndata=len(chdata)
        yfft=sp.fft.fft(chdata)
        xfft=sp.fft.fftfreq(ndata,1/self.framerate)[:ndata//2]
        self.cnvs_unfiltfft.axs[ii].plot(xfft, 2.0/ndata*np.abs(yfft[0:ndata//2]), color="k")
    self.cnvs_unfiltfft.fig.text(0.01, 0.5, "Power", va="center", rotation="vertical")
    self.cnvs_unfiltfft.fig.text(0.5, 0.02, "Frequency (Hz)", ha="center")
    self.cnvs_unfiltrecording.draw()
    self.cnvs_unfiltfft.draw()

def ViewFilter(self, quality=30, order=2):
    """
    Function to view the selected filters in the Filter data tab.

    Parameters
    ----------
    quality : int, optional
        Quality of the notch filter. Higher value has a narrower frequency filtering. The default is 30.
    order : int, optional
        Order of the high/low/band pass filters. Higher order results in a stronger filter. The default is 2.

    Returns
    -------
    filtdata : list
        List containing the filtered data.
    filters : list
        List containing the descriptions of the applied filters.

    """
    #Disable the button
    self.btn_setfilters.setEnabled(False)
    self.btn_setfilters.setStyleSheet(u"background-color: rgb(93, 93, 93);")
    self.btn_setfilters.repaint()
    size=self.data.shape[0]
    #Get filter settings and apply filters
    filtdata=deepcopy(self.data)
    filters=[]
    if self.ch_notch.isChecked():
        #Apply filter
        filtdata=SpikeFunctions.notchfilter(filtdata, self.framerate, quality, self.sp_notch.value())
        filters.append(f'Notch filter: {self.sp_notch.value()}; quality: {quality}; order: 2')
    if self.ch_highpass.isChecked() and self.ch_lowpass.isChecked():
        #Apply filter
        filtdata=SpikeFunctions.bandpassfilter(filtdata, self.framerate, order, [self.filt_highpass, self.filt_lowpass])
        filters.append(f'Bandpass filter: {self.filt_highpass}, {self.filt_lowpass}; order: {order}')
    elif self.ch_highpass.isChecked() and not self.ch_lowpass.isChecked():
        #Apply filter
        filtdata=SpikeFunctions.passfilter(filtdata, self.framerate, order, self.filt_highpass, "high")
        filters.append(f'Highpass filter: {self.filt_highpass}; order: {order}')
    elif not self.ch_highpass.isChecked() and self.ch_lowpass.isChecked():
        #Apply filter
        filtdata=SpikeFunctions.passfilter(filtdata, self.framerate, order, self.filt_lowpass, "low")
        filters.append(f'Lowpass filter: {self.filt_lowpass}; order: {order}')
    #Plot filtered data
    [axis.remove() for axis in self.cnvs_filtrecording.axs]
    self.cnvs_filtrecording.axs=[]
    self.cnvs_filtrecording.axs=[self.cnvs_filtrecording.fig.add_subplot(size,1,1)]
    [self.cnvs_filtrecording.axs.append(self.cnvs_filtrecording.fig.add_subplot(size,1,ii+2,sharex=self.cnvs_filtrecording.axs[0],sharey=self.cnvs_filtrecording.axs[0])) for ii in range(size-1)]
    [self.cnvs_filtrecording.axs[ii].plot(self.time, chdata, color="k") for ii,chdata in enumerate(filtdata)]
    self.cnvs_filtrecording.fig.text(0.01, 0.5, "Amplitude (A.U.)", va="center", rotation="vertical")
    self.cnvs_filtrecording.fig.text(0.5, 0.02, "Time (s)", ha="center")
    #Calculate and plot filtered fft
    [axis.remove() for axis in self.cnvs_filtfft.axs]
    self.cnvs_filtfft.axs=[]
    self.cnvs_filtfft.axs=[self.cnvs_filtfft.fig.add_subplot(size,1,1)]
    [self.cnvs_filtfft.axs.append(self.cnvs_filtfft.fig.add_subplot(size,1,ii+2,sharex=self.cnvs_filtfft.axs[0],sharey=self.cnvs_filtfft.axs[0])) for ii in range(size-1)]
    for ii,chdata in enumerate(filtdata):
        ndata=len(chdata)
        yfft=sp.fft.fft(chdata)
        xfft=sp.fft.fftfreq(ndata,1/self.framerate)[:ndata//2]
        self.cnvs_filtfft.axs[ii].plot(xfft, 2.0/ndata*np.abs(yfft[0:ndata//2]), color="k")
    self.cnvs_filtfft.fig.text(0.01, 0.5, "Power", va="center", rotation="vertical")
    self.cnvs_filtfft.fig.text(0.5, 0.02, "Frequency (Hz)", ha="center")
    self.cnvs_filtrecording.draw()
    self.cnvs_filtfft.draw()
    #Reenable the button
    self.btn_setfilters.setStyleSheet(u"background-color: rgb(0, 255, 0);")
    self.btn_setfilters.setEnabled(True)
    return filtdata, filters

def ApplyFilter(self):
    """Function to apply the filters to the stored data."""
    #Update non-filtered plot
    ViewUnfilter(self)
    #Get filtered data
    self.data, filters=ViewFilter(self)
    #Update data select plot
    data, _=ViewDataSel(self)
    if type(data)==bool:
        #Give warning that no channels are selected
        self.WarningMsg("Please select atleast one channel.")
        return
    #Update history
    [self.history.append(filt) for filt in filters]

def UpdateMarkers(self, starttimes, stoptimes, fdata):
    """
    Function to update the markers for the selected time frames and plot them in the Data selection tab.

    Parameters
    ----------
    starttimes : list
        List containing the start times of each time frame.
    stoptimes : list
        List containing the stop times of each time frame.
    fdata : list
        List containing the data.

    Returns
    -------
    vlines : list
        A list containing the values the time stamps and colour of the markers.
    markers : defaultdict
        Default dictionary containing the markers.

    """
    vlines=[]
    colours=itertools.cycle(TABLEAU_COLORS)
    markers=deepcopy(self.markers)
    clrlist=[]
    for marker in markers.keys():
        clr=next(colours)
        for ii in reversed(range(len(markers[marker]))):
            pop=True
            for jj, start in enumerate(starttimes):
                if markers[marker][ii]>=start/self.framerate and markers[marker][ii]<=stoptimes[jj]/self.framerate:
                    pop=False
            if pop: markers[marker].pop(ii)
        if len(markers[marker]):
            clrlist.append(clr)
    markers=defaultdict(list, {key: item for key, item in markers.items() if item})
    if not starttimes:
        markers=deepcopy(self.markers)
        colours=itertools.cycle(TABLEAU_COLORS)
        clrlist=[next(colours) for _ in markers.keys()]
    for ii,key in enumerate(markers.keys()):
        clr=clrlist[ii]
        if len(markers[key])==1:
            vlines.append([markers[key], clr])
        else:
            [vlines.append([submark,clr]) for submark in markers[key]]
    #Plot markers
    [[self.cnvs_datasel.axs[ii].axvline(line[0], color=line[1]) for line in vlines] for ii,_ in enumerate(fdata)]
    self.cnvs_datasel.draw()
    #Add marker time stamps to the marker string
    colours=itertools.cycle(TABLEAU_COLORS)
    self.lbl_markers.setText(f"Markers:\n{'\n'.join([f'{key}, {next(colours)[4:]}: {[float(mark) for mark in self.markers[key]]}' for key in self.markers.keys()])}")
    return vlines, markers

def ViewDataSel(self):
    """
    Function to show the selected channels and time frames in the Data selection tab.

    Returns
    -------
    fdata : list
        List containing the data.
    markers : defaultdict
        Default dictionary containing the markers.

    """
    self.btn_viewdatasel.setEnabled(False)
    self.btn_viewdatasel.setStyleSheet(u"background-color: rgb(93, 93, 93);")
    self.btn_viewdatasel.repaint()
    #Get data selections to in function data
    chdata=deepcopy(self.data)
    channelsel=[True if cb.isChecked() else False for cb in self.cbs_channels]
    starttimes=[dsp.value()*self.framerate for dsp in self.dsps_starttimes]
    stoptimes=[dsp.value()*self.framerate for dsp in self.dsps_stoptimes]
    if not any(channelsel):
        return False
    #Apply data selections to in function data
    chdata=np.array([chdata[ii] for ii, val in enumerate(channelsel) if val])
    fdata=np.empty((len(chdata), len(chdata[0])))
    fdata[:]=np.nan
    for ii,starttime in enumerate(starttimes):
        for jj,chan in enumerate(chdata):
            fdata[jj][int(starttime):int(stoptimes[ii])]=chan[int(starttime):int(stoptimes[ii])]
    if not starttimes:
        fdata=chdata
    #Clear plots, and plot data in data selection tab
    size=fdata.shape[0]
    [axis.remove() for axis in self.cnvs_datasel.axs]
    self.cnvs_datasel.axs=[]
    self.cnvs_datasel.axs=[self.cnvs_datasel.fig.add_subplot(size,1,1)]
    [self.cnvs_datasel.axs.append(self.cnvs_datasel.fig.add_subplot(size,1,ii+2,sharex=self.cnvs_datasel.axs[0],sharey=self.cnvs_datasel.axs[0])) for ii in range(size-1)]
    [self.cnvs_datasel.axs[ii].plot(self.time, chdata, color="k") for ii,chdata in enumerate(fdata)]
    self.cnvs_datasel.fig.text(0.01, 0.5, "Amplitude (A.U.)", va="center", rotation="vertical")
    self.cnvs_datasel.fig.text(0.5, 0.02, "Time (s)", ha="center")
    vlines, markers=UpdateMarkers(self, starttimes, stoptimes, fdata)
    self.btn_viewdatasel.setStyleSheet(u"background-color: rgb(0, 255, 0);")
    self.btn_viewdatasel.setEnabled(True)
    return fdata, markers

def ApplyDataSel(self):
    """Function to apply the selected channels and time frames to the data."""
    #Get data selection
    data, markers=ViewDataSel(self)
    if type(data)==bool:
        #Give warning that no channels are selected
        self.WarningMsg("Please select atleast one channel.")
        return
    self.data=data
    #Update channel names
    channelsel=[True if cb.isChecked() else False for cb in self.cbs_channels]
    self.channels=np.array([str(self.channels[ii]) for ii, val in enumerate(channelsel) if val])
    #Add new channels in data selection tab
    for ii in reversed(range(len(self.cbs_channels))):
        self.cbs_channels[ii].setParent(None)
    self.cbs_channels=[QCheckBox(f'{self.channels[ii]}', self.scrollAreaWidgetContents_3) for ii in range(self.data.shape[0])]
    [cb.setChecked(True) for cb in self.cbs_channels]
    [self.verticalLayout.insertWidget(len(self.verticalLayout)-1, cb) for cb in self.cbs_channels]
    #Update markers
    self.markers=markers
    colours=itertools.cycle(TABLEAU_COLORS)
    self.lbl_markers.setText(f"Markers:\n{'\n'.join([f'{key}, {next(colours)[4:]}: {self.markers[key]}' for key in self.markers.keys()])}")
    starttimes=[dsp.value()*self.framerate for dsp in self.dsps_starttimes]
    stoptimes=[dsp.value()*self.framerate for dsp in self.dsps_stoptimes]
    UpdateMarkers(self, starttimes, stoptimes, self.data)
    #Update history
    starttimes=[str(time) for time in starttimes]
    stoptimes=[str(time) for time in stoptimes]
    self.history.append(f'Data selection: {", ".join([str(ch) for ch in channelsel])}; {", ".join(starttimes)}; {", ".join(stoptimes)}')


def SpikeSortingNoThr(self):
    """Function to Plot the data from Data selection in the Spike Sorting plot"""
    self.btn_spikesort.setEnabled(False)
    self.btn_spikesort.setStyleSheet(u"background-color: rgb(93, 93, 93);")
    self.btn_spikesort.repaint()
    #Clear plot, then plot data in spike sorting tab
    size=self.data.shape[0]
    [axis.remove() for axis in self.cnvs_spikesort.axs]
    self.cnvs_spikesort.axs=[]
    self.cnvs_spikesort.axs=[self.cnvs_spikesort.fig.add_subplot(size,1,1)]
    [self.cnvs_spikesort.axs.append(self.cnvs_spikesort.fig.add_subplot(size,1,ii+2,sharex=self.cnvs_spikesort.axs[0],sharey=self.cnvs_spikesort.axs[0])) for ii in range(size-1)]
    [self.cnvs_spikesort.axs[ii].plot(self.time, chdata, color="k") for ii,chdata in enumerate(self.data)]
    
    #Plot markers
    vlines=[]
    colours=itertools.cycle(TABLEAU_COLORS)
    for ii,key in enumerate(self.markers.keys()):
        clr=next(colours)
        if len(self.markers[key])==1:
            vlines.append([self.markers[key], clr])
        else:
            [vlines.append([submark,clr]) for submark in self.markers[key]]
    [[self.cnvs_spikesort.axs[ii].axvline(line[0], color=line[1]) for line in vlines] for ii,_ in enumerate(self.data)]
    self.cnvs_spikesort.fig.text(0.01, 0.5, "Amplitude (A.U.)", va="center", rotation="vertical")
    self.cnvs_spikesort.fig.text(0.5, 0.02, "Time (s)", ha="center")
    self.cnvs_spikesort.draw()
    self.btn_spikesort.setStyleSheet(u"background-color: rgb(0, 255, 0);")
    self.btn_spikesort.setEnabled(True)

def SpikeData(self, thresholds, cutoff_thresh):
    self.clusters=SpikeFunctions.SpikeSorting(self.data, thresholds, self.dsp_recurrence.value(), self.framerate, self.time, cutoff_thresh)

def SpikeSort(self, cutoff, recurrence=0.80):
    """
    Function to plot the cluster data in the Spike sorting tab.

    Parameters
    ----------
    cutoff : int
        The cut-off threshold. Can be negative or positive. Can be set to 0 or False if no cut-off threshold is desired.
    recurrence : float, optional
        The proportion of the threshold the signal needs to go below, before looking for the next spike. The default is 0.80.

    """
    thresholds=[]
    #If there is a cutoff threshold, make it an array, containing the value and the colour red
    if cutoff:
        thresholds.append([cutoff, "r"])
    colours=itertools.cycle(TABLEAU_COLORS)
    for clus in self.clusters[0]:
        thresholds.append([clus[4][0], next(colours)])
    #Clear plot, then plot data in spike sorting tab
    size=self.data.shape[0]
    [axis.remove() for axis in self.cnvs_spikesort.axs]
    self.cnvs_spikesort.axs=[]
    self.cnvs_spikesort.axs=[self.cnvs_spikesort.fig.add_subplot(size,1,1)]
    [self.cnvs_spikesort.axs.append(self.cnvs_spikesort.fig.add_subplot(size,1,ii+2,sharex=self.cnvs_spikesort.axs[0],sharey=self.cnvs_spikesort.axs[0])) for ii in range(size-1)]
    [self.cnvs_spikesort.axs[ii].plot(self.time, chdata, color="k") for ii,chdata in enumerate(self.data)]
    #Plot markers
    vlines=[]
    colours=itertools.cycle(TABLEAU_COLORS)
    for ii,key in enumerate(self.markers.keys()):
        clr=next(colours)
        if len(self.markers[key])==1:
            vlines.append([self.markers[key], clr])
        else:
            [vlines.append([submark,clr]) for submark in self.markers[key]]
    [[self.cnvs_spikesort.axs[ii].axvline(line[0], color=line[1]) for line in vlines] for ii,_ in enumerate(self.data)]
    #Plot clusters
    for ii, chan in enumerate(self.clusters):
        for jj, clus in enumerate(chan):
            self.cnvs_spikesort.axs[ii].scatter(clus[1], clus[3], color=thresholds[jj][1], marker='o', label=f'Cluster {clus[4][0]}')
    [self.cnvs_spikesort.axs[ii].legend(frameon=False) for ii, _ in enumerate(self.cnvs_spikesort.axs)]
    self.cnvs_spikesort.fig.text(0.01, 0.5, "Amplitude (A.U.)", va="center", rotation="vertical")
    self.cnvs_spikesort.fig.text(0.5, 0.02, "Time (s)", ha="center")
    #Plot data in spike sorting preview tab
    [axis.remove() for axis in self.cnvs_spikesortpre.axs]
    self.cnvs_spikesortpre.axs=[]
    self.cnvs_spikesortpre.axs=[self.cnvs_spikesortpre.fig.add_subplot(size,1,1)]
    [self.cnvs_spikesortpre.axs.append(self.cnvs_spikesortpre.fig.add_subplot(size,1,ii+2,sharex=self.cnvs_spikesortpre.axs[0],sharey=self.cnvs_spikesortpre.axs[0])) for ii in range(size-1)]
    [self.cnvs_spikesortpre.axs[ii].plot(self.time, chdata, color="k") for ii,chdata in enumerate(self.data)]
    #Plot markers
    vlines=[]
    for ii,key in enumerate(self.markers.keys()):
        clr=next(colours)
        if len(self.markers[key])==1:
            vlines.append([self.markers[key], clr])
        else:
            [vlines.append([submark,clr]) for submark in self.markers[key]]
    [[self.cnvs_spikesortpre.axs[ii].axvline(line[0], color=line[1]) for line in vlines] for ii,_ in enumerate(self.data)]
    #Plot clusters
    for ii, chan in enumerate(self.clusters):
        colours=itertools.cycle(TABLEAU_COLORS)
        for jj, clus in enumerate(chan):
            self.cnvs_spikesortpre.axs[ii].scatter(clus[1], clus[2], color=thresholds[jj][1], marker='o')
    #Plot thresholds, and cut-off threshold
    for line in thresholds:
        for ii in range(size):
            self.cnvs_spikesortpre.axs[ii].axhline(line[0], color=line[1])
    self.cnvs_spikesortpre.fig.text(0.01, 0.5, "Amplitude (A.U.)", va="center", rotation="vertical")
    self.cnvs_spikesortpre.fig.text(0.5, 0.02, "Time (s)", ha="center")
    #Update plots
    self.cnvs_spikesort.draw()
    self.cnvs_spikesortpre.draw()

def AverageWaveform(self, min_val=5, max_val=10):
    """
    Function to plot the average waveforms in the Average waveforms tab.
    Each cluster gets its own tab with a plot within the Average waveforms tab.
    Every plot contains all the applicable waveforms, their average, and the standard deviation.

    Parameters
    ----------
    min_val : int, optional
        Integer denoting the miliseconds before the spike that are plotted. The default is 5.
    max_val : int, optional
        Integer denoting the miliseconds after the spike that are plotted. The default is 10.

    """
    self.btn_getwaveforms.setEnabled(False)
    self.btn_getwaveforms.setStyleSheet(u"background-color: rgb(93, 93, 93);")
    self.btn_getwaveforms.repaint()
    #Clear canvasses and tabs
    [canvas.setParent(None) for canvas in self.cnvss_averagewave]
    self.cnvss_averagewave=[]
    self.plt_container_averagewaves=[]
    self.plt_container_waveforms.clear()
    colours=itertools.cycle(TABLEAU_COLORS)
    #Set up x-axis points
    wvf_x=np.arange(-min_val, max_val, 1/(self.framerate/1000))
    for ii, channel in enumerate(self.clusters):
        for clus in channel:
            #Inititiate empty lists for waveform data
            all_wvf_cl=[]
            all_wvf_cl_std=[]
            wvf_y=np.zeros(wvf_x.shape)+np.nan
            #Get y-values for every spike in the cluster
            for spike in clus[1]:
                spike=spike[~np.isnan(spike)]
                if spike.size>0:
                    wvf_y=self.data[ii][int(spike*self.framerate-(min_val*self.framerate/1000)):int(spike*self.framerate+(max_val*self.framerate/1000))]
                    if len(wvf_y)==len(wvf_x):
                        all_wvf_cl.append([wvf_y, 0.5, 0.3, next(colours)])
            #Add mean and standard deviation then plot the data, if there is any
            self.plt_container_averagewaves.append(QtCanvas(self.plt_container_waveforms))
            self.cnvss_averagewave.append(self.plt_container_averagewaves[-1].canvas)
            self.cnvss_averagewave[-1].axs=[self.cnvss_averagewave[-1].fig.add_subplot(1,1,1)]
            text=[]
            if all_wvf_cl:
                all_wvf_cl.append([np.nanmean([vals[0] for vals in all_wvf_cl], axis=0), 2, 1, 'r'])
                all_wvf_cl_std=np.nanstd([vals[0] for vals in all_wvf_cl], axis=0)
                for line in all_wvf_cl:
                    self.cnvss_averagewave[-1].axs[0].plot(wvf_x, line[0], lw=line[1], alpha=line[2], color=line[3])
                self.cnvss_averagewave[-1].axs[0].plot(wvf_x, all_wvf_cl[-1][0]-all_wvf_cl_std, lw=1.5, alpha=1, color="orange")
                self.cnvss_averagewave[-1].axs[0].plot(wvf_x, all_wvf_cl[-1][0]+all_wvf_cl_std, lw=1.5, alpha=1, color="orange")
            #If there is no data, plot text notifying the user of that.
            else:
                text.append(f"Not enough data\nGot {len(all_wvf_cl)} datapoints\nAtleast 1 datapoint is required.")
                self.cnvss_averagewave[-1].axs[0].text(0.5, 0.6, text[-1],
                                                       horizontalalignment="center",
                                                       verticalalignment="center")
            self.plt_container_waveforms.addTab(self.plt_container_averagewaves[-1], f'{self.fulldata["Channels"][ii]} Cluster {clus[4][0]}')
            self.cnvss_averagewave[-1].fig.text(0.01, 0.5, "Amplitude (A.U.)", va="center", rotation="vertical")
            self.cnvss_averagewave[-1].fig.text(0.5, 0.02, "Time (ms)", ha="center")
            self.cnvss_averagewave[-1].draw()
    self.btn_getwaveforms.setEnabled(True)
    self.btn_getwaveforms.setStyleSheet(u"background-color: rgb(0, 255, 0);")

def InterSpikeInterval(self):
    """Function to plot the interspike interval in the Interspike interval tab."""
    self.btn_getisi.setEnabled(False)
    self.btn_getisi.setStyleSheet(u"background-color: rgb(93, 93, 93);")
    self.btn_getisi.repaint()
    #Clear plot and add subplots
    size=self.data.shape[0]
    [axis.remove() for axis in self.cnvs_isi.axs]
    self.cnvs_isi.axs=[]
    self.cnvs_isi.axs=[self.cnvs_isi.fig.add_subplot(size,1,1)]
    [self.cnvs_isi.axs.append(self.cnvs_isi.fig.add_subplot(size,1,ii+2,sharex=self.cnvs_isi.axs[0],sharey=self.cnvs_isi.axs[0])) for ii in range(size-1)]
    #Extract timestamps of spikes and convert them to milliseconds
    spike_times=[[[x*1000 for x in cl[1] if ~np.isnan(x)] for cl in chan] for chan in self.clusters]
    #Interspike intervals
    isispike_times=[[np.diff(cl) for cl in chan] for chan in spike_times]
    #Create bins and weights if there are any values
    if any([any([any(cl) for cl in chan]) for chan in isispike_times]):
        maxval=[[max(cl, default=100) for cl in chan] for chan in isispike_times]
        maxval=int(math.ceil(max(sum(maxval, []))/100))*100
        bins=np.logspace(np.log10(1),np.log10(maxval), self.isi_bincount)
        weights=[[np.ones_like(spikeset)/len(spikeset) for spikeset in ch] for ch in isispike_times]
    #Plot interspike intervals
    for ii, chan in enumerate(isispike_times):
        colours=itertools.cycle(TABLEAU_COLORS)
        for jj, spikeset in enumerate(chan):
            if len(spikeset):
                self.cnvs_isi.axs[ii].hist(spikeset, bins, weights=weights[ii][jj], color=next(colours), alpha=0.5, label=f'{self.fulldata["Channels"][ii]} Cluster {self.clusters[ii][jj][4][0]}', ec='black')
                self.cnvs_isi.axs[ii].set_xscale('log')
                self.cnvs_isi.axs[ii].legend(frameon=False)
                self.cnvs_isi.fig.text(0.01, 0.5, "Normalised distribution", va="center", rotation="vertical")
                self.cnvs_isi.fig.text(0.5, 0.02, "Interspike interval (ms)", ha="center")
    self.cnvs_isi.draw()
    self.btn_getisi.setEnabled(True)
    self.btn_getisi.setStyleSheet(u"background-color: rgb(0, 255, 0);")

def AmplitudeDistribution(self):
    """Function to plot the amplitude distribution in the Amplitude distribution tab."""
    self.btn_getamplitude.setEnabled(False)
    self.btn_getamplitude.setStyleSheet(u"background-color: rgb(93, 93, 93);")
    self.btn_getamplitude.repaint()
    #Clear plot and add subplots
    size=self.data.shape[0]
    [axis.remove() for axis in self.cnvs_amplitudedis.axs]
    self.cnvs_amplitudedis.axs=[]
    self.cnvs_amplitudedis.axs=[self.cnvs_amplitudedis.fig.add_subplot(size,1,1)]
    [self.cnvs_amplitudedis.axs.append(self.cnvs_amplitudedis.fig.add_subplot(size,1,ii+2,sharex=self.cnvs_amplitudedis.axs[0],sharey=self.cnvs_amplitudedis.axs[0])) for ii in range(size-1)]
    #Extract peak heights
    spike_amp_cl = [[[x for x in cl[2] if ~np.isnan(x)] for cl in chan] for chan in self.clusters]
    #Create bins and weights if there are any values
    if any([any([any(cl) for cl in chan]) for chan in spike_amp_cl]):
        maxval=[[max(cl, default=100) for cl in chan] for chan in spike_amp_cl]
        maxval=int(math.ceil(max(sum(maxval, []))/100))*100
        minval=[[min(cl, default=100) for cl in chan] for chan in spike_amp_cl]
        minval=int(math.floor(min(sum(minval, []))/100))*100
        bins=np.linspace(minval, maxval, self.ampdis_bincount)
        weights=[[np.ones_like(spikeset)/len(spikeset) for spikeset in ch] for ch in spike_amp_cl]
    #Plot amplitude distribution
    for ii, chan in enumerate(spike_amp_cl):
        colours=itertools.cycle(TABLEAU_COLORS)
        for jj, spikeset in enumerate(chan):
            if len(spikeset):
                self.cnvs_amplitudedis.axs[ii].hist(spikeset, bins, weights=weights[ii][jj], color=next(colours), alpha=0.5, label=f'{self.fulldata["Channels"][ii]} Cluster {self.clusters[ii][jj][4][0]}', ec='black')
                self.cnvs_amplitudedis.axs[ii].legend(frameon=False)
                self.cnvs_amplitudedis.fig.text(0.01, 0.5, "Normalised distribution", va="center", rotation="vertical")
                self.cnvs_amplitudedis.fig.text(0.5, 0.02, "Amplitude distribution (A.U.)", ha="center")
    self.cnvs_amplitudedis.draw()
    self.btn_getamplitude.setEnabled(True)
    self.btn_getamplitude.setStyleSheet(u"background-color: rgb(0, 255, 0);")

def AutoCorrelation(self):
    """
    Function to plot the auto-correlation for every cluster in the Auto-correlation tab.
    Every plot has their own tab within the Auto-correlation tab
    The time interval is directly taken from the GUI.

    """
    self.btn_getautocorr.setEnabled(False)
    self.btn_getautocorr.setStyleSheet(u"background-color: rgb(93, 93, 93);")
    self.btn_getautocorr.repaint()
    #Clear plots
    [canvas.setParent(None) for canvas in self.cnvss_autocorr]
    self.cnvss_autocorr=[]
    self.plt_container_autocorrs=[]
    self.plt_container_autocorr.clear()
    #Get window time value
    intervalsize=self.dsp_autotime.value()
    #Extract timestamps of spikes and convert to location
    spike_times=[[[x*1000 for x in cl[1] if ~np.isnan(x)] for cl in chan] for chan in self.clusters]
    #Calculate the autocorrelation per cluster per channel
    autocorr = [[SpikeFunctions.cross_correlate(spikeset, spikeset, intervalsize*1000, self.autocorr_bincount) for spikeset in chan] for chan in spike_times]
    peakcounts=[[0 for cl in chan] for chan in autocorr]
    #Calculate total peaks and set the 0ms to 0 peaks for better readability
    for ii,chan in enumerate(autocorr):
        for jj,cl in enumerate(chan):
            peakcounts[ii][jj]=cl[int(len(cl)/2)]
            autocorr[ii][jj][int(len(cl)/2)]=0
    #Plot auto-correlations
    for ii, chan in enumerate(autocorr):
        for jj, spikeset in enumerate(chan):
            if len(spikeset):
                self.plt_container_autocorrs.append(QtCanvas(self.plt_container_autocorr))
                self.cnvss_autocorr.append(self.plt_container_autocorrs[-1].canvas)
                self.cnvss_autocorr[-1].axs=[self.cnvss_autocorr[-1].fig.add_subplot(1,1,1)]
                self.plt_container_autocorr.addTab(self.plt_container_autocorrs[-1], f'{self.fulldata["Channels"][ii]} Cluster {self.clusters[ii][jj][4][0]}')
                #change x values to corresponding bin sizes when bins are implemented
                self.cnvss_autocorr[-1].axs[0].plot(np.arange(0, spikeset.size/2-1), spikeset[int(spikeset.size/2):-1], color="k")
                self.cnvss_autocorr[-1].fig.text(0.01, 0.5, "# of spikes", va="center", rotation="vertical")
                self.cnvss_autocorr[-1].fig.text(0.5, 0.02, "Time (ms)", ha="center")
                #self.cnvss_autocorr[-1].axs[0].set_title(0.05, 0.93, f'N={peakcounts[ii][jj]}', transform=self.cnvss_autocorr[-1].axs[0].transAxes)
                self.cnvss_autocorr[-1].axs[0].set_title(f'N={peakcounts[ii][jj]}')
                self.cnvss_autocorr[-1].draw()
    self.btn_getautocorr.setEnabled(True)
    self.btn_getautocorr.setStyleSheet(u"background-color: rgb(0, 255, 0);")

def CrossCorrelation(self):
    """
    Function to plot the cross-correlation in the Cross-correlation tab.
    Chosen clusters and time interval to plot are taken directly from the GUI.

    """
    self.btn_getcrosscorr.setEnabled(False)
    self.btn_getcrosscorr.setStyleSheet(u"background-color: rgb(93, 93, 93);")
    self.btn_getcrosscorr.repaint()
    #Clear plot
    [axis.remove() for axis in self.cnvs_crosscorr.axs]
    self.cnvs_crosscorr.axs=[]
    self.cnvs_crosscorr.axs=[self.cnvs_crosscorr.fig.add_subplot(1,1,1)]
    #Get window time value
    intervalsize=self.dsp_crosstime.value()
    #Get cross-correlation clusters
    if "Marker" in self.cb_crossch1.currentText():
        spikeset1=self.markers[float(self.cb_crossch1.currentText().split("Marker ")[-1])]
        spikeset1=np.array([spike*1000 for spike in spikeset1])
    else:
        clusterlist=np.array([f'Cluster {clus[4][0]}' for clus in self.clusters[0]])
        channelindx=np.where(self.channels==self.cb_crossch1.currentText())[0][0]
        clusterindx=np.where(clusterlist==self.cb_crosscl1.currentText())[0][0]
        spikeset1=np.array([x*1000 for x in self.clusters[channelindx][clusterindx][1] if ~np.isnan(x)])
    #Get cluster indices
    clusterlist=np.array([f'Cluster {clus[4][0]}' for clus in self.clusters[0]])
    channelindx=np.where(self.channels==self.cb_crossch2.currentText())[0][0]
    clusterindx=np.where(clusterlist==self.cb_crosscl2.currentText())[0][0]
    spikeset2=np.array([x*1000 for x in self.clusters[channelindx][clusterindx][1] if ~np.isnan(x)])
    #Calculate cross-correlation
    #Add preinterval
    cross_corr=SpikeFunctions.cross_correlate(spikeset1, spikeset2, intervalsize*1000, self.crosscorr_bincount)
    #Plot cross-correlation
    #change x values to corresponding bin sizes when bins are implemented
    self.cnvs_crosscorr.axs[0].plot(np.arange(-cross_corr.size/2, cross_corr.size/2)+0.5, cross_corr, color="k")
    self.cnvs_crosscorr.fig.text(0.01, 0.5, "# of spikes", va="center", rotation="vertical")
    self.cnvs_crosscorr.fig.text(0.5, 0.02, "Time (ms)", ha="center")
    self.cnvs_crosscorr.draw()
    self.btn_getcrosscorr.setEnabled(True)
    self.btn_getcrosscorr.setStyleSheet(u"background-color: rgb(0, 255, 0);")

def SaveData(self, file):
    """
    Function to save the stored data to a file.

    Parameters
    ----------
    extension : str
        String that denotes the save file location.

    """
    savehis=np.empty(len(self.history), dtype=type(np.array))
    maxhislen=0
    for his in self.history:
        if len(str(his))>maxhislen:
            maxhislen=len(str(his))
    for ii, _ in enumerate(self.history):
        savehis[ii]=np.array(self.history[ii], dtype=f'U{maxhislen}')
    self.SetFulldata()
    with open(file, 'wb') as f:
        np.savez(f, allow_pickle=True, **self.fulldata)
    print("data saved")

def ExportAsCSV(self, file):
    """
    Function to export cluster data to a .csv file.

    Parameters
    ----------
    file : str
        String that denotes the save file location.
        
    """
    self.SetFulldata()
    #Create dataframe with first column containing file info
    fdf=pd.DataFrame({"File info": [self.datatype, self.framerate, self.identifier]+self.history})
    #Add a columns per cluster with timestamps of spikes
    for ii,channel in enumerate(self.clusters):
        for clus in channel:
            sdf=pd.DataFrame({f'{self.fulldata["Channels"][ii]} Cluster {clus[4][0]}': clus[1][~np.isnan(clus[1])]})
            fdf=pd.concat([fdf,sdf], axis=1)
    fdf.to_csv(file, index=False)