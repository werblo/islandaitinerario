"""Ricerca: quale stima delle nuvole prevede meglio il cielo notturno in Islanda.

Confronta, nelle ore di buio, le previsioni di Open-Meteo con il cielo osservato
dagli aeroporti (METAR, che riportano gli strati di nuvole con l'altezza) e dalla
stazione di Reykjavík (SYNOP, nuvolosità totale vista da un osservatore).

Metodi confrontati (tutti in %, 0 = sereno):
  totale      cloud_cover del modello automatico (DMI HARMONIE in Islanda): quello di oggi
  pesata      strati pesati: basse contano tutte, medie un po' meno, alte poco
  media       media di più modelli, nuvolosità totale
  media_pes   media di più modelli, strati pesati

Uso:
  python tools/research/nuvole.py storico [giorni]   test veloce sulle previsioni d'archivio
  python tools/research/nuvole.py raccogli FILE.csv  salva le previsioni delle 7:30 per stanotte
  python tools/research/nuvole.py valuta FILE.csv    confronta le previsioni salvate con il cielo reale
"""
import csv, io, json, math, os, sys, time, urllib.request
from datetime import date, datetime, timedelta, timezone

STATIONS = {   # punti con osservazioni del cielo anche di notte
    'BIRK': ('Reykjavík', 64.1300, -21.9406),
    'BIKF': ('Keflavík', 63.9850, -22.6056),
}   # Vestmannaeyjar (BIVM) ha METAR solo di giorno: inutile per le notti
SYNOP_REYKJAVIK = '04030'
MODELS = ['best_match', 'ecmwf_ifs025', 'icon_seamless', 'ukmo_seamless', 'metno_seamless', 'gfs_seamless']
W_MID, W_HIGH = 0.8, 0.3      # pesi degli strati medi e alti (bassi = 1)
OPEN = 0.5                     # "cielo utile": nuvole efficaci <= 50%
COVER = {'FEW': 0.19, 'SCT': 0.44, 'BKN': 0.75, 'OVC': 1.0, 'VV': 1.0}
CLEAR = {'CLR', 'SKC', 'NSC', 'NCD', 'CAVOK'}


def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'islanda-2026-ricerca-nuvole'})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:
            if i == tries - 1:
                raise
            print(f'  riprovo ({e})')
            time.sleep(5 * (i + 1))


def weighted(low, mid, high, w_mid=W_MID, w_high=W_HIGH):
    """Frazione di cielo coperta 'davvero' per l'aurora (strati sovrapposti a caso)."""
    return 1 - (1 - low) * (1 - w_mid * mid) * (1 - w_high * high)


# ---------- sole (algoritmo NOAA, come nell'app) ----------
def sun_altitude(t, lat, lon):
    rad = math.pi / 180
    jd = t.timestamp() / 86400 + 2440587.5
    T = (jd - 2451545) / 36525
    L0 = (280.46646 + T * (36000.76983 + T * 0.0003032)) % 360
    Ma = 357.52911 + T * (35999.05029 - 0.0001537 * T)
    ecc = 0.016708634 - T * (0.000042037 + 0.0000001267 * T)
    C = (math.sin(Ma * rad) * (1.914602 - T * (0.004817 + 0.000014 * T))
         + math.sin(2 * Ma * rad) * (0.019993 - 0.000101 * T) + math.sin(3 * Ma * rad) * 0.000289)
    omega = 125.04 - 1934.136 * T
    lam = L0 + C - 0.00569 - 0.00478 * math.sin(omega * rad)
    eps = 23 + (26 + (21.448 - T * (46.815 + T * (0.00059 - T * 0.001813))) / 60) / 60 + 0.00256 * math.cos(omega * rad)
    decl = math.asin(math.sin(eps * rad) * math.sin(lam * rad)) / rad
    y = math.tan(eps * rad / 2) ** 2
    eq = 4 / rad * (y * math.sin(2 * L0 * rad) - 2 * ecc * math.sin(Ma * rad)
                    + 4 * ecc * y * math.sin(Ma * rad) * math.cos(2 * L0 * rad)
                    - 0.5 * y * y * math.sin(4 * L0 * rad) - 1.25 * ecc * ecc * math.sin(2 * Ma * rad))
    ha = ((t.hour * 60 + t.minute + eq + 4 * lon + 1440) % 1440) / 4 - 180
    cz = math.sin(lat * rad) * math.sin(decl * rad) + math.cos(lat * rad) * math.cos(decl * rad) * math.cos(ha * rad)
    return 90 - math.acos(max(-1, min(1, cz))) / rad


