<<<<<<< HEAD
## Data Sources & Methodology

### Data Sources
- FastF1 API – Raw telemetry for Miami GP 2023, 2024, 2025
- Lap times, pit stops, stint data derived from session information

### Processing Pipeline
1. **Raw data extraction** (FastF1 + F1 API)
2. **Lap time conversion** to seconds
3. **Stint identification** using compound changes
4. **Statistical aggregation** (avg, min, max, count per stint)
5. **Final output** saved to `data/processed/`

### Outputs Generated
- **`tire_stints_analysis.csv`** – Processed tire stint data (input for dashboard)
- **`output/` directory** – Contains all generated plots:
  - `tire_lifespan.png` – Tire lifespan boxplot
  - `pit_window.png` – Median pit stop lap bar chart
  - `compare_3_winners.png` – Winner speed comparison
  - `plot_winner_*.html` – Interactive winner telemetry plots (throttle, brake, RPM, gear)
- **Dashboard** – Streamlit visualization of all processed data

### How to Use
1. Run `main.py` to generate processed data
2. Run `streamlit run dashboard.py` to view interactive dashboard
3. Check `output/` for static plots and HTML files
=======
# f1-telemetry-analytics
Interactive dashboard analyzing Formula 1 Miami Grand Prix tire strategy and winner telemetry (2023-2025)
>>>>>>> adb60a148f9c46d3c641b2d38bb01d751f112dab
