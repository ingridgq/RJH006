import json
import re
import os 

#Paths
folder_base = r"C:\Users\ingri\Documents\IMIM\experiments\RJH006_subj_obj\teste"
experiment_name = "RJH006_subj_obj"
json_path = f"{folder_base}/{experiment_name}_transcription.json"

#Names to find
names = [
    {"text": "朱茵", "text_eng": "Zhu Yin"},
    {"text": "焦恩俊", "text_eng": "Jiao Enjun"},
    {"text": "周星驰", "text_eng": "Stephen Chow"},
    {"text": "金映娟", "text_eng": "Jin Yingjuan"},
    {"text": "张怡宁", "text_eng": "Zhang Yining"},
]

#Original transcription
with open(json_path, 'r', encoding='utf-8') as f: 
    data = json.load(f)

results = []

for seg in data.get("segments", []):
    words = seg.get("words", [])
    full_text = "".join([w["text"] for w in words])

    for name in names: 
        n = name["text"]
        eng = name["text_eng"] 

        #Verify if name is inside the segment
        if n in full_text: 
            text_concat = ""
            for i in range(len(words)):
                text_concat += words[i]["text"]

                if text_concat.endswith(n): 
                    start_idx = i - len(n) + 1
                    end_idx = i
                    start_time = words[start_idx]["start"]
                    end_time = words[end_idx]["end"]

                    results.append({
                        "chin_name": n,
                        "eng_name": eng,
                        "start": start_time,
                        "end": end_time,
                        "sentence": full_text
                    })
                    break 

#Saving results
output_path = f"{folder_base}/{experiment_name}_names_timestampsNEW.json"
with open(output_path, 'w', encoding='utf-8') as f_out:
    json.dump(results, f_out, ensure_ascii=False, indent=2)

print(f"✅ Resultados salvos em: {output_path}")
print(f"Encontrados {len(results)} nomes.")

