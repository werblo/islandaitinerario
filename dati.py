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

# Checklist (da fare, valigia) e biglietti: su Notion, condivisi tra Michele e
# Federica. Nell'app resta solo il link (tab Info).
NOTION_CHECKLIST_URL = 'https://www.notion.so/3f66b411a944814e8d3ae850ce49a9fb'

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
  'tips':"Giornata di arrivo tranquilla: sistematevi con calma e fate un po' di spesa in un Bónus per i giorni successivi. Avrete un paio di soste alle terme nel resto del viaggio, più economiche e meno turistiche della Blue Lagoon. Parcheggio: l'appartamento non ne ha uno incluso e Laugavegur è zona P1 (circa 650 ISK/h, max 3h consecutive), gratis dalle 21:00 alle 9:00 nei feriali/sabato e prima delle 10:00/dopo le 21:00 la domenica (orari da riconfermare su reykjavik.is/en/parking vicino alla partenza). Strategia notte per notte: 15 e 16 novembre parcheggiate in zona P2 verso Hlemmur/Rauðarárstígur (circa 230 ISK/h, senza limite di 3h, più economica se rientrate prima delle 21:00); la notte del 17 invece va bene direttamente P1 sotto casa, perché quella sera rientrerete da Fontana dopo le 21:00 (quando è già gratis anche lì); il mattino dopo dalle 9:00 si paga di nuovo, quindi pagate (app Parka o parchimetro) dalle 9:00 fino alla partenza per la Costa Sud.",
  'culture':"Secondo il Landnámabók, il «Libro degli insediamenti», Reykjavík fu fondata nell'874 da Ingólfur Arnarson, considerato il primo colono stabile dell'isola. Il nome significa «baia dei fumi» e deriva dal vapore delle sorgenti calde della zona. Oggi è la capitale e la città più popolosa del paese.\n\nLa Hallgrímskirkja, progettata dall'architetto Guðjón Samúelsson e dedicata al poeta Hallgrímur Pétursson, è la chiesa più grande d'Islanda: la sua torre è alta circa 75 metri e la facciata riprende la forma delle colonne di basalto. Sul lungomare si trova il Sólfar (Sun Voyager), scultura in acciaio di Jón Gunnar Árnason a forma di nave, che l'autore descrisse come una «nave dei sogni».",
  'culture_links':[("Reykjavík", "https://it.wikipedia.org/wiki/Reykjavik"), ("Colonizzazione dell'Islanda", "https://it.wikipedia.org/wiki/Colonizzazione_dell'Islanda")],
  'parking_nav':[
    {'label':'Naviga a P2 (15-16 nov)','query':'Rauðarárstígur Reykjavik'},
    {'label':'Naviga a P1 (17 nov)','query':'Laugavegur 46 Reykjavik'}
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
    {'time':'14:00','title':'Reykjanes (mezza giornata fuori città)','desc':"Ponte tra i continenti, Gunnuhver (la pozza di fango più grande d'Islanda) e il faro di Reykjanesviti. Circa 55 minuti di guida all'andata e un'ora al ritorno, in un paesaggio di campi di lava. Partite entro le 14:00 per avere luce fino al tramonto (circa 16:30). Zona geologicamente molto attiva e Grindavík e le strade vicine possono essere chiuse: andata e ritorno passano da Keflavík e Hafnir (strada 425); verificate lo stato di accesso il giorno stesso su visitreykjanes.is.",'cost':'gratis','link':'https://www.visitreykjanes.is/en/','nav':'Gunnuhver hot springs parking'},
    {'time':'14:00','title':'National Museum of Iceland (facoltativo, se il meteo è brutto)','desc':'Alternativa a Reykjanes in caso di maltempo: storia e cultura islandese dagli insediamenti vichinghi a oggi, al coperto e in città.','cost':'€ ~2900 ISK / ~20€','link':'https://www.thjodminjasafn.is/english','nav':'National Museum of Iceland parking'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Hlemmur Mathöll','note':'Food hall con vari stand: chiedete stand per stand, nessuna opzione senza glutine confermata','cost':'€€','gf':False},
    {'meal':'Cena','place':'Sushi Social o cucina in appartamento','note':'Opzioni senza glutine non confermate: chiedete allo staff (la salsa di soia normale contiene glutine, chiedete tamari)','cost':'€€€','gf':False}
  ],
  'accommodation':{'name':'46heima Boutique Apartments','detail':'2ª notte a Reykjavík · stanotte parcheggio in zona P2','url':'https://www.booking.com/hotel/is/46heima-apartments.en-gb.html'},
  'tips':"Nel pomeriggio si va a Reykjanes (circa 135 km in tutto tra andata, tappe e ritorno). Se il meteo è brutto, al posto di Reykjanes c'è il National Museum, al coperto in città.",
  'culture':"Il Perlan sorge sulla collina di Öskjuhlíð, sopra i serbatoi che conservano l'acqua calda geotermica usata per il riscaldamento di Reykjavík. All'interno ospita una mostra sulla natura islandese con una grotta di ghiaccio artificiale.\n\nL'Harpa è la sala concerti e centro congressi della città, inaugurata nel 2011: la facciata in vetro è stata progettata con l'artista Ólafur Elíasson e nel 2013 ha ricevuto il Premio Mies van der Rohe. Il Museo nazionale d'Islanda conserva reperti che vanno dalla colonizzazione vichinga ai giorni nostri.\n\nLa penisola di Reykjanes si trova sulla dorsale medio-atlantica, lungo lo stesso confine tra placca nordamericana ed eurasiatica che attraversa Þingvellir; il Bridge Between Continents è un ponte pedonale costruito sopra una fessura di questo confine. Dopo circa 800 anni senza eruzioni, l'attività vulcanica nella penisola è ripresa nel 2021, con più eruzioni nei pressi di Grindavík tra il 2023 e il 2025. Nella zona si trovano anche il Gunnuhver, la pozza di fango bollente più grande d'Islanda, e il faro di Reykjanesviti, che ha sostituito il primo faro del paese, del 1878. L'area fa parte del Reykjanes UNESCO Global Geopark.",
  'culture_links':[("Museo nazionale d'Islanda", "https://it.wikipedia.org/wiki/Museo_nazionale_d'Islanda"), ("Ólafur Elíasson", "https://it.wikipedia.org/wiki/Ólafur_Elíasson"), ("Vulcani dell'Islanda", "https://it.wikipedia.org/wiki/Vulcani_dell'Islanda")],
  'parking_nav':[
    {'label':'Naviga al parcheggio P2','query':'Rauðarárstígur Reykjavik'}
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
    {'time':'14:15','title':'Passeggiata sul lago Laugarvatn','desc':"Passeggiata lungo la riva del lago, proprio accanto a Fontana: sulla spiaggia ci sono sorgenti calde che fumano (è lì che Fontana cuoce il pane di segale nella sabbia calda) e vista sulle montagne attorno. Circa 45 min, con luce fino al tramonto (circa 16:20). Parcheggiate già a Fontana.",'cost':'gratis','nav':'Laugarvatn Fontana'},
    {'time':'15:30','title':'Fontana Geothermal Baths (prenotato)','desc':"Ingresso prenotato alle 15:30: siate alla reception 10-15 minuti prima. Terme geotermiche sul lago di Laugarvatn, sulla strada del ritorno verso Reykjavík: piscine a cielo aperto e sauna a vapore naturale. Se il cielo è sereno conviene restare fino a tardi, quasi in chiusura (21:00), con più possibilità di vedere l'aurora rispetto a rientrare subito in città.",'cost':'€€ ~50€/persona','link':'https://fontana.is/','nav':'Laugarvatn Fontana'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Pranzo al sacco / Bónus','note':'Porta qualcosa dal Bónus di Reykjavík, comodo per una sosta veloce vicino a Þingvellir','cost':'€','gf':False},
    {'meal':'Cena','place':'Hlemmur Mathöll, Reykjavík','note':'Food hall con vari stand (aperto fino alle 23:00), opzioni senza glutine da chiedere stand per stand. Se rientrate tardi in serata, come piano B ci sono minimarket 10-11 aperti 24/7 o Hagkaup (Skeifan, 24h)','cost':'€€','gf':False}
  ],
  'accommodation':{'name':'46heima Boutique Apartments','detail':'Ultima notte a Reykjavík · check-out domani 09:30-10:00 · stanotte parcheggio in zona P1 sotto casa (rientrando da Fontana dopo le 21:00 è già gratis; domattina si paga dalle 9:00 alla partenza)','url':'https://www.booking.com/hotel/is/46heima-apartments.en-gb.html'},
  'tips':"Giornata più leggera (circa 160 km totali) e volutamente rilassante: è l'ultima notte a Reykjavík prima dei due giorni più intensi del viaggio (Costa Sud e Jökulsárlón). Tabella di marcia per non perdere le terme prenotate alle 15:30: partenza da Reykjavík verso le 9:45, Þingvellir dalle 10:30 alle 13:30 con pranzo al sacco lì, Laugarvatn verso le 14:05 (circa 35 min di strada), passeggiata sul lago dalle 14:15, alla reception di Fontana alle 15:15. Geysir e Gullfoss li vedrete il Giorno 7 da Flúðir, molto più vicini da lì che da Reykjavík. Se restate fino a tardi la sera, il rientro a Reykjavík (circa 1h20 da Laugarvatn) va messo in conto: con cielo sereno può valerne la pena per l'aurora. Hlemmur Mathöll chiude alle 23:00 (alcuni stand anche prima): uscendo da Fontana alla chiusura (21:00), tra cambio e parcheggio, arrivate verso le 22:30-22:40, appena in tempo; come piano B c'è sempre un minimarket 10-11 (24/7) o Hagkaup Skeifan (24h).",
  'culture':"Il Parco nazionale Þingvellir si trova sulla dorsale medio-atlantica, nel punto in cui le placche nordamericana ed eurasiatica si allontanano di circa 2 cm all'anno; la gola di Almannagjá è la frattura più nota.\n\nNel 930 vi si riunì per la prima volta l'Alþingi, l'assemblea generale dell'isola, che si tenne a Þingvellir ogni estate fino al 1798 ed è considerata uno dei parlamenti più antichi del mondo. Il 17 giugno 1944 a Þingvellir fu proclamata la Repubblica d'Islanda. Il parco è patrimonio dell'umanità UNESCO dal 2004. Il lago di Laugarvatn, poco più a est, è alimentato da sorgenti calde; le terme di Fontana sfruttano questa stessa energia geotermica.",
  'culture_links':[("Parco nazionale Þingvellir", "https://it.wikipedia.org/wiki/Parco_nazionale_Þingvellir"), ("Alþingi", "https://it.wikipedia.org/wiki/Alþingi")],
  'parking_nav':[
    {'label':'Naviga al parcheggio P1','query':'Laugavegur 46 Reykjavik'}
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
    {'time':'14:45','title':'Dyrhólaey','desc':'Sosta breve (circa 20 min). Promontorio con arco di roccia e vista su Reynisfjara. Da vedere con un po\' di luce ancora buona: il tramonto qui è verso le 16:15.','cost':'gratis','nav':'Dyrhólaey parking'},
    {'time':'15:30','title':'Reynisfjara','desc':'Spiaggia di sabbia nera con colonne basaltiche e i faraglioni di Reynisdrangar. Attenzione alle onde anomale, non voltare le spalle al mare.','cost':'gratis','nav':'Reynisfjara Black Sand Beach parking'},
    {'time':'16:15','title':'Víkurkirkja','desc':"Chiesa bianca dal tetto rosso sulla collina sopra Vík, tra le più fotografate d'Islanda. Dalla collina si vedono il villaggio, la spiaggia nera e i faraglioni Reynisdrangar. È l'ultima tappa del giorno per vederla con la luce del tramonto.",'cost':'gratis','nav':'Víkurkirkja Vík Iceland'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Picnic a Skógar','note':'Porta snack dal Bónus di Reykjavík','cost':'€','gf':False},
    {'meal':'Cena','place':'Suður-Vík Restaurant','note':'Opzioni senza glutine segnate nel menu; segnalate la celiachia, in cucina c\'è rischio di contaminazione','cost':'€€','gf':True}
  ],
  'accommodation':{'name':'Hótel Búrfell','detail':'Vík í Mýrdal · 2 notti · parcheggio gratuito incluso','url':'https://hotelburfell.is/'},
  'tips':'Il 18 novembre a Vík il sole tramonta verso le 16:15 (molto prima di quanto sembri): Dyrhólaey e Reynisfjara vanno viste per bene entro quell\'ora, la Víkurkirkja invece va benissimo proprio al tramonto/appena dopo, dato che è a due passi dal centro del paese e non richiede tempo di guida extra.',
  'culture':"Seljalandsfoss e Skógafoss scendono dall'altopiano ai piedi del ghiacciaio Eyjafjallajökull, lungo l'antica linea di costa: il mare, ritirandosi, ha lasciato una serie di cascate sulla parete rocciosa. Skógafoss è larga 25 metri e alta 60; secondo una leggenda il colono Þrasi vi nascose dietro un forziere d'oro.\n\nLa spiaggia di Reynisfjara è formata da sabbia basaltica nera e chiusa dalle colonne di basalto del monte Reynisfjall; al largo si trovano i faraglioni Reynisdrangar, che la tradizione popolare descrive come troll pietrificati dalla luce del giorno.\n\nIl promontorio di Dyrhólaey, con il suo arco di roccia, si è formato da un'eruzione sottomarina. Vík í Mýrdal è il villaggio più meridionale d'Islanda e si trova vicino al vulcano Katla, coperto dal ghiacciaio Mýrdalsjökull; secondo i piani di emergenza la chiesa sulla collina è il punto di raccolta degli abitanti in caso di eruzione.",
  'culture_links':[("Skógafoss", "https://it.wikipedia.org/wiki/Skogafoss"), ("Eyjafjallajökull", "https://it.wikipedia.org/wiki/Eyjafjallajokull"), ("Cascate dell'Islanda", "https://it.wikipedia.org/wiki/Cascate_dell'Islanda")],
  'parking_nav':[
    {'label':'Naviga al parcheggio dell\'hotel','query':'Hotel Burfell Vík Iceland'}
  ]
 },
 {'id':'d5','num':5,'dateISO':'2026-11-19','dateLabel':'Gio 19 nov','title':'Escursione a Jökulsárlón','locKey':'vik',
  'legs':[
    {'from':'Vík','to':'Jökulsárlón','km':192,'time':'~2h45 (diretto, oltre Fjaðrárgljúfur senza fermarsi)'},
    {'from':'Jökulsárlón','to':'Fjaðrárgljúfur','km':130,'time':'~1h50 (sulla via del ritorno)'},
    {'from':'Fjaðrárgljúfur','to':'Vík','km':72,'time':'~55 min'}
  ],
  'activities':[
    {'time':'07:30','title':'Partenza presto','desc':'Giornata lunga di guida (circa 6 ore in tutto): si parte con il buio, normale in novembre, e la prima luce arriva verso le 9 (alba alle 9:50).','cost':None},
    {'time':'10:30','title':'Jökulsárlón Glacier Lagoon','desc':'Laguna glaciale con iceberg alla deriva verso il mare. Arrivate con la luce dell\'alba, ottima per le foto degli iceberg.','cost':'gratis (parcheggio a pagamento)','nav':'Jökulsárlón Glacier Lagoon parking'},
    {'time':'11:45','title':'Diamond Beach','desc':'Spiaggia nera di fronte alla laguna dove i blocchi di ghiaccio si arenano. Ripartite entro le 12:30: pranzo veloce qui o al sacco in macchina.','cost':'gratis','link':'https://perlan.is/articles/diamond-beach-iceland','nav':'Diamond Beach Iceland parking'},
    {'time':'14:30','title':'Fjaðrárgljúfur','desc':"Canyon serpeggiante con pareti muschiose, punti panoramici accessibili a piedi. Si visita al ritorno perché con la luce del primo mattino (alba verso le 9:50) si vedrebbe pochissimo.",'cost':'gratis','nav':'Fjaðrárgljúfur canyon parking'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Kaffi Jökulsárlón o pranzo al sacco','note':'Nessuna informazione sul senza glutine trovata: chiedete allo staff e portate un\'alternativa al sacco','cost':'€€','gf':False},
    {'meal':'Cena','place':'Ströndin Bistro, Vík','note':'Opzioni senza glutine (per esempio lo stufato di carne e le costolette d\'agnello): chiedete conferma allo staff','cost':'€€','gf':True}
  ],
  'accommodation':{'name':'Hótel Búrfell','detail':'2ª notte a Vík · parcheggio gratuito','url':'https://hotelburfell.is/'},
  'tips':"Circa 390 km andata/ritorno da Vík, circa 6 ore di guida. Tabella di marcia: partenza alle 7:30, Jökulsárlón verso le 10:30-10:45 (circa 2h55 senza soste, in inverno contate qualcosa in più), Diamond Beach e via entro le 12:30, Fjaðrárgljúfur verso le 14:30-14:45 con circa un'ora e mezza di luce prima del tramonto (16:05), rientro a Vík verso le 16:45-17:00. Prima di partire controllate che il sentiero del canyon sia aperto (in inverno a volte viene chiuso per il terreno fradicio) e le strade su road.is; con brutto tempo valutate di fermarvi solo a Jökulsárlón/Diamond Beach.",
  'culture':"Jökulsárlón è una laguna glaciale formata a partire dagli anni Trenta del Novecento, quando la lingua del ghiacciaio Breiðamerkurjökull ha cominciato a ritirarsi. È collegata all'oceano Atlantico da un breve canale: gli iceberg che si staccano dal ghiacciaio attraversano la laguna e arrivano sulla spiaggia di sabbia nera di fronte, nota come Diamond Beach.\n\nIl Breiðamerkurjökull è una lingua del Vatnajökull, la più grande calotta glaciale d'Islanda e tra le più estese d'Europa, che si trova all'interno del Parco nazionale del Vatnajökull, patrimonio dell'umanità UNESCO dal 2019. Il canyon di Fjaðrárgljúfur, profondo fino a circa 100 metri, è stato scavato dal fiume Fjaðrá alla fine dell'ultima glaciazione, circa 9.000 anni fa, in rocce che hanno circa due milioni di anni.",
  'culture_links':[("Parco nazionale del Vatnajökull", "https://it.wikipedia.org/wiki/Parco_nazionale_del_Vatnajökull"), ("Ghiacciai dell'Islanda", "https://it.wikipedia.org/wiki/Ghiacciai_dell'Islanda")],
  'parking_nav':[
    {'label':'Naviga al parcheggio dell\'hotel','query':'Hotel Burfell Vík Iceland'}
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
    {'time':'17:30','title':'Secret Lagoon','desc':"La piscina geotermica più antica d'Islanda, meno turistica e molto più economica della Blue Lagoon. Alle 17:30 il sole è tramontato da circa un'ora e mezza e il cielo è quasi buio: con cielo sereno potete provare a scorgere l'aurora dall'acqua calda.",'cost':'€ ~4500 ISK / ~31€ a persona, prenotare online','link':'https://secretlagoon.is/','nav':'Secret Lagoon Gamla Laugin Flúðir'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Selfoss (pranzo al sacco o supermercato locale)','note':'Ultima città con supermercati grandi prima di Flúðir, sulla strada da Vík','cost':'€','gf':False},
    {'meal':'Cena','place':'Cucina alla guesthouse o Restaurant Grund','note':'Opzioni senza glutine non confermate: verificate il menu in loco','cost':'€€','gf':False}
  ],
  'accommodation':{'name':'The Hill Guesthouse','detail':'Flúðir · 2 notti · parcheggio gratuito incluso','url':'https://thehillhotel.is/guesthouse-fludir/'},
  'tips':'Prenota la Secret Lagoon in anticipo online: gli slot serali si esauriscono. A novembre lo slot più tardo disponibile è 17:30, non più tardi.',
  'culture':"Kerið è un cratere vulcanico di circa 6.500 anni con un piccolo lago sul fondo, alimentato dalla falda. Le pareti sono formate da scorie di colore rosso, diverse dal basalto nero più comune nella zona. La Secret Lagoon di Flúðir, in islandese Gamla Laugin («la vecchia piscina»), fu costruita nel 1891 ed è considerata la piscina pubblica più antica d'Islanda; l'acqua arriva da sorgenti calde vicine a una temperatura di circa 38-40 °C.",
  'culture_links':[("Lago craterico", "https://it.wikipedia.org/wiki/Lago_craterico")],
  'parking_nav':[
    {'label':'Naviga al parcheggio','query':'The Hill Guesthouse Flúðir'}
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
    {'time':'11:30','title':'Gullfoss','desc':"Cascata a due salti sul fiume Hvítá; d'inverno le rocce intorno sono spesso coperte di ghiaccio.",'cost':'gratis','link':'https://it.wikipedia.org/wiki/Gullfoss','nav':'Gullfoss waterfall parking'},
    {'time':'14:00','title':'Faxi','desc':'Cascata piccola e tranquilla vicino a Reykholt, sulla strada del ritorno verso Flúðir, poco turistica.','cost':'gratis','nav':'Faxi waterfall Iceland parking'},
    {'time':'15:30','title':'Efstidalur II','desc':"Fattoria con gelateria e vacche visibili da dietro un vetro, ambiente al caldo e informale. Sosta comoda per il buio che cala presto in questo periodo, prima del rientro a Flúðir.",'cost':'€ gelato/spuntino a parte','nav':'Efstidalur II Farm'}
  ],
  'food':[
    {'meal':'Pranzo','place':'Friðheimar, Reykholt','note':'Famosa zuppa di pomodoro in serra, sulla strada per Geysir: hanno pane senza glutine, ma non garantito senza contaminazione; in alternativa c\'è un\'insalata','cost':'€€','gf':True},
    {'meal':'Cena','place':'Cucina alla guesthouse','note':'Ultima occasione per finire la spesa fatta al Bónus','cost':'€','gf':False}
  ],
  'accommodation':{'name':'The Hill Guesthouse','detail':'Ultima notte a Flúðir · check-out presto domani · parcheggio gratuito','url':'https://thehillhotel.is/guesthouse-fludir/'},
  'tips':"Da Flúðir Geysir e Gullfoss sono a un tiro di schioppo (circa 30-40 km), molto più vicini che da Reykjavík: giornata comoda, e cielo scuro poco inquinato per tenere d'occhio l'aurora la sera.",
  'culture':"Il Cerchio d'Oro è il percorso turistico che collega il Parco nazionale Þingvellir, la cascata di Gullfoss e l'area geotermica di Haukadalur; il nome è nato per scopi promozionali.\n\nA Haukadalur si trova il Geysir, la sorgente da cui deriva la parola «geyser», oggi quasi sempre inattivo, e lo Strokkur, che erutta ogni 5-10 minuti.\n\nGullfoss («cascata d'oro») è formata dal fiume Hvítá con due salti di circa 11 e 20 metri; secondo la tradizione la sua tutela si deve a Sigríður Tómasdóttir, che all'inizio del Novecento si oppose allo sfruttamento della cascata per produrre energia. A Flúðir l'acqua calda del sottosuolo riscalda le serre, dove si coltivano ortaggi anche in inverno. Faxi è una piccola cascata sul fiume Tungufljót, vicino a Reykholt.",
  'culture_links':[("Cerchio d'Oro", "https://it.wikipedia.org/wiki/Cerchio_d'Oro"), ("Cascate dell'Islanda", "https://it.wikipedia.org/wiki/Cascate_dell'Islanda")],
  'parking_nav':[
    {'label':'Naviga al parcheggio','query':'The Hill Guesthouse Flúðir'}
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
  'culture':"L'Islanda produce quasi tutta la sua elettricità da fonti rinnovabili, soprattutto idroelettrico e geotermia. L'acqua calda geotermica serve anche per il riscaldamento della maggior parte delle abitazioni del paese. L'aeroporto di Keflavík, oggi il principale scalo internazionale dell'isola, fu costruito durante la seconda guerra mondiale dagli Stati Uniti, che vi mantennero una base militare fino al 2006.",
  'culture_links':[("Islanda", "https://it.wikipedia.org/wiki/Islanda"), ("Keflavík", "https://it.wikipedia.org/wiki/Keflavik")],
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
# Stima delle nuvole (vedi tools/research/nuvole.py e leggimi sezione 6):
#   'totale'    nuvolosità totale del modello automatico (DMI HARMONIE in Islanda)
#   'pesata'    stesso modello, strati pesati: bassi contano tutti, medi e alti meno
#   'media'     media della nuvolosità totale dei CLOUD_MODELS
#   'media_pes' media dei CLOUD_MODELS, ognuno con gli strati pesati
CLOUD_METHOD = 'media_pes'
CLOUD_W_MID, CLOUD_W_HIGH = 0.8, 0.3
CLOUD_MODELS = ['best_match', 'ecmwf_ifs025', 'icon_seamless', 'ukmo_seamless', 'metno_seamless', 'gfs_seamless']

# Chiave pubblica VAPID degli avvisi aurora: la privata corrispondente sta solo
# nel secret VAPID_PRIVATE_KEY del repo (vedi leggimi, sezione 5).
VAPID_PUBLIC_KEY = 'BMOzcfKagfPhm6Ax0MRUig7SvV7LoQjp2WzP-YWybYEE0TVCguWI11MTKxO5i2UslqyvHeG6HOtsN08FVa_6yZk'
