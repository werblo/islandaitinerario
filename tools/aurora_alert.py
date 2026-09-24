"""Avvisi aurora: notifica push sui telefoni quando stanotte l'aurora è probabile.

Lanciato dal workflow "Avvisi aurora" (.github/workflows/avvisi-aurora.yml)
ogni 30 minuti nelle notti del viaggio. Usa la stessa stima dell'app
(Kp previsto NOAA × cielo sereno Open-Meteo, solo nelle ore di buio) per
l'alloggio della notte, e manda al massimo due avvisi per notte:

- "previsione": appena la stima della notte diventa "buone probabilità";
- "adesso":     quando è buio e Kp misurato + nuvole di quest'ora sono buoni.

Variabili d'ambiente:
  VAPID_PRIVATE_KEY     chiave privata VAPID (secret del repo)
  AURORA_SUBSCRIPTIONS  codici copiati dall'app ("Attiva avvisi aurora"),
                        uno dopo l'altro (secret del repo)
  AURORA_MODE           "controllo" (default) oppure "prova" (notifica subito)
  AURORA_STATE          file con gli avvisi già inviati (default .aurora-state/state.json)
  AURORA_NOW            solo per test: istante da simulare (ISO, UTC)

Uso: python3 tools/aurora_alert.py  (dalla radice del repo, dopo render.py)
"""
import json, math, os, re, sys, urllib.request
from datetime import datetime, timedelta, timezone

VAPID_SUB = 'https://werblo.github.io'   # contatto per i servizi push (solo dominio)
KP_FORECAST_URL = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json'
KP_NOW_URL = 'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json'
CLOUDS_URL = ('https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
              '&hourly=cloud_cover&timezone=UTC&past_days=1&forecast_days=3')
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
    return const('LOCATIONS'), const('DAYS_META')


def night_place_key(date_iso, days):
    # come nightPlaceKey() nell'app: l'alloggio di quel giorno (l'ultimo giorno si riparte)
    day = next((d for d in days if d['dateISO'] == date_iso and d['id'] != 'd8'), None)
    return day['locKey'] if day else 'reykjavik'


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


def clouds_by_hour(data):
    h = (data or {}).get('hourly') or {}
    return {t: c for t, c in zip(h.get('time', []), h.get('cloud_cover', [])) if c is not None}


def kp_factor(kp):
    # alle latitudini islandesi l'aurora si vede spesso già con Kp 2-3
    if kp >= 5: return 1
    if kp >= 4: return 0.85
    if kp >= 3: return 0.65
    if kp >= 2: return 0.4
    return 0.15


def hour_key(t):
    return t.strftime('%Y-%m-%dT%H:00')


def night_estimate(start, loc, kp_rows, clouds):
    """Come nightEstimate() nell'app: ore di buio astronomico della notte che inizia alle 12 UTC."""
    hours = []
    for i in range(24):
        t = start + timedelta(hours=i)
        if sun_altitude(t + timedelta(minutes=30), loc['lat'], loc['lon']) >= -18:
            continue
        kp = next((k for rt, k in kp_rows if rt <= t < rt + timedelta(hours=3)), None)
        hours.append({'t': t, 'kp': kp, 'cloud': clouds.get(hour_key(t))})
    with_kp = [h for h in hours if h['kp'] is not None]
    est = {'hours': hours, 'level': None}
    if not with_kp:
        return est
    has_clouds = any(h['cloud'] is not None for h in with_kp)
    for h in with_kp:
        sky = (0.5 if has_clouds else 1) if h['cloud'] is None else (100 - h['cloud']) / 100
        h['score'] = kp_factor(h['kp']) * sky
    best = max(h['score'] for h in with_kp)
    est['level'] = 'buone' if best >= GOOD else 'scarse' if best >= 0.2 else 'nulle'
    est['kp_max'] = max(h['kp'] for h in with_kp)
    est['clouds'] = [h['cloud'] for h in with_kp if h['cloud'] is not None]
    windows = []
    for h in with_kp:
        if h['score'] < max(0.2, best * 0.8):
            continue
        if windows and windows[-1][1] == h['t']:
            windows[-1][1] = h['t'] + timedelta(hours=1)
        else:
            windows.append([h['t'], h['t'] + timedelta(hours=1)])
    est['windows'] = windows
    return est


def fmt_kp(kp):
    return f'{kp:.1f}'.replace('.0', '')


def describe(est, place):
    if not est['hours']:
        return f'{place}: niente buio astronomico stanotte.'
    if not est['level']:
        return f'{place}: previsione non disponibile.'
    parts = [f'{place}: {est["level"]} probabilità']
    if est['level'] != 'nulle' and est['windows']:
        parts.append('meglio ' + ' e '.join(f'{a:%H}:00–{b:%H}:00' for a, b in est['windows'][:2]))
    parts.append('Kp fino a ' + fmt_kp(est['kp_max']))
    if est['clouds']:
        lo, hi = min(est['clouds']), max(est['clouds'])
        parts.append(f'nuvole {lo}%' if lo == hi else f'nuvole {lo}–{hi}%')
    return ' · '.join(parts)


# ---------- iscrizioni e invio ----------
def parse_subscriptions(text):
    """Accetta i codici incollati uno dopo l'altro (o una lista JSON)."""
    subs, dec, i = [], json.JSONDecoder(), 0
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
            if obj['endpoint'] not in [s['endpoint'] for s in subs]:
                subs.append(obj)
        i = end
    return subs


