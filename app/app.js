
const state = { weather:{}, sun:{}, kp:null, kpStatus:'loading' };

const dayMaps = {};

function ensureDayMap(dayId) {
  const el = document.getElementById('day-map-' + dayId);
  const points = DAY_ROUTES[dayId];
  if (!el || !points || !points.length || typeof L === 'undefined') return;
  if (dayMaps[dayId]) { requestAnimationFrame(() => dayMaps[dayId].invalidateSize()); return; }

  const map = L.map(el, { scrollWheelZoom: false, dragging: false, tap: false, zoomControl: false, zoomSnap: 0.25 });
  L.control.zoom({ position: 'bottomleft', zoomInTitle: 'Ingrandisci mappa', zoomOutTitle: 'Riduci mappa' }).addTo(map);
  dayMaps[dayId] = map;
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
    subdomains: 'abc',
    maxZoom: 19,
    crossOrigin: true
  }).addTo(map);

  const latlngs = points.map(p => [p.lat, p.lon]);
  const routePts = points.filter(p => !p.extra);   // tappe facoltative: solo segnaposto

  const seen = {};
  let seq = 0;
  points.forEach(p => {
    let n, size, bg;
    if (p.extra) {
      n = '+'; size = 18; bg = '#faf7f0';
    } else {
      const key = p.lat.toFixed(3) + ',' + p.lon.toFixed(3);
      if (!(key in seen)) { seq++; seen[key] = seq; }
      n = seen[key];
      const ri = routePts.indexOf(p);
      const isEnd = ri === 0 || ri === routePts.length - 1;
      size = isEnd ? 26 : 20;
      bg = isEnd ? '#b5673a' : '#f2ede2';
    }
    const icon = L.divIcon({
      className: '',
      html: '<div style="width:' + size + 'px;height:' + size + 'px;border-radius:50%;background:' + bg + ';' +
            'border:2px solid #16263b;display:flex;align-items:center;justify-content:center;' +
            'font:700 11px \'IBM Plex Sans\',sans-serif;color:#16263b;">' + n + '</div>',
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2]
    });
    L.marker([p.lat, p.lon], { icon }).addTo(map).bindPopup(p.name);
  });

  // margini: a sinistra in basso ci sono i pulsanti +/−, a destra in basso i crediti della mappa;
  // l'inquadratura comprende anche la strada, non solo le tappe
  map.fitBounds(latlngs.concat(DAY_GEOMETRY[dayId] || []), { paddingTopLeft: [52, 34], paddingBottomRight: [34, 34] });

  const ROUTE_STYLE = { color: '#d9985f', weight: 4, opacity: 0.9, lineCap: 'round' };
  if (DAY_GEOMETRY[dayId]) {
    // percorso stradale precalcolato (routes.json): disponibile anche offline
    L.polyline(DAY_GEOMETRY[dayId], ROUTE_STYLE).addTo(map);
  } else {
    drawRouteLive(map, routePts, routePts.map(p => [p.lat, p.lon]), ROUTE_STYLE);
  }

  el.addEventListener('touchstart', () => { map.scrollWheelZoom.enable(); map.dragging.enable(); }, { once: true, passive: true });
}

function drawRouteLive(map, points, latlngs, routeStyle) {
  const fallback = L.polyline(latlngs, { color: '#4f8fa8', weight: 3, dashArray: '1,9', lineCap: 'round', opacity: 0.9 }).addTo(map);

  const coordStr = points.map(p => p.lon + ',' + p.lat).join(';');
  fetch('https://router.project-osrm.org/route/v1/driving/' + coordStr + '?overview=full&geometries=geojson')
    .then(r => r.ok ? r.json() : Promise.reject())
    .then(data => {
      const route = data.routes && data.routes[0];
      if (!route) return;
      const coords = route.geometry.coordinates.map(c => [c[1], c[0]]);
      map.removeLayer(fallback);
      L.polyline(coords, routeStyle).addTo(map);
    })
    .catch(() => { /* resta la linea retta di riserva */ });
}

function setActive(id, moveFocus) {
  document.querySelectorAll('.nav-btn').forEach(b => {
    const isActive = b.dataset.nav === id;
    b.classList.toggle('active', isActive);
    b.setAttribute('aria-selected', isActive ? 'true' : 'false');
    b.tabIndex = isActive ? 0 : -1;
    if (isActive && moveFocus) b.focus();
    if (isActive && b.scrollIntoView) b.scrollIntoView({ inline: 'center', block: 'nearest' });
  });
  document.querySelectorAll('.page-view').forEach(el => { el.hidden = el.id !== 'view-' + id; });
  if (DAYS_META.some(d => d.id === id)) ensureDayMap(id);
  // la mappa del viaggio creata con la tab Info nascosta va ridimensionata e reinquadrata
  if (id === 'info' && tripMap) requestAnimationFrame(() => { tripMap.invalidateSize(); tripMap.fitBounds(tripBounds, TRIP_FIT); });
  const fabBtn = document.getElementById('fab-fx-btn');
  const fabPopup = document.getElementById('fab-fx-popup');
  if (fabBtn) fabBtn.hidden = id === 'info';
  if (fabPopup && id === 'info') { fabPopup.hidden = true; if (fabBtn) fabBtn.setAttribute('aria-expanded', 'false'); }
  window.scrollTo({ top: 0, behavior: 'instant' in window ? 'instant' : 'auto' });
}
const navBtnList = () => Array.from(document.querySelectorAll('.nav-btn'));
document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => setActive(btn.dataset.nav));
  btn.addEventListener('keydown', (e) => {
    const list = navBtnList();
    const i = list.indexOf(btn);
    let next = -1;
    if (e.key === 'ArrowRight') next = (i + 1) % list.length;
    else if (e.key === 'ArrowLeft') next = (i - 1 + list.length) % list.length;
    else if (e.key === 'Home') next = 0;
    else if (e.key === 'End') next = list.length - 1;
    if (next >= 0) { e.preventDefault(); setActive(list[next].dataset.nav, true); }
  });
});

function weatherFor(day) {
  const live = state.weather[day.locKey];
  if (live && live.time) {
    const idx = live.time.indexOf(day.dateISO);
    if (idx >= 0) {
      const code = live.weathercode[idx];
      return {
        temp: Math.round(live.temperature_2m_max[idx]) + '° / ' + Math.round(live.temperature_2m_min[idx]) + '°C',
        desc: WEATHER_CODES[code] || 'Variabile',
        source: 'Previsione live (aggiornata automaticamente)'
      };
    }
  }
  const s = SEASONAL[day.locKey];
  return {
    temp: '~' + s.tmax + '° / ~' + s.tmin + '°C',
    desc: s.desc + ' · vento ' + s.wind,
    source: 'Media stagionale tipica di novembre — offline o previsione non ancora disponibile (appare da ~16 giorni prima)'
  };
}

