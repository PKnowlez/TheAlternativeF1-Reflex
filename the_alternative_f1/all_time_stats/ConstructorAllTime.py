# All Time Constructor Statistics — Reflex Component
# Replaces the Streamlit version of ConstructorAllTime.py

import reflex as rx
from the_alternative_f1.all_time_stats import Functions


def constructor_stats_view(num_seasons: int) -> rx.Component:
    """Render the All Time Constructor Statistics as a Reflex table."""

    df = Functions.CalculateAllTime(num_seasons, "Team")
    rows = df.to_dict(orient="records")

    constructor_champs, _ = Functions.GetSeasonChampions(num_seasons)

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

    def season_cell(season_num: int, team_name: str, drivers_str: str) -> rx.Component:
        if not drivers_str or drivers_str == "—" or drivers_str.strip() == "":
            return rx.table.cell(rx.text("—", color="#555555", font_size="13px"))
        
        is_champ = constructor_champs.get(season_num) == team_name
        drivers = [d.strip() for d in drivers_str.split(",") if d.strip()]
        
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
                    rx.text(driver, color="#E0E0E0", font_size="13px", white_space="nowrap")
                    for driver in drivers
                ],
                spacing="1",
                align_items="start",
            ),
            padding_y="8px",
        )

    return rx.vstack(
        rx.vstack(
            rx.heading(
                "All Time Constructor Statistics",
                size="6",
                color="white",
                font_weight="900",
                padding_y="2.5%",
                padding_x="2%",
            ),
            rx.text(
                f"Aggregated Constructor's Championship statistics across Season 1 – Season {num_seasons}. "
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
                        header_cell("Constructor"),
                        header_cell("Points"),
                        header_cell("1st"),
                        header_cell("2nd"),
                        header_cell("3rd"),
                        header_cell("Championships"),
                        *[header_cell(f"S{i+1}") for i in range(num_seasons)],
                        bg="#111111",
                    )
                ),
                rx.table.body(
                    *[
                        rx.table.row(
                            data_cell(row["Place"], accent=True),
                            rx.table.cell(
                                rx.hstack(
                                    rx.box(
                                        width="4px",
                                        height="16px",
                                        bg=Functions.team_colors.get(row["Team"], "#555555"),
                                        border_radius="2px",
                                        flex_shrink="0",
                                    ),
                                    rx.text(row["Team"], color="white", font_weight="600", font_size="13px"),
                                    spacing="2",
                                    align="center",
                                )
                            ),
                            data_cell(f"{row['Points']:.0f}" if row["Points"] == int(row["Points"]) else f"{row['Points']:.1f}"),
                            data_cell(row["1st Place"]),
                            data_cell(row["2nd Place"]),
                            data_cell(row["3rd Place"]),
                            champion_cell(row["Constructor's Champion"]),
                            *[
                                season_cell(s, row["Team"], row.get(f"Season {s}", "—"))
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
        width="100%",
        align_items="start",
        margin_bottom="160px",
        padding_right="4",
    )