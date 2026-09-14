"""Tab 1 — Standings (Reflex).

Constructor and Driver championship standings with line/bar charts and
scrollable modal popups for full standings tables.
"""

import pandas as pd
import reflex as rx
from the_alternative_f1.articles.components import (
    zoomable_chart,
    DownloadState,
    interactive_line_chart_key,
    chart_card,
    get_download_position,
)
from the_alternative_f1.constructor_colors import get_constructor_color
from the_alternative_f1.all_time_stats.SummaryAllTime import _build_arc_path, _get_driver_shade


def build_season_donut_svg(
    season_num: int,
    sorted_teams: list,
    team_total_points: pd.Series,
    team_to_drivers: dict,
    team_colors: dict,
    driver_color_map: dict,
) -> str:
    """Build high-precision SVG for the two-ring donut chart for a specific season."""
    total_pts = float(team_total_points.sum())

    cx, cy = 260.0, 260.0
    r_out_in, r_out_out = 174.0, 242.0
    r_in_in, r_in_out = 104.0, 170.0

    curr_angle = -90.0  # 12 o'clock

    outer_paths = []
    inner_paths = []

    if total_pts > 0:
        for team in sorted_teams:
            c_pts = float(team_total_points.get(team, 0.0))
            if c_pts <= 0:
                continue

            c_angle_span = (c_pts / total_pts) * 360.0
            c_start_angle = curr_angle
            c_end_angle = curr_angle + c_angle_span
            c_pct = (c_pts / total_pts) * 100.0
            c_color = team_colors.get(team, get_constructor_color(team))

            c_path_d = _build_arc_path(cx, cy, r_out_in, r_out_out, c_start_angle, c_end_angle)
            outer_paths.append(f"""
            <path class="donut-slice donut-constructor" d="{c_path_d}" fill="{c_color}" stroke="#15151A" stroke-width="2"
                  style="cursor: pointer; transition: opacity 0.15s ease;"
                  data-type="Constructor"
                  data-name="{team}"
                  data-pts="{c_pts:,.1f}"
                  data-meta="{c_pct:.1f}% of Season"
                  onmouseenter="window.taf1DonutEnter && window.taf1DonutEnter(this)"
                  onmouseleave="window.taf1DonutLeave && window.taf1DonutLeave(this)"
                  onclick="window.taf1DonutClick && window.taf1DonutClick(this, event)">
                <title>{team}: {c_pts:,.1f} pts ({c_pct:.1f}% of Season)</title>
            </path>
            """)

            # Drivers for this constructor
            drivers = team_to_drivers.get(team, [])
            pos_drivers = [(d, p) for (d, p) in drivers if p > 0]
            num_pos = len(pos_drivers)

            curr_driver_angle = c_start_angle
            for d_idx, (d_name, d_pts) in enumerate(pos_drivers):
                d_angle_span = c_angle_span * (d_pts / c_pts)
                d_start_angle = curr_driver_angle
                d_end_angle = curr_driver_angle + d_angle_span
                curr_driver_angle = d_end_angle

                d_pct_of_team = (d_pts / c_pts) * 100.0
                d_color = driver_color_map.get(d_name) or _get_driver_shade(c_color, d_idx, num_pos)

                d_path_d = _build_arc_path(cx, cy, r_in_in, r_in_out, d_start_angle, d_end_angle)
                inner_paths.append(f"""
                <path class="donut-slice donut-driver" d="{d_path_d}" fill="{d_color}" stroke="#15151A" stroke-width="1.8"
                      style="cursor: pointer; transition: opacity 0.15s ease;"
                      data-type="Driver"
                      data-name="{d_name}"
                      data-pts="{d_pts:,.1f}"
                      data-meta="{team} • {d_pct_of_team:.1f}% of Team"
                      onmouseenter="window.taf1DonutEnter && window.taf1DonutEnter(this)"
                      onmouseleave="window.taf1DonutLeave && window.taf1DonutLeave(this)"
                      onclick="window.taf1DonutClick && window.taf1DonutClick(this, event)">
                    <title>{d_name} ({team}): {d_pts:,.1f} pts ({d_pct_of_team:.1f}% of {team})</title>
                </path>
                """)

            curr_angle = c_end_angle

    svg_id = f"season-donut-svg-{season_num}"

    return f"""
    <svg id="{svg_id}" class="donut-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 520" width="100%" height="100%"
         data-default-points="{total_pts:,.0f}"
         data-default-type="SEASON {season_num}"
         data-default-meta="TOTAL POINTS"
         style="display: block; max-width: 440px; max-height: 440px; margin: 0 auto; user-select: none;"
         onclick="window.taf1DonutBgClick && window.taf1DonutBgClick(event)">
        <defs>
            <filter id="donut-shadow-{season_num}" x="-10%" y="-10%" width="120%" height="120%">
                <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.5"/>
            </filter>
        </defs>

        <!-- Outer Ring: Constructors -->
        <g id="donut-outer-ring-{season_num}" filter="url(#donut-shadow-{season_num})">
            {''.join(outer_paths)}
        </g>

        <!-- Inner Ring: Drivers -->
        <g id="donut-inner-ring-{season_num}" filter="url(#donut-shadow-{season_num})">
            {''.join(inner_paths)}
        </g>

        <!-- Donut center hole (clickable to reset) -->
        <circle id="season-donut-center-hole-{season_num}" class="donut-center-hole" cx="{cx}" cy="{cy}" r="98"
                fill="#15151A" stroke="rgba(255,255,255,0.08)" stroke-width="1.5"
                style="cursor: pointer;"
                onclick="window.taf1DonutReset && window.taf1DonutReset(event)" />

        <!-- Center Information Display -->
        <g class="donut-svg-center-group" pointer-events="none" text-anchor="middle" font-family="'Outfit', sans-serif" style="user-select: none;">
            <text class="donut-center-type" x="{cx}" y="230" dominant-baseline="middle"
                  fill="#8E8E93" font-size="11" font-weight="700" letter-spacing="1">SEASON {season_num}</text>
            <text class="donut-center-value" x="{cx}" y="260" dominant-baseline="middle"
                  fill="#FFFFFF" font-size="24" font-weight="900">{total_pts:,.0f}</text>
            <text class="donut-center-meta" x="{cx}" y="285" dominant-baseline="middle"
                  fill="#00b4da" font-size="10.5" font-weight="700" letter-spacing="0.5">TOTAL POINTS</text>
        </g>
    </svg>
    """


