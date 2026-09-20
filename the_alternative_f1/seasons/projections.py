"""Projections Tab — Reflex Component & Calculation Engine.
Implements TAF1APP-SDDFEAT-13 and approved downstream SDD requirements:
- SDDREQ-134: Dashed Line Constructor Projection (solid for completed, dashed for future)
- SDDREQ-135: Projection Calculations - Constructors (Track Rating & Inverted Power Ranking)
- SDDREQ-136: Constructor Expected to Win (skipping sprints)
- SDDREQ-137: Winner Projection Calculations (Driver Track Rating * 0.6 + Power Ranking * 0.4)
- SDDREQ-138: Constructor Expected Highest Score (Points Per Team Calculation)
- SDDREQ-139: Expected Teams on the Podium (Top 3 by Total Projection, skipping sprints)
- SDDREQ-140: Expected Points per Team (Points Per Team minus 0.5)
- SDDREQ-141: Points Per Team Calculation (Ranking drivers by track rating, assigning race/sprint pts)
- SDDREQ-151: Previous Lines (.json storage)
- SDDREQ-152: Projections Tab Layout (metric cards matching Map feature right panel above graph)
"""

import os
import json
import math
from pathlib import Path
import pandas as pd
import numpy as np
import reflex as rx

from the_alternative_f1.all_time_stats.Functions import get_excel_sheet
from the_alternative_f1.all_time_stats.DetailedAllTime import compute_entity_detailed_metrics, _extract_track_name
from the_alternative_f1.seasons.power_rankings import load_power_rankings
from the_alternative_f1.constructor_colors import CONSTRUCTOR_COLORS, get_constructor_color
from the_alternative_f1.articles.components import zoomable_chart, interactive_line_chart_key, DownloadState, chart_card

PROJECTIONS_JSON = Path(__file__).parent / "projections_lines.json"

F1_POINTS = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
SPRINT_POINTS = [8, 7, 6, 5, 4, 3, 2, 1]

_PROJECTIONS_CACHE = {}
_PROJECTIONS_MTIME = 0


def _get_driver_track_rating(driver_name: str, track_name: str) -> float:
    """References the already-calculated track rating score for a driver from DetailedAllTime."""
    try:
        df_races, _ = compute_entity_detailed_metrics(5, "Driver", driver_name)
        if df_races.empty:
            return 10.0
        
        # Match track name
        t_clean = _extract_track_name(track_name).lower()
        track_matches = df_races[df_races["track"].astype(str).str.lower() == t_clean]
        if track_matches.empty:
            # Driver has not raced at this specific track: use career average from tracks they have competed at
            valid_competed = df_races[df_races["competed"] == True] if "competed" in df_races.columns else df_races
            if valid_competed.empty:
                return 10.0
            t_avg_pts = float(valid_competed["pts"].mean())
            valid_q = valid_competed[valid_competed["qual"] > 0]["qual"]
            t_avg_q = float(valid_q.mean()) if not valid_q.empty else 10.0
            t_pos_changes = [float(c) for c in valid_competed["pos_change"].dropna() if c is not None]
            t_pos_change = float(np.mean(t_pos_changes)) if t_pos_changes else 0.0
        else:
            t_avg_pts = float(track_matches["pts"].mean())
            t_competed = track_matches[track_matches["competed"] == True] if "competed" in track_matches.columns else track_matches
            t_valid_q = t_competed[t_competed["qual"] > 0]["qual"]
            t_avg_q = float(t_valid_q.mean()) if not t_valid_q.empty else 10.0
            t_pos_changes = [float(c) for c in t_competed["pos_change"].dropna() if c is not None]
            t_pos_change = float(np.mean(t_pos_changes)) if t_pos_changes else 0.0

        q_term = (0.99 / t_avg_q * 0.2) if t_avg_q > 0 else 0.0
        score = (((t_avg_pts / 30.0) * 0.6) + q_term + ((t_pos_change / 22.0) * 0.2)) * 100.0
        return max(0.0, min(100.0, round(score, 2)))
    except Exception:
        return 10.0


