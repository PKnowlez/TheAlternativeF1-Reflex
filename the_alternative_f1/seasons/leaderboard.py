"""Alternative Points Leaderboard — Reflex Component.
Implements TAF1APP-SDDFEAT-17 and approved downstream SDD requirements:
- SDDREQ-153: User Ranking (Ranked by all-time remaining Alternative Points, sets sort)
- SDDREQ-154: Table Format (Frozen columns: User Name, All Time Points; Cascading columns starting with Season 5)
- SDDREQ-165: User Wagers Correct/Incorrect Stacked Bar Chart (Horizontal stacked bar: x=points, y=users, correct=#00b4da, incorrect=#FF8C00)
- SDDREQ-166: All Time Points Growth Chart (Line chart: x=races, y=points, dashed vertical line at Season 5 boundary, season slider starting at Season 5)
- SDDREQ-167: Leaderboard Tab Layout (Top-to-bottom: All-time table in expander, followed side-by-side by User Wagers stacked bar chart and Points Growth chart)
"""

import reflex as rx
from the_alternative_f1.all_time_stats.Functions import get_excel_sheet
from the_alternative_f1.articles.components import (
    interactive_line_chart_key,
    chart_card,
    zoomable_chart,
)
from the_alternative_f1.seasons.predictions_market import (
    get_user_total_points,
    get_user_remaining_points,
    _load_local_user_points,
    _save_local_user_points,
    _get_supabase,
    _load_local_predictions,
    get_all_predictions,
    normalize_username,
)

USER_COLORS_PALETTE = [
    "#00b4da", "#FFD700", "#FF4B4B", "#9B59B6", "#1ABC9C", "#E67E22", "#3498DB", "#2ECC71"
]

def get_predictor_key_items() -> list[tuple[str, str]]:
    """Returns (username, color) for all known predictors in order."""
    known = [
        "Jatthew Newman",
        "PK",
        "Jellywaffles37",
        "uhh_josh",
    ]
    local_pts = _load_local_user_points()
    for u in local_pts.keys():
        u_clean = normalize_username(u)
        if u_clean and u_clean != "Matthew Newman" and u_clean not in known:
            known.append(u_clean)

    palette = [
        "#00b4da", "#FFD700", "#FF4B4B", "#9B59B6", "#1ABC9C", "#E67E22", "#3498DB", "#2ECC71", "#E74C3C", "#F39C12"
    ]
    return [(u, palette[idx % len(palette)]) for idx, u in enumerate(known)]


PREDICTOR_KEY_ITEMS = get_predictor_key_items()


def compute_leaderboard_data() -> list[dict]:
    """Compiles all-time and seasonal points for logged-in users who received points or placed predictions.
    Only displays users who have logged in and received their 100 points or placed predictions (SDDREQ-153).
    Deduplicates accounts if a user has changed display names.
    """
    all_users = set()

    sb = _get_supabase()
    if sb:
        try:
            # Active synchronization: migrate any old predictions and purge obsolete rows
            sb.table("predictions").update({"username": "Jatthew Newman"}).eq("username", "Matthew Newman").execute()
            sb.table("user_prediction_points").delete().eq("username", "Matthew Newman").execute()
        except Exception:
            pass

        try:
            res = sb.table("user_prediction_points").select("*").execute()
            if res.data:
                # Group by discord_id to handle any display name changes dynamically
                users_by_discord_id = {}
                for r in res.data:
                    d_id = r.get("discord_id")
                    raw_name = str(r.get("display_name") or r.get("username", "")).strip()
                    u_name = normalize_username(raw_name)
                    if not u_name or u_name == "Matthew Newman":
                        continue
                    if d_id:
                        if d_id in users_by_discord_id:
                            old_u = users_by_discord_id[d_id]
                            all_users.discard(old_u)
                        users_by_discord_id[d_id] = u_name
                    all_users.add(u_name)
        except Exception:
            pass

        try:
            res_preds = sb.table("predictions").select("username").execute()
            if res_preds.data:
                for r in res_preds.data:
                    raw_u = str(r.get("username", "")).strip()
                    u = normalize_username(raw_u)
                    if u and u != "Matthew Newman" and u not in all_users:
                        all_users.add(u)
        except Exception:
            pass

    local_pts = _load_local_user_points()
    # Always purge obsolete alias from local cache immediately
    if "Matthew Newman" in local_pts:
        del local_pts["Matthew Newman"]
        _save_local_user_points(local_pts)

    if not all_users:
        for u in list(local_pts.keys()):
            u_clean = normalize_username(str(u).strip())
            if u_clean and u_clean != "Matthew Newman":
                all_users.add(u_clean)
    else:
        # Sync local cache with Supabase to purge obsolete accounts
        dirty_local = False
        for u in list(local_pts.keys()):
            if u not in all_users or u == "Matthew Newman":
                del local_pts[u]
                dirty_local = True
        if dirty_local:
            _save_local_user_points(local_pts)

    # Discard obsolete name if it ever entered the set
    all_users.discard("Matthew Newman")

    rows = []
    for user in all_users:
        canonical_user = normalize_username(user)
        if not canonical_user or canonical_user == "Matthew Newman":
            continue
        rem_pts = get_user_remaining_points(canonical_user, 5)
        rows.append({
            "user": canonical_user,
            "all_time_pts": rem_pts,
            "s5": rem_pts,
        })

    # SDDREQ-153: Rank users by all time remaining Alternative Points (sets sort)
    rows.sort(key=lambda r: (-r["all_time_pts"], r["user"].lower()))
    for idx, r in enumerate(rows):
        rank = idx + 1
        r["rank"] = rank
        r["rank_str"] = str(rank)
        badge_color = "#FFD700" if rank == 1 else "#C0C0C0" if rank == 2 else "#CD7F32" if rank == 3 else "#888888"
        r["rank_color"] = badge_color
        r["rank_bg"] = f"{badge_color}22"
        r["rank_border"] = f"1px solid {badge_color}44"
        r["pts_str"] = f"{r['all_time_pts']} pts"
        r["s5_str"] = f"{r['s5']} pts"

    return rows


