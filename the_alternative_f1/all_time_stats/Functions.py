# Universal functions for All Time Stats in Reflex webapp
# Adapted from Functions copy.py to be dependency-free (no streamlit/plotting)

import os
import json
from pathlib import Path
import pandas as pd
import numpy as np

# Global variables for all of the functions
place_suffix = "Place"
qualifying_suffix = "Qualifying"
fastestlap_suffix = "FastestLap" 
points_suffix = "Points"

# Resolve file path dynamically to locate the Excel sheet in the parent folder
current_dir = Path(__file__).parent
file = str((current_dir.parent / "The_Alternative_F1.xlsx").resolve())

_excel_sheets_cache = {}
_excel_mtime = 0
_func_cache = {}

def get_excel_sheet(sheet_name: str) -> pd.DataFrame:
    global _excel_sheets_cache, _excel_mtime, _func_cache
    excel_path = Path(file)
    current_mtime = excel_path.stat().st_mtime if excel_path.exists() else 0
    if _excel_mtime != current_mtime:
        _excel_sheets_cache.clear()
        _func_cache.clear()
        _excel_mtime = current_mtime
    if sheet_name not in _excel_sheets_cache:
        try:
            if excel_path.exists():
                # Read all sheets in a single pass (takes ~0.4s total instead of re-reading per sheet)
                all_sheets = pd.read_excel(file, sheet_name=None)
                _excel_sheets_cache.update(all_sheets)
            if sheet_name not in _excel_sheets_cache:
                _excel_sheets_cache[sheet_name] = pd.DataFrame()
        except Exception:
            _excel_sheets_cache[sheet_name] = pd.DataFrame()
    return _excel_sheets_cache[sheet_name].copy()

from the_alternative_f1.constructor_colors import CONSTRUCTOR_COLORS, get_constructor_color, TEAM_COLORS, get_team_color

# Globally unified constructor colors (Alpine is #FD4BC7 pink)
team_colors = CONSTRUCTOR_COLORS

def PointTotals(season):
    cache_key = ("PointTotals", season)
    excel_path = Path(file)
    current_mtime = excel_path.stat().st_mtime if excel_path.exists() else 0
    if _excel_mtime == current_mtime and cache_key in _func_cache:
        return _func_cache[cache_key]

    # Read in the appropriate sheet for the selected season
    df = get_excel_sheet("Season" + str(season))

    # Read in the list of races from the selected season
    schedule = get_excel_sheet("S" + str(season) + "Schedule")

    # Loop through the schedule and create lists for each global suffix
    races = []
    race_points = []
    for i in range(len(schedule)):
        race_name = schedule['Race'].iloc[i]

        if race_name.startswith(('Pre', 'Post')):
            continue

        races.append(race_name)
        race_points.append(race_name + points_suffix)

    # Strip column values to avoid whitespace issues
    df['Driver'] = df['Driver'].astype(str).str.strip()
    df['Team'] = df['Team'].astype(str).str.strip()

    # Calculate points totals for Constructors/Teams (summing all race points columns)
    team_race_totals = pd.DataFrame([]) 
    for i in range(len(race_points)):
        col = race_points[i]
        # In some seasons, points columns might be missing or have different names, check if exists
        if col in df.columns:
            # fillna with 0 for points calculation
            points_sum = df.groupby('Team')[col].sum().fillna(0)
            if i == 0:
                team_race_totals[col] = points_sum
            else:
                team_race_totals[col] = points_sum + team_race_totals[race_points[i-1]]
        else:
            if i == 0:
                team_race_totals[col] = 0
            else:
                team_race_totals[col] = team_race_totals[race_points[i-1]]

    # Calculate points totals for Drivers
    driver_race_totals = pd.DataFrame([])
    for i in range(len(race_points)):
        col = race_points[i]
        if col in df.columns:
            points_sum = df.groupby('Driver')[col].sum().fillna(0)
            if i == 0:
                driver_race_totals[col] = points_sum
            else:
                driver_race_totals[col] = points_sum + driver_race_totals[race_points[i-1]]
        else:
            if i == 0:
                driver_race_totals[col] = 0
            else:
                driver_race_totals[col] = driver_race_totals[race_points[i-1]]

    # Extract final points from the last race column
    last_col = race_points[-1]
    
    constructor_totals = team_race_totals[[last_col]].rename(columns={last_col: 'Points'}).reset_index()
    constructor_totals = constructor_totals.sort_values(by='Points', ascending=False).reset_index(drop=True)

    driver_totals = driver_race_totals[[last_col]].rename(columns={last_col: 'Points'}).reset_index()
    driver_totals = driver_totals.sort_values(by='Points', ascending=False).reset_index(drop=True)

    res = (None, None, None, constructor_totals, None, driver_totals)
    _func_cache[cache_key] = res
    return res

