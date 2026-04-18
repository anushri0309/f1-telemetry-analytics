import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


sns.set(style="whitegrid")


def load_all_cleaned_data(years=["Miami2023", "Miami2024", "Miami2025"]):
    all_data = []
    for year in years:
        filepath = Path("data/processed") / year / "laps_cleaned.csv"
        if filepath.exists():
            df = pd.read_csv(filepath)
            df['year'] = year
            all_data.append(df)
    return pd.concat(all_data, ignore_index=True)


def analyze_tire_stint(df):
    """FIXED: Convert LapTime to seconds before aggregation"""
    df = df.sort_values(['DriverNumber', 'year', 'LapNumber'])

    if 'Compound' not in df.columns:
        print(" No 'compound' column found!")
        print(f"Available columns: {df.columns.tolist()}")
        return None

    #  Convert LapTime to numeric (seconds) FIRST
    if 'LapTime' in df.columns:
        # If it's timedelta format ('0 days 00:01:32.058')
        df['LapTime_seconds'] = pd.to_timedelta(df['LapTime']).dt.total_seconds()
    else:
        print(" No LapTime column found")
        return None

    # Create stint_id (always)
    if 'Stint' in df.columns:
        df['stint_id'] = df['Stint']
    else:
        df['stint_id'] = (df['Compound'] != df.groupby(['DriverNumber', 'year'])
        ['Compound'].shift(1)).cumsum()

    # ✅ Use LapTime_seconds (numeric) instead of LapTime
    stint_data = df.groupby(['Driver', 'year', 'Compound', 'stint_id']).agg({
        'LapNumber': ['min', 'max', 'count'],
        'LapTime_seconds': ['mean', 'min', 'max']  # Use seconds column
    })

    stint_data.columns = ['stint_start', 'stint_end', 'stint_length',
                          'avg_laptime', 'best_laptime', 'worst_laptime']

    stint_data = stint_data.reset_index()
    stint_data.to_csv("data/processed/tire_stints_analysis.csv", index=False)
    print(f"\n💾 Saved stint analysis to: {Path('data/processed/tire_stints_analysis.csv')}")
    print(f"\n📊 Stint Data Preview:")
    print(stint_data.head(10))

    return stint_data

def plot_tire_lifespan(stint_data,save_path="output/tire_lifespan.png"):
    plt.figure(figsize=(12,6))
    sns.boxplot(x='Compound',y='stint_length',data=stint_data)
    plt.title('Tire Life at Miami GP(2023-2025)',fontsize=16,fontweight='bold')
    plt.xlabel("Tire Compound",fontsize=12)
    plt.ylabel("Stint Length(Laps)",fontsize=12)
    plt.tight_layout()
    Path("output").mkdir(exist_ok=True)
    plt.savefig(save_path,dpi=300)
    plt.show()


def plot_pit_window(df, save_path="output/pit_window.png"):
    df = df.sort_values(['DriverNumber', 'year', 'LapNumber'])

    #  YOUR CODE (perfect!)
    if 'Stint' in df.columns:
        df['pit_stop'] = df['Stint'] != df.groupby(['DriverNumber', 'year'])['Stint'].shift(1)
    else:
        df['pit_stop'] = df['Compound'] != df.groupby(['DriverNumber', 'year'])['Compound'].shift(1)

    # FIX: Only count pit stops AFTER Lap 3 (ignore start)
    pit_laps = df[(df['pit_stop']) & (df['LapNumber'] > 3)].groupby('year')['LapNumber'].median()

    #  ADD: Debug print
    print(f"\n Pit stops found (Lap > 3):")
    print(pit_laps)

    plt.figure(figsize=(10, 6))
    sns.barplot(x=pit_laps.index, y=pit_laps.values)
    plt.title("Median Pit Stop Lap by Year - Miami GP", fontsize=16, fontweight='bold')
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Median Pit Lap", fontsize=12)
    plt.axhline(y=20, color='red', linestyle='--', label='Optimal: ~lap 20')
    plt.legend()
    plt.tight_layout()
    Path("output").mkdir(exist_ok=True)
    plt.savefig(save_path, dpi=300)
    plt.show()