class LeaderboardState(rx.State):
    """Reflex state managing Leaderboard table, stacked bar chart, and growth chart."""
    selected_season: int = 5
    selected_season_col: str = "s5"
    table_expander_open: bool = True
    season_slider: int = 5
    single_season_only: bool = True
    refresh_counter: int = 0

    def set_selected_season(self, season: int | str | dict = 5):
        if isinstance(season, dict):
            return
        try:
            self.selected_season = int(season)
            self.selected_season_col = f"s{self.selected_season}"
        except (TypeError, ValueError):
            pass

    def set_season_col(self, col: str):
        self.selected_season_col = str(col)
        if str(col).startswith("s") and str(col)[1:].isdigit():
            try:
                self.selected_season = int(str(col)[1:])
            except ValueError:
                pass

    def toggle_table_expander(self):
        self.table_expander_open = not self.table_expander_open

    def set_season_slider(self, val: list[float]):
        if isinstance(val, list) and val:
            self.season_slider = int(val[0])
        else:
            try:
                self.season_slider = int(val)
            except Exception:
                self.season_slider = 5

    def set_single_season_only(self, val: bool):
        self.single_season_only = val

    def refresh(self):
        self.refresh_counter += 1

    @rx.var
    def leaderboard_rows(self) -> list[dict]:
        _ = self.refresh_counter
        return compute_leaderboard_data()

    @rx.var
    def has_rows(self) -> bool:
        return len(self.leaderboard_rows) > 0

    @rx.var
    def user_wagers_stacked_data(self) -> list[dict]:
        """Data for User Wagers Correct/Incorrect Stacked Bar Chart (SDDREQ-165)."""
        _ = self.refresh_counter
        all_preds = get_all_predictions(5)
        rows = self.leaderboard_rows
        chart_data = []

        for r in rows:
            u = r["user"]
            u_preds = [p for p in all_preds if p.get("username") == u]
            correct_pts = sum(int(p.get("points", 0)) for p in u_preds if str(p.get("status", "")).lower() == "correct")
            incorrect_pts = sum(int(p.get("points", 0)) for p in u_preds if str(p.get("status", "")).lower() == "incorrect")
            open_pts = sum(int(p.get("points", 0)) for p in u_preds if str(p.get("status", "")).lower() == "open")

            chart_data.append({
                "user": u,
                "correct_pts": correct_pts,
                "incorrect_pts": incorrect_pts,
                "open_pts": open_pts,
                "total_wagered": correct_pts + incorrect_pts + open_pts,
            })

        return chart_data

    @rx.var
    def user_names_list(self) -> list[str]:
        return [r["user"] for r in self.leaderboard_rows]

    @rx.var
    def points_growth_chart_data(self) -> list[dict]:
        """Data for All Time Points Growth Chart across races (SDDREQ-166)."""
        _ = self.refresh_counter
        rows = self.leaderboard_rows
        if not rows:
            return []

        from the_alternative_f1.seasons.projections import compute_season_projections
        proj = compute_season_projections(5)
        next_race_name = proj.get("next_main_race", proj.get("next_race", "Australia"))
        current_race = next_race_name if next_race_name else "Australia"

        data = []
        # Preseason / Starting point: 100 base pts for each user
        base_pt = {"race": "Preseason"}
        for r in rows:
            base_pt[r["user"]] = 100
        data.append(base_pt)

        # Plot active remaining points at the upcoming race
        end_pt = {"race": current_race}
        for r in rows:
            end_pt[r["user"]] = r.get("all_time_pts", 100)
        data.append(end_pt)

        return data

    def refresh(self):
        self.refresh_counter += 1


