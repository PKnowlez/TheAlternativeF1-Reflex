"""
All Time Summary Module for The Alternative F1 Reflex Application
Implements TAF1APP-SDDFEAT-5 downstream approved requirements:
- SDDREQ-109: All Time Graphs Page (New default "Summary" tab in All Time Stats)
- SDDREQ-113: All Time Graphs Page - Layout (Top center donut, Row 2 left constructor line, Row 2 right driver line)
- SDDREQ-107: All Time Pie Charts - General (Two-ring donut, inner ring driver points shaded by team color, outer ring constructor points in constructor color)
- SDDREQ-108: All Time Pie Charts - Center Display (Interactive center text: default total league points; hover/click shows entity name, points, percentage)
- SDDREQ-110: All Time Line Chart Constructor - General (Standings line chart style, omitting leading zeroes before debut)
- SDDREQ-111: All Time Line Chart Driver - General (Standings line chart style, omitting leading zeroes before debut)
- SDDREQ-112: All Time Line Chart - New Driver or Constructor (Omitting leading zeroes prior to debut race)
"""

import math
from pathlib import Path
from collections import defaultdict
import pandas as pd
import reflex as rx

from the_alternative_f1.all_time_stats.Functions import get_excel_sheet, file as excel_file_path
from the_alternative_f1.constructor_colors import CONSTRUCTOR_COLORS, get_constructor_color
from the_alternative_f1.articles.components import zoomable_chart, DownloadState, interactive_line_chart_key

# Comprehensive Driver Colors across all 24 drivers
ALL_TIME_DRIVER_COLORS = {
    "Joshua": "#1634CB",
    "Eddie": "#455A94",
    "Nick": "#FF6A00",
    "Del": "#FFAE00",
    "Patrick": "#FFEA00",
    "Josh": "#D4AF37",
    "Matthew": "#A0A0A0",
    "Brently": "#E0E0E0",
    "Grayson": "#00A0DE",
    "Josh C.": "#6CD5FF",
    "Erick": "#EF1A2D",
    "Zane": "#FD4BC7",
    "Jairo": "#00D2BE",
    "Marcus": "#006F62",
    "Boz": "#A33E2C",
    "Jaden": "#3B82F6",
    "Travis": "#EAB308",
    "David": "#C92D4B",
    "Yeti": "#22C55E",
    "Leo": "#911EB4",
    "Gary": "#46F0F0",
    "Randy": "#F032E6",
    "Josh L": "#BCF60C",
    "Evelo": "#008080",
}

# ── Color Utility Functions ───────────────────────────────────────────────────
def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    hex_str = str(hex_str).strip().lstrip("#")
    if hex_str.lower() == "darkblue":
        return (0, 0, 139)
    if len(hex_str) == 3:
        hex_str = "".join([c * 2 for c in hex_str])
    if len(hex_str) != 6:
        return (120, 120, 120)
    try:
        return int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
    except Exception:
        return (120, 120, 120)


def _rgb_to_hex(r: float, g: float, b: float) -> str:
    r_c = max(0, min(255, int(round(r))))
    g_c = max(0, min(255, int(round(g))))
    b_c = max(0, min(255, int(round(b))))
    return f"#{r_c:02X}{g_c:02X}{b_c:02X}"


def _get_driver_shade(base_hex: str, driver_idx: int, total_drivers: int) -> str:
    """Produce distinct, exaggerated tints of constructor color:
    Highest point driver (idx 0) gets same color as constructor.
    Next driver gets ~25% lighter, next ~50% lighter, and so on.
    """
    if driver_idx <= 0:
        return base_hex
    r, g, b = _hex_to_rgb(base_hex)
    factor = min(0.82, driver_idx * 0.25)
    nr = r + (255 - r) * factor
    ng = g + (255 - g) * factor
    nb = b + (255 - b) * factor
    return _rgb_to_hex(nr, ng, nb)


# ── Global In-Memory Summary Cache ────────────────────────────────────────────
_SUMMARY_CACHE: dict = {}
_SUMMARY_MTIME: float = 0.0


def _format_race_name(race_str: str) -> str:
    res = str(race_str).strip()
    if " Reverse" in res:
        res = res.replace(" Reverse", " (R)")
    if " Sprint" in res:
        res = res.replace(" Sprint", " (S)")
    return res


