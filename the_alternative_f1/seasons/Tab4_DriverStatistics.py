"""Tab 4 — Driver Statistics (Reflex).

Per-driver accordions with stat callout badges and charts.
Handles variable column availability across seasons (DOTD/MOT/CD only S4+).
"""

import math

import numpy as np
import pandas as pd
import reflex as rx
from the_alternative_f1.articles.components import zoomable_chart


def Tab4(data: dict, season_data: dict, sprint_only_var=None, toggle_sprint_only=None) -> rx.Component:
    """Render the Driver Statistics tab."""
    new_df = data["new_df"]
    new_df_FL = data["new_df_FL"]
    new_df_DOTD = data["new_df_DOTD"]
    new_df_MOT = data["new_df_MOT"]
    new_df_Q = data["new_df_Q"]
    new_df_Place = data["new_df_Place"]
    new_df_CD = data["new_df_CD"]
    races_points_only = data["races_points_only"]
    index_x = data["index_x"]
    has_dotd_mot_cd = data["has_dotd_mot_cd"]
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
        )
    ]
    for r in races_points_only:
        sl_header_cells.append(
            rx.table.column_header_cell(
                str(r),
                color="#00b4da",
                font_weight="bold",
                font_size="11px",
                text_align="center",
            )
        )
    sl_header_cells.append(
        rx.table.column_header_cell(
            "Total",
            color="#00b4da",
            font_weight="bold",
            font_size="11px",
            text_align="center",
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

        # ── Points per race bar chart ────────────────────────────────────
        pts_bar_data = []
        num_completed = int(season_data.get("index_x", 0) + 0.5) if "index_x" in season_data else int(new_df.columns.size - 1)
        # Wait, calculations data has "index_x", but let's check: Calculations returns "index_x" in the data dict!
        # So since the function parameter is `data: dict`, we can do:
        num_completed = int(data["index_x"] + 0.5)
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

        pts_chart = zoomable_chart(
            lambda h: rx.recharts.bar_chart(
                rx.recharts.bar(data_key="points", name="Points"),
                rx.recharts.x_axis(data_key="race", font_size=6, angle=-90, height=race_axis_height, stroke="white", text_anchor="end", interval=0, tick={"dx": -5}),
                rx.recharts.y_axis(
                    stroke="white",
                    width=35,
                    tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
                ),
                rx.recharts.cartesian_grid(vertical=False, stroke="rgba(0, 0, 0, 0.25)"),
                data=pts_bar_data,
                margin={"top": 10, "right": 20, "left": 35, "bottom": 30},
                margin_left="-10px",
                width="100%",
                height=h,
            ),
            title=f"{driver_name} - Points Per Race",
            chart_id=f"pts_chart_{i}",
            height=220,
            large_height=350
        )

        # ── Best finish ──────────────────────────────────────────────────
        valid_pts = [p for p in driver_points if not pd.isnull(p)]
        highest_score = max(valid_pts) if valid_pts else 0
        idx_best = driver_points.index(highest_score) if highest_score > 0 else 0

        place_labels = {
            25: "1st", 18: "2nd", 15: "3rd", 12: "4th",
            10: "5th", 8: "6th", 6: "7th", 4: "8th", 3: "9th",
        }
        place = "10th+"
        for threshold, label in place_labels.items():
            if highest_score >= threshold:
                place = label
                break

        best_race = races_points_only[idx_best] if idx_best < len(races_points_only) else "—"
        best_finish = f"Best: {place} at {best_race} ({highest_score} pts)"

        # ── Wins ─────────────────────────────────────────────────────────
        wins = sum(1 for p in valid_pts if p >= 25)

        # ── Podiums ──────────────────────────────────────────────────────
        podiums = sum(1 for p in valid_pts if p >= 15)

        # ── Total points ─────────────────────────────────────────────────
        total_pts = sum(valid_pts)

        # ── Placement summary chart ──────────────────────────────────────
        placements = [0] * 10
        places_list = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th+"]
        thresholds = [25, 18, 15, 12, 10, 8, 6, 4, 3, 0.5]
        for val in valid_pts:
            for k, t in enumerate(thresholds):
                if val >= t:
                    placements[k] += 1
                    break

        placement_data = [{"place": places_list[k], "count": placements[k]} for k in range(10)]

        # Calculate dynamic x-axis height for placement_chart
        max_place_len = max([len(str(item.get("place", ""))) for item in placement_data] or [0])
        place_axis_height = max(40, max_place_len * 5 + 15)

        placement_chart = zoomable_chart(
            lambda h: rx.recharts.bar_chart(
                rx.recharts.bar(data_key="count", fill="#00b4da", name="Count"),
                rx.recharts.x_axis(data_key="place", font_size=7, stroke="white", angle=-90, text_anchor="end", height=place_axis_height, interval=0, tick={"dx": -5}),
                rx.recharts.y_axis(
                    stroke="white",
                    width=35,
                    tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
                ),
                rx.recharts.cartesian_grid(vertical=False, stroke="rgba(0, 0, 0, 0.25)"),
                data=placement_data,
                margin={"top": 10, "right": 20, "left": 35, "bottom": 30},
                margin_left="-10px",
                width="100%",
                height=h,
            ),
            title=f"{driver_name} - Placements Summary",
            chart_id=f"placement_chart_{i}",
            height=220,
            large_height=350
        )

        # ── Fastest laps ────────────────────────────────────────────────
        fl_count = 0
        if len(new_df_FL.columns) > 1:
            fl_values = new_df_FL.iloc[i, 1:].tolist()
            fl_count = sum(1 for v in fl_values if str(v).upper() == "Y")

        # ── Qualifying vs place analysis ────────────────────────────────
        index_a = int(index_x + 0.5)
        driver_qualifying = []
        driver_place_list = []

        if len(new_df_Q.columns) > 1:
            driver_qualifying = new_df_Q.iloc[i, 1:index_a + 1].tolist()
            driver_qualifying = pd.to_numeric(driver_qualifying, errors="coerce")
            driver_qualifying = np.nan_to_num(driver_qualifying, nan=0)

        if len(new_df_Place.columns) > 1:
            driver_place_list = new_df_Place.iloc[i, 1:index_a + 1].tolist()
            driver_place_list = pd.to_numeric(driver_place_list, errors="coerce")
            driver_place_list = np.nan_to_num(driver_place_list, nan=0)

        # Positions gained/lost
        qualifying_place = []
        if len(driver_qualifying) > 0 and len(driver_place_list) > 0:
            qualifying_place = [
                float(q - p) for q, p in zip(driver_qualifying, driver_place_list)
            ]

        pos_change_data = []
        for j, val in enumerate(qualifying_place):
            race = races_points_only[j] if j < len(races_points_only) else f"R{j+1}"
            pos_change_data.append({
                "race": race,
                "change": val,
                "fill": "green" if val >= 0 else "red",
            })

        # Calculate dynamic x-axis height for pos_chart
        max_pos_race_len = max([len(str(item.get("race", ""))) for item in pos_change_data] or [0])
        pos_race_axis_height = max(40, max_pos_race_len * 5 + 15)

        pos_chart = zoomable_chart(
            lambda h: rx.recharts.bar_chart(
                rx.recharts.bar(data_key="change", name="Change"),
                rx.recharts.x_axis(data_key="race", font_size=6, angle=-90, height=pos_race_axis_height, stroke="white", text_anchor="end", interval=0, tick={"dx": -5}),
                rx.recharts.y_axis(
                    stroke="white",
                    width=35,
                    tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
                ),
                rx.recharts.cartesian_grid(vertical=False, stroke="rgba(0, 0, 0, 0.25)"),
                rx.recharts.reference_line(y=0, stroke="#555555"),
                data=pos_change_data,
                margin={"top": 10, "right": 20, "left": 35, "bottom": 30},
                margin_left="-10px",
                width="100%",
                height=h,
            ),
            title=f"{driver_name} - Positions Gained/Lost",
            chart_id=f"pos_chart_{i}",
            height=220,
            large_height=350
        )

        # ── Averages ────────────────────────────────────────────────────
        avg_qualifying = 0.0
        if len(driver_qualifying) > 0:
            non_zero_q = [q for q in driver_qualifying if q > 0]
            avg_qualifying = sum(non_zero_q) / len(non_zero_q) if non_zero_q else 0

        avg_place = 0.0
        if len(driver_place_list) > 0:
            non_zero_p = [p for p in driver_place_list if p > 0]
            avg_place = sum(non_zero_p) / len(non_zero_p) if non_zero_p else 0

        avg_change = avg_qualifying - avg_place

        # ── Pole positions ──────────────────────────────────────────────
        pole_positions = sum(1 for q in driver_qualifying if q == 1) if len(driver_qualifying) > 0 else 0

        # ── DOTD, MOT, CD counts (conditional) ──────────────────────────
        dotd_count = 0
        mot_count = 0
        cd_count = 0

        if has_dotd_mot_cd:
            if len(new_df_DOTD.columns) > 1:
                dotd_vals = new_df_DOTD.iloc[i, 1:].tolist()
                dotd_count = sum(1 for v in dotd_vals if str(v).upper() == "Y")
            if len(new_df_MOT.columns) > 1:
                mot_vals = new_df_MOT.iloc[i, 1:].tolist()
                mot_count = sum(1 for v in mot_vals if str(v).upper() == "Y")
            if len(new_df_CD.columns) > 1:
                cd_vals = new_df_CD.iloc[i, 1:].tolist()
                cd_count = sum(1 for v in cd_vals if str(v).upper() == "Y")

        # ── Build stat badges ────────────────────────────────────────────
        badges = [
            f"Total Points: {total_pts:.1f}",
            f"Wins: {wins}",
            f"Podiums: {podiums}",
            f"Fastest Laps: {fl_count}",
            f"Avg Qualifying: {avg_qualifying:.1f}",
            f"Avg Place: {avg_place:.1f}",
            f"Avg Pos Change: {avg_change:+.1f}",
            f"Pole Positions: {pole_positions}",
        ]
        if has_dotd_mot_cd:
            badges.extend([
                f"DOTD Awards: {dotd_count}",
                f"Most Overtakes: {mot_count}",
                f"Cleanest Driver: {cd_count}",
            ])
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
                            rx.vstack(
                                rx.text("Points Per Race", color="#AAAAAA", font_size="xs"),
                                pts_chart,
                                width="100%",
                                spacing="1",
                            ),
                            rx.vstack(
                                rx.text("Placements Summary", color="#AAAAAA", font_size="xs"),
                                placement_chart,
                                width="100%",
                                spacing="1",
                            ),
                            rx.vstack(
                                rx.text("Positions Gained/Lost", color="#AAAAAA", font_size="xs"),
                                pos_chart,
                                width="100%",
                                spacing="1",
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
        rx.hstack(
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
            align="center",
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