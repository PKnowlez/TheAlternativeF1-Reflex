import os
import urllib.request
import resvg_py
from PIL import Image
import io
import json

race_to_layout = {
    'Abu Dhabi': ('yas-marina-2', 99, 'counter-clockwise'),
    'Australia': ('melbourne-2', -46, 'clockwise'),
    'Austria': ('spielberg-3', -31, 'clockwise'),
    'Austria Reverse': ('spielberg-3', -31, 'clockwise'),
    'Austria Sprint': ('spielberg-3', -31, 'clockwise'),
    'Bahrain': ('bahrain-3', 0, 'clockwise'),
    'Bahrain Sprint': ('bahrain-3', 0, 'clockwise'),
    'Baku': ('baku-1', 73, 'counter-clockwise'),
    'Brazil': ('interlagos-2', 90, 'counter-clockwise'),
    'Brazil Sprint': ('interlagos-2', 90, 'counter-clockwise'),
    'COTA': ('austin-1', 30, 'counter-clockwise'),
    'COTA Sprint': ('austin-1', 30, 'counter-clockwise'),
    'Canada': ('montreal-6', -55, 'clockwise'),
    'China': ('shanghai-1', 24, 'clockwise'),
    'China Sprint': ('shanghai-1', 24, 'clockwise'),
    'France': ('paul-ricard-3', 0, 'clockwise'),
    'Germany': ('hockenheimring-4', 0, 'clockwise'),
    'Hungary': ('hungaroring-3', 52, 'clockwise'),
    'Imola': ('imola-3', 0, 'counter-clockwise'),
    'Jeddah': ('jeddah-1', 0, 'counter-clockwise'),
    'Las Vegas': ('las-vegas-1', 0, 'counter-clockwise'),
    'Mexico': ('mexico-city-3', -8, 'clockwise'),
    'Miami': ('miami-1', -18, 'counter-clockwise'),
    'Miami Sprint': ('miami-1', -18, 'counter-clockwise'),
    'Monaco': ('monaco-6', 45, 'clockwise'),
    'Monza': ('monza-7', -95, 'clockwise'),
    'Mugello': ('mugello-1', 0, 'clockwise'),
    'Nurburgring': ('nurburgring-4', 0, 'clockwise'),
    'Portugal': ('portimao-1', 0, 'clockwise'),
    'Qatar': ('lusail-1', 0, 'clockwise'),
    'Russia': ('sochi-1', 0, 'clockwise'),
    'Saudi Arabia': ('jeddah-1', 0, 'counter-clockwise'),
    'Silverstone': ('silverstone-8', 90, 'clockwise'),
    'Silverstone Sprint': ('silverstone-8', 90, 'clockwise'),
    'Singapore': ('marina-bay-4', 0, 'counter-clockwise'),
    'Singapore Sprint': ('marina-bay-4', 0, 'counter-clockwise'),
    'Spa': ('spa-francorchamps-4', -100, 'clockwise'),
    'Spa Sprint': ('spa-francorchamps-4', -100, 'clockwise'),
    'Spain': ('catalunya-6', 32, 'clockwise'),
    'Suzuka': ('suzuka-2', 0, 'clockwise'),
    'Turkey': ('istanbul-1', 0, 'counter-clockwise'),
    'Zandvoort': ('zandvoort-5', 0, 'clockwise'),
    'Zandvoort Sprint': ('zandvoort-5', 0, 'clockwise'),
}

print(f"Total mapped races: {len(race_to_layout)}")
