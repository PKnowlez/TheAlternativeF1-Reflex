"""Predictions Market Tab — Reflex Component & State Management.
Implements TAF1APP-SDDFEAT-16 and approved downstream SDD requirements:
- SDDREQ-142: Alternative Points Per User (100 points upon first visit/login, recorded in Supabase / fallback)
- SDDREQ-143: Submit a Prediction Button (blue button, visible when logged in and points > 0)
- SDDREQ-144: Display Remaining Alternative Points (real-time balance after active wagers)
- SDDREQ-145: Delete Prediction (only user's own predictions, prior to 1-hour pre-race lockout with days+hours countdown)
- SDDREQ-146: Prediction Options (One stat category per submission; multiple submissions allowed)
- SDDREQ-147: Predictions Dashboard (themed display of all submissions for the race)
- SDDREQ-148: Correct Predictions (wager + 15% + split of opposing pool)
- SDDREQ-149: Incorrect Predictions (0 returned)
- SDDREQ-150: Prediction Finalization (auto-settles upon race upload; grace for revisions)
- SDDREQ-151: Previous Lines storage (.json storage)
- SDDREQ-155: Active Race Predictions Pool - Expander (summary of count & total wagered points when collapsed)
- SDDREQ-156: Prediction Target (all active constructors in target dropdown selector)
- SDDREQ-157: Full List Popouts (interactive popouts for Expected Winner, Highest Scoring Team, and Expected Podium)
- SDDREQ-158: Additional Stat Categories (Fastest Lap, Driver of the Day, Most Overtakes, Cleanest Driver)
- SDDREQ-159: Display Current Predictions - Expected Points (Interactive donut chart: outer teams, inner Over/Under)
- SDDREQ-160: Display Current Predictions - Expected Winner (Interactive donut chart: outer teams, inner For/Against)
- SDDREQ-161: Display Current Predictions - Expected Podium (Interactive donut chart: outer teams, inner For/Against)
- SDDREQ-162: Display Current Predictions - Highest Scoring Team (Interactive donut chart: outer teams, inner For/Against)
- SDDREQ-163: User Predictions Metric (Interactive donut chart: outer users, inner positive/negative split)
- SDDREQ-164: Predictions Tab Layout (Ordered top-to-bottom layout)
- SDDREQ-168: User Account Consistency (persistent account ID across display name changes)
"""

import os
import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pandas as pd
import reflex as rx

from the_alternative_f1.all_time_stats.Functions import get_excel_sheet
from the_alternative_f1.all_time_stats.DetailedAllTime import _extract_track_name
from the_alternative_f1.seasons.projections import compute_season_projections
from the_alternative_f1.constructor_colors import get_constructor_color
from the_alternative_f1.articles.components import (
    chart_download_button,
    chart_card,
    zoomable_chart,
)

USER_POINTS_JSON = Path(__file__).parent / "user_points.json"
PREDICTIONS_JSON = Path(__file__).parent / "predictions.json"


def _get_supabase():
    """Lazy-load Supabase client if available."""
    try:
        from the_alternative_f1.the_alternative_f1 import get_supabase_client
        return get_supabase_client()
    except Exception:
        return None


# ── Account Normalization & Aliases (SDDREQ-168) ──────────────────────────────
ACCOUNT_ALIASES = {
    "matthew newman": "Jatthew Newman",
}


def normalize_username(username: str) -> str:
    """Canonicalizes usernames to handle display name changes across the app."""
    if not username:
        return ""
    clean = str(username).strip()
    return ACCOUNT_ALIASES.get(clean.lower(), clean)


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


# ── Lockout Calculation (1 Hour Pre-Race; Days + Hours Display) ───────────────
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
        dt_race = None
        for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%B %d, %Y"):
            try:
                dt_race = datetime.strptime(date_val, fmt)
                break
            except Exception:
                continue

        if not dt_race:
            return (False, "Open")

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


# ── Points Management (SDDREQ-142, SDDREQ-144, SDDREQ-168) ───────────────────
def get_user_total_points(username: str) -> int:
    """Fetches user points, initializing to 100 if user does not exist yet."""
    username = normalize_username(username)
    if not username:
        return 0

    local_data = _load_local_user_points()
    # Purge any obsolete names from local cache
    dirty = False
    for k in list(local_data.keys()):
        if k == "Matthew Newman" or normalize_username(k) != k:
            del local_data[k]
            dirty = True
    if dirty:
        _save_local_user_points(local_data)

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


def get_user_remaining_points(username: str, season_num: int = 5) -> int:
    """Calculates user's remaining available points after deducting active open wagers (SDDREQ-153)."""
    username = normalize_username(username)
    if not username:
        return 0
    total = get_user_total_points(username)
    all_preds = get_all_predictions(season_num)
    active_wagers = sum(
        int(p.get("points", 0))
        for p in all_preds
        if normalize_username(str(p.get("username", ""))) == username and str(p.get("status", "open")).lower() == "open"
    )
    return max(0, total - active_wagers)


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
    """Auto-settles open predictions when race results are uploaded in the Season sheet."""
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

            valid_pts = pd.to_numeric(df_season[p_col], errors="coerce").fillna(0)
            if not (valid_pts > 0).any():
                continue

            sprint_name = None
            for r in all_races:
                if "sprint" in r.lower() and _extract_track_name(r).lower() == _extract_track_name(main_race).lower():
                    sprint_name = r
                    break

            sprint_p_col = f"{sprint_name}Points" if sprint_name else None

            teams = sorted(df_season["Team"].dropna().unique())
            team_weekend_pts = {}
            for t in teams:
                t_df = df_season[df_season["Team"] == t]
                main_pts = float(pd.to_numeric(t_df[p_col], errors="coerce").fillna(0).sum())
                sprint_pts = float(pd.to_numeric(t_df[sprint_p_col], errors="coerce").fillna(0).sum()) if sprint_p_col and sprint_p_col in df_season.columns else 0.0
                team_weekend_pts[t] = main_pts + sprint_pts

            winner_team = None
            place_col = f"{main_race}Place"
            if place_col in df_season.columns:
                p1_df = df_season[pd.to_numeric(df_season[place_col], errors="coerce") == 1]
                if not p1_df.empty:
                    winner_team = str(p1_df.iloc[0]["Team"]).strip()

            highest_team = max(team_weekend_pts.keys(), key=lambda t: team_weekend_pts[t]) if team_weekend_pts else None
            sorted_teams_by_pts = sorted(teams, key=lambda t: team_weekend_pts.get(t, 0), reverse=True)
            podium_teams = sorted_teams_by_pts[:3]

            # Fastest Lap team (either driver)
            fl_col = f"{main_race}FL" if f"{main_race}FL" in df_season.columns else (f"{main_race}FastestLap" if f"{main_race}FastestLap" in df_season.columns else None)
            fl_team = None
            if fl_col:
                fl_df = df_season[df_season[fl_col].astype(str).str.strip().isin(["1", "Yes", "Y", "True"])]
                if not fl_df.empty:
                    fl_team = str(fl_df.iloc[0]["Team"]).strip()

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
                    elif cat == "Fastest Lap" and fl_team:
                        matched = (fl_team == target)
                        is_correct = (matched if "FOR" in stance else not matched)

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
                for p in combined:
                    p["username"] = normalize_username(p.get("username", ""))
                return combined
        except Exception as e:
            print(f"Supabase get_all_predictions error: {e}")
    local_preds = _load_local_predictions()
    res_list = [p for p in local_preds if int(p.get("season", 5)) == season_num]
    for p in res_list:
        p["username"] = normalize_username(p.get("username", ""))
    return res_list


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


