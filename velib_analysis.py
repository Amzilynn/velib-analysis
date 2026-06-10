# velib_analysis.py
"""
Vélib' Stations – Spatial Distribution Analysis
================================================
Research question:
  "Is the distribution of Vélib' stations in Paris uniform, or does it show
   non-uniform spatial patterns in capacity across the city?"

Steps:
  1. Load full catalogue via Paris Open Data API.
  2. Clean data (id, name, coordinates, capacity).
  3. Compute haversine distance from city centre.
  4. Label stations as Central (<=5 km) or Peripheral (>5 km).
  5. Compute per-group summary statistics.
  6. Produce 5 charts:
       - Map of stations coloured by area
       - Bar chart of station counts per area
       - Bar chart of average capacity per area
       - Scatter: Distance from centre vs Capacity        [NEW]
       - Boxplot: Capacity distribution by area           [NEW]
  7. Save everything in the 'outputs/' folder.

Run: python velib_analysis.py
"""

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

# ─── Constants ─────────────────────────────────────────────────────────────────
API_ENDPOINT = (
    "https://opendata.paris.fr/api/records/1.0/search/"
    "?dataset=velib-emplacement-des-stations&rows=10000"
)
CITY_CENTER = (48.8566, 2.3522)   # lat, lon – historic centre of Paris
RADIUS_KM   = 5.0                  # boundary between Central and Peripheral

# Consistent colour palette used across ALL charts
PALETTE = {"Central (<=5 km)": "#1f77b4", "Peripheral (>5 km)": "#ff7f0e"}

# ─── Helpers ───────────────────────────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    """Return great-circle distance (km) between two lat/lon points (vectorised)."""
    R = 6371.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlam = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(a))


# ─── Data loading ──────────────────────────────────────────────────────────────
def load_velib_data():
    """Download full station catalogue from Paris Open Data API."""
    resp = requests.get(API_ENDPOINT, timeout=30)
    resp.raise_for_status()
    records = resp.json()["records"]
    return pd.json_normalize(records)


# ─── Data preparation ──────────────────────────────────────────────────────────
def prepare(df):
    """Rename columns, extract lat/lon, enforce numeric types, drop nulls."""
    rename_map = {
        "fields.stationcode": "station_id",
        "fields.name":        "station_name",
        "fields.coordonnees_geo": "coordinates",
        "fields.capacity":    "capacity",
    }
    df = df.rename(columns=rename_map)[list(rename_map.values())]
    df = df.dropna(subset=["coordinates", "capacity"])
    df["latitude"]  = df["coordinates"].apply(lambda x: x[0])
    df["longitude"] = df["coordinates"].apply(lambda x: x[1])
    df["capacity"]  = pd.to_numeric(df["capacity"], errors="coerce")
    df = df.dropna(subset=["capacity"])
    return df


# ─── Grouping ──────────────────────────────────────────────────────────────────
def add_group(df):
    """Add distance_km and area_group columns."""
    d = haversine(df["latitude"], df["longitude"], CITY_CENTER[0], CITY_CENTER[1])
    df = df.copy()
    df["distance_km"] = d
    df["area_group"]  = np.where(d <= RADIUS_KM,
                                  "Central (<=5 km)",
                                  "Peripheral (>5 km)")
    return df


# ─── Summary statistics ────────────────────────────────────────────────────────
def compute_stats(df):
    """Return per-group station count and average capacity."""
    return (
        df.groupby("area_group")
          .agg(stations=("station_id", "nunique"),
               avg_capacity=("capacity", "mean"))
          .reset_index()
    )


# ─── Charts ────────────────────────────────────────────────────────────────────
def plot_map(df, out_dir):
    """Scatter map of all stations, coloured by area group."""
    fig, ax = plt.subplots(figsize=(8, 8))
    for grp, color in PALETTE.items():
        sub = df[df["area_group"] == grp]
        ax.scatter(sub["longitude"], sub["latitude"],
                   c=color, s=18, alpha=0.6, edgecolors="none", label=grp)
    ax.set_title("Vélib' Station Locations – Central vs Peripheral", fontsize=13)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(title="Area", fontsize=9)
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(out_dir / "01_stations_map.png", dpi=150)
    plt.close(fig)


