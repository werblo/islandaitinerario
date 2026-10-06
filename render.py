import json, html, math, re, urllib.parse

with open('cinzel.b64') as f:
    cinzel_b64 = f.read().strip()
with open('plex.b64') as f:
    plex_b64 = f.read().strip()

from dati import *   # tutti i dati del viaggio: modificali in dati.py


def e(s):
    return html.escape(s, quote=True) if s else ''

LOGISTICS_TITLES_LOWER = {'partenza presto'}
def is_logistics(title):
    if title.strip().lower() in LOGISTICS_TITLES_LOWER:
        return True
    return bool(re.search(r'check-in|check-out|ritiro auto|riconsegna auto|partenza da|volo ', title, re.I))

import unicodedata
ICELANDIC_MAP = str.maketrans({'Þ':'Th','þ':'th','Ð':'D','ð':'d','Æ':'Ae','æ':'ae','Ö':'O','ö':'o'})
# Percorsi e tratte calcolati con OSRM (azione GitHub "Aggiorna percorsi mappa").
try:
    with open('routes.json', encoding='utf-8') as f:
        _routes_raw = json.load(f)
except FileNotFoundError:
    _routes_raw = {}


def slugify(s):
    s = s.translate(ICELANDIC_MAP)
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode('ascii')
    s = re.sub(r'\(.*?\)', '', s)
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s

# ============================================================
# ICONE ILLUSTRATE — una per tema, riconosciute dal nome del luogo.
# Sostituiscono la foto finché non viene aggiunto un file reale in images/.
# ============================================================

ICON_BG = {
    'airplane':    ('#1b2c40', '#28405c'),
    'village':     ('#3a2f22', '#5c4a33'),
    'rift':        ('#22344a', '#33506b'),
    'geyser':      ('#2c4a55', '#3d6470'),
    'waterfall':   ('#22384a', '#2f5468'),
    'lagoon':      ('#2c4a4a', '#3d6a68'),
    'dome':        ('#1b2c40', '#2c4560'),
    'concerthall': ('#2c2440', '#463a63'),
    'geocoast':    ('#2c4a55', '#3d6470'),
    'blacksand':   ('#20242c', '#333a46'),
    'arch':        ('#22384a', '#2f5468'),
    'iceberg':     ('#1f3a4a', '#2e5a6e'),
    'canyon':      ('#33291f', '#5c4830'),
    'crater':      ('#33291f', '#5c4830'),
    'hotriver':    ('#2c4a55', '#3d6470'),
    'museum':      ('#2c2440', '#463a63'),
    'saga':        ('#16263b', '#22344a'),
}

