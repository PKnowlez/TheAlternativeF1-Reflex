# All Time Detailed Driver & Constructor Statistics — Reflex Component
# Implements TAF1APP-SDDFEAT-5 and downstream SDD requirements (78, 77, 75, 69, 71, 73, 74, 76, 70, 72, 79)

import os
from pathlib import Path
import pandas as pd
import numpy as np
import reflex as rx

from the_alternative_f1.all_time_stats.Functions import get_excel_sheet, file as excel_file
from the_alternative_f1.articles.components import zoomable_chart

_detailed_cache = {}
_detailed_mtime = 0

RACE_COLORS = [
    "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
    "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe",
    "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000",
    "#aaffc3", "#808000", "#ffd8b1", "#000075", "#808080",
]


def _get_mtime():
    p = Path(excel_file)
    return p.stat().st_mtime if p.exists() else 0


def get_entity_lists(num_seasons: int = 5):
    """Retrieve sorted list of Drivers and Constructors across completed seasons."""
    global _detailed_cache, _detailed_mtime
    curr_mtime = _get_mtime()
    cache_key = ("get_entity_lists", num_seasons)
    if _detailed_mtime == curr_mtime and cache_key in _detailed_cache:
        return _detailed_cache[cache_key]

    drivers = set()
    teams = set()
    for s in range(1, num_seasons + 1):
        df = get_excel_sheet(f"Season{s}")
        if not df.empty:
            if "Driver" in df.columns:
                drivers.update([str(d).strip() for d in df["Driver"].dropna().unique() if str(d).strip() not in ("nan", "—", "")])
            if "Team" in df.columns:
                teams.update([str(t).strip() for t in df["Team"].dropna().unique() if str(t).strip() not in ("nan", "—", "")])
    res = (sorted(list(drivers)), sorted(list(teams)))
    if _detailed_mtime != curr_mtime:
        _detailed_cache.clear()
        _detailed_mtime = curr_mtime
    _detailed_cache[cache_key] = res
    return res


def compute_all_time_avg_pos_change(num_seasons: int, entity_type: str, active_entity: str):
    """Requirement 69: Average Positions Gained/Lost All Time comparing all entities.
    Active entity is blue (#00b4da); positive changes are green (#3cb44b), negative are red (#e6194b).
    """
    global _detailed_cache, _detailed_mtime
    curr_mtime = _get_mtime()
    cache_key = ("compute_all_time_avg_pos_change", num_seasons, entity_type, active_entity)
    if _detailed_mtime == curr_mtime and cache_key in _detailed_cache:
        return _detailed_cache[cache_key]

    all_drivers, all_teams = get_entity_lists(num_seasons)
    entities = all_drivers if entity_type == "Driver" else all_teams

    results = []
    for entity in entities:
        pos_changes = []
        for s in range(1, num_seasons + 1):
            df = get_excel_sheet(f"Season{s}")
            sched = get_excel_sheet(f"S{s}Schedule")
            if df.empty or sched.empty:
                continue

            df_copy = df.copy()
            df_copy["Driver"] = df_copy["Driver"].astype(str).str.strip()
            df_copy["Team"] = df_copy["Team"].astype(str).str.strip()

            col_key = "Driver" if entity_type == "Driver" else "Team"
            rows = df_copy[df_copy[col_key] == entity]
            if rows.empty:
                continue

            for race_name in sched["Race"]:
                race_str = str(race_name).strip()
                if race_str.startswith(("Pre", "Post")):
                    continue
                place_col = race_str + "Place"
                qual_col = race_str + "Qualifying"
                pts_col = race_str + "Points"

                valid_pts_s = pd.to_numeric(df_copy[pts_col], errors='coerce').fillna(0) if pts_col in df_copy.columns else pd.Series()
                valid_place_s = pd.to_numeric(df_copy[place_col], errors='coerce').fillna(0) if place_col in df_copy.columns else pd.Series()
                if not ((not valid_pts_s.empty and (valid_pts_s > 0).any()) or (not valid_place_s.empty and (valid_place_s > 0).any())):
                    continue  # Requirement 70: Skip unrun races

                if place_col in df_copy.columns and qual_col in df_copy.columns:
                    for _, r in rows.iterrows():
                        p = r[place_col]
                        q = r[qual_col]
                        if not pd.isnull(p) and not pd.isnull(q):
                            try:
                                p_val = float(p)
                                q_val = float(q)
                                if p_val > 0 and q_val > 0:
                                    pos_changes.append(q_val - p_val)
                            except Exception:
                                pass

        avg_change = float(np.mean(pos_changes)) if pos_changes else 0.0
        is_active = (entity == active_entity)
        if is_active:
            color = "#00b4da"
        elif avg_change > 0:
            color = "#3cb44b"
        elif avg_change < 0:
            color = "#e6194b"
        else:
            color = "#888888"

        results.append({
            "name": entity,
            "avg_change": round(avg_change, 2),
            "fill": color,
        })

    results.sort(key=lambda x: x["avg_change"], reverse=True)
    if _detailed_mtime != curr_mtime:
        _detailed_cache.clear()
        _detailed_mtime = curr_mtime
    _detailed_cache[cache_key] = results
    return results


