"""Confronto delle previsioni meteo (chiesto da Michele l'8/11, fino al 14/11).

Quale fonte ci azzecca di più a Reykjavík e Keflavík: Open-Meteo, met.no (servizio norvegese) e
vedur.is (servizio meteo islandese)? Ogni esecuzione salva le previsioni ora per ora dei prossimi
giorni ("raccogli"); "valuta" le confronta con il tempo osservato agli aeroporti (METAR di BIRK e
BIKF, archivio IEM) e scrive RISULTATI.md.

1. Generale: nuvole (in tutte le ore e la sera, 16-23 UTC, quella che conta per l'aurora),
   pioggia/neve sì o no, temperatura, vento. Per le nuvole anche:
   - "app (media modelli)": la media di più modelli con CLOUD_METHOD (come app e avvisi);
   - miscele calcolate qui: "app + vedur.is" e "app + vedur.is + met.no" (media delle fonti).
2. Raffiche: Open-Meteo (previsione standard) e i singoli modelli che usa (ECMWF, ICON, GFS,
   UKMO, MET Nordic), più la loro media; vedur.is e met.no non prevedono raffiche per stazione.
   Osservato: raffica del METAR (G) oppure, se non c'è, il vento medio (le raffiche si
   segnalano solo quando superano di molto il vento medio).

Uso:  python3 tools/meteo/confronto_meteo.py raccogli <cartella>
      python3 tools/meteo/confronto_meteo.py valuta <cartella>
"""
import csv, json, math, os, re, sys, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import aurora_alert as aa   # stesso calcolo delle nuvole di app e avvisi

UTC = timezone.utc
UA = 'islanda-2026-confronto-meteo (github.com/werblo/islandaitinerario)'
# luogo: coordinate (come dati.py), stazione vedur.is, METAR, file
PLACES = {
    'Reykjavík': {'lat': 64.1466, 'lon': -21.9426, 'vedur': 1, 'metar': 'BIRK',
                  'prev': 'previsioni.csv', 'oss': 'osservato.csv'},
    'Keflavík': {'lat': 63.9850, 'lon': -22.6056, 'vedur': 990, 'metar': 'BIKF',
                 'prev': 'previsioni_keflavik.csv', 'oss': 'osservato_keflavik.csv'},
}
GUST_MODELS = {'ecmwf_ifs025': 'ECMWF', 'icon_seamless': 'ICON', 'gfs_seamless': 'GFS',
               'ukmo_seamless': 'UKMO', 'metno_seamless': 'MET Nordic'}
OPEN_METEO = ('https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
              '&hourly=cloud_cover,precipitation,temperature_2m,wind_speed_10m,wind_gusts_10m'
              '&wind_speed_unit=ms&timezone=UTC&forecast_days=5')
OPEN_METEO_MODELS = ('https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
                     '&hourly=wind_gusts_10m&models=' + ','.join(GUST_MODELS)
                     + '&wind_speed_unit=ms&timezone=UTC&forecast_days=5')
MET_NO = 'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}'
VEDUR = 'https://xmlweather.vedur.is/?op_w=xml&type=forec&lang=en&view=xml&ids={id}&params=F;T;N;R'
IEM = ('https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station={st}&data=metar'
       '&year1={a.year}&month1={a.month}&day1={a.day}&year2={b.year}&month2={b.month}&day2={b.day}'
       '&tz=Etc/UTC&format=onlycomma&latlon=no&missing=M&trace=T&direct=no&report_type=3&report_type=4')
F_PREV = ['emessa', 'fonte', 'ora', 'nuvole', 'pioggia', 'temp', 'vento', 'raffica']


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


# ---------- previsioni: ogni fonte restituisce {nome: [(ora, nuvole, pioggia, temp, vento, raffica)]} ----------
def from_open_meteo(p):
    h = fetch(OPEN_METEO.format(**p))['hourly']
    out = {'Open-Meteo': [(t, num(h['cloud_cover'][i]), num(h['precipitation'][i]), num(h['temperature_2m'][i]),
                           num(h['wind_speed_10m'][i]), num(h['wind_gusts_10m'][i])) for i, t in enumerate(h['time'])]}
    hm = fetch(OPEN_METEO_MODELS.format(**p))['hourly']
    for m, name in GUST_MODELS.items():
        col = hm.get('wind_gusts_10m_' + m)
        if col:
            out[name + ' (raffiche)'] = [(t, None, None, None, None, num(col[i])) for i, t in enumerate(hm['time'])]
    return out


