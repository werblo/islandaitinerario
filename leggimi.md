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
d3-sosta-relax-a-laugarvatn.jpg             → Sosta serale a Laugarvatn

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
d7-passeggiata-a-fludir.jpg                 → Passeggiata a Flúðir

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
apertura online funzionerà anche offline (le mappe restano visibili solo
per le zone già caricate mentre eri online; il resto — meteo, aurora,
cambio valuta — mostra l'ultimo dato salvato).

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

## 4. Struttura delle tab

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