def dark(t, lat, lon):
    return sun_altitude(t, lat, lon) < -12


# ---------- osservazioni ----------
def metar_obs(sid, d0, d1):
    """{ 'YYYY-MM-DDTHH:00': {'total', 'low', 'mid', 'high'} } dai METAR delle ore piene."""
    url = ('https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=' + sid
           + ''.join(f'&data={k}{i}' for i in range(1, 5) for k in ('skyc', 'skyl'))
           + f'&data=metar&year1={d0.year}&month1={d0.month}&day1={d0.day}'
           + f'&year2={d1.year}&month2={d1.month}&day2={d1.day}'
           + '&tz=Etc/UTC&format=onlycomma&latlon=no&missing=M&trace=T&direct=no&report_type=3&report_type=4')
    out = {}
    for r in csv.DictReader(io.StringIO(get(url))):
        t = r['valid']
        if not t.endswith(':00'):
            continue
        key = t.replace(' ', 'T')[:13] + ':00'
        metar = r.get('metar') or ''
        layers = {'low': 0.0, 'mid': 0.0, 'high': 0.0}
        seen = False
        for i in range(1, 5):
            c, h = r.get(f'skyc{i}', 'M'), r.get(f'skyl{i}', 'M')
            if c in CLEAR:
                seen = True
            if c in COVER:
                seen = True
                try:
                    ft = float(h)
                except ValueError:
                    ft = 0.0
                band = 'low' if ft < 6500 else 'mid' if ft < 20000 else 'high'
                layers[band] = max(layers[band], COVER[c])
        if not seen and ('CAVOK' in metar or 'NSC' in metar or 'NCD' in metar or 'SKC' in metar or 'CLR' in metar):
            seen = True
        if not seen:
            continue    # METAR senza informazioni sulle nuvole
        total = max(layers.values())
        out[key] = {'total': total, **layers}
    return out


def synop_obs(d0, d1):
    """Nuvolosità totale N (ottavi) a Reykjavík dai bollettini SYNOP (Ogimet), a blocchi di 5 giorni."""
    out = {}
    cur = d0
    while cur <= d1:
        end = min(cur + timedelta(days=4), d1)
        url = (f'https://www.ogimet.com/cgi-bin/getsynop?block={SYNOP_REYKJAVIK}'
               f'&begin={cur:%Y%m%d}0000&end={end:%Y%m%d}2300')
        try:
            text = get(url)
        except Exception as e:
            print(f'::warning::SYNOP {cur}: {e}')
            text = ''
        for line in text.splitlines():
            p = line.split(',')
            if len(p) < 7 or p[0] != SYNOP_REYKJAVIK:
                continue
            g = p[6].split()
            if len(g) > 4 and g[0] == 'AAXX' and g[4][0].isdigit():
                n = int(g[4][0])
                if n <= 9:
                    out[f'{p[1]}-{p[2]}-{p[3]}T{p[4]}:00'] = 1.0 if n == 9 else n / 8
        cur = end + timedelta(days=1)
        time.sleep(3)     # Ogimet chiede di non martellare
    return out


# ---------- previsioni ----------
VARS = ['cloud_cover', 'cloud_cover_low', 'cloud_cover_mid', 'cloud_cover_high']