def icon_svg(key):
    amber, paper, teal = '#d9985f', '#f2ede2', '#8fd6cd'
    if key == 'airplane':
        return ('<path d="M8 40 L46 20 L58 22 L48 30 L34 30 L26 40 L20 38 L24 30 L14 32 Z" fill="' + amber + '"/>'
                '<path d="M4 44 L16 41 M4 50 L18 46" stroke="' + paper + '" stroke-width="1.6" opacity="0.5"/>')
    if key == 'village':
        return ('<rect x="8" y="30" width="14" height="16" fill="' + paper + '"/><polygon points="6,30 15,20 24,30" fill="' + amber + '"/>'
                '<rect x="26" y="24" width="16" height="22" fill="' + paper + '" opacity="0.9"/><polygon points="24,24 34,12 44,24" fill="' + amber + '"/>'
                '<rect x="46" y="33" width="12" height="13" fill="' + paper + '" opacity="0.8"/><polygon points="44,33 52,25 60,33" fill="' + amber + '"/>')
    if key == 'rift':
        return ('<polygon points="6,8 26,14 22,52 4,52" fill="' + paper + '" opacity="0.85"/>'
                '<polygon points="38,14 58,8 60,52 42,52" fill="' + paper + '" opacity="0.65"/>'
                '<path d="M27 12 L24 52 M37 13 L40 52" stroke="' + teal + '" stroke-width="2"/>')
    if key == 'geyser':
        return ('<path d="M6 50 Q32 46 58 50" stroke="' + paper + '" stroke-width="2" fill="none" opacity="0.6"/>'
                '<path d="M32 48 C30 34 34 20 30 8" stroke="' + paper + '" stroke-width="4" fill="none" stroke-linecap="round"/>'
                '<circle cx="26" cy="12" r="2.2" fill="' + paper + '"/><circle cx="36" cy="6" r="2" fill="' + paper + '"/><circle cx="30" cy="4" r="1.6" fill="' + paper + '"/>'
                '<path d="M14 44 Q18 36 14 28" stroke="' + teal + '" stroke-width="1.6" fill="none" opacity="0.7"/>'
                '<path d="M50 44 Q46 36 50 28" stroke="' + teal + '" stroke-width="1.6" fill="none" opacity="0.7"/>')
    if key == 'waterfall':
        return ('<polygon points="2,52 18,10 22,52" fill="' + amber + '" opacity="0.55"/>'
                '<polygon points="42,52 46,10 62,52" fill="' + amber + '" opacity="0.75"/>'
                '<polygon points="20,12 30,8 44,12 38,40 26,40" fill="' + paper + '" opacity="0.92"/>'
                '<path d="M25 18 Q28 26 25 34 M33 16 Q36 26 33 36 M39 18 Q41 26 39 34" stroke="' + teal + '" stroke-width="1.3" fill="none" opacity="0.7"/>'
                '<ellipse cx="31" cy="49" rx="22" ry="6" fill="' + teal + '" opacity="0.55"/>')
    if key == 'lagoon':
        return ('<ellipse cx="32" cy="42" rx="26" ry="12" fill="' + teal + '" opacity="0.6"/>'
                '<path d="M16 26 Q20 18 16 10 M30 22 Q34 14 30 6 M44 26 Q48 18 44 10" stroke="' + paper + '" stroke-width="2" fill="none" opacity="0.55" stroke-linecap="round"/>'
                '<polygon points="2,50 10,36 18,50" fill="' + amber + '" opacity="0.5"/>')
    if key == 'dome':
        return ('<rect x="12" y="34" width="40" height="16" fill="' + paper + '" opacity="0.85"/>'
                '<path d="M14 34 A18 18 0 0 1 50 34 Z" fill="' + amber + '"/>'
                '<path d="M20 34 L20 20 M28 34 L28 15 M36 34 L36 15 M44 34 L44 20" stroke="' + '#1b2c40' + '" stroke-width="1.4" opacity="0.5"/>')
    if key == 'concerthall':
        return ('<polygon points="6,50 6,26 20,14 34,24 34,50" fill="' + amber + '" opacity="0.85"/>'
                '<polygon points="34,50 34,24 48,16 58,28 58,50" fill="' + teal + '" opacity="0.55"/>'
                '<path d="M10 30 L30 30 M10 38 L30 38 M38 32 L54 32 M38 40 L54 40" stroke="' + '#1b2c40' + '" stroke-width="1" opacity="0.4"/>')
    if key == 'geocoast':
        return ('<path d="M2 40 Q16 30 30 40 T58 40" stroke="' + teal + '" stroke-width="2.5" fill="none"/>'
                '<rect x="46" y="12" width="5" height="20" fill="' + paper + '"/><polygon points="44,12 48,4 53,12" fill="' + amber + '"/>'
                '<path d="M14 36 Q17 28 14 20 M22 36 Q25 30 22 24" stroke="' + paper + '" stroke-width="1.6" fill="none" opacity="0.6" stroke-linecap="round"/>')
    if key == 'blacksand':
        return ('<polygon points="2,52 6,26 18,14 26,24 22,52" fill="' + amber + '" opacity="0.7"/>'
                '<polygon points="10,40 17,32 24,40 17,48" fill="' + paper + '" opacity="0.85"/>'
                '<polygon points="22,42 29,34 36,42 29,50" fill="' + paper + '" opacity="0.7"/>'
                '<path d="M2 50 Q30 44 62 50" stroke="' + teal + '" stroke-width="2.5" fill="none"/>'
                '<path d="M38 52 Q48 46 60 52" stroke="' + teal + '" stroke-width="1.6" fill="none" opacity="0.6"/>')
    if key == 'arch':
        return ('<path d="M10 52 C10 22 50 22 50 52" stroke="' + paper + '" stroke-width="7" fill="none"/>'
                '<path d="M2 46 Q20 40 30 46 T58 46" stroke="' + teal + '" stroke-width="2.5" fill="none"/>'
                '<path d="M44 14 l3 -3 3 2 M50 12 l3 -3 3 2" stroke="' + paper + '" stroke-width="1.2" fill="none" opacity="0.6"/>')
    if key == 'iceberg':
        return ('<path d="M2 46 Q30 40 60 46" stroke="' + teal + '" stroke-width="2.5" fill="none"/>'
                '<polygon points="10,46 18,24 28,46" fill="' + paper + '" opacity="0.9"/>'
                '<polygon points="24,46 36,18 50,46" fill="' + paper + '" opacity="0.7"/>'
                '<polygon points="42,46 50,30 58,46" fill="' + paper + '" opacity="0.55"/>')
    if key == 'canyon':
        return ('<polygon points="2,52 2,10 16,20 10,30 20,38 12,52" fill="' + amber + '" opacity="0.55"/>'
                '<polygon points="60,52 60,10 46,20 52,30 42,38 50,52" fill="' + amber + '" opacity="0.75"/>'
                '<path d="M22 40 Q31 46 40 40" stroke="' + teal + '" stroke-width="2" fill="none"/>')
    if key == 'crater':
        return ('<ellipse cx="31" cy="30" rx="27" ry="18" fill="none" stroke="' + amber + '" stroke-width="4"/>'
                '<ellipse cx="31" cy="32" rx="15" ry="9" fill="' + teal + '" opacity="0.7"/>')
    if key == 'hotriver':
        return ('<ellipse cx="16" cy="44" rx="16" ry="10" fill="' + amber + '" opacity="0.4"/>'
                '<ellipse cx="48" cy="18" rx="16" ry="10" fill="' + amber + '" opacity="0.4"/>'
                '<path d="M4 40 Q20 30 32 32 T58 20" stroke="' + teal + '" stroke-width="3" fill="none" stroke-linecap="round"/>'
                '<path d="M26 30 Q29 24 26 18" stroke="' + paper + '" stroke-width="1.4" fill="none" opacity="0.6"/>')
    if key == 'museum':
        return ('<polygon points="6,24 31,6 56,24" fill="' + amber + '"/>'
                '<rect x="8" y="24" width="46" height="6" fill="' + amber + '" opacity="0.6"/>'
                '<rect x="10" y="30" width="42" height="18" fill="' + paper + '" opacity="0.9"/>'
                '<rect x="17" y="30" width="4" height="18" fill="' + '#1b2c40' + '" opacity="0.5"/>'
                '<rect x="29" y="30" width="4" height="18" fill="' + '#1b2c40' + '" opacity="0.5"/>'
                '<rect x="41" y="30" width="4" height="18" fill="' + '#1b2c40' + '" opacity="0.5"/>'
                '<rect x="6" y="48" width="50" height="4" fill="' + amber + '"/>')
    if key == 'saga':
        return ('<path d="M2 20 Q20 8 34 18 T62 12" stroke="' + teal + '" stroke-width="2" fill="none" opacity="0.8"/>'
                '<circle cx="50" cy="9" r="4.5" fill="' + paper + '"/>'
                '<polygon points="6,50 20,26 34,50" fill="' + paper + '" opacity="0.9"/>'
                '<polygon points="26,50 42,18 60,50" fill="' + amber + '"/>')
    # fallback generico
    return ('<path d="M0 34 L14 20 L26 30 L40 12 L54 26 L64 16 L64 40 L0 40 Z" fill="' + paper + '"/>'
            '<circle cx="50" cy="9" r="6" fill="' + amber + '"/>')

HERO_ICON = {
    'd1': 'airplane', 'd2': 'dome', 'd3': 'rift', 'd4': 'blacksand',
    'd5': 'iceberg', 'd6': 'crater', 'd7': 'hotriver', 'd8': 'airplane',
}

def guess_icon(title):
    t = title.lower()
    checks = [
        (['volo', 'aeroporto'], 'airplane'),
        (['þingvellir', 'thingvellir'], 'rift'),
        (['geysir', 'strokkur'], 'geyser'),
        (['faxi'], 'waterfall'),
        (['foss'], 'waterfall'),
        (['perlan'], 'dome'),
        (['harpa'], 'concerthall'),
        (['museum'], 'museum'),
        (['reykjanes'], 'geocoast'),
        (['reynisfjara'], 'blacksand'),
        (['dyrhólaey', 'dyrholaey'], 'arch'),
        (['jökulsárlón', 'jokulsarlon', 'diamond beach'], 'iceberg'),
        (['fjaðrárgljúfur', 'fjadrargljufur'], 'canyon'),
        (['kerið', 'kerid'], 'crater'),
        (['reykjadalur', 'hot spring'], 'hotriver'),
        (['secret lagoon', 'sky lagoon', 'lagoon'], 'lagoon'),
        (['passeggiata', 'centro', 'villaggio'], 'village'),
    ]
    for keywords, key in checks:
        if any(k in t for k in keywords):
            return key
    return 'village'

# inquadratura delle foto principali (ritagliate a 180 px di altezza) dove il centro non basta
HERO_POS = {'d4': 'center 28%', 'd6': 'center 75%', 'storia': 'center 40%'}

def photo_slot(filename, label, css_class, icon_key='village', pos=None, eager=False):
    bg1, bg2 = ICON_BG.get(icon_key, ('#3a2f22', '#5c4a33'))
    inner = icon_svg(icon_key)
    webp_name = re.sub(r'\.jpg$', '.webp', filename)
    return (f'<div class="photo-slot {css_class}" data-photo="{e(filename)}" '
            f'style="--bg1:{bg1};--bg2:{bg2}">'
            f'<img src="images/web/{webp_name}" alt="{e(label)}" '
            + ('fetchpriority="high" ' if eager else 'loading="lazy" ')
            + (f'style="object-position:{pos}" ' if pos else '') +
            f'onerror="this.parentElement.classList.add(\'photo-slot--empty\')">'
            f'<div class="photo-slot__ph"><svg viewBox="0 0 64 56" class="photo-slot__icon" aria-hidden="true">{inner}</svg>'
            f'<span>{e(label)}</span></div></div>')

