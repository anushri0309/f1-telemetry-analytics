from src.fetch import load_session,sav_raw_data
from src.clean  import clean_laps
from src.analyze import (
    load_all_cleaned_data,
    analyze_tire_stint,
    plot_tire_lifespan,
    plot_pit_window,
    get_winner_telemetry_all_years,
    plot_last_3winners,
    plot_winner_throttle_plotly,
    plot_winner_brake_plotly,
    plot_winner_rpm_plotly,
    plot_winner_gear_plotly,
    create_track_heatmap_plotly,
    create_all_plotly_plots
)


def main():
    print("\n=== LOADING 2024 MIAMI ===")
    session_2024 = load_session(year=2024, gp_name='Miami', session_type='R', driver_str='4')
    sav_raw_data(session_2024, year=2024, gp_name='Miami')

    print("\n=== LOADING 2025 MIAMI ===")
    session_2025 = load_session(year=2025, gp_name='Miami', session_type='R', driver_str='81')
    sav_raw_data(session_2025, year=2025, gp_name='Miami')

    print("\n=== LOADING 2023 MIAMI ===")
    session_2025 = load_session(year=2023, gp_name='Miami', session_type='R', driver_str='1')
    sav_raw_data(session_2025, year=2023, gp_name='Miami')

    clean_laps(filepath="data/raw/Miami2023/laps.csv",year="Miami2023")
    clean_laps(filepath="data/raw/Miami2024/laps.csv", year="Miami2024")
    clean_laps(filepath="data/raw/Miami2025/laps.csv", year="Miami2025")



    # Load data

    print("\n" + "=" * 60)
    print("🏁 F1 Miami GP Tire Strategy Analysis")
    print("=" * 60 + "\n")

    print("📥 Loading cleaned data...")
    all_laps = load_all_cleaned_data()
    print(f"✅ Loaded {len(all_laps):,} total laps from 3 years\n")

    print(f"Available columns: {all_laps.columns.tolist()}\n")

    if 'Compound' not in all_laps.columns:
        print("❌ ERROR: No 'Compound' column found")
        return

    print("\n📊 Compound Distribution:")
    print(all_laps['Compound'].value_counts())

    print(f"\n📊 LapTime data type: {all_laps['LapTime'].dtype}")
    print(f"\n📊 Sample LapTime values:")
    print(all_laps['LapTime'].head())

    print("\n🔬 Analyzing tire stints...")
    try:
        stint_data = analyze_tire_stint(all_laps)

        if stint_data is not None and len(stint_data) > 0:
            print(f"\n✅ Found {len(stint_data)} tire stints")
            print(f"\n📊 Tire Lifespan Summary:")
            print(stint_data.groupby('Compound')['stint_length'].agg(['mean', 'std', 'min', 'max']))

            print(f"\n📋 Sample stints (first 5):")
            print(stint_data[['Driver', 'Compound', 'stint_length', 'avg_laptime']].head())

            print("\n📈 Creating plots...")
            plot_tire_lifespan(stint_data)
            plot_pit_window(all_laps)

            print("\n✅ Analysis complete!")
        else:
            print("❌ No stint data found")

    except TypeError as e:
        print(f"\n❌ ERROR: {e}")
        print("\nFix: Convert LapTime to numeric seconds before aggregation")

    # Usage:
    telemetry_3winners = get_winner_telemetry_all_years()

    # Access individual driver data:
    verstappen_telem = telemetry_3winners[2023]['car_data']
    norris_telem = telemetry_3winners[2024]['car_data']
    piastri_telem = telemetry_3winners[2025]['car_data']

    telemetry_3winners = get_winner_telemetry_all_years()
    plot_last_3winners(telemetry_3winners)
    telemetry_dict = get_winner_telemetry_all_years()
    plot_winner_throttle_plotly(telemetry_dict)
    create_all_plotly_plots(telemetry_dict)
if __name__== "__main__":
    main()