# ── SVG Arc & Donut Helpers (Aligned with All-Time & Season Donut Charts) ────
def _build_arc_path(cx: float, cy: float, r_in: float, r_out: float, start_deg: float, end_deg: float) -> str:
    """Generate SVG path string for a donut arc segment."""
    span = end_deg - start_deg
    if span >= 359.99:
        span = 359.99

    rad1 = math.radians(start_deg)
    rad2 = math.radians(start_deg + span)

    x_out1 = cx + r_out * math.cos(rad1)
    y_out1 = cy + r_out * math.sin(rad1)
    x_out2 = cx + r_out * math.cos(rad2)
    y_out2 = cy + r_out * math.sin(rad2)

    x_in1 = cx + r_in * math.cos(rad1)
    y_in1 = cy + r_in * math.sin(rad1)
    x_in2 = cx + r_in * math.cos(rad2)
    y_in2 = cy + r_in * math.sin(rad2)

    large_arc = 1 if span > 180.0 else 0

    return (
        f"M {x_out1:.2f} {y_out1:.2f} "
        f"A {r_out:.2f} {r_out:.2f} 0 {large_arc} 1 {x_out2:.2f} {y_out2:.2f} "
        f"L {x_in2:.2f} {y_in2:.2f} "
        f"A {r_in:.2f} {r_in:.2f} 0 {large_arc} 0 {x_in1:.2f} {y_in1:.2f} Z"
    )


def build_category_donut_svg(
    category_name: str,
    cat_preds: list[dict],
    svg_id: str,
    default_type: str,
) -> str:
    """Build high-precision interactive two-ring SVG donut chart for category wagers (SDDREQ-159 to SDDREQ-162)."""
    cx, cy = 260.0, 260.0
    r_out_in, r_out_out = 174.0, 242.0
    r_in_in, r_in_out = 104.0, 170.0

    total_pts = sum(int(p.get("points", 0)) for p in cat_preds)

    if total_pts <= 0:
        empty_path = _build_arc_path(cx, cy, r_out_in, r_out_out, 0, 359.99)
        inner_empty = _build_arc_path(cx, cy, r_in_in, r_in_out, 0, 359.99)
        return f"""
        <svg id="{svg_id}" class="donut-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 520" width="100%" height="100%"
             data-default-points="0 PTS"
             data-default-type="{default_type.upper()}"
             data-default-meta="OPEN POOL"
             style="display: block; max-width: 440px; max-height: 440px; margin: 0 auto; user-select: none;"
             onclick="window.taf1DonutBgClick && window.taf1DonutBgClick(event)">
            <defs>
                <filter id="donut-shadow-{svg_id}" x="-10%" y="-10%" width="120%" height="120%">
                    <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.5"/>
                </filter>
            </defs>
            <g filter="url(#donut-shadow-{svg_id})">
                <path class="donut-slice" d="{empty_path}" fill="#22222A" stroke="#15151A" stroke-width="2" />
                <path class="donut-slice" d="{inner_empty}" fill="#1B1B22" stroke="#15151A" stroke-width="1.8" />
            </g>
            <circle class="donut-center-hole" cx="{cx}" cy="{cy}" r="98"
                    fill="#15151A" stroke="rgba(255,255,255,0.08)" stroke-width="1.5"
                    style="cursor: pointer;"
                    onclick="window.taf1DonutReset && window.taf1DonutReset(event)" />
            <g class="donut-svg-center-group" pointer-events="none" text-anchor="middle" font-family="'Outfit', sans-serif" style="user-select: none;">
                <text class="donut-center-type" x="{cx}" y="230" dominant-baseline="middle"
                      fill="#8E8E93" font-size="11" font-weight="700" letter-spacing="1">{default_type.upper()}</text>
                <text class="donut-center-value" x="{cx}" y="260" dominant-baseline="middle"
                      fill="#FFFFFF" font-size="22" font-weight="900">0 PTS</text>
                <text class="donut-center-meta" x="{cx}" y="285" dominant-baseline="middle"
                      fill="#00b4da" font-size="10.5" font-weight="700" letter-spacing="0.5">OPEN POOL</text>
            </g>
        </svg>
        """

    teams = {}
    for p in cat_preds:
        t = str(p.get("target", "Unknown"))
        pts = int(p.get("points", 0))
        stance = str(p.get("stance", "")).upper()
        if t not in teams:
            teams[t] = {"total": 0, "pos": 0, "neg": 0}
        teams[t]["total"] += pts
        if "FOR" in stance or "OVER" in stance:
            teams[t]["pos"] += pts
        else:
            teams[t]["neg"] += pts

    sorted_teams = sorted(teams.items(), key=lambda x: -x[1]["total"])

    curr_angle = -90.0  # 12 o'clock
    outer_paths = []
    inner_paths = []

    pos_label = "Over" if category_name == "Expected Points" else "For"
    neg_label = "Under" if category_name == "Expected Points" else "Against"

    for team, data in sorted_teams:
        c_pts = data["total"]
        if c_pts <= 0:
            continue
        c_angle_span = (c_pts / total_pts) * 360.0
        c_start_angle = curr_angle
        c_end_angle = curr_angle + c_angle_span
        c_pct = (c_pts / total_pts) * 100.0
        c_color = get_constructor_color(team)

        c_path_d = _build_arc_path(cx, cy, r_out_in, r_out_out, c_start_angle, c_end_angle)
        outer_paths.append(f"""
        <path class="donut-slice donut-constructor" d="{c_path_d}" fill="{c_color}" stroke="#15151A" stroke-width="2"
              style="cursor: pointer; transition: opacity 0.15s ease;"
              data-type="Constructor"
              data-name="{team}"
              data-pts="{c_pts:,.0f}"
              data-meta="{c_pct:.1f}% of Pool"
              onmouseenter="window.taf1DonutEnter && window.taf1DonutEnter(this)"
              onmouseleave="window.taf1DonutLeave && window.taf1DonutLeave(this)"
              onclick="window.taf1DonutClick && window.taf1DonutClick(this, event)">
            <title>{team}: {c_pts:,.0f} pts ({c_pct:.1f}% of Pool)</title>
        </path>
        """)

        pos_pts = data["pos"]
        neg_pts = data["neg"]

        curr_stance_angle = c_start_angle
        if pos_pts > 0:
            pos_span = c_angle_span * (pos_pts / c_pts)
            pos_end = curr_stance_angle + pos_span
            pos_pct = (pos_pts / c_pts) * 100.0
            pos_path_d = _build_arc_path(cx, cy, r_in_in, r_in_out, curr_stance_angle, pos_end)
            inner_paths.append(f"""
            <path class="donut-slice donut-driver" d="{pos_path_d}" fill="#3cb44b" stroke="#15151A" stroke-width="1.8"
                  style="cursor: pointer; transition: opacity 0.15s ease;"
                  data-type="Stance"
                  data-name="{team} ({pos_label})"
                  data-pts="{pos_pts:,.0f}"
                  data-meta="{team} • {pos_pct:.1f}% of Team"
                  onmouseenter="window.taf1DonutEnter && window.taf1DonutEnter(this)"
                  onmouseleave="window.taf1DonutLeave && window.taf1DonutLeave(this)"
                  onclick="window.taf1DonutClick && window.taf1DonutClick(this, event)">
                <title>{team} ({pos_label}): {pos_pts:,.0f} pts ({pos_pct:.1f}%)</title>
            </path>
            """)
            curr_stance_angle = pos_end

        if neg_pts > 0:
            neg_span = c_angle_span * (neg_pts / c_pts)
            neg_end = curr_stance_angle + neg_span
            neg_pct = (neg_pts / c_pts) * 100.0
            neg_path_d = _build_arc_path(cx, cy, r_in_in, r_in_out, curr_stance_angle, neg_end)
            inner_paths.append(f"""
            <path class="donut-slice donut-driver" d="{neg_path_d}" fill="#FF4B4B" stroke="#15151A" stroke-width="1.8"
                  style="cursor: pointer; transition: opacity 0.15s ease;"
                  data-type="Stance"
                  data-name="{team} ({neg_label})"
                  data-pts="{neg_pts:,.0f}"
                  data-meta="{team} • {neg_pct:.1f}% of Team"
                  onmouseenter="window.taf1DonutEnter && window.taf1DonutEnter(this)"
                  onmouseleave="window.taf1DonutLeave && window.taf1DonutLeave(this)"
                  onclick="window.taf1DonutClick && window.taf1DonutClick(this, event)">
                <title>{team} ({neg_label}): {neg_pts:,.0f} pts ({neg_pct:.1f}%)</title>
            </path>
            """)

        curr_angle = c_end_angle

    return f"""
    <svg id="{svg_id}" class="donut-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 520" width="100%" height="100%"
         data-default-points="{total_pts:,.0f} PTS"
         data-default-type="{default_type.upper()}"
         data-default-meta="TOTAL WAGERED"
         style="display: block; max-width: 440px; max-height: 440px; margin: 0 auto; user-select: none;"
         onclick="window.taf1DonutBgClick && window.taf1DonutBgClick(event)">
        <defs>
            <filter id="donut-shadow-{svg_id}" x="-10%" y="-10%" width="120%" height="120%">
                <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.5"/>
            </filter>
        </defs>

        <!-- Outer Ring: Constructors -->
        <g id="donut-outer-ring-{svg_id}" filter="url(#donut-shadow-{svg_id})">
            {''.join(outer_paths)}
        </g>

        <!-- Inner Ring: Stance Split -->
        <g id="donut-inner-ring-{svg_id}" filter="url(#donut-shadow-{svg_id})">
            {''.join(inner_paths)}
        </g>

        <!-- Donut center hole (clickable to reset) -->
        <circle id="donut-center-hole-{svg_id}" class="donut-center-hole" cx="{cx}" cy="{cy}" r="98"
                fill="#15151A" stroke="rgba(255,255,255,0.08)" stroke-width="1.5"
                style="cursor: pointer;"
                onclick="window.taf1DonutReset && window.taf1DonutReset(event)" />

        <!-- Center Information Display -->
        <g class="donut-svg-center-group" pointer-events="none" text-anchor="middle" font-family="'Outfit', sans-serif" style="user-select: none;">
            <text class="donut-center-type" x="{cx}" y="230" dominant-baseline="middle"
                  fill="#8E8E93" font-size="11" font-weight="700" letter-spacing="1">{default_type.upper()}</text>
            <text class="donut-center-value" x="{cx}" y="260" dominant-baseline="middle"
                  fill="#FFFFFF" font-size="24" font-weight="900">{total_pts:,.0f} PTS</text>
            <text class="donut-center-meta" x="{cx}" y="285" dominant-baseline="middle"
                  fill="#00b4da" font-size="10.5" font-weight="700" letter-spacing="0.5">TOTAL WAGERED</text>
        </g>
    </svg>
    """


