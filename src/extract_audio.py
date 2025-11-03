import matplotlib.pyplot as plt
import numpy as np
import brpylib
import glob
import scipy.io.wavfile as wavfile
import os

def extract(data_path, destination_path, audio_channel, channel_ids, drive=True):

    """
    Extracts the audio data from the .ns5 file and saves it in a .wav file

    Parameters
    ----------
    patient : str
        Patient ID
    experiment : int
        Experiment number
    audio_channel : int
        Channel ID of the audio channel
    channel_ids : list
        List of channel IDs
    drive : bool
        If True, saves the audio file in the Google Drive folder

    Returns
    -------
    t : array
        Time vector
    audio : array
        Audio data
    """

    ns5_path = glob.glob(data_path + '\*.ns5')[0]

    nsx_file = brpylib.NsxFile(str(ns5_path))
    cont_data = nsx_file.getdata(channel_ids, 0, full_timestamps=True)
    nsx_file.close()

    audio_idx = channel_ids.index(audio_channel)
    
    seg_id = 0

    t = cont_data["data_headers"][seg_id]["Timestamp"] / cont_data["samp_per_s"]
    audio = cont_data["data"][seg_id][audio_idx]

    # save the audio data in a .wav file
    wavfile.write(destination_path, int(cont_data["samp_per_s"]), audio)

    return t, audio  

def extract_from_path(data_path, audio_channel, channel_ids):

    """
    Extracts the audio data from the .ns5 file and saves it in a .wav file

    Parameters
    ----------
    patient : str
        Patient ID
    experiment : int
        Experiment number
    audio_channel : int
        Channel ID of the audio channel
    channel_ids : list
        List of channel IDs
    drive : bool
        If True, saves the audio file in the Google Drive folder

    Returns
    -------
    t : array
        Time vector
    audio : array
        Audio data
    """

    ns5_path = glob.glob(data_path + '\*.ns6')[0]

    nsx_file = brpylib.NsxFile(str(ns5_path))
    cont_data = nsx_file.getdata(channel_ids, 0, full_timestamps=True)
    nsx_file.close()

    audio_idx = channel_ids.index(audio_channel)
    
    seg_id = 0

    t = cont_data["data_headers"][seg_id]["Timestamp"] / cont_data["samp_per_s"]
    audio = cont_data["data"][seg_id][audio_idx]

    # checks if there is a folder for the experiment, if not, creates one

    return t, audio, wavfile 
