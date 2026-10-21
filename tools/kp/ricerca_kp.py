"""Ricerca: quanto ci si può fidare del Kp per l'aurora in Islanda (ottobre-novembre 2026).

Punto 1 (fino al 14/11): la previsione del Kp che l'app e gli avvisi leggono al mattino
(NOAA, 3 giorni) confrontata con il Kp misurato davvero la notte dopo, nelle fasce
18-21, 21-24, 0-3, 3-6 UTC (= ora islandese).

Punto 2 (una settimana, 22-29/10): ogni 10 minuti, di notte, si salvano gli indicatori
"di adesso" che si trovano sui siti dell'aurora:
  kp_1m       Kp stimato al minuto (NOAA), quello della riga "Aurora boreale — ora" dell'app
  ovation     probabilità di aurora sopra Reykjavík del modello OVATION (NOAA, 30-90 minuti avanti)
  ovation_n   come sopra ma il massimo poco più a nord (aurora visibile all'orizzonte nord)
  bz, vento   campo magnetico (Bz, negativo = favorevole) e velocità del vento solare (satellite in L1)
e si confrontano con quello che succede davvero sopra l'Islanda: il magnetometro di
Leirvogur (LRV, vicino a Reykjavík, rete INTERMAGNET), che si agita quando l'aurora è
sopra la zona. Se LRV non è disponibile si usa l'indice Hp30 (GFZ, ogni mezz'ora).
Non esiste un registro automatico di "aurora vista": il magnetometro è il dato misurato
più vicino.

Uso:
  python tools/kp/ricerca_kp.py turno DIR [minuti]   raccolta (mattino + ogni 10 minuti di notte)
  python tools/kp/ricerca_kp.py valuta DIR           confronta i dati raccolti, scrive DIR/RISULTATI.md
  python tools/kp/ricerca_kp.py prova -              mostra il formato di ogni fonte
"""
import csv, json, math, os, sys, time, urllib.error, urllib.request
from datetime import datetime, timedelta, timezone

UTC = timezone.utc
REYKJAVIK = (64.1466, -21.9426)
NIGHT_BLOCKS = (18, 21, 0, 3)          # fasce di 3 ore con il buio, ore UTC di inizio
NOWCAST_UNTIL = datetime(2026, 10, 30, 12, tzinfo=UTC)   # fine del punto 2
MORNING = (6, 15)                      # la previsione "del mattino": salvata tra le 6 e le 15

KP_FORECAST = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json'
KP_OBSERVED = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json'
KP_1M = 'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json'
OVATION = 'https://services.swpc.noaa.gov/json/ovation_aurora_latest.json'
MAG = 'https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json'        # vento solare in tempo reale (L1)
PLASMA = 'https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json'
GFZ = 'https://kp.gfz.de/app/json/?start={start}&end={end}&index={index}'
LRV = ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=json'
       '&testObsys=0&observatoryIagaCode=LRV&samplesPerDay=minute&publicationState=best-avail'
       '&dataStartDate={day}&dataDuration=1')


def get_json(url, tries=2):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'islanda-2026-ricerca-kp'})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode('utf-8', 'replace'))
        except urllib.error.HTTPError as e:
            if i == tries - 1:
                body = e.read().decode('utf-8', 'replace')[:300]
                raise RuntimeError(f'HTTP {e.code}: {body}') from None
            time.sleep(5)
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(5)


def parse_time(s):
    s = str(s).strip().replace(' ', 'T').replace('Z', '+00:00')
    t = datetime.fromisoformat(s)
    return t if t.tzinfo else t.replace(tzinfo=UTC)


def rows_of(data, keys):
    """Prodotti NOAA a righe ([intestazione], [...]) oppure a oggetti: lista di dict."""
    if data and isinstance(data[0], list):
        head = [str(h).lower() for h in data[0]]
        return [dict(zip(head, r)) for r in data[1:]]
    return [{k.lower(): v for k, v in o.items()} for o in data]


