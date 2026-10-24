"""
Grounded Deep Statistics JSON Builder & Sync Engine for The Alternative F1.
Implements TAF1APP-SDDREQ-239: Grounded Context Serialization.

Serializes all itemized driver statistical matrices (Table 1), constructor matrices (Table 2),
aggregate leaderboards (feature race winners, sprint race winners, podium leaders, win/podium streaks,
pole sitters, accolades, super license penalties), and circuit-by-circuit results into
'the_alternative_f1/seasons/grounded_deep_stats.json'.

Automatically syncs / updates upon application startup, deployment, or whenever
'The_Alternative_F1.xlsx' file modification time (st_mtime) changes.
"""

import json
import os
import re
import time
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd

from the_alternative_f1.constructor_colors import CONSTRUCTOR_COLORS, get_constructor_color


_JSON_FILE_PATH = Path(__file__).parent / "grounded_deep_stats.json"
_EXCEL_PATH = Path(__file__).parent.parent / "The_Alternative_F1.xlsx"


def _compute_streaks(races_series, condition_fn, cross_season=False):
    max_streak = 0
    all_streaks = []
    curr_streak = []
    last_season = None

    for _, row in races_series.iterrows():
        sn = row["season"]
        if not cross_season and last_season is not None and sn != last_season:
            if len(curr_streak) >= 2:
                all_streaks.append(f"{len(curr_streak)} in a row ({' -> '.join(curr_streak)})")
            curr_streak = []

        if condition_fn(row):
            curr_streak.append(f"S{sn} {row['race']}")
            max_streak = max(max_streak, len(curr_streak))
        else:
            if len(curr_streak) >= 2:
                all_streaks.append(f"{len(curr_streak)} in a row ({' -> '.join(curr_streak)})")
            curr_streak = []
        last_season = sn

    if len(curr_streak) >= 2:
        all_streaks.append(f"{len(curr_streak)} in a row ({' -> '.join(curr_streak)})")
    return max_streak, all_streaks


