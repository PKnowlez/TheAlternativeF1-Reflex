# The functions within this file are universal for TheAlternativeF1.py
#   PointsTotals:   function that calculates and returns the sum of points
#                   for both drivers and constructors over the course of 
#                   one season
#   CalculateAllTime:   Generate all time statistics tables for either
#                       driver or team

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px
import Plotting

# Global variables for all of the functions
place_suffix = "Place"
qualifying_suffix = "Qualifying"
fastestlap_suffix = "FastestLap" 
points_suffix = "Points"
file = "The_Alternative_F1.xlsx"
# More color names can be found here: https://www.w3schools.com/cssref/css_colors.php
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
    # Input variables
    #   season: numeric value of the season to be calculated

    # Read in the appropriate sheet for the selected season
    sheet = "Season"+str(season)
    df = pd.read_excel(file,sheet_name=sheet)

    # Read in the list of races from the selected season
    sheet = "S"+str(season)+"Schedule"
    schedule = pd.read_excel(file,sheet_name=sheet)

    # Loop through the schedule and create lists for each global suffix
    races = []
    race_place = []
    race_qualifying = []
    race_fastestlap = []
    race_points = []
    for i in range(len(schedule)):
        race_name = schedule['Race'].iloc[i]

        if race_name.startswith(('Pre', 'Post')):
            continue

        races.append(race_name)
        race_place.append(race_name+place_suffix)
        race_qualifying.append(race_name+qualifying_suffix)
        race_fastestlap.append(race_name+fastestlap_suffix)
        race_points.append(race_name+points_suffix)

    team_race_totals = pd.DataFrame([]) 
    for i in range(len(race_points)):
        if i == 0:
            team_race_totals[race_points[i]] = df.groupby('Team')[race_points[i]].sum()
        else:
            team_race_totals[race_points[i]] = df.groupby('Team')[race_points[i]].sum() \
                                                    + team_race_totals[race_points[i-1]]

    driver_race_totals = pd.DataFrame([])
    for i in range(len(race_points)):
        if i == 0:
            driver_race_totals[race_points[i]] = df.groupby('Driver')[race_points[i]].sum()
        else:
            driver_race_totals[race_points[i]] = df.groupby('Driver')[race_points[i]].sum() \
                                                    + driver_race_totals[race_points[i-1]]

    # Create the driver_colors dictionary
    driver_colors = {}
    for index, row in df.iterrows():
        driver = row['Driver']
        team = row['Team']
        driver_colors[driver] = team_colors.get(team)

    # Create line chart plots      
    constructor_line = Plotting.TotalsLineChart(team_race_totals,team_colors,"Constructor's Championship",races,'Team')
    driver_line = Plotting.TotalsLineChart(driver_race_totals,driver_colors,"Driver's Championship",races,'Driver')

    # Create bar chart plots
    constructor_bar, constructor_totals = Plotting.TotalsBarChart(team_race_totals,team_colors,"Constructor's Championship",'Team')
    driver_bar, driver_totals = Plotting.TotalsBarChart(driver_race_totals,driver_colors,"Driver's Championship",'Driver')

    return constructor_line, driver_line, constructor_bar, constructor_totals, driver_bar, driver_totals

