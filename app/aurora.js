// Logica comune dell'aurora, inserita da render.py sia nell'app (index.html) sia nella
// Mappa aurora (mappa-aurora.html): sole, posti delle serate, nuvole efficaci e stima "Adesso".
// Le stesse regole stanno in tools/aurora_alert.py: se si cambiano qui, vanno cambiate anche lì.
// Usa le costanti incorporate da render.py: DAYS_META, AURORA_PLACES, NIGHT_STOPS, CLOUD_*.

// Parametri solari (algoritmo NOAA) per un giorno giuliano: declinazione ed equazione del tempo.
function solarParams(jd) {
  const rad = Math.PI / 180;
  const T = (jd - 2451545) / 36525;
  const L0 = (280.46646 + T * (36000.76983 + T * 0.0003032)) % 360;
  const Ma = 357.52911 + T * (35999.05029 - 0.0001537 * T);
  const ecc = 0.016708634 - T * (0.000042037 + 0.0000001267 * T);
  const C = Math.sin(Ma * rad) * (1.914602 - T * (0.004817 + 0.000014 * T))
          + Math.sin(2 * Ma * rad) * (0.019993 - 0.000101 * T) + Math.sin(3 * Ma * rad) * 0.000289;
  const omega = 125.04 - 1934.136 * T;
  const lambda = L0 + C - 0.00569 - 0.00478 * Math.sin(omega * rad);
  const eps = 23 + (26 + (21.448 - T * (46.815 + T * (0.00059 - T * 0.001813))) / 60) / 60 + 0.00256 * Math.cos(omega * rad);
  const decl = Math.asin(Math.sin(eps * rad) * Math.sin(lambda * rad)) / rad;
  const y = Math.tan(eps * rad / 2) ** 2;
  const eqTime = 4 / rad * (y * Math.sin(2 * L0 * rad) - 2 * ecc * Math.sin(Ma * rad)
    + 4 * ecc * y * Math.sin(Ma * rad) * Math.cos(2 * L0 * rad)
    - 0.5 * y * y * Math.sin(4 * L0 * rad) - 1.25 * ecc * ecc * Math.sin(2 * Ma * rad));
  return { decl, eqTime };
}

// Altezza del sole sull'orizzonte (gradi) in un istante: sotto -18° è buio astronomico.
function sunAltitude(date, lat, lon) {
  const rad = Math.PI / 180;
  const { decl, eqTime } = solarParams(date.getTime() / 86400000 + 2440587.5);
  const minutes = date.getUTCHours() * 60 + date.getUTCMinutes();
  const ha = ((minutes + eqTime + 4 * lon + 1440) % 1440) / 4 - 180;
  const cosZ = Math.sin(lat * rad) * Math.sin(decl * rad) + Math.cos(lat * rad) * Math.cos(decl * rad) * Math.cos(ha * rad);
  return 90 - Math.acos(Math.max(-1, Math.min(1, cosZ))) / rad;
}

function auroraNowPlace() {
  const now = new Date();
  // fino a mezzogiorno vale la notte appena passata (come lo script degli avvisi): all'alba si è
  // ancora dove si è dormito, non nell'alloggio della sera dopo
  const start = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), 12) - (now.getUTCHours() < 12 ? 86400000 : 0);
  const night = new Date(start).toISOString().slice(0, 10);
  const place = stopAt(nightStops(night), now).place;
  return { place, loc: AURORA_PLACES[place], night };
}

const NOAA_AGE = (t, maxMin) => {   // orario NOAA (UTC) non più vecchio di maxMin minuti
  const ms = Date.parse(String(t || '').replace(' ', 'T') + (/Z|[+-]\d\d:?\d\d$/.test(String(t)) ? '' : 'Z'));
  return isFinite(ms) && Date.now() - ms <= maxMin * 60000 ? ms : null;
};
const num = v => (v != null && v !== '' && isFinite(v) ? Number(v) : null);

// OVATION sulla stessa scala di kpFactor (ricerca Kp: sopra il 30% c'era attività quasi sempre)
function ovationFactor(p) {
  if (p >= 30) return 0.85;
  if (p >= 20) return 0.65;
  if (p >= 10) return 0.4;
  return 0.15;
}

// Dove si dorme la notte che inizia in una certa data: durante il viaggio l'alloggio
// di quel giorno, prima e dopo Reykjavík (dati reali, non un esempio).
function nightPlaceKey(dateISO) {
  const day = DAYS_META.find(d => d.dateISO === dateISO && d.id !== 'd8');
  return day ? day.locKey : 'reykjavik';
}

function kpFactor(kp) {
  // alle latitudini islandesi l'aurora si vede spesso già con Kp 2-3
  if (kp >= 5) return 1;
  if (kp >= 4) return 0.85;
  if (kp >= 3) return 0.65;
  if (kp >= 2) return 0.4;
  return 0.15;
}

