"""Avvisi aurora: notifiche push sui telefoni nelle notti del viaggio.

Lanciato dal workflow "Avvisi aurora" (.github/workflows/avvisi-aurora.yml).
Usa la stessa stima dell'app (Kp previsto NOAA × cielo sereno Open-Meteo, solo
nelle ore di buio) nei posti in cui siete la sera, tappa per tappa
(evening_stops in render.py; di default l'alloggio della notte). Avvisi:

- "mattino":    alle 7:30 di ogni giorno del viaggio, sempre: com'è messa stasera,
                con una frase scherzosa (personalizzata se il telefono ha un nome);
- "previsione": la sera, solo se la stima diventa "buone" e al mattino non lo era
                (cambio di programma in meglio);
- "adesso":     quando è buio e Kp misurato + nuvole di quest'ora sono buoni.

Variabili d'ambiente:
  VAPID_PRIVATE_KEY     chiave privata VAPID (secret del repo)
  AURORA_SUBSCRIPTIONS  codici copiati dall'app ("Attiva avvisi aurora"), uno dopo
                        l'altro; un nome davanti ("Federica: {...}") personalizza le frasi
  AURORA_MODE           "controllo" (default), "mattino" oppure "prova" (notifica subito)
  AURORA_STATE          file con gli avvisi già inviati (default .aurora-state/state.json)
  AURORA_NOW            solo per test: istante da simulare (ISO, UTC)

Uso: python3 tools/aurora_alert.py  (dalla radice del repo, dopo render.py)
"""
import json, math, os, random, re, sys, urllib.request
from datetime import datetime, timedelta, timezone

VAPID_SUB = 'https://werblo.github.io'   # contatto per i servizi push (solo dominio)
KP_FORECAST_URL = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json'
KP_NOW_URL = 'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json'
CLOUDS_URL = ('https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
              '&hourly=cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high'
              '&timezone=UTC&past_days=1&forecast_days=3')
GOOD = 0.45   # soglia di "buone probabilità", come nell'app


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
    est = {'hours': hours, 'level': None, 'stops': [], 'last': places[stops[-1]['place']]['name']}
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
    return f'{kp:.1f}'.replace('.0', '')


def place_label(est):
    names = [short_name(s['name']) for s in est['stops']]
    return ' → '.join(names) if len(names) > 1 else (names[0] if names else est['last'])


def details(est):
    """Riga di dettaglio: tappe, ore migliori, Kp, nuvole."""
    parts = []
    if len(est['stops']) > 1:
        parts += [f'{short_name(s["name"])} {s["from"]:%H}–{s["end"]:%H}: {s["level"]}' for s in est['stops']]
    if est['level'] != 'nulle' and est['windows']:
        parts.append('meglio ' + ' e '.join(f'{a:%H}:00–{b:%H}:00' for a, b in est['windows'][:2]))
    parts.append('Kp fino a ' + fmt_kp(est['kp_max']))
    if est['clouds']:
        lo, hi = min(est['clouds']), max(est['clouds'])
        parts.append(f'nuvole {lo}%' if lo == hi else f'nuvole {lo}–{hi}%')
    return ' · '.join(parts)


def describe(est):
    if not est['hours']:
        return f'{est["last"]}: niente buio astronomico stanotte.'
    if not est['level']:
        return f'{place_label(est)}: previsione non disponibile.'
    return f'{place_label(est)}: {est["level"]} probabilità · ' + details(est)


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
        'nd': ["🔭 Fede, stamattina la previsione dell'aurora non arriva: ricontrolla l'app in serata."],
        'strada': ["🚗 Fede, stasera tieni d'occhio il cielo lungo la strada per {ultimo}: se si apre, fermatevi in una piazzola sicura!"],
        'viaggio': ["🛁 Fede, stasera guarda in alto già {da_migliore}, poi anche lungo la strada per {ultimo}!"],
    },
}


MORNING_TITLES = {'buone': '🌅 Aurora stasera: buone probabilità', 'scarse': '🌅 Aurora stasera: qualche chance',
                  'nulle': '🌅 Aurora stasera: quasi impossibile'}


def is_federica(name):
    return re.fullmatch(r'fede(rica)?', name.strip().lower()) is not None


