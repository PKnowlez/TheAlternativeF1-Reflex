"""
All Time Stats Map Module for The Alternative F1 Reflex Application
Implements SDDFEAT-12 and downstream SDD Requirements:
- SDDREQ-93: Grouping Options (Region, States, Metro area)
- SDDREQ-94: Grouping Regions (Mountain West, Great Plains, Midwest, The South, Northeast with defined colors)
- SDDREQ-95: Locations per Driver (24 drivers mapped by season)
- SDDREQ-96: Statistics to Calculate per Grouping Option (Championships, Points, Wins, Podiums, Poles, Ancillaries)
- SDDREQ-97: Default Grouping and Statistics (Regions, All Time, core default stats)
- SDDREQ-98: Statistic Display Options (Driver/Constructor Champs, Wins, Podiums, Points, Poles, Ancillaries)
- SDDREQ-99: Full Map Save (Full screen view dialog & .png download)
- SDDREQ-100: Interactive Map - Select (Highlight grouping on click/hover/select)
- SDDREQ-101: Interactive Map - Display (Detailed statistics overlay box on map)
- SDDREQ-102: General UI Guidance (Dark theme, white state borders, #00b4da blue highlight outline)
- SDDREQ-103: Active vs. Inactive Driver Toggle (Active only vs Inactive + Active)
- SDDREQ-104: Season Selector - Slider (Ticks for each season 1-5 and All Seasons default; cumulative unless single season checked)
- SDDREQ-105: Season Selector - Single Season Only Check (Checkbox below slider)
- SDDREQ-106: How to Handle Driver Locations/Moves (Multi-season driver relocation logic)
"""

import json
from pathlib import Path
from collections import defaultdict
import reflex as rx

from the_alternative_f1.all_time_stats.Functions import get_excel_sheet, is_season_completed, file as excel_file_path
from the_alternative_f1.articles.components import DownloadState

# Path to pre-extracted SVG paths for all 51 states + DC
SVG_DATA_FILE = Path(__file__).parent / "us_states_svg.json"
with open(SVG_DATA_FILE, "r", encoding="utf-8") as f:
    SVG_DATA = json.load(f)

# ── Driver Location Database (per SDDREQ-95 & SDDREQ-106) ─────────────────────
DRIVER_LOCATIONS = {
    "Nick": {"current": ("New York", "NY", "Northeast"), "seasons": {}},
    "Erick": {"current": ("Houston", "TX", "Great Plains"), "seasons": {}},
    "Joshua": {"current": ("New York", "NY", "Northeast"), "seasons": {}},
    "Del": {"current": ("Chicago", "IL", "Midwest"), "seasons": {}},
    "Zane": {"current": ("Houston", "TX", "Great Plains"), "seasons": {}},
    "Patrick": {
        "current": ("Denver", "CO", "Mountain West"),
        "seasons": {
            1: ("Houston", "TX", "Great Plains"),
            2: ("Houston", "TX", "Great Plains"),
            3: ("Houston", "TX", "Great Plains"),
            4: ("Denver", "CO", "Mountain West"),
            5: ("Denver", "CO", "Mountain West"),
        },
    },
    "Jairo": {"current": ("New York", "NY", "Northeast"), "seasons": {}},
    "Marcus": {"current": ("New York", "NY", "Northeast"), "seasons": {}},
    "Boz": {"current": ("New York", "NY", "Northeast"), "seasons": {}},
    "Eddie": {
        "current": ("Rochester", "NY", "Northeast"),
        "seasons": {
            1: ("New York", "NY", "Northeast"),
            2: ("New York", "NY", "Northeast"),
            3: ("New York", "NY", "Northeast"),
            4: ("New York", "NY", "Northeast"),
            5: ("Rochester", "NY", "Northeast"),
        },
    },
    "Jaden": {"current": ("New York", "NY", "Northeast"), "seasons": {}},
    "Brently": {"current": ("Detroit", "MI", "Midwest"), "seasons": {}},
    "Josh": {"current": ("Los Angeles", "CA", "Mountain West"), "seasons": {}},
    "Travis": {"current": ("Austin", "TX", "Great Plains"), "seasons": {}},
    "David": {"current": ("New York", "NY", "Northeast"), "seasons": {}},
    "Yeti": {"current": ("New York", "NY", "Northeast"), "seasons": {}},
    "Matthew": {"current": ("Charlotte", "NC", "The South"), "seasons": {}},
    "Leo": {"current": ("New York", "NY", "Northeast"), "seasons": {}},
    "Gary": {"current": ("New York", "NY", "Northeast"), "seasons": {}},
    "Randy": {"current": ("New York", "NY", "Northeast"), "seasons": {}},
    "Josh L": {"current": ("New York", "NY", "Northeast"), "seasons": {}},
    "Evelo": {"current": ("New York", "NY", "Northeast"), "seasons": {}},
    "Josh C.": {"current": ("Denver", "CO", "Mountain West"), "seasons": {}},
    "Grayson": {"current": ("Houston", "TX", "Great Plains"), "seasons": {}},
}

# ── Region Mapping & Defined Colors (per SDDREQ-94) ───────────────────────────
REGION_COLORS = {
    "Mountain West": "#A855F7",  # Purple
    "Great Plains": "#EAB308",   # Yellow
    "Midwest": "#3B82F6",        # Blue
    "The South": "#EF4444",      # Red
    "Northeast": "#22C55E",      # Green
}

STATE_TO_REGION = {
    # Mountain West
    "HI": "Mountain West", "AK": "Mountain West", "CA": "Mountain West", "OR": "Mountain West",
    "WA": "Mountain West", "ID": "Mountain West", "WY": "Mountain West", "MT": "Mountain West",
    "UT": "Mountain West", "AZ": "Mountain West", "NV": "Mountain West", "NM": "Mountain West",
    "CO": "Mountain West",
    # Great Plains
    "ND": "Great Plains", "SD": "Great Plains", "NE": "Great Plains", "KS": "Great Plains",
    "OK": "Great Plains", "TX": "Great Plains",
    # Midwest
    "MN": "Midwest", "IA": "Midwest", "MO": "Midwest", "IL": "Midwest",
    "WI": "Midwest", "MI": "Midwest", "IN": "Midwest", "OH": "Midwest",
    # The South
    "AR": "The South", "LA": "The South", "MS": "The South", "AL": "The South",
    "GA": "The South", "FL": "The South", "SC": "The South", "NC": "The South",
    "TN": "The South", "KY": "The South", "WV": "The South", "VA": "The South",
    # Northeast
    "DC": "Northeast", "DE": "Northeast", "MD": "Northeast", "PA": "Northeast",
    "NJ": "Northeast", "NY": "Northeast", "CT": "Northeast", "VT": "Northeast",
    "NH": "Northeast", "RI": "Northeast", "MA": "Northeast", "ME": "Northeast",
}

