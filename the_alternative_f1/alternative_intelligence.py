"""Alternative Intelligence: Analytical AI-powered search and assistant for The Alternative F1.

Strictly grounded exclusively on data from the deployed version of the application.
Adheres to Jama specifications:
- TAF1APP-SDDFEAT-26: Alternative Intelligence - Gemini Search
- TAF1APP-SDDREQ-228: DEFINITION: Alternative Intelligence
- TAF1APP-SDDREQ-229: DEFINITION: Grounded League Context
- TAF1APP-SDDREQ-230 to SDDREQ-245: Functional requirements
"""

import os
import re
import json
import time
import httpx
from pathlib import Path
from typing import AsyncGenerator
from pydantic import BaseModel
import reflex as rx
from the_alternative_f1.constructor_colors import get_constructor_color

# Cache storage for grounded league context and working models
_GROUNDED_CONTEXT_CACHE = ""
_GROUNDED_CONTEXT_MTIME = 0
_CACHE_TIMESTAMP = 0
_WORKING_GEMINI_MODEL = None


def get_contrast_text_color(hex_color: str) -> str:
    """Return #000000 (black) for light/yellow colors or #FFFFFF (white) for dark colors."""
    if not hex_color:
        return "#FFFFFF"
    c = str(hex_color).strip().lower()
    if c in ("#ffea00", "yellow", "#e0e0e0", "#ffffff", "white", "#ffcc00", "#ffd700", "#fd4bc7"):
        return "#000000"
    if c.startswith("#") and len(c) == 7:
        try:
            r = int(c[1:3], 16)
            g = int(c[3:5], 16)
            b = int(c[5:7], 16)
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum > 165:
                return "#000000"
        except Exception:
            pass
    return "#FFFFFF"


def get_driver_most_recent_constructor(driver_name: str) -> tuple[str, str]:
    """Retrieve the most recent constructor and color for a driver across official seasons."""
    if not driver_name:
        return "Independent", "#555555"
    d_clean = driver_name.strip().lower()
    try:
        from the_alternative_f1.seasons import seasons
        from the_alternative_f1.seasons.Calculations import Calculations
        for s in reversed(seasons):
            calc = Calculations(s)
            raw_df = calc.get("df")
            if raw_df is not None and not raw_df.empty:
                for _, r in raw_df.iterrows():
                    d = str(r.get("Driver", "")).strip()
                    if d.lower() == d_clean or d_clean in d.lower():
                        team = str(r.get("Team", "")).strip()
                        if team:
                            return team, get_constructor_color(team)
    except Exception:
        pass
    return "Independent", "#555555"


def compute_h2h_battle_stats(entity1: str, entity2: str, is_constructor: bool = False, seasons_filter=None) -> dict:
    """Deterministically compute Head-to-Head battle statistics across official league race records."""
    e1_clean = entity1.strip().lower()
    e2_clean = entity2.strip().lower()

    qual1, qual2 = 0, 0
    race1, race2 = 0, 0
    pod1, pod2 = 0, 0
    pts1, pts2 = 0.0, 0.0
    win1, win2 = 0, 0

    try:
        from the_alternative_f1.seasons import seasons
        from the_alternative_f1.seasons.Calculations import Calculations

        target_seasons = seasons
        if seasons_filter:
            target_seasons = [s for s in seasons if s.get("season_number") in seasons_filter]

        for s in target_seasons:
            calc = Calculations(s)
            df = calc.get("df")
            races = calc.get("races", [])
            index_x = calc.get("index_x", 0)
            num_completed = max(0, int(index_x + 0.5))

            if df is None or df.empty:
                continue

            if is_constructor:
                c1_rows = df[df["Team"].str.strip().str.lower() == e1_clean]
                c2_rows = df[df["Team"].str.strip().str.lower() == e2_clean]
                if c1_rows.empty and c2_rows.empty:
                    continue
                c_totals = calc.get("constructor_totals")
                if c_totals is not None and not c_totals.empty:
                    for _, r in c_totals.iterrows():
                        t = str(r.get("Team", "")).strip().lower()
                        p = float(r.get("Points", 0))
                        if t == e1_clean:
                            pts1 += p
                        elif t == e2_clean:
                            pts2 += p
                for r_name in races[:num_completed]:
                    c_pre = r_name.replace(" Sprint", "Sprint")
                    p_col = f"{c_pre}Place"
                    if p_col in df.columns:
                        w_rows = df[df[p_col] == 1]
                        if not w_rows.empty:
                            w_t = str(w_rows.iloc[0].get("Team", "")).strip().lower()
                            if w_t == e1_clean:
                                win1 += 1
                            elif w_t == e2_clean:
                                win2 += 1
                        for _, pod_row in df[df[p_col].isin([1, 2, 3])].iterrows():
                            pod_t = str(pod_row.get("Team", "")).strip().lower()
                            if pod_t == e1_clean:
                                pod1 += 1
                            elif pod_t == e2_clean:
                                pod2 += 1
            else:
                d1_row = df[df["Driver"].str.strip().str.lower() == e1_clean]
                d2_row = df[df["Driver"].str.strip().str.lower() == e2_clean]
                if d1_row.empty:
                    d1_row = df[df["Driver"].str.strip().str.lower().str.contains(e1_clean, regex=False)]
                if d2_row.empty:
                    d2_row = df[df["Driver"].str.strip().str.lower().str.contains(e2_clean, regex=False)]

                has_d1 = not d1_row.empty
                has_d2 = not d2_row.empty

                d_totals = calc.get("driver_totals")
                if d_totals is not None and not d_totals.empty:
                    for _, r in d_totals.iterrows():
                        d_name = str(r.get("Driver", "")).strip().lower()
                        p_val = float(r.get("Points", 0))
                        if d_name == e1_clean or (has_d1 and d_name in d1_row.iloc[0]["Driver"].strip().lower()):
                            pts1 += p_val
                        elif d_name == e2_clean or (has_d2 and d_name in d2_row.iloc[0]["Driver"].strip().lower()):
                            pts2 += p_val

                if not has_d1 or not has_d2:
                    continue

                d1_data = d1_row.iloc[0]
                d2_data = d2_row.iloc[0]

                for r_name in races[:num_completed]:
                    c_pre = r_name.replace(" Sprint", "Sprint")
                    q_col = f"{c_pre}Qualifying"
                    p_col = f"{c_pre}Place"

                    if q_col in df.columns:
                        try:
                            q1_val = float(d1_data.get(q_col))
                            q2_val = float(d2_data.get(q_col))
                            if q1_val > 0 and q2_val > 0:
                                if q1_val < q2_val:
                                    qual1 += 1
                                elif q2_val < q1_val:
                                    qual2 += 1
                        except Exception:
                            pass

                    if p_col in df.columns:
                        try:
                            p1_val = float(d1_data.get(p_col))
                            p2_val = float(d2_data.get(p_col))
                            if p1_val > 0 and p2_val > 0:
                                if p1_val < p2_val:
                                    race1 += 1
                                elif p2_val < p1_val:
                                    race2 += 1
                                if p1_val == 1:
                                    win1 += 1
                                if p2_val == 1:
                                    win2 += 1
                                if p1_val in (1, 2, 3):
                                    pod1 += 1
                                if p2_val in (1, 2, 3):
                                    pod2 += 1
                        except Exception:
                            pass

        pts1_str = f"{pts1:.0f}" if pts1.is_integer() else f"{pts1:.1f}"
        pts2_str = f"{pts2:.0f}" if pts2.is_integer() else f"{pts2:.1f}"

        return {
            "qual1": qual1,
            "qual2": qual2,
            "race1": race1,
            "race2": race2,
            "pod1": pod1,
            "pod2": pod2,
            "pts1": pts1_str,
            "pts2": pts2_str,
            "win1": win1,
            "win2": win2,
        }
    except Exception:
        return {
            "qual1": qual1, "qual2": qual2,
            "race1": race1, "race2": race2,
            "pod1": pod1, "pod2": pod2,
            "pts1": str(pts1), "pts2": str(pts2),
            "win1": win1, "win2": win2,
        }


def compute_champion_campaign_stats(season_num: int = 4, entity_name: str = "", is_constructor: bool = True) -> dict:
    """Deterministically compute championship campaign statistics for an entity in a given season (TAF1APP-SDDREQ-250)."""
    try:
        from the_alternative_f1.seasons import seasons
        from the_alternative_f1.seasons.Calculations import Calculations

        target_season = next((s for s in seasons if s.get("season_number") == season_num), None)
        if target_season is None:
            target_season = seasons[-2]  # Default to season 4 (most recent completed)

        calc = Calculations(target_season)
        df = calc.get("df")
        trt = calc.get("team_race_totals") if is_constructor else calc.get("driver_race_totals")
        idx_x = int(calc.get("index_x", 0) + 0.5)
        races = calc.get("races", [])[:idx_x]
        tot = calc.get("constructor_totals") if is_constructor else calc.get("driver_totals")
        key_col = "Team" if is_constructor else "Driver"

        row_idx = 0
        if entity_name and tot is not None and not tot.empty:
            e_clean = entity_name.strip().lower()
            m = tot[tot[key_col].str.strip().str.lower() == e_clean]
            if m.empty:
                m = tot[tot[key_col].str.strip().str.lower().str.contains(e_clean, regex=False)]
            if not m.empty:
                row_idx = m.index[0]

        if tot is None or tot.empty:
            return {
                "name": entity_name or "Champion",
                "season": f"Season {season_num}",
                "is_constructor": is_constructor,
                "team": entity_name if is_constructor else "",
                "color": "#00b4da",
                "text_color": "#ffffff",
                "points": 0.0,
                "runner_up": "None",
                "margin": 0.0,
                "wins": 0,
                "podiums": 0,
                "poles": 0,
                "fl": 0,
                "cd": 0,
                "dotd": 0,
                "mot": 0,
                "total_accolades": 0,
                "races_led": 0,
                "total_races": len(races),
            }

        champ_name = str(tot.iloc[row_idx][key_col]).strip()
        pts = float(tot.iloc[row_idx]["Points"])

        if row_idx == 0:
            runner_up = str(tot.iloc[1][key_col]).strip() if len(tot) > 1 else "None"
            runner_up_pts = float(tot.iloc[1]["Points"]) if len(tot) > 1 else 0.0
            margin = pts - runner_up_pts
        else:
            runner_up = str(tot.iloc[0][key_col]).strip()
            margin = float(tot.iloc[0]["Points"]) - pts

        if is_constructor:
            color = get_constructor_color(champ_name)
            team_label = champ_name
        else:
            team_label, color = get_driver_most_recent_constructor(champ_name)
        text_color = get_contrast_text_color(color)

        wins, pods, poles, fl, cd, dotd, mot = 0, 0, 0, 0, 0, 0, 0
        e_clean = champ_name.strip().lower()

        if df is not None and not df.empty:
            for r in races:
                c_pre = r.replace(" Sprint", "Sprint")
                p_c = f"{c_pre}Place"
                q_c = f"{c_pre}Qualifying"
                fl_c = f"{c_pre}FastestLap"
                cd_c = f"{c_pre}CD"
                dotd_c = f"{c_pre}DOTD"
                mot_c = f"{c_pre}MOT"

                m_rows = df[df[key_col].str.strip().str.lower() == e_clean]
                for _, row in m_rows.iterrows():
                    if p_c in df.columns:
                        try:
                            p_v = float(row.get(p_c, 0))
                            if p_v == 1:
                                wins += 1
                            if p_v in (1, 2, 3):
                                pods += 1
                        except Exception:
                            pass
                    if q_c in df.columns:
                        try:
                            if float(row.get(q_c, 0)) == 1:
                                poles += 1
                        except Exception:
                            pass
                    if fl_c in df.columns and str(row.get(fl_c, "")).strip().lower() in ("y", "1", "true"):
                        fl += 1
                    if cd_c in df.columns and str(row.get(cd_c, "")).strip().lower() in ("y", "1", "true"):
                        cd += 1
                    if dotd_c in df.columns and str(row.get(dotd_c, "")).strip().lower() in ("y", "1", "true"):
                        dotd += 1
                    if mot_c in df.columns and str(row.get(mot_c, "")).strip().lower() in ("y", "1", "true"):
                        mot += 1

        races_led = 0
        if trt is not None and not trt.empty:
            for col in list(trt.columns)[:idx_x]:
                try:
                    lead = str(trt[col].idxmax()).strip().lower()
                    if lead == e_clean:
                        races_led += 1
                except Exception:
                    pass

        return {
            "name": champ_name,
            "season": f"Season {season_num}",
            "is_constructor": is_constructor,
            "team": team_label,
            "color": color,
            "text_color": text_color,
            "points": pts,
            "runner_up": runner_up,
            "margin": margin,
            "wins": wins,
            "podiums": pods,
            "poles": poles,
            "fl": fl,
            "cd": cd,
            "dotd": dotd,
            "mot": mot,
            "total_accolades": poles + fl + cd + dotd + mot,
            "races_led": races_led,
            "total_races": len(races),
        }
    except Exception:
        return {
            "name": entity_name or "Champion",
            "season": f"Season {season_num}",
            "is_constructor": is_constructor,
            "team": entity_name if is_constructor else "",
            "color": "#00b4da",
            "text_color": "#ffffff",
            "points": 0.0,
            "runner_up": "None",
            "margin": 0.0,
            "wins": 0,
            "podiums": 0,
            "poles": 0,
            "fl": 0,
            "cd": 0,
            "dotd": 0,
            "mot": 0,
            "total_accolades": 0,
            "races_led": 0,
            "total_races": 0,
        }


def format_all_season_articles() -> list[str]:
    """Format all published editorial articles across all seasons for grounded context."""
    lines = []
    lines.append("## COMPLETE LEAGUE EDITORIAL NEWS & ARTICLES ARCHIVE (ALL SEASONS)")
    lines.append(
        "This archive contains all official editorial articles, race recaps, race week previews, "
        "and investigative reports published in the league. You can answer questions about who wrote articles, "
        "what article covered specific races, driver milestones, drama, and awards.\n"
    )

    try:
        from the_alternative_f1.seasons import seasons
        for s in seasons:
            s_num = s.get("season_number")
            arts = s.get("articles", [])
            if not arts:
                continue
            lines.append(f"### Season {s_num} Published Articles ({len(arts)} Articles):")
            for a in arts:
                title = str(a.get("title", "")).strip()
                date_str = str(a.get("date", "")).strip()
                author = str(a.get("author", "")).strip()
                blurb = str(a.get("blurb", "")).strip()

                # Extract textual narrative excerpts from content if available
                content_excerpts = []
                content_raw = a.get("content", [])
                if isinstance(content_raw, list):
                    for item in content_raw:
                        if isinstance(item, str) and item.strip():
                            clean_item = " ".join(item.split())
                            content_excerpts.append(clean_item)
                elif isinstance(content_raw, str):
                    content_excerpts.append(" ".join(content_raw.split()))

                summary_text = ""
                if content_excerpts:
                    first_text = content_excerpts[0]
                    summary_text = f" | Excerpt: \"{first_text[:220]}...\"" if len(first_text) > 220 else f" | Excerpt: \"{first_text}\""

                date_part = f"Published: {date_str}" if date_str else "Date: Not specified"
                author_part = f"by {author}" if author else ""
                lines.append(f"- **\"{title}\"** ({date_part} {author_part}): {blurb}{summary_text}")
            lines.append("")

        # Also include App Platform Launch article
        try:
            from the_alternative_f1.articles.app_intro import article as App_Intro_Article
            if App_Intro_Article:
                lines.append("### League Platform Launch Articles:")
                lines.append(f"- **\"{App_Intro_Article.get('title')}\"** ({App_Intro_Article.get('date')} by {App_Intro_Article.get('author')}): {App_Intro_Article.get('blurb')}")
                lines.append("")
        except Exception:
            pass

    except Exception as e:
        lines.append(f"Note: Error formatting articles archive: {str(e)}")

    return lines