def plot_counts(stats, out_dir):
    """Bar chart: number of distinct stations per area."""
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(stats["area_group"], stats["stations"],
                  color=[PALETTE[g] for g in stats["area_group"]], width=0.5)
    for bar, v in zip(bars, stats["stations"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                str(int(v)), ha="center", va="bottom", fontsize=11)
    ax.set_title("Number of Vélib' Stations per Area", fontsize=13)
    ax.set_xlabel("")
    ax.set_ylabel("Station Count")
    ax.set_ylim(0, stats["stations"].max() * 1.15)
    fig.tight_layout()
    fig.savefig(out_dir / "02_stations_bar.png", dpi=150)
    plt.close(fig)


def plot_avg_capacity(stats, out_dir):
    """Bar chart: average station capacity per area."""
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(stats["area_group"], stats["avg_capacity"],
                  color=[PALETTE[g] for g in stats["area_group"]], width=0.5)
    for bar, v in zip(bars, stats["avg_capacity"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                f"{v:.1f}", ha="center", va="bottom", fontsize=11)
    ax.set_title("Average Station Capacity per Area", fontsize=13)
    ax.set_xlabel("")
    ax.set_ylabel("Mean Capacity (bike docks)")
    ax.set_ylim(0, stats["avg_capacity"].max() * 1.2)
    fig.tight_layout()
    fig.savefig(out_dir / "03_capacity_bar.png", dpi=150)
    plt.close(fig)


# ── NEW CHART 1 ───────────────────────────────────────────────────────────────
def plot_distance_vs_capacity(df, out_dir):
    """
    Scatter plot: Distance from city centre (x) vs Station capacity (y).

    What it answers:
        Does capacity systematically decrease as we move away from the centre?
    Why it matters:
        This directly tests the spatial hypothesis using continuous data,
        not just a binary group split. A regression line makes the trend
        (or lack of it) immediately visible.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    for grp, color in PALETTE.items():
        sub = df[df["area_group"] == grp]
        ax.scatter(sub["distance_km"], sub["capacity"],
                   c=color, alpha=0.35, s=18, edgecolors="none", label=grp)

    # Linear regression line (numpy)
    m, b = np.polyfit(df["distance_km"], df["capacity"], 1)
    x_line = np.linspace(df["distance_km"].min(), df["distance_km"].max(), 200)
    ax.plot(x_line, m * x_line + b,
            color="black", linewidth=1.8, linestyle="--",
            label=f"Trend  (slope={m:.2f} docks/km)")

    ax.axvline(RADIUS_KM, color="grey", linewidth=1, linestyle=":",
               label=f"{RADIUS_KM} km boundary")

    ax.set_title("Distance from City Centre vs Station Capacity", fontsize=13)
    ax.set_xlabel("Distance from city centre (km)")
    ax.set_ylabel("Station capacity (bike docks)")
    ax.legend(fontsize=9, framealpha=0.8)
    ax.xaxis.set_minor_locator(mticker.AutoMinorLocator())
    fig.tight_layout()
    fig.savefig(out_dir / "04_distance_vs_capacity.png", dpi=150)
    plt.close(fig)


# ── NEW CHART 2 ───────────────────────────────────────────────────────────────
def plot_boxplot_capacity(df, out_dir):
    """
    Boxplot: Distribution of station capacity by area group.

    What it answers:
        Is the difference in capacity a genuine distributional shift,
        or just an artefact of one or two outliers pulling the mean?
    Why it matters:
        Averages can hide skewed or bimodal distributions.
        A boxplot instantly shows median, spread (IQR), and outliers –
        giving a much more honest picture of the data.
    """
    fig, ax = plt.subplots(figsize=(7, 5))

    groups   = ["Central (<=5 km)", "Peripheral (>5 km)"]
    data     = [df.loc[df["area_group"] == g, "capacity"].values for g in groups]
    colors   = [PALETTE[g] for g in groups]

    bp = ax.boxplot(data, patch_artist=True, widths=0.45,
                    medianprops=dict(color="black", linewidth=2))

    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)

    ax.set_xticks([1, 2])
    ax.set_xticklabels(groups, fontsize=10)
    ax.set_title("Distribution of Station Capacity – Central vs Peripheral",
                 fontsize=13)
    ax.set_ylabel("Station capacity (bike docks)")
    ax.set_xlabel("")

    # Annotate medians
    for i, d in enumerate(data, start=1):
        med = np.median(d)
        ax.text(i + 0.27, med, f"median={med:.0f}",
                va="center", fontsize=9, color="black")

    fig.tight_layout()
    fig.savefig(out_dir / "05_boxplot_capacity.png", dpi=150)
    plt.close(fig)


# ─── Main workflow ─────────────────────────────────────────────────────────────
def main():
    project_root = Path(__file__).parent
    out_dir = project_root / "outputs"
    out_dir.mkdir(exist_ok=True)

    print("Downloading data...")
    df_raw     = load_velib_data()
    df_clean   = prepare(df_raw)
    df_grouped = add_group(df_clean)
    stats      = compute_stats(df_grouped)

    # Save tidy CSVs
    df_grouped.to_csv(out_dir / "velib_clean.csv", index=False)
    stats.to_csv(out_dir / "area_stats.csv", index=False)

    # Generate all charts
    print("Generating charts...")
    plot_map(df_grouped, out_dir)
    plot_counts(stats, out_dir)
    plot_avg_capacity(stats, out_dir)
    plot_distance_vs_capacity(df_grouped, out_dir)   # NEW
    plot_boxplot_capacity(df_grouped, out_dir)        # NEW

    # Console summary
    print("\n=== Summary Statistics ===")
    print(stats.to_string(index=False))
    print("\nAll outputs saved in:", out_dir)
    print("Charts produced:")
    for f in sorted(out_dir.glob("*.png")):
        print(" ", f.name)


if __name__ == "__main__":
    main()
