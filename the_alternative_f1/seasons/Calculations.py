"""Season-agnostic calculations engine for The Alternative F1.

Accepts a season_data dict (from season_N.py) and returns a computed data
dictionary that all tab views consume. No Streamlit or Plotly dependencies.
"""

import math
from pathlib import Path

import numpy as np
import pandas as pd

# Resolve the Excel file path relative to this module
_EXCEL_PATH = str((Path(__file__).parent.parent / "The_Alternative_F1.xlsx").resolve())

_calculations_cache = {}
_calculations_mtime = {}


def Calculations(season_data: dict, sprint_only: bool = False) -> dict:
    # Use sheet_name and sprint_only as the cache key
    cache_key = (season_data["sheet_name"], sprint_only)
    
    excel_path = Path(_EXCEL_PATH)
    current_mtime = excel_path.stat().st_mtime if excel_path.exists() else 0
    
    if cache_key in _calculations_cache and _calculations_mtime.get(cache_key) == current_mtime:
        return _calculations_cache[cache_key]

    """Run all calculations for the given season and return a results dict.

    Parameters
    ----------
    season_data : dict
        A season dict from season_N.py containing sheet_name, schedule_sheet,
        rookies, team_colors, driver_colors, etc.

    Returns
    -------
    dict with keys consumed by Tab views:
        team_race_totals, driver_race_totals, df, races,
        team_colors, driver_colors, rookies,
        race_place, race_points, index_x,
        new_df, new_df_FL, new_df_DOTD, new_df_MOT, new_df_Q,
        new_df_Place, new_df_CD,
        races_points_only, drivers_total_points,
        constructor_totals, driver_totals,
        team_df, team_races_points_only,
        drivers_points_df, colors_driver_team, colors_driver_df,
        has_dotd_mot_cd,
        # Line chart data (pre-computed for recharts)
        team_line_data, driver_line_data, rookie_line_data,
        # Schedule
        schedule_df,
    """
    sheet_name = season_data["sheet_name"]
    schedule_sheet = season_data["schedule_sheet"]
    team_colors = season_data["team_colors"]
    driver_colors = season_data["driver_colors"]
    rookies = season_data["rookies"]

    # ── Read Excel data ──────────────────────────────────────────────────
    df = pd.read_excel(_EXCEL_PATH, sheet_name=sheet_name)
    df = df.dropna(subset=["Driver"])
    df["Driver"] = df["Driver"].astype(str).str.strip()
    df["Team"] = df["Team"].astype(str).str.strip()

    # ── Read schedule ────────────────────────────────────────────────────
    schedule_df = pd.read_excel(_EXCEL_PATH, sheet_name=schedule_sheet)

    # ── Identify column groups ───────────────────────────────────────────
    race_points = [col for col in df.columns if col.endswith("Points")]
    race_place = [col for col in df.columns if col.endswith("Place")]

    # Detect if any completed Sprint columns exist
    sprint_points_cols = [col for col in df.columns if col.endswith("Points") and "Sprint" in col]
    sprint_points_completed = [col for col in sprint_points_cols if df[col].fillna(0).sum() > 0]
    has_sprint = len(sprint_points_completed) > 0

    if sprint_only and has_sprint:
        race_points = [col for col in race_points if "Sprint" in col]
        race_place = [col for col in race_place if "Sprint" in col]

    races = []
    for col in race_points:
        name = col[:-6]  # strip "Points"
        if "Sprint" in name and not name.endswith(" Sprint"):
            name = name.replace("Sprint", " Sprint")
        races.append(name)

    # Detect optional column groups
    fastest_lap_columns = [col for col in df.columns if col.endswith("FastestLap")]
    DOTD_columns = [col for col in df.columns if col.endswith("DOTD")]
    MOT_columns = [col for col in df.columns if col.endswith("MOT")]
    CD_columns = [col for col in df.columns if col.endswith("CD")]
    qualifying_columns = [col for col in df.columns if col.endswith("Qualifying")]
    place_columns = [col for col in df.columns if col.endswith("Place")]

    if sprint_only and has_sprint:
        fastest_lap_columns = [col for col in fastest_lap_columns if "Sprint" in col]
        DOTD_columns = [col for col in DOTD_columns if "Sprint" in col]
        MOT_columns = [col for col in MOT_columns if "Sprint" in col]
        CD_columns = [col for col in CD_columns if "Sprint" in col]
        qualifying_columns = [col for col in qualifying_columns if "Sprint" in col]
        place_columns = [col for col in place_columns if "Sprint" in col]

    has_dotd_mot_cd = len(DOTD_columns) > 0

    # ── Total points column ──────────────────────────────────────────────
    df["Total"] = 0
    for col in race_points:
        df["Total"] = df["Total"] + df[col].fillna(0)

    # ── Cumulative team totals ───────────────────────────────────────────
    team_race_totals = pd.DataFrame()
    for i, col in enumerate(race_points):
        pts = df.groupby("Team")[col].sum().fillna(0)
        if i == 0:
            team_race_totals[col] = pts
        else:
            team_race_totals[col] = pts + team_race_totals[race_points[i - 1]]

    # ── Cumulative driver totals ─────────────────────────────────────────
    driver_race_totals = pd.DataFrame()
    for i, col in enumerate(race_points):
        pts = df.groupby("Driver")[col].sum().fillna(0)
        if i == 0:
            driver_race_totals[col] = pts
        else:
            driver_race_totals[col] = pts + driver_race_totals[race_points[i - 1]]

    # ── Determine how many races have been completed ─────────────────────
    index_x = len(race_place) - 0.5  # default: all races completed
    for i, col in enumerate(race_place):
        if df[race_points[i]].fillna(0).sum() == 0:
            index_x = i - 0.5
            break
        if col == race_place[-1]:
            index_x = i + 1

    # ── Constructor standings (sorted) ───────────────────────────────────
    # team_race_totals has Team as index; get the last (most recent) column
    last_team_col = race_points[-1]
    constructor_sorted = team_race_totals[[last_team_col]].sort_values(
        last_team_col, ascending=False
    ).reset_index()
    constructor_totals = pd.DataFrame({
        "Team": constructor_sorted["Team"],
        "Points": [f"{p:.1f}" for p in constructor_sorted[last_team_col]],
    })

    # ── Driver standings (sorted) ────────────────────────────────────────
    last_driver_col = race_points[-1]
    driver_sorted = driver_race_totals[[last_driver_col]].sort_values(
        last_driver_col, ascending=False
    ).reset_index()
    driver_totals = pd.DataFrame({
        "Driver": driver_sorted["Driver"],
        "Points": [f"{p:.1f}" for p in driver_sorted[last_driver_col]],
    })

    # ── Line chart data (for recharts) ───────────────────────────────────
    # Insert "Start" point with 0 for all teams/drivers
    team_race_totals_t = team_race_totals.copy()
    team_race_totals_t.insert(0, "Start", 0)
    team_race_totals_t = team_race_totals_t.T

    races_with_start = ["Start"] + races

    # Only include completed races in line charts
    num_completed = int(index_x + 0.5)
    races_with_start_completed = races_with_start[:1 + num_completed]

    # Build list-of-dicts for recharts team line chart
    team_line_data = []
    for i, race_label in enumerate(races_with_start_completed):
        point = {"race": race_label}
        for team in team_race_totals_t.columns:
            point[team] = float(team_race_totals_t.iloc[i][team])
        team_line_data.append(point)

    driver_race_totals_t = driver_race_totals.copy()
    driver_race_totals_t.insert(0, "Start", 0)
    driver_race_totals_t = driver_race_totals_t.T

    driver_line_data = []
    for i, race_label in enumerate(races_with_start_completed):
        point = {"race": race_label}
        for driver in driver_race_totals_t.columns:
            point[driver] = float(driver_race_totals_t.iloc[i][driver])
        driver_line_data.append(point)

    # Rookie line chart data
    rookie_line_data = []
    if rookies:
        rookie_cols = [d for d in driver_race_totals_t.columns if d in rookies]
        for i, race_label in enumerate(races_with_start_completed):
            point = {"race": race_label}
            for rookie in rookie_cols:
                point[rookie] = float(driver_race_totals_t.iloc[i][rookie])
            rookie_line_data.append(point)

    # ── Points-only race list (no "Start") ───────────────────────────────
    races_points_only = races.copy()

    # ── Filtered DataFrames for driver stats ─────────────────────────────
    points_columns = [col for col in df.columns if col.endswith(("Points", "SprintPoints"))]
    if sprint_only and has_sprint:
        points_columns = [col for col in points_columns if "Sprint" in col]

    new_df = df.set_index("Driver")[points_columns].reset_index()
    new_df_FL = df.set_index("Driver")[fastest_lap_columns].reset_index() if fastest_lap_columns else pd.DataFrame({"Driver": df["Driver"]})
    new_df_DOTD = df.set_index("Driver")[DOTD_columns].reset_index() if DOTD_columns else pd.DataFrame({"Driver": df["Driver"]})
    new_df_MOT = df.set_index("Driver")[MOT_columns].reset_index() if MOT_columns else pd.DataFrame({"Driver": df["Driver"]})
    new_df_Q = df.set_index("Driver")[qualifying_columns].reset_index() if qualifying_columns else pd.DataFrame({"Driver": df["Driver"]})
    new_df_Place = df.set_index("Driver")[place_columns].reset_index() if place_columns else pd.DataFrame({"Driver": df["Driver"]})
    new_df_CD = df.set_index("Driver")[CD_columns].reset_index() if CD_columns else pd.DataFrame({"Driver": df["Driver"]})

    # ── Driver total points list ─────────────────────────────────────────
    drivers_total_points = []
    for i in range(len(new_df)):
        driver_pts = new_df.iloc[i, 1:].tolist()
        drivers_total_points.append(sum(driver_pts))

    # ── Team-level aggregations for Tab1/Tab3 ────────────────────────────
    team_points_columns = [col for col in df.columns if col.endswith(("Points", "SprintPoints"))]
    if sprint_only and has_sprint:
        team_points_columns = [col for col in team_points_columns if "Sprint" in col]
    team_races_points_only = races.copy()

    team_df = df.groupby("Team")[team_points_columns].sum().reset_index()

    # Driver points df for stacked chart
    drivers_points_df = pd.DataFrame({
        "Driver": new_df["Driver"].copy(),
        "Team": df["Team"].copy(),
        "Points": drivers_total_points,
    })

    # Build driver color mapping for charts
    drivers_points_2df = drivers_points_df.groupby("Driver")["Points"].sum().reset_index()
    drivers_points_3df = drivers_points_2df.sort_values(by="Points", ascending=False)

    colors_driver_team = []
    colors_driver_list = []
    for driver in drivers_points_3df["Driver"]:
        color = driver_colors.get(driver, "#555555")
        colors_driver_team.append(color)
        colors_driver_list.append(driver)
    colors_driver_df = pd.DataFrame(
        list(zip(colors_driver_list, colors_driver_team)),
        columns=["Driver", "Color"],
    )

    result = {
        "team_race_totals": team_race_totals,
        "driver_race_totals": driver_race_totals,
        "df": df,
        "races": races,
        "races_with_start": races_with_start,
        "team_colors": team_colors,
        "driver_colors": driver_colors,
        "rookies": rookies,
        "race_place": race_place,
        "race_points": race_points,
        "index_x": index_x,
        "new_df": new_df,
        "new_df_FL": new_df_FL,
        "new_df_DOTD": new_df_DOTD,
        "new_df_MOT": new_df_MOT,
        "new_df_Q": new_df_Q,
        "new_df_Place": new_df_Place,
        "new_df_CD": new_df_CD,
        "races_points_only": races_points_only,
        "drivers_total_points": drivers_total_points,
        "constructor_totals": constructor_totals,
        "driver_totals": driver_totals,
        "team_df": team_df,
        "team_races_points_only": team_races_points_only,
        "drivers_points_df": drivers_points_df,
        "colors_driver_team": colors_driver_team,
        "colors_driver_df": colors_driver_df,
        "has_dotd_mot_cd": has_dotd_mot_cd,
        "team_line_data": team_line_data,
        "driver_line_data": driver_line_data,
        "rookie_line_data": rookie_line_data,
        "schedule_df": schedule_df,
        "fastest_lap_columns": fastest_lap_columns,
        "DOTD_columns": DOTD_columns,
        "MOT_columns": MOT_columns,
        "CD_columns": CD_columns,
        "qualifying_columns": qualifying_columns,
        "place_columns": place_columns,
        "has_sprint": has_sprint,
    }
    _calculations_cache[cache_key] = result
    _calculations_mtime[cache_key] = current_mtime
    return result