# Stato strade in tempo reale (Vegagerðin), allerte meteo (Veðurstofan) e avvisi
# di sicurezza del giorno (Safetravel, soccorso alpino islandese):
# pagine nazionali, quindi una sola riga per giorno, non per ogni tratta.
ROAD_COND_URL = 'https://umferdin.is/en'
VEDUR_ALERTS_URL = 'https://en.vedur.is/alerts'
SAFETRAVEL_URL = 'https://safetravel.is/'
LEG_LINKS_HTML = (f'<div class="leg-links">'
                  f'<a href="{ROAD_COND_URL}" target="_blank" rel="noopener" class="leg-link" aria-label="Stato delle strade in Islanda in tempo reale, umferdin.is">Strade ↗</a>'
                  f'<a href="{VEDUR_ALERTS_URL}" target="_blank" rel="noopener" class="leg-link" aria-label="Allerte vento e meteo in Islanda, vedur.is">Allerte meteo ↗</a>'
                  f'<a href="{SAFETRAVEL_URL}" target="_blank" rel="noopener" class="leg-link" aria-label="Avvisi di sicurezza del giorno, safetravel.is">Sicurezza ↗</a>'
                  f'</div>')

# Coordinate delle località citate nelle tratte (per calcolarne km e tempi con
# OSRM): tappe della mappa, località principali e qualche nome alternativo.
LEG_ALIASES = {
    'Aeroporto di Keflavík': 'Aeroporto Keflavík',
    'Keflavík': 'Aeroporto Keflavík',
    'Ponte tra i continenti': 'Bridge Between Continents',
    'Vík': 'Vík í Mýrdal',
}


def leg_place(name):
    name = LEG_ALIASES.get(name, name)
    for pts in map_points.values():
        for p in pts:
            if p['name'].split(' (')[0] == name:
                return p['lat'], p['lon']
    for loc in locations.values():
        if loc['name'] == name:
            return loc['lat'], loc['lon']
    return None


def _fmt_minutes(m):
    m = max(5, int(round(m / 5.0)) * 5) if m >= 20 else max(1, int(round(m)))
    return f'~{m} min' if m < 60 else f'~{m // 60}h{m % 60:02d}'


def leg_values(day_id, i, leg):
    """km e tempo della tratta: da routes.json (OSRM) se calcolati per le stesse
    località, altrimenti i valori scritti a mano. Le note tra parentesi restano."""
    r = (_routes_raw.get('_legs') or {}).get(day_id) or []
    if i < len(r) and 'km' in r[i] and r[i].get('from') == leg['from'] and r[i].get('to') == leg['to']:
        suffix = leg['time'][leg['time'].index(' ('):] if ' (' in leg['time'] else ''
        km = r[i]['km']
        return ('meno di 1' if km < 1 else round(km)), _fmt_minutes(r[i]['min']) + suffix
    return leg['km'], leg['time']


def render_leg(leg, day_id='', i=0):
    note = f'<div class="leg-note">{e(leg["note"])}</div>' if leg.get('note') else ''
    route_label = f'{e(leg["from"])} → {e(leg["to"])}'
    km, time_ = leg_values(day_id, i, leg)
    return (f'<div class="leg"><div class="leg-route">{route_label}</div>'
            f'<div class="leg-meta">{km} km · {e(time_)}</div>{note}</div>')

def render_activity(day_id, idx, act):

    has_img = not is_logistics(act['title']) and act['title'].strip()
    img_html = ''
    if has_img:
        fname = f"{day_id}-{slugify(act['title'])}.jpg"
        img_html = photo_slot(fname, act['title'], 'photo-slot--thumb', guess_icon(act['title']))
    cost_html = f'<div class="act-cost">{e(act["cost"])}</div>' if act.get('cost') else ''
    desc_html = f'<div class="act-desc">{e(act["desc"])}</div>' if act.get('desc') else ''
    if act.get('link'):
        title_html = (f'<a class="act-title act-title--link" href="{e(act["link"])}" '
                       f'target="_blank" rel="noopener">{e(act["title"])}\u00a0<span class="act-title-arrow">\u2197</span></a>')
    else:
        title_html = f'<div class="act-title">{e(act["title"])}</div>'
    links_html = ''
    if act.get('link'):
        links_html += (f'<a class="act-link" href="{e(act["link"])}" target="_blank" rel="noopener">'
                        f'Scopri di più \u2197</a>')
    if act.get('nav'):
        maps_url = 'https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote(act['nav'])
        links_html += (f'<a class="act-link act-link--nav" href="{e(maps_url)}" target="_blank" rel="noopener">'
                        f'Naviga \u2197</a>')
    return (f'<div class="act-card">{img_html}<div class="act-body">'
            f'<div class="act-top">{title_html}'
            f'<div class="act-time">{e(act["time"])}</div></div>{desc_html}{cost_html}'
            + (f'<div class="act-links">{links_html}</div>' if links_html else '') + '</div></div>')

def render_food(f):
    note = f'<div class="food-note">{e(f["note"])}</div>' if f.get('note') else ''
    # badge solo dove abbiamo trovato opzioni senza glutine (ricerca ottobre 2026)
    gf = '<span class="gf-badge">opzioni senza glutine</span>' if f.get('gf') else ''
    return (f'<div class="food-card"><div class="food-top">'
            f'<div><strong>{e(f["meal"])}</strong> — {e(f["place"])}</div>'
            f'<div class="food-cost">{e(f["cost"])}</div></div>{note}{gf}</div>')

