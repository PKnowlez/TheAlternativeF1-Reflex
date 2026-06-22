"""Seasons package — imports all season data files and exposes them as a list."""

from .season_1 import season as season_1
from .season_2 import season as season_2
from .season_3 import season as season_3
from .season_4 import season as season_4
from .season_5 import season as season_5

# Ordered list of all seasons (add new seasons here)
seasons = [season_1, season_2, season_3, season_4, season_5]

# Dynamically derived from the list length
LATEST_SEASON = len(seasons)
