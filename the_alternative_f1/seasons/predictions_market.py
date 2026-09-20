"""Predictions Market Tab — Reflex Component & State Management.
Implements TAF1APP-SDDFEAT-16 and approved downstream SDD requirements:
- SDDREQ-142: Alternative Points Per User (100 points upon first visit/login, recorded in Supabase / fallback)
- SDDREQ-143: Submit a Prediction Button (blue button, visible when logged in and points > 0)
- SDDREQ-144: Display Remaining Alternative Points (real-time balance after active wagers)
- SDDREQ-145: Delete Prediction (only user's own predictions, prior to 1-hour pre-race lockout)
- SDDREQ-146: Prediction Options (Winner FOR/AGAINST, Highest Score FOR/AGAINST, Podium FOR/AGAINST, Expected Points OVER/UNDER)
- SDDREQ-147: Predictions Dashboard (themed display of all submissions for the race)
- SDDREQ-148: Correct Predictions (wager + 15% + split of opposing pool)
- SDDREQ-149: Incorrect Predictions (0 returned)
- SDDREQ-150: Prediction Finalization (auto-settles upon race upload)
- SDDREQ-151: Previous Lines storage
"""

import os
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pandas as pd
import reflex as rx

from the_alternative_f1.all_time_stats.Functions import get_excel_sheet
from the_alternative_f1.all_time_stats.DetailedAllTime import _extract_track_name
from the_alternative_f1.seasons.projections import compute_season_projections
from the_alternative_f1.constructor_colors import get_constructor_color

USER_POINTS_JSON = Path(__file__).parent / "user_points.json"
PREDICTIONS_JSON = Path(__file__).parent / "predictions.json"


def _get_supabase():
    """Lazy-load Supabase client if available."""
    try:
        from the_alternative_f1.the_alternative_f1 import get_supabase_client
        return get_supabase_client()
    except Exception:
        return None


