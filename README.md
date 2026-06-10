# Vélib' Métropole – Spatial Distribution Analysis

> **A junior data science project using Paris Open Data**  
> *Python · pandas · matplotlib · seaborn · Paris Open Data API*

---

## 1. Objective

This project explores whether Vélib' bike-share stations are distributed **uniformly** across Paris, or whether observable **spatial differences** exist between the city centre and its outskirts.

The goal is not to make causal claims about mobility policy, but to practice **evidence-based reasoning** on a real public dataset: formulating a hypothesis, testing it with data, and communicating results clearly.

---

## 2. Research Hypothesis

> **"Vélib' stations are not uniformly distributed across Paris: stations closer to the city centre tend to have a higher capacity than those further out, suggesting a non-uniform spatial pattern in service density."**

This is a descriptive/observational hypothesis — no causal claim is made.

---

## 3. Dataset

| Property | Value |
|----------|-------|
| **Source** | [Paris Open Data](https://opendata.paris.fr/explore/dataset/velib-emplacement-des-stations/) |
| **Access** | REST API (JSON) |
| **Records loaded** | ~1 500 stations |
| **Key fields used** | `stationcode`, `name`, `coordonnees_geo`, `capacity` |
| **Type** | Static infrastructure snapshot (not real-time availability) |

---

## 4. Methodology

### Step 1 – Data Loading
All station records were fetched via the public API endpoint using the `requests` library. No manual download was required.

### Step 2 – Data Cleaning
- Dropped rows with missing coordinates or capacity values.
- Converted capacity to numeric type.
- Extracted latitude and longitude from the coordinate pair field.

### Step 3 – Feature Engineering
Computed the **haversine distance** from each station to the geographic centre of Paris (48.8566°N, 2.3522°E). This gives a continuous spatial metric without relying on administrative boundaries.

### Step 4 – Grouping
Stations were split into two groups using a **5 km radius** threshold:
- **Central (≤5 km)** – 887 stations
- **Peripheral (>5 km)** – 630 stations

The 5 km boundary was chosen to broadly capture the inner arrondissements (1–11) while keeping the method transparent and reproducible.

### Step 5 – Aggregation
For each group:
- Count of distinct stations
- Mean station capacity (number of bike docks)

### Step 6 – Visualisation
Five charts were produced (see `outputs/`).

---

## 5. Results

| Area | Stations | Avg. Capacity (docks) |
|------|----------|-----------------------|
| **Central (≤5 km)** | **887** | **33.3** |
| **Peripheral (>5 km)** | 630 | 31.4 |

**Key numerical observations:**
- The central zone contains **41% more stations** than the peripheral zone.
- Average capacity is **1.9 docks/station higher** in the central zone.
- The trend line in the scatter plot shows a **slight negative slope**: capacity tends to decrease modestly as distance from the centre increases.
- The **boxplot** shows overlapping distributions, confirming the difference exists but is not a sharp divide.

---

## 6. Visualisations

### 01 – Station Map
A geographic scatter plot of all stations, colour-coded by area group (blue = Central, orange = Peripheral). Visually confirms the clustering of stations around the historic core.

### 02 – Station Count Bar Chart
Compares the total number of stations in each area. Central Paris hosts significantly more stations (887 vs 630), despite covering a smaller geographic surface.

### 03 – Average Capacity Bar Chart
Shows the mean number of bike docks per station in each area. The central zone averages ~1.9 more docks per station — a modest but consistent difference.

### 04 – Distance vs Capacity Scatter
Each point represents one station. The x-axis is distance from the city centre; the y-axis is station capacity. A regression line shows the overall trend. This chart **directly tests the hypothesis** using continuous data.

### 05 – Boxplot: Capacity Distribution
Shows the **full distribution** of station capacities in each group — not just the average. The median, interquartile range, and outliers are all visible.

---

## 7. Interpretation

The data **support the hypothesis** with important nuances:

1. **Both the number of stations and their average capacity are higher in central Paris.**
2. **The capacity difference is modest (~1.9 docks per station).** It does not imply a severe access disparity.
3. **The boxplot shows considerable distributional overlap.** The difference is a *tendency*, not a rule.
4. **The scatter plot confirms a slight spatial gradient.** The relationship is weak, meaning geography is only one of many factors.

> **Caution:** This analysis does not measure actual bike availability, usage frequency, or demand. Conclusions about service quality cannot be drawn from infrastructure data alone.

---

## 8. Limitations

| Limitation | Impact |
|------------|--------|
| **Static snapshot** | Captures planned infrastructure, not real-time availability. |
| **Radial grouping simplification** | A single distance threshold ignores neighbourhood heterogeneity. |
| **No demand data** | Station density says nothing about whether supply meets local demand. |
| **No temporal dimension** | Cannot capture seasonal patterns or time-of-day variation. |
| **Causal inference** | Observed differences cannot be attributed to any specific policy factor. |

---

## 9. Conclusion

Vélib' stations in Paris are **not uniformly distributed**. The central zone has both more stations and slightly higher average capacity. The spatial gradient is real but modest, and distributions overlap substantially.

---

## 10. Repository Structure

```
velib-analysis/
├── velib_analysis.py          # Main analysis script (Python 3)
├── requirements.txt           # pip dependencies
├── README.md                  # This file
├── .gitignore
└── outputs/
    ├── 01_stations_map.png
    ├── 02_stations_bar.png
    ├── 03_capacity_bar.png
    ├── 04_distance_vs_capacity.png
    ├── 05_boxplot_capacity.png
    └── area_stats.csv
```

---

## 11. How to Run

```bash
# Clone the repository
git clone https://github.com/Amzilynn/velib-analysis.git
cd velib-analysis

# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\activate        # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Run the analysis
python velib_analysis.py
```

All outputs are saved automatically in the `outputs/` folder.

---

*Data source: [opendata.paris.fr](https://opendata.paris.fr) · Licence Ouverte v2.0*
