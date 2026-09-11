"""Centralized race metrics module for The Alternative F1.

Calculates dynamic positions gained/lost and effective race classifications
based on active competitors per race.
"""

from typing import Any, Dict, List, Optional
import pandas as pd


def parse_status(val: Any, season_num: int = 1) -> str:
    """Parse a place or qualifying value into a status string.

    Returns: 'FINISH', 'DNF', 'DNS', 'DSQ', or 'EMPTY'.
    """
    if val is None or pd.isnull(val):
        return "EMPTY"

    str_val = str(val).strip().upper()
    if str_val in ("", "-", "NONE", "NAN", "NULL"):
        return "EMPTY"

    # Check for text codes
    if "DNS" in str_val:
        return "DNS"
    if "DSQ" in str_val:
        return "DSQ"
    if "DNF" in str_val:
        return "DNF"

    try:
        num = float(str_val)
    except ValueError:
        return "EMPTY"

    # Numeric status codes in the 20s
    if season_num <= 4:
        if num == 21.0:
            return "DNF"
        elif num == 22.0:
            return "DNS"
        elif num == 23.0:
            return "DSQ"
    else:
        if num == 23.0:
            return "DNF"
        elif num == 24.0:
            return "DNS"
        elif num == 25.0:
            return "DSQ"

    return "FINISH"


def get_race_metrics(
    df: pd.DataFrame,
    place_col: str,
    qual_col: Optional[str],
    season_num: int,
    starting_col: Optional[str] = None,
) -> Dict[str, Any]:
    """Compute dynamic metrics for a single race column.

    A driver 'actually competed' if their race place is not DNS (and not empty).
    - N_competed is the total number of drivers who actually competed.
    - If a driver DNF/DSQ, their effective place is N_competed.
    - If a driver DNS/DNF in qualifying but competed in the race:
      - If starting_col is populated (Season 5+), use starting_col.
      - Otherwise, they started at the back of the grid (effective qualifying = N_competed).
    - If a driver DNS the race, they did not compete (competed = False).

    Returns a dict with:
        'n_competed': int
        'drivers': {
            driver_name: {
                'competed': bool,
                'effective_place': Optional[float],
                'effective_qual': Optional[float],
                'effective_start': Optional[float],
                'pos_change': Optional[float],
            }
        }
    """
    if place_col not in df.columns:
        return {"n_competed": 0, "drivers": {}}

    # Auto-detect starting column for Season 5+ if not provided
    if starting_col is None and season_num >= 5:
        candidate_start = place_col.replace("Place", "Starting")
        if candidate_start in df.columns:
            starting_col = candidate_start

    # Find who actually competed
    competitors = []
    for _, row in df.iterrows():
        driver = str(row.get("Driver", "")).strip()
        p_val = row.get(place_col)
        status_p = parse_status(p_val, season_num)
        if status_p not in ("EMPTY", "DNS"):
            competitors.append(driver)

    n_competed = len(competitors)
    drivers_data: Dict[str, Dict[str, Any]] = {}

    for _, row in df.iterrows():
        driver = str(row.get("Driver", "")).strip()
        p_val = row.get(place_col)
        status_p = parse_status(p_val, season_num)

        if status_p in ("EMPTY", "DNS") or n_competed == 0:
            drivers_data[driver] = {
                "competed": False,
                "effective_place": None,
                "effective_qual": None,
                "effective_start": None,
                "pos_change": None,
            }
            continue

        # Finishing place
        if status_p in ("DNF", "DSQ"):
            effective_p = float(n_competed)
        else:
            try:
                effective_p = float(p_val)
            except (ValueError, TypeError):
                effective_p = float(n_competed)

        # Qualifying position
        effective_q = None
        if qual_col and qual_col in df.columns:
            q_val = row.get(qual_col)
            status_q = parse_status(q_val, season_num)
            if status_q in ("EMPTY", "DNS", "DNF", "DSQ"):
                # Started at the back of the grid among competitors
                effective_q = float(n_competed)
            else:
                try:
                    q_num = float(q_val)
                    effective_q = q_num if q_num > 0 else float(n_competed)
                except (ValueError, TypeError):
                    effective_q = float(n_competed)
        else:
            effective_q = None

        # Starting position (populated if driver DNF, DNS, DSQ in qualifying but joined for the race)
        start_val = None
        if starting_col and starting_col in df.columns and season_num >= 5:
            s_raw = row.get(starting_col)
            if s_raw is not None and not pd.isnull(s_raw):
                s_str = str(s_raw).strip()
                if s_str not in ("", "-", "NONE", "NAN", "NULL"):
                    try:
                        start_val = float(s_str)
                    except (ValueError, TypeError):
                        start_val = None

        # For positions gained/lost, use starting column value if populated, else qualifying
        if start_val is not None and start_val > 0:
            effective_start = start_val
        else:
            effective_start = effective_q

        pos_change = (effective_start - effective_p) if (effective_start is not None and effective_p is not None) else None

        drivers_data[driver] = {
            "competed": True,
            "effective_place": effective_p,
            "effective_qual": effective_start if effective_start is not None else effective_q,
            "effective_start": effective_start,
            "raw_effective_qual": effective_q,
            "pos_change": pos_change,
        }

    return {
        "n_competed": n_competed,
        "drivers": drivers_data,
    }
