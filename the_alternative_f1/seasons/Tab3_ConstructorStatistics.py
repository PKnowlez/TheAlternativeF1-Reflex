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

    # ── Stacked constructor points bar chart ─────────────────────────────
    # Build data for a horizontal stacked bar chart showing each team's
    # driver contributions
    drivers_points_df_copy = drivers_points_df.copy()
    drivers_points_df_copy["Points"] = pd.to_numeric(
        drivers_points_df_copy["Points"], errors="coerce"
    ).fillna(0)

    team_total_points = (
        drivers_points_df_copy.groupby("Team")["Points"]
        .sum()
        .sort_values(ascending=True)
    )
    sorted_teams = team_total_points.index.tolist()

    # Build stacked data: each item = {team, driver1_points, driver2_points, ...}
    driver_color_map = dict(zip(colors_driver_df["Driver"], colors_driver_df["Color"]))
    all_drivers_in_chart = set()

    stacked_data = []
    for team in sorted_teams:
        team_drivers = drivers_points_df_copy[
            drivers_points_df_copy["Team"] == team
        ].reset_index(drop=True)
        item = {"team": team}
        for _, row in team_drivers.iterrows():
            d_name = row["Driver"]
            item[d_name] = float(row["Points"])
            all_drivers_in_chart.add(d_name)
        stacked_data.append(item)

    all_drivers_list = list(all_drivers_in_chart)

    stacked_chart = rx.recharts.bar_chart(
        *[
            rx.recharts.bar(
                data_key=driver,
                fill=driver_color_map.get(driver, "#555555"),
                stack_id="a",
                name=driver,
            )
            for driver in all_drivers_list
        ],
        rx.recharts.x_axis(data_key="team", type_="category", font_size=10),
        rx.recharts.y_axis(type_="number", font_size=10),
        rx.recharts.legend(layout="vertical", align="right", vertical_align="middle", style={"color": "white"}),
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        data=stacked_data,
        width="100%",
        height=max(300, len(sorted_teams) * 45),
        layout="vertical",
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
        for j, race in enumerate(team_races_points_only):
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
            rx.recharts.x_axis(data_key="race", font_size=9, angle=-45, height=60),
            rx.recharts.y_axis(font_size=10),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            data=bar_data,
            width="100%",
            height=250,
        )

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
                        rx.grid(
                            rx.badge(
                                f"Total Points: {total_pts:.1f}",
                                color_scheme="cyan",
                                variant="solid",
                                font_size="11px",
                            ),
                            rx.badge(
                                best_result,
                                color_scheme="cyan",
                                variant="outline",
                                font_size="11px",
                            ),
                            columns=rx.breakpoints(initial="1", sm="2"),
                            spacing="2",
                            width="100%",
                        ),
                        team_chart,
                        width="100%",
                        spacing="3",
                    ),
                ),
                value=f"constructor_{idx}",
            )
        )

    return rx.vstack(
        rx.heading(
            f"Season {season_num} Constructor Statistics",
            size="6",
            color="white",
            font_weight="900",
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
                border="1px solid #2C2C32",
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
                border="1px solid #2C2C32",
            ),
            columns=rx.breakpoints(initial="1", md="2"),
            spacing="5",
            width="100%",
        ),
        width="100%",
        align_items="start",
        spacing="5",
    )