def send_all(subs, payload, ttl):
    from pywebpush import webpush, WebPushException
    key = os.environ.get('VAPID_PRIVATE_KEY', '').strip()
    if not key:
        print('::error::Manca il secret VAPID_PRIVATE_KEY')
        return 0
    ok = 0
    for n, sub in enumerate(subs, 1):
        host = re.sub(r'^https?://([^/]+).*$', r'\1', sub['endpoint'])
        try:
            webpush(sub, json.dumps(payload, ensure_ascii=False), vapid_private_key=key,
                    vapid_claims={'sub': VAPID_SUB}, ttl=ttl, headers={'Urgency': 'high'})
            print(f'Telefono {n} ({host}): inviata')
            ok += 1
        except WebPushException as e:
            code = getattr(e.response, 'status_code', None)
            if code in (404, 410):
                print(f'::warning::Telefono {n} ({host}): iscrizione scaduta, '
                      'ricopia il codice dall\'app e aggiorna AURORA_SUBSCRIPTIONS')
            else:
                print(f'::warning::Telefono {n} ({host}): invio fallito ({code or e})')
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
    now = (parse_time(os.environ['AURORA_NOW']) if os.environ.get('AURORA_NOW')
           else datetime.now(timezone.utc)).replace(second=0, microsecond=0)
    locations, days = trip_data()

    # la notte "di stasera" inizia alle 12 UTC di oggi (prima delle 10 è ancora quella di ieri);
    # in Islanda l'ora locale coincide con UTC tutto l'anno
    start = now.replace(hour=12, minute=0) - timedelta(days=1 if now.hour < 10 else 0)
    night = start.strftime('%Y-%m-%d')
    trip_nights = {d['dateISO'] for d in days if d['id'] != 'd8'}
    if mode != 'prova' and night not in trip_nights:
        print(f'Notte del {night}: fuori dalle date del viaggio, nessun controllo.')
        return 0

    place_key = night_place_key(night, days)
    loc = locations[place_key]
    subs = parse_subscriptions(os.environ.get('AURORA_SUBSCRIPTIONS'))
    print(f'Notte del {night} a {loc["name"]} · {now:%H:%M} UTC · telefoni iscritti: {len(subs)}')

    kp_rows, clouds, kp_now = [], {}, None
    try:
        kp_rows = parse_kp_forecast(get_json(KP_FORECAST_URL))
    except Exception as e:
        print(f'::warning::Previsione Kp NOAA non disponibile: {e}')
    try:
        clouds = clouds_by_hour(get_json(CLOUDS_URL.format(**loc)))
    except Exception as e:
        print(f'::warning::Nuvolosità Open-Meteo non disponibile: {e}')
    try:
        last = get_json(KP_NOW_URL)[-1]
        kp_now = float(last.get('estimated_kp', last.get('kp_index')))
    except Exception as e:
        print(f'::warning::Kp attuale NOAA non disponibile: {e}')

    est = night_estimate(start, loc, kp_rows, clouds)
    summary = describe(est, loc['name'])
    print('Stima:', summary)

    if mode == 'prova':
        if not subs:
            print('::error::Nessun telefono in AURORA_SUBSCRIPTIONS: copia il codice dall\'app '
                  '("Attiva avvisi aurora") e incollalo nel secret.')
            return 1
        payload = {'title': '🔔 Prova avvisi aurora', 'tag': 'aurora-prova',
                   'body': 'Le notifiche funzionano. Stanotte a ' + summary
                           if est['level'] else 'Le notifiche funzionano!'}
        ok = send_all(subs, payload, ttl=3600)
        print(f'Prova inviata a {ok} telefoni su {len(subs)}.')
        return 0 if ok == len(subs) else 1

    sent = load_state(state_path)
    done = set(sent.get(night, []))
    alerts = []

    # 1) previsione della notte: buone probabilità in una fascia non ancora passata
    if 'previsione' not in done and est['level'] == 'buone' and any(b > now for _, b in est['windows']):
        alerts.append(('previsione', {
            'title': '🌌 Aurora stanotte: buone probabilità',
            'body': summary.replace(': buone probabilità', ''),
            'tag': 'aurora-' + night,
        }, 6 * 3600))

    # 2) adesso: buio, Kp misurato e cielo di quest'ora buoni
    cloud = clouds.get(hour_key(now))
    dark = sun_altitude(now, loc['lat'], loc['lon']) < -12
    if 'adesso' not in done and dark and kp_now is not None:
        sky = 0.5 if cloud is None else (100 - cloud) / 100
        if kp_factor(kp_now) * sky >= GOOD:
            alerts.append(('adesso', {
                'title': '🌌 Aurora: condizioni buone adesso',
                'body': f'{loc["name"]}: Kp {fmt_kp(kp_now)} in questo momento'
                        + (f', nuvole {cloud}%' if cloud is not None else '')
                        + '. Allontanatevi dalle luci e guardate verso nord!',
                'tag': 'aurora-' + night,
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
        if send_all(subs, payload, ttl):
            done.add(kind)
        else:
            failed = True
    sent[night] = sorted(done)
    save_state(state_path, sent)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
