"""Tab 5 — Driver Comparisons (Reflex).

Comparison bar charts for all drivers or rookies only. The rookies toggle
is driven by SeasonsState.rookies_only (managed in the main app State).
"""

import math

import numpy as np
import pandas as pd
import reflex as rx
from the_alternative_f1.articles.components import (
    zoomable_chart,
    interactive_line_chart_key,
    chart_card,
)
from the_alternative_f1.race_metrics import parse_status



def Tab5(data: dict, season_data: dict, rookies_only: bool = False, rookies_only_var = None, toggle_rookies_only = None, sprint_only_var = None, toggle_sprint_only = None) -> rx.Component:
    """Render the Driver Comparisons tab.

    Parameters
    ----------
    data : dict
        Computed data from Calculations().
    season_data : dict
        Season config dict.
    rookies_only : bool
        Whether to filter to rookies only (controlled by state).
    """
    new_df = data["new_df"]
    drivers_total_points = data["drivers_total_points"]
    new_df_Q = data["new_df_Q"]
    new_df_Place = data["new_df_Place"]
    new_df_EffectivePlace = data.get("new_df_EffectivePlace", new_df_Place)
    new_df_EffectiveQ = data.get("new_df_EffectiveQ", new_df_Q)
    new_df_PosChange = data.get("new_df_PosChange")
    index_x = data["index_x"]
    rookies = data["rookies"]
    driver_colors = data["driver_colors"]
    rookie_line_data = data["rookie_line_data"]
    season_num = season_data["season_number"]

    # ── Build full data ──────────────────────────────────────────────────
    index_a = int(index_x + 0.5)
    max_drivers = len(new_df)
    average_changed = []
    average_qualifying = []
    average_place = []

    for i in range(len(new_df)):
        dq = []
        dp = []
        dchg = []
        if new_df_EffectiveQ is not None and len(new_df_EffectiveQ.columns) > 1:
            dq = new_df_EffectiveQ.iloc[i, 1:index_a + 1].tolist()
        elif len(new_df_Q.columns) > 1:
            dq = new_df_Q.iloc[i, 1:index_a + 1].tolist()

        if new_df_EffectivePlace is not None and len(new_df_EffectivePlace.columns) > 1:
            dp = new_df_EffectivePlace.iloc[i, 1:index_a + 1].tolist()
        elif len(new_df_Place.columns) > 1:
            dp = new_df_Place.iloc[i, 1:index_a + 1].tolist()

        if new_df_PosChange is not None and len(new_df_PosChange.columns) > 1:
            dchg = new_df_PosChange.iloc[i, 1:index_a + 1].tolist()

        raw_places = new_df_Place.iloc[i, 1:index_a + 1].tolist() if len(new_df_Place.columns) > 1 else []
        raw_quals = new_df_Q.iloc[i, 1:index_a + 1].tolist() if len(new_df_Q.columns) > 1 else []

        valid_q = []
        valid_p = []

        for j in range(index_a):
            raw_p = raw_places[j] if j < len(raw_places) else None
            status_p = parse_status(raw_p, season_num)

            raw_q = raw_quals[j] if j < len(raw_quals) else None
            status_q = parse_status(raw_q, season_num)

            # Qualifying
            if status_q == "DNS" or status_p == "DNS":
                eff_q = dq[j] if j < len(dq) else None
                if eff_q is not None and not pd.isnull(eff_q) and eff_q > 0 and status_p != "DNS":
                    valid_q.append(float(eff_q))
                else:
                    valid_q.append(float(max_drivers))
            elif status_q != "EMPTY":
                val_q = dq[j] if j < len(dq) else None
                if val_q is not None and not pd.isnull(val_q) and val_q > 0:
                    valid_q.append(float(val_q))
                elif raw_q is not None and not pd.isnull(raw_q):
                    try:
                        q_num = float(raw_q)
                        if q_num > 0:
                            valid_q.append(q_num)
                    except (ValueError, TypeError):
                        pass

            # Place
            if status_p == "DNS":
                valid_p.append(float(max_drivers))
            elif status_p != "EMPTY":
                val_p = dp[j] if j < len(dp) else None
                if val_p is not None and not pd.isnull(val_p) and val_p > 0:
                    valid_p.append(float(val_p))
                elif raw_p is not None and not pd.isnull(raw_p):
                    try:
                        p_num = float(raw_p)
                        if p_num > 0:
                            valid_p.append(p_num)
                    except (ValueError, TypeError):
                        pass

        valid_chg = [float(c) for c in dchg if c is not None and not pd.isnull(c)]

        avg_q = sum(valid_q) / len(valid_q) if valid_q else 0.0
        avg_p = sum(valid_p) / len(valid_p) if valid_p else 0.0
        avg_chg = sum(valid_chg) / len(valid_chg) if valid_chg else (avg_q - avg_p)

        average_qualifying.append(avg_q)
        average_place.append(avg_p)
        average_changed.append(avg_chg)

    full_data_df = pd.DataFrame({
        "Driver": new_df["Driver"],
        "average_changed": average_changed,
        "drivers_total_points": drivers_total_points,
        "average_qualifying": average_qualifying,
        "average_place": average_place,
    })

    # Filter for rookies if enabled
    if rookies_only and rookies:
        filtered_df = full_data_df[full_data_df["Driver"].isin(rookies)]
    else:
        filtered_df = full_data_df

    # ── Average Positions Gained or Lost ─────────────────────────────────
    avg_changed_df = filtered_df.sort_values(by="average_changed", ascending=False)
    pos_change_data = [
        {
            "driver": row["Driver"],
            "change": round(row["average_changed"], 1),
            "fill": "green" if row["average_changed"] >= 0 else "red",
        }
        for _, row in avg_changed_df.iterrows()
    ]

    max_pos_change_driver_len = max([len(str(item.get("driver", ""))) for item in pos_change_data] or [0])
    pos_change_driver_axis_height = max(40, max_pos_change_driver_len * 5 + 15)
    pos_chg = "top_right"

    pos_change_chart = zoomable_chart(
        lambda h: rx.recharts.bar_chart(
            rx.recharts.bar(
                *[
                    rx.recharts.cell(fill=item["fill"])
                    for item in pos_change_data
                ],
                data_key="change",
                name="Pos Change",
            ),
            rx.recharts.x_axis(data_key="driver", font_size=7, angle=-90, height=pos_change_driver_axis_height, stroke="white", text_anchor="end", interval=0, style={"fontFamily": "Outfit"}, tick={"dx": -5}),
            rx.recharts.y_axis(
                stroke="white",
                width=35,
                tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
            ),
            rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.2)"),
            rx.recharts.reference_line(y=0, stroke="#555555"),
            data=pos_change_data,
            margin={"top": 10, "right": 20, "left": 35, "bottom": 40},
            width="100%",
            height=h,
        ),
        title="Average Positions Changed",
        chart_id="pos_change_chart",
        height=300,
        large_height=400,
        download_position=pos_chg,
    )

    # ── Points Per Driver ────────────────────────────────────────────────
    drivers_pts_df = filtered_df.sort_values(by="drivers_total_points", ascending=False)

    # Gold/silver/bronze for top 3, then theme color
    pts_data = []
    medal_colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
    for idx, (_, row) in enumerate(drivers_pts_df.iterrows()):
        fill = medal_colors[idx] if idx < 3 else "#0068c9"
        pts_data.append({
            "driver": row["Driver"],
            "points": round(row["drivers_total_points"], 1),
            "fill": fill,
        })

    max_pts_driver_len = max([len(str(item.get("driver", ""))) for item in pts_data] or [0])
    pts_driver_axis_height = max(40, max_pts_driver_len * 5 + 15)
    pos_pts = "top_right"

    pts_chart = zoomable_chart(
        lambda h: rx.recharts.bar_chart(
            rx.recharts.bar(
                *[
                    rx.recharts.cell(fill=item["fill"])
                    for item in pts_data
                ],
                data_key="points",
                name="Points",
            ),
            rx.recharts.x_axis(data_key="driver", font_size=7, angle=-90, height=pts_driver_axis_height, stroke="white", text_anchor="end", interval=0, style={"fontFamily": "Outfit"}, tick={"dx": -5}),
            rx.recharts.y_axis(
                stroke="white",
                width=35,
                tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
            ),
            rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.2)"),
            data=pts_data,
            margin={"top": 10, "right": 20, "left": 35, "bottom": 40},
            width="100%",
            height=h,
        ),
        title="Points Per Driver",
        chart_id="pts_chart",
        height=300,
        large_height=400,
        download_position=pos_pts,
    )

    # ── Average Qualifying Position ──────────────────────────────────────
    avg_qual_df = filtered_df.sort_values(by="average_qualifying", ascending=True)
    qual_data = []
    medal_colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
    for idx, (_, row) in enumerate(avg_qual_df.iterrows()):
        fill = medal_colors[idx] if idx < 3 else "#0068c9"
        qual_data.append({
            "driver": row["Driver"],
            "qualifying": round(row["average_qualifying"], 1),
            "fill": fill,
        })

    pos_qual = "top_right"

    qual_chart = zoomable_chart(
        lambda h: rx.recharts.bar_chart(
            rx.recharts.bar(
                *[
                    rx.recharts.cell(fill=item["fill"])
                    for item in qual_data
                ],
                data_key="qualifying",
                name="Avg Qualifying",
            ),
            rx.recharts.y_axis(
                data_key="driver",
                type_="category",
                stroke="white",
                interval=0,
                axis_line=False,
                tick_line=False,
                width=60,
                tick={"textAnchor": "start", "dx": -50, "fill": "white", "fontSize": 9, "fontFamily": "Outfit"},
            ),
            rx.recharts.x_axis(
                type_="number",
                font_size=8,
                stroke="white",
                style={"fontFamily": "Outfit"},
            ),
            rx.recharts.cartesian_grid(stroke="rgba(255, 255, 255, 0.2)", stroke_dasharray="3 3"),
            data=qual_data,
            width="100%",
            height=h,
            layout="vertical",
            margin={"left": 60, "right": 25, "top": 10, "bottom": 10},
        ),
        title="Average Qualifying Position",
        chart_id="qual_chart",
        height=300,
        large_height=400,
        download_position=pos_qual,
    )

    # ── Average Place ────────────────────────────────────────────────────
    avg_place_df = filtered_df.sort_values(by="average_place", ascending=True)
    place_data = []
    for idx, (_, row) in enumerate(avg_place_df.iterrows()):
        fill = medal_colors[idx] if idx < 3 else "#0068c9"
        place_data.append({
            "driver": row["Driver"],
            "place": round(row["average_place"], 1),
            "fill": fill,
        })

    pos_plc = "top_right"

    place_chart = zoomable_chart(
        lambda h: rx.recharts.bar_chart(
            rx.recharts.bar(
                *[
                    rx.recharts.cell(fill=item["fill"])
                    for item in place_data
                ],
                data_key="place",
                name="Avg Place",
            ),
            rx.recharts.y_axis(
                data_key="driver",
                type_="category",
                stroke="white",
                interval=0,
                axis_line=False,
                tick_line=False,
                width=60,
                tick={"textAnchor": "start", "dx": -50, "fill": "white", "fontSize": 9, "fontFamily": "Outfit"},
            ),
            rx.recharts.x_axis(
                type_="number",
                font_size=8,
                stroke="white",
                style={"fontFamily": "Outfit"},
            ),
            rx.recharts.cartesian_grid(stroke="rgba(255, 255, 255, 0.2)", stroke_dasharray="3 3"),
            data=place_data,
            width="100%",
            height=h,
            layout="vertical",
            margin={"left": 60, "right": 25, "top": 10, "bottom": 10},
        ),
        title="Average Place",
        chart_id="place_chart",
        height=300,
        large_height=400,
        download_position=pos_plc,
    )

    # ── Leader badges ────────────────────────────────────────────────────
    leader_badges = []
    if not drivers_pts_df.empty:
        pts_leader = drivers_pts_df.iloc[0]["Driver"]
        leader_badges.append(f"Points Leader: {pts_leader}")
    if not avg_changed_df.empty:
        pos_leader = avg_changed_df.iloc[0]["Driver"]
        leader_badges.append(f"Positions Gained Leader: {pos_leader}")
    if not avg_qual_df.empty:
        qual_leader = avg_qual_df.iloc[0]["Driver"]
        leader_badges.append(f"Qualifying Leader: {qual_leader}")
    if not avg_place_df.empty:
        place_leader = avg_place_df.iloc[0]["Driver"]
        leader_badges.append(f"Place Leader: {place_leader}")

    # ── Rookie of the Year chart (shown only when rookies_only) ──────────
    rookie_chart_component = rx.fragment()
    if rookies_only and rookie_line_data and rookies:
        rookie_names = [d for d in rookies if d in driver_colors]
        
        # Calculate dynamic x-axis height
        max_rookie_race_len = max([len(str(item.get("race", ""))) for item in rookie_line_data] or [0])
        rookie_race_axis_height = max(40, max_rookie_race_len * 5 + 15)
        rookie_legend_margin = max(15, rookie_race_axis_height - 30)
        pos_rookie = "top_right"

        rookie_chart = zoomable_chart(
            lambda h: rx.recharts.line_chart(
                *[
                    rx.recharts.line(
                        data_key=r,
                        stroke=driver_colors.get(r, "#555555"),
                        stroke_width=2,
                        dot={"fill": driver_colors.get(r, "#555555"), "stroke": driver_colors.get(r, "#555555")},
                        name=r,
                        type_="monotone",
                    )
                    for r in rookie_names
                ],
                rx.recharts.x_axis(data_key="race", font_size=8, angle=-90, height=rookie_race_axis_height, stroke="white", text_anchor="end", interval=0, tick={"dx": -5}),
                rx.recharts.y_axis(
                    stroke="white",
                    width=35,
                    tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
                ),
                rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.2)"),
                rx.recharts.graphing_tooltip(),
                data=rookie_line_data,
                margin={"top": 10, "right": 20, "left": 35, "bottom": 30},
                width="100%",
                height=h,
            ),
            title="Rookie of the Year",
            chart_id="rookie_chart",
            height=300,
            large_height=400,
            download_position=pos_rookie,
        )

        rookie_chart_component = chart_card(
            title="Rookie of the Year",
            chart_component=rookie_chart,
            chart_id="rookie_chart",
            download_position=pos_rookie,
            extra_content=interactive_line_chart_key(
                chart_id="rookie_chart",
                items=[(r, driver_colors.get(r, "#555555")) for r in rookie_names],
                title="Key (Rookies)",
                hint="Click rookie to highlight",
            ),
        )

    has_sprint = data.get("has_sprint", False)

    return rx.vstack(
        rx.flex(
            rx.heading(
                f"Season {season_num} Driver Comparisons",
                size="6",
                color="white",
                font_weight="900",
            ),
            rx.spacer(),
            rx.vstack(
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
                rx.cond(
                    (rookies_only_var is not None) & (len(season_data.get("rookies", [])) > 0),
                    rx.hstack(
                        rx.text("Rookies Only", color="white", font_size="sm", font_weight="600"),
                        rx.switch(
                            checked=rookies_only_var,
                            on_change=toggle_rookies_only,
                            color_scheme="cyan",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.fragment()
                ),
                spacing="2",
                align_items=rx.breakpoints(initial="start", sm="end"),
            ),
            width="100%",
            direction=rx.breakpoints(initial="column", sm="row"),
            align=rx.breakpoints(initial="start", sm="center"),
            gap="2",
            padding_y="2.5%",
            padding_x="2%",
        ),

        # Leader badges
        rx.flex(
            *[
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
                for b in leader_badges
            ],
            flex_wrap="wrap",
            gap=["2", "3", "4", "5"],
            justify="center",
            align="center",
            width="100%",
            margin_bottom="4",
        ),

        # Rookie chart (conditional)
        rookie_chart_component,

        # Comparison charts: 2 columns on wide, stacked on narrow
        rx.grid(
            chart_card(
                title="Points Per Driver",
                chart_component=pts_chart,
                chart_id="pts_chart",
                download_position=pos_pts,
            ),
            chart_card(
                title="Avg Positions Gained/Lost",
                chart_component=pos_change_chart,
                chart_id="pos_change_chart",
                download_position=pos_chg,
            ),
            chart_card(
                title="Average Qualifying Position",
                chart_component=qual_chart,
                chart_id="qual_chart",
                download_position=pos_qual,
                extra_content=rx.text(
                    "Qualifying Position",
                    color="white",
                    font_size="11px",
                    font_family="Outfit",
                    font_weight="500",
                    margin_top="-2",
                    margin_left="40px",
                    align_self="center",
                ),
            ),
            chart_card(
                title="Average Place",
                chart_component=place_chart,
                chart_id="place_chart",
                download_position=pos_plc,
                extra_content=rx.text(
                    "Place",
                    color="white",
                    font_size="11px",
                    font_family="Outfit",
                    font_weight="500",
                    margin_top="-2",
                    margin_left="40px",
                    align_self="center",
                ),
            ),
            columns=rx.breakpoints(initial="1", md="2"),
            spacing="5",
            width="100%",
        ),

        width="100%",
        align_items="start",
        spacing="5",
    )
