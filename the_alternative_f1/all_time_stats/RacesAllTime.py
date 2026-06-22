# All Time Race Results — Reflex Component
# Replaces the Streamlit version of RacesAllTime.py

import reflex as rx
from the_alternative_f1.all_time_stats import Functions


def races_all_time_view(num_seasons: int) -> rx.Component:
    """Render the All Time Race Results as Reflex tables side by side."""

    df_team = Functions.RacesAllTime(num_seasons, "Team")
    df_driver = Functions.RacesAllTime(num_seasons, "Driver")

    team_rows = df_team.to_dict(orient="records")
    driver_rows = df_driver.to_dict(orient="records")

    season_cols = [f"Season {i+1}" for i in range(num_seasons)]

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

    def podium_cell(text_val: str) -> rx.Component:
        """Format a podium result string (1st/2nd/3rd per season)."""
        if not text_val or str(text_val).strip() == "":
            return rx.table.cell(rx.text("—", color="#444444", font_size="12px"))

        lines = [l.strip() for l in str(text_val).replace("\\n\\n", "\n\n").replace("\\n", "\n").split("\n\n") if l.strip()]

        def format_season_block(block: str) -> rx.Component:
            sub_lines = [sl.strip() for sl in block.split("\n") if sl.strip()]
            def line_color(line: str) -> str:
                if line.startswith("1st"):
                    return "#FFD700"
                elif line.startswith("2nd"):
                    return "#C0C0C0"
                elif line.startswith("3rd"):
                    return "#CD7F32"
                return "#888888"
            return rx.vstack(
                *[
                    rx.text(sl, font_size="11px", color=line_color(sl))
                    for sl in sub_lines
                ],
                spacing="0",
                align_items="start",
            )

        return rx.table.cell(
            rx.vstack(
                *[format_season_block(blk) for blk in lines],
                spacing="3",
                align_items="start",
            ),
            padding_y="8px",
        )

    def build_table(rows, title: str) -> rx.Component:
        return rx.vstack(
            rx.heading(title, size="4", color="white", font_weight="700", margin_bottom="3"),
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            header_cell("Race"),
                            *[header_cell(f"S{i+1}") for i in range(num_seasons)],
                            bg="#111111",
                        )
                    ),
                    rx.table.body(
                        *[
                            rx.table.row(
                                rx.table.cell(
                                    rx.text(row["Race"], color="white", font_weight="600", font_size="12px", white_space="nowrap"),
                                ),
                                *[
                                    podium_cell(row.get(col, ""))
                                    for col in season_cols
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
        )

    return rx.vstack(
        rx.vstack(
            rx.heading(
                "All Time Race Results",
                size="6",
                color="white",
                font_weight="900",
            ),
            rx.text(
                f"Podium finishers for every race across Season 1 – Season {num_seasons}.",
                color="#AAAAAA",
                font_size="sm",
            ),
            rx.hstack(
                rx.badge("🥇 1st", color_scheme="yellow", variant="soft", font_size="10px"),
                rx.badge("🥈 2nd", color_scheme="gray", variant="soft", font_size="10px"),
                rx.badge("🥉 3rd", color_scheme="orange", variant="soft", font_size="10px"),
                spacing="3",
                margin_top="2",
            ),
            spacing="2",
            align_items="start",
            width="100%",
            margin_bottom="6",
        ),
        rx.vstack(
            build_table(team_rows, "Race Results by Constructor"),
            build_table(driver_rows, "Race Results by Driver"),
            width="100%",
            spacing="8",
        ),
        width="100%",
        align_items="start",
        margin_bottom="160px",
        padding_right="4",
    )