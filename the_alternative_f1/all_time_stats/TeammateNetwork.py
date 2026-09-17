"""
Teammate Network Module for The Alternative F1 Reflex Application
Implements TAF1APP-SDDFEAT-14 and downstream approved SDD Requirements:
- SDDREQ-117: Bubble per Driver (Driver's name, total points, outer circle in most recent team color)
- SDDREQ-118: Bubble Connector Lines (50/50 gradient between teammate bubbles based on team colors)
- SDDREQ-119: Bubble Map Background (Dark gray/black background identical to Driver Map)
- SDDREQ-120: Right Hand Panel (Number of drivers between, number of teams separating, path breakdown)
- SDDREQ-121: Default View (Bubbles fading forward/backward, side-to-side, slow bubbling animation)
- SDDREQ-122: Primary User Inputs - Select Two Drivers (Calculate closest mapping, highlight shortest path)
- SDDREQ-123: Secondary Driver Inputs - Select One Driver (Center driver in web connecting to all drivers and teams)
"""

import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import reflex as rx

from the_alternative_f1.all_time_stats.Functions import get_excel_sheet, PointTotals
from the_alternative_f1.constructor_colors import get_constructor_color, CONSTRUCTOR_COLORS


# ── Data Extraction & Graph Construction ──────────────────────────────────────