def compute_entity_detailed_metrics(num_seasons: int, entity_type: str, entity_name: str):
    """Compute detailed race-by-race metrics for a single Driver or Constructor."""
    global _detailed_cache, _detailed_mtime
    curr_mtime = _get_mtime()
    cache_key = ("compute_entity_detailed_metrics", num_seasons, entity_type, entity_name)
    if _detailed_mtime == curr_mtime and cache_key in _detailed_cache:
        return _detailed_cache[cache_key]

    races_detail = []
    season_boundaries = []
    current_race_index = 0

    for s in range(1, num_seasons + 1):
        df = get_excel_sheet(f"Season{s}")
        sched = get_excel_sheet(f"S{s}Schedule")
        if df.empty or sched.empty:
            continue

        df_copy = df.copy()
        df_copy["Driver"] = df_copy["Driver"].astype(str).str.strip()
        df_copy["Team"] = df_copy["Team"].astype(str).str.strip()

        col_key = "Driver" if entity_type == "Driver" else "Team"
        entity_rows = df_copy[df_copy[col_key] == entity_name]

        if entity_rows.empty:
            continue  # Requirement 70: Scope of Calculations

        season_start_idx = current_race_index
        season_race_count = 0

        for race_name in sched["Race"]:
            race_str = str(race_name).strip()
            if race_str.startswith(("Pre", "Post")):
                continue

            place_col = race_str + "Place"
            qual_col = race_str + "Qualifying"
            fl_col = race_str + "FastestLap"
            pts_col = race_str + "Points"
            dotd_col = race_str + "DOTD"
            mot_col = race_str + "MOT"
            cd_col = race_str + "CD"

            if pts_col not in df_copy.columns and place_col not in df_copy.columns:
                continue

            valid_pts_s = pd.to_numeric(df_copy[pts_col], errors='coerce').fillna(0) if pts_col in df_copy.columns else pd.Series()
            valid_place_s = pd.to_numeric(df_copy[place_col], errors='coerce').fillna(0) if place_col in df_copy.columns else pd.Series()
            if not ((not valid_pts_s.empty and (valid_pts_s > 0).any()) or (not valid_place_s.empty and (valid_place_s > 0).any())):
                continue  # Requirement 70: Skip unrun races (no points/finishes associated yet)

            if entity_type == "Driver":
                row = entity_rows.iloc[0]
                pts = row[pts_col] if pts_col in row and not pd.isnull(row[pts_col]) else 0.0
                place = row[place_col] if place_col in row and not pd.isnull(row[place_col]) else None
                qual = row[qual_col] if qual_col in row and not pd.isnull(row[qual_col]) else None
                fl = row[fl_col] if fl_col in row and not pd.isnull(row[fl_col]) else "N"
                dotd = row[dotd_col] if dotd_col in row and not pd.isnull(row[dotd_col]) else "N"
                mot = row[mot_col] if mot_col in row and not pd.isnull(row[mot_col]) else "N"
                cd = row[cd_col] if cd_col in row and not pd.isnull(row[cd_col]) else "N"

                if pd.isnull(pts) and pd.isnull(place):
                    continue

                try:
                    place_val = float(place) if place is not None and not pd.isnull(place) else 0.0
                except Exception:
                    place_val = 0.0

                try:
                    qual_val = float(qual) if qual is not None and not pd.isnull(qual) else 0.0
                except Exception:
                    qual_val = 0.0

                try:
                    pts_val = float(pts) if pts is not None and not pd.isnull(pts) else 0.0
                except Exception:
                    pts_val = 0.0

                pos_change = (qual_val - place_val) if (qual_val > 0 and place_val > 0) else 0.0

                races_detail.append({
                    "season": s,
                    "race": race_str,
                    "track": race_str.replace(" Sprint", "").strip(),
                    "place": place_val,
                    "qual": qual_val,
                    "fl": str(fl).strip().upper() == "Y",
                    "pts": pts_val,
                    "dotd": str(dotd).strip().upper() == "Y",
                    "mot": str(mot).strip().upper() == "Y",
                    "cd": str(cd).strip().upper() == "Y",
                    "pos_change": pos_change,
                    "label": f"S{s} {race_str}",
                    "season_race_idx": season_race_count,
                })
                current_race_index += 1
                season_race_count += 1

            else:  # Constructor
                pts_sum = float(entity_rows[pts_col].sum()) if pts_col in entity_rows.columns else 0.0

                valid_places = []
                valid_quals = []
                if place_col in entity_rows.columns:
                    for p in entity_rows[place_col].dropna():
                        try:
                            valid_places.append(float(p))
                        except Exception:
                            pass
                if qual_col in entity_rows.columns:
                    for q in entity_rows[qual_col].dropna():
                        try:
                            valid_quals.append(float(q))
                        except Exception:
                            pass

                place_val = min(valid_places) if valid_places else 0.0
                qual_val = min(valid_quals) if valid_quals else 0.0

                fl_cnt = (entity_rows[fl_col].astype(str).str.strip().str.upper() == "Y").sum() if fl_col in entity_rows.columns else 0
                dotd_cnt = (entity_rows[dotd_col].astype(str).str.strip().str.upper() == "Y").sum() if dotd_col in entity_rows.columns else 0
                mot_cnt = (entity_rows[mot_col].astype(str).str.strip().str.upper() == "Y").sum() if mot_col in entity_rows.columns else 0
                cd_cnt = (entity_rows[cd_col].astype(str).str.strip().str.upper() == "Y").sum() if cd_col in entity_rows.columns else 0

                pos_change = (qual_val - place_val) if (qual_val > 0 and place_val > 0) else 0.0

                races_detail.append({
                    "season": s,
                    "race": race_str,
                    "track": race_str.replace(" Sprint", "").strip(),
                    "place": place_val,
                    "qual": qual_val,
                    "fl": fl_cnt > 0,
                    "pts": pts_sum,
                    "dotd": dotd_cnt > 0,
                    "mot": mot_cnt > 0,
                    "cd": cd_cnt > 0,
                    "pos_change": pos_change,
                    "label": f"S{s} {race_str}",
                    "season_race_idx": season_race_count,
                })
                current_race_index += 1
                season_race_count += 1

        if current_race_index > season_start_idx:
            season_boundaries.append(f"S{s}")

    df_races = pd.DataFrame(races_detail)
    res = (df_races, season_boundaries)
    if _detailed_mtime != curr_mtime:
        _detailed_cache.clear()
        _detailed_mtime = curr_mtime
    _detailed_cache[cache_key] = res
    return res