def compute_season_projections(season_num: int = 5) -> dict:
    """Pre-calculates all projection metrics and line chart data for the season."""
    global _PROJECTIONS_CACHE, _PROJECTIONS_MTIME
    if not isinstance(season_num, int):
        try:
            season_num = int(season_num)
        except Exception:
            season_num = 5

    excel_path = Path(__file__).parent.parent / "The_Alternative_F1.xlsx"
    curr_mtime = excel_path.stat().st_mtime if excel_path.exists() else 0.0

    cache_key = f"season_{season_num}"
    if _PROJECTIONS_MTIME == curr_mtime and cache_key in _PROJECTIONS_CACHE:
        return _PROJECTIONS_CACHE[cache_key]

    df_season = get_excel_sheet(f"Season{season_num}")
    df_sched = get_excel_sheet(f"S{season_num}Schedule")

    if df_season.empty or df_sched.empty:
        return {}

    # Map driver to team
    df_season_clean = df_season.dropna(subset=["Driver"]).copy()
    df_season_clean["Driver"] = df_season_clean["Driver"].astype(str).str.strip()
    df_season_clean["Team"] = df_season_clean["Team"].astype(str).str.strip()

    driver_to_team = dict(zip(df_season_clean["Driver"], df_season_clean["Team"]))
    all_drivers = list(driver_to_team.keys())
    teams = sorted(list(set(df_season_clean["Team"].unique())))
    team_to_drivers = {}
    for team in teams:
        team_to_drivers[team] = df_season_clean[df_season_clean["Team"] == team]["Driver"].tolist()

    # Determine races from columns
    race_points_cols = [c for c in df_season_clean.columns if c.endswith("Points") and not c.startswith("Sprint")]
    all_races = [c[:-6].strip() for c in race_points_cols]

    # Find completed races
    completed_races = []
    for c in race_points_cols:
        r_name = c[:-6].strip()
        pts_s = pd.to_numeric(df_season_clean[c], errors="coerce").fillna(0)
        if pts_s.sum() > 0:
            completed_races.append(r_name)

    # Use schedule for the canonical full list of races in season order
    if not df_sched.empty and "Race" in df_sched.columns:
        sched_races = [
            str(r).strip() for r in df_sched["Race"].dropna()
            if str(r).strip() and not str(r).lower().startswith(("pre", "post"))
        ]
    else:
        sched_races = all_races

    completed_lower = [r.lower() for r in completed_races]
    upcoming_races = [r for r in sched_races if r.lower() not in completed_lower]
    all_races = sched_races if sched_races else all_races

    # Past seasons or seasons with no upcoming races are complete: use actual final results
    is_season_complete = (len(upcoming_races) == 0) or (season_num < 5)

    if is_season_complete:
        cum_totals = {t: 0.0 for t in teams}
        line_chart_data = []

        start_point = {"race": "Start"}
        for t in teams:
            start_point[f"{t}_actual"] = 0.0
        line_chart_data.append(start_point)

        for r in completed_races:
            p_col = f"{r}Points"
            pt = {"race": r}
            for t in teams:
                t_df = df_season_clean[df_season_clean["Team"] == t]
                r_pts = pd.to_numeric(t_df[p_col], errors="coerce").fillna(0).sum() if p_col in t_df.columns else 0.0
                cum_totals[t] += float(r_pts)
                pt[f"{t}_actual"] = round(cum_totals[t], 1)
            line_chart_data.append(pt)

        sorted_teams = sorted(teams, key=lambda t: cum_totals.get(t, 0), reverse=True)
        champion_team = sorted_teams[0] if sorted_teams else "None"
        champion_pts = int(cum_totals.get(champion_team, 0))
        podium_teams = sorted_teams[:3] if len(sorted_teams) >= 3 else sorted_teams

        # Determine Drivers Champion
        driver_pts = {}
        for d in all_drivers:
            d_df = df_season_clean[df_season_clean["Driver"] == d]
            pts = 0.0
            if not d_df.empty:
                for c in race_points_cols:
                    if c in d_df.columns:
                        pts += pd.to_numeric(d_df[c], errors="coerce").fillna(0).sum()
            driver_pts[d] = pts
        champion_driver = max(driver_pts.keys(), key=lambda d: driver_pts[d]) if driver_pts else ""

        team_final_lines = {t: round(cum_totals.get(t, 0), 1) for t in sorted_teams}

        result = {
            "season": season_num,
            "is_complete": True,
            "next_race": f"Season {season_num} Final",
            "next_main_race": f"Season {season_num} Final",
            "completed_races": completed_races,
            "upcoming_races": [],
            "teams": teams,
            "sorted_teams": sorted_teams,
            "champion_team": champion_team,
            "champion_driver": champion_driver,
            "expected_winner": champion_team,
            "expected_winner_score": 1.0,
            "expected_highest_score_team": champion_team,
            "highest_expected_points": champion_pts,
            "expected_podium": podium_teams,
            "team_expected_lines": team_final_lines,
            "team_points_calc": {t: int(cum_totals.get(t, 0)) for t in sorted_teams},
            "team_total_projections": {t: (1.0 if t == champion_team else 0.0) for t in sorted_teams},
            "line_chart_data": line_chart_data,
            "lines_record": {},
        }
        _PROJECTIONS_CACHE[cache_key] = result
        _PROJECTIONS_MTIME = curr_mtime
        return result

    # Power rankings
    pr_data = load_power_rankings(season_num)
    latest_pr_races = pr_data.get("races", [])
    latest_pr_key = latest_pr_races[-1] if latest_pr_races else "Preseason"
    pr_rankings = pr_data.get("rankings", {}).get(latest_pr_key, teams)

    n_teams = len(teams)
    # Power ranking factor: Rank 1 -> N/N=1.0, Rank 2 -> (N-1)/N, etc.
    team_pr_factor = {}
    for idx, t in enumerate(pr_rankings):
        rank = idx + 1
        inverted = n_teams - rank + 1
        team_pr_factor[t] = inverted / float(n_teams) if n_teams > 0 else 1.0

    # Ensure all teams have factor
    for t in teams:
        if t not in team_pr_factor:
            team_pr_factor[t] = 0.5

    # Target upcoming race for primary projections (skipping sprints per SDDREQ-136 / SDDREQ-139)
    next_race = upcoming_races[0] if upcoming_races else (all_races[-1] if all_races else "Upcoming Race")
    is_next_race_sprint = "sprint" in next_race.lower()

    # Next main race (skipping sprints if next race is sprint)
    next_main_race = next_race
    if is_next_race_sprint:
        for r in upcoming_races:
            if "sprint" not in r.lower():
                next_main_race = r
                break

    next_track = _extract_track_name(next_race)
    next_main_track = _extract_track_name(next_main_race)

    # 1. SDDREQ-135: Projection Calculations - Constructors
    # Track Rating = (Driver1 + Driver2) / 2
    # Total Projection = (Track Rating / 100) * 0.5 + Current Season Power Ranking * 0.5
    team_track_ratings = {}
    team_total_projections = {}
    driver_track_ratings = {}

    all_drivers = list(driver_to_team.keys())
    for d in all_drivers:
        driver_track_ratings[d] = _get_driver_track_rating(d, next_main_track)

    TRACK_WEIGHT = 0.70
    PR_WEIGHT = 0.30

    for team in teams:
        d_list = team_to_drivers.get(team, [])
        ratings = [driver_track_ratings.get(d, 10.0) for d in d_list]
        avg_track_rating = float(np.mean(ratings)) if ratings else 10.0
        team_track_ratings[team] = round(avg_track_rating, 2)
        pr_factor = team_pr_factor.get(team, 0.5)
        total_proj = (avg_track_rating / 100.0) * TRACK_WEIGHT + (pr_factor * PR_WEIGHT)
        team_total_projections[team] = round(total_proj, 3)

    # 2. SDDREQ-136 & SDDREQ-137: Winner Projection Calculations (unified with team projections)
    sorted_teams_by_proj = sorted(teams, key=lambda t: team_total_projections.get(t, 0), reverse=True)
    expected_winner_team = sorted_teams_by_proj[0] if sorted_teams_by_proj else (teams[0] if teams else "None")
    expected_winner_score = team_total_projections.get(expected_winner_team, 0.0)

    # 3. SDDREQ-139: Expected Teams on the Podium (Top 3 constructors by Total Projection, skipping sprints)
    expected_podium_teams = sorted_teams_by_proj[:3]

    # 4. SDDREQ-141: Points Per Team Calculation
    # Rank individual drivers from best to worst based on unified composite score:
    # (Track Rating / 100) * 0.70 + Current Season Power Ranking * 0.30
    # Assign points individually based on ranking (add sprint points if race date has sprint)
    driver_race_scores = {}
    for d in all_drivers:
        d_team = driver_to_team.get(d, "")
        t_rating = driver_track_ratings.get(d, 10.0)
        pr_factor = team_pr_factor.get(d_team, 0.5)
        driver_race_scores[d] = (t_rating / 100.0) * TRACK_WEIGHT + (pr_factor * PR_WEIGHT)

    drivers_sorted_by_rating = sorted(all_drivers, key=lambda d: driver_race_scores.get(d, 0.0), reverse=True)
    driver_assigned_points = {}
    for idx, d in enumerate(drivers_sorted_by_rating):
        pts = F1_POINTS[idx] if idx < len(F1_POINTS) else 0
        if is_next_race_sprint:
            s_pts = SPRINT_POINTS[idx] if idx < len(SPRINT_POINTS) else 0
            pts += s_pts
        driver_assigned_points[d] = pts

    # Sum two drivers for constructor (if sum ends in 0.5, round up)
    team_points_calc = {}
    team_expected_lines = {}
    for team in teams:
        d_list = team_to_drivers.get(team, [])
        pts_sum = sum(driver_assigned_points.get(d, 0) for d in d_list)
        if str(pts_sum).endswith(".5"):
            pts_sum = math.ceil(pts_sum)
        team_points_calc[team] = int(pts_sum)
        # SDDREQ-140: Display each team & expected points minus 0.5 (cannot be negative; automatically changes to 1.5)
        line_val = round(pts_sum - 0.5, 1)
        if line_val < 0:
            line_val = 1.5
        team_expected_lines[team] = line_val

    # SDDREQ-138: Constructor Expected Highest Score (uses same unified points calculations)
    highest_scoring_team = max(team_points_calc.keys(), key=lambda t: (team_points_calc[t], team_total_projections.get(t, 0))) if team_points_calc else "None"
    highest_expected_points = team_points_calc.get(highest_scoring_team, 0)

    # 5. SDDREQ-134: Dashed Line Constructor Projection Graph Data
    # Calculate cumulative points for completed races
    cum_totals = {t: 0.0 for t in teams}
    line_chart_data = []

    start_point = {"race": "Start"}
    for t in teams:
        start_point[f"{t}_actual"] = 0.0
        start_point[f"{t}_projected"] = 0.0
    line_chart_data.append(start_point)

    for r in completed_races:
        p_col = f"{r}Points"
        pt = {"race": r}
        for t in teams:
            t_df = df_season_clean[df_season_clean["Team"] == t]
            r_pts = pd.to_numeric(t_df[p_col], errors="coerce").fillna(0).sum() if p_col in t_df.columns else 0.0
            cum_totals[t] += float(r_pts)
            pt[f"{t}_actual"] = round(cum_totals[t], 1)
        line_chart_data.append(pt)

    # If there are completed races, bridge actual to projected on the last completed race
    if completed_races:
        for t in teams:
            line_chart_data[-1][f"{t}_projected"] = line_chart_data[-1].get(f"{t}_actual", 0.0)

    # Project upcoming races
    proj_cum_totals = {t: cum_totals[t] for t in teams}
    for r in upcoming_races:
        pt = {"race": f"{r}*"}  # Asterisk indicates projected
        # Calculate expected points for that specific track
        r_track = _extract_track_name(r)
        r_is_sprint = "sprint" in r.lower()

        r_driver_ratings = {d: _get_driver_track_rating(d, r_track) for d in all_drivers}
        r_driver_scores = {}
        for d in all_drivers:
            d_team = driver_to_team.get(d, "")
            pr_f = team_pr_factor.get(d_team, 0.5)
            r_driver_scores[d] = (r_driver_ratings.get(d, 10.0) / 100.0) * TRACK_WEIGHT + (pr_f * PR_WEIGHT)

        r_sorted_drivers = sorted(all_drivers, key=lambda d: r_driver_scores.get(d, 0.0), reverse=True)
        r_driver_pts = {}
        for idx, d in enumerate(r_sorted_drivers):
            pts = F1_POINTS[idx] if idx < len(F1_POINTS) else 0
            if r_is_sprint:
                pts += SPRINT_POINTS[idx] if idx < len(SPRINT_POINTS) else 0
            r_driver_pts[d] = pts

        for t in teams:
            d_list = team_to_drivers.get(t, [])
            team_pts = sum(r_driver_pts.get(d, 0) for d in d_list)
            proj_cum_totals[t] += float(team_pts)
            pt[f"{t}_projected"] = round(proj_cum_totals[t], 1)
        line_chart_data.append(pt)

    # 6. SDDREQ-151: Save Previous Lines to JSON
    lines_record = {
        "season": season_num,
        "next_race": next_race,
        "next_main_race": next_main_race,
        "expected_winner": expected_winner_team,
        "expected_winner_prob": round(expected_winner_score * 100, 1),
        "expected_highest_score_team": highest_scoring_team,
        "expected_highest_score_pts": highest_expected_points,
        "expected_podium": expected_podium_teams,
        "expected_points_lines": team_expected_lines,
    }

    try:
        all_lines = {}
        if PROJECTIONS_JSON.exists():
            with open(PROJECTIONS_JSON, "r", encoding="utf-8") as f:
                all_lines = json.load(f)
        s_key = str(season_num)
        if s_key not in all_lines:
            all_lines[s_key] = {}
        all_lines[s_key][next_race] = lines_record
        with open(PROJECTIONS_JSON, "w", encoding="utf-8") as f:
            json.dump(all_lines, f, indent=2)
    except Exception as e:
        print(f"Error persisting projections lines: {e}")

    result = {
        "season": season_num,
        "next_race": next_race,
        "next_main_race": next_main_race,
        "completed_races": completed_races,
        "upcoming_races": upcoming_races,
        "teams": teams,
        "team_track_ratings": team_track_ratings,
        "team_total_projections": team_total_projections,
        "expected_winner": expected_winner_team,
        "expected_winner_score": expected_winner_score,
        "expected_highest_score_team": highest_scoring_team,
        "highest_expected_points": highest_expected_points,
        "team_points_calc": team_points_calc,
        "expected_podium": expected_podium_teams,
        "team_expected_lines": team_expected_lines,
        "line_chart_data": line_chart_data,
        "lines_record": lines_record,
    }

    _PROJECTIONS_CACHE[cache_key] = result
    _PROJECTIONS_MTIME = curr_mtime
    return result


