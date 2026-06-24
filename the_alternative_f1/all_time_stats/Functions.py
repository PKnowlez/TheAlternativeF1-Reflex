# Universal functions for All Time Stats in Reflex webapp
# Adapted from Functions copy.py to be dependency-free (no streamlit/plotting)

import os
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

team_colors = {
    'Alpine': 'hotpink', 
    'Aston Martin': 'teal',
    'Ferrari': 'red',
    'McLaren': 'darkorange',
    'Red Bull': 'darkblue',
    'VCARB': 'blue',
    'AlphaTauri': 'LightSlateGray',
    'Alfa Romeo': 'Maroon',
    'Mercedes': 'black',
    'Haas': 'gray',
}

def PointTotals(season):
    # Read in the appropriate sheet for the selected season
    sheet = "Season" + str(season)
    df = pd.read_excel(file, sheet_name=sheet)

    # Read in the list of races from the selected season
    sheet_sched = "S" + str(season) + "Schedule"
    schedule = pd.read_excel(file, sheet_name=sheet_sched)

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

    return None, None, None, constructor_totals, None, driver_totals

def is_season_completed(season):
    sheet = "Season" + str(season)
    try:
        df = pd.read_excel(file, sheet_name=sheet)
        sheet_sched = "S" + str(season) + "Schedule"
        schedule = pd.read_excel(file, sheet_name=sheet_sched)
    except Exception:
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
        return False

    last_col = race_points[-1]
    if last_col not in df.columns:
        return False

    col_values = df[last_col].dropna()
    if col_values.empty:
        return False

    try:
        numeric_values = pd.to_numeric(col_values, errors='coerce').dropna()
        if numeric_values.empty or (numeric_values == 0).all():
            return False
    except Exception:
        return False

    return True

def CalculateAllTime(NumSeason, tORd):
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
        sheet = "Season" + str(i+1)
        df_season = pd.read_excel(file, sheet_name=sheet)

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

    # Create the second dataframe that sums placements
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

    # Read in all season dataframes and concatenate them
    dfs_all_seasons = []
    for i in range(NumSeason):
        sheet = "Season" + str(i+1)
        df_season = pd.read_excel(file, sheet_name=sheet)
        df_season['Season'] = i + 1
        df_season['Driver'] = df_season['Driver'].astype(str).str.strip()
        df_season['Team'] = df_season['Team'].astype(str).str.strip()
        dfs_all_seasons.append(df_season)
    all_races_df = pd.concat(dfs_all_seasons)

    # Melt the dataframe to have a single column for race results
    melted_races = all_races_df.melt(id_vars=[tORd, 'Season'], value_vars=[col for col in all_races_df.columns if col.endswith('Place')], var_name='Race', value_name='Place')
    
    # Sort the dataframe by season and then race to ensure correct streak calculations
    melted_races['Race_Order'] = melted_races.groupby('Season')['Race'].rank(method='dense')
    melted_races = melted_races.sort_values(by=['Season', 'Race_Order']).reset_index(drop=True)

    # Calculate streaks
    if tORd == 'Driver':
        combined_totals['Win Streak'] = 0
        combined_totals['Single Season Win Streak'] = 0
        
        for entity in combined_totals[tORd].unique():
            entity_df = melted_races[melted_races[tORd] == entity].sort_values(by=['Season', 'Race_Order']).copy()
            
            # Overall win streak
            max_win_streak = 0
            current_win_streak = 0
            
            # Single-season win streak
            max_ss_win_streak = 0
            current_ss_win_streak = 0
            
            last_season = None
            
            for index, row in entity_df.iterrows():
                place = row['Place']
                season = row['Season']
                
                # Overall win streak logic
                is_win = place == 1

                if is_win:
                    current_win_streak += 1
                else:
                    max_win_streak = max(max_win_streak, current_win_streak)
                    current_win_streak = 0
                
                # Single-season win streak logic
                if last_season is not None and season != last_season:
                    max_ss_win_streak = max(max_ss_win_streak, current_ss_win_streak)
                    current_ss_win_streak = 0
                
                if is_win:
                    current_ss_win_streak += 1
                else:
                    max_ss_win_streak = max(max_ss_win_streak, current_ss_win_streak)
                    current_ss_win_streak = 0
                
                last_season = season
                
            max_win_streak = max(max_win_streak, current_win_streak)
            max_ss_win_streak = max(max_ss_win_streak, current_ss_win_streak)
            
            combined_totals.loc[combined_totals[tORd] == entity, 'Win Streak'] = int(max_win_streak)
            combined_totals.loc[combined_totals[tORd] == entity, 'Single Season Win Streak'] = int(max_ss_win_streak)
        
        combined_totals['Win Streak'] = combined_totals['Win Streak'].astype(int)
        combined_totals['Single Season Win Streak'] = combined_totals['Single Season Win Streak'].astype(int)
        
        # Reorder columns for drivers
        combined_totals = combined_totals[['Place', tORd, 'Points', '1st Place', '2nd Place', '3rd Place', 'Podiums', x, 'Win Streak', 'Single Season Win Streak']]
        combined_totals['Place'] = combined_totals.index + 1

    elif tORd == 'Team':
        # Remove Podium columns as they are not needed for Team analysis as requested
        combined_totals = combined_totals.drop(columns=['Podiums'])
        
        # Reorder columns for teams
        combined_totals = combined_totals[['Place', tORd, 'Points', '1st Place', '2nd Place', '3rd Place', x]]
        combined_totals['Place'] = combined_totals.index + 1

    return combined_totals

def RacesAllTime(NumSeason, tORd):
    dfs3 = []
    for i in range(NumSeason):
        sheet = "Season" + str(i + 1)
        df = pd.read_excel(file, sheet_name=sheet)

        df['Driver'] = df['Driver'].astype(str).str.strip()
        df['Team'] = df['Team'].astype(str).str.strip()

        x = tORd

        cols_to_keep = [col for col in df.columns if col.endswith("Place") or col == x]
        df = df[cols_to_keep]

        place_cols = [col.replace("Place", "").strip() for col in df.columns if col != x]
        summary_data = {'Race': place_cols}

        podium_list = []
        for col in [c + "Place" for c in place_cols]:
            podium_entries = []
            for place, prefix in [(1, '1st: '), (2, '2nd: '), (3, '3rd: ')]:
                drivers = df[df[col] == place][x].tolist()
                if drivers:
                    podium_entries.append(prefix + ', '.join(drivers))
                else:
                    podium_entries.append(prefix + "None")

            podium_list.append('\n'.join(podium_entries))

        summary_data['Season ' + str(i + 1)] = podium_list
        summary_df = pd.DataFrame(summary_data)
        dfs3.append(summary_df)

    # Concatenate all DataFrames
    final_df = pd.concat(dfs3, ignore_index=True)

    # Group by 'Race' and aggregate 'Season X' columns
    grouped_df = final_df.groupby('Race').agg(lambda x: '\n\n'.join(x.dropna())).reset_index()
    return grouped_df