def CalculateAllTime(NumSeason,tORd):
    # Input Variables
    #   NumSeason:   the number of seasons that the league has completed to be combined
    #   tORd: 'Team' or 'Driver'
     
    # Loop through the points scored for each tORd 
    dfs = []
    champs = []
    for i in range(NumSeason):
        if tORd == 'Team':
            x, x, x, globals()[f'df{i}'], x, x = PointTotals(i+1)
            champ = globals()[f'df{i}']['Team'].iloc[0]
            champs.append(champ)
            dfs.append(globals()[f'df{i}'])
        elif tORd == 'Driver':
            x, x, x, x, x, globals()[f'df{i}'] = PointTotals(i+1)
            champ = globals()[f'df{i}']['Driver'].iloc[0]
            champs.append(champ)
            dfs.append(globals()[f'df{i}'])

    # Create the initial combined dataframe with place, tORd, and points
    combined_df = pd.concat(dfs)
    totals = combined_df.groupby(tORd)['Points'].sum().reset_index()
    totals_sorted = totals.sort_values(by='Points', ascending=False).reset_index(drop=True)
    totals_sorted['Place'] = totals_sorted.index + 1
    totals_sorted = totals_sorted[['Place', tORd, 'Points']]

    dfs2 = []
    for i in range(NumSeason):
        sheet = "Season"+str(i+1)
        globals()[f'df{i}'] = pd.read_excel(file,sheet_name=sheet)

        if tORd == 'Team':
            x = 'Team'
        elif tORd == 'Driver':
            x = 'Driver'

        # Keep place columns and remove the rest
        cols_to_keep = [col for col in globals()[f'df{i}'].columns if col.endswith("Place") or col == x]
        globals()[f'df{i}'] = globals()[f'df{i}'][cols_to_keep]
        place_cols = [col for col in globals()[f'df{i}'].columns if col!= x]
        melted_df = globals()[f'df{i}'].melt(id_vars=x, value_vars=place_cols, value_name='Place')

        # Count 1st, 2nd, and 3rd places for each driver
        placement_counts = melted_df.groupby(tORd)['Place'].value_counts().unstack(fill_value=0)
        globals()[f'df2{i}'] = placement_counts.rename(columns={1.0: '1st Place', 2.0: '2nd Place', 3.0: '3rd Place'})

        dfs2.append(globals()[f'df2{i}'])

    # Create the second dataframe that sums placements
    combined_df2 = pd.concat(dfs2)
    totals2 = combined_df2.groupby(tORd).sum().reset_index()  
    totals_sorted2 = totals2.sort_values(by=['1st Place', '2nd Place', '3rd Place'], ascending=False).reset_index(drop=True)
    totals_sorted2 = totals_sorted2[[tORd, '1st Place', '2nd Place', '3rd Place']]

    # Combine totals_sorted and totals_sorted2 using an outer join
    combined_totals = pd.merge(totals_sorted, totals_sorted2, on=[tORd], how='outer')
    combined_totals = combined_totals.groupby([tORd, 'Points']).sum().reset_index()
    combined_totals = combined_totals.sort_values(by='Points', ascending=False).reset_index(drop=True)
    combined_totals['Podiums'] = combined_totals['1st Place'] + combined_totals['2nd Place'] + combined_totals['3rd Place']
    combined_totals = combined_totals[['Place', tORd, 'Points', '1st Place', '2nd Place', '3rd Place','Podiums']]
    if tORd == 'Team':
        x = "Constructor's Champion"
    elif tORd == 'Driver':
        x = "Driver's Champion"
    combined_totals[x] = 0
    for champ in champs:
        combined_totals.loc[combined_totals[tORd] == champ, x] += 1

    # Read in all season dataframes and concatenate them
    dfs_all_seasons = []
    for i in range(NumSeason):
        sheet = "Season"+str(i+1)
        df_season = pd.read_excel(file, sheet_name=sheet)
        df_season['Season'] = i + 1
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
            
            combined_totals.loc[combined_totals[tORd] == entity, 'Win Streak'] = max_win_streak
            combined_totals.loc[combined_totals[tORd] == entity, 'Single Season Win Streak'] = max_ss_win_streak
        
        # Reorder columns for drivers
        combined_totals = combined_totals[['Place', tORd, 'Points', '1st Place', '2nd Place', '3rd Place', 'Podiums', x, 'Win Streak', 'Single Season Win Streak']]

        # # Find the index of the row with the maximum 'Win Streak'
        # max_streak_index = combined_totals['Win Streak'].idxmax()
        # # Use that index to get the driver's name from that row
        # driver_with_max_streak = combined_totals.loc[max_streak_index, 'Driver']
        # # Get the win streak value from that same row
        # win_streak_value = combined_totals.loc[max_streak_index, 'Win Streak']\
        # # Update the subheader to include both the name and the streak count
        # st.markdown(f"🏆 Longest Win Streak: {driver_with_max_streak} ({win_streak_value} Wins)")

    elif tORd == 'Team':
        # Remove Podium columns as they are not needed for Team analysis as requested
        combined_totals = combined_totals.drop(columns=['Podiums'])
        
        # Reorder columns for teams
        combined_totals = combined_totals[['Place', tORd, 'Points', '1st Place', '2nd Place', '3rd Place', x]]

    # Display the final combined dataframe
    st.dataframe(combined_totals, hide_index=True)

def RacesAllTime(NumSeason, tORd):
    # Input Variables
    #   NumSeason: the number of seasons that have occurred for the league
    #   tORd:  team or driver

    dfs3 = []
    for i in range(NumSeason):
        sheet = "Season" + str(i + 1)
        df = pd.read_excel(file, sheet_name=sheet)

        if tORd == 'Team':
            x = 'Team'
        elif tORd == 'Driver':
            x = 'Driver'

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

    # Convert DataFrame to HTML with replaced newlines
    html = grouped_df.to_html(escape=False, index=False).replace(r'\n', '<br>')

    # Display HTML using st.write
    st.write(html, unsafe_allow_html=True)