class ProjectionsState(rx.State):
    """Reflex state for the Projections Tab."""
    active_season: int = 5

    @rx.var
    def projections_data(self) -> dict:
        return compute_season_projections(self.active_season)

    @rx.var
    def next_race_name(self) -> str:
        data = self.projections_data
        return data.get("next_race", "Next Race")

    @rx.var
    def expected_winner(self) -> str:
        data = self.projections_data
        return data.get("expected_winner", "—")

    @rx.var
    def expected_highest_score_team(self) -> str:
        data = self.projections_data
        return data.get("expected_highest_score_team", "—")

    @rx.var
    def expected_highest_pts(self) -> int:
        data = self.projections_data
        return data.get("highest_expected_points", 0)

    @rx.var
    def expected_podium(self) -> list[str]:
        data = self.projections_data
        return data.get("expected_podium", ["—", "—", "—"])

    @rx.var
    def team_lines_list(self) -> list[dict]:
        data = self.projections_data
        lines = data.get("team_expected_lines", {})
        return [{"team": t, "line": lines[t], "color": get_constructor_color(t)} for t in sorted(lines.keys())]

    @rx.var
    def line_chart_data(self) -> list[dict]:
        data = self.projections_data
        return data.get("line_chart_data", [])

    @rx.var
    def teams_list(self) -> list[str]:
        data = self.projections_data
        return data.get("teams", [])

    # Full list popout dialog state (SDDREQ-157)
    popout_open: bool = False
    popout_type: str = ""
    popout_title: str = ""

    def set_popout_open(self, val: bool):
        self.popout_open = val

    def open_popout(self, popout_type: str, season_num: int = 5):
        self.active_season = season_num
        self.popout_type = popout_type
        if popout_type == "winner":
            self.popout_title = "Full Expected Winner Probabilities"
        elif popout_type == "highest_score":
            self.popout_title = "Full Highest Scoring Team Projections"
        elif popout_type == "podium":
            self.popout_title = "Full Expected Podium Projections"
        else:
            self.popout_title = "Full Category Projections"
        self.popout_open = True

    def close_popout(self):
        self.popout_open = False

    @rx.var
    def popout_rows(self) -> list[dict]:
        proj = compute_season_projections(self.active_season)
        is_complete = proj.get("is_complete", False)
        teams = proj.get("teams", [])
        team_total_projections = proj.get("team_total_projections", {})
        team_points_calc = proj.get("team_points_calc", {})
        sorted_teams = proj.get("sorted_teams", teams)

        rows = []
        if self.popout_type == "winner":
            if is_complete:
                champion = proj.get("champion_team", "")
                for idx, team in enumerate(sorted_teams):
                    pct = 100.0 if team == champion else 0.0
                    rows.append({
                        "rank": str(idx + 1),
                        "team": team,
                        "team_color": get_constructor_color(team),
                        "metric_label": "Championship Winner",
                        "metric_val": f"{pct:.1f}%",
                        "badge_color": "#FFD700" if idx == 0 else "#00b4da",
                    })
            else:
                sorted_by_win = sorted(teams, key=lambda t: team_total_projections.get(t, 0.0), reverse=True)
                for idx, team in enumerate(sorted_by_win):
                    score = team_total_projections.get(team, 0.0)
                    pct = round(score * 100, 1)
                    rows.append({
                        "rank": str(idx + 1),
                        "team": team,
                        "team_color": get_constructor_color(team),
                        "metric_label": "Win Expectation",
                        "metric_val": f"{pct:.1f}%",
                        "badge_color": "#FFD700" if idx == 0 else "#00b4da",
                    })
        elif self.popout_type == "highest_score":
            sort_source = sorted_teams if is_complete else teams
            sorted_by_pts = sorted(sort_source, key=lambda t: (team_points_calc.get(t, 0), team_total_projections.get(t, 0.0)), reverse=True)
            for idx, team in enumerate(sorted_by_pts):
                pts = team_points_calc.get(team, 0)
                rows.append({
                    "rank": str(idx + 1),
                    "team": team,
                    "team_color": get_constructor_color(team),
                    "metric_label": "Final Points" if is_complete else "Expected Points",
                    "metric_val": f"{pts} pts",
                    "badge_color": "#FFD700" if idx == 0 else "#00b4da",
                })
        elif self.popout_type == "podium":
            if is_complete:
                podium_set = set(proj.get("expected_podium", []))
                for idx, team in enumerate(sorted_teams):
                    prob_pct = 100.0 if team in podium_set else 0.0
                    rows.append({
                        "rank": str(idx + 1),
                        "team": team,
                        "team_color": get_constructor_color(team),
                        "metric_label": "Podium Finish",
                        "metric_val": f"{prob_pct:.1f}%",
                        "badge_color": "#FFD700" if idx == 0 else ("#C0C0C0" if idx == 1 else ("#CD7F32" if idx == 2 else "#666666")),
                    })
            else:
                total_score = sum(team_total_projections.values()) if team_total_projections else 1.0
                podium_probs = {t: 0.0 for t in teams}
                if total_score > 0:
                    for t1 in teams:
                        s1 = team_total_projections.get(t1, 0.0)
                        p1 = s1 / total_score
                        podium_probs[t1] += p1
                        rem1 = total_score - s1
                        if rem1 <= 0:
                            continue
                        for t2 in teams:
                            if t2 == t1:
                                continue
                            s2 = team_total_projections.get(t2, 0.0)
                            p2 = p1 * (s2 / rem1)
                            podium_probs[t2] += p2
                            rem2 = rem1 - s2
                            if rem2 <= 0:
                                continue
                            for t3 in teams:
                                if t3 == t1 or t3 == t2:
                                    continue
                                s3 = team_total_projections.get(t3, 0.0)
                                p3 = p2 * (s3 / rem2)
                                podium_probs[t3] += p3

                sorted_by_podium = sorted(teams, key=lambda t: (podium_probs.get(t, 0.0), team_total_projections.get(t, 0.0)), reverse=True)
                for idx, team in enumerate(sorted_by_podium):
                    prob_pct = round(podium_probs.get(team, 0.0) * 100, 1)
                    rows.append({
                        "rank": str(idx + 1),
                        "team": team,
                        "team_color": get_constructor_color(team),
                        "metric_label": "Podium Probability",
                        "metric_val": f"{prob_pct:.1f}%",
                        "badge_color": "#FFD700" if idx == 0 else ("#C0C0C0" if idx == 1 else ("#CD7F32" if idx == 2 else "#666666")),
                    })
        return rows


