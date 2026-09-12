"""Season 2 data — 13 drivers, 7 teams, 10 races."""

from the_alternative_f1.constructor_colors import CONSTRUCTOR_COLORS

season = {
    "season_number": 2,
    "sheet_name": "Season2",
    "schedule_sheet": "S2Schedule",

    # Rookies: drivers not present in Season 1
    "rookies": {"Del", "Joshua", "Eddie", "Yeti"},

    "articles": [],

    "preseason_power_rankings": [
        "Mercedes",
        "McLaren",
        "Ferrari",
        "Alpine",
        "Red Bull",
        "Alfa Romeo",
        "AlphaTauri",
    ],

    "team_colors": {
        "McLaren": CONSTRUCTOR_COLORS["McLaren"],
        "Mercedes": CONSTRUCTOR_COLORS["Mercedes"],
        "Ferrari": CONSTRUCTOR_COLORS["Ferrari"],
        "Alpine": CONSTRUCTOR_COLORS["Alpine"],
        "Red Bull": CONSTRUCTOR_COLORS["Red Bull"],
        "Alfa Romeo": CONSTRUCTOR_COLORS["Alfa Romeo"],
        "AlphaTauri": CONSTRUCTOR_COLORS["AlphaTauri"],
    },

    "driver_colors": {
        "Nick": "#FF6A00",
        "Gary": "#FFAE00",
        "Del": "#00D2BE",
        "Boz": "#70ECE0",
        "Erick": "#EF1A2D",
        "David": "#FF6B7A",
        "Joshua": "#FD4BC7",
        "Eddie": "#FFA0E0",
        "Zane": "darkblue",
        "Marcus": "#455A94",
        "Josh L": "#8B0000",
        "Yeti": "#C54E62",
        "Travis": "#5E7A96",
    },

    "super_license_points": {
        "Nick": [0] * 10,
        "Gary": [0] * 10,
        "Del": [0] * 10,
        "Boz": [0] * 10,
        "Erick": [0] * 10,
        "David": [0] * 10,
        "Joshua": [0] * 10,
        "Eddie": [0] * 10,
        "Zane": [0] * 10,
        "Marcus": [0] * 10,
        "Josh L": [0] * 10,
        "Yeti": [0] * 10,
        "Travis": [0] * 10,
    },

    "preseason_races": [],
    "postseason_races": [],
}