function renderWeatherAndSun() {
  DAYS_META.forEach(day => {
    const w = weatherFor(day);
    const tempEl = document.querySelector('[data-weather-temp="' + day.id + '"]');
    const descEl = document.querySelector('[data-weather-desc="' + day.id + '"]');
    const srcEl = document.querySelector('[data-weather-source="' + day.id + '"]');
    if (tempEl) tempEl.textContent = w.temp;
    if (descEl) descEl.textContent = w.desc;
    if (srcEl) srcEl.textContent = w.source;

    const sun = state.sun[day.id] || { sunrise: '—', sunset: '—', daylight: '—' };
    const sr = sun.sunrise, ss = sun.sunset, dl = sun.daylight;
    const srEl = document.querySelector('[data-sunrise="' + day.id + '"]');
    const ssEl = document.querySelector('[data-sunset="' + day.id + '"]');
    const dlEl = document.querySelector('[data-daylight="' + day.id + '"]');
    if (srEl) srEl.textContent = sr;
    if (ssEl) ssEl.textContent = ss;
    if (dlEl) dlEl.textContent = dl + ' di luce';

    const auroraEl = document.querySelector('[data-aurora="' + day.id + '"]');
    if (auroraEl && day.id !== 'd8') {   // l'ultima sera siete già in volo
      auroraEl.innerHTML = '<strong>Aurora:</strong> Notte dal tramonto (' + ss + ') all\'alba (' + sr + ') del giorno dopo; il buio pieno arriva circa tre ore dopo il tramonto: finestra ampia. Novembre è piena stagione aurora: serve cielo sereno e attività geomagnetica. Controlla vedur.is/aurora nei giorni prima.<span data-aurora-live="' + day.id + '"></span>';
    }
  });
  if (auroraReady) renderAurora();   // il box aurora dei giorni è appena stato riscritto
}
computeAllSun();
renderWeatherAndSun();

async function fetchAllWeather() {
  for (const key of Object.keys(AURORA_PLACES)) {
    const loc = AURORA_PLACES[key];
    try {
      // meteo giornaliero solo per gli alloggi; nuvole orarie (anche per strati) per tutte le tappe
      const daily = LOCATIONS[key] ? '&daily=weathercode,temperature_2m_max,temperature_2m_min' : '';
      const url = 'https://api.open-meteo.com/v1/forecast?latitude=' + loc.lat + '&longitude=' + loc.lon + daily + '&hourly=cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high&timezone=UTC&past_days=1&forecast_days=16';
      const res = await fetch(url);
      const json = await res.json();
      if (json && json.daily) { state.weather[key] = json.daily; renderWeatherAndSun(); }
      let hourly = json && json.hourly;
      if (CLOUD_METHOD.startsWith('media')) {
        // più modelli insieme: le variabili arrivano con il nome del modello (cloud_cover_icon_seamless…)
        const multi = await (await fetch('https://api.open-meteo.com/v1/forecast?latitude=' + loc.lat + '&longitude=' + loc.lon
          + '&hourly=cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high&models=' + CLOUD_MODELS.join(',') + '&timezone=UTC&past_days=1&forecast_days=3')).json();
        if (multi && multi.hourly) hourly = multi.hourly;
      }
      if (hourly && navigator.onLine) auroraSave({ clouds: { [key]: hourly } });
    } catch (e) { /* resta sulla stima stagionale */ }
  }
}

// Alba e tramonto calcolati in locale (algoritmo NOAA, come sunrise-sunset.org):
// nessuna rete, funziona offline. Restituisce i minuti dalla mezzanotte UTC,
// che in Islanda coincide con l'ora locale (niente ora legale).

function sunEventsUTC(dateISO, lat, lon) {
  const rad = Math.PI / 180;
  const [Y, M, D] = dateISO.split('-').map(Number);
  const jdNoon = Date.UTC(Y, M - 1, D, 12) / 86400000 + 2440587.5;
  const solar = solarParams;
  function event(rising) {
    let minutes = 720;
    for (let i = 0; i < 3; i++) {
      const { decl, eqTime } = solar(jdNoon - 0.5 + minutes / 1440);
      const cosH = (Math.cos(90.833 * rad) - Math.sin(lat * rad) * Math.sin(decl * rad))
                 / (Math.cos(lat * rad) * Math.cos(decl * rad));
      if (cosH > 1 || cosH < -1) return null;
      const H = Math.acos(cosH) / rad * (rising ? 1 : -1);
      minutes = 720 - 4 * (lon + H) - eqTime;
    }
    return minutes;
  }
  return { sunrise: event(true), sunset: event(false) };
}

function computeAllSun() {
  const hhmm = m => String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(Math.floor(m % 60)).padStart(2, '0');
  DAYS_META.forEach(day => {
    const loc = LOCATIONS[day.locKey];
    const ev = sunEventsUTC(day.dateISO, loc.lat, loc.lon);
    if (ev.sunrise === null || ev.sunset === null) return;
    const len = Math.round(ev.sunset - ev.sunrise);
    state.sun[day.id] = {
      sunrise: hhmm(ev.sunrise), sunset: hhmm(ev.sunset),
      daylight: Math.floor(len / 60) + 'h ' + String(len % 60).padStart(2, '0') + 'm'
    };
  });
}

async function fetchKp() {
  try {
    const res = await fetch('https://services.swpc.noaa.gov/json/planetary_k_index_1m.json');
    const json = await res.json();
    const last = json[json.length - 1];
    if (last.kp_index == null || !isFinite(last.kp_index)) throw new Error('Kp mancante');
    state.kp = Math.round(last.kp_index * 10) / 10;
    state.kpStatus = 'ok';
    // ora del dato NOAA (UTC), non dell'apertura: offline la copia salvata può essere vecchia
    const at = last.time_tag ? new Date(String(last.time_tag).replace(' ', 'T') + (/Z|[+-]\d\d:?\d\d$/.test(last.time_tag) ? '' : 'Z')) : null;
    state.kpAt = at && isFinite(at) ? at : new Date();
  } catch (e) { state.kpStatus = 'error'; }
  document.getElementById('kp-value').textContent = state.kpStatus === 'ok' ? ('Kp adesso ' + String(state.kp).replace('.', ',')) : '—';
  let kpText;
  if (state.kpStatus === 'ok') {
    const t = state.kpAt;
    const hh = String(t.getUTCHours()).padStart(2, '0') + ':' + String(t.getUTCMinutes()).padStart(2, '0');
    const dd = String(t.getUTCDate()).padStart(2, '0') + '/' + String(t.getUTCMonth() + 1).padStart(2, '0');
    kpText = (state.kp >= 4 ? 'Attività alta' : 'Attività bassa/moderata')
           + (navigator.onLine ? ' · aggiornato alle ' + hh + ' (ora islandese)' : ' · dato del ' + dd + ' alle ' + hh + ', sei offline');
  } else {
    kpText = navigator.onLine ? 'Dato non disponibile al momento (NOAA non risponde)' : 'Dato non disponibile offline';
  }
  document.getElementById('kp-status').textContent = kpText;
  renderAuroraNow();
}