# ── Metro Area Coordinates for Map Pins ───────────────────────────────────────
METRO_COORDS = {
    "New York": {"x": 818, "y": 198, "state": "NY", "region": "Northeast", "label": "New York, NY"},
    "Rochester": {"x": 755, "y": 152, "state": "NY", "region": "Northeast", "label": "Rochester, NY"},
    "Houston": {"x": 470, "y": 475, "state": "TX", "region": "Great Plains", "label": "Houston, TX"},
    "Austin": {"x": 430, "y": 468, "state": "TX", "region": "Great Plains", "label": "Austin, TX"},
    "Chicago": {"x": 610, "y": 215, "state": "IL", "region": "Midwest", "label": "Chicago, IL"},
    "Denver": {"x": 335, "y": 265, "state": "CO", "region": "Mountain West", "label": "Denver, CO"},
    "Detroit": {"x": 672, "y": 195, "state": "MI", "region": "Midwest", "label": "Detroit, MI"},
    "Los Angeles": {"x": 105, "y": 350, "state": "CA", "region": "Mountain West", "label": "Los Angeles, CA"},
    "Charlotte": {"x": 740, "y": 340, "state": "NC", "region": "The South", "label": "Charlotte, NC"},
}

# ── Centroid Coordinates for Centered Driver Count Badges ─────────────────────
STATE_CENTROIDS = {
    "AL": (654.2, 415.5),
    "AK": (114.0, 510.2),
    "AZ": (194.4, 366.0),
    "AR": (548.8, 374.3),
    "CA": (84.3, 267.8),
    "CO": (317.3, 273.0),
    "CT": (858.8, 182.0),
    "DE": (832.0, 242.0),
    "FL": (718.1, 511.6),
    "GA": (714.2, 404.8),
    "HI": (284.1, 546.7),
    "ID": (193.0, 111.7),
    "IL": (590.5, 260.8),
    "IN": (644.2, 256.7),
    "IA": (523.4, 215.1),
    "KS": (439.5, 291.3),
    "KY": (658.1, 301.0),
    "LA": (566.1, 456.2),
    "ME": (895.2, 87.5),
    "MD": (792.0, 245.0),
    "MA": (873.7, 155.0),
    "MI": (631.9, 144.1),
    "MN": (520.2, 117.8),
    "MS": (594.0, 419.4),
    "MO": (542.9, 295.3),
    "MT": (273.2, 87.1),
    "NE": (419.6, 223.5),
    "NV": (133.1, 252.3),
    "NH": (867.4, 118.0),
    "NJ": (835.0, 212.0),
    "NM": (297.2, 374.1),
    "NY": (809.2, 157.3),
    "NC": (766.8, 333.5),
    "ND": (414.7, 92.3),
    "OH": (700.1, 237.3),
    "OK": (433.0, 361.4),
    "OR": (96.8, 118.6),
    "PA": (782.7, 212.0),
    "RI": (882.0, 175.0),
    "SC": (752.1, 380.2),
    "SD": (412.6, 163.7),
    "TN": (657.0, 342.0),
    "TX": (404.6, 452.5),
    "UT": (216.4, 249.4),
    "VT": (845.3, 127.7),
    "VA": (766.5, 282.9),
    "WA": (116.0, 48.5),
    "WV": (748.7, 264.2),
    "WI": (575.7, 151.5),
    "WY": (294.2, 181.1),
    "DC": (808.0, 268.0),
}

REGION_CENTROIDS = {
    "Mountain West": (205, 240),
    "Great Plains": (420, 290),
    "Midwest": (610, 210),
    "The South": (675, 380),
    "Northeast": (815, 175),
}



def _is_truthy(val) -> bool:
    if isinstance(val, bool):
        return val
    if val is None:
        return False
    return str(val).strip().upper() in ("Y", "YES", "TRUE", "1")


def _get_driver_loc(driver: str, season: int) -> tuple[str, str, str]:
    """Returns (metro, state, region) for a driver in a specific season per SDDREQ-95 & SDDREQ-106."""
    d_info = DRIVER_LOCATIONS.get(driver)
    if not d_info:
        return ("Unknown", "Unknown", "Unknown")
    if season in d_info["seasons"]:
        return d_info["seasons"][season]
    return d_info["current"]


# ── Global In-Memory Pre-Calculation Cache ─────────────────────────────────────
_PRECOMPUTED_MAP_CACHE: dict = {}
_PRECOMPUTED_MTIME: float = 0.0


def _build_blank_stats() -> dict:
    return {
        "driver_count": 0,
        "drivers": [],
        "driver_championships": 0,
        "constructor_championships": 0,
        "points": 0.0,
        "avg_points": 0.0,
        "wins": 0,
        "avg_wins": 0.0,
        "podiums": 0,
        "avg_podiums": 0.0,
        "poles": 0,
        "avg_poles": 0.0,
        "fastest_laps": 0,
        "avg_fastest_laps": 0.0,
        "dotd": 0,
        "avg_dotd": 0.0,
        "mot": 0,
        "avg_mot": 0.0,
        "cd": 0,
        "avg_cd": 0.0,
        "ancillary_total": 0,
        "avg_ancillary": 0.0,
    }