def from_app(p):   # nuvole come le calcola l'app (CLOUD_METHOD, più modelli insieme)
    trip = aa.trip_data()
    by_hour = aa.clouds_by_hour(fetch(aa.clouds_url({'lat': p['lat'], 'lon': p['lon']}, trip)), trip)
    return {'app (media modelli)': [(t, c, None, None, None, None) for t, c in sorted(by_hour.items())]}


def from_met_no(p):
    out = []
    for s in fetch(MET_NO.format(**p))['properties']['timeseries']:
        d = s['data']['instant']['details']
        nxt = s['data'].get('next_1_hours')   # pioggia oraria solo nei primi 2-3 giorni
        out.append((s['time'][:13] + ':00', num(d.get('cloud_area_fraction')),
                    num(nxt['details'].get('precipitation_amount')) if nxt else None,
                    num(d.get('air_temperature')), num(d.get('wind_speed')), None))
    return {'met.no': out}


def from_vedur(p):
    root = ET.fromstring(fetch(VEDUR.format(id=p['vedur']), 'text'))
    out, prev = [], None
    for f in root.iter('forecast'):
        t = f.findtext('ftime', '').replace(' ', 'T')[:13] + ':00'
        # R è la quantità del passo: si confronta ora per ora solo dove i passi sono di 1 ora
        step = (datetime.fromisoformat(t) - prev).total_seconds() / 3600 if prev else 1
        prev = datetime.fromisoformat(t)
        out.append((t, num(f.findtext('N')), num(f.findtext('R')) if step == 1 else None,
                    num(f.findtext('T')), num(f.findtext('F')), None))
    return {'vedur.is': out}


FETCHERS = [from_open_meteo, from_app, from_met_no, from_vedur]
GENERAL = ['Open-Meteo', 'app (media modelli)', 'met.no', 'vedur.is']
MIXES = {'app + vedur.is': ['app (media modelli)', 'vedur.is'],
         'app + vedur.is + met.no': ['app (media modelli)', 'vedur.is', 'met.no']}
GUSTS = ['Open-Meteo'] + [n + ' (raffiche)' for n in GUST_MODELS.values()]


def read_prev(path):
    """Righe salvate; i file dell'8/11 mattina non hanno la colonna "raffica": si aggiunge."""
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        r = csv.DictReader(f)
        rows, header = list(r), r.fieldnames or []
    if 'raffica' not in header:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, F_PREV)
            w.writeheader()
            for row in rows:
                w.writerow({k: row.get(k, '') for k in F_PREV})
    return rows


def raccogli(d):
    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    for place, p in PLACES.items():
        path = os.path.join(d, p['prev'])
        old = {(r['emessa'], r['fonte']) for r in read_prev(path)}
        new = not os.path.exists(path)
        with open(path, 'a', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, F_PREV)
            if new:
                w.writeheader()
            for fn in FETCHERS:
                try:
                    got = fn(p)
                except Exception as e:
                    print(f'::warning::{place}, {fn.__name__}: {type(e).__name__}: {e}'[:300])
                    continue
                for name, rows in got.items():
                    if (hour_iso(now), name) in old:
                        continue
                    rows = [r for r in rows if hour_iso(now) <= r[0] <= hour_iso(now + timedelta(days=4))]
                    for t, c, pr, tt, v, g in rows:
                        w.writerow({'emessa': hour_iso(now), 'fonte': name, 'ora': t, 'nuvole': c, 'pioggia': pr,
                                    'temp': tt, 'vento': v, 'raffica': g})
                    print(f'{place} · {name}: {len(rows)} ore salvate')


# ---------- osservazioni (METAR) ----------
COVER = {'FEW': 19, 'SCT': 44, 'BKN': 75, 'OVC': 100, 'VV': 100}


