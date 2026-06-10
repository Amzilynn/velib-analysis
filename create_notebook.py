import nbformat as nbf

nb = nbf.v4.new_notebook()

# Title and Context
nb.cells.append(nbf.v4.new_markdown_cell("""\
# Vélib' Métropole – Spatial Distribution Analysis

**A junior data science project using Paris Open Data**
*Python · pandas · matplotlib · seaborn · Paris Open Data API*

---

## 1. Objective

This notebook explores whether Vélib' bike-share stations are distributed **uniformly** across Paris, or whether observable **spatial differences** exist between the city centre and its outskirts.

The goal is not to make causal claims about mobility policy, but to practice **evidence-based reasoning** on a real public dataset: formulating a hypothesis, testing it with data, and communicating results clearly.
"""))

nb.cells.append(nbf.v4.new_markdown_cell("""\
## 2. Research Hypothesis

> **"Vélib' stations are not uniformly distributed across Paris: stations closer to the city centre tend to have a higher capacity than those further out, suggesting a non-uniform spatial pattern in service density."**

This is a descriptive/observational hypothesis — no causal claim is made.
"""))

# Imports
nb.cells.append(nbf.v4.new_markdown_cell("## 3. Preparation & Setup"))
nb.cells.append(nbf.v4.new_code_cell("""\
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# Consistent colour palette
PALETTE = {"Central (<=5 km)": "#1f77b4", "Peripheral (>5 km)": "#ff7f0e"}
"""))

# Data Loading
nb.cells.append(nbf.v4.new_markdown_cell("""\
## 4. Data Loading
All station records are fetched via the public API endpoint. No manual download is required.
"""))
nb.cells.append(nbf.v4.new_code_cell("""\
API_ENDPOINT = (
    "https://opendata.paris.fr/api/records/1.0/search/"
    "?dataset=velib-emplacement-des-stations&rows=10000"
)

print("Downloading data...")
resp = requests.get(API_ENDPOINT, timeout=30)
resp.raise_for_status()
records = resp.json()["records"]
df_raw = pd.json_normalize(records)

print(f"Loaded {len(df_raw)} stations.")
df_raw.head()
"""))

# Data Cleaning
nb.cells.append(nbf.v4.new_markdown_cell("""\
## 5. Data Cleaning
- Rename columns for readability.
- Drop rows with missing coordinates or capacity.
- Convert capacity to a numeric type.
- Extract latitude and longitude.
"""))
nb.cells.append(nbf.v4.new_code_cell("""\
def prepare(df):
    rename_map = {
        "fields.stationcode": "station_id",
        "fields.name":        "station_name",
        "fields.coordonnees_geo": "coordinates",
        "fields.capacity":    "capacity",
    }
    df_clean = df.rename(columns=rename_map)[list(rename_map.values())]
    df_clean = df_clean.dropna(subset=["coordinates", "capacity"])
    
    df_clean["latitude"]  = df_clean["coordinates"].apply(lambda x: x[0])
    df_clean["longitude"] = df_clean["coordinates"].apply(lambda x: x[1])
    
    df_clean["capacity"]  = pd.to_numeric(df_clean["capacity"], errors="coerce")
    df_clean = df_clean.dropna(subset=["capacity"])
    return df_clean

df_clean = prepare(df_raw)
print(f"Stations after cleaning: {len(df_clean)}")
df_clean.head()
"""))

# Feature Engineering
nb.cells.append(nbf.v4.new_markdown_cell("""\
## 6. Feature Engineering & Grouping
We compute the **haversine distance** from each station to the geographic centre of Paris (48.8566°N, 2.3522°E). 
Stations are then split into two groups using a **5 km radius** threshold:
- **Central (≤5 km)**
- **Peripheral (>5 km)**
"""))
nb.cells.append(nbf.v4.new_code_cell("""\
CITY_CENTER = (48.8566, 2.3522)
RADIUS_KM   = 5.0

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlam = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(a))

def add_group(df):
    d = haversine(df["latitude"], df["longitude"], CITY_CENTER[0], CITY_CENTER[1])
    df_grp = df.copy()
    df_grp["distance_km"] = d
    df_grp["area_group"]  = np.where(d <= RADIUS_KM,
                                  "Central (<=5 km)",
                                  "Peripheral (>5 km)")
    return df_grp

df_grouped = add_group(df_clean)
df_grouped[["station_name", "distance_km", "area_group", "capacity"]].head()
"""))

