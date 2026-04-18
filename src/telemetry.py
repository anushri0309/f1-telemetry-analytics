import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import matplotlib.patches as mpatches

sns.set(style="whitegrid")


def load_winner_telemetry(year, driver_number, gp_name='Miami'):
    """
    Load winner telemetry data from FastF1
    Returns session object with career telemetry
    """
    import fastf1

    # Map years to correct driver numbers for Miami winners
    driver_map = {
        2023: '1',  # Max Verstappen
        2024: '4',  # Lando Norris
        2025: '81'  # Oscar Piastri
    }

    driver_str = driver_map.get(year, str(driver_number))

    print(f"🏎️ Loading {year} Miami GP winner (Driver #{driver_str})...")

    # Load session
    session = fastf1.get_session(year, gp_name, 'R')
    session.load()

    # Get winner's telemetry
    driver_telem = session.drivers[driver_str].telemetry

    return session, driver_telem


def create_track_heatmap(telemetry, driver_name, year,
                         save_path="output/track_heatmap.png"):
    """
    Create track position heat map showing speed/telemetry distribution
    Uses X, Y coordinates from telemetry to show track layout with color intensity
    """
    plt.figure(figsize=(14, 8))

    # Extract X, Y and Speed
    x = telemetry['X'].values
    y = telemetry['Y'].values
    speed = telemetry['Speed'].values

    # Create scatter plot with speed as color
    scatter = plt.scatter(x, y, c=speed, cmap='hot',
                          s=2, alpha=0.6, vmin=0, vmax=350)

    # Add colorbar
    cbar = plt.colorbar(scatter, label='Speed (km/h)')
    cbar.set_fontsize(12)

    plt.title(f'{driver_name} - {year} Miami GP\nTrack Speed Heat Map',
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('X Position (m)', fontsize=12)
    plt.ylabel('Y Position (m)', fontsize=12)
    plt.axis('equal')
    plt.grid(False)

    Path("output").mkdir(exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✅ Saved track heat map: {save_path}")
    return save_path


def create_speed_trace_over_laps(telemetry, driver_name, year,
                                 save_path="output/speed_trace_laps.png"):
    """
    Show speed variation throughout the race by lap
    """
    plt.figure(figsize=(14, 6))

    # Need Distance or Time to show progression
    if 'Distance' in telemetry.columns:
        x_col = 'Distance'
        xlabel = 'Distance Along Track (m)'
    else:
        x_col = 'Time'
        xlabel = 'Time'

    x = telemetry[x_col].values
    speed = telemetry['Speed'].values

    plt.plot(x, speed, linewidth=0.8, color='#ff6b35', alpha=0.7)
    plt.fill_between(x, speed, alpha=0.3, color='#ff6b35')

    plt.title(f'{driver_name} - {year} Miami GP\nSpeed Trace Throughout Race',
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel('Speed (km/h)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    Path("output").mkdir(exist_ok=True)
    plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"✅ Saved speed trace: {save_path}")
    return save_path


def plot_winner_speed_traces(all_sessions_data, save_path="output/compare_winner_speeds.png"):
    """
    Compare speed traces across all 3 winners (2023-2025 Miami)

    all_sessions_data: dict like {
        2023: (session, telemetry, 'Max Verstappen'),
        2024: (session, telemetry, 'Lando Norris'),
        2025: (session, telemetry, 'Oscar Piastri')
    }
    """
    plt.figure(figsize=(14, 7))

    colors = {2023: '#062C4D', 2024: '#FF8700', 2025: '#3D8B3D'}  # Red Bull, McLaren, McLaren green
    drivers = {2023: 'Verstappen 2023', 2024: 'Norris 2024', 2025: 'Piastri 2025'}

    for year, (session, telemetry, driver_name) in all_sessions_data.items():
        x = telemetry['Distance'].values if 'Distance' in telemetry.columns else range(len(telemetry))
        speed = telemetry['Speed'].values

        # Smooth for comparison
        window = min(100, len(speed) // 10)
        if window > 1:
            speed_smooth = np.convolve(speed, np.ones(window) / window, mode='same')
        else:
            speed_smooth = speed

        plt.plot(speed_smooth, linewidth=1.5, color=colors[year],
                 label=drivers[year], alpha=0.8)

    plt.title('Miami GP Winners - Speed Trace Comparison (2023-2025)',
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Distance / Time Along Track', fontsize=12)
    plt.ylabel('Speed (km/h)', fontsize=12)
    plt.legend(fontsize=11, loc='upper right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    Path("output").mkdir(exist_ok=True)
    plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"✅ Saved winner speed comparison: {save_path}")
    return save_path


def compare_cornering_winners(telemetry_2023, telemetry_2024, telemetry_2025,
                              save_path="output/cornering_comparison.png"):
    """
    Compare cornering speeds between the 3 Miami winners
    Identifies slow-speed sections (corners) and compares entry/exit speeds
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    drivers = [(telemetry_2023, 'Verstappen 2023', axes[0]),
               (telemetry_2024, 'Norris 2024', axes[1]),
               (telemetry_2025, 'Piastri 2025', axes[2])]

    speeds = []

    for i, (telemetry, driver_name, ax) in enumerate(drivers):
        speed = telemetry['Speed'].values

        speeds.append(speed)

        # Box plot of speeds (shows cornering vs straight distribution)
        ax.boxplot(speed, vert=True, patch_artist=True,
                   boxprops=dict(facecolor='#FF8700', alpha=0.7))

        ax.set_title(driver_name, fontsize=14, fontweight='bold')
        ax.set_ylabel('Speed (km/h)', fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_xticks([])

    plt.suptitle('Miami GP Winners - Cornering Speed Distribution (2023-2025)',
                 fontsize=18, fontweight='bold', y=1.02)
    plt.tight_layout()

    Path("output").mkdir(exist_ok=True)
    plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"✅ Saved cornering comparison: {save_path}")

    # Return statistics for analysis
    stats = {}
    for i, (telemetry, driver_name, _) in enumerate(drivers):
        speed = telemetry['Speed'].values
        stats[driver_name] = {
            'mean_speed': np.mean(speed),
            'max_speed': np.max(speed),
            'min_speed': np.min(speed),
            'std_speed': np.std(speed)
        }

    return stats


def create_lap_by_lap_speed_heatmap(telemetry, driver_name, year, lap_numbers=[1, 5, 10, 'fastest'],
                                    save_path="output/lap_speed_heatmap.png"):
    """
    Create comparative heat maps showing speed evolution across key laps
    Shows how driver's speed changed throughout the race
    """
    laps_to_plot = lap_numbers.copy()

    # Get unique laps if Dataframe has LapNumber
    if 'LapNumber' not in telemetry.columns:
        print("⚠️ No LapNumber column, showing whole race instead")
        plt.figure(figsize=(12, 6))
        plt.scatter(range(len(telemetry)), telemetry['Speed'].values,
                    c=telemetry['Speed'].values, cmap='viridis', s=10, alpha=0.6)
        plt.colorbar(label='Speed (km/h)')
        plt.title(f'{driver_name} - {year} Miami GP\nSpeed Over Race Distance',
                  fontsize=16, fontweight='bold')
        plt.xlabel('Data Point')
        plt.ylabel('Speed (km/h)')
        Path("output").mkdir(exist_ok=True)
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for i, lap in enumerate(laps_to_plot):
        if lap == 'fastest':
            # Find fastest lap
            fastest_lap_num = telemetry.groupby('LapNumber')['LapTime'].min().idxmax()
            lap_data = telemetry[telemetry['LapNumber'] == fastest_lap_num]
            title = f'Fastest Lap (Lap {fastest_lap_num})'
        else:
            lap_data = telemetry[telemetry['LapNumber'] == lap]
            title = f'Lap {lap}'

        if len(lap_data) > 0:
            x = lap_data['X'].values
            y = lap_data['Y'].values
            speed = lap_data['Speed'].values

            scatter = axes[i].scatter(x, y, c=speed, cmap='viridis',
                                      s=15, alpha=0.7, vmin=0, vmax=350)
            axes[i].set_title(f'{title}\nAvg Speed: {np.mean(speed):.1f} km/h',
                              fontsize=12, fontweight='bold')
            axes[i].set_xlabel('X (m)')
            axes[i].set_ylabel('Y (m)')
            axes[i].set_aspect('equal')
            axes[i].grid(False)

            # Add colorbar to each
            cbar = plt.colorbar(scatter, ax=axes[i])
            cbar.set_label('Speed (km/h)', fontsize=10)

    plt.suptitle(f'{driver_name} - {year} Miami GP\nLap-by-Lap Speed Heat Maps',
                 fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()

    Path("output").mkdir(exist_ok=True)
    plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"✅ Saved lap-by-lap heat map: {save_path}")
    return save_path


def analyze_winner_telemetry_summary(telemetry, driver_name, year):
    """
    Generate key telemetry statistics for winner analysis
    """
    summary = {
        'Driver': driver_name,
        'Year': year,
        'Mean Speed (km/h)': round(telemetry['Speed'].mean(), 2),
        'Max Speed (km/h)': round(telemetry['Speed'].max(), 2),
        'Min Speed (km/h)': round(telemetry['Speed'].min(), 2),
        'Speed Std Dev': round(telemetry['Speed'].std(), 2),
        'Total Distance (km)': round(telemetry['Distance'].max() / 1000,
                                     2) if 'Distance' in telemetry.columns else 'N/A',
        'Lap Count': telemetry['LapNumber'].nunique() if 'LapNumber' in telemetry.columns else 'N/A'
    }

    return pd.DataFrame([summary])


# ============= MAIN EXECUTION FOR MIAMI WINNERS =============
if __name__ == "__main__":
    import fastf1

    print("=" * 70)
    print("🏁 F1 MIAMI GP WINNER TELEMETRY ANALYSIS (2023-2025)")
    print("=" * 70)

    # Winner info
    winners = {
        2023: {'name': 'Max Verstappen', 'number': '1'},
        2024: {'name': 'Lando Norris', 'number': '4'},
        2025: {'name': 'Oscar Piastri', 'number': '81'}
    }

    all_telemetry = {}

    for year in [2023, 2024, 2025]:
        winner = winners[year]
        print(f"\n{'=' * 70}")
        print(f"🏆 Analyzing {winner['name']} - {year} Miami GP Winner")
        print(f"{'=' * 70}")

        # Load session and telemetry
        session = fastf1.get_session(year, 'Miami', 'R')
        session.load()

        driver_telem = session.drivers[winner['number']].telemetry

        # Store for comparison
        all_telemetry[year] = (session, driver_telem, winner['name'])

        # === Create heat maps ===
        print(f"\n🗺️ Creating track heat map...")
        create_track_heatmap(
            driver_telem,
            winner['name'],
            year,
            save_path=f"output/track_heatmap_{year}_{winner['name'].replace(' ', '_')}.png"
        )

        print(f"\n📈 Creating speed trace...")
        create_speed_trace_over_laps(
            driver_telem,
            winner['name'],
            year,
            save_path=f"output/speed_trace_{year}_{winner['name'].replace(' ', '_')}.png"
        )

        # === Analyze summary stats ===
        print(f"\n📊 Telemetry Summary:")
        summary = analyze_winner_telemetry_summary(driver_telem, winner['name'], year)
        print(summary)

        # Save summary
        summary.to_csv(f"output/telemetry_summary_{year}.csv", index=False)

    print(f"\n{'=' * 70}")
    print("🔥 Creating COMPARISON plots across all 3 winners...")
    print(f"{'=' * 70}")

    # === Compare all winners ===
    plot_winner_speed_traces(all_telemetry)

    compare_cornering_winners(
        all_telemetry[2023][1],
        all_telemetry[2024][1],
        all_telemetry[2025][1]
    )

    print(f"\n✅ ANALYSIS COMPLETE! Check 'output/' folder for all plots")