def parse_metar(m):
    """Nuvole % (strato più coperto), pioggia/neve in corso, temperatura, vento e raffica (m/s)."""
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
    wm = re.search(r'\b(\d{3}|VRB)(\d{2,3})(?:G(\d{2,3}))?KT\b', body)
    wind = round(int(wm.group(2)) * 0.5144, 1) if wm else None
    gust = round(int(wm.group(3)) * 0.5144, 1) if wm and wm.group(3) else wind
    return cloud, precip, temp, wind, gust


def osservazioni(d, p, start, end):
    path = os.path.join(d, p['oss'])
    try:
        text = fetch(IEM.format(st=p['metar'], a=start, b=end + timedelta(days=1)), 'text')
        obs = {}
        for r in csv.DictReader(text.splitlines()):
            if not r.get('metar') or r['metar'] == 'M':
                continue
            t = r['valid'].replace(' ', 'T')
            if t[14:16] == '00' or t[:13] + ':00' not in obs:   # il bollettino dell'ora piena
                obs[t[:13] + ':00'] = parse_metar(r['metar'])
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['ora', 'nuvole', 'pioggia', 'temp', 'vento', 'raffica'])
            for t, v in sorted(obs.items()):
                w.writerow([t, *v])
    except Exception as e:
        print(f'::warning::METAR {p["metar"]} non disponibili ({type(e).__name__}: {e}); uso la copia salvata'[:300])
    out = {}
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                v = num(r['vento'])
                out[r['ora']] = (num(r['nuvole']), r['pioggia'] == 'True', num(r['temp']), v,
                                 num(r.get('raffica')) if r.get('raffica') not in (None, '') else v)
    return out


# ---------- confronto ----------
BUCKETS = [(0, 24, 'entro 24 ore'), (24, 48, 'fra 1-2 giorni'), (48, 96, 'fra 2-4 giorni')]
KEYS = ('nuv', 'nuv_sera', 'cielo', 'piog', 'temp', 'vento', 'raff', 'raff_bias', 'raff_max')


def bucket(r):
    lead = (datetime.fromisoformat(r['ora']) - datetime.fromisoformat(r['emessa'])).total_seconds() / 3600
    return next((name for lo, hi, name in BUCKETS if lo <= lead < hi), None)


