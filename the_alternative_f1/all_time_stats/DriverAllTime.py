# All Time Driver Statistics — Reflex Component
# Replaces the Streamlit version of DriverAllTime.py

import reflex as rx
from the_alternative_f1.all_time_stats import Functions


def driver_stats_view(num_seasons: int) -> rx.Component:
    """Render the All Time Driver Statistics as a Reflex table."""

    df = Functions.CalculateAllTime(num_seasons, "Driver")
    rows = df.to_dict(orient="records")

    _, driver_champs = Functions.GetSeasonChampions(num_seasons)

    def header_cell(label: str) -> rx.Component:
        return rx.table.column_header_cell(
            label,
            color="#00b4da",
            font_weight="bold",
            font_size="11px",
            text_transform="uppercase",
            letter_spacing="0.05em",
            white_space="nowrap",
        )

    def data_cell(value, accent: bool = False) -> rx.Component:
        return rx.table.cell(
            str(value),
            color="#00b4da" if accent else "#E0E0E0",
            font_weight="bold" if accent else "normal",
            font_size="13px",
            white_space="nowrap",
        )

    def champion_cell(value: int) -> rx.Component:
        if value > 0:
            return rx.table.cell(
                rx.badge(
                    f"🏆 x{value}",
                    color_scheme="cyan",
                    variant="solid",
                    font_size="11px",
                ),
            )
        return rx.table.cell(rx.text("—", color="#555555", font_size="13px"))

    def streak_cell(value: int) -> rx.Component:
        if value >= 3:
            return rx.table.cell(
                rx.badge(
                    f"🔥 {value}",
                    color_scheme="orange",
                    variant="soft",
                    font_size="11px",
                ),
            )
        return rx.table.cell(
            rx.text(str(value), color="#AAAAAA", font_size="13px")
        )

    def season_cell(season_num: int, driver_name: str, teams_str: str) -> rx.Component:
        if not teams_str or teams_str == "—" or teams_str.strip() == "":
            return rx.table.cell(rx.text("—", color="#555555", font_size="13px"))
        
        is_champ = driver_champs.get(season_num) == driver_name
        teams = [t.strip() for t in teams_str.split(",") if t.strip()]
        
        return rx.table.cell(
            rx.vstack(
                rx.cond(
                    is_champ,
                    rx.badge(
                        "🥇 Champion",
                        color_scheme="yellow",
                        variant="solid",
                        font_size="10px",
                        margin_bottom="1",
                    ),
                    rx.fragment(),
                ),
                *[
                    rx.hstack(
                        rx.box(
                            width="4px",
                            height="16px",
                            bg=Functions.team_colors.get(team, "#555555"),
                            border_radius="2px",
                            flex_shrink="0",
                        ),
                        rx.text(team, color="white", font_weight="600", font_size="13px", white_space="nowrap"),
                        spacing="2",
                        align="center",
                    )
                    for team in teams
                ],
                spacing="1",
                align_items="start",
            ),
            padding_y="8px",
        )

    return rx.vstack(
        rx.vstack(
            rx.heading(
                "All Time Driver Standings",
                size="6",
                color="white",
                font_weight="900",
                padding_y="2.5%",
                padding_x="2%",
            ),
            rx.text(
                f"Aggregated Driver's Championship statistics across Season 1 – Season {num_seasons}. "
                "Championships are updated at the conclusion of each season once all points, wins, and podiums are finalized.",
                color="#AAAAAA",
                font_size="sm",
                max_width="700px",
                padding_x="2%",
            ),
            spacing="2",
            align_items="start",
            width="100%",
            margin_bottom="6",
        ),
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        header_cell("Pos"),
                        header_cell("Driver"),
                        header_cell("Points"),
                        header_cell("1st"),
                        header_cell("2nd"),
                        header_cell("3rd"),
                        header_cell("Podiums"),
                        header_cell("Champ."),
                        header_cell("Win Streak"),
                        header_cell("SS Streak"),
                        *[header_cell(f"S{i+1}") for i in range(num_seasons)],
                        bg="#111111",
                    )
                ),
                rx.table.body(
                    *[
                        rx.table.row(
                            data_cell(row["Place"], accent=True),
                            rx.table.cell(
                                rx.text(row["Driver"], color="white", font_weight="600", font_size="13px")
                            ),
                            data_cell(f"{row['Points']:.0f}" if row["Points"] == int(row["Points"]) else f"{row['Points']:.1f}"),
                            data_cell(row["1st Place"]),
                            data_cell(row["2nd Place"]),
                            data_cell(row["3rd Place"]),
                            data_cell(row["Podiums"]),
                            champion_cell(row["Driver's Champion"]),
                            streak_cell(row["Win Streak"]),
                            streak_cell(row["Single Season Win Streak"]),
                            *[
                                season_cell(s, row["Driver"], row.get(f"Season {s}", "—"))
                                for s in range(1, num_seasons + 1)
                            ],
                            _hover={"bg": "rgba(0,180,218,0.05)"},
                            transition="background 0.15s",
                        )
                        for row in rows
                    ]
                ),
                width="100%",
                variant="ghost",
            ),
            width="100%",
            overflow_x="auto",
            bg="#18181C",
            border_radius="xl",
            border="1px solid #2C2C32",
            padding="4",
        ),
        rx.hstack(
            rx.badge("🔥 3+ consecutive wins", color_scheme="orange", variant="soft", font_size="10px"),
            rx.text("SS Streak = Single Season Win Streak", color="#666666", font_size="10px"),
            spacing="4",
            margin_top="3",
            align="center",
        ),
        width="100%",
        align_items="start",
        margin_bottom="160px",
        padding_right="4",
    )