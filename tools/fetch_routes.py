"""Scarica una volta da OSRM i percorsi stradali di ogni giorno (per la mappa)
e distanza/durata di ogni tratta della sezione "Spostamenti in auto", e li
salva in routes.json, che render.py incorpora nella pagina.

Si lancia dall'azione GitHub "Aggiorna percorsi mappa" (tab Actions), perché
serve internet. Va rilanciata quando cambiano le tappe o le tratte.
"""
import json
import os
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_render_data():
    # esegue solo la parte "dati" di render.py (prima di generare la pagina)
    src = (ROOT / 'render.py').read_text(encoding='utf-8')
    ns = {}
    os.chdir(ROOT)
    exec(compile(src[:src.index("html_out = f'''")], 'render.py', 'exec'), ns)
    return ns


def osrm(coords):
    cs = ';'.join(f'{lon},{lat}' for lat, lon in coords)
    url = f'https://router.project-osrm.org/route/v1/driving/{cs}?overview=full&geometries=geojson'
    req = urllib.request.Request(url, headers={'User-Agent': 'islandaitinerario-build (github.com/werblo/islandaitinerario)'})
    with urllib.request.urlopen(req, timeout=60) as res:
        data = json.load(res)
    time.sleep(1.5)  # server demo pubblico: niente raffiche di richieste
    return data['routes'][0]


def main():
    ns = load_render_data()
    routes = {}
    for day_id, points in ns['map_points'].items():
        pts = ns['route_points'](points)
        if len(pts) < 2:
            continue
        route = osrm([(p['lat'], p['lon']) for p in pts])
        routes[day_id] = {'coords': ns['_coord_str'](points), 'geometry': route['geometry']['coordinates']}
        print(f"{day_id}: {len(route['geometry']['coordinates'])} punti, {route['distance'] / 1000:.0f} km")

    legs = {}
    for day in ns['days']:
        out = []
        for leg in day['legs']:
            a, b = ns['leg_place'](leg['from']), ns['leg_place'](leg['to'])
            if not a or not b or a == b:
                out.append({'from': leg['from'], 'to': leg['to'], 'skip': True})
                print(f"  {day['id']} {leg['from']} → {leg['to']}: località non trovata, restano i valori manuali")
                continue
            r = osrm([a, b])
            out.append({'from': leg['from'], 'to': leg['to'],
                        'km': round(r['distance'] / 1000, 1), 'min': round(r['duration'] / 60, 1)})
            print(f"  {day['id']} {leg['from']} → {leg['to']}: {r['distance'] / 1000:.0f} km, {r['duration'] / 60:.0f} min (prima {leg['km']} km, {leg['time']})")
        legs[day['id']] = out
    routes['_legs'] = legs
    (ROOT / 'routes.json').write_text(json.dumps(routes, separators=(',', ':')), encoding='utf-8')


if __name__ == '__main__':
    main()
