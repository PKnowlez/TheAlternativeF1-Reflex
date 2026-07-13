import json
import os
import pandas as pd
import numpy as np
from pathlib import Path
from the_alternative_f1.seasons import seasons
from the_alternative_f1.seasons.Calculations import Calculations

JSON_PATH = Path(__file__).parent / "power_rankings.json"

def custom_round(val):
    if pd.isna(val) or np.isnan(val):
        return np.nan
    return int(val + 0.5) if val >= 0 else int(val - 0.5)

def get_team_qualifying_avg(team, r_name, df):
    quali_col = f"{r_name}Qualifying"
    if quali_col not in df.columns:
        return np.nan
    team_df = df[df["Team"] == team]
    if team_df.empty:
        return np.nan
    vals = pd.to_numeric(team_df[quali_col], errors="coerce").dropna().tolist()
    vals = [v for v in vals if v > 0]
    return np.mean(vals) if vals else np.nan

def get_team_place_avg(team, r_name, df):
    place_col = f"{r_name}Place"
    if place_col not in df.columns:
        return np.nan
    team_df = df[df["Team"] == team]
    if team_df.empty:
        return np.nan
    vals = pd.to_numeric(team_df[place_col], errors="coerce").dropna().tolist()
    vals = [v for v in vals if v > 0]
    return np.mean(vals) if vals else np.nan

def get_team_seasonal_qualifying_avg(team, race_idx, races, df):
    all_vals = []
    for idx in range(race_idx + 1):
        r_name = races[idx]
        quali_col = f"{r_name}Qualifying"
        if quali_col in df.columns:
            team_df = df[df["Team"] == team]
            vals = pd.to_numeric(team_df[quali_col], errors="coerce").dropna().tolist()
            all_vals.extend([v for v in vals if v > 0])
    return np.mean(all_vals) if all_vals else np.nan

def get_team_seasonal_place_avg(team, race_idx, races, df):
    all_vals = []
    for idx in range(race_idx + 1):
        r_name = races[idx]
        place_col = f"{r_name}Place"
        if place_col in df.columns:
            team_df = df[df["Team"] == team]
            vals = pd.to_numeric(team_df[place_col], errors="coerce").dropna().tolist()
            all_vals.extend([v for v in vals if v > 0])
    return np.mean(all_vals) if all_vals else np.nan

def get_comparison_score(recent_val, target_val):
    if pd.isna(recent_val) or pd.isna(target_val) or np.isnan(recent_val) or np.isnan(target_val):
        return 0
    r_recent = custom_round(recent_val)
    r_target = custom_round(target_val)
    if r_recent < r_target:
        return 1
    elif r_recent > r_target:
        return -1
    else:
        return 0

def get_constructor_standings(race_idx, races, teams, df):
    points = {team: 0.0 for team in teams}
    for idx in range(race_idx + 1):
        r_name = races[idx]
        pts_col = f"{r_name}Points"
        for team in teams:
            team_df = df[df["Team"] == team]
            if pts_col in df.columns and not team_df.empty:
                points[team] += pd.to_numeric(team_df[pts_col], errors="coerce").fillna(0).sum()
    sorted_teams = sorted(teams, key=lambda t: (-points[t], t))
    return {team: idx + 1 for idx, team in enumerate(sorted_teams)}

def get_team_awards_score(team, r_name, df):
    awards_cols = [f"{r_name}FastestLap", f"{r_name}DOTD", f"{r_name}MOT", f"{r_name}CD"]
    count = 0
    team_df = df[df["Team"] == team]
    if team_df.empty:
        return 0.0
    for col in awards_cols:
        if col in df.columns:
            for val in team_df[col]:
                if val is True or str(val).upper() in ("Y", "YES"):
                    count += 1
    return count * 0.1

def get_final_rankings(prev_rankings, moves):
    n = len(prev_rankings)
    prev_rank = {team: idx + 1 for idx, team in enumerate(prev_rankings)}
    target_rank = {}
    for team in prev_rankings:
        tgt = prev_rank[team] - moves[team]
        target_rank[team] = max(1, min(n, tgt))
        
    import functools
    def compare(team_a, team_b):
        tgt_a = target_rank[team_a]
        tgt_b = target_rank[team_b]
        if tgt_a != tgt_b:
            return -1 if tgt_a < tgt_b else 1
            
        rank_a = prev_rank[team_a]
        rank_b = prev_rank[team_b]
        
        if rank_a < rank_b:
            if moves[team_b] == 2 and moves[team_a] == -1:
                return 1
            else:
                return -1
        else:
            if moves[team_a] == 2 and moves[team_b] == -1:
                return -1
            else:
                return 1
                
    sorted_teams = sorted(prev_rankings, key=functools.cmp_to_key(compare))
    
    result = []
    used = set()
    
    def backtrack(rank_idx):
        if rank_idx == n:
            return True
            
        current_rank = rank_idx + 1
        for team in sorted_teams:
            if team in used:
                continue
            if prev_rank[team] - 2 <= current_rank <= prev_rank[team] + 2:
                result.append(team)
                used.add(team)
                if backtrack(rank_idx + 1):
                    return True
                used.remove(team)
                result.pop()
        return False
        
    if backtrack(0):
        return result
    return sorted_teams

