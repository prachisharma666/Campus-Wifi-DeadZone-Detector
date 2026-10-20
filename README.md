```markdown
# Campus WiFi Dead-Zone Detection & Indoor Localization (PCA + Deep Neural Network)

An end-to-end Machine Learning and Data Engineering pipeline that compresses high-dimensional, noisy campus WiFi fingerprint vectors using **Principal Component Analysis (PCA)** and trains a **Deep Neural Network (DNN)** to:
1. **Locate Devices:** Accurately classify which building and floor a device is on based on its active WiFi fingerprint.
2. **Flag Coverage Dead-Zones:** Automatically identify weak aggregate signal locations ($<-80\text{ dBm}$) to produce actionable coverage-quality reports for campus IT and facilities management.

---

## 📌 Problem & Technical Motivation

In large multi-story academic buildings, students and faculty routinely experience dropped connections in structural blind spots (e.g., stairwells, basement labs, library stacks). IT departments struggle to diagnose these coverage gaps systematically because:
* A single WiFi reading captures signal strengths (RSSI) from **hundreds of access points simultaneously**.
* The vast majority of access points are undetected at any single location, producing **sparse, high-dimensional data (520+ features)**.
* Feeding raw, uncompressed RSSI vectors directly into a neural network causes severe overfitting and unnecessary computational overhead.

### Why PCA + Deep Neural Network?
* **PCA (Dimensionality Reduction):** Strips away noisy and redundant access point dimensions, retaining the top principal components that explain **95% of total variance** (reducing features from 520 down to $\approx 110$).
* **Deep Neural Network (Classifier):** Learns nonlinear spatial decision boundaries from the dense, compressed principal components to predict building and floor coordinates reliably.

---

## 🔬 System Architecture & Methodology

```text
[ Raw WiFi Fingerprint ] ──► [ Preprocessing & Scaling ] ──► [ PCA Compression (95% Var) ]
  (520 RSSI Values)            (Map 100 to -105, Scale [0,1])       (520 → ~110 Components)
                                                                            │
                                                                            ▼
[ IT Dead-Zone Report ] ◄── [ Dead-Zone Detector ] ◄────────── [ Deep Neural Network ]
 (Flag Max RSSI < -80 dBm)   (Spatial Thresholding)            (Dense ReLU + Softmax Classifier)

```

1. **Signal Preprocessing & Normalization:**
* Missing/undetected access point values (encoded as `100` in raw scans) are mapped to a theoretical noise floor of $-105\text{ dBm}$.
* RSSI values (ranging from $-105\text{ dBm}$ to $0\text{ dBm}$) are min-max scaled to $[0.0, 1.0]$ for stable neural network gradient updates.


2. **Target Encoding:**
* Spatial targets `BUILDINGID` and `FLOOR` are fused into unified spatial zone categories (e.g., `Building0_Floor1`, `Building1_Floor3`) and transformed via `LabelEncoder`.


3. **Dimensionality Reduction:**
* `PCA(n_components=0.95)` is fitted strictly on training data and used to transform both train and evaluation sets.


4. **Model Architecture:**
* **Input Layer:** Dense (128 units, ReLU activation) + Dropout (0.3)
* **Hidden Layers:** Dense (64 units, ReLU) + Dropout (0.2) $\rightarrow$ Dense (32 units, ReLU)
* **Output Layer:** Dense ($N_{\text{classes}}$ units, Softmax activation)
* **Compilation:** Adam Optimizer ($\text{lr}=0.001$), Loss: `sparse_categorical_crossentropy`


5. **Coverage Quality Auditing:**
* Scans where $\max(\text{RSSI}_{\text{available}}) < -80\text{ dBm}$ are flagged as connection drop hazards and aggregated by `SPACEID`/location to generate IT installation priorities.



---

## 📁 Repository Directory Structure

```text
campus-wifi-localization/
│
├── data/                               # Dataset storage directory
│   ├── trainingData.csv                # Benchmark training dataset (UJIIndoorLoc)
│   ├── validationData.csv              # Benchmark validation dataset (UJIIndoorLoc)
│   ├── campus_wifi_raw_log.csv         # Custom raw BSSID log captured on campus
│   ├── custom_trainingData.csv         # Pivoted custom dataset (wide WAP format)
│   └── wap_mac_mapping.csv             # Reference mapping between MAC addresses & WAP columns
│
├── models/                             # Output directory for serialized artifacts
│   ├── nn_localization_model.keras     # Trained Keras Neural Network model
│   ├── pca_transformer.pkl             # Fitted PCA object (retaining 95% variance)
│   └── label_encoder.pkl               # Saved LabelEncoder mapping for Building_Floor
│
├── reports/                            # Analytics & output reports
│   └── facilities_dead_zone_report.csv # Priority ranking of flagged dead zones for IT
│
├── windows_wifi_scanner.py             # Custom Data Collection: Logs netsh BSSIDs on Windows
├── pivot_wifi_data.py                  # Data Engineering: Converts long BSSID logs to wide WAPs
├── wifi_localization_model.py          # ML Pipeline: Data cleaning, PCA fitting, & DNN training
├── dead_zone_detector.py               # Analytics: Identifies weak coverage locations (< -80 dBm)
│
├── requirements.txt                    # Python environment dependencies
└── README.md                           # Comprehensive project documentation

