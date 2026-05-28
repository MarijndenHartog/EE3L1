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
import numpy as np
import scipy as sp
import os
import traceback
from collections import defaultdict
from scipy.signal import butter, iirnotch, filtfilt


def OpenRecording(folder, filename):
    """
    Function to load in data and markers.
    Accepted file extensions are .wav, and .ssa.
    .ssa files are numpy archives with a custom .ssa extension.

    Parameters
    ----------
    folder : String
        String of the folder path from where to load the file.
    filename : String
        String of the filename including extension.

    Returns
    -------
    data : Array of int64
        Array containing y-values per channel.
    clusters : list
        A list containing all peaks above threshold height, timestamps of peaks, heights of peaks, height of spike marker per peak, and the threshold height per threshold per channel.
    markers : defaultdict
        Dictionary with marker numbers as keys, and marker time stamps as values.
    time : Array of float64
        Array containing x-values per channel. First index is channel, second contains x-values.
    framerate : int
        Sampling rate of the data.
    datatype : str
        String denoting the type of the data.
    history : list
        List containing all changes made to the original data.
    identifier : string
        String denoting the identifier of the data.
    channels : list
        List containing the available channels.
    nomarker : list
        Contains the FileNotFoundError traceback if there was no marker file found.

    """
    #Setup file paths and default information
    file = os.path.join(folder, filename)
    markername =f"{filename[:-4]}-events.txt"
    markerfile=os.path.join(folder, markername)
    defaults={"Datatype": "SpikerBox",
              "Data": [],
              "Markers": defaultdict(list),
              "Clusters": [],
              "Time": [],
              "Framerate": 10000,
              "History": [],
              "Identifier": "001",
              "Channels": []
              }
    if ".wav" in filename: #SpikeRecorder Data (Backyard Brains, SpikerBox)
        #import .wav file and corresponding marker file
        rec = sp.io.wavfile.read(file)
        nomarker=False
        try:
            with open(markerfile, encoding="utf8") as csvfile:
                markersCSV=np.genfromtxt(csvfile, delimiter=',')
        except FileNotFoundError:
            nomarker=[traceback.format_exc()]
            markersCSV=[]
        #setup data from import .wav file
        framerate = rec[0]
        if len(rec[1].shape)==1: #when single channel recording
            data=np.array([rec[1]])
            ch=1
        elif rec[1].shape[0]>rec[1].shape[1]: #check if axes need to be swapped
            data=np.swapaxes(rec[1], 0, 1)
            ch=rec[1].shape[1]
        else:
            data=rec[1]
            ch=rec[1].shape[0]
        nframes = np.size(data, 1)
        time = np.array([x/framerate for x in np.arange(nframes)]) # in seconds
        #setup marker list
        markers=defaultdict(list)
        for key in markersCSV:
            markers[key[0]].append(key[1])
        datatype=defaults["Datatype"]
        clusters=defaults["Clusters"]
        history=defaults["History"]
        identifier=defaults["Identifier"]
        channels=np.array([f'Channel {ii+1}' for ii in range(ch)])
    elif ".ssa" in filename: #SpikeAnalysis Tool saved data (Spike Sorting Analysis)
        npzfile=np.load(file, allow_pickle=True)
        loaddata=[]
        for key in defaults.keys():
            try:
                loaddata.append(npzfile[key])
            except KeyError:
                if key=="Channels":
                    loaddata.append([f'Channel {ii+1}' for ii in range(ch)])
                else:
                    loaddata.append(defaults[key])
        #Load data to variables
        datatype=loaddata[0]
        data=loaddata[1]
        markerstmp=loaddata[2]
        markersdict=dict(enumerate(markerstmp.flatten(),1))[1]
        markers=defaultdict(list,markersdict)
        clusters=loaddata[3]
        time=loaddata[4]
        framerate=loaddata[5]
        history=loaddata[6]
        identifier=loaddata[7]
        channels=loaddata[8]
        if markers:
            nomarker=False
        else:
            nomarker=True
    return data, clusters, markers, time, framerate, datatype, history, identifier, channels, nomarker

