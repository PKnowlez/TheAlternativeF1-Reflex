# All Time Race Results — Reflex Component
# Implements TAF1APP-SDDFEAT-5 and approved downstream requirement:
# - SDDREQ-115: Cascading Table Columns (~70% overlap, most recent season as top layer on far right, page-flipping selection)

import reflex as rx
from the_alternative_f1.all_time_stats import Functions


class RacesAllTimeState(rx.State):
    """Reflex state managing page-flipping cascading columns for Race Results."""
    selected_constructor_season: int = 5
    selected_driver_season: int = 5

    def set_constructor_season(self, season: int | str | dict = 5):
        if isinstance(season, dict):
            return
        try:
            self.selected_constructor_season = int(season)
        except (TypeError, ValueError):
            pass

    def set_driver_season(self, season: int | str | dict = 5):
        if isinstance(season, dict):
            return
        try:
            self.selected_driver_season = int(season)
        except (TypeError, ValueError):
            pass


def races_all_time_view(num_seasons: int) -> rx.Component:
    """Render the All Time Race Results with ~70% overlapping cascading columns and page-flipping selection."""

    df_team = Functions.RacesAllTime(num_seasons, "Team")
    df_driver = Functions.RacesAllTime(num_seasons, "Driver")

    team_rows = df_team.to_dict(orient="records")
    driver_rows = df_driver.to_dict(orient="records")

    def race_cell(race_name: str) -> rx.Component:
        """Fixed race name cell on the pinned left column."""
        return rx.box(
            rx.text(race_name, color="white", font_weight="700", font_size="12px", white_space="nowrap"),
            height="64px",
            display="flex",
            align_items="center",
            border_bottom="1px solid rgba(255,255,255,0.06)",
            padding="4px 10px",
            width="100%",
        )

    def podium_cell(text_val: str) -> rx.Component:
        """Format a podium result block (1st/2nd/3rd per season) within a fixed-height cell."""
        if not text_val or str(text_val).strip() == "":
            return rx.box(
                rx.text("—", color="#555555", font_size="12px"),
                height="64px",
                display="flex",
                align_items="center",
                justify_content="center",
                border_bottom="1px solid rgba(255,255,255,0.06)",
                padding="4px 8px",
            )

        lines = [l.strip() for l in str(text_val).replace("\\n\\n", "\n\n").replace("\\n", "\n").split("\n\n") if l.strip()]

        def format_season_block(block: str) -> rx.Component:
            sub_lines = [sl.strip() for sl in block.split("\n") if sl.strip()]
            def line_color(line: str) -> str:
                if line.startswith("🥇") or line.startswith("1st"):
                    return "#FFD700"
                elif line.startswith("🥈") or line.startswith("2nd"):
                    return "#C0C0C0"
                elif line.startswith("🥉") or line.startswith("3rd"):
                    return "#CD7F32"
                return "#888888"
            return rx.vstack(
                *[
                    rx.text(sl, font_size="11px", color=line_color(sl), font_weight="600", white_space="nowrap")
                    for sl in sub_lines
                ],
                spacing="0",
                align_items="start",
            )

        return rx.box(
            rx.vstack(
                *[format_season_block(blk) for blk in lines],
                spacing="1",
                align_items="start",
            ),
            height="64px",
            display="flex",
            align_items="center",
            border_bottom="1px solid rgba(255,255,255,0.06)",
            padding="4px 8px",
            overflow="hidden",
        )

    def build_cascading_table(rows: list, is_constructor: bool = True) -> rx.Component:
        """Build table with ~70% overlapping cascading columns and page-flipping selection per SDDREQ-115."""
        selected_var = (
            RacesAllTimeState.selected_constructor_season
            if is_constructor
            else RacesAllTimeState.selected_driver_season
        )
        select_fn = (
            RacesAllTimeState.set_constructor_season
            if is_constructor
            else RacesAllTimeState.set_driver_season
        )

        # Precompute dynamic content width for each season column
        def compute_season_col_width(s_num: int) -> int:
            max_c = 0
            for r in rows:
                val = str(r.get(f"Season {s_num}", "") or "")
                for block in val.replace("\\n\\n", "\n\n").split("\n\n"):
                    for line in block.split("\n"):
                        clean_l = line.strip()
                        if clean_l:
                            max_c = max(max_c, len(clean_l))
            if max_c <= 1:
                return 95
            calc_w = int(max_c * 7.2 + 32)
            return max(100, min(145, calc_w))

        col_widths = {s: compute_season_col_width(s) for s in range(1, num_seasons + 1)}

        # Dynamic width for pinned race column, tightly hugging race names
        max_race_len = max([len(str(r.get("Race", "")).strip()) for r in rows] or [4])
        race_col_w = max(80, int(max_race_len * 6.8 + 22))

        # 1. Pinned Left Column (Race Names)
        race_col = rx.box(
            rx.box(
                rx.text("RACE", font_size="11px", font_weight="800", color="#00b4da", letter_spacing="0.06em"),
                height="44px",
                display="flex",
                align_items="center",
                padding_x="10px",
                bg="#15151D",
                border_bottom="2px solid rgba(255,255,255,0.1)",
                width="100%",
            ),
            *[race_cell(row.get("Race", "—")) for row in rows],
            width=f"{race_col_w}px",
            min_width=f"{race_col_w}px",
            max_width=f"{race_col_w}px",
            bg="#181822",
            border="1px solid #2C2C36",
            border_radius="md",
            z_index="25",
            box_shadow="4px 0 12px rgba(0,0,0,0.5)",
            flex_shrink="0",
        )

        # 2. Cascading Season Columns (Dynamic content width, left-justified S# header)
        season_columns = []
        for s in range(1, num_seasons + 1):
            is_active = (selected_var == s)
            col_w = col_widths[s]
            margin_l = "0px" if s == 1 else f"-{col_widths[s - 1] - 40}px"

            header_tab = rx.box(
                rx.hstack(
                    rx.text(f"S{s}", font_size="12px", font_weight="800", font_family="Outfit"),
                    rx.cond(
                        is_active,
                        rx.box(width="6px", height="6px", border_radius="50%", bg="white", flex_shrink="0"),
                        rx.fragment(),
                    ),
                    spacing="1",
                    align="center",
                    justify="start",
                ),
                height="44px",
                display="flex",
                align_items="center",
                justify_content="flex-start",
                padding_left="10px",
                padding_right="6px",
                bg=rx.cond(is_active, "#00b4da", "#191922"),
                color=rx.cond(is_active, "white", "#8E8E98"),
                border_bottom="2px solid rgba(255,255,255,0.1)",
                transition="all 0.2s ease",
                width="100%",
            )

            col_card = rx.box(
                header_tab,
                *[podium_cell(row.get(f"Season {s}", "")) for row in rows],
                width=f"{col_w}px",
                min_width=f"{col_w}px",
                max_width=f"{col_w}px",
                class_name=f"cascading-season-col cascading-season-col-{s}",
                style={"--cascaded-margin": margin_l},
                position="relative",
                z_index=rx.cond(is_active, 20, s),
                bg=rx.cond(is_active, "#1A1A26", "#121218"),
                border=rx.cond(is_active, "1.5px solid #00b4da", "1px solid #282834"),
                border_radius="md",
                box_shadow=rx.cond(
                    is_active,
                    "0 8px 24px rgba(0, 180, 218, 0.35), 0 4px 12px rgba(0,0,0,0.8)",
                    "0 3px 10px rgba(0,0,0,0.5)",
                ),
                cursor="pointer",
                on_click=select_fn(s),
                flex_shrink="0",
            )
            season_columns.append(col_card)

        # 3. Quick Selector Bar above table
        quick_selector = rx.hstack(
            rx.text("Flip Season Column:", color="#8E8E93", font_size="11px", font_weight="600"),
            *[
                rx.button(
                    f"S{s}",
                    size="1",
                    variant="solid" if False else "surface",
                    color_scheme=rx.cond(selected_var == s, "cyan", "gray"),
                    on_click=select_fn(s),
                    cursor="pointer",
                    font_weight="bold",
                )
                for s in range(1, num_seasons + 1)
            ],
            spacing="2",
            align="center",
            margin_bottom="3",
        )

        return rx.vstack(
            quick_selector,
            rx.box(
                rx.hstack(
                    race_col,
                    rx.hstack(
                        *season_columns,
                        spacing="0",
                        align_items="stretch",
                    ),
                    spacing="2",
                    align_items="stretch",
                ),
                class_name="cascading-table-container",
                overflow_x="auto",
                width="100%",
                padding="3",
                bg="#111116",
                border_radius="xl",
                border="1px solid #282832",
            ),
            width="100%",
            spacing="2",
        )

    return rx.vstack(
        rx.vstack(
            rx.heading(
                "All Time Race Results",
                size="6",
                color="white",
                font_weight="900",
                padding_y="2.5%",
                padding_x="2%",
            ),
            rx.text(
                f"Podium finishers for every race across Season 1 – Season {num_seasons}. "
                "Season columns display side-by-side on wide screens and smoothly cascade with a ~70% overlap on narrower screens. "
                "Click any season column or tab to inspect or flip that column to the top layer.",
                color="#AAAAAA",
                font_size="sm",
                padding_x="2%",
            ),
            rx.hstack(
                rx.badge("🥇 1st", color_scheme="yellow", variant="soft", font_size="10px"),
                rx.badge("🥈 2nd", color_scheme="gray", variant="soft", font_size="10px"),
                rx.badge("🥉 3rd", color_scheme="orange", variant="soft", font_size="10px"),
                spacing="3",
                margin_top="2",
                padding_x="2%",
                wrap="wrap",
            ),
            spacing="2",
            align_items="start",
            width="100%",
            margin_bottom="6",
        ),
        rx.accordion.root(
            rx.accordion.item(
                rx.accordion.trigger(
                    rx.text("Race Results by Constructor", color="white", font_weight="600"),
                ),
                rx.accordion.content(
                    build_cascading_table(team_rows, is_constructor=True),
                    padding_y="4px",
                ),
                value="constructor_results",
                bg="#3C3C41",
                border_radius="md",
                padding_x="3",
                margin_y="1",
            ),
            rx.accordion.item(
                rx.accordion.trigger(
                    rx.text("Race Results by Driver", color="white", font_weight="600"),
                ),
                rx.accordion.content(
                    build_cascading_table(driver_rows, is_constructor=False),
                    padding_y="4px",
                ),
                value="driver_results",
                bg="#525259",
                border_radius="md",
                padding_x="3",
                margin_y="1",
            ),
            collapsible=True,
            width="100%",
            variant="ghost",
        ),
        width="100%",
        align_items="start",
        margin_bottom="160px",
        padding_right="4",
    )