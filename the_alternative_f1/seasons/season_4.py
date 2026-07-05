from the_alternative_f1.articles.Season4.LiveryRanking2026 import article as LiveryRanking2026_Article
from the_alternative_f1.articles.Season4.PowerRankings import article as PowerRankings_Article
from the_alternative_f1.articles.Season4.MonacoRecap import article as MonacoRecap_Article
from the_alternative_f1.articles.Season4.Trophies import article as Trophies_Article
from the_alternative_f1.articles.Season4.MonzaRecap import article as MonzaRecap_Article
from the_alternative_f1.articles.Season4.Champions import article as Champions_Article
from the_alternative_f1.articles.Season4.MonzaWeek import article as MonzaWeek_Article
from the_alternative_f1.articles.Season4.AbuDhabiRecap import article as AbuDhabiRecap_Article
from the_alternative_f1.articles.Season4.AbuDhabiWeek import article as AbuDhabiWeek_Article
from the_alternative_f1.articles.Season4.JeddahVegasRecap import article as JeddahVegasRecap_Article
from the_alternative_f1.articles.Season4.StandingsRumors import article as StandingsRumors_Article
from the_alternative_f1.articles.Season4.ZandvoortRecap import article as ZandvoortRecap_Article
from the_alternative_f1.articles.Season4.ZandvoortWeek import article as ZandvoortWeek_Article
from the_alternative_f1.articles.Season4.AustriaRecap import article as AustriaRecap_Article
from the_alternative_f1.articles.Season4.BrazilRecapAustriaWeek import article as BrazilRecapAustriaWeek_Article
from the_alternative_f1.articles.Season4.BrazilFIA import article as BrazilFIA_Article
from the_alternative_f1.articles.Season4.BrazilWeek import article as BrazilWeek_Article
from the_alternative_f1.articles.Season4.SpaRecap import article as SpaRecap_Article
from the_alternative_f1.articles.Season4.SpaFIA import article as SpaFIA_Article
from the_alternative_f1.articles.Season4.SpaWeek import article as SpaWeek_Article
from the_alternative_f1.articles.Season4.AustriaRRecap import article as AustriaRRecap_Article
from the_alternative_f1.articles.Season4.AustriaRWeek import article as AustriaRWeek_Article
from the_alternative_f1.articles.Season4.BakuRecap import article as BakuRecap_Article
from the_alternative_f1.articles.Season4.BakuWeek import article as BakuWeek_Article
from the_alternative_f1.articles.Season4.MexicoRecap import article as MexicoRecap_Article
from the_alternative_f1.articles.Season4.Nick1000 import article as Nick1000_Article
from the_alternative_f1.articles.Season4.MexicoWeek import article as MexicoWeek_Article
from the_alternative_f1.articles.Season4.SpainFIA import article as SpainFIA_Article
from the_alternative_f1.articles.Season4.SpainRecap import article as SpainRecap_Article
from the_alternative_f1.articles.Season4.SpainWeek import article as SpainWeek_Article
from the_alternative_f1.articles.Season4.MiamiRecap import article as MiamiRecap_Article
from the_alternative_f1.articles.Season4.MiamiFIA import article as MiamiFIA_Article
from the_alternative_f1.articles.Season4.MiamiWeek import article as MiamiWeek_Article
from the_alternative_f1.articles.Season4.BahrainRecap import article as BahrainRecap_Article
from the_alternative_f1.articles.Season4.BahrainWeek import article as BahrainWeek_Article
from the_alternative_f1.articles.Season4.Preseason import article as Preseason_Article
from the_alternative_f1.articles.Season4.ROTYAward import article as ROTYAward_Article
from the_alternative_f1.articles.Season4.TrackRankings import article as TrackRankings_Article
from the_alternative_f1.articles.Season4.TrackTierList import article as TrackTierList_Article
from the_alternative_f1.articles.Season4.TrophyReveal import article as TrophyReveal_Article
from the_alternative_f1.articles.Season4.ScheduleReveal import article as ScheduleReveal_Article
from the_alternative_f1.articles.Season4.TrackOverview import article as TrackOverview_Article

"""Season 4 data — 14 drivers, 7 teams, 17 races."""

season = {
    "season_number": 4,
    "sheet_name": "Season4",
    "schedule_sheet": "S4Schedule",

    # Rookies: drivers not present in Season 3
    "rookies": {"Josh", "Matthew", "Leo", "Jaden", "Jairo"},

    "articles": [
        LiveryRanking2026_Article,
        PowerRankings_Article,
        MonacoRecap_Article,
        Trophies_Article,
        MonzaRecap_Article,
        Champions_Article,
        MonzaWeek_Article,
        AbuDhabiRecap_Article,
        AbuDhabiWeek_Article,
        JeddahVegasRecap_Article,
        StandingsRumors_Article,
        ZandvoortRecap_Article,
        ZandvoortWeek_Article,
        AustriaRecap_Article,
        BrazilRecapAustriaWeek_Article,
        BrazilFIA_Article,
        BrazilWeek_Article,
        SpaRecap_Article,
        SpaFIA_Article,
        SpaWeek_Article,
        AustriaRRecap_Article,
        AustriaRWeek_Article,
        BakuRecap_Article,
        BakuWeek_Article,
        MexicoRecap_Article,
        Nick1000_Article,
        MexicoWeek_Article,
        SpainFIA_Article,
        SpainRecap_Article,
        SpainWeek_Article,
        MiamiRecap_Article,
        MiamiFIA_Article,
        MiamiWeek_Article,
        BahrainRecap_Article,
        BahrainWeek_Article,
        Preseason_Article,
        ROTYAward_Article,
        TrackRankings_Article,
        TrackTierList_Article,
        TrophyReveal_Article,
        ScheduleReveal_Article,
        TrackOverview_Article,
    ],

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
        "Joshua": [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        "Eddie": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "Nick": [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "Travis": [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "Patrick": [0] * 17,
        "Josh": [0] * 17,
        "Brently": [0] * 17,
        "Matthew": [0] * 17,
        "Del": [0] * 17,
        "Boz": [0] * 17,
        "Erick": [0] * 17,
        "Leo": [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        "Jaden": [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
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