def num(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def append(path, fields, row):
    new = not os.path.exists(path)
    with open(path, 'a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new:
            w.writeheader()
        w.writerow(row)


def read(path):
    if not os.path.exists(path):
        return []
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


# ---------- punto 1: previsione del mattino e Kp osservato ----------
F_PREV = ['salvata', 'notte', 'anticipo', 'fascia', 'kp_previsto']


def save_forecast(d, now):
    """Salva una volta al giorno (la prima tra le 6 e le 15) il Kp previsto per stanotte
    (anticipo 0) e per la notte dopo (anticipo 1), fascia per fascia."""
    path = os.path.join(d, 'kp_previsioni.csv')
    today = now.strftime('%Y-%m-%d')
    if not (MORNING[0] <= now.hour < MORNING[1]):
        return
    if any(r['salvata'][:10] == today for r in read(path)):
        return
    rows = rows_of(get_json(KP_FORECAST), ['time_tag', 'kp', 'observed'])
    pred = {}
    for r in rows:
        t, kp = r.get('time_tag'), num(r.get('kp'))
        if t is None or kp is None or str(r.get('observed', '')).lower() != 'predicted':
            continue
        pred[parse_time(t)] = kp
    n = 0
    for lead in (0, 1):
        night = (now + timedelta(days=lead)).replace(hour=12, minute=0, second=0, microsecond=0)
        for h in NIGHT_BLOCKS:
            t = night.replace(hour=h) + (timedelta(days=1) if h < 12 else timedelta())
            if t in pred:
                append(path, F_PREV, {'salvata': now.strftime('%Y-%m-%d %H:%M'), 'notte': night.strftime('%Y-%m-%d'),
                                      'anticipo': lead, 'fascia': t.strftime('%Y-%m-%dT%H:%M'), 'kp_previsto': pred[t]})
                n += 1
    print(f'Previsione del mattino salvata: {n} fasce (stanotte e domani notte)')


def save_observed(d):
    """Kp misurato (NOAA, ultimi 7 giorni) e Kp della GFZ (il riferimento ufficiale)."""
    path = os.path.join(d, 'kp_osservato.csv')
    have = {(r['fonte'], r['fascia']) for r in read(path)}
    n = 0
    try:
        for r in rows_of(get_json(KP_OBSERVED), ['time_tag', 'kp']):
            t, kp = r.get('time_tag'), num(r.get('kp'))
            if t is None or kp is None:
                continue
            key = ('noaa', parse_time(t).strftime('%Y-%m-%dT%H:%M'))
            if key not in have:
                append(path, ['fonte', 'fascia', 'kp'], {'fonte': key[0], 'fascia': key[1], 'kp': kp}); have.add(key); n += 1
    except Exception as e:
        print(f'::warning::Kp osservato NOAA non disponibile: {e}')
    try:
        end = datetime.now(UTC)
        url = GFZ.format(start=(end - timedelta(days=7)).strftime('%Y-%m-%dT00:00:00Z'),
                         end=end.strftime('%Y-%m-%dT%H:%M:00Z'), index='Kp')
        g = get_json(url)
        for t, kp in zip(g.get('datetime', []), g.get('Kp', [])):
            key = ('gfz', parse_time(t).strftime('%Y-%m-%dT%H:%M'))
            if num(kp) is not None and key not in have:
                append(path, ['fonte', 'fascia', 'kp'], {'fonte': key[0], 'fascia': key[1], 'kp': kp}); have.add(key); n += 1
    except Exception as e:
        print(f'::warning::Kp GFZ non disponibile: {e}')
    print(f'Kp osservato: {n} valori nuovi')


# ---------- punto 2: indicatori "di adesso" ogni 10 minuti ----------
F_NOW = ['ora', 'kp_1m', 'ovation', 'ovation_n', 'bz', 'bt', 'vento', 'lrv_range60', 'lrv_minuti', 'hp30']


def ovation_probs(data):
    """Probabilità OVATION sopra Reykjavík (cella più vicina, ±1°) e massimo poco più a nord (fino a 70°)."""
    lon0 = round(REYKJAVIK[1]) % 360
    here = north = 0
    for lon, lat, p in data.get('coordinates', []):
        if abs(((lon - lon0 + 180) % 360) - 180) > 2:
            continue
        if abs(lat - REYKJAVIK[0]) <= 1:
            here = max(here, p)
        if REYKJAVIK[0] <= lat <= 70:
            north = max(north, p)
    return here, north


def last_valid(rows, key):
    # il più recente: alcuni prodotti sono dal più vecchio, altri (rtsw) dal più nuovo e con più satelliti
    if rows and 'time_tag' in rows[0]:
        rows = sorted((r for r in rows if r.get('active', True) is not False), key=lambda r: str(r['time_tag']))
    for r in reversed(rows):
        v = num(r.get(key))
        if v is not None:
            return v
    return None


def lrv_range(now, code='LRV'):
    """Escursione della componente orizzontale nell'ultima ora (nT) e minuti validi, osservatorio INTERMAGNET."""
    vals = []
    for day in sorted({(now - timedelta(minutes=60)).date(), now.date()}):
        g = get_json(LRV.format(day=day.isoformat()).replace('Code=LRV', 'Code=' + code))
        times = g.get('datetime') or g.get('times')
        t0 = parse_time(g['startDate']) if g.get('startDate') else None
        if not times and t0 is None:
            raise ValueError('formato LRV sconosciuto: ' + str(list(g))[:200])
        comps = g.get('dataComponents') or g.get('data') or {}
        if isinstance(comps, list):    # [{"component":"X","data":[...]}, ...]
            comps = {c.get('component', '').upper(): c.get('data', []) for c in comps}
        x = comps.get('X') or comps.get('H') or []
        for i, v in enumerate(x):
            t = parse_time(times[i]) if times else t0 + timedelta(minutes=i)
            v = num(v)
            if v is not None and abs(v) < 99999 and now - timedelta(minutes=60) <= t <= now:
                vals.append(v)
    return (round(max(vals) - min(vals), 1), len(vals)) if len(vals) >= 20 else (None, len(vals))


def hp30_now(now):
    url = GFZ.format(start=(now - timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:00Z'),
                     end=now.strftime('%Y-%m-%dT%H:%M:00Z'), index='Hp30')
    g = get_json(url)
    v = [num(x) for x in g.get('Hp30', []) if num(x) is not None]
    return v[-1] if v else None


def save_nowcast(d, now):
    row = {'ora': now.strftime('%Y-%m-%dT%H:%M')}
    tries = {
        'kp_1m': lambda: last_valid(rows_of(get_json(KP_1M), []), 'kp_index'),     # lo stesso valore della riga "ora" dell'app
        'ovation': lambda: ovation_probs(get_json(OVATION)),
        'mag': lambda: rows_of(get_json(MAG), []),
        'vento': lambda: last_valid(rows_of(get_json(PLASMA), []), 'proton_speed') or last_valid(rows_of(get_json(PLASMA), []), 'speed'),
        'lrv': lambda: lrv_range(now),
        'hp30': lambda: hp30_now(now),
    }
    for k, f in tries.items():
        try:
            v = f()
            if k == 'ovation':
                row['ovation'], row['ovation_n'] = v
            elif k == 'mag':
                row['bz'], row['bt'] = last_valid(v, 'bz_gsm'), last_valid(v, 'bt')
            elif k == 'lrv':
                row['lrv_range60'], row['lrv_minuti'] = v
            else:
                row[k] = v
        except Exception as e:
            print(f'  {k} non disponibile: {type(e).__name__}: {e}'[:200])
    append(os.path.join(d, 'adesso.csv'), F_NOW, row)
    print('  ' + ' · '.join(f'{k} {row.get(k)}' for k in F_NOW))


def is_dark_hours(t):
    return t.hour >= 17 or t.hour < 7


def turno(d, minutes):
    os.makedirs(d, exist_ok=True)
    start = datetime.now(UTC)
    deadline = start + timedelta(minutes=minutes)
    print(f'Turno dalle {start:%d/%m %H:%M} alle {deadline:%d/%m %H:%M} UTC')
    while True:
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        try:
            save_forecast(d, now)
        except Exception as e:
            print(f'::warning::Previsione Kp non disponibile: {e}')
        if now < NOWCAST_UNTIL and is_dark_hours(now):
            print(f'--- {now:%d/%m %H:%M} UTC')
            save_nowcast(d, now)
        if now + timedelta(minutes=10) > deadline or now >= NOWCAST_UNTIL or not is_dark_hours(now + timedelta(minutes=10)):
            break
        time.sleep(max(0, (now + timedelta(minutes=10) - datetime.now(UTC)).total_seconds()))
    save_observed(d)


# ---------- valutazione ----------
def category(kp):
    # le stesse soglie della stima dell'app (kpFactor): <2, 2-3, 3-4, 4-5, >=5
    return 0 if kp < 2 else 1 if kp < 3 else 2 if kp < 4 else 3 if kp < 5 else 4


def rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(a, b):
    if len(a) < 5:
        return None
    ra, rb = rank(a), rank(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num_ = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num_ / den if den else None


# soglie "dice di sì" di ogni indicatore (quelle consigliate di solito dai siti dell'aurora)
YES = (('kp_1m', 'Kp al minuto ≥ 4', lambda v: v >= 4, 0),
       ('ovation', 'OVATION sopra Reykjavík ≥ 10%', lambda v: v >= 10, 0),
       ('ovation_n', 'OVATION a nord ≥ 10%', lambda v: v >= 10, 0),
       ('bz', 'Bz ≤ −5 nT (riferimento 30 minuti dopo)', lambda v: v <= -5, 30),
       ('hp30', 'Hp30 ≥ 4', lambda v: v >= 4, 0))
ACTIVE = {'lrv_range60': (150, 'Leirvogur si muove più di 150 nT in un\'ora'), 'hp30': (4, 'Hp30 ≥ 4')}


def hit_table(rows, ref):
    """Quante volte ogni indicatore "ci azzecca": sì quando c'è attività, no quando non c'è."""
    thr, ref_text = ACTIVE[ref]
    by_time = {r['ora']: r for r in rows}
    out = [f'**Chi ci azzecca più spesso.** "Attività in Islanda" = {ref_text}. Per ogni indicatore: '
           'quante volte ha detto la cosa giusta, quante volte l\'attività c\'era davvero quando diceva sì, '
           'e quante attività ha visto in anticipo o in tempo. Il Bz si confronta con 30 minuti dopo, '
           'perché il vento solare arriva in Islanda con un po\' di ritardo.', '',
           '| indicatore | misure | azzeccate | quando dice sì, c\'è davvero | attività viste |', '|---|---|---|---|---|']
    for k, label, yes, lag in YES:
        if k == ref:
            continue
        tp = fp = fn = tn = 0
        for r in rows:
            if not r.get(k):
                continue
            later = by_time.get((parse_time(r['ora']) + timedelta(minutes=lag)).strftime('%Y-%m-%dT%H:%M')) if lag else r
            if not later or not later.get(ref):
                continue
            said, real = yes(float(r[k])), float(later[ref]) >= thr
            tp += said and real; fp += said and not real; fn += real and not said; tn += not said and not real
        n = tp + fp + fn + tn
        pct = lambda a, b: f'{100 * a / b:.0f}%' if b else '–'
        out.append(f'| {label} | {n} | {pct(tp + tn, n)} | {pct(tp, tp + fp)} | {pct(tp, tp + fn)} |')
    out.append('')
    return out


def valuta(d):
    out = ['# Ricerca Kp: risultati', '']
    obs = {}
    for r in read(os.path.join(d, 'kp_osservato.csv')):
        obs.setdefault(r['fascia'], {})[r['fonte']] = float(r['kp'])
    truth = {k: v.get('gfz', v.get('noaa')) for k, v in obs.items()}
    prev = read(os.path.join(d, 'kp_previsioni.csv'))

    out += ['## Punto 1: la previsione del mattino è affidabile?', '',
            'Kp previsto al mattino (NOAA) contro Kp misurato (GFZ, o NOAA se manca), nelle fasce di buio.',
            '"Stessa fascia dell\'app" = stessa soglia della stima (<2, 2-3, 3-4, 4-5, 5+).', '',
            '| anticipo | fasce | notti | errore medio | in media | entro ±1 | stessa fascia dell\'app | notti "Kp 4+" previste / misurate / entrambe |',
            '|---|---|---|---|---|---|---|---|']
    for lead, label in (('0', 'stanotte (mattino stesso)'), ('1', 'domani notte (un giorno prima)')):
        pairs, nights = [], {}
        for r in prev:
            if r['anticipo'] != lead or r['fascia'] not in truth:
                continue
            p, o = float(r['kp_previsto']), truth[r['fascia']]
            pairs.append((p, o))
            n = nights.setdefault(r['notte'], [0, 0])
            n[0], n[1] = max(n[0], p), max(n[1], o)
        if not pairs:
            out.append(f'| {label} | 0 | 0 | – | – | – | – | – |')
            continue
        err = sum(abs(p - o) for p, o in pairs) / len(pairs)
        bias = sum(p - o for p, o in pairs) / len(pairs)
        within = 100 * sum(abs(p - o) <= 1 for p, o in pairs) / len(pairs)
        same = 100 * sum(category(p) == category(o) for p, o in pairs) / len(pairs)
        fp = sum(v[0] >= 4 for v in nights.values()); fo = sum(v[1] >= 4 for v in nights.values())
        both = sum(v[0] >= 4 and v[1] >= 4 for v in nights.values())
        out.append(f'| {label} | {len(pairs)} | {len(nights)} | {err:.2f} | {"+" if bias >= 0 else ""}{bias:.2f} '
                   f'(+ = previsione troppo alta) | {within:.0f}% | {same:.0f}% | {fp} / {fo} / {both} |')
    out.append('')

    rows = read(os.path.join(d, 'adesso.csv'))
    out += ['## Punto 2: quale indicatore "di adesso" segue meglio l\'Islanda?', '']
    if not rows:
        out.append('Nessun dato raccolto.')
    else:
        ref = 'lrv_range60' if sum(bool(r.get('lrv_range60')) for r in rows) >= max(10, len(rows) // 2) else 'hp30'
        ref_name = ('escursione del magnetometro di Leirvogur nell\'ultima ora (nT)' if ref == 'lrv_range60'
                    else 'indice Hp30 della GFZ (Leirvogur non disponibile)')
        out += [f'{len(rows)} misure di notte. Riferimento: {ref_name}.', '',
                'Correlazione di Spearman (1 = va su e giù insieme al riferimento, 0 = nessun legame; '
                'per il Bz conta il segno meno: più negativo = più attività).', '',
                '| indicatore | misure | correlazione |', '|---|---|---|']
        for k, label, sign in (('kp_1m', 'Kp stimato al minuto (NOAA, riga "ora" dell\'app)', 1),
                               ('ovation', 'OVATION sopra Reykjavík', 1),
                               ('ovation_n', 'OVATION a nord di Reykjavík', 1),
                               ('bz', 'Bz del vento solare (segno invertito)', -1),
                               ('vento', 'velocità del vento solare', 1),
                               ('hp30', 'Hp30 (GFZ, ogni 30 minuti)', 1)):
            if k == ref:
                continue
            a = [(sign * float(r[k]), float(r[ref])) for r in rows if r.get(k) and r.get(ref)]
            c = spearman([x for x, _ in a], [y for _, y in a]) if a else None
            out.append(f'| {label} | {len(a)} | {"–" if c is None else f"{c:.2f}"} |')
        out.append('')
        out += hit_table(rows, ref)
    text = '\n'.join(out)
    print(text)
    with open(os.path.join(d, 'RISULTATI.md'), 'w', encoding='utf-8') as f:
        f.write(text + '\n')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as f:
            f.write(text + '\n')


def prova():
    """Mostra com'è fatta la risposta di ogni fonte (per controllare i formati)."""
    now = datetime.now(UTC)
    for name, url in (('kp previsto', KP_FORECAST), ('kp osservato', KP_OBSERVED), ('kp 1m', KP_1M),
                      ('mag', MAG), ('plasma', PLASMA),
                      ('gfz Kp', GFZ.format(start=(now - timedelta(days=1)).strftime('%Y-%m-%dT00:00:00Z'),
                                            end=now.strftime('%Y-%m-%dT%H:%M:00Z'), index='Kp')),
                      ('gfz Hp30', GFZ.format(start=(now - timedelta(hours=3)).strftime('%Y-%m-%dT%H:%M:00Z'),
                                              end=now.strftime('%Y-%m-%dT%H:%M:00Z'), index='Hp30')),
                      ('lrv', LRV.format(day=now.date().isoformat())),
                      ('gin osservatori', 'https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetCapabilities&format=json'),
                      ('ovation', OVATION)):
        print(f'… {name}', flush=True)
        t0 = time.time()
        try:
            g = get_json(url)
            print(f'  ({time.time() - t0:.0f} s)')
            if isinstance(g, dict):
                desc = {k: (v[:2] + ['…', v[-1]] if isinstance(v, list) and len(v) > 3 else v) for k, v in g.items()}
                print(f'{name}: dict {json.dumps(desc, default=str)[:700]}')
            else:
                print(f'{name}: list di {len(g)} · primo {json.dumps(g[0])[:200]} · ultimo {json.dumps(g[-1])[:200]}')
        except Exception as e:
            print(f'{name}: ERRORE {type(e).__name__}: {e}'[:300])
    try:
        obs = get_json('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetCapabilities&format=json')['ObservatoryList']
        print('Osservatori sopra 55° N:', ', '.join(f"{o['IagaCode']} {o['Name']} ({o['Latitude']:.1f}, {o['Longitude']:.1f}, ritardo {o['DataEmbargoHours']} h)"
                                               for o in obs if o['Latitude'] > 55))
    except Exception as e:
        print('elenco osservatori: ERRORE', e)
    for code in ('NAQ', 'LER', 'TRO', 'ABK', 'SOD'):
        try:
            print(code, '-> escursione ultima ora', lrv_range(now, code))
        except Exception as e:
            print(code, '-> ERRORE', str(e)[:150])
    for url in ('https://kp.gfz-potsdam.de/app/files/Hp30_ap30_nowcast.txt', 'https://kp.gfz.de/app/files/Hp30_ap30_nowcast.txt'):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'islanda-2026-ricerca-kp'})
            with urllib.request.urlopen(req, timeout=30) as r:
                lines = r.read().decode('utf-8', 'replace').strip().splitlines()
            print(url, '-> ultime righe:', lines[-2:])
        except Exception as e:
            print(url, '-> ERRORE', type(e).__name__, str(e)[:120])
    for f, args in ((ovation_probs, (get_json(OVATION),)), (lrv_range, (now,)), (hp30_now, (now,))):
        try:
            print(f.__name__, '->', f(*args))
        except Exception as e:
            print(f.__name__, '-> ERRORE', type(e).__name__, str(e)[:200])


if __name__ == '__main__':
    cmd, d = sys.argv[1], sys.argv[2]
    if cmd == 'turno':
        turno(d, int(sys.argv[3]) if len(sys.argv) > 3 else 170)
    elif cmd == 'prova':
        prova()
    elif cmd == 'valuta':
        valuta(d)
    else:
        sys.exit(__doc__)