def build_user_metrics_donut_svg(preds: list[dict], svg_id: str = "user-metrics-donut-svg") -> str:
    """Build high-precision interactive two-ring SVG donut chart for user prediction metrics (SDDREQ-163)."""
    cx, cy = 260.0, 260.0
    r_out_in, r_out_out = 174.0, 242.0
    r_in_in, r_in_out = 104.0, 170.0

    total_pts = sum(int(p.get("points", 0)) for p in preds)

    if total_pts <= 0:
        empty_path = _build_arc_path(cx, cy, r_out_in, r_out_out, 0, 359.99)
        inner_empty = _build_arc_path(cx, cy, r_in_in, r_in_out, 0, 359.99)
        return f"""
        <svg id="{svg_id}" class="donut-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 520" width="100%" height="100%"
             data-default-points="0 PTS"
             data-default-type="PREDICTOR METRIC"
             data-default-meta="TOTAL WAGERED"
             style="display: block; max-width: 440px; max-height: 440px; margin: 0 auto; user-select: none;"
             onclick="window.taf1DonutBgClick && window.taf1DonutBgClick(event)">
            <defs>
                <filter id="donut-shadow-{svg_id}" x="-10%" y="-10%" width="120%" height="120%">
                    <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.5"/>
                </filter>
            </defs>
            <g filter="url(#donut-shadow-{svg_id})">
                <path class="donut-slice" d="{empty_path}" fill="#22222A" stroke="#15151A" stroke-width="2" />
                <path class="donut-slice" d="{inner_empty}" fill="#1B1B22" stroke="#15151A" stroke-width="1.8" />
            </g>
            <circle class="donut-center-hole" cx="{cx}" cy="{cy}" r="98"
                    fill="#15151A" stroke="rgba(255,255,255,0.08)" stroke-width="1.5"
                    style="cursor: pointer;"
                    onclick="window.taf1DonutReset && window.taf1DonutReset(event)" />
            <g class="donut-svg-center-group" pointer-events="none" text-anchor="middle" font-family="'Outfit', sans-serif" style="user-select: none;">
                <text class="donut-center-type" x="{cx}" y="230" dominant-baseline="middle"
                      fill="#8E8E93" font-size="11" font-weight="700" letter-spacing="1">PREDICTOR METRIC</text>
                <text class="donut-center-value" x="{cx}" y="260" dominant-baseline="middle"
                      fill="#FFFFFF" font-size="22" font-weight="900">0 PTS</text>
                <text class="donut-center-meta" x="{cx}" y="285" dominant-baseline="middle"
                      fill="#00b4da" font-size="10.5" font-weight="700" letter-spacing="0.5">TOTAL WAGERED</text>
            </g>
        </svg>
        """

    palette = ["#00b4da", "#FFD700", "#FF4B4B", "#9B59B6", "#1ABC9C", "#E67E22", "#3498DB", "#2ECC71"]

    users = {}
    for p in preds:
        u = str(p.get("username", "Unknown"))
        pts = int(p.get("points", 0))
        stance = str(p.get("stance", "")).upper()
        if u not in users:
            users[u] = {"total": 0, "pos": 0, "neg": 0}
        users[u]["total"] += pts
        if "FOR" in stance or "OVER" in stance:
            users[u]["pos"] += pts
        else:
            users[u]["neg"] += pts

    sorted_users = sorted(users.items(), key=lambda x: -x[1]["total"])

    curr_angle = -90.0
    outer_paths = []
    inner_paths = []

    for idx, (u, data) in enumerate(sorted_users):
        u_pts = data["total"]
        if u_pts <= 0:
            continue
        u_angle_span = (u_pts / total_pts) * 360.0
        u_start_angle = curr_angle
        u_end_angle = curr_angle + u_angle_span
        u_pct = (u_pts / total_pts) * 100.0
        u_color = palette[idx % len(palette)]

        u_path_d = _build_arc_path(cx, cy, r_out_in, r_out_out, u_start_angle, u_end_angle)
        outer_paths.append(f"""
        <path class="donut-slice donut-constructor" d="{u_path_d}" fill="{u_color}" stroke="#15151A" stroke-width="2"
              style="cursor: pointer; transition: opacity 0.15s ease;"
              data-type="Predictor"
              data-name="{u}"
              data-pts="{u_pts:,.0f}"
              data-meta="{u_pct:.1f}% of Total"
              onmouseenter="window.taf1DonutEnter && window.taf1DonutEnter(this)"
              onmouseleave="window.taf1DonutLeave && window.taf1DonutLeave(this)"
              onclick="window.taf1DonutClick && window.taf1DonutClick(this, event)">
            <title>{u}: {u_pts:,.0f} pts ({u_pct:.1f}% of Total)</title>
        </path>
        """)

        pos_pts = data["pos"]
        neg_pts = data["neg"]

        curr_stance_angle = u_start_angle
        if pos_pts > 0:
            pos_span = u_angle_span * (pos_pts / u_pts)
            pos_end = curr_stance_angle + pos_span
            pos_pct = (pos_pts / u_pts) * 100.0
            pos_path_d = _build_arc_path(cx, cy, r_in_in, r_in_out, curr_stance_angle, pos_end)
            inner_paths.append(f"""
            <path class="donut-slice donut-driver" d="{pos_path_d}" fill="#3cb44b" stroke="#15151A" stroke-width="1.8"
                  style="cursor: pointer; transition: opacity 0.15s ease;"
                  data-type="Stance"
                  data-name="{u} (Positive)"
                  data-pts="{pos_pts:,.0f}"
                  data-meta="{u} • {pos_pct:.1f}% For/Over"
                  onmouseenter="window.taf1DonutEnter && window.taf1DonutEnter(this)"
                  onmouseleave="window.taf1DonutLeave && window.taf1DonutLeave(this)"
                  onclick="window.taf1DonutClick && window.taf1DonutClick(this, event)">
                <title>{u} (Positive): {pos_pts:,.0f} pts ({pos_pct:.1f}%)</title>
            </path>
            """)
            curr_stance_angle = pos_end

        if neg_pts > 0:
            neg_span = u_angle_span * (neg_pts / u_pts)
            neg_end = curr_stance_angle + neg_span
            neg_pct = (neg_pts / u_pts) * 100.0
            neg_path_d = _build_arc_path(cx, cy, r_in_in, r_in_out, curr_stance_angle, neg_end)
            inner_paths.append(f"""
            <path class="donut-slice donut-driver" d="{neg_path_d}" fill="#FF4B4B" stroke="#15151A" stroke-width="1.8"
                  style="cursor: pointer; transition: opacity 0.15s ease;"
                  data-type="Stance"
                  data-name="{u} (Negative)"
                  data-pts="{neg_pts:,.0f}"
                  data-meta="{u} • {neg_pct:.1f}% Against/Under"
                  onmouseenter="window.taf1DonutEnter && window.taf1DonutEnter(this)"
                  onmouseleave="window.taf1DonutLeave && window.taf1DonutLeave(this)"
                  onclick="window.taf1DonutClick && window.taf1DonutClick(this, event)">
                <title>{u} (Negative): {neg_pts:,.0f} pts ({neg_pct:.1f}%)</title>
            </path>
            """)

        curr_angle = u_end_angle

    return f"""
    <svg id="{svg_id}" class="donut-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 520" width="100%" height="100%"
         data-default-points="{total_pts:,.0f} PTS"
         data-default-type="PREDICTOR METRIC"
         data-default-meta="TOTAL WAGERED"
         style="display: block; max-width: 440px; max-height: 440px; margin: 0 auto; user-select: none;"
         onclick="window.taf1DonutBgClick && window.taf1DonutBgClick(event)">
        <defs>
            <filter id="donut-shadow-{svg_id}" x="-10%" y="-10%" width="120%" height="120%">
                <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.5"/>
            </filter>
        </defs>

        <!-- Outer Ring: Users -->
        <g id="donut-outer-ring-{svg_id}" filter="url(#donut-shadow-{svg_id})">
            {''.join(outer_paths)}
        </g>

        <!-- Inner Ring: Positive / Negative Stance Breakdown -->
        <g id="donut-inner-ring-{svg_id}" filter="url(#donut-shadow-{svg_id})">
            {''.join(inner_paths)}
        </g>

        <!-- Donut center hole (clickable to reset) -->
        <circle id="donut-center-hole-{svg_id}" class="donut-center-hole" cx="{cx}" cy="{cy}" r="98"
                fill="#15151A" stroke="rgba(255,255,255,0.08)" stroke-width="1.5"
                style="cursor: pointer;"
                onclick="window.taf1DonutReset && window.taf1DonutReset(event)" />

        <!-- Center Information Display -->
        <g class="donut-svg-center-group" pointer-events="none" text-anchor="middle" font-family="'Outfit', sans-serif" style="user-select: none;">
            <text class="donut-center-type" x="{cx}" y="230" dominant-baseline="middle"
                  fill="#8E8E93" font-size="11" font-weight="700" letter-spacing="1">PREDICTOR METRIC</text>
            <text class="donut-center-value" x="{cx}" y="260" dominant-baseline="middle"
                  fill="#FFFFFF" font-size="24" font-weight="900">{total_pts:,.0f} PTS</text>
            <text class="donut-center-meta" x="{cx}" y="285" dominant-baseline="middle"
                  fill="#00b4da" font-size="10.5" font-weight="700" letter-spacing="0.5">TOTAL WAGERED</text>
        </g>
    </svg>
    """


