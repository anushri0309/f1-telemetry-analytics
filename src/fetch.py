import fastf1 as ff1
import pandas as pd
from pathlib import Path

def load_session(year,gp_name,session_type,driver_str):
    print(f":Loading{year}{gp_name} {session_type}...")
    session=ff1.get_session(year,gp_name,session_type)
    session.load(telemetry=True,
                 laps=True,
                 weather=True,
                 messages=True
                 )
    for driver_num in session.results['DriverNumber']:
        if driver_num in session.car_data:
            pass
    telemetry=session.car_data[driver_str]
    print("Columns in car data")
    print(telemetry.columns.tolist())
    print(f'\n First three rows:')
    print(telemetry.head(3))

    return session
PROJECT_ROOT = Path(__file__).parent.parent
def sav_raw_data(session,gp_name,year,base_dir=None):
    if base_dir is None:
        base_dir = PROJECT_ROOT / "data" / "raw" / f"{gp_name}{year}"  # ← Use absolute path

    Path(base_dir).mkdir(parents=True, exist_ok=True)
    laps=session.laps
    session.results.to_csv(f"{base_dir}/session_result.csv",index=False)
    laps.to_csv(f"{base_dir}/laps.csv",index=False)
    session.weather_data.to_csv(f'{base_dir}/weather_data.csv',index=False)

    winner_driver=session.results.iloc[0]["DriverNumber"]
    winner_laps=laps[laps['DriverNumber']==winner_driver]
    fastest_laps=winner_laps.pick_fastest()
    telemetry=fastest_laps.get_car_data().add_distance()
    telemetry.to_csv(f"{base_dir}/telemetry_winner_fastest_lap.csv",index=False)

    drivers=session.results[['DriverNumber']].drop_duplicates()
    drivers.to_csv(f"{base_dir}/drivers.csv")

    print(f'Raw data saved to {base_dir}/')
    return base_dir
print("\n=== LOADING 2024 MIAMI ===")
session_2024 = load_session(year=2024, gp_name='Miami', session_type='R', driver_str='4')
sav_raw_data(session_2024, year=2024, gp_name='Miami')

print("\n=== LOADING 2025 MIAMI ===")
session_2025 = load_session(year=2025, gp_name='Miami', session_type='R', driver_str='81')
sav_raw_data(session_2025, year=2025, gp_name='Miami')

print("\n=== LOADING 2023 MIAMI ===")
session_2025 = load_session(year=2023, gp_name='Miami', session_type='R', driver_str='1')
sav_raw_data(session_2025, year=2023, gp_name='Miami')