def build_grounded_league_context() -> str:
    """Build a comprehensive, structured text summary of all deployed league data.
    
    Includes:
    - Season 5 standings, schedule, and race results
    - All-time cumulative highest positions
    - Latest power rankings
    - Historical championship summaries
    """
    global _GROUNDED_CONTEXT_CACHE, _GROUNDED_CONTEXT_MTIME, _CACHE_TIMESTAMP

    # Invalidate every 300 seconds (5 minutes)
    now = time.time()
    if _GROUNDED_CONTEXT_CACHE and (now - _CACHE_TIMESTAMP < 300):
        return _GROUNDED_CONTEXT_CACHE

    lines = []
    lines.append("# THE ALTERNATIVE F1 - OFFICIAL LEAGUE RECORDS DATABASE")
    lines.append("League: The Alternative F1 (Sim Racing League)\n")

    current_dir = Path(__file__).parent
    excel_path = current_dir / "The_Alternative_F1.xlsx"

    # 1. Ingest Season Data via Official Calculations Engine
    all_season_calcs = {}
    active_drivers = []
    active_teams = []

    def _format_season_qualifying_battles(s_number, df_data, const_totals, done_races, all_r):
        if df_data is None or df_data.empty:
            return []
        res = [f"### Season {s_number} Teammate Qualifying Head-to-Head Battles (Constructors Standings Order):"]
        try:
            team_order = [str(t).strip() for t in const_totals["Team"]] if (const_totals is not None and not const_totals.empty) else sorted(df_data["Team"].dropna().unique())
            target_races = done_races if (s_number == 5 and done_races) else all_r
            qual_cols = [f"{r.replace(' Sprint', 'Sprint')}Qualifying" for r in target_races if f"{r.replace(' Sprint', 'Sprint')}Qualifying" in df_data.columns]
            if not qual_cols:
                qual_cols = [c for c in df_data.columns if "qualifying" in c.lower()]
            rows_found = 0
            for tm in team_order:
                tm_drivers = df_data[df_data["Team"] == tm]["Driver"].dropna().unique()
                if len(tm_drivers) >= 2:
                    d1, d2 = str(tm_drivers[0]).strip(), str(tm_drivers[1]).strip()
                    d1_wins, d2_wins = 0, 0
                    for qc in qual_cols:
                        d1_q_rows = df_data[(df_data["Driver"] == d1) & (df_data["Team"] == tm)][qc]
                        d2_q_rows = df_data[(df_data["Driver"] == d2) & (df_data["Team"] == tm)][qc]
                        if not d1_q_rows.empty and not d2_q_rows.empty:
                            q1, q2 = d1_q_rows.iloc[0], d2_q_rows.iloc[0]
                            try:
                                q1_f, q2_f = float(q1), float(q2)
                                if q1_f > 0 and q2_f > 0:
                                    if q1_f < q2_f:
                                        d1_wins += 1
                                    elif q2_f < q1_f:
                                        d2_wins += 1
                            except Exception:
                                pass
                    res.append(f"- {tm}: {d1} ({d1_wins}) vs. {d2} ({d2_wins}) [Across {len(qual_cols)} qualifying sessions]")
                    rows_found += 1
            if rows_found > 0:
                res.append("")
                return res
            return []
        except Exception as e:
            return [f"Note: Error calculating Season {s_number} qualifying battles: {str(e)}\n"]

    try:
        from the_alternative_f1.seasons import seasons, LATEST_SEASON
        from the_alternative_f1.seasons.Calculations import Calculations
        from the_alternative_f1.seasons.projections import _get_driver_track_rating

        for s in seasons:
            s_num = s.get("season_number")
            try:
                calc = Calculations(s)
                all_season_calcs[s_num] = calc
                driver_totals = calc.get("driver_totals")  # pd.DataFrame: ["Driver", "Points"]
                constructor_totals = calc.get("constructor_totals")  # pd.DataFrame: ["Team", "Points"]
                raw_df = calc.get("df")
                schedule_df = calc.get("schedule_df")
                races = calc.get("races", [])
                index_x = calc.get("index_x", 0)
                num_completed = max(0, int(index_x + 0.5))
                completed_races = races[:num_completed]

                # Map drivers to their teams
                driver_team_map = {}
                if raw_df is not None and not raw_df.empty:
                    for _, r in raw_df.iterrows():
                        d = str(r.get("Driver", "")).strip()
                        t = str(r.get("Team", "")).strip()
                        if d and d not in driver_team_map:
                            driver_team_map[d] = t

                if s_num == LATEST_SEASON:
                    lines.append(f"## ACTIVE SEASON: SEASON {s_num} (CURRENT OFFICIAL STANDINGS & STATS)")

                    # Driver Standings
                    if driver_totals is not None and not driver_totals.empty:
                        active_drivers = [str(d).strip() for d in driver_totals["Driver"]]
                        lines.append("### Season 5 Official Driver Championship Standings:")
                        for rank, (_, row) in enumerate(driver_totals.iterrows(), start=1):
                            d = str(row.get("Driver", "")).strip()
                            pts = row.get("Points", 0)
                            team = driver_team_map.get(d, "Independent")
                            badge = " [CHAMPIONSHIP LEADER]" if rank == 1 else ""
                            lines.append(f"{rank}. {d} ({team}): {pts} pts{badge}")
                        lines.append("")

                    # Constructor Standings
                    if constructor_totals is not None and not constructor_totals.empty:
                        active_teams = [str(t).strip() for t in constructor_totals["Team"]]
                        lines.append("### Season 5 Official Constructor Championship Standings:")
                        for rank, (_, row) in enumerate(constructor_totals.iterrows(), start=1):
                            team = str(row.get("Team", "")).strip()
                            pts = row.get("Points", 0)
                            badge = " [CONSTRUCTORS LEADER]" if rank == 1 else ""
                            lines.append(f"{rank}. {team}: {pts} pts{badge}")
                        lines.append("")

                    # Completed Race Results & Winners
                    if completed_races and raw_df is not None and not raw_df.empty:
                        lines.append("### Season 5 Completed Races & Winners:")
                        for race_name in completed_races:
                            col_prefix = race_name.replace(" Sprint", "Sprint")
                            place_col = f"{col_prefix}Place"
                            fl_col = f"{col_prefix}FastestLap"
                            winner_name = "Unknown"
                            winner_team = ""
                            fl_name = ""

                            if place_col in raw_df.columns:
                                winners = raw_df[raw_df[place_col] == 1]
                                if not winners.empty:
                                    winner_name = str(winners.iloc[0].get("Driver", "Unknown")).strip()
                                    winner_team = str(winners.iloc[0].get("Team", "")).strip()

                            if fl_col in raw_df.columns:
                                fl_rows = raw_df[raw_df[fl_col] == 1]
                                if not fl_rows.empty:
                                    fl_name = str(fl_rows.iloc[0].get("Driver", "")).strip()

                            fl_str = f" | Fastest Lap: {fl_name}" if fl_name else ""
                            team_str = f" ({winner_team})" if winner_team else ""
                            lines.append(f"- {race_name}: Winner: {winner_name}{team_str}{fl_str}")
                        lines.append("")

                    # Seasonal Teammate Qualifying Battles (SDDREQ-249)
                    lines.extend(_format_season_qualifying_battles(s_num, raw_df, constructor_totals, completed_races, races))

                    # Calendar & Schedule
                    if schedule_df is not None and not schedule_df.empty:
                        lines.append("### Season 5 Calendar & Schedule (Races held on Wednesdays):")
                        for _, row in schedule_df.iterrows():
                            r_name = str(row.get("Race", "")).strip()
                            r_track = str(row.get("Track", "")).strip()
                            status = str(row.get("Status", "")).strip()
                            raw_date = str(row.get("Date", "")).strip().replace(" 00:00:00", "")
                            date_str = f" (Date: {raw_date})" if raw_date and raw_date.lower() != "nan" else " (Date: Not Recorded)"
                            status_str = f" [{status}]" if status and status.lower() != "nan" else ""
                            if r_track and r_track.lower() != "nan":
                                lines.append(f"- {r_name} at {r_track}{date_str}{status_str}")
                            elif r_name and r_name.lower() != "nan":
                                lines.append(f"- {r_name}{date_str}{status_str}")
                        lines.append("")

                    # Rookies
                    rookies = s.get("rookies")
                    if rookies:
                        lines.append(f"### Season 5 Designated Rookies: {', '.join(sorted(rookies))}\n")


                else:
                    # Individual Historical Season Data
                    season_year = ""
                    if s_num in (1, 2):
                        season_year = " (Year: 2023)"
                    elif s_num == 3:
                        season_year = " (Year: 2024)"
                    lines.append(f"## SEASON {s_num}{season_year} COMPLETE HISTORICAL STANDINGS")
                    if s_num in (1, 2):
                        lines.append("Official Calendar Note: Season 1 and Season 2 occurred in 2023. Races were held on Wednesdays.")
                    elif s_num == 3:
                        lines.append("Official Calendar Note: Season 3 occurred in 2024. Races were held on Wednesdays.")
                    if driver_totals is not None and not driver_totals.empty:
                        champ = driver_totals.iloc[0]
                        lines.append(f"- Season {s_num} Champion Driver: {champ.get('Driver')} ({champ.get('Points')} pts)")
                        lines.append("Top Drivers Final Standings:")
                        for rank, (_, row) in enumerate(driver_totals.head(10).iterrows(), start=1):
                            lines.append(f"  {rank}. {row.get('Driver')}: {row.get('Points')} pts")
                    if constructor_totals is not None and not constructor_totals.empty:
                        c_champ = constructor_totals.iloc[0]
                        champ_team_name = str(c_champ.get('Team', '')).strip()
                        winning_drivers = []
                        if raw_df is not None and not raw_df.empty and "Team" in raw_df.columns:
                            t_rows = raw_df[raw_df["Team"].astype(str).str.strip() == champ_team_name]
                            for _, r in t_rows.iterrows():
                                d_name = str(r.get("Driver", "")).strip()
                                d_pts = r.get("Total", r.get("Points", 0))
                                if d_name:
                                    winning_drivers.append(f"{d_name} ({d_pts} pts)")
                        drivers_str = f" | Winning Drivers (Official Constructor Champions): {', '.join(winning_drivers)}" if winning_drivers else ""
                        lines.append(f"- Season {s_num} Champion Constructor: {champ_team_name} ({c_champ.get('Points')} pts){drivers_str}")
                    if completed_races and raw_df is not None and not raw_df.empty:
                        race_winners_s = []
                        for r_name in races:
                            c_pre = r_name.replace(" Sprint", "Sprint")
                            p_col = f"{c_pre}Place"
                            if p_col in raw_df.columns:
                                w_rows = raw_df[raw_df[p_col] == 1]
                                if not w_rows.empty:
                                    w_d = str(w_rows.iloc[0].get("Driver", "")).strip()
                                    race_winners_s.append(f"{r_name}: {w_d}")
                        if race_winners_s:
                            lines.append(f"- Race Winners: {'; '.join(race_winners_s)}")

                    # Historical Teammate Qualifying Battles (SDDREQ-249)
                    lines.extend(_format_season_qualifying_battles(s_num, raw_df, constructor_totals, completed_races, races))

                    # Historical Calendar & Schedule
                    if schedule_df is not None and not schedule_df.empty:
                        lines.append(f"### Season {s_num} Calendar & Schedule (Races held on Wednesdays):")
                        for _, row in schedule_df.iterrows():
                            r_name = str(row.get("Race", "")).strip()
                            r_track = str(row.get("Track", "")).strip()
                            status = str(row.get("Status", "")).strip()
                            raw_date = str(row.get("Date", "")).strip().replace(" 00:00:00", "")
                            date_str = f" (Date: {raw_date})" if raw_date and raw_date.lower() != "nan" else " (Date: Not Recorded)"
                            status_str = f" [{status}]" if status and status.lower() != "nan" else ""
                            if r_track and r_track.lower() != "nan":
                                lines.append(f"- {r_name} at {r_track}{date_str}{status_str}")
                            elif r_name and r_name.lower() != "nan":
                                lines.append(f"- {r_name}{date_str}{status_str}")
                        lines.append("")
                    lines.append("")

            except Exception as e:
                lines.append(f"Note: Error loading Season {s_num}: {str(e)}")

    except Exception as e:
        lines.append(f"Note: Error initializing Seasons engine: {str(e)}")

    # 2. Per-Track Driver Statistical Ratings (SDDREQ-76 & Projections)
    try:
        from the_alternative_f1.seasons.projections import _get_driver_track_rating
        lines.append("## OFFICIAL PER-TRACK DRIVER STATISTICAL RATINGS (SCALE 0 - 100)")
        lines.append(
            "Formula (SDDREQ-76): (((average points scored / 30) * 0.6) + ((0.99 / qualifying position) * 0.2) + ((positions gained/lost / 22) * 0.2)) * 100\n"
            "This metric measures each driver's historical statistical efficiency and performance specifically for each circuit.\n"
        )
        tracks_to_compute = [
            "Spa", "Monza", "Australia", "Imola", "Miami", "Brazil",
            "Silverstone", "Suzuka", "Qatar", "COTA", "Mexico", "Las Vegas", "Abu Dhabi",
            "Bahrain", "Jeddah", "Spain", "Canada", "Austria", "Zandvoort", "Singapore"
        ]

        if not active_drivers:
            active_drivers = ["Josh", "Jairo", "Joshua", "Jaden", "Nick", "Eddie", "Del", "Patrick", "Matthew", "Brently", "Grayson", "Josh C.", "Boz", "Evelo", "Leo", "Randy"]

        for track_name in tracks_to_compute:
            ratings = []
            for d in active_drivers:
                score = _get_driver_track_rating(d, track_name)
                ratings.append((d, score))
            ratings.sort(key=lambda x: x[1], reverse=True)
            formatted_ratings = [f"{d}: {s:.1f}" for d, s in ratings]
            lines.append(f"### Track: {track_name}")
            lines.append(f"- Driver Track Ratings (Best to Worst): {', '.join(formatted_ratings)}")
        lines.append("")
    except Exception as e:
        lines.append(f"Note: Error generating track ratings: {str(e)}")

    # 3. All-Time League Career Records (Drivers & Constructors)
    try:
        from the_alternative_f1.all_time_stats.Functions import CalculateAllTime
        all_time_drivers = CalculateAllTime(5, "Driver")
        if all_time_drivers is not None and not all_time_drivers.empty:
            lines.append("## ALL-TIME LEAGUE DRIVER CAREER RECORDS (ALL SEASONS CUMULATIVE)")
            lines.append("| Rank | Driver | Career Points | Wins (1st) | 2nd | 3rd | Podiums | Championships | Highest Rank | Single Season Win Streak |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            for _, r in all_time_drivers.iterrows():
                rank = r.get("Place", "")
                d = r.get("Driver", "")
                pts = r.get("Points", 0)
                w = r.get("1st Place", 0)
                p2 = r.get("2nd Place", 0)
                p3 = r.get("3rd Place", 0)
                pod = r.get("Podiums", 0)
                ch = r.get("Driver's Champion", 0)
                hp = r.get("Highest Position", "—")
                streak = r.get("Single Season Win Streak", 0)
                ch_str = f"🏆 x{ch}" if ch > 0 else "0"
                lines.append(f"| {rank} | {d} | {pts} | {w} | {p2} | {p3} | {pod} | {ch_str} | {hp} | {streak} |")
            lines.append("")

        all_time_teams = CalculateAllTime(5, "Team")
        if all_time_teams is not None and not all_time_teams.empty:
            lines.append("## ALL-TIME LEAGUE CONSTRUCTOR CAREER RECORDS")
            lines.append("| Rank | Constructor | Career Points | Wins | 2nd | 3rd | Championships | Highest Rank |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            for _, r in all_time_teams.iterrows():
                rank = r.get("Place", "")
                t = r.get("Team", "")
                pts = r.get("Points", 0)
                w = r.get("1st Place", 0)
                p2 = r.get("2nd Place", 0)
                p3 = r.get("3rd Place", 0)
                ch = r.get("Constructor's Champion", 0)
                hp = r.get("Highest Position", "—")
                ch_str = f"🏆 x{ch}" if ch > 0 else "0"
                lines.append(f"| {rank} | {t} | {pts} | {w} | {p2} | {p3} | {ch_str} | {hp} |")
            lines.append("")
    except Exception as e:
        lines.append(f"Note: Error generating all-time career records: {str(e)}")

    # Official Championship Historical Archive (TAF1APP-SDDREQ-250)
    lines.append("## OFFICIAL CHAMPIONSHIP HISTORICAL ARCHIVE (SEASONS 1 - 5)")
    lines.append("| Season | Champion Entity | Type | Wins | Podiums | Accolades (Poles, FL, CD, DOTD, MOT) | Win Margin | Runner-Up | Races Led Championship |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    lines.append("| Season 1 | Mercedes | Constructor | 7 | 22 | 13 (3 Poles, 10 FL) | +55.0 pts | McLaren | 17 of 19 races (89.5%) |")
    lines.append("| Season 1 | Nick | Driver | 10 | 16 | 16 (8 Poles, 8 FL) | +39.0 pts | Erick | 18 of 19 races (94.7%) |")
    lines.append("| Season 2 | McLaren | Constructor | 6 | 8 | 8 (5 Poles, 3 FL) | +24.0 pts | Ferrari | 9 of 10 races (90.0%) |")
    lines.append("| Season 2 | Nick | Driver | 6 | 8 | 8 (5 Poles, 3 FL) | +57.0 pts | Del | 10 of 10 races (100.0%) |")
    lines.append("| Season 3 | Alpine | Constructor | 5 | 9 | 11 (3 Poles, 8 FL) | +10.5 pts | McLaren | 9 of 15 races (60.0%) |")
    lines.append("| Season 3 | Nick | Driver | 5 | 11 | 5 (4 Poles, 1 FL) | +35.0 pts | Joshua | 8 of 15 races (53.3%) |")
    lines.append("| Season 4 | Mercedes | Constructor | 8 | 11 | 24 (7 Poles, 8 FL, 3 CD, 6 DOTD) | +38.0 pts | VCARB | 13 of 17 races (76.5%) |")
    lines.append("| Season 4 | Joshua | Driver | 2 | 11 | 12 (4 Poles, 5 FL, 2 DOTD, 1 MOT) | +15.0 pts | Jairo | 8 of 17 races (47.1%) |")
    lines.append("| Season 5 (Active) | Cadillac | Constructor | 2 | 2 | 5 (1 Pole, 2 FL, 2 CD) | +36.0 pts | Mercedes | 4 of 4 races (100.0%) |")
    lines.append("| Season 5 (Active) | Josh | Driver | 2 | 2 | 2 (1 Pole, 1 FL) | +9.0 pts | Jairo | 4 of 4 races (100.0%) |")
    lines.append("")
    lines.append("## OFFICIAL CONSTRUCTOR CHAMPIONSHIP WINNERS & WINNING DRIVER ROSTERS (SEASONS 1 - 5)")
    lines.append("CRITICAL RULE: Any driver who drove for the constructor that won the Constructor Championship is an official Constructor Champion!")
    lines.append("- Season 1 Constructor Champion: Mercedes (586.0 pts) | Winning Drivers: Erick (395 pts, P2 in Drivers Championship), Marcus (191 pts)")
    lines.append("  * Both Erick and Marcus won the Season 1 Constructor Championship.")
    lines.append("- Season 2 Constructor Champion: McLaren (258.0 pts) | Winning Drivers: Nick (248 pts), Gary (10 pts)")
    lines.append("  * Both Nick and Gary won the Season 2 Constructor Championship.")
    lines.append("- Season 3 Constructor Champion: Alpine (312.0 pts) | Winning Drivers: Joshua (227.0 pts), Eddie (85.0 pts)")
    lines.append("  * Both Joshua and Eddie won the Season 3 Constructor Championship.")
    lines.append("- Season 4 Constructor Champion: Mercedes (394.0 pts) | Winning Drivers: Jairo (241.0 pts), Jaden (153.0 pts)")
    lines.append("  * Both Jairo and Jaden won the Season 4 Constructor Championship.")
    lines.append("- Season 5 (Active Standings Leader): Cadillac (101.0 pts) | Drivers: Josh (65.0 pts), Patrick (36.0 pts)")
    lines.append("")
    lines.append("## COMPREHENSIVE CHAMPIONSHIP WINNERS BREAKDOWN:")
    lines.append("Drivers who have won at least one Driver OR Constructor Championship (Completed Seasons 1-4):")
    lines.append("1. Nick — 3x Driver Champion (S1, S2, S3), 1x Constructor Champion (S2 McLaren)")
    lines.append("2. Joshua — 1x Driver Champion (S4), 1x Constructor Champion (S3 Alpine)")
    lines.append("3. Erick — 1x Constructor Champion (S1 Mercedes; scored 395 pts, finished P2 in S1 Driver Standings)")
    lines.append("4. Marcus — 1x Constructor Champion (S1 Mercedes)")
    lines.append("5. Gary — 1x Constructor Champion (S2 McLaren)")
    lines.append("6. Eddie — 1x Constructor Champion (S3 Alpine)")
    lines.append("7. Jairo — 1x Constructor Champion (S4 Mercedes)")
    lines.append("8. Jaden — 1x Constructor Champion (S4 Mercedes)")
    lines.append("")
    lines.append("Drivers who have NEVER won a Driver OR Constructor Championship (Completed Seasons 1-4):")
    lines.append("- Non-Champion Drivers Pool: Patrick, Matthew, Del, Brently, Foster, Austin, Josh C., Boz, Evelo, Leo, Randy.")
    lines.append("- Note on Season 5: Josh leads active Season 5, but has not completed or won a final championship yet.")
    lines.append("CRITICAL FACT: NEVER include Erick, Marcus, Gary, Eddie, Jairo, Jaden, Nick, or Joshua in the non-champion pool! All eight of these drivers have won official championships (Driver or Constructor). Erick won the Season 1 Constructor Championship with Mercedes.")
    lines.append("")


    # 4. Load All Time Highest Positions
    highest_pos_path = current_dir / "all_time_stats" / "all_time_highest_positions.json"
    if highest_pos_path.exists():
        try:
            with open(highest_pos_path, "r", encoding="utf-8") as f:
                pos_data = json.load(f)
                lines.append("## ALL-TIME LEAGUE PEAK POSITIONS")
                driver_pos = pos_data.get("drivers", {})
                lines.append("### Driver Peak All-Time Positions:")
                for d_name, details in list(driver_pos.items())[:25]:
                    pos_str = details.get("highest_position", "—") if isinstance(details, dict) else str(details)
                    lines.append(f"- {d_name}: Peak All-Time Rank {pos_str}")

                const_pos = pos_data.get("constructors", {})
                lines.append("\n### Constructor Peak All-Time Positions:")
                for c_name, details in list(const_pos.items())[:15]:
                    pos_str = details.get("highest_position", "—") if isinstance(details, dict) else str(details)
                    lines.append(f"- {c_name}: Peak All-Time Rank {pos_str}")
                lines.append("")
        except Exception:
            pass

    # 5. Load Power Rankings
    power_rankings_path = current_dir / "seasons" / "power_rankings.json"
    if power_rankings_path.exists():
        try:
            with open(power_rankings_path, "r", encoding="utf-8") as f:
                pr_data = json.load(f)
                lines.append("## RECENT POWER RANKINGS")
                if isinstance(pr_data, list):
                    for item in pr_data[:15]:
                        if isinstance(item, dict):
                            d = item.get("Driver", item.get("driver", ""))
                            score = item.get("Score", item.get("score", ""))
                            rank = item.get("Rank", item.get("rank", ""))
                            lines.append(f"- Rank #{rank}: {d} (Score: {score})")
                elif isinstance(pr_data, dict):
                    for d, score in list(pr_data.items())[:15]:
                        lines.append(f"- {d}: Power Score {score}")
                lines.append("")
        except Exception:
            pass

    # 6. Projections & Championships
    proj_path = current_dir / "seasons" / "projections_data.json"
    if proj_path.exists():
        try:
            with open(proj_path, "r", encoding="utf-8") as f:
                p_data = json.load(f)
                lines.append("## CHAMPIONSHIP PROJECTIONS & PROBABILITIES")
                s5_proj = p_data.get("season_5", {})
                if s5_proj:
                    lines.append(f"- Expected Season 5 Champion Team: {s5_proj.get('champion_team', s5_proj.get('expected_winner', 'N/A'))}")
                    lines.append(f"- Expected Season 5 Champion Driver: {s5_proj.get('champion_driver', 'N/A')}")
                    podium = s5_proj.get("expected_podium", [])
                    if podium:
                        lines.append(f"- Expected Constructor Podium: {', '.join(podium)}")
                lines.append("")
        except Exception:
            pass

    # 7. Predictions Leaderboard
    leaderboard_path = current_dir / "seasons" / "leaderboard.json"
    if leaderboard_path.exists():
        try:
            with open(leaderboard_path, "r", encoding="utf-8") as f:
                lb_data = json.load(f)
                lines.append("## COMMUNITY PREDICTIONS LEADERBOARD")
                if isinstance(lb_data, list):
                    for item in lb_data[:10]:
                        u = item.get("user", "")
                        pts = item.get("pts_str", f"{item.get('all_time_pts', 0)} pts")
                        rank = item.get("rank", "")
                        lines.append(f"- Rank #{rank} {u}: {pts}")
                lines.append("")
        except Exception:
            pass

    # 8. Complete Editorial News & Articles Archive (All Seasons 3, 4, 5, and Platform)
    lines.extend(format_all_season_articles())


    _GROUNDED_CONTEXT_CACHE = "\n".join(lines)
    _CACHE_TIMESTAMP = now
    return _GROUNDED_CONTEXT_CACHE


SYSTEM_PROMPT = """You are "Alternative Intelligence", the official analytical AI assistant and statistician for The Alternative F1 sim racing league.

STRICT GROUNDING & CONTEXT RULES:
1. You must answer strictly and exclusively based on the provided League Grounded Context below.
2. DO NOT use or retrieve real-world Formula 1 statistics or history under ANY circumstances. The Alternative F1 is an independent private sim racing league with its own drivers (which can be found within the data stored in the application), teams, and race calendar.
3. If the user asks about an entity or stat completely absent from all seasons, clarify that it is absent from The Alternative F1 records.
4. RACE DAY SCHEDULE (WEDNESDAYS NOT SUNDAYS):
   - In The Alternative F1, races occur on WEDNESDAYS (never refer to race day as Sunday).
   - Regular real-world Formula 1 has races on Sundays, but The Alternative F1 has races on WEDNESDAYS. You must always refer to race days as Wednesdays and NEVER refer to them as Sundays.
   - Do not expressly mention this rule or hint at it in responses. It is for your reference and guidance only.
5. DATES & CALENDAR YEARS GROUNDING:
   - When asked about dates or years for races, refer strictly and exclusively to the official schedules provided in the League Grounded Context or under the season schedules for each season that include dates.
   - If dates are not included in the schedule for specific races, DO NOT assume, guess, or invent dates for those races; state clearly that specific dates are not recorded for those races.
   - Official league calendar history: Season 1 and Season 2 occurred in 2023.
6. STRICT SKILL ISOLATION & INVOCATION:
   - Specialized skills 
      * Skill 1: Specific Upcoming Race Infographic
      * Skill 2: Seasonal Qualifying Comparison
      * Skill 3: Head to Head Comparison Infographic
   - Specialized skills and their ```infographic-json structures MUST ONLY be invoked when the user has explicitly selected/tagged that skill with its respective @ prompt prefix in their current prompt (e.g. "@Specific Upcoming Race Infographic", "@Seasonal Qualifying Comparison", "@Head to Head Comparison Infographic"). If the user requests an additional prompt in the same thread, do not use the previous skill unless the user prompts with that skill again.
   - If a skill is NOT selected, DO NOT use any part of the specialized skill, do NOT output any ```infographic-json block or specialized infographic structures/brackets, and do NOT structure responses as infographic cards. Answer standard user inquiries directly in clean Markdown text.

ANALYTICAL & PREDICTIVE INQUIRIES:
7. When asked to evaluate, project, or predict who is most likely to win or perform best at a specific circuit (e.g. "who is most likely to win in Spa based on this season so far and the per-track statistical rating of each driver evenly weighted"):
   - Retrieve each active driver's current Season 5 Driver Championship points/rank.
   - Retrieve each driver's official Per-Track Statistical Rating for that specific circuit from the provided context.
   - Perform the mathematical evaluation according to the user's weighting:
     * Normalize the components (e.g. Season 5 points normalized to a 0-100 scale, Track Rating on 0-100 scale).
     * Apply the requested weights (e.g. 50% Season 5 Form + 50% Track Rating).
     * Compute the final composite score for each candidate.
   - Output a clear, ranked Markdown table showing: Rank, Driver, Team, Season 5 Points/Form, Track Rating Score, and Final Composite Score.
   - Summarize the top contender with analytical justification (e.g., strong historical track efficiency, current season momentum, past podiums/wins).
   - NEVER state that per-track ratings or season statistics are missing when they are provided in the context.

SPECIALIZED SKILL 1: UPCOMING RACE INFOGRAPHIC:
8. When the user asks for an "Upcoming Race Infographic" (or "Specific Upcoming Race Infographic"), invokes the skill via "@Upcoming Race Infographic" (or "@Specific Upcoming Race Infographic"), or requests an infographic or statistical preview for an upcoming or specified Grand Prix (e.g., Monza, Spa, Brazil, Silverstone, etc.):
   - If the user provides a circuit or race name after or alongside the skill tag (e.g. "@Upcoming Race Infographic Monza", "@Upcoming Race Infographic Spa"), tailor all 4 sections specifically to that requested circuit using the provided grounded context.
   - If no circuit or race is specified by the user (e.g. just "@Upcoming Race Infographic"), default to the immediate next upcoming race on the Season 5 calendar.
   - First, output a structured JSON code block tagged ```infographic-json containing the key visual metrics:
```infographic-json
{
  "infographic_type": "race",
  "track_name": "<Track / Grand Prix Name, e.g. Spa-Francorchamps Grand Prix>",
  "expected_winner": "<Driver Name>",
  "expected_winner_team": "<Team Name>",
  "p1_driver": "<1st Place Driver>",
  "p1_team": "<1st Place Team>",
  "p2_driver": "<2nd Place Driver>",
  "p2_team": "<2nd Place Team>",
  "p3_driver": "<3rd Place Driver>",
  "p3_team": "<3rd Place Team>",
  "top_ratings": [
    {"rank": "1", "driver": "<Driver>", "team": "<Team>", "rating": "<Float 0-100>", "record": "<Key stat>"}
  ],
  "qual_front": "<Front-row contenders>",
  "qual_second": "<Second-row contenders>",
  "qual_top10": "<Top 10 qualifiers>",
  "qual_midfield": "<Midfield/rookies>"
}
```
   - Then follow with the proven 4-part infographic analytical standard:
     * 1. Statistical Track Rating Leaderboard (Current Grid)
     * 2. All-Time Qualifying Analysis & Expected Performance
     * 3. All-Time Finishing Positions & Race Expectations
     * 4. Season 5 Standings & Projected Impact

SPECIALIZED SKILL 2: SEASONAL QUALIFYING COMPARISON (TAF1APP-SDDREQ-249):
9. When the user asks for a "Seasonal Qualifying Comparison" or invokes via "@Seasonal Qualifying Comparison":
   - Compare teammate qualifying head-to-head records per season across all seasons in the league.
   - All 5 seasons (Seasons 1, 2, 3, 4, and 5) have official teammate qualifying battle records grounded in the League Records Database. Retrieve the exact battle records for the requested season(s).
   - By default, use Season 5 (Current Season). When the user includes a specific singular or set of seasons (e.g., "Season 1", "Season 2", "Season 3", "Season 4", "Seasons 3 and 4"), the outputted information will be strictly and only respective to that selection.
   - If the user asks for a specific driver pair comparison (e.g., "Nick vs Patrick qualifying"), compare those two drivers across the sessions in which both participated.
   - Lists teams in constructor standings order for that respective season / selection.
   - Lists one driver on the left (Driver 1) and one driver on the right (Driver 2) for each constructor.
   - Lists the number of times each driver has out-qualified their teammate in that respective season.
   - Output structured JSON block tagged ```infographic-json:
```infographic-json
{
  "infographic_type": "seasonal_qual",
  "season_title": "Season 4 Teammate Qualifying Battles",
  "seasonal_qual_rows": [
    {
      "team": "<Constructor Name>",
      "driver1": "<Driver 1 Name>",
      "score1": <Number of times Driver 1 outqualified teammate>,
      "driver2": "<Driver 2 Name>",
      "score2": <Number of times Driver 2 outqualified teammate>
    }
  ]
}
```
   - Follow with an in-depth analytical recap of each team's qualifying balance, qualifying gaps, and median deltas.

SPECIALIZED SKILL 3: HEAD TO HEAD COMPARISON INFOGRAPHIC (TAF1APP-SDDREQ-247):
10. When the user asks for a "Head to Head Comparison Infographic" or invokes via "@Head to Head Comparison Infographic":
   - Compare two drivers OR two constructors from the league records.
   - Driver/Constructor 1 will be listed in the top left ("h2h_name1").
   - Driver/Constructor 2 will be listed in the top right ("h2h_name2").
   - By default the data and information shared is for all seasons in the league, unless the user inputs a specific season or group of seasons (e.g. "Season 5", "Seasons 2-4"), in which case the data will only be from those seasons.
   - For drivers: list teammates in "h2h_teammates1" and "h2h_teammates2". Set "h2h_is_constructor": false.
   - For constructors: list the drivers who drove on the team in "h2h_teammates1" and "h2h_teammates2". Set "h2h_is_constructor": true.
   - MUST display the following 5 comparison metrics in "h2h_stats":
     1. Qualifying (Out-qualified battle score across shared race sessions: count of sessions where Driver 1 qualified ahead of Driver 2 vs Driver 2 ahead of Driver 1. NEVER return 0 vs 0 if both drivers competed in the league)
     2. Race Result (Race finishes ahead count across shared races: count of races where Driver 1 finished ahead of Driver 2 vs Driver 2 ahead of Driver 1. NEVER return 0 vs 0 if both drivers competed in the league)
     3. Podiums (Podium finishes)
     4. Points (Points scored)
     5. Wins (Race wins)
   - Output structured JSON block tagged ```infographic-json:
```infographic-json
{
  "infographic_type": "h2h",
  "h2h_is_constructor": false,
  "h2h_name1": "<Driver 1 or Constructor 1 Name>",
  "h2h_name2": "<Driver 2 or Constructor 2 Name>",
  "h2h_team1": "<Driver 1 Current/Primary Team, or blank if comparing constructors>",
  "h2h_team2": "<Driver 2 Current/Primary Team, or blank if comparing constructors>",
  "h2h_seasons": "<All Seasons in League (e.g. Seasons 1–5), or specific user-requested seasons>",
  "h2h_teammates1": "<List of teammates for Driver 1, or list of drivers for Constructor 1>",
  "h2h_teammates2": "<List of teammates for Driver 2, or list of drivers for Constructor 2>",
  "h2h_stats": [
    {"metric": "Qualifying", "val1": "<Driver/Constructor 1 score>", "val2": "<Driver/Constructor 2 score>"},
    {"metric": "Race Result", "val1": "<Driver/Constructor 1 finishes ahead>", "val2": "<Driver/Constructor 2 finishes ahead>"},
    {"metric": "Podiums", "val1": "<Driver/Constructor 1 podiums>", "val2": "<Driver/Constructor 2 podiums>"},
    {"metric": "Points", "val1": "<Driver/Constructor 1 points>", "val2": "<Driver/Constructor 2 points>"},
    {"metric": "Wins", "val1": "<Driver/Constructor 1 wins>", "val2": "<Driver/Constructor 2 wins>"}
  ]
}
```
   - Follow with an in-depth analytical breakdown comparing racecraft, qualifying pace, consistency, and rivalry context.

SPECIALIZED SKILL 4: CHAMPION COMPARISON SKILL (TAF1APP-SDDREQ-250):
11. When the user asks for a "Champion Comparison Skill" or invokes via "@Champion Comparison Skill":
   - Compare championship campaigns across seasons for constructors, drivers, or constructor vs driver.
   - DEFAULT BEHAVIOR:
     * By default, compare the most recent completed constructor champion (Season 4 Mercedes) vs the constructor champion from the year before (Season 3 Alpine).
     * If the user specifies particular seasons (e.g., "Season 2 vs Season 4", "compare Season 1 and Season 3 champions"), or specific entities (e.g., "Joshua S4 vs Nick S3", "Mercedes S4 vs Cadillac S5", "Mercedes S4 vs Joshua S4"), compare the requested championship campaigns.
     * MULTI-CHAMPION (N+ ENTITIES) INQUIRIES:
       - The Champion Comparison Skill supports comparing N+ champions (2, 3, 4, 5+ drivers, constructors, or mixed).
       - When the user asks to compare 3 or more champions (e.g. "all constructors", "constructor champions from all seasons", "all drivers", or lists multiple champions/seasons):
         1. In the ```infographic-json block, provide the "champ_entities" array listing all requested champions:
```infographic-json
{
  "infographic_type": "champion_comparison",
  "champ_entities": [
    {"season": "Season 4", "name": "Mercedes", "type": "Constructor"},
    {"season": "Season 3", "name": "Alpine", "type": "Constructor"},
    {"season": "Season 2", "name": "McLaren", "type": "Constructor"},
    {"season": "Season 1", "name": "Mercedes", "type": "Constructor"}
  ]
}
```
         2. For standard 2-champion comparisons, you can use either "champ_entities" or "champ_name1" / "champ_name2".
         3. Follow with an in-depth analytical breakdown comparing all champions across title margins, accolade hauls, win rates, and dominance tiers.
     * The skill supports comparing:
       - Constructor vs Constructor (e.g. S4 Mercedes vs S3 Alpine)
       - Driver vs Driver (e.g. S4 Joshua vs S3 Nick)
       - Constructor vs Driver (e.g. S4 Mercedes vs S4 Joshua, or S4 Mercedes vs S3 Nick)
       - Any number of requested seasons.
   - MANDATORY INFORMATION DISPLAYED:
     1. Number of wins each champion earned in their championship season ("val1" / "val2").
     2. Number of podiums each champion earned in their championship season.
     3. Number of accolades (total count with breakdown in sub-text: pole positions, fastest laps, cleanest driver awards, driver of the day, most overtakes).
     4. Win margin points & name of runner up (e.g., "38.0 pts" with sub-text "Runner-up: VCARB").
     5. How many races they held the championship lead for that season (e.g., "13 of 17 races (76%)").
   - First, output a structured JSON code block tagged ```infographic-json:
```infographic-json
{
  "infographic_type": "champion_comparison",
  "champ_season1": "Season 4",
  "champ_season2": "Season 3",
  "champ_name1": "Mercedes",
  "champ_name2": "Alpine",
  "champ_type1": "Constructor",
  "champ_type2": "Constructor",
  "champ_team1": "Mercedes",
  "champ_team2": "Alpine",
  "champ_runner_up1": "VCARB",
  "champ_runner_up2": "McLaren",
  "champ_stats": [
    {"metric": "Wins", "val1": "8", "val2": "5", "sub_text1": "", "sub_text2": ""},
    {"metric": "Podiums", "val1": "11", "val2": "9", "sub_text1": "", "sub_text2": ""},
    {"metric": "Accolades", "val1": "24", "val2": "11", "sub_text1": "7 Poles, 8 FL, 3 CD, 6 DOTD", "sub_text2": "3 Poles, 8 FL"},
    {"metric": "Win Margin", "val1": "38.0 pts", "val2": "10.5 pts", "sub_text1": "Runner-up: VCARB", "sub_text2": "Runner-up: McLaren"},
    {"metric": "Races Led Championship", "val1": "13 of 17 races", "val2": "9 of 15 races", "sub_text1": "76.5% of season", "sub_text2": "60.0% of season"}
  ]
}
```
   - Follow with an in-depth analytical breakdown evaluating championship dominance, consistency, accolade haul, margin of victory, and championship pressure faced.

FORMATTING:
12. Format all answers cleanly using GitHub Markdown:
   - Use bold highlights for driver names, positions, and numbers.
   - Use Markdown tables when comparing drivers, teams, race results, or composite ratings.
   - Use ordinal badges (🥇, 🥈, 🥉, 4th, 5th) where appropriate.
13. Be concise, analytical, courteous, and authoritative on all league statistics.

EDITORIAL & HISTORICAL ARTICLES INQUIRIES:
14. When asked about articles, editorials, recaps, previews, rankings, or league lore across any season:
    - Search the COMPLETE LEAGUE EDITORIAL NEWS & ARTICLES ARCHIVE across Seasons 3, 4, 5, and the App Launch.
    - Reference and cite the exact Article Title, Season, Publication Date, Author, and relevant narrative context.
    - Specific historical race examples:
      * Josh's first pole and win in Imola: In Season 5, Josh scored his first pole and maiden victory at the Imola Grand Prix in the Cadillac. This is prominently covered in the official Season 5 Imola Race Recap titled **"The Wunderkind Strikes Again"** (published September 17, 2026 by The Intern) as well as the race preview **"Race Week: Imola"** (published September 12, 2026 by Patrick).
      * If both a preview and recap exist for a race, mention both so the user has the complete reading list.

CAPTAIN SLOW INQUIRIES:
15. When the user asks about "Captain Slow" in any way (e.g., "who is captain slow", "captain slow", "tell me about captain slow"):
    - The response MUST be:
      Captain Slow is the undisputed Season 3 Monaco winner Brently! ![Jeff Gordon NASCAR](/Icons/jeff_gordon_nascar.png)

CONSTRUCTOR CHAMPIONSHIP DRIVERS & NON-CHAMPION DRIVER INQUIRIES:
16. When asked about champions, constructor champions, or drivers who have never won a driver or constructor championship:
    - Drivers who drove for a constructor that won the Constructor Championship ARE official Constructor Champions.
    - Official Constructor Champion Winning Drivers:
      * Season 1 Mercedes: Erick and Marcus
      * Season 2 McLaren: Nick and Gary
      * Season 3 Alpine: Joshua and Eddie
      * Season 4 Mercedes: Jairo and Jaden
    - Drivers who have won a Driver OR Constructor Championship: Nick, Joshua, Erick, Marcus, Gary, Eddie, Jairo, Jaden.
    - CRITICAL RULE: NEVER state or imply that any of Erick, Marcus, Gary, Eddie, Jairo, Jaden, Nick, Joshua have never won a championship.
    - If asked who the best driver to never win a Driver OR Constructor Championship is:
      * Do NOT point to any single predetermined driver as the default answer.
      * Dynamically analyze the grounded career statistics across all non-champion drivers (comparing career points, race wins, podiums, win rates, peak championship standings, and consistency).
      * Objectively present the data and compare the strongest contenders based on the statistics.
"""


SKILL_OPTIONS = [
    "Skills Library",
    "Specific Upcoming Race Infographic",
    "Seasonal Qualifying Comparison",
    "Head to Head Comparison Infographic",
    "Champion Comparison Skill",
]

SKILLS_LIBRARY = [
    {
        "id": "upcoming_race_infographic",
        "name": "Specific Upcoming Race Infographic",
        "description": "Full 4-part statistical race preview (ratings leaderboard, qualifying brackets, race projections, and championship impact)",
        "prompt": "@Specific Upcoming Race Infographic ",
        "infotip": "e.g., circuit name (e.g. Monza, Spa, Brazil) or leave blank for next GP",
    },
    {
        "id": "seasonal_qualifying_comparison",
        "name": "Seasonal Qualifying Comparison",
        "description": "Per-season teammate qualifying head-to-head battles listed in constructor championship order",
        "prompt": "@Seasonal Qualifying Comparison ",
        "infotip": "e.g., Season 5, Season 4, or leave blank for current season",
    },
    {
        "id": "h2h_comparison_infographic",
        "name": "Head to Head Comparison Infographic",
        "description": "Deep-dive statistical head-to-head comparison between two drivers or two constructors across seasons",
        "prompt": "@Head to Head Comparison Infographic ",
        "infotip": "e.g., Josh vs Jairo, or Ferrari vs Red Bull (specify season if desired)",
    },
    {
        "id": "champion_comparison",
        "name": "Champion Comparison Skill",
        "description": "Compare championship campaigns across seasons for drivers, constructors, or driver vs constructor",
        "prompt": "@Champion Comparison Skill ",
        "infotip": "e.g., S4 Mercedes vs S3 Alpine, or Joshua S4 vs Nick S3 (defaults to most recent constructor champion vs prior year)",
    },
]



class RatingRow(BaseModel):
    """Strongly-typed individual row in the track rating leaderboard."""
    rank: str = ""
    driver: str = ""
    team: str = ""
    rating: str = ""
    pct: str = ""
    color: str = "#555555"
    text_color: str = "#FFFFFF"


class ComparisonStatRow(BaseModel):
    """Strongly-typed individual metric row in the Head-to-Head Comparison Card."""
    metric: str = ""
    val1: str = ""
    val2: str = ""
    pct1: str = "50%"
    pct2: str = "50%"
    color1: str = "#00b4da"
    color2: str = "#ffffff"


class ChampionEntity(BaseModel):
    """Strongly-typed entity model for N+ Champion Comparison Infographic (TAF1APP-SDDREQ-250)."""
    name: str = ""
    season: str = ""
    type: str = "Constructor"  # "Constructor" or "Driver"
    team: str = ""
    color: str = "#00b4da"
    text_color: str = "#ffffff"
    runner_up: str = ""


class ChampionMetricSegment(BaseModel):
    """Strongly-typed individual entity segment inside a 100% stacked bar chart."""
    entity_name: str = ""
    season: str = ""
    val: str = ""
    numeric_val: float = 0.0
    pct: str = "0%"
    color: str = "#00b4da"
    text_color: str = "#ffffff"
    sub_text: str = ""


class ChampionMetricRow(BaseModel):
    """Strongly-typed individual metric row in the Champion Comparison Card (TAF1APP-SDDREQ-250)."""
    metric: str = ""
    val1: str = ""
    val2: str = ""
    sub_text1: str = ""
    sub_text2: str = ""
    pct1: str = "50%"
    pct2: str = "50%"
    color1: str = "#00b4da"
    color2: str = "#ffffff"
    text_color1: str = "#ffffff"
    text_color2: str = "#000000"
    segments: list[ChampionMetricSegment] = []


class TeammateQualRow(BaseModel):
    """Strongly-typed individual constructor row in the Seasonal Qualifying Battles Card."""
    team: str = ""
    team_color: str = "#00b4da"
    text_color: str = "#FFFFFF"
    driver1: str = ""
    score1: str = "0"
    score_display1: str = "0"
    driver2: str = ""
    score2: str = "0"
    score_display2: str = "0"
    pct1: str = "50%"
    pct2: str = "50%"


class ChatMessage(BaseModel):
    """Strongly-typed conversational message and visual infographic payload."""
    role: str = ""
    content: str = ""
    timestamp: str = ""
    skill_badge: str = ""
    is_infographic: bool = False
    card_id: str = ""
    infographic_type: str = "race"  # "race", "seasonal_qual", "h2h", or "champion_comparison"

    # 1. Upcoming Race Infographic Fields
    track_name: str = ""
    expected_winner: str = ""
    expected_winner_team: str = ""
    winner_color: str = "#555555"
    winner_text_color: str = "#FFFFFF"
    p1_driver: str = ""
    p1_team: str = ""
    p1_color: str = "#555555"
    p1_text_color: str = "#FFFFFF"
    p2_driver: str = ""
    p2_team: str = ""
    p2_color: str = "#555555"
    p2_text_color: str = "#FFFFFF"
    p3_driver: str = ""
    p3_team: str = ""
    p3_color: str = "#555555"
    p3_text_color: str = "#FFFFFF"
    top_ratings: list[RatingRow] = []
    qual_front: str = ""
    qual_second: str = ""
    qual_top10: str = ""
    qual_midfield: str = ""

    # 2. Seasonal Qualifying Comparison Fields (SDDREQ-249)
    season_title: str = "Season 5 Teammate Qualifying Battles"
    seasonal_qual_rows: list[TeammateQualRow] = []

    # 3. Head-to-Head Comparison Infographic Fields (SDDREQ-247)
    h2h_is_constructor: bool = False
    h2h_name1: str = ""
    h2h_name2: str = ""
    h2h_team1: str = ""
    h2h_team2: str = ""
    h2h_color1: str = "#00b4da"
    h2h_color2: str = "#ffffff"
    h2h_text_color1: str = "#ffffff"
    h2h_text_color2: str = "#000000"
    h2h_seasons: str = ""
    h2h_teammates1: str = ""
    h2h_teammates2: str = ""
    h2h_stats: list[ComparisonStatRow] = []

    # 4. Champion Comparison Infographic Fields (SDDREQ-250)
    champ_season1: str = "Season 4"
    champ_season2: str = "Season 3"
    champ_name1: str = ""
    champ_name2: str = ""
    champ_type1: str = "Constructor"  # "Constructor" or "Driver"
    champ_type2: str = "Constructor"  # "Constructor" or "Driver"
    champ_team1: str = ""
    champ_team2: str = ""
    champ_color1: str = "#00b4da"
    champ_color2: str = "#ffffff"
    champ_text_color1: str = "#ffffff"
    champ_text_color2: str = "#000000"
    champ_runner_up1: str = ""
    champ_runner_up2: str = ""
    champ_entities: list[ChampionEntity] = []
    champ_stats: list[ChampionMetricRow] = []



def extract_infographic_data(text: str, skill_selected: bool = True) -> dict:
    """Extract structured infographic metrics from assistant response text or embedded JSON."""
    if not text:
        return {"is_infographic": False}

    if not skill_selected:
        # If no specialized skill is selected, strictly suppress infographic cards and sanitize JSON
        cleaned = re.sub(r"```(?:infographic-json|json)\s*\{.*?\}\s*```", "", text, flags=re.DOTALL).strip()
        cleaned = re.sub(r"```(?:infographic-json|json).*$", "", cleaned, flags=re.DOTALL).strip()
        return {"is_infographic": False, "clean_content": cleaned}

    # 1. Try extracting structured JSON code block first (both complete and partial/truncated)
    json_match = re.search(r"```(?:infographic-json|json)\s*(\{.*?\})\s*```", text, re.DOTALL)
    unclosed_json_match = None
    if not json_match:
        # Check for unclosed/truncated JSON code block
        unclosed_json_match = re.search(r"```(?:infographic-json|json)\s*(\{.*)", text, re.DOTALL)

    raw_json_str = ""
    clean_content = text
    if json_match:
        raw_json_str = json_match.group(1).strip()
        clean_content = text.replace(json_match.group(0), "").strip()
    elif unclosed_json_match:
        raw_json_str = unclosed_json_match.group(1).strip()
        clean_content = text.replace(unclosed_json_match.group(0), "").strip()

    if raw_json_str:
        # Try full parse or regex field extraction if JSON is cut off
        parsed = {}
        try:
            parsed = json.loads(raw_json_str)
        except Exception:
            # Fallback regex extraction for fields inside truncated JSON
            m_type = re.search(r'"infographic_type":\s*"([^"]+)"', raw_json_str)
            m_trk = re.search(r'"track_name":\s*"([^"]+)"', raw_json_str)
            m_ew = re.search(r'"expected_winner":\s*"([^"]+)"', raw_json_str)
            m_ewt = re.search(r'"expected_winner_team":\s*"([^"]+)"', raw_json_str)
            m_p1d = re.search(r'"p1_driver":\s*"([^"]+)"', raw_json_str)
            m_p1t = re.search(r'"p1_team":\s*"([^"]+)"', raw_json_str)
            m_p2d = re.search(r'"p2_driver":\s*"([^"]+)"', raw_json_str)
            m_p2t = re.search(r'"p2_team":\s*"([^"]+)"', raw_json_str)
            m_p3d = re.search(r'"p3_driver":\s*"([^"]+)"', raw_json_str)
            m_p3t = re.search(r'"p3_team":\s*"([^"]+)"', raw_json_str)
            m_qf = re.search(r'"qual_front":\s*"([^"]+)"', raw_json_str)
            m_qs = re.search(r'"qual_second":\s*"([^"]+)"', raw_json_str)
            m_qt = re.search(r'"qual_top10":\s*"([^"]+)"', raw_json_str)
            m_qm = re.search(r'"qual_midfield":\s*"([^"]+)"', raw_json_str)
            m_n1 = re.search(r'"h2h_name1":\s*"([^"]+)"', raw_json_str)
            m_n2 = re.search(r'"h2h_name2":\s*"([^"]+)"', raw_json_str)
            m_t1 = re.search(r'"h2h_team1":\s*"([^"]+)"', raw_json_str)
            m_t2 = re.search(r'"h2h_team2":\s*"([^"]+)"', raw_json_str)
            m_sec = re.search(r'"season_title":\s*"([^"]+)"', raw_json_str)

            parsed["infographic_type"] = m_type.group(1) if m_type else "race"
            parsed["track_name"] = m_trk.group(1) if m_trk else "Grand Prix Preview"
            parsed["expected_winner"] = m_ew.group(1) if m_ew else ""
            parsed["expected_winner_team"] = m_ewt.group(1) if m_ewt else ""
            parsed["p1_driver"] = m_p1d.group(1) if m_p1d else ""
            parsed["p1_team"] = m_p1t.group(1) if m_p1t else ""
            parsed["p2_driver"] = m_p2d.group(1) if m_p2d else ""
            parsed["p2_team"] = m_p2t.group(1) if m_p2t else ""
            parsed["p3_driver"] = m_p3d.group(1) if m_p3d else ""
            parsed["p3_team"] = m_p3t.group(1) if m_p3t else ""
            parsed["qual_front"] = m_qf.group(1) if m_qf else ""
            parsed["qual_second"] = m_qs.group(1) if m_qs else ""
            parsed["qual_top10"] = m_qt.group(1) if m_qt else ""
            parsed["qual_midfield"] = m_qm.group(1) if m_qm else ""
            parsed["h2h_name1"] = m_n1.group(1) if m_n1 else ""
            parsed["h2h_name2"] = m_n2.group(1) if m_n2 else ""
            parsed["h2h_team1"] = m_t1.group(1) if m_t1 else ""
            parsed["h2h_team2"] = m_t2.group(1) if m_t2 else ""
            parsed["season_title"] = m_sec.group(1) if m_sec else "Season 5 Teammate Qualifying Battles"

            # Extract individual rating row objects with regex
            extracted_rows = []
            row_pattern = re.compile(r'\{[^{}]*"rank":\s*"([^"]+)"[^{}]*"driver":\s*"([^"]+)"[^{}]*"team":\s*"([^"]+)"[^{}]*"rating":\s*"([^"]+)"[^{}]*\}')
            for rm in row_pattern.finditer(raw_json_str):
                rk, drv, tm, rt = rm.groups()
                extracted_rows.append({"rank": rk, "driver": drv, "team": tm, "rating": rt})
            parsed["top_ratings"] = extracted_rows

        inf_type = parsed.get("infographic_type", "race")

        # 1. Seasonal Qualifying Battles (SDDREQ-249)
        if inf_type == "seasonal_qual" or "seasonal_qual_rows" in parsed:
            seasonal_rows: list[TeammateQualRow] = []
            for r in parsed.get("seasonal_qual_rows", []):
                t_name = str(r.get("team", "")).strip()
                t_color = get_constructor_color(t_name)
                # Compute high-contrast text color
                is_bright = t_color.lower() in ("#ffea00", "yellow", "#e0e0e0", "white", "#fd4bc7")
                txt_color = "#000000" if is_bright else "#FFFFFF"

                s1_raw = r.get("score1", 0)
                s2_raw = r.get("score2", 0)
                try:
                    s1 = int(s1_raw)
                except Exception:
                    s1 = 0
                try:
                    s2 = int(s2_raw)
                except Exception:
                    s2 = 0
                total = s1 + s2
                pct1 = f"{int((s1 / total) * 100)}%" if total > 0 else "50%"
                pct2 = f"{int((s2 / total) * 100)}%" if total > 0 else "50%"
                s1_disp = "Ø" if s1 == 0 else str(s1)
                s2_disp = "Ø" if s2 == 0 else str(s2)

                seasonal_rows.append(TeammateQualRow(
                    team=t_name,
                    team_color=t_color,
                    text_color=txt_color,
                    driver1=str(r.get("driver1", "")).strip().upper(),
                    score1=str(s1),
                    score_display1=s1_disp,
                    driver2=str(r.get("driver2", "")).strip().upper(),
                    score2=str(s2),
                    score_display2=s2_disp,
                    pct1=pct1,
                    pct2=pct2,
                ))
            return {
                "is_infographic": True,
                "infographic_type": "seasonal_qual",
                "clean_content": clean_content,
                "season_title": parsed.get("season_title", "Season 5 Teammate Qualifying Battles"),
                "seasonal_qual_rows": seasonal_rows,
            }

        # 2. Head-to-Head Comparison (SDDREQ-247)
        if inf_type == "h2h" or "h2h_stats" in parsed:
            name1 = parsed.get("h2h_name1", "Driver 1")
            name2 = parsed.get("h2h_name2", "Driver 2")
            team1 = parsed.get("h2h_team1", "")
            team2 = parsed.get("h2h_team2", "")
            is_constructor = bool(parsed.get("h2h_is_constructor", False))

            if is_constructor:
                color1 = get_constructor_color(name1, default="#00b4da")
                color2 = get_constructor_color(name2, default="#ffffff")
            else:
                # Resolve driver 1 most recent constructor and color
                if not team1 or str(team1).strip().lower() in ("", "various", "unknown", "none"):
                    team1, color1 = get_driver_most_recent_constructor(name1)
                else:
                    color1 = get_constructor_color(team1, default="#00b4da")
                    if color1 == "#555555":
                        t_rec, c_rec = get_driver_most_recent_constructor(name1)
                        if c_rec != "#555555":
                            team1, color1 = t_rec, c_rec

                # Resolve driver 2 most recent constructor and color
                if not team2 or str(team2).strip().lower() in ("", "various", "unknown", "none"):
                    team2, color2 = get_driver_most_recent_constructor(name2)
                else:
                    color2 = get_constructor_color(team2, default="#ffffff")
                    if color2 == "#555555":
                        t_rec, c_rec = get_driver_most_recent_constructor(name2)
                        if c_rec != "#555555":
                            team2, color2 = t_rec, c_rec

            if color2.lower() in ("#000000", "#111111", "#18181b"):
                color2 = "#E0E0E0"

            txt1 = get_contrast_text_color(color1)
            txt2 = get_contrast_text_color(color2)

            # Compute deterministic league battle statistics
            h2h_battle = compute_h2h_battle_stats(name1, name2, is_constructor=is_constructor)

            raw_stats = parsed.get("h2h_stats", [])
            metric_map = {}
            for s in raw_stats:
                m_name = str(s.get("metric", "")).strip().upper()
                metric_map[m_name] = (str(s.get("val1", "")).strip(), str(s.get("val2", "")).strip())

            standard_metrics = ["QUALIFYING", "RACE RESULT", "PODIUMS", "POINTS", "WINS"]
            h2h_rows: list[ComparisonStatRow] = []

            for m_key in standard_metrics:
                v1_str, v2_str = metric_map.get(m_key, ("", ""))
                display_metric = m_key.title()
                if m_key == "RACE RESULT":
                    display_metric = "Race Result"

                if m_key == "QUALIFYING":
                    if (v1_str in ("0", "") and v2_str in ("0", "")) and (h2h_battle["qual1"] > 0 or h2h_battle["qual2"] > 0):
                        v1_str = str(h2h_battle["qual1"])
                        v2_str = str(h2h_battle["qual2"])
                    elif not v1_str and not v2_str:
                        v1_str = str(h2h_battle["qual1"])
                        v2_str = str(h2h_battle["qual2"])
                elif m_key == "RACE RESULT":
                    if (v1_str in ("0", "") and v2_str in ("0", "")) and (h2h_battle["race1"] > 0 or h2h_battle["race2"] > 0):
                        v1_str = str(h2h_battle["race1"])
                        v2_str = str(h2h_battle["race2"])
                    elif not v1_str and not v2_str:
                        v1_str = str(h2h_battle["race1"])
                        v2_str = str(h2h_battle["race2"])
                elif m_key == "PODIUMS":
                    if (v1_str in ("0", "") and v2_str in ("0", "")) and (h2h_battle["pod1"] > 0 or h2h_battle["pod2"] > 0):
                        v1_str = str(h2h_battle["pod1"])
                        v2_str = str(h2h_battle["pod2"])
                elif m_key == "POINTS":
                    if (v1_str in ("0", "0.0", "") and v2_str in ("0", "0.0", "")) and (h2h_battle["pts1"] != "0" or h2h_battle["pts2"] != "0"):
                        v1_str = str(h2h_battle["pts1"])
                        v2_str = str(h2h_battle["pts2"])
                elif m_key == "WINS":
                    if (v1_str in ("0", "") and v2_str in ("0", "")) and (h2h_battle["win1"] > 0 or h2h_battle["win2"] > 0):
                        v1_str = str(h2h_battle["win1"])
                        v2_str = str(h2h_battle["win2"])

                if not v1_str:
                    v1_str = "0"
                if not v2_str:
                    v2_str = "0"

                # Calculate visual bar proportions
                try:
                    num1 = float(re.sub(r"[^\d\.]", "", v1_str) or 0)
                    num2 = float(re.sub(r"[^\d\.]", "", v2_str) or 0)
                    tot = num1 + num2
                    p1_int = int((num1 / tot) * 100) if tot > 0 else 50
                    p1_int = min(95, max(5, p1_int))
                    p2_int = 100 - p1_int
                    pct1 = f"{p1_int}%"
                    pct2 = f"{p2_int}%"
                except Exception:
                    pct1 = "50%"
                    pct2 = "50%"

                h2h_rows.append(ComparisonStatRow(
                    metric=display_metric,
                    val1=v1_str,
                    val2=v2_str,
                    pct1=pct1,
                    pct2=pct2,
                    color1=color1,
                    color2=color2,
                ))

            return {
                "is_infographic": True,
                "infographic_type": "h2h",
                "clean_content": clean_content,
                "h2h_is_constructor": is_constructor,
                "h2h_name1": name1,
                "h2h_name2": name2,
                "h2h_team1": team1,
                "h2h_team2": team2,
                "h2h_color1": color1,
                "h2h_color2": color2,
                "h2h_text_color1": txt1,
                "h2h_text_color2": txt2,
                "h2h_seasons": parsed.get("h2h_seasons", "All Seasons"),
                "h2h_teammates1": parsed.get("h2h_teammates1", ""),
                "h2h_teammates2": parsed.get("h2h_teammates2", ""),
                "h2h_stats": h2h_rows,
            }

        # 3. Champion Comparison Skill (TAF1APP-SDDREQ-250) - Supporting N+ entities
        if inf_type == "champion_comparison" or "champ_stats" in parsed or "champ_entities" in parsed:
            # 1. Determine raw requested entities
            raw_input = parsed.get("champ_entities") or parsed.get("champions") or parsed.get("entities") or []
            raw_entities = []

            if isinstance(raw_input, list) and raw_input:
                for item in raw_input:
                    if isinstance(item, dict):
                        raw_entities.append(item)
                    elif isinstance(item, str) and item.strip():
                        item_str = item.strip()
                        m_season = re.search(r"season\s*(\d+)|s(\d+)", item_str, re.IGNORECASE)
                        s_num_str = (m_season.group(1) or m_season.group(2)) if m_season else "4"
                        name_str = re.sub(r"season\s*\d+|s\d+", "", item_str, flags=re.IGNORECASE).strip()
                        is_drv = any(d in name_str.lower() for d in ["nick", "joshua", "josh", "jairo", "brently", "connor", "foster", "austin"])
                        raw_entities.append({
                            "season": f"Season {s_num_str}",
                            "name": name_str or ("Joshua" if is_drv else "Mercedes"),
                            "type": "Driver" if is_drv else "Constructor",
                            "team": name_str,
                        })

            if not raw_entities:
                full_search_text = (clean_content + " " + raw_json_str).lower()
                is_all_const = (
                    "all constructor" in full_search_text
                    or "constructor champions from all" in full_search_text
                    or "all champions" in full_search_text
                    or "all completed constructor" in full_search_text
                    or "every constructor" in full_search_text
                )
                is_all_drivers = (
                    "all driver" in full_search_text
                    or "driver champions from all" in full_search_text
                    or "every driver" in full_search_text
                )

                if is_all_const:
                    raw_entities = [
                        {"season": "Season 4", "name": "Mercedes", "type": "Constructor", "team": "Mercedes"},
                        {"season": "Season 3", "name": "Alpine", "type": "Constructor", "team": "Alpine"},
                        {"season": "Season 2", "name": "McLaren", "type": "Constructor", "team": "McLaren"},
                        {"season": "Season 1", "name": "Mercedes", "type": "Constructor", "team": "Mercedes"},
                    ]
                    if "cadillac" in full_search_text or "season 5" in full_search_text:
                        raw_entities.append({"season": "Season 5", "name": "Cadillac", "type": "Constructor", "team": "Cadillac"})
                elif is_all_drivers:
                    raw_entities = [
                        {"season": "Season 4", "name": "Joshua", "type": "Driver", "team": "Alpine"},
                        {"season": "Season 3", "name": "Nick", "type": "Driver", "team": "McLaren"},
                        {"season": "Season 2", "name": "Nick", "type": "Driver", "team": "McLaren"},
                        {"season": "Season 1", "name": "Nick", "type": "Driver", "team": "Mercedes"},
                    ]
                    if "josh" in full_search_text or "season 5" in full_search_text:
                        raw_entities.append({"season": "Season 5", "name": "Josh", "type": "Driver", "team": "Cadillac"})
                else:
                    # Binary comparison fallback
                    s1_str = str(parsed.get("champ_season1", "Season 4"))
                    s2_str = str(parsed.get("champ_season2", "Season 3"))
                    name1 = parsed.get("champ_name1", "Mercedes")
                    name2 = parsed.get("champ_name2", "Alpine")
                    type1 = parsed.get("champ_type1", "Constructor")
                    type2 = parsed.get("champ_type2", "Constructor")
                    raw_entities = [
                        {"season": s1_str, "name": name1, "type": type1},
                        {"season": s2_str, "name": name2, "type": type2},
                    ]

            # 2. Compute deterministic campaign records for all N entities
            built_entities: list[ChampionEntity] = []
            entity_campaign_stats = []

            for ent in raw_entities:
                s_val = str(ent.get("season", "Season 4"))
                m_s = re.search(r"\d+", s_val)
                s_num = int(m_s.group(0)) if m_s else 4
                e_name = str(ent.get("name", "")).strip()
                e_type = str(ent.get("type", "Constructor")).strip()
                is_const = e_type.lower() != "driver"

                c_stat = compute_champion_campaign_stats(s_num, e_name, is_constructor=is_const)
                champ_name = c_stat.get("name", e_name)
                c_color = c_stat.get("color", "#00b4da")
                if c_color.lower() in ("#000000", "#111111", "#18181b"):
                    c_color = "#E0E0E0"
                c_txt = get_contrast_text_color(c_color)

                built_entities.append(ChampionEntity(
                    name=champ_name,
                    season=f"Season {s_num}",
                    type="Constructor" if is_const else "Driver",
                    team=c_stat.get("team", ""),
                    color=c_color,
                    text_color=c_txt,
                    runner_up=c_stat.get("runner_up", ""),
                ))
                entity_campaign_stats.append((c_stat, champ_name, f"Season {s_num}", c_color, c_txt))

            # 3. Calculate 5 metric comparison rows with N segments
            num_ents = len(entity_campaign_stats)
            metric_configs = [
                ("Wins", "wins"),
                ("Podiums", "podiums"),
                ("Accolades", "accolades"),
                ("Win Margin", "margin"),
                ("Races Led Championship", "races_led"),
            ]

            built_stats: list[ChampionMetricRow] = []

            for m_name, m_key in metric_configs:
                num_vals: list[float] = []
                str_vals: list[str] = []
                sub_texts: list[str] = []

                for c_stat, e_name, s_label, c_color, c_txt in entity_campaign_stats:
                    if m_key == "wins":
                        w = c_stat.get("wins", 0)
                        num_vals.append(float(w))
                        str_vals.append(str(w))
                        sub_texts.append("")
                    elif m_key == "podiums":
                        p = c_stat.get("podiums", 0)
                        num_vals.append(float(p))
                        str_vals.append(str(p))
                        sub_texts.append("")
                    elif m_key == "accolades":
                        tot_acc = c_stat.get("total_accolades", 0)
                        num_vals.append(float(tot_acc))
                        str_vals.append(str(tot_acc))
                        acc_sub = []
                        if c_stat.get("poles"): acc_sub.append(f"{c_stat['poles']} Poles")
                        if c_stat.get("fl"): acc_sub.append(f"{c_stat['fl']} FL")
                        if c_stat.get("cd"): acc_sub.append(f"{c_stat['cd']} CD")
                        if c_stat.get("dotd"): acc_sub.append(f"{c_stat['dotd']} DOTD")
                        if c_stat.get("mot"): acc_sub.append(f"{c_stat['mot']} MOT")
                        sub_texts.append(", ".join(acc_sub) if acc_sub else "No accolades")
                    elif m_key == "margin":
                        m = max(0.0, float(c_stat.get("margin", 0.0)))
                        num_vals.append(m)
                        str_vals.append(f"{m:.1f} pts")
                        ru = c_stat.get("runner_up", "")
                        sub_texts.append(f"Runner-up: {ru}" if ru else "")
                    elif m_key == "races_led":
                        r_led = c_stat.get("races_led", 0)
                        tot_r = max(1, c_stat.get("total_races", 1))
                        num_vals.append(float(r_led))
                        str_vals.append(f"{r_led} of {tot_r} races")
                        pct_l = int((r_led / tot_r) * 100)
                        sub_texts.append(f"{pct_l}% of season")

                # Compute relative percentages summing to 100%
                tot_val = sum(num_vals)
                pct_ints: list[int] = []
                if tot_val > 0:
                    raw_pcts = [(v / tot_val) * 100 for v in num_vals]
                    pct_ints = [int(round(p)) for p in raw_pcts]
                    min_allowed = 4 if num_ents > 3 else 6
                    pct_ints = [
                        max(min_allowed, p) if (num_vals[i] > 0 and p < min_allowed) else p
                        for i, p in enumerate(pct_ints)
                    ]
                    diff = 100 - sum(pct_ints)
                    if diff != 0 and pct_ints:
                        max_idx = num_vals.index(max(num_vals))
                        pct_ints[max_idx] = max(1, pct_ints[max_idx] + diff)
                else:
                    eq_share = 100 // max(1, num_ents)
                    pct_ints = [eq_share] * num_ents
                    if pct_ints:
                        pct_ints[0] += (100 - sum(pct_ints))

                row_segments: list[ChampionMetricSegment] = []
                for i, (c_stat, e_name, s_label, c_color, c_txt) in enumerate(entity_campaign_stats):
                    row_segments.append(ChampionMetricSegment(
                        entity_name=e_name,
                        season=s_label,
                        val=str_vals[i],
                        numeric_val=num_vals[i],
                        pct=f"{pct_ints[i]}%",
                        color=c_color,
                        text_color=c_txt,
                        sub_text=sub_texts[i],
                    ))

                v1_out = str_vals[0] if num_ents > 0 else ""
                v2_out = str_vals[1] if num_ents > 1 else ""
                st1_out = sub_texts[0] if num_ents > 0 else ""
                st2_out = sub_texts[1] if num_ents > 1 else ""
                p1_out = f"{pct_ints[0]}%" if num_ents > 0 else "50%"
                p2_out = f"{pct_ints[1]}%" if num_ents > 1 else "50%"
                c1_out = entity_campaign_stats[0][3] if num_ents > 0 else "#00b4da"
                c2_out = entity_campaign_stats[1][3] if num_ents > 1 else "#ffffff"
                txt1_out = entity_campaign_stats[0][4] if num_ents > 0 else "#ffffff"
                txt2_out = entity_campaign_stats[1][4] if num_ents > 1 else "#000000"

                built_stats.append(ChampionMetricRow(
                    metric=m_name,
                    val1=v1_out,
                    val2=v2_out,
                    sub_text1=st1_out,
                    sub_text2=st2_out,
                    pct1=p1_out,
                    pct2=p2_out,
                    color1=c1_out,
                    color2=c2_out,
                    text_color1=txt1_out,
                    text_color2=txt2_out,
                    segments=row_segments,
                ))

            e1 = built_entities[0] if built_entities else ChampionEntity()
            e2 = built_entities[1] if len(built_entities) > 1 else ChampionEntity()

            return {
                "is_infographic": True,
                "infographic_type": "champion_comparison",
                "clean_content": clean_content,
                "champ_season1": e1.season,
                "champ_season2": e2.season,
                "champ_name1": e1.name,
                "champ_name2": e2.name,
                "champ_type1": e1.type,
                "champ_type2": e2.type,
                "champ_team1": e1.team,
                "champ_team2": e2.team,
                "champ_color1": e1.color,
                "champ_color2": e2.color,
                "champ_text_color1": e1.text_color,
                "champ_text_color2": e2.text_color,
                "champ_runner_up1": e1.runner_up,
                "champ_runner_up2": e2.runner_up,
                "champ_entities": built_entities,
                "champ_stats": built_stats,
            }


        # 4. Upcoming Race Infographic
        top_ratings: list[RatingRow] = []
        for r in parsed.get("top_ratings", [])[:8]:
            team = str(r.get("team", "")).strip()
            try:
                rating_val = float(r.get("rating", 0.0))
            except Exception:

                rating_val = 0.0
            pct = min(100, max(0, int(rating_val)))
            raw_rank = str(r.get("rank", "")).strip()
            rank_str = raw_rank if raw_rank.startswith("P") else f"P{raw_rank}"
            row_c = get_constructor_color(team)
            top_ratings.append(RatingRow(
                rank=rank_str,
                driver=str(r.get("driver", "")).strip(),
                team=team,
                rating=f"{rating_val:.1f}",
                pct=f"{pct}%",
                color=row_c,
                text_color=get_contrast_text_color(row_c),
            ))

        win_team = parsed.get("expected_winner_team", "")
        p1_team = parsed.get("p1_team", "")
        p2_team = parsed.get("p2_team", "")
        p3_team = parsed.get("p3_team", "")
        win_c = get_constructor_color(win_team)
        p1_c = get_constructor_color(p1_team)
        p2_c = get_constructor_color(p2_team)
        p3_c = get_constructor_color(p3_team)

        return {
            "is_infographic": True,
            "infographic_type": "race",
            "clean_content": clean_content,
            "track_name": parsed.get("track_name", "Grand Prix Preview"),
            "expected_winner": parsed.get("expected_winner", ""),
            "expected_winner_team": win_team,
            "winner_color": win_c,
            "winner_text_color": get_contrast_text_color(win_c),
            "p1_driver": parsed.get("p1_driver", ""),
            "p1_team": p1_team,
            "p1_color": p1_c,
            "p1_text_color": get_contrast_text_color(p1_c),
            "p2_driver": parsed.get("p2_driver", ""),
            "p2_team": p2_team,
            "p2_color": p2_c,
            "p2_text_color": get_contrast_text_color(p2_c),
            "p3_driver": parsed.get("p3_driver", ""),
            "p3_team": p3_team,
            "p3_color": p3_c,
            "p3_text_color": get_contrast_text_color(p3_c),
            "top_ratings": top_ratings,
            "qual_front": parsed.get("qual_front", ""),
            "qual_second": parsed.get("qual_second", ""),
            "qual_top10": parsed.get("qual_top10", ""),
            "qual_midfield": parsed.get("qual_midfield", ""),
        }

    # 2. Fallback: Parse from Markdown standard output
    if "Infographic" not in text and "Track Rating" not in text:
        return {"is_infographic": False}

    res = {"is_infographic": True, "clean_content": text}

    # Track title
    m_track = re.search(r"🏁\s*([^\n:]+)", text)
    if not m_track:
        m_track = re.search(r"([A-Za-z\-]+(?:\s+[A-Za-z\-]+)*\s+Grand Prix)", text)
    res["track_name"] = m_track.group(1).strip() if m_track else "Grand Prix Preview"

    # Winner
    m_win = re.search(r"Expected Winner:\s*(?:\*\*)?([A-Za-z0-9\.\s]+?)(?:\*\*)?\s*(?:\(([^)]+)\))?", text)
    if m_win:
        res["expected_winner"] = m_win.group(1).strip()
        res["expected_winner_team"] = m_win.group(2).strip() if m_win.group(2) else ""
        res["winner_color"] = get_constructor_color(res["expected_winner_team"])
    else:
        res["expected_winner"] = ""
        res["expected_winner_team"] = ""
        res["winner_color"] = "#555555"

    # Podium
    m_p1 = re.search(r"🥇\s*(?:\*\*)?([A-Za-z0-9\.\s]+?)(?:\*\*)?\s*(?:\(([^)]+)\))?", text)
    m_p2 = re.search(r"🥈\s*(?:\*\*)?([A-Za-z0-9\.\s]+?)(?:\*\*)?\s*(?:\(([^)]+)\))?", text)
    m_p3 = re.search(r"🥉\s*(?:\*\*)?([A-Za-z0-9\.\s]+?)(?:\*\*)?\s*(?:\(([^)]+)\))?", text)

    res["p1_driver"] = m_p1.group(1).strip() if m_p1 else ""
    res["p1_team"] = m_p1.group(2).strip() if m_p1 and m_p1.group(2) else ""
    res["p1_color"] = get_constructor_color(res["p1_team"])

    res["p2_driver"] = m_p2.group(1).strip() if m_p2 else ""
    res["p2_team"] = m_p2.group(2).strip() if m_p2 and m_p2.group(2) else ""
    res["p2_color"] = get_constructor_color(res["p2_team"])

    res["p3_driver"] = m_p3.group(1).strip() if m_p3 else ""
    res["p3_team"] = m_p3.group(2).strip() if m_p3 and m_p3.group(2) else ""
    res["p3_color"] = get_constructor_color(res["p3_team"])

    # Ratings Leaderboard Rows
    top_ratings_fallback: list[RatingRow] = []
    rating_pattern = re.compile(r"(?:^|\n)\|?\s*(\d{1,2})\s*\|?[\t\s]+([A-Za-z0-9\.\s]+?)\s*\|?[\t\s]+([A-Za-z0-9\s]+?)\s*\|?[\t\s]+(\d+\.?\d*)")
    for m in rating_pattern.finditer(text):
        rk, d, t, r = m.groups()
        try:
            r_val = float(r)
            pct = min(100, max(0, int(r_val)))
            team_str = t.strip()
            top_ratings_fallback.append(RatingRow(
                rank=f"P{rk}",
                driver=d.strip(),
                team=team_str,
                rating=f"{r_val:.1f}",
                pct=f"{pct}%",
                color=get_constructor_color(team_str),
            ))
        except Exception:
            continue
    res["top_ratings"] = top_ratings_fallback[:8]

    # Qualifying
    m_q1 = re.search(r"Front-Row Contenders.*?:?\s*([^\n]+)", text)
    m_q2 = re.search(r"Second-Row Contenders.*?:?\s*([^\n]+)", text)
    m_q3 = re.search(r"Top-10 Qualifiers.*?:?\s*([^\n]+)", text)
    m_q4 = re.search(r"Midfield.*?Rookies.*?:?\s*([^\n]+)", text)

    res["qual_front"] = m_q1.group(1).strip() if m_q1 else ""
    res["qual_second"] = m_q2.group(1).strip() if m_q2 else ""
    res["qual_top10"] = m_q3.group(1).strip() if m_q3 else ""
    res["qual_midfield"] = m_q4.group(1).strip() if m_q4 else ""

    return res


class AlternativeIntelligenceState(rx.State):
    """Reflex state managing the Alternative Intelligence sidebar drawer and query engine."""

    show_drawer: bool = False
    search_query: str = ""
    is_generating: bool = False
    error_message: str = ""
    messages: list[ChatMessage] = []
    selected_skill: str = "Skills Library"
    active_skill_badge: str = ""
    active_skill_infotip: str = ""

    def toggle_drawer(self):
        """Toggle the sidebar drawer open or closed."""
        self.show_drawer = not self.show_drawer
        if self.show_drawer and not self.messages:
            self.error_message = ""

    def open_drawer(self):
        """Explicitly open the drawer."""
        self.show_drawer = True

    def close_drawer(self):
        """Explicitly close the drawer."""
        self.show_drawer = False

    def set_search_query(self, query: str):
        """Update the input search bar value."""
        self.search_query = query

    def clear_chat(self):
        """Clear conversation history."""
        self.messages = []
        self.error_message = ""

    def handle_key_down(self, key: str):
        """Submit query on Enter without Shift."""
        if key == "Enter":
            return AlternativeIntelligenceState.submit_query

    def download_infographic_png(self, card_id: str, track_name: str):
        """Capture the visual infographic card in the browser and trigger a high-res .PNG file download."""
        safe_name = re.sub(r"[^A-Za-z0-9_\-]+", "_", track_name.strip()) if track_name else "Race_Infographic"
        filename = f"{safe_name}_Infographic.png"
        js_code = f"""
        (async () => {{
            const loadHtml2Canvas = () => new Promise((resolve, reject) => {{
                if (window.html2canvas) return resolve(window.html2canvas);
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
                script.onload = () => resolve(window.html2canvas);
                script.onerror = reject;
                document.head.appendChild(script);
            }});

            try {{
                const h2c = await loadHtml2Canvas();
                const card = document.getElementById('{card_id}');
                if (!card) {{
                    console.error('Infographic card element with ID {card_id} not found.');
                    return;
                }}

                const canvas = await h2c(card, {{
                    scale: 2,
                    useCORS: true,
                    backgroundColor: '#18181B',
                    logging: false,
                    ignoreElements: (el) => el.getAttribute('data-html2canvas-ignore') === 'true',
                }});

                const link = document.createElement('a');
                link.download = '{filename}';
                link.href = canvas.toDataURL('image/png');
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }} catch (err) {{
                console.error('Error generating infographic PNG:', err);
            }}
        }})();
        """
        return rx.call_script(js_code)

    def select_skill(self, skill_name: str):
        """Populate @<Skill Name> badge box into search bar without executing immediately."""
        if not skill_name or skill_name == "Skills Library":
            return
        if "Upcoming Race" in skill_name:
            self.active_skill_badge = "@Specific Upcoming Race Infographic "
            self.active_skill_infotip = "e.g., Monza, Spa, Brazil, or leave blank for next GP"
        elif "Qualifying" in skill_name:
            self.active_skill_badge = "@Seasonal Qualifying Comparison "
            self.active_skill_infotip = "e.g., Season 5, Season 4, or leave blank"
        elif "Head to Head" in skill_name or "H2H" in skill_name:
            self.active_skill_badge = "@Head to Head Comparison Infographic "
            self.active_skill_infotip = "e.g., Josh vs Jairo, or Ferrari vs Red Bull"
        elif "Champion" in skill_name:
            self.active_skill_badge = "@Champion Comparison Skill "
            self.active_skill_infotip = "e.g., S4 Mercedes vs S3 Alpine, or Joshua S4 vs Nick S3 (defaults to most recent constructor champion vs prior year)"
        else:
            self.active_skill_badge = f"@{skill_name} "
            self.active_skill_infotip = f"Expected inputs for {skill_name}"
        self.selected_skill = "Skills Library"

    def clear_active_skill(self):
        """Clear the active skill badge box and infotip."""
        self.active_skill_badge = ""
        self.active_skill_infotip = ""

    async def select_prompt(self, prompt_text: str) -> AsyncGenerator:
        """Select a suggested quick prompt and execute it immediately."""
        self.search_query = prompt_text
        async for step in self.submit_query():
            yield step

    async def submit_query(self) -> AsyncGenerator:
        """Execute the query against Gemini with Grounded League Context streaming."""
        from datetime import datetime, timezone

        user_input = self.search_query.strip()
        is_skill_request = bool(
            self.active_skill_badge
            or user_input.startswith("@")
            or "@Specific Upcoming Race Infographic" in user_input
            or "@Upcoming Race Infographic" in user_input
            or "@Seasonal Qualifying Comparison" in user_input
            or "@Head to Head Comparison Infographic" in user_input
            or "@Champion Comparison Skill" in user_input
        )


        badge_name = ""
        if self.active_skill_badge:
            badge_name = self.active_skill_badge.strip().lstrip("@")
            if not user_input.startswith("@"):
                query = f"{self.active_skill_badge}{user_input}".strip()
            else:
                query = user_input
        else:
            query = user_input
            if query.startswith("@"):
                for s_opt in SKILL_OPTIONS[1:]:
                    if query.startswith(f"@{s_opt}"):
                        badge_name = s_opt
                        break
                if not badge_name:
                    m_skill = re.match(r"^@([A-Za-z0-9\s]+?)(?:\s+(.*))?$", query)
                    if m_skill:
                        badge_name = m_skill.group(1).strip()

        if not query or self.is_generating:
            return

        now_iso = datetime.now(timezone.utc).isoformat()

        # Clean display content if a skill badge was extracted
        display_content = user_input
        if badge_name:
            if display_content.startswith(f"@{badge_name}"):
                display_content = display_content[len(f"@{badge_name}"):].strip()
            if not display_content:
                display_content = badge_name
        else:
            display_content = query

        # Append user query to conversation with ISO timestamp and persistent skill badge
        self.messages.append(ChatMessage(
            role="user",
            content=display_content,
            timestamp=now_iso,
            skill_badge=badge_name,
        ))
        self.search_query = ""
        self.active_skill_badge = ""
        self.active_skill_infotip = ""
        self.error_message = ""

        # Prepare placeholder assistant response
        self.messages.append(ChatMessage(
            role="assistant",
            content="",
            timestamp=now_iso,
        ))
        self.is_generating = True
        yield
        try:
            yield rx.call_script("""
                setTimeout(() => {
                    const anchor = document.getElementById('ai-chat-bottom-anchor');
                    if (anchor) {
                        anchor.scrollIntoView({ behavior: 'smooth' });
                    } else {
                        const feed = document.getElementById('ai-chat-feed');
                        if (feed) feed.scrollTop = feed.scrollHeight;
                    }
                }, 60);
            """)
        except Exception:
            pass


        # Custom Easter egg response for Captain Slow (Brently Season 3 Monaco winner)
        captain_slow_match = re.search(r"\bcaptain\s*slow\b", query, re.IGNORECASE)
        if captain_slow_match:
            self.messages[-1].content = (
                "Captain Slow is the undisputed Season 3 Monaco winner Brently! "
                "![Jeff Gordon NASCAR](/Icons/jeff_gordon_nascar.png)"
            )
            self.is_generating = False
            yield
            try:
                yield rx.call_script("""
                    setTimeout(() => {
                        const anchor = document.getElementById('ai-chat-bottom-anchor');
                        if (anchor) {
                            anchor.scrollIntoView({ behavior: 'smooth' });
                        } else {
                            const feed = document.getElementById('ai-chat-feed');
                            if (feed) feed.scrollTop = feed.scrollHeight;
                        }
                    }, 60);
                """)
            except Exception:
                pass
            return

        # Custom Easter egg response for poopy person / poopy head
        poopy_match = re.search(r"\b(poopy(?:\s+(?:person|head|[a-zA-Z0-9_-]+))?)\b", query, re.IGNORECASE)
        if poopy_match:
            raw_matched = poopy_match.group(1).strip()
            poopy_comment = "poopy person" if raw_matched.lower() == "poopy" else raw_matched
            matthew_wins = 0
            try:
                from the_alternative_f1.all_time_stats.Functions import CalculateAllTime
                all_time_df = CalculateAllTime(5, "Driver")
                if all_time_df is not None and not all_time_df.empty:
                    m_row = all_time_df[all_time_df["Driver"].str.strip().str.lower() == "matthew"]
                    if not m_row.empty:
                        matthew_wins = int(m_row.iloc[0].get("1st Place", 0))
            except Exception:
                matthew_wins = 0

            self.messages[-1].content = f"Matthew is a {poopy_comment} and has {matthew_wins} wins."
            self.is_generating = False
            yield
            yield rx.call_script("""
                setTimeout(() => {
                    const anchor = document.getElementById('ai-chat-bottom-anchor');
                    if (anchor) {
                        anchor.scrollIntoView({ behavior: 'smooth' });
                    } else {
                        const feed = document.getElementById('ai-chat-feed');
                        if (feed) feed.scrollTop = feed.scrollHeight;
                    }
                }, 60);
            """)
            return

        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            self.is_generating = False
            self.messages[-1].content = (
                "⚠️ **Gemini API Key Required**\n\n"
                "Please configure `GEMINI_API_KEY` in your `.env` or Reflex Cloud secrets to enable live responses."
            )
            yield
            return

        # Prepare Grounded League Context
        try:
            grounded_context = build_grounded_league_context()
        except Exception as e:
            grounded_context = f"Error extracting context: {str(e)}"

        skill_directive = ""
        if not is_skill_request:
            skill_directive = (
                "\n\n[USER DIRECTIVE: No specialized skill is selected. Respond conversationally using standard Markdown only. "
                "Do NOT output any ```infographic-json block, do NOT use specialized infographic structures, and do NOT construct preview cards.]"
            )

        prompt_payload = (
            f"LEAGUE GROUNDED CONTEXT:\n{grounded_context}\n\n"
            f"USER INQUIRY:\n{query}{skill_directive}"
        )

        # Call Google Gemini API (gemini-3.5-flash with gemini-3.5-flash-lite fallback)
        model_name = "gemini-3.5-flash"
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:streamGenerateContent?alt=sse&key={api_key}"

        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt_payload}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 4096,
            }
        }

        accumulated_text = ""
        global _WORKING_GEMINI_MODEL
        try:
            http_timeout = httpx.Timeout(120.0, connect=10.0, read=120.0, write=15.0, pool=10.0)
            async with httpx.AsyncClient(timeout=http_timeout) as client:
                # 1. Discover available models for this specific API key or use verified working models
                candidate_models = [
                    "gemini-3.5-flash-lite",
                    "gemini-3.8-flash",
                    "gemini-3.6-flash",
                    "gemini-3.1-flash-lite",
                    "gemini-flash-lite-latest",
                    "gemini-3-flash-preview",
                    "gemini-3.5-flash",
                ]
                if _WORKING_GEMINI_MODEL and _WORKING_GEMINI_MODEL in candidate_models:
                    candidate_models = [_WORKING_GEMINI_MODEL] + [m for m in candidate_models if m != _WORKING_GEMINI_MODEL]
                elif not _WORKING_GEMINI_MODEL:
                    try:
                        models_resp = await client.get(
                            f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
                            timeout=4.0,
                        )
                        if models_resp.status_code == 200:
                            discovered = [
                                m["name"].replace("models/", "")
                                for m in models_resp.json().get("models", [])
                                if "generateContent" in m.get("supportedGenerationMethods", [])
                                and not any(dep in m["name"] for dep in ["1.5", "2.0", "2.5"])
                            ]
                            if discovered:
                                flash_first = sorted(
                                    discovered,
                                    key=lambda x: (
                                        0 if "3.5-flash-lite" in x else
                                        1 if "3.8-flash" in x else
                                        2 if "3.6-flash" in x else
                                        3 if "flash-lite" in x else
                                        4 if "flash" in x.lower() else 5
                                    )
                                )
                                candidate_models = flash_first + [m for m in candidate_models if m not in flash_first]
                    except Exception:
                        pass

                # 2. Iterate through candidate models with per-candidate exception and timeout protection
                active_stream = None
                last_err = ""
                for model_candidate in candidate_models:
                    try:
                        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_candidate}:streamGenerateContent?alt=sse&key={api_key}"
                        req = client.build_request("POST", endpoint, json=body)
                        resp = await client.send(req, stream=True)
                        if resp.status_code == 200:
                            active_stream = resp
                            _WORKING_GEMINI_MODEL = model_candidate
                            break
                        else:
                            err_bytes = await resp.aread()
                            last_err = f"{model_candidate} ({resp.status_code}): {err_bytes.decode('utf-8', errors='ignore')[:120]}"
                            await resp.aclose()
                    except (httpx.TimeoutException, httpx.HTTPError, Exception) as cand_exc:
                        last_err = f"{model_candidate}: {str(cand_exc)}"
                        continue

                if not active_stream:
                    self.error_message = f"Could not connect to Gemini model: {last_err}"
                    self.messages[-1].content = (
                        "Sorry, I encountered an issue connecting to the Gemini model with this API key. "
                        "Please verify your key in Google AI Studio."
                    )
                    self.is_generating = False
                    yield
                    return

                async for line in active_stream.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk_json = json.loads(data_str)
                            candidates = chunk_json.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                for part in parts:
                                    text_delta = part.get("text", "")
                                    accumulated_text += text_delta

                                    # Sanitize displayed text so raw JSON block is never visible during streaming
                                    display_text = accumulated_text
                                    if "```infographic-json" in display_text or "```json" in display_text:
                                        # If block is completed, strip it
                                        display_text = re.sub(r"```(?:infographic-json|json)\s*\{.*?\}\s*```", "", display_text, flags=re.DOTALL).strip()
                                        # If block is still unclosed, hide everything from start of block
                                        display_text = re.sub(r"```(?:infographic-json|json).*$", "", display_text, flags=re.DOTALL).strip()

                                    self.messages[-1].content = display_text
                                    yield
                        except Exception:
                            continue
                await active_stream.aclose()

                # Check if an infographic was generated and extract structured visual fields
                info_data = extract_infographic_data(accumulated_text, skill_selected=is_skill_request)
                if info_data and info_data.get("is_infographic"):
                    clean_text = info_data.get("clean_content", accumulated_text)
                    unique_card_id = f"infographic-card-{int(time.time() * 1000)}"
                    self.messages[-1] = ChatMessage(
                        role="assistant",
                        content=clean_text,
                        timestamp=now_iso,
                        is_infographic=True,
                        card_id=unique_card_id,
                        infographic_type=info_data.get("infographic_type", "race"),
                        track_name=info_data.get("track_name", "Grand Prix Preview"),
                        expected_winner=info_data.get("expected_winner", ""),
                        expected_winner_team=info_data.get("expected_winner_team", ""),
                        winner_color=info_data.get("winner_color", "#555555"),
                        winner_text_color=info_data.get("winner_text_color", "#FFFFFF"),
                        p1_driver=info_data.get("p1_driver", ""),
                        p1_team=info_data.get("p1_team", ""),
                        p1_color=info_data.get("p1_color", "#555555"),
                        p1_text_color=info_data.get("p1_text_color", "#FFFFFF"),
                        p2_driver=info_data.get("p2_driver", ""),
                        p2_team=info_data.get("p2_team", ""),
                        p2_color=info_data.get("p2_color", "#555555"),
                        p2_text_color=info_data.get("p2_text_color", "#FFFFFF"),
                        p3_driver=info_data.get("p3_driver", ""),
                        p3_team=info_data.get("p3_team", ""),
                        p3_color=info_data.get("p3_color", "#555555"),
                        p3_text_color=info_data.get("p3_text_color", "#FFFFFF"),
                        top_ratings=info_data.get("top_ratings", []),
                        qual_front=info_data.get("qual_front", ""),
                        qual_second=info_data.get("qual_second", ""),
                        qual_top10=info_data.get("qual_top10", ""),
                        qual_midfield=info_data.get("qual_midfield", ""),
                        season_title=info_data.get("season_title", "Season 5 Teammate Qualifying Battles"),
                        seasonal_qual_rows=info_data.get("seasonal_qual_rows", []),
                        h2h_name1=info_data.get("h2h_name1", ""),
                        h2h_name2=info_data.get("h2h_name2", ""),
                        h2h_team1=info_data.get("h2h_team1", ""),
                        h2h_team2=info_data.get("h2h_team2", ""),
                        h2h_color1=info_data.get("h2h_color1", "#00b4da"),
                        h2h_color2=info_data.get("h2h_color2", "#ffffff"),
                        h2h_text_color1=info_data.get("h2h_text_color1", "#ffffff"),
                        h2h_text_color2=info_data.get("h2h_text_color2", "#000000"),
                        h2h_seasons=info_data.get("h2h_seasons", ""),
                        h2h_teammates1=info_data.get("h2h_teammates1", ""),
                        h2h_teammates2=info_data.get("h2h_teammates2", ""),
                        h2h_stats=info_data.get("h2h_stats", []),
                        champ_season1=info_data.get("champ_season1", "Season 4"),
                        champ_season2=info_data.get("champ_season2", "Season 3"),
                        champ_name1=info_data.get("champ_name1", ""),
                        champ_name2=info_data.get("champ_name2", ""),
                        champ_type1=info_data.get("champ_type1", "Constructor"),
                        champ_type2=info_data.get("champ_type2", "Constructor"),
                        champ_team1=info_data.get("champ_team1", ""),
                        champ_team2=info_data.get("champ_team2", ""),
                        champ_color1=info_data.get("champ_color1", "#00b4da"),
                        champ_color2=info_data.get("champ_color2", "#ffffff"),
                        champ_text_color1=info_data.get("champ_text_color1", "#ffffff"),
                        champ_text_color2=info_data.get("champ_text_color2", "#000000"),
                        champ_runner_up1=info_data.get("champ_runner_up1", ""),
                        champ_runner_up2=info_data.get("champ_runner_up2", ""),
                        champ_entities=info_data.get("champ_entities", []),
                        champ_stats=info_data.get("champ_stats", []),
                    )
                    self.messages = list(self.messages)
                    yield
                else:
                    # Sanitize in case an unclosed JSON block lingered without triggering full infographic
                    display_text = accumulated_text
                    if "```infographic-json" in display_text or "```json" in display_text:
                        display_text = re.sub(r"```(?:infographic-json|json)\s*\{.*?\}\s*```", "", display_text, flags=re.DOTALL).strip()
                        display_text = re.sub(r"```(?:infographic-json|json).*$", "", display_text, flags=re.DOTALL).strip()
                    self.messages[-1].content = display_text
                    yield

            if not accumulated_text:
                self.messages[-1].content = "No response generated. Please refine your query."
                yield

        except httpx.TimeoutException:
            self.error_message = "Request timed out. Please try asking again."
            self.messages[-1].content = "The inquiry timed out while evaluating league statistics. Please retry."
            yield
        except Exception as e:
            self.error_message = f"Communication error: {str(e)}"
            self.messages[-1].content = f"An error occurred while connecting to Alternative Intelligence: {str(e)}"
            yield
        finally:
            self.is_generating = False
            yield
            try:
                yield rx.call_script("""
                    setTimeout(() => {
                        const anchor = document.getElementById('ai-chat-bottom-anchor');
                        if (anchor) {
                            anchor.scrollIntoView({ behavior: 'smooth' });
                        } else {
                            const feed = document.getElementById('ai-chat-feed');
                            if (feed) feed.scrollTop = feed.scrollHeight;
                        }
                    }, 60);
                """)
            except Exception:
                pass



