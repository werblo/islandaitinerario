import json, html, math

with open('cinzel.b64') as f:
    cinzel_b64 = f.read().strip()
with open('plex.b64') as f:
    plex_b64 = f.read().strip()

# ============================================================
# DATI DEL VIAGGIO — modifica qui per aggiornare l'itinerario,
# poi rilancia: python3 render.py
# ============================================================

locations = {
    'reykjavik': {'name': 'Reykjavík', 'lat': 64.1466, 'lon': -21.9426},
    'vik': {'name': 'Vík í Mýrdal', 'lat': 63.4186, 'lon': -19.0060},
    'fludir': {'name': 'Flúðir', 'lat': 64.1372, 'lon': -20.3033},
    'keflavik': {'name': 'Keflavík', 'lat': 63.9850, 'lon': -22.6056}
}

seasonal = {
    'reykjavik': {'tmax': 4, 'tmin': -1, 'desc': 'Nuvoloso, rovesci di pioggia/neve frequenti', 'wind': 'moderato-forte'},
    'vik': {'tmax': 5, 'tmin': 0, 'desc': 'Molto piovoso, tipico della costa sud', 'wind': 'forte, zona esposta'},
    'fludir': {'tmax': 3, 'tmin': -3, 'desc': 'Più freddo, neve possibile in quota', 'wind': 'moderato'},
    'keflavik': {'tmax': 4, 'tmin': -1, 'desc': 'Piovoso e ventoso, zona costiera aperta', 'wind': 'forte'}
}

# Alba/tramonto precalcolati (astral, Nov 2026) — fallback quando si è offline
sun_fallback = {
    'd1': {'sunrise': '09:57', 'sunset': '16:26', 'daylight': '6h 29m'},
    'd2': {'sunrise': '10:00', 'sunset': '16:23', 'daylight': '6h 23m'},
    'd3': {'sunrise': '10:03', 'sunset': '16:21', 'daylight': '6h 17m'},
    'd4': {'sunrise': '09:48', 'sunset': '16:13', 'daylight': '6h 25m'},
    'd5': {'sunrise': '09:51', 'sunset': '16:10', 'daylight': '6h 19m'},
    'd6': {'sunrise': '09:54', 'sunset': '16:08', 'daylight': '6h 14m'},
    'd7': {'sunrise': '10:09', 'sunset': '16:03', 'daylight': '5h 54m'},
    'd8': {'sunrise': '10:12', 'sunset': '16:01', 'daylight': '5h 49m'},
}

checklist_groups = [
    {'title': 'Documenti', 'items': [
        "Carta d'identità o passaporto in corso di validità",
        'Patente di guida (valida in Islanda, non serve il permesso internazionale per cittadini UE)',
        'Carta di credito intestata al conducente, per il noleggio auto',
        'Voucher noleggio auto FairCar, stampato o salvato offline',
        'Conferme di prenotazione degli alloggi',
        'Biglietti aerei / carte d\'imbarco',
        'Assicurazione di viaggio (verifica che copra guida invernale/neve)',
        "Itinerario registrato su safetravel.is",
    ]},
    {'title': 'Abbigliamento', 'items': [
        'Giacca impermeabile e antivento (guscio esterno)',
        'Strato termico o pile sotto la giacca',
        'Scarponcini impermeabili con buon grip su ghiaccio',
        'Guanti, berretto, sciarpa',
        'Calzini di ricambio (pioggia/neve)',
        'Costume da bagno (per le terme in programma)',
        'Asciugamano compatto a rapida asciugatura',
    ]},
    {'title': 'Tecnologia & varie', 'items': [
        'Power bank (il freddo scarica le batterie più in fretta)',
        'Torcia frontale, comoda a mani libere col buio che scende presto',
        'Mappe offline di Google Maps scaricate per l\'Islanda',
        'App 112 Iceland installata',
        'Carta con PIN attivo per le colonnine self-service (vedi nota sotto)',
        'Un po\' di contanti, anche se l\'Islanda è quasi completamente cashless',
    ]},
]

stays = [
    {'name': '46heima Boutique Apartments', 'detail': 'Laugavegur 46, Reykjavík · 15–18 nov (3 notti)'},
    {'name': 'Hotel Burfell', 'detail': 'Vík í Mýrdal · 18–20 nov (2 notti)'},
    {'name': 'The Hill Guesthouse', 'detail': 'Flúðir · 20–22 nov (2 notti)'}
]

