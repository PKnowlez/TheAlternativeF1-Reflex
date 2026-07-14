from the_alternative_f1.articles.Season5.Grid_Announcements.Haas import article as Haas_Article
from the_alternative_f1.articles.Season5.Grid_Announcements.Erick import article as Erick_Article
from the_alternative_f1.articles.Season5.Grid_Announcements.RedBull import article as RedBull_Article
from the_alternative_f1.articles.Season5.Grid_Announcements.Cadillac import article as Cadillac_Article
from the_alternative_f1.articles.Season5.Grid_Announcements.Ferrari import article as Ferrari_Article
from the_alternative_f1.articles.Season5.Grid_Announcements.McLaren import article as McLaren_Article
from the_alternative_f1.articles.Season5.Grid_Announcements.Williams import article as Williams_Article
from the_alternative_f1.articles.Season5.Tracks.Rankings import article as Rankings_Article
from the_alternative_f1.articles.Season5.Tracks.Schedule import article as Schedule_Article
from the_alternative_f1.articles.Season5.Grid_Announcements.Audi import article as Audi_Article
from the_alternative_f1.articles.Season5.Grid_Announcements.Mercedes import article as Mercedes_Article
from the_alternative_f1.articles.Season5.Grid_Announcements.TheGrid import article as TheGrid_Article

season = {
    "season_number": 5,
    "sheet_name": "Season5",
    "schedule_sheet": "S5Schedule",

    # Rookies: drivers not present in Season 4
    "rookies": {"Grayson", "Josh C.", "Randy", "Evelo"},

    "articles": [Mercedes_Article, Audi_Article, Schedule_Article, Rankings_Article, Williams_Article, 
    McLaren_Article, Ferrari_Article, Cadillac_Article, RedBull_Article, Erick_Article, Haas_Article],

    "team_colors": {
        "Ferrari": "red",
        "McLaren": "#FF6A00",
        "Red Bull": "darkblue",
        "Mercedes": "black",
        "Haas": "white",
        "Audi": "#A33E2C",
        "Cadillac": "#FFEA00",
        "Williams": "DodgerBlue",
    },

    "driver_colors": {
        "Joshua": "darkblue",
        "Eddie": "#8888c9",
        "Nick": "#FF6A00",
        "Del": "#FFAE00",
        "Patrick": "#FFEA00",
        "Josh": "#A8A153",
        "Matthew": "white",
        "Brently": "#C5C5C5",
        "Grayson": "DodgerBlue",
        "Josh C.": "#99ccff",
        "Boz": "#A33E2C",
        "Evelo": "#9E6156",
        "Jaden": "red",
        "Leo": "#ff6060",
        "Jairo": "black",
        "Randy": "#909090",
    },

    "super_license_points": {
        "Joshua":   [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Eddie":    [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Nick":     [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Del":      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Patrick":  [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Josh":     [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Matthew":  [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Brently":  [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Grayson":  [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Josh C.":  [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Boz":      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Evelo":    [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Jaden":    [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Leo":      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Jairo":    [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Randy":    [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    },

    "preseason_power_rankings": [
        "McLaren",
        "Cadillac",
        "Red Bull",
        "Ferrari",
        "Mercedes",
        "Haas",
        "Williams",
        "Audi",
    ],

    "preseason_races": [],
    "postseason_races": [],
}