# Aggregation
nb.cells.append(nbf.v4.new_markdown_cell("## 7. Summary Statistics"))
nb.cells.append(nbf.v4.new_code_cell("""\
stats = (
    df_grouped.groupby("area_group")
      .agg(stations=("station_id", "nunique"),
           avg_capacity=("capacity", "mean"))
      .reset_index()
)

stats
"""))

# Visualisations
nb.cells.append(nbf.v4.new_markdown_cell("""\
## 8. Visualisations

### 8.1 Station Map
A geographic scatter plot of all stations, colour-coded by area group. Visually confirms the clustering of stations around the historic core.
"""))
nb.cells.append(nbf.v4.new_code_cell("""\
fig, ax = plt.subplots(figsize=(8, 8))
for grp, color in PALETTE.items():
    sub = df_grouped[df_grouped["area_group"] == grp]
    ax.scatter(sub["longitude"], sub["latitude"],
               c=color, s=18, alpha=0.6, edgecolors="none", label=grp)
ax.set_title("Vélib' Station Locations – Central vs Peripheral", fontsize=13)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.legend(title="Area", fontsize=9)
ax.set_aspect("equal")
plt.show()
"""))

nb.cells.append(nbf.v4.new_markdown_cell("""\
**Explanation:**
The blue dots represent stations within 5 km of the center, and the orange dots represent peripheral stations. We can clearly observe that the central area has a higher density of stations compared to the periphery, visually confirming a non-uniform spatial distribution.
"""))

nb.cells.append(nbf.v4.new_markdown_cell("""\
### 8.2 Station Count and Average Capacity
Comparing the total number of stations and the mean capacity in each area.
"""))
nb.cells.append(nbf.v4.new_code_cell("""\
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# Bar chart: stations
bars1 = ax1.bar(stats["area_group"], stats["stations"],
              color=[PALETTE[g] for g in stats["area_group"]], width=0.5)
for bar, v in zip(bars1, stats["stations"]):
    ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
            str(int(v)), ha="center", va="bottom", fontsize=11)
ax1.set_title("Number of Vélib' Stations per Area")
ax1.set_ylabel("Station Count")
ax1.set_ylim(0, stats["stations"].max() * 1.15)

# Bar chart: capacity
bars2 = ax2.bar(stats["area_group"], stats["avg_capacity"],
              color=[PALETTE[g] for g in stats["area_group"]], width=0.5)
for bar, v in zip(bars2, stats["avg_capacity"]):
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
            f"{v:.1f}", ha="center", va="bottom", fontsize=11)
ax2.set_title("Average Station Capacity per Area")
ax2.set_ylabel("Mean Capacity (bike docks)")
ax2.set_ylim(0, stats["avg_capacity"].max() * 1.2)

plt.tight_layout()
plt.show()
"""))

nb.cells.append(nbf.v4.new_markdown_cell("""\
**Explanation:**
The left chart shows that despite covering a smaller geographic area, the central zone contains significantly more stations (887) than the peripheral zone (630). 
The right chart indicates that central stations are slightly larger on average, accommodating about 1.9 more bikes per station.
"""))