@rx.memo
def memoized_market_donut_chart(*, html_content: rx.Var[str]) -> rx.Component:
    """Memoized SVG container preventing React re-renders from ticker loops or unrelated state."""
    return rx.box(
        rx.html(html_content),
        width="100%",
        max_width="440px",
        margin="0 auto",
    )


# ── Reflex State ─────────────────────────────────────────────────────────────
class PredictionsMarketState(rx.State):
    """Reflex state for the Predictions Market Tab."""
    discord_username: str = rx.LocalStorage("", name="discord_username", sync=True)
    discord_id: str = rx.LocalStorage("", name="discord_id", sync=True)
    discord_handle: str = rx.LocalStorage("", name="discord_handle", sync=True)
    refresh_trigger: int = 0

    # Submit Prediction Modal state
    modal_open: bool = False
    selected_category: str = "Expected Race Winner"
    selected_target: str = ""
    selected_stance: str = "FOR"
    wager_amount: int = 10
    feedback_message: str = ""

    # Pool expander state (SDDREQ-155)
    pool_expander_open: bool = True
    table_filters: list[str] = []

    def toggle_pool_expander(self):
        self.pool_expander_open = not self.pool_expander_open

    def toggle_table_filter(self, filter_name: str):
        if filter_name in self.table_filters:
            self.table_filters = [f for f in self.table_filters if f != filter_name]
        else:
            self.table_filters = self.table_filters + [filter_name]

    def clear_table_filters(self):
        self.table_filters = []

    def sync_account(self):
        """Maintains user account consistency across Discord display name changes (SDDREQ-168)."""
        sb = _get_supabase()
        display_name = self.discord_username.strip()
        user_id = self.discord_id.strip()
        handle = self.discord_handle.strip()

        if not display_name:
            return

        old_names_to_clean = set()

        if sb:
            try:
                # 1. Search for existing account by discord_id first if available
                res = None
                if user_id:
                    res = sb.table("user_prediction_points").select("*").eq("discord_id", user_id).execute()
                # 2. Fallback to username matching display_name or handle
                if not (res and res.data):
                    res = sb.table("user_prediction_points").select("*").eq("username", display_name).execute()
                if not (res and res.data) and handle:
                    res = sb.table("user_prediction_points").select("*").eq("username", handle).execute()

                if res and res.data and len(res.data) > 0:
                    for row in res.data:
                        prev_uname = row.get("username")
                        prev_dname = row.get("display_name")
                        if prev_uname and prev_uname != display_name:
                            old_names_to_clean.add(prev_uname)
                        if prev_dname and prev_dname != display_name:
                            old_names_to_clean.add(prev_dname)

                    target_row = res.data[0]
                    target_pts = int(target_row.get("points", 100))
                    target_all_time = int(target_row.get("all_time_points", 100))

                    # Consolidate and delete any obsolete duplicate rows in user_prediction_points
                    for old_name in old_names_to_clean:
                        sb.table("predictions").update({"username": display_name}).eq("username", old_name).execute()
                        sb.table("user_prediction_points").delete().eq("username", old_name).execute()

                    # Upsert unified row for current display_name
                    sb.table("user_prediction_points").upsert({
                        "username": display_name,
                        "display_name": display_name,
                        "discord_id": user_id if user_id else None,
                        "points": target_pts,
                        "all_time_points": target_all_time,
                        "season_points": {"5": target_pts},
                    }, on_conflict="username").execute()
                else:
                    # New user: create record with 100 points
                    payload = {
                        "username": display_name,
                        "display_name": display_name,
                        "discord_id": user_id if user_id else None,
                        "points": 100,
                        "all_time_points": 100,
                        "season_points": {"5": 100},
                    }
                    sb.table("user_prediction_points").insert(payload).execute()
            except Exception as e:
                print(f"Error syncing account in Supabase: {e}")

        # Update local file cache & purge any old names
        local_pts = _load_local_user_points()
        for old_name in old_names_to_clean:
            if old_name in local_pts and old_name != display_name:
                del local_pts[old_name]

        if display_name not in local_pts:
            local_pts[display_name] = {
                "points": 100,
                "all_time_points": 100,
                "season_points": {"5": 100},
            }
        _save_local_user_points(local_pts)

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

    async def logout(self):
        self.discord_username = ""
        self.discord_id = ""
        self.discord_handle = ""
        try:
            from the_alternative_f1.the_alternative_f1 import State
            main_state = await self.get_state(State)
            main_state.discord_username = ""
            main_state.discord_avatar = ""
            main_state.discord_id = ""
            main_state.discord_handle = ""
        except Exception:
            pass

    def open_modal(self):
        self.modal_open = True
        self.feedback_message = ""
        self.wager_amount = 10
        self.selected_category = "Expected Race Winner"
        self.selected_stance = "FOR"
        proj = compute_season_projections(5)
        teams = sorted(proj.get("teams", []))
        self.selected_target = proj.get("expected_winner", teams[0] if teams else "")

    def close_modal(self):
        self.modal_open = False
        self.feedback_message = ""

    def set_category(self, cat: str):
        self.selected_category = cat
        proj = compute_season_projections(5)
        teams = sorted(proj.get("teams", []))
        if cat == "Expected Race Winner":
            self.selected_target = proj.get("expected_winner", teams[0] if teams else "")
            self.selected_stance = "FOR"
        elif cat == "Highest Scoring Team":
            self.selected_target = proj.get("expected_highest_score_team", teams[0] if teams else "")
            self.selected_stance = "FOR"
        elif cat == "Podium Teams":
            podiums = proj.get("expected_podium", [])
            self.selected_target = podiums[0] if podiums else (teams[0] if teams else "")
            self.selected_stance = "FOR"
        elif cat == "Expected Points":
            self.selected_target = teams[0] if teams else ""
            self.selected_stance = "OVER"
        else:
            # Additional stat categories (Fastest Lap, Driver of the Day, Most Overtakes, Cleanest Driver)
            self.selected_target = teams[0] if teams else ""
            self.selected_stance = "FOR"

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
    def category_options(self) -> list[str]:
        return [
            "Expected Race Winner",
            "Highest Scoring Team",
            "Podium Teams",
            "Expected Points",
            "Fastest Lap",
            "Driver of the Day",
            "Most Overtakes",
            "Cleanest Driver",
        ]

    @rx.var
    def target_options(self) -> list[str]:
        """All prediction targets are active constructors (SDDREQ-156)."""
        proj = compute_season_projections(5)
        return sorted(proj.get("teams", []))

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
        return get_user_remaining_points(username, 5)

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

    @rx.var
    def filtered_predictions_list(self) -> list[dict]:
        all_preds = self.all_predictions_list
        if not self.table_filters:
            return all_preds

        selected_stances = [f for f in self.table_filters if f in ["For / Over", "Against / Under"]]
        selected_statuses = [f for f in self.table_filters if f in ["Correct", "Incorrect", "Open"]]

        filtered = []
        for p in all_preds:
            if selected_stances:
                is_pos = bool(p.get("is_positive", False))
                stance_match = False
                if "For / Over" in selected_stances and is_pos:
                    stance_match = True
                if "Against / Under" in selected_stances and not is_pos:
                    stance_match = True
                if not stance_match:
                    continue

            if selected_statuses:
                status_val = str(p.get("status", "open")).lower()
                status_match = False
                if "Correct" in selected_statuses and status_val == "correct":
                    status_match = True
                if "Incorrect" in selected_statuses and status_val == "incorrect":
                    status_match = True
                if "Open" in selected_statuses and status_val == "open":
                    status_match = True
                if not status_match:
                    continue

            filtered.append(p)

        return filtered

    @rx.var
    def total_predictions_count(self) -> int:
        return len(self.filtered_predictions_list)

    @rx.var
    def total_predictions_points(self) -> int:
        return sum(int(p.get("points", 0)) for p in self.filtered_predictions_list)

    @rx.var
    def filtered_predictions_count_display(self) -> str:
        count = len(self.filtered_predictions_list)
        return f"{count} Prediction" if count == 1 else f"{count} Predictions"

    @rx.var
    def filtered_predictions_points_display(self) -> str:
        pts = sum(int(p.get("points", 0)) for p in self.filtered_predictions_list)
        return f"{pts} Points Wagered"

    # ── Donut Chart Data Generation (SDDREQ-159 to SDDREQ-163) ────────────────
    def _build_category_donut(self, category_name: str) -> tuple[list[dict], list[dict]]:
        cat_preds = [p for p in self.all_predictions_list if p.get("category") == category_name]
        if not cat_preds:
            return [], []

        teams = {}
        for p in cat_preds:
            t = p.get("target", "Unknown")
            pts = int(p.get("points", 0))
            stance = str(p.get("stance", "")).upper()
            if t not in teams:
                teams[t] = {"total": 0, "pos": 0, "neg": 0}
            teams[t]["total"] += pts
            if "FOR" in stance or "OVER" in stance:
                teams[t]["pos"] += pts
            else:
                teams[t]["neg"] += pts

        outer = []
        inner = []
        for t, data in sorted(teams.items(), key=lambda x: -x[1]["total"]):
            outer.append({
                "name": t,
                "value": data["total"],
                "fill": get_constructor_color(t),
            })
            pos_label = "Over" if category_name == "Expected Points" else "For"
            neg_label = "Under" if category_name == "Expected Points" else "Against"
            if data["pos"] > 0:
                inner.append({
                    "name": f"{t} ({pos_label})",
                    "value": data["pos"],
                    "fill": "#3cb44b",
                })
            if data["neg"] > 0:
                inner.append({
                    "name": f"{t} ({neg_label})",
                    "value": data["neg"],
                    "fill": "#FF4B4B",
                })

        return outer, inner

    @rx.var
    def expected_points_donut_outer(self) -> list[dict]:
        outer, _ = self._build_category_donut("Expected Points")
        return outer

    @rx.var
    def expected_points_donut_inner(self) -> list[dict]:
        _, inner = self._build_category_donut("Expected Points")
        return inner

    @rx.var
    def expected_winner_donut_outer(self) -> list[dict]:
        outer, _ = self._build_category_donut("Expected Race Winner")
        return outer

    @rx.var
    def expected_winner_donut_inner(self) -> list[dict]:
        _, inner = self._build_category_donut("Expected Race Winner")
        return inner

    @rx.var
    def expected_podium_donut_outer(self) -> list[dict]:
        outer, _ = self._build_category_donut("Podium Teams")
        return outer

    @rx.var
    def expected_podium_donut_inner(self) -> list[dict]:
        _, inner = self._build_category_donut("Podium Teams")
        return inner

    @rx.var
    def highest_score_donut_outer(self) -> list[dict]:
        outer, _ = self._build_category_donut("Highest Scoring Team")
        return outer

    @rx.var
    def highest_score_donut_inner(self) -> list[dict]:
        _, inner = self._build_category_donut("Highest Scoring Team")
        return inner

    @rx.var
    def user_metrics_donut_outer(self) -> list[dict]:
        """Outer ring: Each user who submitted predictions (SDDREQ-163)."""
        users = {}
        for p in self.all_predictions_list:
            u = p.get("username", "Unknown")
            pts = int(p.get("points", 0))
            users[u] = users.get(u, 0) + pts

        palette = ["#00b4da", "#FFD700", "#FF4B4B", "#9B59B6", "#1ABC9C", "#E67E22", "#3498DB", "#2ECC71"]
        outer = []
        for idx, (u, total_pts) in enumerate(sorted(users.items(), key=lambda x: -x[1])):
            outer.append({
                "name": u,
                "value": total_pts,
                "fill": palette[idx % len(palette)],
            })
        return outer

    @rx.var
    def user_metrics_donut_inner(self) -> list[dict]:
        """Inner ring: Positive (For/Over) vs Negative (Against/Under) per user (SDDREQ-163)."""
        users = {}
        for p in self.all_predictions_list:
            u = p.get("username", "Unknown")
            pts = int(p.get("points", 0))
            stance = str(p.get("stance", "")).upper()
            if u not in users:
                users[u] = {"pos": 0, "neg": 0}
            if "FOR" in stance or "OVER" in stance:
                users[u]["pos"] += pts
            else:
                users[u]["neg"] += pts

        inner = []
        for u, data in users.items():
            if data["pos"] > 0:
                inner.append({
                    "name": f"{u} (Positive)",
                    "value": data["pos"],
                    "fill": "#3cb44b",
                })
            if data["neg"] > 0:
                inner.append({
                    "name": f"{u} (Negative)",
                    "value": data["neg"],
                    "fill": "#FF4B4B",
                })
        return inner

    @rx.var
    def expected_points_donut_svg(self) -> str:
        cat_preds = [p for p in self.all_predictions_list if p.get("category") == "Expected Points"]
        return build_category_donut_svg("Expected Points", cat_preds, "expected-points-donut-svg", "Expected Points")

    @rx.var
    def expected_winner_donut_svg(self) -> str:
        cat_preds = [p for p in self.all_predictions_list if p.get("category") == "Expected Race Winner"]
        return build_category_donut_svg("Expected Race Winner", cat_preds, "expected-winner-donut-svg", "Expected Winner")

    @rx.var
    def expected_podium_donut_svg(self) -> str:
        cat_preds = [p for p in self.all_predictions_list if p.get("category") == "Podium Teams"]
        return build_category_donut_svg("Podium Teams", cat_preds, "expected-podium-donut-svg", "Podium Teams")

    @rx.var
    def highest_score_donut_svg(self) -> str:
        cat_preds = [p for p in self.all_predictions_list if p.get("category") == "Highest Scoring Team"]
        return build_category_donut_svg("Highest Scoring Team", cat_preds, "highest-score-donut-svg", "Highest Score")

    @rx.var
    def user_metrics_donut_svg(self) -> str:
        return build_user_metrics_donut_svg(self.all_predictions_list, "user-metrics-donut-svg")

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
    """Modal dialog for placing a prediction (SDDREQ-143, SDDREQ-146, SDDREQ-156, SDDREQ-158)."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Submit a Prediction", font_family="Outfit", font_weight="800", color="white"),
            rx.dialog.description(
                "Wager your Alternative Points against constructor projection lines for the upcoming race.",
                color="#A0A0AA",
                font_size="xs",
                margin_bottom="4",
            ),
            rx.vstack(
                # Category selector
                rx.vstack(
                    rx.text("STAT CATEGORY", font_size="10px", font_weight="800", color="#00b4da", letter_spacing="0.05em"),
                    rx.select(
                        PredictionsMarketState.category_options,
                        value=PredictionsMarketState.selected_category,
                        on_change=PredictionsMarketState.set_category,
                        width="100%",
                        bg="#1F1F26",
                        color="white",
                        border="1px solid #33333E",
                    ),
                    spacing="1",
                    width="100%",
                    align_items="start",
                ),
                # Prediction target (All constructors per SDDREQ-156)
                rx.vstack(
                    rx.text("PREDICTION TARGET (CONSTRUCTOR)", font_size="10px", font_weight="800", color="#00b4da", letter_spacing="0.05em"),
                    rx.select(
                        PredictionsMarketState.target_options,
                        value=PredictionsMarketState.selected_target,
                        on_change=PredictionsMarketState.set_target,
                        width="100%",
                        bg="#1F1F26",
                        color="white",
                        border="1px solid #33333E",
                    ),
                    spacing="1",
                    width="100%",
                    align_items="start",
                ),
                # Stance selector (FOR/AGAINST or OVER/UNDER)
                rx.vstack(
                    rx.text("STANCE", font_size="10px", font_weight="800", color="#00b4da", letter_spacing="0.05em"),
                    rx.cond(
                        PredictionsMarketState.selected_category != "Expected Points",
                        rx.segmented_control.root(
                            rx.segmented_control.item("FOR", value="FOR"),
                            rx.segmented_control.item("AGAINST", value="AGAINST"),
                            value=PredictionsMarketState.selected_stance,
                            on_change=PredictionsMarketState.set_stance,
                            width="100%",
                            color_scheme="cyan",
                        ),
                        rx.segmented_control.root(
                            rx.segmented_control.item("OVER", value="OVER"),
                            rx.segmented_control.item("UNDER", value="UNDER"),
                            value=PredictionsMarketState.selected_stance,
                            on_change=PredictionsMarketState.set_stance,
                            width="100%",
                            color_scheme="cyan",
                        ),
                    ),
                    spacing="1",
                    width="100%",
                    align_items="start",
                ),
                # Points to wager
                rx.vstack(
                    rx.hstack(
                        rx.text("POINTS TO WAGER", font_size="10px", font_weight="800", color="#00b4da", letter_spacing="0.05em"),
                        rx.spacer(),
                        rx.text(f"Available: {PredictionsMarketState.user_remaining_points} pts", font_size="10px", color="#888888"),
                        width="100%",
                        align="center",
                    ),
                    rx.input(
                        type="number",
                        min="1",
                        max=PredictionsMarketState.user_remaining_points,
                        value=PredictionsMarketState.wager_amount,
                        on_change=PredictionsMarketState.set_wager,
                        width="100%",
                        bg="#1F1F26",
                        color="white",
                        border="1px solid #33333E",
                    ),
                    spacing="1",
                    width="100%",
                    align_items="start",
                ),
                # Feedback error message if any
                rx.cond(
                    PredictionsMarketState.feedback_message != "",
                    rx.text(PredictionsMarketState.feedback_message, color="#FF4B4B", font_size="xs", font_weight="600"),
                    rx.fragment(),
                ),
                # Action buttons
                rx.hstack(
                    rx.button("Cancel", variant="soft", color_scheme="gray", on_click=PredictionsMarketState.close_modal),
                    rx.spacer(),
                    rx.button(
                        "Submit Wager",
                        bg="#00b4da",
                        color="white",
                        font_weight="700",
                        _hover={"bg": "#009bbd"},
                        on_click=PredictionsMarketState.submit_prediction,
                    ),
                    width="100%",
                    align="center",
                    margin_top="3",
                ),
                spacing="3",
                width="100%",
            ),
            bg="#18181F",
            border="1px solid #2D2D38",
            border_radius="xl",
            padding="20px",
            max_width="440px",
        ),
        open=PredictionsMarketState.modal_open,
        on_open_change=PredictionsMarketState.close_modal,
    )


def _donut_chart_card(
    title: str,
    subtitle: str,
    svg_var: rx.Var[str],
    chart_id: str,
) -> rx.Component:
    """Card wrapper for concentric multi-ring donut charts matching standard chart theming."""
    download_container_id = f"{chart_id}-download-container"

    chart_area = rx.box(
        rx.center(
            memoized_market_donut_chart(html_content=svg_var),
            width="100%",
        ),
        id=download_container_id,
        position="relative",
        width="100%",
    )

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("pie-chart", size=18, color="#00b4da"),
                    rx.vstack(
                        rx.text(title, font_size="15px", font_weight="800", color="white", font_family="Outfit"),
                        rx.text(subtitle, font_size="10px", color="#8E8E93"),
                        spacing="0",
                        align_items="start",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                chart_download_button(download_container_id, title),
                width="100%",
                align="center",
            ),
            chart_area,
            width="100%",
            spacing="3",
        ),
        id=f"card-{chart_id}",
        class_name="donut-chart-card",
        bg="#15151A",
        border="1px solid #2C2C32",
        border_radius="2xl",
        padding=["16px", "20px", "24px"],
        box_shadow="0 8px 24px rgba(0,0,0,0.4)",
        box_sizing="border-box",
        width="100%",
    )


def _active_race_table_key() -> rx.Component:
    """Interactive filter key for the Active Race Predictions Table."""
    key_options = [
        ("For / Over", "#3cb44b"),
        ("Against / Under", "#FF4B4B"),
        ("Correct", "#00b4da"),
        ("Incorrect", "#FF8C00"),
        ("Open", "#D0D0D5"),
    ]

    has_any = PredictionsMarketState.table_filters.length() > 0

    item_boxes = []
    for label, color in key_options:
        is_sel = PredictionsMarketState.table_filters.contains(label)
        box = rx.box(
            rx.hstack(
                rx.box(
                    width="8px",
                    height="8px",
                    border_radius="50%",
                    bg=color,
                    flex_shrink="0",
                ),
                rx.text(
                    label,
                    font_size="12px",
                    font_weight=rx.cond(is_sel, "800", "700"),
                    font_family="Outfit",
                    color=rx.cond(is_sel, "white", rx.cond(has_any, "#8E8E98", "#FFFFFF")),
                    white_space="nowrap",
                ),
                rx.cond(
                    is_sel,
                    rx.icon("check", size=12, color=color),
                    rx.fragment(),
                ),
                spacing="2",
                align="center",
            ),
            on_click=PredictionsMarketState.toggle_table_filter(label),
            cursor="pointer",
            padding="4px 10px",
            border_radius="6px",
            bg=rx.cond(
                is_sel,
                "rgba(255, 255, 255, 0.1)",
                rx.cond(has_any, "#14141A", "#1B1B22"),
            ),
            border=rx.cond(
                is_sel,
                f"1.5px solid {color}",
                rx.cond(has_any, "1px solid #202028", "1px solid #2A2A34"),
            ),
            box_shadow=rx.cond(
                is_sel,
                f"0 0 10px {color}33",
                "none",
            ),
            opacity=rx.cond(
                is_sel,
                "1",
                rx.cond(has_any, "0.5", "1"),
            ),
            transition="all 0.15s ease",
            _hover={
                "border_color": color,
                "opacity": "1",
                "transform": "translateY(-1px)",
            },
        )
        item_boxes.append(box)

    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.text("Key", color="#00b4da", font_weight="700", font_size="12px", font_family="Outfit"),
                rx.text("(Click any combination to filter table)", color="#8E8E98", font_size="11px", font_family="Outfit"),
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            rx.cond(
                has_any,
                rx.button(
                    rx.hstack(
                        rx.icon("rotate-ccw", size=11),
                        rx.text("Reset Filters", font_size="10px", font_weight="700"),
                        spacing="1",
                        align="center",
                    ),
                    size="1",
                    variant="ghost",
                    color_scheme="gray",
                    color="#AAAAAA",
                    on_click=PredictionsMarketState.clear_table_filters,
                    cursor="pointer",
                    _hover={"color": "#00b4da"},
                    padding="2px 6px",
                    height="22px",
                ),
                rx.fragment(),
            ),
            width="100%",
            align="center",
            margin_bottom="2",
        ),
        rx.flex(
            *item_boxes,
            flex_wrap="wrap",
            gap="6px",
            align="center",
        ),
        width="100%",
    )


# ── Main Page View ────────────────────────────────────────────────────────────
def predictions_market_tab_view() -> rx.Component:
    """Renders the Predictions Market Tab strictly following SDDREQ-164 layout."""

    # 1. Warning box (SDDREQ-164)
    warning_banner = rx.box(
        rx.hstack(
            rx.icon("triangle-alert", size=18, color="#FF8C00", flex_shrink="0"),
            rx.text(
                "Alternative Points hold no monetary value. Wagers are purely for entertainment purposes.",
                font_size=["11px", "12px"],
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
        padding="10px 16px",
        width="100%",
    )

    # 2. Title (SDDREQ-164)
    title_heading = rx.heading(
        "Predictions Market",
        size="6",
        color="white",
        font_family="Outfit",
    )

    # 3. Your Alternative Points/Sign in box (SDDREQ-164, SDDREQ-143, SDDREQ-144, SDDREQ-168)
    unauthenticated_banner = rx.cond(
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
            padding="12px 18px",
            width="100%",
        ),
        rx.fragment(),
    )

    balance_card = rx.box(
        rx.hstack(
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
            # Lockout Badge with days+hours countdown (SDDREQ-145)
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
            # Submit Prediction Blue Button (SDDREQ-143)
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
            # Logout Button
            rx.cond(
                PredictionsMarketState.current_user != "",
                rx.button(
                    rx.hstack(
                        rx.icon("log-out", size=15),
                        rx.text("Logout", font_weight="700", font_size="xs"),
                        spacing="1",
                        align="center",
                    ),
                    variant="soft",
                    color_scheme="red",
                    cursor="pointer",
                    padding_x="3",
                    height="36px",
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
        bg="#15151A",
        border="1px solid #2C2C32",
        border_radius="2xl",
        padding=["16px", "20px", "24px"],
        width="100%",
        box_shadow="0 8px 24px rgba(0,0,0,0.4)",
        box_sizing="border-box",
    )

    # 4. Active Race Predictions Table Expander (SDDREQ-155, SDDREQ-164)
    expander_header = rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon("table", size=18, color="#00b4da", flex_shrink="0"),
                rx.text("Active Race Predictions Pool", font_size=["14px", "15px", "16px"], font_weight="800", color="white", font_family="Outfit"),
                spacing="2",
                align="center",
            ),
            rx.flex(
                rx.badge(
                    PredictionsMarketState.filtered_predictions_count_display,
                    bg="rgba(0, 180, 218, 0.15)",
                    color="#00b4da",
                    border="1px solid rgba(0, 180, 218, 0.4)",
                    border_radius="full",
                    font_size="11px",
                    font_weight="700",
                    padding_x="2.5",
                    white_space="nowrap",
                ),
                rx.badge(
                    PredictionsMarketState.filtered_predictions_points_display,
                    bg="rgba(255, 215, 0, 0.15)",
                    color="#FFD700",
                    border="1px solid rgba(255, 215, 0, 0.4)",
                    border_radius="full",
                    font_size="11px",
                    font_weight="700",
                    padding_x="2.5",
                    white_space="nowrap",
                ),
                direction=rx.breakpoints(initial="column", sm="row"),
                align=rx.breakpoints(initial="start", sm="center"),
                spacing="2",
            ),
            rx.spacer(),
            rx.icon(
                rx.cond(PredictionsMarketState.pool_expander_open, "chevron-up", "chevron-down"),
                size=20,
                color="#AAAAAA",
                flex_shrink="0",
            ),
            width="100%",
            align="center",
            spacing="3",
        ),
        cursor="pointer",
        on_click=PredictionsMarketState.toggle_pool_expander,
        padding_y="1",
        width="100%",
    )

    expander_content = rx.cond(
        PredictionsMarketState.pool_expander_open,
        rx.vstack(
            _active_race_table_key(),
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("STATUS", color="#00b4da", font_size="11px", font_weight="800"),
                            rx.table.column_header_cell("USER", color="#00b4da", font_size="11px", font_weight="800"),
                            rx.table.column_header_cell("CATEGORY", color="#00b4da", font_size="11px", font_weight="800"),
                            rx.table.column_header_cell("TARGET", color="#00b4da", font_size="11px", font_weight="800"),
                            rx.table.column_header_cell("STANCE", color="#00b4da", font_size="11px", font_weight="800"),
                            rx.table.column_header_cell("LINE", color="#00b4da", font_size="11px", font_weight="800"),
                            rx.table.column_header_cell("POINTS", color="#00b4da", font_size="11px", font_weight="800"),
                            rx.table.column_header_cell("PAYOUT", color="#00b4da", font_size="11px", font_weight="800"),
                            rx.table.column_header_cell("ACTION", color="#00b4da", font_size="11px", font_weight="800"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            PredictionsMarketState.filtered_predictions_list,
                            lambda p: rx.table.row(
                                rx.table.cell(
                                    rx.badge(
                                        p["status_upper"],
                                        bg=p["status_bg"],
                                        color=p["status_color"],
                                        border=p["status_border"],
                                        font_size="10px",
                                        font_weight="800",
                                        padding_x="6px",
                                        padding_y="2px",
                                        border_radius="md",
                                    )
                                ),
                                rx.table.cell(
                                    rx.hstack(
                                        rx.cond(
                                            p["is_mine"],
                                            rx.badge("YOU", bg="rgba(0,180,218,0.2)", color="#00b4da", font_size="9px", font_weight="900"),
                                            rx.fragment(),
                                        ),
                                        rx.text(p["username"], font_size="xs", font_weight="700", color="white"),
                                        spacing="1",
                                        align="center",
                                    )
                                ),
                                rx.table.cell(rx.text(p["category"], font_size="xs", color="#D0D0D5")),
                                rx.table.cell(
                                    rx.hstack(
                                        rx.box(width="4px", height="16px", bg=p["team_color"], border_radius="full", flex_shrink="0"),
                                        rx.text(p["target"], font_size="xs", font_weight="700", color="white"),
                                        spacing="2",
                                        align="center",
                                    )
                                ),
                                rx.table.cell(
                                    rx.badge(
                                        p["stance"],
                                        color=rx.cond(p["is_positive"], "#3cb44b", "#FF4B4B"),
                                        bg=rx.cond(p["is_positive"], "rgba(60, 180, 75, 0.15)", "rgba(255, 75, 75, 0.15)"),
                                        border=rx.cond(p["is_positive"], "1px solid rgba(60, 180, 75, 0.3)", "1px solid rgba(255, 75, 75, 0.3)"),
                                        font_size="10px",
                                        font_weight="800",
                                    )
                                ),
                                rx.table.cell(rx.text(p["line_display"], font_size="xs", color="#AAAAAA")),
                                rx.table.cell(rx.badge(p["points_display"], bg="rgba(255,255,255,0.06)", color="white", font_size="xs", font_weight="800")),
                                rx.table.cell(rx.text(f"{p['payout']} pts" if str(p['status']).lower() == 'correct' else "—", font_size="xs", color="#00b4da" if str(p['status']).lower() == 'correct' else "#888888", font_weight="700")),
                                rx.table.cell(
                                    rx.cond(
                                        p["can_delete"],
                                        rx.icon_button(
                                            rx.icon("trash-2", size=13),
                                            size="1",
                                            variant="ghost",
                                            color_scheme="red",
                                            on_click=PredictionsMarketState.delete_prediction(p["id"]),
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
                rx.cond(
                    PredictionsMarketState.filtered_predictions_list.length() == 0,
                    rx.center(
                        rx.vstack(
                            rx.icon("filter-x", size=24, color="#666670"),
                            rx.text("No predictions match the selected filter criteria", color="#8E8E98", font_size="xs", font_weight="600"),
                            spacing="2",
                            align="center",
                            padding="24px",
                        ),
                        width="100%",
                    ),
                    rx.fragment(),
                ),
                width="100%",
                overflow_x="auto",
                margin_top="2",
            ),
            width="100%",
            spacing="3",
        ),
        rx.fragment(),
    )

    pool_expander_box = rx.box(
        rx.vstack(
            expander_header,
            expander_content,
            width="100%",
            spacing="2",
        ),
        bg="#15151A",
        border="1px solid #2C2C32",
        border_radius="2xl",
        padding=["16px", "20px", "24px"],
        width="100%",
        box_shadow="0 8px 24px rgba(0,0,0,0.4)",
        box_sizing="border-box",
    )

    # 5. 2x2 grid of the four category charts (SDDREQ-164, SDDREQ-159 to 162)
    grid_2x2_charts = rx.grid(
        _donut_chart_card(
            "Expected Points Distribution",
            "Outer: Constructor wagers | Inner: Over vs Under split",
            PredictionsMarketState.expected_points_donut_svg,
            chart_id="expected_points_donut",
        ),
        _donut_chart_card(
            "Expected Winner Projections",
            "Outer: Constructor wagers | Inner: For vs Against split",
            PredictionsMarketState.expected_winner_donut_svg,
            chart_id="expected_winner_donut",
        ),
        _donut_chart_card(
            "Expected Podium Contenders",
            "Outer: Constructor wagers | Inner: For vs Against split",
            PredictionsMarketState.expected_podium_donut_svg,
            chart_id="expected_podium_donut",
        ),
        _donut_chart_card(
            "Highest Scoring Team Pool",
            "Outer: Constructor wagers | Inner: For vs Against split",
            PredictionsMarketState.highest_score_donut_svg,
            chart_id="highest_score_donut",
        ),
        columns=rx.breakpoints(initial="1", md="2"),
        spacing="5",
        width="100%",
    )

    # 6. User Predictions Metric Pie Chart (SDDREQ-164, SDDREQ-163)
    user_metric_download_id = "user_predictions_metric_donut-download-container"
    user_metric_card = rx.box(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("pie-chart", size=18, color="#00b4da"),
                    rx.vstack(
                        rx.text("User Predictions Metric", font_size="15px", font_weight="800", color="white", font_family="Outfit"),
                        rx.text("Outer ring: Points wagered per user | Inner ring: Positive (For/Over) vs Negative (Against/Under)", font_size="11px", color="#8E8E93"),
                        spacing="0",
                        align_items="start",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                chart_download_button(user_metric_download_id, "User Predictions Metric"),
                width="100%",
                align="center",
            ),
            rx.box(
                rx.center(
                    memoized_market_donut_chart(html_content=PredictionsMarketState.user_metrics_donut_svg),
                    width="100%",
                ),
                id=user_metric_download_id,
                position="relative",
                width="100%",
            ),
            width="100%",
            spacing="3",
        ),
        id="card-user_predictions_metric_donut",
        class_name="donut-chart-card",
        bg="#15151A",
        border="1px solid #2C2C32",
        border_radius="2xl",
        padding=["16px", "20px", "24px"],
        box_shadow="0 8px 24px rgba(0,0,0,0.4)",
        box_sizing="border-box",
        width="100%",
    )

    return rx.vstack(
        rx.el.script(src="/donut_chart.js?v=20260912_06"),
        warning_banner,
        title_heading,
        unauthenticated_banner,
        balance_card,
        pool_expander_box,
        grid_2x2_charts,
        user_metric_card,
        _submit_prediction_modal(),
        width="100%",
        spacing="5",
        align_items="start",
    )
