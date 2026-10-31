"""Avvisi aurora: notifiche push sui telefoni nelle notti del viaggio.

Lanciato dal workflow "Avvisi aurora" (.github/workflows/avvisi-aurora.yml).
Usa la stessa stima dell'app (Kp previsto NOAA × cielo sereno Open-Meteo, solo
nelle ore di buio) nei posti in cui siete la sera, tappa per tappa
(evening_stops in dati.py; di default l'alloggio della notte). Avvisi:

- "mattino":    dalle 7:37 di ogni giorno del viaggio, sempre: com'è messa stasera,
                con una frase scherzosa (personalizzata se il telefono ha un nome);
- "previsione": la sera, solo se la stima diventa "buone" e al mattino non lo era
                (cambio di programma in meglio);
- "adesso":     quando è buio e attività del momento (la migliore tra Kp attuale e OVATION
                verso nord) + nuvole di quest'ora sono buone;
- "arrivo":     quando è buio, il cielo non è coperto e il vento solare è favorevole da un po'
                (Bz molto negativo, vento veloce): l'aurora potrebbe accendersi entro 30-60 minuti.

Le esecuzioni programmate di GitHub partono spesso con ore di ritardo: per questo il
workflow lancia dei "turni" (AURORA_MODE=turno) che restano accesi circa 5 ore e mezza e
fanno da soli i controlli ogni 30 minuti (ai minuti :07 e :37; di notte, in mezzo, ogni 10
minuti solo il vento solare per l'avviso "arrivo"), il messaggio del mattino
(dalle 7:37) e la prova automatica del 13 novembre (dalle 18:07). I turni partono ogni 2
ore e si mettono in coda uno dopo l'altro: anche se uno parte tardi, quello già acceso
copre le ore in cui serve.

Variabili d'ambiente:
  VAPID_PRIVATE_KEY     chiave privata VAPID (secret del repo)
  AURORA_SUBSCRIPTIONS  codici copiati dall'app ("Attiva avvisi aurora"), uno dopo
                        l'altro; un nome davanti ("Federica: {...}") personalizza le frasi
  AURORA_MODE           "turno" (esecuzioni programmate), "controllo" (default), "vento"
                        (solo l'avviso "arrivo"), "mattino" oppure "prova" (notifica subito)
  AURORA_TURNO_MIN      durata di un turno in minuti (default 330)
  AURORA_TURNO_SIMULA   solo per test: "1" = il turno non aspetta davvero, fa avanzare
                        l'orologio da AURORA_NOW
  AURORA_STATE          file con gli avvisi già inviati (default .aurora-state/state.json)
  AURORA_NOW            solo per test: istante da simulare (ISO, UTC)

Uso: python3 tools/aurora_alert.py  (dalla radice del repo, dopo render.py)
"""
import json, math, os, random, re, sys, time, urllib.request
from datetime import datetime, timedelta, timezone

VAPID_SUB = 'https://werblo.github.io'   # contatto per i servizi push (solo dominio)
KP_FORECAST_URL = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json'
KP_NOW_URL = 'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json'
CLOUDS_URL = ('https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
              '&hourly=cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high'
              '&timezone=UTC&past_days=1&forecast_days=3')
GOOD = 0.45   # soglia di "buone probabilità", come nell'app
# vento solare in tempo reale (satellite in L1, circa 30-60 minuti prima dell'arrivo sulla Terra)
WIND_MAG_URL = 'https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json'
WIND_PLASMA_URL = 'https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json'
# frase sulla previsione del Kp (ricerca Kp di ottobre: al mattino sbaglia in media di circa 1),
# uguale a KP_NOTE in app/app.js
OVATION_URL = 'https://services.swpc.noaa.gov/json/ovation_aurora_latest.json'
KP_NOTE = 'La previsione del Kp sbaglia spesso di circa 1 punto: ricontrollate la sera.'


# ---------- dati del viaggio: letti da index.html, così restano allineati all'app ----------
def trip_data(path='index.html'):
    with open(path, encoding='utf-8') as f:
        page = f.read()
    def const(name):
        m = re.search(r'^const ' + name + r' = (.+);$', page, re.M)
        if not m:
            sys.exit(f'{name} non trovato in {path}: rilancia python3 render.py')
        return json.loads(m.group(1))
    method = re.search(r"^const CLOUD_METHOD = '(\w+)';$", page, re.M)
    w = re.search(r'^const CLOUD_W_MID = ([\d.]+), CLOUD_W_HIGH = ([\d.]+);$', page, re.M)
    return {
        'places': const('AURORA_PLACES'), 'days': const('DAYS_META'), 'stops': const('NIGHT_STOPS'),
        'method': method.group(1) if method else 'totale', 'w_mid': float(w.group(1)), 'w_high': float(w.group(2)),
        'models': const('CLOUD_MODELS'),
    }


def night_place_key(date_iso, days):
    # come nightPlaceKey() nell'app: l'alloggio di quel giorno (l'ultimo giorno si riparte)
    day = next((d for d in days if d['dateISO'] == date_iso and d['id'] != 'd8'), None)
    return day['locKey'] if day else 'reykjavik'


def night_stops(date_iso, trip):
    # come nightStops() nell'app: le tappe della sera, di default l'alloggio
    return trip['stops'].get(date_iso) or [{'place': night_place_key(date_iso, trip['days'])}]


def stop_at(stops, t):
    # come stopAt(): 'until' è l'ora islandese di fine tappa, contata dalle 12
    off = (t.hour + 12) % 24
    return next((s for s in stops if 'until' not in s or off < (s['until'] + 12) % 24), stops[-1])


