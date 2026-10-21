# Islanda 2026 · webapp del viaggio

App del viaggio di Michele e Federica in Islanda, 15-22 novembre 2026.
Questo file descrive **com'è il progetto oggi**. La storia delle modifiche
(cosa è cambiato, quando e perché) è su GitHub: tab **Pull requests** →
*Closed*, oppure la cronologia dei commit di `main`.

## 1. In breve

- **Sito:** werblo.github.io/islandaitinerario, pubblicato con GitHub Pages
  dal branch `main`. Installato come app con Firefox su Android (menu ⋮ →
  "Installa").
- **Tab:** Info (countdown, aurora, mappa del viaggio, cambio €/ISK, budget
  e celiachia, sicurezza, alloggi, numeri utili, checklist su Notion, avvisi
  aurora in una riga che si apre toccandola, Prepara offline), Giorno 1-8,
  Storia.
- **Checklist e biglietti:** solo su Notion, pagina "Islanda · 15-22 novembre
  2026", condivisa; nella tab Info c'è il link.
- **Aspetto:** tema scuro automatico quando il telefono è in modalità scura.
- **Date da ricordare:**
  - 2 novembre: risultato finale della ricerca sulle nuvole (sezione 6).
  - 8 novembre: ricontrollo automatico pre-partenza (Routine su claude.ai).
  - 13 novembre, 19:07 ora italiana: notifica di prova degli avvisi aurora
    su entrambi i telefoni (sezione 5).

## 2. File

| File | Cosa contiene |
|---|---|
| `dati.py` | Tutti i dati e i testi: giorni, attività, pasti, tratte, `map_points`, tappe serali, metodo nuvole, chiave pubblica VAPID. Quasi tutte le modifiche si fanno qui. |
| `render.py` | Genera la pagina: giorni, tab Storia, tab Info. |
| `app/stile.css`, `app/app.js` | Aspetto e funzioni della pagina (meteo, alba/tramonto, aurora, mappe, offline, notifiche). |
| `index.html`, `sw.js`, `images/web/` | **Generati** da `render.py`: non si modificano a mano, ma vanno sempre nel commit. |
| `images/` | Foto originali in .jpg; `images/archivio/` foto non più usate. Le `storia-*.jpg` dei box della tab Storia sono illustrazioni minimal fatte con Canva (ottobre 2026): il riquadro compare solo se il file esiste. |
| `icons/` | Icona dell'app (Canva, ottobre 2026): `icon-180/192/512.png` e le `-maskable` per Android. Dopo un cambio d'icona il telefono la aggiorna solo reinstallando l'app. |
| `routes.json` | Percorsi stradali precalcolati (sezione 4). |
| `tools/aurora_alert.py` | Avvisi aurora (sezione 5). |
| `tools/research/` | Ricerca sulle nuvole (sezione 6), da cancellare dopo il 2 novembre. |
| `CLAUDE.md` | Promemoria breve per le sessioni con Claude. |

## 3. Come si modifica

1. Si cambia `dati.py` (o le foto in `images/`).
2. Si lancia `python3 render.py` (serve Pillow: `pip install Pillow`), che
   rigenera `index.html`, `sw.js` e le foto in `images/web/`.
3. Pull request verso `main` e merge: GitHub Pages ripubblica il sito in
   pochi minuti.
4. Sul telefono la nuova versione si scarica alla prima apertura e si vede
   alla successiva (avviso "Contenuti aggiornati"). In fondo alla tab Info,
   "Versione app" e "Ricevuta il" dicono quale versione ha il telefono.

**Foto.** Il nome del file segue il giorno e il titolo dell'attività, in
minuscolo e senza accenti (es. `d4-skogafoss.jpg`, `d2-hero.jpg` per la foto
grande del giorno, `storia-hero.jpg`, `cover.jpg`). Se una foto manca compare
un segnaposto con un'icona. `render.py` converte le foto in WebP: 1200 px per
quelle grandi, 400 px sul lato corto per le miniature (nelle schede delle
attività si vedono piccole, 64 px, a sinistra del testo).

**Ordine di un giorno.** Foto, mappa, meteo e alba/tramonto, nota aurora,
Spostamenti in auto, Itinerario, Storia & curiosità, Dove mangiare, alloggio,
consiglio del giorno.