// ---------- Aurora adesso: OVATION e vento solare (NOAA) ----------
// Scaricati all'apertura dell'app solo online e quando è buio (o sta per esserlo) dove siete;
// OVATION (circa 900 kB, 150 kB compresso) al massimo ogni 15 minuti, anche tra un'apertura e
// l'altra (ultimo valore salvato nel telefono). Il vento solare qui è
// l'ultimo minuto (l'avviso "arrivo" in tools/aurora_alert.py guarda invece la media di 15-20 minuti).
const OVATION_KEY = 'islanda2026-ovation';
async function fetchAuroraNow() {
  try {
    const { loc, night } = auroraNowPlace();
    // dopo l'ultima notte in Islanda (21-22 novembre) non serve più
    if (!navigator.onLine || !loc || night > '2026-11-21' || sunAltitude(new Date(), loc.lat, loc.lon) >= 0) {
      state.auroraNow = null; renderAuroraNow(); return;
    }
    const opt = { cache: 'no-store' };
    let prev = state.auroraNow;
    if (!prev) { try { prev = JSON.parse(localStorage.getItem(OVATION_KEY) || 'null'); } catch (e) {} }
    const fresh = prev && prev.ov != null && prev.place === loc.name && Date.now() - prev.at < 15 * 60000
      && Date.now() - prev.ovAt <= 60 * 60000;
    const [ov, mag, sp] = await Promise.all([
      fresh ? null : fetch('https://services.swpc.noaa.gov/json/ovation_aurora_latest.json', opt).then(r => r.json()).catch(() => null),
      fetch('https://services.swpc.noaa.gov/products/summary/solar-wind-mag-field.json', opt).then(r => r.json()).catch(() => null),
      fetch('https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json', opt).then(r => r.json()).catch(() => null)
    ]);
    const now = fresh ? Object.assign({}, prev) : { place: loc.name, at: Date.now(), ov: null, ovAt: null };
    now.bz = null; now.v = null;
    // con la rete che non risponde il service worker restituisce l'ultima copia: i dati vecchi si scartano
    const ovAt = ov && NOAA_AGE(ov['Observation Time'], 60);
    if (ovAt) {
      const p = ovationNorth(ov.coordinates, loc);
      if (p !== null) {
        now.ov = p; now.ovAt = ovAt;
        try { localStorage.setItem(OVATION_KEY, JSON.stringify({ place: now.place, at: now.at, ov: p, ovAt })); } catch (e) {}
      }
    }
    const m = Array.isArray(mag) && mag[0], w = Array.isArray(sp) && sp[0];
    if (m && NOAA_AGE(m.time_tag, 30)) now.bz = num(m.bz_gsm);
    if (w && NOAA_AGE(w.time_tag, 30)) now.v = num(w.proton_speed);
    state.auroraNow = now;
  } catch (e) { /* resta il dato precedente */ }
  renderAuroraNow();
}


// "Si vede adesso?": attività (la migliore tra Kp attuale e OVATION) × cielo sereno di quest'ora
function renderAuroraNow() {
  const el = document.getElementById('aurora-now');
  const n = state.auroraNow;
  const kpLine = document.querySelector('.kp-line');
  if (!el) return;
  if (!n) { el.hidden = true; if (kpLine) kpLine.hidden = false; return; }
  if (kpLine) kpLine.hidden = true;
  const { place, loc } = auroraNowPlace();
  const t = new Date();
  const fmt = x => String(x).replace('.', ',').replace('-', '−');
  const facts = [];
  const kp = state.kpStatus === 'ok' && t - state.kpAt <= 30 * 60000 ? state.kp : null;
  if (n.ov !== null) facts.push('aurora verso nord <b>' + n.ov + '%</b> (OVATION)');
  if (kp !== null) facts.push('Kp <b>' + fmt(kp) + '</b>');
  const clouds = (auroraLoad().clouds || {})[place];
  let cloud = null;
  if (clouds && clouds.time) {
    const idx = clouds.time.indexOf(t.toISOString().slice(0, 13) + ':00');
    if (idx >= 0) cloud = effCloud(clouds, idx);
  }
  facts.push(cloud !== null ? 'nuvole <b>' + cloud + '%</b>' : 'nuvole non disponibili');
  const wind = windState(n.bz, n.v);
  if (wind) facts.push('vento solare ' + wind.label + ' (Bz ' + (n.bz > 0 ? '+' : '') + fmt(Math.round(n.bz)) + '\u00a0nT'
    + (n.v !== null ? ', ' + Math.round(n.v) + '\u00a0km/s' : '') + ')');
  const { level, text } = auroraNowVerdict({ ov: n.ov, kp, cloud, sunAlt: sunAltitude(t, loc.lat, loc.lon), wind });
  const nm = shortPlace(loc.name);
  const where = nm.startsWith('strada') ? 'lungo la ' + nm : 'a ' + nm;
  if (n.ovAt) { const d = new Date(n.ovAt); facts.push('OVATION delle ' + String(d.getUTCHours()).padStart(2, '0') + ':' + String(d.getUTCMinutes()).padStart(2, '0')); }
  el.innerHTML = '<span class="aurora-now__verdict' + (level ? ' aurora-now__verdict--' + level : '') + '">🌌 Adesso ' + where + ': ' + text + '</span>'
    + '<span class="aurora-now__facts">' + facts.join(' · ') + '</span>';
  el.hidden = false;
}

// ---------- Aurora: stima per stasera (Kp previsto + nuvole + buio) ----------
const AURORA_KEY = 'islanda2026-aurora';
// ricerca Kp di ottobre: la previsione del mattino sbaglia in media di circa 1 (uguale in tools/aurora_alert.py)
const KP_NOTE = 'La previsione del Kp sbaglia spesso di circa 1 punto: ricontrollate la sera.';
function auroraLoad() {
  let d = null;
  try { d = JSON.parse(localStorage.getItem(AURORA_KEY) || 'null'); } catch (e) {}
  if (!d || typeof d !== 'object' || Array.isArray(d)) d = {};
  // tiene solo dati con la forma attesa: un salvataggio rovinato non deve bloccare l'app
  if (!Array.isArray(d.kp)) delete d.kp;
  const clouds = {};
  if (d.clouds && typeof d.clouds === 'object') {
    Object.keys(d.clouds).forEach(k => {
      const c = d.clouds[k];
      if (c && Array.isArray(c.time)) clouds[k] = c;
    });
  }
  d.clouds = clouds;
  return d;
}
// Salva solo dati ricevuti online, con l'ora: offline si mostra l'ultimo dato e quando è stato preso.
function auroraSave(part) {
  const d = auroraLoad();
  if (part.kp) { d.kp = part.kp; d.kpAt = new Date().toISOString(); }
  if (part.clouds) { d.clouds = Object.assign(d.clouds || {}, part.clouds); d.cloudsAt = new Date().toISOString(); }
  try { localStorage.setItem(AURORA_KEY, JSON.stringify(d)); } catch (e) {}
  renderAurora();
  renderAuroraNow();   // le nuvole possono arrivare dopo OVATION: il box "Adesso" va ricalcolato
}

