# Islanda 2026 — webapp del viaggio

## 1. Aggiungere le foto

Nella cartella `images/` metti i file **con questi nomi esatti** (formato .jpg,
va bene anche una foto già scattata col telefono). L'app li mostra da sola
appena li trova — non serve toccare il codice.

```
cover.jpg                                   → copertina (aurora o paesaggio a piacere)

d1-hero.jpg                                 → Arrivo & Reykjavík
d1-passeggiata-nel-centro.jpg               → Passeggiata nel centro

d2-hero.jpg                                 → Reykjavík: cultura e Reykjanes
d2-perlan.jpg                               → Perlan
d2-harpa-porto-vecchio.jpg                  → Harpa & porto vecchio
d2-national-museum-of-iceland.jpg           → National Museum
d2-reykjanes.jpg                            → Reykjanes

d3-hero.jpg                                 → Þingvellir & relax serale
d3-thingvellir-national-park.jpg            → Þingvellir
d3-fontana-geothermal-baths.jpg             → Fontana Geothermal Baths

d4-hero.jpg                                 → Costa Sud
d4-seljalandsfoss.jpg                       → Seljalandsfoss
d4-skogafoss.jpg                            → Skógafoss
d4-reynisfjara.jpg                          → Reynisfjara
d4-dyrholaey.jpg                            → Dyrhólaey
d4-vikurkirkja.jpg                          → Víkurkirkja

d5-hero.jpg                                 → Escursione a Jökulsárlón
d5-fjadrargljufur.jpg                       → Fjaðrárgljúfur
d5-jokulsarlon-glacier-lagoon.jpg           → Jökulsárlón
d5-diamond-beach.jpg                        → Diamond Beach

d6-hero.jpg                                 → Vík → Flúðir
d6-kerid.jpg                                → Kerið
d6-secret-lagoon.jpg                        → Secret Lagoon

d7-hero.jpg                                 → Geysir & Gullfoss e sorgenti calde
d7-geysir-strokkur.jpg                      → Geysir & Strokkur
d7-gullfoss.jpg                             → Gullfoss
d7-faxi.jpg                                 → Faxi
d7-efstidalur-ii.jpg                        → Efstidalur II

d8-hero.jpg                                 → Rientro

storia-hero.jpg                             → Tab "Storia" (Alþingi, saghe, paesaggio storico a piacere)
```

Finché una foto non c'è, al suo posto compare un placeholder con un'icona
illustrata e il nome del posto — non si rompe niente, l'app resta usabile.
I nomi file corrispondono al giorno/attività attuale dell'itinerario: se
cambi l'ordine o il testo di un'attività in `render.py`, il nome atteso
cambia di conseguenza (segue il titolo, in minuscolo e senza accenti).

Se preferisci, mandami le foto in chat mano a mano che le hai e te le
incorporo/rinomino io.

Le foto restano .jpg come le metti tu: `render.py` le converte da solo in
formato più leggero per il sito (vedi sezione 11).

## 2. Come funziona online (GitHub Pages)

Il sito è pubblicato su **GitHub Pages** dal branch `main` di questo
repository: ogni volta che `index.html` viene aggiornato su `main`, il sito
pubblico si aggiorna da solo in pochi minuti, senza bisogno di caricare
manualmente file da nessuna parte.

Flusso di lavoro per qualunque modifica:

1. Si modifica `render.py` (i dati/testi dell'itinerario) e/o le foto in
   `images/`.
2. Si rilancia `python3 render.py` per rigenerare `index.html`.
3. Si apre una pull request verso `main` e la si fa mergiare.
4. GitHub Pages ripubblica automaticamente il sito aggiornato.

Da telefono, una volta pubblicato il sito:
- **Android (Chrome):** apri il link → menu ⋮ → "Aggiungi a schermata Home"
  / "Installa app"
- **iPhone (Safari):** apri il link → icona Condividi → "Aggiungi a Home"

Da quel momento l'icona sarà sulla home come un'app vera, e dopo la prima
apertura online funzionerà anche offline: foto, percorsi, alba/tramonto
sempre; le mappe lungo tutto il tragitto dopo aver premuto "Prepara
offline" nella tab Info (vedi sezione 11); meteo, aurora e cambio valuta
mostrano l'ultimo dato salvato.

## 3. Aggiornare i contenuti in futuro

Tutto il testo dell'itinerario (giorni, attività, box "Storia & curiosità",
alloggi, checklist, tab Storia) è dentro `render.py`. Se cambia qualcosa
(orari, tappe, alloggi), basta modificare i dati lì e rilanciare
`python3 render.py` per rigenerare `index.html` — molto più leggero che
editare l'export di Claude Design.