def valuta(d):
    stats, info = {}, []
    for place, p in PLACES.items():
        prev = read_prev(os.path.join(d, p['prev']))
        if not prev:
            continue
        first = min(datetime.fromisoformat(r['emessa']) for r in prev)
        obs = osservazioni(d, p, first, datetime.now(UTC).replace(tzinfo=None))
        info.append(f'{place}: previsioni dal {first:%d/%m %H:%M} UTC, osservato {len(obs)} ore (METAR {p["metar"]})')
        # miscele per le nuvole: media delle fonti salvate nella stessa esecuzione per la stessa ora
        by = {}
        for r in prev:
            by.setdefault((r['emessa'], r['ora']), {})[r['fonte']] = num(r['nuvole'])
            if r['fonte'] in GUSTS[1:]:
                by[(r['emessa'], r['ora'])].setdefault('_raff', []).append(num(r['raffica']))
        extra = []
        for (e, t), v in by.items():
            for mix, parts in MIXES.items():
                vals = [v.get(x) for x in parts]
                if all(x is not None for x in vals):
                    extra.append({'emessa': e, 'fonte': mix, 'ora': t, 'nuvole': sum(vals) / len(vals)})
            gs = [x for x in v.get('_raff', []) if x is not None]
            if len(gs) >= 3:
                extra.append({'emessa': e, 'fonte': 'media modelli (raffiche)', 'ora': t, 'raffica': sum(gs) / len(gs)})
        daymax = {}
        for r in prev + extra:
            o = obs.get(r['ora'])
            b = bucket(r)
            if not o or not b:
                continue
            for key in ((r['fonte'], b), (r['fonte'], b, place)):
                s = stats.setdefault(key, {k: [] for k in KEYS})
                c, pr, tt, v, g = (num(r.get(k)) for k in ('nuvole', 'pioggia', 'temp', 'vento', 'raffica'))
                if c is not None and o[0] is not None:
                    s['nuv'].append(abs(c - o[0]))
                    s['cielo'].append((c >= 50) == (o[0] >= 50))
                    if 16 <= int(r['ora'][11:13]) <= 23:
                        s['nuv_sera'].append(abs(c - o[0]))
                if pr is not None:
                    s['piog'].append((pr >= 0.1) == o[1])
                if tt is not None and o[2] is not None:
                    s['temp'].append(abs(tt - o[2]))
                if v is not None and o[3] is not None:
                    s['vento'].append(abs(v - o[3]))
                if g is not None and o[4] is not None:
                    s['raff'].append(abs(g - o[4]))
                    s['raff_bias'].append(g - o[4])
            if num(r.get('raffica')) is not None and o[4] is not None:
                k = (r['fonte'], b, place, r['emessa'], r['ora'][:10])
                m = daymax.setdefault(k, [None, None, 0])
                m[0] = max(m[0] if m[0] is not None else -1, num(r['raffica']))
                m[1] = max(m[1] if m[1] is not None else -1, o[4])
                m[2] += 1
        for (src, b, place_, _, _), (fmax, omax, n) in daymax.items():
            if n >= 12:   # giornata coperta almeno per metà
                for key in ((src, b), (src, b, place_)):
                    stats.setdefault(key, {k: [] for k in KEYS})['raff_max'].append(abs(fmax - omax))
    avg = lambda xs, f='{:.0f}': f.format(sum(xs) / len(xs)) if xs else '–'
    pct = lambda xs: f'{100 * sum(xs) / len(xs):.0f}%' if xs else '–'
    sign = lambda xs: (('+' if sum(xs) >= 0 else '') + f'{sum(xs) / len(xs):.1f}') if xs else '–'
    lines = ['# Confronto meteo: chi ci azzecca', '', *[f'- {x}' for x in info], '',
             'Errore medio: più basso è meglio; "giusto": più alto è meglio. Reykjavík e Keflavík insieme.', '',
             '## Nuvole, pioggia/neve, temperatura, vento', '',
             '"cielo giusto" = sereno/poco nuvoloso (sotto 50%) o nuvoloso/coperto azzeccato; '
             '"pioggia/neve giusta" = sì o no azzeccato per l\'ora (METAR: precipitazione in corso). '
             'Le miscele sono la media delle fonti indicate.', '',
             '| anticipo | fonte | ore | nuvole: errore medio | nuvole la sera (16-23) | cielo giusto | '
             'pioggia/neve giusta | temperatura: errore °C | vento: errore m/s |',
             '|---|---|---|---|---|---|---|---|---|']
    for _, _, b in BUCKETS:
        for src in GENERAL + list(MIXES):
            s = stats.get((src, b))
            if not s or not (s['nuv'] or s['temp']):
                continue
            n = max(len(s[k]) for k in ('nuv', 'temp', 'vento'))
            lines.append(f'| {b} | {src} | {n} | {avg(s["nuv"])} | {avg(s["nuv_sera"])} | {pct(s["cielo"])} | '
                         f'{pct(s["piog"])} | {avg(s["temp"], "{:.1f}")} | {avg(s["vento"], "{:.1f}")} |')
    lines += ['', '## Raffiche (m/s)', '',
              'Osservato: raffica del METAR o, se non c\'è, vento medio. "tendenza": + = la previsione '
              'esagera, − = sottostima. "massima del giorno": errore sulla raffica più forte della giornata.', '',
              '| anticipo | fonte | ore | errore medio | tendenza | massima del giorno: errore | '
              'errore Reykjavík | errore Keflavík |', '|---|---|---|---|---|---|---|---|']
    for _, _, b in BUCKETS:
        for src in GUSTS + ['media modelli (raffiche)']:
            s = stats.get((src, b))
            if not s or not s['raff']:
                continue
            per = [avg((stats.get((src, b, pl)) or {}).get('raff', []), '{:.1f}') for pl in PLACES]
            lines.append(f'| {b} | {src.replace(" (raffiche)", "")} | {len(s["raff"])} | {avg(s["raff"], "{:.1f}")} | '
                         f'{sign(s["raff_bias"])} | {avg(s["raff_max"], "{:.1f}")} | {per[0]} | {per[1]} |')
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