function parseKpForecast(json) {
  // formato NOAA a righe ([intestazione], [time_tag, kp, observed, scala]) oppure a oggetti
  const rows = Array.isArray(json[0])
    ? json.slice(1).map(r => ({ t: r[0], kp: parseFloat(r[1]) }))
    : json.map(o => ({ t: o.time_tag, kp: parseFloat(o.kp !== undefined ? o.kp : o.Kp) }));
  return rows.filter(r => r.t && isFinite(r.kp))
    .map(r => ({ t: Date.parse(String(r.t).replace(' ', 'T') + (/Z|[+-]\d\d:?\d\d$/.test(r.t) ? '' : 'Z')), kp: r.kp }))
    .filter(r => isFinite(r.t));
}

async function fetchKpForecast() {
  try {
    const res = await fetch('https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json');
    const rows = parseKpForecast(await res.json());
    if (rows.length && navigator.onLine) auroraSave({ kp: rows });
  } catch (e) { /* resta l'ultimo dato salvato */ }
  renderAurora();
}


// fasce orarie migliori: ore consecutive vicine al massimo
function auroraWindows(hours, best) {
  const windows = [];
  hours.filter(h => h.score >= Math.max(0.2, best * 0.8)).forEach(h => {
    const last = windows[windows.length - 1];
    if (last && h.t - last.end === 0) last.end = new Date(h.t.getTime() + 3600000);
    else windows.push({ from: h.t, end: new Date(h.t.getTime() + 3600000) });
  });
  return windows;
}

// Stima per la notte che inizia alle 12 UTC di startMs: ore di buio astronomico,
// Kp previsto per ogni ora e nuvolosità oraria del luogo in cui siete a quell'ora.
function nightEstimate(startMs, stops, data) {
  if (typeof stops === 'string') stops = [{ place: stops }];
  const kpRows = data.kp || [];
  const hours = [];
  for (let i = 0; i < 24; i++) {
    const t = new Date(startMs + i * 3600000);
    const place = stopAt(stops, t).place;
    const loc = AURORA_PLACES[place];
    if (sunAltitude(new Date(t.getTime() + 1800000), loc.lat, loc.lon) >= -18) continue;
    const row = kpRows.find(r => t.getTime() >= r.t && t.getTime() < r.t + 3 * 3600000);
    const clouds = (data.clouds || {})[place];
    let cloud = null;
    if (clouds && clouds.time) {
      const idx = clouds.time.indexOf(t.toISOString().slice(0, 13) + ':00');
      if (idx >= 0) cloud = effCloud(clouds, idx);
    }
    hours.push({ t, place, kp: row ? row.kp : null, cloud });
  }
  const withKp = hours.filter(h => h.kp !== null);
  const est = { loc: AURORA_PLACES[stops[stops.length - 1].place], hours, withKp, level: null, stops: [] };
  if (!withKp.length) return est;
  const hasClouds = withKp.some(h => h.cloud !== null);
  withKp.forEach(h => { h.score = kpFactor(h.kp) * (h.cloud === null ? (hasClouds ? 0.5 : 1) : (100 - h.cloud) / 100); });
  const best = Math.max(...withKp.map(h => h.score));
  est.level = auroraLevel(best);
  est.kpMax = Math.max(...withKp.map(h => h.kp));
  est.clouds = withKp.filter(h => h.cloud !== null).map(h => h.cloud);
  est.windows = auroraWindows(withKp, best);
  // con più tappe: una stima per ognuna, nelle sue ore di buio
  if (stops.length > 1) {
    est.stops = stops.map(s => {
      const hs = withKp.filter(h => h.place === s.place);
      if (!hs.length) return null;
      const b = Math.max(...hs.map(h => h.score));
      return { place: s.place, name: AURORA_PLACES[s.place].name, level: auroraLevel(b), windows: auroraWindows(hs, b),
               from: hs[0].t, end: new Date(hs[hs.length - 1].t.getTime() + 3600000) };
    }).filter(Boolean);
  }
  return est;
}

// nomi delle tappe di una notte, anche senza dati (est.stops si riempie solo con il Kp)
function stopsLabel(stops) {
  return stops.length > 1 ? stops.map(s => shortPlace(AURORA_PLACES[s.place].name)).join(' → ') : AURORA_PLACES[stops[0].place].name;
}
function nightPlaceNames(est) {
  if (est.stops.length > 1) return est.stops.map(s => shortPlace(s.name)).join(' → ');
  return est.stops.length === 1 ? est.stops[0].name : est.loc.name;
}

const AU_HH = d => String(d.getUTCHours()).padStart(2, '0') + ':00';
const AU_DAYNAMES = ['dom', 'lun', 'mar', 'mer', 'gio', 'ven', 'sab'];
function auroraWindowsText(est) {
  return est.windows.slice(0, 2).map(w => AU_HH(w.from) + '–' + AU_HH(w.end)).join(' e ');
}

// Nuvole in breve, invece del minimo–massimo su tutta la notte (es. "0–98%", poco utile):
// se cambiano poco un valore tipico; se cambiano molto, le nuvole nelle ore migliori
// e com'è la sera rispetto a dopo mezzanotte.
const AU_R5 = v => Math.round(v / 5) * 5;
const auAvg = hs => hs.reduce((a, h) => a + h.cloud, 0) / hs.length;
// stima senza dati sulle nuvole: come le notifiche, "previsione incompleta" e niente verdetto
function auroraNoClouds(est) { return !est.withKp.some(h => h.cloud !== null); }

function auroraClouds(est) {
  const hs = est.withKp.filter(h => h.cloud !== null);
  if (!hs.length) return { variable: false, text: 'nuvole non disponibili' };
  const vals = hs.map(h => h.cloud), lo = Math.min(...vals), hi = Math.max(...vals);
  if (hi - lo < 30) return { variable: false, text: 'nuvole ~' + AU_R5(auAvg(hs)) + '%' };
  const eve = hs.filter(h => h.t.getUTCHours() >= 12), late = hs.filter(h => h.t.getUTCHours() < 12);
  const text = eve.length && late.length && Math.abs(auAvg(eve) - auAvg(late)) >= 20
    ? 'nuvole ~' + AU_R5(auAvg(eve)) + '% in serata, ~' + AU_R5(auAvg(late)) + '% dopo mezzanotte'
    : 'nuvole variabili, tra ' + lo + ' e ' + hi + '%';
  return { variable: true, text };
}
function auroraWindowsCloudText(est) {
  return est.windows.slice(0, 2).map(w => {
    const hs = est.withKp.filter(h => h.cloud !== null && h.t >= w.from && h.t < w.end);
    return AU_HH(w.from) + '–' + AU_HH(w.end) + (hs.length ? ' (nuvole ~' + AU_R5(auAvg(hs)) + '%)' : '');
  }).join(' e ');
}

