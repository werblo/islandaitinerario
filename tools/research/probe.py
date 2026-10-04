"""Sonda 2: stazioni con osservazioni di nuvolosità vicino alle località del viaggio."""
import csv, io, json, math, re, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'islanda-2026-ricerca'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode('utf-8', 'replace')

PLACES = {'reykjavik': (64.1466, -21.9426), 'vik': (63.4186, -19.0060), 'fludir': (64.1372, -20.3033),
          'laugarvatn': (64.2150, -20.7300), 'strada': (64.2559, -21.1299)}
def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    return 6371 * 2 * math.asin(math.sqrt(math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2))

# METAR (IEM)
gj = json.loads(get('https://mesonet.agron.iastate.edu/geojson/network/IS__ASOS.geojson'))
metar = [(f['properties']['sid'], f['properties']['sname'], f['geometry']['coordinates'][1], f['geometry']['coordinates'][0]) for f in gj['features']]
print('METAR stations', len(metar))
for p, c in PLACES.items():
    near = sorted(metar, key=lambda s: km(c, (s[2], s[3])))[:4]
    print(' ', p, [(s[0], s[1], round(km(c, (s[2], s[3])))) for s in near])

# SYNOP: chi riporta N (nuvolosità totale) in un giorno, con coordinate da ISD
syn = get('https://www.ogimet.com/cgi-bin/getsynop?block=04&begin=202610010000&end=202610012300')
withN = {}
for line in syn.splitlines():
    parts = line.split(',')
    if len(parts) < 7: continue
    groups = parts[6].split()
    # AAXX YYGGi IIiii iRixhVV Nddff
    if len(groups) > 4 and groups[0] == 'AAXX':
        n = groups[4][0]
        withN.setdefault(parts[0], []).append(n)
isd = list(csv.DictReader(io.StringIO(get('https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv'))))
coords = {}
for r in isd:
    if r['CTRY'] == 'IC' and r['USAF'].startswith('04') and r['LAT'] and r['END'] >= '20260101':
        coords[r['USAF'][:5]] = (r['STATION NAME'], float(r['LAT']), float(r['LON']))
print('SYNOP stations', len(withN), 'with coords', sum(k in coords for k in withN))
rows = []
for sid, ns in withN.items():
    if sid in coords:
        name, la, lo = coords[sid]
        rows.append((sid, name, la, lo, ''.join(ns)))
for p, c in PLACES.items():
    near = sorted(rows, key=lambda s: km(c, (s[2], s[3])))[:6]
    print(' ', p)
    for s in near:
        print('     ', s[0], s[1], round(km(c, (s[2], s[3]))), 'km  N:', s[4])