def precompute_summary_data(num_seasons: int = 5) -> dict:
    """Precompute all-time cumulative points with debut trimming and aligned donut slices."""
    global _SUMMARY_CACHE, _SUMMARY_MTIME
    excel_p = Path(excel_file_path)
    current_mtime = excel_p.stat().st_mtime if excel_p.exists() else 0.0

    if _SUMMARY_CACHE and _SUMMARY_MTIME == current_mtime:
        return _SUMMARY_CACHE

    all_races = []  # list of tuples: (season, raw_race_name, full_label)
    season_dfs = {}

    for s in range(1, num_seasons + 1):
        df_s = get_excel_sheet(f"Season{s}")
        if df_s.empty:
            continue
        df_s["Driver"] = df_s["Driver"].astype(str).str.strip()
        df_s["Team"] = df_s["Team"].astype(str).str.strip()
        season_dfs[s] = df_s

        sched = get_excel_sheet(f"S{s}Schedule")
        if not sched.empty:
            for r in sched["Race"]:
                r_str = str(r).strip()
                if r_str.lower().startswith(("pre", "post")) or not r_str:
                    continue
                
                # Exclude future races that have not occurred yet
                p_col = f"{r_str}Points"
                pl_col = f"{r_str}Place"
                has_occurred = False
                if p_col in df_s.columns:
                    pts_sum = pd.to_numeric(df_s[p_col], errors="coerce").fillna(0).sum()
                    if pts_sum > 0:
                        has_occurred = True
                if not has_occurred and pl_col in df_s.columns:
                    valid_places = df_s[pl_col].dropna().astype(str).str.strip()
                    valid_places = valid_places[~valid_places.isin(["", "nan", "None", "—", "-", "0"])]
                    if len(valid_places) > 0:
                        has_occurred = True

                if not has_occurred:
                    continue

                label = f"S{s} {_format_race_name(r_str)}"
                all_races.append((s, r_str, label))

    # Identify first race of each subsequent season for vertical boundary lines
    seen_seasons = set()
    first_season = all_races[0][0] if all_races else 1
    season_start_races = []
    for s, r_str, label in all_races:
        if s not in seen_seasons:
            seen_seasons.add(s)
            if s > first_season:
                season_start_races.append(label)

    # Identify debut race index for each constructor and driver
    constructor_debut = {}
    driver_debut = {}

    for race_idx, (s, r_str, _) in enumerate(all_races):
        df_s = season_dfs.get(s)
        if df_s is None or df_s.empty:
            continue
        p_col = f"{r_str}Points"
        pl_col = f"{r_str}Place"

        for _, row in df_s.iterrows():
            drv = str(row.get("Driver", "")).strip()
            team = str(row.get("Team", "")).strip()
            if not drv or drv.lower() in ("nan", "none", "—", ""):
                continue
            # A driver/team debuted if they are listed in this season and have this race on schedule
            if p_col in df_s.columns or pl_col in df_s.columns:
                if team and team not in constructor_debut and team.lower() not in ("nan", "", "—", "none"):
                    constructor_debut[team] = race_idx
                if drv not in driver_debut:
                    driver_debut[drv] = race_idx

    # Build chronological running cumulative points
    team_line_data = []
    driver_line_data = []

    running_team_pts = defaultdict(float)
    running_driver_pts = defaultdict(float)

    # Track team each driver was on at each race index (for stint coloring)
    # driver_team_per_race: { driver -> [team_at_race_0, team_at_race_1, ...] }
    driver_team_per_race: dict[str, list] = defaultdict(list)

    # Breakdown for donut chart:
    # constructor_totals: team -> total points
    # constructor_driver_breakdown: team -> { driver -> points_for_team }
    constructor_totals = defaultdict(float)
    driver_totals = defaultdict(float)
    constructor_driver_breakdown = defaultdict(lambda: defaultdict(float))

    for race_idx, (s, r_str, label) in enumerate(all_races):
        df_s = season_dfs.get(s)
        p_col = f"{r_str}Points"

        # Collect which team each driver is on this race (for stint tracking)
        race_driver_team: dict[str, str] = {}
        if df_s is not None and not df_s.empty:
            for _, row in df_s.iterrows():
                drv = str(row.get("Driver", "")).strip()
                team = str(row.get("Team", "")).strip()
                if drv and drv.lower() not in ("nan", "none", "—", "") and team and team.lower() not in ("nan", "none", "—", ""):
                    race_driver_team[drv] = team

        if df_s is not None and not df_s.empty and p_col in df_s.columns:
            for _, row in df_s.iterrows():
                drv = str(row.get("Driver", "")).strip()
                team = str(row.get("Team", "")).strip()
                if not drv or drv.lower() in ("nan", "none", "—", ""):
                    continue
                val = row[p_col]
                try:
                    pts = float(val) if val is not None and not pd.isna(val) else 0.0
                except Exception:
                    pts = 0.0

                if pts > 0:
                    running_team_pts[team] += pts
                    running_driver_pts[drv] += pts
                    constructor_totals[team] += pts
                    driver_totals[drv] += pts
                    constructor_driver_breakdown[team][drv] += pts

        # Record snapshot for Constructor Line Chart (omitting leading zeroes before debut)
        c_point = {"race": label}
        for team, debut_idx in constructor_debut.items():
            if race_idx >= debut_idx:
                c_point[team] = round(running_team_pts[team], 1)
        team_line_data.append(c_point)

        # Record snapshot for Driver Line Chart (omitting leading zeroes before debut)
        d_point = {"race": label}
        for drv, debut_idx in driver_debut.items():
            if race_idx >= debut_idx:
                d_point[drv] = round(running_driver_pts[drv], 1)
                # Record team for stint tracking
                driver_team_per_race[drv].append(race_driver_team.get(drv, ""))
            else:
                driver_team_per_race[drv].append("")  # not yet debuted
        driver_line_data.append(d_point)

    # Sort constructors by total points descending
    sorted_constructors = sorted(
        [t for t in constructor_totals.keys() if constructor_totals[t] > 0],
        key=lambda x: constructor_totals[x],
        reverse=True,
    )
    sorted_drivers = sorted(
        [d for d in driver_totals.keys() if driver_totals[d] > 0],
        key=lambda x: driver_totals[x],
        reverse=True,
    )

    total_league_points = sum(constructor_totals.values())

    # ── Build driver stints (consecutive races on same team) ──────────────────
    # driver_stints: { driver -> [ {team, start_race_idx, end_race_idx}, ... ] }
    # driver_last_team: { driver -> team_name }  (for key color)
    driver_stints: dict[str, list[dict]] = {}
    driver_last_team: dict[str, str] = {}
    num_races = len(all_races)

    for drv in sorted_drivers:
        debut_idx = driver_debut.get(drv, 0)
        teams_per_race = driver_team_per_race.get(drv, [])
        stints: list[dict] = []
        current_team = ""
        stint_start = debut_idx

        for r_idx in range(debut_idx, num_races):
            team_at_r = teams_per_race[r_idx] if r_idx < len(teams_per_race) else ""
            if team_at_r and team_at_r != current_team:
                if current_team and stints:
                    # Close current stint at previous race
                    stints[-1]["end_race_idx"] = r_idx - 1
                current_team = team_at_r
                stints.append({"team": current_team, "start_race_idx": r_idx, "end_race_idx": num_races - 1})

        if not stints and current_team == "":
            # Driver had no team info recorded — fall back to single stint with unknown team
            stints.append({"team": "", "start_race_idx": debut_idx, "end_race_idx": num_races - 1})

        driver_stints[drv] = stints
        # Last team = last stint's team (may be empty if tracking failed)
        driver_last_team[drv] = stints[-1]["team"] if stints else ""

    # Build stint-keyed line data
    # Each data point dict has keys: race, {drv}__s{stint_i} for each stint
    # At the handoff race between stints, both the ending and starting stint share the same
    # cumulative value so the line segments connect seamlessly.
    driver_stint_line_data: list[dict] = [{"race": pt["race"]} for pt in driver_line_data]

    for drv in sorted_drivers:
        stints = driver_stints[drv]
        for s_i, stint in enumerate(stints):
            key = f"{drv}__s{s_i}"
            s_start = stint["start_race_idx"]
            s_end = stint["end_race_idx"]
            # Determine the overlap race: starting at s_start (first race of new stint)
            # Previous stint's last point = s_start - 1 cumulative, but we add the
            # transition race to BOTH stints at the same value so segments connect.
            # For the first stint we share s_end with the next stint's s_start.
            overlap_end = stints[s_i + 1]["start_race_idx"] if s_i + 1 < len(stints) else None

            for r_idx, pt in enumerate(driver_line_data):
                val = pt.get(drv)  # cumulative pts at this race (None if before debut)
                if val is None:
                    driver_stint_line_data[r_idx][key] = None
                    continue
                # Include point if within this stint's range, PLUS the overlap transition race
                in_stint = s_start <= r_idx <= s_end
                is_overlap = (overlap_end is not None and r_idx == overlap_end)
                if in_stint or is_overlap:
                    driver_stint_line_data[r_idx][key] = val
                else:
                    driver_stint_line_data[r_idx][key] = None

    # Build aligned donut chart geometry (SDDREQ-107, SDDREQ-108 & user alignment requirement)
    # Center (260, 260). Outer Ring (Constructors): r=174..242. Inner Ring (Drivers): r=102..170.
    cx, cy = 260.0, 260.0
    r_out_in, r_out_out = 174.0, 242.0
    r_in_in, r_in_out = 104.0, 170.0

    constructor_slices = []
    driver_slices = []

    curr_angle = -90.0  # start at 12 o'clock

    for team in sorted_constructors:
        c_pts = constructor_totals[team]
        if total_league_points <= 0 or c_pts <= 0:
            continue

        c_angle_span = (c_pts / total_league_points) * 360.0
        c_start_angle = curr_angle
        c_end_angle = curr_angle + c_angle_span
        c_color = get_constructor_color(team)
        c_pct = (c_pts / total_league_points) * 100.0

        constructor_slices.append({
            "name": team,
            "points": c_pts,
            "percentage": c_pct,
            "color": c_color,
            "start_angle": c_start_angle,
            "end_angle": c_end_angle,
        })

        # Process drivers for this constructor, sub-slicing within this constructor's exact angular span
        drv_map = constructor_driver_breakdown[team]
        sorted_team_drivers = sorted(
            [d for d in drv_map.keys() if drv_map[d] > 0],
            key=lambda d: drv_map[d],
            reverse=True,
        )

        curr_driver_angle = c_start_angle
        num_team_drivers = len(sorted_team_drivers)

        for d_idx, drv in enumerate(sorted_team_drivers):
            d_pts = drv_map[drv]
            # Angular span proportional to driver points within constructor slice
            d_angle_span = c_angle_span * (d_pts / c_pts)
            d_start_angle = curr_driver_angle
            d_end_angle = curr_driver_angle + d_angle_span
            curr_driver_angle = d_end_angle

            d_color = _get_driver_shade(c_color, d_idx, num_team_drivers)
            d_pct_of_team = (d_pts / c_pts) * 100.0

            driver_slices.append({
                "driver": drv,
                "constructor": team,
                "points": d_pts,
                "percentage_team": d_pct_of_team,
                "color": d_color,
                "start_angle": d_start_angle,
                "end_angle": d_end_angle,
            })

        curr_angle = c_end_angle

    _SUMMARY_CACHE = {
        "all_races": all_races,
        "season_start_races": season_start_races,
        "constructor_totals": dict(constructor_totals),
        "driver_totals": dict(driver_totals),
        "sorted_constructors": sorted_constructors,
        "sorted_drivers": sorted_drivers,
        "total_league_points": round(total_league_points, 1),
        "team_line_data": team_line_data,
        "driver_line_data": driver_line_data,
        "driver_stint_line_data": driver_stint_line_data,
        "driver_stints": driver_stints,
        "driver_last_team": driver_last_team,
        "constructor_slices": constructor_slices,
        "driver_slices": driver_slices,
    }
    _SUMMARY_MTIME = current_mtime
    return _SUMMARY_CACHE