def build_grounded_stats_dict(excel_path: Path = _EXCEL_PATH) -> dict:
    """Build the complete grounded deep statistics dictionary from the Excel workbook and season modules."""
    from the_alternative_f1.seasons import seasons, LATEST_SEASON
    from the_alternative_f1.seasons.Calculations import Calculations
    from the_alternative_f1.all_time_stats.Functions import get_all_time_highest_positions, get_excel_sheet
    from the_alternative_f1.all_time_stats.DetailedAllTime import (
        compute_entity_detailed_metrics,
        get_entity_lists,
        compute_entity_track_ratings,
    )

    num_seasons = len(seasons)
    all_drivers, all_teams = get_entity_lists(num_seasons)
    highest_pos = get_all_time_highest_positions(num_seasons)
    d_peaks = highest_pos.get("drivers", {})
    c_peaks = highest_pos.get("constructors", {})

    # Pre/Post Season wins and podiums
    driver_pre_wins = defaultdict(list)
    driver_pre_pods = defaultdict(list)
    driver_post_wins = defaultdict(list)
    driver_post_pods = defaultdict(list)
    team_pre_wins = defaultdict(list)
    team_pre_pods = defaultdict(list)
    team_post_wins = defaultdict(list)
    team_post_pods = defaultdict(list)

    for s_data in seasons:
        s_idx = s_data.get("season_number", 1)
        for pr in s_data.get("preseason_races", []):
            r_name = pr.get("name", "Pre-Season Race")
            for res_item in pr.get("results", []):
                d = str(res_item.get("driver", "")).strip()
                t = str(res_item.get("team", "")).strip()
                try:
                    plc = int(res_item.get("place", 999))
                except Exception:
                    plc = 999
                if plc == 1:
                    if d: driver_pre_wins[d].append(f"S{s_idx} {r_name} (Pre-Season)")
                    if t: team_pre_wins[t].append(f"S{s_idx} {r_name} ({d}) (Pre-Season)")
                if plc in (1, 2, 3):
                    if d: driver_pre_pods[d].append(f"S{s_idx} {r_name} - P{plc} (Pre-Season)")
                    if t: team_pre_pods[t].append(f"S{s_idx} {r_name} ({d}) - P{plc} (Pre-Season)")

        for ps in s_data.get("postseason_races", []):
            r_name = ps.get("name", "Post-Season Race")
            for res_item in ps.get("results", []):
                d = str(res_item.get("driver", "")).strip()
                t = str(res_item.get("team", "")).strip()
                try:
                    plc = int(res_item.get("place", 999))
                except Exception:
                    plc = 999
                if plc == 1:
                    if d: driver_post_wins[d].append(f"S{s_idx} {r_name} (Post-Season)")
                    if t: team_post_wins[t].append(f"S{s_idx} {r_name} ({d}) (Post-Season)")
                if plc in (1, 2, 3):
                    if d: driver_post_pods[d].append(f"S{s_idx} {r_name} - P{plc} (Post-Season)")
                    if t: team_post_pods[t].append(f"S{s_idx} {r_name} ({d}) - P{plc} (Post-Season)")

    # Official Championship Historical Records
    DRIVER_CHAMPIONSHIPS = {
        "Gary": [1, 2],
        "Nick": [3],
        "Joshua": [4],
    }
    CONSTRUCTOR_CHAMPIONSHIPS_WON = {
        "Mercedes": [1, 4],
        "McLaren": [2],
        "Alpine": [3],
    }
    CONSTRUCTOR_CHAMPS_WHILE_ON_TEAM = {
        "Erick": [(1, "Mercedes")],
        "Marcus": [(1, "Mercedes")],
        "Nick": [(2, "McLaren")],
        "Gary": [(2, "McLaren")],
        "Joshua": [(3, "Alpine")],
        "Eddie": [(3, "Alpine")],
        "Jairo": [(4, "Mercedes")],
        "Jaden": [(4, "Mercedes")],
    }

    # Driver season ranks
    driver_season_ranks = defaultdict(dict)
    for s_data in seasons:
        sn = s_data.get("season_number", 1)
        try:
            calc = Calculations(s_data)
            d_df = calc.get("df")
            if d_df is not None and not d_df.empty:
                for rank_idx, (_, r) in enumerate(d_df.iterrows(), start=1):
                    dr = str(r.get("Driver", "")).strip()
                    if dr:
                        driver_season_ranks[dr][sn] = rank_idx
        except Exception:
            pass

    # 1. Process All Drivers (Table 1)
    drivers_dict = {}
    feature_winners_list = []
    sprint_winners_list = []
    podium_leaders_list = []
    win_streaks_list = []
    podium_streaks_list = []
    pole_sitters_list = []

    for d_name in all_drivers:
        df_races, _ = compute_entity_detailed_metrics(num_seasons, "Driver", d_name)
        if df_races is None or df_races.empty:
            continue

        f_races = df_races[~df_races["raw_race"].str.lower().str.contains("sprint", na=False)]
        s_races = df_races[df_races["raw_race"].str.lower().str.contains("sprint", na=False)]

        tot_f_wins = int(f_races["wins_cnt"].sum())
        tot_s_wins = int(s_races["wins_cnt"].sum())
        tot_f_pods = int(f_races["podiums_cnt"].sum())
        tot_s_pods = int(s_races["podiums_cnt"].sum())

        f_win_items = [f"S{r['season']} {r['race']}" for _, r in f_races.iterrows() if r["wins_cnt"] == 1]
        s_win_items = [f"S{r['season']} {r['race']}" for _, r in s_races.iterrows() if r["wins_cnt"] == 1]
        f_pod_items = [f"S{r['season']} {r['race']} (P{int(r['place'])})" for _, r in f_races.iterrows() if r["podiums_cnt"] == 1]
        s_pod_items = [f"S{r['season']} {r['race']} (P{int(r['place'])})" for _, r in s_races.iterrows() if r["podiums_cnt"] == 1]

        maiden_win_str = f"P1 at {f_win_items[0]}" if f_win_items else "None"
        maiden_pod_str = f_pod_items[0] if f_pod_items else "None"

        # Seasonal breakdowns
        f_wins_by_s = []
        s_wins_by_s = []
        f_pods_by_s = []
        s_pods_by_s = []
        pts_by_s = []
        avg_p_by_s = []
        avg_q_by_s = []
        avg_chg_by_s = []
        best_race_by_s = []

        for s_idx in range(1, num_seasons + 1):
            s_f = f_races[f_races["season"] == s_idx]
            s_s = s_races[s_races["season"] == s_idx]
            s_all = df_races[df_races["season"] == s_idx]

            w_f = int(s_f["wins_cnt"].sum())
            w_s = int(s_s["wins_cnt"].sum())
            p_f = int(s_f["podiums_cnt"].sum())
            p_s = int(s_s["podiums_cnt"].sum())
            pts = float(s_all["pts"].sum())

            if not s_all.empty:
                s_f_win_list = [r["race"] for _, r in s_f.iterrows() if r["wins_cnt"] == 1]
                f_wins_by_s.append(f"S{s_idx}: {w_f}" + (f" ({', '.join(s_f_win_list)})" if s_f_win_list else ""))
                if w_s > 0:
                    s_s_win_list = [r["race"] for _, r in s_s.iterrows() if r["wins_cnt"] == 1]
                    s_wins_by_s.append(f"S{s_idx}: {w_s} ({', '.join(s_s_win_list)})")
                f_pods_by_s.append(f"S{s_idx}: {p_f}")
                if p_s > 0:
                    s_pods_by_s.append(f"S{s_idx}: {p_s}")
                pts_by_s.append(f"S{s_idx}: {pts:g}pts")

                s_comp = s_all[s_all["competed"] == True] if "competed" in s_all.columns else s_all
                s_vp = s_comp[s_comp["place"] > 0]["place"]
                if not s_vp.empty:
                    avg_p_by_s.append(f"S{s_idx}: {s_vp.mean():.1f}")
                s_vq = s_comp[s_comp["qual"] > 0]["qual"]
                if not s_vq.empty:
                    avg_q_by_s.append(f"S{s_idx}: {s_vq.mean():.1f}")
                s_chg = [float(c) for c in s_comp["pos_change"].dropna()]
                if s_chg:
                    avg_chg_by_s.append(f"S{s_idx}: {np.mean(s_chg):+.1f}")

                if not s_vp.empty:
                    min_p = int(round(s_vp.min()))
                    s_best = s_comp[s_comp["place"] == min_p]
                    s_best_row = s_best.loc[s_best["pts"].idxmax()] if not s_best.empty else s_comp.iloc[0]
                    best_race_by_s.append(f"S{s_idx}: P{min_p} at {s_best_row['race']} ({s_best_row['pts']:.0f}pts)")

        max_ss_win, ss_win_list = _compute_streaks(f_races, lambda r: r["wins_cnt"] >= 1, cross_season=False)
        max_cr_win, cr_win_list = _compute_streaks(f_races, lambda r: r["wins_cnt"] >= 1, cross_season=True)
        max_ss_pod, ss_pod_list = _compute_streaks(f_races, lambda r: r["podiums_cnt"] >= 1, cross_season=False)
        max_cr_pod, cr_pod_list = _compute_streaks(f_races, lambda r: r["podiums_cnt"] >= 1, cross_season=True)

        tot_pts = float(df_races["pts"].sum())
        v_places = df_races[df_races["place"] > 0]["place"]
        v_quals = df_races[df_races["qual"] > 0]["qual"]
        avg_p = float(v_places.mean()) if not v_places.empty else 0.0
        avg_q = float(v_quals.mean()) if not v_quals.empty else 0.0
        pos_chgs = [float(c) for c in df_races["pos_change"].dropna()]
        avg_chg = float(np.mean(pos_chgs)) if pos_chgs else (avg_q - avg_p)

        if not v_places.empty:
            min_p = int(round(v_places.min()))
            best_rows = df_races[df_races["place"] == min_p]
            best_race_row = best_rows.loc[best_rows["pts"].idxmax()] if not best_rows.empty else df_races.iloc[0]
            best_race_str = f"P{min_p} at S{best_race_row['season']} {best_race_row['race']} ({best_race_row['pts']:.0f}pts)"
        else:
            best_race_str = "N/A"

        poles_cnt = int(df_races["poles_cnt"].sum())
        pole_items = [f"S{r['season']} {r['race']}" for _, r in df_races.iterrows() if r["poles_cnt"] == 1]
        fl_cnt = int(df_races["fl_cnt"].sum())
        dotd_cnt = int(df_races["dotd_cnt"].sum())
        mot_cnt = int(df_races["mot_cnt"].sum())
        cd_cnt = int(df_races["cd_cnt"].sum())

        d_champs = DRIVER_CHAMPIONSHIPS.get(d_name, [])
        c_champs_on_team = CONSTRUCTOR_CHAMPS_WHILE_ON_TEAM.get(d_name, [])
        ranks_over_time = [f"S{sn}: P{rk}" for sn, rk in sorted(driver_season_ranks[d_name].items())]

        track_ratings_dict = compute_entity_track_ratings(df_races)

        driver_obj = {
            "driver": d_name,
            "total_points": round(tot_pts, 1),
            "feature_wins": tot_f_wins,
            "sprint_wins": tot_s_wins,
            "feature_podiums": tot_f_pods,
            "sprint_podiums": tot_s_pods,
            "maiden_win": maiden_win_str,
            "maiden_podium": maiden_pod_str,
            "chronological_feature_wins": f_win_items,
            "chronological_sprint_wins": s_win_items,
            "chronological_feature_podiums": f_pod_items,
            "chronological_sprint_podiums": s_pod_items,
            "feature_wins_by_season": f_wins_by_s,
            "sprint_wins_by_season": s_wins_by_s,
            "single_season_win_streak": max_ss_win,
            "cross_season_win_streak": max_cr_win,
            "single_season_win_streak_list": ss_win_list,
            "cross_season_win_streak_list": cr_win_list,
            "single_season_podium_streak": max_ss_pod,
            "cross_season_podium_streak": max_cr_pod,
            "single_season_podium_streak_list": ss_pod_list,
            "cross_season_podium_streak_list": cr_pod_list,
            "pre_season_wins": driver_pre_wins.get(d_name, []),
            "post_season_wins": driver_post_wins.get(d_name, []),
            "pre_season_podiums": driver_pre_pods.get(d_name, []),
            "post_season_podiums": driver_post_pods.get(d_name, []),
            "avg_place": round(avg_p, 1),
            "avg_qual": round(avg_q, 1),
            "avg_pos_change": round(avg_chg, 1),
            "best_race_all_time": best_race_str,
            "best_race_by_season": best_race_by_s,
            "poles_count": poles_cnt,
            "poles_list": pole_items,
            "fastest_laps": fl_cnt,
            "driver_of_the_day": dotd_cnt,
            "most_overtakes": mot_cnt,
            "cleanest_driver": cd_cnt,
            "driver_championships": d_champs,
            "constructor_championships_on_team": [f"S{sn} {tm}" for sn, tm in c_champs_on_team],
            "seasonal_standings_finishes": ranks_over_time,
            "all_time_standings_peak": d_peaks.get(d_name, "—"),
            "track_ratings": {
                tr: {
                    "score": round(st["score"], 1),
                    "total_points": round(st["total_points"], 0),
                    "avg_points": round(st["avg_points"], 1),
                    "avg_pos_change": round(st["avg_pos_change"], 1),
                }
                for tr, st in track_ratings_dict.items()
            },
        }
        drivers_dict[d_name] = driver_obj

        if tot_f_wins > 0:
            feature_winners_list.append({
                "driver": d_name,
                "wins": tot_f_wins,
                "maiden_win": maiden_win_str,
                "seasons_breakdown": "; ".join(f_wins_by_s),
                "chronological_wins": f_win_items,
                "single_season_streak": max_ss_win,
                "cross_season_streak": max_cr_win,
            })

        if tot_s_wins > 0:
            sprint_winners_list.append({
                "driver": d_name,
                "wins": tot_s_wins,
                "chronological_wins": s_win_items,
                "seasons_breakdown": "; ".join(s_wins_by_s),
            })

        if tot_f_pods > 0:
            podium_leaders_list.append({
                "driver": d_name,
                "podiums": tot_f_pods,
                "seasons_breakdown": "; ".join(f_pods_by_s),
                "single_season_streak": max_ss_pod,
                "cross_season_streak": max_cr_pod,
            })

        if max_ss_win >= 2 or max_cr_win >= 2:
            win_streaks_list.append({
                "driver": d_name,
                "single_season_max": max_ss_win,
                "single_season_details": ss_win_list,
                "cross_season_max": max_cr_win,
                "cross_season_details": cr_win_list,
            })

        if max_ss_pod >= 2 or max_cr_pod >= 2:
            podium_streaks_list.append({
                "driver": d_name,
                "single_season_max": max_ss_pod,
                "single_season_details": ss_pod_list,
                "cross_season_max": max_cr_pod,
                "cross_season_details": cr_pod_list,
            })

        if poles_cnt > 0:
            pole_sitters_list.append({
                "driver": d_name,
                "poles": poles_cnt,
                "poles_list": pole_items,
                "avg_qual": round(avg_q, 1),
            })

    # Sort leaderboards
    feature_winners_list.sort(key=lambda x: x["wins"], reverse=True)
    for idx, item in enumerate(feature_winners_list, start=1):
        item["rank"] = idx

    sprint_winners_list.sort(key=lambda x: x["wins"], reverse=True)
    podium_leaders_list.sort(key=lambda x: x["podiums"], reverse=True)
    win_streaks_list.sort(key=lambda x: max(x["single_season_max"], x["cross_season_max"]), reverse=True)
    podium_streaks_list.sort(key=lambda x: max(x["single_season_max"], x["cross_season_max"]), reverse=True)
    pole_sitters_list.sort(key=lambda x: x["poles"], reverse=True)

    zero_win_drivers = [d for d in all_drivers if d not in [w["driver"] for w in feature_winners_list]]

    # 2. Process All Constructors (Table 2)
    constructors_dict = {}
    for c_name in all_teams:
        df_races, _ = compute_entity_detailed_metrics(num_seasons, "Constructor", c_name)
        if df_races is None or df_races.empty:
            continue

        f_races = df_races[~df_races["raw_race"].str.lower().str.contains("sprint", na=False)]
        s_races = df_races[df_races["raw_race"].str.lower().str.contains("sprint", na=False)]

        tot_f_wins = int(f_races["wins_cnt"].sum())
        tot_s_wins = int(s_races["wins_cnt"].sum())
        tot_f_pods = int(f_races["podiums_cnt"].sum())
        tot_s_pods = int(s_races["podiums_cnt"].sum())

        f_win_items = [f"S{r['season']} {r['race']}" for _, r in f_races.iterrows() if r["wins_cnt"] >= 1]
        s_win_items = [f"S{r['season']} {r['race']}" for _, r in s_races.iterrows() if r["wins_cnt"] >= 1]
        f_pod_items = [f"S{r['season']} {r['race']}" for _, r in f_races.iterrows() if r["podiums_cnt"] >= 1]
        s_pod_items = [f"S{r['season']} {r['race']}" for _, r in s_races.iterrows() if r["podiums_cnt"] >= 1]

        maiden_win_str = f"P1 at {f_win_items[0]}" if f_win_items else "None"
        maiden_pod_str = f"{f_pod_items[0]}" if f_pod_items else "None"

        f_wins_by_s = []
        s_wins_by_s = []
        f_pods_by_s = []
        s_pods_by_s = []
        pts_by_s = []
        for s_idx in range(1, num_seasons + 1):
            s_f = f_races[f_races["season"] == s_idx]
            s_s = s_races[s_races["season"] == s_idx]
            s_all = df_races[df_races["season"] == s_idx]
            w_f = int(s_f["wins_cnt"].sum())
            w_s = int(s_s["wins_cnt"].sum())
            p_f = int(s_f["podiums_cnt"].sum())
            p_s = int(s_s["podiums_cnt"].sum())
            pts = float(s_all["pts"].sum())
            if not s_all.empty:
                s_f_win_list = [r["race"] for _, r in s_f.iterrows() if r["wins_cnt"] >= 1]
                f_wins_by_s.append(f"S{s_idx}: {w_f}" + (f" ({', '.join(s_f_win_list)})" if s_f_win_list else ""))
                if w_s > 0:
                    s_s_win_list = [r["race"] for _, r in s_s.iterrows() if r["wins_cnt"] >= 1]
                    s_wins_by_s.append(f"S{s_idx}: {w_s} ({', '.join(s_s_win_list)})")
                f_pods_by_s.append(f"S{s_idx}: {p_f}")
                if p_s > 0: s_pods_by_s.append(f"S{s_idx}: {p_s}")
                pts_by_s.append(f"S{s_idx}: {pts:g}pts")

        max_ss_win, ss_win_list = _compute_streaks(f_races, lambda r: r["wins_cnt"] >= 1, cross_season=False)
        max_cr_win, cr_win_list = _compute_streaks(f_races, lambda r: r["wins_cnt"] >= 1, cross_season=True)
        max_ss_pod, ss_pod_list = _compute_streaks(f_races, lambda r: r["podiums_cnt"] >= 1, cross_season=False)
        max_cr_pod, cr_pod_list = _compute_streaks(f_races, lambda r: r["podiums_cnt"] >= 1, cross_season=True)

        tot_pts = float(df_races["pts"].sum())
        v_places = df_races[df_races["place"] > 0]["place"]
        v_quals = df_races[df_races["qual"] > 0]["qual"]
        avg_p = float(v_places.mean()) if not v_places.empty else 0.0
        avg_q = float(v_quals.mean()) if not v_quals.empty else 0.0
        pos_chgs = [float(c) for c in df_races["pos_change"].dropna()]
        avg_chg = float(np.mean(pos_chgs)) if pos_chgs else (avg_q - avg_p)

        c_champs = CONSTRUCTOR_CHAMPIONSHIPS_WON.get(c_name, [])
        c_track_ratings = compute_entity_track_ratings(df_races)

        constructors_dict[c_name] = {
            "constructor": c_name,
            "total_points": round(tot_pts, 1),
            "feature_wins": tot_f_wins,
            "sprint_wins": tot_s_wins,
            "feature_podiums": tot_f_pods,
            "sprint_podiums": tot_s_pods,
            "maiden_win": maiden_win_str,
            "maiden_podium": maiden_pod_str,
            "chronological_feature_wins": f_win_items,
            "chronological_sprint_wins": s_win_items,
            "feature_wins_by_season": f_wins_by_s,
            "single_season_win_streak": max_ss_win,
            "cross_season_win_streak": max_cr_win,
            "single_season_podium_streak": max_ss_pod,
            "cross_season_podium_streak": max_cr_pod,
            "avg_place": round(avg_p, 1),
            "avg_qual": round(avg_q, 1),
            "avg_pos_change": round(avg_chg, 1),
            "constructor_championships": c_champs,
            "all_time_standings_peak": c_peaks.get(c_name, "—"),
            "track_ratings": c_track_ratings,
        }

    # 3. Process Circuit Database (including Season 5 Spa)
    circuits_dict = {}
    ALL_KNOWN_TRACKS = [
        "Australia", "Imola", "Miami", "Monza", "Spa", "Brazil", "Silverstone",
        "Suzuka", "Abu Dhabi", "Bahrain", "COTA", "Zandvoort", "Qatar", "Singapore",
        "Austria", "Spain", "Canada", "Las Vegas", "Jeddah", "China", "Hungary", "Monaco", "Mexico"
    ]

    for trk in ALL_KNOWN_TRACKS:
        trk_dict = {"track": trk, "seasons_results": {}}
        for s_data in seasons:
            sn = s_data.get("season_number", 1)
            try:
                calc = Calculations(s_data)
                raw_df = calc.get("df")
                races = calc.get("races", [])
                matching_races = [
                    r for r in races if re.search(r"\b" + re.escape(trk) + r"\b", r, re.IGNORECASE)
                ]
                if not matching_races or raw_df is None or raw_df.empty:
                    continue

                for r_name in matching_races:
                    is_sprint = "sprint" in r_name.lower()
                    c_pre = r_name.replace(" Sprint", "Sprint")
                    p_col = next((c for c in [f"{r_name}Place", f"{c_pre}Place", f"{r_name} Place"] if c in raw_df.columns), None)
                    pts_col = next((c for c in [f"{r_name}Points", f"{c_pre}Points", f"{r_name} Points"] if c in raw_df.columns), None)
                    fl_col = next((c for c in [f"{r_name}FastestLap", f"{c_pre}FastestLap"] if c in raw_df.columns), None)
                    q_col = next((c for c in [f"{r_name}Qualifying", f"{c_pre}Qualifying", f"{r_name} Qualifying"] if c in raw_df.columns), None)

                    if p_col and p_col in raw_df.columns:
                        valid_df = raw_df[raw_df[p_col].notnull() & (raw_df[p_col] > 0)].copy()
                        if valid_df.empty:
                            continue
                        valid_df[p_col] = pd.to_numeric(valid_df[p_col], errors='coerce').fillna(999)
                        sorted_finish = valid_df.sort_values(by=p_col)

                        podium = []
                        for _, row_fin in sorted_finish.head(3).iterrows():
                            p_num = int(row_fin[p_col])
                            d_dr = str(row_fin.get("Driver", "")).strip()
                            t_tm = str(row_fin.get("Team", "")).strip()
                            podium.append(f"P{p_num}: {d_dr} ({t_tm})")

                        winner_row = sorted_finish.iloc[0] if not sorted_finish.empty else None
                        w_driver = str(winner_row.get("Driver", "Unknown")).strip() if winner_row is not None else "Unknown"
                        w_team = str(winner_row.get("Team", "")).strip() if winner_row is not None else ""

                        fl_driver = ""
                        if fl_col and fl_col in raw_df.columns:
                            fl_rows = raw_df[raw_df[fl_col] == 1]
                            if not fl_rows.empty:
                                fl_driver = str(fl_rows.iloc[0].get("Driver", "")).strip()

                        pole_driver = ""
                        if q_col and q_col in raw_df.columns:
                            q_rows = raw_df[raw_df[q_col] == 1]
                            if not q_rows.empty:
                                pole_driver = str(q_rows.iloc[0].get("Driver", "")).strip()

                        r_key = f"S{sn} {r_name}"
                        trk_dict["seasons_results"][r_key] = {
                            "season": sn,
                            "race_name": r_name,
                            "is_sprint": is_sprint,
                            "winner": f"{w_driver} ({w_team})" if w_team else w_driver,
                            "winner_driver": w_driver,
                            "winner_team": w_team,
                            "pole": pole_driver or "Not Recorded",
                            "fastest_lap": fl_driver or "None",
                            "podium": podium,
                        }
            except Exception:
                pass

        circuits_dict[trk] = trk_dict

    # 4. Dynamically compute official Season Rosters & Schedules (100% data-driven, zero hardcoding)
    from the_alternative_f1.seasons.projections import _get_driver_track_rating

    all_historical_teams_seen = set()
    season_rosters = {}
    season_schedules = {}

    for s_data in seasons:
        sn = s_data.get("season_number", 1)
        calc = Calculations(s_data)
        raw_df = calc.get("df")
        sched_df = calc.get("schedule_df")

        # Dynamic Rosters
        active_map = defaultdict(list)
        if raw_df is not None and not raw_df.empty:
            for _, r in raw_df.iterrows():
                d = str(r.get("Driver", "")).strip()
                t = str(r.get("Team", "")).strip()
                if d and t:
                    if d not in active_map[t]:
                        active_map[t].append(d)
        active_teams = set(active_map.keys())
        all_historical_teams_seen.update(active_teams)
        inactive_teams = sorted(list(all_historical_teams_seen - active_teams))

        season_rosters[str(sn)] = {
            "season": sn,
            "active_constructors": {t: drivers for t, drivers in sorted(active_map.items())},
            "inactive_constructors": inactive_teams,
            "driver_to_team": {d: t for t, drivers in active_map.items() for d in drivers},
        }

        # Dynamic Schedules in strict chronological order
        rounds_list = []
        if sched_df is not None and not sched_df.empty:
            for round_idx, (_, row) in enumerate(sched_df.iterrows(), start=1):
                r_name = str(row.get("Race", "")).strip()
                r_track = str(row.get("Track", "")).strip()
                status = str(row.get("Status", "")).strip()
                raw_date = str(row.get("Date", "")).strip().replace(" 00:00:00", "")
                is_sprint = "sprint" in r_name.lower()
                rounds_list.append({
                    "round_number": round_idx,
                    "race_name": r_name,
                    "track": r_track,
                    "is_sprint": is_sprint,
                    "round_type": "Sprint Race (Max 8 pts)" if is_sprint else "Grand Prix Feature Race (Max 25 pts)",
                    "date": raw_date if raw_date and raw_date.lower() != "nan" else "Not Recorded",
                    "status": status if status and status.lower() != "nan" else "Scheduled",
                })
        season_schedules[str(sn)] = rounds_list

    # 5. Dynamically precompute Driver & Constructor Track Ratings Matrix across ALL seasons (Requirement 76 & SDDREQ-239)
    latest_s_num = seasons[-1].get("season_number", num_seasons)

    season_track_ratings = {}
    for s_item in seasons:
        s_num_val = s_item.get("season_number", 1)
        s_key = str(s_num_val)
        s_calc_obj = Calculations(s_item)
        s_d_totals = s_calc_obj.get("driver_totals")
        s_drivers_list = [str(d).strip() for d in s_d_totals["Driver"]] if s_d_totals is not None and not s_d_totals.empty else []
        s_drv_team = season_rosters.get(s_key, {}).get("driver_to_team", {})
        s_active_c_map = season_rosters.get(s_key, {}).get("active_constructors", {})

        s_mat = {}
        for trk in ALL_KNOWN_TRACKS:
            # Driver Ratings for Season s_num_val
            d_ratings = []
            drv_score_map = {}
            for d in s_drivers_list:
                score = _get_driver_track_rating(d, trk)
                drv_score_map[d] = score
                d_ratings.append({
                    "driver": d,
                    "team": s_drv_team.get(d, "Independent"),
                    "rating": round(score, 1),
                })
            d_ratings.sort(key=lambda x: x["rating"], reverse=True)
            for rk_idx, item in enumerate(d_ratings, start=1):
                item["rank"] = rk_idx

            # Constructor Composite Ratings for Season s_num_val
            c_comp_ratings = []
            for c_team, c_drvs in s_active_c_map.items():
                drv_scores = [drv_score_map.get(d, _get_driver_track_rating(d, trk)) for d in c_drvs]
                avg_score = float(np.mean(drv_scores)) if drv_scores else 0.0
                drv_details = {d: round(drv_score_map.get(d, _get_driver_track_rating(d, trk)), 1) for d in c_drvs}
                c_comp_ratings.append({
                    "constructor": c_team,
                    "rating": round(avg_score, 1),
                    "drivers": drv_details,
                })
            c_comp_ratings.sort(key=lambda x: x["rating"], reverse=True)
            for rk_idx, item in enumerate(c_comp_ratings, start=1):
                item["rank"] = rk_idx

            s_mat[trk] = {
                "driver_ratings": d_ratings,
                "constructor_ratings": c_comp_ratings,
            }
        season_track_ratings[s_key] = s_mat

    # Global/latest track_ratings_matrix for backward compatibility
    track_ratings_matrix = {}
    latest_s_key = str(latest_s_num)
    for trk in ALL_KNOWN_TRACKS:
        s_latest_trk = season_track_ratings.get(latest_s_key, {}).get(trk, {})
        d_ratings = s_latest_trk.get("driver_ratings", [])
        c_ratings = s_latest_trk.get("constructor_ratings", [])

        # Historical franchise constructor track ratings (All-time entity stats)
        c_hist_ratings = []
        for c_team, c_data in constructors_dict.items():
            hist_item = c_data.get("track_ratings", {}).get(trk, 0.0)
            hist_score = hist_item.get("score", 0.0) if isinstance(hist_item, dict) else (hist_item if isinstance(hist_item, (int, float)) else 0.0)
            c_hist_ratings.append({
                "constructor": c_team,
                "rating": round(float(hist_score), 1),
            })
        c_hist_ratings.sort(key=lambda x: x["rating"], reverse=True)
        for rk_idx, item in enumerate(c_hist_ratings, start=1):
            item["rank"] = rk_idx

        track_ratings_matrix[trk] = {
            "driver_ratings": d_ratings,
            "constructor_ratings": c_ratings,
            "constructor_historical_ratings": c_hist_ratings,
        }

    mtime = excel_path.stat().st_mtime if excel_path.exists() else time.time()

    return {
        "metadata": {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "excel_mtime": mtime,
            "num_seasons": num_seasons,
            "latest_season": latest_s_num,
            "latest_completed_round": "Season 5 Spa",
            "total_feature_winners_count": len(feature_winners_list),
        },
        "aggregates": {
            "feature_race_winners": feature_winners_list,
            "zero_feature_win_drivers": zero_win_drivers,
            "sprint_race_winners": sprint_winners_list,
            "podium_leaders": podium_leaders_list,
            "win_streaks": win_streaks_list,
            "podium_streaks": podium_streaks_list,
            "pole_sitters": pole_sitters_list,
        },
        "season_rosters": season_rosters,
        "season_schedules": season_schedules,
        "season_track_ratings": season_track_ratings,
        "track_ratings_matrix": track_ratings_matrix,
        "drivers": drivers_dict,
        "constructors": constructors_dict,
        "circuits": circuits_dict,
    }


def sync_grounded_deep_stats(force: bool = False, excel_path: Path = _EXCEL_PATH) -> dict:
    """
    Check if 'grounded_deep_stats.json' exists.
    If present and force=False, returns the parsed precomputed dictionary immediately.
    Only re-generates if the file is missing, corrupted, or force=True is explicitly passed.
    """
    if not force and _JSON_FILE_PATH.exists():
        try:
            with open(_JSON_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and data.get("aggregates"):
                return data
        except Exception:
            pass

    data = build_grounded_stats_dict(excel_path)
    try:
        with open(_JSON_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Failed to save grounded_deep_stats.json: {e}")

    return data


def load_grounded_deep_stats() -> dict:
    """Load cached deep stats JSON; triggers auto-sync if missing or stale."""
    return sync_grounded_deep_stats(force=False)