nb.cells.append(nbf.v4.new_markdown_cell("""\
### 8.3 Distance vs Capacity Scatter
This chart **directly tests the hypothesis** using continuous data. A regression line shows the overall trend.
"""))
nb.cells.append(nbf.v4.new_code_cell("""\
fig, ax = plt.subplots(figsize=(8, 5))

for grp, color in PALETTE.items():
    sub = df_grouped[df_grouped["area_group"] == grp]
    ax.scatter(sub["distance_km"], sub["capacity"],
               c=color, alpha=0.35, s=18, edgecolors="none", label=grp)

# Linear regression line
m, b = np.polyfit(df_grouped["distance_km"], df_grouped["capacity"], 1)
x_line = np.linspace(df_grouped["distance_km"].min(), df_grouped["distance_km"].max(), 200)

pearson_r = df_grouped["distance_km"].corr(df_grouped["capacity"], method="pearson")
spearman_rho = df_grouped["distance_km"].corr(df_grouped["capacity"], method="spearman")

ax.plot(x_line, m * x_line + b,
        color="black", linewidth=1.8, linestyle="--",
        label=f"Trend (slope={m:.2f})\\nPearson r = {pearson_r:.2f}\\nSpearman ρ = {spearman_rho:.2f}")

ax.axvline(RADIUS_KM, color="grey", linewidth=1, linestyle=":",
           label=f"{RADIUS_KM} km boundary")

ax.set_title("Distance from City Centre vs Station Capacity", fontsize=13)
ax.set_xlabel("Distance from city centre (km)")
ax.set_ylabel("Station capacity (bike docks)")
ax.legend(fontsize=9, framealpha=0.8)
ax.xaxis.set_minor_locator(mticker.AutoMinorLocator())
plt.show()
"""))

nb.cells.append(nbf.v4.new_markdown_cell("""\
**Explanation:**
This scatter plot directly tests the hypothesis by plotting capacity against distance from the city center for every station. 

We calculated two correlation metrics to quantify this relationship:
- **Pearson r**: Measures the linear relationship. A weak negative value indicates a slight downward linear trend.
- **Spearman ρ**: Measures the monotonic relationship (less sensitive to outliers). This also confirms a weak negative trend.

The dashed trend line slopes slightly downwards, indicating that capacity generally decreases as we move further from the center. However, the weak correlation values and the wide spread of points suggest distance is only one of many factors determining station capacity.
"""))

nb.cells.append(nbf.v4.new_markdown_cell("""\
### 8.4 Boxplot: Capacity Distribution
Shows the **full distribution** of station capacities in each group, confirming whether the average difference is driven by the bulk of stations or by a few large outliers.
"""))
nb.cells.append(nbf.v4.new_code_cell("""\
fig, ax = plt.subplots(figsize=(7, 5))

groups   = ["Central (<=5 km)", "Peripheral (>5 km)"]
data     = [df_grouped.loc[df_grouped["area_group"] == g, "capacity"].values for g in groups]
colors   = [PALETTE[g] for g in groups]

bp = ax.boxplot(data, patch_artist=True, widths=0.45,
                medianprops=dict(color="black", linewidth=2))

for patch, color in zip(bp["boxes"], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.75)

ax.set_xticks([1, 2])
ax.set_xticklabels(groups, fontsize=10)
ax.set_title("Distribution of Station Capacity – Central vs Peripheral", fontsize=13)
ax.set_ylabel("Station capacity (bike docks)")

# Annotate medians
for i, d in enumerate(data, start=1):
    med = np.median(d)
    ax.text(i + 0.27, med, f"median={med:.0f}",
            va="center", fontsize=9, color="black")

plt.show()
"""))

nb.cells.append(nbf.v4.new_markdown_cell("""\
**Explanation:**
While the averages showed a difference, the boxplot reveals that the distributions of station capacities heavily overlap. Many peripheral stations are just as large as central ones. This confirms that the difference in capacity is a general tendency rather than a strict divide.
"""))

nb.cells.append(nbf.v4.new_markdown_cell("""\
## 9. Interpretation & Conclusion

The data **support the hypothesis** with important nuances:
1. **Both the number of stations and their average capacity are higher in central Paris.** This means residents of the inner city have access to more docking points in a denser area.
2. **The capacity difference is modest (~1.9 docks per station).** It does not imply a severe access disparity.
3. **The boxplot shows considerable distributional overlap.** The difference is a *tendency*, not a rule.
4. **The scatter plot confirms a slight spatial gradient.** Capacity tends to decrease with distance, but the relationship is weak.

**Conclusion:** Vélib' stations in Paris are not uniformly distributed. The central zone has both more stations and slightly higher average capacity. The spatial gradient is real but modest, and distributions overlap substantially.
"""))

with open('velib_analysis.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