@rx.memo
def memoized_season_donut_chart(*, html_content: rx.Var[str]) -> rx.Component:
    """Memoized wrapper preventing React re-renders from ticker loops or unrelated state."""
    return rx.box(
        rx.html(html_content),
        width="100%",
        max_width="480px",
    )


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
    pos_team_line = get_download_position(team_line_data, "race")

    constructor_line_chart = zoomable_chart(
        lambda h: rx.recharts.line_chart(
            *[
                rx.recharts.line(
                    data_key=team,
                    stroke=team_colors.get(team, "#555555"),
                    stroke_width=2,
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
            rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.2)"),
            data=team_line_data,
            margin={"top": 10, "right": 20, "left": 35, "bottom": 30},
            width="100%",
            height=h,
        ),
        title="Constructor's Championship",
        chart_id="constructor_line_chart",
        height=350,
        large_height=450,
        download_position=pos_team_line,
    )

    # ── Constructor interactive key ──────────────────────────────────────
    constructor_legend_expander = interactive_line_chart_key(
        chart_id="constructor_line_chart",
        items=[(team, team_colors.get(team, "#555555")) for team in teams_in_data],
        title="Key (Constructors)",
        hint="Click constructor to highlight",
    )

    # ── Driver line chart ────────────────────────────────────────────────
    drivers_in_data = list(driver_totals["Driver"])
    pos_driver_line = get_download_position(driver_line_data, "race")

    driver_line_chart = zoomable_chart(
        lambda h: rx.recharts.line_chart(
            *[
                rx.recharts.line(
                    data_key=driver,
                    stroke=driver_colors.get(driver, "#555555"),
                    stroke_width=2,
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
            rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.2)"),
            data=driver_line_data,
            margin={"top": 10, "right": 20, "left": 35, "bottom": 30},
            width="100%",
            height=h,
        ),
        title="Driver's Championship",
        chart_id="driver_line_chart",
        height=350,
        large_height=450,
        download_position=pos_driver_line,
    )

    # ── Driver interactive key ───────────────────────────────────────────
    driver_legend_expander = interactive_line_chart_key(
        chart_id="driver_line_chart",
        items=[(driver, driver_colors.get(driver, "#555555")) for driver in drivers_in_data],
        title="Key (Drivers)",
        hint="Click driver to highlight",
    )

    # ── Constructor points bar chart data ────────────────────────────────
    constructor_bar_data = [
        {"team": row["Team"], "points": float(row["Points"]), "fill": team_colors.get(row["Team"], "#555555")}
        for _, row in constructor_totals.iterrows()
    ]

    max_team_len = max([len(str(item.get("team", ""))) for item in constructor_bar_data] or [0])
    team_axis_height = max(40, max_team_len * 5 + 15)
    pos_team_bar = get_download_position(constructor_bar_data, "team")

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
            rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.2)"),
            data=constructor_bar_data,
            margin={"top": 10, "right": 20, "left": 35, "bottom": 40},
            width="100%",
            height=h,
        ),
        title="Constructor Points",
        chart_id="constructor_bar_chart",
        height=300,
        large_height=400,
        download_position=pos_team_bar,
    )

    # ── Driver points bar chart data ─────────────────────────────────────
    driver_bar_data = [
        {"driver": row["Driver"], "points": float(row["Points"]), "fill": driver_colors.get(row["Driver"], "#555555")}
        for _, row in driver_totals.iterrows()
    ]

    max_driver_len = max([len(str(item.get("driver", ""))) for item in driver_bar_data] or [0])
    driver_axis_height = max(40, max_driver_len * 5 + 15)
    pos_driver_bar = get_download_position(driver_bar_data, "driver")

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
            rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.2)"),
            data=driver_bar_data,
            margin={"top": 10, "right": 20, "left": 35, "bottom": 40},
            width="100%",
            height=h,
        ),
        title="Driver Points",
        chart_id="driver_bar_chart",
        height=300,
        large_height=400,
        download_position=pos_driver_bar,
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

    # ── Season Donut Points Distribution Chart ───────────────────────────
    drivers_points_df_copy = drivers_points_df.copy()
    drivers_points_df_copy["Points"] = pd.to_numeric(
        drivers_points_df_copy["Points"], errors="coerce"
    ).fillna(0)

    # Sort teams by total points descending
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

    colors_driver_df = data.get("colors_driver_df", pd.DataFrame())
    if not colors_driver_df.empty and "Driver" in colors_driver_df.columns and "Color" in colors_driver_df.columns:
        driver_color_map = dict(zip(colors_driver_df["Driver"], colors_driver_df["Color"]))
    else:
        driver_color_map = driver_colors

    season_donut_svg = build_season_donut_svg(
        season_num=season_num,
        sorted_teams=sorted_teams,
        team_total_points=team_total_points,
        team_to_drivers=team_to_drivers,
        team_colors=team_colors,
        driver_color_map=driver_color_map,
    )

    season_total_pts = float(team_total_points.sum())
    download_container_id = f"season-{season_num}-donut-download-container"

    season_donut_chart_card = rx.box(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("pie-chart", size=18, color="#00b4da"),
                    rx.text(
                        f"Season {season_num} Points Distribution",
                        font_family="Outfit",
                        font_weight="800",
                        font_size="16px",
                        color="white",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.badge(
                    f"{season_total_pts:,.0f} Total Season Points",
                    bg="rgba(0, 180, 218, 0.15)",
                    color="#00b4da",
                    border="1px solid rgba(0, 180, 218, 0.4)",
                    border_radius="full",
                    font_size="11px",
                    font_weight="700",
                    padding_x="8px",
                    padding_y="3px",
                ),
                width="100%",
                align="center",
                flex_wrap="wrap",
                gap="2",
            ),
            rx.text(
                "Outer Ring: Constructors (colored by official team colors) | Inner Ring: Drivers (shaded by team color, radially aligned as slices). Click or hover any slice to inspect.",
                font_size="12px",
                color="#8E8E93",
                margin_bottom="2",
                white_space="normal",
                word_break="break-word",
                width="100%",
                padding_x="1",
            ),
            # Donut SVG with native center information & download button
            rx.box(
                rx.center(
                    memoized_season_donut_chart(html_content=season_donut_svg),
                    width="100%",
                ),
                rx.button(
                    rx.icon("download", size=14),
                    on_click=lambda: DownloadState.download_chart(
                        download_container_id, f"Season {season_num} Points Distribution"
                    ),
                    position="absolute",
                    bottom="8px",
                    right="8px",
                    bg="rgba(0,180,218,0.15)",
                    color="#00b4da",
                    border="1px solid rgba(0,180,218,0.4)",
                    border_radius="full",
                    padding_x="10px",
                    padding_y="6px",
                    font_size="11px",
                    cursor="pointer",
                    _hover={"bg": "rgba(0,180,218,0.3)"},
                ),
                id=download_container_id,
                position="relative",
                width="100%",
            ),
            width="100%",
            spacing="3",
        ),
        id=f"season-donut-chart-card-{season_num}",
        class_name="donut-chart-card",
        bg="#15151A",
        border="1px solid #2C2C32",
        border_radius="2xl",
        padding=["16px", "20px", "24px"],
        padding_x=["16px", "20px", "24px"],
        padding_y=["16px", "20px", "24px"],
        box_shadow="0 8px 24px rgba(0,0,0,0.4)",
        width="100%",
        box_sizing="border-box",
    )

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
        season_donut_chart_card,

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
                chart_card(
                    title="Constructor's Championship",
                    chart_component=constructor_line_chart,
                    chart_id="constructor_line_chart",
                    download_position=pos_team_line,
                    extra_content=constructor_legend_expander,
                ),
                chart_card(
                    title="Constructor Points",
                    chart_component=constructor_bar_chart,
                    chart_id="constructor_bar_chart",
                    download_position=pos_team_bar,
                ),
                width="100%",
                spacing="5",
            ),
            rx.vstack(
                chart_card(
                    title="Driver's Championship",
                    chart_component=driver_line_chart,
                    chart_id="driver_line_chart",
                    download_position=pos_driver_line,
                    extra_content=driver_legend_expander,
                ),
                chart_card(
                    title="Driver Points",
                    chart_component=driver_bar_chart,
                    chart_id="driver_bar_chart",
                    download_position=pos_driver_bar,
                ),
                width="100%",
                spacing="5",
            ),
            columns=rx.breakpoints(initial="1", md="2"),
            spacing="5",
            width="100%",
        ),

        width="100%",
        align_items="start",
        spacing="5",
    )