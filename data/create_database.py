import sqlite3
import os

# Crea il database SQLite
db_path = os.path.join(os.path.dirname(__file__), 'riza_database.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crea la tabella per le rubriche
cursor.execute('''
CREATE TABLE IF NOT EXISTS rubriche (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disciplina_ambito TEXT NOT NULL,
    ciclo TEXT NOT NULL,
    dimensione_riza TEXT NOT NULL,
    processo_specifico_verbo TEXT NOT NULL,
    livello TEXT NOT NULL,
    livello_numerico INTEGER NOT NULL,
    testo_descrittore TEXT NOT NULL,
    indicatore_criterio TEXT
)
''')

# Crea la tabella per i descrittori RIZA
cursor.execute('''
CREATE TABLE IF NOT EXISTS descrittori_riza (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verbo TEXT NOT NULL,
    dimensione_riza TEXT NOT NULL,
    descrizione TEXT NOT NULL
)
''')

# Crea la tabella per le osservazioni salvate
cursor.execute('''
CREATE TABLE IF NOT EXISTS osservazioni (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    classe TEXT NOT NULL,
    allievo TEXT NOT NULL,
    disciplina_ambito TEXT NOT NULL,
    situazione_problema_attivita TEXT,
    testo_osservazione TEXT NOT NULL,
    dimensione_riza_validata TEXT NOT NULL,
    processo_specifico_verbo_validato TEXT NOT NULL,
    livello_validato TEXT NOT NULL,
    id_descrittore_suggerito INTEGER,
    FOREIGN KEY (id_descrittore_suggerito) REFERENCES rubriche (id)
)
''')

# Popola la tabella dei descrittori RIZA con i dati estratti dal PDF
descrittori_riza = [
    # Interpretazione (descrittori di percezione, capacità passive)
    ("Cogliere", "Interpretazione", "Percepire in un insieme di elementi gli elementi di interesse, non scelti soggettivamente ma definiti da una consegna data all'allievo."),
    ("Identificare", "Interpretazione", "Percepire in un insieme di elementi gli elementi che presentano caratteristiche identiche a quelle di un modello che l'allievo ha in mente."),
    ("Individuare", "Interpretazione", "Percepire in un insieme di elementi quelli che rispettano determinate caratteristiche o criteri."),
    ("Localizzare", "Interpretazione", "Percepire la collocazione spaziale di qualcosa o qualcuno oppure l'area interessata da un fenomeno."),
    ("Riconoscere", "Interpretazione", "Associare un elemento informativo dato ad uno dei modelli già noti."),
    ("Scegliere", "Interpretazione", "Isolare in un insieme di elementi quelli che a proprio avviso rispondono a determinati criteri soggettivi, senza applicare un processo sistematico."),
    ("Selezionare", "Interpretazione", "Isolare in un insieme di elementi quelli che soddisfano un insieme di criteri esterni dati, applicando un processo sistematico."),
    
    # Azione (descrittori di esecuzione, capacità attive)
    ("Analizzare", "Azione", "Scomporre un materiale in parti costituenti e riorganizzarle in una forma differente in base ai propri scopi."),
    ("Attribuire", "Azione", "Verbalizzare i punti di vista, le posizioni, i valori di fondo, gli intenti dei comunicanti, presenti in un materiale anche collegandoli ad una teoria o pensiero di un soggetto."),
    ("Calcolare", "Azione", "Determinare una grandezza facendo uso di operazioni matematiche."),
    ("Classificare", "Azione", "Inserire elementi all'interno di categorie fissate a priori, derivanti da una classificazione monodimensionale o multidimensionale."),
    ("Confrontare", "Azione", "Osservare con attenzione due o più elementi allo scopo di identificare corrispondenze 'uno a uno' tra di loro."),
    ("Costruire", "Azione", "Mettere insieme e comporre prodotti materiali o immateriali, utilizzando determinati saperi e soddisfacendo determinati requisiti."),
    ("Descrivere", "Azione", "Riprodurre verbalmente o per iscritto uno o più segmenti di informazione memorizzata rievocandola dalla propria memoria o ricostruendola sulla base di un insieme strutturato di stimoli."),
    ("Dimostrare", "Azione", "Riprodurre verbalmente i passaggi logici compiuti per giungere da delle premesse a delle conclusioni."),
    ("Eseguire", "Azione", "Mettere in atto una procedura allo scopo di risolvere un problema o raggiungere un obiettivo."),
    
    # Autoregolazione (descrittori di controllo, capacità metacognitive)
    ("Giustificare", "Autoregolazione", "Fornire ragioni a supporto delle proprie scelte o conclusioni, facendo riferimento a criteri esterni."),
    ("Motivare", "Autoregolazione", "Fornire ragioni a supporto delle proprie scelte o conclusioni, facendo riferimento a criteri interni."),
    ("Trovare errori", "Autoregolazione", "Individuare incongruenze o errori in un ragionamento o in una procedura."),
    ("Argomentare", "Autoregolazione", "Esporre le proprie idee sostenendole con prove e ragionamenti logici."),
    ("Valutare", "Autoregolazione", "Esprimere un giudizio basato su criteri e standard."),
    ("Riflettere", "Autoregolazione", "Pensare in modo critico e consapevole sulle proprie azioni, decisioni o processi di pensiero.")
]

# Inserisci i descrittori RIZA
cursor.executemany(
    "INSERT INTO descrittori_riza (verbo, dimensione_riza, descrizione) VALUES (?, ?, ?)",
    descrittori_riza
)

# Popola la tabella delle rubriche con i dati estratti dal PDF
rubriche = [
    # Matematica - Sapere e riconoscere
    ("Matematica", "Secondo ciclo", "Interpretazione", "Sapere e riconoscere (numeri e calcoli)", "Iniziale", 3, "Nell'ambito dei numeri e dei calcoli riconosce gli elementi di base.", ""),
    ("Matematica", "Secondo ciclo", "Interpretazione", "Sapere e riconoscere (numeri e calcoli)", "Base", 4, "Riconosce alcune proprietà e relazioni nell'ambito dei numeri e dei calcoli.", ""),
    ("Matematica", "Secondo ciclo", "Interpretazione", "Sapere e riconoscere (numeri e calcoli)", "Intermedio", 5, "Riconosce proprietà e relazioni nell'ambito dei numeri e dei calcoli.", ""),
    ("Matematica", "Secondo ciclo", "Interpretazione", "Sapere e riconoscere (numeri e calcoli)", "Avanzato", 6, "Riconosce proprietà e relazioni, anche nuove, nell'ambito dei numeri e dei calcoli.", ""),
    
    ("Matematica", "Secondo ciclo", "Interpretazione", "Sapere e riconoscere (grandezze e misure)", "Iniziale", 3, "Nell'ambito delle grandezze e delle misure riconosce gli elementi di base.", ""),
    ("Matematica", "Secondo ciclo", "Interpretazione", "Sapere e riconoscere (grandezze e misure)", "Base", 4, "Riconosce alcune proprietà e relazioni nell'ambito delle grandezze e delle misure.", ""),
    ("Matematica", "Secondo ciclo", "Interpretazione", "Sapere e riconoscere (grandezze e misure)", "Intermedio", 5, "Riconosce proprietà e relazioni nell'ambito delle grandezze e delle misure.", ""),
    ("Matematica", "Secondo ciclo", "Interpretazione", "Sapere e riconoscere (grandezze e misure)", "Avanzato", 6, "Riconosce proprietà e relazioni, anche nuove, nell'ambito delle grandezze e delle misure.", ""),
    
    ("Matematica", "Secondo ciclo", "Interpretazione", "Sapere e riconoscere (geometria)", "Iniziale", 3, "Nell'ambito della geometria riconosce gli elementi di base.", ""),
    ("Matematica", "Secondo ciclo", "Interpretazione", "Sapere e riconoscere (geometria)", "Base", 4, "Riconosce alcune proprietà e relazioni nell'ambito della geometria.", ""),
    ("Matematica", "Secondo ciclo", "Interpretazione", "Sapere e riconoscere (geometria)", "Intermedio", 5, "Riconosce proprietà e relazioni nell'ambito della geometria.", ""),
    ("Matematica", "Secondo ciclo", "Interpretazione", "Sapere e riconoscere (geometria)", "Avanzato", 6, "Riconosce proprietà e relazioni, anche nuove, nell'ambito della geometria.", ""),
    
    # Matematica - Esplorare e provare
    ("Matematica", "Secondo ciclo", "Azione", "Esplorare e provare", "Iniziale", 3, "Di fronte a contesti noti, talvolta esplora per tentativi ed errori.", ""),
    ("Matematica", "Secondo ciclo", "Azione", "Esplorare e provare", "Base", 4, "Esplora per tentativi ed errori, individuando talvolta strategie e procedimenti.", ""),
    ("Matematica", "Secondo ciclo", "Azione", "Esplorare e provare", "Intermedio", 5, "Esplora per tentativi ed errori, individuando strategie e procedimenti.", ""),
    ("Matematica", "Secondo ciclo", "Azione", "Esplorare e provare", "Avanzato", 6, "Esplora in modo approfondito per tentativi ed errori, individuando strategie e procedimenti pertinenti.", ""),
    
    # Matematica - Eseguire e applicare
    ("Matematica", "Secondo ciclo", "Azione", "Eseguire e applicare (calcoli)", "Iniziale", 3, "Con il docente esegue calcoli e trasformazioni di base, applicando parte dei procedimenti.", ""),
    ("Matematica", "Secondo ciclo", "Azione", "Eseguire e applicare (calcoli)", "Base", 4, "Con aiuto esegue calcoli e trasformazioni, applicando procedimenti e concetti.", ""),
    ("Matematica", "Secondo ciclo", "Azione", "Eseguire e applicare (calcoli)", "Intermedio", 5, "Esegue calcoli e trasformazioni, applicando procedimenti e concetti.", ""),
    ("Matematica", "Secondo ciclo", "Azione", "Eseguire e applicare (calcoli)", "Avanzato", 6, "Esegue calcoli e trasformazioni complessi, applicando procedimenti e concetti.", ""),
    
    ("Matematica", "Secondo ciclo", "Azione", "Eseguire e applicare (geometria)", "Iniziale", 3, "Con il docente esegue costruzioni geometriche di base, applicando parte dei procedimenti.", ""),
    ("Matematica", "Secondo ciclo", "Azione", "Eseguire e applicare (geometria)", "Base", 4, "Con aiuto esegue costruzioni geometriche, applicando procedimenti e concetti.", ""),
    ("Matematica", "Secondo ciclo", "Azione", "Eseguire e applicare (geometria)", "Intermedio", 5, "Esegue costruzioni geometriche, applicando procedimenti e concetti.", ""),
    ("Matematica", "Secondo ciclo", "Azione", "Eseguire e applicare (geometria)", "Avanzato", 6, "Esegue costruzioni geometriche complesse, applicando procedimenti e concetti.", ""),
    
    # Matematica - Matematizzare e modellizzare
    ("Matematica", "Secondo ciclo", "Azione", "Matematizzare e modellizzare", "Iniziale", 3, "Con materiali concreti rappresenta e traduce nel linguaggio matematico certe situazioni reali semplici.", ""),
    ("Matematica", "Secondo ciclo", "Azione", "Matematizzare e modellizzare", "Base", 4, "Rappresenta e traduce nel linguaggio matematico situazioni reali semplici, talvolta con materiali concreti.", ""),
    ("Matematica", "Secondo ciclo", "Azione", "Matematizzare e modellizzare", "Intermedio", 5, "Rappresenta e traduce nel linguaggio matematico situazioni reali.", ""),
    ("Matematica", "Secondo ciclo", "Azione", "Matematizzare e modellizzare", "Avanzato", 6, "Rappresenta e traduce nel linguaggio matematico situazioni reali articolate.", ""),
    
    # Matematica - Interpretare e riflettere sui risultati
    ("Matematica", "Secondo ciclo", "Autoregolazione", "Interpretare e riflettere sui risultati", "Iniziale", 3, "Su richiesta riflette sulla pertinenza dei risultati.", ""),
    ("Matematica", "Secondo ciclo", "Autoregolazione", "Interpretare e riflettere sui risultati", "Base", 4, "Su richiesta riflette su procedimenti e risultati.", ""),
    ("Matematica", "Secondo ciclo", "Autoregolazione", "Interpretare e riflettere sui risultati", "Intermedio", 5, "Assume un atteggiamento critico e verifica procedimenti, strategie e risultati.", ""),
    ("Matematica", "Secondo ciclo", "Autoregolazione", "Interpretare e riflettere sui risultati", "Avanzato", 6, "Assume un atteggiamento critico e verifica sistematicamente procedimenti, strategie e risultati, identificando soluzioni alternative.", ""),
    
    # Matematica - Comunicare e argomentare
    ("Matematica", "Secondo ciclo", "Autoregolazione", "Comunicare e argomentare", "Iniziale", 3, "Con una guida comunica alcune riflessioni, scelte e conclusioni.", ""),
    ("Matematica", "Secondo ciclo", "Autoregolazione", "Comunicare e argomentare", "Base", 4, "Comunica alcune riflessioni, scelte e conclusioni.", ""),
    ("Matematica", "Secondo ciclo", "Autoregolazione", "Comunicare e argomentare", "Intermedio", 5, "Comunica e argomenta riflessioni, scelte e conclusioni.", ""),
    ("Matematica", "Secondo ciclo", "Autoregolazione", "Comunicare e argomentare", "Avanzato", 6, "Comunica e argomenta in modo esaustivo riflessioni, scelte e conclusioni.", ""),
    
    # Scienze Umane, Sociali e Naturali - Rappresentare e rappresentarsi
    ("Scienze Umane, Sociali e Naturali", "Secondo ciclo", "Interpretazione", "Rappresentare e rappresentarsi", "Iniziale", 3, "Su richiesta rievoca certe preconoscenze ed esperienze.", ""),
    ("Scienze Umane, Sociali e Naturali", "Secondo ciclo", "Interpretazione", "Rappresentare e rappresentarsi", "Base", 4, "Attribuisce significato a situazioni semplici, rievocando alcune preconoscenze ed esperienze.", ""),
    ("Scienze Umane, Sociali e Naturali", "Secondo ciclo", "Interpretazione", "Rappresentare e rappresentarsi", "Intermedio", 5, "Attribuisce significato a situazioni complesse e articolate, rievocando preconoscenze ed esperienze.", ""),
    ("Scienze Umane, Sociali e Naturali", "Secondo ciclo", "Interpretazione", "Rappresentare e rappresentarsi", "Avanzato", 6, "Attribuisce significato a situazioni complesse e articolate, rievocando e mettendo in relazione preconoscenze ed esperienze.", ""),
    
    # Scienze Umane, Sociali e Naturali - Contestualizzare, identificare, classificare
    ("Scienze Umane, Sociali e Naturali", "Secondo ciclo", "Interpretazione", "Contestualizzare, identificare, classificare", "Iniziale", 3, "Identifica in parte gli elementi caratterizzanti di contesti socioculturali e naturali.", ""),
    ("Scienze Umane, Sociali e Naturali", "Secondo ciclo", "Interpretazione", "Contestualizzare, identificare, classificare", "Base", 4, "Identifica e classifica in parte gli elementi caratterizzanti di contesti socioculturali e naturali.", ""),
    ("Scienze Umane, Sociali e Naturali", "Secondo ciclo", "Interpretazione", "Contestualizzare, identificare, classificare", "Intermedio", 5, "Identifica, classifica e contestualizza gli elementi caratterizzanti di contesti socioculturali e naturali.", ""),
    ("Scienze Umane, Sociali e Naturali", "Secondo ciclo", "Interpretazione", "Contestualizzare, identificare, classificare", "Avanzato", 6, "Identifica, classifica, contestualizza e approfondisce, ponendosi domande, gli elementi caratterizzanti di contesti socioculturali e naturali.", ""),
    
    # Scienze Umane, Sociali e Naturali - Esplorare
    ("Scienze Umane, Sociali e Naturali", "Secondo ciclo", "Azione", "Esplorare", "Iniziale", 3, "Con accompagnamento, esplora alcune domande di ricerca, formulando ipotesi, pianificando strategie d'indagine, raccogliendo e valutando informazioni.", ""),
    ("Scienze Umane, Sociali e Naturali", "Secondo ciclo", "Azione", "Esplorare", "Base", 4, "Con aiuto, esplora le domande di ricerca, formulando ipotesi, pianificando strategie d'indagine, raccogliendo e valutando informazioni.", ""),
    ("Scienze Umane, Sociali e Naturali", "Secondo ciclo", "Azione", "Esplorare", "Intermedio", 5, "Esplora e risponde a domande di ricerca, formula ipotesi, pianifica strategie d'indagine, raccogliendo informazioni e valutandone la pertinenza.", ""),
    ("Scienze Umane, Sociali e Naturali", "Secondo ciclo", "Azione", "Esplorare", "Avanzato", 6, "È in grado di formulare autonomamente domande di ricerca, ipotizza, pianifica strategie d'indagine, raccoglie informazioni e le valuta.", ""),
    
    # Scienze Umane, Sociali e Naturali - Concettualizzare, trasferire, motivare
    ("Scienze Umane, Sociali e Naturali", "Secondo ciclo", "Autoregolazione", "Concettualizzare, trasferire, motivare", "Iniziale", 3, "Replica semplici modelli forniti. Riconosce alcuni procedimenti in ambiti simili.", ""),
    ("Scienze Umane, Sociali e Naturali", "Secondo ciclo", "Autoregolazione", "Concettualizzare, trasferire, motivare", "Base", 4, "Seguendo semplici modelli forniti, spiega i fenomeni indagati. Talvolta motiva le proprie scelte e trasferisce i procedimenti in ambiti simili.", ""),
    ("Scienze Umane, Sociali e Naturali", "Secondo ciclo", "Autoregolazione", "Concettualizzare, trasferire, motivare", "Intermedio", 5, "Spiega i fenomeni indagati, motiva le proprie scelte e trasferisce procedimenti e conclusioni in ambiti simili.", ""),
    ("Scienze Umane, Sociali e Naturali", "Secondo ciclo", "Autoregolazione", "Concettualizzare, trasferire, motivare", "Avanzato", 6, "Spiega i fenomeni indagati, motiva le proprie scelte e trasferisce procedimenti e conclusioni anche in altri ambiti.", "")
]

# Inserisci le rubriche
cursor.executemany(
    "INSERT INTO rubriche (disciplina_ambito, ciclo, dimensione_riza, processo_specifico_verbo, livello, livello_numerico, testo_descrittore, indicatore_criterio) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    rubriche
)

# Commit e chiusura
conn.commit()
conn.close()

print("Database creato con successo!")
