"""Alternative Points Leaderboard — Reflex Component.
Implements TAF1APP-SDDFEAT-17 and approved downstream SDD requirements:
- SDDREQ-153: Driver Ranking (Ranked by all-time remaining Alternative Points, sets sort)
- SDDREQ-154: Table Format (Frozen columns: Driver Name, All Time Points; Cascading columns starting with Season 5)
Matches the cascading table design in all time > races (RacesAllTime.py).
"""

import reflex as rx
from the_alternative_f1.all_time_stats.Functions import get_excel_sheet
from the_alternative_f1.seasons.predictions_market import get_user_total_points, _load_local_user_points, _get_supabase, _load_local_predictions

_LEAGUE_DRIVERS_CACHE = None

def _get_all_league_drivers() -> set[str]:
    """Returns lowercased names of all official F1 league drivers across all seasons."""
    global _LEAGUE_DRIVERS_CACHE
    if _LEAGUE_DRIVERS_CACHE is not None:
        return _LEAGUE_DRIVERS_CACHE

    drivers = {
        "joshua", "eddie", "nick", "del", "patrick", "josh", "matthew",
        "brently", "grayson", "josh c.", "boz", "evelo", "jaden", "leo",
        "jairo", "randy", "unknown", "driver", "none"
    }
    for s in range(1, 6):
        try:
            df = get_excel_sheet(f"Season{s}")
            if not df.empty and "Driver" in df.columns:
                for d in df["Driver"].dropna():
                    d_str = str(d).strip().lower()
                    if d_str:
                        drivers.add(d_str)
        except Exception:
            pass
    _LEAGUE_DRIVERS_CACHE = drivers
    return drivers


def is_league_driver(username: str) -> bool:
    """Returns True if the username matches an official F1 league driver."""
    if not username:
        return False
    return str(username).strip().lower() in _get_all_league_drivers()


def compute_leaderboard_data() -> list[dict]:
    """Compiles all-time and seasonal points for logged-in users who received points or placed predictions.
    Only displays users who have logged in and received their 100 points or placed predictions.
    """
    all_users = set()

    # Add any users from Supabase user_prediction_points or predictions tables
    sb = _get_supabase()
    if sb:
        try:
            res = sb.table("user_prediction_points").select("username").execute()
            if res.data:
                for r in res.data:
                    u = str(r.get("username", "")).strip()
                    if u:
                        all_users.add(u)
        except Exception:
            pass

        try:
            res_preds = sb.table("predictions").select("username").execute()
            if res_preds.data:
                for r in res_preds.data:
                    u = str(r.get("username", "")).strip()
                    if u:
                        all_users.add(u)
        except Exception:
            pass

    local_pts = _load_local_user_points()
    for u in list(local_pts.keys()):
        u_clean = str(u).strip()
        if u_clean:
            all_users.add(u_clean)

    local_preds = _load_local_predictions()
    for p in local_preds:
        u_clean = str(p.get("username", "")).strip()
        if u_clean:
            all_users.add(u_clean)

    rows = []
    for user in all_users:
        curr_pts = get_user_total_points(user)
        rows.append({
            "driver": user,
            "all_time_pts": curr_pts,
            "s5": curr_pts,
        })

    # SDDREQ-153: Rank users by all time remaining Alternative Points (sets sort)
    rows.sort(key=lambda r: (-r["all_time_pts"], r["driver"].lower()))
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
    """Reflex state managing page-flipping cascading columns for Leaderboard."""
    selected_season_col: str = "s5"
    refresh_counter: int = 0

    def set_season_col(self, col: str):
        self.selected_season_col = col

    @rx.var
    def leaderboard_rows(self) -> list[dict]:
        _ = self.refresh_counter
        return compute_leaderboard_data()

    @rx.var
    def has_rows(self) -> bool:
        return len(self.leaderboard_rows) > 0

    def refresh(self):
        self.refresh_counter += 1


def alternative_points_leaderboard_view() -> rx.Component:
    """Render the Alternative Points Leaderboard with frozen left columns and cascading season columns."""

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
                rx.text(row["driver"], color="white", font_weight="700", font_size="12px", white_space="nowrap"),
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

    def season_points_cell(row: dict) -> rx.Component:
        return rx.box(
            rx.text(row["s5_str"], color="#D0D0D5", font_weight="600", font_size="12px"),
            height="48px",
            display="flex",
            align_items="center",
            justify_content="center",
            border_bottom="1px solid rgba(255,255,255,0.06)",
            padding="4px 8px",
            width="100%",
        )

    # 1. Pinned Left Columns: User Name & All Time Alternative Points (SDDREQ-154)
    pinned_driver_col = rx.box(
        rx.box(
            rx.text("USER", font_size="11px", font_weight="800", color="#00b4da", letter_spacing="0.06em"),
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

    # 2. Cascading Season Columns (Starting with Season 5 per SDDREQ-154)
    is_active = (LeaderboardState.selected_season_col == "s5")
    header_tab = rx.box(
        rx.hstack(
            rx.text("Season 5", font_size="11px", font_weight="800", font_family="Outfit"),
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
        padding_x="10px",
        display="flex",
        align_items="center",
        bg=rx.cond(is_active, "#00b4da", "#15151D"),
        color="white",
        border_bottom="2px solid rgba(255,255,255,0.1)",
        cursor="pointer",
        on_click=lambda: LeaderboardState.set_season_col("s5"),
        _hover={"bg": "#00b4da", "color": "white"},
        transition="all 0.15s ease",
        width="100%",
    )

    season_col_box = rx.box(
        header_tab,
        rx.foreach(LeaderboardState.leaderboard_rows, season_points_cell),
        width="120px",
        min_width="120px",
        max_width="120px",
        bg=rx.cond(is_active, "#1A1A26", "#14141A"),
        border="1px solid #2C2C36",
        border_radius="md",
        z_index=rx.cond(is_active, "20", "10"),
        box_shadow=rx.cond(is_active, "0 8px 24px rgba(0,0,0,0.6)", "2px 0 8px rgba(0,0,0,0.3)"),
        transition="all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
        flex_shrink="0",
        cursor="pointer",
        on_click=lambda: LeaderboardState.set_season_col("s5"),
    )

    table_body = rx.cond(
        LeaderboardState.has_rows,
        rx.box(
            rx.hstack(
                pinned_driver_col,
                pinned_pts_col,
                season_col_box,
                spacing="0",
                align_items="flex-start",
                padding_bottom="12px",
                width="100%",
                min_width="fit-content",
            ),
            width="100%",
            overflow_x="auto",
            padding="12px",
            bg="#111116",
            border="1px solid #2C2C32",
            border_radius="xl",
        ),
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

    return rx.vstack(
        rx.hstack(
            rx.heading(
                "Alternative Points Leaderboard",
                size="6",
                color="white",
                font_family="Outfit",
            ),
            rx.spacer(),
            rx.badge("Ranked by All Time Points", bg="rgba(0, 180, 218, 0.15)", color="#00b4da", border="1px solid rgba(0, 180, 218, 0.3)", border_radius="full", font_size="11px", padding_x="3"),
            width="100%",
            align="center",
            margin_bottom="3",
        ),
        table_body,
        width="100%",
        spacing="3",
        align_items="start",
    )
