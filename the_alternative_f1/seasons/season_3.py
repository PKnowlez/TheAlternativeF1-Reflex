"""Season 3 data — 14 drivers, 6 teams, 15 races."""

season = {
    "season_number": 3,
    "sheet_name": "Season3",
    "schedule_sheet": "S3Schedule",

    # Rookies: drivers not present in Season 2
    "rookies": {"Patrick", "Brently"},

    "articles": [],

    "team_colors": {
        "McLaren": "#FF6A00",
        "VCARB": "blue",
        "Ferrari": "red",
        "Alpine": "hotpink",
        "Red Bull": "darkblue",
        "Aston Martin": "teal",
    },

    "driver_colors": {
        "Nick": "#FF6A00",
        "Travis": "#FFAE00",
        "Patrick": "blue",
        "Brently": "#6699CC",
        "Erick": "red",
        "Zane": "#ff6060",
        "Del": "#C92020",
        "Eddie": "hotpink",
        "Joshua": "#ff69b4",
        "Yeti": "darkblue",
        "Boz": "#8888c9",
        "Gary": "teal",
    },

    "super_license_points": {
        "Nick": [0] * 15,
        "Travis": [0] * 15,
        "Patrick": [0] * 15,
        "Brently": [0] * 15,
        "Erick": [0] * 15,
        "Zane": [0] * 15,
        "Del": [0] * 15,
        "Eddie": [0] * 15,
        "Joshua": [0] * 15,
        "Yeti": [0] * 15,
        "Boz": [0] * 15,
        "Gary": [0] * 15,
    },

    "preseason_races": [
        {
            "name": "Pre-Season: Miami",
            "results": [
                {"place": "1", "driver": "Joshua"},
                {"place": "2", "driver": "Nick"},
                {"place": "3", "driver": "Patrick"},
                {"place": "4", "driver": "Erick"},
                {"place": "5", "driver": "Yeti"},
                {"place": "6", "driver": "Boz"},
                {"place": "7", "driver": "Del"},
                {"place": "8", "driver": "Gary"}                
            ]
        }
    ],
    "postseason_races": [
        {
            "name": "Post-Season: Monaco",
            "results": [
                {"place": "1", "driver": "Brently", "qualifying": "3"}, 
                {"place": "10", "driver": "Joshua", "qualifying": "15"}, 
                {"place": "17", "driver": "Boz", "qualifying": "19"}, 
                {"place": "DNF", "driver": "Nick", "qualifying": "2"}, 
                {"place": "DNF", "driver": "Del", "qualifying": "1"}, 
                {"place": "DNF", "driver": "Eddie", "qualifying": "18"},             
            ]
        }
    ],
}