**Testi.** I box "Storia & curiosità" e la tab Storia sono in stile
enciclopedico (come Wikipedia), con sotto i link alle voci di Wikipedia in
italiano (`culture_links` in `dati.py`), solo se la voce esiste. Nei box si
va a capo con una riga vuota (`\n\n`). Nelle descrizioni si scrive "circa";
"~" resta solo in tratte e costi.

**Tema scuro.** Ogni nuovo colore aggiunto in `app/stile.css` va ripetuto
nel blocco `prefers-color-scheme: dark` in fondo al file.

**Ripristino.** I punti di ripristino sono tag git (es. `v1-stabile`). Da
GitHub: menu dei branch → scheda "Tags". Per crearne uno: Releases → "Draft a
new release" → nuovo tag su `main`.

**Privacy.** Il repository è pubblico: niente voucher, conferme di
prenotazione o dati personali (stanno su telefono, Drive o Notion). *Da fare:*
chiedere al supporto GitHub (support.github.com/contact → Repository →
Eliminazioni) di cancellare le "cached views" delle vecchie PR #26-#68, che
tengono ancora raggiungibili vecchi commit con voucher ed email.

## 4. Mappe, percorsi e offline

- **Mappe:** Leaflet con le mappe OpenStreetMap (senza chiave). Si spostano
  dopo il primo tocco; i pulsanti +/− sono in basso a sinistra.
- **Percorsi e km:** calcolati una volta con OSRM e salvati in `routes.json`.
  Se cambiano tappe o coordinate in `map_points`: tab Actions → "Aggiorna
  percorsi mappa" → Run workflow (ricalcola percorsi, km e tempi delle
  tratte e ripubblica). L'ordine di `map_points` deve seguire l'ordine reale
  di visita.
- **Offline:** pagina, foto e Leaflet funzionano offline da soli. Il pulsante
  "Prepara offline" (ultimo riquadro della tab Info) salva anche circa 930
  riquadri di mappa (circa 15 MB) lungo il percorso: va fatto con il Wi-Fi su
  entrambi i telefoni e ripetuto solo se l'app lo chiede (percorso cambiato).
  Meteo, aurora e cambio mostrano offline l'ultimo dato salvato.
- **Alba e tramonto** sono calcolati dall'app (formula NOAA), anche offline.
- Ogni giorno ha i pulsanti "Strade" (umferdin.is), "Allerte meteo"
  (vedur.is) e "Sicurezza" (safetravel.is), e un link "Naviga" per ogni tappa
  che apre Google Maps con una ricerca testuale.

## 5. Aurora e avvisi sul telefono

**Stima nell'app.** Nella tab Info: "Stasera a …: buone / scarse / nulle
probabilità" con le ore migliori, più le due notti successive; nella tab di
ogni giorno la stima di quella notte. Combina Kp previsto (NOAA, fino a 3
giorni), nuvole ora per ora (Open-Meteo) e buio astronomico. La località
segue il viaggio: l'alloggio della notte, oppure le tappe serali ora per ora
(`evening_stops` in `dati.py`; oggi solo il Giorno 3: Fontana fino alle 21,
strada del ritorno fino alle 22, poi Reykjavík).

**Notifiche** (workflow "Avvisi aurora", `tools/aurora_alert.py`, orari in
ora islandese = UTC):

- **Mattino**, alle 7:37 dal 15 al 21 novembre (se il turno parte tardi, appena
  parte, fino alle 15; se alle 7:37 mancano i dati, riprova ogni mezz'ora fino
  alle 10): com'è messa la sera, con
  una frase scherzosa personalizzata per nome. Se mancano nuvole o Kp, il
  titolo dice "previsione incompleta" o "non disponibile".
- **"🔄 Cambio di programma"**: controlli ogni 30 minuti (16:07-3:37); solo
  se la stima diventa "buone" e al mattino non lo era.
- **"Aurora: condizioni buone adesso"**: quando è buio e Kp e nuvole del
  momento sono buoni.