# ---------- sole: stesso algoritmo NOAA dell'app ----------
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
    eps = (23 + (26 + (21.448 - T * (46.815 + T * (0.00059 - T * 0.001813))) / 60) / 60
           + 0.00256 * math.cos(omega * rad))
    decl = math.asin(math.sin(eps * rad) * math.sin(lam * rad)) / rad
    y = math.tan(eps * rad / 2) ** 2
    eq_time = 4 / rad * (y * math.sin(2 * L0 * rad) - 2 * ecc * math.sin(Ma * rad)
                         + 4 * ecc * y * math.sin(Ma * rad) * math.cos(2 * L0 * rad)
                         - 0.5 * y * y * math.sin(4 * L0 * rad) - 1.25 * ecc * ecc * math.sin(2 * Ma * rad))
    minutes = t.hour * 60 + t.minute
    ha = ((minutes + eq_time + 4 * lon + 1440) % 1440) / 4 - 180
    cos_z = (math.sin(lat * rad) * math.sin(decl * rad)
             + math.cos(lat * rad) * math.cos(decl * rad) * math.cos(ha * rad))
    return 90 - math.acos(max(-1, min(1, cos_z))) / rad


# ---------- previsioni ----------
def get_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'islanda-2026-avvisi-aurora'})
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.load(res)


def parse_time(s):
    s = str(s).replace(' ', 'T')
    t = datetime.fromisoformat(s.replace('Z', '+00:00'))
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def parse_kp_forecast(data):
    # formato NOAA a righe ([intestazione], [time_tag, kp, ...]) oppure a oggetti
    if data and isinstance(data[0], list):
        rows = [(r[0], r[1]) for r in data[1:]]
    else:
        rows = [(o.get('time_tag'), o.get('kp', o.get('Kp'))) for o in data]
    out = []
    for t, kp in rows:
        try:
            out.append((parse_time(t), float(kp)))
        except (TypeError, ValueError):
            pass
    return out


def clouds_url(loc, trip):
    url = CLOUDS_URL.format(**loc)
    return url + '&models=' + ','.join(trip['models']) if trip['method'].startswith('media') else url


def clouds_by_hour(data, trip):
    """{ora: nuvole efficaci %} secondo CLOUD_METHOD, come effCloud() nell'app."""
    h = (data or {}).get('hourly') or {}
    def val(key, i):
        col = h.get(key)
        return col[i] if col and i < len(col) else None
    def layered(i, sfx):
        lo, mi, hi = (val(k + sfx, i) for k in ('cloud_cover_low', 'cloud_cover_mid', 'cloud_cover_high'))
        if None in (lo, mi, hi):
            return None
        return 100 * (1 - (1 - lo / 100) * (1 - trip['w_mid'] * mi / 100) * (1 - trip['w_high'] * hi / 100))
    out = {}
    for i, t in enumerate(h.get('time', [])):
        v = None
        if trip['method'].startswith('media'):
            vals = [val('cloud_cover_' + m, i) if trip['method'] == 'media' else layered(i, '_' + m)
                    for m in trip['models']]
            vals = [x for x in vals if x is not None]
            if len(vals) >= 3:
                v = sum(vals) / len(vals)
        elif trip['method'] == 'pesata':
            v = layered(i, '')
        if v is None:
            v = val('cloud_cover', i)
        if v is not None:
            out[t] = math.floor(v + 0.5)    # come Math.round nell'app (round() di Python va al pari)
    return out


def kp_factor(kp):
    # alle latitudini islandesi l'aurora si vede spesso già con Kp 2-3
    if kp >= 5: return 1
    if kp >= 4: return 0.85
    if kp >= 3: return 0.65
    if kp >= 2: return 0.4
    return 0.15


def hour_key(t):
    return t.strftime('%Y-%m-%dT%H:00')


def level_of(best):
    return 'buone' if best >= GOOD else 'scarse' if best >= 0.2 else 'nulle'


def windows_of(hours, best):
    # fasce orarie migliori: ore consecutive vicine al massimo
    windows = []
    for h in hours:
        if h['score'] < max(0.2, best * 0.8):
            continue
        if windows and windows[-1][1] == h['t']:
            windows[-1][1] = h['t'] + timedelta(hours=1)
        else:
            windows.append([h['t'], h['t'] + timedelta(hours=1)])
    return windows


def short_name(name):
    return re.sub(r' \(.*\)$', '', name)


def night_estimate(start, stops, trip, kp_rows, clouds):
    """Come nightEstimate() nell'app: ore di buio astronomico della notte che inizia alle 12 UTC,
    ognuna nel posto in cui siete a quell'ora."""
    places = trip['places']
    hours = []
    for i in range(24):
        t = start + timedelta(hours=i)
        place = stop_at(stops, t)['place']
        loc = places[place]
        if sun_altitude(t + timedelta(minutes=30), loc['lat'], loc['lon']) >= -18:
            continue
        kp = next((k for rt, k in kp_rows if rt <= t < rt + timedelta(hours=3)), None)
        hours.append({'t': t, 'place': place, 'kp': kp, 'cloud': clouds.get(place, {}).get(hour_key(t))})
    with_kp = [h for h in hours if h['kp'] is not None]
    est = {'hours': hours, 'level': None, 'stops': [], 'last': places[stops[-1]['place']]['name'],
           'route': [places[s['place']]['name'] for s in stops]}
    if not with_kp:
        return est
    has_clouds = any(h['cloud'] is not None for h in with_kp)
    for h in with_kp:
        sky = (0.5 if has_clouds else 1) if h['cloud'] is None else (100 - h['cloud']) / 100
        h['score'] = kp_factor(h['kp']) * sky
    best = max(h['score'] for h in with_kp)
    est.update(level=level_of(best), best=best, kp_max=max(h['kp'] for h in with_kp),
               clouds=[h['cloud'] for h in with_kp if h['cloud'] is not None],
               windows=windows_of(with_kp, best))
    for s in stops:
        hs = [h for h in with_kp if h['place'] == s['place']]
        if hs:
            b = max(h['score'] for h in hs)
            est['stops'].append({'name': places[s['place']]['name'], 'level': level_of(b), 'best': b,
                                 'from': hs[0]['t'], 'end': hs[-1]['t'] + timedelta(hours=1)})
    return est


