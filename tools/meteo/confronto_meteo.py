"""Confronto delle previsioni meteo per Reykjavík (chiesto da Michele l'8/11, fino al 14/11).

Quale fonte ci azzecca di più: Open-Meteo (quella dell'app), met.no (servizio norvegese) e
vedur.is (servizio meteo islandese)? Ogni esecuzione salva le previsioni ora per ora dei
prossimi giorni ("raccogli"); "valuta" le confronta con il tempo osservato all'aeroporto di
Reykjavík (METAR di BIRK, archivio IEM) e scrive RISULTATI.md.

Si confrontano: nuvole (in tutte le ore e la sera, 16-23 UTC, quella che conta per l'aurora),
pioggia/neve sì o no, temperatura e vento. Per le nuvole c'è anche "app": la media di più
modelli con il metodo di CLOUD_METHOD (come app e avvisi).

Uso:  python3 tools/meteo/confronto_meteo.py raccogli <cartella>
      python3 tools/meteo/confronto_meteo.py valuta <cartella>
"""
import csv, json, math, os, re, sys, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import aurora_alert as aa   # stesso calcolo delle nuvole di app e avvisi

UTC = timezone.utc
LAT, LON = 64.1466, -21.9426          # Reykjavík (come in dati.py)
UA = 'islanda-2026-confronto-meteo (github.com/werblo/islandaitinerario)'
OPEN_METEO = ('https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
              '&hourly=cloud_cover,precipitation,temperature_2m,wind_speed_10m'
              '&wind_speed_unit=ms&timezone=UTC&forecast_days=5')
MET_NO = 'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}'
VEDUR = 'https://xmlweather.vedur.is/?op_w=xml&type=forec&lang=en&view=xml&ids=1&params=F;T;N;R'
IEM = ('https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=BIRK&data=metar'
       '&year1={a.year}&month1={a.month}&day1={a.day}&year2={b.year}&month2={b.month}&day2={b.day}'
       '&tz=Etc/UTC&format=onlycomma&latlon=no&missing=M&trace=T&direct=no&report_type=3&report_type=4')
F_PREV = ['emessa', 'fonte', 'ora', 'nuvole', 'pioggia', 'temp', 'vento']


def fetch(url, kind='json'):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return json.loads(data) if kind == 'json' else data.decode('utf-8', 'replace')