# Initial warm-up of summary dataset
precompute_summary_data()


# ── Reflex State for Summary Page ─────────────────────────────────────────────
class SummaryState(rx.State):
    """State for the All Time Summary donut chart.

    Receives interaction payloads from donut_chart.js via the hidden
    #taf1_donut_select_input element, mirroring the stats_map.js pattern.

    Payload format:
        "hover:Constructor:McLaren:1234.5:42.3% of League"
        "click:Driver:Patrick:567.0:VCARB • 38.1% of Team"
        "reset"
    """

    # State fields
    event_type: str = ""          # "hover" | "click" | ""
    entity_type: str = ""         # "Constructor" | "Driver" | ""
    entity_name: str = ""
    entity_pts:  str = ""
    entity_meta: str = ""

    # ── Reactive display vars ──────────────────────────────────────────────
    @rx.var
    def center_type_label(self) -> str:
        if not self.entity_type:
            return "ALL-TIME LEAGUE"
        return self.entity_type.upper()

    @rx.var
    def center_value(self) -> str:
        if not self.entity_name:
            ds = precompute_summary_data()
            return f"{ds.get('total_league_points', 0):,.0f}"
        return self.entity_name

    @rx.var
    def center_value_size(self) -> str:
        name = self.entity_name
        if not name:
            return "24px"
        return "15px" if len(name) > 10 else "22px"

    @rx.var
    def center_meta_label(self) -> str:
        if not self.entity_pts:
            return "TOTAL POINTS"
        return self.entity_pts + " PTS • " + self.entity_meta

    @rx.var
    def center_type_fill(self) -> str:
        if self.event_type == "click":
            return "#00b4da"
        return "#8E8E93"

    # ── Event handler ─────────────────────────────────────────────────────
    def select_donut_event(self, payload: str | list = ""):
        """Receives the structured payload string from donut_chart.js."""
        if isinstance(payload, list):
            payload = payload[0] if payload else ""
        payload = str(payload).strip()

        if not payload or payload == "reset":
            self.event_type  = ""
            self.entity_type = ""
            self.entity_name = ""
            self.entity_pts  = ""
            self.entity_meta = ""
            return

        # Expected: "hover:Type:Name:Pts:Meta" or "click:Type:Name:Pts:Meta"
        parts = payload.split(":", 4)
        if len(parts) < 5:
            return

        event_type, entity_type, entity_name, pts, meta = parts
        self.event_type  = event_type.strip()
        self.entity_type = entity_type.strip()
        self.entity_name = entity_name.strip()
        self.entity_pts  = pts.strip()
        self.entity_meta = meta.strip()