# ==============================================================================
# UI COMPONENTS
# ==============================================================================

def ai_logo(size: str = "24px", border_radius: str = "sm") -> rx.Component:
    """The Alternative F1 IconLogo with rainbow bokeh background matching the official icon."""
    return rx.box(
        rx.image(
            src="/Icons/IconLogo.png",
            height=size,
            width=size,
            object_fit="contain",
        ),
        background="radial-gradient(circle at 20% 25%, #E60049 0%, transparent 55%), radial-gradient(circle at 80% 25%, #FF8C00 0%, transparent 50%), radial-gradient(circle at 20% 80%, #7B00FF 0%, transparent 55%), radial-gradient(circle at 80% 80%, #0099FF 0%, transparent 50%), #121214",
        border_radius=border_radius,
        display="flex",
        align_items="center",
        justify_content="center",
        padding="2px",
    )


def gemini_trigger_button() -> rx.Component:
    """Alternative Intelligence trigger button with IconLogo on rainbow bokeh background pinned to far left.
    
    Styled per TAF1APP-SDDREQ-230 (V6) as a square button with heavily rounded corners and rainbow bokeh background,
    sized ~15% smaller than the 36px navigation button squares.
    """
    return rx.button(
        rx.image(
            src="/Icons/IconLogo.png",
            height="18px",
            width="18px",
            object_fit="contain",
        ),
        background="radial-gradient(circle at 20% 25%, #E60049 0%, transparent 55%), radial-gradient(circle at 80% 25%, #FF8C00 0%, transparent 50%), radial-gradient(circle at 20% 80%, #7B00FF 0%, transparent 55%), radial-gradient(circle at 80% 80%, #0099FF 0%, transparent 50%), #121214",
        border=rx.cond(
            AlternativeIntelligenceState.show_drawer,
            "2px solid white",
            "1px solid rgba(255, 255, 255, 0.4)"
        ),
        box_shadow=rx.cond(
            AlternativeIntelligenceState.show_drawer,
            "0 0 15px rgba(255, 0, 128, 0.8), 0 0 25px rgba(0, 180, 218, 0.6)",
            "0 2px 8px rgba(0, 0, 0, 0.5), 0 0 10px rgba(0, 180, 218, 0.3)"
        ),
        border_radius="9px",
        width="30px",
        height="30px",
        min_width="30px",
        max_width="30px",
        on_click=AlternativeIntelligenceState.toggle_drawer,
        _hover={
            "transform": "scale(1.08)",
            "box_shadow": "0 0 15px rgba(255, 0, 128, 0.7), 0 0 25px rgba(0, 180, 218, 0.6)",
        },
        cursor="pointer",
        padding="0",
        position="absolute",
        left="16px",
        z_index="102",
        title="Alternative Intelligence",
    )