function renderAurora() {
  const verdictEl = document.getElementById('aurora-verdict');
  const data = auroraLoad();
  const now = new Date();
  // la notte "di stasera" inizia alle 12 UTC di oggi (prima delle 7, quando arriva l'avviso
  // del mattino, è ancora la notte in corso)
  const start = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), 12) - (now.getUTCHours() < 7 ? 86400000 : 0);
  const isoOf = ms => new Date(ms).toISOString().slice(0, 10);
  // prima delle 7 la notte in corso è "stanotte", non "stasera"
  const tonight = now.getUTCHours() < 7 ? 'Stanotte' : 'Stasera';

  // dopo l'ultima notte in Islanda (21-22 novembre) la stima non serve più
  const tonightBox = document.getElementById('aurora-tonight');
  if (tonightBox) tonightBox.hidden = verdictEl.hidden = isoOf(start) > '2026-11-21';
  if (verdictEl) {
    const detailEl = document.getElementById('aurora-detail');
    const daysEl = document.getElementById('aurora-days');
    const srcEl = document.getElementById('aurora-src');
    const est = nightEstimate(start, nightStops(isoOf(start)), data);
    verdictEl.className = 'aurora-tonight__verdict';
    if (!est.hours.length) {
      verdictEl.textContent = tonight + ' a ' + stopsLabel(nightStops(isoOf(start))) + ': niente buio astronomico';
      detailEl.textContent = '';
    } else if (!est.level) {
      verdictEl.textContent = tonight + ' a ' + stopsLabel(nightStops(isoOf(start))) + ': previsione non disponibile';
      detailEl.textContent = navigator.onLine ? 'Dati NOAA non ancora ricevuti.' : 'Serve una connessione per scaricare la previsione.';
    } else if (auroraNoClouds(est)) {
      verdictEl.textContent = tonight + ' a ' + nightPlaceNames(est) + ': previsione incompleta';
      detailEl.textContent = 'Kp previsto fino a ' + est.kpMax.toFixed(1).replace('.0', '').replace('.', ',')
        + ' · nuvole non disponibili' + (navigator.onLine ? '' : ' (sei offline)') + ': guardate se il cielo è sereno';
    } else {
      const why = auroraReason(est.level, est.withKp);
      verdictEl.textContent = tonight + ' a ' + nightPlaceNames(est) + ': ' + est.level + ' probabilità' + (why ? (why[0] === 'p' ? ' ' : ', ') + why : '');
      verdictEl.classList.add('aurora-tonight__verdict--' + est.level);
      const parts = [];
      if (est.stops.length > 1) est.stops.forEach(st => parts.push(shortPlace(st.name) + ' ' + AU_HH(st.from) + '–' + AU_HH(st.end) + ': ' + st.level));
      const cl = auroraClouds(est);
      if (est.level !== 'nulle' && est.windows.length) parts.push('meglio ' + (cl.variable ? auroraWindowsCloudText(est) : auroraWindowsText(est)));
      parts.push('Kp previsto fino a ' + est.kpMax.toFixed(1).replace('.0', '').replace('.', ','));
      parts.push(cl.text);
      parts.push('buio ' + AU_HH(est.hours[0].t) + '–' + AU_HH(new Date(est.hours[est.hours.length - 1].t.getTime() + 3600000)) + ' (ora islandese)');
      detailEl.textContent = parts.join(' · ') + '. ' + KP_NOTE;
    }
    // le due notti successive, ognuna nel suo luogo
    const next = [1, 2].map(n => {
      const ms = start + n * 86400000;
      const e = nightEstimate(ms, nightStops(isoOf(ms)), data);
      const dn = AU_DAYNAMES[new Date(ms).getUTCDay()];
      return e.level ? dn + ' a ' + nightPlaceNames(e) + ': ' + (auroraNoClouds(e) ? 'incompleta' : e.level) : null;
    }).filter(Boolean);
    daysEl.textContent = next.length ? 'Prossime notti: ' + next.join(' · ') : '';
    if (data.kpAt) {
      const when = new Date(data.kpAt);
      const t = String(when.getUTCHours()).padStart(2, '0') + ':' + String(when.getUTCMinutes()).padStart(2, '0');
      const d = String(when.getUTCDate()).padStart(2, '0') + '/' + String(when.getUTCMonth() + 1).padStart(2, '0');
      const today = when.toISOString().slice(0, 10) === new Date().toISOString().slice(0, 10);
      srcEl.textContent = !navigator.onLine ? 'Ultimo dato salvato il ' + d + ' alle ' + t + ' · sei offline'
        : today ? 'Aggiornato alle ' + t + ' (ora islandese)' : 'Ultimo aggiornamento il ' + d + ' alle ' + t;
    } else {
      srcEl.textContent = '';
    }
  }

  // nelle tab dei giorni: stima per quella notte, appena la previsione copre la data
  DAYS_META.forEach(day => {
    const el = document.querySelector('[data-aurora-live="' + day.id + '"]');
    if (!el) return;
    const [Y, M, D] = day.dateISO.split('-').map(Number);
    const e = day.id === 'd8' ? {} : nightEstimate(Date.UTC(Y, M - 1, D, 12), nightStops(day.dateISO), data);
    el.textContent = e.level && auroraNoClouds(e)
      ? ' Previsione per questa notte: incompleta (mancano i dati sulle nuvole).'
      : e.level
      ? ' Previsione per questa notte: ' + e.level + ' probabilità' + ((w => w ? (w[0] === 'p' ? ' ' : ', ') + w : '')(auroraReason(e.level, e.withKp)))
        + (e.level !== 'nulle' && e.windows.length ? ', meglio ' + auroraWindowsText(e) : '')
        + (e.stops.length > 1 ? ' (' + e.stops.map(st => shortPlace(st.name) + ' ' + st.level).join(', ') + ')' : '') + '. ' + KP_NOTE
      : '';
  });
}

var auroraReady = true;   // var: all'avvio vale ancora undefined, prima di queste definizioni
try { renderAurora(); } catch (e) { /* la stima aurora non deve fermare il resto dell'app */ }

// riquadro aurora compatto: aprendolo si scaricano OVATION e vento solare (se è buio)
const auroraPanel = document.getElementById('aurora-panel');
if (auroraPanel) auroraPanel.addEventListener('toggle', () => {
  const tg = auroraPanel.querySelector('.aurora-panel__toggle');
  if (tg) tg.textContent = auroraPanel.open ? 'Chiudi' : 'Dettagli';
  if (auroraPanel.open) fetchAuroraNow();
});

const FX_FALLBACK_RATE = 145.5; // stima approssimativa EUR->ISK, usata se offline
let fxRate = FX_FALLBACK_RATE;
const FX_PAIRS = [['fx-eur', 'fx-isk'], ['fab-fx-eur', 'fab-fx-isk']];

// numeri scritti all'italiana: "12,5", "1.500" (punto delle migliaia); niente negativi
function fxParse(v) {
  let t = String(v).replace(/[^\d.,-]/g, '');   // via spazi, simboli (€, kr) e lettere
  if (/^\d{1,3}(\.\d{3})+(,\d*)?$/.test(t)) t = t.replace(/\./g, '');
  const n = parseFloat(t.replace(',', '.'));
  return isFinite(n) && n >= 0 ? n : NaN;
}
// punto delle migliaia (1.442), che fxParse rilegge
const fxFmt = s => s.replace(/^\d+/, d => d.replace(/\B(?=(\d{3})+$)/g, '.'));