# ── Local File Persistence Fallbacks for Total Points & Predictions ───────────
def _load_local_user_points() -> dict:
    if USER_POINTS_JSON.exists():
        try:
            with open(USER_POINTS_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_local_user_points(data: dict):
    try:
        with open(USER_POINTS_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving user_points.json: {e}")


def _load_local_predictions() -> list[dict]:
    if PREDICTIONS_JSON.exists():
        try:
            with open(PREDICTIONS_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save_local_predictions(data: list[dict]):
    try:
        with open(PREDICTIONS_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving predictions.json: {e}")


# ── Lockout Calculation (1 Hour Pre-Race) ──────────────────────────────────────
def is_race_locked(season_num: int, race_name: str) -> tuple[bool, str]:
    """Determines if the race is locked (1 hour before 6:45 PM Mountain Time on race date)."""
    try:
        df_sched = get_excel_sheet(f"S{season_num}Schedule")
        if df_sched.empty or "Race" not in df_sched.columns or "Date" not in df_sched.columns:
            return (False, "Open")

        row = df_sched[df_sched["Race"].astype(str).str.strip().str.lower() == str(race_name).strip().lower()]
        if row.empty:
            return (False, "Open")

        date_val = str(row.iloc[0]["Date"]).strip()
        # Parse date assuming format like MM/DD/YYYY or YYYY-MM-DD
        dt_race = None
        for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%B %d, %Y"):
            try:
                dt_race = datetime.strptime(date_val, fmt)
                break
            except Exception:
                continue

        if not dt_race:
            return (False, "Open")

        # 6:45 PM Mountain Time (MDT is UTC-6, MST is UTC-7; using UTC-6 for race season)
        mountain_tz = timezone(timedelta(hours=-6))
        race_start_time = datetime(
            year=dt_race.year, month=dt_race.month, day=dt_race.day,
            hour=18, minute=45, second=0, tzinfo=mountain_tz
        )
        lockout_time = race_start_time - timedelta(hours=1)
        now_mountain = datetime.now(mountain_tz)

        if now_mountain >= lockout_time:
            return (True, f"Locked (Closed at {lockout_time.strftime('%I:%M %p MDT')})")
        else:
            time_left = lockout_time - now_mountain
            total_secs = max(0, int(time_left.total_seconds()))
            days = total_secs // 86400
            rem_secs = total_secs % 86400
            hours = rem_secs // 3600
            mins = (rem_secs % 3600) // 60
            day_unit = "day" if days == 1 else "days"
            hour_unit = "hour" if hours == 1 else "hours"
            if days == 0 and hours == 0:
                return (False, f"Locks in 0 days {mins}m" if mins > 0 else "Locks in < 1m")
            return (False, f"Locks in {days} {day_unit} {hours} {hour_unit}")
    except Exception:
        return (False, "Open")


# ── Points Management (SDDREQ-142 & SDDREQ-144) ───────────────────────────────
def get_user_total_points(username: str) -> int:
    """Fetches user points, initializing to 100 if user does not exist yet."""
    if not username:
        return 0

    local_data = _load_local_user_points()
    if username not in local_data:
        local_data[username] = {
            "points": 100,
            "all_time_points": 100,
            "season_points": {"5": 100},
        }
        _save_local_user_points(local_data)

    sb = _get_supabase()
    if sb:
        try:
            res = sb.table("user_prediction_points").select("points").eq("username", username).execute()
            if res.data and len(res.data) > 0:
                pts = int(res.data[0]["points"])
                local_data[username]["points"] = pts
                local_data[username]["all_time_points"] = pts
                _save_local_user_points(local_data)
                return pts
            else:
                payload = {
                    "username": username,
                    "points": 100,
                    "all_time_points": 100,
                    "season_points": {"5": 100},
                }
                sb.table("user_prediction_points").insert(payload).execute()
                return 100
        except Exception as e:
            print(f"Supabase user_prediction_points error: {e}")

    return int(local_data[username].get("points", 100))


def update_user_points(username: str, new_points: int):
    """Updates user points in Supabase and local storage."""
    if not username:
        return
    sb = _get_supabase()
    if sb:
        try:
            sb.table("user_prediction_points").update({
                "points": new_points,
                "all_time_points": new_points,
            }).eq("username", username).execute()
        except Exception as e:
            print(f"Supabase update points error: {e}")

    local_data = _load_local_user_points()
    if username in local_data:
        local_data[username]["points"] = new_points
        local_data[username]["all_time_points"] = new_points
        _save_local_user_points(local_data)


# ── Prediction Records & Settlement Engine ─────────────────────────────────────
def settle_completed_predictions(season_num: int = 5):
    """Auto-settles open predictions when race results are uploaded in the Season sheet.
    Crucially, sprints are summed with their regular races for final prediction verdicts (SDDREQ-150).
    """
    sb = _get_supabase()
    if not sb:
        return

    try:
        df_season = get_excel_sheet(f"Season{season_num}")
        df_sched = get_excel_sheet(f"S{season_num}Schedule")
        if df_season.empty or df_sched.empty:
            return

        res = sb.table("predictions").select("*").eq("season", season_num).eq("status", "open").execute()
        open_preds = res.data if res.data else []
        if not open_preds:
            return

        all_races = [str(r).strip() for r in df_sched["Race"] if pd.notna(r) and not str(r).strip().startswith(("Pre", "Post"))]
        main_races = [r for r in all_races if "sprint" not in r.lower()]

        for main_race in main_races:
            p_col = f"{main_race}Points"
            if p_col not in df_season.columns:
                continue

            # Check if this main race has been run
            valid_pts = pd.to_numeric(df_season[p_col], errors="coerce").fillna(0)
            if not (valid_pts > 0).any():
                continue

            # Associated sprint name
            sprint_name = None
            for r in all_races:
                if "sprint" in r.lower() and _extract_track_name(r).lower() == _extract_track_name(main_race).lower():
                    sprint_name = r
                    break

            sprint_p_col = f"{sprint_name}Points" if sprint_name else None

            # Calculate total weekend points per team (Sprint + Regular race summed)
            teams = sorted(df_season["Team"].dropna().unique())
            team_weekend_pts = {}
            for t in teams:
                t_df = df_season[df_season["Team"] == t]
                main_pts = float(pd.to_numeric(t_df[p_col], errors="coerce").fillna(0).sum())
                sprint_pts = float(pd.to_numeric(t_df[sprint_p_col], errors="coerce").fillna(0).sum()) if sprint_p_col and sprint_p_col in df_season.columns else 0.0
                team_weekend_pts[t] = main_pts + sprint_pts

            # Winner of the main race
            winner_team = None
            place_col = f"{main_race}Place"
            if place_col in df_season.columns:
                p1_df = df_season[pd.to_numeric(df_season[place_col], errors="coerce") == 1]
                if not p1_df.empty:
                    winner_team = str(p1_df.iloc[0]["Team"]).strip()

            # Highest scoring team (Sprint + Race summed)
            highest_team = max(team_weekend_pts.keys(), key=lambda t: team_weekend_pts[t]) if team_weekend_pts else None

            # Podium teams (Top 3 by weekend points summed)
            sorted_teams_by_pts = sorted(teams, key=lambda t: team_weekend_pts.get(t, 0), reverse=True)
            podium_teams = sorted_teams_by_pts[:3]

            # Filter open predictions for this race
            race_preds = [
                p for p in open_preds 
                if str(p.get("race", "")).strip().lower() in (main_race.lower(), (sprint_name or "").lower(), _extract_track_name(main_race).lower())
            ]
            if not race_preds:
                continue

            pools = {}
            for p in race_preds:
                k = (p["category"], p["target"])
                pools.setdefault(k, []).append(p)

            for (cat, target), pred_list in pools.items():
                for p in pred_list:
                    stance = str(p.get("stance", "FOR")).upper()
                    is_correct = False

                    if cat == "Expected Race Winner":
                        matched = (winner_team == target)
                        is_correct = (matched if "FOR" in stance else not matched)
                    elif cat == "Highest Scoring Team":
                        matched = (highest_team == target)
                        is_correct = (matched if "FOR" in stance else not matched)
                    elif cat == "Podium Teams":
                        matched = (target in podium_teams)
                        is_correct = (matched if "FOR" in stance else not matched)
                    elif cat == "Expected Points":
                        line = float(p.get("line_value", 0.0) or 0.0)
                        actual = team_weekend_pts.get(target, 0.0)
                        is_correct = (actual > line) if "OVER" in stance else (actual < line)

                    p["_is_correct"] = is_correct

                winners = [p for p in pred_list if p["_is_correct"]]
                losers = [p for p in pred_list if not p["_is_correct"]]
                losing_pool = sum(int(p["points"]) for p in losers)
                total_win_wagers = sum(int(p["points"]) for p in winners)

                for p in winners:
                    wager = int(p["points"])
                    base_payout = wager + int(round(wager * 0.15))
                    opposing_split = int(round(losing_pool * (wager / float(total_win_wagers)))) if total_win_wagers > 0 else 0
                    total_payout = base_payout + opposing_split

                    sb.table("predictions").update({
                        "status": "correct",
                        "payout": total_payout,
                    }).eq("id", p["id"]).execute()

                    u = p["username"]
                    curr_pts = get_user_total_points(u)
                    update_user_points(u, curr_pts + total_payout)

                for p in losers:
                    sb.table("predictions").update({
                        "status": "incorrect",
                        "payout": 0,
                    }).eq("id", p["id"]).execute()
    except Exception as e:
        print(f"Prediction settlement error: {e}")


def get_all_predictions(season_num: int = 5) -> list[dict]:
    """Retrieves all predictions for the season, auto-settling completed races."""
    settle_completed_predictions(season_num)
    sb = _get_supabase()
    if sb:
        try:
            res = sb.table("predictions").select("*").eq("season", season_num).order("created_at", desc=True).execute()
            if res.data is not None:
                local_preds = _load_local_predictions()
                sb_ids = {str(p.get("id")) for p in res.data}
                combined = list(res.data)
                for lp in local_preds:
                    if str(lp.get("id")) not in sb_ids and int(lp.get("season", 5)) == season_num:
                        combined.append(lp)
                return combined
        except Exception as e:
            print(f"Supabase get_all_predictions error: {e}")
    local_preds = _load_local_predictions()
    return [p for p in local_preds if int(p.get("season", 5)) == season_num]


def insert_prediction(pred: dict) -> bool:
    """Inserts a new prediction record into database and local storage."""
    local_preds = _load_local_predictions()
    local_preds.insert(0, pred)
    _save_local_predictions(local_preds)

    sb = _get_supabase()
    if sb:
        try:
            sb.table("predictions").insert(pred).execute()
            return True
        except Exception as e:
            print(f"Supabase insert_prediction error: {e}")
    return True


def remove_prediction(pred_id: str | int, username: str) -> bool:
    """Removes a prediction and refunds points."""
    refund_points = 0
    local_preds = _load_local_predictions()
    updated = []
    for p in local_preds:
        if str(p.get("id")) == str(pred_id) and p.get("username") == username:
            refund_points = int(p.get("points", 0))
        else:
            updated.append(p)
    _save_local_predictions(updated)

    sb = _get_supabase()
    if sb:
        try:
            res = sb.table("predictions").select("points").eq("id", pred_id).eq("username", username).execute()
            if res.data and len(res.data) > 0:
                refund_points = int(res.data[0]["points"])
                sb.table("predictions").delete().eq("id", pred_id).eq("username", username).execute()
        except Exception as e:
            print(f"Supabase remove_prediction error: {e}")

    return True


class PredictionsMarketState(rx.State):
    """Reflex state for the Predictions Market Tab."""
    discord_username: str = rx.LocalStorage("", name="discord_username", sync=True)
    refresh_trigger: int = 0
    modal_open: bool = False
    selected_category: str = "Expected Race Winner"
    selected_target: str = ""
    selected_stance: str = "FOR"
    wager_amount: int = 10
    feedback_message: str = ""

    @rx.var
    def discord_auth_url(self) -> str:
        from the_alternative_f1.oauth_discord import load_env
        load_env()
        client_id = os.getenv("DISCORD_CLIENT_ID", "").strip()
        redirect_uri = os.getenv("DISCORD_REDIRECT_URI", "").strip()
        if not client_id or not redirect_uri:
            return ""
        import urllib.parse
        encoded_redirect = urllib.parse.quote(redirect_uri, safe="")
        return f"https://discord.com/oauth2/authorize?client_id={client_id}&redirect_uri={encoded_redirect}&response_type=code&scope=identify"

    def sync_user(self, username: str):
        self.discord_username = username

    async def logout(self):
        self.discord_username = ""
        try:
            from the_alternative_f1.the_alternative_f1 import State
            main_state = await self.get_state(State)
            main_state.discord_username = ""
            main_state.discord_avatar = ""
        except Exception:
            pass

    def open_modal(self):
        self.modal_open = True
        self.feedback_message = ""
        self.wager_amount = 10
        self.selected_category = "Expected Race Winner"
        self.selected_stance = "FOR"
        # Default target
        proj = compute_season_projections(5)
        self.selected_target = proj.get("expected_winner", "")

    def close_modal(self):
        self.modal_open = False
        self.feedback_message = ""

    def set_category(self, cat: str):
        self.selected_category = cat
        proj = compute_season_projections(5)
        if cat == "Expected Race Winner":
            self.selected_target = proj.get("expected_winner", "")
            self.selected_stance = "FOR"
        elif cat == "Highest Scoring Team":
            self.selected_target = proj.get("expected_highest_score_team", "")
            self.selected_stance = "FOR"
        elif cat == "Podium Teams":
            podiums = proj.get("expected_podium", [])
            self.selected_target = podiums[0] if podiums else ""
            self.selected_stance = "FOR"
        elif cat == "Expected Points":
            teams = proj.get("teams", [])
            self.selected_target = teams[0] if teams else ""
            self.selected_stance = "OVER"

    def set_target(self, target: str):
        self.selected_target = target

    def set_stance(self, stance: str | list[str]):
        if isinstance(stance, list):
            self.selected_stance = stance[0] if stance else "FOR"
        else:
            self.selected_stance = str(stance)

    def set_wager(self, amount: int | str):
        try:
            self.wager_amount = max(1, int(amount))
        except Exception:
            self.wager_amount = 1

    @rx.var
    def target_options(self) -> list[str]:
        proj = compute_season_projections(5)
        if self.selected_category == "Expected Race Winner":
            return [proj.get("expected_winner", "")]
        elif self.selected_category == "Highest Scoring Team":
            return [proj.get("expected_highest_score_team", "")]
        elif self.selected_category == "Podium Teams":
            return proj.get("expected_podium", [])
        elif self.selected_category == "Expected Points":
            return sorted(proj.get("teams", []))
        return []

    @rx.var
    def stance_options(self) -> list[str]:
        if self.selected_category == "Expected Points":
            return ["OVER", "UNDER"]
        return ["FOR", "AGAINST"]

    @rx.var
    def current_user(self) -> str:
        return self.discord_username

    @rx.var
    def user_remaining_points(self) -> int:
        _ = self.refresh_trigger
        username = self.current_user
        if not username:
            return 0
        total = get_user_total_points(username)
        # Deduct active open wagers
        all_preds = get_all_predictions(5)
        active_wagers = sum(int(p["points"]) for p in all_preds if p.get("username") == username and p.get("status") == "open")
        return max(0, total - active_wagers)

    @rx.var
    def is_locked(self) -> bool:
        proj = compute_season_projections(5)
        race_name = proj.get("next_race", "")
        locked, _ = is_race_locked(5, race_name)
        return locked

    @rx.var
    def lockout_label(self) -> str:
        proj = compute_season_projections(5)
        race_name = proj.get("next_race", "")
        _, status_str = is_race_locked(5, race_name)
        return status_str

    @rx.var
    def all_predictions_list(self) -> list[dict]:
        _ = self.refresh_trigger
        preds = get_all_predictions(5)
        res = []
        for p in preds:
            item = dict(p)
            item["is_mine"] = (p.get("username") == self.current_user)
            item["can_delete"] = (p.get("username") == self.current_user and p.get("status") == "open" and not self.is_locked)
            item["team_color"] = get_constructor_color(str(p.get("target", "")))
            stance = str(p.get("stance", "FOR")).upper()
            item["is_positive"] = bool("FOR" in stance or "OVER" in stance)
            status_val = str(p.get("status", "open")).lower()
            item["status_upper"] = status_val.upper()
            if status_val == "correct":
                item["status_color"] = "#00b4da"
                item["status_bg"] = "rgba(0, 180, 218, 0.18)"
                item["status_border"] = "1px solid rgba(0, 180, 218, 0.4)"
            elif status_val == "incorrect":
                item["status_color"] = "#FF8C00"
                item["status_bg"] = "rgba(255, 140, 0, 0.18)"
                item["status_border"] = "1px solid rgba(255, 140, 0, 0.4)"
            else:
                item["status_color"] = "#D0D0D5"
                item["status_bg"] = "rgba(255, 255, 255, 0.08)"
                item["status_border"] = "1px solid rgba(255, 255, 255, 0.15)"
            item["points_display"] = f"{p.get('points', 0)} pts"
            res.append(item)
        return res

    async def submit_prediction(self):
        username = self.current_user
        if not username:
            self.feedback_message = "Please log in with Discord first."
            return

        if self.is_locked:
            self.feedback_message = "Predictions are currently locked for this race."
            return

        rem = self.user_remaining_points
        if self.wager_amount > rem:
            self.feedback_message = f"Insufficient points. You only have {rem} points available."
            return

        proj = compute_season_projections(5)
        race_name = proj.get("next_main_race", proj.get("next_race", "Upcoming Race"))
        lines = proj.get("team_expected_lines", {})
        line_val = lines.get(self.selected_target, 0.0) if self.selected_category == "Expected Points" else None

        import time
        pred_id = int(time.time() * 1000)

        new_pred = {
            "id": pred_id,
            "username": username,
            "season": 5,
            "race": race_name,
            "category": self.selected_category,
            "target": self.selected_target,
            "line_value": line_val,
            "stance": self.selected_stance,
            "points": self.wager_amount,
            "status": "open",
            "payout": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        insert_prediction(new_pred)
        self.modal_open = False
        self.refresh_trigger += 1
        try:
            from the_alternative_f1.seasons.leaderboard import LeaderboardState
            lb_state = await self.get_state(LeaderboardState)
            lb_state.refresh()
        except Exception:
            pass

    async def delete_prediction(self, pred_id: str | int):
        username = self.current_user
        if not username or self.is_locked:
            return
        remove_prediction(pred_id, username)
        self.refresh_trigger += 1
        try:
            from the_alternative_f1.seasons.leaderboard import LeaderboardState
            lb_state = await self.get_state(LeaderboardState)
            lb_state.refresh()
        except Exception:
            pass


# ── UI Components ─────────────────────────────────────────────────────────────
def _submit_prediction_modal() -> rx.Component:
    """Modal dialog allowing selection of category, stance, and points wagered (SDDREQ-146)."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.dialog.title("Submit a Prediction", color="white", font_family="Outfit", font_weight="800", font_size="xl"),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button(rx.icon("x", size=18), variant="ghost", color="white", _hover={"bg": "#00b4da"}, cursor="pointer", padding="1", on_click=PredictionsMarketState.close_modal)
                    ),
                    width="100%",
                    align="center",
                ),
                rx.text(
                    "Select a projection category to wager for or against. Predictions lock 1 hour before race start.",
                    color="#8E8E93",
                    font_size="sm",
                ),
                # Category Dropdown
                rx.vstack(
                    rx.text("Stat Category", font_size="xs", color="#AAAAAA", font_weight="700"),
                    rx.select(
                        ["Expected Race Winner", "Highest Scoring Team", "Podium Teams", "Expected Points"],
                        value=PredictionsMarketState.selected_category,
                        on_change=PredictionsMarketState.set_category,
                        bg="#15151A",
                        color="white",
                        border="1px solid #2C2C32",
                        border_radius="md",
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),
                # Target Dropdown
                rx.vstack(
                    rx.text("Prediction Target", font_size="xs", color="#AAAAAA", font_weight="700"),
                    rx.select(
                        PredictionsMarketState.target_options,
                        value=PredictionsMarketState.selected_target,
                        on_change=PredictionsMarketState.set_target,
                        bg="#15151A",
                        color="white",
                        border="1px solid #2C2C32",
                        border_radius="md",
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),
                # Stance Selector (FOR/AGAINST or OVER/UNDER)
                rx.vstack(
                    rx.text("Your Stance", font_size="xs", color="#AAAAAA", font_weight="700"),
                    rx.cond(
                        PredictionsMarketState.selected_category == "Expected Points",
                        rx.segmented_control.root(
                            rx.segmented_control.item("OVER", value="OVER"),
                            rx.segmented_control.item("UNDER", value="UNDER"),
                            value=PredictionsMarketState.selected_stance,
                            on_change=PredictionsMarketState.set_stance,
                            radius="large",
                            size="2",
                            width="100%",
                        ),
                        rx.segmented_control.root(
                            rx.segmented_control.item("FOR", value="FOR"),
                            rx.segmented_control.item("AGAINST", value="AGAINST"),
                            value=PredictionsMarketState.selected_stance,
                            on_change=PredictionsMarketState.set_stance,
                            radius="large",
                            size="2",
                            width="100%",
                        ),
                    ),
                    spacing="1",
                    width="100%",
                ),
                # Points Input
                rx.vstack(
                    rx.hstack(
                        rx.text("Points to Wager", font_size="xs", color="#AAAAAA", font_weight="700"),
                        rx.spacer(),
                        rx.text(f"Available: {PredictionsMarketState.user_remaining_points} pts", font_size="xs", color="#00b4da", font_weight="700"),
                        width="100%",
                    ),
                    rx.input(
                        type="number",
                        value=PredictionsMarketState.wager_amount,
                        on_change=PredictionsMarketState.set_wager,
                        min=1,
                        max=PredictionsMarketState.user_remaining_points,
                        bg="#15151A",
                        color="white",
                        border="1px solid #2C2C32",
                        border_radius="md",
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),
                # Feedback message
                rx.cond(
                    PredictionsMarketState.feedback_message != "",
                    rx.text(PredictionsMarketState.feedback_message, color="#FF4B4B", font_size="xs", font_weight="600"),
                    rx.fragment(),
                ),
                # Submit Action Button
                rx.button(
                    "Confirm Prediction",
                    on_click=PredictionsMarketState.submit_prediction,
                    bg="#00b4da",
                    color="white",
                    font_weight="700",
                    _hover={"bg": "#009bbd"},
                    cursor="pointer",
                    width="100%",
                    margin_top="3",
                    height="40px",
                ),
                width="100%",
                spacing="3",
            ),
            bg="#18181C",
            border="1px solid #2C2C32",
            border_radius="xl",
            padding="5",
            max_width="480px",
            width="94vw",
        ),
        open=PredictionsMarketState.modal_open,
        on_open_change=lambda _: PredictionsMarketState.close_modal(),
    )


def predictions_market_tab_view() -> rx.Component:
    """Renders the Predictions Market Tab."""
    # Discord Login Banner if not logged in
    login_banner = rx.cond(
        PredictionsMarketState.current_user == "",
        rx.box(
            rx.hstack(
                rx.icon("log-in", size=20, color="#00b4da"),
                rx.vstack(
                    rx.text("Log in with Discord to place predictions", font_size="sm", font_weight="700", color="white"),
                    rx.text("All verified racers and fans automatically receive 100 Alternative Points to start wager pools!", font_size="xs", color="#A0A0AA"),
                    spacing="0",
                    align_items="start",
                ),
                rx.spacer(),
                rx.link(
                    rx.button(
                        rx.hstack(rx.icon("message-square", size=14), rx.text("Login with Discord")),
                        bg="#5865F2",
                        color="white",
                        font_weight="700",
                        font_size="xs",
                        _hover={"bg": "#4752C4"},
                        cursor="pointer",
                        padding_x="4",
                    ),
                    href=PredictionsMarketState.discord_auth_url,
                    is_external=True,
                    text_decoration="none",
                ),
                width="100%",
                align="center",
                spacing="3",
            ),
            bg="rgba(0, 180, 218, 0.08)",
            border="1px solid rgba(0, 180, 218, 0.25)",
            border_radius="xl",
            padding="14px 18px",
            margin_bottom="3",
            width="100%",
        ),
        rx.fragment(),
    )

    # Header Card: Real-time points balance & Submit button (SDDREQ-143 & SDDREQ-144)
    balance_and_action_card = rx.box(
        rx.hstack(
            # Points Balance
            rx.hstack(
                rx.icon("coins", size=24, color="#FFD700"),
                rx.vstack(
                    rx.text("Your Alternative Points", font_size="11px", color="#A0A0AA", font_weight="700", text_transform="uppercase"),
                    rx.text(f"{PredictionsMarketState.user_remaining_points} PTS", font_size=["20px", "24px"], font_weight="900", color="white", font_family="Outfit"),
                    spacing="0",
                    align_items="start",
                ),
                align="center",
                spacing="3",
            ),
            rx.spacer(),
            # Lockout Badge
            rx.badge(
                PredictionsMarketState.lockout_label,
                bg=rx.cond(PredictionsMarketState.is_locked, "rgba(255, 75, 75, 0.15)", "rgba(60, 180, 75, 0.15)"),
                color=rx.cond(PredictionsMarketState.is_locked, "#FF4B4B", "#3cb44b"),
                border="1px solid rgba(255,255,255,0.1)",
                font_size="12px",
                font_weight="700",
                padding_x="3",
                padding_y="1",
                border_radius="full",
            ),
            # Submit Prediction Button (SDDREQ-143: Blue button, visible if logged in and points > 0)
            rx.cond(
                (PredictionsMarketState.current_user != "") & (PredictionsMarketState.user_remaining_points > 0),
                rx.button(
                    rx.hstack(
                        rx.icon("circle-plus", size=16),
                        rx.text("Submit a Prediction", font_weight="700"),
                        spacing="2",
                        align="center",
                    ),
                    bg=rx.cond(PredictionsMarketState.is_locked, "#444444", "#00b4da"),
                    color="white",
                    _hover=rx.cond(PredictionsMarketState.is_locked, {}, {"bg": "#009bbd", "transform": "scale(1.02)"}),
                    cursor=rx.cond(PredictionsMarketState.is_locked, "not-allowed", "pointer"),
                    disabled=PredictionsMarketState.is_locked,
                    padding_x="4",
                    height="38px",
                    border_radius="lg",
                    on_click=PredictionsMarketState.open_modal,
                ),
                rx.fragment(),
            ),
            # Logout Button (visible when logged in)
            rx.cond(
                PredictionsMarketState.current_user != "",
                rx.button(
                    rx.hstack(
                        rx.icon("log-out", size=16),
                        rx.text("Logout", font_weight="700"),
                        spacing="2",
                        align="center",
                    ),
                    bg="#FF4B4B",
                    color="white",
                    _hover={"bg": "#E04040", "transform": "scale(1.02)"},
                    cursor="pointer",
                    padding_x="4",
                    height="38px",
                    border_radius="lg",
                    on_click=PredictionsMarketState.logout,
                ),
                rx.fragment(),
            ),
            width="100%",
            align="center",
            spacing="3",
            wrap="wrap",
        ),
        bg="#18181C",
        border="1px solid #2D2D35",
        border_radius="xl",
        padding="14px 18px",
        width="100%",
        box_shadow="0 6px 18px rgba(0,0,0,0.35)",
    )

    # Predictions Dashboard Table (SDDREQ-147)
    dashboard_table = rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("trending-up", size=16, color="#00b4da"),
                rx.text("Active Race Predictions Pool", font_size="13px", font_weight="800", color="white", letter_spacing="0.05em", text_transform="uppercase"),
                rx.spacer(),
                rx.text("Season 5", font_size="11px", color="#888888", font_weight="700"),
                width="100%",
                align="center",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("USER", color="#00b4da", font_size="10px", font_weight="800"),
                        rx.table.column_header_cell("CATEGORY", color="#00b4da", font_size="10px", font_weight="800"),
                        rx.table.column_header_cell("TARGET", color="#00b4da", font_size="10px", font_weight="800"),
                        rx.table.column_header_cell("STANCE", color="#00b4da", font_size="10px", font_weight="800"),
                        rx.table.column_header_cell("WAGER", color="#00b4da", font_size="10px", font_weight="800"),
                        rx.table.column_header_cell("STATUS", color="#00b4da", font_size="10px", font_weight="800"),
                        rx.table.column_header_cell("ACTION", color="#00b4da", font_size="10px", font_weight="800"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        PredictionsMarketState.all_predictions_list,
                        lambda p: rx.table.row(
                            rx.table.cell(
                                rx.hstack(
                                    rx.icon("user", size=12, color="#888"),
                                    rx.text(p["username"], color="white", font_weight="700", font_size="xs"),
                                    spacing="1",
                                    align="center",
                                )
                            ),
                            rx.table.cell(rx.text(p["category"], color="#CCCCCC", font_size="xs")),
                            rx.table.cell(
                                rx.hstack(
                                    rx.box(width="4px", height="16px", bg=p["team_color"], border_radius="full"),
                                    rx.text(p["target"], color="white", font_weight="600", font_size="xs"),
                                    spacing="2",
                                    align="center",
                                )
                            ),
                            rx.table.cell(
                                rx.badge(
                                    p["stance"],
                                    bg=rx.cond(p["is_positive"], "rgba(60, 180, 75, 0.2)", "rgba(255, 75, 75, 0.2)"),
                                    color=rx.cond(p["is_positive"], "#3cb44b", "#FF4B4B"),
                                    font_size="10px",
                                    font_weight="800",
                                )
                            ),
                            rx.table.cell(rx.text(p["points_display"], color="#FFD700", font_weight="700", font_size="xs")),
                            rx.table.cell(
                                rx.badge(
                                    p["status_upper"],
                                    bg=p["status_bg"],
                                    color=p["status_color"],
                                    border=p["status_border"],
                                    font_size="10px",
                                    font_weight="800",
                                    padding_x="2.5",
                                    padding_y="0.5",
                                    border_radius="md",
                                )
                            ),
                            rx.table.cell(
                                rx.cond(
                                    p["can_delete"],
                                    rx.button(
                                        rx.icon("trash-2", size=13),
                                        on_click=PredictionsMarketState.delete_prediction(p["id"]),
                                        variant="ghost",
                                        color="#FF4B4B",
                                        _hover={"bg": "rgba(255, 75, 75, 0.15)"},
                                        cursor="pointer",
                                        padding="1",
                                        title="Delete Prediction (Refund Points)",
                                    ),
                                    rx.text("—", color="#555555", font_size="xs"),
                                )
                            ),
                            _hover={"bg": "#1C1C22"},
                        )
                    )
                ),
                variant="ghost",
                width="100%",
            ),
            width="100%",
            spacing="3",
        ),
        bg="#18181C",
        border="1px solid #2D2D35",
        border_radius="xl",
        padding="14px 18px",
        width="100%",
        box_shadow="0 6px 18px rgba(0,0,0,0.35)",
        overflow_x="auto",
    )

    warning_banner = rx.box(
        rx.hstack(
            rx.icon("triangle-alert", size=20, color="#FF8C00", flex_shrink="0"),
            rx.text(
                "Alternative Points hold no monetary value. Wagers are purely for entertainment purposes.",
                font_size=["12px", "13px"],
                font_weight="700",
                color="#FFFFFF",
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        bg="rgba(255, 140, 0, 0.12)",
        border="1px solid rgba(255, 140, 0, 0.35)",
        border_radius="xl",
        padding="12px 18px",
        width="100%",
        margin_bottom="2",
    )

    return rx.vstack(
        warning_banner,
        rx.heading(
            "Predictions Market",
            size="6",
            color="white",
            font_family="Outfit",
            margin_bottom="2",
        ),
        login_banner,
        balance_and_action_card,
        dashboard_table,
        _submit_prediction_modal(),
        width="100%",
        spacing="3",
        align_items="start",
    )