def rating_bar_row(row: RatingRow) -> rx.Component:
    """Render a single driver row in the track rating leaderboard with proportional progress bar."""
    return rx.hstack(
        rx.text(row.rank, font_size="10px", font_weight="bold", color="#71717A", width="22px"),
        rx.text(row.driver, font_size="12px", font_weight="semibold", color="white", width="65px", no_of_lines=1),
        rx.badge(
            row.team,
            bg=row.color,
            color=row.text_color,
            border="1px solid rgba(255, 255, 255, 0.4)",
            font_size="9px",
            width="65px",
            justify="center",
        ),
        rx.box(
            rx.box(
                width=row.pct,
                bg=row.color,
                border="1px solid rgba(255, 255, 255, 0.4)",
                height="7px",
                border_radius="full",
                box_shadow="0 0 4px rgba(255, 255, 255, 0.25)",
            ),
            bg="#27272A",
            border_radius="full",
            height="7px",
            flex="1",
            overflow="hidden",
        ),
        rx.text(row.rating, font_size="11px", font_weight="bold", color="white", width="32px", text_align="right"),
        spacing="2",
        align="center",
        width="100%",
    )


def native_race_infographic_card(msg: ChatMessage) -> rx.Component:
    """Rich native Reflex visual infographic card rendering 4-part race preview analytics."""
    return rx.box(
        # Rainbow top highlight line
        rx.box(
            width="100%",
            height="3px",
            background="linear-gradient(90deg, #E60049 0%, #FF8C00 28%, #FFE500 50%, #00B4D8 75%, #7B00FF 100%)",
            border_radius="full",
            margin_bottom="12px",
        ),
        # Circuit & Grand Prix Header
        rx.hstack(
            rx.hstack(
                rx.icon("flag", size=18, color="#00b4da"),
                rx.text(
                    msg.track_name,
                    font_size="14px",
                    font_weight="bold",
                    color="white",
                    letter_spacing="-0.02em",
                ),
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            rx.hstack(
                rx.badge("OFFICIAL INFOGRAPHIC", color_scheme="cyan", variant="solid", font_size="9px", font_weight="bold"),
                rx.button(
                    rx.hstack(
                        rx.icon("download", size=12),
                        rx.text("PNG", font_size="10px", font_weight="bold"),
                        spacing="1",
                        align="center",
                    ),
                    size="1",
                    variant="surface",
                    color_scheme="cyan",
                    on_click=AlternativeIntelligenceState.download_infographic_png(msg.card_id, msg.track_name),
                    cursor="pointer",
                    title="Download Infographic as .PNG",
                    custom_attrs={"data-html2canvas-ignore": "true"},
                ),
                spacing="2",
                align="center",
            ),
            width="100%",
            align="center",
            margin_bottom="12px",
        ),
        # Expected Winner Spotlight Bar
        rx.cond(
            msg.expected_winner != "",
            rx.hstack(
                rx.icon("trophy", size=16, color="#FFD700"),
                rx.text("EXPECTED WINNER:", font_size="10px", font_weight="bold", color="#A1A1AA", letter_spacing="0.05em"),
                rx.text(msg.expected_winner, font_size="12px", font_weight="bold", color="white"),
                rx.cond(
                    msg.expected_winner_team != "",
                    rx.badge(msg.expected_winner_team, bg=msg.winner_color, color=msg.winner_text_color, font_size="9px", font_weight="bold"),
                    rx.fragment(),
                ),
                spacing="2",
                align="center",
                width="100%",
                padding="8px 12px",
                bg="rgba(255, 215, 0, 0.08)",
                border="1px solid rgba(255, 215, 0, 0.25)",
                border_radius="md",
                margin_bottom="12px",
            ),
            rx.fragment(),
        ),
        # 3-Step Elevated Podium Display
        rx.cond(
            (msg.p1_driver != "") | (msg.p2_driver != "") | (msg.p3_driver != ""),
            rx.vstack(
                rx.hstack(
                    rx.icon("award", size=14, color="#EAB308"),
                    rx.text("Projected Podium", font_size="11px", font_weight="bold", color="#E4E4E7"),
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    # 2nd Place (Silver)
                    rx.vstack(
                        rx.text(msg.p2_driver, font_size="11px", font_weight="bold", color="white", no_of_lines=1, text_align="center"),
                        rx.cond(
                            msg.p2_team != "",
                            rx.badge(msg.p2_team, bg=msg.p2_color, color=msg.p2_text_color, font_size="8px", max_width="80px"),
                            rx.fragment(),
                        ),
                        rx.box(
                            rx.text("2", font_size="20px", font_weight="900", color="white"),
                            width="100%",
                            height="55px",
                            background="linear-gradient(180deg, #94A3B8 0%, #475569 100%)",
                            border_radius="6px 6px 0 0",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            box_shadow="0 -3px 10px rgba(148, 163, 184, 0.25)",
                        ),
                        align="center",
                        spacing="1",
                        flex="1",
                    ),
                    # 1st Place (Gold Elevated)
                    rx.vstack(
                        rx.icon("crown", size=16, color="#FFD700"),
                        rx.text(msg.p1_driver, font_size="12px", font_weight="bold", color="#FFD700", no_of_lines=1, text_align="center"),
                        rx.cond(
                            msg.p1_team != "",
                            rx.badge(msg.p1_team, bg=msg.p1_color, color=msg.p1_text_color, font_size="9px", max_width="90px"),
                            rx.fragment(),
                        ),
                        rx.box(
                            rx.text("1", font_size="26px", font_weight="900", color="white"),
                            width="100%",
                            height="80px",
                            background="linear-gradient(180deg, #F59E0B 0%, #B45309 100%)",
                            border_radius="6px 6px 0 0",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            box_shadow="0 -4px 14px rgba(245, 158, 11, 0.4)",
                        ),
                        align="center",
                        spacing="1",
                        flex="1.1",
                    ),
                    # 3rd Place (Bronze)
                    rx.vstack(
                        rx.text(msg.p3_driver, font_size="11px", font_weight="bold", color="white", no_of_lines=1, text_align="center"),
                        rx.cond(
                            msg.p3_team != "",
                            rx.badge(msg.p3_team, bg=msg.p3_color, color=msg.p3_text_color, font_size="8px", max_width="80px"),
                            rx.fragment(),
                        ),
                        rx.box(
                            rx.text("3", font_size="18px", font_weight="900", color="white"),
                            width="100%",
                            height="42px",
                            background="linear-gradient(180deg, #D97706 0%, #78350F 100%)",
                            border_radius="6px 6px 0 0",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            box_shadow="0 -3px 8px rgba(217, 119, 6, 0.25)",
                        ),
                        align="center",
                        spacing="1",
                        flex="1",
                    ),
                    justify="center",
                    align="end",
                    spacing="2",
                    width="100%",
                    padding_top="6px",
                ),
                width="100%",
                padding="10px",
                bg="#141416",
                border="1px solid #27272A",
                border_radius="md",
                margin_bottom="12px",
            ),
            rx.fragment(),
        ),
        # Track Rating Leaderboard Progress Bars
        rx.cond(
            msg.top_ratings.length() > 0,
            rx.vstack(
                rx.hstack(
                    rx.icon("chart-bar", size=14, color="#00b4da"),
                    rx.text("Statistical Track Rating Leaderboard (0–100 Scale)", font_size="11px", font_weight="bold", color="#E4E4E7"),
                    spacing="1",
                    align="center",
                ),
                rx.vstack(
                    rx.foreach(msg.top_ratings, rating_bar_row),
                    spacing="2",
                    width="100%",
                    padding="10px",
                    bg="#141416",
                    border="1px solid #27272A",
                    border_radius="md",
                ),
                width="100%",
                spacing="2",
                margin_bottom="12px",
            ),
            rx.fragment(),
        ),
        # Qualifying Grid Tiers
        rx.cond(
            (msg.qual_front != "") | (msg.qual_second != ""),
            rx.vstack(
                rx.hstack(
                    rx.icon("timer", size=14, color="#A855F7"),
                    rx.text("All-Time Qualifying & Projected Grid", font_size="11px", font_weight="bold", color="#E4E4E7"),
                    spacing="1",
                    align="center",
                ),
                rx.vstack(
                    rx.cond(
                        msg.qual_front != "",
                        rx.hstack(
                            rx.badge("ROW 1 (P1-P2)", bg="#22C55E", color="black", font_size="9px", font_weight="bold", width="90px", justify="center"),
                            rx.text(msg.qual_front, font_size="11px", color="white", flex="1"),
                            spacing="2",
                            align="center",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        msg.qual_second != "",
                        rx.hstack(
                            rx.badge("ROW 2 (P3-P4)", bg="#3B82F6", color="white", font_size="9px", font_weight="bold", width="90px", justify="center"),
                            rx.text(msg.qual_second, font_size="11px", color="white", flex="1"),
                            spacing="2",
                            align="center",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        msg.qual_top10 != "",
                        rx.hstack(
                            rx.badge("TOP 10 (P5-P10)", bg="#A855F7", color="white", font_size="9px", font_weight="bold", width="90px", justify="center"),
                            rx.text(msg.qual_top10, font_size="11px", color="white", flex="1"),
                            spacing="2",
                            align="center",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        msg.qual_midfield != "",
                        rx.hstack(
                            rx.badge("MIDFIELD (P11-16)", bg="#71717A", color="white", font_size="9px", font_weight="bold", width="90px", justify="center"),
                            rx.text(msg.qual_midfield, font_size="11px", color="white", flex="1"),
                            spacing="2",
                            align="center",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    spacing="2",
                    width="100%",
                    padding="10px",
                    bg="#141416",
                    border="1px solid #27272A",
                    border_radius="md",
                ),
                width="100%",
                spacing="2",
                margin_bottom="8px",
            ),
            rx.fragment(),
        ),
        id=msg.card_id,
        background="linear-gradient(145deg, #18181B 0%, #1f1f24 100%)",
        border="1px solid #3F3F46",
        border_radius="lg",
        padding="14px",
        width="100%",
        box_shadow="0 8px 24px rgba(0, 0, 0, 0.4)",
        margin_bottom="12px",
    )


def comparison_bar_row(row: ComparisonStatRow) -> rx.Component:
    """Render an individual metric comparison row with opposing dual-contrast horizontal bars."""
    return rx.vstack(
        # Centered metric label
        rx.text(
            row.metric,
            font_size="10px",
            font_weight="800",
            color="#A1A1AA",
            letter_spacing="0.1em",
            text_align="center",
            width="100%",
        ),
        # Dual-sided bar and numerical scores
        rx.hstack(
            # Driver 1 Value
            rx.text(
                row.val1,
                font_size="18px",
                font_weight="900",
                color=row.color1,
                width="70px",
                white_space="nowrap",
                text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                text_align="left",
            ),
            # Opposing Progress Bars Container
            rx.hstack(
                # Left bar (Driver 1 - grows right to center or fills left side)
                rx.box(
                    rx.box(
                        width=row.pct1,
                        height="14px",
                        bg=row.color1,
                        border="1px solid rgba(255, 255, 255, 0.45)",
                        border_radius="2px 0 0 2px",
                    ),
                    width="100%",
                    height="14px",
                    bg="#27272A",
                    display="flex",
                    justify_content="flex-end",
                    overflow="hidden",
                    flex="1",
                ),
                # Vertical Center Separator
                rx.box(width="2px", height="18px", bg="#18181B"),
                # Right bar (Driver 2 - grows left to right from center)
                rx.box(
                    rx.box(
                        width=row.pct2,
                        height="14px",
                        bg=row.color2,
                        border="1px solid rgba(255, 255, 255, 0.45)",
                        border_radius="0 2px 2px 0",
                    ),
                    width="100%",
                    height="14px",
                    bg="#27272A",
                    display="flex",
                    justify_content="flex-start",
                    overflow="hidden",
                    flex="1",
                ),
                spacing="0",
                align="center",
                flex="1",
                bg="#18181B",
                border_radius="4px",
                border="1px solid #3F3F46",
                overflow="hidden",
            ),
            # Driver 2 Value
            rx.text(
                row.val2,
                font_size="18px",
                font_weight="900",
                color=row.color2,
                width="70px",
                white_space="nowrap",
                text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                text_align="right",
            ),
            width="100%",
            align="center",
            spacing="2",
        ),
        # Subtle horizontal divider line
        rx.box(width="100%", height="1px", bg="#27272A", margin_y="4px"),
        spacing="1",
        width="100%",
    )


def native_h2h_infographic_card(msg: ChatMessage) -> rx.Component:
    """Rich native Reflex Head-to-Head Comparison Card (TAF1APP-SDDREQ-247) matching the mockup."""
    return rx.box(
        # Rainbow top highlight line
        rx.box(
            width="100%",
            height="3px",
            background="linear-gradient(90deg, #E60049 0%, #FF8C00 28%, #FFE500 50%, #00B4D8 75%, #7B00FF 100%)",
            border_radius="full",
            margin_bottom="12px",
        ),
        # Header with Download Button
        rx.hstack(
            rx.hstack(
                rx.icon("swords", size=16, color="#00b4da"),
                rx.text("HEAD TO HEAD COMPARISON", font_size="12px", font_weight="bold", color="white", letter_spacing="0.05em"),
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            rx.button(
                rx.hstack(
                    rx.icon("download", size=12),
                    rx.text("PNG", font_size="10px", font_weight="bold"),
                    spacing="1",
                    align="center",
                ),
                size="1",
                variant="surface",
                color_scheme="cyan",
                on_click=AlternativeIntelligenceState.download_infographic_png(msg.card_id, f"{msg.h2h_name1}_vs_{msg.h2h_name2}_H2H"),
                cursor="pointer",
                title="Download Infographic as .PNG",
                custom_attrs={"data-html2canvas-ignore": "true"},
            ),
            width="100%",
            align="center",
            margin_bottom="10px",
        ),
        # Driver 1 vs. Driver 2 Header with The Alternative F1 NEW Logo in Center
        rx.hstack(
            # Driver 1 (Left)
            rx.vstack(
                rx.text(
                    msg.h2h_name1,
                    font_size="15px",
                    font_weight="900",
                    color=msg.h2h_color1,
                    text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                    letter_spacing="-0.02em",
                    no_of_lines=1,
                ),
                rx.cond(
                    msg.h2h_team1 != "",
                    rx.badge(
                        msg.h2h_team1,
                        bg=msg.h2h_color1,
                        color=msg.h2h_text_color1,
                        border="1px solid rgba(255, 255, 255, 0.4)",
                        font_size="8px",
                        font_weight="bold",
                    ),
                    rx.fragment(),
                ),
                align="start",
                spacing="1",
                flex="1",
            ),
            # Center Circle with The Alternative F1 NEW Logo (Replaces F1 logo)
            rx.box(
                rx.image(
                    src="/The Alternative F1 NEW Logo.png",
                    height="32px",
                    width="32px",
                    object_fit="contain",
                ),
                background="radial-gradient(circle, #27272A 0%, #18181B 100%)",
                border="2px solid #00b4da",
                border_radius="full",
                padding="4px",
                display="flex",
                align_items="center",
                justify_content="center",
                box_shadow="0 0 12px rgba(0, 180, 218, 0.4)",
            ),
            # Driver 2 (Right)
            rx.vstack(
                rx.text(
                    msg.h2h_name2,
                    font_size="15px",
                    font_weight="900",
                    color=msg.h2h_color2,
                    text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                    letter_spacing="-0.02em",
                    no_of_lines=1,
                    text_align="right",
                ),
                rx.cond(
                    msg.h2h_team2 != "",
                    rx.badge(
                        msg.h2h_team2,
                        bg=msg.h2h_color2,
                        color=msg.h2h_text_color2,
                        border="1px solid rgba(255, 255, 255, 0.4)",
                        font_size="8px",
                        font_weight="bold",
                    ),
                    rx.fragment(),
                ),
                align="end",
                spacing="1",
                flex="1",
            ),
            width="100%",
            align="center",
            padding="12px",
            bg="#141416",
            border="1px solid #27272A",
            border_radius="md",
            margin_bottom="12px",
        ),
        # Metric Comparison Rows
        rx.vstack(
            rx.foreach(msg.h2h_stats, comparison_bar_row),
            width="100%",
            spacing="1",
            margin_bottom="12px",
        ),
        # Footer: Shared Seasons & Teammate History
        rx.vstack(
            rx.cond(
                msg.h2h_seasons != "",
                rx.hstack(
                    rx.icon("calendar", size=12, color="#A1A1AA"),
                    rx.text("Seasons in League:", font_size="10px", font_weight="bold", color="#A1A1AA"),
                    rx.text(msg.h2h_seasons, font_size="10px", color="white", font_weight="semibold"),
                    spacing="1",
                    align="center",
                    width="100%",
                ),
                rx.fragment(),
            ),
            rx.cond(
                msg.h2h_teammates1 != "",
                rx.hstack(
                    rx.icon("users", size=12, color="#00b4da"),
                    rx.hstack(
                        rx.text(msg.h2h_name1, font_size="10px", font_weight="bold", color="#A1A1AA"),
                        rx.text(rx.cond(msg.h2h_is_constructor, "Drivers:", "Teammates:"), font_size="10px", font_weight="bold", color="#A1A1AA"),
                        spacing="1",
                    ),
                    rx.text(msg.h2h_teammates1, font_size="10px", color="#E4E4E7"),
                    spacing="1",
                    align="center",
                    width="100%",
                ),
                rx.fragment(),
            ),
            rx.cond(
                msg.h2h_teammates2 != "",
                rx.hstack(
                    rx.icon("users", size=12, color="#FFFFFF"),
                    rx.hstack(
                        rx.text(msg.h2h_name2, font_size="10px", font_weight="bold", color="#A1A1AA"),
                        rx.text(rx.cond(msg.h2h_is_constructor, "Drivers:", "Teammates:"), font_size="10px", font_weight="bold", color="#A1A1AA"),
                        spacing="1",
                    ),
                    rx.text(msg.h2h_teammates2, font_size="10px", color="#E4E4E7"),
                    spacing="1",
                    align="center",
                    width="100%",
                ),
                rx.fragment(),
            ),
            # Bottom Center League Logo (Replaces F1 badge in mockup footer)
            rx.center(
                rx.image(
                    src="/The Alternative F1 NEW Logo.png",
                    height="26px",
                    object_fit="contain",
                ),
                width="100%",
                padding_top="8px",
            ),
            spacing="1",
            width="100%",
            padding="10px",
            bg="#141416",
            border="1px solid #27272A",
            border_radius="md",
        ),
        id=msg.card_id,
        background="linear-gradient(145deg, #111113 0%, #18181B 100%)",
        border="1px solid #3F3F46",
        border_radius="lg",
        padding="14px",
        width="100%",
        box_shadow="0 8px 24px rgba(0, 0, 0, 0.4)",
        margin_bottom="12px",
    )


def seasonal_qual_row_item(row: TeammateQualRow) -> rx.Component:
    """Render an individual team's qualifying head-to-head battle row matching the official mockup."""
    return rx.box(
        rx.hstack(
            # Left: Huge Driver 1 Score + Driver 1 Name
            rx.hstack(
                rx.text(
                    row.score_display1,
                    font_size="28px",
                    font_weight="900",
                    color=row.text_color,
                    width="42px",
                    text_align="left",
                    line_height="1",
                ),
                rx.text(
                    row.driver1,
                    font_size="13px",
                    font_weight="800",
                    color=row.text_color,
                    letter_spacing="0.06em",
                    no_of_lines=1,
                ),
                spacing="2",
                align="center",
                flex="1",
            ),
            # Center: Team Monogram / Name Pill (no team logos per instructions)
            rx.box(
                rx.text(
                    row.team,
                    font_size="11px",
                    font_weight="900",
                    letter_spacing="0.1em",
                    color=row.text_color,
                    text_align="center",
                    text_transform="uppercase",
                ),
                padding_x="10px",
                padding_y="4px",
                bg="rgba(0, 0, 0, 0.28)",
                border_radius="sm",
                border=rx.cond(row.text_color == "#000000", "1px solid rgba(0,0,0,0.3)", "1px solid rgba(255,255,255,0.2)"),
                display="flex",
                align_items="center",
                justify_content="center",
                min_width="90px",
            ),
            # Right: Driver 2 Name + Huge Driver 2 Score
            rx.hstack(
                rx.text(
                    row.driver2,
                    font_size="13px",
                    font_weight="800",
                    color=row.text_color,
                    letter_spacing="0.06em",
                    no_of_lines=1,
                    text_align="right",
                ),
                rx.text(
                    row.score_display2,
                    font_size="28px",
                    font_weight="900",
                    color=row.text_color,
                    width="42px",
                    text_align="right",
                    line_height="1",
                ),
                spacing="2",
                align="center",
                justify="end",
                flex="1",
            ),
            width="100%",
            align="center",
            padding_x="14px",
            padding_y="10px",
        ),
        width="100%",
        bg=row.team_color,
        border="1px solid rgba(255, 255, 255, 0.35)",
        border_radius="4px",
        margin_bottom="3px",
    )


def native_seasonal_qual_infographic_card(msg: ChatMessage) -> rx.Component:
    """Rich native Reflex Seasonal Qualifying Battles Card (TAF1APP-SDDREQ-249) matching the mockup."""
    return rx.box(
        # Rainbow top highlight line
        rx.box(
            width="100%",
            height="3px",
            background="linear-gradient(90deg, #E60049 0%, #FF8C00 28%, #FFE500 50%, #00B4D8 75%, #7B00FF 100%)",
            border_radius="full",
            margin_bottom="12px",
        ),
        # Action Bar (Download Button)
        rx.hstack(
            rx.badge("OFFICIAL LEAGUE DOSSIER", color_scheme="cyan", variant="solid", font_size="9px", font_weight="bold"),
            rx.spacer(),
            rx.button(
                rx.hstack(
                    rx.icon("download", size=12),
                    rx.text("PNG", font_size="10px", font_weight="bold"),
                    spacing="1",
                    align="center",
                ),
                size="1",
                variant="surface",
                color_scheme="cyan",
                on_click=AlternativeIntelligenceState.download_infographic_png(msg.card_id, "Seasonal_Qualifying_Head_to_Head"),
                cursor="pointer",
                title="Download Infographic as .PNG",
                custom_attrs={"data-html2canvas-ignore": "true"},
            ),
            width="100%",
            align="center",
            margin_bottom="10px",
        ),
        # Top Card Header Block: Off-white high-contrast title matching the mockup
        rx.vstack(
            # Center Top League Logo (The Alternative F1 NEW Logo)
            rx.image(
                src="/The Alternative F1 NEW Logo.png",
                height="38px",
                object_fit="contain",
                margin_bottom="2px",
            ),
            # Huge QUALIFYING title
            rx.text(
                "QUALIFYING",
                font_size=["28px", "34px", "38px"],
                font_weight="900",
                color="#0F172A",
                letter_spacing="-0.02em",
                line_height="1",
                text_align="center",
            ),
            # HEAD - TO - HEAD red subtitle with wide tracking
            rx.text(
                "H E A D - T O - H E A D",
                font_size="12px",
                font_weight="900",
                color="#E11D48",
                letter_spacing="0.32em",
                text_align="center",
                margin_top="2px",
            ),
            # Season badge
            rx.badge(
                msg.season_title,
                bg="#E2E8F0",
                color="#334155",
                font_size="9px",
                font_weight="bold",
                margin_top="6px",
            ),
            spacing="1",
            align="center",
            width="100%",
            padding_top="18px",
            padding_bottom="14px",
            padding_x="12px",
            bg="linear-gradient(180deg, #F8FAFC 0%, #EDE9FE 100%)",
            border_radius="md md 0 0",
            border_bottom="3px solid #0F172A",
        ),
        # Solid Full-Bleed Team Rows (Stacked in Constructor Championship Order)
        rx.box(
            rx.foreach(msg.seasonal_qual_rows, seasonal_qual_row_item),
            width="100%",
            overflow="hidden",
            box_shadow="0 4px 12px rgba(0, 0, 0, 0.5)",
        ),
        # Bottom League Branding Footer
        rx.center(
            rx.hstack(
                rx.image(
                    src="/The Alternative F1 NEW Logo.png",
                    height="20px",
                    object_fit="contain",
                ),
                rx.text("THE ALTERNATIVE F1 • OFFICIAL QUALIFYING TELEMETRY", font_size="9px", font_weight="bold", color="#71717A", letter_spacing="0.05em"),
                spacing="2",
                align="center",
            ),
            width="100%",
            padding_y="10px",
            bg="#141416",
            border_radius="0 0 md md",
            border_top="1px solid #27272A",
        ),
        id=msg.card_id,
        background="#18181B",
        border="1px solid #3F3F46",
        border_radius="lg",
        padding="12px",
        width="100%",
        box_shadow="0 10px 30px rgba(0, 0, 0, 0.6)",
        margin_bottom="12px",
    )


def champion_entity_badge_card(entity: ChampionEntity) -> rx.Component:
    """Render an individual champion card in the multi-champion header grid."""
    return rx.box(
        rx.vstack(
            rx.badge(
                f"🏆 {entity.season} {entity.type}",
                bg="rgba(245, 158, 11, 0.15)",
                color="#F59E0B",
                border="1px solid rgba(245, 158, 11, 0.4)",
                font_size="8px",
                font_weight="bold",
                padding_x="6px",
                padding_y="1px",
            ),
            rx.text(
                entity.name,
                font_size="13px",
                font_weight="900",
                color=entity.color,
                text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                letter_spacing="-0.01em",
                no_of_lines=1,
            ),
            rx.cond(
                entity.team != "",
                rx.badge(
                    entity.team,
                    bg=entity.color,
                    color=entity.text_color,
                    border="1px solid rgba(255, 255, 255, 0.4)",
                    font_size="7px",
                    font_weight="bold",
                ),
                rx.fragment(),
            ),
            align="center",
            spacing="1",
        ),
        bg="#18181B",
        border="1px solid #27272A",
        border_radius="md",
        padding="8px",
        flex="1",
        min_width=["110px", "120px", "130px"],
        text_align="center",
    )


def champion_metric_segment_box(seg: ChampionMetricSegment) -> rx.Component:
    """Render an individual segment inside the 100% stacked bar chart."""
    return rx.box(
        rx.text(
            seg.pct,
            font_size="10px",
            font_weight="900",
            color=seg.text_color,
            letter_spacing="-0.02em",
            no_of_lines=1,
        ),
        width=seg.pct,
        height="22px",
        bg=seg.color,
        display="flex",
        align_items="center",
        justify_content="center",
        border_right="2px solid #121214",
        overflow="hidden",
    )


def champion_metric_header_chip(seg: ChampionMetricSegment) -> rx.Component:
    """Render an individual entity value chip in the metric row header."""
    return rx.hstack(
        rx.box(width="8px", height="8px", border_radius="full", bg=seg.color),
        rx.text(f"{seg.entity_name} ({seg.season}):", font_size="10px", font_weight="bold", color="#A1A1AA"),
        rx.text(seg.val, font_size="12px", font_weight="900", color=seg.color, text_shadow="0 0 1px rgba(255,255,255,0.7)"),
        spacing="1",
        align="center",
    )


def champion_metric_subtext_chip(seg: ChampionMetricSegment) -> rx.Component:
    """Render an individual entity sub-detail badge."""
    return rx.cond(
        seg.sub_text != "",
        rx.badge(
            f"{seg.entity_name}: {seg.sub_text}",
            font_size="8px",
            font_weight="bold",
            bg="rgba(255, 255, 255, 0.08)",
            color="#E4E4E7",
            border="1px solid #3F3F46",
            padding_x="6px",
            padding_y="1px",
            no_of_lines=1,
        ),
        rx.fragment(),
    )


def champion_metric_bar_row(row: ChampionMetricRow) -> rx.Component:
    """Render an individual comparison metric row as a 100% stacked bar chart with telemetry details."""
    return rx.vstack(
        # Top Header: Metric Name & Values
        rx.cond(
            row.segments.length() > 2,
            # N >= 3 layout: Metric pill badge on left, wrap of entity value chips
            rx.vstack(
                rx.hstack(
                    rx.badge(
                        row.metric.upper(),
                        font_size="9px",
                        font_weight="800",
                        bg="#27272A",
                        color="#E4E4E7",
                        border="1px solid #3F3F46",
                        letter_spacing="0.08em",
                        padding_x="8px",
                        padding_y="2px",
                        border_radius="full",
                    ),
                    rx.spacer(),
                    align="center",
                    width="100%",
                ),
                rx.flex(
                    rx.foreach(row.segments, champion_metric_header_chip),
                    wrap="wrap",
                    gap="2",
                    width="100%",
                    align="center",
                ),
                width="100%",
                spacing="1",
                padding_x="2px",
            ),
            # Classic N <= 2 layout
            rx.hstack(
                # Champion 1 Value (Left)
                rx.hstack(
                    rx.text(
                        row.val1,
                        font_size="15px",
                        font_weight="900",
                        color=row.color1,
                        text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                        line_height="1",
                    ),
                    align="center",
                    spacing="1",
                    flex="1",
                ),
                # Metric Badge (Center)
                rx.badge(
                    row.metric.upper(),
                    font_size="9px",
                    font_weight="800",
                    bg="#27272A",
                    color="#E4E4E7",
                    border="1px solid #3F3F46",
                    letter_spacing="0.08em",
                    padding_x="8px",
                    padding_y="2px",
                    border_radius="full",
                ),
                # Champion 2 Value (Right)
                rx.hstack(
                    rx.text(
                        row.val2,
                        font_size="15px",
                        font_weight="900",
                        color=row.color2,
                        text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                        text_align="right",
                        line_height="1",
                    ),
                    justify="end",
                    align="center",
                    spacing="1",
                    flex="1",
                ),
                width="100%",
                align="center",
                padding_x="2px",
            ),
        ),
        # 100% Stacked Bar Chart (Center)
        rx.box(
            rx.hstack(
                rx.cond(
                    row.segments.length() > 0,
                    rx.foreach(row.segments, champion_metric_segment_box),
                    # Fallback to dual segments
                    rx.fragment(
                        rx.box(
                            rx.text(row.pct1, font_size="11px", font_weight="900", color=row.text_color1),
                            width=row.pct1, height="22px", bg=row.color1, display="flex", align_items="center", justify_content="center", overflow="hidden"
                        ),
                        rx.box(width="2px", height="22px", bg="#121214"),
                        rx.box(
                            rx.text(row.pct2, font_size="11px", font_weight="900", color=row.text_color2),
                            width=row.pct2, height="22px", bg=row.color2, display="flex", align_items="center", justify_content="center", overflow="hidden"
                        ),
                    ),
                ),
                spacing="0",
                width="100%",
                height="22px",
            ),
            width="100%",
            height="22px",
            bg="#18181B",
            border_radius="6px",
            border="1px solid #3F3F46",
            overflow="hidden",
            box_shadow="inset 0 1px 3px rgba(0, 0, 0, 0.6), 0 2px 6px rgba(0, 0, 0, 0.3)",
        ),
        # Optional Sub-Detail Badges Row
        rx.cond(
            row.segments.length() > 2,
            rx.flex(
                rx.foreach(row.segments, champion_metric_subtext_chip),
                wrap="wrap",
                gap="2",
                width="100%",
                padding_x="2px",
            ),
            # Classic N <= 2 subtext
            rx.cond(
                (row.sub_text1 != "") | (row.sub_text2 != ""),
                rx.hstack(
                    rx.box(
                        rx.cond(
                            row.sub_text1 != "",
                            rx.badge(row.sub_text1, font_size="8px", font_weight="bold", bg="rgba(255, 255, 255, 0.08)", color="#E4E4E7", border="1px solid #3F3F46", padding_x="6px", padding_y="1px", no_of_lines=1),
                            rx.fragment(),
                        ),
                        flex="1", display="flex", justify_content="flex-start",
                    ),
                    rx.box(
                        rx.cond(
                            row.sub_text2 != "",
                            rx.badge(row.sub_text2, font_size="8px", font_weight="bold", bg="rgba(255, 255, 255, 0.08)", color="#E4E4E7", border="1px solid #3F3F46", padding_x="6px", padding_y="1px", no_of_lines=1, text_align="right"),
                            rx.fragment(),
                        ),
                        flex="1", display="flex", justify_content="flex-end",
                    ),
                    width="100%", align="center", padding_x="2px",
                ),
                rx.fragment(),
            ),
        ),
        # Subtle separator between metric rows
        rx.box(width="100%", height="1px", bg="#27272A", margin_y="4px"),
        spacing="1",
        width="100%",
    )


def native_champion_comparison_card(msg: ChatMessage) -> rx.Component:
    """Rich native Reflex Champion Comparison Card (TAF1APP-SDDREQ-250) supporting N+ champions."""
    return rx.box(
        # Rainbow top highlight line
        rx.box(
            width="100%",
            height="3px",
            background="linear-gradient(90deg, #E60049 0%, #FF8C00 28%, #FFE500 50%, #00B4D8 75%, #7B00FF 100%)",
            border_radius="full",
            margin_bottom="12px",
        ),
        # Header with Download Button
        rx.hstack(
            rx.hstack(
                rx.icon("trophy", size=16, color="#F59E0B"),
                rx.text("CHAMPION COMPARISON", font_size="12px", font_weight="bold", color="white", letter_spacing="0.05em"),
                rx.badge("OFFICIAL LEAGUE DOSSIER", color_scheme="amber", variant="surface", font_size="8px", font_weight="bold"),
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            rx.button(
                rx.hstack(
                    rx.icon("download", size=12),
                    rx.text("PNG", font_size="10px", font_weight="bold"),
                    spacing="1",
                    align="center",
                ),
                size="1",
                variant="surface",
                color_scheme="amber",
                on_click=AlternativeIntelligenceState.download_infographic_png(msg.card_id, "Champion_Comparison_Dossier"),
                cursor="pointer",
                title="Download Infographic as .PNG",
                custom_attrs={"data-html2canvas-ignore": "true"},
            ),
            width="100%",
            align="center",
            margin_bottom="10px",
        ),
        # Champions Showcase (Multi-Grid if N >= 3, else Classic Dual Header)
        rx.cond(
            msg.champ_entities.length() > 2,
            # Multi-Champion Grid Showcase (N >= 3)
            rx.flex(
                rx.foreach(msg.champ_entities, champion_entity_badge_card),
                wrap="wrap",
                gap="2",
                width="100%",
                padding="8px",
                bg="#141416",
                border="1px solid #27272A",
                border_radius="md",
                margin_bottom="12px",
                justify="center",
            ),
            # Classic Dual Champion Layout (N <= 2)
            rx.hstack(
                # Champion 1 (Left)
                rx.vstack(
                    rx.badge(
                        f"🏆 {msg.champ_season1} {msg.champ_type1} Champion",
                        bg="rgba(245, 158, 11, 0.15)",
                        color="#F59E0B",
                        border="1px solid rgba(245, 158, 11, 0.4)",
                        font_size="9px",
                        font_weight="bold",
                    ),
                    rx.text(
                        msg.champ_name1,
                        font_size="15px",
                        font_weight="900",
                        color=msg.champ_color1,
                        text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                        letter_spacing="-0.02em",
                        no_of_lines=1,
                    ),
                    rx.cond(
                        msg.champ_team1 != "",
                        rx.badge(
                            msg.champ_team1,
                            bg=msg.champ_color1,
                            color=msg.champ_text_color1,
                            border="1px solid rgba(255, 255, 255, 0.4)",
                            font_size="8px",
                            font_weight="bold",
                        ),
                        rx.fragment(),
                    ),
                    align="start",
                    spacing="1",
                    flex="1",
                ),
                # Center Circle with The Alternative F1 NEW Logo & Trophy Aura
                rx.box(
                    rx.image(
                        src="/The Alternative F1 NEW Logo.png",
                        height="32px",
                        width="32px",
                        object_fit="contain",
                    ),
                    background="radial-gradient(circle, #27272A 0%, #18181B 100%)",
                    border="2px solid #F59E0B",
                    border_radius="full",
                    padding="4px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    box_shadow="0 0 12px rgba(245, 158, 11, 0.4)",
                ),
                # Champion 2 (Right)
                rx.vstack(
                    rx.badge(
                        f"🏆 {msg.champ_season2} {msg.champ_type2} Champion",
                        bg="rgba(245, 158, 11, 0.15)",
                        color="#F59E0B",
                        border="1px solid rgba(245, 158, 11, 0.4)",
                        font_size="9px",
                        font_weight="bold",
                    ),
                    rx.text(
                        msg.champ_name2,
                        font_size="15px",
                        font_weight="900",
                        color=msg.champ_color2,
                        text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                        letter_spacing="-0.02em",
                        no_of_lines=1,
                        text_align="right",
                    ),
                    rx.cond(
                        msg.champ_team2 != "",
                        rx.badge(
                            msg.champ_team2,
                            bg=msg.champ_color2,
                            color=msg.champ_text_color2,
                            border="1px solid rgba(255, 255, 255, 0.4)",
                            font_size="8px",
                            font_weight="bold",
                        ),
                        rx.fragment(),
                    ),
                    align="end",
                    spacing="1",
                    flex="1",
                ),
                width="100%",
                align="center",
                padding="12px",
                bg="#141416",
                border="1px solid #27272A",
                border_radius="md",
                margin_bottom="12px",
            ),
        ),
        # Metric Comparison Rows
        rx.vstack(
            rx.foreach(msg.champ_stats, champion_metric_bar_row),
            width="100%",
            spacing="1",
            margin_bottom="12px",
        ),
        # Bottom League Branding Footer
        rx.center(
            rx.hstack(
                rx.image(
                    src="/The Alternative F1 NEW Logo.png",
                    height="20px",
                    object_fit="contain",
                ),
                rx.text("THE ALTERNATIVE F1 • OFFICIAL CHAMPIONSHIP HISTORICAL TELEMETRY", font_size="9px", font_weight="bold", color="#71717A", letter_spacing="0.05em"),
                spacing="2",
                align="center",
            ),
            width="100%",
            padding_y="10px",
            bg="#141416",
            border_radius="0 0 md md",
            border_top="1px solid #27272A",
        ),
        id=msg.card_id,
        background="#18181B",
        border="1px solid #3F3F46",
        border_radius="lg",
        padding="12px",
        width="100%",
        box_shadow="0 10px 30px rgba(0, 0, 0, 0.6)",
        margin_bottom="12px",
    )


def message_card(msg: ChatMessage) -> rx.Component:
    """Render an individual conversational message card."""
    is_user = msg.role == "user"
    return rx.hstack(
        rx.vstack(
            rx.cond(
                msg.is_infographic,
                rx.cond(
                    msg.infographic_type == "champion_comparison",
                    native_champion_comparison_card(msg),
                    rx.cond(
                        msg.infographic_type == "h2h",
                        native_h2h_infographic_card(msg),
                        rx.cond(
                            msg.infographic_type == "seasonal_qual",
                            native_seasonal_qual_infographic_card(msg),
                            native_race_infographic_card(msg),
                        ),
                    ),
                ),
                rx.fragment(),
            ),

            rx.cond(
                msg.content != "",
                rx.box(
                    # Assistant response top thin rainbow accent line
                    rx.cond(
                        ~is_user,
                        rx.box(
                            width="100%",
                            height="3px",
                            background="linear-gradient(90deg, #E60049 0%, #FF8C00 28%, #FFE500 50%, #00B4D8 75%, #7B00FF 100%)",
                            border_radius="full",
                            margin_bottom="10px",
                        ),
                        rx.fragment(),
                    ),
                    # User prompt skill badge pill box (persisted with prompt)
                    rx.cond(
                        is_user & (msg.skill_badge != ""),
                        rx.box(
                            rx.hstack(
                                rx.icon("sparkles", size=11, color="white"),
                                rx.text(msg.skill_badge, font_size="10px", font_weight="bold", color="white", letter_spacing="0.02em"),
                                spacing="1",
                                align="center",
                            ),
                            background="radial-gradient(circle at 20% 25%, rgba(230, 0, 73, 0.6) 0%, transparent 55%), radial-gradient(circle at 80% 25%, rgba(255, 140, 0, 0.6) 0%, transparent 50%), radial-gradient(circle at 20% 80%, rgba(123, 0, 255, 0.6) 0%, transparent 55%), radial-gradient(circle at 80% 80%, rgba(0, 153, 255, 0.6) 0%, transparent 50%), rgba(24, 24, 28, 0.7)",
                            border="1px solid rgba(255, 255, 255, 0.35)",
                            box_shadow="0 0 10px rgba(0, 180, 218, 0.3)",
                            border_radius="full",
                            padding_x="8px",
                            padding_y="3px",
                            margin_bottom="8px",
                            display="inline-block",
                        ),
                        rx.fragment(),
                    ),
                    rx.markdown(
                        msg.content,
                        style={
                            "font_size": "0.9rem",
                            "color": "#E4E4E7",
                            "line_height": "1.5",
                            "p": {"margin_bottom": "0.5rem"},
                            "table": {
                                "display": "block",
                                "width": "100%",
                                "max_width": "100%",
                                "overflow_x": "auto",
                                "-webkit-overflow-scrolling": "touch",
                                "border_collapse": "collapse",
                                "margin": "0.6rem 0",
                                "font_size": "0.82rem",
                            },
                            "th": {
                                "border": "1px solid #3F3F46",
                                "padding": "6px 10px",
                                "background": "#27272A",
                                "color": "#00b4da",
                                "white_space": "nowrap",
                            },
                            "td": {
                                "border": "1px solid #27272A",
                                "padding": "6px 10px",
                                "white_space": "nowrap",
                            },
                            "code": {
                                "background": "#27272A",
                                "padding": "2px 4px",
                                "border_radius": "4px",
                                "font_size": "0.8rem",
                            },
                            "pre": {
                                "overflow_x": "auto",
                                "max_width": "100%",
                                "background": "#27272A",
                                "padding": "8px",
                                "border_radius": "6px",
                                "margin": "0.5rem 0",
                            },
                            "img": {
                                "display": "inline-block",
                                "vertical_align": "middle",
                                "width": "34px",
                                "height": "34px",
                                "border_radius": "50%",
                                "margin_left": "6px",
                                "box_shadow": "0 0 10px rgba(245, 158, 11, 0.6)",
                                "border": "1px solid rgba(245, 158, 11, 0.8)",
                            },
                        },
                    ),
                    bg=rx.cond(is_user, "#27272A", "#18181B"),
                    border=rx.cond(is_user, "1px solid #3F3F46", "1px solid #2C2C32"),
                    border_radius="md",
                    padding="10px 14px",
                    max_width=rx.cond(is_user, "85%", "100%"),
                    width=rx.cond(is_user, "auto", "100%"),
                    overflow_x="auto",
                    box_sizing="border-box",
                    box_shadow="0 2px 8px rgba(0, 0, 0, 0.3)",
                ),
                rx.fragment(),
            ),
            rx.cond(
                msg.timestamp != "",
                rx.moment(
                    date=msg.timestamp,
                    format="h:mm A",
                    local=True,
                    font_size="10px",
                    color="#71717A",
                    padding_x="4px",
                    width="100%",
                    text_align=rx.cond(is_user, "right", "left"),
                ),
                rx.fragment(),
            ),
            align_items=rx.cond(is_user, "end", "center"),
            spacing="1",
            width="100%",
            min_width="0",
            flex="1",
        ),
        rx.cond(
            is_user,
            rx.box(
                rx.icon("user", size=16, color="#00b4da"),
                bg="#27272A",
                border="1px solid #3F3F46",
                border_radius="50%",
                padding="6px",
                display="flex",
                align_items="center",
                justify_content="center",
                height="32px",
                width="32px",
                min_width="32px",
                margin_right="4px",
            ),
            rx.fragment(),
        ),
        width="100%",
        justify=rx.cond(is_user, "end", "center"),
        spacing="2",
        align_items="start",
        padding_right=rx.cond(is_user, "4px", "0px"),
    )


def skills_library_selector() -> rx.Component:
    """Dropdown selector displaying the library of analytical skills."""
    return rx.vstack(
        rx.hstack(
            rx.icon("sparkles", size=15, color="#00b4da"),
            rx.text("Skills Library", font_size="13px", font_weight="bold", color="white"),
            spacing="2",
            align="center",
        ),
        rx.select(
            SKILL_OPTIONS,
            value=AlternativeIntelligenceState.selected_skill,
            on_change=AlternativeIntelligenceState.select_skill,
            bg="#18181B",
            color="white",
            border="1px solid #3F3F46",
            border_radius="md",
            width="100%",
            max_width="320px",
            height="38px",
            font_size="13px",
            cursor="pointer",
            _hover={"border_color": "#00b4da"},
        ),
        rx.text(
            "Select an optional skill or simply ask a question in the input bar.",
            font_size="11px",
            color="#A1A1AA",
            text_align="center",
            max_width="320px",
            line_height="1.4",
        ),
        spacing="2",
        align="center",
        width="100%",
        padding="14px",
        bg="#18181B",
        border="1px solid #27272A",
        border_radius="lg",
    )


def alternative_intelligence_drawer() -> rx.Component:
    """Sliding left-hand pop-out drawer for Alternative Intelligence."""
    return rx.cond(
        AlternativeIntelligenceState.show_drawer,
        rx.box(
            # Backdrop Overlay
            rx.box(
                position="fixed",
                top="0",
                left="0",
                width="100vw",
                height="100vh",
                bg="rgba(0,0,0,0.6)",
                backdrop_filter="blur(3px)",
                z_index="1999",
                on_click=AlternativeIntelligenceState.toggle_drawer,
            ),
            # Sliding Container (Left Side)
            rx.vstack(
                # Header Bar (Rainbow stretches across header and gently fades out before buttons)
                rx.hstack(
                    rx.hstack(
                        rx.heading(
                            "Alternative Intelligence",
                            size="4",
                            color="white",
                            font_weight="800",
                            letter_spacing="tight",
                            text_shadow="0 2px 6px rgba(0, 0, 0, 0.85)",
                        ),
                        rx.badge(
                            "BETA",
                            color_scheme="cyan",
                            variant="surface",
                            font_size="9px",
                            font_weight="900",
                            letter_spacing="0.08em",
                            border="1px solid rgba(0, 180, 218, 0.4)",
                            box_shadow="0 0 8px rgba(0, 180, 218, 0.3)",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.button(
                            rx.icon("trash-2", size=16),
                            bg="transparent",
                            color="#A1A1AA",
                            _hover={"color": "#EF4444"},
                            on_click=AlternativeIntelligenceState.clear_chat,
                            size="1",
                            padding="4px",
                            title="Clear conversation",
                        ),
                        rx.button(
                            rx.icon("x", size=20),
                            bg="transparent",
                            color="#A1A1AA",
                            _hover={"color": "white"},
                            on_click=AlternativeIntelligenceState.toggle_drawer,
                            size="1",
                            padding="4px",
                            title="Close drawer",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    width="100%",
                    align="center",
                    padding_left=["20px", "24px", "26px"],
                    padding_right=["14px", "18px", "20px"],
                    padding_y="4",
                    background="radial-gradient(circle at 10% 30%, rgba(230, 0, 73, 0.75) 0%, transparent 55%), radial-gradient(circle at 35% 20%, rgba(255, 140, 0, 0.7) 0%, transparent 50%), radial-gradient(circle at 65% 80%, rgba(123, 0, 255, 0.75) 0%, transparent 55%), radial-gradient(circle at 90% 40%, rgba(0, 153, 255, 0.75) 0%, transparent 50%), #111113",
                    border_bottom="1px solid #27272A",
                ),

                # Message Feed with generous horizontal and vertical inset
                rx.box(
                    rx.cond(
                        AlternativeIntelligenceState.messages.length() > 0,
                        rx.vstack(
                            rx.foreach(AlternativeIntelligenceState.messages, message_card),
                            rx.cond(
                                AlternativeIntelligenceState.is_generating,
                                rx.hstack(
                                    ai_logo("16px", border_radius="sm"),
                                    rx.text("Analyzing league database...", font_size="12px", color="#00b4da"),
                                    spacing="2",
                                    align="center",
                                    padding="6px 12px",
                                    bg="#18181B",
                                    border_radius="md",
                                    border="1px solid #00b4da",
                                ),
                                rx.fragment(),
                            ),
                            rx.box(id="ai-chat-bottom-anchor", height="1px", width="100%"),
                            width="100%",
                            spacing="4",
                            padding_y="2",
                        ),
                        # Empty state with Skills Library
                        rx.vstack(
                            rx.box(
                                rx.image(
                                    src="/Icons/IconLogo.png",
                                    height="48px",
                                    width="48px",
                                    object_fit="contain",
                                ),
                                background="radial-gradient(circle at 20% 25%, #E60049 0%, transparent 55%), radial-gradient(circle at 80% 25%, #FF8C00 0%, transparent 50%), radial-gradient(circle at 20% 80%, #7B00FF 0%, transparent 55%), radial-gradient(circle at 80% 80%, #0099FF 0%, transparent 50%), #121214",
                                border_radius="18px",
                                padding="14px",
                                border="1px solid rgba(255, 255, 255, 0.3)",
                                box_shadow="0 0 25px rgba(0, 180, 218, 0.4), 0 0 15px rgba(230, 0, 73, 0.4)",
                                margin_bottom="3",
                            ),
                            rx.text("Alternative Intelligence", font_size="15px", font_weight="bold", color="white"),
                            rx.text("Official analytical AI statistician for The Alternative F1.", font_size="12px", color="#A1A1AA", text_align="center"),
                            rx.box(
                                skills_library_selector(),
                                width="100%",
                                max_width="340px",
                                margin_top="4",
                            ),
                            align="center",
                            justify="center",
                            height="100%",
                            padding_y="6",
                        ),
                    ),
                    id="ai-chat-feed",
                    width="100%",
                    flex="1",
                    overflow_y="auto",
                    padding_x=["12px", "16px", "20px"],
                    padding_top="16px",
                    padding_bottom="12px",
                ),

                # Error banner if present
                rx.cond(
                    AlternativeIntelligenceState.error_message != "",
                    rx.box(
                        rx.hstack(
                            rx.icon("circle-alert", size=16, color="#EF4444"),
                            rx.text(AlternativeIntelligenceState.error_message, font_size="12px", color="#EF4444"),
                            spacing="2",
                        ),
                        bg="#271515",
                        border="1px solid #7F1D1D",
                        border_radius="md",
                        padding="8px 12px",
                        margin_x="5",
                        margin_bottom="2",
                        width="calc(100% - 40px)",
                    ),
                    rx.fragment(),
                ),

                # Bottom Search Bar (Anchored comfortably at bottom with safe-area support and luminous card)
                rx.box(
                    rx.cond(
                        AlternativeIntelligenceState.messages.length() > 0,
                        rx.hstack(
                            rx.hstack(
                                rx.icon("sparkles", size=13, color="#00b4da"),
                                rx.text("Skill:", font_size="11px", color="#A1A1AA", font_weight="semibold"),
                                spacing="1",
                                align="center",
                            ),
                            rx.select(
                                SKILL_OPTIONS,
                                value=AlternativeIntelligenceState.selected_skill,
                                on_change=AlternativeIntelligenceState.select_skill,
                                bg="#18181B",
                                color="white",
                                border="1px solid #27272A",
                                border_radius="md",
                                height="28px",
                                font_size="11px",
                                cursor="pointer",
                                flex="1",
                                _hover={"border_color": "#00b4da"},
                            ),
                            spacing="2",
                            align="center",
                            width="100%",
                            margin_bottom="2",
                        ),
                        rx.fragment(),
                    ),
                    rx.hstack(
                        rx.hstack(
                            rx.cond(
                                AlternativeIntelligenceState.active_skill_badge != "",
                                rx.hstack(
                                    rx.text(
                                        AlternativeIntelligenceState.active_skill_badge,
                                        font_size="11px",
                                        font_weight="bold",
                                        color="white",
                                        text_shadow="0 1px 3px rgba(0, 0, 0, 0.8)",
                                        white_space="nowrap",
                                    ),
                                    rx.button(
                                        rx.icon("x", size=12, color="rgba(255, 255, 255, 0.8)"),
                                        size="1",
                                        variant="ghost",
                                        padding="0",
                                        height="16px",
                                        width="16px",
                                        min_width="16px",
                                        cursor="pointer",
                                        on_click=AlternativeIntelligenceState.clear_active_skill,
                                        _hover={"color": "#EF4444"},
                                        title="Clear selected skill",
                                    ),
                                    background="radial-gradient(circle at 20% 25%, rgba(230, 0, 73, 0.55) 0%, transparent 55%), radial-gradient(circle at 80% 25%, rgba(255, 140, 0, 0.55) 0%, transparent 50%), radial-gradient(circle at 20% 80%, rgba(123, 0, 255, 0.55) 0%, transparent 55%), radial-gradient(circle at 80% 80%, rgba(0, 153, 255, 0.55) 0%, transparent 50%), rgba(18, 18, 20, 0.55)",
                                    border="1px solid rgba(255, 255, 255, 0.3)",
                                    box_shadow="0 0 8px rgba(0, 180, 218, 0.3)",
                                    border_radius="md",
                                    padding="3px 8px",
                                    align="center",
                                    spacing="1",
                                ),
                                rx.fragment(),
                            ),
                            rx.input(
                                id="ai-search-input",
                                class_name="ai-search-input",
                                placeholder=rx.cond(
                                    AlternativeIntelligenceState.active_skill_badge != "",
                                    AlternativeIntelligenceState.active_skill_infotip,
                                    "Ask Alternative Intelligence...",
                                ),
                                value=AlternativeIntelligenceState.search_query,
                                on_change=AlternativeIntelligenceState.set_search_query,
                                on_key_down=AlternativeIntelligenceState.handle_key_down,
                                disabled=AlternativeIntelligenceState.is_generating,
                                bg="transparent",
                                color="white",
                                border="none",
                                height="38px",
                                padding_x="6px",
                                font_size="13px",
                                flex="1",
                                _focus={"outline": "none"},
                                _placeholder={
                                    "color": "#D4D4D8",
                                    "-webkit-text-fill-color": "#D4D4D8",
                                    "opacity": "1",
                                },
                            ),
                            bg="rgba(24, 24, 28, 0.95)",
                            border="1px solid rgba(255, 255, 255, 0.22)",
                            box_shadow="0 4px 18px rgba(0, 0, 0, 0.45)",
                            border_radius="10px",
                            padding_x="10px",
                            align="center",
                            flex="1",
                            min_height="44px",
                            _focus_within={"border_color": "#00b4da", "box_shadow": "0 0 12px rgba(0, 180, 218, 0.4)"},
                        ),
                        rx.button(
                            rx.cond(
                                AlternativeIntelligenceState.is_generating,
                                rx.spinner(size="1", color="white"),
                                rx.icon("send", size=16, color="white"),
                            ),
                            background="linear-gradient(135deg, #00b4da, #7B2CBF)",
                            color="white",
                            height="44px",
                            width="44px",
                            min_width="44px",
                            margin_right=["44px", "0px", "0px"],
                            border_radius="10px",
                            cursor="pointer",
                            disabled=AlternativeIntelligenceState.is_generating,
                            on_click=AlternativeIntelligenceState.submit_query,
                            _hover={"transform": "scale(1.05)", "box_shadow": "0 0 10px rgba(0, 180, 218, 0.5)"},
                            transition="all 0.15s ease",
                        ),

                        spacing="3",
                        width="100%",
                        align="center",
                    ),
                    width="100%",
                    padding_x=["12px", "16px", "20px"],
                    padding_top="10px",
                    padding_bottom=["calc(12px + env(safe-area-inset-bottom, 0px))", "12px", "14px"],
                    border_top="1px solid rgba(255, 255, 255, 0.12)",
                    background="rgba(17, 17, 19, 0.85)",
                    backdrop_filter="blur(16px)",
                ),

                # Main Panel Styling (Sliding in from Left with ambient glowing rainbow bokeh)
                position="fixed",
                top="0",
                left="0",
                height="100vh",
                width=["100%", "440px", "500px"],
                background="radial-gradient(circle at 10% 12%, rgba(230, 0, 73, 0.08) 0%, transparent 45%), radial-gradient(circle at 85% 20%, rgba(255, 140, 0, 0.07) 0%, transparent 45%), radial-gradient(circle at 15% 75%, rgba(123, 0, 255, 0.08) 0%, transparent 50%), radial-gradient(circle at 85% 85%, rgba(0, 180, 218, 0.08) 0%, transparent 50%), #111113",
                border_right="1px solid #2C2C32",
                box_shadow="10px 0px 35px rgba(0,0,0,0.7)",
                z_index="2000",
                padding="0",
                spacing="0",
                align_items="start",
            ),
            position="relative",
            z_index="1999",
        ),
        rx.fragment(),
    )