// Tappe della sera (vedi evening_stops in dati.py): di default l'alloggio della notte.
function nightStops(dateISO) {
  return NIGHT_STOPS[dateISO] || [{ place: nightPlaceKey(dateISO) }];
}
// Tappa in cui si è all'ora t ('until' = ora islandese di fine tappa, contata dalle 12).
function stopAt(stops, t) {
  const off = (t.getUTCHours() + 12) % 24;
  return stops.find(s => s.until === undefined || off < (s.until + 12) % 24) || stops[stops.length - 1];
}

// Nuvole "efficaci" per l'aurora in un'ora secondo CLOUD_METHOD (vedi dati.py):
// gli strati alti e medi pesano meno perché le nuvole alte sottili lasciano vedere.
function layeredCloud(c, idx, sfx) {
  const l = (c['cloud_cover_low' + sfx] || [])[idx], m = (c['cloud_cover_mid' + sfx] || [])[idx], h = (c['cloud_cover_high' + sfx] || [])[idx];
  if (l == null || m == null || h == null) return null;
  return 100 * (1 - (1 - l / 100) * (1 - CLOUD_W_MID * m / 100) * (1 - CLOUD_W_HIGH * h / 100));
}
function effCloud(c, idx) {
  if (CLOUD_METHOD.startsWith('media')) {
    const vals = CLOUD_MODELS.map(m => CLOUD_METHOD === 'media'
      ? (c['cloud_cover_' + m] || [])[idx] : layeredCloud(c, idx, '_' + m)).filter(v => v != null);
    if (vals.length >= 3) return Math.round(vals.reduce((a, b) => a + b, 0) / vals.length);
  } else if (CLOUD_METHOD === 'pesata') {
    const v = layeredCloud(c, idx, '');
    if (v != null) return Math.round(v);
  }
  return c.cloud_cover ? c.cloud_cover[idx] : null;
}

function auroraLevel(best) {
  return best >= 0.45 ? 'buone' : best >= 0.2 ? 'scarse' : 'nulle';
}

const shortPlace = name => name.replace(/ \(.*\)$/, '');

// Probabilità OVATION "verso nord" per un posto: massimo tra la sua latitudine e 70°N alla stessa
// longitudine (±2°), scartando voci malformate. null se non c'è nessun valore utile.
function ovationNorth(coords, loc) {
  if (!Array.isArray(coords) || !loc) return null;
  const lon0 = ((Math.round(loc.lon) % 360) + 360) % 360;
  let p = null;
  coords.forEach(c => {
    if (!Array.isArray(c) || c.length !== 3 || !c.every(x => typeof x === 'number' && isFinite(x))) return;
    const [lon, lat, v] = c;
    if (Math.abs(((lon - lon0 + 540) % 360) - 180) <= 2 && lat >= loc.lat && lat <= 70) p = Math.max(p || 0, v);
  });
  return p;
}

// Vento solare dell'ultimo minuto: soglie come l'avviso "arrivo" (che però guarda la media di 15-20 minuti)
function windState(bz, v) {
  if (bz === null) return null;
  const fav = (bz <= -7 && v !== null && v >= 500) || bz <= -10;
  return { fav, label: fav ? 'favorevole' : bz <= -3 ? 'un po\' favorevole' : 'nella norma' };
}

// "Si vede adesso?": attività (la migliore tra Kp attuale e OVATION) × cielo sereno di quest'ora,
// con la variante "cielo variabile" per l'attività forte (come l'avviso "adesso").
// o = { ov, kp, cloud, sunAlt, wind }: valori null se mancano. Restituisce { level, text }.
function auroraNowVerdict(o) {
  const acts = [];
  if (o.ov !== null) acts.push(ovationFactor(o.ov));
  if (o.kp !== null) acts.push(kpFactor(o.kp));
  let level = null, text;
  if (o.sunAlt >= -12) {
    text = 'troppo chiaro per vederla';
  } else if (!acts.length) {
    text = 'dati sull\'attività non disponibili';
  } else {
    const act = Math.max(...acts);
    if (o.cloud === null) {
      level = act >= 0.65 ? 'scarse' : 'nulle';
      text = act >= 0.65 ? 'attività buona: se il cielo è sereno, uscite a guardare' : 'attività bassa';
    } else {
      level = auroraLevel(act * (100 - o.cloud) / 100);
      const variable = level !== 'buone' && act >= 0.85 && o.cloud < 80;
      if (variable) level = 'scarse';
      text = level === 'buone' ? 'buone probabilità di vederla: uscite e guardate verso nord!'
        : variable ? 'attività forte, cielo variabile: guardate fuori nelle schiarite'
        : level === 'scarse' ? 'forse: vale la pena dare un\'occhiata fuori'
        : act >= 0.65 ? 'c\'è attività, ma il cielo è troppo coperto' : 'difficile vederla';
    }
    if (o.wind && o.wind.fav && level !== 'buone') text += '; il vento solare è favorevole, può accendersi entro un\'ora';
  }
  return { level, text };
}
