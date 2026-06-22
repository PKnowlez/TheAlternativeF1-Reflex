"""Tab 6 — Race Schedule (Reflex).

Reads the schedule from the Excel sheet for the selected season.
Handles 1-column (S1/S2), 2-column (S3), and 3-column (S4/S5) formats.
"""

import pandas as pd
import reflex as rx


def Tab6(data: dict, season_data: dict) -> rx.Component:
    """Render the Race Schedule tab."""
    schedule_df = data["schedule_df"]
    season_num = season_data["season_number"]

    # Drop completely empty columns
    schedule_df = schedule_df.dropna(axis=1, how="all")
    # Drop rows where all values are NaN
    schedule_df = schedule_df.dropna(how="all")

    col_names = list(schedule_df.columns)

    # Build header
    header_cells = [
        rx.table.column_header_cell(
            str(col),
            color="#00b4da",
            font_weight="bold",
            font_size="11px",
            text_transform="uppercase",
        )
        for col in col_names
    ]

    # Build rows
    table_rows = []
    for _, row in schedule_df.iterrows():
        cells = []
        for j, col in enumerate(col_names):
            val = row[col]
            if pd.isnull(val):
                val = "—"
            else:
                val = str(val)
            # First column (Race) gets white bold text
            if j == 0:
                cells.append(
                    rx.table.cell(val, color="white", font_weight="600", font_size="sm")
                )
            else:
                cells.append(
                    rx.table.cell(val, color="#CCCCCC", font_size="sm")
                )
        table_rows.append(
            rx.table.row(*cells, _hover={"bg": "#1C1C20"})
        )

    return rx.vstack(
        rx.heading(
            f"Season {season_num} Race Schedule",
            size="6",
            color="white",
            font_weight="900",
        ),
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(*header_cells),
                ),
                rx.table.body(*table_rows),
                width="100%",
                variant="ghost",
            ),
            width="100%",
            overflow_x="auto",
            bg="#18181C",
            padding="4",
            border_radius="xl",
            border="1px solid #2C2C32",
        ),
        width="100%",
        align_items="start",
        spacing="4",
    )