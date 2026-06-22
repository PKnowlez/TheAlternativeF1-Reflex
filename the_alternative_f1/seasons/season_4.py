"""Season 4 data — 14 drivers, 7 teams, 17 races."""

season = {
    "season_number": 4,
    "sheet_name": "Season4",
    "schedule_sheet": "S4Schedule",

    # Rookies: drivers not present in Season 3
    "rookies": {"Josh", "Matthew", "Leo", "Jaden", "Jairo"},

    "team_colors": {
        "Alpine": "hotpink",
        "McLaren": "#FF6A00",
        "VCARB": "blue",
        "Red Bull": "darkblue",
        "Aston Martin": "teal",
        "Ferrari": "red",
        "Mercedes": "black",
    },

    "driver_colors": {
        "Joshua": "hotpink",
        "Eddie": "#ff69b4",
        "Nick": "#FF6A00",
        "Travis": "#FFAE00",
        "Patrick": "blue",
        "Josh": "#6699CC",
        "Brently": "darkblue",
        "Matthew": "#8888c9",
        "Del": "teal",
        "Boz": "#01C79E",
        "Erick": "red",
        "Leo": "#ff6060",
        "Jaden": "black",
        "Jairo": "#909090",
    },

    "super_license_points": {
        "Joshua": [0] * 17,
        "Eddie": [0] * 17,
        "Nick": [0] * 17,
        "Travis": [0] * 17,
        "Patrick": [0] * 17,
        "Josh": [0] * 17,
        "Brently": [0] * 17,
        "Matthew": [0] * 17,
        "Del": [0] * 17,
        "Boz": [0] * 17,
        "Erick": [0] * 17,
        "Leo": [0] * 17,
        "Jaden": [0] * 17,
        "Jairo": [0] * 17,
    },

    "preseason_races": [
        {
            "name": "Pre-Season: Silverstone",
            "results": [
                {"place": "1", "driver": "Jayden", "team": "Mercedes", "qualifying": "3", "points": 25, "FL": "Yes", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "2", "driver": "Joshua", "team": "Alpine", "qualifying": "1", "points": 18, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "3", "driver": "Del", "team": "Aston Martin", "qualifying": "5", "points": 15, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "Yes"},
                {"place": "4", "driver": "Nick", "team": "McLaren", "qualifying": "2", "points": 12, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "5", "driver": "Jairo", "team": "Mercedes", "qualifying": "9", "points": 10, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "6", "driver": "Patrick", "team": "VCARB", "qualifying": "4", "points": 8, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "7", "driver": "Eddie", "team": "Alpine", "qualifying": "7", "points": 6, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "8", "driver": "Brently", "team": "Red Bull", "qualifying": "6", "points": 4, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "9", "driver": "Travis", "team": "McLaren", "qualifying": "12", "points": 3, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "10", "driver": "Matthew", "team": "Red Bull", "qualifying": "11", "points": 2, "FL": "-", "DOTD": "Yes", "MOT": "-", "CD": "-"},
                {"place": "11", "driver": "Erick", "team": "Ferrari", "qualifying": "8", "points": 1, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "12", "driver": "Josh", "team": "VCARB", "qualifying": "10", "points": 1, "FL": "-", "DOTD": "-", "MOT": "Yes", "CD": "-"},
                {"place": "DNF", "driver": "Leo", "team": "Ferrari", "qualifying": "14", "points": 0, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "DNF/S", "driver": "Boz", "team": "Aston Martin", "qualifying": "13", "points": 0, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
            ]
        }
    ],
    "postseason_races": [
        {
            "name": "Post-Season: Monaco",
            "results": [
                {"place": "1", "driver": "Josh", "team": "VCARB", "qualifying": "8", "points": 25, "FL": "Yes", "DOTD": "Yes", "MOT": "Yes", "CD": "Yes"},
                {"place": "2", "driver": "Matthew", "team": "Haas", "qualifying": "12", "points": 18, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "DNF", "driver": "Patrick", "team": "VCARB", "qualifying": "6", "points": 0, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "DNF", "driver": "Erick", "team": "McLaren", "qualifying": "9", "points": 0, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "DNF", "driver": "Jaden", "team": "Mercedes", "qualifying": "3", "points": 0, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "DNF", "driver": "Leo", "team": "Ferrari", "qualifying": "10", "points": 0, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "DNF", "driver": "Joshua", "team": "Red Bull", "qualifying": "1", "points": 0, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "DNF", "driver": "Jairo", "team": "Mercedes", "qualifying": "2", "points": 0, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "DNF", "driver": "Nick", "team": "McLaren", "qualifying": "4", "points": 0, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "DNF", "driver": "Del", "team": "Aston Martin", "qualifying": "5", "points": 0, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "DNF", "driver": "Eddie", "team": "Williams", "qualifying": "7", "points": 0, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "DNF", "driver": "Brently", "team": "Haas", "qualifying": "11", "points": 0, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "DNS", "driver": "Boz", "team": "Aston Martin", "qualifying": "DNS", "points": 0, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
                {"place": "DNS", "driver": "Travis", "team": "McLaren", "qualifying": "DNS", "points": 0, "FL": "-", "DOTD": "-", "MOT": "-", "CD": "-"},
            ]
        }
    ],
}