## 4. Controllo di coerenza (distanze, orari, luce)

L'itinerario contiene dati che vanno tenuti sincronizzati manualmente quando
si spostano o si riordinano le tappe: km/tempi di guida in `legs`, orari
delle `activities` rispetto ad alba/tramonto reali, e l'ordine di
`map_points` (deve rispecchiare l'ordine reale di visita, altrimenti la
mappa disegna un percorso sbagliato).

Un controllo di questo tipo è stato fatto una volta a fondo (fine agosto
2026) e ha trovato/corretto diversi errori: distanze sbagliate rispetto al
reale (es. Kerið→Flúðir dichiarato più corto della sola linea d'aria,
quindi impossibile), attività programmate prima dell'alba o dopo il
tramonto reale (calcolato per le coordinate esatte, non per le città
capoluogo), e un `map_points` rimasto disallineato dopo un riordino delle
attività.

È programmato un ricontrollo automatico una settimana prima della
partenza (8 novembre 2026, promemoria anche su calendario) per rifare la
stessa verifica nel caso qualcosa cambi nei mesi prima del viaggio. Se
si sposta o si inverte una tappa manualmente, vale la pena rifare almeno
il controllo su `legs`/`map_points` di quel giorno.

Dopo ogni modifica confermata come funzionante, si aggiorna anche la
cartella `backup-pre-storia/` con la stessa copia di `render.py`,
`index.html`, `sw.js` e `leggimi.md`: serve come punto di ripristino noto
se una modifica successiva rompe qualcosa.

## 5. Prenotazioni

Entrambe le soste terme in programma (Fontana al Giorno 3, Secret Lagoon al
Giorno 6) sono prenotate. I voucher **non** stanno in questo repository,
che è pubblico: sono conservati solo fuori da GitHub (telefono/Drive).
Non aggiungere mai al repo voucher, conferme di prenotazione o altri
documenti con dati personali: tutto ciò che viene committato qui è
leggibile da chiunque.

Durante la prenotazione sono emerse due correzioni ai dati in `render.py`,
poi applicate: l'orario della Secret Lagoon (19:00 → 17:30, il sito non
offriva slot più tardi) e il prezzo (4500 ISK/persona).

## 6. Mappe e fix mobile (settembre 2026)

Le mappe (ogni giorno + "Mappa del viaggio" nella tab Info) usano Leaflet
con tile OpenStreetMap standard, gratuiti e senza chiave di accesso — un
primo tentativo con CARTO Voyager è stato scartato perché quell'endpoint
richiede ora una API key, mostrando "API key required" al posto della
mappa.

Un audit mirato all'uso su telefono ha trovato e corretto due bug:
- le mappe avevano il drag/pan sempre attivo, quindi uno swipe verticale
  che partiva sulla mappa la spostava invece di scrollare la pagina;
  ora dragging e zoom si riattivano solo al primo tocco intenzionale
  sulla mappa;
- i pulsanti di navigazione dei giorni e le checkbox della checklist
  avevano un'area toccabile sotto i 44px consigliati per il tocco su
  telefono — alzati entrambi.

Ogni mappa vive nel proprio contesto di stacking (`isolation:isolate`)
apposta per evitare che i controlli interni di Leaflet finiscano sopra
il menu dei giorni durante lo scroll (bug corretto in precedenza).

## 7. Giorno 7: Passeggiata a Flúðir sostituita con Efstidalur II

La vecchia attività "Passeggiata a Flúðir" (15:30) è stata sostituita con
**Efstidalur II**, fattoria con gelateria e vacche visibili da dietro un
vetro (~9 km da Faxi, ~20 km da Efstidalur a Flúðir — corretto da un
refuso nelle coordinate di Faxi, vedi sezione 8).

Motivo: un controllo ha confermato che il centro di Flúðir offre poco
oltre alla Secret Lagoon (già coperta al Giorno 6) — niente borgo
pittoresco, solo una collina panoramica (Miðfell) e un fiume. Efstidalur
è aperta tutto l'anno ed è una sosta calda/comoda per il pomeriggio buio
di novembre. Scartata anche l'idea di un sito vichingo (Þjóðveldisbærinn
Stöng, a ~45 min): chiuso da ottobre a maggio, non visitabile a novembre.

