// Mappa aurora (mappa-aurora.html): aurora OVATION, nuvole ora per ora, satellite, posti delle
// serate, schiarita più vicina, Luna e stima "Adesso". Scarica i dati solo quando la pagina è aperta.
// La stima "Adesso" e le nuvole efficaci vengono da app/aurora.js, come nell'app.

const NOAA = 'https://services.swpc.noaa.gov/';
const CLOUD_KEY = 'islanda2026-mappa-nuvole';
const CLOUD_MAX_AGE = 45 * 60000;            // nuvole riusate per 45 minuti: niente richieste doppie
// griglia delle nuvole: ogni 0,5° (circa 55 km nord-sud, 25 km est-ovest) su tutta l'Islanda
const G_LATS = [], G_LONS = [];
for (let la = 63.25; la <= 66.751; la += 0.5) G_LATS.push(Math.round(la * 100) / 100);
for (let lo = -24.5; lo <= -13.499; lo += 0.5) G_LONS.push(Math.round(lo * 100) / 100);
// scala dell'aurora (probabilità OVATION sopra quel punto), come le immagini NOAA
const AUR_STOPS = [[5, [61, 220, 132], 0], [10, [61, 220, 132], 0.30], [20, [168, 224, 95], 0.45],
  [30, [255, 216, 74], 0.55], [50, [255, 159, 46], 0.65], [80, [255, 59, 48], 0.72]];

const st = { ov: null, ovAt: null, grid: null, kp: null, kpFc: [], bz: null, v: null, hour: 0, me: null, cloudErr: null };
const $ = id => document.getElementById(id);
const HHMM = ms => { const d = new Date(ms); return String(d.getUTCHours()).padStart(2, '0') + ':' + String(d.getUTCMinutes()).padStart(2, '0'); };
const fmtNum = x => String(x).replace('.', ',').replace('-', '−');

// ---------- mappa di base: le tile OSM dell'app (anche offline dopo "Prepara offline") ----------
const map = L.map('am-map', { zoomControl: false, attributionControl: true, minZoom: 4, maxZoom: 12 })
  .setView([64.6, -19.2], 6);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 12, subdomains: 'abc',
  attribution: '© OpenStreetMap' }).addTo(map);
map.attributionControl.setPrefix(false);
map.createPane('sat').style.zIndex = 250;
map.createPane('clouds').style.zIndex = 410;
map.createPane('aurora').style.zIndex = 420;
const satLayer = L.tileLayer.wms('https://view.eumetsat.int/geoserver/wms', { pane: 'sat',
  layers: 'mtg_fd:ir105_hrfi', version: '1.3.0', format: 'image/png', transparent: true, opacity: 0.5,
  attribution: '© EUMETSAT' });

// ---------- immagini su canvas proiettate in Mercatore, così combaciano con la mappa ----------
const mercY = lat => Math.log(Math.tan(Math.PI / 4 + lat * Math.PI / 360));
const invMercY = y => (2 * Math.atan(Math.exp(y)) - Math.PI / 2) * 180 / Math.PI;
function canvasOverlay(south, north, west, east, pxPerDeg, colorAt) {
  const W = Math.round((east - west) * pxPerDeg);
  const yN = mercY(north), yS = mercY(south);
  const H = Math.round((yN - yS) / ((east - west) * Math.PI / 180) * W);
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d'), img = ctx.createImageData(W, H);
  for (let j = 0; j < H; j++) {
    const lat = invMercY(yN - (j + 0.5) / H * (yN - yS));
    for (let i = 0; i < W; i++) {
      const c = colorAt(lat, west + (i + 0.5) / pxPerDeg);
      if (!c) continue;
      const k = (j * W + i) * 4;
      img.data[k] = c[0]; img.data[k + 1] = c[1]; img.data[k + 2] = c[2]; img.data[k + 3] = c[3];
    }
  }
  ctx.putImageData(img, 0, 0);
  return cv.toDataURL('image/png');
}

