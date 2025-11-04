import glob
import elevenlabs
import pandas as pd
import pickle
from elevenlabs.client import ElevenLabs
import os
import argparse


client = ElevenLabs(
  api_key='sk_9bfb178b61bda622a6bd3f8780487620d0fb58031e0febf9',
)

def transcribe(audio_path, experiment_name):

    # check existing pkl, skip existing

    folder_base = f'../../experiments/{experiment_name}'
    transcription_path = os.path.join(folder_base, experiment_name) + '_transcription.pkl'

    if os.path.exists(transcription_path):
        print('[-] {} transcription already exists, skipping...'.format(experiment_name))
        return

    print('[-] Transcribing {}...'.format(experiment_name))

    with open(audio_path, "rb") as f:
        audio_data = f.read()

    transcription = client.speech_to_text.convert(
        file=audio_data,
        model_id="scribe_v1",
        tag_audio_events=True,
        diarize=True,
        additional_formats=[{"format": "segmented_json"},{"format": "srt"}],
        num_speakers=2,
    )

    with open(transcription_path, 'wb') as f:
        pickle.dump(transcription, f)

    for af in transcription.additional_formats:
        fmt = af.file_extension
        content = af.content
        with open(f'{folder_base}/{experiment_name}_transcription.{fmt}', 'wb') as f:
            if isinstance(content, str):
                f.write(content.encode('utf-8'))
            else:
                f.write(content)

    print(f"[-] Finished transcribing {experiment_name}.")