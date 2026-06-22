"""Season 1 data — 9 drivers, 5 teams, 19 races."""

season = {
    "season_number": 1,
    "sheet_name": "Season1",
    "schedule_sheet": "S1Schedule",

    # No rookies in the inaugural season
    "rookies": set(),

    "team_colors": {
        "McLaren": "#FF6A00",
        "Aston Martin": "teal",
        "Mercedes": "black",
        "Red Bull": "darkblue",
        "Ferrari": "red",
    },

    "driver_colors": {
        "Nick": "#FF6A00",
        "Travis": "#FFAE00",
        "Zane": "teal",
        "David": "#01C79E",
        "Erick": "black",
        "Marcus": "#909090",
        "Josh L": "darkblue",
        "Boz": "#8888c9",
        "Gary": "red",
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


