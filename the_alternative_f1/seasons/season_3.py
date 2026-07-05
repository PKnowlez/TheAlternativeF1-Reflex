from the_alternative_f1.articles.Season3.HistoricalArchive import article as HistoricalArchive_Article
from the_alternative_f1.articles.Season3.MonacoMassacre import article as MonacoMassacre_Article
from the_alternative_f1.articles.Season3.ConstructorChampions import article as ConstructorChampions_Article
from the_alternative_f1.articles.Season3.McLarenStatement import article as McLarenStatement_Article
from the_alternative_f1.articles.Season3.AlpineStatement import article as AlpineStatement_Article
from the_alternative_f1.articles.Season3.COTARecap import article as COTARecap_Article
from the_alternative_f1.articles.Season3.InsiderScoopAlpine import article as InsiderScoopAlpine_Article
from the_alternative_f1.articles.Season3.RaceWeekCOTA import article as RaceWeekCOTA_Article
from the_alternative_f1.articles.Season3.CongratulationsNick import article as CongratulationsNick_Article
from the_alternative_f1.articles.Season3.AustriaRecap import article as AustriaRecap_Article
from the_alternative_f1.articles.Season3.AbuDhabiRecap import article as AbuDhabiRecap_Article
from the_alternative_f1.articles.Season3.StandingsUpdate import article as StandingsUpdate_Article
from the_alternative_f1.articles.Season3.RaceWeekAbuDhabiAustria import article as RaceWeekAbuDhabiAustria_Article
from the_alternative_f1.articles.Season3.BreakingNewsDriverSwap import article as BreakingNewsDriverSwap_Article
from the_alternative_f1.articles.Season3.MonzaRecap import article as MonzaRecap_Article
from the_alternative_f1.articles.Season3.RaceWeekMonza import article as RaceWeekMonza_Article
from the_alternative_f1.articles.Season3.CanadaRecap import article as CanadaRecap_Article
from the_alternative_f1.articles.Season3.InsiderScoopRedBull import article as InsiderScoopRedBull_Article
from the_alternative_f1.articles.Season3.RaceWeekCanada import article as RaceWeekCanada_Article
from the_alternative_f1.articles.Season3.BakuRecap import article as BakuRecap_Article
from the_alternative_f1.articles.Season3.ChinaPressReleaseUpdate import article as ChinaPressReleaseUpdate_Article
from the_alternative_f1.articles.Season3.RaceWeekBaku import article as RaceWeekBaku_Article
from the_alternative_f1.articles.Season3.ChinaPressRelease import article as ChinaPressRelease_Article
from the_alternative_f1.articles.Season3.ChinaRecap import article as ChinaRecap_Article
from the_alternative_f1.articles.Season3.RaceWeekChina import article as RaceWeekChina_Article
from the_alternative_f1.articles.Season3.SpaSpainRecap import article as SpaSpainRecap_Article
from the_alternative_f1.articles.Season3.RaceWeekSpaSpain import article as RaceWeekSpaSpain_Article
from the_alternative_f1.articles.Season3.SpaUpdate import article as SpaUpdate_Article
from the_alternative_f1.articles.Season3.RaceWeekSpa import article as RaceWeekSpa_Article
from the_alternative_f1.articles.Season3.AustraliaRecap import article as AustraliaRecap_Article
from the_alternative_f1.articles.Season3.RaceWeekAustralia import article as RaceWeekAustralia_Article
from the_alternative_f1.articles.Season3.SilverstoneRecap import article as SilverstoneRecap_Article
from the_alternative_f1.articles.Season3.RaceWeekSilverstone import article as RaceWeekSilverstone_Article
from the_alternative_f1.articles.Season3.SuzukaRecap import article as SuzukaRecap_Article

season = {
    "season_number": 3,
    "sheet_name": "Season3",
    "schedule_sheet": "S3Schedule",

    # Rookies: drivers not present in Season 2
    "rookies": {"Patrick", "Brently"},

    "articles": [
        HistoricalArchive_Article,
        MonacoMassacre_Article,
        ConstructorChampions_Article,
        McLarenStatement_Article,
        AlpineStatement_Article,
        COTARecap_Article,
        InsiderScoopAlpine_Article,
        RaceWeekCOTA_Article,
        CongratulationsNick_Article,
        AustriaRecap_Article,
        AbuDhabiRecap_Article,
        StandingsUpdate_Article,
        RaceWeekAbuDhabiAustria_Article,
        BreakingNewsDriverSwap_Article,
        MonzaRecap_Article,
        RaceWeekMonza_Article,
        CanadaRecap_Article,
        InsiderScoopRedBull_Article,
        RaceWeekCanada_Article,
        BakuRecap_Article,
        ChinaPressReleaseUpdate_Article,
        RaceWeekBaku_Article,
        ChinaPressRelease_Article,
        ChinaRecap_Article,
        RaceWeekChina_Article,
        SpaSpainRecap_Article,
        RaceWeekSpaSpain_Article,
        SpaUpdate_Article,
        RaceWeekSpa_Article,
        AustraliaRecap_Article,
        RaceWeekAustralia_Article,
        SilverstoneRecap_Article,
        RaceWeekSilverstone_Article,
        SuzukaRecap_Article,
    ],

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


