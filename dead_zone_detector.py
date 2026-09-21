import pandas as pd
import numpy as np
def detect_dead_zones(filepath,signal_threshold=-80):
#Identifies zones where the maximum RSSI is below the functional threshold. -80 dBm is typically where connection becomes highly unstable.
    print(f"Analyzing {filepath} for dead zones...")
    df=pd.read_csv(filepath)
    wap_cols=[col for col in df.columns if "WAP" in col]
    x=df[wap_cols].copy()
    x.replace(100,-105,inplace=True)
    df["Max_Available_RSSI"]=x.max(axis=1)
    dead_zone=df[df["Max_Available_RSSI"]<signal_threshold].copy()
    if not dead_zone.empty:
        summary=dead_zone.groupby(["BUILDINGID","FLOOR","SPACEID"]).size().reset_index(name="Dead_Zone_Instances")
        summary=summary.sort_values(by="Dead_Zone_Instances",ascending=False)
        print(f"Dead Zone Report (Threshold:{signal_threshold}dBm)")
        print(f"Total Weak Coverage Spots Detected:{len(dead_zone)} out of {len(df)} records")
        print(f"Top 10 Priority Locations for New Access Points:")
        print(summary.head(10).to_string(index=False))
        summary.to_csv(r"C:\Users\Prachi\OneDrive\Desktop\FOML_Project_1\data\facilities_dead_zone_report.csv",index=False)
        print("Detailed Report Saved to facilities_dead_zone_report.csv")
    else:
        print("No Dead Zones Detected Below {signal_threshold} dBm threshold")

if __name__=="__main__":
    detect_dead_zones(r"C:\Users\Prachi\OneDrive\Desktop\FOML_Project_1\data\validationData.csv",signal_threshold=-80)