function fxUpdateFrom(source, eurId, iskId) {
  const eurEl = document.getElementById(eurId);
  const iskEl = document.getElementById(iskId);
  if (!eurEl || !iskEl) return;
  if (source === 'eur') {
    const eur = fxParse(eurEl.value);
    iskEl.value = isFinite(eur) ? fxFmt(String(Math.round(eur * fxRate))) : '';
  } else {
    const isk = fxParse(iskEl.value);
    eurEl.value = isFinite(isk) ? fxFmt(String(Math.round((isk / fxRate) * 100) / 100).replace('.', ',')) : '';
  }
}

function fxUpdateAll(source) {
  FX_PAIRS.forEach(([eurId, iskId]) => fxUpdateFrom(source, eurId, iskId));
}

function fxSetup() {
  FX_PAIRS.forEach(([eurId, iskId]) => {
    const eurEl = document.getElementById(eurId);
    const iskEl = document.getElementById(iskId);
    if (!eurEl || !iskEl) return;
    eurEl.addEventListener('input', () => fxUpdateFrom('eur', eurId, iskId));
    iskEl.addEventListener('input', () => fxUpdateFrom('isk', eurId, iskId));
  });
  fxUpdateAll('eur');
}
fxSetup();

async function fetchFxRate() {
  const label = document.getElementById('fx-rate-label');
  const fabLabel = document.getElementById('fab-fx-rate-label');
  // La BCE (e quindi Frankfurter, che ne replica i tassi) non pubblica un
  // cambio per la corona islandese: usiamo open.er-api.com, gratuita e
  // senza chiave, che copre l'ISK.
  try {
    const res = await fetch('https://open.er-api.com/v6/latest/EUR');
    const json = await res.json();
    if (json && json.result === 'success' && json.rates && json.rates.ISK) {
      fxRate = json.rates.ISK;
      const when = json.time_last_update_utc ? new Date(json.time_last_update_utc) : new Date();
      const hh = String(when.getHours()).padStart(2, '0') + ':' + String(when.getMinutes()).padStart(2, '0');
      if (label) label.textContent = '1 € \u2248 ' + fxRate.toFixed(1).replace('.', ',') + ' ISK \u00b7 aggiornato alle ' + hh;
      if (fabLabel) fabLabel.textContent = '1 € \u2248 ' + fxRate.toFixed(1).replace('.', ',') + ' ISK';
      fxUpdateAll('eur');
      return;
    }
    throw new Error('no rate');
  } catch (e) {
    if (label) label.textContent = '1 € \u2248 ' + FX_FALLBACK_RATE.toFixed(1).replace('.', ',') + ' ISK \u00b7 stima offline, non è il tasso di oggi';
    if (fabLabel) fabLabel.textContent = '1 € \u2248 ' + FX_FALLBACK_RATE.toFixed(1).replace('.', ',') + ' ISK (stima offline)';
  }
}

function fabFxSetup() {
  const btn = document.getElementById('fab-fx-btn');
  const popup = document.getElementById('fab-fx-popup');
  const closeBtn = document.getElementById('fab-fx-close');
  if (!btn || !popup) return;
  const setOpen = (open) => { popup.hidden = !open; btn.setAttribute('aria-expanded', open ? 'true' : 'false'); };
  btn.addEventListener('click', () => { setOpen(popup.hidden); });
  if (closeBtn) closeBtn.addEventListener('click', () => { setOpen(false); btn.focus(); });
  document.addEventListener('click', (e) => {
    if (!popup.hidden && !popup.contains(e.target) && e.target !== btn) setOpen(false);
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !popup.hidden) { setOpen(false); btn.focus(); }
  });
}
fabFxSetup();

let tripMap = null, tripBounds = null;
const TRIP_FIT = { paddingTopLeft: [52, 34], paddingBottomRight: [34, 34] };
function initTripMap() {
  const el = document.getElementById('trip-map');
  if (!el || typeof L === 'undefined') return;

  const stops = [
    { key: 'keflavik', label: 'Keflavík (aeroporto)', n: '1' },
    { key: 'reykjavik', label: 'Reykjavík', n: '2' },
    { key: 'vik', label: 'Vík í Mýrdal', n: '3' },
    { key: 'fludir', label: 'Flúðir', n: '4' }
  ];

  const map = L.map(el, { scrollWheelZoom: false, dragging: false, tap: false, zoomControl: false, zoomSnap: 0.25 });
  L.control.zoom({ position: 'bottomleft', zoomInTitle: 'Ingrandisci mappa', zoomOutTitle: 'Riduci mappa' }).addTo(map);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
    subdomains: 'abc',
    maxZoom: 19,
    crossOrigin: true
  }).addTo(map);

  const latlngs = stops.map(s => [LOCATIONS[s.key].lat, LOCATIONS[s.key].lon]);

  const dayLines = Object.values(DAY_GEOMETRY);
  if (dayLines.length) {
    // strade reali di tutti i giorni (percorsi precalcolati)
    dayLines.forEach(line => L.polyline(line, { color: '#d9985f', weight: 3, opacity: 0.9, lineCap: 'round' }).addTo(map));
  } else {
    L.polyline(latlngs, {
      color: '#d9985f',
      weight: 3,
      dashArray: '1,9',
      lineCap: 'round'
    }).addTo(map);
  }

  stops.forEach(s => {
    const loc = LOCATIONS[s.key];
    const icon = L.divIcon({
      className: '',
      html: '<div style="width:26px;height:26px;border-radius:50%;background:#b5673a;border:2px solid #16263b;' +
            'display:flex;align-items:center;justify-content:center;font:700 12px \'IBM Plex Sans\',sans-serif;color:#16263b;">' + s.n + '</div>',
      iconSize: [26, 26],
      iconAnchor: [13, 13]
    });
    L.marker([loc.lat, loc.lon], { icon }).addTo(map).bindPopup(s.label);
  });

  // margini: a sinistra in basso ci sono i pulsanti +/−, a destra in basso i crediti della mappa;
  // l'inquadratura comprende anche le strade di tutti i giorni
  tripBounds = L.latLngBounds(latlngs.concat(...dayLines));
  map.fitBounds(tripBounds, TRIP_FIT);
  tripMap = map;

  el.addEventListener('touchstart', () => { map.scrollWheelZoom.enable(); map.dragging.enable(); }, { once: true, passive: true });
}

// Aggiornamento dei dati live (aurora, meteo, cambio).
// Le fetch vengono tentate sempre: se sei offline il service worker
// risponde con l'ultimo dato valido salvato in cache.
let lastLiveRefresh = 0;
function refreshLiveData(force) {
  const now = Date.now();
  if (!force && now - lastLiveRefresh < 60000) return;
  lastLiveRefresh = now;
  fetchKp();
  fetchAuroraNow();
  fetchKpForecast();
  fetchAllWeather();
  fetchFxRate();
}

// Al ritorno della connessione, e quando si torna sull'app dopo averla
// lasciata in background (tipico della PWA sul telefono).
window.addEventListener('online', () => refreshLiveData(true));
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') refreshLiveData(false);
});

