import pandas as pd
from pathlib import Path

def clean_laps(filepath,year):

    laps=pd.read_csv(filepath)
    laps=laps[laps["LapTime"].notna()]
    laps=laps[laps["LapTime"]!=""]
    print(f"Kept {len(laps)} rows(original:{len(pd.read_csv(filepath))}")
    Path(f"data/processed/{year}").mkdir(parents=True, exist_ok=True)
    laps.to_csv(f"data/processed/{year}/laps_cleaned.csv", index=False)
    team_mapping = {
        'red bull racing': 'red bull',
        'mclaren': 'mclaren',
        'mercedes': 'mercedes',
        'ferrari': 'ferrari',
        'aston martin': 'aston martin',
        'alpine': 'alpine',
        'williams': 'williams',
        'alphatauri': 'alphatauri',
        'alfa romeo': 'sauber',
        'haas': 'haas'
    }

    # Create constructorid from Team
    laps['constructorid'] = laps['Team'].str.lower().map(team_mapping)

    # If unmapped, keep original team name
    unmapped = laps['constructorid'].isna()
    laps.loc[unmapped, 'constructorid'] = laps.loc[unmapped, 'Team'].str.lower()

    print(f"✅ Created constructorid from Team column")
    print(f"Teams found: {laps['constructorid'].value_counts().to_dict()}")
    print(laps.columns)
    return laps