// ---------- aurora OVATION ----------
let auroraLayer = null, viewLine = null;
function ovGrid(coords) {
  const g = new Float32Array(360 * 181);
  coords.forEach(c => {
    if (Array.isArray(c) && c.length === 3 && c.every(x => typeof x === 'number' && isFinite(x))
        && c[0] >= 0 && c[0] < 360 && c[1] >= -90 && c[1] <= 90) g[(c[1] + 90) * 360 + c[0]] = c[2];
  });
  return g;
}
function ovAt(g, lon, lat) {   // interpolazione tra i 4 punti vicini (griglia di 1°)
  const x = ((lon % 360) + 360) % 360, x0 = Math.floor(x), y0 = Math.floor(lat), fx = x - x0, fy = lat - y0;
  const v = (xx, yy) => g[(Math.max(-90, Math.min(90, yy)) + 90) * 360 + (xx % 360)];
  return (v(x0, y0) * (1 - fx) + v(x0 + 1, y0) * fx) * (1 - fy) + (v(x0, y0 + 1) * (1 - fx) + v(x0 + 1, y0 + 1) * fx) * fy;
}
function auroraColor(p) {
  if (p < AUR_STOPS[0][0]) return null;
  for (let i = 1; i < AUR_STOPS.length; i++) {
    const [p1, c1, a1] = AUR_STOPS[i], [p0, c0, a0] = AUR_STOPS[i - 1];
    if (p <= p1) {
      const f = (p - p0) / (p1 - p0);
      return [0, 1, 2].map(k => Math.round(c0[k] + (c1[k] - c0[k]) * f)).concat(Math.round((a0 + (a1 - a0) * f) * 255));
    }
  }
  const last = AUR_STOPS[AUR_STOPS.length - 1];
  return last[1].concat(Math.round(last[2] * 255));
}
function drawAurora() {
  if (auroraLayer) { map.removeLayer(auroraLayer); auroraLayer = null; }
  if (viewLine) { map.removeLayer(viewLine); viewLine = null; }
  if (!st.ov || !layerOn('aurora')) return;
  const g = st.ov;
  const url = canvasOverlay(58, 74, -45, 5, 6, (lat, lon) => auroraColor(ovAt(g, lon, lat)));
  auroraLayer = L.imageOverlay(url, [[58, -45], [74, 5]], { pane: 'aurora', interactive: false }).addTo(map);
  // "fin qui si vede bassa a nord": bordo sud dell'ovale (≥ 10%) spostato di 7° (circa 800 km) verso sud
  const pts = [];
  for (let lon = -45; lon <= 5; lon++) {
    let edge = null;
    for (let lat = 80; lat >= 50; lat -= 0.25) { if (ovAt(g, lon, lat) >= 10) edge = lat; else if (edge !== null) break; }
    pts.push(edge === null ? null : [edge - 7, lon]);
  }
  const smooth = pts.map((p, i) => {
    if (!p) return null;
    const near = [pts[i - 1], p, pts[i + 1]].filter(Boolean);
    return [near.reduce((a, q) => a + q[0], 0) / near.length, p[1]];
  });
  const segs = [];
  smooth.forEach(p => { if (!p) segs.push([]); else { if (!segs.length) segs.push([]); segs[segs.length - 1].push(p); } });
  const lines = segs.filter(s => s.length > 1);
  if (lines.length) viewLine = L.polyline(lines, { pane: 'aurora', color: '#e0b400', weight: 2.5, dashArray: '6 5', interactive: false }).addTo(map);
}