def render_day_section(day):
    legs_html = ''
    if day['legs']:
        legs_html = ('<div class="section"><div class="section-title">Spostamenti in auto</div>'
                     '<div class="stack">' + ''.join(render_leg(l, day['id'], i) for i, l in enumerate(day['legs'])) + '</div>'
                     + LEG_LINKS_HTML + '</div>')
    acts_html = ''.join(render_activity(day['id'], i, a) for i, a in enumerate(day['activities']))
    food_html = ''.join(render_food(f) for f in day['food'])
    acc = day.get('accommodation')
    acc_html = ''
    if acc:
        acc_name_html = e(acc["name"])
        if acc.get('url'):
            acc_name_html = f'<a href="{e(acc["url"])}" target="_blank" rel="noopener">{acc_name_html}</a>'
        parking_nav_html = ''
        if day.get('parking_nav'):
            links = ''.join(
                f'<a class="act-link act-link--nav" href="https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(p["query"])}" target="_blank" rel="noopener">{e(p["label"])} ↗</a>'
                for p in day['parking_nav']
            )
            parking_nav_html = f'<div class="acc-parking-nav">{links}</div>'
        acc_html = (f'<div class="acc-card"><div class="acc-name">Alloggio: {acc_name_html}</div>'
                    f'<div class="acc-detail">{e(acc["detail"])}</div>{parking_nav_html}</div>')
    tips_html = ''
    if day.get('tips'):
        tips_html = f'<div class="tip-card"><strong>Consiglio:</strong> {e(day["tips"])}</div>'

    aurora_note_html = '' if day['id'] == 'd8' else f'<div class="aurora-note" data-aurora="{day["id"]}">Calcolo delle ore di buio in corso…</div>'   # l'ultima sera siete in volo
    culture_html = ''
    if day.get('culture'):
        culture_icon = f'<svg viewBox="0 0 64 56" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{icon_svg("saga")}</svg>'
        culture_html = (f'<div class="culture-card"><div class="culture-card__label">{culture_icon}Storia &amp; curiosità</div>'
                         f'<p>{e(day["culture"])}</p></div>')

    hero_fname = f"{day['id']}-hero.jpg"

    return f'''
<section class="day-view page-view" id="view-{day['id']}" role="tabpanel" aria-labelledby="tab-{day['id']}" hidden>
  <div class="day-head">
    <div class="day-date">{e(day['dateLabel'])} · Giorno {day['num']}/8</div>
    <div class="day-title">{e(day['title'])}</div>
  </div>
  {photo_slot(hero_fname, day['title'], 'photo-slot--hero', HERO_ICON.get(day['id'], 'village'), HERO_POS.get(day['id']))}
  <div class="map-frame"><div class="day-map" id="day-map-{day['id']}" role="region" aria-label="Mappa del percorso del giorno {day['num']}"></div></div>
  <div class="line" style="margin:6px 0 0;font-size:0.8125rem;color:#5c6a78;">Mappa reale (OpenStreetMap) — zoomabile e trascinabile. Percorso stradale indicativo (disponibile anche offline); per la navigazione vera usa Google Maps offline.</div>
  <div class="grid2">
    <div class="info-card">
      <div class="info-card__label">Meteo · {e(locations[day['locKey']]['name'])}</div>
      <div class="info-card__big" data-weather-temp="{day['id']}">…</div>
      <div class="info-card__sub" data-weather-desc="{day['id']}">Caricamento…</div>
      <div class="info-card__source" data-weather-source="{day['id']}"></div>
    </div>
    <div class="info-card">
      <div class="info-card__label">Sole &amp; buio</div>
      <div class="sun-line">Alba <strong data-sunrise="{day['id']}">…</strong> · Tramonto <strong data-sunset="{day['id']}">…</strong></div>
      <div class="info-card__sub" data-daylight="{day['id']}">Calcolo…</div>
    </div>
  </div>
  {aurora_note_html}
  {culture_html}
  {legs_html}
  <div class="section">
    <div class="section-title">Itinerario</div>
    <div class="stack">{acts_html}</div>
  </div>
  <div class="section">
    <div class="section-title">Dove mangiare</div>
    <div class="stack">{food_html}</div>
  </div>
  {acc_html}
  {tips_html}
</section>'''

stays_html = ''.join(
    f'<div class="stay-row"><div class="stay-name">{e(s["name"])}</div><div class="stay-detail">{e(s["detail"])}</div></div>'
    for s in stays
)

DAY_WEEKDAYS_IT = {
    'Dom': 'domenica', 'Lun': 'lunedì', 'Mar': 'martedì', 'Mer': 'mercoledì',
    'Gio': 'giovedì', 'Ven': 'venerdì', 'Sab': 'sabato',
}
MONTHS_IT_GEN = {'nov': 'novembre'}

def _tab_btn(nav_id, label, aria_label, active):
    cls = 'nav-btn active' if active else 'nav-btn'
    sel = 'true' if active else 'false'
    tabindex = '0' if active else '-1'
    return (f'<button class="{cls}" id="tab-{nav_id}" data-nav="{nav_id}" role="tab" '
            f'aria-selected="{sel}" aria-controls="view-{nav_id}" tabindex="{tabindex}" '
            f'aria-label="{e(aria_label)}">{label}</button>')

nav_items = [_tab_btn('info', 'Info', 'Info', True)]
for d in days:
    parts = d['dateLabel'].split(' ')
    label = parts[1] + ' ' + parts[2]
    weekday_full = DAY_WEEKDAYS_IT.get(parts[0], parts[0])
    month_full = MONTHS_IT_GEN.get(parts[2], parts[2])
    aria_label = f"Giorno {d['num']}, {weekday_full} {parts[1]} {month_full}: {d['title']}"
    nav_items.append(_tab_btn(d['id'], e(label), aria_label, False))
nav_items.append(_tab_btn('storia', 'Storia', 'Storia dell\'Islanda', False))
nav_items.append(_tab_btn('checklist', 'Checklist', 'Checklist', False))
nav_html = ''.join(nav_items)

days_sections_html = ''.join(render_day_section(d) for d in days)

