import json
import os

tracks_path = os.path.join("assets", "circuit_tracks.json")
with open(tracks_path, "r", encoding="utf-8") as f:
    tracks = json.load(f)

# Define aliases
aliases = {
    "Vegas": tracks["Las Vegas"],
    "Barcelona": tracks["Spain"],
    "Hungary Sprint": tracks["Hungary"],
    "Post-Season: Monaco": tracks["Monaco"],
    "Pre-Season: Monaco": tracks["Monaco"],
    "Pre-Season: Mexico": tracks["Mexico"],
    "Pre-Season: Vegas": tracks["Las Vegas"],
    "Pre-Season: Hungary": tracks["Hungary"],
    "Pre-Season: Hungary Sprint": tracks["Hungary"],
    "Pre-Season: Silverstone": tracks["Silverstone"],
    "Pre-Season: Miami": tracks["Miami"],
}

for k, v in aliases.items():
    tracks[k] = v

with open(tracks_path, "w", encoding="utf-8") as f:
    json.dump(tracks, f)

web_path = os.path.join(".web", "public", "circuit_tracks.json")
if os.path.exists(web_path):
    with open(web_path, "w", encoding="utf-8") as f:
        json.dump(tracks, f)

print(f"Added {len(aliases)} aliases. Total tracks keys: {len(tracks)}")
