"""
Prepare Premier League match data for the Tableau dashboard.

Input : data/E0_2122.csv ... data/E0_2526.csv  (from football-data.co.uk)
Output: output/matches_long.csv   one row per team per match
        output/team_season.csv    one row per team per season
Run   : python prep_data.py
"""
from pathlib import Path
import pandas as pd

DATA = Path("data")
OUT = Path("output")
OUT.mkdir(exist_ok=True)

frames = []
for f in sorted(DATA.glob("E0_*.csv")):
    code = f.stem.split("_")[1]                      # e.g. "2425"
    season = f"20{code[:2]}/{code[2:]}"              # -> "2024/25"
    df = pd.read_csv(f, encoding="latin-1")
    df = df.dropna(subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG"])
    df["Season"] = season
    frames.append(df)
    print(f"Loaded {f.name}: {len(df)} matches ({season})")

if not frames:
    raise SystemExit("No files found. Put the E0_*.csv files in the data/ folder.")

raw = pd.concat(frames, ignore_index=True)
raw["Date"] = pd.to_datetime(raw["Date"], dayfirst=True, errors="coerce")

def side(df, venue):
    """Reshape matches so each row is one team's view of one match."""
    h = venue == "Home"
    me, opp = ("H", "A") if h else ("A", "H")
    out = pd.DataFrame({
        "Season": df["Season"],
        "Date": df["Date"],
        "Team": df["HomeTeam"] if h else df["AwayTeam"],
        "Opponent": df["AwayTeam"] if h else df["HomeTeam"],
        "Venue": venue,
        "GoalsFor": df[f"FT{me}G"],
        "GoalsAgainst": df[f"FT{opp}G"],
        "Shots": df.get(f"{me}S"),
        "ShotsOnTarget": df.get(f"{me}ST"),
        "ShotsConceded": df.get(f"{opp}S"),
        "ShotsOnTargetConceded": df.get(f"{opp}ST"),
        "Corners": df.get(f"{me}C"),
        "Yellows": df.get(f"{me}Y"),
        "Reds": df.get(f"{me}R"),
    })
    return out

long = pd.concat([side(raw, "Home"), side(raw, "Away")], ignore_index=True)
long["Result"] = (long["GoalsFor"] > long["GoalsAgainst"]).map({True: "W", False: ""})
long.loc[long["GoalsFor"] == long["GoalsAgainst"], "Result"] = "D"
long.loc[long["GoalsFor"] < long["GoalsAgainst"], "Result"] = "L"
long["Points"] = long["Result"].map({"W": 3, "D": 1, "L": 0})
long = long.sort_values(["Season", "Team", "Date"])
long["Matchweek"] = long.groupby(["Season", "Team"]).cumcount() + 1
long["CumulativePoints"] = long.groupby(["Season", "Team"])["Points"].cumsum()
long["Form5"] = (long.groupby(["Season", "Team"])["Points"]
                 .transform(lambda s: s.rolling(5, min_periods=1).sum()))
long.to_csv(OUT / "matches_long.csv", index=False)

g = long.groupby(["Season", "Team"])
team = g.agg(Played=("Points", "size"), Points=("Points", "sum"),
             Wins=("Result", lambda r: (r == "W").sum()),
             Draws=("Result", lambda r: (r == "D").sum()),
             Losses=("Result", lambda r: (r == "L").sum()),
             GoalsFor=("GoalsFor", "sum"), GoalsAgainst=("GoalsAgainst", "sum"),
             Shots=("Shots", "sum"), ShotsOnTarget=("ShotsOnTarget", "sum"),
             ShotsConceded=("ShotsConceded", "sum")).reset_index()
home = long[long.Venue == "Home"].groupby(["Season", "Team"])["Points"].sum().rename("HomePoints")
away = long[long.Venue == "Away"].groupby(["Season", "Team"])["Points"].sum().rename("AwayPoints")
team = (team.merge(home, on=["Season", "Team"], how="left")
            .merge(away, on=["Season", "Team"], how="left")
            .fillna({"HomePoints": 0, "AwayPoints": 0}))
team["GoalDifference"] = team.GoalsFor - team.GoalsAgainst
team["PointsPerGame"] = (team.Points / team.Played).round(2)
team["ShotConversion"] = (team.GoalsFor / team.Shots).round(3)          # goals per shot
team["ShotAccuracy"] = (team.ShotsOnTarget / team.Shots).round(3)       # share on target
team["Position"] = (team.sort_values(["Points", "GoalDifference", "GoalsFor"], ascending=False)
                    .groupby("Season").cumcount() + 1)
team = team.sort_values(["Season", "Position"])
team.to_csv(OUT / "team_season.csv", index=False)

print(f"\nWrote {len(long)} team-match rows and {len(team)} team-season rows to {OUT}/")
print("Champions by season:")
print(team[team.Position == 1][["Season", "Team", "Points"]].to_string(index=False))
