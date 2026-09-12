"""Centralized Constructor / Team Colors for The Alternative F1.

Single authoritative source for constructor colors across the application:
- All Time Stats (DriverAllTime, ConstructorAllTime, DetailedAllTime, etc.)
- Seasons (Tab1 Standings, Tab2 Results, Tab3 Stats, Tab4 Stats, Tab5 Comparisons)
- Power Rankings
- Articles and Global Components
"""

from typing import Dict

CONSTRUCTOR_COLORS: Dict[str, str] = {
    "Alpine": "#FD4BC7",         # Pink (as used in Season 2-4 and Power Rankings)
    "Aston Martin": "#006F62",   # British Racing Green
    "Ferrari": "#EF1A2D",        # Rosso Corsa Red
    "McLaren": "#FF6A00",        # Papaya Orange
    "Red Bull": "darkblue",      # Dark Blue
    "VCARB": "#1634CB",          # Royal Blue
    "AlphaTauri": "#5E8FAA",     # Matte Blue-Grey
    "Alfa Romeo": "#C92D4B",     # Crimson / Maroon
    "Mercedes": "#00D2BE",       # Silver Arrows / Petronas Turquoise
    "Haas": "#E0E0E0",           # Light Grey / White
    "Audi": "#A33E2C",           # Burnt Red / Copper
    "Cadillac": "#FFEA00",       # Racing Yellow
    "Williams": "#00A0DE",       # Heritage Blue
}

# Aliases for convenience and compatibility
TEAM_COLORS = CONSTRUCTOR_COLORS
DEFAULT_CONSTRUCTOR_COLOR = "#555555"


def get_constructor_color(constructor_name: str, default: str = DEFAULT_CONSTRUCTOR_COLOR) -> str:
    """Return the official hex/named color for any constructor.

    Args:
        constructor_name: The constructor/team name (e.g. 'Alpine', 'Ferrari').
        default: Fallback color if the constructor is not recognized.

    Returns:
        The color hex code or name.
    """
    if not constructor_name:
        return default
    return CONSTRUCTOR_COLORS.get(str(constructor_name).strip(), default)


def get_team_color(team_name: str, default: str = DEFAULT_CONSTRUCTOR_COLOR) -> str:
    """Alias for get_constructor_color."""
    return get_constructor_color(team_name, default)
