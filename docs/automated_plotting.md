# Automated Plot Generation

This document describes the automated plot generation feature that has been integrated into the debug workflow.

## Overview

The `run_debug.py` script has been updated to automatically generate a comprehensive set of plots for each simulation run. This ensures that all relevant visualizations are consistently produced, providing a complete picture of the simulation results without requiring manual intervention.

When you execute a triangle formation simulation using `run_debug.py --triangle`, the script will now perform the following steps:

1.  **Run the simulation**: The core simulation is executed as before, generating the raw data artefacts (CSV files, JSON summaries, etc.).
2.  **Generate debug plots**: The `tools/render_debug_plots.py` script is called to produce a set of standard visualizations, including time-series plots and 3D formation views.
3.  **Generate report plots**: The `tools/generate_triangle_report.py` script is then called to create a more extensive set of analytical plots, such as sensitivity analyses, maintenance projections, and performance metrics.

All generated plots are saved in the `plots` subdirectory within the corresponding run's artefact directory (e.g., `artefacts/debug/YYYYMMDDTHHMMSSZ/plots/`).

## Benefits

-   **Consistency**: Ensures that the same set of plots is generated for every run, making it easier to compare results across different simulations.
-   **Efficiency**: Eliminates the need to manually run separate plotting scripts after each simulation, saving time and reducing the chance of errors.
-   **Completeness**: Guarantees that all available visualizations are produced, providing a comprehensive overview of the simulation results.

## Usage

To use the automated plot generation feature, simply run the debug script with the `--triangle` flag as you normally would:

```bash
python run_debug.py --triangle
```

The script will automatically handle the generation of all plots and log the progress to the console.
