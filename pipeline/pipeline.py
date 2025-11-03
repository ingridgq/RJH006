import parse_audio
import glob
import transcribe
import argparse
import video

parser = argparse.ArgumentParser()
parser.add_argument('--transcribe', action='store_true', help='Run transcription pipeline.')
parser.add_argument('--parse', action='store_true', help='Run audio parsing pipeline.')
parser.add_argument('--video', action='store_true', help='Run video processing pipeline.')

args = parser.parse_args()

do_transcription = args.transcribe
do_parsing = args.parse
do_video = args.video

data_paths = [r"C:\Users\ingri\OneDrive\Documentos\IMIM\RJH006 - Copia\RJH006_subj_obj_1\RJH006_eze_miniscr1\sub_obj\20250803-160512-002.ns5"]
names = [r"RJH006_subj_obj"]

if do_parsing:
    for data_path, name in zip(data_paths, names):
        print(f"Processing {name}...")
        parse_audio.parse_audio(data_path, name)
        print(f"Finished processing {name}.")

if do_transcription:
    for name in names:
        audio_path = f'../../experiments/{name}/{name}_audio.wav'
        transcribe.transcribe(audio_path, name)

if do_video:
    for name in names:
        base_folder = f'../../experiments/{name}'
        print(f'[-] Generating video of {name}.')
        audio_path = f'{base_folder}/{name}_audio.wav'
        json_path = f'{base_folder}/{name}_transcription.json'
        output_path = f'{base_folder}/{name}_video.mp4'
        video.generate_video(audio_path, json_path, output_path)

print("[-] Pipeline execution completed.")
