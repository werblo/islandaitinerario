"""Scarica una volta i percorsi stradali (OSRM) di ogni giorno e li salva in
routes.json, che render.py incorpora nella pagina per l'uso offline.

Si lancia dall'azione GitHub "Aggiorna percorsi mappa" (tab Actions), perché
serve internet. Va rilanciata solo se cambiano le tappe in map_points.
"""
import ast
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_map_points():
    tree = ast.parse((ROOT / 'render.py').read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, 'id', None) == 'map_points' for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit('map_points non trovato in render.py')


def coord_str(points):
    # stesso formato usato da render.py e dalla vecchia chiamata runtime
    return ';'.join(f"{p['lon']},{p['lat']}" for p in points)


def main():
    routes = {}
    for day_id, points in load_map_points().items():
        if len(points) < 2:
            continue
        cs = coord_str(points)
        url = f'https://router.project-osrm.org/route/v1/driving/{cs}?overview=full&geometries=geojson'
        req = urllib.request.Request(url, headers={'User-Agent': 'islandaitinerario-build (github.com/werblo/islandaitinerario)'})
        with urllib.request.urlopen(req, timeout=60) as res:
            data = json.load(res)
        route = data['routes'][0]
        routes[day_id] = {'coords': cs, 'geometry': route['geometry']['coordinates']}
        print(f"{day_id}: {len(route['geometry']['coordinates'])} punti, {route['distance'] / 1000:.0f} km")
        time.sleep(1.5)  # server demo pubblico: niente raffiche di richieste
    (ROOT / 'routes.json').write_text(json.dumps(routes, separators=(',', ':')), encoding='utf-8')


if __name__ == '__main__':
    main()