def fmt_kp(kp):
    return f'{kp:.1f}'.replace('.0', '').replace('.', ',')    # all'italiana: 4,3


def place_label(est):
    # come nightPlaceNames()/stopsLabel() nell'app: senza dati valgono le tappe previste
    names = [short_name(s['name']) for s in est['stops']] or [short_name(n) for n in est['route']]
    return ' → '.join(names) if len(names) > 1 else (names[0] if est['stops'] else est['last'])


def r5(v):
    return int(5 * math.floor(v / 5 + 0.5))      # come Math.round(v / 5) * 5 nell'app


def cloud_summary(est):
    """Come auroraClouds() nell'app: valore tipico, oppure sera / dopo mezzanotte se cambia molto.
    Restituisce (testo, nuvole_variabili)."""
    hs = [h for h in est['hours'] if h['kp'] is not None and h['cloud'] is not None]
    if not hs:
        return None, False
    avg = lambda xs: sum(h['cloud'] for h in xs) / len(xs)
    lo, hi = min(h['cloud'] for h in hs), max(h['cloud'] for h in hs)
    if hi - lo < 30:
        return f'nuvole ~{r5(avg(hs))}%', False
    eve = [h for h in hs if h['t'].hour >= 12]
    late = [h for h in hs if h['t'].hour < 12]
    if eve and late and abs(avg(eve) - avg(late)) >= 20:
        return f'nuvole ~{r5(avg(eve))}% in serata, ~{r5(avg(late))}% dopo mezzanotte', True
    return f'nuvole variabili, tra {lo} e {hi}%', True


def details(est):
    """Riga di dettaglio: tappe, ore migliori (con le loro nuvole), Kp, nuvole."""
    parts = []
    clouds, variable = cloud_summary(est)
    # senza nuvole livelli e ore migliori verrebbero dal solo Kp: come l'app, solo Kp e "nuvole non disponibili"
    if clouds and len(est['stops']) > 1:
        parts += [f'{short_name(s["name"])} {s["from"]:%H}–{s["end"]:%H}: {s["level"]}' for s in est['stops']]
    if clouds and est['level'] != 'nulle' and est['windows']:
        wins = []
        for a, b in est['windows'][:2]:
            w = f'{a:%H}:00–{b:%H}:00'
            hs = [h for h in est['hours'] if h['kp'] is not None and h['cloud'] is not None and a <= h['t'] < b]
            if variable and hs:
                w += f' (nuvole ~{r5(sum(h["cloud"] for h in hs) / len(hs))}%)'
            wins.append(w)
        parts.append('meglio ' + ' e '.join(wins))
    parts.append('Kp fino a ' + fmt_kp(est['kp_max']))
    parts.append(clouds or 'nuvole non disponibili')
    return ' · '.join(parts)


def describe(est):
    if not est['hours']:
        return f'{est["last"]}: niente buio astronomico stanotte.'
    if not est['level']:
        return f'{place_label(est)}: previsione non disponibile.'
    if not est['clouds']:      # come l'app: senza nuvole niente verdetto
        return f'{place_label(est)}: previsione incompleta · ' + details(est)
    return f'{place_label(est)}: {est["level"]} probabilità · ' + details(est)


# ---------- avviso "arrivo": vento solare favorevole ----------
def solar_wind(now):
    """Bz e velocità del vento solare negli ultimi minuti (solo il satellite attivo, che arriva
    con 5-6 minuti di ritardo: le finestre partono dal dato più recente, non da adesso).
    None se l'ultimo dato è vecchio di più di 15 minuti o se i dati sono troppo pochi."""
    def series(url, key):
        rows = [r for r in get_json(url) if r.get('active') and isinstance(r.get(key), (int, float))]
        return [(parse_time(r['time_tag']), r[key]) for r in rows]
    def window(rows, minutes, last):
        return [v for t, v in rows if last - timedelta(minutes=minutes) < t <= last]
    mag = [(t, v) for t, v in series(WIND_MAG_URL, 'bz_gsm') if t <= now + timedelta(minutes=2)]
    last = max((t for t, _ in mag), default=None)
    if last is None or now - last > timedelta(minutes=15):
        return None
    bz20, bz15 = window(mag, 20, last), window(mag, 15, last)
    if len(bz20) < 12 or len(bz15) < 9:
        return None
    plasma = [(t, v) for t, v in series(WIND_PLASMA_URL, 'proton_speed') if t <= now + timedelta(minutes=2)]
    plast = max((t for t, _ in plasma), default=None)
    speed = window(plasma, 20, plast) if plast and now - plast <= timedelta(minutes=15) else []
    return {'bz20': sum(bz20) / len(bz20), 'bz15': sum(bz15) / len(bz15),
            'neg5': sum(v <= -5 for v in bz20) / len(bz20), 'neg7': sum(v <= -7 for v in bz15) / len(bz15),
            'speed': sum(speed) / len(speed) if speed else None}