storia_html = f'''
<section class="page-view" id="view-storia" role="tabpanel" aria-labelledby="tab-storia" hidden>
  <div class="day-head">
    <div class="day-date"><span class="rune-mark">ᚨ</span>Infarinatura generale<span class="rune-mark">ᚾ</span></div>
    <div class="day-title"><span class="rune-mark">ᛋ</span>Storia dell'Islanda<span class="rune-mark">ᛁ</span></div>
  </div>
  {photo_slot('storia-hero.jpg', "Storia dell'Islanda", 'photo-slot--hero', 'saga', HERO_POS['storia'])}

  <div class="panel">
    <div class="panel-title"><span class="rune-mark">ᛒ</span>Un'isola giovanissima</div>
    <div class="rune-rule"></div>
    <p class="line">L'Islanda entra nella storia scritta molto tardi rispetto al resto d'Europa. Tra i primi ad avvistarla, intorno all'<strong>868 d.C.</strong>, è il navigatore norvegese <strong>Hrafna-Flóki Vilgerðarson</strong> ("Flóki dei corvi", dai tre corvi che portava con sé per trovare la rotta): dopo un inverno durissimo passato a osservare i fiordi pieni di ghiaccio alla deriva, se ne va deluso e ribattezza l'isola <strong>Ísland</strong>, "terra di ghiaccio" — il nome che porta ancora oggi. Solo pochi anni dopo, nell'<strong>874 d.C.</strong>, il norvegese Ingólfur Arnarson vi fonda il primo insediamento permanente, proprio dove oggi sorge Reykjavík. Secondo l'usanza vichinga, aveva lanciato in mare i pilastri del suo trono cerimoniale e costruito casa dove le correnti li avevano portati a riva. Nei decenni successivi arrivano altre migliaia di coloni, soprattutto dalla Norvegia, insieme a genti e schiavi dalle isole britanniche: da questo mix nasce la popolazione islandese.</p>
  </div>

  <div class="panel">
    <div class="panel-title"><span class="rune-mark">ᛏ</span>Dal primo parlamento all'indipendenza</div>
    <div class="rune-rule"></div>
    <p class="line">Nel <strong>930 d.C.</strong>, a Þingvellir, i capi dell'isola fondano l'<strong>Alþingi</strong>: un'assemblea annuale all'aperto per fare leggi e giudicare le liti, una delle istituzioni parlamentari più antiche ancora esistenti al mondo. È l'epoca del cosiddetto Commonwealth islandese, senza re né esercito centrale. Nel 1262, dilaniata da faide interne, l'isola giura fedeltà al re di Norvegia; nel 1380 passa sotto la corona danese insieme alla Norvegia. Bisogna aspettare il <strong>1º dicembre 1918</strong> per un regno autonomo (ma ancora legato alla Danimarca), e il <strong>17 giugno 1944</strong> per la Repubblica islandese piena, approvata al referendum con oltre il 98% dei voti mentre la Danimarca era sotto occupazione tedesca.</p>
  </div>

  <div class="culture-card">
    <div class="culture-card__label">{f'<svg viewBox="0 0 64 56" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{icon_svg("saga")}</svg>'}<span class="rune-mark">ᚱ</span>Le saghe e una lingua rimasta ferma nel tempo</div>
    <p>Preparatevi a un piccolo miracolo linguistico: l'islandese di oggi è così vicino al norreno medievale che un lettore islandese può ancora leggere le saghe scritte otto secoli fa, senza traduzione — un lusso che i cugini scandinavi hanno perso da tempo. Altrettanto insolito è il sistema dei nomi: niente cognomi di famiglia, solo patronimici o matronimici (un Jónsson è "figlio di Jón"), tanto che l'elenco telefonico islandese è ordinato per nome di battesimo. La popolazione resta minuscola, circa 390.000 persone su un'isola grande quanto il Portogallo, e fino a poco tempo fa con un primato curioso: nessuna zanzara (le prime sono state trovate solo nel 2025). Gli alberi invece scarseggiano, abbattuti in gran parte dai primi coloni per legna e pascoli.</p>
  </div>

  <div class="culture-card">
    <div class="culture-card__label">{f'<svg viewBox="0 0 64 56" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{icon_svg("saga")}</svg>'}<span class="rune-mark">ᛟ</span>Troll, elfi e le luci del cielo</div>
    <p>La tradizione islandese abbonda di creature che spiegano il paesaggio prima ancora della geologia. I <strong>troll</strong> vivono nelle scogliere e nelle montagne ma temono la luce del sole: chi viene sorpreso all'alba resta pietrificato per sempre — da qui nascono formazioni come i faraglioni di Reynisfjara, che vedrete il Giorno 4. Accanto a loro vive un popolo più discreto, gli <strong>Huldufólk</strong> ("il popolo nascosto"): elfi che abitano rocce e colline e si mostrano solo quando lo scelgono loro. La credenza è ancora abbastanza radicata che alcuni progetti stradali islandesi siano stati deviati proprio per non disturbarli.</p>
  </div>

  <div class="panel">
    <div class="panel-title"><span class="rune-mark">ᚲ</span>Il paese del fuoco sotto il ghiaccio</div>
    <div class="rune-rule"></div>
    <p class="line">L'Islanda siede a cavallo della dorsale medio-atlantica, il punto dove le placche nordamericana ed eurasiatica si allontanano di circa 2 cm l'anno: la vedrete a occhio nudo a Þingvellir il Giorno 3. Questa posizione rende l'isola una delle zone vulcaniche più attive del pianeta, con oltre 30 sistemi vulcanici attivi. È lo stesso fuoco sotterraneo, imbrigliato, a rendere l'Islanda quasi autosufficiente: circa l'85% del consumo energetico totale del paese (riscaldamento, industria e trasporti inclusi) viene da fonti rinnovabili, soprattutto geotermia e idroelettrico — la sola elettricità è quasi al 100% rinnovabile. Sono le stesse sorgenti calde in cui vi immergerete a Fontana e alla Secret Lagoon.</p>
  </div>
</section>'''

def render_checklist_group(group, group_idx):
    items_html = ''
    for item_idx, text in enumerate(group['items']):
        item_id = f'chk-{group_idx}-{item_idx}'
        items_html += (f'<label class="chk-item" for="{item_id}">'
                        f'<input type="checkbox" id="{item_id}" class="chk-box" data-chk-id="{item_id}">'
                        f'<span>{e(text)}</span></label>')
    return (f'<div class="panel">'
            f'<div class="panel-title">{e(group["title"])}</div>'
            f'<div class="rune-rule"></div>'
            f'<div class="chk-list">{items_html}</div>'
            f'</div>')

checklist_groups_html = ''.join(render_checklist_group(g, i) for i, g in enumerate(checklist_groups))

checklist_html = f'''
<section class="page-view" id="view-checklist" role="tabpanel" aria-labelledby="tab-checklist" hidden>
  <div class="day-head">
    <div class="day-date">Prima di partire</div>
    <div class="day-title">Checklist</div>
  </div>

  <div class="panel">
    <div class="panel-title">Quanto manca</div>
    <div class="rune-rule"></div>
    <div class="line" id="chk-progress" aria-live="polite">Caricamento…</div>
  </div>

  {checklist_groups_html}

  <div class="tip-card">
    <strong>Colonnine di benzina:</strong> in Islanda sono quasi tutte self-service e chiedono una carta con PIN attivo (niente carte prepagate senza PIN o solo contactless). Se avete una carta di credito o debito normale con PIN funziona senza problemi — verificate solo di avere il PIN a mente prima di partire.
  </div>

  <div class="panel aurora-push" id="aurora-push">
    <div class="panel-title">Avvisi aurora sul telefono</div>
    <div class="rune-rule"></div>
    <div class="line">Nei giorni del viaggio, anche ad app chiusa: ogni mattina verso le 7:30 com'è messa la sera dove sarete, la sera un avviso solo se la previsione migliora, e &laquo;adesso&raquo; quando le condizioni sono buone. Serve la connessione per riceverle.</div>
    <div class="aurora-push__status" id="aurora-push-status" aria-live="polite"></div>
    <div class="aurora-push__btns">
      <button type="button" class="aurora-push__btn" id="aurora-push-on">Attiva avvisi aurora</button>
      <button type="button" class="aurora-push__btn" id="aurora-push-copy" hidden>Copia codice</button>
      <button type="button" class="aurora-push__btn aurora-push__btn--ghost" id="aurora-push-off" hidden>Disattiva</button>
    </div>
    <textarea class="aurora-push__code" id="aurora-push-code" readonly hidden aria-label="Codice di iscrizione agli avvisi aurora"></textarea>
  </div>
</section>'''

seasonal_js = json.dumps(seasonal, ensure_ascii=False)
locations_js = json.dumps(locations, ensure_ascii=False)
day_routes_js = json.dumps(map_points, ensure_ascii=False)

aurora_places_js = json.dumps({**locations, **evening_places}, ensure_ascii=False)
night_stops_js = json.dumps({d['dateISO']: evening_stops[d['id']] for d in days if d['id'] in evening_stops},
                            ensure_ascii=False)
days_meta_js = json.dumps(
    [{'id': d['id'], 'dateISO': d['dateISO'], 'locKey': d['locKey']} for d in days],
    ensure_ascii=False
)