// ---------- nuvole a gradini (griglia Open-Meteo, stesso metodo dell'app) ----------
let cloudLayer = null;
function sandColors() {
  const cs = getComputedStyle(document.documentElement);
  return [1, 2, 3, 4].map(n => {
    const m = cs.getPropertyValue('--sand-' + n).match(/[\d.]+/g) || [0, 0, 0, 0];
    return [+m[0], +m[1], +m[2], Math.round(+m[3] * 255)];
  });
}
function cloudAt(hour, lat, lon) {   // interpolazione tra i 4 punti della griglia; null fuori o senza dati
  const g = st.grid && st.grid.v[hour];
  if (!g) return null;
  const fy = (lat - G_LATS[0]) / 0.5, fx = (lon - G_LONS[0]) / 0.5;
  const y0 = Math.floor(fy), x0 = Math.floor(fx);
  if (y0 < 0 || x0 < 0 || y0 >= G_LATS.length - 1 || x0 >= G_LONS.length - 1) return null;
  const v = (y, x) => g[y * G_LONS.length + x];
  const q = [v(y0, x0), v(y0, x0 + 1), v(y0 + 1, x0), v(y0 + 1, x0 + 1)];
  if (q.some(x => x === null)) return null;
  const tx = fx - x0, ty = fy - y0;
  return (q[0] * (1 - tx) + q[1] * tx) * (1 - ty) + (q[2] * (1 - tx) + q[3] * tx) * ty;
}
// indice della griglia per l'ora in corso (la previsione salvata può partire da qualche ora prima)
function hourNow() {
  if (!st.grid) return -1;
  return st.grid.times.findIndex(t => t > Date.now() - 3600000 && t <= Date.now());
}
function drawClouds() {
  if (cloudLayer) { map.removeLayer(cloudLayer); cloudLayer = null; }
  if (!st.grid || !layerOn('cloud')) return;
  const sand = sandColors();
  const s = G_LATS[0], n = G_LATS[G_LATS.length - 1], w = G_LONS[0], e = G_LONS[G_LONS.length - 1];
  const url = canvasOverlay(s, n, w, e, 12, (lat, lon) => {
    const c = cloudAt(st.hour, lat, lon);
    return c === null || c < 20 ? null : sand[Math.min(3, Math.floor(c / 20) - 1)];
  });
  cloudLayer = L.imageOverlay(url, [[s, w], [n, e]], { pane: 'clouds', interactive: false }).addTo(map);
}
async function loadClouds() {
  try {
    const saved = JSON.parse(localStorage.getItem(CLOUD_KEY) || 'null');
    if (saved && Array.isArray(saved.v) && Array.isArray(saved.times)) {
      st.grid = saved;
      if (Date.now() - saved.at < CLOUD_MAX_AGE || !navigator.onLine) return;
    }
  } catch (e) {}
  if (!navigator.onLine) return;
  const lats = [], lons = [];
  G_LATS.forEach(la => G_LONS.forEach(lo => { lats.push(la); lons.push(lo); }));
  const multi = CLOUD_METHOD.startsWith('media');
  const vars = CLOUD_METHOD === 'media' || CLOUD_METHOD === 'totale' ? 'cloud_cover' : 'cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high';
  const url = 'https://api.open-meteo.com/v1/forecast?latitude=' + lats.join(',') + '&longitude=' + lons.join(',')
    + '&hourly=' + vars + (multi ? '&models=' + CLOUD_MODELS.join(',') : '') + '&forecast_hours=24&timezone=UTC';
  try {
    const res = await fetch(url, { cache: 'no-store' });
    if (res.status === 429) {   // limite d'uso gratuito: si riprova da soli una volta dopo un minuto
      st.cloudErr = 'Nuvole: troppe richieste, riprovo tra un minuto';
      if (!loadClouds.retry) { loadClouds.retry = true; setTimeout(start, 61000); }
      return;
    }
    const json = await res.json();
    const pts = Array.isArray(json) ? json : [json];
    if (pts.length !== lats.length || !pts[0].hourly) throw new Error('risposta inattesa');
    const times = pts[0].hourly.time.map(t => Date.parse(t + 'Z'));
    const v = times.map((_, h) => pts.map(p => { const c = effCloud(p.hourly, h); return c == null ? null : Math.round(c); }));
    st.grid = { at: Date.now(), times, v };
    st.cloudErr = null;
    try { localStorage.setItem(CLOUD_KEY, JSON.stringify(st.grid)); } catch (e) {}
  } catch (e) {
    if (!st.grid) st.cloudErr = 'Nuvole non disponibili al momento';
  }
}

// ---------- posti delle serate del viaggio ----------
const placesLayer = L.layerGroup().addTo(map);
function tonightKey() { return auroraNowPlace().place; }
function placeNights(key) {
  return DAYS_META.filter(d => d.id !== 'd8' && nightStops(d.dateISO).some(s => s.place === key))
    .map(d => +d.dateISO.slice(8, 10) + '/' + +d.dateISO.slice(5, 7));
}
function drawPlaces() {
  placesLayer.clearLayers();
  if (!layerOn('places')) return;
  const tonight = tonightKey();
  // solo i posti dove si passa una serata (non l'aeroporto dell'ultimo giorno)
  Object.keys(AURORA_PLACES).filter(key => key === tonight || placeNights(key).length).forEach(key => {
    const p = AURORA_PLACES[key], nm = shortPlace(p.name), isT = key === tonight;
    const html = '<span><b>' + nm.replace(/^strada.*/, 'S').charAt(0).toUpperCase() + '</b>'
      + (isT ? nm + ' <em>stasera</em>' : '') + '</span>' + (isT ? '' : '<i>' + nm + '</i>');
    const m = L.marker([p.lat, p.lon], { icon: L.divIcon({ className: 'am-pin' + (isT ? ' am-pin--tonight' : ''), html, iconSize: [0, 0] }),
      zIndexOffset: isT ? 1000 : 0, keyboard: false });
    const nights = placeNights(key);
    m.bindPopup('<b>' + p.name + '</b>' + (nights.length ? '<br>Serate: ' + nights.join(', ') : ''));
    m.addTo(placesLayer);
  });
}