def calculate_all_seasons():
    data = {}
    for s in seasons:
        s_num = str(s["season_number"])
        try:
            res = Calculations(s)
            df = res["df"]
            races = res["races"]
            race_points = res["race_points"]
            race_place = res["race_place"]
            team_colors = s["team_colors"]
            teams = sorted(list(team_colors.keys()))
            
            # Determine how many races are completed
            completed_races_count = 0
            for i, col in enumerate(race_place):
                if df[race_points[i]].fillna(0).sum() > 0:
                    completed_races_count = i + 1
                else:
                    break
            
            completed_race_names = ["Preseason"] + races[:completed_races_count]
            
            # Allow custom preseason rankings if defined in the season config dictionary
            preseason_rankings = s.get("preseason_power_rankings")
            if preseason_rankings:
                preseason_list = [t for t in preseason_rankings if t in teams]
                for t in teams:
                    if t not in preseason_list:
                        preseason_list.append(t)
                rankings = {
                    "Preseason": preseason_list
                }
            else:
                rankings = {
                    "Preseason": teams.copy()
                }
            
            for idx in range(completed_races_count):
                r_name = races[idx]
                prev_race_name = "Preseason" if idx == 0 else races[idx - 1]
                prev_rankings_list = rankings[prev_race_name]
                
                # Fetch Standings
                StandingsRank_recent = get_constructor_standings(idx, races, teams, df)
                if idx == 0:
                    StandingsRank_prev = {team: teams.index(team) + 1 for team in teams}
                else:
                    StandingsRank_prev = get_constructor_standings(idx - 1, races, teams, df)
                
                moves = {}
                for team in teams:
                    # Seasonal Averages Calculations
                    Q_recent = get_team_qualifying_avg(team, r_name, df)
                    P_recent = get_team_place_avg(team, r_name, df)
                    
                    Q_seasonal = get_team_seasonal_qualifying_avg(team, idx, races, df)
                    P_seasonal = get_team_seasonal_place_avg(team, idx, races, df)
                    
                    qualifying_avg_score = get_comparison_score(Q_recent, Q_seasonal)
                    finishing_place_avg_score = get_comparison_score(P_recent, P_seasonal)
                    
                    # Overall standings rank comparison
                    rank_recent = StandingsRank_recent[team]
                    rank_prev = StandingsRank_prev[team]
                    if rank_recent < rank_prev:
                        overall_standings_score = 2
                    elif rank_recent > rank_prev:
                        overall_standings_score = -2
                    else:
                        overall_standings_score = 0
                        
                    seasonal_avg_total = (qualifying_avg_score + finishing_place_avg_score + overall_standings_score) / 3.0
                    
                    # Recent Race vs Last Race Calculations
                    awards_score = get_team_awards_score(team, r_name, df)
                    
                    if idx == 0:
                        qualifying_avg_score_vs_last = 0
                        finishing_place_avg_score_vs_last = 0
                    else:
                        Q_last = get_team_qualifying_avg(team, prev_race_name, df)
                        P_last = get_team_place_avg(team, prev_race_name, df)
                        
                        qualifying_avg_score_vs_last = get_comparison_score(Q_recent, Q_last)
                        finishing_place_avg_score_vs_last = get_comparison_score(P_recent, P_last)
                        
                    recent_vs_last_total = (awards_score + qualifying_avg_score_vs_last + finishing_place_avg_score_vs_last) / 3.0
                    
                    # Final Value
                    final_val = seasonal_avg_total * 0.65 + recent_vs_last_total * 0.35
                    
                    if final_val >= 1.0:
                        move = 2
                    elif final_val >= 0.5:
                        move = 1
                    elif final_val > -0.5:
                        move = 0
                    elif final_val > -1.0:
                        move = -1
                    else:
                        move = -2
                        
                    moves[team] = move
                    
                sorted_teams = get_final_rankings(prev_rankings_list, moves)
                rankings[r_name] = sorted_teams
                
            data[s_num] = {
                "races": completed_race_names,
                "rankings": rankings
            }
        except Exception as e:
            print(f"Error calculating rankings for season {s_num}: {e}")
            try:
                team_colors = s["team_colors"]
                teams = sorted(list(team_colors.keys()))
                data[s_num] = {
                    "races": ["Preseason"],
                    "rankings": {"Preseason": teams}
                }
            except Exception:
                pass
    return data

_power_rankings_cache = None

def load_power_rankings(season_num: int):
    global _power_rankings_cache
    
    excel_path = Path(__file__).parent.parent / "The_Alternative_F1.xlsx"
    force_recalculate = False
    
    if excel_path.exists() and JSON_PATH.exists():
        excel_mtime = excel_path.stat().st_mtime
        json_mtime = JSON_PATH.stat().st_mtime
        if excel_mtime > json_mtime:
            force_recalculate = True

    if _power_rankings_cache is None or force_recalculate:
        if JSON_PATH.exists() and not force_recalculate:
            try:
                with open(JSON_PATH, "r", encoding="utf-8") as f:
                    _power_rankings_cache = json.load(f)
            except Exception as e:
                print(f"Error reading power_rankings.json: {e}")
                _power_rankings_cache = {}
        else:
            _power_rankings_cache = {}
            
    s_key = str(season_num)
    if force_recalculate or s_key not in _power_rankings_cache:
        calculated_data = calculate_all_seasons()
        _power_rankings_cache.update(calculated_data)
        try:
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(_power_rankings_cache, f, indent=2)
        except Exception as e:
            print(f"Error writing power_rankings.json: {e}")
            
    return _power_rankings_cache.get(s_key, {"races": ["Preseason"], "rankings": {"Preseason": []}})