# ------------------------------------------------------------
# Percorsi stradali precalcolati (routes.json, prodotto dall'azione
# GitHub "Aggiorna percorsi mappa"). Un giorno viene incorporato solo se
# le sue tappe coincidono ancora con quelle usate per il calcolo:
# altrimenti la pagina torna al calcolo OSRM al volo.
# ------------------------------------------------------------
def _simplify(pts, tol):
    # Douglas-Peucker: toglie i punti che non cambiano il disegno (tol in gradi)
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (ax, ay), (bx, by) = pts[a], pts[b]
        dx, dy = bx - ax, by - ay
        norm = math.hypot(dx, dy)
        best, idx = 0.0, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            # giri ad anello (partenza = arrivo): distanza dal punto, non dalla retta
            d = abs(dy * (px - ax) - dx * (py - ay)) / norm if norm else math.hypot(px - ax, py - ay)
            if d > best:
                best, idx = d, i
        if best > tol and idx > 0:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(pts, keep) if k]


def route_points(points):
    return [p for p in points if not p.get('extra')]


def _coord_str(points):
    return ';'.join(f"{p['lon']},{p['lat']}" for p in route_points(points))



day_geometry = {}
for _day_id, _points in map_points.items():
    _r = _routes_raw.get(_day_id)
    if _r and _r.get('coords') == _coord_str(_points):
        _latlon = [[round(c[1], 5), round(c[0], 5)] for c in _r['geometry']]
        day_geometry[_day_id] = _simplify(_latlon, 0.00003)
day_geometry_js = json.dumps(day_geometry, separators=(',', ':'))


# ------------------------------------------------------------
# Tile OpenStreetMap per "Prepara offline": solo un corridoio stretto
# attorno ai percorsi, a zoom limitati (tile usage policy OSM).
# ------------------------------------------------------------
def _tile_xy(lat, lon, z):
    n = 2 ** z
    x = int((lon + 180) / 360 * n)
    y = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)
    return x, y


def _corridor_tiles():
    lines = []
    for _day_id, _points in map_points.items():
        lines.append(day_geometry.get(_day_id) or [[p['lat'], p['lon']] for p in route_points(_points)])
    tiles = set()
    for z in range(6, 13):
        buf = 1 if z >= 9 else 0
        for line in lines:
            for (la1, lo1), (la2, lo2) in zip(line, line[1:] or line):
                steps = max(1, int(max(abs(la2 - la1), abs(lo2 - lo1)) * 2 ** z / 90))
                for s in range(steps + 1):
                    x, y = _tile_xy(la1 + (la2 - la1) * s / steps, lo1 + (lo2 - lo1) * s / steps, z)
                    for ddx in range(-buf, buf + 1):
                        for ddy in range(-buf, buf + 1):
                            tiles.add(f'{z}/{x + ddx}/{y + ddy}')
    return sorted(tiles, key=lambda t: [int(v) for v in t.split('/')])


offline_tiles = _corridor_tiles()
offline_tiles_js = json.dumps(offline_tiles, separators=(',', ':'))
offline_tiles_label = f'{len(offline_tiles):,}'.replace(',', '.')
offline_mb = max(1, round(len(offline_tiles) * 0.016))

WEATHER_CODES_JS = """{0:'Sereno',1:'Prevalentemente sereno',2:'Parzialmente nuvoloso',3:'Nuvoloso',45:'Nebbia',48:'Nebbia con brina',51:'Pioviggine leggera',53:'Pioviggine',55:'Pioviggine intensa',56:'Pioviggine gelata',57:'Pioviggine gelata intensa',61:'Pioggia leggera',63:'Pioggia',65:'Pioggia intensa',66:'Pioggia gelata',67:'Pioggia gelata intensa',71:'Neve leggera',73:'Neve',75:'Neve intensa',77:'Granelli di neve',80:'Rovesci leggeri',81:'Rovesci',82:'Rovesci forti',85:'Rovesci di neve leggeri',86:'Rovesci di neve forti',95:'Temporale'}"""

# Stile e codice della pagina: file a parte in app/, inseriti così come sono
with open('app/stile.css', encoding='utf-8') as f:
    APP_CSS = f.read().rstrip('\n')
with open('app/app.js', encoding='utf-8') as f:
    APP_JS = f.read().rstrip('\n')

