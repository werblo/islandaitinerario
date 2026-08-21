# Islanda 2026 — webapp del viaggio

## 1. Aggiungere le foto

Nella cartella `images/` metti i file **con questi nomi esatti** (formato .jpg,
va bene anche una foto già scattata col telefono). L'app li mostra da sola
appena li trova — non serve toccare il codice.

```
cover.jpg                              → copertina (aurora o paesaggio a piacere)

d1-hero.jpg                            → Arrivo & Reykjavík
d1-passeggiata-nel-centro.jpg          → Passeggiata nel centro

d2-hero.jpg                            → Cerchio d'Oro
d2-thingvellir-national-park.jpg       → Þingvellir
d2-geysir-strokkur.jpg                 → Geysir & Strokkur
d2-gullfoss.jpg                        → Gullfoss
d2-sky-lagoon.jpg                      → Sky Lagoon

d3-hero.jpg                            → Reykjavík: cultura e relax
d3-perlan.jpg                          → Perlan
d3-harpa-porto-vecchio.jpg             → Harpa & porto vecchio
d3-national-museum-of-iceland.jpg      → National Museum
d3-reykjanes.jpg                       → Reykjanes

d4-hero.jpg                            → Costa Sud
d4-seljalandsfoss.jpg                  → Seljalandsfoss
d4-skogafoss.jpg                       → Skógafoss
d4-reynisfjara.jpg                     → Reynisfjara
d4-dyrholaey.jpg                       → Dyrhólaey

d5-hero.jpg                            → Escursione a Jökulsárlón
d5-fjadrargljufur.jpg                  → Fjaðrárgljúfur
d5-jokulsarlon-glacier-lagoon.jpg      → Jökulsárlón
d5-diamond-beach.jpg                   → Diamond Beach

d6-hero.jpg                            → Vík → Flúðir
d6-kerid.jpg                           → Kerið
d6-secret-lagoon.jpg                   → Secret Lagoon

d7-hero.jpg                            → Sorgenti calde
d7-reykjadalur-hot-spring-river.jpg    → Reykjadalur
d7-faxi.jpg                            → Faxi
d7-passeggiata-a-fludir.jpg            → Passeggiata a Flúðir

d8-hero.jpg                            → Rientro

storia-hero.jpg                        → Tab "Storia" (Alþingi, saghe, paesaggio storico a piacere)
```

Finché una foto non c'è, al suo posto compare un placeholder con l'icona e il
nome del posto — non si rompe niente, l'app resta usabile.

Se preferisci, mandami le foto in chat mano a mano che le hai e te le
incorporo/rinomino io.

## 2. Metterla online (per poterla installare sul telefono)

L'app è pensata per essere ospitata su un hosting statico gratuito — serve
per far funzionare l'installazione "vera" con icona in home e cache offline.
Il modo più semplice, senza scrivere codice:

1. Vai su **https://app.netlify.com/drop**
2. Trascina dentro l'intera cartella di questo progetto (quella con
   `index.html`, `manifest.json`, `sw.js`, `icons/`, `images/`)
3. In pochi secondi ottieni un link tipo `https://nome-a-caso.netlify.app`

Poi da telefono:
- **Android (Chrome):** apri il link → menu ⋮ → "Aggiungi a schermata Home"
  / "Installa app"
- **iPhone (Safari):** apri il link → icona Condividi → "Aggiungi a Home"

Da quel momento l'icona sarà sulla home come un'app vera, e dopo la prima
apertura online funzionerà anche offline (mappe escluse, che richiedono
sempre connessione).

Se preferite un nome fisso invece del link casuale di Netlify, potete
creare un account gratuito su Netlify e assegnare un sottodominio a piacere
dalle impostazioni del sito — non è obbligatorio, il link temporaneo
funziona lo stesso.

## 3. Aggiornare i contenuti in futuro

Tutto il testo dell'itinerario è dentro `render.py`. Se cambia qualcosa
(orari, tappe, alloggi), basta modificare i dati lì e rilanciare
`python3 render.py` per rigenerare `index.html` — molto più leggero che
editare l'export di Claude Design.