def is_season_completed(season):
    cache_key = ("is_season_completed", season)
    excel_path = Path(file)
    current_mtime = excel_path.stat().st_mtime if excel_path.exists() else 0
    if _excel_mtime == current_mtime and cache_key in _func_cache:
        return _func_cache[cache_key]

    try:
        df = get_excel_sheet("Season" + str(season))
        schedule = get_excel_sheet("S" + str(season) + "Schedule")
        if df.empty or schedule.empty:
            _func_cache[cache_key] = False
            return False
    except Exception:
        _func_cache[cache_key] = False
        return False

    races = []
    race_points = []
    for i in range(len(schedule)):
        race_name = schedule['Race'].iloc[i]
        if race_name.startswith(('Pre', 'Post')):
            continue
        races.append(race_name)
        race_points.append(race_name + points_suffix)

    if not race_points:
        _func_cache[cache_key] = False
        return False

    last_col = race_points[-1]
    if last_col not in df.columns:
        _func_cache[cache_key] = False
        return False

    col_values = df[last_col].dropna()
    if col_values.empty:
        _func_cache[cache_key] = False
        return False

    try:
        numeric_values = pd.to_numeric(col_values, errors='coerce').dropna()
        if numeric_values.empty or (numeric_values == 0).all():
            _func_cache[cache_key] = False
            return False
    except Exception:
        _func_cache[cache_key] = False
        return False

    _func_cache[cache_key] = True
    return True


_HIGHEST_POSITIONS_CACHE = {}


def get_all_time_highest_positions(num_seasons: int = 5, force_refresh: bool = False) -> dict:
    """Retrieve all-time highest positions for constructors and drivers (TAF1APP-SDDREQ-224, 225, 226).
    Loads from persistent precomputed JSON storage (zero-lag builds).
    If recalculating, entities not active in the current season sheet are preserved without recalculation.
    """
    global _HIGHEST_POSITIONS_CACHE
    if _HIGHEST_POSITIONS_CACHE and not force_refresh:
        return _HIGHEST_POSITIONS_CACHE

    json_file = Path(__file__).parent / "all_time_highest_positions.json"
    if json_file.exists() and not force_refresh:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                _HIGHEST_POSITIONS_CACHE = data
                return data
        except Exception:
            pass

    # Dynamic calculation with optimization: preserve historical records for inactive entities
    from the_alternative_f1.all_time_stats.SummaryAllTime import precompute_summary_data
    ds = precompute_summary_data(num_seasons)
    team_line = ds.get("team_line_data", [])
    driver_line = ds.get("driver_line_data", [])

    def format_pos(rank, race_label):
        if rank == 1:
            return f"🥇 {race_label}"
        elif rank == 2:
            return f"🥈 {race_label}"
        elif rank == 3:
            return f"🥉 {race_label}"
        else:
            suffix = "th" if 11 <= (rank % 100) <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(rank % 10, "th")
            return f"{rank}{suffix} - {race_label}"

    def compute_highest(line_data):
        highest = {}
        for entry in line_data:
            race = entry.get("race", "")
            pts_map = {k: v for k, v in entry.items() if k != "race" and v is not None}
            sorted_entities = sorted(pts_map.items(), key=lambda item: item[1], reverse=True)
            for i, (entity, pts) in enumerate(sorted_entities):
                rank = i + 1
                if entity not in highest or rank < highest[entity]["rank"]:
                    highest[entity] = {
                        "rank": rank,
                        "race": race,
                        "display": format_pos(rank, race)
                    }
        return highest

    # Check active entities in current season
    current_season_df = get_excel_sheet(f"Season{num_seasons}")
    active_drivers = set()
    active_teams = set()
    if not current_season_df.empty:
        if "Driver" in current_season_df.columns:
            active_drivers = set(current_season_df["Driver"].dropna().astype(str).str.strip().unique())
        if "Team" in current_season_df.columns:
            active_teams = set(current_season_df["Team"].dropna().astype(str).str.strip().unique())

    # Load existing stored data if present
    existing_data = {"constructors": {}, "drivers": {}}
    if json_file.exists():
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception:
            pass

    team_h = compute_highest(team_line)
    driver_h = compute_highest(driver_line)

    constructors_dict = existing_data.get("constructors", {})
    for k, v in team_h.items():
        if k in active_teams or k not in constructors_dict:
            constructors_dict[k] = v["display"]

    drivers_dict = existing_data.get("drivers", {})
    for k, v in driver_h.items():
        if k in active_drivers or k not in drivers_dict:
            drivers_dict[k] = v["display"]

    data = {
        "constructors": constructors_dict,
        "drivers": drivers_dict
    }

    try:
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    _HIGHEST_POSITIONS_CACHE = data
    return data


