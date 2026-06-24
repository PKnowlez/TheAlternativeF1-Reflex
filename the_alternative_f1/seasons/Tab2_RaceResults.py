"""Tab 2 — Race Results (Reflex).

Accordion of completed races showing full race results tables.
Dynamically scales with the number of races in the season.
"""

import math

import pandas as pd
import reflex as rx


def _build_manual_race_item(race: dict, idx: int, prefix: str, bg_color: str = "transparent") -> rx.Component:
    """Helper to build an accordion item for a custom manual pre-season or post-season race."""
    race_name = race.get("name", "Manual Race")
    results = race.get("results", [])

    # Sort results by place. Numeric values first, then DNF/DNS/DSQ/etc.
    def get_sort_key(r):
        pl = r.get("place", 99)
        if isinstance(pl, (int, float)):
            return pl
        try:
            return float(pl)
        except ValueError:
            return 999

    sorted_results = sorted(results, key=get_sort_key)

    # Detect which optional columns are present in the results list
    show_dotd = any("DOTD" in r for r in results)
    show_mot = any("MOT" in r for r in results)
    show_cd = any("CD" in r for r in results)

    # Info about the winner
    winner = sorted_results[0].get("driver", "—") if sorted_results else "—"
    constructor = sorted_results[0].get("team", "—") if sorted_results else "—"

    # Build header cells
    header_cells = [
        rx.table.column_header_cell("Place", color="#00b4da"),
        rx.table.column_header_cell("Driver", color="#00b4da"),
        rx.table.column_header_cell("Team", color="#00b4da"),
        rx.table.column_header_cell("Qualifying", color="#00b4da"),
        rx.table.column_header_cell("Points", color="#00b4da"),
        rx.table.column_header_cell("Fastest Lap", color="#00b4da"),
    ]
    if show_dotd:
        header_cells.append(rx.table.column_header_cell("DOTD", color="#00b4da"))
    if show_mot:
        header_cells.append(rx.table.column_header_cell("Most Overtakes", color="#00b4da"))
    if show_cd:
        header_cells.append(rx.table.column_header_cell("Cleanest Driver", color="#00b4da"))

    table_rows = []
    for r in sorted_results:
        place_val = r.get("place", "-")
        driver_val = r.get("driver", "-")
        team_val = r.get("team", "-")
        qualifying_val = r.get("qualifying", "-")
        points_val = r.get("points", 0)

        fl_val = "-"
        if "FL" in r:
            flv = r.get("FL", False)
            if isinstance(flv, bool):
                fl_val = "Yes" if flv else "-"
            else:
                fl_val = "Yes" if str(flv).upper() == "Y" else "-"

        cells = [
            rx.table.cell(str(place_val), color="#E0E0E0", font_size="sm"),
            rx.table.cell(str(driver_val), color="white", font_weight="600", font_size="sm"),
            rx.table.cell(str(team_val), color="#CCCCCC", font_size="sm"),
            rx.table.cell(str(qualifying_val), color="#CCCCCC", font_size="sm"),
            rx.table.cell(str(points_val), color="#CCCCCC", font_size="sm"),
            rx.table.cell(fl_val, color="#CCCCCC", font_size="sm"),
        ]

        if show_dotd:
            dotd_val = "-"
            dv = r.get("DOTD", False)
            if isinstance(dv, bool):
                dotd_val = "Yes" if dv else "-"
            else:
                dotd_val = "Yes" if str(dv).upper() == "Y" else "-"
            cells.append(rx.table.cell(dotd_val, color="#CCCCCC", font_size="sm"))

        if show_mot:
            mot_val = "-"
            mv = r.get("MOT", False)
            if isinstance(mv, bool):
                mot_val = "Yes" if mv else "-"
            else:
                mot_val = "Yes" if str(mv).upper() == "Y" else "-"
            cells.append(rx.table.cell(mot_val, color="#CCCCCC", font_size="sm"))

        if show_cd:
            cd_val = "-"
            cv = r.get("CD", False)
            if isinstance(cv, bool):
                cd_val = "Yes" if cv else "-"
            else:
                cd_val = "Yes" if str(cv).upper() == "Y" else "-"
            cells.append(rx.table.cell(cd_val, color="#CCCCCC", font_size="sm"))

        table_rows.append(
            rx.table.row(*cells, _hover={"bg": "#1C1C20"})
        )

    race_content = rx.vstack(
        rx.text(
            f"Winner: {winner} — {constructor}",
            color="#00b4da",
            font_weight="700",
            font_size="md",
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
        ),
        width="100%",
        spacing="3",
        padding="3",
    )

    return rx.accordion.item(
        rx.accordion.trigger(
            rx.vstack(
                rx.text(race_name, color="white", font_weight="600"),
                rx.text(f"Winner: {winner}", color="#00b4da", font_size="10px", font_weight="bold"),
                align_items="start",
                spacing="0",
            )
        ),
        rx.accordion.content(race_content),
        value=f"{prefix}_{idx}",
        bg=bg_color,
        border_radius="md",
        padding_x="3",
        margin_y="1",
    )


