"""Tab 4 — Driver Statistics (Reflex).

Per-driver accordions with stat callout badges and charts.
Handles variable column availability across seasons (DOTD/MOT/CD only S4+).
"""

import math

import numpy as np
import pandas as pd
import reflex as rx
from the_alternative_f1.articles.components import (
    zoomable_chart,
    chart_card,
)
from the_alternative_f1.race_metrics import parse_status


def is_truthy(val) -> bool:
    if isinstance(val, bool):
        return val
    if val is None:
        return False
    return str(val).strip().upper() in ("Y", "YES", "TRUE", "1")


def Tab4(data: dict, season_data: dict, sprint_only_var=None, toggle_sprint_only=None) -> rx.Component:
    """Render the Driver Statistics tab."""
    new_df = data["new_df"]
    new_df_FL = data["new_df_FL"]
    new_df_DOTD = data["new_df_DOTD"]
    new_df_MOT = data["new_df_MOT"]
    new_df_Q = data["new_df_Q"]
    new_df_Place = data["new_df_Place"]
    new_df_EffectivePlace = data.get("new_df_EffectivePlace", new_df_Place)
    new_df_EffectiveQ = data.get("new_df_EffectiveQ", new_df_Q)
    new_df_PosChange = data.get("new_df_PosChange")
    new_df_CD = data["new_df_CD"]
    races_points_only = data["races_points_only"]
    index_x = data["index_x"]
    has_fl = data.get("has_fl", len(new_df_FL.columns) > 1)
    has_dotd = data.get("has_dotd", len(new_df_DOTD.columns) > 1)
    has_mot = data.get("has_mot", len(new_df_MOT.columns) > 1)
    has_cd = data.get("has_cd", len(new_df_CD.columns) > 1)
    has_dotd_mot_cd = data.get("has_dotd_mot_cd", has_dotd or has_mot or has_cd)
    season_num = season_data["season_number"]
    team_colors = data.get("team_colors", {})
    drivers_points_df = data["drivers_points_df"]
    driver_to_team = dict(zip(drivers_points_df["Driver"], drivers_points_df["Team"]))

    # 15+ unique colors for per-race bars
    race_colors = [
        "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
        "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe",
        "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000",
        "#aaffc3", "#808000", "#ffd8b1", "#000075", "#808080",
    ]

    driver_items = []

    # ── Super License Points Expander ─────────────────────────────────────
    sl_points_data = season_data.get("super_license_points", {})
    sl_header_cells = [
        rx.table.column_header_cell(
            "Driver",
            color="#00b4da",
            font_weight="bold",
            font_size="11px",
            vertical_align="bottom",
            padding_bottom="8px",
        )
    ]
    for r in races_points_only:
        sl_header_cells.append(
            rx.table.column_header_cell(
                rx.box(
                    rx.text(
                        str(r),
                        color="#00b4da",
                        font_weight="bold",
                        font_size="11px",
                        white_space="nowrap",
                    ),
                    writing_mode="vertical-rl",
                    transform="rotate(180deg)",
                    margin="0 auto",
                    display="inline-block",
                ),
                text_align="center",
                vertical_align="bottom",
                padding_bottom="8px",
                padding_x="4px",
            )
        )
    sl_header_cells.append(
        rx.table.column_header_cell(
            "Total",
            color="#00b4da",
            font_weight="bold",
            font_size="11px",
            text_align="center",
            vertical_align="bottom",
            padding_bottom="8px",
        )
    )

    sl_drivers = []
    for i in range(len(new_df)):
        d_name = new_df["Driver"].iloc[i]
        pts_list = sl_points_data.get(d_name, [])
        if len(pts_list) < len(races_points_only):
            pts_list = pts_list + [0] * (len(races_points_only) - len(pts_list))
        else:
            pts_list = pts_list[:len(races_points_only)]
        
        total_sl = sum(pts_list)
        
        # Find the index of the first race where points were earned (> 0)
        first_earned_idx = len(pts_list)
        for idx, val in enumerate(pts_list):
            if val > 0:
                first_earned_idx = idx
                break
        
        sl_drivers.append({
            "driver": d_name,
            "pts_list": pts_list,
            "total": total_sl,
            "first_earned": first_earned_idx,
            "original_index": i
        })
    
    # Sort by total points descending, then by earliest race index where points were earned ascending,
    # and fallback to original standings index ascending.
    sl_drivers.sort(key=lambda x: (-x["total"], x["first_earned"], x["original_index"]))

    sl_table_rows = []
    for item in sl_drivers:
        d_name = item["driver"]
        pts_list = item["pts_list"]
        total_sl = item["total"]
        if total_sl == 0:
            continue
        
        cells = [
            rx.table.cell(d_name, color="white", font_weight="600", font_size="sm")
        ]
        
        for val in pts_list:
            cells.append(
                rx.table.cell(
                    str(val) if val > 0 else "—",
                    color="red" if val > 0 else "#888888",
                    text_align="center",
                    font_size="sm",
                    font_weight="bold" if val > 0 else "normal",
                )
            )
        
        cells.append(
            rx.table.cell(
                str(total_sl),
                color="red" if total_sl > 0 else "white",
                text_align="center",
                font_weight="bold",
                font_size="sm",
            )
        )
        sl_table_rows.append(
            rx.table.row(*cells, _hover={"bg": "#1C1C20"})
        )

    sl_expander = rx.accordion.item(
        rx.accordion.trigger(
            rx.hstack(
                rx.icon("award", color="#00b4da", size=18),
                rx.text("FIA Super License Penalty Points", color="white", font_weight="600"),
                align="center",
                spacing="2",
            )
        ),
        rx.accordion.content(
            rx.vstack(
                rx.text(
                    "Penalty points added to driver super licenses for driving infractions. Accumulating points leads to grid penalties.",
                    color="#AAAAAA",
                    font_size="xs",
                ),
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(*sl_header_cells),
                        ),
                        rx.table.body(*sl_table_rows),
                        width="100%",
                        variant="ghost",
                    ),
                    width="100%",
                    overflow_x="auto",
                    bg="#111115",
                    padding="3",
                    border_radius="lg",
                    border="1px solid #2D2D32",
                ),
                width="100%",
                spacing="3",
                padding_y="2",
            )
        ),
        value="super_license_item",
        bg="#525259",
        border_radius="md",
        padding_x="3",
        margin_y="1",
    )
    driver_items.append(sl_expander)

    for i in range(len(new_df)):
        driver_name = new_df["Driver"].iloc[i]
        driver_points = new_df.iloc[i, 1:].tolist()

        index_a = int(index_x + 0.5)
        num_completed = index_a

        # Retrieve place, qualifying, and pos change series for this driver
        driver_qualifying = []
        driver_place_list = []
        driver_pos_changes = []

        if new_df_EffectiveQ is not None and len(new_df_EffectiveQ.columns) > 1:
            driver_qualifying = new_df_EffectiveQ.iloc[i, 1:index_a + 1].tolist()
        elif len(new_df_Q.columns) > 1:
            driver_qualifying = new_df_Q.iloc[i, 1:index_a + 1].tolist()

        if new_df_EffectivePlace is not None and len(new_df_EffectivePlace.columns) > 1:
            driver_place_list = new_df_EffectivePlace.iloc[i, 1:index_a + 1].tolist()
        elif len(new_df_Place.columns) > 1:
            driver_place_list = new_df_Place.iloc[i, 1:index_a + 1].tolist()

        if new_df_PosChange is not None and len(new_df_PosChange.columns) > 1:
            driver_pos_changes = new_df_PosChange.iloc[i, 1:index_a + 1].tolist()

        raw_places = new_df_Place.iloc[i, 1:index_a + 1].tolist() if (new_df_Place is not None and len(new_df_Place.columns) > 1) else []

        # ── Points per race bar chart ────────────────────────────────────
        pts_bar_data = []
        for j in range(num_completed):
            race = races_points_only[j]
            pts = driver_points[j] if j < len(driver_points) else 0
            pts_bar_data.append({
                "race": race,
                "points": float(pts) if not pd.isnull(pts) else 0,
                "fill": race_colors[j % len(race_colors)],
            })

        # Calculate dynamic x-axis height for pts_chart
        max_race_len = max([len(str(item.get("race", ""))) for item in pts_bar_data] or [0])
        race_axis_height = max(40, max_race_len * 5 + 15)
        pos_pts = "top_right"

        pts_chart = zoomable_chart(
            lambda h: rx.recharts.bar_chart(
                rx.recharts.bar(data_key="points", name="Points"),
                rx.recharts.x_axis(data_key="race", font_size=6, angle=-90, height=race_axis_height, stroke="white", text_anchor="end", interval=0, tick={"dx": -5}),
                rx.recharts.y_axis(
                    stroke="white",
                    width=35,
                    tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
                ),
                rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.2)"),
                data=pts_bar_data,
                margin={"top": 10, "right": 20, "left": 35, "bottom": 30},
                width="100%",
                height=h,
            ),
            title=f"{driver_name} - Points Per Race",
            chart_id=f"pts_chart_{i}",
            height=220,
            large_height=350,
            download_position=pos_pts,
        )

        # ── Best finish (based on actual finishing place) ───────────────
        best_race_info = None
        for j in range(index_a):
            raw_p = raw_places[j] if j < len(raw_places) else None
            p_val = driver_place_list[j] if j < len(driver_place_list) else None
            status_p = parse_status(raw_p, season_num) if raw_p is not None else parse_status(p_val, season_num)
            if status_p in ("EMPTY", "DNS") or (p_val is None and raw_p is None) or (pd.isnull(p_val) and pd.isnull(raw_p)):
                continue

            pts = float(driver_points[j]) if j < len(driver_points) and not pd.isnull(driver_points[j]) else 0.0
            race = races_points_only[j] if j < len(races_points_only) else "—"

            if status_p == "FINISH":
                try:
                    p_num = int(float(raw_p if raw_p is not None and not pd.isnull(raw_p) else p_val))
                except (ValueError, TypeError):
                    p_num = 99
                rank = (0, p_num, -pts)
                suffix = "st" if p_num == 1 else "nd" if p_num == 2 else "rd" if p_num == 3 else "th"
                label = f"{p_num}{suffix}"
            else:
                rank = (1, 99, -pts)
                label = status_p

            if best_race_info is None or rank < best_race_info["rank"]:
                pts_str = f"{pts:.1f}" if pts % 1 != 0 else f"{int(pts)}"
                best_race_info = {
                    "rank": rank,
                    "label": label,
                    "race": race,
                    "pts_str": pts_str,
                }

        if best_race_info:
            best_finish = f"Best: {best_race_info['label']} at {best_race_info['race']} ({best_race_info['pts_str']} pts)"
        else:
            best_finish = "Best: —"

        # ── Placement summary chart (based on actual finishing place) ───
        placements = [0] * 10
        places_list = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th+"]
        for j in range(index_a):
            raw_p = raw_places[j] if j < len(raw_places) else None
            p_val = driver_place_list[j] if j < len(driver_place_list) else None
            status_p = parse_status(raw_p, season_num) if raw_p is not None else parse_status(p_val, season_num)
            if status_p in ("EMPTY", "DNS") or (p_val is None and raw_p is None) or (pd.isnull(p_val) and pd.isnull(raw_p)):
                continue

            if status_p == "FINISH":
                try:
                    p_num = int(float(raw_p if raw_p is not None and not pd.isnull(raw_p) else p_val))
                except (ValueError, TypeError):
                    p_num = int(float(p_val)) if p_val is not None and not pd.isnull(p_val) else 10
                if 1 <= p_num <= 9:
                    placements[p_num - 1] += 1
                elif p_num >= 10:
                    placements[9] += 1
            elif status_p in ("DNF", "DSQ"):
                placements[9] += 1

        placement_data = [{"place": places_list[k], "count": placements[k]} for k in range(10)]

        # Calculate dynamic x-axis height for placement_chart
        max_place_len = max([len(str(item.get("place", ""))) for item in placement_data] or [0])
        place_axis_height = max(40, max_place_len * 5 + 15)
        pos_plc = "top_right"

        placement_chart = zoomable_chart(
            lambda h: rx.recharts.bar_chart(
                rx.recharts.bar(data_key="count", fill="#00b4da", name="Count"),
                rx.recharts.x_axis(data_key="place", font_size=7, stroke="white", angle=-90, text_anchor="end", height=place_axis_height, interval=0, tick={"dx": -5}),
                rx.recharts.y_axis(
                    stroke="white",
                    width=35,
                    tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
                ),
                rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.2)"),
                data=placement_data,
                margin={"top": 10, "right": 20, "left": 35, "bottom": 30},
                width="100%",
                height=h,
            ),
            title=f"{driver_name} - Placements Summary",
            chart_id=f"placement_chart_{i}",
            height=220,
            large_height=350,
            download_position=pos_plc,
        )

        # ── Wins & Podiums (derived directly from actual finishing places) ──
        wins = placements[0]
        podiums = sum(placements[:3])

        # ── Total points ─────────────────────────────────────────────────
        valid_pts = [p for p in driver_points if not pd.isnull(p)]
        total_pts = sum(valid_pts)

        # ── Fastest laps ────────────────────────────────────────────────
        fl_count = 0
        if len(new_df_FL.columns) > 1:
            fl_values = new_df_FL.iloc[i, 1:].tolist()
            fl_count = sum(1 for v in fl_values if is_truthy(v))

        # Positions gained/lost (exclude DNS / unrun races)
        pos_change_data = []
        for j in range(index_a):
            race = races_points_only[j] if j < len(races_points_only) else f"R{j+1}"
            chg = driver_pos_changes[j] if j < len(driver_pos_changes) else None
            if chg is not None and not pd.isnull(chg):
                val = float(chg)
                pos_change_data.append({
                    "race": race,
                    "change": val,
                    "fill": "green" if val >= 0 else "red",
                })
            else:
                pos_change_data.append({
                    "race": race,
                    "change": None,
                    "fill": "#555555",
                })

        # Calculate dynamic x-axis height for pos_chart
        max_pos_race_len = max([len(str(item.get("race", ""))) for item in pos_change_data] or [0])
        pos_race_axis_height = max(40, max_pos_race_len * 5 + 15)
        pos_gained = "top_right"

        pos_chart = zoomable_chart(
            lambda h: rx.recharts.bar_chart(
                rx.recharts.bar(data_key="change", name="Change"),
                rx.recharts.x_axis(data_key="race", font_size=6, angle=-90, height=pos_race_axis_height, stroke="white", text_anchor="end", interval=0, tick={"dx": -5}),
                rx.recharts.y_axis(
                    stroke="white",
                    width=35,
                    tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
                ),
                rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.2)"),
                rx.recharts.reference_line(y=0, stroke="#555555"),
                data=pos_change_data,
                margin={"top": 10, "right": 20, "left": 35, "bottom": 30},
                width="100%",
                height=h,
            ),
            title=f"{driver_name} - Positions Gained/Lost",
            chart_id=f"pos_chart_{i}",
            height=220,
            large_height=350,
            download_position=pos_gained,
        )

        # ── Averages (only across races actually competed) ──────────────
        valid_chg = [float(c) for c in driver_pos_changes if c is not None and not pd.isnull(c)]
        avg_change = sum(valid_chg) / len(valid_chg) if valid_chg else 0.0

        valid_q = [float(q) for q in driver_qualifying if q is not None and not pd.isnull(q) and q > 0]
        avg_qualifying = sum(valid_q) / len(valid_q) if valid_q else 0.0

        valid_p = [float(p) for p in driver_place_list if p is not None and not pd.isnull(p) and p > 0]
        avg_place = sum(valid_p) / len(valid_p) if valid_p else 0.0

        # ── Pole positions ──────────────────────────────────────────────
        pole_positions = sum(1 for q in driver_qualifying if q == 1) if len(driver_qualifying) > 0 else 0

        # ── DOTD, MOT, CD counts (conditional) ──────────────────────────
        dotd_count = 0
        mot_count = 0
        cd_count = 0

        if has_dotd_mot_cd:
            if len(new_df_DOTD.columns) > 1:
                dotd_vals = new_df_DOTD.iloc[i, 1:].tolist()
                dotd_count = sum(1 for v in dotd_vals if is_truthy(v))
            if len(new_df_MOT.columns) > 1:
                mot_vals = new_df_MOT.iloc[i, 1:].tolist()
                mot_count = sum(1 for v in mot_vals if is_truthy(v))
            if len(new_df_CD.columns) > 1:
                cd_vals = new_df_CD.iloc[i, 1:].tolist()
                cd_count = sum(1 for v in cd_vals if is_truthy(v))

        # ── Single season win streak & podium streak calculations (Req 81 & 82) ──
        max_ss_win_streak = 0
        curr_ss_win_streak = 0
        max_ss_podium_streak = 0
        curr_ss_podium_streak = 0

        for j in range(num_completed):
            race_name = str(races_points_only[j]).strip() if j < len(races_points_only) else ""
            raw_p = raw_places[j] if j < len(raw_places) else None
            p_val = driver_place_list[j] if j < len(driver_place_list) else None
            status_p = parse_status(raw_p, season_num) if raw_p is not None else parse_status(p_val, season_num)

            p_finish = None
            if status_p == "FINISH":
                try:
                    p_finish = float(raw_p if raw_p is not None and not pd.isnull(raw_p) else p_val)
                except (ValueError, TypeError):
                    p_finish = float(p_val) if p_val is not None and not pd.isnull(p_val) else None

            # Single season win streak logic (consecutive 1st place finishes)
            if p_finish == 1.0:
                curr_ss_win_streak += 1
                max_ss_win_streak = max(max_ss_win_streak, curr_ss_win_streak)
            else:
                curr_ss_win_streak = 0

            # Single season podium streak logic (exclude preseason, sprint, and postseason races)
            if race_name.startswith(("Pre", "Post")) or "Sprint" in race_name:
                continue

            is_podium = (p_finish is not None and 1.0 <= p_finish <= 3.0)
            if is_podium:
                curr_ss_podium_streak += 1
                max_ss_podium_streak = max(max_ss_podium_streak, curr_ss_podium_streak)
            else:
                curr_ss_podium_streak = 0

        # ── Build stat badges ────────────────────────────────────────────
        badges = [
            f"Total Points: {total_pts:.1f}",
            f"Wins: {wins}",
            f"Single Season Win Streak: {max_ss_win_streak}",
            f"Podiums: {podiums}",
            f"Single Season Podium Streak: {max_ss_podium_streak}",
        ]
        if has_fl:
            badges.append(f"Fastest Laps: {fl_count}")
        badges.extend([
            f"Avg Qualifying: {avg_qualifying:.1f}",
            f"Avg Place: {avg_place:.1f}",
            f"Avg Pos Change: {avg_change:+.1f}",
            f"Pole Positions: {pole_positions}",
        ])
        if has_dotd:
            badges.append(f"DOTD Awards: {dotd_count}")
        if has_mot:
            badges.append(f"Most Overtakes: {mot_count}")
        if has_cd:
            badges.append(f"Cleanest Driver: {cd_count}")
        badges.append(best_finish)

        badge_components = [
            rx.badge(
                b,
                color_scheme="cyan",
                variant="solid",
                font_size="11px",
                font_family="Outfit",
                font_weight="600",
                border_radius="md",
                padding_x="3",
                padding_y="1.5",
            )
            for b in badges
        ]

        total_points = sum(p for p in driver_points if not pd.isnull(p))
        pts_str = f"{total_points:.1f}" if total_points % 1 != 0 else f"{int(total_points)}"
        bg_color = "#525259" if (i + 1) % 2 == 0 else "#3C3C41"
        team_name = driver_to_team.get(driver_name, "—")
        driver_items.append(
            rx.accordion.item(
                rx.accordion.trigger(
                    rx.flex(
                        rx.vstack(
                            rx.text(driver_name, color="white", font_weight="600"),
                            rx.text(f"Points: {pts_str}", color="#00b4da", font_size="10px", font_weight="bold"),
                            align_items="start",
                            spacing="0",
                        ),
                        rx.hstack(
                            rx.box(
                                width="4px",
                                height="16px",
                                bg=team_colors.get(team_name, "#555555"),
                                border_radius="2px",
                                flex_shrink="0",
                            ),
                            rx.text(team_name, color="#CCCCCC", font_size="xs", font_weight="500"),
                            spacing="2",
                            align="center",
                            margin_right="4",
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                    )
                ),
                rx.accordion.content(
                    rx.vstack(
                        # Stat badges in a responsive grid
                        rx.flex(
                            *badge_components,
                            flex_wrap="wrap",
                            gap=["2", "3", "4", "5"],
                            justify="center",
                            align="center",
                            width="100%",
                        ),
                        # Charts
                        rx.grid(
                            chart_card(
                                title="Points Per Race",
                                chart_component=pts_chart,
                                chart_id=f"pts_chart_{i}",
                                download_position=pos_pts,
                                border_radius="xl",
                                padding=["12px", "16px", "16px"],
                                box_shadow="0 4px 16px rgba(0,0,0,0.3)",
                                font_size="13px",
                            ),
                            chart_card(
                                title="Placements Summary",
                                chart_component=placement_chart,
                                chart_id=f"placement_chart_{i}",
                                download_position=pos_plc,
                                border_radius="xl",
                                padding=["12px", "16px", "16px"],
                                box_shadow="0 4px 16px rgba(0,0,0,0.3)",
                                font_size="13px",
                            ),
                            chart_card(
                                title="Positions Gained/Lost",
                                chart_component=pos_chart,
                                chart_id=f"pos_chart_{i}",
                                download_position=pos_gained,
                                border_radius="xl",
                                padding=["12px", "16px", "16px"],
                                box_shadow="0 4px 16px rgba(0,0,0,0.3)",
                                font_size="13px",
                            ),
                            columns=rx.breakpoints(initial="1", md="3"),
                            spacing="4",
                            width="100%",
                        ),
                        width="100%",
                        spacing="4",
                    ),
                ),
                value=f"driver_{i}",
                bg=bg_color,
                border_radius="md",
                padding_x="3",
                margin_y="1",
            )
        )

    has_sprint = data.get("has_sprint", False)

    return rx.vstack(
        rx.flex(
            rx.heading(
                f"Season {season_num} Driver Statistics",
                size="6",
                color="white",
                font_weight="900",
            ),
            rx.spacer(),
            rx.cond(
                has_sprint & (sprint_only_var is not None),
                rx.hstack(
                    rx.text("Sprint Championship", color="white", font_size="sm", font_weight="600"),
                    rx.switch(
                        checked=sprint_only_var,
                        on_change=toggle_sprint_only,
                        color_scheme="cyan",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.fragment()
            ),
            width="100%",
            direction=rx.breakpoints(initial="column", sm="row"),
            align=rx.breakpoints(initial="start", sm="center"),
            gap="4",
            padding_y="2.5%",
            padding_x="2%",
        ),
        rx.accordion.root(
            *driver_items,
            collapsible=True,
            width="100%",
            variant="ghost",
        ),
        width="100%",
        align_items="start",
        spacing="4",
        bg="transparent",
        padding="4",
        border_radius="xl",
    )