def build_teammate_network_data() -> Tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, Dict[str, List[Dict[str, Any]]]]]:
    """Extract all drivers, all-time career points, most recent teams, and teammate relationships.

    Returns:
        drivers_dict: {driver_name: {"name": str, "points": float, "recent_team": str, "recent_season": int, "color": str}}
        edges_list: [{"source": str, "target": str, "teams": list, "seasons": list, "color1": str, "color2": str}]
        adjacency_dict: {driver: {neighbor: [{"team": str, "season": int}]}}
    """
    # 1. Driver all-time career points
    driver_points: Dict[str, float] = defaultdict(float)
    for s in range(1, 6):
        try:
            _, _, _, _, _, dt = PointTotals(s)
            if dt is not None and not dt.empty and "Driver" in dt.columns and "Points" in dt.columns:
                for _, r in dt.iterrows():
                    d_name = str(r["Driver"]).strip()
                    if d_name and d_name != "nan":
                        driver_points[d_name] += float(r["Points"])
        except Exception:
            continue

    # 2. Most recent team & teammate relationships across seasons 1 to 5
    recent_team: Dict[str, Tuple[int, str]] = {}
    adjacency: Dict[str, Dict[str, List[Dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    all_drivers_set = set()

    for s in range(1, 6):
        try:
            df = get_excel_sheet(f"Season{s}")
            if df.empty or "Driver" not in df.columns or "Team" not in df.columns:
                continue
            sub = df[["Driver", "Team"]].dropna()
            teams_in_season: Dict[str, List[str]] = defaultdict(list)
            for _, r in sub.iterrows():
                d = str(r["Driver"]).strip()
                t = str(r["Team"]).strip()
                if d and d != "nan" and t and t != "nan":
                    all_drivers_set.add(d)
                    recent_team[d] = (s, t)
                    teams_in_season[t].append(d)

            for t, drvs in teams_in_season.items():
                for i in range(len(drvs)):
                    for j in range(i + 1, len(drvs)):
                        u, v = drvs[i], drvs[j]
                        adjacency[u][v].append({"team": t, "season": s})
                        adjacency[v][u].append({"team": t, "season": s})
        except Exception:
            continue

    # 3. Assemble drivers info
    drivers_data: Dict[str, Any] = {}
    for d in sorted(all_drivers_set):
        s_rec, t_rec = recent_team.get(d, (1, "Unknown"))
        pts = driver_points.get(d, 0.0)
        color = get_constructor_color(t_rec)
        drivers_data[d] = {
            "name": d,
            "points": round(pts, 1),
            "recent_team": t_rec,
            "recent_season": s_rec,
            "color": color,
            "direct_teammates_count": len(adjacency[d]),
        }

    # 4. Assemble unique edges list
    edges_list: List[Dict[str, Any]] = []
    seen_pairs = set()
    for u in sorted(adjacency.keys()):
        for v in sorted(adjacency[u].keys()):
            pair_key = tuple(sorted([u, v]))
            if pair_key not in seen_pairs:
                seen_pairs.add(pair_key)
                shared = adjacency[u][v]
                teams = list(dict.fromkeys([item["team"] for item in shared]))
                seasons = list(dict.fromkeys([item["season"] for item in shared]))
                edges_list.append({
                    "source": pair_key[0],
                    "target": pair_key[1],
                    "teams": teams,
                    "seasons": seasons,
                    "primary_team": teams[-1],
                    "color1": drivers_data.get(pair_key[0], {}).get("color", "#888888"),
                    "color2": drivers_data.get(pair_key[1], {}).get("color", "#888888"),
                })

    return drivers_data, edges_list, adjacency


# Pre-compute static network dataset
NETWORK_DRIVERS, NETWORK_EDGES, NETWORK_ADJACENCY = build_teammate_network_data()
ALL_DRIVER_NAMES = sorted(list(NETWORK_DRIVERS.keys()))


def compute_shortest_path(start: str, end: str) -> Optional[List[str]]:
    """BFS shortest path between two drivers on the unweighted teammate graph."""
    if start not in NETWORK_ADJACENCY or end not in NETWORK_ADJACENCY:
        return None
    if start == end:
        return [start]
    q = deque([[start]])
    visited = {start}
    while q:
        path = q.popleft()
        node = path[-1]
        for neighbor in NETWORK_ADJACENCY[node]:
            if neighbor == end:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                q.append(path + [neighbor])
    return None


def get_path_breakdown(path: List[str]) -> List[Dict[str, Any]]:
    """Build detailed step-by-step breakdown of teams and seasons for a path."""
    steps = []
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        shared = NETWORK_ADJACENCY[u].get(v, [])
        teams = [s["team"] for s in shared]
        seasons = [s["season"] for s in shared]
        primary_team = teams[-1] if teams else "Shared Team"
        primary_season = seasons[-1] if seasons else 1
        steps.append({
            "from_driver": u,
            "to_driver": v,
            "team": primary_team,
            "season": f"Season {primary_season}" if len(seasons) == 1 else f"Seasons {', '.join(str(s) for s in seasons)}",
            "from_color": NETWORK_DRIVERS.get(u, {}).get("color", "#FFFFFF"),
            "to_color": NETWORK_DRIVERS.get(v, {}).get("color", "#FFFFFF"),
            "team_color": get_constructor_color(primary_team),
        })
    return steps


def get_all_degree_layers(start_driver: str) -> Tuple[Dict[int, List[Dict[str, Any]]], float, int]:
    """Compute all degree layers (degree 1, 2, 3, ...) from start_driver via BFS.

    Returns:
        layers: {degree_int: [driver_item_dict, ...]}
        total_connection_points: float
        total_connections_count: int
    """
    if start_driver not in NETWORK_ADJACENCY:
        return {}, 0.0, 0

    dist = {start_driver: 0}
    parents: Dict[str, set] = {start_driver: set()}
    q = deque([start_driver])
    while q:
        u = q.popleft()
        for v in NETWORK_ADJACENCY[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                parents[v] = {u}
                q.append(v)
            elif dist[v] == dist[u] + 1:
                parents[v].add(u)

    layers: Dict[int, List[Dict[str, Any]]] = {}
    total_pts = 0.0
    total_count = 0

    for d in range(1, 8):
        drvs_in_d = [k for k, v in dist.items() if v == d]
        items = []
        for drv in sorted(drvs_in_d):
            info = NETWORK_DRIVERS.get(drv, {})
            pts = info.get("points", 0.0)
            total_pts += pts
            total_count += 1
            pts_str = f"{int(pts)} pts" if pts % 1 == 0 else f"{pts:.1f} pts"

            if d == 1:
                shared = NETWORK_ADJACENCY[start_driver][drv]
                teams = list(dict.fromkeys([s["team"] for s in shared]))
                seasons = list(dict.fromkeys([s["season"] for s in shared]))
                seasons_str = ", ".join(f"S{s}" for s in seasons)
                sub = f"{', '.join(teams)} ({seasons_str})"
            else:
                via = sorted(list(parents[drv]))
                sub = f"via {', '.join(via)}"

            items.append({
                "driver": drv,
                "points": pts,
                "points_str": pts_str,
                "recent_team": info.get("recent_team", "Unknown"),
                "color": info.get("color", "#FFFFFF"),
                "subtitle": sub,
            })
        layers[d] = items

    return layers, round(total_pts, 1), total_count


# ── Reflex State for Teammate Network ─────────────────────────────────────────

class TeammateNetworkState(rx.State):
    """Manages user inputs, active visualization mode, and shortest path calculations."""

    # View modes: "default", "single_driver", "two_drivers"
    mode: str = "default"

    # Selection fields
    driver_1: str = "Nick"
    driver_2: str = "Randy"
    single_driver: str = ""

    # Computed Two-Driver Metrics (SDDREQ-120 & SDDREQ-122)
    is_connected: bool = True
    drivers_between_count: int = 5
    teams_separating_count: int = 6
    path_nodes: List[str] = ["Nick", "Del", "Erick", "Leo", "Jaden", "Jairo", "Randy"]
    path_steps: List[Dict[str, Any]] = []

    # Single-Driver Metrics (SDDREQ-123)
    single_driver_points: float = 1128.0
    single_driver_team: str = "McLaren"
    single_driver_color: str = "#FF6A00"
    single_driver_total_connection_points: float = 2896.5
    single_driver_total_connections_count: int = 15

    # Degree layer driver lists, counts, and accordion open states
    deg1_drivers: List[Dict[str, Any]] = []
    deg1_count: int = 0
    deg1_open: bool = False

    deg2_drivers: List[Dict[str, Any]] = []
    deg2_count: int = 0
    deg2_open: bool = False

    deg3_drivers: List[Dict[str, Any]] = []
    deg3_count: int = 0
    deg3_open: bool = False

    deg4_drivers: List[Dict[str, Any]] = []
    deg4_count: int = 0
    deg4_open: bool = False

    deg5_drivers: List[Dict[str, Any]] = []
    deg5_count: int = 0
    deg5_open: bool = False

    deg6_drivers: List[Dict[str, Any]] = []
    deg6_count: int = 0
    deg6_open: bool = False

    deg7_drivers: List[Dict[str, Any]] = []
    deg7_count: int = 0
    deg7_open: bool = False

    # Bridge payload passed to JS canvas
    network_payload_json: str = ""

    def toggle_deg1(self):
        self.deg1_open = not self.deg1_open

    def toggle_deg2(self):
        self.deg2_open = not self.deg2_open

    def toggle_deg3(self):
        self.deg3_open = not self.deg3_open

    def toggle_deg4(self):
        self.deg4_open = not self.deg4_open

    def toggle_deg5(self):
        self.deg5_open = not self.deg5_open

    def toggle_deg6(self):
        self.deg6_open = not self.deg6_open

    def toggle_deg7(self):
        self.deg7_open = not self.deg7_open

    def on_mount(self):
        """Initialize and calculate default state on component load."""
        self._calculate_two_drivers_path()
        self._calculate_single_driver_details()
        self._update_network_payload()

    def set_mode(self, new_mode: str | list[str]):
        """Switch between Two Drivers, Single Driver, and Default Floating modes."""
        if isinstance(new_mode, list):
            new_mode = new_mode[0] if new_mode else "two_drivers"
        self.mode = str(new_mode)
        if self.mode == "two_drivers":
            # Default two driver option to Nick > Randy unless a single driver is already selected,
            # then use that as Driver 1 and Randy as the second.
            if self.single_driver and self.single_driver in NETWORK_DRIVERS:
                self.driver_1 = self.single_driver
                self.driver_2 = "Randy" if self.single_driver != "Randy" else "Nick"
            else:
                self.driver_1 = "Nick"
                self.driver_2 = "Randy"
            self._calculate_two_drivers_path()
        elif self.mode == "single_driver":
            if not self.single_driver or self.single_driver not in NETWORK_DRIVERS:
                self.single_driver = "Nick"
            self._calculate_single_driver_details()
        self._update_network_payload()

    def set_driver_1(self, driver_name: str | list[str]):
        """Set Driver 1 and recalculate path."""
        if isinstance(driver_name, list):
            driver_name = driver_name[0] if driver_name else ""
        self.driver_1 = str(driver_name).strip()
        self.mode = "two_drivers"
        self._calculate_two_drivers_path()
        self._update_network_payload()

    def set_driver_2(self, driver_name: str | list[str]):
        """Set Driver 2 and recalculate path."""
        if isinstance(driver_name, list):
            driver_name = driver_name[0] if driver_name else ""
        self.driver_2 = str(driver_name).strip()
        self.mode = "two_drivers"
        self._calculate_two_drivers_path()
        self._update_network_payload()

    def swap_drivers(self):
        """Swap Driver 1 and Driver 2."""
        d1 = self.driver_1
        self.driver_1 = self.driver_2
        self.driver_2 = d1
        self._calculate_two_drivers_path()
        self._update_network_payload()

    def _close_all_expanders(self):
        """Close all degree expander cards."""
        self.deg1_open = False
        self.deg2_open = False
        self.deg3_open = False
        self.deg4_open = False
        self.deg5_open = False
        self.deg6_open = False
        self.deg7_open = False

    def set_single_driver(self, driver_name: str | list[str]):
        """Set Single Driver and recalculate centered ego web."""
        if isinstance(driver_name, list):
            driver_name = driver_name[0] if driver_name else ""
        self.single_driver = str(driver_name).strip()
        self.mode = "single_driver"
        # Pre-assign Driver 1 to the selected driver and Driver 2 to Randy (or Nick if Randy was chosen)
        self.driver_1 = self.single_driver
        self.driver_2 = "Randy" if self.single_driver != "Randy" else "Nick"
        self._calculate_two_drivers_path()
        self._close_all_expanders()
        self._calculate_single_driver_details()
        self._update_network_payload()

    def reset_view(self):
        """Reset view to default floating spiderweb."""
        self.mode = "default"
        self.single_driver = ""
        self.driver_1 = "Nick"
        self.driver_2 = "Randy"
        self._close_all_expanders()
        self._calculate_two_drivers_path()
        self._update_network_payload()

    def handle_js_select(self, payload: str | list[str]):
        """Handle driver bubble clicked from client-side JavaScript canvas or touchscreen."""
        if isinstance(payload, list):
            payload = payload[0] if payload else ""
        if not payload:
            return
        try:
            data = json.loads(payload) if payload.startswith("{") else {"driver": payload}
            driver = data.get("driver", "")
            if not driver or driver not in NETWORK_DRIVERS:
                return

            # When a user clicks a bubble, automatically switch to single driver mode
            self.set_single_driver(driver)
        except Exception:
            pass

    def _calculate_two_drivers_path(self):
        """Run BFS shortest path algorithm and compute separation metrics (SDDREQ-120)."""
        d1 = self.driver_1
        d2 = self.driver_2
        path = compute_shortest_path(d1, d2)
        if path is not None:
            self.is_connected = True
            self.path_nodes = path
            self.path_steps = get_path_breakdown(path)
            if d1 == d2:
                self.drivers_between_count = 0
                self.teams_separating_count = 0
            else:
                self.drivers_between_count = max(0, len(path) - 2)
                self.teams_separating_count = max(1, len(path) - 1)
        else:
            self.is_connected = False
            self.path_nodes = []
            self.path_steps = []
            self.drivers_between_count = 0
            self.teams_separating_count = 0

    def _calculate_single_driver_details(self):
        """Extract ego network and all degree layers for selected single driver (SDDREQ-123)."""
        d = self.single_driver if (self.single_driver and self.single_driver in NETWORK_DRIVERS) else "Nick"
        info = NETWORK_DRIVERS.get(d, {})
        self.single_driver_points = info.get("points", 0.0)
        self.single_driver_team = info.get("recent_team", "Unknown")
        self.single_driver_color = info.get("color", "#FFFFFF")

        layers, tot_pts, tot_count = get_all_degree_layers(d)
        self.single_driver_total_connection_points = tot_pts
        self.single_driver_total_connections_count = tot_count

        self.deg1_drivers = layers.get(1, [])
        self.deg1_count = len(self.deg1_drivers)

        self.deg2_drivers = layers.get(2, [])
        self.deg2_count = len(self.deg2_drivers)

        self.deg3_drivers = layers.get(3, [])
        self.deg3_count = len(self.deg3_drivers)

        self.deg4_drivers = layers.get(4, [])
        self.deg4_count = len(self.deg4_drivers)

        self.deg5_drivers = layers.get(5, [])
        self.deg5_count = len(self.deg5_drivers)

        self.deg6_drivers = layers.get(6, [])
        self.deg6_count = len(self.deg6_drivers)

        self.deg7_drivers = layers.get(7, [])
        self.deg7_count = len(self.deg7_drivers)

    def _update_network_payload(self):
        """Prepare compact JSON string consumed by the client canvas bridge."""
        payload = {
            "mode": self.mode,
            "driver1": self.driver_1,
            "driver2": self.driver_2,
            "singleDriver": self.single_driver or "Nick",
            "pathNodes": self.path_nodes,
            "isConnected": self.is_connected,
            "drivers": [
                {
                    "id": d["name"],
                    "name": d["name"],
                    "points": d["points"],
                    "recentTeam": d["recent_team"],
                    "color": d["color"],
                }
                for d in NETWORK_DRIVERS.values()
            ],
            "edges": [
                {
                    "source": e["source"],
                    "target": e["target"],
                    "teams": e["teams"],
                    "color1": e["color1"],
                    "color2": e["color2"],
                }
                for e in NETWORK_EDGES
            ],
        }
        self.network_payload_json = json.dumps(payload)


# ── UI Components ─────────────────────────────────────────────────────────────

def _metric_box(title: str, value: Any, subtitle: str, color: str = "#00b4da") -> rx.Component:
    """Styled numerical indicator card for the Right Hand Panel."""
    return rx.box(
        rx.vstack(
            rx.text(
                title.upper(),
                font_size="10px",
                font_weight="700",
                color="#888899",
                letter_spacing="0.04em",
                white_space="nowrap",
            ),
            rx.text(
                value,
                font_size=["18px", "22px", "26px"],
                font_weight="900",
                color=color,
                line_height="1",
            ),
            rx.text(
                subtitle,
                font_size="11px",
                color="#A0A0B0",
                font_weight="500",
                white_space="nowrap",
            ),
            spacing="1",
            align_items="center",
        ),
        bg="#18181C",
        border="1px solid #2C2C32",
        border_radius="xl",
        padding=["8px", "10px"],
        flex="1",
        min_width="0",
        text_align="center",
    )


def _degree_layer_card(
    title: str,
    badge_prefix: str,
    count_var: Any,
    drivers_var: Any,
    is_open_var: Any,
    toggle_fn: Any,
    icon_name: str = "users",
    color_scheme: str = "cyan",
) -> rx.Component:
    """Collapsible card displaying drivers grouped by degree of separation matching screenshot styling."""
    return rx.cond(
        count_var > 0,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon(icon_name, size=18, color="#00b4da"),
                    rx.text(title, font_size="14px", font_weight="700", color="white"),
                    rx.spacer(),
                    rx.badge(
                        rx.text(count_var, " ", badge_prefix),
                        color_scheme=color_scheme,
                        variant="soft",
                        font_size="11px",
                    ),
                    rx.icon(
                        rx.cond(is_open_var, "chevron-up", "chevron-down"),
                        size=18,
                        color="#888899",
                    ),
                    width="100%",
                    align="center",
                    cursor="pointer",
                    on_click=toggle_fn,
                    user_select="none",
                ),
                rx.cond(
                    is_open_var,
                    rx.vstack(
                        rx.foreach(
                            drivers_var,
                            lambda tm: rx.box(
                                rx.hstack(
                                    rx.box(
                                        width="10px",
                                        height="10px",
                                        border_radius="2px",
                                        bg=tm["color"],
                                        flex_shrink="0",
                                    ),
                                    rx.vstack(
                                        rx.text(
                                            tm["driver"],
                                            font_size="13px",
                                            font_weight="700",
                                            color="white",
                                        ),
                                        rx.text(
                                            tm["subtitle"],
                                            font_size="11px",
                                            color="#888899",
                                        ),
                                        spacing="0",
                                    ),
                                    rx.spacer(),
                                    rx.text(
                                        tm["points_str"],
                                        font_size="12px",
                                        font_weight="600",
                                        color="#00b4da",
                                    ),
                                    width="100%",
                                    align="center",
                                    padding="8px 10px",
                                    bg="#131317",
                                    border="1px solid #232329",
                                    border_radius="md",
                                ),
                                width="100%",
                            ),
                        ),
                        width="100%",
                        spacing="2",
                        padding_top="2",
                    ),
                ),
                width="100%",
                spacing="2",
            ),
            bg="#18181C",
            border="1px solid #2C2C32",
            border_radius="xl",
            padding="12px",
            width="100%",
            margin_bottom="2",
        ),
        rx.box(),
    )


def right_hand_panel() -> rx.Component:
    """Right Hand Panel displaying separation metrics or driver details (SDDREQ-120)."""
    two_drivers_content = rx.cond(
        TeammateNetworkState.is_connected,
        rx.vstack(
            rx.hstack(
                _metric_box(
                    "Drivers Between",
                    TeammateNetworkState.drivers_between_count,
                    "Intermediate teammates",
                    "#00b4da",
                ),
                _metric_box(
                    "Teams Separating",
                    TeammateNetworkState.teams_separating_count,
                    "Team transition hops",
                    "#FD4BC7",
                ),
                width="100%",
                spacing="3",
            ),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("git-commit-horizontal", size=18, color="#00b4da"),
                        rx.text(
                            "Shortest Connection Path",
                            font_size="14px",
                            font_weight="700",
                            color="white",
                        ),
                        spacing="2",
                        align="center",
                        margin_bottom="2",
                    ),
                    rx.cond(
                        TeammateNetworkState.driver_1 == TeammateNetworkState.driver_2,
                        rx.text(
                            "Same driver selected. Choose two different drivers to view intermediate path.",
                            color="#888899",
                            font_size="13px",
                        ),
                        rx.vstack(
                            rx.foreach(
                                TeammateNetworkState.path_steps,
                                lambda step, idx: rx.box(
                                    rx.hstack(
                                        rx.vstack(
                                            rx.text(
                                                step["from_driver"],
                                                font_size="13px",
                                                font_weight="700",
                                                color=step["from_color"],
                                            ),
                                            rx.text(
                                                "teammate with",
                                                font_size="10px",
                                                color="#777788",
                                            ),
                                            rx.text(
                                                step["to_driver"],
                                                font_size="13px",
                                                font_weight="700",
                                                color=step["to_color"],
                                            ),
                                            spacing="0",
                                        ),
                                        rx.spacer(),
                                        rx.box(
                                            rx.vstack(
                                                rx.badge(
                                                    step["team"],
                                                    color_scheme="gray",
                                                    variant="surface",
                                                    style={"borderColor": step["team_color"], "borderWidth": "1px"},
                                                    font_size="11px",
                                                    font_weight="600",
                                                ),
                                                rx.text(
                                                    step["season"],
                                                    font_size="10px",
                                                    color="#9999AA",
                                                ),
                                                spacing="1",
                                                align="end",
                                            ),
                                        ),
                                        width="100%",
                                        align="center",
                                        padding="8px 10px",
                                        bg="#131317",
                                        border="1px solid #232329",
                                        border_radius="lg",
                                    ),
                                    width="100%",
                                ),
                            ),
                            width="100%",
                            spacing="2",
                        ),
                    ),
                    width="100%",
                    spacing="2",
                ),
                bg="#18181C",
                border="1px solid #2C2C32",
                border_radius="xl",
                padding="12px",
                width="100%",
            ),
            width="100%",
            spacing="3",
        ),
        rx.box(
            rx.vstack(
                rx.icon("triangle-alert", size=24, color="#EF4444"),
                rx.text(
                    "No Connection Found",
                    font_size="16px",
                    font_weight="700",
                    color="#EF4444",
                ),
                rx.text(
                    "No direct or indirect teammate connection exists between ",
                    TeammateNetworkState.driver_1,
                    " and ",
                    TeammateNetworkState.driver_2,
                    " across all 5 seasons.",
                    font_size="13px",
                    color="#AAAAAA",
                    text_align="center",
                ),
                rx.text(
                    "These drivers belong to completely separate driver clusters in The Alternative F1 history.",
                    font_size="12px",
                    color="#777788",
                    text_align="center",
                ),
                spacing="2",
                align="center",
                padding="20px 14px",
            ),
            bg="#1C1818",
            border="1px solid #442222",
            border_radius="xl",
            width="100%",
        ),
    )

    single_driver_content = rx.vstack(
        # Driver Profile Card with 3 metric boxes (Career Points, Connection Points, Total Connections)
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        width="14px",
                        height="14px",
                        border_radius="full",
                        bg=TeammateNetworkState.single_driver_color,
                    ),
                    rx.heading(
                        TeammateNetworkState.single_driver,
                        size="5",
                        color="white",
                        font_weight="800",
                    ),
                    rx.spacer(),
                    rx.badge(
                        TeammateNetworkState.single_driver_team,
                        color_scheme="gray",
                        variant="surface",
                        style={"borderColor": TeammateNetworkState.single_driver_color, "borderWidth": "1px"},
                        font_size="12px",
                        font_weight="700",
                    ),
                    width="100%",
                    align="center",
                ),
                rx.hstack(
                    _metric_box(
                        "Career Points",
                        TeammateNetworkState.single_driver_points,
                        "Driver total",
                        TeammateNetworkState.single_driver_color,
                    ),
                    _metric_box(
                        "Connection Pts",
                        TeammateNetworkState.single_driver_total_connection_points,
                        "All connections",
                        "#00b4da",
                    ),
                    _metric_box(
                        "Connections",
                        TeammateNetworkState.single_driver_total_connections_count,
                        "Network count",
                        "#3B82F6",
                    ),
                    width="100%",
                    spacing="2",
                    margin_top="2",
                ),
                width="100%",
                spacing="2",
            ),
            bg="#18181C",
            border="1px solid #2C2C32",
            border_radius="xl",
            padding="12px",
            width="100%",
        ),
        # Expandable Degree of Separation Cards (Direct, Secondary, Tertiary, etc.)
        rx.box(
            rx.vstack(
                _degree_layer_card(
                    "Direct Teammates",
                    "Teammates",
                    TeammateNetworkState.deg1_count,
                    TeammateNetworkState.deg1_drivers,
                    TeammateNetworkState.deg1_open,
                    TeammateNetworkState.toggle_deg1,
                    icon_name="users",
                    color_scheme="cyan",
                ),
                _degree_layer_card(
                    "Secondary Connections",
                    "Connections",
                    TeammateNetworkState.deg2_count,
                    TeammateNetworkState.deg2_drivers,
                    TeammateNetworkState.deg2_open,
                    TeammateNetworkState.toggle_deg2,
                    icon_name="network",
                    color_scheme="purple",
                ),
                _degree_layer_card(
                    "Tertiary Connections",
                    "Connections",
                    TeammateNetworkState.deg3_count,
                    TeammateNetworkState.deg3_drivers,
                    TeammateNetworkState.deg3_open,
                    TeammateNetworkState.toggle_deg3,
                    icon_name="network",
                    color_scheme="blue",
                ),
                _degree_layer_card(
                    "4th Degree Connections",
                    "Connections",
                    TeammateNetworkState.deg4_count,
                    TeammateNetworkState.deg4_drivers,
                    TeammateNetworkState.deg4_open,
                    TeammateNetworkState.toggle_deg4,
                    icon_name="network",
                    color_scheme="indigo",
                ),
                _degree_layer_card(
                    "5th Degree Connections",
                    "Connections",
                    TeammateNetworkState.deg5_count,
                    TeammateNetworkState.deg5_drivers,
                    TeammateNetworkState.deg5_open,
                    TeammateNetworkState.toggle_deg5,
                    icon_name="network",
                    color_scheme="amber",
                ),
                _degree_layer_card(
                    "6th Degree Connections",
                    "Connections",
                    TeammateNetworkState.deg6_count,
                    TeammateNetworkState.deg6_drivers,
                    TeammateNetworkState.deg6_open,
                    TeammateNetworkState.toggle_deg6,
                    icon_name="network",
                    color_scheme="ruby",
                ),
                _degree_layer_card(
                    "7th Degree Connections",
                    "Connections",
                    TeammateNetworkState.deg7_count,
                    TeammateNetworkState.deg7_drivers,
                    TeammateNetworkState.deg7_open,
                    TeammateNetworkState.toggle_deg7,
                    icon_name="network",
                    color_scheme="gray",
                ),
                width="100%",
                spacing="2",
                max_height="440px",
                overflow_y="auto",
            ),
            width="100%",
        ),
        width="100%",
        spacing="3",
    )

    default_content = rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("info", size=20, color="#00b4da"),
                rx.text(
                    "Teammate Spiderweb Overview",
                    font_size="15px",
                    font_weight="700",
                    color="white",
                ),
                spacing="2",
                align="center",
            ),
            rx.text(
                "Explore the interconnected history of drivers who have shared teams across Seasons 1 to 5. "
                "Bubbles drift dynamically with outer rings colored by each driver's most recent team.",
                font_size="13px",
                color="#AAAAAA",
                line_height="1.5",
            ),
            rx.hstack(
                _metric_box("Drivers", len(ALL_DRIVER_NAMES), "Total in network", "#00b4da"),
                _metric_box("Pairings", len(NETWORK_EDGES), "Teammate edges", "#FD4BC7"),
                width="100%",
                spacing="3",
                margin_y="2",
            ),
            rx.vstack(
                rx.text("Interactive Modes:", font_size="12px", font_weight="700", color="white"),
                rx.hstack(
                    rx.badge("1", color_scheme="cyan", variant="solid", radius="full"),
                    rx.text("Select Two Drivers to compute shortest teammate path & separation hops.", font_size="12px", color="#9999AA"),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.badge("2", color_scheme="purple", variant="solid", radius="full"),
                    rx.text("Select One Driver to center them and radiate out their extended family tree.", font_size="12px", color="#9999AA"),
                    spacing="2",
                    align="center",
                ),
                spacing="2",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        bg="#18181C",
        border="1px solid #2C2C32",
        border_radius="xl",
        padding="14px",
        width="100%",
    )

    return rx.box(
        rx.cond(
            TeammateNetworkState.mode == "two_drivers",
            two_drivers_content,
            rx.cond(
                TeammateNetworkState.mode == "single_driver",
                single_driver_content,
                default_content,
            ),
        ),
        width="100%",
    )