html_out = f'''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#16263b">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Islanda 2026">
<title>Islanda 2026 · Federica &amp; Michele</title>
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="icons/icon-180.png">
<link rel="icon" href="icons/icon-192.png">
<style>
@font-face {{
  font-family:'Cinzel'; font-style:normal; font-weight:500 700; font-display:swap;
  src:url(data:font/woff2;base64,{cinzel_b64}) format('woff2');
}}
@font-face {{
  font-family:'IBM Plex Sans'; font-style:normal; font-weight:400 700; font-display:swap;
  src:url(data:font/woff2;base64,{plex_b64}) format('woff2');
}}
{APP_CSS}
</style>
<link rel="stylesheet" href="vendor/leaflet/leaflet.css"/>
</head>
<body>

<div class="hero">
  {photo_slot('cover.jpg', 'Islanda 2026', 'photo-slot--cover', 'saga', eager=True)}
  <div class="hero__scrim"></div>
  <div class="hero__inner">
    <div class="hero__eyebrow">Saga di viaggio</div>
    <div class="hero__title">ISLANDA 2026</div>
    <div class="hero__sub">Federica &amp; Michele · 15–22 novembre · Reykjavík → Vík → Flúðir</div>
  </div>
</div>

<div class="navbar"><div class="navbar__inner" role="tablist" aria-label="Sezioni del viaggio">{nav_html}</div></div>

<main>

<section id="view-info" class="page-view" role="tabpanel" aria-labelledby="tab-info">
  <div class="countdown-banner">
    <div class="countdown-banner__big" id="countdown-big">…</div>
    <div class="countdown-banner__sub" id="countdown-sub"></div>
  </div>

  <div class="aurora-panel">
    <div class="panel-title">Aurora boreale — ora</div>
    <div class="kp-row"><div class="kp-big" id="kp-value">…</div><div class="kp-status" id="kp-status">Caricamento…</div></div>
    <div class="aurora-tonight" aria-live="polite">
      <div class="aurora-tonight__verdict" id="aurora-verdict">Stasera: calcolo…</div>
      <div class="aurora-tonight__detail" id="aurora-detail"></div>
      <div class="aurora-tonight__days" id="aurora-days"></div>
      <div class="aurora-tonight__src" id="aurora-src"></div>
    </div>
    <p>Indice geomagnetico Kp attuale (NOAA), aggiornato in tempo reale se sei online. La stima di stasera combina Kp previsto (NOAA), copertura nuvolosa oraria (Open-Meteo) e buio astronomico per il luogo in cui sarete la sera (alloggio o tappe serali, come Fontana il Giorno 3).</p>
    <div class="more">Più vicino alla partenza, controlla <a href="https://en.vedur.is/weather/forecasts/aurora/" target="_blank" rel="noopener">vedur.is/aurora</a> per la previsione reale sulle vostre date e sul cielo sereno.</div>
  </div>

  <div class="panel">
    <div class="panel-title">Mappa del viaggio</div>
    <div class="rune-rule"></div>
    <div id="trip-map" role="region" aria-label="Mappa del viaggio" style="position:relative;isolation:isolate;z-index:0;height:260px;border-radius:8px;overflow:hidden;border:2px solid var(--navy);box-shadow:0 4px 16px rgba(0,0,0,.12);background:#e4e6e3;"></div>
    <div class="line" style="margin-top:10px;font-size:0.8125rem;color:#5c6a78;">Mappa reale (OpenStreetMap) — zoomabile e trascinabile. Tocca un marker per il nome della tappa. Per la navigazione stradale vera e propria usa Google Maps offline.</div>
  </div>

  <div class="panel">
    <div class="panel-title">Cambio Euro &harr; Corona islandese</div>
    <div class="rune-rule"></div>
    <div class="line" style="margin-bottom:10px;">Tasso aggiornato in tempo reale se sei online (fonte: open.er-api.com); altrimenti resta sulla stima approssimativa.</div>
    <div class="fx-row">
      <div class="fx-field">
        <label for="fx-eur">Euro (EUR)</label>
        <input type="number" id="fx-eur" inputmode="decimal" value="10" min="0" step="1">
      </div>
      <div class="fx-arrow">&harr;</div>
      <div class="fx-field">
        <label for="fx-isk">Corone (ISK)</label>
        <input type="number" id="fx-isk" inputmode="decimal" value="0" min="0" step="1">
      </div>
    </div>
    <div class="fx-rate" id="fx-rate-label">1 € &asymp; … ISK &middot; caricamento tasso…</div>
  </div>

  <div class="panel">
    <div class="panel-title">Il viaggio in breve</div>
    <div class="rune-rule"></div>
    <div class="line"><strong>Volo andata:</strong> EJU3969 Milano Malpensa → Keflavík, dom 15 nov, 07:00 → 10:35</div>
    <div class="line"><strong>Volo ritorno:</strong> EJU3970 Keflavík → Milano Malpensa, dom 22 nov, 11:25 → 16:45</div>
    <div class="line"><strong>Auto:</strong> 4x4 (FairCar) · ritiro Keflavík 15 nov ore 11:00 · riconsegna Keflavík 22 nov ore 11:00</div>
    <div class="warn-box"><strong>Attenzione:</strong> il voucher auto indica riconsegna alle 11:00, ma il volo decolla alle 11:25 — margine quasi nullo. Contatta FairCar per riconsegnare prima (vedi Giorno 8).</div>
  </div>

  <div class="panel">
    <div class="panel-title">Budget &amp; celiachia</div>
    <div class="rune-rule"></div>
    <div class="line">• Supermercati Bónus (logo maialino rosa) e Krónan sono i più economici per colazioni/pranzi al sacco.</div>
    <div class="line">• Le stazioni N1 hanno zuppe e hot dog a buon prezzo lungo la Ring Road (strada 1).</div>
    <div class="line">• L'acqua del rubinetto è potabile ovunque: niente acqua in bottiglia.</div>
    <div class="line">• Cerca la parola <strong>"glútenlaust"</strong> o <strong>"glútenlaus"</strong> (senza glutine) sui menu — molti locali islandesi la indicano chiaramente.</div>
    <div class="line">• Segnalati nell'itinerario i locali con opzioni gluten-free note; conferma comunque con lo staff.</div>
  </div>

  <div class="panel">
    <div class="panel-title">Sicurezza &amp; risorse utili</div>
    <div class="rune-rule"></div>
    <div class="line">• <a href="https://www.safetravel.is" target="_blank" rel="noopener">safetravel.is</a> — registra il vostro itinerario (gratis, consigliato per la guida invernale).</div>
    <div class="line">• <a href="https://www.road.is" target="_blank" rel="noopener">road.is</a> — condizioni stradali in tempo reale.</div>
    <div class="line">• <a href="https://en.vedur.is" target="_blank" rel="noopener">vedur.is</a> — meteo, vento e aurora ufficiali islandesi.</div>
    <div class="line">• Numero unico di emergenza: <strong>112</strong> (anche via app 112 Iceland).</div>
    <div class="line">• Consolato Onorario d'Italia a Reykjavík: <a href="tel:+3546981223">+354 698 1223</a> · reykjavik.onorario@esteri.it (Bankastræti 7).</div>
    <div class="line">• Con il 4x4 in novembre è normale trovare vento forte e strade bagnate/ghiacciate: guida con margine, specialmente sulla costa sud.</div>
    <div class="line">• Le mappe di questa app mostrano il percorso ma non sono per la navigazione stradale vera e propria; offline si vedono solo dopo aver usato "Prepara offline". Per guidare, scarica prima di partire le mappe offline di Google Maps (o Organic Maps) per l'Islanda.</div>
  </div>

  <div class="panel">
    <div class="panel-title">Dove dormite</div>
    <div class="rune-rule"></div>
    <div class="stack">{stays_html}</div>
  </div>

  <div class="panel">
    <div class="panel-title">Numeri utili</div>
    <div class="rune-rule"></div>
    <div class="line">• <strong>FairCar (auto):</strong> <a href="tel:+3545717222">+354 571 7222</a> · info@faircar.is</div>
    <div class="line">• <strong>46heima / Heimaleiga (Reykjavík, Giorni 1-3):</strong> <a href="tel:+3544494900">+354 449 4900</a></div>
    <div class="line">• <strong>Hótel Búrfell (Vík, Giorni 4-5):</strong> <a href="tel:+3544874660">+354 487 4660</a></div>
    <div class="line">• <strong>The Hill Guesthouse (The Hill Hotel, Flúðir, Giorni 6-7):</strong> <a href="tel:+3544864430">+354 486 4430</a></div>
    <div class="line" style="margin-top:6px;font-size:0.8125rem;color:#5c6a78;">Numeri trovati via ricerca online, non verificati con una chiamata diretta: ricontrollateli nelle email di conferma prima di partire.</div>
  </div>

  <div class="panel">
    <div class="panel-title">Prepara offline</div>
    <div class="rune-rule"></div>
    <div class="line">Salva sul telefono foto, percorsi e mappe lungo tutto il tragitto del viaggio (circa {offline_tiles_label} riquadri di mappa, ~{offline_mb} MB), così l'app funziona anche senza rete. Fallo con il Wi-Fi prima di partire, su entrambi i telefoni.</div>
    <div class="offline-bar" id="offline-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" hidden><div class="offline-bar__fill" id="offline-fill"></div></div>
    <div class="offline-status" id="offline-status" aria-live="polite"></div>
    <button type="button" class="offline-btn" id="offline-btn">Prepara offline</button>
    <div class="offline-status" id="app-version"></div>
    <div class="offline-status app-received" id="app-received"></div>
  </div>
</section>

{days_sections_html}

{storia_html}

{checklist_html}

</main>

<button id="fab-fx-btn" class="fab-fx-btn" aria-label="Convertitore euro-corone" title="Convertitore euro-corone" aria-expanded="false" aria-controls="fab-fx-popup" hidden>€↔kr</button>
<div id="fab-fx-popup" class="fab-fx-popup" hidden>
  <div class="fab-fx-popup__head">
    <span>Cambio rapido</span>
    <button id="fab-fx-close" class="fab-fx-close" aria-label="Chiudi">&times;</button>
  </div>
  <div class="fx-row">
    <div class="fx-field">
      <label for="fab-fx-eur">Euro (EUR)</label>
      <input type="number" id="fab-fx-eur" inputmode="decimal" value="10" min="0" step="1">
    </div>
    <div class="fx-arrow">&harr;</div>
    <div class="fx-field">
      <label for="fab-fx-isk">Corone (ISK)</label>
      <input type="number" id="fab-fx-isk" inputmode="decimal" value="0" min="0" step="1">
    </div>
  </div>
  <div class="fx-rate" id="fab-fx-rate-label">1 € &asymp; … ISK</div>
  <div class="fab-fx-quick">
    <a href="https://road.is" target="_blank" rel="noopener" class="fab-fx-quick__btn">Stato strade (road.is)</a>
  </div>
</div>

<!-- Leaflet in fondo: non blocca la prima schermata all'apertura -->
<script src="vendor/leaflet/leaflet.js"></script>
<script>
const SEASONAL = {seasonal_js};
const LOCATIONS = {locations_js};
const DAY_ROUTES = {day_routes_js};
const DAY_GEOMETRY = {day_geometry_js};
const OFFLINE_TILES = {offline_tiles_js};
const APP_VERSION = '__APP_VERSION__';
const DAYS_META = {days_meta_js};
const VAPID_PUBLIC_KEY = '{VAPID_PUBLIC_KEY}';
const AURORA_PLACES = {aurora_places_js};
const NIGHT_STOPS = {night_stops_js};
const CLOUD_METHOD = '{CLOUD_METHOD}';
const CLOUD_W_MID = {CLOUD_W_MID}, CLOUD_W_HIGH = {CLOUD_W_HIGH};
const CLOUD_MODELS = {json.dumps(CLOUD_MODELS)};
const WEATHER_CODES = {WEATHER_CODES_JS};
{APP_JS}
</script>
</body>
</html>
'''

