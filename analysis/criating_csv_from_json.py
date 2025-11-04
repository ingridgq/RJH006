import json
import csv

#Paths
json_path = r"C:\Users\ingri\Documents\IMIM\experiments\RJH006_subj_obj\teste\RJH006_subj_obj_names_timestampsNEW.json"
csv_path = r"C:\Users\ingri\Documents\IMIM\experiments\RJH006_subj_obj\teste\RJH006_subj_obj_names_timestamps_CSV.csv"

#Opening json
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

#criating and writing csv
with open(csv_path, "w", newline="", encoding="utf-8-sig") as csvfile:
    writer = csv.writer(csvfile)

    #headers
    writer.writerow(["chinese_name", "english_name", "start_time", "end_time", "sentence"])

    #iterating
    for item in data:
        chinese = item.get("chin_name", "")
        english = item.get("eng_name", "")
        start = item.get("start", "")
        end = item.get("end", "")
        sentence = item.get("sentence", "")

        writer.writerow([chinese, english, start, end, sentence])

print(f'csv criado com sucesso {csv_path}')