def ovation_north(data, now, loc):
    """Probabilità OVATION di aurora verso nord: massimo tra la latitudine del posto e 70°N alla
    stessa longitudine (±2°), come nella riga "Adesso" dell'app. None se il dato ha più di un'ora."""
    try:
        if now - parse_time(data['Observation Time']) > timedelta(hours=1):
            return None
    except (KeyError, TypeError, ValueError):
        return None
    lon0 = round(loc['lon']) % 360
    vals = [p for c in data.get('coordinates') or [] if isinstance(c, list) and len(c) == 3
            and all(isinstance(x, (int, float)) for x in c)
            for lon, lat, p in [c]
            if abs(((lon - lon0 + 180) % 360) - 180) <= 2 and loc['lat'] <= lat <= 70]
    return max(vals) if vals else None


def ovation_factor(p):
    """OVATION sulla stessa scala di kp_factor (come ovationFactor nell'app; ricerca Kp di ottobre:
    sopra il 30% c'era attività quasi sempre)."""
    return 0.85 if p >= 30 else 0.65 if p >= 20 else 0.4 if p >= 10 else 0.15


def wind_favorable(w):
    """Bz medio ≤ −7 nT da 20 minuti con vento oltre 500 km/s, oppure Bz medio ≤ −10 da 15 minuti;
    in entrambi i casi stabile (quasi tutti i minuti ben negativi), non un picco isolato."""
    fast = w['speed'] is not None and w['speed'] >= 500
    return ((w['bz20'] <= -7 and w['neg5'] >= 0.8 and fast)
            or (w['bz15'] <= -10 and w['neg7'] >= 0.8))


def arrivo_alert(now, night, stops, trip, clouds, done, preview):
    """Avviso "arrivo" (una volta per notte, non dopo un "adesso"): buio, cielo non coperto,
    vento solare favorevole. Restituisce (tipo, messaggio, ttl) oppure None."""
    if 'arrivo' in done or 'adesso' in done:
        return None
    place = stop_at(stops, now)['place']
    loc = trip['places'][place]
    if sun_altitude(now, loc['lat'], loc['lon']) >= -12:
        return None
    try:
        w = solar_wind(now)
    except Exception as e:
        print(f'::warning::Vento solare NOAA non disponibile: {e}')
        return None
    if not w:
        print('Vento solare: dati non aggiornati.')
        return None
    bz = w['bz15'] if w['bz15'] <= -10 else w['bz20']
    sp = f', {w["speed"]:.0f} km/s' if w['speed'] is not None else ''
    print(f'Vento solare: Bz medio {w["bz20"]:.1f} nT (20 min), {w["bz15"]:.1f} (15 min){sp}')
    if not wind_favorable(w):
        return None
    if place not in clouds:
        try:
            clouds[place] = clouds_by_hour(get_json(clouds_url(loc, trip)), trip)
        except Exception as e:
            print(f'::warning::Nuvolosità Open-Meteo per {place} non disponibile: {e}')
    cloud = clouds.get(place, {}).get(hour_key(now + timedelta(minutes=45)))   # quando arriva
    if cloud is not None and cloud >= 75:
        print(f'Vento solare favorevole, ma cielo coperto ({cloud}%): niente avviso.')
        return None
    name = short_name(loc['name'])
    return ('arrivo', {
        'title': '🌌 Aurora in arrivo?',
        'body': f'{name[:1].upper()}{name[1:]}: il vento solare è favorevole (Bz {bz:.0f} nT{sp}): '
                'nei prossimi 30-60 minuti l\'aurora potrebbe accendersi'
                + (f', nuvole {cloud}%' if cloud is not None else ' (dati sulle nuvole non disponibili)')
                + ('. Tieni d\'occhio le webcam verso nord (livefromiceland.is)!' if preview
                   else '. Preparatevi e guardate verso nord!'),
        'tag': f'aurora-{night}-arrivo',
    }, 3600)