class DetailedStatsState(rx.State):
    """State management for Detailed All Time Statistics."""
    entity_type: str = "Driver"
    selected_driver: str = ""
    selected_constructor: str = ""

    def set_entity_type(self, value: str):
        self.entity_type = value

    def set_selected_driver(self, value: str):
        self.selected_driver = value

    def set_selected_constructor(self, value: str):
        self.selected_constructor = value

    @rx.var
    def driver_options(self) -> list[str]:
        drivers, _ = get_entity_lists(5)
        return drivers

    @rx.var
    def constructor_options(self) -> list[str]:
        _, teams = get_entity_lists(5)
        return teams

    @rx.var
    def active_name(self) -> str:
        if self.entity_type == "Constructor":
            teams = self.constructor_options
            if self.selected_constructor in teams:
                return self.selected_constructor
            return teams[0] if teams else ""
        else:
            drivers = self.driver_options
            if self.selected_driver in drivers:
                return self.selected_driver
            return drivers[0] if drivers else ""

    @rx.var(auto_deps=False, deps=["entity_type", "selected_driver", "selected_constructor"])
    def calculated_data(self) -> dict:
        num_seasons = 5
        entity_type = self.entity_type
        active_name = self.active_name

        df_races, _ = compute_entity_detailed_metrics(num_seasons, entity_type, active_name)

        if not df_races.empty:
            tot_pts = float(df_races["pts"].sum())
            wins = int((df_races["place"] == 1.0).sum())
            podiums = int(((df_races["place"] >= 1.0) & (df_races["place"] <= 3.0)).sum())
            fl_count = int(df_races["fl"].sum())
            valid_q = df_races[df_races["qual"] > 0]["qual"]
            avg_q = float(valid_q.mean()) if not valid_q.empty else 0.0
            valid_p = df_races[df_races["place"] > 0]["place"]
            avg_p = float(valid_p.mean()) if not valid_p.empty else 0.0
            avg_change = avg_q - avg_p
            poles = int((df_races["qual"] == 1.0).sum())
            dotd_count = int(df_races["dotd"].sum())
            mot_count = int(df_races["mot"].sum())
            cd_count = int(df_races["cd"].sum())

            best_row = df_races.loc[df_races["pts"].idxmax()]
            best_pts_str = f"{best_row['pts']:.0f} pts (S{best_row['season']} {best_row['race']})"
        else:
            tot_pts, wins, podiums, fl_count = 0.0, 0, 0, 0
            avg_q, avg_p, avg_change, poles = 0.0, 0.0, 0.0, 0
            dotd_count, mot_count, cd_count = 0, 0, 0
            best_pts_str = "N/A"

        badges = [
            f"Total Points: {tot_pts:.1f}",
            f"Wins: {wins}",
            f"Podiums: {podiums}",
            f"Fastest Laps: {fl_count}",
            f"Avg Qualifying: {avg_q:.1f}",
            f"Avg Place: {avg_p:.1f}",
            f"Avg Position Change: {avg_change:+.1f}",
            f"Pole Positions: {poles}",
            f"DOTD Awards: {dotd_count}",
            f"Most Overtakes: {mot_count}",
            f"Cleanest Driver: {cd_count}",
            f"Best: {best_pts_str}",
        ]

        all_pos_change_data = compute_all_time_avg_pos_change(num_seasons, entity_type, active_name)

        pts_per_race_data = []
        indiv_pos_change_data = []
        season_start_races = []

        if not df_races.empty:
            seasons_present = df_races["season"].unique()
            first_season = seasons_present[0] if len(seasons_present) > 0 else 1

            for s in seasons_present:
                if s > first_season:
                    s_races = df_races[df_races["season"] == s]
                    if not s_races.empty:
                        first_r_label = f"S{s} {s_races.iloc[0]['race']}"
                        season_start_races.append(first_r_label)

            for idx, row in df_races.iterrows():
                s_race_idx = int(row["season_race_idx"])
                pts_fill = RACE_COLORS[s_race_idx % len(RACE_COLORS)]
                pts_per_race_data.append({
                    "race": f"S{row['season']} {row['race']}",
                    "points": float(row["pts"]),
                    "fill": pts_fill,
                })

                p_chg = float(row["pos_change"])
                p_chg_fill = "#3cb44b" if p_chg > 0 else "#e6194b" if p_chg < 0 else "#888888"
                indiv_pos_change_data.append({
                    "race": f"S{row['season']} {row['race']}",
                    "pos_change": p_chg,
                    "fill": p_chg_fill,
                })

        placements_data = []
        fixed_categories = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th+"]
        place_counts = {cat: 0 for cat in fixed_categories}

        if not df_races.empty:
            valid_finishes = df_races[df_races["place"] > 0]["place"]
            for p_val in valid_finishes:
                p_int = int(p_val)
                if 1 <= p_int <= 9:
                    suffix = "st" if p_int == 1 else "nd" if p_int == 2 else "rd" if p_int == 3 else "th"
                    place_counts[f"{p_int}{suffix}"] += 1
                elif p_int >= 10:
                    place_counts["10th+"] += 1

        for cat in fixed_categories:
            placements_data.append({
                "placement": cat,
                "count": place_counts[cat],
            })

        track_total_pts_data = []
        track_avg_pts_data = []
        track_pos_change_data = []
        track_score_data = []

        if not df_races.empty:
            track_groups = df_races.groupby("track")
            alphabetical_tracks = sorted(list(track_groups.groups.keys()))

            for tr in alphabetical_tracks:
                t_df = track_groups.get_group(tr)
                t_tot_pts = float(t_df["pts"].sum())
                t_avg_pts = float(t_df["pts"].mean())
                t_valid_q = t_df[t_df["qual"] > 0]["qual"]
                t_valid_p = t_df[t_df["place"] > 0]["place"]
                t_avg_q = float(t_valid_q.mean()) if not t_valid_q.empty else 0.0
                t_avg_p = float(t_valid_p.mean()) if not t_valid_p.empty else 0.0
                t_pos_change = t_avg_q - t_avg_p

                track_total_pts_data.append({"track": tr, "total_points": round(t_tot_pts, 1)})
                track_avg_pts_data.append({"track": tr, "avg_points": round(t_avg_pts, 2)})

                t_chg_fill = "#3cb44b" if t_pos_change > 0 else "#e6194b" if t_pos_change < 0 else "#888888"
                track_pos_change_data.append({
                    "track": tr,
                    "pos_change": round(t_pos_change, 2),
                    "fill": t_chg_fill,
                })

                score = ((t_avg_pts / 30.0) * 0.6) + ((t_pos_change / 22.0) * 0.4)
                track_score_data.append({
                    "track": tr,
                    "score": round(score, 3),
                })

            track_score_data.sort(key=lambda x: x["score"], reverse=True)
            for idx, item in enumerate(track_score_data):
                if idx == 0:
                    item["fill"] = "#FFD700"
                elif idx == 1:
                    item["fill"] = "#C0C0C0"
                elif idx == 2:
                    item["fill"] = "#CD7F32"
                else:
                    item["fill"] = "#00b4da"

        return {
            "badges": badges,
            "all_pos_change_data": all_pos_change_data,
            "pts_per_race_data": pts_per_race_data,
            "placements_data": placements_data,
            "indiv_pos_change_data": indiv_pos_change_data,
            "track_total_pts_data": track_total_pts_data,
            "track_avg_pts_data": track_avg_pts_data,
            "track_pos_change_data": track_pos_change_data,
            "track_score_data": track_score_data,
            "season_start_races": season_start_races,
        }

    @rx.var(auto_deps=False, deps=["entity_type", "selected_driver", "selected_constructor"])
    def badges(self) -> list[str]:
        return self.calculated_data["badges"]

    @rx.var(auto_deps=False, deps=["entity_type", "selected_driver", "selected_constructor"])
    def all_pos_change_data(self) -> list[dict]:
        return self.calculated_data["all_pos_change_data"]

    @rx.var(auto_deps=False, deps=["entity_type", "selected_driver", "selected_constructor"])
    def pts_per_race_data(self) -> list[dict]:
        return self.calculated_data["pts_per_race_data"]

    @rx.var(auto_deps=False, deps=["entity_type", "selected_driver", "selected_constructor"])
    def placements_data(self) -> list[dict]:
        return self.calculated_data["placements_data"]

    @rx.var(auto_deps=False, deps=["entity_type", "selected_driver", "selected_constructor"])
    def indiv_pos_change_data(self) -> list[dict]:
        return self.calculated_data["indiv_pos_change_data"]

    @rx.var(auto_deps=False, deps=["entity_type", "selected_driver", "selected_constructor"])
    def track_total_pts_data(self) -> list[dict]:
        return self.calculated_data["track_total_pts_data"]

    @rx.var(auto_deps=False, deps=["entity_type", "selected_driver", "selected_constructor"])
    def track_avg_pts_data(self) -> list[dict]:
        return self.calculated_data["track_avg_pts_data"]

    @rx.var(auto_deps=False, deps=["entity_type", "selected_driver", "selected_constructor"])
    def track_pos_change_data(self) -> list[dict]:
        return self.calculated_data["track_pos_change_data"]

    @rx.var(auto_deps=False, deps=["entity_type", "selected_driver", "selected_constructor"])
    def track_score_data(self) -> list[dict]:
        return self.calculated_data["track_score_data"]

    @rx.var(auto_deps=False, deps=["entity_type", "selected_driver", "selected_constructor"])
    def season_start_races(self) -> list[str]:
        return self.calculated_data["season_start_races"]


