"""Tab 5 — Driver Comparisons (Reflex).

Comparison bar charts for all drivers or rookies only. The rookies toggle
is driven by SeasonsState.rookies_only (managed in the main app State).
"""

import math

import numpy as np
import pandas as pd
import reflex as rx


def Tab5(data: dict, season_data: dict, rookies_only: bool = False, rookies_only_var = None, toggle_rookies_only = None) -> rx.Component:
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
    index_x = data["index_x"]
    rookies = data["rookies"]
    driver_colors = data["driver_colors"]
    rookie_line_data = data["rookie_line_data"]
    season_num = season_data["season_number"]

    # ── Build full data ──────────────────────────────────────────────────
    index_a = int(index_x + 0.5)
    average_changed = []
    average_qualifying = []
    average_place = []

    for i in range(len(new_df)):
        dq = []
        dp = []
        if len(new_df_Q.columns) > 1:
            dq = new_df_Q.iloc[i, 1:index_a + 1].tolist()
            dq = pd.to_numeric(dq, errors="coerce")
            dq = np.nan_to_num(dq, nan=0)
        if len(new_df_Place.columns) > 1:
            dp = new_df_Place.iloc[i, 1:index_a + 1].tolist()
            dp = pd.to_numeric(dp, errors="coerce")
            dp = np.nan_to_num(dp, nan=0)

        non_zero_q = [q for q in dq if q > 0] if len(dq) > 0 else []
        non_zero_p = [p for p in dp if p > 0] if len(dp) > 0 else []
        avg_q = sum(non_zero_q) / len(non_zero_q) if non_zero_q else 0
        avg_p = sum(non_zero_p) / len(non_zero_p) if non_zero_p else 0
        average_qualifying.append(avg_q)
        average_place.append(avg_p)
        average_changed.append(avg_q - avg_p)

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

    pos_change_chart = rx.recharts.bar_chart(
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
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        rx.recharts.reference_line(y=0, stroke="#555555"),
        data=pos_change_data,
        margin={"top": 10, "right": 20, "left": 35, "bottom": 40},
        margin_left="-10px",
        width="100%",
        height=300,
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

    pts_chart = rx.recharts.bar_chart(
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
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        data=pts_data,
        margin={"top": 10, "right": 20, "left": 35, "bottom": 40},
        margin_left="-10px",
        width="100%",
        height=300,
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

    qual_chart = rx.recharts.bar_chart(
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
        data=qual_data,
        width="100%",
        height=300,
        layout="vertical",
        margin={"left": 60, "right": 25, "top": 10, "bottom": 10},
        margin_left="-10px",
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

    place_chart = rx.recharts.bar_chart(
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
        data=place_data,
        width="100%",
        height=300,
        layout="vertical",
        margin={"left": 60, "right": 25, "top": 10, "bottom": 10},
        margin_left="-10px",
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

        rookie_chart_component = rx.vstack(
            rx.text("Rookie of the Year", color="white", font_weight="700", font_size="sm"),
            rx.recharts.line_chart(
                *[
                    rx.recharts.line(
                        data_key=r,
                        stroke=driver_colors.get(r, "#555555"),
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
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                data=rookie_line_data,
                margin={"top": 10, "right": 20, "left": 35, "bottom": 30},
                margin_left="-10px",
                width="100%",
                height=300,
            ),
            rx.accordion.root(
                rx.accordion.item(
                    rx.accordion.trigger(
                        rx.text("Key", color="#555555", font_weight="600", font_size="13px", font_family="Outfit"),
                    ),
                    rx.accordion.content(
                        rx.flex(
                            *[
                                rx.text(r, color=driver_colors.get(r, "#555555"), font_size="13px", font_family="Outfit", font_weight="600", text_shadow="0px 1px 4px rgba(0,0,0,0.2)")
                                for r in rookie_names
                            ],
                            flex_wrap="wrap",
                            gap="24px",
                        ),
                    ),
                    value="rookie_key",
                ),
                collapsible=True,
                width="100%",
                variant="ghost",
                bg="#F0F0F2",
                border_radius="6px",
                border="1px solid #CCCCCC",
                box_shadow="0 2px 8px rgba(0,0,0,0.15)",
            ),
            width="100%",
            bg="transparent",
            padding="4",
            border_radius="xl",
        )

    return rx.vstack(
        rx.heading(
            f"Season {season_num} Driver Comparisons",
            size="6",
            color="white",
            font_weight="900",
            padding_y="2.5%",
            padding_x="2%",
        ),
        # Rookies toggle
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
                margin_bottom="4",
                padding_x="2%",
            ),
            rx.fragment()
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
            rx.vstack(
                rx.text("Points Per Driver", color="white", font_weight="700", font_size="sm"),
                pts_chart,
                width="100%",
                spacing="2",
                bg="transparent",
                padding="4",
                border_radius="xl",
            ),
            rx.vstack(
                rx.text("Avg Positions Gained/Lost", color="white", font_weight="700", font_size="sm"),
                pos_change_chart,
                width="100%",
                spacing="2",
                bg="transparent",
                padding="4",
                border_radius="xl",
            ),
            rx.vstack(
                rx.text("Average Qualifying Position", color="white", font_weight="700", font_size="sm"),
                qual_chart,
                rx.text(
                    "Qualifying Position",
                    color="white",
                    font_size="11px",
                    font_family="Outfit",
                    font_weight="500",
                    margin_top="-2",
                    margin_left="40px",
                    align_self="center",
                ),
                width="100%",
                spacing="2",
                bg="transparent",
                padding="4",
                border_radius="xl",
            ),
            rx.vstack(
                rx.text("Average Place", color="white", font_weight="700", font_size="sm"),
                place_chart,
                rx.text(
                    "Place",
                    color="white",
                    font_size="11px",
                    font_family="Outfit",
                    font_weight="500",
                    margin_top="-2",
                    margin_left="40px",
                    align_self="center",
                ),
                width="100%",
                spacing="2",
                bg="transparent",
                padding="4",
                border_radius="xl",
            ),
            columns=rx.breakpoints(initial="1", md="2"),
            spacing="5",
            width="100%",
        ),

        width="100%",
        align_items="start",
        spacing="5",
    )