# ---------- frasi del mattino ----------
# {luogo} = dove siete stasera; {nome} = nome davanti al codice del telefono.
PHRASES = {
    'tutti': {
        'buone': ["🌌 Attenzione: stasera naso all'insù! A {luogo} il cielo promette spettacolo.",
                  "🧣 Sciarpa, thermos e torcicollo assicurato: stasera a {luogo} l'aurora ha buone chance.",
                  "📸 Treppiede carico? Stasera a {luogo} l'aurora potrebbe fare le prove generali.",
                  "🎆 Stasera il cielo di {luogo} potrebbe accendersi: scarponi pronti e tanta pazienza."],
        'scarse': ["🤞 Stasera l'aurora fa la timida: a {luogo} qualche chance c'è, un'occhiata fuori prima di dormire vale la pena.",
                   "🌥️ Possibilità modeste a {luogo}: non rinunciate alla cena, ma tenete un occhio alla finestra.",
                   "🔭 Stasera a {luogo} è un terno al lotto: se vi svegliate di notte, sbirciate fuori."],
        'nulle': ["♨️ Stasera a {luogo} l'aurora dà forfait. Piano B: piscina calda e birra islandese.",
                  "😴 L'aurora si è presa la serata libera. A nanna presto, domani si guida!",
                  "🍲 Niente spettacolo in cielo stasera a {luogo}: concentratevi sulla zuppa di agnello."],
        'nonuvole': ["☁️ Stamattina mancano i dati sulle nuvole: il Kp da solo non basta, ricontrollate l'app prima di cena.",
                     "📡 Previsione a metà: il Kp c'è, le nuvole no. Un'occhiata all'app in serata e siete a posto."],
        'nd': ["🔭 Previsione dell'aurora non disponibile stamattina: in serata guardate l'app o vedur.is/aurora.",
               "📡 Stamattina i dati sull'aurora non arrivano: ricontrollate l'app prima di cena."],
        'strada': ["🚗 Stasera il momento migliore potrebbe arrivare lungo la strada per {ultimo}: se il cielo si apre, fermatevi in una piazzola sicura e guardate in alto!"],
        'viaggio': ["🛁 Stasera occhi al cielo già a {migliore}: è la tappa più promettente della serata, poi via verso {ultimo}.",
                    "🚗 Stasera il meglio potrebbe arrivare a {migliore}: guardate in alto prima di ripartire per {ultimo}!"],
    },
    'nome': {
        'buone': ["🌌 {nome}, stasera naso all'insù! A {luogo} il cielo promette spettacolo.",
                  "🧤 {nome}, guanti e cappello: stasera a {luogo} si va a caccia di aurora!"],
        'scarse': ["🤞 {nome}, stasera l'aurora fa la preziosa: a {luogo} qualche chance c'è.",
                   "🔭 {nome}, stasera serve un pizzico di fortuna: a {luogo} non è detta l'ultima parola."],
        'nulle': ["☁️ {nome}, stasera a {luogo} il cielo è chiuso per ferie. Domani andrà meglio!",
                  "😴 {nome}, l'aurora stasera resta a casa. Goditi la cena a {luogo}!"],
        'nonuvole': ["☁️ {nome}, stamattina mancano i dati sulle nuvole: ricontrolla l'app prima di cena."],
        'nd': ["🔭 {nome}, stamattina la previsione dell'aurora non arriva: ricontrolla l'app in serata."],
        'strada': ["🚗 {nome}, stasera il meglio potrebbe arrivare lungo la strada per {ultimo}: se il cielo si apre, fermatevi in una piazzola sicura!"],
        'viaggio': ["🛁 {nome}, stasera guarda in alto già a {migliore}, poi anche lungo la strada per {ultimo}!"],
    },
    'federica': {
        'buone': ["👑 Federica, stasera l'aurora ha chiesto di te: a {luogo} buone probabilità!",
                  "🧤 Fede, guanti e cappello: stasera a {luogo} si va a caccia di aurora!",
                  "📸 Fede, telefono carico: stasera il cielo di {luogo} potrebbe meritarsi una storia.",
                  "✨ Fede, stasera a {luogo} il cielo si mette in ghingheri per te."],
        'scarse': ["🤞 Fede, stasera l'aurora fa la timida: a {luogo} qualche chance c'è, tieni d'occhio la finestra.",
                   "🔭 Federica, stasera serve un pizzico di fortuna: a {luogo} non è detta l'ultima parola."],
        'nulle': ["🛌 Fede, stasera niente aurora: è andata a dormire prima di te!",
                  "😴 Fede, l'aurora stasera ha mal di testa: a {luogo} niente spettacolo. Domani ci riprova!"],
        'nonuvole': ["☁️ Fede, stamattina mancano i dati sulle nuvole: ricontrolla l'app prima di cena."],
        'nd': ["🔭 Fede, stamattina la previsione dell'aurora non arriva: ricontrolla l'app in serata."],
        'strada': ["🚗 Fede, stasera tieni d'occhio il cielo lungo la strada per {ultimo}: se si apre, fermatevi in una piazzola sicura!"],
        'viaggio': ["🛁 Fede, stasera guarda in alto già {da_migliore}, poi anche lungo la strada per {ultimo}!"],
    },
}


MORNING_TITLES = {'buone': '🌅 Aurora stasera: buone probabilità', 'scarse': '🌅 Aurora stasera: qualche chance',
                  'nulle': '🌅 Aurora stasera: quasi impossibile'}


def is_federica(name):
    return re.match(r'fede(rica)?\b', name.strip().lower()) is not None


def morning_phrase(name, est, night, last_night=False):
    """Frase del mattino per un telefono: stesso giorno e stesso nome -> stessa frase."""
    pool = PHRASES['federica'] if is_federica(name) else PHRASES['nome'] if name else PHRASES['tutti']
    level = est['level']
    kind = level or 'nd'
    if level and not est.get('clouds'):
        kind = 'nonuvole'      # c'è il Kp ma non le nuvole: niente verdetto
    stops = est['stops']
    last = stops[-1] if stops else None
    # tappa migliore: solo se è strettamente meglio dell'ultima (a pari merito vale l'ultima)
    best_stop = max(stops, key=lambda s: s['best']) if stops else None
    if best_stop and last and best_stop['best'] <= last['best']:
        best_stop = last
    # sera in movimento e la tappa migliore non è l'ultima: frase "di viaggio"
    if kind in ('buone', 'scarse') and len(stops) > 1 and best_stop is not last and best_stop['level'] != 'nulle':
        kind = 'strada' if best_stop['name'].startswith('strada') else 'viaggio'
    choices = pool[kind]
    if last_night:      # l'ultima notte non c'è un "domani" per l'aurora
        choices = [c for c in choices if 'omani' not in c] or choices
    text = random.Random(f'{night}|{name}|{kind}').choice(choices)
    migliore = short_name(best_stop['name']) if best_stop else ''
    # con più tappe {luogo} è la tappa migliore della serata, non tutto il percorso;
    # senza probabilità (o se la migliore è la strada) vale dove passate la serata
    if len(stops) > 1 and kind in ('buone', 'scarse', 'strada', 'viaggio') and not migliore.startswith('strada'):
        luogo = migliore
    elif len(stops) > 1 and last:
        luogo = short_name(last['name'])
    else:
        luogo = place_label(est)
    da_migliore = (f'dalla piscina di {migliore}' if best_stop and 'Fontana' in best_stop['name']
                   else f'a {migliore}')
    return text.format(nome=name, luogo=luogo, migliore=migliore, da_migliore=da_migliore,
                       ultimo=short_name(last['name']) if last else est['last'])


