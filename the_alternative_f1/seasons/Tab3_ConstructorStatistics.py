"""Tab 3 — Constructor Statistics (Reflex).

Stacked constructor points chart and individual constructor accordions
with per-race bar charts and callout stats.
"""

import reflex as rx
import pandas as pd


def Tab3(data: dict, season_data: dict) -> rx.Component:
    """Render the Constructor Statistics tab."""
    team_df = data["team_df"]
    team_races_points_only = data["team_races_points_only"]
    drivers_points_df = data["drivers_points_df"]
    colors_driver_df = data["colors_driver_df"]
    team_colors = data["team_colors"]
    season_num = season_data["season_number"]

    # ── Grouped constructor points bar chart ─────────────────────────────
    drivers_points_df_copy = drivers_points_df.copy()
    drivers_points_df_copy["Points"] = pd.to_numeric(
        drivers_points_df_copy["Points"], errors="coerce"
    ).fillna(0)

    # Sort teams by total points descending to place the highest at the top
    team_total_points = (
        drivers_points_df_copy.groupby("Team")["Points"]
        .sum()
        .sort_values(ascending=False)
    )
    sorted_teams = team_total_points.index.tolist()

    # Group drivers by team
    team_to_drivers = {}
    for _, row in drivers_points_df_copy.iterrows():
        t = row["Team"]
        d = row["Driver"]
        p = float(row["Points"])
        if t not in team_to_drivers:
            team_to_drivers[t] = []
        if d not in [x[0] for x in team_to_drivers[t]]:
            team_to_drivers[t].append((d, p))

    # Sort drivers within each team by points descending
    for t in team_to_drivers:
        team_to_drivers[t] = sorted(team_to_drivers[t], key=lambda x: x[1], reverse=True)

    if team_to_drivers:
        max_drivers = max(len(drivers) for drivers in team_to_drivers.values())
    else:
        max_drivers = 0

    driver_color_map = dict(zip(colors_driver_df["Driver"], colors_driver_df["Color"]))

    stacked_data = []
    for team in sorted_teams:
        drivers = team_to_drivers.get(team, [])
        item = {"team": team}
        for k in range(max_drivers):
            if k < len(drivers):
                d_name, d_pts = drivers[k]
                item[f"driver_{k}_pts"] = d_pts
                item[f"driver_{k}_color"] = driver_color_map.get(d_name, "#555555")
            else:
                item[f"driver_{k}_pts"] = 0
                item[f"driver_{k}_color"] = "transparent"
        stacked_data.append(item)

    # Create the Bar components with child Cells for custom coloring
    bar_components = []
    for k in range(max_drivers):
        cells = [
            rx.recharts.cell(fill=item[f"driver_{k}_color"])
            for item in stacked_data
        ]
        bar_components.append(
            rx.recharts.bar(
                *cells,
                data_key=f"driver_{k}_pts",
            )
        )

    stacked_chart = rx.recharts.bar_chart(
        *bar_components,
        rx.recharts.y_axis(
            data_key="team",
            type_="category",
            stroke="white",
            interval=0,
            width=95,
            tick={"textAnchor": "start", "dx": -85, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
        ),
        rx.recharts.x_axis(type_="number", font_size=10, stroke="white"),
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        data=stacked_data,
        width="100%",
        height=max(300, len(sorted_teams) * 45),
        layout="vertical",
        bar_gap=0,
        margin={"left": 95, "right": 10, "top": 10, "bottom": 10},
        margin_left="-10px",
    )

    # ── Individual constructor accordions ────────────────────────────────
    # 15 unique colors for per-race bars
    race_colors = [
        "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
        "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe",
        "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000",
        "#aaffc3", "#808000", "#ffd8b1", "#000075", "#808080",
    ]

    constructor_items = []
    for idx in range(len(team_df)):
        team_name = team_df["Team"].iloc[idx]
        team_points = team_df.iloc[idx, 1:].tolist()

        # Bar chart data for this constructor
        bar_data = []
        num_completed = int(data["index_x"] + 0.5)
        for j in range(num_completed):
            race = team_races_points_only[j]
            pts = team_points[j] if j < len(team_points) else 0
            bar_data.append({
                "race": race,
                "points": float(pts) if not pd.isnull(pts) else 0,
                "fill": race_colors[j % len(race_colors)],
            })

        # Stats
        valid_points = [p for p in team_points if not pd.isnull(p) and p > 0]
        if valid_points:
            highest_score = max(valid_points)
            index = team_points.index(highest_score)
            best_result = f"Best Result: {team_races_points_only[index]} ({highest_score} pts)"
        else:
            best_result = "Best Result: —"

        total_pts = sum(p for p in team_points if not pd.isnull(p))

        team_chart = rx.recharts.bar_chart(
            rx.recharts.bar(data_key="points", name="Points"),
            rx.recharts.x_axis(data_key="race", font_size=9, angle=-90, height=80, stroke="white", text_anchor="end", interval=0),
            rx.recharts.y_axis(
                stroke="white",
                width=35,
                tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
            ),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            data=bar_data,
            margin={"top": 10, "right": 20, "left": 35, "bottom": 30},
            margin_left="-10px",
            width="100%",
            height=250,
        )

        bg_color = "#525259" if idx % 2 == 0 else "#3C3C41"
        constructor_items.append(
            rx.accordion.item(
                rx.accordion.trigger(
                    rx.hstack(
                        rx.box(
                            width="8px",
                            height="8px",
                            bg=team_colors.get(team_name, "#555555"),
                            border_radius="50%",
                            flex_shrink="0",
                        ),
                        rx.text(team_name, color="white", font_weight="600"),
                        spacing="2",
                        align="center",
                    ),
                ),
                rx.accordion.content(
                    rx.vstack(
                        rx.flex(
                            rx.badge(
                                f"Total Points: {total_pts:.1f}",
                                color_scheme="cyan",
                                variant="solid",
                                font_size="11px",
                                font_family="Outfit",
                                font_weight="600",
                                border_radius="md",
                                padding_x="3",
                                padding_y="1.5",
                            ),
                            rx.badge(
                                best_result,
                                color_scheme="cyan",
                                variant="outline",
                                font_size="11px",
                                font_family="Outfit",
                                font_weight="600",
                                border_radius="md",
                                padding_x="3",
                                padding_y="1.5",
                            ),
                            flex_wrap="wrap",
                            gap=["2", "3", "4", "5"],
                            justify="center",
                            align="center",
                            width="100%",
                        ),
                        team_chart,
                        width="100%",
                        spacing="3",
                    ),
                ),
                value=f"constructor_{idx}",
                bg=bg_color,
                border_radius="md",
                padding_x="3",
                margin_y="1",
            )
        )

    return rx.vstack(
        rx.heading(
            f"Season {season_num} Constructor Statistics",
            size="6",
            color="white",
            font_weight="900",
            padding_y="2.5%",
            padding_x="2%",
        ),
        rx.grid(
            # Left: Stacked chart
            rx.vstack(
                rx.text(
                    "Stacked Constructor Points",
                    color="white",
                    font_weight="700",
                    font_size="sm",
                ),
                rx.box(
                    stacked_chart,
                    width="100%",
                    overflow_x="auto",
                ),
                width="100%",
                spacing="3",
                bg="transparent",
                padding="4",
                border_radius="xl",
            ),
            # Right: Individual constructors
            rx.vstack(
                rx.text(
                    "Individual Constructor Statistics",
                    color="white",
                    font_weight="700",
                    font_size="sm",
                ),
                rx.accordion.root(
                    *constructor_items,
                    collapsible=True,
                    width="100%",
                    variant="ghost",
                ),
                width="100%",
                spacing="3",
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