def archived_forecasts(lat, lon, model, d0, d1):
    """Previsioni fatte il giorno prima (Open-Meteo 'previous runs', anticipo ~24 h)."""
    hv = ','.join(v + '_previous_day1' for v in VARS)
    url = (f'https://previous-runs-api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
           f'&hourly={hv}&models={model}&start_date={d0}&end_date={d1}&timezone=UTC')
    h = json.loads(get(url))['hourly']
    cols = [h.get(v + '_previous_day1') or [None] * len(h['time']) for v in VARS]
    print(f'    {model}: ' + ', '.join(f'{v} {sum(x is not None for x in c)}/{len(c)}' for v, c in zip(VARS, cols)))
    out = {}
    for i, t in enumerate(h['time']):
        vals = [c[i] for c in cols]
        if vals[0] is not None:
            out[t] = [None if v is None else v / 100 for v in vals]
    return out


def short_forecasts(lat, lon, model, d0, d1):
    """Previsioni a breve termine d'archivio (prime ore di ogni corsa), con gli strati."""
    url = (f'https://historical-forecast-api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
           f'&hourly={",".join(VARS)}&models={model}&start_date={d0}&end_date={d1}&timezone=UTC')
    h = json.loads(get(url))['hourly']
    cols = [h.get(v) or [None] * len(h['time']) for v in VARS]
    print(f'    {model} (breve): ' + ', '.join(f'{v} {sum(x is not None for x in c)}/{len(c)}' for v, c in zip(VARS, cols)))
    return {t: [None if c[i] is None else c[i] / 100 for c in cols]
            for i, t in enumerate(h['time']) if cols[0][i] is not None}


def live_forecasts(lat, lon, model):
    url = (f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
           f'&hourly={",".join(VARS)}&models={model}&timezone=UTC&forecast_days=2')
    h = json.loads(get(url))['hourly']
    return {t: [None if h[v][i] is None else h[v][i] / 100 for v in VARS]
            for i, t in enumerate(h['time']) if h['cloud_cover'][i] is not None}


def methods(fc):
    """fc: {modello: [tot, low, mid, high]} di un'ora -> stime dei 4 metodi (0..1)."""
    out = {}
    layered = lambda v: v and None not in v[1:]
    base = fc.get('best_match')
    if base:
        out['totale'] = base[0]
        if layered(base):
            out['pesata'] = weighted(*base[1:])
    others = [v for v in fc.values() if v]
    if len(others) >= 3:
        out['media'] = sum(v[0] for v in others) / len(others)
        lay = [v for v in others if layered(v)]
        if len(lay) >= 3:
            out['media_pes'] = sum(weighted(*v[1:]) for v in lay) / len(lay)
    return out


# ---------- confronto ----------
def score(rows, label):
    """rows: lista di (stime_metodi, verità) -> tabella di errori.
    Tutti i metodi sono valutati sulle stesse ore (quelle in cui esistono tutti)."""
    names = ['totale', 'pesata', 'media', 'media_pes']
    present = [m for m in names if any(m in e for e, _ in rows)]
    common = [(e, t) for e, t in rows if all(m in e for m in present)]
    nights = len({e.get('_notte') for e, _ in common})
    lines = [f'\n### {label} ({len(common)} ore di buio in comune, circa {nights} notti)\n',
             'Le ore della stessa notte si somigliano: differenze di pochi punti non sono significative.\n',
             '| metodo | errore medio | ore azzeccate (soglia 50%) | ore azzeccate (soglia 30%) | cielo aperto previsto e reale | cielo aperto perso |',
             '|---|---|---|---|---|---|']
    best = None
    for m in present:
        pairs = [(e[m], t) for e, t in common]
        if not pairs:
            continue
        mae = sum(abs(f - t) for f, t in pairs) / len(pairs)
        ok = sum((f <= OPEN) == (t <= OPEN) for f, t in pairs) / len(pairs)
        ok30 = sum((f <= 0.3) == (t <= 0.3) for f, t in pairs) / len(pairs)
        said_open = [(f, t) for f, t in pairs if f <= OPEN]
        prec = sum(t <= OPEN for f, t in said_open) / len(said_open) if said_open else float('nan')
        real_open = [(f, t) for f, t in pairs if t <= OPEN]
        miss = sum(f > OPEN for f, t in real_open) / len(real_open) if real_open else float('nan')
        lines.append(f'| {m} | {mae*100:.0f} punti | {ok*100:.0f}% | {ok30*100:.0f}% | {prec*100:.0f}% ({len(said_open)} ore) | {miss*100:.0f}% di {len(real_open)} ore |')
        if best is None or ok > best[1]:
            best = (m, ok)
    return '\n'.join(lines), best