def alternative_points_leaderboard_view() -> rx.Component:
    """Render the Alternative Points Leaderboard strictly following SDDREQ-167 layout."""

    def pinned_driver_cell(row: dict) -> rx.Component:
        return rx.box(
            rx.hstack(
                rx.badge(
                    row["rank_str"],
                    bg=row["rank_bg"],
                    color=row["rank_color"],
                    border=row["rank_border"],
                    font_size="10px",
                    font_weight="800",
                    width="22px",
                    justify="center",
                ),
                rx.text(row["user"], color="white", font_weight="700", font_size="12px", white_space="nowrap"),
                spacing="2",
                align="center",
            ),
            height="48px",
            display="flex",
            align_items="center",
            border_bottom="1px solid rgba(255,255,255,0.06)",
            padding="4px 10px",
            width="100%",
        )

    def pinned_points_cell(row: dict) -> rx.Component:
        return rx.box(
            rx.text(row["pts_str"], color="#00b4da", font_weight="800", font_size="12px", font_family="Outfit"),
            height="48px",
            display="flex",
            align_items="center",
            justify_content="center",
            border_bottom="1px solid rgba(255,255,255,0.06)",
            padding="4px 10px",
            width="100%",
        )

    def season_points_cell(s: int):
        def _cell(row: dict) -> rx.Component:
            if s == 5:
                return rx.box(
                    rx.text(row["s5_str"], color="#00b4da", font_weight="700", font_size="12px", font_family="Outfit"),
                    height="48px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    border_bottom="1px solid rgba(255,255,255,0.06)",
                    padding="4px 8px",
                    width="100%",
                )
            else:
                return rx.box(
                    rx.text(row[f"s{s}_str"], color="#555555", font_weight="600", font_size="12px"),
                    height="48px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    border_bottom="1px solid rgba(255,255,255,0.06)",
                    padding="4px 8px",
                    width="100%",
                )
        return _cell

    # 1. Two Frozen Left Columns: User Name & All Time Alternative Points (SDDREQ-154)
    pinned_driver_col = rx.box(
        rx.box(
            rx.text("USER NAME", font_size="11px", font_weight="800", color="#00b4da", letter_spacing="0.06em"),
            height="44px",
            display="flex",
            align_items="center",
            padding_x="10px",
            bg="#15151D",
            border_bottom="2px solid rgba(255,255,255,0.1)",
            width="100%",
        ),
        rx.foreach(LeaderboardState.leaderboard_rows, pinned_driver_cell),
        width="160px",
        min_width="160px",
        max_width="160px",
        bg="#181822",
        border="1px solid #2C2C36",
        border_radius="md",
        z_index="25",
        box_shadow="4px 0 12px rgba(0,0,0,0.5)",
        flex_shrink="0",
    )

    pinned_pts_col = rx.box(
        rx.box(
            rx.text("ALL TIME PTS", font_size="11px", font_weight="800", color="#00b4da", letter_spacing="0.06em"),
            height="44px",
            display="flex",
            align_items="center",
            justify_content="center",
            padding_x="10px",
            bg="#15151D",
            border_bottom="2px solid rgba(255,255,255,0.1)",
            width="100%",
        ),
        rx.foreach(LeaderboardState.leaderboard_rows, pinned_points_cell),
        width="110px",
        min_width="110px",
        max_width="110px",
        bg="#181822",
        border="1px solid #2C2C36",
        border_radius="md",
        z_index="24",
        box_shadow="4px 0 12px rgba(0,0,0,0.4)",
        flex_shrink="0",
    )

    frozen_columns = rx.hstack(
        pinned_driver_col,
        pinned_pts_col,
        spacing="2",
        position="sticky",
        left="0",
        z_index="25",
        flex_shrink="0",
    )

    # 2. Season 5 Column (Alternative Points begins in Season 5 per SDDREQ-154)
    header_tab = rx.box(
        rx.hstack(
            rx.text("Season 5", font_size="11px", font_weight="800", font_family="Outfit"),
            rx.box(width="6px", height="6px", border_radius="50%", bg="white", flex_shrink="0"),
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
        bg="#00b4da",
        color="white",
        border_bottom="2px solid rgba(255,255,255,0.1)",
        width="100%",
    )

    season_col_card = rx.box(
        header_tab,
        rx.foreach(LeaderboardState.leaderboard_rows, season_points_cell(5)),
        width="120px",
        min_width="120px",
        max_width="120px",
        position="relative",
        z_index=20,
        bg="#1A1A26",
        border="1.5px solid #00b4da",
        border_radius="md",
        box_shadow="0 8px 24px rgba(0, 180, 218, 0.35), 0 4px 12px rgba(0,0,0,0.8)",
        flex_shrink="0",
    )

    # 3. Table Container: Frozen User Name + Frozen All Time Points + Season 5
    standings_table = rx.box(
        rx.hstack(
            frozen_columns,
            season_col_card,
            spacing="2",
            align_items="stretch",
        ),
        overflow_x="auto",
        width="100%",
        padding="3",
        bg="#111116",
        border_radius="xl",
        border="1px solid #282832",
    )

    table_body = rx.cond(
        LeaderboardState.has_rows,
        standings_table,
        rx.box(
            rx.vstack(
                rx.icon("users", size=36, color="#00b4da"),
                rx.text("No Predictors on the Leaderboard Yet", font_weight="800", color="white", font_size="md"),
                rx.text(
                    "Log in with Discord and place predictions to earn Alternative Points and claim the top spot!",
                    color="#8E8E93",
                    font_size="sm",
                    text_align="center",
                    max_width="450px",
                ),
                align="center",
                spacing="2",
                padding="32px",
            ),
            width="100%",
            bg="#111116",
            border="1px solid #2C2C32",
            border_radius="xl",
        ),
    )

    # Expander container for All Time Table (SDDREQ-167)
    table_expander = rx.box(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("table", size=18, color="#00b4da"),
                    rx.text(
                        "All-Time Standings Table",
                        font_size="16px",
                        font_weight="800",
                        color="white",
                        font_family="Outfit",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.badge(
                    "Ranked by All Time Points",
                    bg="rgba(0, 180, 218, 0.15)",
                    color="#00b4da",
                    border="1px solid rgba(0, 180, 218, 0.4)",
                    border_radius="full",
                    font_size="11px",
                    font_weight="700",
                    padding_x="8px",
                    padding_y="3px",
                ),
                rx.spacer(),
                rx.icon(
                    rx.cond(LeaderboardState.table_expander_open, "chevron-up", "chevron-down"),
                    size=20,
                    color="#AAAAAA",
                ),
                width="100%",
                align="center",
                spacing="3",
                cursor="pointer",
                on_click=LeaderboardState.toggle_table_expander,
                padding_y="1",
            ),
            rx.cond(
                LeaderboardState.table_expander_open,
                table_body,
                rx.fragment(),
            ),
            width="100%",
            spacing="3",
        ),
        bg="#15151A",
        border="1px solid #2C2C32",
        border_radius="2xl",
        padding=["16px", "20px", "24px"],
        width="100%",
        box_shadow="0 8px 24px rgba(0,0,0,0.4)",
        box_sizing="border-box",
    )

    # 3. Side-by-side section: User Wagers Stacked Bar Chart & Points Growth Line Chart (SDDREQ-167)
    stacked_bar_chart = zoomable_chart(
        lambda h: rx.cond(
            LeaderboardState.has_rows,
            rx.recharts.bar_chart(
                rx.recharts.x_axis(type_="number", stroke="#888888", font_size=10),
                rx.recharts.y_axis(data_key="user", type_="category", stroke="#FFFFFF", font_size=10, width=95),
                rx.recharts.cartesian_grid(horizontal=False, stroke="rgba(255, 255, 255, 0.1)"),
                rx.recharts.bar(data_key="correct", stack_id="a", fill="#00b4da", name="Correct Points"),
                rx.recharts.bar(data_key="incorrect", stack_id="a", fill="#FF8C00", name="Incorrect Points"),
                rx.recharts.graphing_tooltip(),
                data=LeaderboardState.user_wagers_stacked_data,
                layout="vertical",
                width="100%",
                height=h,
            ),
            rx.center(
                rx.text("No wager results yet", color="#666", font_size="xs"),
                height=f"{h}px",
                width="100%",
            ),
        ),
        title="User Wagers Outcome",
        chart_id="user_wagers_stacked_bar_chart",
        height=270,
        large_height=370,
        download_position="top_right",
    )

    stacked_bar_card = chart_card(
        title="User Wagers Outcome",
        chart_component=stacked_bar_chart,
        chart_id="user_wagers_stacked_bar_chart",
        download_position="top_right",
        icon="bar-chart-2",
        extra_content=interactive_line_chart_key(
            chart_id="user_wagers_stacked_bar_chart",
            items=[("Correct Points", "#00b4da"), ("Incorrect Points", "#FF8C00")],
            title="Key (Wager Outcomes)",
            hint="Click outcome to highlight",
        ),
        border_radius="2xl",
        box_shadow="0 8px 24px rgba(0,0,0,0.4)",
    )

    growth_toolbar = rx.hstack(
        rx.hstack(
            rx.text("Season 5", font_size="11px", color="#00b4da", font_weight="700"),
            rx.slider(
                min=5,
                max=5,
                step=1,
                value=[LeaderboardState.season_slider],
                on_change=LeaderboardState.set_season_slider,
                color_scheme="cyan",
                size="1",
                width="110px",
            ),
            spacing="2",
            align="center",
        ),
        rx.spacer(),
        rx.hstack(
            rx.checkbox(
                checked=LeaderboardState.single_season_only,
                on_change=LeaderboardState.set_single_season_only,
                size="1",
                color_scheme="cyan",
            ),
            rx.text("Single Season", font_size="11px", color="#D0D0D5"),
            spacing="1",
            align="center",
        ),
        width="100%",
        align="center",
        padding_x="1",
        margin_bottom="1",
    )

    growth_line_chart = zoomable_chart(
        lambda h: rx.cond(
            LeaderboardState.has_rows,
            rx.recharts.line_chart(
                rx.recharts.x_axis(data_key="race", stroke="#888888", font_size=9),
                rx.recharts.y_axis(stroke="#888888", font_size=10, domain=[0, "auto"]),
                rx.recharts.reference_line(y=100, stroke="rgba(255, 255, 255, 0.25)", stroke_dasharray="3 3", label="100 Base Pts"),
                rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.1)"),
                rx.recharts.graphing_tooltip(),
                *[
                    rx.recharts.line(
                        data_key=user,
                        stroke=color,
                        stroke_width=2,
                        dot={"fill": color, "stroke": color, "r": 3},
                        name=user,
                        type_="monotone",
                    )
                    for user, color in PREDICTOR_KEY_ITEMS
                ],
                data=LeaderboardState.points_growth_chart_data,
                width="100%",
                height=h,
            ),
            rx.center(
                rx.text("No points growth data yet", color="#666", font_size="xs"),
                height=f"{h}px",
                width="100%",
            ),
        ),
        title="All Time Points Growth",
        chart_id="points_growth_line_chart",
        height=230,
        large_height=330,
        download_position="top_right",
    )

    growth_chart_card = chart_card(
        title="All Time Points Growth",
        chart_component=rx.vstack(growth_toolbar, growth_line_chart, width="100%", spacing="2"),
        chart_id="points_growth_line_chart",
        download_position="top_right",
        icon="trending-up",
        extra_content=interactive_line_chart_key(
            chart_id="points_growth_line_chart",
            items=PREDICTOR_KEY_ITEMS,
            title="Key (Predictors)",
            hint="Click predictor to highlight",
        ),
        border_radius="2xl",
        box_shadow="0 8px 24px rgba(0,0,0,0.4)",
    )

    side_by_side_grid = rx.grid(
        stacked_bar_card,
        growth_chart_card,
        columns=rx.breakpoints(initial="1", md="2"),
        spacing="5",
        width="100%",
    )

    return rx.vstack(
        rx.hstack(
            rx.heading(
                "Alternative Points Leaderboard",
                size="6",
                color="white",
                font_family="Outfit",
            ),
            rx.spacer(),
            width="100%",
            align="center",
            margin_bottom="1",
        ),
        table_expander,
        side_by_side_grid,
        width="100%",
        spacing="5",
        align_items="start",
    )