# ---------- iscrizioni e invio ----------
def parse_subscriptions(text):
    """Codici incollati uno dopo l'altro (o lista JSON), ognuno con un nome davanti facoltativo:
    'Federica: {...}'. Restituisce [(nome, iscrizione)]."""
    subs, dec, i, prev = [], json.JSONDecoder(), 0, 0
    text = text or ''
    while True:
        i = text.find('{', i)
        if i < 0:
            break
        try:
            obj, end = dec.raw_decode(text, i)
        except json.JSONDecodeError:
            i += 1
            continue
        if isinstance(obj, dict) and obj.get('endpoint') and (obj.get('keys') or {}).get('p256dh'):
            gap = text[prev:i].replace('\r', '').split('\n')
            # il testo rimasto sulla riga del codice precedente non è il nome di questo telefono
            lines = [l.strip() for l in (gap[1:] if prev else gap) if l.strip()]
            label = lines[-1] if lines else ''
            label = re.sub(r'^(\d+\s*[).:-]|[-*•])\s*', '', label)      # "1) Federica:", "- Fede"
            name = ' '.join(re.sub(r'[^\wÀ-ÿ\' -]', '', label).split())
            if obj['endpoint'] not in [s['endpoint'] for _, s in subs]:
                subs.append((name, obj))
        i = prev = end
    return subs


def send_all(subs, make_payload, ttl):
    """make_payload(nome) -> payload della notifica per quel telefono."""
    from pywebpush import webpush, WebPushException
    key = os.environ.get('VAPID_PRIVATE_KEY', '').strip()
    if not key:
        print('::error::Manca il secret VAPID_PRIVATE_KEY')
        return 0
    ok = 0
    for n, (name, sub) in enumerate(subs, 1):
        host = re.sub(r'^https?://([^/]+).*$', r'\1', sub['endpoint'])
        who = f'Telefono {n}' + (f' ({name})' if name else '') + f' [{host}]'
        payload = make_payload(name)
        try:
            webpush(sub, json.dumps(payload, ensure_ascii=False), vapid_private_key=key,
                    vapid_claims={'sub': VAPID_SUB}, ttl=ttl, headers={'Urgency': 'high'}, timeout=30)
            print(f'{who}: inviata · {payload["title"]} · {payload["body"]}')
            ok += 1
        except WebPushException as e:
            code = getattr(e.response, 'status_code', None)
            if code in (404, 410):
                print(f'::warning::{who}: iscrizione scaduta, '
                      'ricopia il codice dall\'app e aggiorna AURORA_SUBSCRIPTIONS')
            else:
                print(f'::warning::{who}: invio fallito ({code or e})')
        except Exception as e:     # rete giù, timeout, chiave non valida…: si passa al telefono dopo
            print(f'::warning::{who}: invio fallito ({type(e).__name__}: {e})')
    return ok


def load_state(path):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(path, state):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, sort_keys=True)


def main():
    mode = os.environ.get('AURORA_MODE', 'controllo').strip() or 'controllo'
    now = (parse_time(os.environ['AURORA_NOW']).astimezone(timezone.utc) if os.environ.get('AURORA_NOW')
           else datetime.now(timezone.utc)).replace(second=0, microsecond=0)
    manual = os.environ.get('AURORA_MANUAL') == '1'   # lanciato a mano dalla tab Actions
    if mode == 'turno':
        if manual and datetime(2026, 11, 13, tzinfo=timezone.utc) <= now < datetime(2026, 11, 23, tzinfo=timezone.utc):
            # in parallelo ai turni programmati manderebbe avvisi doppi
            print('::error::Il turno a mano non si usa durante il viaggio: per un controllo in più '
                  'scegli "controllo", per una notifica di prova "prova".')
            return 1
        return turno(now)
    return run(mode, now, manual)


# ---------- turno: controlli ogni 30 minuti per ~5 ore e mezza ----------
PROVA_AUTO = (2026, 11, 13, 18, 7)    # prova automatica: 13 novembre 2026 dalle 18:07
# anteprima prima del viaggio (chiesta da Michele il 22/10): di notte solo l'avviso "adesso"
# per Reykjavík, solo ai telefoni che non sono di Federica, per guardare le webcam
ANTEPRIMA = ('2026-10-22', '2026-11-12')
MORNING_FROM, MORNING_UNTIL = (7, 25), (15, 0)   # messaggio del mattino: dalle 7:37 (slot) alle 15


def is_night_hour(t):
    return t.hour >= 16 or t.hour < 4


def next_slot(t):
    """Prossimo controllo dopo t: ai minuti :07 e :37, di notte anche ogni 10 minuti in mezzo."""
    for m in (7, 17, 27, 37, 47, 57, 67):
        cand = t.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=m)
        if cand > t and (cand.minute in (7, 37) or is_night_hour(cand)):
            return cand