// ---------- posti bui per l'aurora (aurora_spots in dati.py) ----------
const spotsLayer = L.layerGroup().addTo(map);
map.on('zoomend', () => drawSpots());
function drawSpots() {   // da vicino (zoom 8 o più): nella vista d'insieme coprirebbero i posti delle serate
  spotsLayer.clearLayers();
  if (!layerOn('spots') || map.getZoom() < 8) return;
  DARK_SPOTS.forEach(sp => {
    const nav = 'https://www.google.com/maps/dir/?api=1&destination=' + sp.lat + ',' + sp.lon;
    L.marker([sp.lat, sp.lon], { icon: L.divIcon({ className: '', html: '<div class="am-spot">★</div>', iconSize: [0, 0] }), keyboard: false, zIndexOffset: 2000 })
      .bindPopup('<b>⭐ ' + sp.name + '</b><br>' + sp.drive + '<br>' + sp.note + '<br><a class="am-nav" href="' + nav + '" target="_blank" rel="noopener">Naviga ›</a>')
      .addTo(spotsLayer);
  });
}

// ---------- strati accesi/spenti (pillole in alto) ----------
function layerOn(name) { const b = document.querySelector('[data-layer="' + name + '"]'); return !!b && b.getAttribute('aria-pressed') === 'true'; }
document.querySelectorAll('[data-layer]').forEach(b => b.addEventListener('click', () => {
  b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
  const name = b.dataset.layer;
  if (name === 'aurora') drawAurora();
  else if (name === 'cloud') { drawClouds(); renderClear(); }
  else if (name === 'places') drawPlaces();
  else if (name === 'spots') {
    if (layerOn('spots') && map.getZoom() < 8) { const p = AURORA_PLACES[tonightKey()]; map.flyTo([p.lat, p.lon], 9, { duration: 0.8 }); }
    drawSpots();
  }
  else if (name === 'sat') { if (layerOn('sat')) satLayer.addTo(map); else map.removeLayer(satLayer); }
}));
$('am-tonight').addEventListener('click', () => {
  const p = AURORA_PLACES[tonightKey()];
  map.flyTo([p.lat, p.lon], 8, { duration: 0.8 });
});

// ---------- "dove sono" ----------
let meMarker = null;
$('am-locate').addEventListener('click', () => {
  if (!navigator.geolocation) { setStatus('Posizione non disponibile su questo telefono', 'error'); return; }
  setStatus('Cerco la posizione…', 'loading');
  navigator.geolocation.getCurrentPosition(pos => {
    st.me = { lat: pos.coords.latitude, lon: pos.coords.longitude };
    if (meMarker) map.removeLayer(meMarker);
    meMarker = L.marker([st.me.lat, st.me.lon], { icon: L.divIcon({ className: '', html: '<div class="am-me"></div>', iconSize: [0, 0] }), keyboard: false }).addTo(map);
    map.flyTo([st.me.lat, st.me.lon], Math.max(map.getZoom(), 8), { duration: 0.8 });
    setStatus(inIceland(st.me) ? null : 'Sei fuori dall\'Islanda: la stima resta sul posto della serata', inIceland(st.me) ? null : 'offline');
    renderNow(); renderClear();
  }, () => setStatus('Posizione non concessa: attivala per Firefox nelle impostazioni', 'error'),
  { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 });
});