def bandpassfilter(data, framerate, order, frequencies):
    """
    Function to apply a bandpass filter to the given multichannel data.

    Parameters
    ----------
    data : list
        List containing the data per channel.
    framerate : int
        Framerate in frames per second.
    order : int
        Order of the filter.
    frequencies : list
        List containing first the lower, then the upper bound values of the frequencies to keep.

    Returns
    -------
    filtdata : list
        List containing the filtered data per channel.

    """
    #Nyquist frequency
    nyq = framerate/2
    #Calculate bandpass filter coefficients for a matlabstyle iir filter
    b, a = butter(order, [freq/nyq for freq in frequencies], btype='band')
    #Apply filter
    return np.array([filtfilt(b,a, channel) for channel in data])

def notchfilter(data, framerate, quality, frequency):
    """
    Function to apply a notch filter to the given multichannel data.

    Parameters
    ----------
    data : list
        List containing the data per channel.
    framerate : int
        Framerate in frames per second.
    quality : int
        quality of the filter.
    frequency : int
        Frequency to be filtered out.

    Returns
    -------
    filtdata : list
        List containing the filtered data per channel.

    """
    #Calculate notch filter coefficients for a 2nd order matlab style iir filter.
    b, a=iirnotch(frequency, quality, framerate)
    #Apply filter
    return np.array([filtfilt(b,a, channel) for channel in data])

def passfilter(data, framerate, order, frequency, highlow):
    """
    Function to apply a highpass or lowpass filter to the given multichannel data.

    Parameters
    ----------
    data : list
        List containing the data per channel.
    framerate : int
        Framerate in frames per second.
    order : int
        Order of the filter.
    frequency : int
        Frequency to be filtered out.
    highlow : str
        "high" for a highpass filter. "low" for a lowpass filter.

    Returns
    -------
    filtdata : list
        List containing the filtered data per channel.

    """
    #Nyquist frequency
    nyq = framerate/2
    #Calculate highpass filter coefficients for a matlabstyle iir filter
    b, a = butter(order, frequency/nyq, btype=highlow)
    #Apply filter
    return np.array([filtfilt(b,a, channel) for channel in data])

def find_peaks(data, threshold, offset=0, subthresh=0.8):
    """
    Function to find peaks.
    Search method uses thresholds and a subthreshold proportion.
    Signal needs to go below the threshold before it searches for the first peak, and below the subthresh proportion of the threshold for subsequent peaks.

    Parameters
    ----------
    data : list
        List containing the signal data.
    threshold : int
        Threshold for which peaks need to be found.
    offset : int, optional
        Signal off-set. The default is 0.
    subthresh : float, optional
        Proportion that determines how far the signal needs to go below the signal before the function searches for another peak. The default is 0.8.

    Returns
    -------
    peakdata : tuple
        Tuple containing a list of the peak times and a dictionary containing the peak heights.
    peakcount : int
        The amount of peaks found.

    """
    if threshold<0:
        threshold=abs(threshold)
        data=[val*-1 for val in data]
        negthresh=-1
    else:
        negthresh=1
    last=len(data)
    peaks=np.empty((2,0))
    peakstart=False
    peaklocation=0
    peakmax=threshold
    for ii, peak in enumerate(data):
        #only look for a peak if the data has gone below the threshold
        if peak<(threshold+offset):
            peakstart=True
        #Check if the peak is a local maximum, and exclude first and last values
        if ii>0 and ii<last-1 and peak>=threshold+offset:
            if peak>=data[ii-1] and peak>=data[ii+1] and peakstart:
                #Check if the peak is higher than last found peak
                if peak>peakmax:
                    peaklocation=ii
                    peakmax=peak
        #If the start of a peak has been found, check if the peak drops below half of the threshold
        if peaklocation:
            if data[ii-1]>=(subthresh*threshold+offset) and peak<(subthresh*threshold+offset) and peakstart:
                #Add the peaklocation and height of the highest point of the peak to the peaks array
                peaks=np.append(peaks, np.array([[peaklocation], [data[peaklocation]*negthresh]]), axis=1)
                #Reset peak finding variables
                peakmax=0
                peaklocation=0
                peakstart=False
    peakcount=len(peaks[0])
    peakdata=(peaks[0], {"peak_heights": peaks[1]})
    return peakdata, peakcount