# ── SVG Arc Math Helper ───────────────────────────────────────────────────────
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


def build_two_ring_donut_svg() -> str:
    """Build high-precision SVG for the two-ring donut chart with aligned radial slices.

    The SVG is rendered via rx.html() (dangerouslySetInnerHTML).
    The center display text is driven by SummaryState vars rendered as separate
    Reflex components overlaid on the SVG — this avoids the rx.html() script
    execution problem entirely.  The SVG itself contains only the visual paths.
    """
    ds = precompute_summary_data()
    c_slices = ds.get("constructor_slices", [])
    d_slices = ds.get("driver_slices", [])
    total_pts = ds.get("total_league_points", 0)

    cx, cy = 260.0, 260.0
    r_out_in, r_out_out = 174.0, 242.0
    r_in_in, r_in_out = 104.0, 170.0

    outer_paths = []
    for s in c_slices:
        name = s["name"]
        pts = s["points"]
        pct = s["percentage"]
        color = s["color"]
        path_d = _build_arc_path(cx, cy, r_out_in, r_out_out, s["start_angle"], s["end_angle"])
        outer_paths.append(f"""
        <path class="donut-slice donut-constructor" d="{path_d}" fill="{color}" stroke="#15151A" stroke-width="2"
              style="cursor: pointer; transition: opacity 0.15s ease;"
              data-type="Constructor"
              data-name="{name}"
              data-pts="{pts:,.1f}"
              data-meta="{pct:.1f}% of League"
              onmouseenter="window.taf1DonutEnter && window.taf1DonutEnter(this)"
              onmouseleave="window.taf1DonutLeave && window.taf1DonutLeave(this)"
              onclick="window.taf1DonutClick && window.taf1DonutClick(this, event)">
            <title>{name}: {pts:,.1f} pts ({pct:.1f}% of League)</title>
        </path>
        """)

    inner_paths = []
    for s in d_slices:
        drv = s["driver"]
        team = s["constructor"]
        pts = s["points"]
        pct = s["percentage_team"]
        color = s["color"]
        path_d = _build_arc_path(cx, cy, r_in_in, r_in_out, s["start_angle"], s["end_angle"])
        inner_paths.append(f"""
        <path class="donut-slice donut-driver" d="{path_d}" fill="{color}" stroke="#15151A" stroke-width="1.8"
              style="cursor: pointer; transition: opacity 0.15s ease;"
              data-type="Driver"
              data-name="{drv}"
              data-pts="{pts:,.1f}"
              data-meta="{team} • {pct:.1f}% of Team"
              onmouseenter="window.taf1DonutEnter && window.taf1DonutEnter(this)"
              onmouseleave="window.taf1DonutLeave && window.taf1DonutLeave(this)"
              onclick="window.taf1DonutClick && window.taf1DonutClick(this, event)">
            <title>{drv} ({team}): {pts:,.1f} pts ({pct:.1f}% of {team})</title>
        </path>
        """)

    return f"""
    <svg id="summary-donut-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 520" width="100%" height="100%"
         data-default-points="{ds.get('total_league_points', 0):,.0f}"
         style="display: block; max-width: 440px; max-height: 440px; margin: 0 auto; user-select: none;"
         onclick="window.taf1DonutBgClick && window.taf1DonutBgClick(event)">
        <defs>
            <filter id="donut-shadow" x="-10%" y="-10%" width="120%" height="120%">
                <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.5"/>
            </filter>
        </defs>

        <!-- Outer Ring: Constructors -->
        <g id="donut-outer-ring" filter="url(#donut-shadow)">
            {''.join(outer_paths)}
        </g>

        <!-- Inner Ring: Drivers -->
        <g id="donut-inner-ring" filter="url(#donut-shadow)">
            {''.join(inner_paths)}
        </g>

        <!-- Donut center hole (clickable to reset) -->
        <circle id="donut-center-hole" cx="{cx}" cy="{cy}" r="98"
                fill="#15151A" stroke="rgba(255,255,255,0.08)" stroke-width="1.5"
                style="cursor: pointer;"
                onclick="window.taf1DonutReset && window.taf1DonutReset(event)" />

        <!-- Center Information Display (inside SVG: saved in image export, immune to React context re-renders) -->
        <g id="donut-svg-center-group" pointer-events="none" text-anchor="middle" font-family="'Outfit', sans-serif" style="user-select: none;">
            <text id="donut-center-type" x="{cx}" y="230" dominant-baseline="middle"
                  fill="#8E8E93" font-size="11" font-weight="700" letter-spacing="1">ALL-TIME LEAGUE</text>
            <text id="donut-center-value" x="{cx}" y="260" dominant-baseline="middle"
                  fill="#FFFFFF" font-size="24" font-weight="900">{total_pts:,.0f}</text>
            <text id="donut-center-meta" x="{cx}" y="285" dominant-baseline="middle"
                  fill="#00b4da" font-size="10.5" font-weight="700" letter-spacing="0.5">TOTAL POINTS</text>
        </g>
    </svg>
    """