days = [
 {'id':'d1','num':1,'dateISO':'2026-11-15','dateLabel':'Dom 15 nov','title':'Arrivo & Reykjavík','locKey':'reykjavik',
  'legs':[
    {'from':'Aeroporto di Keflavík','to':'Ufficio FairCar','km':3,'time':'~10 min (navetta inclusa)','note':'Atterraggio 10:35 · ritiro auto previsto 11:00'},
    {'from':'Keflavík','to':'Reykjavík','km':48,'time':'~45 min','note':'Se si salta la Blue Lagoon; con tappa +45 min circa'}
  ],
  'activities':[
    {'time':'11:00','title':'Ritiro auto 4x4','desc':'FairCar, Bogatröð 1, Keflavík. Portare patente, carta di credito intestata al conducente e voucher stampato o digitale.','cost':None},
    {'time':'15:00','title':'Check-in appartamento','desc':"46heima Boutique Apartments, Laugavegur 46. Codice d'accesso via email prima dell'arrivo.",'cost':None},
    {'time':'16:30','title':'Passeggiata nel centro','desc':'Laugavegur, Hallgrímskirkja (belvedere sulla torre), porto vecchio, Sun Voyager.','cost':'gratis'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Bónus (supermercato) o hot dog da Bæjarins Beztu','note':'Per il senza glutine, chiedi il würstel senza pane','cost':'€','gf':True},
    {'meal':'Cena','place':'Gló, Laugavegur','note':'Cucina salutista, piatti glútenlaus segnalati in menu','cost':'€€','gf':True}
  ],
  'accommodation':{'name':'46heima Boutique Apartments','detail':'Laugavegur 46, Reykjavík · 3 notti · check-in dalle 15:00','url':'https://www.booking.com/hotel/is/46heima-apartments.en-gb.html'},
  'tips':"Giornata di arrivo tranquilla: sistematevi con calma e fate un po' di spesa in un Bónus per i giorni successivi. Avrete un paio di soste alle terme nel resto del viaggio, più economiche e meno turistiche della Blue Lagoon.",
  'culture':"Reykjavík ha una storia più antica di quanto sembri: fondata nell'874 d.C. da Ingólfur Arnarson, primo colono vichingo dell'isola, deve il nome — \"baia dei fumi\" — al vapore geotermico che i primi coloni scambiarono per fumo di incendi. La Hallgrímskirkja che vedrete oggi non è un caso: il suo profilo a colonne è un omaggio diretto alle colonne di basalto che modellano le coste islandesi, le stesse che troverete tra qualche giorno a Reynisfjara. Passeggiando da Laugavegur al porto vecchio, fino al Sun Voyager sul lungomare, si attraversano più di mille anni di storia in mezz'ora a piedi."
 },
 {'id':'d2','num':2,'dateISO':'2026-11-16','dateLabel':'Lun 16 nov','title':'Reykjavík: cultura e Reykjanes','locKey':'reykjavik',
  'legs':[],
  'activities':[
    {'time':'10:00','title':'Perlan','desc':'Museo con grotta di ghiaccio artificiale e vista panoramica a 360° sulla città.','cost':'€€ ~4900 ISK / ~34€','link':'https://perlan.is/en'},
    {'time':'12:30','title':'Harpa & porto vecchio','desc':'Sala concerti in vetro iridescente, passeggiata sul lungomare.','cost':'gratis','link':'https://www.harpa.is/en/'},
    {'time':'14:00','title':'National Museum of Iceland (facoltativo, in città)','desc':'Storia e cultura islandese dagli insediamenti vichinghi a oggi.','cost':'€ ~2900 ISK / ~20€','link':'https://www.thjodminjasafn.is/english'},
    {'time':'14:00','title':'Reykjanes (facoltativo, mezza giornata fuori città)','desc':"Ponte tra i continenti, Gunnuhver (la pozza di fango più grande d'Islanda) e il faro di Reykjanesviti. ~45 min di guida a tratta, paesaggio lunare e vulcanico diverso da tutto il resto del viaggio. Zona geologicamente molto attiva: verificate lo stato di accesso il giorno stesso su visitreykjanes.is.",'cost':'gratis','link':'https://www.visitreykjanes.is/en/'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Hlemmur Mathöll','note':'Più stand con piatti glútenlaus','cost':'€€','gf':True},
    {'meal':'Cena','place':'Sushi Social o cucina in appartamento','note':'Menu con opzioni senza glutine indicate','cost':'€€€','gf':True}
  ],
  'accommodation':{'name':'46heima Boutique Apartments','detail':'2ª notte a Reykjavík','url':'https://www.booking.com/hotel/is/46heima-apartments.en-gb.html'},
  'tips':"Giornata cuscinetto: se il meteo è brutto, si può invertire con il Giorno 3. Nel pomeriggio scegliete: Museo se preferite restare in città con calma, Reykjanes se volete uscire a vedere un paesaggio diverso.",
  'culture':"Il Perlan racconta la geologia islandese da dentro una grotta di ghiaccio artificiale, costruito sopra sei enormi serbatoi che ancora oggi riscaldano Reykjavík con l'acqua calda del sottosuolo. L'Harpa, sala concerti dalla facciata a nido d'ape ispirata alle colonne di basalto, è diventata il simbolo della rinascita della città dopo la crisi finanziaria del 2008. Al National Museum si ripercorre la storia islandese dai primi coloni vichinghi a oggi. Se scegliete invece Reykjanes, camminerete letteralmente tra due continenti sul Bridge Between Continents, un ponte pedonale sulla stessa faglia di Þingvellir. Qui la terra non è statica: dopo quasi 800 anni di quiete, dal 2021 il vulcanismo è tornato con eruzioni vicino a Grindavík, l'ultima tra il 2023 e il 2024. Vedrete il Gunnuhver, la pozza di fango più grande d'Islanda, e il Reykjanesviti, il faro più antico della nazione — tutto dentro un UNESCO Global Geopark dove la terra si sta ancora formando."
 },
 {'id':'d3','num':3,'dateISO':'2026-11-17','dateLabel':'Mar 17 nov','title':'Þingvellir & relax serale','locKey':'reykjavik',
  'legs':[
    {'from':'Reykjavík','to':'Þingvellir','km':45,'time':'~45 min'},
    {'from':'Þingvellir','to':'Laugarvatn','km':25,'time':'~20 min'},
    {'from':'Laugarvatn','to':'Reykjavík','km':80,'time':'~1h05'}
  ],
  'activities':[
    {'time':'10:00','title':'Þingvellir National Park','desc':'Faglia tra le placche nordamericana ed euroasiatica, sito del primo parlamento islandese (Unesco).','cost':'gratis (parcheggio ~1000 ISK / ~7€)','link':'https://www.thingvellir.is/en/'},
    {'time':'15:30','title':'Sosta relax a Laugarvatn (facoltativo, di sera)','desc':"Una pausa rilassante nella zona di Laugarvatn, sulla strada del ritorno verso Reykjavík.",'cost':'€€ ~50€/persona'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Pranzo al sacco / Bónus','note':'Porta qualcosa dal Bónus di Reykjavík, comodo per una sosta veloce vicino a Þingvellir','cost':'€','gf':True},
    {'meal':'Cena','place':'Hlemmur Mathöll, Reykjavík','note':'Food hall con vari stand, alcuni segnalano opzioni senza glutine','cost':'€€','gf':True}
  ],
  'accommodation':{'name':'46heima Boutique Apartments','detail':'Ultima notte a Reykjavík · check-out domani 09:30-10:00','url':'https://www.booking.com/hotel/is/46heima-apartments.en-gb.html'},
  'tips':"Giornata più leggera (~150 km totali) e volutamente rilassante: è l'ultima notte a Reykjavík prima dei due giorni più intensi del viaggio (Costa Sud e Jökulsárlón). Geysir e Gullfoss li vedrete il Giorno 7 da Flúðir, molto più vicini da lì che da Reykjavík. Se prenotate qualcosa per la sera, fatelo con anticipo — gli slot serali si esauriscono in fretta.",
  'culture':"A Þingvellir camminerete letteralmente tra due continenti: la faglia che attraversa il parco segna il punto in cui le placche nordamericana ed eurasiatica si allontanano di circa 2 cm l'anno. Qui, nel 930 d.C., nacque l'Alþingi, tra i più antichi parlamenti al mondo ancora in vita — la culla della democrazia islandese che riprenderete più avanti nella tab Storia. Poco più a sud, sul lago di Laugarvatn, la zona sfrutta la stessa energia del sottosuolo che alimenta Þingvellir e Geysir."
 },
 {'id':'d4','num':4,'dateISO':'2026-11-18','dateLabel':'Mer 18 nov','title':'Reykjavík → Vík: Costa Sud','locKey':'vik',
  'legs':[
    {'from':'Reykjavík','to':'Seljalandsfoss','km':125,'time':'~1h40'},
    {'from':'Seljalandsfoss','to':'Skógafoss','km':30,'time':'~25 min'},
    {'from':'Skógafoss','to':'Dyrhólaey','km':30,'time':'~25 min'},
    {'from':'Dyrhólaey','to':'Reynisfjara','km':7,'time':'~10 min'},
    {'from':'Reynisfjara','to':'Vík','km':12,'time':'~12 min'}
  ],
  'activities':[
    {'time':'09:30','title':'Check-out appartamento','desc':'','cost':None},
    {'time':'11:30','title':'Seljalandsfoss','desc':"Cascata che si può costeggiare sul retro (in inverno spesso ghiacciata, occhio al sentiero). A 10 min a piedi c'è Gljúfrabúi, cascata nascosta in un canyon.",'cost':'gratis','link':'https://it.wikipedia.org/wiki/Seljalandsfoss'},
    {'time':'13:15','title':'Skógafoss','desc':"Una delle cascate più imponenti d'Islanda, 60m, scalinata panoramica in cima.",'cost':'gratis','link':'https://it.wikipedia.org/wiki/Skogafoss'},
    {'time':'14:45','title':'Dyrhólaey','desc':'Promontorio con arco di roccia e vista su Reynisfjara. Da vedere con un po\' di luce ancora buona: il tramonto qui è verso le 16:15.','cost':'gratis'},
    {'time':'15:30','title':'Reynisfjara','desc':'Spiaggia di sabbia nera con colonne basaltiche e i faraglioni di Reynisdrangar. Attenzione alle onde anomale, non voltare le spalle al mare.','cost':'gratis'},
    {'time':'16:15','title':'Víkurkirkja','desc':"La chiesetta bianca dal tetto rosso su per la collina di Vík, tra le più fotografate d'Islanda: da lassù la vista abbraccia il villaggio, la spiaggia nera e i faraglioni di Reynisdrangar sullo sfondo. Ultima tappa apposta: proprio all'ora del tramonto puo' regalare una luce spettacolare.",'cost':'gratis'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Picnic a Skógar','note':'Porta snack dal Bónus di Reykjavík','cost':'€','gf':True},
    {'meal':'Cena','place':'Suður-Vík Restaurant','note':'Menu con opzioni glútenlaus indicate','cost':'€€','gf':True}
  ],
  'accommodation':{'name':'Hotel Burfell','detail':'Vík í Mýrdal · 2 notti','url':'https://hotelburfell.is/'},
  'tips':'Il 18 novembre a Vík il sole tramonta verso le 16:15 (molto prima di quanto sembri): Dyrhólaey e Reynisfjara vanno viste per bene entro quell\'ora, la Víkurkirkja invece va benissimo proprio al tramonto/appena dopo, dato che è a due passi dal centro del paese e non richiede tempo di guida extra.',
  'culture':"Oggi si passa dalle cascate alla costa vulcanica. Skógafoss, 60 metri di salto, nasconde secondo la leggenda un forziere vichingo dietro le sue acque. A Reynisfjara la sabbia nera è lava basaltica frantumata da millenni di oceano, e le pareti a colonne esagonali sono le stesse che hanno ispirato l'architettura della Hallgrímskirkja. Al largo, i faraglioni Reynisdrangar sarebbero — dice la leggenda — due troll pietrificati dall'alba mentre trascinavano a riva una nave: attenzione alle onde anomale, il mare qui non scherza. Dyrhólaey, il promontorio con l'arco di roccia, nacque da un'eruzione sottomarina durante l'ultima glaciazione. Vík, il villaggio più a sud dell'isola, vive all'ombra del vulcano Katla, sepolto sotto il ghiacciaio Mýrdalsjökull — e la sua chiesetta rossa e bianca, arroccata sulla collina, era il punto di raccolta designato per gli abitanti in caso di eruzione improvvisa."
 },
 {'id':'d5','num':5,'dateISO':'2026-11-19','dateLabel':'Gio 19 nov','title':'Escursione a Jökulsárlón','locKey':'vik',
  'legs':[
    {'from':'Vík','to':'Jökulsárlón','km':192,'time':'~2h45 (diretto, oltre Fjaðrárgljúfur senza fermarsi)'},
    {'from':'Jökulsárlón','to':'Fjaðrárgljúfur','km':100,'time':'~1h15 (sulla via del ritorno)'},
    {'from':'Fjaðrárgljúfur','to':'Vík','km':72,'time':'~55 min'}
  ],
  'activities':[
    {'time':'08:00','title':'Partenza presto','desc':'Giornata lunga di guida: partire con il buio è normale in novembre, il sole sorge solo verso le 9:50.','cost':None},
    {'time':'10:45','title':'Jökulsárlón Glacier Lagoon','desc':'Laguna glaciale con iceberg alla deriva verso il mare.','cost':'gratis (parcheggio a pagamento)'},
    {'time':'12:15','title':'Diamond Beach','desc':'Spiaggia nera di fronte alla laguna dove i blocchi di ghiaccio si arenano.','cost':'gratis','link':'https://perlan.is/articles/diamond-beach-iceland'},
    {'time':'14:30','title':'Fjaðrárgljúfur','desc':"Canyon serpeggiante con pareti muschiose, punti panoramici accessibili a piedi. Visitato sulla via del ritorno apposta: con la luce del primo mattino (alba verso le 9:50) si vedrebbe pochissimo.",'cost':'gratis'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Kaffi Jökulsárlón o pranzo al sacco','note':'Zuppe spesso senza glutine, conferma con lo staff','cost':'€€','gf':True},
    {'meal':'Cena','place':'Ströndin Bistro, Vík','note':'','cost':'€€','gf':True}
  ],
  'accommodation':{'name':'Hotel Burfell','detail':'2ª notte a Vík','url':'https://hotelburfell.is/'},
  'tips':"~370 km andata/ritorno da Vík: con brutto tempo valuta di fermarti solo a Jökulsárlón/Diamond Beach, tagliando Fjaðrárgljúfur. Il giro è organizzato per arrivare a Jökulsárlón e Diamond Beach con il sole già alto, e vedere Fjaðrárgljúfur nel primo pomeriggio con luce piena.",
  'culture':"Giornata dedicata al ghiaccio. A Jökulsárlón la laguna esiste solo da un secolo: il Vatnajökull, il ghiacciaio più esteso d'Europa, si è ritirato rapidamente da inizio '900 lasciando dietro di sé questo bacino pieno di iceberg alla deriva verso il mare. Quelli che si arenano sulla sabbia nera di Diamond Beach, levigati e trasparenti, possono contenere ghiaccio compresso da centinaia o migliaia di anni. Sulla via del ritorno, il canyon di Fjaðrárgljúfur, scavato da un fiume glaciale in circa due milioni di anni, è diventato famoso di recente anche grazie a un video musicale di Justin Bieber."
 },
 {'id':'d6','num':6,'dateISO':'2026-11-20','dateLabel':'Ven 20 nov','title':'Vík → Flúðir','locKey':'fludir',
  'legs':[
    {'from':'Vík','to':'Kerið','km':130,'time':'~1h50'},
    {'from':'Kerið','to':'Flúðir','km':39,'time':'~30 min'}
  ],
  'activities':[
    {'time':'10:00','title':'Check-out Hotel Burfell','desc':'','cost':None},
    {'time':'12:30','title':'Kerið','desc':'Cratere vulcanico con un lago sul fondo, percorribile a piedi in 15-20 min.','cost':'€ ~400 ISK / ~3€','link':'https://kerid.is/'},
    {'time':'15:30','title':'Check-in The Hill Guesthouse','desc':'Flúðir','cost':None},
    {'time':'19:00','title':'Secret Lagoon','desc':"La piscina geotermica più antica d'Islanda, meno turistica ed economica della Blue Lagoon. Ottima anche di sera per provare a scorgere l'aurora dall'acqua calda.",'cost':'€€ ~7000 ISK / ~48€ a persona, prenotare online','link':'https://secretlagoon.is/'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Selfoss (pranzo al sacco o supermercato locale)','note':'Ultima città con supermercati grandi prima di Flúðir, sulla strada da Vík','cost':'€','gf':True},
    {'meal':'Cena','place':'Cucina alla guesthouse o Restaurant Grund','note':'Verifica il menu glútenlaus in loco','cost':'€€','gf':True}
  ],
  'accommodation':{'name':'The Hill Guesthouse','detail':'Flúðir · 2 notti','url':'https://thehillhotel.is/guesthouse-fludir/'},
  'tips':'Prenota la Secret Lagoon in anticipo online: gli slot serali si esauriscono.',
  'culture':"Kerið è un cratere vulcanico di circa 3000 anni, insolito nel colore: la roccia è ricca di scoria rossastra invece del solito basalto nero, e sul fondo si è formato un piccolo lago verde-azzurro alimentato dalla falda. A Flúðir vi aspetta la Secret Lagoon, la piscina geotermica più antica dell'isola: costruita nel 1891 come prima piscina pubblica islandese, oggi resta piccola e informale rispetto alla Blue Lagoon, con l'acqua che sgorga naturalmente a circa 38-40°C da una sorgente a pochi passi dalla vasca."
 },
 {'id':'d7','num':7,'dateISO':'2026-11-21','dateLabel':'Sab 21 nov','title':'Geysir & Gullfoss e sorgenti calde','locKey':'fludir',
  'legs':[
    {'from':'Flúðir','to':'Geysir','km':30,'time':'~25 min'},
    {'from':'Geysir','to':'Gullfoss','km':10,'time':'~10 min'},
    {'from':'Gullfoss','to':'Faxi','km':21,'time':'~20 min'},
    {'from':'Faxi','to':'Flúðir','km':8,'time':'~10 min'}
  ],
  'activities':[
    {'time':'10:00','title':'Geysir & Strokkur','desc':'Area geotermica: Strokkur erutta ogni 5-10 minuti.','cost':'gratis'},
    {'time':'11:30','title':'Gullfoss','desc':"Cascata a doppio salto, spettacolare anche d'inverno con il ghiaccio sulle rocce.",'cost':'gratis','link':'https://it.wikipedia.org/wiki/Gullfoss'},
    {'time':'14:00','title':'Faxi','desc':'Cascata piccola e tranquilla vicino a Flúðir, poco turistica.','cost':'gratis','link':'https://it.wikipedia.org/wiki/Faxi'},
    {'time':'15:30','title':'Passeggiata a Flúðir','desc':'Villaggio geotermico, serre e piccole botteghe locali.','cost':'gratis'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Friðheimar, Reykholt','note':'Famosa zuppa di pomodoro in serra, sulla strada per Geysir; chiedi la versione senza pane/crostini','cost':'€€','gf':True},
    {'meal':'Cena','place':'Cucina alla guesthouse','note':'Ultima occasione per finire la spesa dal Bónus','cost':'€','gf':True}
  ],
  'accommodation':{'name':'The Hill Guesthouse','detail':'Ultima notte a Flúðir · check-out presto domani','url':'https://thehillhotel.is/guesthouse-fludir/'},
  'tips':"Da Flúðir Geysir e Gullfoss sono a un tiro di schioppo (~30-40 km), molto più vicini che da Reykjavík: giornata comoda, e cielo scuro poco inquinato per tenere d'occhio l'aurora la sera.",
  'culture':"Il nome stesso di \"geyser\" nasce qui: Strokkur erutta ogni 5-10 minuti, mentre il Grande Geysir che gli ha dato il nome dorme quasi sempre dal 2003. Gullfoss esiste ancora grazie a Sigríður Tómasdóttir, che ai primi del '900 si oppose a un progetto di diga che l'avrebbe sommersa. Flúðir vive di geotermia da oltre un secolo: le sue serre, riscaldate dal vapore del sottosuolo, coltivano pomodori e ortaggi anche nel buio di novembre. Faxi, piccola e quasi sempre deserta, è la cascata che molti islandesi preferiscono a Gullfoss nei weekend affollati."
 },
 {'id':'d8','num':8,'dateISO':'2026-11-22','dateLabel':'Dom 22 nov','title':'Flúðir → Keflavík → Volo di ritorno','locKey':'keflavik',
  'legs':[
    {'from':'Flúðir','to':'Aeroporto di Keflavík','km':140,'time':'~2h05'}
  ],
  'activities':[
    {'time':'06:45','title':'Partenza da Flúðir','desc':'Partite presto per avere margine: riconsegna auto e imbarco sono molto ravvicinati.','cost':None},
    {'time':'~09:00','title':'Riconsegna auto FairCar','desc':'Il voucher indica riconsegna alle 11:00, ma il volo parte alle 11:25: verificate con FairCar se potete riconsegnare prima (es. entro le 9:00-9:30) per avere tempo per check-in e imbarco.','cost':None},
    {'time':'11:25','title':'Volo EJU3970 Keflavík → Milano Malpensa','desc':'Arrivo previsto alle 16:45.','cost':None}
  ],
  'food':[
    {'meal':'Colazione','place':'Guesthouse o avanzi della spesa','note':'','cost':'€','gf':True}
  ],
  'accommodation': None,
  'tips':'Pochissimo margine tra riconsegna auto (11:00) e decollo (11:25): meglio anticipare la riconsegna il più possibile.',
  'culture':"L'Islanda produce quasi il 100% della sua elettricità da fonti rinnovabili — geotermia e idroelettrico — un'anomalia quasi unica al mondo, resa possibile proprio dal fuoco sotto i piedi che avete attraversato in questi otto giorni. Buon rientro."
 }
]

map_points = {
    'd1': [{'name':'Aeroporto Keflavík','lat':63.9850,'lon':-22.6056}, {'name':'Reykjavík','lat':64.1466,'lon':-21.9426}],
    'd2': [{'name':'Perlan','lat':64.1289,'lon':-21.9147}, {'name':'Harpa','lat':64.1500,'lon':-21.9326}, {'name':'National Museum','lat':64.1417,'lon':-21.9530}, {'name':'Bridge Between Continents (facolt.)','lat':63.8697,'lon':-22.6764}, {'name':'Gunnuhver (facolt.)','lat':63.8181,'lon':-22.6994}, {'name':'Reykjanesviti (facolt.)','lat':63.8156,'lon':-22.6913}],
    'd3': [{'name':'Reykjavík','lat':64.1466,'lon':-21.9426}, {'name':'Þingvellir','lat':64.2559,'lon':-21.1297}, {'name':'Laugarvatn','lat':64.2019,'lon':-20.7357}, {'name':'Reykjavík','lat':64.1466,'lon':-21.9426}],
    'd4': [{'name':'Reykjavík','lat':64.1466,'lon':-21.9426}, {'name':'Seljalandsfoss','lat':63.6156,'lon':-19.9886}, {'name':'Skógafoss','lat':63.5321,'lon':-19.5116}, {'name':'Dyrhólaey','lat':63.4033,'lon':-19.1250}, {'name':'Reynisfjara','lat':63.4038,'lon':-19.0428}, {'name':'Víkurkirkja','lat':63.4193,'lon':-19.0058}],
    'd5': [{'name':'Vík','lat':63.4186,'lon':-19.0060}, {'name':'Jökulsárlón','lat':64.0784,'lon':-16.2300}, {'name':'Diamond Beach','lat':64.0645,'lon':-16.1809}, {'name':'Fjaðrárgljúfur','lat':63.7722,'lon':-18.1725}, {'name':'Vík','lat':63.4186,'lon':-19.0060}],
    'd6': [{'name':'Vík','lat':63.4186,'lon':-19.0060}, {'name':'Kerið','lat':64.0410,'lon':-20.8834}, {'name':'Flúðir','lat':64.1372,'lon':-20.3033}, {'name':'Secret Lagoon','lat':64.1306,'lon':-20.2989}],
    'd7': [{'name':'Flúðir','lat':64.1372,'lon':-20.3033}, {'name':'Geysir','lat':64.3128,'lon':-20.3009}, {'name':'Gullfoss','lat':64.3271,'lon':-20.1199}, {'name':'Faxi','lat':64.1197,'lon':-20.2394}, {'name':'Flúðir','lat':64.1372,'lon':-20.3033}],
    'd8': [{'name':'Flúðir','lat':64.1372,'lon':-20.3033}, {'name':'Aeroporto Keflavík','lat':63.9850,'lon':-22.6056}]
}

def e(s):
    return html.escape(s, quote=True) if s else ''

LOGISTICS_TITLES_LOWER = {'partenza presto'}
import re
def is_logistics(title):
    if title.strip().lower() in LOGISTICS_TITLES_LOWER:
        return True
    return bool(re.search(r'check-in|check-out|ritiro auto|riconsegna auto|partenza da|volo ', title, re.I))

import unicodedata
ICELANDIC_MAP = str.maketrans({'Þ':'Th','þ':'th','Ð':'D','ð':'d','Æ':'Ae','æ':'ae','Ö':'O','ö':'o'})
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

def photo_slot(filename, label, css_class, icon_key='village'):
    bg1, bg2 = ICON_BG.get(icon_key, ('#3a2f22', '#5c4a33'))
    inner = icon_svg(icon_key)
    return (f'<div class="photo-slot {css_class}" data-photo="{e(filename)}" '
            f'style="--bg1:{bg1};--bg2:{bg2}">'
            f'<img src="images/{filename}" alt="{e(label)}" loading="lazy" '
            f'onerror="this.parentElement.classList.add(\'photo-slot--empty\')">'
            f'<div class="photo-slot__ph"><svg viewBox="0 0 64 56" class="photo-slot__icon">{inner}</svg>'
            f'<span>{e(label)}</span></div></div>')

def render_leg(leg):
    note = f'<div class="leg-note">{e(leg["note"])}</div>' if leg.get('note') else ''
    return (f'<div class="leg"><div class="leg-route">{e(leg["from"])} → {e(leg["to"])}</div>'
            f'<div class="leg-meta">{leg["km"]} km · {e(leg["time"])}</div>{note}</div>')

def render_activity(day_id, idx, act):

    has_img = not is_logistics(act['title']) and act['title'].strip()
    img_html = ''
    if has_img:
        fname = f"{day_id}-{slugify(act['title'])}.jpg"
        img_html = photo_slot(fname, act['title'], 'photo-slot--thumb', guess_icon(act['title']))
    cost_html = f'<div class="act-cost">{e(act["cost"])}</div>' if act.get('cost') else ''
    desc_html = f'<div class="act-desc">{e(act["desc"])}</div>' if act.get('desc') else ''
    link_html = ''
    if act.get('link'):
        title_html = (f'<a class="act-title act-title--link" href="{e(act["link"])}" '
                       f'target="_blank" rel="noopener">{e(act["title"])} <span class="act-title-arrow">\u2197</span></a>')
        link_html = (f'<a class="act-link" href="{e(act["link"])}" target="_blank" rel="noopener">'
                     f'Scopri di più \u2197</a>')
    else:
        title_html = f'<div class="act-title">{e(act["title"])}</div>'
    return (f'<div class="act-card">{img_html}<div class="act-body">'
            f'<div class="act-top">{title_html}'
            f'<div class="act-time">{e(act["time"])}</div></div>{desc_html}{cost_html}{link_html}</div></div>')

def render_food(f):
    note = f'<div class="food-note">{e(f["note"])}</div>' if f.get('note') else ''
    gf = '<span class="gf-badge">senza glutine indicato</span>' if f.get('gf') else ''
    return (f'<div class="food-card"><div class="food-top">'
            f'<div><strong>{e(f["meal"])}</strong> — {e(f["place"])}</div>'
            f'<div class="food-cost">{e(f["cost"])}</div></div>{note}{gf}</div>')

def route_svg(day_id):
    points = map_points.get(day_id, [])
    if not points:
        return ''

    W, H, PAD = 600, 320, 46

    lat0, lon0 = points[0]['lat'], points[0]['lon']
    lat_mean = sum(p['lat'] for p in points) / len(points)
    coslat = math.cos(math.radians(lat_mean))

    proj = []
    for p in points:
        x_km = (p['lon'] - lon0) * 111.32 * coslat
        y_km = (p['lat'] - lat0) * 110.57
        proj.append((x_km, y_km, p['name']))

    xs = [c[0] for c in proj]
    ys = [c[1] for c in proj]
    range_x = max(xs) - min(xs) or 1.0
    range_y = max(ys) - min(ys) or 1.0
    scale = min((W - 2 * PAD) / range_x, (H - 2 * PAD) / range_y)
    cx0 = (max(xs) + min(xs)) / 2
    cy0 = (max(ys) + min(ys)) / 2

    def to_svg(x_km, y_km):
        sx = W / 2 + (x_km - cx0) * scale
        sy = H / 2 - (y_km - cy0) * scale
        return sx, sy

    svg_pts = [(to_svg(x, y), name) for x, y, name in proj]

    # linea di percorso (unisce le tappe nell'ordine di visita)
    path_d = 'M ' + ' L '.join(f'{sx:.1f} {sy:.1f}' for (sx, sy), _ in svg_pts)
    route_path = f'<path d="{path_d}" fill="none" stroke="#4f8fa8" stroke-width="3" stroke-dasharray="1,9" stroke-linecap="round"/>'

    markers = []
    labels = []
    n = len(svg_pts)
    # tappe uniche (senza contare due volte lo stesso punto di ritorno) per la numerazione
    seen = {}
    seq = 0
    for i, ((sx, sy), name) in enumerate(svg_pts):
        is_endpoint = i == 0 or i == n - 1
        key = round(sx, 1), round(sy, 1)
        if key not in seen:
            seq += 1
            seen[key] = seq
        r = 9 if is_endpoint else 7
        fill = '#b5673a' if is_endpoint else '#f2ede2'
        markers.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{r}" fill="{fill}" stroke="#16263b" stroke-width="2"/>')
        if is_endpoint:
            markers.append(f'<text x="{sx:.1f}" y="{sy+3.5:.1f}" font-size="9" font-weight="700" fill="#16263b" text-anchor="middle" font-family="IBM Plex Sans,sans-serif">{seen[key]}</text>')
        # etichetta ruotata in 4 direzioni (evita sovrapposizioni tra punti vicini),
        # e per punti molto ravvicinati (< 30px) alterna un raggio maggiore
        near_prev = i > 0 and math.hypot(sx - svg_pts[i-1][0][0], sy - svg_pts[i-1][0][1]) < 30
        radius = 24 if near_prev else 15
        direction = i % 4
        if direction == 0:
            lx, ly, anchor = sx, sy - radius, 'middle'
        elif direction == 1:
            lx, ly, anchor = sx + radius, sy + 3, 'start'
        elif direction == 2:
            lx, ly, anchor = sx, sy + radius + 8, 'middle'
        else:
            lx, ly, anchor = sx - radius, sy + 3, 'end'
        labels.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="12" font-weight="600" fill="#e4dcc8" '
            f'text-anchor="{anchor}" font-family="IBM Plex Sans,sans-serif" '
            f'style="paint-order:stroke;stroke:#16263b;stroke-width:3px;stroke-linejoin:round;">{e(name)}</text>'
        )

    # barra di scala (in km, basata sulla stessa proiezione)
    scale_km_options = [5, 10, 20, 30, 50, 75, 100, 150]
    target_px = 70
    best_km = min(scale_km_options, key=lambda k: abs(k * scale - target_px))
    bar_px = best_km * scale
    bar_x0, bar_y0 = 24, H - 22

    compass = (
        f'<g transform="translate({W-38},34)">'
        f'<path d="M0 -12 L5 6 L0 2 L-5 6 Z" fill="#d9985f"/>'
        f'<text x="0" y="-16" font-size="10" font-weight="700" fill="#e4dcc8" text-anchor="middle" font-family="IBM Plex Sans,sans-serif">N</text>'
        f'</g>'
    )

    scale_bar = (
        f'<g>'
        f'<line x1="{bar_x0}" y1="{bar_y0}" x2="{bar_x0+bar_px:.1f}" y2="{bar_y0}" stroke="#e4dcc8" stroke-width="2"/>'
        f'<line x1="{bar_x0}" y1="{bar_y0-4}" x2="{bar_x0}" y2="{bar_y0+4}" stroke="#e4dcc8" stroke-width="2"/>'
        f'<line x1="{bar_x0+bar_px:.1f}" y1="{bar_y0-4}" x2="{bar_x0+bar_px:.1f}" y2="{bar_y0+4}" stroke="#e4dcc8" stroke-width="2"/>'
        f'<text x="{bar_x0}" y="{bar_y0-8}" font-size="10" fill="#e4dcc8" font-family="IBM Plex Sans,sans-serif">~{best_km} km</text>'
        f'</g>'
    )

    return (f'<svg viewBox="0 0 {W} {H}" class="route-map" preserveAspectRatio="xMidYMid meet">'
            f'<defs><radialGradient id="rmv-{day_id}" cx="50%" cy="40%" r="75%">'
            f'<stop offset="0%" stop-color="#22344a"/><stop offset="100%" stop-color="#16263b"/>'
            f'</radialGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#rmv-{day_id})"/>'
            f'{route_path}{"".join(markers)}{"".join(labels)}{compass}{scale_bar}'
            f'</svg>')

def render_day_section(day):
    legs_html = ''
    if day['legs']:
        legs_html = ('<div class="section"><div class="section-title">Spostamenti in auto</div>'
                     '<div class="stack">' + ''.join(render_leg(l) for l in day['legs']) + '</div></div>')
    acts_html = ''.join(render_activity(day['id'], i, a) for i, a in enumerate(day['activities']))
    food_html = ''.join(render_food(f) for f in day['food'])
    acc = day.get('accommodation')
    acc_html = ''
    if acc:
        acc_name_html = e(acc["name"])
        if acc.get('url'):
            acc_name_html = f'<a href="{e(acc["url"])}" target="_blank" rel="noopener">{acc_name_html}</a>'
        acc_html = (f'<div class="acc-card"><div class="acc-name">Alloggio: {acc_name_html}</div>'
                    f'<div class="acc-detail">{e(acc["detail"])}</div></div>')
    tips_html = ''
    if day.get('tips'):
        tips_html = f'<div class="tip-card"><strong>Consiglio:</strong> {e(day["tips"])}</div>'

    culture_html = ''
    if day.get('culture'):
        culture_icon = f'<svg viewBox="0 0 64 56" xmlns="http://www.w3.org/2000/svg">{icon_svg("saga")}</svg>'
        culture_html = (f'<div class="culture-card"><div class="culture-card__label">{culture_icon}Storia &amp; curiosità</div>'
                         f'<p>{e(day["culture"])}</p></div>')

    hero_fname = f"{day['id']}-hero.jpg"

    return f'''
<section class="day-view page-view" id="view-{day['id']}" hidden>
  <div class="day-head">
    <div class="day-date">{e(day['dateLabel'])} · Giorno {day['num']}/8</div>
    <div class="day-title">{e(day['title'])}</div>
  </div>
  {photo_slot(hero_fname, day['title'], 'photo-slot--hero', HERO_ICON.get(day['id'], 'village'))}
  <div class="map-frame"><div class="day-map" id="day-map-{day['id']}"></div></div>
  <div class="line" style="margin:6px 0 0;font-size:12px;color:#7c8794;">Mappa reale (OpenStreetMap) — zoomabile e trascinabile. Percorso stradale indicativo (calcolato online); per la navigazione vera usa Google Maps offline.</div>
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
  <div class="aurora-note" data-aurora="{day['id']}">Calcolo delle ore di buio in corso…</div>
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

nav_items = ['<button class="nav-btn active" data-nav="info">Info</button>']
for d in days:
    label = d['dateLabel'].split(' ')[1] + ' ' + d['dateLabel'].split(' ')[2]
    nav_items.append(f'<button class="nav-btn" data-nav="{d["id"]}">{e(label)}</button>')
nav_items.append('<button class="nav-btn" data-nav="storia">Storia</button>')
nav_items.append('<button class="nav-btn" data-nav="checklist">Checklist</button>')
nav_html = ''.join(nav_items)

days_sections_html = ''.join(render_day_section(d) for d in days)

storia_html = f'''
<section class="page-view" id="view-storia" hidden>
  <div class="day-head">
    <div class="day-date">Infarinatura generale</div>
    <div class="day-title">Storia dell'Islanda</div>
  </div>
  {photo_slot('storia-hero.jpg', "Storia dell'Islanda", 'photo-slot--hero', 'saga')}

  <div class="panel">
    <div class="panel-title">Un'isola giovanissima</div>
    <div class="rune-rule"></div>
    <p class="line">L'Islanda entra nella storia scritta molto tardi rispetto al resto d'Europa: solo nell'<strong>874 d.C.</strong> il norvegese Ingólfur Arnarson fonda il primo insediamento permanente, proprio dove oggi sorge Reykjavík. Secondo l'usanza vichinga, aveva lanciato in mare i pilastri del suo trono cerimoniale e costruito casa dove le correnti li avevano portati a riva. Nei decenni successivi arrivano altre migliaia di coloni, soprattutto dalla Norvegia, insieme a genti e schiavi dalle isole britanniche: da questo mix nasce la popolazione islandese.</p>
  </div>

  <div class="panel">
    <div class="panel-title">Dal primo parlamento all'indipendenza</div>
    <div class="rune-rule"></div>
    <p class="line">Nel <strong>930 d.C.</strong>, a Þingvellir, i capi dell'isola fondano l'<strong>Alþingi</strong>: un'assemblea annuale all'aperto per fare leggi e giudicare le liti, una delle istituzioni parlamentari più antiche ancora esistenti al mondo. È l'epoca del cosiddetto Commonwealth islandese, senza re né esercito centrale. Nel 1262, dilaniata da faide interne, l'isola giura fedeltà al re di Norvegia; nel 1380 passa sotto la corona danese insieme alla Norvegia. Bisogna aspettare il <strong>1º dicembre 1918</strong> per un regno autonomo (ma ancora legato alla Danimarca), e il <strong>17 giugno 1944</strong> per la Repubblica islandese piena, proclamata con il 97% dei consensi mentre la Danimarca era sotto occupazione tedesca.</p>
  </div>

  <div class="culture-card">
    <div class="culture-card__label">{f'<svg viewBox="0 0 64 56" xmlns="http://www.w3.org/2000/svg">{icon_svg("saga")}</svg>'}Le saghe e una lingua rimasta ferma nel tempo</div>
    <p>Preparatevi a un piccolo miracolo linguistico: l'islandese di oggi è così vicino al norreno medievale che un lettore islandese può ancora leggere le saghe scritte otto secoli fa, senza traduzione — un lusso che i cugini scandinavi hanno perso da tempo. Altrettanto insolito è il sistema dei nomi: niente cognomi di famiglia, solo patronimici o matronimici (un Jónsson è "figlio di Jón"), tanto che l'elenco telefonico islandese è ordinato per nome di battesimo. La popolazione resta minuscola, poco più di 380.000 persone su un'isola grande quanto il Portogallo, con un effetto collaterale gradito: zero zanzare. Gli alberi invece scarseggiano, abbattuti in gran parte dai primi coloni per legna e pascoli.</p>
  </div>

  <div class="culture-card">
    <div class="culture-card__label">{f'<svg viewBox="0 0 64 56" xmlns="http://www.w3.org/2000/svg">{icon_svg("saga")}</svg>'}Troll, elfi e le luci del cielo</div>
    <p>La tradizione islandese abbonda di creature che spiegano il paesaggio prima ancora della geologia. I <strong>troll</strong> vivono nelle scogliere e nelle montagne ma temono la luce del sole: chi viene sorpreso all'alba resta pietrificato per sempre — da qui nascono formazioni come i faraglioni di Reynisfjara, che vedrete il Giorno 4. Accanto a loro vive un popolo più discreto, gli <strong>Huldufólk</strong> ("il popolo nascosto"): elfi che abitano rocce e colline e si mostrano solo quando lo scelgono loro. La credenza è ancora abbastanza radicata che alcuni progetti stradali islandesi siano stati deviati proprio per non disturbarli.</p>
  </div>

  <div class="panel">
    <div class="panel-title">Il paese del fuoco sotto il ghiaccio</div>
    <div class="rune-rule"></div>
    <p class="line">L'Islanda siede a cavallo della dorsale medio-atlantica, il punto dove le placche nordamericana ed eurasiatica si allontanano di circa 2 cm l'anno: la vedrete a occhio nudo a Þingvellir il Giorno 3. Questa posizione rende l'isola una delle zone vulcaniche più attive del pianeta, con oltre 30 sistemi vulcanici attivi. È lo stesso fuoco sotterraneo, imbrigliato, a rendere l'Islanda quasi autosufficiente: circa il 85% dell'energia del paese viene da fonti rinnovabili, soprattutto geotermia e idroelettrico — le stesse sorgenti calde che userete nelle terme in programma.</p>
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
<section class="page-view" id="view-checklist" hidden>
  <div class="day-head">
    <div class="day-date">Prima di partire</div>
    <div class="day-title">Checklist</div>
  </div>

  <div class="panel">
    <div class="panel-title">Quanto manca</div>
    <div class="rune-rule"></div>
    <div class="line" id="chk-progress">Caricamento…</div>
  </div>

  {checklist_groups_html}

  <div class="tip-card">
    <strong>Colonnine di benzina:</strong> in Islanda sono quasi tutte self-service e chiedono una carta con PIN attivo (niente carte prepagate senza PIN o solo contactless). Se avete una carta di credito o debito normale con PIN funziona senza problemi — verificate solo di avere il PIN a mente prima di partire.
  </div>
</section>'''

sun_fallback_js = json.dumps(sun_fallback, ensure_ascii=False)
seasonal_js = json.dumps(seasonal, ensure_ascii=False)
locations_js = json.dumps(locations, ensure_ascii=False)
day_routes_js = json.dumps(map_points, ensure_ascii=False)
days_meta_js = json.dumps(
    [{'id': d['id'], 'dateISO': d['dateISO'], 'locKey': d['locKey']} for d in days],
    ensure_ascii=False
)

WEATHER_CODES_JS = """{0:'Sereno',1:'Prevalentemente sereno',2:'Parzialmente nuvoloso',3:'Nuvoloso',45:'Nebbia',48:'Nebbia con brina',51:'Pioviggine leggera',53:'Pioviggine',55:'Pioviggine intensa',56:'Pioviggine gelata',57:'Pioviggine gelata intensa',61:'Pioggia leggera',63:'Pioggia',65:'Pioggia intensa',66:'Pioggia gelata',67:'Pioggia gelata intensa',71:'Neve leggera',73:'Neve',75:'Neve intensa',77:'Granelli di neve',80:'Rovesci leggeri',81:'Rovesci',82:'Rovesci forti',85:'Rovesci di neve leggeri',86:'Rovesci di neve forti',95:'Temporale'}"""

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
:root {{
  --ink:#1c2b3a; --paper:#f2ede2; --panel:#faf7f0; --panel-border:#ddd5c4;
  --navy:#16263b; --navy-2:#101d2d; --amber:#b5673a; --amber-2:#8f4d29;
  --amber-soft:#f0d9b8; --amber-soft-border:#d9b487;
  --teal:#2c4a55; --teal-soft:#dcecee; --teal-border:#8fb9bf;
  --green-soft:#dcefdd; --green-border:#8fc79a; --green-text:#2c6b3a;
  --muted:#5a6675; --muted-2:#7c8794;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--paper); color:var(--ink); font-family:'IBM Plex Sans',-apple-system,sans-serif; -webkit-font-smoothing:antialiased; }}
a {{ color:var(--amber); }}
::-webkit-scrollbar {{ height:6px; width:6px; }}
::-webkit-scrollbar-thumb {{ background:#c9c0ac; border-radius:4px; }}
.rune-rule {{ height:1px; background:linear-gradient(90deg,transparent,#c9b98f,transparent); position:relative; margin:4px 0 14px; }}
.rune-rule::after {{ content:''; position:absolute; left:50%; top:50%; width:6px; height:6px; background:var(--amber); transform:translate(-50%,-50%) rotate(45deg); }}

.hero {{ position:relative; overflow:hidden; background:linear-gradient(160deg,var(--navy),var(--navy-2)); border-bottom:3px solid var(--amber); }}
.hero__scrim {{ position:absolute; inset:0; background:linear-gradient(180deg,rgba(16,29,45,.15),rgba(12,20,32,.9)); }}
.hero__inner {{ position:relative; max-width:820px; margin:0 auto; padding:30px 20px 18px; }}
.hero__eyebrow {{ font-size:11px; font-weight:600; letter-spacing:.18em; text-transform:uppercase; color:#e0ab7f; margin-bottom:6px; }}
.hero__title {{ font-family:'Cinzel',serif; font-weight:600; font-size:30px; line-height:1.15; color:#faf5ea; letter-spacing:.01em; }}
.hero__sub {{ font-size:13px; color:#cfd3d8; margin-top:8px; }}

.navbar {{ position:sticky; top:0; z-index:10; background:var(--navy); border-bottom:1px solid #26374a; box-shadow:0 2px 10px rgba(0,0,0,.25); }}
.navbar__inner {{ max-width:820px; margin:0 auto; display:flex; gap:8px; overflow-x:auto; padding:10px 20px; -webkit-overflow-scrolling:touch; }}
.nav-btn {{ flex-shrink:0; padding:10px 16px; min-height:24px; border-radius:5px; font-size:13px; font-weight:600; border:1px solid #3a4a5c; background:transparent; color:#c7ccd2; cursor:pointer; font-family:'IBM Plex Sans',sans-serif; }}
.nav-btn.active {{ border-color:#d9985f; background:var(--amber); color:#fffaf2; }}

main {{ max-width:820px; margin:0 auto; padding:20px 20px 70px; display:flex; flex-direction:column; gap:18px; }}
.panel {{ background:var(--panel); border:1px solid var(--panel-border); border-radius:8px; padding:18px 20px; }}
.panel-title {{ font-family:'Cinzel',serif; font-weight:600; font-size:15px; letter-spacing:.06em; text-transform:uppercase; color:#2c3c4d; margin-bottom:4px; }}
.panel p, .panel div.line {{ font-size:14px; line-height:1.8; color:#333c46; }}
.warn-box {{ margin-top:12px; background:var(--amber-soft); border:1px solid var(--amber-soft-border); border-radius:6px; padding:12px 14px; font-size:13px; line-height:1.6; color:#5c3a1f; }}
.stay-row {{ border-top:1px solid #e4ddcb; padding-top:10px; font-size:14px; }}
.stay-row:first-child {{ border-top:none; padding-top:0; }}
.stay-name {{ font-weight:600; color:#28323e; }}
.stay-detail {{ color:#576270; font-size:13px; margin-top:2px; }}
.stack {{ display:flex; flex-direction:column; gap:10px; }}

.aurora-panel {{ background:var(--navy); border-radius:8px; padding:18px 20px; }}
.aurora-panel .panel-title {{ color:#8fd6cd; }}
.aurora-panel p {{ color:#c7ccd2; }}
.kp-row {{ display:flex; align-items:baseline; gap:10px; margin-top:6px; }}
.kp-big {{ font-family:'Cinzel',serif; font-weight:600; font-size:30px; color:#faf5ea; }}
.kp-status {{ font-size:13px; color:#c7ccd2; }}

.fx-row {{ display:flex; align-items:flex-end; gap:10px; }}
.fx-field {{ flex:1; display:flex; flex-direction:column; gap:4px; }}
.fx-field label {{ font-size:11px; font-weight:600; letter-spacing:.04em; text-transform:uppercase; color:var(--muted-2); }}
.fx-field input {{ font-family:'IBM Plex Sans',sans-serif; font-size:16px; font-weight:600; color:var(--ink); background:var(--paper); border:1px solid var(--panel-border); border-radius:6px; padding:9px 10px; width:100%; }}
.fx-field input:focus-visible {{ outline:2px solid var(--amber); outline-offset:1px; }}
.fx-arrow {{ font-size:15px; color:var(--muted-2); padding-bottom:10px; }}
.fx-rate {{ margin-top:10px; font-size:12px; color:var(--muted-2); }}

.chk-list {{ display:flex; flex-direction:column; gap:2px; }}
.chk-item {{ display:flex; align-items:flex-start; gap:10px; padding:9px 4px; font-size:14px; line-height:1.5; color:#333c46; cursor:pointer; border-radius:6px; }}
.chk-item:hover {{ background:rgba(0,0,0,.03); }}
.chk-box {{ margin-top:3px; width:18px; height:18px; flex-shrink:0; accent-color:var(--amber); }}
.chk-item:has(.chk-box:checked) span {{ color:var(--muted-2); text-decoration:line-through; text-decoration-color:var(--amber-soft-border); }}

.countdown-banner {{ background:transparent; text-align:center; padding:14px 20px 6px; margin-top:4px; }}
.countdown-banner__big {{ font-family:'Cinzel',serif; font-weight:600; font-size:26px; color:var(--navy); }}
.countdown-banner__sub {{ font-size:12px; color:#7c8794; margin-top:4px; }}
.aurora-panel .more {{ font-size:13px; line-height:1.6; margin-top:10px; color:#c7ccd2; }}
.aurora-panel .more a {{ color:#8fd6cd; }}

.photo-slot {{ position:relative; overflow:hidden; background:linear-gradient(135deg,var(--bg1,#3a2f22),var(--bg2,#5c4a33)); border-radius:8px; }}
.photo-slot img {{ width:100%; height:100%; object-fit:cover; display:block; }}
.photo-slot__ph {{ position:absolute; inset:0; display:none; flex-direction:column; align-items:center; justify-content:center; gap:6px; color:#e4dcc8; text-align:center; padding:10px; }}
.photo-slot__icon {{ width:56px; height:44px; opacity:.95; }}
.photo-slot__ph span {{ font-size:11px; font-weight:600; letter-spacing:.02em; max-width:88%; color:#d9d0ba; }}
.photo-slot--empty img {{ display:none; }}
.photo-slot--empty .photo-slot__ph {{ display:flex; }}
.photo-slot--hero {{ width:100%; height:180px; }}
.photo-slot--hero .photo-slot__icon {{ width:74px; height:58px; }}
.photo-slot--hero .photo-slot__ph span {{ font-size:13px; }}
.photo-slot--thumb {{ width:92px; height:92px; flex-shrink:0; }}
.photo-slot--thumb .photo-slot__icon {{ width:34px; height:26px; }}
.photo-slot--thumb .photo-slot__ph span {{ font-size:8.5px; line-height:1.2; }}
.photo-slot--cover {{ position:absolute; inset:0; opacity:.55; border-radius:0; }}
.photo-slot--cover .photo-slot__ph span {{ display:none; }}
.photo-slot--cover .photo-slot__icon {{ width:110px; height:86px; }}

.day-head .day-date {{ font-size:12px; color:var(--amber); font-weight:700; text-transform:uppercase; letter-spacing:.08em; }}
.day-head .day-title {{ font-family:'Cinzel',serif; font-weight:600; font-size:25px; margin-top:6px; color:#1f2c39; letter-spacing:.005em; }}

.map-frame {{ border-radius:8px; overflow:hidden; border:2px solid var(--navy); box-shadow:0 4px 16px rgba(0,0,0,.12); line-height:0; height:260px; }}
.map-frame .route-map {{ width:100%; height:auto; display:block; }}
.day-map {{ width:100%; height:100%; background:#16263b; }}

.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
.info-card {{ background:var(--panel); border:1px solid var(--panel-border); border-radius:8px; padding:16px; }}
.info-card__label {{ font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.06em; color:#5a6675; margin-bottom:8px; }}
.info-card__big {{ font-family:'Cinzel',serif; font-weight:600; font-size:20px; color:#28323e; }}
.info-card__sub {{ font-size:13px; color:#3a4351; margin-top:4px; }}
.info-card__source {{ font-size:11px; color:#7c8794; margin-top:8px; }}
.sun-line {{ font-size:14px; line-height:1.7; color:#28323e; }}

.aurora-note {{ background:var(--teal-soft); border:1px solid var(--teal-border); border-radius:8px; padding:14px 16px; font-size:13px; line-height:1.6; color:#1e3038; }}
.aurora-note strong {{ color:var(--teal); }}

.section-title {{ font-family:'Cinzel',serif; font-weight:600; font-size:16px; margin-bottom:8px; color:#2c3c4d; letter-spacing:.02em; }}

.leg {{ background:var(--panel); border:1px solid var(--panel-border); border-left:3px solid var(--amber); border-radius:6px; padding:12px 14px; font-size:13px; }}
.leg-route {{ font-weight:600; color:#28323e; }}
.leg-meta {{ color:#576270; margin-top:2px; }}
.leg-note {{ color:#3a4351; margin-top:4px; }}

.act-card {{ background:var(--panel); border:1px solid var(--panel-border); border-radius:8px; padding:14px 16px; display:flex; gap:14px; }}
.act-body {{ flex:1; min-width:0; }}
.act-top {{ display:flex; justify-content:space-between; gap:10px; align-items:baseline; }}
.act-title {{ font-weight:600; font-size:14px; color:#1f2c39; }}
.act-title--link {{ text-decoration:none; border-bottom:1px dashed var(--navy); padding-bottom:1px; }}
.act-title--link:hover {{ border-bottom-style:solid; }}
.act-title-arrow {{ font-weight:400; color:var(--amber); font-size:12px; }}
.act-time {{ font-size:12px; color:#7c8794; white-space:nowrap; }}
.act-desc {{ font-size:13px; color:#3a4351; margin-top:6px; line-height:1.6; }}
.act-cost {{ display:inline-block; margin-top:8px; background:var(--amber-soft); border:1px solid var(--amber-soft-border); border-radius:5px; padding:3px 9px; font-size:12px; color:#5c3a1f; }}
.act-link {{ display:block; margin-top:8px; font-size:12.5px; font-weight:600; color:var(--navy); text-decoration:none; }}
.act-link:hover {{ text-decoration:underline; }}

.food-card {{ background:var(--panel); border:1px solid var(--panel-border); border-radius:6px; padding:12px 14px; font-size:13px; }}
.food-top {{ display:flex; justify-content:space-between; gap:10px; color:#28323e; }}
.food-cost {{ color:#7c8794; white-space:nowrap; }}
.food-note {{ color:#4a5361; margin-top:4px; }}
.gf-badge {{ display:inline-block; margin-top:6px; background:var(--green-soft); border:1px solid var(--green-border); border-radius:5px; padding:2px 8px; font-size:11px; color:var(--green-text); }}

.acc-card {{ background:var(--navy); border-radius:8px; padding:14px 16px; font-size:13px; }}
.acc-name {{ font-weight:600; color:#f2ede2; }}
.acc-name a {{ color:inherit; text-decoration:underline; text-underline-offset:2px; }}
.acc-name a:hover {{ color:var(--amber); }}
.acc-detail {{ color:#c7ccd2; margin-top:2px; }}

.tip-card {{ background:var(--amber-soft); border:1px solid var(--amber-soft-border); border-radius:8px; padding:12px 14px; font-size:13px; line-height:1.6; color:#5c3a1f; }}

.culture-card {{ background:var(--teal-soft); border:1px solid var(--teal-border); border-radius:8px; padding:14px 16px; }}
.culture-card__label {{ font-family:'Cinzel',serif; font-weight:600; font-size:13px; letter-spacing:.03em; color:var(--teal); margin-bottom:6px; display:flex; align-items:center; gap:6px; }}
.culture-card__label svg {{ width:15px; height:15px; flex-shrink:0; }}
.culture-card p {{ margin:0; font-size:13.5px; line-height:1.65; color:#22404a; }}

.section {{ display:flex; flex-direction:column; gap:8px; }}

.install-hint {{ font-size:12px; color:#7c8794; text-align:center; padding:6px 20px 0; }}</style>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
</head>
<body>

<div class="hero">
  {photo_slot('cover.jpg', 'Islanda 2026', 'photo-slot--cover', 'saga')}
  <div class="hero__scrim"></div>
  <div class="hero__inner">
    <div class="hero__eyebrow">Saga di viaggio</div>
    <div class="hero__title">ISLANDA 2026</div>
    <div class="hero__sub">Federica &amp; Michele · 15–22 novembre · Reykjavík → Vík → Flúðir</div>
  </div>
</div>

<div class="navbar"><div class="navbar__inner">{nav_html}</div></div>

<main>

<section id="view-info" class="page-view">
  <div class="countdown-banner">
    <div class="countdown-banner__big" id="countdown-big">…</div>
    <div class="countdown-banner__sub" id="countdown-sub"></div>
  </div>

  <div class="aurora-panel">
    <div class="panel-title">Aurora boreale — ora</div>
    <p>Indice geomagnetico Kp attuale (NOAA), aggiornato in tempo reale se sei online. Non è una previsione per le date del viaggio, ma dà l'idea dell'attività del momento.</p>
    <div class="kp-row"><div class="kp-big" id="kp-value">…</div><div class="kp-status" id="kp-status">Caricamento…</div></div>
    <div class="more">Più vicino alla partenza, controlla <a href="https://en.vedur.is/weather/forecasts/aurora/" target="_blank" rel="noopener">vedur.is/aurora</a> per la previsione reale sulle vostre date e sul cielo sereno.</div>
  </div>

  <div class="panel">
    <div class="panel-title">Mappa del viaggio</div>
    <div class="rune-rule"></div>
    <div id="trip-map" style="height:260px;border-radius:8px;overflow:hidden;border:2px solid var(--navy);box-shadow:0 4px 16px rgba(0,0,0,.12);"></div>
    <div class="line" style="margin-top:10px;font-size:12px;color:#7c8794;">Mappa reale (OpenStreetMap) — zoomabile e trascinabile. Tocca un marker per il nome della tappa. Per la navigazione stradale vera e propria usa Google Maps offline.</div>
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
    <div class="line">• Le stazioni N1 hanno zuppe e hot dog a buon prezzo lungo il Ring Road.</div>
    <div class="line">• L'acqua del rubinetto è potabile ovunque: niente acqua in bottiglia.</div>
    <div class="line">• Cerca la parola <strong>"glútenlaus"</strong> o <strong>"glútenfrítt"</strong> (senza glutine) sui menu — molti locali islandesi la indicano chiaramente.</div>
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
    <div class="line">• Le mappe di questa pagina sono schizzi del percorso (funzionano sempre, anche offline) ma non sono per la navigazione stradale vera e propria. Per guidare, scarica prima di partire le mappe offline di Google Maps (o Maps.me / Organic Maps) per Islanda.</div>
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
    <div class="line">• <strong>The Hill Hotel (Flúðir, Giorni 6-7):</strong> <a href="tel:+3544864430">+354 486 4430</a></div>
    <div class="line" style="margin-top:6px;font-size:12px;color:#7c8794;">Numeri trovati via ricerca online, non verificati con una chiamata diretta: ricontrollateli nelle email di conferma prima di partire.</div>
  </div>
</section>

{days_sections_html}

{storia_html}

{checklist_html}

</main>

<script>
const SEASONAL = {seasonal_js};
const LOCATIONS = {locations_js};
const DAY_ROUTES = {day_routes_js};
const SUN_FALLBACK = {sun_fallback_js};
const DAYS_META = {days_meta_js};
const WEATHER_CODES = {WEATHER_CODES_JS};

const state = {{ weather:{{}}, sun:{{}}, kp:null, kpStatus:'loading' }};

const dayMaps = {{}};

function ensureDayMap(dayId) {{
  const el = document.getElementById('day-map-' + dayId);
  const points = DAY_ROUTES[dayId];
  if (!el || !points || !points.length || typeof L === 'undefined') return;
  if (dayMaps[dayId]) {{ requestAnimationFrame(() => dayMaps[dayId].invalidateSize()); return; }}

  const map = L.map(el, {{ scrollWheelZoom: false, zoomControl: true }});
  dayMaps[dayId] = map;
  L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions" target="_blank" rel="noopener">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19,
    crossOrigin: true
  }}).addTo(map);

  const latlngs = points.map(p => [p.lat, p.lon]);

  const seen = {{}};
  let seq = 0;
  points.forEach((p, i) => {{
    const key = p.lat.toFixed(3) + ',' + p.lon.toFixed(3);
    if (!(key in seen)) {{ seq++; seen[key] = seq; }}
    const n = seen[key];
    const isEnd = i === 0 || i === points.length - 1;
    const size = isEnd ? 26 : 20;
    const bg = isEnd ? '#b5673a' : '#f2ede2';
    const icon = L.divIcon({{
      className: '',
      html: '<div style="width:' + size + 'px;height:' + size + 'px;border-radius:50%;background:' + bg + ';' +
            'border:2px solid #16263b;display:flex;align-items:center;justify-content:center;' +
            'font:700 11px \\'IBM Plex Sans\\',sans-serif;color:#16263b;">' + n + '</div>',
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2]
    }});
    L.marker([p.lat, p.lon], {{ icon }}).addTo(map).bindPopup(p.name);
  }});

  map.fitBounds(latlngs, {{ padding: [24, 24] }});

  const fallback = L.polyline(latlngs, {{ color: '#4f8fa8', weight: 3, dashArray: '1,9', lineCap: 'round', opacity: 0.9 }}).addTo(map);

  const coordStr = points.map(p => p.lon + ',' + p.lat).join(';');
  fetch('https://router.project-osrm.org/route/v1/driving/' + coordStr + '?overview=full&geometries=geojson')
    .then(r => r.ok ? r.json() : Promise.reject())
    .then(data => {{
      const route = data.routes && data.routes[0];
      if (!route) return;
      const coords = route.geometry.coordinates.map(c => [c[1], c[0]]);
      map.removeLayer(fallback);
      L.polyline(coords, {{ color: '#d9985f', weight: 4, opacity: 0.9, lineCap: 'round' }}).addTo(map);
    }})
    .catch(() => {{ /* resta la linea retta di riserva */ }});

  el.addEventListener('touchstart', () => map.scrollWheelZoom.enable(), {{ once: true, passive: true }});
}}

function setActive(id) {{
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.toggle('active', b.dataset.nav === id));
  document.querySelectorAll('.page-view').forEach(el => {{ el.hidden = el.id !== 'view-' + id; }});
  if (DAYS_META.some(d => d.id === id)) ensureDayMap(id);
  window.scrollTo({{ top: 0, behavior: 'instant' in window ? 'instant' : 'auto' }});
}}
document.querySelectorAll('.nav-btn').forEach(btn => {{
  btn.addEventListener('click', () => setActive(btn.dataset.nav));
}});

function weatherFor(day) {{
  const live = state.weather[day.locKey];
  if (live && live.time) {{
    const idx = live.time.indexOf(day.dateISO);
    if (idx >= 0) {{
      const code = live.weathercode[idx];
      return {{
        temp: Math.round(live.temperature_2m_max[idx]) + '° / ' + Math.round(live.temperature_2m_min[idx]) + '°C',
        desc: WEATHER_CODES[code] || 'Variabile',
        source: 'Previsione live (aggiornata automaticamente)'
      }};
    }}
  }}
  const s = SEASONAL[day.locKey];
  return {{
    temp: '~' + s.tmax + '° / ~' + s.tmin + '°C',
    desc: s.desc + ' · vento ' + s.wind,
    source: 'Media stagionale tipica di novembre — offline o previsione non ancora disponibile (appare da ~16 giorni prima)'
  }};
}}

function renderWeatherAndSun() {{
  DAYS_META.forEach(day => {{
    const w = weatherFor(day);
    const tempEl = document.querySelector('[data-weather-temp="' + day.id + '"]');
    const descEl = document.querySelector('[data-weather-desc="' + day.id + '"]');
    const srcEl = document.querySelector('[data-weather-source="' + day.id + '"]');
    if (tempEl) tempEl.textContent = w.temp;
    if (descEl) descEl.textContent = w.desc;
    if (srcEl) srcEl.textContent = w.source;

    const live = state.sun[day.id];
    const fb = SUN_FALLBACK[day.id];
    const sr = live ? live.sunrise : fb.sunrise;
    const ss = live ? live.sunset : fb.sunset;
    const dl = live ? live.daylight : fb.daylight + ' (stima)';
    const srEl = document.querySelector('[data-sunrise="' + day.id + '"]');
    const ssEl = document.querySelector('[data-sunset="' + day.id + '"]');
    const dlEl = document.querySelector('[data-daylight="' + day.id + '"]');
    if (srEl) srEl.textContent = sr;
    if (ssEl) ssEl.textContent = ss;
    if (dlEl) dlEl.textContent = dl + ' di luce';

    const auroraEl = document.querySelector('[data-aurora="' + day.id + '"]');
    if (auroraEl) {{
      auroraEl.innerHTML = '<strong>Aurora:</strong> Buio da ' + ss + ' a ' + sr + ' del giorno dopo — finestra ampia. Novembre è piena stagione aurora: serve cielo sereno e attività geomagnetica. Controlla vedur.is/aurora nei giorni prima.';
    }}
  }});
}}
renderWeatherAndSun();

async function fetchAllWeather() {{
  for (const key of Object.keys(LOCATIONS)) {{
    const loc = LOCATIONS[key];
    try {{
      const url = 'https://api.open-meteo.com/v1/forecast?latitude=' + loc.lat + '&longitude=' + loc.lon + '&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=UTC&forecast_days=16';
      const res = await fetch(url);
      const json = await res.json();
      if (json && json.daily) {{ state.weather[key] = json.daily; renderWeatherAndSun(); }}
    }} catch (e) {{ /* resta sulla stima stagionale */ }}
  }}
}}

async function fetchAllSun() {{
  for (const day of DAYS_META) {{
    const loc = LOCATIONS[day.locKey];
    try {{
      const url = 'https://api.sunrise-sunset.org/json?lat=' + loc.lat + '&lng=' + loc.lon + '&date=' + day.dateISO + '&formatted=0';
      const res = await fetch(url);
      const json = await res.json();
      if (json && json.results) {{
        const sr = new Date(json.results.sunrise);
        const ss = new Date(json.results.sunset);
        const fmt = d => String(d.getUTCHours()).padStart(2,'0') + ':' + String(d.getUTCMinutes()).padStart(2,'0');
        const lenSec = json.results.day_length;
        const h = Math.floor(lenSec/3600), m = Math.round((lenSec%3600)/60);
        state.sun[day.id] = {{ sunrise: fmt(sr), sunset: fmt(ss), daylight: h + 'h ' + String(m).padStart(2,'0') + 'm' }};
        renderWeatherAndSun();
      }}
    }} catch (e) {{ /* resta sulla stima calcolata offline */ }}
  }}
}}

async function fetchKp() {{
  try {{
    const res = await fetch('https://services.swpc.noaa.gov/json/planetary_k_index_1m.json');
    const json = await res.json();
    const last = json[json.length - 1];
    state.kp = Math.round(last.kp_index * 10) / 10;
    state.kpStatus = 'ok';
    state.kpAt = new Date();
  }} catch (e) {{ state.kpStatus = 'error'; }}
  document.getElementById('kp-value').textContent = state.kpStatus === 'ok' ? ('Kp ' + state.kp) : '—';
  let kpText;
  if (state.kpStatus === 'ok') {{
    const t = state.kpAt;
    const hh = String(t.getHours()).padStart(2, '0') + ':' + String(t.getMinutes()).padStart(2, '0');
    kpText = (state.kp >= 4 ? 'Attività alta' : 'Attività bassa/moderata')
           + (navigator.onLine ? ' · aggiornato alle ' + hh : ' · ultimo dato salvato, sei offline');
  }} else {{
    kpText = 'Dato non disponibile offline';
  }}
  document.getElementById('kp-status').textContent = kpText;
}}

const FX_FALLBACK_RATE = 145.5; // stima approssimativa EUR->ISK, usata se offline
let fxRate = FX_FALLBACK_RATE;

function fxUpdateFrom(source) {{
  const eurEl = document.getElementById('fx-eur');
  const iskEl = document.getElementById('fx-isk');
  if (!eurEl || !iskEl) return;
  if (source === 'eur') {{
    const eur = parseFloat(eurEl.value);
    iskEl.value = isFinite(eur) ? Math.round(eur * fxRate) : '';
  }} else {{
    const isk = parseFloat(iskEl.value);
    eurEl.value = isFinite(isk) ? Math.round((isk / fxRate) * 100) / 100 : '';
  }}
}}

function fxSetup() {{
  const eurEl = document.getElementById('fx-eur');
  const iskEl = document.getElementById('fx-isk');
  if (!eurEl || !iskEl) return;
  eurEl.addEventListener('input', () => fxUpdateFrom('eur'));
  iskEl.addEventListener('input', () => fxUpdateFrom('isk'));
  fxUpdateFrom('eur');
}}
fxSetup();

async function fetchFxRate() {{
  const label = document.getElementById('fx-rate-label');
  // La BCE (e quindi Frankfurter, che ne replica i tassi) non pubblica un
  // cambio per la corona islandese: usiamo open.er-api.com, gratuita e
  // senza chiave, che copre l'ISK.
  try {{
    const res = await fetch('https://open.er-api.com/v6/latest/EUR');
    const json = await res.json();
    if (json && json.result === 'success' && json.rates && json.rates.ISK) {{
      fxRate = json.rates.ISK;
      const when = json.time_last_update_utc ? new Date(json.time_last_update_utc) : new Date();
      const hh = String(when.getHours()).padStart(2, '0') + ':' + String(when.getMinutes()).padStart(2, '0');
      if (label) label.textContent = '1 € \\u2248 ' + fxRate.toFixed(1) + ' ISK \\u00b7 aggiornato alle ' + hh;
      fxUpdateFrom('eur');
      return;
    }}
    throw new Error('no rate');
  }} catch (e) {{
    if (label) label.textContent = '1 € \\u2248 ' + FX_FALLBACK_RATE.toFixed(1) + ' ISK \\u00b7 stima offline, verifica il tasso reale prima di partire';
  }}
}}

function initTripMap() {{
  const el = document.getElementById('trip-map');
  if (!el || typeof L === 'undefined') return;

  const stops = [
    {{ key: 'keflavik', label: 'Keflavík (aeroporto)', n: '1' }},
    {{ key: 'reykjavik', label: 'Reykjavík', n: '2' }},
    {{ key: 'vik', label: 'Vík í Mýrdal', n: '3' }},
    {{ key: 'fludir', label: 'Flúðir', n: '4' }}
  ];

  const map = L.map(el, {{ scrollWheelZoom: false, zoomControl: true }});
  L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions" target="_blank" rel="noopener">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19,
    crossOrigin: true
  }}).addTo(map);

  const latlngs = stops.map(s => [LOCATIONS[s.key].lat, LOCATIONS[s.key].lon]);

  L.polyline(latlngs, {{
    color: '#d9985f',
    weight: 3,
    dashArray: '1,9',
    lineCap: 'round'
  }}).addTo(map);

  stops.forEach(s => {{
    const loc = LOCATIONS[s.key];
    const icon = L.divIcon({{
      className: '',
      html: '<div style="width:26px;height:26px;border-radius:50%;background:#b5673a;border:2px solid #16263b;' +
            'display:flex;align-items:center;justify-content:center;font:700 12px \\'IBM Plex Sans\\',sans-serif;color:#16263b;">' + s.n + '</div>',
      iconSize: [26, 26],
      iconAnchor: [13, 13]
    }});
    L.marker([loc.lat, loc.lon], {{ icon }}).addTo(map).bindPopup(s.label);
  }});

  map.fitBounds(latlngs, {{ padding: [24, 24] }});

  el.addEventListener('touchstart', () => map.scrollWheelZoom.enable(), {{ once: true, passive: true }});
}}

// Aggiornamento dei dati live (alba/tramonto, aurora, meteo, cambio).
// Le fetch vengono tentate sempre: se sei offline il service worker
// risponde con l'ultimo dato valido salvato in cache.
let lastLiveRefresh = 0;
function refreshLiveData(force) {{
  const now = Date.now();
  if (!force && now - lastLiveRefresh < 60000) return;
  lastLiveRefresh = now;
  fetchAllSun();
  fetchKp();
  fetchAllWeather();
  fetchFxRate();
}}

// Al ritorno della connessione, e quando si torna sull'app dopo averla
// lasciata in background (tipico della PWA sul telefono).
window.addEventListener('online', () => refreshLiveData(true));
document.addEventListener('visibilitychange', () => {{
  if (document.visibilityState === 'visible') refreshLiveData(false);
}});

function updateCountdown() {{
  const bigEl = document.getElementById('countdown-big');
  const subEl = document.getElementById('countdown-sub');
  if (!bigEl || !DAYS_META.length) return;
  const start = new Date(DAYS_META[0].dateISO + 'T00:00:00');
  const end = new Date(DAYS_META[DAYS_META.length - 1].dateISO + 'T23:59:59');
  const now = new Date();
  if (now < start) {{
    const days = Math.ceil((start - now) / 86400000);
    bigEl.textContent = days === 1 ? 'Manca 1 giorno' : ('Mancano ' + days + ' giorni');
    subEl.textContent = "alla partenza per l'Islanda";
  }} else if (now <= end) {{
    const dayNum = Math.min(Math.floor((now - start) / 86400000) + 1, DAYS_META.length);
    bigEl.textContent = 'Siete in viaggio!';
    subEl.textContent = 'Giorno ' + dayNum + ' di ' + DAYS_META.length;
  }} else {{
    bigEl.textContent = 'Bentornati!';
    subEl.textContent = "Il viaggio in Islanda è finito \\u2014 che ricordo dev'essere stato.";
  }}
}}
updateCountdown();
setInterval(updateCountdown, 3600000);

const CHK_STORAGE_KEY = 'islanda2026-checklist';
function loadChecklist() {{
  try {{
    const raw = localStorage.getItem(CHK_STORAGE_KEY);
    return raw ? JSON.parse(raw) : {{}};
  }} catch (e) {{ return {{}}; }}
}}
function saveChecklist(state) {{
  try {{ localStorage.setItem(CHK_STORAGE_KEY, JSON.stringify(state)); }} catch (e) {{ /* storage non disponibile */ }}
}}
function updateChecklistProgress() {{
  const boxes = document.querySelectorAll('.chk-box');
  const el = document.getElementById('chk-progress');
  if (!el || !boxes.length) return;
  const total = boxes.length;
  const checked = document.querySelectorAll('.chk-box:checked').length;
  el.textContent = checked + ' su ' + total + ' completati'
    + (checked === total ? ' \\u2014 pronti per partire!' : '');
}}
function setupChecklist() {{
  const boxes = document.querySelectorAll('.chk-box');
  if (!boxes.length) return;
  const saved = loadChecklist();
  boxes.forEach((box) => {{
    const id = box.dataset.chkId;
    if (saved[id]) box.checked = true;
    box.addEventListener('change', () => {{
      const state = loadChecklist();
      state[id] = box.checked;
      saveChecklist(state);
      updateChecklistProgress();
    }});
  }});
  updateChecklistProgress();
}}
setupChecklist();

refreshLiveData(true);
initTripMap();

if ('serviceWorker' in navigator) {{
  window.addEventListener('load', () => {{
    navigator.serviceWorker.register('sw.js').catch(() => {{}});
  }});
}}
</script>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_out)

print('index.html written,', len(html_out), 'bytes')