function updateCountdown() {
  const bigEl = document.getElementById('countdown-big');
  const subEl = document.getElementById('countdown-sub');
  if (!bigEl || !DAYS_META.length) return;
  const start = new Date(DAYS_META[0].dateISO + 'T00:00:00');
  const end = new Date(DAYS_META[DAYS_META.length - 1].dateISO + 'T23:59:59');
  const now = new Date();
  if (now < start) {
    const days = Math.ceil((start - now) / 86400000);
    bigEl.textContent = days === 1 ? 'Manca 1 giorno' : ('Mancano ' + days + ' giorni');
    subEl.textContent = "alla partenza per l'Islanda";
  } else if (now <= end) {
    const dayNum = Math.min(Math.floor((now - start) / 86400000) + 1, DAYS_META.length);
    bigEl.textContent = 'Siete in viaggio!';
    subEl.textContent = 'Giorno ' + dayNum + ' di ' + DAYS_META.length;
  } else {
    bigEl.textContent = 'Bentornati!';
    subEl.textContent = "Il viaggio in Islanda è finito \u2014 che ricordo dev'essere stato.";
  }
}
updateCountdown();
setInterval(updateCountdown, 3600000);

function localISO(d) {
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
}
let jumpedISO = localISO(new Date());
function jumpToTodayIfInTrip() {
  jumpedISO = localISO(new Date());
  const match = DAYS_META.find(d => d.dateISO === jumpedISO);
  if (match) setActive(match.id);
}
initTripMap();          // prima del salto al giorno: con la tab Info nascosta la mappa resterebbe vuota
jumpToTodayIfInTrip();
// app lasciata aperta la sera e ripresa la mattina dopo: passa da sola al giorno nuovo
// (solo se è cambiata la data, così durante il giorno non sposta la tab scelta)
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible' && localISO(new Date()) !== jumpedISO) {
    updateCountdown();
    jumpToTodayIfInTrip();
  }
});


refreshLiveData(true);

// ---------- Offline: pacchetto completo e aggiornamenti ----------
const APP_CACHE = 'islanda-2026-app-' + APP_VERSION;
const TILE_CACHE = 'islanda-2026-tiles';
const OFFLINE_KEY = 'islanda2026-offline';
const VERSION_KEY = 'islanda2026-version';
const UPDATED_KEY = 'islanda2026-updated-at';

function showToast(msg) {
  const t = document.createElement('div');
  t.className = 'app-toast';
  t.setAttribute('role', 'status');
  t.textContent = msg;
  document.body.appendChild(t);
  requestAnimationFrame(() => t.classList.add('app-toast--show'));
  setTimeout(() => { t.classList.remove('app-toast--show'); setTimeout(() => t.remove(), 400); }, 3500);
}

// Tab Info: versione in uso e quando il telefono l'ha ricevuta (per capire
// se un aggiornamento è arrivato).
function showAppVersion() {
  const el = document.getElementById('app-version');
  if (!el) return;
  let when = null;
  try { when = localStorage.getItem(UPDATED_KEY); } catch (e) {}
  el.textContent = 'Versione app ' + APP_VERSION.slice(0, 7);
  const rec = document.getElementById('app-received');
  if (rec) rec.textContent = when ? 'Ricevuta il ' + fmtWhen(when) : '';
}

(function announceUpdate() {
  // La nuova versione di solito si carica mentre l'app è in background:
  // l'avviso aspetta che la pagina sia visibile, altrimenti nessuno lo vede.
  try {
    const prev = localStorage.getItem(VERSION_KEY);
    if (prev === APP_VERSION) return;
    const announce = () => {
      if (prev) showToast('Contenuti aggiornati');
      localStorage.setItem(VERSION_KEY, APP_VERSION);
      localStorage.setItem(UPDATED_KEY, new Date().toISOString());
      showAppVersion();
    };
    if (document.visibilityState !== 'hidden') { announce(); return; }
    const onVisible = () => {
      if (document.visibilityState === 'hidden') return;
      document.removeEventListener('visibilitychange', onVisible);
      setTimeout(announce, 600);   // il tempo di ridisegnare la pagina
    };
    document.addEventListener('visibilitychange', onVisible);
  } catch (e) { /* storage non disponibile */ }
})();
showAppVersion();

function fmtWhen(iso) {
  const d = new Date(iso);
  return String(d.getDate()).padStart(2, '0') + '/' + String(d.getMonth() + 1).padStart(2, '0')
       + ' alle ' + String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
}

// Impronta dell'elenco preciso dei riquadri di mappa: cambia con qualunque
// modifica del percorso, anche se il numero di riquadri resta uguale.
const OFFLINE_TILES_KEY = (() => {
  let h = 2166136261;
  for (const ch of OFFLINE_TILES.join(',')) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619); }
  return (h >>> 0).toString(16);
})();

async function showOfflineState() {
  const status = document.getElementById('offline-status');
  if (!status) return;
  let saved = null;
  try { saved = JSON.parse(localStorage.getItem(OFFLINE_KEY) || 'null'); } catch (e) {}
  if (saved && saved.tilesKey === OFFLINE_TILES_KEY && !saved.missing) {
    let used = '';
    try {
      const est = await navigator.storage.estimate();
      used = ' · spazio usato ~' + Math.round(est.usage / 1048576) + ' MB';
    } catch (e) {}
    status.textContent = '\u2713 Pronto per l\u2019offline · preparato il ' + fmtWhen(saved.at) + used;
    status.classList.add('offline-status--ok');
    const btn = document.getElementById('offline-btn');
    // già pronto: il pulsante resta (per ripetere) ma passa in secondo piano
    if (btn) { btn.textContent = 'Già pronto \u2713 · riscarica'; btn.classList.add('offline-btn--done'); }
  } else if (saved && saved.missing && saved.tilesKey === OFFLINE_TILES_KEY) {
    status.textContent = 'Preparazione incompleta: mancano ' + saved.missing + ' elementi. Ripeti (scarica solo quelli mancanti).';
  } else if (saved) {
    status.textContent = 'Il percorso è cambiato dall\u2019ultima preparazione: ripeti per aggiornare le mappe.';
  }
}