def CalculateAllTime(NumSeason, tORd):
    cache_key = ("CalculateAllTime", NumSeason, tORd)
    excel_path = Path(file)
    current_mtime = excel_path.stat().st_mtime if excel_path.exists() else 0
    if _excel_mtime == current_mtime and cache_key in _func_cache:
        return _func_cache[cache_key].copy()

    # Loop through the points scored for each tORd 
    dfs = []
    champs = []
    for i in range(NumSeason):
        season_num = i + 1
        if tORd == 'Team':
            _, _, _, df_i, _, _ = PointTotals(season_num)
            if is_season_completed(season_num):
                champ = df_i['Team'].iloc[0]
                champs.append(champ)
            dfs.append(df_i)
        elif tORd == 'Driver':
            _, _, _, _, _, df_i = PointTotals(season_num)
            if is_season_completed(season_num):
                champ = df_i['Driver'].iloc[0]
                champs.append(champ)
            dfs.append(df_i)

    # Create the initial combined dataframe with place, tORd, and points
    combined_df = pd.concat(dfs)
    totals = combined_df.groupby(tORd)['Points'].sum().reset_index()
    totals_sorted = totals.sort_values(by='Points', ascending=False).reset_index(drop=True)
    totals_sorted['Place'] = totals_sorted.index + 1
    totals_sorted = totals_sorted[['Place', tORd, 'Points']]

    dfs2 = []
    for i in range(NumSeason):
        df_season = get_excel_sheet("Season" + str(i+1))

        # Strip whitespaces
        df_season['Driver'] = df_season['Driver'].astype(str).str.strip()
        df_season['Team'] = df_season['Team'].astype(str).str.strip()

        x = tORd

        # Keep place columns and remove the rest
        cols_to_keep = [col for col in df_season.columns if col.endswith("Place") or col == x]
        df_season = df_season[cols_to_keep]
        place_cols = [col for col in df_season.columns if col != x]
        melted_df = df_season.melt(id_vars=x, value_vars=place_cols, value_name='Place')

        # Count 1st, 2nd, and 3rd places for each driver/team
        placement_counts = melted_df.groupby(tORd)['Place'].value_counts().unstack(fill_value=0)
        
        # Ensure 1.0, 2.0, 3.0 columns exist in placement_counts
        for p in [1.0, 2.0, 3.0]:
            if p not in placement_counts.columns:
                placement_counts[p] = 0
                
        df2_i = placement_counts.rename(columns={1.0: '1st Place', 2.0: '2nd Place', 3.0: '3rd Place'})
        # Select only these three columns
        df2_i = df2_i[['1st Place', '2nd Place', '3rd Place']]

        dfs2.append(df2_i)

    combined_df2 = pd.concat(dfs2)
    totals2 = combined_df2.groupby(tORd).sum().reset_index()  
    totals_sorted2 = totals2.sort_values(by=['1st Place', '2nd Place', '3rd Place'], ascending=False).reset_index(drop=True)
    totals_sorted2 = totals_sorted2[[tORd, '1st Place', '2nd Place', '3rd Place']]

    # Combine totals_sorted and totals_sorted2 using an outer join
    combined_totals = pd.merge(totals_sorted, totals_sorted2, on=[tORd], how='outer')
    combined_totals = combined_totals.groupby([tORd, 'Points']).sum().reset_index()
    combined_totals = combined_totals.sort_values(by='Points', ascending=False).reset_index(drop=True)
    
    combined_totals['1st Place'] = combined_totals['1st Place'].astype(int)
    combined_totals['2nd Place'] = combined_totals['2nd Place'].astype(int)
    combined_totals['3rd Place'] = combined_totals['3rd Place'].astype(int)
    
    combined_totals['Podiums'] = combined_totals['1st Place'] + combined_totals['2nd Place'] + combined_totals['3rd Place']
    combined_totals = combined_totals[['Place', tORd, 'Points', '1st Place', '2nd Place', '3rd Place', 'Podiums']]
    
    if tORd == 'Team':
        x = "Constructor's Champion"
    elif tORd == 'Driver':
        x = "Driver's Champion"
    combined_totals[x] = 0
    for champ in champs:
        combined_totals.loc[combined_totals[tORd] == champ, x] += 1
    
    combined_totals[x] = combined_totals[x].astype(int)

    all_races_winners = []
    for s in range(NumSeason):
        season_num = s + 1
        try:
            df_season = get_excel_sheet("Season" + str(season_num))
            df_season['Driver'] = df_season['Driver'].astype(str).str.strip()
            df_season['Team'] = df_season['Team'].astype(str).str.strip()
            
            schedule = get_excel_sheet("S" + str(season_num) + "Schedule")
            
            for race in schedule['Race']:
                if str(race).lower().startswith(('pre', 'post')):
                    continue
                col_name = str(race) + "Place"
                if col_name in df_season.columns:
                    winners = df_season[df_season[col_name] == 1]
                    if not winners.empty:
                        driver = winners['Driver'].iloc[0]
                        team = winners['Team'].iloc[0]
                        all_races_winners.append((season_num, race, driver, team))
        except Exception:
            pass

    from collections import defaultdict
    max_streak = defaultdict(int)
    curr_streak = defaultdict(int)
    max_ss_streak = defaultdict(int)
    curr_ss_streak = defaultdict(int)
    
    last_season = None
    for season, race, driver, team in all_races_winners:
        entity = driver if tORd == 'Driver' else team
        
        if last_season is not None and season != last_season:
            curr_ss_streak.clear()
            
        curr_streak[entity] += 1
        for e in list(curr_streak.keys()):
            if e != entity:
                max_streak[e] = max(max_streak[e], curr_streak[e])
                curr_streak[e] = 0
                
        curr_ss_streak[entity] += 1
        for e in list(curr_ss_streak.keys()):
            if e != entity:
                max_ss_streak[e] = max(max_ss_streak[e], curr_ss_streak[e])
                curr_ss_streak[e] = 0
                
        last_season = season
        
    for e in curr_streak:
        max_streak[e] = max(max_streak[e], curr_streak[e])
    for e in curr_ss_streak:
        max_ss_streak[e] = max(max_ss_streak[e], curr_ss_streak[e])
        
    combined_totals['Win Streak'] = combined_totals[tORd].map(max_streak).fillna(0).astype(int)
    combined_totals['Single Season Win Streak'] = combined_totals[tORd].map(max_ss_streak).fillna(0).astype(int)

    highest_positions = get_all_time_highest_positions(NumSeason)

    if tORd == 'Driver':
        combined_totals['Highest Position'] = combined_totals['Driver'].map(highest_positions.get('drivers', {})).fillna("—")
        for i in range(NumSeason):
            season_num = i + 1
            try:
                df_season = get_excel_sheet("Season" + str(season_num))
                df_season['Driver'] = df_season['Driver'].astype(str).str.strip()
                df_season['Team'] = df_season['Team'].astype(str).str.strip()
                
                driver_teams = df_season.groupby('Driver')['Team'].apply(lambda x: ", ".join(x.unique())).to_dict()
                combined_totals[f'Season {season_num}'] = combined_totals['Driver'].map(driver_teams).fillna('—')
            except Exception:
                combined_totals[f'Season {season_num}'] = '—'

        season_cols = [f'Season {i+1}' for i in range(NumSeason)]
        combined_totals = combined_totals[['Place', tORd, 'Points', '1st Place', '2nd Place', '3rd Place', 'Podiums', x, 'Highest Position', 'Win Streak', 'Single Season Win Streak'] + season_cols]
        combined_totals['Place'] = combined_totals.index + 1

    elif tORd == 'Team':
        if 'Podiums' in combined_totals.columns:
            combined_totals = combined_totals.drop(columns=['Podiums'])
        combined_totals['Highest Position'] = combined_totals['Team'].map(highest_positions.get('constructors', {})).fillna("—")
        
        for i in range(NumSeason):
            season_num = i + 1
            try:
                df_season = get_excel_sheet("Season" + str(season_num))
                df_season['Driver'] = df_season['Driver'].astype(str).str.strip()
                df_season['Team'] = df_season['Team'].astype(str).str.strip()
                
                team_drivers = df_season.groupby('Team')['Driver'].apply(lambda x: ", ".join(x.unique())).to_dict()
                combined_totals[f'Season {season_num}'] = combined_totals['Team'].map(team_drivers).fillna('—')
            except Exception:
                combined_totals[f'Season {season_num}'] = '—'

        season_cols = [f'Season {i+1}' for i in range(NumSeason)]
        combined_totals = combined_totals[['Place', tORd, 'Points', '1st Place', '2nd Place', '3rd Place', x, 'Highest Position', 'Win Streak', 'Single Season Win Streak'] + season_cols]
        combined_totals['Place'] = combined_totals.index + 1

    _func_cache[cache_key] = combined_totals.copy()
    return combined_totals

