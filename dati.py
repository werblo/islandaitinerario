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
        'Costume da bagno (per Fontana e Secret Lagoon)',
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
    {'name': 'Hótel Búrfell', 'detail': 'Vík í Mýrdal · 18–20 nov (2 notti)'},
    {'name': 'The Hill Guesthouse', 'detail': 'Flúðir · 20–22 nov (2 notti)'}
]

days = [
 {'id':'d1','num':1,'dateISO':'2026-11-15','dateLabel':'Dom 15 nov','title':'Arrivo & Reykjavík','locKey':'reykjavik',
  'legs':[
    {'from':'Aeroporto di Keflavík','to':'Ufficio FairCar','km':3,'time':'~10 min (navetta inclusa)','note':'Atterraggio 10:35 · ritiro auto previsto 11:00'},
    {'from':'Keflavík','to':'Reykjavík','km':48,'time':'~45 min','note':'Strada 41 diretta per Reykjavík: check-in all\'appartamento alle 15:00'}
  ],
  'activities':[
    {'time':'11:00','title':'Ritiro auto 4x4','desc':'FairCar, Bogatröð 1, Keflavík. Portare patente, carta di credito intestata al conducente e voucher stampato o digitale.','cost':None},
    {'time':'15:00','title':'Check-in appartamento','desc':"46heima Boutique Apartments, Laugavegur 46. Codice d'accesso via email prima dell'arrivo.",'cost':None},
    {'time':'16:30','title':'Passeggiata nel centro','desc':'Laugavegur, Hallgrímskirkja (belvedere sulla torre: in inverno chiude nel tardo pomeriggio, verificate l\'orario e andateci per prima), porto vecchio, Sun Voyager.','cost':'gratis','nav':'Laugavegur Reykjavik'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Bónus (supermercato) o hot dog da Bæjarins Beztu','note':'Il würstel senza pane non è garantito senza glutine: per un pranzo sicuro meglio il Bónus (prodotti "glútenlaust")','cost':'€','gf':False},
    {'meal':'Cena','place':'Brass Kitchen & Bar, Laugavegur 66','note':'A 200 m dall\'appartamento, adatto ai celiaci: friggitrice dedicata, fish & chips, hamburger e pane senza glutine. Alternative vicine: Harry\'s Seafood and Grill (Laugavegur 85, menu senza glutine) e Old Iceland (Laugavegur 72). Segnalate comunque la celiachia','cost':'€€','gf':True}
  ],
  'accommodation':{'name':'46heima Boutique Apartments','detail':'Laugavegur 46, Reykjavík · 3 notti · check-in dalle 15:00','url':'https://www.booking.com/hotel/is/46heima-apartments.en-gb.html'},
  'tips':"Giornata di arrivo tranquilla: sistematevi con calma e fate un po' di spesa in un Bónus per i giorni successivi. Avrete un paio di soste alle terme nel resto del viaggio, più economiche e meno turistiche della Blue Lagoon. Parcheggio: l'appartamento non ne ha uno incluso e Laugavegur è zona P1 (~650 ISK/h, max 3h consecutive), gratis dalle 21:00 alle 9:00 nei feriali/sabato e prima delle 10:00/dopo le 21:00 la domenica (orari da riconfermare su reykjavik.is/en/parking vicino alla partenza). Strategia notte per notte: 15 e 16 novembre parcheggiate in zona P2 verso Hlemmur/Rauðarárstígur (~230 ISK/h, senza limite di 3h, più economica se rientrate prima delle 21:00); la notte del 17 invece va bene direttamente P1 sotto casa, perché quella sera rientrerete da Fontana dopo le 21:00 (quando è già gratis anche lì) e ripartirete presto il mattino dopo per la Costa Sud.",
  'culture':"Reykjavík ha una storia più antica di quanto sembri: fondata nell'874 d.C. da Ingólfur Arnarson, primo colono vichingo dell'isola, deve il nome — \"baia dei fumi\" — al vapore geotermico che i primi coloni scambiarono per fumo di incendi. La Hallgrímskirkja che vedrete oggi non è un caso: il suo profilo a colonne è un omaggio diretto alle colonne di basalto che modellano le coste islandesi, le stesse che troverete tra qualche giorno a Reynisfjara. Passeggiando da Laugavegur al porto vecchio, fino al Sun Voyager sul lungomare, si attraversano più di mille anni di storia in mezz'ora a piedi.",
  'parking_nav':[
    {'label':'Naviga verso zona P2 (15-16 nov)','query':'Rauðarárstígur Reykjavik'},
    {'label':'Naviga verso zona P1 (17 nov)','query':'Laugavegur 46 Reykjavik'}
  ]
 },
 {'id':'d2','num':2,'dateISO':'2026-11-16','dateLabel':'Lun 16 nov','title':'Reykjavík: cultura e Reykjanes','locKey':'reykjavik',
  'legs':[
    {'from':'Reykjavík','to':'Ponte tra i continenti','km':61,'time':'~55 min','note':'Via Keflavík e Hafnir (strade 41, 44 e 425).'},
    {'from':'Ponte tra i continenti','to':'Gunnuhver','km':9,'time':'~12 min'},
    {'from':'Gunnuhver','to':'Reykjanesviti','km':2,'time':'~5 min'},
    {'from':'Reykjanesviti','to':'Reykjavík','km':72,'time':'~1h05','note':'Rientro dalla stessa strada via Keflavík: Grindavík e la strada 43 possono essere chiuse per l\'attività vulcanica.'}
  ],
  'activities':[
    {'time':'10:00','title':'Perlan','desc':'Museo con grotta di ghiaccio artificiale e vista panoramica a 360° sulla città.','cost':'€€ ~4900 ISK / ~34€','link':'https://perlan.is/en','nav':'Perlan Reykjavik parking'},
    {'time':'12:30','title':'Harpa & porto vecchio','desc':'Sala concerti in vetro iridescente, passeggiata sul lungomare.','cost':'gratis','link':'https://www.harpa.is/en/','nav':'Harpa Reykjavik parking'},
    {'time':'14:00','title':'Reykjanes (mezza giornata fuori città)','desc':"Ponte tra i continenti, Gunnuhver (la pozza di fango più grande d'Islanda) e il faro di Reykjanesviti. ~55 min di guida all'andata e ~1h05 al ritorno, paesaggio lunare e vulcanico diverso da tutto il resto del viaggio. Partite entro le 14:00 per avere luce fino al tramonto (~16:30). Zona geologicamente molto attiva e Grindavík e le strade vicine possono essere chiuse: andata e ritorno passano da Keflavík e Hafnir (strada 425); verificate lo stato di accesso il giorno stesso su visitreykjanes.is.",'cost':'gratis','link':'https://www.visitreykjanes.is/en/','nav':'Gunnuhver hot springs parking'},
    {'time':'14:00','title':'National Museum of Iceland (facoltativo, se il meteo è brutto)','desc':'Alternativa a Reykjanes in caso di maltempo: storia e cultura islandese dagli insediamenti vichinghi a oggi, al coperto e in città.','cost':'€ ~2900 ISK / ~20€','link':'https://www.thjodminjasafn.is/english','nav':'National Museum of Iceland parking'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Hlemmur Mathöll','note':'Food hall con vari stand: chiedete stand per stand, nessuna opzione senza glutine confermata','cost':'€€','gf':False},
    {'meal':'Cena','place':'Sushi Social o cucina in appartamento','note':'Opzioni senza glutine non confermate: chiedete allo staff (la salsa di soia normale contiene glutine, chiedete tamari)','cost':'€€€','gf':False}
  ],
  'accommodation':{'name':'46heima Boutique Apartments','detail':'2ª notte a Reykjavík','url':'https://www.booking.com/hotel/is/46heima-apartments.en-gb.html'},
  'tips':"Nel pomeriggio si va a Reykjanes (~135 km in tutto tra andata, tappe e ritorno). Se il meteo è brutto, al posto di Reykjanes c'è il National Museum, al coperto in città.",
  'culture':"Il Perlan racconta la geologia islandese da dentro una grotta di ghiaccio artificiale, costruito sopra sei enormi serbatoi che ancora oggi riscaldano Reykjavík con l'acqua calda del sottosuolo. L'Harpa, sala concerti dalla facciata a nido d'ape ispirata alle colonne di basalto, è diventata il simbolo della rinascita della città dopo la crisi finanziaria del 2008. Al National Museum si ripercorre la storia islandese dai primi coloni vichinghi a oggi. Nel pomeriggio, a Reykjanes, camminerete letteralmente tra due continenti sul Bridge Between Continents, un ponte pedonale sullo stesso confine tra placche che attraversa Þingvellir. Qui la terra non è statica: dopo quasi 800 anni di quiete, dal 2021 il vulcanismo è tornato con eruzioni vicino a Grindavík, ripetute più volte tra il 2023 e il 2025. Vedrete il Gunnuhver, la pozza di fango più grande d'Islanda, e il Reykjanesviti, erede del primo faro d'Islanda (1878) — tutto dentro un UNESCO Global Geopark dove la terra si sta ancora formando.",
  'parking_nav':[
    {'label':'Naviga verso zona P2 (per questa notte)','query':'Rauðarárstígur Reykjavik'}
  ]
 },
 {'id':'d3','num':3,'dateISO':'2026-11-17','dateLabel':'Mar 17 nov','title':'Þingvellir & relax serale','locKey':'reykjavik',
  'legs':[
    {'from':'Reykjavík','to':'Þingvellir','km':45,'time':'~45 min'},
    {'from':'Þingvellir','to':'Laugarvatn','km':25,'time':'~20 min'},
    {'from':'Laugarvatn','to':'Reykjavík','km':78,'time':'~1h20'}
  ],
  'activities':[
    {'time':'10:30','title':'Þingvellir National Park','desc':'Faglia tra le placche nordamericana ed euroasiatica, sito del primo parlamento islandese (Unesco). Ripartite entro le 13:30 per arrivare con calma a Laugarvatn prima delle terme.','cost':'gratis (parcheggio ~1000 ISK / ~7€)','link':'https://www.thingvellir.is/en/','nav':'Þingvellir National Park P1 parking'},
    {'time':'14:15','title':'Passeggiata sul lago Laugarvatn','desc':"Passeggiata lungo la riva del lago, proprio accanto a Fontana: sulla spiaggia ci sono sorgenti calde che fumano (è lì che Fontana cuoce il pane di segale nella sabbia calda) e vista sulle montagne attorno. ~45 min, con luce fino al tramonto (~16:20). Parcheggiate già a Fontana.",'cost':'gratis','nav':'Laugarvatn Fontana'},
    {'time':'15:30','title':'Fontana Geothermal Baths (prenotato)','desc':"Ingresso prenotato alle 15:30: siate alla reception 10-15 minuti prima. Terme geotermiche sul lago di Laugarvatn, sulla strada del ritorno verso Reykjavík: piscine a cielo aperto e sauna a vapore naturale. Se il cielo è sereno vale la pena restare fino a tardi, quasi in chiusura (21:00), con più possibilità di vedere l'aurora rispetto a rientrare subito in città.",'cost':'€€ ~50€/persona','link':'https://fontana.is/','nav':'Laugarvatn Fontana'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Pranzo al sacco / Bónus','note':'Porta qualcosa dal Bónus di Reykjavík, comodo per una sosta veloce vicino a Þingvellir','cost':'€','gf':False},
    {'meal':'Cena','place':'Hlemmur Mathöll, Reykjavík','note':'Food hall con vari stand (aperto fino alle 23:00), opzioni senza glutine da chiedere stand per stand. Se rientrate tardi in serata, come piano B ci sono minimarket 10-11 aperti 24/7 o Hagkaup (Skeifan, 24h)','cost':'€€','gf':False}
  ],
  'accommodation':{'name':'46heima Boutique Apartments','detail':'Ultima notte a Reykjavík · check-out domani 09:30-10:00','url':'https://www.booking.com/hotel/is/46heima-apartments.en-gb.html'},
  'tips':"Giornata più leggera (~160 km totali) e volutamente rilassante: è l'ultima notte a Reykjavík prima dei due giorni più intensi del viaggio (Costa Sud e Jökulsárlón). Tabella di marcia per non perdere le terme prenotate alle 15:30: partenza da Reykjavík verso le 9:45, Þingvellir dalle 10:30 alle 13:30 con pranzo al sacco lì, Laugarvatn verso le 14:05 (~35 min di strada), passeggiata sul lago dalle 14:15, alla reception di Fontana alle 15:15. Geysir e Gullfoss li vedrete il Giorno 7 da Flúðir, molto più vicini da lì che da Reykjavík. Se restate fino a tardi la sera, il rientro a Reykjavík (~1h20 da Laugarvatn) va messo in conto: con cielo sereno può valerne la pena per l'aurora. Hlemmur Mathöll chiude alle 23:00 (alcuni stand anche prima): uscendo da Fontana alla chiusura (21:00), tra cambio e parcheggio, arrivate verso le 22:30-22:40, appena in tempo; come piano B c'è sempre un minimarket 10-11 (24/7) o Hagkaup Skeifan (24h).",
  'culture':"A Þingvellir camminerete letteralmente tra due continenti: la faglia che attraversa il parco segna il punto in cui le placche nordamericana ed eurasiatica si allontanano di circa 2 cm l'anno. Qui, nel 930 d.C., nacque l'Alþingi, tra i più antichi parlamenti al mondo ancora in vita — la culla della democrazia islandese che riprenderete più avanti nella tab Storia. Poco più a sud, sul lago di Laugarvatn, la Fontana sfrutta la stessa energia del sottosuolo che alimenta Þingvellir e Geysir.",
  'parking_nav':[
    {'label':'Naviga verso zona P1 (rientro tardi da Fontana, già gratis dopo le 21:00)','query':'Laugavegur 46 Reykjavik'}
  ]
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
    {'time':'11:45','title':'Seljalandsfoss','desc':"Cascata che si può costeggiare sul retro: in inverno il sentiero dietro la cascata è spesso ghiacciato o chiuso, guardatela dal davanti se è transennato. A 10 min a piedi c'è Gljúfrabúi, cascata nascosta in un canyon.",'cost':'gratis','link':'https://it.wikipedia.org/wiki/Seljalandsfoss','nav':'Seljalandsfoss parking'},
    {'time':'13:15','title':'Skógafoss','desc':"Una delle cascate più imponenti d'Islanda, 60 m di salto, scalinata panoramica in cima.",'cost':'gratis','link':'https://it.wikipedia.org/wiki/Skogafoss','nav':'Skógafoss parking'},
    {'time':'14:45','title':'Dyrhólaey','desc':'Sosta breve (~20 min). Promontorio con arco di roccia e vista su Reynisfjara. Da vedere con un po\' di luce ancora buona: il tramonto qui è verso le 16:15.','cost':'gratis','nav':'Dyrhólaey parking'},
    {'time':'15:30','title':'Reynisfjara','desc':'Spiaggia di sabbia nera con colonne basaltiche e i faraglioni di Reynisdrangar. Attenzione alle onde anomale, non voltare le spalle al mare.','cost':'gratis','nav':'Reynisfjara Black Sand Beach parking'},
    {'time':'16:15','title':'Víkurkirkja','desc':"La chiesetta bianca dal tetto rosso su per la collina di Vík, tra le più fotografate d'Islanda: da lassù la vista abbraccia il villaggio, la spiaggia nera e i faraglioni di Reynisdrangar sullo sfondo. Ultima tappa apposta: proprio all'ora del tramonto può regalare una luce spettacolare.",'cost':'gratis','nav':'Víkurkirkja Vík Iceland'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Picnic a Skógar','note':'Porta snack dal Bónus di Reykjavík','cost':'€','gf':False},
    {'meal':'Cena','place':'Suður-Vík Restaurant','note':'Opzioni senza glutine segnate nel menu; segnalate la celiachia, in cucina c\'è rischio di contaminazione','cost':'€€','gf':True}
  ],
  'accommodation':{'name':'Hótel Búrfell','detail':'Vík í Mýrdal · 2 notti · parcheggio gratuito incluso','url':'https://hotelburfell.is/'},
  'tips':'Il 18 novembre a Vík il sole tramonta verso le 16:15 (molto prima di quanto sembri): Dyrhólaey e Reynisfjara vanno viste per bene entro quell\'ora, la Víkurkirkja invece va benissimo proprio al tramonto/appena dopo, dato che è a due passi dal centro del paese e non richiede tempo di guida extra.',
  'culture':"Oggi si passa dalle cascate alla costa vulcanica. Skógafoss, 60 metri di salto, nasconde secondo la leggenda un forziere vichingo dietro le sue acque. A Reynisfjara la sabbia nera è lava basaltica frantumata da millenni di oceano, e le pareti a colonne esagonali sono le stesse che hanno ispirato l'architettura della Hallgrímskirkja. Al largo, i faraglioni Reynisdrangar sarebbero — dice la leggenda — due troll pietrificati dall'alba mentre trascinavano a riva una nave: attenzione alle onde anomale, il mare qui non scherza. Dyrhólaey, il promontorio con l'arco di roccia, nacque da un'eruzione sottomarina durante l'ultima glaciazione. Vík, il villaggio più a sud dell'isola, vive all'ombra del vulcano Katla, sepolto sotto il ghiacciaio Mýrdalsjökull — e la sua chiesetta rossa e bianca, arroccata sulla collina, era il punto di raccolta designato per gli abitanti in caso di eruzione improvvisa.",
  'parking_nav':[
    {'label':'Naviga verso il parcheggio dell\'hotel (gratuito)','query':'Hotel Burfell Vík Iceland'}
  ]
 },
 {'id':'d5','num':5,'dateISO':'2026-11-19','dateLabel':'Gio 19 nov','title':'Escursione a Jökulsárlón','locKey':'vik',
  'legs':[
    {'from':'Vík','to':'Jökulsárlón','km':192,'time':'~2h45 (diretto, oltre Fjaðrárgljúfur senza fermarsi)'},
    {'from':'Jökulsárlón','to':'Fjaðrárgljúfur','km':130,'time':'~1h50 (sulla via del ritorno)'},
    {'from':'Fjaðrárgljúfur','to':'Vík','km':72,'time':'~55 min'}
  ],
  'activities':[
    {'time':'07:30','title':'Partenza presto','desc':'Giornata lunga di guida (~6 ore in tutto): si parte con il buio, normale in novembre, e la prima luce arriva verso le 9 (alba alle 9:50).','cost':None},
    {'time':'10:30','title':'Jökulsárlón Glacier Lagoon','desc':'Laguna glaciale con iceberg alla deriva verso il mare. Arrivate con la luce dell\'alba, ottima per le foto degli iceberg.','cost':'gratis (parcheggio a pagamento)','nav':'Jökulsárlón Glacier Lagoon parking'},
    {'time':'11:45','title':'Diamond Beach','desc':'Spiaggia nera di fronte alla laguna dove i blocchi di ghiaccio si arenano. Ripartite entro le 12:30: pranzo veloce qui o al sacco in macchina.','cost':'gratis','link':'https://perlan.is/articles/diamond-beach-iceland','nav':'Diamond Beach Iceland parking'},
    {'time':'14:30','title':'Fjaðrárgljúfur','desc':"Canyon serpeggiante con pareti muschiose, punti panoramici accessibili a piedi. Visitato sulla via del ritorno apposta: con la luce del primo mattino (alba verso le 9:50) si vedrebbe pochissimo.",'cost':'gratis','nav':'Fjaðrárgljúfur canyon parking'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Kaffi Jökulsárlón o pranzo al sacco','note':'Nessuna informazione sul senza glutine trovata: chiedete allo staff e portate un\'alternativa al sacco','cost':'€€','gf':False},
    {'meal':'Cena','place':'Ströndin Bistro, Vík','note':'Opzioni senza glutine (per esempio lo stufato di carne e le costolette d\'agnello): chiedete conferma allo staff','cost':'€€','gf':True}
  ],
  'accommodation':{'name':'Hótel Búrfell','detail':'2ª notte a Vík','url':'https://hotelburfell.is/'},
  'tips':"~390 km andata/ritorno da Vík, circa 6 ore di guida. Tabella di marcia: partenza alle 7:30, Jökulsárlón verso le 10:30-10:45 (~2h55 senza soste, in inverno contate qualcosa in più), Diamond Beach e via entro le 12:30, Fjaðrárgljúfur verso le 14:30-14:45 con circa un'ora e mezza di luce prima del tramonto (16:05), rientro a Vík verso le 16:45-17:00. Prima di partire controllate che il sentiero del canyon sia aperto (in inverno a volte viene chiuso per il terreno fradicio) e le strade su road.is; con brutto tempo valutate di fermarvi solo a Jökulsárlón/Diamond Beach.",
  'culture':"Giornata dedicata al ghiaccio. A Jökulsárlón la laguna esiste solo da un secolo: il Vatnajökull, il ghiacciaio più esteso d'Europa, si è ritirato rapidamente da inizio '900 lasciando dietro di sé questo bacino pieno di iceberg alla deriva verso il mare. Quelli che si arenano sulla sabbia nera di Diamond Beach, levigati e trasparenti, possono contenere ghiaccio compresso da centinaia o migliaia di anni. Sulla via del ritorno, il canyon di Fjaðrárgljúfur, scavato da un fiume glaciale in circa due milioni di anni, è diventato famoso di recente anche grazie a un video musicale di Justin Bieber.",
  'parking_nav':[
    {'label':'Naviga verso il parcheggio dell\'hotel (gratuito)','query':'Hotel Burfell Vík Iceland'}
  ]
 },
 {'id':'d6','num':6,'dateISO':'2026-11-20','dateLabel':'Ven 20 nov','title':'Vík → Flúðir','locKey':'fludir',
  'legs':[
    {'from':'Vík','to':'Kerið','km':130,'time':'~1h50'},
    {'from':'Kerið','to':'Flúðir','km':39,'time':'~30 min'}
  ],
  'activities':[
    {'time':'10:00','title':'Check-out Hótel Búrfell','desc':'','cost':None},
    {'time':'12:30','title':'Kerið','desc':'Cratere vulcanico con un lago sul fondo, percorribile a piedi in 15-20 min.','cost':'€ ~400 ISK / ~3€','link':'https://kerid.is/','nav':'Kerið crater parking'},
    {'time':'15:30','title':'Check-in The Hill Guesthouse','desc':'Flúðir','cost':None},
    {'time':'17:30','title':'Secret Lagoon','desc':"La piscina geotermica più antica d'Islanda, meno turistica e molto più economica della Blue Lagoon. Alle 17:30 il sole è tramontato da circa un'ora e mezza e il cielo è ormai buio: con cielo sereno potete provare a scorgere l'aurora dall'acqua calda.",'cost':'€ ~4500 ISK / ~31€ a persona, prenotare online','link':'https://secretlagoon.is/','nav':'Secret Lagoon Gamla Laugin Flúðir'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Selfoss (pranzo al sacco o supermercato locale)','note':'Ultima città con supermercati grandi prima di Flúðir, sulla strada da Vík','cost':'€','gf':False},
    {'meal':'Cena','place':'Cucina alla guesthouse o Restaurant Grund','note':'Opzioni senza glutine non confermate: verificate il menu in loco','cost':'€€','gf':False}
  ],
  'accommodation':{'name':'The Hill Guesthouse','detail':'Flúðir · 2 notti · parcheggio gratuito incluso','url':'https://thehillhotel.is/guesthouse-fludir/'},
  'tips':'Prenota la Secret Lagoon in anticipo online: gli slot serali si esauriscono. A novembre lo slot più tardo disponibile è 17:30, non più tardi.',
  'culture':"Kerið è un cratere vulcanico di circa 6.500 anni, insolito nel colore: la roccia è ricca di scoria rossastra invece del solito basalto nero, e sul fondo si è formato un piccolo lago verde-azzurro alimentato dalla falda. A Flúðir vi aspetta la Secret Lagoon, la piscina geotermica più antica dell'isola: costruita nel 1891 come prima piscina pubblica islandese, oggi resta piccola e informale rispetto alla Blue Lagoon, con l'acqua che sgorga naturalmente a circa 38-40°C da una sorgente a pochi passi dalla vasca.",
  'parking_nav':[
    {'label':'Naviga verso il parcheggio della guesthouse (gratuito)','query':'The Hill Guesthouse Flúðir'}
  ]
 },
 {'id':'d7','num':7,'dateISO':'2026-11-21','dateLabel':'Sab 21 nov','title':'Geysir & Gullfoss e sorgenti calde','locKey':'fludir',
  'legs':[
    {'from':'Flúðir','to':'Geysir','km':30,'time':'~25 min'},
    {'from':'Geysir','to':'Gullfoss','km':10,'time':'~10 min'},
    {'from':'Gullfoss','to':'Faxi','km':21,'time':'~20 min'},
    {'from':'Faxi','to':'Efstidalur II','km':9,'time':'~12 min'},
    {'from':'Efstidalur II','to':'Flúðir','km':20,'time':'~18 min'}
  ],
  'activities':[
    {'time':'10:30','title':'Geysir & Strokkur','desc':'Area geotermica: Strokkur erutta ogni 5-10 minuti.','cost':'gratis','nav':'Geysir Geothermal Area parking'},
    {'time':'11:30','title':'Gullfoss','desc':"Cascata a doppio salto, spettacolare anche d'inverno con il ghiaccio sulle rocce.",'cost':'gratis','link':'https://it.wikipedia.org/wiki/Gullfoss','nav':'Gullfoss waterfall parking'},
    {'time':'14:00','title':'Faxi','desc':'Cascata piccola e tranquilla vicino a Reykholt, sulla strada del ritorno verso Flúðir, poco turistica.','cost':'gratis','link':'https://it.wikipedia.org/wiki/Faxi','nav':'Faxi waterfall Iceland parking'},
    {'time':'15:30','title':'Efstidalur II','desc':"Fattoria con gelateria e vacche visibili da dietro un vetro, ambiente al caldo e informale. Sosta comoda per il buio che cala presto in questo periodo, prima del rientro a Flúðir.",'cost':'€ gelato/spuntino a parte','nav':'Efstidalur II Farm'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Friðheimar, Reykholt','note':'Famosa zuppa di pomodoro in serra, sulla strada per Geysir: hanno pane senza glutine, ma non garantito senza contaminazione; in alternativa c\'è un\'insalata','cost':'€€','gf':True},
    {'meal':'Cena','place':'Cucina alla guesthouse','note':'Ultima occasione per finire la spesa fatta al Bónus','cost':'€','gf':False}
  ],
  'accommodation':{'name':'The Hill Guesthouse','detail':'Ultima notte a Flúðir · check-out presto domani','url':'https://thehillhotel.is/guesthouse-fludir/'},
  'tips':"Da Flúðir Geysir e Gullfoss sono a un tiro di schioppo (~30-40 km), molto più vicini che da Reykjavík: giornata comoda, e cielo scuro poco inquinato per tenere d'occhio l'aurora la sera.",
  'culture':"Il nome stesso di \"geyser\" nasce qui: Strokkur erutta ogni 5-10 minuti, mentre il Grande Geysir che gli ha dato il nome dorme quasi sempre dal 2003. Gullfoss esiste ancora grazie a Sigríður Tómasdóttir, che ai primi del '900 si oppose a un progetto di diga che l'avrebbe sommersa. Flúðir vive di geotermia da oltre un secolo: le sue serre, riscaldate dal vapore del sottosuolo, coltivano pomodori e ortaggi anche nel buio di novembre. Faxi, piccola e quasi sempre deserta, è la cascata che molti islandesi preferiscono a Gullfoss nei weekend affollati.",
  'parking_nav':[
    {'label':'Naviga verso il parcheggio della guesthouse (gratuito)','query':'The Hill Guesthouse Flúðir'}
  ]
 },
 {'id':'d8','num':8,'dateISO':'2026-11-22','dateLabel':'Dom 22 nov','title':'Flúðir → Keflavík → Volo di ritorno','locKey':'keflavik',
  'legs':[
    {'from':'Flúðir','to':'Aeroporto di Keflavík','km':140,'time':'~2h05'}
  ],
  'activities':[
    {'time':'06:45','title':'Partenza da Flúðir','desc':'Partite presto per avere margine: riconsegna auto e imbarco sono molto ravvicinati.','cost':None},
    {'time':'~09:15','title':'Riconsegna auto FairCar','desc':'Il voucher indica riconsegna alle 11:00, ma il volo parte alle 11:25: verificate con FairCar se potete riconsegnare prima (es. entro le 9:00\u20119:30) per avere tempo per check-in e imbarco. Controllate sul voucher la regola del carburante: se va riconsegnata col pieno, fate benzina a Keflavík/Reykjanesbær prima di arrivare.','cost':None,'nav':'FairCar Bogatröð 1 Keflavík'},
    {'time':'11:25','title':'Volo EJU3970 Keflavík → Milano Malpensa','desc':'Arrivo previsto alle 16:45.','cost':None}
  ],
  'food':[
    {'meal':'Colazione','place':'Avanzi della spesa','note':'Partendo alle 6:45 la colazione della guesthouse difficilmente è già servita: tenete da parte qualcosa dalla spesa del Bónus','cost':'€','gf':False}
  ],
  'accommodation': None,
  'tips':'Pochissimo margine tra riconsegna auto (11:00) e decollo (11:25): meglio anticipare la riconsegna il più possibile.',
  'culture':"L'Islanda produce quasi il 100% della sua elettricità da fonti rinnovabili — geotermia e idroelettrico — un'anomalia quasi unica al mondo, resa possibile proprio dal fuoco sotto i piedi che avete attraversato in questi otto giorni. Buon rientro."
 }
]

# 'extra': True = tappa facoltativa: compare come segnaposto sulla mappa ma non
# fa parte del percorso stradale.
map_points = {
    'd1': [{'name':'Aeroporto Keflavík','lat':63.9850,'lon':-22.6056}, {'name':'Reykjavík','lat':64.1466,'lon':-21.9426}],
    'd2': [{'name':'Perlan','lat':64.1289,'lon':-21.9147}, {'name':'Harpa','lat':64.1500,'lon':-21.9326}, {'name':'Bridge Between Continents','lat':63.8697,'lon':-22.6764}, {'name':'Gunnuhver','lat':63.8181,'lon':-22.6994}, {'name':'Reykjanesviti','lat':63.8156,'lon':-22.6913}, {'name':'Reykjavík','lat':64.1466,'lon':-21.9426}, {'name':'National Museum (facoltativo, se piove)','lat':64.1417,'lon':-21.9530,'extra':True}],
    'd3': [{'name':'Reykjavík','lat':64.1466,'lon':-21.9426}, {'name':'Þingvellir','lat':64.2559,'lon':-21.1297}, {'name':'Laugarvatn','lat':64.2019,'lon':-20.7357}, {'name':'Reykjavík','lat':64.1466,'lon':-21.9426}],
    'd4': [{'name':'Reykjavík','lat':64.1466,'lon':-21.9426}, {'name':'Seljalandsfoss','lat':63.6156,'lon':-19.9886}, {'name':'Skógafoss','lat':63.5321,'lon':-19.5116}, {'name':'Dyrhólaey','lat':63.4033,'lon':-19.1250}, {'name':'Reynisfjara','lat':63.4038,'lon':-19.0428}, {'name':'Víkurkirkja','lat':63.4193,'lon':-19.0058}],
    'd5': [{'name':'Vík','lat':63.4186,'lon':-19.0060}, {'name':'Jökulsárlón','lat':64.0784,'lon':-16.2300}, {'name':'Diamond Beach','lat':64.0645,'lon':-16.1809}, {'name':'Fjaðrárgljúfur','lat':63.7722,'lon':-18.1725}, {'name':'Vík','lat':63.4186,'lon':-19.0060}],
    'd6': [{'name':'Vík','lat':63.4186,'lon':-19.0060}, {'name':'Kerið','lat':64.0410,'lon':-20.8834}, {'name':'Flúðir','lat':64.1372,'lon':-20.3033}, {'name':'Secret Lagoon','lat':64.1306,'lon':-20.2989}],
    'd7': [{'name':'Flúðir','lat':64.1372,'lon':-20.3033}, {'name':'Geysir','lat':64.3128,'lon':-20.3009}, {'name':'Gullfoss','lat':64.3271,'lon':-20.1199}, {'name':'Faxi','lat':64.2266,'lon':-20.3402}, {'name':'Efstidalur II','lat':64.2567,'lon':-20.5029}, {'name':'Flúðir','lat':64.1372,'lon':-20.3033}],
    'd8': [{'name':'Flúðir','lat':64.1372,'lon':-20.3033}, {'name':'Aeroporto Keflavík','lat':63.9850,'lon':-22.6056}]
}

# Tappe serali per la stima aurora (app e notifiche): dove siete la sera, ora per ora
# (ora islandese = UTC). 'until' = ora di fine tappa; l'ultima vale fino al mattino.
# I giorni non elencati usano l'alloggio della notte (locKey).
evening_places = {
    'laugarvatn': {'name': 'Laugarvatn (Fontana)', 'lat': 64.2141, 'lon': -20.7290},
    'thingvellir': {'name': 'strada del ritorno (Þingvellir)', 'lat': 64.2559, 'lon': -21.1299},
}
evening_stops = {
    'd3': [{'place': 'laugarvatn', 'until': 21},     # Fontana fino alla chiusura
           {'place': 'thingvellir', 'until': 22},    # ~1h20 di strada verso Reykjavík
           {'place': 'reykjavik'}],
}
# Stima delle nuvole (vedi tools/research/nuvole.py e leggimi sezione 13):
#   'totale'    nuvolosità totale del modello automatico (DMI HARMONIE in Islanda)
#   'pesata'    stesso modello, strati pesati: bassi contano tutti, medi e alti meno
#   'media'     media della nuvolosità totale dei CLOUD_MODELS
#   'media_pes' media dei CLOUD_MODELS, ognuno con gli strati pesati
CLOUD_METHOD = 'totale'
CLOUD_W_MID, CLOUD_W_HIGH = 0.8, 0.3
CLOUD_MODELS = ['best_match', 'ecmwf_ifs025', 'icon_seamless', 'ukmo_seamless', 'metno_seamless', 'gfs_seamless']

# Chiave pubblica VAPID degli avvisi aurora: la privata corrispondente sta solo
# nel secret VAPID_PRIVATE_KEY del repo (vedi leggimi, sezione 12).
VAPID_PUBLIC_KEY = 'BMOzcfKagfPhm6Ax0MRUig7SvV7LoQjp2WzP-YWybYEE0TVCguWI11MTKxO5i2UslqyvHeG6HOtsN08FVa_6yZk'