- **Prova automatica**: 13 novembre dalle 18:07 (19:07 in Italia), una volta
  sola anche se un telefono non la riceve (in quel caso il turno su GitHub
  risulta in rosso: ricontrollate l'iscrizione di quel telefono).

**Turni.** GitHub fa partire le esecuzioni programmate anche con 4-12 ore di
ritardo (misurato a ottobre). Per questo ogni esecuzione è un "turno" che resta
acceso 5 ore e mezza e fa da solo tutti i controlli, ai minuti :07 e :37. I
turni partono ogni 2 ore dal 13 al 22 novembre e si mettono in coda: quando uno
finisce parte il successivo, così le ore utili restano coperte anche se GitHub
ritarda. Gli avvisi già mandati sono salvati nella cache di GitHub Actions, non
nel repo, e non si ripetono tra un turno e l'altro.

Nell'app, se mancano i dati sulle nuvole la stima dice "previsione incompleta",
come le notifiche; prima delle 7 di mattina il riquadro parla di "Stanotte". La
stima delle notifiche è la stessa dell'app: se si cambia in `app/app.js`, va
cambiata anche in `tools/aurora_alert.py`.

**Configurazione** (già fatta):

1. Secret `VAPID_PRIVATE_KEY` (Settings → Secrets and variables → Actions):
   la chiave privata che corrisponde a `VAPID_PUBLIC_KEY` in `dati.py`. Se si
   perde, si crea una nuova coppia, si aggiorna la pubblica, si rilancia
   `render.py` e si riattivano gli avvisi su ogni telefono.
2. Secret `AURORA_SUBSCRIPTIONS`: un telefono per riga, con il nome davanti
   (con "Fede…" arrivano le frasi per Federica):
   ```
   Michele: {"endpoint":"https://...","keys":{...}}
   Federica: {"endpoint":"https://...","keys":{...}}
   ```
   Il codice si copia dall'app: tab Info → riga "🔔 Avvisi aurora" in fondo (toccala per aprirla) →
   "Attiva avvisi aurora" → "Copia codice". I secret non si rileggono: per
   aggiungere un telefono si reincollano tutti i codici.
3. Prova a mano: tab Actions → "Avvisi aurora" → Run workflow → `prova`
   (`turno` con una durata breve, es. 40 minuti, prova il giro dei controlli,
   ma solo fuori dalle date del viaggio: dal 13 al 22 novembre è bloccato per
   non mandare avvisi doppi; per un controllo in più usate `controllo`).

**Firefox su Android:** notifiche di Firefox attive, batteria di Firefox su
"Senza restrizioni", dati di Firefox non cancellati alla chiusura (si
perderebbero iscrizione e copia offline). Se nel log compare "iscrizione
scaduta", su quel telefono si tocca di nuovo "Attiva avvisi aurora" e si
aggiorna il secret.

## 6. Ricerca sulle nuvole (fino al 2 novembre)

`tools/research/nuvole.py` e il workflow "Ricerca nuvole" confrontano le
previsioni delle nuvole delle 7:30 con il cielo osservato (METAR di Reykjavík
e Keflavík, SYNOP di Reykjavík), per scegliere il metodo usato da app e
notifiche: `CLOUD_METHOD` in `dati.py` (`'totale'`, `'pesata'`, `'media'`,
`'media_pes'`). Raccolta ogni mattina di ottobre (alle 10:47 c'è una seconda
prova se GitHub ritarda), risultati nel riepilogo di ogni esecuzione e
nell'artifact `ricerca-nuvole`.

Metodo in uso dal 19 ottobre: **`media_pes`** (prima `'totale'`). Confronto
del 18/10 (circa 13 notti, Reykjavík + Keflavík, soglia 30%): ore azzeccate
92% contro 84% di `'totale'`, errore medio 17 punti contro 25.
Programmati con Claude: il 2
novembre risultato finale (conferma o ritorno indietro solo con il sì di
Michele) e cancellazione di `tools/research/` e `ricerca-nuvole.yml`, con
test completo. Dopo un cambio di metodo si rilancia `render.py` e si fa il
commit di `index.html`, perché le notifiche leggono il valore da lì.

## 7. Prenotazioni e alloggi

- Fontana (Giorno 3, 15:30) e Secret Lagoon (Giorno 6, 17:30) sono
  **prenotate**; i voucher non sono nel repo.
- Reykjavík (Giorni 1-3): 46heima, senza parcheggio incluso. Le zone e la
  strategia per la notte sono nel consiglio del Giorno 1.
- Hótel Búrfell (Giorni 4-5) e The Hill Guesthouse (Giorni 6-7): parcheggio
  gratuito.
- Giorno 8: la riconsegna dell'auto da voucher è alle 11:00 con volo alle
  11:25; nell'app c'è l'invito a chiedere a FairCar di anticipare.