Nota a margine: esiste anche **Laugarás Lagoon**, una laguna termale
moderna a due livelli aperta da ottobre 2025 vicino a Skálholt — più
scenografica della Secret Lagoon ma quasi il triplo del prezzo (da 6900
ISK contro 4500 ISK). Non inserita nell'itinerario perché la Secret
Lagoon è già prenotata e pagata; resta un'opzione da considerare per un
eventuale viaggio futuro.

## 8. Correzioni distanze e funzionalità aggiunte (settembre 2026)

Un debug incrociato con più controlli indipendenti (haversine + verifica
web) ha trovato due errori reali:

- **Coordinate di Faxi sbagliate** in `map_points['d7']` da tempo
  (puntavano vicino a Flúðir invece che al vero Faxi vicino a Reykholt).
  Questo aveva reso "impossibile" per errore la distanza Gullfoss→Faxi
  (in realtà corretta, 21 km) e sballata la tappa Faxi→Efstidalur II
  (28 km/25 min errati, corretto a 9 km/12 min con le coordinate giuste).
- **Jökulsárlón→Fjaðrárgljúfur davvero impossibile**: dichiarata 100 km
  ma con un pavimento a linea d'aria di 100.9 km. Corretta a 130 km/~1h50
  (verificato via Kirkjubæjarklaustur come riferimento), con l'attività
  Fjaðrárgljúfur del Giorno 5 spostata da 14:30 a 15:00 e il totale
  km/giorno aggiornato nei tips (~370 → ~395 km).

Corretta anche un'incoerenza testuale: l'energia rinnovabile islandese
era indicata come "quasi 100%" (Giorno 8) e "85%" (tab Storia) senza
spiegare la differenza — ora è chiaro che il 100% riguarda la sola
elettricità, l'85% il consumo energetico totale (riscaldamento,
industria, trasporti inclusi).

**Nuove funzionalità:**
- L'app salta automaticamente alla tab del giorno corrente se aperta
  tra il 15 e il 22 novembre 2026 (testato con Chromium/Playwright
  simulando diverse date).
- Ogni attività con una tappa reale ha un link **"Naviga"** che apre
  Google Maps (22 attività su 8 giorni, incluso il ritiro/riconsegna
  auto FairCar). Usa una **ricerca testuale** (es. "Skógafoss parking",
  "Laugarvatn Fontana") invece di coordinate fisse: Google Maps trova
  da solo il pin più preciso su parcheggio/struttura reale, verificato
  via web search per ognuna delle 22 query.
- Un pulsante flottante (FAB) per il cambio Euro/Corona è visibile su
  tutte le tab tranne Info (dove il convertitore è già un pannello),
  con un link rapido a road.is per lo stato delle strade.
- Rune vichinghe decorative (Futhark) nella sola tab Storia, e un
  paragrafo su Hrafna-Flóki Vilgerðarson, il navigatore che diede il
  nome "Ísland" all'isola prima della colonizzazione di Ingólfur
  Arnarson.

## 9. Parcheggi

Ogni giorno con un pernottamento (Giorni 1-7) ha una sezione parcheggio
sotto "Alloggio", con link "Naviga" diretti:

- **Reykjavík (Giorni 1-3)**: l'appartamento 46heima non ha parcheggio
  incluso ed è in zona P1 (~650 ISK/h, max 3h consecutive, gratis
  21:00-9:00 nei feriali/sabato e prima delle 10:00/dopo le 21:00 la
  domenica — orari da riconfermare su reykjavik.is/en/parking vicino
  alla partenza). Strategia notte per notte: zona P2 verso
  Hlemmur/Rauðarárstígur (~230 ISK/h, senza limite di 3h) il 15 e 16
  novembre; P1 direttamente sotto casa il 17, perché quella sera si
  rientra da Fontana dopo le 21:00 (già gratis anche lì).
- **Hotel Burfell (Giorni 4-5)** e **The Hill Guesthouse (Giorni 6-7)**:
  parcheggio gratuito incluso, confermato via web search.
