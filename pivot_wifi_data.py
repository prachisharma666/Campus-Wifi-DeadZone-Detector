import pandas as pd
import os

def pivot_wifi_data(input_csv, output_csv):
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} not found.")
        return

    print(f"Loading raw data from {input_csv}...")
    df = pd.read_csv(input_csv)
    
    # 1. Pivot the data to wide format
    # Index: Groups readings by specific scan instances
    # Columns: Creates a new column for every unique MAC Address
    # Values: Places the RSSI value in the corresponding cell
    print("Pivoting data to wide format...")
    wide_df = df.pivot_table(
        index=['Timestamp', 'Location_ID'], 
        columns='MAC_Address', 
        values='RSSI', 
        aggfunc='mean' # Averages RSSI if a network is logged twice in the same second
    )
    
    # 2. Fill missing access points with 100 
    # (This matches the standard UJIIndoorLoc format for "not detected")
    wide_df = wide_df.fillna(100)
    
    # Reset index to make Timestamp and Location_ID standard columns again
    wide_df = wide_df.reset_index()
    
    # 3. Rename MAC Address columns to WAP001, WAP002... format
    mac_columns = [col for col in wide_df.columns if col not in ['Timestamp', 'Location_ID']]
    wap_mapping = {mac: f"WAP{str(i+1).zfill(3)}" for i, mac in enumerate(mac_columns)}
    wide_df.rename(columns=wap_mapping, inplace=True)
    
    # 4. Parse Location_ID into Neural Network Target Columns
    # Expects you typed your locations as "Building_Floor_Space" (e.g., "Lib_1_Stairs")
    def parse_location(loc_string):
        parts = str(loc_string).split('_')
        if len(parts) >= 3:
            return pd.Series([parts[0], parts[1], '_'.join(parts[2:])])
        elif len(parts) == 2:
            return pd.Series([parts[0], parts[1], 'Unknown'])
        else:
            return pd.Series(['Campus', '0', loc_string])
            
    wide_df[['BUILDINGID', 'FLOOR', 'SPACEID']] = wide_df['Location_ID'].apply(parse_location)
    
    # 5. Save the final Neural Network ready dataset
    wide_df.to_csv(output_csv, index=False)
    
    # 6. Save a mapping dictionary (Crucial for translating WAP columns back to physical routers later)
    mapping_df = pd.DataFrame(list(wap_mapping.items()), columns=['MAC_Address', 'WAP_Column'])
    mapping_df.to_csv('wap_mac_mapping.csv', index=False)
    
    print("\n--- Processing Complete ---")
    print(f"Raw readings processed: {len(df)}")
    print(f"Unique scan locations/instances: {len(wide_df)}")
    print(f"Total unique Access Points (WAPs) detected: {len(mac_columns)}")
    print(f"\nTraining data saved to: {output_csv}")
    print("MAC-to-WAP mapping saved to: wap_mac_mapping.csv")

if __name__ == "__main__":
    # Ensure you have installed pandas: pip install pandas
    pivot_wifi_data('campus_wifi_raw_log.csv', 'custom_trainingData.csv')