def teammate_network_controls() -> rx.Component:
    """Top controls bar for switching modes and selecting drivers."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                # Segmented Control for Mode ordered: Default Web, Single Driver, Two Drivers
                rx.segmented_control.root(
                    rx.segmented_control.item("Default Web", value="default"),
                    rx.segmented_control.item("Single Driver", value="single_driver"),
                    rx.segmented_control.item("Two Drivers", value="two_drivers"),
                    value=TeammateNetworkState.mode,
                    on_change=TeammateNetworkState.set_mode,
                    radius="large",
                    size={"initial": "1", "sm": "2"},
                    class_name="map-segmented-control",
                ),
                rx.spacer(),
                rx.button(
                    rx.hstack(
                        rx.icon("rotate-ccw", size=14),
                        rx.text("Reset", font_size="12px", font_weight="600"),
                        spacing="1",
                        align="center",
                    ),
                    on_click=TeammateNetworkState.reset_view,
                    variant="soft",
                    color_scheme="gray",
                    size="2",
                    cursor="pointer",
                ),
                width="100%",
                align="center",
                spacing="2",
            ),
            rx.cond(
                TeammateNetworkState.mode == "two_drivers",
                rx.hstack(
                    rx.vstack(
                        rx.text("Driver 1", font_size="11px", font_weight="600", color="#888899"),
                        rx.select(
                            ALL_DRIVER_NAMES,
                            value=TeammateNetworkState.driver_1,
                            on_change=TeammateNetworkState.set_driver_1,
                            size="2",
                            variant="surface",
                            color_scheme="cyan",
                        ),
                        spacing="1",
                        flex="1",
                    ),
                    rx.button(
                        rx.icon("arrow-left-right", size=16),
                        on_click=TeammateNetworkState.swap_drivers,
                        variant="ghost",
                        color_scheme="gray",
                        size="2",
                        margin_top="18px",
                        cursor="pointer",
                        title="Swap Drivers",
                    ),
                    rx.vstack(
                        rx.text("Driver 2", font_size="11px", font_weight="600", color="#888899"),
                        rx.select(
                            ALL_DRIVER_NAMES,
                            value=TeammateNetworkState.driver_2,
                            on_change=TeammateNetworkState.set_driver_2,
                            size="2",
                            variant="surface",
                            color_scheme="purple",
                        ),
                        spacing="1",
                        flex="1",
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                    padding_top="2px",
                ),
                rx.cond(
                    TeammateNetworkState.mode == "single_driver",
                    rx.hstack(
                        rx.vstack(
                            rx.text("Centered Driver", font_size="11px", font_weight="600", color="#888899"),
                            rx.select(
                                ALL_DRIVER_NAMES,
                                value=TeammateNetworkState.single_driver,
                                on_change=TeammateNetworkState.set_single_driver,
                                size="2",
                                variant="surface",
                                color_scheme="cyan",
                                width="220px",
                            ),
                            spacing="1",
                        ),
                        rx.spacer(),
                        spacing="2",
                        width="100%",
                        align="center",
                        padding_top="2px",
                    ),
                    rx.box(),
                ),
            ),
            width="100%",
            spacing="2",
        ),
        width="100%",
        bg="#18181C",
        border="1px solid #2C2C32",
        border_radius="xl",
        padding="10px 14px",
        margin_bottom="3",
    )


def teammate_network_view() -> rx.Component:
    """Main view for the Teammate Network feature (SDDREQ-117 through SDDREQ-123)."""
    return rx.vstack(
        rx.hstack(
            rx.heading(
                "Teammate Network",
                size="6",
                color="white",
                font_family="Outfit",
                font_weight="800",
            ),
            rx.spacer(),
            rx.badge(
                "Seasons 1 – 5",
                color_scheme="cyan",
                variant="soft",
                font_size="12px",
                font_weight="700",
            ),
            width="100%",
            align="center",
            margin_bottom="3",
        ),
        teammate_network_controls(),
        rx.flex(
            rx.box(
                rx.vstack(
                    rx.box(
                        rx.el.canvas(
                            id="teammate-network-canvas",
                            style={
                                "width": "100%",
                                "height": "560px",
                                "display": "block",
                                "borderRadius": "12px",
                                "backgroundColor": "#15151A",
                            },
                        ),
                        id="teammate-canvas-wrapper",
                        width="100%",
                        height="560px",
                        position="relative",
                        overflow="hidden",
                        border_radius="xl",
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
            rx.box(
                right_hand_panel(),
                width=["100%", "100%", "35%"],
                min_width=["100%", "100%", "320px"],
            ),
            direction={"initial": "column", "md": "row"},
            width="100%",
            spacing="4",
            align="start",
        ),
        rx.box(
            id="taf1-network-data-bridge",
            data_payload=TeammateNetworkState.network_payload_json,
            display="none",
        ),
        rx.input(
            id="taf1_network_select_input",
            value="",
            on_change=TeammateNetworkState.handle_js_select,
            style={"display": "none"},
        ),
        rx.el.script(src="/teammate_network.js?v=20260915_02"),
        width="100%",
        spacing="3",
        on_mount=TeammateNetworkState.on_mount,
    )
