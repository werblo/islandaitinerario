# Islanda 2026 — promemoria per Claude

App (PWA) del viaggio in Islanda di Michele e Federica, 15–22 novembre 2026.
Sito: https://werblo.github.io/islandaitinerario (GitHub Pages da `main`),
installato con Firefox su due telefoni Android. Documentazione completa per
l'utente: `leggimi.md` (lunga: leggi solo la sezione che serve).

## Regole
- Rispondi sempre in **italiano**, in modo semplice (Michele non è uno sviluppatore).
- Consuma pochi token: niente sottoagenti se Michele non li chiede, leggi solo
  le parti dei file che servono (Grep + Read con offset), niente screenshot
  superflui.
- Non cambiare decisioni sull'itinerario senza chiedere. In particolare:
  Fontana (Giorno 3, ore 15:30) è **prenotata**, quindi non proporre mai di
  scambiare il Giorno 2 con il Giorno 3; la foto della Secret Lagoon va bene così.
- `CLOUD_METHOD` (in `dati.py`) si cambia solo dopo conferma esplicita di Michele.
- Il badge senza glutine (`'gf': True`) solo per locali con opzioni senza
  glutine verificate (il celiaco è Michele).
- Mai mettere segreti nel repo (la chiave privata VAPID sta solo nei secret).

## File
- `dati.py` — tutti i dati e testi del viaggio: giorni, attività, pasti,
  tratte, `map_points`, checklist, tappe serali (`evening_stops`),
  configurazione nuvole e chiave pubblica VAPID. **Quasi tutte le modifiche
  sono qui.**
- `render.py` — genera la pagina: HTML dei giorni, tab Storia, Info,
  checklist. Inserisce `app/stile.css` e `app/app.js` così come sono.
- `app/stile.css`, `app/app.js` — aspetto e logica della pagina (meteo,
  alba/tramonto, stima aurora, mappe Leaflet, offline, notifiche).
- Generati, da committare sempre: `index.html`, `sw.js` (da
  `sw-template.js`), `images/web/*.webp` (dalle foto in `images/`).
- `routes.json` — percorsi OSRM, aggiornati dal workflow "Aggiorna percorsi mappa".
- `tools/aurora_alert.py` — notifiche push (legge i dati da `index.html`);
  la sua stima deve restare identica a quella di `app/app.js`.
- `tools/research/` + workflow `ricerca-nuvole.yml` — ricerca di ottobre sul
  metodo delle nuvole; dopo la scelta del 1° novembre si possono cancellare.

## Come si lavora
1. `pip install Pillow` (e `pywebpush` solo per provare gli avvisi).
2. Modifica, poi `python3 render.py`. I testi in `dati.py` sono stringhe
   Python: attenzione agli apostrofi nelle stringhe tra `'...'` (`\'`).
3. Verifica: `render.py` senza errori, `node --check` sul JS se tocchi
   `app/app.js`, controllo in Chromium/Playwright (già installato, non fare
   `playwright install`) se tocchi l'aspetto o il JS.
4. Branch della sessione → PR verso `main` → merge squash dopo la verifica
   (Michele è d'accordo), poi attendi il deploy di Pages e avvisalo di
   chiudere e riaprire l'app.

## Workflow GitHub (orari UTC = ora islandese)
- `avvisi-aurora.yml`: mattino 7:15 dal 15 al 21/11, controlli ogni 30 min di
  notte, prova automatica il 13/11 alle 18:07. La riga `AURORA_MODE` confronta
  il testo esatto dei cron: se cambi un cron, cambia anche lì.
  Secret: `VAPID_PRIVATE_KEY`, `AURORA_SUBSCRIPTIONS` (righe "Nome: {json}").
- `ricerca-nuvole.yml`: ottobre 2026, risultato finale 1/11.
- `aggiorna-percorsi.yml`: manuale, ricalcola percorsi e km con OSRM.
- Il proxy della sessione non permette di cancellare branch: chiedilo a Michele.