def Tab2(data: dict, season_data: dict) -> rx.Component:
    """Render the Race Results tab.

    Parameters
    ----------
    data : dict
        Computed data from Calculations().
    season_data : dict
        The season config dict from season_N.py.
    """
    races = data["races"]
    df = data["df"]
    race_place = data["race_place"]
    race_points = data["race_points"]
    has_dotd_mot_cd = data["has_dotd_mot_cd"]
    season_num = season_data["season_number"]

    preseason_items = []
    preseason_races = season_data.get("preseason_races", [])
    item_idx = 0
    for idx, pr in enumerate(preseason_races):
        bg_color = "#1E1E24" if item_idx % 2 == 0 else "#131316"
        preseason_items.append(_build_manual_race_item(pr, idx, "preseason", bg_color))
        item_idx += 1

    regular_items = []

    for i in range(len(races)):
        # Skip the first entry if it's a header row, and check if race data exists
        if i >= len(race_place):
            continue

        # Check if the race has been completed (has non-null place data)
        if pd.isnull(df.iloc[0][race_place[i]]):
            continue

        race_name = races[i]
        place_col = race_place[i]
        points_col = race_points[i]

        # Sort by finishing position
        df_sorted = df.sort_values(place_col, ascending=True)
        winner = df_sorted["Driver"].iloc[0]
        constructor = df_sorted["Team"].iloc[0]

        # Build column names for this race
        # Strip (S) for sprint column lookups
        base_name = race_name.replace(" (S)", "").replace(" Sprint", "")
        is_sprint = "Sprint" in race_name or "(S)" in race_name

        if is_sprint:
            qualifying_col = base_name + " SprintQualifying"
            fastestlap_col = base_name + " SprintFastestLap"
            dotd_col = base_name + " SprintDOTD"
            mot_col = base_name + " SprintMOT"
            cd_col = base_name + " SprintCD"
        else:
            qualifying_col = race_name + "Qualifying"
            fastestlap_col = race_name + "FastestLap"
            dotd_col = race_name + "DOTD"
            mot_col = race_name + "MOT"
            cd_col = race_name + "CD"

        # Build the results rows
        table_rows = []
        for _, row in df_sorted.iterrows():
            place_val = row[place_col]
            # Replace numeric codes with text
            place_display = str(int(place_val)) if not pd.isnull(place_val) else "-"
            if season_num <= 4:
                if place_display == "21":
                    place_display = "DNF"
                elif place_display == "22":
                    place_display = "DNS"
                elif place_display == "23":
                    place_display = "DSQ"
            else:
                if place_display == "23":
                    place_display = "DNF"
                elif place_display == "24":
                    place_display = "DNS"
                elif place_display == "25":
                    place_display = "DSQ"

            qualifying_val = "-"
            if qualifying_col in df.columns:
                qv = row.get(qualifying_col, "-")
                qualifying_val = str(int(qv)) if not pd.isnull(qv) and qv != "-" else "-"
                if season_num <= 4:
                    if qualifying_val == "21":
                        qualifying_val = "DNF"
                    elif qualifying_val == "22":
                        qualifying_val = "DNS"
                    elif qualifying_val == "23":
                        qualifying_val = "DSQ"
                else:
                    if qualifying_val == "23":
                        qualifying_val = "DNF"
                    elif qualifying_val == "24":
                        qualifying_val = "DNS"
                    elif qualifying_val == "25":
                        qualifying_val = "DSQ"

            points_val = row[points_col] if not pd.isnull(row[points_col]) else 0

            fl_val = "-"
            if fastestlap_col in df.columns:
                flv = row.get(fastestlap_col, "n")
                fl_val = "Yes" if str(flv).upper() == "Y" else "-"

            # Optional columns
            cells = [
                rx.table.cell(place_display, color="#E0E0E0", font_size="sm"),
                rx.table.cell(str(row["Driver"]), color="white", font_weight="600", font_size="sm"),
                rx.table.cell(str(row["Team"]), color="#CCCCCC", font_size="sm"),
                rx.table.cell(qualifying_val, color="#CCCCCC", font_size="sm"),
                rx.table.cell(str(points_val), color="#CCCCCC", font_size="sm"),
                rx.table.cell(fl_val, color="#CCCCCC", font_size="sm"),
            ]

            # Add DOTD/MOT/CD if they exist for this season
            if has_dotd_mot_cd:
                dotd_val = "-"
                if dotd_col in df.columns:
                    dv = row.get(dotd_col, "n")
                    dotd_val = "Yes" if str(dv).upper() == "Y" else "-"
                cells.append(rx.table.cell(dotd_val, color="#CCCCCC", font_size="sm"))

                mot_val = "-"
                if mot_col in df.columns:
                    mv = row.get(mot_col, "n")
                    mot_val = "Yes" if str(mv).upper() == "Y" else "-"
                cells.append(rx.table.cell(mot_val, color="#CCCCCC", font_size="sm"))

                cd_val = "-"
                if cd_col in df.columns:
                    cv = row.get(cd_col, "n")
                    cd_val = "Yes" if str(cv).upper() == "Y" else "-"
                cells.append(rx.table.cell(cd_val, color="#CCCCCC", font_size="sm"))

            table_rows.append(
                rx.table.row(*cells, _hover={"bg": "#1C1C20"})
            )

        # Build header cells
        header_cells = [
            rx.table.column_header_cell("Place", color="#00b4da"),
            rx.table.column_header_cell("Driver", color="#00b4da"),
            rx.table.column_header_cell("Team", color="#00b4da"),
            rx.table.column_header_cell("Qualifying", color="#00b4da"),
            rx.table.column_header_cell("Points", color="#00b4da"),
            rx.table.column_header_cell("Fastest Lap", color="#00b4da"),
        ]
        if has_dotd_mot_cd:
            header_cells.extend([
                rx.table.column_header_cell("DOTD", color="#00b4da"),
                rx.table.column_header_cell("Most Overtakes", color="#00b4da"),
                rx.table.column_header_cell("Cleanest Driver", color="#00b4da"),
            ])

        race_content = rx.vstack(
            rx.text(
                f"Winner: {winner} — {constructor}",
                color="#00b4da",
                font_weight="700",
                font_size="md",
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
            ),
            width="100%",
            spacing="3",
            padding="3",
        )

        bg_color = "#1E1E24" if item_idx % 2 == 0 else "#131316"
        regular_items.append(
            rx.accordion.item(
                rx.accordion.trigger(
                    rx.vstack(
                        rx.text(race_name, color="white", font_weight="600"),
                        rx.text(f"Winner: {winner}", color="#00b4da", font_size="10px", font_weight="bold"),
                        align_items="start",
                        spacing="0",
                    )
                ),
                rx.accordion.content(race_content),
                value=f"race_{i}",
                bg=bg_color,
                border_radius="md",
                padding_x="3",
                margin_y="1",
            )
        )
        item_idx += 1

    postseason_items = []
    postseason_races = season_data.get("postseason_races", [])
    for idx, pr in enumerate(postseason_races):
        bg_color = "#1E1E24" if item_idx % 2 == 0 else "#131316"
        postseason_items.append(_build_manual_race_item(pr, idx, "postseason", bg_color))
        item_idx += 1

    accordion_items = preseason_items + regular_items + postseason_items

    if not accordion_items:
        return rx.vstack(
            rx.heading(f"Season {season_num} Race Results", size="6", color="white", font_weight="900", padding_y="2.5%", padding_x="2%"),
            rx.text("No race results available yet.", color="#888888", padding_x="2%"),
            width="100%",
            spacing="4",
        )

    return rx.vstack(
        rx.heading(
            f"Season {season_num} Race Results",
            size="6",
            color="white",
            font_weight="900",
            padding_y="2.5%",
            padding_x="2%",
        ),
        rx.accordion.root(
            *accordion_items,
            collapsible=True,
            width="100%",
            variant="ghost",
        ),
        width="100%",
        align_items="start",
        spacing="4",
        bg="#18181C",
        padding="4",
        border_radius="xl",
        border="1px solid #2C2C32",
    )