def turno(now):
    state_path = os.environ.get('AURORA_STATE', '.aurora-state/state.json')
    simulate = os.environ.get('AURORA_TURNO_SIMULA') == '1'
    deadline = now + timedelta(minutes=min(330, int(os.environ.get('AURORA_TURNO_MIN') or 330)))   # GitHub ferma i job a 360
    trip_nights = {d['dateISO'] for d in trip_data()['days'] if d['id'] != 'd8'}
    print(f'Turno dalle {now:%d/%m %H:%M} alle {deadline:%d/%m %H:%M} UTC')
    failed = False
    t = slot = now     # il primo giro (all'avvio) è un controllo completo
    while True:
        jobs = []
        hm = (t.hour, t.minute)
        prova = datetime(*PROVA_AUTO, tzinfo=timezone.utc)
        if prova <= t < prova + timedelta(hours=6) and '_prova_auto' not in load_state(state_path):
            jobs.append('prova')
        tonight = t.strftime('%Y-%m-%d')
        rec = load_state(state_path).get(tonight) or {}
        if (tonight in trip_nights and MORNING_FROM <= hm < MORNING_UNTIL
                and 'mattino' not in (rec.get('inviati', rec) if isinstance(rec, dict) else rec)):
            jobs.append('mattino')
        if is_night_hour(t):
            # il tipo dipende dall'orario previsto, non da quando parte (può slittare di un minuto)
            jobs.append('controllo' if slot == now or slot.minute in (7, 37) else 'vento')
        if not jobs:
            print(f'--- {t:%d/%m %H:%M} UTC: niente da fare a quest\'ora')
        for job in jobs:
            print(f'--- {t:%d/%m %H:%M} UTC: {job}')
            try:
                rc = run(job, t, manual=False)
            except Exception as e:     # un errore non deve fermare il turno
                print(f'::error::{job} alle {t:%H:%M}: {e}')
                rc = 1
            if job == 'prova' and rc in (0, 3):   # 3 = arrivata solo ad alcuni telefoni: non ripeterla
                st = load_state(state_path)
                st['_prova_auto'] = t.strftime('%Y-%m-%d %H:%M')
                save_state(state_path, st)
            failed = failed or rc != 0
        t = slot = next_slot(t)
        if t > deadline:
            break
        if simulate:
            continue
        wait = (t - datetime.now(timezone.utc)).total_seconds()
        if wait > 0:
            time.sleep(wait)
        t = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    print('Fine del turno.')
    return 1 if failed else 0