_OBS = {}


def evaluate(fc_by_station, d0, d1, title):
    """fc_by_station: {sid: {ora: {modello: [tot, low, mid, high]}}}"""
    report = [f'# {title}', '', f'Periodo: {d0} → {d1}. Ore di buio (sole sotto −12°).',
              'Verità "totale": tutte le nuvole osservate. Verità "senza alte": solo strati bassi e medi '
              '(le nuvole alte sottili di solito lasciano vedere l\'aurora).',
              f'"Cielo utile" = nuvole ≤ {OPEN*100:.0f}%. Errore medio in punti percentuali (più basso = meglio).']
    all_tot, all_eff, syn_rows = [], [], []
    if 'synop' not in _OBS:
        _OBS['synop'] = synop_obs(d0, d1)
    syn = _OBS['synop']
    print('SYNOP Reykjavík:', len(syn), 'osservazioni')
    if not syn:
        print('::warning::Nessuna osservazione SYNOP (Ogimet non risponde o limita le richieste)')
    for sid, (name, lat, lon) in STATIONS.items():
        try:
            if sid not in _OBS:
                _OBS[sid] = metar_obs(sid, d0, d1 + timedelta(days=1))
            obs = _OBS[sid]
        except Exception as e:
            print(f'::warning::METAR {sid} non disponibile: {e}')
            continue
        rows_tot, rows_eff = [], []
        hours = fc_by_station.get(sid, {})
        n_dark = sum(dark(datetime.fromisoformat(t).replace(tzinfo=timezone.utc), lat, lon) for t in hours)
        print(f'{sid}: {len(hours)} ore previste, {n_dark} di buio, esempi previsione {sorted(hours)[:2]} '
              f'osservazione {sorted(obs)[:2]}')
        for t, fc in sorted(hours.items()):
            when = datetime.fromisoformat(t).replace(tzinfo=timezone.utc)
            if not dark(when, lat, lon):
                continue
            est = methods(fc)
            if not est:
                continue
            est['_notte'] = (when - timedelta(hours=12)).date().isoformat()
            o = obs.get(t)
            if o:
                rows_tot.append((est, o['total']))
                rows_eff.append((est, 1 - (1 - o['low']) * (1 - o['mid'])))
            if sid == 'BIRK' and t in syn:
                syn_rows.append((est, syn[t]))
        print(f'{sid}: {len(obs)} METAR, {len(rows_tot)} ore di buio confrontabili')
        all_tot += rows_tot
        all_eff += rows_eff
        if rows_tot:
            report.append(f'\n## {name} ({sid})')
            report.append(score(rows_tot, 'verità totale')[0])
            report.append(score(rows_eff, 'verità senza nuvole alte')[0])
    report.append('\n## Tutte le stazioni insieme')
    t1, b1 = score(all_tot, 'verità totale (METAR)')
    t2, b2 = score(all_eff, 'verità senza nuvole alte (METAR)')
    report += [t1, t2]
    if syn_rows:
        t3, b3 = score(syn_rows, 'Reykjavík, osservatore umano (SYNOP, totale)')
        report.append(t3)
    report.append(f'\nMigliore per ore azzeccate: totale → **{b1 and b1[0]}**, senza alte → **{b2 and b2[0]}**')
    return '\n'.join(report)