// ---------- schiarita più vicina (in linea d'aria, nell'ora scelta col cursore) ----------
let clearPin = null;
function distKm(a, b) {
  const r = Math.PI / 180, dLat = (b.lat - a.lat) * r, dLon = (b.lon - a.lon) * r;
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(a.lat * r) * Math.cos(b.lat * r) * Math.sin(dLon / 2) ** 2;
  return 6371 * 2 * Math.asin(Math.sqrt(h));
}
function compass(a, b) {
  const r = Math.PI / 180;
  const y = Math.sin((b.lon - a.lon) * r) * Math.cos(b.lat * r);
  const x = Math.cos(a.lat * r) * Math.sin(b.lat * r) - Math.sin(a.lat * r) * Math.cos(b.lat * r) * Math.cos((b.lon - a.lon) * r);
  const deg = (Math.atan2(y, x) / r + 360) % 360;
  return ['nord', 'nord-est', 'est', 'sud-est', 'sud', 'sud-ovest', 'ovest', 'nord-ovest'][Math.round(deg / 45) % 8];
}
function findClear() {
  if (!st.grid) return null;
  const ref = inIceland(st.me) ? st.me : AURORA_PLACES[tonightKey()];
  const here = cloudAt(st.hour, ref.lat, ref.lon);
  if (here === null || here < 40) return null;
  let best = null;
  G_LATS.forEach((la, y) => G_LONS.forEach((lo, x) => {
    const c = st.grid.v[st.hour][y * G_LONS.length + x];
    if (c === null || c > 30 || c > here - 25) return;
    const p = { lat: la, lon: lo }, d = distKm(ref, p);
    if (d > 120) return;
    const score = c + d / 4;
    if (!best || score < best.score) best = { lat: la, lon: lo, cloud: c, d, score };
  }));
  return best && Object.assign(best, { here: Math.round(here), dir: compass(ref, best), from: inIceland(st.me) ? 'da te' : 'da ' + shortPlace(ref.name) });
}
function renderClear() {
  const el = $('am-clear');
  if (clearPin) { map.removeLayer(clearPin); clearPin = null; }
  const c = layerOn('cloud') ? findClear() : null;
  if (!c) { el.hidden = true; return; }
  el.href = 'https://www.google.com/maps/dir/?api=1&destination=' + c.lat + ',' + c.lon;
  el.innerHTML = '<span>☀</span><span>Più sereno a <b>' + Math.round(c.d / 5) * 5 + ' km verso ' + c.dir + '</b> (nuvole ~' + c.cloud
    + '% invece di ' + c.here + '%), in linea d\'aria ' + c.from + '</span><span>Naviga ›</span>';
  el.hidden = false;
  clearPin = L.marker([c.lat, c.lon], { icon: L.divIcon({ className: '', html: '<div class="am-clear-pin"></div>', iconSize: [0, 0] }), keyboard: false }).addTo(map);
}

// ---------- Luna (formule di SunCalc, V. Agafonkin, semplificate) ----------
function moonInfo(date, lat, lon) {
  const r = Math.PI / 180, e = r * 23.4397;
  const d = date.getTime() / 86400000 - 0.5 + 2440588 - 2451545;
  const raDec = (l, b) => ({ ra: Math.atan2(Math.sin(l) * Math.cos(e) - Math.tan(b) * Math.sin(e), Math.cos(l)),
    dec: Math.asin(Math.sin(b) * Math.cos(e) + Math.cos(b) * Math.sin(e) * Math.sin(l)) });
  const L0 = r * (218.316 + 13.176396 * d), M = r * (134.963 + 13.064993 * d), F = r * (93.272 + 13.229350 * d);
  const moon = raDec(L0 + r * 6.289 * Math.sin(M), r * 5.128 * Math.sin(F));
  const mDist = 385001 - 20905 * Math.cos(M);
  const Ms = r * (357.5291 + 0.98560028 * d);
  const Ls = Ms + r * (1.9148 * Math.sin(Ms) + 0.02 * Math.sin(2 * Ms) + 0.0003 * Math.sin(3 * Ms)) + r * 102.9372 + Math.PI;
  const sun = raDec(Ls, 0), sDist = 149598000;
  const phi = Math.acos(Math.sin(sun.dec) * Math.sin(moon.dec) + Math.cos(sun.dec) * Math.cos(moon.dec) * Math.cos(sun.ra - moon.ra));
  const inc = Math.atan2(sDist * Math.sin(phi), mDist - sDist * Math.cos(phi));
  const angle = Math.atan2(Math.cos(sun.dec) * Math.sin(sun.ra - moon.ra),
    Math.sin(sun.dec) * Math.cos(moon.dec) - Math.cos(sun.dec) * Math.sin(moon.dec) * Math.cos(sun.ra - moon.ra));
  const H = r * (280.16 + 360.9856235 * d) + r * lon - moon.ra, ph = r * lat;
  const alt = Math.asin(Math.sin(ph) * Math.sin(moon.dec) + Math.cos(ph) * Math.cos(moon.dec) * Math.cos(H)) / r;
  return { frac: (1 + Math.cos(inc)) / 2, waxing: angle < 0, alt };
}
function moonText(loc) {
  const m = moonInfo(new Date(), loc.lat, loc.lon), pct = Math.round(m.frac * 100);
  const phase = pct >= 97 ? 'piena' : pct <= 3 ? 'nuova' : (m.waxing ? 'crescente' : 'calante') + ' al ' + pct + '%';
  if (m.alt < 0) return 'Luna ' + phase + ', sotto l\'orizzonte: non disturba';
  return 'Luna ' + phase + ', alta ' + Math.round(m.alt) + '°' + (m.frac > 0.6 && m.alt > 10 ? ': schiarisce il cielo, l\'aurora debole si vede meno' : '');
}