def get_winner_telemetry_all_years():
    """Get telemetry for all 3 Miami GP winners (2023-2025)"""
    import fastf1

    winners = {
        2023: {'driver': 'VER', 'number': '1', 'name': 'Max Verstappen'},
        2024: {'driver': 'NOR', 'number': '4', 'name': 'Lando Norris'},
        2025: {'driver': 'PIA', 'number': '81', 'name': 'Oscar Piastri'}
    }

    telemetry_dict = {}

    for year, winner in winners.items():
        print(f"\n🏎️ Loading {winner['name']} - {year} Miami GP")

        # Load session
        session = fastf1.get_session(year, 'Miami', 'R')
        session.load(telemetry=True, laps=True)

        # Get fastest lap telemetry
        fastest_lap = (session.laps
                       .pick_driver(winner['number'])
                       .pick_fastest())

        car_data = fastest_lap.get_car_data().add_distance()
        gps_data = fastest_lap.get_telemetry().add_distance()

        telemetry_dict[year] = {
            'name': winner['name'],
            'number': winner['number'],
            'car_data': car_data,  # Speed, Throttle, Brake, RPM, Gear
            'gps_data': gps_data,  # X, Y positions
            'fastest_lap': fastest_lap
        }

        print(f"   ✅ Loaded {len(car_data)} data points")
        print(f"   Fastest lap: {fastest_lap['LapTime']}")

    return telemetry_dict