# ── UI Components (SDDREQ-152, SDDREQ-157) ────────────────────────────────────
def _full_list_popout_dialog() -> rx.Component:
    """Dialog displaying the full calculated list for next race (SDDREQ-157)."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.close(
                rx.button(
                    rx.icon("x", size=16),
                    variant="ghost",
                    color="#AAAAAA",
                    position="absolute",
                    top="14px",
                    right="14px",
                    _hover={"bg": "rgba(255,255,255,0.1)", "color": "white"},
                    cursor="pointer",
                    on_click=ProjectionsState.close_popout,
                ),
            ),
            rx.dialog.title(ProjectionsState.popout_title, font_family="Outfit", font_weight="800", color="white", padding_right="28px"),
            rx.dialog.description(
                "Full ranked constructor projection scores and metrics calculated for ",
                rx.text(ProjectionsState.next_race_name, as_="span", color="#00b4da", font_weight="700"),
                ".",
                color="#A0A0AA",
                font_size="xs",
                margin_bottom="3",
            ),
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("RANK", color="#00b4da", font_size="10px", font_weight="800"),
                            rx.table.column_header_cell("CONSTRUCTOR", color="#00b4da", font_size="10px", font_weight="800"),
                            rx.table.column_header_cell("SCORE / METRIC", color="#00b4da", font_size="10px", font_weight="800"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            ProjectionsState.popout_rows,
                            lambda r: rx.table.row(
                                rx.table.cell(
                                    rx.badge(
                                        r["rank"],
                                        bg="rgba(0,180,218,0.15)",
                                        color=r["badge_color"],
                                        border="1px solid rgba(255,255,255,0.1)",
                                        font_size="10px",
                                        font_weight="800",
                                        width="20px",
                                        justify="center",
                                    )
                                ),
                                rx.table.cell(
                                    rx.hstack(
                                        rx.box(width="4px", height="16px", bg=r["team_color"], border_radius="full"),
                                        rx.text(r["team"], color="white", font_weight="700", font_size="xs"),
                                        spacing="2",
                                        align="center",
                                    )
                                ),
                                rx.table.cell(
                                    rx.badge(
                                        r["metric_val"],
                                        bg="rgba(255,255,255,0.06)",
                                        color="white",
                                        font_weight="800",
                                        font_size="xs",
                                    )
                                ),
                                _hover={"bg": "#1F1F29"},
                            )
                        )
                    ),
                    variant="ghost",
                    width="100%",
                ),
                max_height="360px",
                overflow_y="auto",
                margin_y="2",
            ),
            position="relative",
            bg="#15151A",
            border="1px solid #2C2C32",
            border_radius="2xl",
            box_shadow="0 8px 24px rgba(0,0,0,0.4)",
            padding=["16px", "20px", "24px"],
            max_width="480px",
        ),
        open=ProjectionsState.popout_open,
        on_open_change=ProjectionsState.set_popout_open,
    )


def _stat_box(title: str, value_content: rx.Component | str, subtext: str, badge_color: str, icon_name: str, popout_type: str = "", season_num: int = 5) -> rx.Component:
    """Card layout matching the Map feature right-hand panel styling."""
    val_node = (
        value_content
        if isinstance(value_content, rx.Component)
        else rx.text(str(value_content), font_size=["18px", "20px"], font_weight="900", color="white", font_family="Outfit")
    )
    popout_btn = rx.cond(
        popout_type != "",
        rx.button(
            rx.hstack(
                rx.icon("maximize-2", size=11),
                rx.text("Full List", font_size="10px", font_weight="700"),
                spacing="1",
                align="center",
            ),
            size="1",
            variant="surface",
            color_scheme="cyan",
            cursor="pointer",
            on_click=lambda: ProjectionsState.open_popout(popout_type, season_num),
        ),
        rx.fragment(),
    )
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon(icon_name, size=16, color=badge_color),
                    rx.text(title, font_size="11px", color="#A0A0AA", font_weight="700", letter_spacing="0.05em", text_transform="uppercase"),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                popout_btn,
                width="100%",
                align="center",
            ),
            val_node,
            rx.text(subtext, font_size="11px", color="#00b4da", font_weight="600"),
            spacing="1",
            align_items="start",
        ),
        bg="#18181C",
        border="1px solid #2D2D35",
        border_radius="xl",
        padding="12px 14px",
        box_shadow="0 6px 18px rgba(0,0,0,0.35)",
        flex="1",
        min_width=["100%", "220px"],
    )


def projections_tab_view(season_num: int = 5) -> rx.Component:
    """Renders the complete Projections Tab per SDDREQ-152."""
    if not isinstance(season_num, int):
        try:
            season_num = int(season_num)
        except Exception:
            season_num = 5
    data = compute_season_projections(season_num)
    teams = data.get("teams", [])
    team_lines = data.get("team_expected_lines", {})
    chart_data = data.get("line_chart_data", [])

    is_complete = data.get("is_complete", False)
    champion_driver = data.get("champion_driver", "")
    sorted_teams = data.get("sorted_teams", sorted(teams))

    # Dynamic x-axis height
    max_label_len = max([len(str(p.get("race", ""))) for p in chart_data] or [4])
    axis_height = max(40, max_label_len * 5 + 15)

    # 1. Metric Boxes Row (SDDREQ-136, 138, 139, 140, 152, SDDREQ-157)
    podium_teams = data.get("expected_podium", ["—", "—", "—"])

    def _team_pill(team: str, font_size: str = "18px") -> rx.Component:
        if not team or team == "—":
            return rx.text("—", font_size=font_size, color="white", font_weight="900")
        return rx.hstack(
            rx.box(width="4px", height="18px", bg=get_constructor_color(team), border_radius="full", flex_shrink="0"),
            rx.text(team, font_size=font_size, font_weight="900", color="white", font_family="Outfit"),
            align="center",
            spacing="2",
        )

    def _podium_pill(medal: str, team: str) -> rx.Component:
        if not team or team == "—":
            return rx.text("—", font_size="13px", color="white")
        return rx.hstack(
            rx.text(medal, font_size="14px", line_height="1"),
            rx.box(width="3px", height="14px", bg=get_constructor_color(team), border_radius="full", flex_shrink="0"),
            rx.text(team, font_size=["12px", "13px"], font_weight="800", color="white", font_family="Outfit", white_space="nowrap"),
            align="center",
            spacing="1",
        )

    podium_content = (
        rx.flex(
            _podium_pill("🥇", podium_teams[0]),
            _podium_pill("🥈", podium_teams[1]),
            _podium_pill("🥉", podium_teams[2]),
            align="center",
            wrap="wrap",
            gap="8px",
        )
        if len(podium_teams) >= 3 and podium_teams[0] != "—"
        else rx.text("—", font_size="18px", color="white")
    )

    winner_team = data.get("expected_winner", "—")
    winner_prob = round(data.get("expected_winner_score", 0.0) * 100, 1)

    highest_team = data.get("expected_highest_score_team", "—")
    highest_pts = data.get("highest_expected_points", 0)

    winner_node = _team_pill(winner_team, font_size="18px")
    highest_node = _team_pill(highest_team, font_size="18px")

    if is_complete:
        stat_cards_row = rx.flex(
            _stat_box("Season Champion", winner_node, f"Constructors Champion ({champion_driver} WDC)" if champion_driver else "Constructors Champion", "#FFD700", "trophy", popout_type="winner", season_num=season_num),
            _stat_box("Highest Scoring Team", highest_node, f"Final Score: {highest_pts} pts", "#00b4da", "award", popout_type="highest_score", season_num=season_num),
            _stat_box("Final Podium", podium_content, "Final Championship Standings", "#CD7F32", "flag", popout_type="podium", season_num=season_num),
            direction={"initial": "column", "sm": "row"},
            width="100%",
            spacing="3",
            wrap="wrap",
        )
    else:
        stat_cards_row = rx.flex(
            _stat_box("Expected Winner", winner_node, f"Projection Factor: {winner_prob:.1f}%", "#FFD700", "trophy", popout_type="winner", season_num=season_num),
            _stat_box("Highest Scoring Team", highest_node, f"Expected Score: {highest_pts} pts", "#00b4da", "award", popout_type="highest_score", season_num=season_num),
            _stat_box("Expected Podium", podium_content, f"For {data.get('next_main_race', 'Upcoming Race')}", "#CD7F32", "flag", popout_type="podium", season_num=season_num),
            direction={"initial": "column", "sm": "row"},
            width="100%",
            spacing="3",
            wrap="wrap",
        )

    # Expected Points Lines Grid / Final Standings Grid (SDDREQ-140)
    teams_to_show = sorted_teams if is_complete else sorted(teams)
    grid_title = "Constructor Final Standings & Points" if is_complete else "Constructor Expected Points Lines (Over / Under)"
    grid_badge = "Final Results" if is_complete else f"Race: {data.get('next_main_race', data.get('next_race', 'Upcoming'))}"

    lines_grid = rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("activity", size=15, color="#00b4da"),
                rx.text(grid_title, font_size="12px", font_weight="800", color="white", letter_spacing="0.04em", text_transform="uppercase"),
                rx.spacer(),
                rx.text(grid_badge, font_size="11px", color="#888888", font_weight="600"),
                width="100%",
                align="center",
            ),
            rx.grid(
                *[
                    rx.box(
                        rx.hstack(
                            rx.box(width="4px", height="24px", bg=get_constructor_color(t), border_radius="full", flex_shrink="0"),
                            rx.vstack(
                                rx.text(f"#{idx+1} {t}" if is_complete else t, font_size="11px", font_weight="700", color="white", white_space="nowrap"),
                                rx.text(f"Total: {team_lines.get(t, 0.0):.0f} pts" if is_complete else f"Line: {1.5 if team_lines.get(t, 1.5) < 0 else team_lines.get(t, 1.5)} pts", font_size="10px", color="#AAAAAA", font_weight="600"),
                                spacing="0",
                                align_items="start",
                            ),
                            align="center",
                            spacing="2",
                        ),
                        bg="#15151A",
                        border="1px solid #28282E",
                        border_radius="lg",
                        padding="6px 10px",
                    )
                    for idx, t in enumerate(teams_to_show)
                ],
                columns={"initial": "2", "sm": "4", "md": "4"},
                spacing="2",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        bg="#18181C",
        border="1px solid #2D2D35",
        border_radius="xl",
        padding="12px 14px",
        width="100%",
        box_shadow="0 6px 18px rgba(0,0,0,0.35)",
    )

    # 2. Dashed Line Constructor Projection Chart (SDDREQ-134)
    chart_lines = []
    for t in teams:
        c_color = get_constructor_color(t)
        # Solid line for actual completed races
        chart_lines.append(
            rx.recharts.line(
                data_key=f"{t}_actual",
                stroke=c_color,
                stroke_width=2.2,
                dot={"fill": c_color, "stroke": c_color, "r": 3},
                name=f"{t}" if is_complete else f"{t} (Actual)",
                type_="monotone",
            )
        )
        if not is_complete:
            # Dashed line for projected upcoming races
            chart_lines.append(
                rx.recharts.line(
                    data_key=f"{t}_projected",
                    stroke=c_color,
                    stroke_width=2.0,
                    stroke_dasharray="5 5",
                    dot={"fill": c_color, "stroke": c_color, "r": 2},
                    name=f"{t} (Projected)",
                    type_="monotone",
                )
            )

    chart_title = (
        f"Season {season_num} Final Results"
        if is_complete
        else f"Projected Season {season_num} Final Results"
    )

    projections_line_chart = zoomable_chart(
        lambda h: rx.recharts.line_chart(
            *chart_lines,
            rx.recharts.x_axis(data_key="race", font_size=8, angle=-90, height=axis_height, stroke="white", text_anchor="end", interval=0, tick={"dx": -5}),
            rx.recharts.y_axis(
                stroke="white",
                width=35,
                tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
            ),
            rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.15)"),
            data=chart_data,
            margin={"top": 10, "right": 20, "left": 35, "bottom": 30},
            width="100%",
            height=h,
        ),
        title=chart_title,
        chart_id="constructor_projections_line_chart",
        height=380,
        large_height=480,
        download_position="top_right",
    )

    legend_items = [(t, get_constructor_color(t)) for t in teams]
    projections_legend_expander = interactive_line_chart_key(
        chart_id="constructor_projections_line_chart",
        items=legend_items,
        title="Constructor Key",
        hint="Click constructor to highlight line",
    )

    header_title = f"Results: Season {season_num}" if is_complete else f"Projections: Season {season_num}"
    header_badge = (
        rx.badge("Final Season Results", bg="rgba(60, 180, 75, 0.15)", color="#3cb44b", border="1px solid rgba(60, 180, 75, 0.3)", border_radius="full", font_size="11px", padding_x="3")
        if is_complete
        else rx.badge("Dashed: Projected Future Races", bg="rgba(0, 180, 218, 0.15)", color="#00b4da", border="1px solid rgba(0, 180, 218, 0.3)", border_radius="full", font_size="11px", padding_x="3")
    )

    return rx.vstack(
        rx.hstack(
            rx.heading(
                header_title,
                size="6",
                color="white",
                font_family="Outfit",
            ),
            rx.spacer(),
            header_badge,
            width="100%",
            align="center",
            margin_bottom="3",
        ),
        stat_cards_row,
        lines_grid,
        chart_card(
            title=chart_title,
            chart_component=projections_line_chart,
            chart_id="constructor_projections_line_chart",
            download_position="top_right",
            icon="trending-up",
            extra_content=projections_legend_expander,
            border_radius="xl",
            box_shadow="0 6px 18px rgba(0,0,0,0.35)",
            margin_bottom="2",
        ),
        _full_list_popout_dialog(),
        width="100%",
        spacing="3",
        align_items="start",
    )