// ---------- stima "Adesso" (stessa regola dell'app e dell'avviso) ----------
function appCloudNow(place) {   // nuvole del posto salvate dall'app, se ci sono: stessi numeri del box "Adesso"
  try {
    const d = JSON.parse(localStorage.getItem('islanda2026-aurora') || 'null');
    const c = d && d.clouds && d.clouds[place];
    if (c && Array.isArray(c.time)) {
      const idx = c.time.indexOf(new Date().toISOString().slice(0, 13) + ':00');
      if (idx >= 0) return effCloud(c, idx);
    }
  } catch (e) {}
  return null;
}
const inIceland = p => p && p.lat > 62.8 && p.lat < 67.2 && p.lon > -25.5 && p.lon < -12.5;
function renderNow() {
  const { place, loc } = auroraNowPlace();
  const me = inIceland(st.me) ? st.me : null;   // da casa la stima resta sul posto della serata
  const ref = me ? { lat: me.lat, lon: me.lon } : loc;
  const ovRaw = st.ov && st.ovAt ? ovationNorth(st.ovCoords, ref) : null;
  const ov = ovRaw === null ? null : Math.round(ovRaw);
  let cloud = me ? null : appCloudNow(place);
  if (cloud === null && hourNow() >= 0) { const c = cloudAt(hourNow(), ref.lat, ref.lon); cloud = c === null ? null : Math.round(c); }
  const wind = windState(st.bz, st.v);
  const sunAlt = sunAltitude(new Date(), ref.lat, ref.lon);
  const { level, text } = auroraNowVerdict({ ov, kp: st.kp, cloud, sunAlt, wind });
  const nm = me ? 'dove sei' : shortPlace(loc.name);
  const facts = [me ? 'Adesso dove sei' : 'Adesso a ' + nm];
  if (st.kp !== null) facts.push('Kp ' + fmtNum(st.kp));
  facts.push(cloud !== null ? 'nuvole ' + cloud + '%' : 'nuvole n.d.');
  if (st.ovAt) facts.push('dati ' + HHMM(st.ovAt));
  $('am-ring').style.setProperty('--p', ov === null ? 0 : Math.min(100, ov));
  $('am-ring-txt').textContent = ov === null ? '–' : ov + '%';
  const v = $('am-verdict');
  v.className = 'am-now__verdict' + (level ? ' am-now__verdict--' + level : '');
  v.textContent = text.charAt(0).toUpperCase() + text.slice(1);
  $('am-facts').textContent = facts.join(' · ');
  // dettaglio
  const li = [];
  li.push('<b>Aurora verso nord:</b> ' + (ov === null ? 'dato OVATION non disponibile' : ov + '% (OVATION, NOAA' + (st.ovAt ? ', delle ' + HHMM(st.ovAt) : '') + ')'));
  li.push('<b>Kp adesso:</b> ' + (st.kp === null ? 'non disponibile' : fmtNum(st.kp)));
  li.push('<b>Nuvole quest\'ora:</b> ' + (cloud === null ? 'non disponibili' : cloud + '%'));
  li.push('<b>Vento solare:</b> ' + (wind ? wind.label + ' (Bz ' + (st.bz > 0 ? '+' : '') + fmtNum(Math.round(st.bz)) + ' nT'
    + (st.v !== null ? ', ' + Math.round(st.v) + ' km/s' : '') + ')' : 'non disponibile'));
  li.push('<b>Luna:</b> ' + moonText(ref).replace(/^Luna /, ''));
  li.push('<b>Sole:</b> ' + (sunAlt < -12 ? 'buio' : sunAlt < 0 ? 'crepuscolo (' + Math.round(sunAlt) + '°)' : 'giorno'));
  $('am-detail-title').textContent = (me ? 'Adesso dove sei' : 'Adesso a ' + nm) + ': ' + text
    + (st.me && !me ? ' (sei fuori dall\'Islanda: stima per il posto della serata)' : '');
  $('am-detail-list').innerHTML = li.map(x => '<li>' + x + '</li>').join('');
  renderNight();
}