async function prepareOffline() {
  const btn = document.getElementById('offline-btn');
  const bar = document.getElementById('offline-bar');
  const fill = document.getElementById('offline-fill');
  const status = document.getElementById('offline-status');
  status.classList.remove('offline-status--ok');
  btn.classList.remove('offline-btn--done');
  btn.textContent = 'Prepara offline';
  if (!('caches' in window)) { status.textContent = 'Questo browser non permette di salvare i contenuti offline.'; return; }
  if (!navigator.onLine) { status.textContent = 'Serve una connessione (meglio Wi-Fi) per scaricare i contenuti.'; return; }
  btn.disabled = true;
  bar.hidden = false;
  bar.setAttribute('aria-valuenow', '0');
  try { if (navigator.storage && navigator.storage.persist) await navigator.storage.persist(); } catch (e) {}

  const appCache = await caches.open(APP_CACHE);
  const tileCache = await caches.open(TILE_CACHE);
  const photos = [...new Set([...document.querySelectorAll('[data-photo]')].map(el => 'images/web/' + el.dataset.photo.replace(/\.jpg$/, '.webp')))];
  const jobs = photos.map(u => ({ url: u, cache: appCache, optional: true }))
    .concat(OFFLINE_TILES.map(t => ({ url: 'https://tile.openstreetmap.org/' + t + '.png', cache: tileCache, optional: false })));
  let done = 0, failed = 0, next = 0;

  async function run(job) {
    // fino a 3 tentativi: OpenStreetMap a volte rifiuta qualche riquadro se si scarica in fretta
    for (let attempt = 0; ; attempt++) {
      try {
        if (await job.cache.match(job.url, { ignoreSearch: true })) break;
        const res = await fetch(job.url, { mode: 'cors' });
        if (res.ok) { await job.cache.put(job.url, res); break; }
        if (job.optional) break;   // una foto non ancora caricata (404) non è un errore
      } catch (e) {}
      if (attempt === 2) { failed++; break; }
      await new Promise(r => setTimeout(r, 1500 * (attempt + 1)));
    }
    done++;
    const pct = Math.round(done / jobs.length * 100);
    fill.style.width = pct + '%';
    bar.setAttribute('aria-valuenow', String(pct));
    status.textContent = 'Scaricamento… ' + done + ' di ' + jobs.length;
  }
  // al massimo 2 richieste alla volta, come chiede la policy dei tile OpenStreetMap
  await Promise.all([0, 1].map(async () => { while (next < jobs.length) await run(jobs[next++]); }));

  btn.disabled = false;
  // salvato anche se incompleto, così alla riapertura il messaggio dice cosa manca
  try { localStorage.setItem(OFFLINE_KEY, JSON.stringify({ at: new Date().toISOString(), tiles: OFFLINE_TILES.length, tilesKey: OFFLINE_TILES_KEY, missing: failed })); } catch (e) {}
  if (failed) {
    status.textContent = failed + ' elementi non scaricati: riprova con una connessione migliore (quelli già salvati restano).';
    return;
  }
  bar.hidden = true;
  showOfflineState();
}

(function setupOffline() {
  const btn = document.getElementById('offline-btn');
  if (btn) btn.addEventListener('click', prepareOffline);
  showOfflineState();
})();

// ---------- Avvisi aurora (notifiche push dal workflow GitHub "Avvisi aurora") ----------
function b64urlToBytes(s) {
  const bin = atob(s.replace(/-/g, '+').replace(/_/g, '/') + '='.repeat((4 - s.length % 4) % 4));
  return Uint8Array.from(bin, c => c.charCodeAt(0));
}

(function setupAuroraPush() {
  const status = document.getElementById('aurora-push-status');
  const onBtn = document.getElementById('aurora-push-on');
  const copyBtn = document.getElementById('aurora-push-copy');
  const offBtn = document.getElementById('aurora-push-off');
  const code = document.getElementById('aurora-push-code');
  if (!status) return;
  const say = (msg, ok) => { status.textContent = msg; status.classList.toggle('aurora-push__status--ok', !!ok); };
  // riga chiusa del riquadro: dice subito se gli avvisi sono attivi su questo telefono
  const sumEl = document.getElementById('aurora-push-sum');
  const sum = text => { if (sumEl) sumEl.textContent = text; };
  if (!('serviceWorker' in navigator) || !('PushManager' in window) || !('Notification' in window)) {
    onBtn.hidden = true;
    sum('non disponibili');
    say('Questo browser non supporta le notifiche push. Su iPhone aggiungi prima l’app alla schermata Home.');
    return;
  }

  function show(sub) {
    const on = !!sub;
    onBtn.hidden = on;
    copyBtn.hidden = offBtn.hidden = code.hidden = !on;
    code.value = on ? JSON.stringify(sub) : '';
    sum(on ? 'attivi su questo telefono' : Notification.permission === 'denied' ? 'notifiche bloccate' : 'non attivi');
    if (on) say('✓ Avvisi attivi su questo telefono. Se non l’hai già fatto, copia il codice e incollalo nel secret AURORA_SUBSCRIPTIONS del repo (istruzioni nel leggimi).', true);
    else if (Notification.permission === 'denied') say('Notifiche bloccate: riattivale dalle impostazioni del sito nel browser, poi riprova.');
    else say('');
  }

  // il service worker può non partire mai (es. browser che blocca i dati dei siti): non aspettare all'infinito
  const swReady = () => Promise.race([
    navigator.serviceWorker.ready,
    new Promise((_, reject) => setTimeout(() => reject(new Error('sw')), 10000)),
  ]);
  const swProblem = 'Avvisi non disponibili: il browser non ha avviato l’app installata. Riapri l’app dall’icona e controlla che il browser non cancelli i dati dei siti.';

  swReady().then(reg => reg.pushManager.getSubscription()).then(show).catch(() => show(null));

  onBtn.addEventListener('click', async () => {
    if (!navigator.onLine) { say('Serve una connessione per attivare gli avvisi.'); return; }
    onBtn.disabled = true;
    say('Attivazione…');
    try {
      if (await Notification.requestPermission() !== 'granted') { show(null); if (Notification.permission !== 'denied') say('Permesso per le notifiche non concesso.'); return; }
      const reg = await swReady();
      const sub = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: b64urlToBytes(VAPID_PUBLIC_KEY) });
      show(sub);
    } catch (e) {
      say(e && e.message === 'sw' ? swProblem
        : 'Attivazione non riuscita (' + (e && e.message ? e.message : e) + '). Riprova con la connessione; se continua, riapri l’app.');
    } finally {
      onBtn.disabled = false;
    }
  });

  copyBtn.addEventListener('click', async () => {
    let copied = false;
    try { await navigator.clipboard.writeText(code.value); copied = true; }
    catch (e) { code.select(); try { copied = document.execCommand('copy'); } catch (e2) {} }
    showToast(copied ? 'Codice copiato' : 'Copia non riuscita: tieni premuto sul codice e copialo a mano');
  });

  offBtn.addEventListener('click', async () => {
    try {
      const reg = await swReady();
      const sub = await reg.pushManager.getSubscription();
      if (sub) await sub.unsubscribe();
    } catch (e) {}
    show(null);
    say('Avvisi disattivati su questo telefono.');
  });
})();

if ('serviceWorker' in navigator) {
  // Una nuova versione si scarica in background e si applica solo quando
  // l'app non è in uso: appena riaperta o mentre è in background.
  const hadController = !!navigator.serviceWorker.controller;
  const openedAt = Date.now();
  let reloadPending = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (!hadController) return;   // prima installazione: niente da ricaricare
    if (document.visibilityState === 'hidden' || Date.now() - openedAt < 10000) location.reload();
    else reloadPending = true;    // la stai usando: si ricarica quando esci dall'app
  });
  window.addEventListener('load', async () => {
    let reg;
    try { reg = await navigator.serviceWorker.register('sw.js'); } catch (e) { return; }
    if (!reg) return;   // service worker non disponibile (es. bloccato dal browser)
    const applyUpdate = () => {
      if (reg.waiting && navigator.serviceWorker.controller) reg.waiting.postMessage('skipWaiting');
    };
    applyUpdate();
    let lastCheck = Date.now();
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        if (reloadPending) location.reload(); else applyUpdate();
      } else if (navigator.onLine && Date.now() - lastCheck > 3600000) {
        lastCheck = Date.now();
        reg.update().catch(() => {});
      }
    });
  });
}
