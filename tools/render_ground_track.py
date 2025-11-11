"""
Generates a plot of the repeating ground track from CSV data.
"""
import argparse
import re
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
        help="Path to the ground track CSV file. If not provided, it will be constructed using --duration-days.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory in which to save the plot.",
    )
    parser.add_argument(
        "--duration-days",
        type=int,
        help="The duration in days for which the ground track was propagated. Used for input/output filename construction.",
    )
    args = parser.parse_args()

    if args.input_csv:
        input_csv_path = args.input_csv
        match = re.search(r'_(\d+)day\.csv', str(input_csv_path.name))
        if match:
            duration_days_str = f"{match.group(1)}-Day"
        else:
            duration_days_str = "N-Day"
    elif args.duration_days is not None:
        duration_days_str = f"{args.duration_days}-Day"
        input_csv_path = args.output_dir.parent / f"ground_track_{args.duration_days}day.csv"
    else:
        raise ValueError("Either --input-csv or --duration-days must be provided.")

    df = pd.read_csv(input_csv_path)

    plot_title = f'{duration_days_str} Repeating Ground Track over Tehran'
    output_filename = f"{duration_days_str.replace('-','').lower()}_ground_track.svg"


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

    ax.set_title(plot_title)
    ax.legend()
    ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.output_dir / output_filename
    plt.savefig(output_path, dpi=300, format='svg')
    print(f"Ground track plot saved to: {output_path}")

if __name__ == "__main__":
    main()