# ------------------------------------------------------------
# Versione automatica: hash di pagina, foto, percorsi e file statici.
# Qualunque modifica pubblicata cambia CACHE_NAME in sw.js, e il
# telefono scarica la nuova versione da solo.
# ------------------------------------------------------------
import hashlib, os

photo_files = sorted({p for p in re.findall(r'data-photo="([^"]+)"', html_out)
                      if os.path.isfile(os.path.join('images', p))})

# ------------------------------------------------------------
# Conversione automatica foto → WebP (images/web/), lato lungo max
# 1200px, qualità 75 (per stare sui ~3 MB totali), orientamento EXIF. Le foto usate
# solo come miniature (92px sullo schermo) bastano a 400px sul lato corto.
# Riconverte solo se il .jpg sorgente o il formato è cambiato (hash sha256 salvato in un manifest),
# così due run consecutivi di render.py producono file identici.
# ------------------------------------------------------------
from PIL import Image, ImageOps

WEBP_DIR = os.path.join('images', 'web')
os.makedirs(WEBP_DIR, exist_ok=True)
_manifest_path = os.path.join(WEBP_DIR, 'manifest.json')
try:
    with open(_manifest_path, encoding='utf-8') as f:
        _webp_manifest = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    _webp_manifest = {}

# foto che compaiono solo come miniature (non come copertina o foto principale)
thumb_only = (set(re.findall(r'photo-slot--thumb" data-photo="([^"]+)"', html_out))
              - set(re.findall(r'photo-slot--(?:hero|cover)" data-photo="([^"]+)"', html_out)))

_new_manifest = {}
webp_files = []
for _p in photo_files:
    _src = os.path.join('images', _p)
    with open(_src, 'rb') as f:
        _src_bytes = f.read()
    _src_hash = hashlib.sha256(_src_bytes).hexdigest()
    _webp_name = re.sub(r'\.jpg$', '.webp', _p)
    _webp_path = os.path.join(WEBP_DIR, _webp_name)
    _thumb = _p in thumb_only
    _key = _src_hash + (':thumb400' if _thumb else '')
    if _webp_manifest.get(_p) != _key or not os.path.isfile(_webp_path):
        _img = Image.open(_src)
        _img = ImageOps.exif_transpose(_img)
        _img = _img.convert('RGB')
        _w, _h_ = _img.size
        _long = max(_w, _h_)
        if _thumb and min(_w, _h_) > 400:
            _scale = 400 / min(_w, _h_)
            _img = _img.resize((max(1, round(_w * _scale)), max(1, round(_h_ * _scale))), Image.LANCZOS)
        elif _long > 1200:
            _scale = 1200 / _long
            _img = _img.resize((max(1, round(_w * _scale)), max(1, round(_h_ * _scale))), Image.LANCZOS)
        _img.save(_webp_path, 'WEBP', quality=75, method=6)
    _new_manifest[_p] = _key
    webp_files.append('web/' + _webp_name)
_webp_manifest = _new_manifest
with open(_manifest_path, 'w', encoding='utf-8') as f:
    json.dump(_webp_manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
    f.write('\n')
webp_files = sorted(webp_files)
# WebP di foto non più usate o cancellate: via, così non restano online né in cache
for _f in sorted(os.listdir(WEBP_DIR)):
    if _f.endswith('.webp') and 'web/' + _f not in webp_files:
        os.remove(os.path.join(WEBP_DIR, _f))

STATIC_FILES = ['manifest.json', 'icons/icon-180.png', 'icons/icon-192.png', 'icons/icon-512.png',
                'icons/icon-192-maskable.png', 'icons/icon-512-maskable.png',
                'vendor/leaflet/leaflet.js', 'vendor/leaflet/leaflet.css',
                'vendor/leaflet/images/layers.png', 'vendor/leaflet/images/layers-2x.png']
SW_TEMPLATE = open('sw-template.js', encoding='utf-8').read()

_h = hashlib.sha256()
for _chunk in [html_out.encode('utf-8'), SW_TEMPLATE.encode('utf-8'), json.dumps(_routes_raw, sort_keys=True).encode()]:
    _h.update(_chunk)
for _path in STATIC_FILES + ['images/' + p for p in webp_files]:
    _h.update(_path.encode())
    with open(_path, 'rb') as f:
        _h.update(f.read())
app_version = _h.hexdigest()[:12]

html_out = html_out.replace('__APP_VERSION__', app_version)
precache = ['./', 'index.html'] + STATIC_FILES + ['images/' + p for p in webp_files]
sw_out = (SW_TEMPLATE
          .replace('__APP_VERSION__', app_version)
          .replace('__PRECACHE__', json.dumps(precache, ensure_ascii=False, indent=2)))

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_out)
with open('sw.js', 'w', encoding='utf-8') as f:
    f.write(sw_out)

print('index.html written,', len(html_out), 'bytes · versione', app_version,
      '· foto in precache', len(photo_files), '· percorsi incorporati', len(day_geometry),
      '· tile offline', len(offline_tiles))
