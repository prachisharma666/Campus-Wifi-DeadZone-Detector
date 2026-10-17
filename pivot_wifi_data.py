import csv
import os
from collections import defaultdict

input_file = 'campus_wifi_raw_log.csv'
output_file = 'data/campus_trainingData.csv'

# Ensure the output directory exists
os.makedirs('data', exist_ok=True)

# Store signal readings: sessions[(Timestamp, Location_ID)][AP_ID] = max_RSSI
sessions = defaultdict(dict)
all_aps = set()

# 1. Read raw CSV and filter personal hotspots
with open(input_file, mode='r', encoding='cp1252') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ssid = row['SSID']
        
        # Keep only campus Wi-Fi infrastructure
        if ssid.startswith('SVKM'):
            timestamp = row['Timestamp']
            location = row['Location_ID']
            ap_id = f"WAP_{row['MAC_Address']}"
            rssi = float(row['RSSI'])

            all_aps.add(ap_id)
            session_key = (timestamp, location)

            # Store peak RSSI per scan session
            if ap_id not in sessions[session_key] or rssi > sessions[session_key][ap_id]:
                sessions[session_key][ap_id] = rssi

sorted_aps = sorted(list(all_aps))

# 2. Write wide-format matrix
with open(output_file, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    
    # Write header columns
    writer.writerow(['Timestamp', 'Location_ID'] + sorted_aps)

    # Write data rows
    for (timestamp, location), ap_signals in sessions.items():
        row = [timestamp, location]
        for ap in sorted_aps:
            # Impute undetectable APs with -100.0 dBm
            row.append(ap_signals.get(ap, -100.0))
        writer.writerow(row)

print(f"Successfully processed raw logs into {output_file} using pure Python!")