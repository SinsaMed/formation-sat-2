"""
Generates a plot of the 14-day repeating ground track from CSV data.
"""
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-csv",
        type=Path,
        required=True,
        help="Path to the 14-day ground track CSV file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory in which to save the plot.",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.input_csv)

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.LAND, edgecolor='black')
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.RIVERS)

    # Plot ground tracks for each satellite
    for sat_id in df['satellite_id'].unique():
        sat_df = df[df['satellite_id'] == sat_id]
        ax.plot(sat_df['longitude_deg'], sat_df['latitude_deg'], transform=ccrs.PlateCarree(), label=sat_id, linewidth=0.5)

    # Mark Tehran
    tehran_lat = 35.6892
    tehran_lon = 51.3890
    ax.plot(tehran_lon, tehran_lat, 'ro', markersize=8, transform=ccrs.PlateCarree(), label='Tehran')
    ax.text(tehran_lon + 3, tehran_lat + 3, 'Tehran', transform=ccrs.PlateCarree())

    ax.set_title('14-Day Repeating Ground Track over Tehran')
    ax.legend()
    ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.output_dir / "14day_ground_track.svg"
    plt.savefig(output_path, dpi=300, format='svg')
    print(f"14-day ground track plot saved to: {output_path}")

if __name__ == "__main__":
    main()