def run(mode, now, manual=False):
    state_path = os.environ.get('AURORA_STATE', '.aurora-state/state.json')
    trip = trip_data()

    # la notte "di stasera" inizia alle 12 UTC di oggi (di notte, prima delle 10, è ancora
    # quella di ieri; il messaggio del mattino parla invece della sera che verrà).
    # In Islanda l'ora locale coincide con UTC tutto l'anno.
    start = now.replace(hour=12, minute=0) - timedelta(days=1 if now.hour < 10 and mode != 'mattino' else 0)
    night = start.strftime('%Y-%m-%d')
    trip_nights = {d['dateISO'] for d in trip['days'] if d['id'] != 'd8'}
    preview = mode in ('controllo', 'vento') and night not in trip_nights and ANTEPRIMA[0] <= night <= ANTEPRIMA[1]
    if night not in trip_nights and not preview and (mode in ('controllo', 'vento') or (mode == 'mattino' and not manual)):
        print(f'Notte del {night}: fuori dalle date del viaggio, nessun controllo.')
        return 0

    stops = [{'place': 'reykjavik'}] if preview else night_stops(night, trip)
    subs = parse_subscriptions(os.environ.get('AURORA_SUBSCRIPTIONS'))
    if preview:
        print('Anteprima prima del viaggio: solo gli avvisi "adesso" e "arrivo" per Reykjavík, Federica esclusa.')
        subs = [(n, s) for n, s in subs if not is_federica(n)]
    names = ', '.join(n or '(senza nome)' for n, _ in subs)
    print(f'Notte del {night} · tappe: {" → ".join(s["place"] for s in stops)} · {now:%H:%M} UTC'
          f' · nuvole: {trip["method"]} · telefoni: {len(subs)} ({names})')

    sent = load_state(state_path)
    rec = sent.get(night)
    rec = {'inviati': rec} if isinstance(rec, list) else (rec or {'inviati': []})
    done = set(rec['inviati'])
    if mode == 'vento':      # tra un controllo e l'altro: solo il vento solare, senza stima
        alert = arrivo_alert(now, night, stops, trip, {}, done, preview)
        return send_alerts([alert] if alert else [], subs, sent, rec, done, night, state_path)

    kp_rows, clouds, kp_now = [], {}, None
    try:
        kp_rows = parse_kp_forecast(get_json(KP_FORECAST_URL))
    except Exception as e:
        print(f'::warning::Previsione Kp NOAA non disponibile: {e}')
    for place in dict.fromkeys(s['place'] for s in stops):
        try:
            clouds[place] = clouds_by_hour(get_json(clouds_url(trip['places'][place], trip)), trip)
        except Exception as e:
            print(f'::warning::Nuvolosità Open-Meteo per {place} non disponibile: {e}')
    ov_now = None
    if mode == 'controllo':
        try:
            last = get_json(KP_NOW_URL)[-1]
            kp_now = float(last['kp_index'])      # lo stesso valore del Kp grande dell'app
        except Exception as e:
            print(f'::warning::Kp attuale NOAA non disponibile: {e}')

    est = night_estimate(start, stops, trip, kp_rows, clouds)
    summary = describe(est)
    print('Stima:', summary)

    if (mode in ('prova', 'mattino')) and not subs:
        print('::error::Nessun telefono in AURORA_SUBSCRIPTIONS: copia il codice dall\'app '
              '("Attiva avvisi aurora") e incollalo nel secret.')
        return 1

    if mode == 'prova':
        # la prova automatica (cron del 13 novembre) serve solo prima del viaggio del 2026
        if os.environ.get('GITHUB_EVENT_NAME') == 'schedule' and now.year != 2026:
            print('Prova automatica: solo nel 2026, niente da fare.')
            return 0
        ok = send_all(subs, lambda name: {
            'title': '🔔 Prova avvisi aurora', 'tag': 'aurora-prova',
            'body': (f'Ciao {name}! ' if name else '') + 'Le notifiche funzionano.'
                    + (' Stanotte a ' + summary if est['level'] else '')}, ttl=3600)
        print(f'Prova inviata a {ok} telefoni su {len(subs)}.')
        return 0 if ok == len(subs) else 3 if ok else 1

    if mode == 'mattino':
        if not manual and not (est['level'] and est['clouds']) and now.hour < 10:
            # dati NOAA o nuvole mancanti (rete o servizio giù): il turno riprova al prossimo
            # controllo; dalle 10 manda comunque il messaggio con quello che c'è
            print('Previsione incompleta: riprovo al prossimo controllo (fino alle 10).')
            return 0
        body_info = '\n' + details(est) + '\n' + KP_NOTE if est['level'] else ''
        complete = bool(est['level'] and est['clouds'])
        title = (MORNING_TITLES[est['level']] if complete
                 else '🌅 Aurora stasera: previsione incompleta' if est['level']
                 else '🌅 Aurora stasera: previsione non disponibile')
        last_night = night == max(trip_nights)
        ok = send_all(subs, lambda name: {
            'title': title,
            'body': morning_phrase(name, est, night, last_night) + body_info,
            'tag': f'aurora-{night}-mattino'}, ttl=4 * 3600)
        if manual:
            print('Anteprima lanciata a mano: lo stato della notte non viene toccato.')
        elif ok:
            rec['mattino'] = est['level'] if complete else None
            done.add('mattino')
            rec['inviati'] = sorted(done)
            sent[night] = rec
            save_state(state_path, sent)
        return 0 if ok else 1

    alerts = []
    morning = rec.get('mattino')
    # 1) cambio di programma: stanotte "buone", ma al mattino non lo era (o il mattino è mancato).
    #    Solo con dati sulle nuvole: senza, il solo Kp darebbe un falso "buone".
    if (not preview and 'previsione' not in done and est['level'] == 'buone' and morning != 'buone' and est['clouds']
            and any(b > now for _, b in est['windows'])):
        title = ('🔄 Cambio di programma: stanotte buone probabilità!' if morning
                 else '🌌 Aurora stanotte: buone probabilità')
        alerts.append(('previsione', {'title': title, 'body': place_label(est) + ' · ' + details(est),
                                      'tag': f'aurora-{night}-previsione'}, 6 * 3600))

    # 2) adesso: buio, attività del momento (la migliore tra Kp attuale e OVATION verso nord, come la
    #    riga "Adesso" dell'app) e cielo di quest'ora buoni, dove siete adesso
    place = stop_at(stops, now)['place']
    loc = trip['places'][place]
    cloud = clouds.get(place, {}).get(hour_key(now))
    dark = sun_altitude(now, loc['lat'], loc['lon']) < -12
    if 'adesso' not in done and dark:
        try:
            ov_now = ovation_north(get_json(OVATION_URL), now, loc)
        except Exception as e:
            print(f'::warning::OVATION NOAA non disponibile: {e}')
        print(f'Adesso: Kp {kp_now}, OVATION verso nord {ov_now}%, nuvole {cloud}%')
    acts = [f(x) for f, x in ((kp_factor, kp_now), (ovation_factor, ov_now)) if x is not None]
    if 'adesso' not in done and dark and acts:
        sky = 0.5 if cloud is None else (100 - cloud) / 100
        if max(acts) * sky >= GOOD:
            facts = ([f'aurora verso nord {ov_now}% (OVATION)'] if ov_now is not None else []) \
                + ([f'Kp {fmt_kp(kp_now)}'] if kp_now is not None else [])
            alerts.append(('adesso', {
                'title': '🌌 Aurora: condizioni buone adesso',
                'body': f'{short_name(loc["name"])[:1].upper()}{short_name(loc["name"])[1:]}: ' + ', '.join(facts)
                        + (f', nuvole {cloud}%' if cloud is not None else ' (dati sulle nuvole non disponibili: guardate se il cielo è sereno)')
                        + ('. Guarda le webcam verso nord (livefromiceland.is)!' if preview
                           else '. Allontanatevi dalle luci e guardate verso nord!'),
                'tag': f'aurora-{night}-adesso',
            }, 3600))

    # 3) arrivo: vento solare favorevole, l'aurora potrebbe accendersi entro 30-60 minuti
    alert = arrivo_alert(now, night, stops, trip, clouds, done | {a[0] for a in alerts}, preview)
    if alert:
        alerts.append(alert)
    return send_alerts(alerts, subs, sent, rec, done, night, state_path)


def send_alerts(alerts, subs, sent, rec, done, night, state_path):
    if not alerts:
        print('Nessun avviso da mandare' + (f' (già inviati: {", ".join(sorted(done))})' if done else '') + '.')
        return 0
    if not subs:
        print('::warning::Avviso da mandare ma nessun telefono in AURORA_SUBSCRIPTIONS.')
        return 0

    failed = False
    for kind, payload, ttl in alerts:
        print(f'Avviso "{kind}": {payload["body"]}')
        if send_all(subs, lambda name, p=payload: p, ttl):
            done.add(kind)
        else:
            failed = True
        # salvato dopo ogni avviso: se qualcosa va storto dopo, non si rimanda lo stesso
        rec['inviati'] = sorted(done)
        sent[night] = rec
        save_state(state_path, sent)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