# ── Summary View Component ────────────────────────────────────────────────────
def summary_all_time_view(num_seasons: int = 5) -> rx.Component:
    """Render the All Time Summary page per SDDREQ-109 & SDDREQ-113."""
    ds = precompute_summary_data(num_seasons)
    team_line_data = ds["team_line_data"]
    driver_line_data = ds["driver_line_data"]
    sorted_constructors = ds["sorted_constructors"]
    sorted_drivers = ds["sorted_drivers"]
    total_pts = ds["total_league_points"]
    season_start_races = ds.get("season_start_races", [])

    # Calculate dynamic x-axis heights
    max_race_len = max([len(str(item.get("race", ""))) for item in team_line_data] or [0])
    race_axis_height = max(42, max_race_len * 5 + 14)

    # ── 1. Top Center: Two-Ring Donut Pie Chart ────────────────────────────────
    donut_svg_markup = build_two_ring_donut_svg()

    donut_chart_card = rx.box(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("pie-chart", size=18, color="#00b4da"),
                    rx.text("All Time Points Distribution", font_family="Outfit", font_weight="800", font_size="16px", color="white"),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.badge(
                    f"{total_pts:,.0f} Total League Points",
                    bg="rgba(0, 180, 218, 0.15)",
                    color="#00b4da",
                    border="1px solid rgba(0, 180, 218, 0.4)",
                    border_radius="full",
                    font_size="11px",
                    font_weight="700",
                    padding_x="8px",
                    padding_y="3px",
                ),
                width="100%",
                align="center",
                flex_wrap="wrap",
                gap="2",
            ),
            rx.text(
                "Outer Ring: Constructors (colored by official team colors) | Inner Ring: Drivers (shaded by team color, radially aligned as slices). Click or hover any slice to inspect.",
                font_size="12px",
                color="#8E8E93",
                margin_bottom="2",
                white_space="normal",
                word_break="break-word",
                width="100%",
                padding_x="1",
            ),
            # Donut SVG with native center information & download button
            rx.box(
                rx.center(
                    rx.box(
                        rx.html(donut_svg_markup),
                        width="100%",
                        max_width="480px",
                    ),
                    width="100%",
                ),
                # Download button bottom-right (matching map style)
                rx.button(
                    rx.icon("download", size=14),
                    on_click=lambda: DownloadState.download_chart("donut-download-container", "All Time Points Distribution"),
                    position="absolute",
                    bottom="8px",
                    right="8px",
                    bg="rgba(0,180,218,0.15)",
                    color="#00b4da",
                    border="1px solid rgba(0,180,218,0.4)",
                    border_radius="full",
                    padding_x="10px",
                    padding_y="6px",
                    font_size="11px",
                    cursor="pointer",
                    _hover={"bg": "rgba(0,180,218,0.3)"},
                ),
                id="donut-download-container",
                position="relative",
                width="100%",
            ),
            # Hidden input bridge — same pattern as MapAllTime.py / stats_map.js
            rx.input(
                id="taf1_donut_select_input",
                value="",
                on_change=SummaryState.select_donut_event,
                style={"display": "none"},
            ),
            width="100%",
            spacing="3",
        ),
        id="donut-chart-card",
        bg="#15151A",
        border="1px solid #2C2C32",
        border_radius="2xl",
        padding=["16px", "20px", "24px"],
        padding_x=["16px", "20px", "24px"],
        padding_y=["16px", "20px", "24px"],
        box_shadow="0 8px 24px rgba(0,0,0,0.4)",
        width="100%",
        box_sizing="border-box",
    )

    # Load the donut interaction script — rx.el.script (same as MapAllTime.py)
    donut_chart_card = rx.fragment(
        rx.el.script(src="/donut_chart.js?v=20260912_02"),
        donut_chart_card,
    )

    # ── 2. Left Second Row: Constructor Line Chart (SDDREQ-110, SDDREQ-112) ───
    constructor_line_chart = zoomable_chart(
        lambda h: rx.recharts.line_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.08)"),
            *[
                rx.recharts.reference_line(
                    x=r_label,
                    stroke="white",
                    custom_attrs={"strokeDasharray": "3 3", "isFront": False},
                )
                for r_label in season_start_races
            ],
            *[
                rx.recharts.line(
                    data_key=team,
                    stroke=get_constructor_color(team),
                    stroke_width=2,
                    dot={"fill": get_constructor_color(team), "stroke": get_constructor_color(team), "r": 1.5},
                    name=team,
                    type_="monotone",
                )
                for team in sorted_constructors
            ],
            rx.recharts.x_axis(
                data_key="race",
                font_size=8,
                angle=-90,
                height=race_axis_height,
                stroke="white",
                text_anchor="end",
                interval=0,
                tick={"dx": -5},
            ),
            rx.recharts.y_axis(
                stroke="white",
                width=38,
                tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
            ),
            data=team_line_data,
            margin={"top": 10, "right": 20, "left": 35, "bottom": 30},
            margin_left="-10px",
            width="100%",
            height=h,
        ),
        title="Constructor All Time Points Progression",
        chart_id="constructor_all_time_line_chart",
        height=360,
        large_height=480,
    )

    # ── Constructor interactive key ──────────────────────────────────────
    constructor_legend_expander = interactive_line_chart_key(
        chart_id="constructor_all_time_line_chart",
        items=[(team, get_constructor_color(team)) for team in sorted_constructors],
        title="Key (Constructors)",
        hint="Click constructor to highlight",
    )

    # ── 3. Right Second Row: Driver Line Chart (SDDREQ-111, SDDREQ-112) ────────
    # Each driver is split into stint segments (one per team), all sharing the
    # same `name` prop (the driver's name) so the key highlight JS still finds
    # and highlights every segment belonging to that driver together.
    driver_stint_line_data = ds["driver_stint_line_data"]
    driver_stints = ds["driver_stints"]
    driver_last_team = ds["driver_last_team"]

    # Build one Line component per driver-stint
    driver_stint_lines = []
    for drv in sorted_drivers:
        stints = driver_stints.get(drv, [])
        for s_i, stint in enumerate(stints):
            stint_team = stint["team"]
            stint_color = get_constructor_color(stint_team) if stint_team else ALL_TIME_DRIVER_COLORS.get(drv, "#00b4da")
            stint_key = f"{drv}__s{s_i}"
            driver_stint_lines.append(
                rx.recharts.line(
                    data_key=stint_key,
                    stroke=stint_color,
                    stroke_width=2,
                    dot={
                        "fill": stint_color,
                        "stroke": stint_color,
                        "r": 1.5,
                    },
                    # All stints for the same driver share the same `name` so the
                    # key highlight logic matches all of them together.
                    name=drv,
                    type_="monotone",
                    connect_nulls=False,
                )
            )

    driver_line_chart = zoomable_chart(
        lambda h: rx.recharts.line_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255, 255, 255, 0.08)"),
            *[
                rx.recharts.reference_line(
                    x=r_label,
                    stroke="white",
                    custom_attrs={"strokeDasharray": "3 3", "isFront": False},
                )
                for r_label in season_start_races
            ],
            *driver_stint_lines,
            rx.recharts.x_axis(
                data_key="race",
                font_size=8,
                angle=-90,
                height=race_axis_height,
                stroke="white",
                text_anchor="end",
                interval=0,
                tick={"dx": -5},
            ),
            rx.recharts.y_axis(
                stroke="white",
                width=38,
                tick={"textAnchor": "start", "dx": -25, "fill": "white", "fontSize": 10, "fontFamily": "Outfit"},
            ),
            data=driver_stint_line_data,
            margin={"top": 10, "right": 20, "left": 35, "bottom": 30},
            margin_left="-10px",
            width="100%",
            height=h,
        ),
        title="Driver All Time Points Progression",
        chart_id="driver_all_time_line_chart",
        height=360,
        large_height=480,
    )

    # ── Driver interactive key ───────────────────────────────────────────
    # Key color = driver's last (current) team constructor color
    driver_legend_expander = interactive_line_chart_key(
        chart_id="driver_all_time_line_chart",
        items=[
            (drv, get_constructor_color(driver_last_team[drv]) if driver_last_team.get(drv) else ALL_TIME_DRIVER_COLORS.get(drv, "#00b4da"))
            for drv in sorted_drivers
        ],
        title="Key (Drivers)",
        hint="Click driver to highlight",
    )

    # Assemble line chart cards
    constructor_card = rx.vstack(
        constructor_line_chart,
        constructor_legend_expander,
        width="100%",
        spacing="2",
    )

    driver_card = rx.vstack(
        driver_line_chart,
        driver_legend_expander,
        width="100%",
        spacing="2",
    )

    second_row = rx.grid(
        constructor_card,
        driver_card,
        columns={"initial": "1", "xl": "2"},
        spacing="4",
        width="100%",
    )

    return rx.vstack(
        rx.heading(
            "All Time Summary",
            size="6",
            color="white",
            font_family="Outfit",
            font_weight="800",
            margin_bottom="3",
        ),
        donut_chart_card,
        second_row,
        width="100%",
        spacing="5",
    )
