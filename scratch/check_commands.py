import urllib.request
import re

layout_ids = [
    'yas-marina-2', 'melbourne-2', 'spielberg-3', 'bahrain-3', 'baku-1',
    'interlagos-2', 'austin-1', 'montreal-6', 'shanghai-1', 'paul-ricard-3',
    'hockenheimring-4', 'hungaroring-3', 'imola-3', 'jeddah-1', 'las-vegas-1',
    'mexico-city-3', 'miami-1', 'monaco-6', 'monza-7', 'mugello-1',
    'nurburgring-4', 'portimao-1', 'lusail-1', 'sochi-1', 'silverstone-8',
    'marina-bay-4', 'spa-francorchamps-4', 'catalunya-6', 'suzuka-2',
    'istanbul-1', 'zandvoort-5'
]

headers = {'User-Agent': 'Mozilla/5.0'}
all_cmds = set()
for lid in layout_ids:
    url = f"https://raw.githubusercontent.com/julesr0y/f1-circuits-svg/main/circuits/minimal/white/{lid}.svg"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode('utf-8')
        d = text.split('<path d="')[1].split('"')[0]
        cmds = re.findall(r'[a-zA-Z]', d)
        all_cmds.update(cmds)
    except Exception as e:
        print(f"Error on {lid}: {e}")

print('Track path commands used across all circuits:', sorted(list(all_cmds)))