// ---------- stasera ora per ora: Kp previsto × nuvole della griglia, nel posto di ogni ora ----------
function renderNight() {
  const el = $('am-night');
  const { night } = auroraNowPlace();
  const start = Date.parse(night + 'T16:00:00Z'), stops = nightStops(night);
  const cells = [];
  for (let i = 0; i < 16; i++) {   // dalle 16 alle 8 del mattino
    const t = start + i * 3600000, p = AURORA_PLACES[stopAt(stops, new Date(t)).place];
    const h = st.grid ? st.grid.times.indexOf(t) : -1;
    const cloud = h >= 0 ? cloudAt(h, p.lat, p.lon) : null;
    const row = st.kpFc.find(r => t >= r.t && t < r.t + 3 * 3600000);
    let cls = 'chiaro', tip = 'troppo chiaro';
    if (sunAltitude(new Date(t + 1800000), p.lat, p.lon) < -12) {
      if (!row || cloud === null) { cls = ''; tip = 'dati non disponibili'; }
      else { cls = auroraLevel(kpFactor(row.kp) * (100 - cloud) / 100); tip = 'Kp ' + fmtNum(row.kp) + ', nuvole ' + Math.round(cloud) + '%'; }
    }
    const hh = new Date(t).getUTCHours(), isNow = Date.now() >= t && Date.now() < t + 3600000;
    cells.push('<div' + (isNow ? ' class="am-night__now"' : '') + ' title="' + String(hh).padStart(2, '0') + ':00 · ' + shortPlace(p.name) + ' · ' + tip + '">'
      + '<span class="' + (cls ? 'am-night--' + cls : '') + '"' + (cls ? '' : ' style="background:repeating-linear-gradient(45deg,var(--line) 0 3px,transparent 3px 6px)"') + '></span>'
      + (hh % 3 === 1 ? String(hh).padStart(2, '0') : '&nbsp;') + '</div>');
  }
  el.innerHTML = cells.join('');
  $('am-night-title').textContent = (Date.now() < start + 16 * 3600000 && Date.now() >= start - 4 * 3600000 ? 'Stasera' : 'Notte del ' + +night.slice(8, 10) + '/' + +night.slice(5, 7)) + ' ora per ora';
}

// ---------- cursore "Ora" (ore della previsione delle nuvole) ----------
function setupHours() {
  const input = $('am-hour'), ticks = $('am-ticks');
  const n = st.grid ? st.grid.times.length : 24;
  input.max = String(n - 1);
  ticks.innerHTML = '';
  for (let h = 0; h < n; h++) {
    const t = st.grid ? new Date(st.grid.times[h]) : null;
    const i = document.createElement('i');
    if (t && t.getUTCHours() === 0) i.className = 'long';
    ticks.appendChild(i);
  }
  // all'apertura il cursore va sull'ora attuale (la previsione salvata può partire da prima)
  if (st.grid) {
    const nowH = Date.now() - 3600000;
    const idx = st.grid.times.findIndex(t => t > nowH);
    st.hour = Math.max(0, idx);
    if (st.hour > +input.max) st.hour = +input.max;
  }
  input.value = String(st.hour);
  hourLabel();
}
function hourLabel() {
  const lbl = $('am-hour-lbl');
  if (!st.grid) { lbl.textContent = 'Ora'; return; }
  const t = new Date(st.grid.times[st.hour]);
  const isNow = Math.abs(t - Date.now()) < 3600000 && t <= Date.now();
  lbl.innerHTML = isNow ? 'Ora' : String(t.getUTCHours()).padStart(2, '0') + ':00'
    + (t.getUTCDate() !== new Date().getUTCDate() ? (t.getUTCHours() < 12 ? '<small>dopo mezzanotte</small>' : '<small>domani</small>') : '');
  $('am-legend-note').hidden = isNow;
}
$('am-hour').addEventListener('input', e => {
  st.hour = +e.target.value; hourLabel(); drawClouds(); renderClear();
});