def num(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def hour_iso(t):
    return t.astimezone(UTC).strftime('%Y-%m-%dT%H:00')


# ---------- previsioni ----------
def from_open_meteo():
    h = fetch(OPEN_METEO.format(lat=LAT, lon=LON))['hourly']
    return [(t, num(h['cloud_cover'][i]), num(h['precipitation'][i]), num(h['temperature_2m'][i]),
             num(h['wind_speed_10m'][i])) for i, t in enumerate(h['time'])]


def from_app():   # nuvole come le calcola l'app (CLOUD_METHOD, più modelli insieme)
    trip = aa.trip_data()
    loc = {'lat': LAT, 'lon': LON}
    by_hour = aa.clouds_by_hour(fetch(aa.clouds_url(loc, trip)), trip)
    return [(t, c, None, None, None) for t, c in sorted(by_hour.items())]


def from_met_no():
    out = []
    for p in fetch(MET_NO.format(lat=LAT, lon=LON))['properties']['timeseries']:
        d = p['data']['instant']['details']
        nxt = p['data'].get('next_1_hours')   # pioggia oraria solo nei primi 2-3 giorni
        out.append((p['time'][:13] + ':00', num(d.get('cloud_area_fraction')),
                    num(nxt['details'].get('precipitation_amount')) if nxt else None,
                    num(d.get('air_temperature')), num(d.get('wind_speed'))))
    return out


def from_vedur():
    root = ET.fromstring(fetch(VEDUR, 'text'))
    out, prev = [], None
    for f in root.iter('forecast'):
        t = f.findtext('ftime', '').replace(' ', 'T')[:13] + ':00'
        # R è la pioggia dell'ultima ora solo dove i passi sono di 1 ora
        step = (datetime.fromisoformat(t) - prev).total_seconds() / 3600 if prev else 1
        prev = datetime.fromisoformat(t)
        out.append((t, num(f.findtext('N')), num(f.findtext('R')) if step == 1 else None,
                    num(f.findtext('T')), num(f.findtext('F'))))
    return out


SOURCES = {'Open-Meteo': from_open_meteo, 'app (media modelli)': from_app,
           'met.no': from_met_no, 'vedur.is': from_vedur}


def raccogli(d):
    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    path = os.path.join(d, 'previsioni.csv')
    old = set()
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            old = {(r['emessa'], r['fonte']) for r in csv.DictReader(f)}
    new = not os.path.exists(path)
    with open(path, 'a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, F_PREV)
        if new:
            w.writeheader()
        for name, fn in SOURCES.items():
            if (hour_iso(now), name) in old:
                print(f'{name}: già salvata per le {now:%H}:00')
                continue
            try:
                rows = [r for r in fn() if now.strftime('%Y-%m-%dT%H:00') <= r[0] <= hour_iso(now + timedelta(days=4))]
            except Exception as e:
                print(f'::warning::{name} non disponibile: {type(e).__name__}: {e}'[:300])
                continue
            for t, c, p, tt, v in rows:
                w.writerow({'emessa': hour_iso(now), 'fonte': name, 'ora': t, 'nuvole': c, 'pioggia': p,
                            'temp': tt, 'vento': v})
            print(f'{name}: {len(rows)} ore salvate')


# ---------- osservazioni (METAR di Reykjavík) ----------
COVER = {'FEW': 19, 'SCT': 44, 'BKN': 75, 'OVC': 100, 'VV': 100}


def parse_metar(m):
    """Nuvole % (strato più coperto), pioggia/neve in corso, temperatura, vento (m/s)."""
    if re.search(r'\b(CAVOK|NSC|SKC|CLR|NCD)\b', m):
        cloud = 0
    else:
        layers = [COVER[c] for c in re.findall(r'\b(FEW|SCT|BKN|OVC|VV)\d{3}', m)]
        cloud = max(layers) if layers else None
    body = re.split(r' (?:RMK|TEMPO|BECMG|NOSIG)\b', m)[0]   # solo il tempo osservato, non le tendenze
    wx = re.findall(r'(?<![A-Z])[-+]?(?:VC)?(?:SH|TS|FZ)?(?:DZ|RA|SN|SG|PL|GS|GR|UP)+\b', body)
    precip = any(not w.startswith('VC') for w in wx)
    tm = re.search(r'\b(M?\d{2})/(M?\d{2})?\b', body)
    temp = float(tm.group(1).replace('M', '-')) if tm else None
    wm = re.search(r'\b(\d{3}|VRB)(\d{2,3})(?:G\d{2,3})?KT\b', body)
    wind = round(int(wm.group(2)) * 0.5144, 1) if wm else None
    return cloud, precip, temp, wind


def osservazioni(d, start, end):
    path = os.path.join(d, 'osservato.csv')
    try:
        text = fetch(IEM.format(a=start, b=end + timedelta(days=1)), 'text')
        obs = {}
        for r in csv.DictReader(text.splitlines()):
            if not r.get('metar') or r['metar'] == 'M':
                continue
            t = r['valid'].replace(' ', 'T')
            if t[14:16] == '00' or t[:13] + ':00' not in obs:   # il bollettino dell'ora piena
                obs[t[:13] + ':00'] = parse_metar(r['metar'])
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['ora', 'nuvole', 'pioggia', 'temp', 'vento'])
            for t, v in sorted(obs.items()):
                w.writerow([t, *v])
    except Exception as e:
        print(f'::warning::METAR non disponibili ({type(e).__name__}: {e}); uso la copia salvata'[:300])
    out = {}
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                out[r['ora']] = (num(r['nuvole']), r['pioggia'] == 'True', num(r['temp']), num(r['vento']))
    return out


# ---------- confronto ----------
BUCKETS = [(0, 24, 'entro 24 ore'), (24, 48, 'fra 1-2 giorni'), (48, 96, 'fra 2-4 giorni')]


def valuta(d):
    path = os.path.join(d, 'previsioni.csv')
    if not os.path.exists(path):
        print('Nessuna previsione salvata.')
        return
    with open(path, encoding='utf-8') as f:
        prev = list(csv.DictReader(f))
    first = min(datetime.fromisoformat(r['emessa']) for r in prev)
    now = datetime.now(UTC).replace(tzinfo=None)
    obs = osservazioni(d, first, now)
    stats = {}
    for r in prev:
        o = obs.get(r['ora'])
        if not o:
            continue
        lead = (datetime.fromisoformat(r['ora']) - datetime.fromisoformat(r['emessa'])).total_seconds() / 3600
        b = next((name for lo, hi, name in BUCKETS if lo <= lead < hi), None)
        if not b:
            continue
        s = stats.setdefault((r['fonte'], b), {k: [] for k in ('nuv', 'nuv_sera', 'cielo', 'piog', 'temp', 'vento')})
        c, p, t, v = num(r['nuvole']), num(r['pioggia']), num(r['temp']), num(r['vento'])
        evening = 16 <= int(r['ora'][11:13]) <= 23
        if c is not None and o[0] is not None:
            s['nuv'].append(abs(c - o[0]))
            s['cielo'].append((c >= 50) == (o[0] >= 50))
            if evening:
                s['nuv_sera'].append(abs(c - o[0]))
        if p is not None:
            s['piog'].append((p >= 0.1) == o[1])
        if t is not None and o[2] is not None:
            s['temp'].append(abs(t - o[2]))
        if v is not None and o[3] is not None:
            s['vento'].append(abs(v - o[3]))
    avg = lambda xs, f='{:.0f}': f.format(sum(xs) / len(xs)) if xs else '–'
    pct = lambda xs: f'{100 * sum(xs) / len(xs):.0f}%' if xs else '–'
    lines = ['# Confronto meteo: chi ci azzecca a Reykjavík', '',
             f'Previsioni salvate dal {first:%d/%m %H:%M} UTC; osservato: METAR dell\'aeroporto di Reykjavík '
             f'(BIRK), {len(obs)} ore. Errore medio: più basso è meglio; "giusto": più alto è meglio.', '',
             '"cielo giusto" = sereno/poco nuvoloso (sotto 50%) o nuvoloso/coperto azzeccato; '
             '"pioggia/neve giusta" = sì o no azzeccato per l\'ora (METAR: precipitazione in corso).', '',
             '| anticipo | fonte | ore | nuvole: errore medio | nuvole la sera (16-23) | cielo giusto | '
             'pioggia/neve giusta | temperatura: errore °C | vento: errore m/s |',
             '|---|---|---|---|---|---|---|---|---|']
    for _, _, b in BUCKETS:
        for src in SOURCES:
            s = stats.get((src, b))
            if not s:
                continue
            n = max(len(x) for x in s.values())
            lines.append(f'| {b} | {src} | {n} | {avg(s["nuv"])} | {avg(s["nuv_sera"])} | {pct(s["cielo"])} | '
                         f'{pct(s["piog"])} | {avg(s["temp"], "{:.1f}")} | {avg(s["vento"], "{:.1f}")} |')
    out = '\n'.join(lines) + '\n'
    print(out)
    with open(os.path.join(d, 'RISULTATI.md'), 'w', encoding='utf-8') as f:
        f.write(out)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as f:
            f.write(out)


if __name__ == '__main__':
    cmd, d = sys.argv[1], sys.argv[2]
    os.makedirs(d, exist_ok=True)
    {'raccogli': raccogli, 'valuta': valuta}[cmd](d)