def GetSeasonChampions(num_seasons: int):
    cache_key = ("GetSeasonChampions", num_seasons)
    excel_path = Path(file)
    current_mtime = excel_path.stat().st_mtime if excel_path.exists() else 0
    if _excel_mtime == current_mtime and cache_key in _func_cache:
        return _func_cache[cache_key]

    constructor_champs = {}
    driver_champs = {}
    for s in range(1, num_seasons + 1):
        if is_season_completed(s):
            try:
                _, _, _, df_team, _, df_driver = PointTotals(s)
                if not df_team.empty:
                    constructor_champs[s] = df_team['Team'].iloc[0]
                if not df_driver.empty:
                    driver_champs[s] = df_driver['Driver'].iloc[0]
            except Exception:
                pass
    res = (constructor_champs, driver_champs)
    _func_cache[cache_key] = res
    return res

def RacesAllTime(NumSeason, tORd):
    cache_key = ("RacesAllTime", NumSeason, tORd)
    excel_path = Path(file)
    current_mtime = excel_path.stat().st_mtime if excel_path.exists() else 0
    if _excel_mtime == current_mtime and cache_key in _func_cache:
        return _func_cache[cache_key].copy()

    dfs3 = []
    for i in range(NumSeason):
        df = get_excel_sheet("Season" + str(i + 1))

        df['Driver'] = df['Driver'].astype(str).str.strip()
        df['Team'] = df['Team'].astype(str).str.strip()

        x = tORd

        cols_to_keep = [col for col in df.columns if col.endswith("Place") or col == x]
        df = df[cols_to_keep]

        place_cols = [col.replace("Place", "").strip() for col in df.columns if col != x]
        summary_data = {'Race': place_cols}

        podium_list = []
        for col in [c + "Place" for c in place_cols]:
            has_scores = False
            if col in df.columns:
                valid_scores = df[col].dropna()
                try:
                    numeric_scores = pd.to_numeric(valid_scores, errors='coerce').dropna()
                    if not numeric_scores.empty and not (numeric_scores == 0).all():
                        has_scores = True
                except Exception:
                    pass

            if has_scores:
                podium_entries = []
                for place, prefix in [(1, '🥇 '), (2, '🥈 '), (3, '🥉 ')]:
                    drivers = df[df[col] == place][x].tolist()
                    if drivers:
                        podium_entries.append(prefix + ', '.join(drivers))
                    else:
                        podium_entries.append(prefix + "None")
                podium_list.append('\n'.join(podium_entries))
            else:
                podium_list.append(None)

        summary_data['Season ' + str(i + 1)] = podium_list
        summary_df = pd.DataFrame(summary_data)
        dfs3.append(summary_df)

    final_df = pd.concat(dfs3, ignore_index=True)
    grouped_df = final_df.groupby('Race').agg(lambda x: '\n\n'.join(x.dropna())).reset_index()

    season_cols = [col for col in grouped_df.columns if col.startswith('Season ')]
    is_completed = grouped_df[season_cols].apply(lambda row: any(str(val).strip() != "" for val in row), axis=1)
    grouped_df = grouped_df[is_completed].reset_index(drop=True)

    _func_cache[cache_key] = grouped_df.copy()
    return grouped_df