- La maggior parte delle tappe turistiche lungo il percorso (Þingvellir,
  Seljalandsfoss, Skógafoss, Dyrhólaey, Reynisfjara, Jökulsárlón/Diamond
  Beach, Fjaðrárgljúfur, Geysir) ha un parcheggio a pagamento a sé
  (500-1000 ISK circa, spesso tramite l'app Parka con lettura targa) —
  si paga sempre con carta, l'Islanda è quasi cashless anche ai
  distributori dei parcheggi.

## 10. Struttura delle tab

- **Info** — countdown, aurora boreale in tempo reale, mappa del viaggio,
  cambio EUR/ISK, riepilogo volo/auto, budget, sicurezza, alloggi, numeri
  utili.
- **Giorno 1–8** — un tab per ogni giornata: attività, spostamenti, mappa
  del percorso, box "Storia & curiosità", pasti, alloggio.
- **Storia** — panoramica generale sulla storia islandese (colonizzazione,
  Alþingi, lingua, folklore, geologia).
- **Checklist** — documenti, abbigliamento, tecnologia, con caselle
  spuntabili salvate sul telefono (localStorage) e contatore di
  avanzamento.

## 11. Aggiornamento settembre 2026 (23/09)

### Dati sensibili rimossi
I voucher che stavano in `segreto/` sono stati tolti dal repository e da
tutta la cronologia git (riscritta con `git filter-repo`; nei commit
l'email personale è stata sostituita con l'indirizzo "noreply" di GitHub).
Una copia completa del repository com'era prima, voucher inclusi, è
conservata solo in locale (backup scaricato il 23/09). Il repository è
pubblico: non aggiungere mai file con dati personali.

### Offline completo
- **Tutto in cache all'installazione**: pagina, Leaflet (ora nel repo in
  `vendor/leaflet/`, non più da unpkg) e tutte le foto usate.
- **Versione automatica**: `render.py` calcola un'impronta (hash) di
  pagina, foto, percorsi e file statici e la scrive in `sw.js` (generato
  da `sw-template.js`: **non modificare `sw.js` a mano**). Ogni modifica
  pubblicata cambia l'impronta e i telefoni scaricano la nuova versione da
  soli.
- **Aggiornamento senza interruzioni**: con internet la nuova versione si
  scarica in background e si applica alla riapertura dell'app (o quando
  la metti in background), con un avviso discreto "Contenuti aggiornati".
  Una foto sostituita con lo stesso nome si aggiorna comunque.
- **Alba/tramonto** calcolati in locale (algoritmo NOAA), niente più
  chiamate a sunrise-sunset.org. Correzione emersa: i vecchi valori di
  riserva del Giorno 6 e del Giorno 8 erano calcolati per Vík e Flúðir
  invece che per Flúðir e Keflavík.
- **Pulsante "Prepara offline"** (tab Info): salva foto e circa un migliaio di riquadri
  di mappa (~15 MB) lungo un corridoio stretto attorno al percorso, zoom
  6-12, massimo 2 download alla volta (tile usage policy OSM). Da fare
  con il Wi-Fi prima di partire, su entrambi i telefoni. Ingrandendo oltre
  lo zoom 12 senza rete la mappa resta grigia.
- **Spazio**: il pacchetto totale resta sotto i 30 MB, ben dentro i limiti
  di Android (Chrome) e iPhone (Safari). Su iPhone i dati offline restano
  al sicuro se l'app è **aggiunta alla schermata Home**; da Safari normale
  iOS può cancellarli dopo alcune settimane di non utilizzo.

### Immagini
Le foto in `images/` restano .jpg (quelle che metti tu, sezione 1): a ogni
`python3 render.py` vengono convertite in automatico in **WebP**, dentro
`images/web/`, ridotte a un massimo di 1200px sul lato lungo e con
l'orientamento corretto (le foto da telefono a volte sono ruotate solo nei
metadati). Il sito carica sempre i .webp: più leggeri, stesso aspetto.
Se una foto non cambia, non viene riconvertita (viene tenuto un piccolo
elenco di controllo in `images/web/manifest.json`): questo rende il sito
riproducibile, oltre a essere più veloce. Se il .jpg manca, resta il
placeholder come prima.

Le foto scattate ma non usate nell'itinerario (per esempio quando
un'attività è stata sostituita) sono spostate in `images/archivio/`: restano
nel repository come ricordo/scorta, ma non vengono convertite né incluse nel
sito o nell'offline.

### Percorsi mappa precalcolati
Il percorso stradale di ogni giorno non si calcola più al momento
(server demo OSRM), ma una volta sola e resta dentro la pagina, così
funziona offline. Si aggiorna dalla tab **Actions** di GitHub →
**"Aggiorna percorsi mappa"** → **Run workflow**: l'azione scarica i
percorsi (`tools/fetch_routes.py` → `routes.json`), rigenera `index.html` e
pubblica. **Va rilanciata ogni volta che cambiano le tappe** in
`map_points`: finché non lo fai, il giorno modificato torna al calcolo
online (con la linea tratteggiata di riserva se sei offline).