def SpikeSorting(DataSelection,thresholds,subthresh,framerate,time,cutoff_thresh=False):
    """
    Function to sort spikes based on thresholds

    Parameters
    ----------
    DataSelection : list
        A list containing the signal data in the selected time frames per channel.
    thresholds : list
        List containing the thresholds, ordered from the absolute value of the largest to the absolute value of the smallest.
    subthresh : float
        Float determining how far the signal needs to go below the threshold before searching for a new spike.
    framerate : int
        Sampling rate of the data.
    time : Array of float64
        Array containing x-values per channel. First index is channel, second contains x-values.
    cutoff_thresh : int or bool
        Integer if the cut-off threshold is being used, otherwise the bool False. The default is False.

    Returns
    -------
    clusters : list
        A list containing all peaks above threshold height, timestamps of peaks, heights of peaks, height of spike marker per peak, and the threshold height per threshold per channel.

    """
    # First, get everything above cutoff if cutoff is given
    cutoff1=[[[]] for _ in range(len(DataSelection))]
    if type(cutoff_thresh)==int:
        for ii in range(len(DataSelection)):
            th = cutoff_thresh
            cutoff1[ii], _ = find_peaks(DataSelection[ii], threshold=th, subthresh=subthresh)
        
    cl2=[[] for _ in range(len(DataSelection))]
    maxval=[[] for _ in range(len(DataSelection))]
    #clusters: [[peak data], [time], [plot height of points], ["Cluster threshold {threshold}"]
    clusters=[[[[],[],[],[],np.array([th], dtype=np.float64)] for ii,th in enumerate(thresholds)] for _ in range(len(DataSelection))]
    maxsize=1
    for ii in range(len(DataSelection)):
        #Get largest peak of selected data
        cl2[ii]=np.nanmax(DataSelection[ii])
        maxval[ii]=cl2[ii]
        #Detect the other spikes per cluster
        for clusterN,th in enumerate(thresholds):
            clusters[ii][clusterN][0],_ = find_peaks(DataSelection[ii], threshold=th, subthresh=subthresh)
            for peakN,x in enumerate(clusters[ii][clusterN][0][0]):
                if x not in cutoff1[ii][0] and not any(x in clusters[ii][jj][0][0] for jj in range(clusterN)):
                    clusters[ii][clusterN][1].append(x/framerate)
                    clusters[ii][clusterN][2].append(clusters[ii][clusterN][0][1]["peak_heights"][peakN])
            clusters[ii][clusterN][1]=np.array(clusters[ii][clusterN][1])
            clusters[ii][clusterN][2]=np.array(clusters[ii][clusterN][2])
            #y value for points denothing peaks above largest peak
            clusters[ii][clusterN][3] = np.ones(len(clusters[ii][clusterN][1] ))*maxval[ii]+(maxval[ii]/10*(clusterN+1))
            if len(clusters[ii][clusterN][0][0])>maxsize:
                maxsize=len(clusters[ii][clusterN][0][0])
    for ii in range(len(clusters)):
        for jj in range(len(clusters[ii])):
            clusters[ii][jj][0]=clusters[ii][jj][0][0]
            for kk in range(len(clusters[ii][jj])):
                clusters[ii][jj][kk]=np.append(clusters[ii][jj][kk], np.zeros(maxsize-len(clusters[ii][jj][kk]))+np.nan)
    return clusters

def cross_correlate(spikeset1, spikeset2, interval, binsize, preinterval=0):
    """
    Function to calculate cross-correlation.
    Giving the same spikeset twice will calculate auto-correlation.

    Parameters
    ----------
    spikeset1 : list of int
        First set of spike timings in frames.
    spikeset2 : list of int
        Second set of spike timings in frames.
    interval : int
        Interval in frames to calculate cross-correlation in.

    Returns
    -------
    cross : numpy.array
        Array containing the amount of spikes at a given relative datapoint.

    """
    cross = np.zeros(int(2*interval+1), 'd') #prepare array filled with zeros
    #cross = np.zeros(int(np.ceil(2*max(preinterval, interval)/binsize+1)), 'd')
    startint=0 #index at which spike search is started
    for spike in spikeset1:
        ii=startint
        #Look for the index of the first spike in spikeset2 that is within the interval
        while ii<len(spikeset2) and spikeset2[ii]-spike<-max(preinterval, interval):
            ii+=1
        startint=ii #update startint to skip values that are certain to be outside the interval of the next spike
        #Add spikes to the correct bins
        while ii<len(spikeset2) and spikeset2[ii]-spike<=max(preinterval, interval):
            #int(np.ceil(ii/binsize))
            cross[int(spikeset2[ii]-spike+interval)]+=1 #change interval to preinterval when implementing variable interval sizes on both sides
            ii+=1
    return cross
