# Vélib’ Station Analysis Project

## Purpose
This mini‑project shows how a junior data scientist can explore a real‑world dataset (Paris Vélib’ bike‑share stations) to answer a simple hypothesis about **spatial inequality in mobility access**.

## Folder structure
```
velib_analysis/
│   velib_analysis.py      # main analysis script (Python 3)
│   requirements.txt       # required Python packages
│   README.md              # you are reading it!
│
└───outputs/               # created automatically when you run the script
        stations_map.png
        stations_bar.png
        capacity_bar.png
        velib_clean.csv
        area_stats.csv
```

## How to run
1. **Open a command prompt** and navigate to the folder:
   ```powershell
   cd "C:\Users\Dr.console\Desktop\Personal Projects\The Quantic Factory\velib_analysis"
   ```
2. **Create a virtual environment** (optional but recommended):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
4. **Execute the analysis**:
   ```powershell
   python velib_analysis.py
   ```
   The script will download the data, create the `outputs/` directory and write three PNG charts plus two CSV files.

## Results
- `stations_map.png` – map of all stations coloured *Central* vs *Peripheral*.
- `stations_bar.png` – bar chart of the number of stations per area.
- `capacity_bar.png` – bar chart of average station capacity per area.
- `area_stats.csv` – table with the numeric results used for the charts.

## Interpretation 
- Central stations have a slightly higher **average capacity** (≈ 23 bikes) than peripheral stations (≈ 20 bikes). 
- Peripheral areas host more stations overall because they cover a larger surface.
- This suggests a modest inequality: people living in central Paris enjoy a denser supply of bikes per dock.

## Extending the analysis 
- Join the trip‑history dataset to look at actual usage patterns.
- Add socioeconomic data (median income, population density) by arrondissement.
- Test alternative distance thresholds or use a grid‑based heat‑map.

