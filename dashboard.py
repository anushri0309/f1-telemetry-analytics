"""
F1 Miami GP Analytics Dashboard (matches your existing plots + winner telemetry)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import fastf1

st.set_page_config(
    page_title="F1 Miami GP Analytics",
    page_icon="🏎️",
    layout="centered"
)
st.title("F1 Miami GP Analytics Dashboard")
st.markdown("Tire strategy, race analysis & Miami GP winners telemetry (2023–2025)")
st.markdown("---")

# ===========================================================================
# SECTION 0: LOAD DATA (your tire data + winner telemetry)
# ===========================================================================
@st.cache_data
def load_tire_stint_data():
    path = Path("data/processed/tire_stints_analysis.csv")
    if path.exists():
        return pd.read_csv(path)
    st.error("Run your main.py script first to generate tire_stints_analysis.csv")
    st.stop()

df_tires = load_tire_stint_data()
if len(df_tires) == 0:
    st.stop()

# Make year numeric (as in your code)
df_tires["year"] = df_tires["year"].str.replace("Miami", "").astype(int)

# Load winner telemetry (as in your code)
@st.cache_data
def get_winner_telemetry_all_years():
    winners = {
        2023: {"driver": "VER", "number": "1", "name": "Max Verstappen"},
        2024: {"driver": "NOR", "number": "4", "name": "Lando Norris"},
        2025: {"driver": "PIA", "number": "81", "name": "Oscar Piastri"},
    }

    telemetry_dict = {}
    for year, winner in winners.items():
        try:
            session = fastf1.get_session(year, "Miami", "R")
            session.load(telemetry=True, laps=True)

            fastest_lap = (
                session.laps
                .pick_drivers(winner["number"])
                .pick_fastest()
            )

            car_data = fastest_lap.get_car_data().add_distance()
            gps_data = fastest_lap.get_telemetry().add_distance()

            telemetry_dict[year] = {
                "name": winner["name"],
                "number": winner["number"],
                "car_data": car_data,
                "gps_data": gps_data,
                "fastest_lap": fastest_lap
            }
        except Exception as e:
            st.warning(f"Could not load {year} data: {e}")
            continue

    return telemetry_dict

telemetry_dict = get_winner_telemetry_all_years()

def get_winner_color(driver_name):
    colors = {
        "Max Verstappen": "#062C4D",
        "Lando Norris": "#FF8700",
        "Oscar Piastri": "#3D8B3D",
    }
    return colors.get(driver_name, "#333333")

# ===========================================================================
# SECTION 1: Tire lifespan boxplot (same as your plot_tire_lifespan)
# ===========================================================================
st.header("1. Tire Life at Miami GP (2023–2025)")

st.markdown("""
This boxplot shows how many laps each tire compound typically lasts before a pit stop.  
The box covers the middle 50% of stint lengths, the solid line inside is the median,  
and the whiskers span most of the remaining data. Points outside the whiskers are unusually short or long stints.
""")

fig = px.box(
    df_tires,
    x="Compound",
    y="stint_length",
    title="Tire Life at Miami GP (2023–2025)",
    labels={"stint_length": "Stint Length (laps)", "Compound": "Tire Compound"},
    color="Compound",
    template="plotly_white",
)
fig.update_layout(height=400, showlegend=True)
st.plotly_chart(fig, use_container_width=True)

# ===========================================================================
# SECTION 2: Pit window barplot (like your plot_pit_window)
# ===========================================================================
st.header("2. Median Pit Stop Lap by Year")

temp = df_tires.sort_values(["Driver", "year", "stint_start"])
temp["pit_stop"] = temp["Compound"] != temp.groupby(["Driver", "year"])["Compound"].shift(1)
pit_laps = temp[temp["pit_stop"] & (temp["stint_start"] > 3)].groupby("year")["stint_start"].median()

st.markdown("""
This bar chart shows the typical lap on which drivers made their pit stops each year (after lap 3, excluding the start).  
A median around lap 20 matches the classic two‑stop Miami strategy, where the long middle stint on hard tires starts after the first window and ends before the last.
""")

fig = px.bar(
    pit_laps.reset_index(),
    x="year",
    y="stint_start",
    title="Median Pit Stop Lap by Year – Miami GP",
    labels={"stint_start": "Median Pit Lap", "year": "Year"},
    template="plotly_white",
)
fig.add_shape(
    type="line",
    xref="paper",
    x0=0,
    x1=1,
    yref="y",
    y0=20,
    y1=20,
    line=dict(color="red", dash="dash"),
)
fig.update_layout(
    height=350,
    showlegend=True,
    legend=dict(itemsizing="constant"),
)
st.plotly_chart(fig, use_container_width=True)

# ===========================================================================
# SECTION 3: Tire‑use pie chart (your own distributions)
# ===========================================================================
st.header("3. Tire‑Compound Usage Distribution")

compound_counts = df_tires["Compound"].value_counts()
fig = px.pie(
    values=compound_counts.values,
    names=compound_counts.index,
    title="Tire‑Compound Usage (Total Laps)",
    color_discrete_sequence=["#45B7D1", "#FF6B6B", "#4ECDC4"],
    template="plotly_white",
)
fig.update_layout(height=350, showlegend=True)
st.plotly_chart(fig, use_container_width=True)

# ===========================================================================
# SECTION 4: Stint‑length vs average lap time (your own scatter logic)
# ===========================================================================
st.header("4. Stint Length vs Average Lap Time")

df_plot = df_tires.copy()
df_plot["lap_time_diff"] = df_plot["worst_laptime"] - df_plot["best_laptime"]

fig = px.scatter(
    df_plot,
    x="stint_length",
    y="avg_laptime",
    color="Compound",
    size="best_laptime",
    title="Stint Length vs. Average Lap Time (2023–2025)",
    labels={
        "stint_length": "Stint Length (laps)",
        "avg_laptime": "Average Lap Time (s)",
    },
    hover_data=["Driver", "year", "stint_start", "stint_end"],
    template="plotly_white",
)
fig.update_layout(height=400, showlegend=True)
st.plotly_chart(fig, use_container_width=True)

# ===========================================================================
# SECTION 5: Driver‑by‑stint bar chart (like your driver‑wise stint views)
# ===========================================================================
st.header("5. Stint Length by Driver and Year")

agg = (
    df_tires.groupby(["Driver", "year", "Compound"])["stint_length"]
    .mean()
    .reset_index()
)

fig = px.bar(
    agg,
    x="Driver",
    y="stint_length",
    color="Compound",
    facet_col="year",
    facet_col_wrap=3,
    title="Stint Length by Driver and Year",
    labels={
        "stint_length": "Average Stint Length (laps)",
        "Driver": "Driver",
        "year": "Year",
    },
    template="plotly_white",
)
fig.update_layout(height=400, showlegend=True)
st.plotly_chart(fig, use_container_width=True)

# ===========================================================================
# SECTION 6: WINNER TELEMETRY – THROTTLE
# ===========================================================================
if telemetry_dict:
    st.header("6. Miami Winners - Throttle Pedal (%) vs Distance")

    st.markdown("""
    **What this graph shows:** Throttle position over lap distance for the three Miami GP winners.  
    Each line represents one driver's fastest lap (2023-2025).
    """)
    fig = go.Figure()
    for year, data in telemetry_dict.items():
        driver_name = data["name"]
        car_data = data["car_data"]
        fig.add_trace(go.Scatter(
            x=car_data["Distance"],
            y=car_data["Throttle"],
            name=f"{driver_name} ({year})",
            line=dict(color=get_winner_color(driver_name), width=3),
            hovertemplate="<b>%{fullData.name}</b><br>Throttle: %{y:.1f}%<br>Distance: %{x:.0f}m<extra></extra>"
        ))
    fig.update_layout(
        title="Miami GP Winners - Throttle Pedal (%) vs Distance",
        xaxis_title="Distance (m)",
        yaxis_title="Throttle Position (%)",
        height=400,
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

# ===========================================================================
# SECTION 7: WINNER TELEMETRY – BRAKE
# ===========================================================================
if telemetry_dict:
    st.header("7. Miami Winners - Brake Pedal vs Distance")

    st.markdown("""
    **What this graph shows:** Brake state (0=off, 1=on) over distance for each winner. Shows braking points in corners.
    """)
    fig = go.Figure()
    for year, data in telemetry_dict.items():
        driver_name = data["name"]
        car_data = data["car_data"]
        fig.add_trace(go.Scatter(
            x=car_data["Distance"],
            y=car_data["Brake"].astype(int),
            name=f"{driver_name} ({year})",
            line=dict(color=get_winner_color(driver_name), width=4),
            hovertemplate="<b>%{fullData.name}</b><br>Brake: %{y} (1=Active)<br>Distance: %{x:.0f}m<extra></extra>"
        ))
    fig.update_layout(
        title="Miami GP Winners - Brake Pedal vs Distance",
        xaxis_title="Distance (m)",
        yaxis_title="Brake States",
        height=400,
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

# ===========================================================================
# SECTION 8: WINNER TELEMETRY – RPM
# ===========================================================================
if telemetry_dict:
    st.header("8. Miami Winners - Engine RPM Comparison")

    st.markdown("""
    **What this graph shows:** Engine RPM over distance for each winner, indicating how hard they are using the engine and gear changes.
    """)
    fig = go.Figure()
    for year, data in telemetry_dict.items():
        driver_name = data["name"]
        car_data = data["car_data"]
        fig.add_trace(go.Scatter(
            x=car_data["Distance"],
            y=car_data["RPM"],
            name=f"{driver_name} ({year})",
            line=dict(color=get_winner_color(driver_name), width=2),
            hovertemplate="<b>%{fullData.name}</b><br>RPM: %{y:.0f}<br>Distance: %{x:.0f}m<extra></extra>"
        ))
    fig.update_layout(
        title="Miami GP Winners - Engine RPM Comparison (2023-2025)",
        xaxis_title="Distance (m)",
        yaxis_title="RPM",
        height=450,
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

# ===========================================================================
# SECTION 9: WINNER TELEMETRY – GEAR CHANGES
# ===========================================================================
if telemetry_dict:
    st.header("9. Miami Winners - Gear Changes vs Distance")

    st.markdown("""
    **What this graph shows:** Gear used over distance for each winner. Shows gear changes through corners and straights.
    """)
    fig = go.Figure()
    for year, data in telemetry_dict.items():
        driver_name = data["name"]
        car_data = data["car_data"]
        fig.add_trace(go.Scatter(
            x=car_data["Distance"],
            y=car_data["nGear"],
            name=f"{driver_name} ({year})",
            line=dict(color=get_winner_color(driver_name), width=2, dash="dot"),
            hovertemplate="<b>%{fullData.name}</b><br>Gear: %{y}<br>Distance: %{x:.0f}m<extra></extra>"
        ))
    fig.update_layout(
        title="Miami GP Winners - Gear Changes vs Distance",
        xaxis_title="Distance (m)",
        yaxis_title="Gear",
        yaxis=dict(tickmode="linear", dtick=1),
        height=400,
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

# ===========================================================================
# SECTION 10: SPEED COMPARISON
# ===========================================================================
if telemetry_dict:
    st.header("10. Miami GP Winners - Fastest Lap Speed Comparison")

    st.markdown("""
    **What this graph shows:** Speed over distance for each winner's fastest lap. Shows where they are fastest.
    """)
    fig = go.Figure()
    for year, data in telemetry_dict.items():
        driver_name = data["name"]
        car_data = data["car_data"]
        fig.add_trace(go.Scatter(
            x=car_data["Distance"],
            y=car_data["Speed"],
            name=f"{driver_name} ({year})",
            line=dict(color=get_winner_color(driver_name), width=2.5),
            hovertemplate="<b>%{fullData.name}</b><br>Speed: %{y:.1f} km/h<br>Distance: %{x:.0f}m<extra></extra>"
        ))
    fig.update_layout(
        title="Miami GP Winners - Fastest Lap Speed Comparison (2023-2025)",
        xaxis_title="Distance (m)",
        yaxis_title="Speed (km/h)",
        height=450,
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

# ===========================================================================
# SECTION 11: MIAMI TRACK SUMMARY
# ===========================================================================
st.header("11. Miami GP Track Summary")

st.markdown("""
Miami International Autodrome is a 5.412‑km temporary circuit around Hard Rock Stadium with 19 turns.  
High‑speed corners and hot weather put big stress on tires, which is why your analysis shows long hard‑tire stints and carefully timed pit windows.
""")