// ---------- stato e dettaglio ----------
function setStatus(text, kind) {
  const el = $('am-status');
  if (!text) { el.hidden = true; return; }
  el.textContent = text; el.className = 'am-status am-status--' + (kind || 'info'); el.hidden = false;
}
$('am-now').addEventListener('click', () => { $('am-detail').hidden = !$('am-detail').hidden; });
$('am-detail-close').addEventListener('click', () => { $('am-detail').hidden = true; });
$('am-back').addEventListener('click', e => {
  // si torna dov'eri nell'app (stessa tab); se la pagina è stata aperta da sola, si apre l'app
  if (document.referrer && new URL(document.referrer).origin === location.origin && history.length > 1) { e.preventDefault(); history.back(); }
});

// ---------- caricamento ----------
async function loadNoaa() {
  const opt = { cache: 'no-store' };
  const get = p => fetch(NOAA + p, opt).then(r => r.json()).catch(() => null);
  const [ov, kp, mag, sp, fc] = await Promise.all([get('json/ovation_aurora_latest.json'), get('json/planetary_k_index_1m.json'),
    get('products/summary/solar-wind-mag-field.json'), get('products/summary/solar-wind-speed.json'),
    get('products/noaa-planetary-k-index-forecast.json')]);
  if (Array.isArray(fc)) {   // righe [time_tag, kp, …] con intestazione, oppure oggetti
    const rows = Array.isArray(fc[0]) ? fc.slice(1).map(r => ({ t: r[0], kp: r[1] })) : fc.map(o => ({ t: o.time_tag, kp: o.kp }));
    st.kpFc = rows.map(r => ({ t: Date.parse(String(r.t).replace(' ', 'T') + (/Z$/.test(r.t) ? '' : 'Z')), kp: num(r.kp) }))
      .filter(r => isFinite(r.t) && r.kp !== null);
  }
  // offline il service worker restituisce l'ultima copia: i dati vecchi si scartano
  const ovT = ov && NOAA_AGE(ov['Observation Time'], 60);
  const okCoords = ov && Array.isArray(ov.coordinates) && ov.coordinates.filter(c => Array.isArray(c) && c.length === 3).length > 1000;
  if (ovT && okCoords) { st.ov = ovGrid(ov.coordinates); st.ovCoords = ov.coordinates; st.ovAt = ovT; }
  else if (okCoords) { st.ovOld = Date.parse(ov['Observation Time']); }
  const last = Array.isArray(kp) && kp[kp.length - 1];
  if (last && NOAA_AGE(last.time_tag, 30) && num(last.kp_index) !== null) st.kp = Math.round(num(last.kp_index) * 10) / 10;
  const m = Array.isArray(mag) && mag[0], w = Array.isArray(sp) && sp[0];
  if (m && NOAA_AGE(m.time_tag, 30)) st.bz = num(m.bz_gsm);
  if (w && NOAA_AGE(w.time_tag, 30)) st.v = num(w.proton_speed);
}
async function start() {
  const tn = AURORA_PLACES[tonightKey()];
  $('am-tonight-name').textContent = 'Stasera: ' + shortPlace(tn.name);
  drawPlaces(); drawSpots();
  if (!start.done) {   // all'apertura: tutti i posti delle serate (Reykjavík, Laugarvatn, Flúðir, Vík)
    const pts = Object.keys(AURORA_PLACES).filter(k => placeNights(k).length).map(k => [AURORA_PLACES[k].lat, AURORA_PLACES[k].lon]);
    if (pts.length) map.fitBounds(pts, { paddingTopLeft: [80, 90], paddingBottomRight: [30, 230], maxZoom: 8 });
    start.done = true;
  }
  setStatus(navigator.onLine ? 'Carico aurora e nuvole…' : 'Offline: uso gli ultimi dati salvati', navigator.onLine ? 'loading' : 'offline');
  await Promise.all([loadNoaa(), loadClouds()]);
  setupHours();
  drawClouds(); drawAurora(); renderNow(); renderClear();
  const problems = [];
  if (!st.ovAt) problems.push(st.ovOld ? 'aurora: dato vecchio delle ' + HHMM(st.ovOld) : 'aurora non disponibile');
  if (st.cloudErr) problems.push(st.cloudErr);
  else if (st.grid && Date.now() - st.grid.at > CLOUD_MAX_AGE) problems.push('nuvole delle ' + HHMM(st.grid.at));
  if (!navigator.onLine) setStatus('Offline' + (problems.length ? ' · ' + problems.join(' · ') : ''), 'offline');
  else if (problems.length) setStatus(problems.join(' · '), 'error');
  else setStatus(null);
}
start();
window.addEventListener('online', () => start());
