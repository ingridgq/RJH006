import os
import subprocess
import pysrt
from datetime import timedelta
from tqdm import tqdm
import threading
import os
import glob
import json
import re
import os

import json, re
from pathlib import Path
from math import ceil

CENTI = 10  # 1 centésima = 10 ms

def fmt(ms):
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms,    60_000)
    s, cs = divmod(ms,     1_000)
    return f"{h:d}:{m:02d}:{s:02d}.{cs//10:02d}"

def esc(t):
    return (t.replace("\\", r"\\").replace("{", r"\{")
             .replace("}", r"\}").replace("&", r"\&"))

def lighten(bgr, alpha=0.6):
    b, g, r = int(bgr[2:4],16), int(bgr[4:6],16), int(bgr[6:8],16)
    to = lambda c: min(255, round(c + (255-c)*alpha))
    return f"&H00{to(b):02X}{to(g):02X}{to(r):02X}"

PALETTE = [
    "&H000000FF", "&H0000AA00", "&H00AA0000", "&H00AA00AA",
    "&H0000AAAA", "&H00AAAA00", "&H000055FF", "&H00550055",
]

def json_to_ass(src, dst):
    data = json.load(open(src, encoding="utf-8"))

    styles, next_c = {}, 0
    with open(dst, "w", encoding="utf-8") as f:

        # -------- Header & styles ----------
        f.write("[Script Info]\nTitle: Smooth Karaoke\nScriptType: v4.00+\n\n")
        f.write("[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour,"
                " SecondaryColour, OutlineColour, BackColour, Bold, Italic,"
                " Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle,"
                " BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR,"
                " MarginV, Encoding\n")

        for seg in data["segments"]:
            spk = seg["words"][0].get("speaker_id","")
            if spk and spk not in styles:
                dark = PALETTE[next_c % len(PALETTE)]
                light = lighten(dark, .6)
                sty = f"S{len(styles)}"
                styles[spk] = (sty, dark, light)
                next_c += 1
                f.write(f"Style: {sty},Arial,20,{light},{dark},&H0,&H64000000,"
                        "0,0,0,0,100,100,0,0,1,3,0,2,40,40,40,-1\n")

        f.write("Style: Default,Arial,40,&H00FFFFFF,&H00777777,&H0,&H64000000,"
                "0,0,0,0,100,100,0,0,1,3,0,2,60,60,40,-1\n\n")

        f.write("[Events]\n")
        f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR,"
                " MarginV, Effect, Text\n")

        # -------- Karaoke line per segment ----------
        for seg in data["segments"]:
            W = seg["words"];  n=len(W)
            if not n: continue

            sty,dark,light = styles.get(W[0].get("speaker_id",""),
                                        ("Default","",""))
            tokens, cents = [], []        # build text & durations
            for w in W:
                st, ed = round(w["start"]*1000), round(w["end"]*1000)
                dur_cs = max(1, round((ed-st)/CENTI))
                tag = r"\kf" if w["type"]=="word" else r"\kf0"
                tokens.append(f"{{{tag}{dur_cs}}}{esc(w['text'])}")
                cents.append(dur_cs)

            # ajuste final: suma exacta = duración segmento
            real_cs = round((W[-1]["end"]*1000 - W[0]["start"]*1000)/CENTI)
            diff = real_cs - sum(cents)
            if diff:                      # corrige último token
                last = tokens[-1].replace(r"\kf0", r"\kf")  # ensure tag
                dur = int(cents[-1] + diff)
                tokens[-1] = re.sub(r"(\\kf)\d+", rf"\g<1>{dur}", last)


            line = "".join(tokens)
            f.write(
                f"Dialogue: 0,{fmt(round(W[0]['start']*1000))},"
                f"{fmt(round(W[-1]['end']*1000))},{sty},,"
                f"0,0,0,,{line}\n"
            )



def get_audio_length(audio_path):
    result = subprocess.run(["ffmpeg", "-i", audio_path, "-hide_banner"], stderr=subprocess.PIPE, universal_newlines=True)
    for line in result.stderr.splitlines():
        if "Duration" in line:
            duration = line.split()[1].strip(",")
            h, m, s = duration.split(":")
            total_seconds = int(h) * 3600 + int(m) * 60 + float(s)
            return total_seconds
    return None

def create_black_video(duration, resolution, video_path):
    try:
        command = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=black:s={resolution}", "-t", str(duration), "-r", "25", "-pix_fmt", "yuv420p", video_path
        ]
        result = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, command, result.stderr)
        else:
            print(f"Black video created successfully: {video_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating black video: {e}")
        print(f"ffmpeg stderr: {e.stderr}")

def merge_audio_video(video_path, audio_path, output_path):
    try:
        command = [
            "ffmpeg", "-y", "-i", video_path, "-i", audio_path, "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", output_path
        ]
        result = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, command, result.stderr)
        else:
            print(f"Audio and video merged successfully: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error merging audio and video: {e}")
        print(f"ffmpeg stderr: {e.stderr}")

import subprocess
from pathlib import Path

def burn_subtitles(video_path, ass_path, output_path):
    # 1) Ruta absoluta en formato POSIX
    posix = Path(ass_path).resolve().as_posix()          # C:/Users/…

    # 2) Escapa sólo el colon de la unidad
    if posix[1:3] == ':/':
        posix = posix[0] + r'\:/' + posix[3:]            # C\:/Users/…

    # 3) Construye el filtro con filename=
    vf = f"ass=filename='{posix}'"

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", vf,
        "-c:a", "copy",
        output_path,
    ]
    try:
        subprocess.run(cmd, check=True, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Subtitles burned successfully:", output_path)
    except subprocess.CalledProcessError as e:
        print("Error burning subtitles:")
        print("ffmpeg command:", " ".join(e.cmd))
        print("ffmpeg stderr:", e.stderr)



def generate_video(audio_path, json_path, output_path, resolution="1280x720"):
    video_path = "black_video.mp4"
    merged_path = "merged_video.mp4"
    ass_path = json_path.replace('.json', '.ass')
    
    # Format subtitles
    print("Formating subtittles...")
    json_to_ass(json_path, ass_path)

    # Get audio length
    audio_length = get_audio_length(audio_path)
    if not audio_length:
        print("Could not determine the length of the audio.")
        return
    
    # Create black video
    print('Creating black video...')
    create_black_video(audio_length, resolution, video_path)
    
    # Merge audio with black video
    print('Merging audio with black video...')
    merge_audio_video(video_path, audio_path, merged_path)
    
    # Burn subtitles onto the video
    print('Burning subtitles onto the video...')
    burn_subtitles(merged_path, ass_path, output_path)
    
    # Cleanup
    os.remove(video_path)
    os.remove(merged_path)
    print('Process completed successfully.')

import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate video with burned subtitles.')
    parser.add_argument('audio_path', type=str, help='path to the audio file')
    parser.add_argument('json_path', type=str, help='path to the json file')
    parser.add_argument('output_path', type=str, help='path to save the final video')
    parser.add_argument('--resolution', type=str, default='1280x720', help='video resolution')
    args = parser.parse_args()
    generate_video(args.audio_path, args.json_path, args.output_path, args.resolution)
    