def precompute_all_map_data(force: bool = False) -> dict:
    """Pre-calculates all statistics across every permutation of:
    - Season Scope: All Time (1..5), Cumulative (1..N), Single (N)
    - Active Filter: All Drivers (24), Active Drivers Only (16)
    - Grouping: Region, State, Metro Area
    Stores in-memory for instant $O(1)$ lookups with zero UI latency.
    """
    global _PRECOMPUTED_MAP_CACHE, _PRECOMPUTED_MTIME
    excel_p = Path(excel_file_path)
    current_mtime = excel_p.stat().st_mtime if excel_p.exists() else 0.0

    if not force and _PRECOMPUTED_MAP_CACHE and _PRECOMPUTED_MTIME == current_mtime:
        return _PRECOMPUTED_MAP_CACHE

    # 1. Identify active drivers (drivers participating in Season 5)
    s5_df = get_excel_sheet("Season5")
    active_drivers_s5 = set(
        s5_df["Driver"].dropna().astype(str).str.strip().unique()
    ) if not s5_df.empty else set()

    # 2. Extract raw race data and champions for seasons 1 through 5
    # Raw structure: season -> driver -> stats dict
    season_driver_stats: dict[int, dict[str, dict]] = {}
    driver_champs_by_season: dict[int, str] = {}
    constructor_champs_by_season: dict[int, str] = {}
    constructor_drivers_by_season: dict[int, list[str]] = {}

    for s in range(1, 6):
        df_s = get_excel_sheet(f"Season{s}")
        if df_s.empty:
            continue
        df_s["Driver"] = df_s["Driver"].astype(str).str.strip()
        df_s["Team"] = df_s["Team"].astype(str).str.strip()

        sched = get_excel_sheet(f"S{s}Schedule")
        races = [
            str(r).strip() for r in sched["Race"]
            if not str(r).lower().startswith(("pre", "post"))
        ] if not sched.empty else []

        s_stats = defaultdict(lambda: {
            "team": "",
            "points": 0.0,
            "wins": 0,
            "podiums": 0,
            "poles": 0,
            "fastest_laps": 0,
            "dotd": 0,
            "mot": 0,
            "cd": 0,
        })

        driver_pts = defaultdict(float)
        team_pts = defaultdict(float)

        for _, row in df_s.iterrows():
            drv = row["Driver"]
            team = row["Team"]
            s_stats[drv]["team"] = team

            for r in races:
                p_col = f"{r}Points"
                pl_col = f"{r}Place"
                q_col = f"{r}Qualifying"
                fl_col = f"{r}FastestLap"
                dotd_col = f"{r}DOTD"
                mot_col = f"{r}MOT"
                cd_col = f"{r}CD"

                if p_col in row and row[p_col] is not None:
                    try:
                        p_val = float(row[p_col])
                        s_stats[drv]["points"] += p_val
                        driver_pts[drv] += p_val
                        team_pts[team] += p_val
                    except Exception:
                        pass

                if pl_col in row and row[pl_col] is not None:
                    try:
                        place = float(row[pl_col])
                        if place == 1.0:
                            s_stats[drv]["wins"] += 1
                            s_stats[drv]["podiums"] += 1
                        elif place in (2.0, 3.0):
                            s_stats[drv]["podiums"] += 1
                    except Exception:
                        pass

                if q_col in row and row[q_col] is not None:
                    try:
                        if float(row[q_col]) == 1.0:
                            s_stats[drv]["poles"] += 1
                    except Exception:
                        pass

                if fl_col in row and _is_truthy(row[fl_col]):
                    s_stats[drv]["fastest_laps"] += 1
                if dotd_col in row and _is_truthy(row[dotd_col]):
                    s_stats[drv]["dotd"] += 1
                if mot_col in row and _is_truthy(row[mot_col]):
                    s_stats[drv]["mot"] += 1
                if cd_col in row and _is_truthy(row[cd_col]):
                    s_stats[drv]["cd"] += 1

        season_driver_stats[s] = dict(s_stats)

        # Official championship rules: completed seasons have official champions
        if is_season_completed(s):
            if driver_pts:
                driver_champs_by_season[s] = max(driver_pts.items(), key=lambda x: x[1])[0]
            if team_pts:
                top_team = max(team_pts.items(), key=lambda x: x[1])[0]
                constructor_champs_by_season[s] = top_team
                winning_drivers = df_s[df_s["Team"] == top_team]["Driver"].unique().tolist()
                constructor_drivers_by_season[s] = winning_drivers

    # 3. Generate all permutations
    permutations = {}
    scopes = [("all", 0)] + [("cum", s) for s in range(1, 6)] + [("single", s) for s in range(1, 6)]
    filters = [False, True]  # False = all drivers, True = active only

    for scope_type, scope_val in scopes:
        if scope_type == "all":
            active_seasons = list(range(1, 6))
            key_prefix = "all"
        elif scope_type == "cum":
            active_seasons = list(range(1, scope_val + 1))
            key_prefix = f"cum_{scope_val}"
        else:
            active_seasons = [scope_val]
            key_prefix = f"single_{scope_val}"

        for act_only in filters:
            cache_key = f"{key_prefix}_{'active' if act_only else 'all'}"

            by_region: dict[str, dict] = {r: _build_blank_stats() for r in REGION_COLORS.keys()}
            by_state: dict[str, dict] = {st: _build_blank_stats() for st in STATE_TO_REGION.keys()}
            by_metro: dict[str, dict] = {m: _build_blank_stats() for m in METRO_COORDS.keys()}

            drivers_in_region = defaultdict(set)
            drivers_in_state = defaultdict(set)
            drivers_in_metro = defaultdict(set)

            # Aggregate statistics per season incorporating driver location at that time (SDDREQ-106)
            for s in active_seasons:
                s_data = season_driver_stats.get(s, {})
                for drv, stats in s_data.items():
                    if act_only and drv not in active_drivers_s5:
                        continue

                    metro, state, region = _get_driver_loc(drv, s)

                    # Track driver membership
                    if region in by_region:
                        drivers_in_region[region].add(drv)
                    if state in by_state:
                        drivers_in_state[state].add(drv)
                    if metro in by_metro:
                        drivers_in_metro[metro].add(drv)

                    # Accumulate metric values
                    for target_dict, key in [(by_region, region), (by_state, state), (by_metro, metro)]:
                        if key in target_dict:
                            target = target_dict[key]
                            target["points"] += stats["points"]
                            target["wins"] += stats["wins"]
                            target["podiums"] += stats["podiums"]
                            target["poles"] += stats["poles"]
                            target["fastest_laps"] += stats["fastest_laps"]
                            target["dotd"] += stats["dotd"]
                            target["mot"] += stats["mot"]
                            target["cd"] += stats["cd"]
                            target["ancillary_total"] += (
                                stats["fastest_laps"] + stats["dotd"] + stats["mot"] + stats["cd"]
                            )

            # Process championships
            # Non-season based championships are credited across completed seasons (SDDREQ-96)
            for s in active_seasons:
                d_champ = driver_champs_by_season.get(s)
                if d_champ and (not act_only or d_champ in active_drivers_s5):
                    m_c, st_c, r_c = _get_driver_loc(d_champ, s)
                    if r_c in by_region:
                        by_region[r_c]["driver_championships"] += 1
                    if st_c in by_state:
                        by_state[st_c]["driver_championships"] += 1
                    if m_c in by_metro:
                        by_metro[m_c]["driver_championships"] += 1

                c_drivers = constructor_drivers_by_season.get(s, [])
                for c_drv in c_drivers:
                    if act_only and c_drv not in active_drivers_s5:
                        continue
                    m_c, st_c, r_c = _get_driver_loc(c_drv, s)
                    if r_c in by_region:
                        by_region[r_c]["constructor_championships"] += 1
                    if st_c in by_state:
                        by_state[st_c]["constructor_championships"] += 1
                    if m_c in by_metro:
                        by_metro[m_c]["constructor_championships"] += 1

            # Finalize counts and averages per group
            for target_dict, driver_map in [
                (by_region, drivers_in_region),
                (by_state, drivers_in_state),
                (by_metro, drivers_in_metro),
            ]:
                for k, stats in target_dict.items():
                    d_list = sorted(list(driver_map.get(k, set())))
                    stats["drivers"] = d_list
                    cnt = len(d_list)
                    stats["driver_count"] = cnt
                    stats["points"] = round(stats["points"], 1)

                    if cnt > 0:
                        stats["avg_points"] = round(stats["points"] / cnt, 1)
                        stats["avg_wins"] = round(stats["wins"] / cnt, 2)
                        stats["avg_podiums"] = round(stats["podiums"] / cnt, 2)
                        stats["avg_poles"] = round(stats["poles"] / cnt, 2)
                        stats["avg_fastest_laps"] = round(stats["fastest_laps"] / cnt, 2)
                        stats["avg_dotd"] = round(stats["dotd"] / cnt, 2)
                        stats["avg_mot"] = round(stats["mot"] / cnt, 2)
                        stats["avg_cd"] = round(stats["cd"] / cnt, 2)
                        stats["avg_ancillary"] = round(stats["ancillary_total"] / cnt, 2)
                    else:
                        stats["avg_points"] = 0.0
                        stats["avg_wins"] = 0.0
                        stats["avg_podiums"] = 0.0
                        stats["avg_poles"] = 0.0
                        stats["avg_fastest_laps"] = 0.0
                        stats["avg_dotd"] = 0.0
                        stats["avg_mot"] = 0.0
                        stats["avg_cd"] = 0.0
                        stats["avg_ancillary"] = 0.0

            permutations[cache_key] = {
                "by_region": by_region,
                "by_state": by_state,
                "by_metro": by_metro,
                "active_drivers_s5": sorted(list(active_drivers_s5)),
            }

    _PRECOMPUTED_MAP_CACHE = permutations
    _PRECOMPUTED_MTIME = current_mtime
    return _PRECOMPUTED_MAP_CACHE