def chart_card(title: str, chart_component: rx.Component) -> rx.Component:
    """Helper to wrap each chart with a prominent heading title on the main page (Requirement 79)."""
    return rx.vstack(
        rx.heading(
            title,
            size="4",
            color="white",
            font_weight="700",
            margin_bottom="1",
        ),
        chart_component,
        width="100%",
        align_items="start",
        spacing="2",
        margin_bottom="8",
    )


def detailed_stats_view(num_seasons: int = 5) -> rx.Component:
    """Render Detailed All Time Statistics for selected Driver or Constructor."""

    # 1. Simple Statistics Bubbles (Requirement 75 & 77)
    bubbles_component = rx.flex(
        rx.foreach(
            DetailedStatsState.badges,
            lambda b: rx.badge(
                b,
                color_scheme="cyan",
                variant="solid",
                font_size="11px",
                font_family="Outfit",
                font_weight="600",
                border_radius="md",
                padding_x="3",
                padding_y="1.5",
                margin="1",
            ),
        ),
        wrap="wrap",
        spacing="1",
        margin_bottom="6",
    )

    # 2. Average Positions Gained/Lost All Time (Requirement 69 & 79)
    pos_change_chart = chart_card(
        "Average Positions Gained/Lost All Time",
        zoomable_chart(
            lambda h: rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.1)"),
                rx.recharts.reference_line(y=0, stroke="#666666", custom_attrs={"isFront": False}),
                rx.recharts.bar(
                    rx.foreach(
                        DetailedStatsState.all_pos_change_data,
                        lambda item: rx.recharts.cell(fill=item["fill"]),
                    ),
                    data_key="avg_change",
                ),
                rx.recharts.x_axis(data_key="name", font_size=9, stroke="white", angle=-45, text_anchor="end", interval=0, height=60),
                rx.recharts.y_axis(stroke="white", width=35, tick={"fill": "white", "fontSize": 10}),
                data=DetailedStatsState.all_pos_change_data,
                margin={"top": 10, "right": 20, "left": 10, "bottom": 40},
                width="100%",
                height=h,
            ),
            title="Average Positions Gained/Lost All Time",
            chart_id="detailed_avg_pos_change",
            height=280,
            large_height=400,
        )
    )

    # 3. All Time Points Per Race (Requirement 71 & 79) - Dashed vertical lines behind bars at new seasons
    pts_per_race_chart = chart_card(
        "All Time Points Per Race",
        zoomable_chart(
            lambda h: rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.1)"),
                rx.foreach(
                    DetailedStatsState.season_start_races,
                    lambda r_label: rx.recharts.reference_line(
                        x=r_label,
                        stroke="white",
                        custom_attrs={"strokeDasharray": "3 3", "isFront": False},
                    ),
                ),
                rx.recharts.bar(
                    rx.foreach(
                        DetailedStatsState.pts_per_race_data,
                        lambda item: rx.recharts.cell(fill=item["fill"]),
                    ),
                    data_key="points",
                ),
                rx.recharts.x_axis(data_key="race", font_size=8, stroke="white", angle=-90, text_anchor="end", interval=0, height=80),
                rx.recharts.y_axis(stroke="white", width=35, tick={"fill": "white", "fontSize": 10}),
                data=DetailedStatsState.pts_per_race_data,
                margin={"top": 10, "right": 20, "left": 10, "bottom": 50},
                width="100%",
                height=h,
            ),
            title="All Time Points Per Race",
            chart_id="detailed_pts_per_race",
            height=280,
            large_height=400,
        )
    )

    # 4. Placements Summary (Requirement 73 & 79)
    placements_chart = chart_card(
        "Placements Summary",
        zoomable_chart(
            lambda h: rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.1)"),
                rx.recharts.bar(data_key="count", fill="#00b4da"),
                rx.recharts.x_axis(data_key="placement", font_size=10, stroke="white"),
                rx.recharts.y_axis(stroke="white", width=35, tick={"fill": "white", "fontSize": 10}),
                data=DetailedStatsState.placements_data,
                margin={"top": 10, "right": 20, "left": 10, "bottom": 20},
                width="100%",
                height=h,
            ),
            title="Placements Summary",
            chart_id="detailed_placements",
            height=250,
            large_height=360,
        )
    )

    # 5. Positions Gained/Lost Individual (Requirement 74 & 79) - Dashed vertical lines behind bars at new seasons
    indiv_pos_chart = chart_card(
        "Positions Gained/Lost Individual",
        zoomable_chart(
            lambda h: rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.1)"),
                rx.recharts.reference_line(y=0, stroke="#666666", custom_attrs={"isFront": False}),
                rx.foreach(
                    DetailedStatsState.season_start_races,
                    lambda r_label: rx.recharts.reference_line(
                        x=r_label,
                        stroke="white",
                        custom_attrs={"strokeDasharray": "3 3", "isFront": False},
                    ),
                ),
                rx.recharts.bar(
                    rx.foreach(
                        DetailedStatsState.indiv_pos_change_data,
                        lambda item: rx.recharts.cell(fill=item["fill"]),
                    ),
                    data_key="pos_change",
                ),
                rx.recharts.x_axis(data_key="race", font_size=8, stroke="white", angle=-90, text_anchor="end", interval=0, height=80),
                rx.recharts.y_axis(stroke="white", width=35, tick={"fill": "white", "fontSize": 10}),
                data=DetailedStatsState.indiv_pos_change_data,
                margin={"top": 10, "right": 20, "left": 10, "bottom": 50},
                width="100%",
                height=h,
            ),
            title="Positions Gained/Lost Individual",
            chart_id="detailed_indiv_pos_change",
            height=280,
            large_height=400,
        )
    )

    # 6. Per Track Statistics (Requirement 76 & 79) - Horizontal Bar Charts (tracks on Y-axis)
    track_tot_chart = chart_card(
        "Per Track Total Points Scored",
        zoomable_chart(
            lambda h: rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(horizontal=False, stroke="rgba(255, 255, 255, 0.1)"),
                rx.recharts.bar(data_key="total_points", fill="#00b4da"),
                rx.recharts.x_axis(type_="number", stroke="white", font_size=10),
                rx.recharts.y_axis(data_key="track", type_="category", stroke="white", font_size=9, width=110, interval=0),
                data=DetailedStatsState.track_total_pts_data,
                layout="vertical",
                margin={"top": 10, "right": 20, "left": 20, "bottom": 10},
                width="100%",
                height=h,
            ),
            title="Per Track Total Points Scored",
            chart_id="detailed_track_tot_pts",
            height=320,
            large_height=450,
        )
    )

    track_avg_chart = chart_card(
        "Per Track Average Points Scored",
        zoomable_chart(
            lambda h: rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(horizontal=False, stroke="rgba(255, 255, 255, 0.1)"),
                rx.recharts.bar(data_key="avg_points", fill="#00b4da"),
                rx.recharts.x_axis(type_="number", stroke="white", font_size=10),
                rx.recharts.y_axis(data_key="track", type_="category", stroke="white", font_size=9, width=110, interval=0),
                data=DetailedStatsState.track_avg_pts_data,
                layout="vertical",
                margin={"top": 10, "right": 20, "left": 20, "bottom": 10},
                width="100%",
                height=h,
            ),
            title="Per Track Average Points Scored",
            chart_id="detailed_track_avg_pts",
            height=320,
            large_height=450,
        )
    )

    track_pos_chart = chart_card(
        "Per Track Positions Gained/Lost",
        zoomable_chart(
            lambda h: rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(horizontal=False, stroke="rgba(255, 255, 255, 0.1)"),
                rx.recharts.reference_line(x=0, stroke="#666666", custom_attrs={"isFront": False}),
                rx.recharts.bar(
                    rx.foreach(
                        DetailedStatsState.track_pos_change_data,
                        lambda item: rx.recharts.cell(fill=item["fill"]),
                    ),
                    data_key="pos_change",
                ),
                rx.recharts.x_axis(type_="number", stroke="white", font_size=10),
                rx.recharts.y_axis(data_key="track", type_="category", stroke="white", font_size=9, width=110, interval=0),
                data=DetailedStatsState.track_pos_change_data,
                layout="vertical",
                margin={"top": 10, "right": 20, "left": 20, "bottom": 10},
                width="100%",
                height=h,
            ),
            title="Per Track Positions Gained/Lost",
            chart_id="detailed_track_pos_change",
            height=320,
            large_height=450,
        )
    )

    track_score_chart = chart_card(
        "Statistical Track Rating Score (Best to Worst)",
        zoomable_chart(
            lambda h: rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(horizontal=False, stroke="rgba(255, 255, 255, 0.1)"),
                rx.recharts.bar(
                    rx.foreach(
                        DetailedStatsState.track_score_data,
                        lambda item: rx.recharts.cell(fill=item["fill"]),
                    ),
                    data_key="score",
                ),
                rx.recharts.x_axis(type_="number", stroke="white", font_size=10),
                rx.recharts.y_axis(data_key="track", type_="category", stroke="white", font_size=9, width=110, interval=0),
                data=DetailedStatsState.track_score_data,
                layout="vertical",
                margin={"top": 10, "right": 20, "left": 20, "bottom": 10},
                width="100%",
                height=h,
            ),
            title="Statistical Track Rating Score (Best to Worst)",
            chart_id="detailed_track_score",
            height=340,
            large_height=480,
        )
    )

    # Selection Controls (Requirement 78)
    dropdown_section = rx.flex(
        rx.vstack(
            rx.text("Category", color="#AAAAAA", font_size="xs", font_weight="600"),
            rx.select(
                ["Driver", "Constructor"],
                value=DetailedStatsState.entity_type,
                on_change=DetailedStatsState.set_entity_type,
                bg="#18181C",
                color="white",
                border="1px solid #2C2C32",
                border_radius="md",
                width=["100%", "160px"],
                max_width="100%",
            ),
            align_items="start",
            spacing="1",
            width=["100%", "auto"],
        ),
        rx.vstack(
            rx.text("Selection", color="#AAAAAA", font_size="xs", font_weight="600"),
            rx.cond(
                DetailedStatsState.entity_type == "Constructor",
                rx.select(
                    DetailedStatsState.constructor_options,
                    value=DetailedStatsState.active_name,
                    on_change=DetailedStatsState.set_selected_constructor,
                    bg="#18181C",
                    color="white",
                    border="1px solid #2C2C32",
                    border_radius="md",
                    width=["100%", "220px"],
                    max_width="100%",
                ),
                rx.select(
                    DetailedStatsState.driver_options,
                    value=DetailedStatsState.active_name,
                    on_change=DetailedStatsState.set_selected_driver,
                    bg="#18181C",
                    color="white",
                    border="1px solid #2C2C32",
                    border_radius="md",
                    width=["100%", "220px"],
                    max_width="100%",
                ),
            ),
            align_items="start",
            spacing="1",
            width=["100%", "auto"],
        ),
        flex_wrap="wrap",
        gap="4",
        align="center",
        margin_bottom="6",
        width="100%",
        max_width="100%",
        padding_right=["4", "6", "8"],
    )

    return rx.vstack(
        rx.heading(
            "Detailed Statistics",
            size="6",
            color="white",
            font_weight="900",
            padding_top="2.5%",
            padding_bottom="1%",
        ),
        rx.text(
            "In-depth career metrics, position trends, race placement breakdown, and track performance scores.",
            color="#AAAAAA",
            font_size="sm",
            margin_bottom="4",
        ),
        dropdown_section,
        rx.heading(
            f"{DetailedStatsState.active_name} Overview",
            size="4",
            color="#00b4da",
            font_weight="700",
            margin_bottom="2",
        ),
        bubbles_component,
        pos_change_chart,
        pts_per_race_chart,
        placements_chart,
        indiv_pos_chart,
        track_tot_chart,
        track_avg_chart,
        track_pos_chart,
        track_score_chart,
        width="100%",
        max_width="100%",
        align_items="start",
        margin_bottom="160px",
        padding_right=["6", "8", "10"],
        padding_left=["2", "4"],
    )