def morning_phrase(name, est, night):
    """Frase del mattino per un telefono: stesso giorno e stesso nome -> stessa frase."""
    pool = PHRASES['federica'] if is_federica(name) else PHRASES['nome'] if name else PHRASES['tutti']
    level = est['level']
    kind = level or 'nd'
    stops = est['stops']
    last = stops[-1] if stops else None
    # tappa migliore: solo se è strettamente meglio dell'ultima (a pari merito vale l'ultima)
    best_stop = max(stops, key=lambda s: s['best']) if stops else None
    if best_stop and last and best_stop['best'] <= last['best']:
        best_stop = last
    # sera in movimento e la tappa migliore non è l'ultima: frase "di viaggio"
    if level in ('buone', 'scarse') and len(stops) > 1 and best_stop is not last and best_stop['level'] != 'nulle':
        kind = 'strada' if best_stop['name'].startswith('strada') else 'viaggio'
    text = random.Random(f'{night}|{name}|{kind}').choice(pool[kind])
    migliore = short_name(best_stop['name']) if best_stop else ''
    # con più tappe {luogo} è la tappa migliore della serata, non tutto il percorso
    luogo = migliore if len(stops) > 1 else place_label(est)
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
            name = re.sub(r'[^\wÀ-ÿ\' -]', '', label).strip()
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
    state_path = os.environ.get('AURORA_STATE', '.aurora-state/state.json')
    now = (parse_time(os.environ['AURORA_NOW']).astimezone(timezone.utc) if os.environ.get('AURORA_NOW')
           else datetime.now(timezone.utc)).replace(second=0, microsecond=0)
    manual = os.environ.get('AURORA_MANUAL') == '1'   # lanciato a mano dalla tab Actions
    trip = trip_data()

    # la notte "di stasera" inizia alle 12 UTC di oggi (di notte, prima delle 10, è ancora
    # quella di ieri; il messaggio del mattino parla invece della sera che verrà).
    # In Islanda l'ora locale coincide con UTC tutto l'anno.
    start = now.replace(hour=12, minute=0) - timedelta(days=1 if now.hour < 10 and mode != 'mattino' else 0)
    night = start.strftime('%Y-%m-%d')
    trip_nights = {d['dateISO'] for d in trip['days'] if d['id'] != 'd8'}
    if mode == 'controllo' and night not in trip_nights:
        print(f'Notte del {night}: fuori dalle date del viaggio, nessun controllo.')
        return 0

    stops = night_stops(night, trip)
    subs = parse_subscriptions(os.environ.get('AURORA_SUBSCRIPTIONS'))
    names = ', '.join(n or '(senza nome)' for n, _ in subs)
    print(f'Notte del {night} · tappe: {" → ".join(s["place"] for s in stops)} · {now:%H:%M} UTC'
          f' · nuvole: {trip["method"]} · telefoni: {len(subs)} ({names})')

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
    if mode == 'controllo':
        try:
            last = get_json(KP_NOW_URL)[-1]
            kp_now = float(last.get('estimated_kp', last.get('kp_index')))
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
        return 0 if ok == len(subs) else 1

    sent = load_state(state_path)
    rec = sent.get(night)
    rec = {'inviati': rec} if isinstance(rec, list) else (rec or {'inviati': []})
    done = set(rec['inviati'])

    if mode == 'mattino':
        body_info = '\n' + details(est) if est['level'] else ''
        ok = send_all(subs, lambda name: {
            'title': MORNING_TITLES.get(est['level'], '🌅 Aurora stasera: previsione non disponibile'),
            'body': morning_phrase(name, est, night) + body_info,
            'tag': f'aurora-{night}-mattino'}, ttl=4 * 3600)
        if manual:
            print('Anteprima lanciata a mano: lo stato della notte non viene toccato.')
        elif ok:
            rec['mattino'] = est['level']
            done.add('mattino')
            rec['inviati'] = sorted(done)
            sent[night] = rec
            save_state(state_path, sent)
        return 0 if ok else 1

    alerts = []
    morning = rec.get('mattino')
    # 1) cambio di programma: stanotte "buone", ma al mattino non lo era (o il mattino è mancato).
    #    Solo con dati sulle nuvole: senza, il solo Kp darebbe un falso "buone".
    if ('previsione' not in done and est['level'] == 'buone' and morning != 'buone' and est['clouds']
            and any(b > now for _, b in est['windows'])):
        title = ('🔄 Cambio di programma: stanotte buone probabilità!' if morning
                 else '🌌 Aurora stanotte: buone probabilità')
        alerts.append(('previsione', {'title': title, 'body': place_label(est) + ' · ' + details(est),
                                      'tag': f'aurora-{night}-previsione'}, 6 * 3600))

    # 2) adesso: buio, Kp misurato e cielo di quest'ora buoni, dove siete adesso
    place = stop_at(stops, now)['place']
    loc = trip['places'][place]
    cloud = clouds.get(place, {}).get(hour_key(now))
    dark = sun_altitude(now, loc['lat'], loc['lon']) < -12
    if 'adesso' not in done and dark and kp_now is not None:
        sky = 0.5 if cloud is None else (100 - cloud) / 100
        if kp_factor(kp_now) * sky >= GOOD:
            alerts.append(('adesso', {
                'title': '🌌 Aurora: condizioni buone adesso',
                'body': f'{short_name(loc["name"])}: Kp {fmt_kp(kp_now)} in questo momento'
                        + (f', nuvole {cloud}%' if cloud is not None else '')
                        + '. Allontanatevi dalle luci e guardate verso nord!',
                'tag': f'aurora-{night}-adesso',
            }, 3600))

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