# Initial warm-up of precomputed dataset at module load time for zero latency
precompute_all_map_data()


# ── Reflex State for Stats Map ────────────────────────────────────────────────
class StatsMapState(rx.State):
    """Reflex state managing the interactive All Time Stats Map with zero latency."""
    grouping: str = "region"          # "region", "state", "metro"
    active_only: bool = False         # False = Inactive + Active (24), True = Active Only (16)
    season_slider: int = 6            # 1..5 = Seasons 1..5, 6 = All Seasons
    single_season_only: bool = False  # Checkbox below slider
    stat_display: str = "default"     # "default", "driver_champs", "constructor_champs", "wins", "podiums", "points", "poles", "ancillary"
    selected_group: str = "Northeast" # Current selected group
    hovered_group: str = ""
    full_screen_open: bool = False

    # ── Computed Variables ────────────────────────────────────────────────────
    @rx.var
    def current_dataset_key(self) -> str:
        if self.season_slider >= 6:
            scope = "all"
        else:
            scope = f"single_{self.season_slider}" if self.single_season_only else f"cum_{self.season_slider}"
        act = "active" if self.active_only else "all"
        return f"{scope}_{act}"

    @rx.var
    def season_display_label(self) -> str:
        if self.season_slider >= 6:
            return "All Seasons (1–5)"
        if self.single_season_only:
            return f"Season {self.season_slider} Only"
        return f"Seasons 1 – {self.season_slider}"

    @rx.var
    def active_filter_label(self) -> str:
        return "Active Only (16)" if self.active_only else "Active + Inactive (24)"

    @rx.var
    def available_groups(self) -> list[str]:
        if self.grouping == "region":
            return list(REGION_COLORS.keys())
        elif self.grouping == "metro":
            return list(METRO_COORDS.keys())
        else:
            # Sort states with drivers first, then alphabetically
            ds = precompute_all_map_data().get(self.current_dataset_key, {})
            by_st = ds.get("by_state", {})
            st_with_drivers = [st for st, v in by_st.items() if v.get("driver_count", 0) > 0]
            st_others = [st for st in by_st.keys() if st not in st_with_drivers]
            return sorted(st_with_drivers) + sorted(st_others)

    @rx.var
    def selected_group_metrics(self) -> dict:
        ds = precompute_all_map_data().get(self.current_dataset_key, {})
        if self.grouping == "region":
            data_map = ds.get("by_region", {})
            default_key = "Northeast"
        elif self.grouping == "metro":
            data_map = ds.get("by_metro", {})
            default_key = "New York"
        else:
            data_map = ds.get("by_state", {})
            default_key = "NY"

        key = self.selected_group if self.selected_group in data_map else default_key
        res = dict(data_map.get(key, _build_blank_stats()))
        res["group_name"] = key
        res["group_type"] = self.grouping

        if self.grouping == "region":
            res["region_color"] = REGION_COLORS.get(key, "#00b4da")
            res["region_name"] = key
        elif self.grouping == "metro":
            m_info = METRO_COORDS.get(key, {})
            r_name = m_info.get("region", "Northeast")
            res["region_color"] = REGION_COLORS.get(r_name, "#00b4da")
            res["region_name"] = r_name
            res["display_title"] = m_info.get("label", key)
        else:
            r_name = STATE_TO_REGION.get(key, "Unknown")
            res["region_color"] = REGION_COLORS.get(r_name, "#00b4da")
            res["region_name"] = r_name
            res["display_title"] = f"{key} ({r_name})"

        return res

    @rx.var
    def selected_group_drivers(self) -> list[str]:
        return list(self.selected_group_metrics.get("drivers", []))

    @rx.var
    def map_svg_html(self) -> str:
        return self._build_svg_markup(is_fullscreen=False)

    @rx.var
    def full_map_svg_html(self) -> str:
        return self._build_svg_markup(is_fullscreen=True)

    # ── SVG Builder ───────────────────────────────────────────────────────────
    def _build_svg_markup(self, is_fullscreen: bool = False) -> str:
        ds = precompute_all_map_data().get(self.current_dataset_key, {})
        by_region = ds.get("by_region", {})
        by_state = ds.get("by_state", {})
        by_metro = ds.get("by_metro", {})

        states_svg = []
        selected = self.selected_group

        # Helper to determine state fill and stroke
        for code, info in SVG_DATA.get("states", {}).items():
            d = info["d"]
            name = info["name"]
            region = STATE_TO_REGION.get(code, "Unknown")
            reg_color = REGION_COLORS.get(region, "#555555")

            state_stats = by_state.get(code, {})
            has_drivers = state_stats.get("driver_count", 0) > 0

            # Determine state styling depending on current grouping mode
            is_selected = False
            if self.grouping == "region":
                is_selected = (region == selected)
                fill_color = reg_color
                fill_opacity = "0.80" if is_selected else "0.38"
                stroke_color = "#00b4da" if is_selected else "rgba(255,255,255,0.4)"
                stroke_width = "3.0" if is_selected else "1.0"
            elif self.grouping == "state":
                is_selected = (code == selected)
                if is_selected:
                    fill_color = "#00b4da"
                    fill_opacity = "0.90"
                    stroke_color = "#FFFFFF"
                    stroke_width = "3.2"
                elif has_drivers:
                    fill_color = reg_color
                    fill_opacity = "0.58"
                    stroke_color = "rgba(255,255,255,0.7)"
                    stroke_width = "1.5"
                else:
                    fill_color = "#23232A"
                    fill_opacity = "0.9"
                    stroke_color = "rgba(255,255,255,0.22)"
                    stroke_width = "0.9"
            else:  # metro mode: states are subtle dark background
                r_color = REGION_COLORS.get(region, "#282830")
                fill_color = r_color
                fill_opacity = "0.22"
                stroke_color = "rgba(255,255,255,0.25)"
                stroke_width = "0.9"

            states_svg.append(
                f'<path id="st-{code}" class="state-path" d="{d}" fill="{fill_color}" '
                f'fill-opacity="{fill_opacity}" stroke="{stroke_color}" stroke-width="{stroke_width}" '
                f'onclick="window.taf1SelectMapGroup(\'{code}\')" '
                f'style="transition: all 0.25s ease; cursor: pointer;">'
                f'<title>{name} ({code}) - {region} (Click to inspect)</title></path>'
            )

        # Separator line around AK/HI
        separator_d = SVG_DATA.get("separator", "")
        sep_svg = f'<path d="{separator_d}" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="1.2" />' if separator_d else ""

        # Pins for Metro areas: ONLY showing in metro mode per requirement
        pins_svg = []
        if self.grouping == "metro":
            for m_name, coord in METRO_COORDS.items():
                cx, cy = coord["x"], coord["y"]
                m_stats = by_metro.get(m_name, {})
                m_cnt = m_stats.get("driver_count", 0)
                m_region = coord["region"]
                m_color = REGION_COLORS.get(m_region, "#00b4da")

                is_m_selected = (selected == m_name)
                pin_radius = "10" if is_m_selected else "7"
                halo_radius = "18" if is_m_selected else "13"
                pin_stroke = "#00b4da" if is_m_selected else "#FFFFFF"
                pin_stroke_w = "3.5" if is_m_selected else "2"
                halo_opacity = "0.55" if is_m_selected else "0.25"

                pins_svg.append(f"""
                <g id="pin-{m_name.replace(' ', '_')}" class="metro-pin" style="cursor: pointer;" onclick="window.taf1SelectMapGroup('{m_name}')">
                    <circle cx="{cx}" cy="{cy}" r="{halo_radius}" fill="{m_color}" fill-opacity="{halo_opacity}">
                        <animate attributeName="r" values="{pin_radius};{halo_radius};{pin_radius}" dur="2.4s" repeatCount="indefinite"/>
                        <animate attributeName="fill-opacity" values="{halo_opacity};0.05;{halo_opacity}" dur="2.4s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="{cx}" cy="{cy}" r="{pin_radius}" fill="{m_color}" stroke="{pin_stroke}" stroke-width="{pin_stroke_w}" filter="drop-shadow(0px 2px 5px rgba(0,0,0,0.9))" />
                    <text x="{cx}" y="{cy - 14}" text-anchor="middle" fill="#FFFFFF" font-family="Outfit, sans-serif" font-size="19px" font-weight="700" filter="drop-shadow(0px 1px 4px rgba(0,0,0,0.95))">
                        {m_name} ({m_cnt})
                    </text>
                    <title>{coord['label']}: {m_cnt} Driver(s) - Region: {m_region} (Click to inspect)</title>
                </g>
                """)

        # Direct Map Labels for Regions and States per requirement (replaces bottom key)
        map_labels_svg = []
        if self.grouping == "region":
            for reg_name, (cx, cy) in REGION_CENTROIDS.items():
                r_stats = by_region.get(reg_name, {})
                cnt = r_stats.get("driver_count", 0)
                reg_color = REGION_COLORS.get(reg_name, "#00b4da")
                is_r_selected = (selected == reg_name)

                stroke_color = "#00b4da" if is_r_selected else reg_color
                stroke_w = "3.5" if is_r_selected else "2.2"
                fill_bg = "#0B0B12"

                label_title = reg_name
                count_str = f"{cnt} Driver{'s' if cnt != 1 else ''}"
                pill_w = max(195, max(len(label_title), len(count_str)) * 12 + 28)
                pill_h = 58

                map_labels_svg.append(f"""
                <g class="region-label" style="pointer-events: none;">
                    <rect x="{cx - pill_w / 2}" y="{cy - pill_h / 2}" width="{pill_w}" height="{pill_h}" rx="16"
                          fill="{fill_bg}" fill-opacity="0.94" stroke="{stroke_color}" stroke-width="{stroke_w}"
                          filter="drop-shadow(0 4px 12px rgba(0,0,0,0.95))" />
                    <text x="{cx}" y="{cy - 4}" text-anchor="middle" fill="#FFFFFF"
                          font-family="Outfit, sans-serif" font-size="20px" font-weight="800"
                          filter="drop-shadow(0 1px 3px rgba(0,0,0,0.95))">
                        {label_title}
                    </text>
                    <text x="{cx}" y="{cy + 20}" text-anchor="middle" fill="{reg_color if not is_r_selected else '#00b4da'}"
                          font-family="Outfit, sans-serif" font-size="19px" font-weight="700"
                          filter="drop-shadow(0 1px 3px rgba(0,0,0,0.95))">
                        {count_str}
                    </text>
                </g>
                """)
        elif self.grouping == "state":
            for code, (cx, cy) in STATE_CENTROIDS.items():
                st_stats = by_state.get(code, {})
                cnt = st_stats.get("driver_count", 0)
                is_st_selected = (selected == code)
                region = STATE_TO_REGION.get(code, "Unknown")
                reg_color = REGION_COLORS.get(region, "#00b4da")

                if is_st_selected:
                    label_text = f"{code}: {cnt}"
                    pill_w = 76
                    pill_h = 36
                    map_labels_svg.append(f"""
                    <g class="state-label" style="pointer-events: none;">
                        <rect x="{cx - pill_w / 2}" y="{cy - pill_h / 2}" width="{pill_w}" height="{pill_h}" rx="18"
                              fill="#00b4da" fill-opacity="0.95" stroke="#FFFFFF" stroke-width="3.0"
                              filter="drop-shadow(0 3px 8px rgba(0,0,0,0.9))" />
                        <text x="{cx}" y="{cy + 6.5}" text-anchor="middle" fill="#FFFFFF"
                              font-family="Outfit, sans-serif" font-size="19px" font-weight="800"
                              filter="drop-shadow(0 1px 3px rgba(0,0,0,0.95))">
                            {label_text}
                        </text>
                    </g>
                    """)
                elif cnt > 0:
                    label_text = f"{code}: {cnt}"
                    pill_w = 76
                    pill_h = 36
                    map_labels_svg.append(f"""
                    <g class="state-label" style="pointer-events: none;">
                        <rect x="{cx - pill_w / 2}" y="{cy - pill_h / 2}" width="{pill_w}" height="{pill_h}" rx="18"
                              fill="#0C0C14" fill-opacity="0.94" stroke="{reg_color}" stroke-width="2.5"
                              filter="drop-shadow(0 3px 8px rgba(0,0,0,0.9))" />
                        <text x="{cx}" y="{cy + 6.5}" text-anchor="middle" fill="#FFFFFF"
                              font-family="Outfit, sans-serif" font-size="19px" font-weight="800"
                              filter="drop-shadow(0 1px 3px rgba(0,0,0,0.95))">
                            {label_text}
                        </text>
                    </g>
                    """)
                else:
                    # States with 0 drivers display their 2-letter state code directly centered over the state
                    map_labels_svg.append(f"""
                    <g class="state-label" style="pointer-events: none;">
                        <text x="{cx}" y="{cy + 6}" text-anchor="middle" fill="rgba(255,255,255,0.72)"
                              font-family="Outfit, sans-serif" font-size="19px" font-weight="700"
                              filter="drop-shadow(0 1px 3px rgba(0,0,0,0.95))">
                            {code}
                        </text>
                    </g>
                    """)

        w = "100%"
        h = "100%"
        view_box = SVG_DATA.get("viewBox", "0 0 959 593")

        return f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}" width="{w}" height="{h}"
             style="display: block; width: 100%; height: auto; max-height: {'80vh' if is_fullscreen else '560px'}; background: #15151A; border-radius: 14px; user-select: none;">
            <defs>
                <filter id="map-glow" x="-10%" y="-10%" width="120%" height="120%">
                    <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000000" flood-opacity="0.75" />
                </filter>
            </defs>
            <rect width="959" height="593" fill="#15151A" rx="14" />
            <g filter="url(#map-glow)">
                {''.join(states_svg)}
                {sep_svg}
            </g>
            <g>{''.join(pins_svg)}</g>
            <g class="map-labels">{''.join(map_labels_svg)}</g>
        </svg>
        """


    # ── Event Handlers ────────────────────────────────────────────────────────
    def set_grouping(self, grouping: str | list[str]):
        if isinstance(grouping, list):
            grouping = grouping[0] if grouping else "region"
        self.grouping = str(grouping)
        # Automatically choose sensible default selection
        if self.grouping == "region":
            self.selected_group = "Northeast"
        elif self.grouping == "metro":
            self.selected_group = "New York"
        else:
            self.selected_group = "NY"

    def set_active_only(self, active_only: bool):
        self.active_only = active_only

    def set_season_slider(self, val: list[int] | int | float | list[float]):
        if isinstance(val, (list, tuple)):
            self.season_slider = int(val[0]) if val else 6
        else:
            self.season_slider = int(val)

    def set_single_season_only(self, single: bool):
        self.single_season_only = single

    def select_group(self, group_id: str | list[str]):
        if isinstance(group_id, list):
            group_id = group_id[0] if group_id else ""
        group_id = str(group_id).strip()
        if not group_id:
            return

        if self.grouping == "region":
            # Map clicked state code to region if a state was clicked
            region = STATE_TO_REGION.get(group_id, group_id)
            if region in REGION_COLORS:
                self.selected_group = region
            else:
                self.selected_group = group_id
        elif self.grouping == "state":
            self.selected_group = group_id
        elif self.grouping == "metro":
            if group_id in METRO_COORDS:
                self.selected_group = group_id
            else:
                # If a state was clicked, check if it has a known metro area
                for m_name, m_info in METRO_COORDS.items():
                    if m_info.get("state") == group_id:
                        self.selected_group = m_name
                        break


# ── Region Legend Bar (rendered in real CSS with font size >= 14pt) ────────────
def region_legend_bar() -> rx.Component:
    """Responsive region legend with font size guaranteed >= 14pt (18.7px) on any device."""
    return rx.hstack(
        *[
            rx.hstack(
                rx.box(width="14px", height="14px", border_radius="4px", bg=color, border="1px solid rgba(255,255,255,0.3)"),
                rx.text(name, font_size="14pt", color="#E0E0E5", font_weight="600"),
                align="center",
                spacing="2",
            )
            for name, color in REGION_COLORS.items()
        ],
        wrap="wrap",
        spacing="5",
        padding="8px",
        width="100%",
        justify="center",
    )


# ── Detailed Stats Details Card (per SDDREQ-101) ──────────────────────────────
def stats_details_box() -> rx.Component:
    """Dedicated card displaying detailed statistics for the selected region/state/metro."""
    m = StatsMapState.selected_group_metrics

    def stat_badge(label: str, total_val: rx.Var, avg_val: rx.Var, icon_name: str) -> rx.Component:
        return rx.box(
            rx.hstack(
                rx.icon(icon_name, size=15, color="#00b4da"),
                rx.text(label, font_size="11px", color="#A0A0AA", font_weight="600"),
                spacing="2",
                align="center",
            ),
            rx.hstack(
                rx.text(total_val, font_size="17px", font_weight="800", color="white", font_family="Outfit"),
                rx.text(f"({avg_val} avg/d)", font_size="10px", color="#8E8E93", padding_top="1"),
                spacing="2",
                align="baseline",
            ),
            bg="rgba(255,255,255,0.03)",
            border="1px solid rgba(255,255,255,0.07)",
            border_radius="lg",
            padding="8px",
        )

    return rx.box(
        rx.vstack(
            # Header with inspected group title and region pill
            rx.hstack(
                rx.vstack(
                    rx.text(
                        m["display_title"],
                        font_family="Outfit",
                        font_size="20px",
                        font_weight="800",
                        color="white",
                    ),
                    rx.hstack(
                        rx.box(
                            width="9px",
                            height="9px",
                            border_radius="50%",
                            bg=m["region_color"],
                        ),
                        rx.text(
                            m["region_name"],
                            font_size="12px",
                            color=m["region_color"],
                            font_weight="700",
                        ),
                        align="center",
                        spacing="2",
                    ),
                    spacing="1",
                    align_items="start",
                ),
                rx.spacer(),
                rx.badge(
                    f"{m['driver_count']} Drivers",
                    bg="rgba(0, 180, 218, 0.15)",
                    color="#00b4da",
                    border="1px solid rgba(0, 180, 218, 0.4)",
                    border_radius="full",
                    font_size="12px",
                    font_weight="700",
                    padding_x="8px",
                    padding_y="4px",
                ),
                width="100%",
                align="center",
                padding="8px",
            ),
            # Championship Titles Row
            rx.grid(
                rx.box(
                    rx.text("Driver Titles", font_size="11px", color="#A0A0AA", font_weight="600"),
                    rx.text(m["driver_championships"], font_size="18px", font_weight="800", color="#FFD700", font_family="Outfit"),
                    bg="rgba(255, 215, 0, 0.08)",
                    border="1px solid rgba(255, 215, 0, 0.25)",
                    border_radius="lg",
                    padding="8px",
                ),
                rx.box(
                    rx.text("Constructor Titles", font_size="11px", color="#A0A0AA", font_weight="600"),
                    rx.text(m["constructor_championships"], font_size="18px", font_weight="800", color="#FF9F0A", font_family="Outfit"),
                    bg="rgba(255, 159, 10, 0.08)",
                    border="1px solid rgba(255, 159, 10, 0.25)",
                    border_radius="lg",
                    padding="8px",
                ),
                columns="2",
                spacing="3",
                width="100%",
            ),
            # Performance Metrics Grid
            rx.grid(
                stat_badge("Points", m["points"], m["avg_points"], "award"),
                stat_badge("Wins", m["wins"], m["avg_wins"], "trophy"),
                stat_badge("Podiums", m["podiums"], m["avg_podiums"], "flag"),
                stat_badge("Poles", m["poles"], m["avg_poles"], "zap"),
                columns="2",
                spacing="3",
                width="100%",
            ),
            # Race Awards row (formerly Ancillary Race Awards per requirement 4)
            rx.box(
                rx.text("Race Awards", font_size="11px", color="#8E8E93", font_weight="bold", margin_bottom="1.5"),
                rx.grid(
                    rx.vstack(
                        rx.text("Fastest Laps", font_size="10px", color="#A0A0AA"),
                        rx.text(m["fastest_laps"], font_size="15px", font_weight="800", color="white", font_family="Outfit"),
                        spacing="0",
                        align="center",
                        padding="8px",
                        bg="rgba(255,255,255,0.03)",
                        border_radius="md",
                    ),
                    rx.vstack(
                        rx.text("Driver of Day", font_size="10px", color="#A0A0AA"),
                        rx.text(m["dotd"], font_size="15px", font_weight="800", color="white", font_family="Outfit"),
                        spacing="0",
                        align="center",
                        padding="8px",
                        bg="rgba(255,255,255,0.03)",
                        border_radius="md",
                    ),
                    rx.vstack(
                        rx.text("Most Overtakes", font_size="10px", color="#A0A0AA"),
                        rx.text(m["mot"], font_size="15px", font_weight="800", color="white", font_family="Outfit"),
                        spacing="0",
                        align="center",
                        padding="8px",
                        bg="rgba(255,255,255,0.03)",
                        border_radius="md",
                    ),
                    rx.vstack(
                        rx.text("Cleanest Driver", font_size="10px", color="#A0A0AA"),
                        rx.text(m["cd"], font_size="15px", font_weight="800", color="white", font_family="Outfit"),
                        spacing="0",
                        align="center",
                        padding="8px",
                        bg="rgba(255,255,255,0.03)",
                        border_radius="md",
                    ),
                    columns="4",
                    spacing="2",
                    width="100%",
                ),
                width="100%",
                padding="8px",
                bg="rgba(0,0,0,0.25)",
                border="1px solid rgba(255,255,255,0.05)",
                border_radius="lg",
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
        bg="#18181C",
        border="1px solid #2D2D35",
        border_radius="2xl",
        padding="8px",
        box_shadow="0 8px 24px rgba(0,0,0,0.4)",
    )


# ── Save Map Dialog (per SDDREQ-99, renamed to Save Map) ──────────────────────
def save_map_dialog() -> rx.Component:
    """Save Map button & dialog for viewing map in full screen and downloading as PNG."""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("download", size=15),
                bg="#18181C",
                color="white",
                border="1px solid #2C2C32",
                _hover={"bg": "#00b4da", "border_color": "#00b4da"},
                cursor="pointer",
                padding="8px",
                border_radius="lg",
                title="Save Map",
            ),
        ),
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.dialog.title(
                        f"All Time Stats Map — {StatsMapState.grouping.capitalize()} Mode ({StatsMapState.season_display_label})",
                        color="white",
                        font_family="Outfit",
                        font_weight="800",
                        font_size="lg",
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button(
                            rx.icon("x", size=18),
                            variant="ghost",
                            color="white",
                            _hover={"bg": "#00b4da"},
                            cursor="pointer",
                            padding="1",
                        ),
                    ),
                    width="100%",
                    align="center",
                    margin_bottom="2",
                ),
                rx.box(
                    rx.html(StatsMapState.full_map_svg_html),
                    id="full_stats_map_container",
                    width="100%",
                    bg="#15151A",
                    border="1px solid #28282E",
                    border_radius="xl",
                    padding="3",
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("download", size=16),
                        rx.text("Download PNG", font_family="Outfit", font_weight="600"),
                        spacing="2",
                        align="center",
                    ),
                    on_click=lambda: DownloadState.download_chart(
                        "full_stats_map_container",
                        f"All_Time_Stats_Map_{StatsMapState.grouping}",
                    ),
                    bg="#00b4da",
                    color="white",
                    _hover={"bg": "#009bbd"},
                    cursor="pointer",
                    margin_top="3",
                    padding_x="6",
                    border_radius="lg",
                ),
                width="100%",
                align="center",
                spacing="3",
            ),
            bg="#111116",
            border="1px solid #2C2C32",
            border_radius="xl",
            max_width="96vw",
            width=["98vw", "96vw", "1180px"],
            padding="5",
        ),
    )


# ── Main View Component ───────────────────────────────────────────────────────
def stats_map_view() -> rx.Component:
    """The interactive All Time Stats Map page view component."""

    # Season Slider Control: Made the same width as the map (100% width) with responsive reactivity
    season_slider_control = rx.box(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("calendar", size=15, color="#00b4da"),
                    rx.text("Season Scope:", font_size="13px", color="white", font_weight="bold"),
                    rx.badge(
                        StatsMapState.season_display_label,
                        bg="rgba(0, 180, 218, 0.15)",
                        color="#00b4da",
                        border="1px solid rgba(0, 180, 218, 0.3)",
                        border_radius="full",
                        font_size="12px",
                        font_weight="bold",
                        padding_x="2.5",
                        padding_y="0.5",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.checkbox(
                        checked=StatsMapState.single_season_only,
                        on_change=StatsMapState.set_single_season_only,
                        size="1",
                        color_scheme="cyan",
                    ),
                    rx.text("Single Season Only", font_size="12px", color="#D0D0D5", font_weight="500"),
                    align="center",
                    spacing="2",
                ),
                width="100%",
                align="center",
                padding="8px",
            ),
            rx.box(
                rx.slider(
                    min=1,
                    max=6,
                    step=1,
                    value=[StatsMapState.season_slider],
                    on_change=StatsMapState.set_season_slider,
                    color_scheme="cyan",
                    size="2",
                    width="100%",
                ),
                width="100%",
                padding_x="28px",
                padding_top="8px",
                padding_bottom="4px",
            ),
            rx.box(
                rx.box(
                    rx.text("S1", position="absolute", left="calc(0% + 8px)", transform="translateX(-50%)", font_size="11px", color="#888", font_weight="600", white_space="nowrap", user_select="none"),
                    rx.text("S2", position="absolute", left="calc(20% + 4.8px)", transform="translateX(-50%)", font_size="11px", color="#888", font_weight="600", white_space="nowrap", user_select="none"),
                    rx.text("S3", position="absolute", left="calc(40% + 1.6px)", transform="translateX(-50%)", font_size="11px", color="#888", font_weight="600", white_space="nowrap", user_select="none"),
                    rx.text("S4", position="absolute", left="calc(60% - 1.6px)", transform="translateX(-50%)", font_size="11px", color="#888", font_weight="600", white_space="nowrap", user_select="none"),
                    rx.text("S5", position="absolute", left="calc(80% - 4.8px)", transform="translateX(-50%)", font_size="11px", color="#888", font_weight="600", white_space="nowrap", user_select="none"),
                    rx.text("ALL SEASONS", position="absolute", left="calc(100% - 8px)", transform="translateX(-50%)", font_size="11px", color="#00b4da", font_weight="700", white_space="nowrap", user_select="none"),
                    position="relative",
                    width="100%",
                    height="18px",
                ),
                width="100%",
                padding_x="28px",
                padding_top="2px",
                padding_bottom="8px",
            ),
            width="100%",
            spacing="1",
        ),
        width="100%",
        bg="#18181C",
        border="1px solid #2C2C32",
        border_radius="xl",
        padding="8px",
        margin_bottom="3",
    )

    # Side-by-side section: Map on the left (with integrated controls), Stats Details Card on the right
    map_and_stats_section = rx.flex(
        # Left: Map Container with top grouping & active toggle, map SVG, and bottom-right download button
        rx.box(
            rx.vstack(
                # Top controls connected to the top of the map box: Grouping left, Active Only toggle right
                rx.hstack(
                    rx.segmented_control.root(
                        rx.segmented_control.item("Regions", value="region"),
                        rx.segmented_control.item("States", value="state"),
                        rx.segmented_control.item("Metros", value="metro"),
                        value=StatsMapState.grouping,
                        on_change=StatsMapState.set_grouping,
                        radius="large",
                        size="2",
                        bg="#18181C",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.text("Active Only", color="white", font_size="sm", font_weight="600"),
                        rx.switch(
                            checked=StatsMapState.active_only,
                            on_change=StatsMapState.set_active_only,
                            color_scheme="cyan",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    width="100%",
                    align="center",
                    padding_x="4px",
                    padding_top="4px",
                    padding_bottom="2px",
                ),
                # Map Container
                rx.box(
                    rx.html(StatsMapState.map_svg_html),
                    width="100%",
                ),
                # Bottom controls: Download icon button justified to bottom right
                rx.hstack(
                    rx.spacer(),
                    save_map_dialog(),
                    width="100%",
                    align="center",
                    padding_x="4px",
                    padding_bottom="4px",
                ),
                width="100%",
                spacing="2",
            ),
            width=["100%", "100%", "65%"],
            bg="#15151A",
            border="1px solid #2C2C32",
            border_radius="2xl",
            padding="8px",
            flex="1",
            min_width="0",
        ),
        # Right: Detailed Stats Data Card (never over the map)
        rx.box(
            stats_details_box(),
            width=["100%", "100%", "35%"],
            min_width=["100%", "100%", "320px"],
        ),
        direction={"initial": "column", "md": "row"},
        width="100%",
        spacing="4",
        align="start",
    )

    return rx.vstack(
        # Page Title (Interactive GIS badge removed per requirement)
        rx.heading(
            "All Time Stats Map",
            size="6",
            color="white",
            font_family="Outfit",
            font_weight="800",
            margin_bottom="3",
        ),
        season_slider_control,
        map_and_stats_section,
        # Hidden input & script for direct map clicking
        rx.input(
            id="taf1_map_select_input",
            value="",
            on_change=StatsMapState.select_group,
            style={"display": "none"},
        ),
        rx.el.script(src="/stats_map.js"),
        width="100%",
        spacing="3",
    )