```

---

## 🚀 Quickstart & Execution Guide

### 1. Environment Setup

```bash
# Clone repository
git clone [https://github.com/prachisharma666/Campus-Wifi-DeadZone-Detector.git](https://github.com/prachisharma666/Campus-Wifi-DeadZone-Detector.git)
cd campus-wifi-localization

# Create virtual environment
python -m venv venv

# Activate environment (Windows PowerShell)
.\venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt

```

### 2. Benchmark Model Training (UJIIndoorLoc)

Place `trainingData.csv` and `validationData.csv` inside the `data/` directory, then execute:

```bash
# Train the model, fit PCA, and evaluate validation accuracy
python wifi_localization_model.py

# Run dead-zone detection to extract coverage blind spots
python dead_zone_detector.py

```

---
└────────────────────────────────────────────────────────┴─────────────────────────┘

```

### 📍 Milestone 1: Custom Campus Data Gathering & Integration

* **Objective:** Replace the benchmark UJIIndoorLoc dataset with live, real-world WiFi fingerprint data gathered directly across our own university campus buildings.
* **Collection Strategy:**
1. **Physical Grid Mapping:** Obtain campus floor plans (Engineering, Library, Main Academic block) and map physical Reference Points (RPs) spaced 2–3 meters apart, focusing on known blind spots (stairwells, basements).
2. **Field Scanning:** Utilize `windows_wifi_scanner.py` on a Windows laptop to capture BSSID, SSID, and RSSI readings across 4 cardinal orientations at each reference point.
3. **Data Pipeline Transformation:** Execute `pivot_wifi_data.py` to structure raw BSSID scans into the wide format (`WAP001`–`WAPxxx`), generating `custom_trainingData.csv` and updating `wap_mac_mapping.csv`.
4. **Model Fine-Tuning:** Retrain the PCA transformer and Deep Neural Network on our local campus distribution to establish baseline accuracy and generate an actual campus dead-zone map.



└──────────────────────────────────────────────────────────────────────────┘

```

* **Key Features to Implement:**
1. **Live Scan Predictor:** An interface where users or laptop background agents can send a raw JSON/CSV scan, and the backend returns their predicted Building, Floor, and Space ID in real time.
2. **IT Facilities Dashboard:** An admin panel displaying an interactive heat map of campus coverage quality, highlighting zones where average RSSI drops below threshold levels.
3. **CSV Batch Ingestion:** Ability for IT engineers to upload raw scan files and receive instant PDF/CSV reports specifying exact locations needing additional Wireless Access Points (WAPs).


---

## 🛠️ Built With

* **Machine Learning & Math:** TensorFlow / Keras, Scikit-Learn, NumPy, Pandas
* **Data Collection & OS APIs:** Windows `netsh wlan` CLI, Subprocess API

```

```
