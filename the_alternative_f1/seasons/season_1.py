"""Season 1 data — 9 drivers, 5 teams, 19 races."""

from the_alternative_f1.constructor_colors import CONSTRUCTOR_COLORS

season = {
    "season_number": 1,
    "sheet_name": "Season1",
    "schedule_sheet": "S1Schedule",

    # No rookies in the inaugural season
    "rookies": set(),

    "articles": [],

    "preseason_power_rankings": [
        "McLaren",
        "Mercedes",
        "Red Bull",
        "Aston Martin",
        "Ferrari",
    ],

    "team_colors": {
        "McLaren": CONSTRUCTOR_COLORS["McLaren"],
        "Aston Martin": CONSTRUCTOR_COLORS["Aston Martin"],
        "Mercedes": CONSTRUCTOR_COLORS["Mercedes"],
        "Red Bull": CONSTRUCTOR_COLORS["Red Bull"],
        "Ferrari": CONSTRUCTOR_COLORS["Ferrari"],
    },

    "driver_colors": {
        "Nick": "#FF6A00",
        "Travis": "#FFAE00",
        "Zane": "#006F62",
        "David": "#2CB69A",
        "Erick": "#00D2BE",
        "Marcus": "#70ECE0",
        "Josh L": "darkblue",
        "Boz": "#455A94",
        "Gary": "#EF1A2D",
    },

    "super_license_points": {
        "Nick": [0] * 19,
        "Travis": [0] * 19,
        "Zane": [0] * 19,
        "David": [0] * 19,
        "Erick": [0] * 19,
        "Marcus": [0] * 19,
        "Josh L": [0] * 19,
        "Boz": [0] * 19,
        "Gary": [0] * 19,
    },

    "preseason_races": [
        {
            "name": "Pre-Season Test Barcelona",
            "results": [
                {"driver": "Nick", "team": "McLaren", "qualifying": 1, "place": 1, "points": 25, "FL": True, "DOTD": True, "CD": True, "MOT": False},
                {"driver": "Travis", "team": "McLaren", "qualifying": 2, "place": 2, "points": 18, "FL": False, "DOTD": False, "CD": True, "MOT": True},
            ]
        }
    ],
    "postseason_races": [],
}


