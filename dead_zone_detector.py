import csv
from collections import defaultdict

def detect_dead_zones(filepath, signal_threshold=-80):
    print(f"Analyzing {filepath} for dead zones...")
    
    dead_zone_counts = defaultdict(int)
    total_records = 0
    dead_zone_instances = 0
    
    metadata_cols = {'Timestamp', 'Location_ID'}

    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_records += 1
            location = row.get('Location_ID', 'Unknown')
            
            # Extract signal levels for all router columns
            rssi_values = []
            for col, val in row.items():
                if col not in metadata_cols and val is not None:
                    try:
                        rssi_values.append(float(val))
                    except ValueError:
                        pass
            
            # Find peak signal strength across all routers for this scan
            if rssi_values:
                max_rssi = max(rssi_values)
                if max_rssi < signal_threshold:
                    dead_zone_counts[location] += 1
                    dead_zone_instances += 1

    if dead_zone_instances > 0:
        # Sort locations by dead zone counts descending
        sorted_summary = sorted(dead_zone_counts.items(), key=lambda item: item[1], reverse=True)
        
        print(f"\n--- Dead Zone Report (Threshold: {signal_threshold} dBm) ---")
        print(f"Total Weak Coverage Spots Detected: {dead_zone_instances} out of {total_records} records")
        print(f"\nPriority Locations Needing Coverage Improvement:")
        print(f"{'Location_ID':<35} | {'Dead_Zone_Instances'}")
        print("-" * 55)
        for loc, count in sorted_summary:
            print(f"{loc:<35} | {count}")
            
        output_path = r"C:\Users\Prachi\OneDrive\Desktop\FOML_Project_1\data\facilities_dead_zone_report.csv"
        
        with open(output_path, mode='w', newline='', encoding='utf-8') as out_f:
            writer = csv.writer(out_f)
            writer.writerow(['Location_ID', 'Dead_Zone_Instances'])
            for loc, count in sorted_summary:
                writer.writerow([loc, count])
                
        print(f"\nDetailed Report Saved to {output_path}")
    else:
        print(f"\nNo Dead Zones Detected Below {signal_threshold} dBm threshold")

if __name__ == "__main__":
    detect_dead_zones(r"C:\Users\Prachi\OneDrive\Desktop\FOML_Project_1\data\campus_trainingData.csv", signal_threshold=-80)