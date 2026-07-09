"""Tab 1 — Standings (Reflex).

Constructor and Driver championship standings with line/bar charts and
scrollable modal popups for full standings tables.
"""

import reflex as rx
from the_alternative_f1.articles.components import zoomable_chart, DownloadState


def Tab1(data: dict, season_data: dict, sprint_only_var=None, toggle_sprint_only=None) -> rx.Component:
    """Render the Standings tab.

    Parameters
    ----------
    data : dict
        Computed data from Calculations().
    season_data : dict
        The season config dict from season_N.py.
    """
    team_colors = data["team_colors"]
    driver_colors = data["driver_colors"]
    constructor_totals = data["constructor_totals"]
    driver_totals = data["driver_totals"]
    team_line_data = data["team_line_data"]
    driver_line_data = data["driver_line_data"]
    races_with_start = data["races_with_start"]
    drivers_points_df = data["drivers_points_df"]

    # Calculate dynamic x-axis heights based on longest label
    max_team_race_len = max([len(str(item.get("race", ""))) for item in team_line_data] or [0])
    team_race_axis_height = max(40, max_team_race_len * 5 + 15)

    max_driver_race_len = max([len(str(item.get("race", ""))) for item in driver_line_data] or [0])
    driver_race_axis_height = max(40, max_driver_race_len * 5 + 15)

    # Dynamic legend top margin based on longest label (ensures legend clears labels)
    team_race_legend_margin = max(15, team_race_axis_height - 30)
    driver_race_legend_margin = max(15, driver_race_axis_height - 30)

    # ── Constructor line chart ───────────────────────────────────────────
    team_names = list(team_colors.keys())
    # Filter to only teams present in the data
    teams_in_data = [t for t in constructor_totals["Team"]]

    constructor_line_chart = zoomable_chart(
        lambda h: rx.recharts.line_chart(
            *[
                rx.recharts.line(
                    data_key=team,
                    stroke=team_colors.get(team, "#555555"),
                    dot={"fill": team_colors.get(team, "#555555"), "stroke": team_colors.get(team, "#555555")},
                    name=team,
                    type_="monotone",
                )
                for team in teams_in_data
            ],
            rx.recharts.x_axis(data_key="race", font_size=8, angle=-90, height=team_race_axis_height, stroke="white", text_anchor="end", interval=0, tick={"dx": -5}),
            rx.recharts.y_axis(
                stroke="white",
                width=35,
                tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
            ),
            rx.recharts.cartesian_grid(vertical=False, stroke="rgba(0, 0, 0, 0.25)"),
            data=team_line_data,
            margin={"top": 10, "right": 20, "left": 35, "bottom": 30},
            margin_left="-10px",
            width="100%",
            height=h,
        ),
        title="Constructor's Championship",
        chart_id="constructor_line_chart",
        height=350,
        large_height=450
    )

    # ── Constructor legend expander ──────────────────────────────────────
    constructor_legend_expander = rx.accordion.root(
        rx.accordion.item(
            rx.accordion.trigger(
                rx.text("Key", color="#555555", font_weight="600", font_size="13px", font_family="Outfit"),
            ),
            rx.accordion.content(
                rx.flex(
                    *[
                        rx.text(team, color=team_colors.get(team, "#555555"), font_size="13px", font_family="Outfit", font_weight="600", text_shadow="0px 1px 4px rgba(0,0,0,0.2)")
                        for team in teams_in_data
                    ],
                    flex_wrap="wrap",
                    gap="24px",
                ),
            ),
            value="constructor_key",
        ),
        collapsible=True,
        width="100%",
        variant="ghost",
        bg="#F0F0F2",
        border_radius="6px",
        border="1px solid #CCCCCC",
        box_shadow="0 2px 8px rgba(0,0,0,0.15)",
    )

    # ── Driver line chart ────────────────────────────────────────────────
    drivers_in_data = list(driver_totals["Driver"])

    driver_line_chart = zoomable_chart(
        lambda h: rx.recharts.line_chart(
            *[
                rx.recharts.line(
                    data_key=driver,
                    stroke=driver_colors.get(driver, "#555555"),
                    dot={"fill": driver_colors.get(driver, "#555555"), "stroke": driver_colors.get(driver, "#555555")},
                    name=driver,
                    type_="monotone",
                )
                for driver in drivers_in_data
            ],
            rx.recharts.x_axis(data_key="race", font_size=8, angle=-90, height=driver_race_axis_height, stroke="white", text_anchor="end", interval=0, tick={"dx": -5}),
            rx.recharts.y_axis(
                stroke="white",
                width=35,
                tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
            ),
            rx.recharts.cartesian_grid(vertical=False, stroke="rgba(0, 0, 0, 0.25)"),
            data=driver_line_data,
            margin={"top": 10, "right": 20, "left": 35, "bottom": 30},
            margin_left="-10px",
            width="100%",
            height=h,
        ),
        title="Driver's Championship",
        chart_id="driver_line_chart",
        height=350,
        large_height=450
    )

    # ── Driver legend expander ───────────────────────────────────────────
    driver_legend_expander = rx.accordion.root(
        rx.accordion.item(
            rx.accordion.trigger(
                rx.text("Key", color="#555555", font_weight="600", font_size="13px", font_family="Outfit"),
            ),
            rx.accordion.content(
                rx.flex(
                    *[
                        rx.text(driver, color=driver_colors.get(driver, "#555555"), font_size="13px", font_family="Outfit", font_weight="600", text_shadow="0px 1px 4px rgba(0,0,0,0.2)")
                        for driver in drivers_in_data
                    ],
                    flex_wrap="wrap",
                    gap="24px",
                ),
            ),
            value="driver_key",
        ),
        collapsible=True,
        width="100%",
        variant="ghost",
        bg="#F0F0F2",
        border_radius="6px",
        border="1px solid #CCCCCC",
        box_shadow="0 2px 8px rgba(0,0,0,0.15)",
    )

    # ── Constructor points bar chart data ────────────────────────────────
    constructor_bar_data = [
        {"team": row["Team"], "points": float(row["Points"]), "fill": team_colors.get(row["Team"], "#555555")}
        for _, row in constructor_totals.iterrows()
    ]

    max_team_len = max([len(str(item.get("team", ""))) for item in constructor_bar_data] or [0])
    team_axis_height = max(40, max_team_len * 5 + 15)

    constructor_bar_chart = zoomable_chart(
        lambda h: rx.recharts.bar_chart(
            rx.recharts.bar(
                data_key="points",
                name="Points",
            ),
            rx.recharts.x_axis(data_key="team", font_size=8, angle=-90, height=team_axis_height, stroke="white", text_anchor="end", interval=0, tick={"dx": -5}),
            rx.recharts.y_axis(
                stroke="white",
                width=35,
                tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
            ),
            rx.recharts.cartesian_grid(vertical=False, stroke="rgba(0, 0, 0, 0.25)"),
            data=constructor_bar_data,
            margin={"top": 10, "right": 20, "left": 35, "bottom": 40},
            margin_left="-10px",
            width="100%",
            height=h,
        ),
        title="Constructor Points",
        chart_id="constructor_bar_chart",
        height=300,
        large_height=400
    )

    # ── Driver points bar chart data ─────────────────────────────────────
    driver_bar_data = [
        {"driver": row["Driver"], "points": float(row["Points"]), "fill": driver_colors.get(row["Driver"], "#555555")}
        for _, row in driver_totals.iterrows()
    ]

    max_driver_len = max([len(str(item.get("driver", ""))) for item in driver_bar_data] or [0])
    driver_axis_height = max(40, max_driver_len * 5 + 15)

    driver_bar_chart = zoomable_chart(
        lambda h: rx.recharts.bar_chart(
            rx.recharts.bar(
                data_key="points",
                name="Points",
            ),
            rx.recharts.x_axis(data_key="driver", font_size=8, angle=-90, height=driver_axis_height, stroke="white", text_anchor="end", interval=0, tick={"dx": -5}),
            rx.recharts.y_axis(
                stroke="white",
                width=35,
                tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
            ),
            rx.recharts.cartesian_grid(vertical=False, stroke="rgba(0, 0, 0, 0.25)"),
            data=driver_bar_data,
            margin={"top": 10, "right": 20, "left": 35, "bottom": 40},
            margin_left="-10px",
            width="100%",
            height=h,
        ),
        title="Driver Points",
        chart_id="driver_bar_chart",
        height=300,
        large_height=400
    )

    # ── Full standings table helper ──────────────────────────────────────
    def standings_table(title: str, df, col_name: str, table_id: str = None) -> rx.Component:
        is_team_table = col_name == "Team"
        driver_to_team = dict(zip(drivers_points_df["Driver"], drivers_points_df["Team"]))

        if is_team_table:
            header_row = rx.table.row(
                rx.table.column_header_cell("Pos", color="#00b4da", width="50px"),
                rx.table.column_header_cell("Team", color="#00b4da"),
                rx.table.column_header_cell("Drivers", color="#00b4da"),
                rx.table.column_header_cell("Points", color="#00b4da", justify="end"),
            )
        else:
            header_row = rx.table.row(
                rx.table.column_header_cell("Pos", color="#00b4da", width="50px"),
                rx.table.column_header_cell("Driver", color="#00b4da"),
                rx.table.column_header_cell("Team", color="#00b4da"),
                rx.table.column_header_cell("Points", color="#00b4da", justify="end"),
            )

        rows = []
        for idx, (_, row) in enumerate(df.iterrows()):
            if is_team_table:
                team_name = str(row["Team"])
                team_drivers = drivers_points_df[drivers_points_df["Team"] == team_name].sort_values("Points", ascending=False)
                driver_names = team_drivers["Driver"].tolist()
                drivers_text = " & ".join(driver_names)
                
                rows.append(
                    rx.table.row(
                        rx.table.cell(str(idx + 1), color="#00b4da", font_weight="bold"),
                        rx.table.cell(
                            rx.hstack(
                                rx.box(
                                    width="4px",
                                    height="16px",
                                    bg=team_colors.get(team_name, "#555555"),
                                    border_radius="2px",
                                    flex_shrink="0",
                                ),
                                rx.text(team_name, color="white", font_weight="600"),
                                spacing="2",
                                align="center",
                            )
                        ),
                        rx.table.cell(drivers_text, color="#CCCCCC"),
                        rx.table.cell(str(row["Points"]), color="#CCCCCC", justify="end"),
                        _hover={"bg": "#1C1C20"},
                    )
                )
            else:
                driver_name = str(row["Driver"])
                team_name = driver_to_team.get(driver_name, "—")
                
                rows.append(
                    rx.table.row(
                        rx.table.cell(str(idx + 1), color="#00b4da", font_weight="bold"),
                        rx.table.cell(driver_name, color="white", font_weight="600"),
                        rx.table.cell(
                            rx.hstack(
                                rx.box(
                                    width="4px",
                                    height="16px",
                                    bg=team_colors.get(team_name, "#555555"),
                                    border_radius="2px",
                                    flex_shrink="0",
                                ),
                                rx.text(team_name, color="#CCCCCC", font_weight="600"),
                                spacing="2",
                                align="center",
                            )
                        ),
                        rx.table.cell(str(row["Points"]), color="#CCCCCC", justify="end"),
                        _hover={"bg": "#1C1C20"},
                    )
                )

        return rx.table.root(
            rx.table.header(header_row),
            rx.table.body(*rows),
            id=table_id,
            width="100%",
            variant="ghost",
        )

    # ── Layout ───────────────────────────────────────────────────────────
    season_num = season_data["season_number"]

    has_sprint = data.get("has_sprint", False)

    return rx.vstack(
        rx.flex(
            rx.heading(
                f"Season {season_num} Standings",
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

        # Standings popup buttons
        rx.grid(
            # Constructor standings dialog
            rx.dialog.root(
                rx.dialog.trigger(
                    rx.button(
                        "Full Constructor's Championship Standings",
                        bg="#18181C",
                        color="white",
                        border="1px solid #2C2C32",
                        _hover={"bg": "#00b4da", "border_color": "#00b4da"},
                        cursor="pointer",
                        width="100%",
                    ),
                ),
                rx.dialog.content(
                    rx.vstack(
                        rx.dialog.title(
                            "Constructor's Championship Standings",
                            color="white",
                            font_weight="900",
                            align_self="start",
                        ),
                        rx.box(
                            standings_table("Constructor Standings", constructor_totals, "Team", "constructor_standings_table"),
                            max_height="60vh",
                            overflow_y="auto",
                            width="100%",
                        ),
                        rx.button(
                            rx.hstack(
                                rx.icon("download", size=16),
                                rx.text("Download PNG"),
                                spacing="2",
                            ),
                            on_click=lambda: DownloadState.download_table("constructor_standings_table", f"Season {season_num} Constructor's Championship Standings"),
                            bg="#00b4da",
                            color="white",
                            _hover={"bg": "#009bbd"},
                            cursor="pointer",
                            margin_top="4",
                        ),
                        width="100%",
                        spacing="3",
                    ),
                    rx.dialog.close(
                        rx.button(
                            rx.icon("x", size=16),
                            variant="ghost",
                            color="white",
                            position="absolute",
                            top="12px",
                            right="12px",
                            _hover={"bg": "#00b4da"},
                            cursor="pointer",
                        ),
                    ),
                    bg="#111111",
                    border="1px solid #2C2C32",
                    max_width="500px",
                ),
            ),
            # Driver standings dialog
            rx.dialog.root(
                rx.dialog.trigger(
                    rx.button(
                        "Full Driver's Championship Standings",
                        bg="#18181C",
                        color="white",
                        border="1px solid #2C2C32",
                        _hover={"bg": "#00b4da", "border_color": "#00b4da"},
                        cursor="pointer",
                        width="100%",
                    ),
                ),
                rx.dialog.content(
                    rx.vstack(
                        rx.dialog.title(
                            "Driver's Championship Standings",
                            color="white",
                            font_weight="900",
                            align_self="start",
                        ),
                        rx.box(
                            standings_table("Driver Standings", driver_totals, "Driver", "driver_standings_table"),
                            max_height="60vh",
                            overflow_y="auto",
                            width="100%",
                        ),
                        rx.button(
                            rx.hstack(
                                rx.icon("download", size=16),
                                rx.text("Download PNG"),
                                spacing="2",
                            ),
                            on_click=lambda: DownloadState.download_table("driver_standings_table", f"Season {season_num} Driver's Championship Standings"),
                            bg="#00b4da",
                            color="white",
                            _hover={"bg": "#009bbd"},
                            cursor="pointer",
                            margin_top="4",
                        ),
                        width="100%",
                        spacing="3",
                    ),
                    rx.dialog.close(
                        rx.button(
                            rx.icon("x", size=16),
                            variant="ghost",
                            color="white",
                            position="absolute",
                            top="12px",
                            right="12px",
                            _hover={"bg": "#00b4da"},
                            cursor="pointer",
                        ),
                    ),
                    bg="#111111",
                    border="1px solid #2C2C32",
                    max_width="500px",
                ),
            ),
            columns=rx.breakpoints(initial="1", md="2"),
            spacing="4",
            width="100%",
        ),

        # Charts: 2 columns on wide, stacked on narrow
        rx.grid(
            rx.vstack(
                rx.text("Constructor's Championship", color="white", font_weight="700", font_size="sm"),
                constructor_line_chart,
                constructor_legend_expander,
                rx.text("Constructor Points", color="white", font_weight="700", font_size="sm"),
                constructor_bar_chart,
                width="100%",
                spacing="4",
                bg="transparent",
                padding="4",
                border_radius="xl",
            ),
            rx.vstack(
                rx.text("Driver's Championship", color="white", font_weight="700", font_size="sm"),
                driver_line_chart,
                driver_legend_expander,
                rx.text("Driver Points", color="white", font_weight="700", font_size="sm"),
                driver_bar_chart,
                width="100%",
                spacing="4",
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