def plot_last_3winners(telemetry_dict, save_path="output/compare_3_winners.png"):
    """Plot speed comparison for the 3 Miami winners"""
    import matplotlib.pyplot as plt

    plt.figure(figsize=(14, 7))

    # Colors for each driver/team
    colors = {
        'Max Verstappen': '#062C4D',  # Red Bull blue
        'Lando Norris': '#FF8700',  # McLaren orange
        'Oscar Piastri': '#3D8B3D'  # McLaren green
    }

    for year, data in telemetry_dict.items():
        driver_name = data['name']
        car_data = data['car_data']

        plt.plot(car_data['Distance'], car_data['Speed'],
                 linewidth=1.5, color=colors.get(driver_name, 'gray'),
                 label=f"{driver_name} ({year})")

    plt.title('Miami GP Winners - Fastest Lap Speed Comparison (2023-2025)',
              fontsize=16, fontweight='bold')
    plt.xlabel('Distance (m)', fontsize=12)
    plt.ylabel('Speed (km/h)', fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    Path("output").mkdir(exist_ok=True)
    plt.savefig(save_path, dpi=300)
    plt.show()

# Add this RIGHT AFTER your imports (before any functions)

def get_winner_color(driver_name):
    """Custom color function for Miami winners - avoids FastF1 conflict"""
    colors = {
        'Max Verstappen': '#062C4D',  # Red Bull blue
        'Lando Norris': '#FF8700',     # McLaren orange
        'Oscar Piastri': '#3D8B3D'     # McLaren green
    }
    return colors.get(driver_name, '#333333')

def plot_winner_throttle_plotly(telemetry_dict, save_path="output/plot_winner_throttle_plotly.html"):
    import plotly.graph_objects as go
    from pathlib import Path

    fig = go.Figure()

    for year, data in telemetry_dict.items():
        driver_name = data['name']
        car_data = data['car_data']

        fig.add_trace(go.Scatter(
            x=car_data['Distance'],
            y=car_data['Throttle'],
            name=f"{driver_name} Throttle",
            line=dict(color=get_winner_color(driver_name), dash='dash', width=3),  #  Fixed
            hovertemplate='<b>%{fullData.name}</b><br>' +
                          'Throttle: %{y:.1f}%<br>' +
                          'Distance: %{x:.0f}m<extra></extra>'
        ))

    fig.update_layout(
        title="⚡ Miami GP Winners - Throttle Pedal (%) vs Distance",
        xaxis_title="Distance (m)",
        yaxis_title="Throttle Position (%)",
        height=320,
        hovermode="x unified",
        template="plotly_white"
    )

    Path("output").mkdir(exist_ok=True)
    fig.write_html(save_path)
    print(f" Saved: {save_path}")

    return fig
def plot_winner_brake_plotly(telemetry_dict,save_path="output/plot_winner_brake_plotly.html"):
    import plotly.graph_objects as go
    from pathlib import Path

    fig=go.Figure()

    for year,data in telemetry_dict.items():
        driver_name=data['name']
        car_data=data['car_data']

        fig.add_trace(go.Scatter(
            x=car_data['Distance'],
            y=car_data['Brake'].astype(int),
            name=f"{driver_name} Brake",
            line=dict(color=get_winner_color(driver_name),width=4),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Brake: %{y} (1=Active)<br>' +
                         'Distance: %{x:.0f}m<extra></extra>'
        ))

    fig.update_layout(
        title="Miami GP Winners-Brake Pedal vs Distance",
        xaxis_title="Distance (m)",
        yaxis_title='Brake States',
        height=320,
        hovermode="x unified",
        template='plotly_white'
    )
    Path("output").mkdir(exist_ok=True)
    fig.write_html(save_path)
    print(f'Saved:{save_path}')

    return fig


def plot_winner_rpm_plotly(telemetry_dict, save_path="output/plot_winner_rpm_plotly.html"):
    """
    Plot RPM comparison using Plotly (interactive)
    """
    import plotly.graph_objects as go
    from pathlib import Path

    fig = go.Figure()

    for year, data in telemetry_dict.items():
        driver_name = data['name']
        car_data = data['car_data']

        fig.add_trace(go.Scatter(
            x=car_data['Distance'],
            y=car_data['RPM'],
            name=f"{driver_name} RPM",
            line=dict(color=get_winner_color(driver_name), width=2),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                          'RPM: %{y:.0f}<br>' +
                          'Distance: %{x:.0f}m<extra></extra>'
        ))

    fig.update_layout(
        title=" Miami GP Winners - Engine RPM Comparison (2023-2025)",
        xaxis_title="Distance (m)",
        yaxis_title="RPM",
        height=350,
        hovermode="x unified",
        template="plotly_white"
    )

    Path("output").mkdir(exist_ok=True)
    fig.write_html(save_path)
    print(f" Saved: {save_path}")

    return fig


def plot_winner_gear_plotly(telemetry_dict, save_path="output/plot_winner_gear_plotly.html"):
    """
    Plot gear changes using Plotly (interactive)
    """
    import plotly.graph_objects as go
    from pathlib import Path

    fig = go.Figure()

    for year, data in telemetry_dict.items():
        driver_name = data['name']
        car_data = data['car_data']

        fig.add_trace(go.Scatter(
            x=car_data['Distance'],
            y=car_data['nGear'],
            name=f"{driver_name} Gear",
            line=dict(color=get_winner_color(driver_name), width=2, dash='dot'),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                          'Gear: %{y}<br>' +
                          'Distance: %{x:.0f}m<extra></extra>'
        ))

    fig.update_layout(
        title="Miami GP Winners - Gear Changes vs Distance",
        xaxis_title="Distance (m)",
        yaxis_title="Gear",
        yaxis=dict(tickmode='linear', dtick=1),
        height=320,
        hovermode="x unified",
        template="plotly_white"
    )

    Path("output").mkdir(exist_ok=True)
    fig.write_html(save_path)
    print(f" Saved: {save_path}")

    return fig


def create_track_heatmap_plotly(gps_data, driver_name, year, save_path="output/track_heatmap_plotly.html"):
    """
    Create track heat map using Plotly - requires gps_data (not car_data)
    """
    import plotly.express as px
    from pathlib import Path

    fig = px.scatter(
        gps_data,
        x='X',
        y='Y',
        color='Speed',
        color_continuous_scale='Hot',
        title=f' {driver_name} - {year} Miami GP Track Heat Map',
        labels={'Speed': 'Speed (km/h)'},
        hover_data={'Speed': '.1f', 'X': '.1f', 'Y': '.1f'}
    )

    fig.update_layout(
        height=500,
        xaxis_title="X Position (m)",
        yaxis_title="Y Position (m)",
        template='plotly_dark'
    )

    Path("output").mkdir(exist_ok=True)
    fig.write_html(save_path)
    print(f"✅ Saved: {save_path}")

    return fig


def create_all_plotly_plots(telemetry_dict):
    """
    Create ALL Plotly plots for winners - convenient wrapper
    """
    print("\n" + "=" * 60)
    print(" Creating All Plotly Winner Plots")
    print("=" * 60 + "\n")


    plot_winner_throttle_plotly(telemetry_dict)
    plot_winner_brake_plotly(telemetry_dict)
    plot_winner_rpm_plotly(telemetry_dict)
    plot_winner_gear_plotly(telemetry_dict)

    print("\n All Plotly plots created!")
    print(" Check 'output/' folder for interactive HTML files")