def cmd_storico(days):
    d1 = date.today() - timedelta(days=2)
    d0 = d1 - timedelta(days=days - 1)
    out = []
    # 1) previsioni fatte il giorno prima: solo nuvolosità totale (l'archivio non ha gli strati)
    # 2) previsioni a breve termine: con gli strati, per provare il metodo pesato
    for title, fetch in [('Test veloce A: previsioni fatte il giorno prima (solo totale)', archived_forecasts),
                         ('Test veloce B: previsioni a brevissimo termine, 0-6 ore (con gli strati) - NON è la previsione delle 7:30', short_forecasts)]:
        fc = {}
        for sid, (name, lat, lon) in STATIONS.items():
            per_hour = {}
            for m in MODELS:
                try:
                    for t, v in fetch(lat, lon, m, d0, d1).items():
                        per_hour.setdefault(t, {})[m] = v
                except Exception as e:
                    print(f'{sid} {m}: non disponibile ({e})')
                time.sleep(1)
            fc[sid] = per_hour
        out.append(evaluate(fc, d0, d1, title))
    return '\n\n'.join(out)


def cmd_raccogli(path):
    """Salva le previsioni attuali per le ore di buio delle prossime 24 h (lanciato alle 7:30)."""
    now = datetime.now(timezone.utc)
    new = os.path.exists(path)
    with open(path, 'a', newline='') as f:
        w = csv.writer(f)
        if not new:
            w.writerow(['emessa', 'stazione', 'ora', 'modello', 'tot', 'low', 'mid', 'high'])
        n = 0
        for sid, (name, lat, lon) in STATIONS.items():
            for m in MODELS:
                try:
                    data = live_forecasts(lat, lon, m)
                except Exception as e:
                    print(f'::warning::Previsione {sid} {m} non disponibile: {e}')
                    continue
                for t, v in data.items():
                    when = datetime.fromisoformat(t).replace(tzinfo=timezone.utc)
                    if now < when <= now + timedelta(hours=24) and dark(when, lat, lon):
                        w.writerow([now.strftime('%Y-%m-%dT%H:%M'), sid, t, m]
                                   + ['' if x is None else round(x, 3) for x in v])
                        n += 1
                time.sleep(1)
    print('righe salvate:', n)
    if n == 0:
        print('::error::Nessuna previsione salvata stamattina')
        sys.exit(1)


def cmd_valuta(path):
    if not os.path.exists(path):
        return '# Nessuna previsione raccolta finora'
    fc = {}
    dates = []
    with open(path) as f:
        for r in csv.DictReader(f):
            try:
                vals = [float(r[k]) if r[k] not in ('', None) else None for k in ('tot', 'low', 'mid', 'high')]
            except ValueError:
                continue    # riga troncata
            if vals[0] is None:
                continue
            fc.setdefault(r['stazione'], {}).setdefault(r['ora'], {})[r['modello']] = vals
            dates.append(r['ora'][:10])
    if not dates:
        return '# Nessuna previsione raccolta'
    d0, d1 = date.fromisoformat(min(dates)), date.fromisoformat(max(dates))
    return evaluate(fc, d0, d1, 'Test approfondito: previsioni delle 7:30 per la notte')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'storico'
    # i cron si ripetono ogni anno: la ricerca serve solo per il viaggio del 2026
    if os.environ.get('GITHUB_EVENT_NAME') == 'schedule' and date.today().year != 2026:
        print('Ricerca nuvole: solo per il 2026, niente da fare.')
        sys.exit(0)
    if cmd == 'storico':
        text = cmd_storico(int(sys.argv[2]) if len(sys.argv) > 2 else 40)
    elif cmd == 'raccogli':
        cmd_raccogli(sys.argv[2]); sys.exit(0)
    else:
        text = cmd_valuta(sys.argv[2])
    print(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f:
            f.write(text + '\n')
    if os.environ.get('REPORT'):
        with open(os.environ['REPORT'], 'w') as f:
            f.write(text + '\n')
