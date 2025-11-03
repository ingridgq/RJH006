import matplotlib.pyplot as plt
import numpy as np
import brpylib
import glob
import scipy.io.wavfile as wavfile
import os
import argparse

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

    ns5_path = glob.glob(data_path + '\*.ns5')[0]

    nsx_file = brpylib.NsxFile(str(ns5_path))
    cont_data = nsx_file.getdata(channel_ids, 0, full_timestamps=True)
    nsx_file.close()

    audio_idx = channel_ids.index(audio_channel)
    
    seg_id = 0

    t = cont_data["data_headers"][seg_id]["Timestamp"] / cont_data["samp_per_s"]
    audio = cont_data["data"][seg_id][audio_idx]

    # checks if there is a folder for the experiment, if not, creates one

    return t, audio, wavfile

def parse_audio(ns5_path, experiment_name):
    channel_ids = [33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    257]

    audio_channel = 257
    nsx_file = brpylib.NsxFile(str(ns5_path))
    cont_data = nsx_file.getdata(channel_ids, 0, full_timestamps=True)
    nsx_file.close()

    audio_idx = channel_ids.index(audio_channel)

    seg_id = 0

    t = cont_data["data_headers"][seg_id]["Timestamp"] / cont_data["samp_per_s"]
    audio = cont_data["data"][seg_id][audio_idx]

    folder_base = f'../../experiments/{experiment_name}'

    os.makedirs(folder_base, exist_ok=True)

    wavfile.write(rf'{folder_base}\{experiment_name}_audio.wav', int(cont_data["samp_per_s"]), audio)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, help='Path to the data folder.')
    parser.add_argument('--name', type=str, help='Experiment name.')

    args = parser.parse_args()

    ns5_path = args.path
    experiment_name = args.name

    parse_audio(ns5_path, experiment_name)


