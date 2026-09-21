import subprocess
import csv
import time
import os

def get_windows_wifi_scan():
    """Runs the Windows netsh command and parses the WiFi data."""
    # Execute the Windows command to get detailed WiFi network data
    result = subprocess.check_output(['netsh', 'wlan', 'show', 'networks', 'mode=bssid'])
    result = result.decode('utf-8', errors='backslashreplace')
    
    networks = []
    current_ssid = ""
    
    for line in result.split('\n'):
        line = line.strip()
        if line.startswith('SSID'):
            current_ssid = line.split(':')[1].strip()
        elif line.startswith('BSSID'):
            mac_address = line.split(':')[1].strip()
        elif line.startswith('Signal'):
            # Windows reports signal as a percentage (e.g., 80%)
            signal_percent = int(line.split(':')[1].strip().replace('%', ''))
            # Approximate conversion from Windows Percentage to RSSI (dBm)
            rssi = (signal_percent / 2) - 100 
            
            networks.append({
                'MAC_Address': mac_address,
                'SSID': current_ssid,
                'RSSI': rssi
            })
            
    return networks

def main():
    csv_filename = "campus_wifi_raw_log.csv"
    file_exists = os.path.isfile(csv_filename)
    
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Timestamp', 'Location_ID', 'MAC_Address', 'SSID', 'RSSI'])
            
        print("--- Windows WiFi Fingerprint Logger ---")
        print("Type 'exit' to quit.\n")
        
        while True:
            location = input("Enter current Location ID (e.g., Lib_Floor1_A) and press Enter to scan: ")
            
            if location.lower() == 'exit':
                break
                
            print(f"Scanning WiFi networks at {location}...")
            # Windows sometimes caches results; a short sleep ensures a fresh read
            time.sleep(2) 
            
            networks = get_windows_wifi_scan()
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            
            for net in networks:
                writer.writerow([timestamp, location, net['MAC_Address'], net['SSID'], net['RSSI']])
                
            print(f"Logged {len(networks)} access points for {location}.\n")

if __name__ == "__main__":
    main()