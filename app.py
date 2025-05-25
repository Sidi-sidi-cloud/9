import os
import sqlite3
import json
import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Carica variabili d'ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'chiave_segreta_predefinita')

# Configurazione OpenAI
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
AI_MODEL = os.environ.get('AI_MODEL', 'gpt-3.5-turbo')
MAX_TOKENS = int(os.environ.get('MAX_TOKENS', 1000))
TEMPERATURE = float(os.environ.get('TEMPERATURE', 0.3))
ENABLE_AI = os.environ.get('ENABLE_AI', 'True').lower() in ('true', '1', 't')

# Importa openai solo se abilitato
if ENABLE_AI and OPENAI_API_KEY:
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        print("OpenAI configurato con successo")
    except ImportError:
        print("Libreria OpenAI non disponibile")
        ENABLE_AI = False
    except Exception as e:
        print(f"Errore nella configurazione di OpenAI: {str(e)}")
        ENABLE_AI = False
else:
    print("OpenAI disabilitato o chiave API non configurata")
    ENABLE_AI = False

# Percorsi database
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'riza.db')
ADMIN_DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'admin.db')

# Funzioni di utilità per il database
def get_db_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_admin_db_connection():
    # Assicurati che la directory esista
    os.makedirs(os.path.dirname(ADMIN_DB_PATH), exist_ok=True)
    
    # Verifica se il database admin esiste, altrimenti crealo
    if not os.path.exists(ADMIN_DB_PATH):
        print(f"Database admin non trovato, creazione in corso: {ADMIN_DB_PATH}")
        initialize_admin_db()
    
    conn = get_db_connection(ADMIN_DB_PATH)
    
    # Verifica se le tabelle esistono
    cursor = conn.cursor()
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    table_names = [table[0] for table in tables]
    
    if 'users' not in table_names:
        print("Tabella 'users' non trovata, inizializzazione database admin")
        initialize_admin_db()
        conn = get_db_connection(ADMIN_DB_PATH)  # Riconnetti dopo l'inizializzazione
    
    return conn

def initialize_admin_db():
    """Inizializza il database admin con le tabelle necessarie"""
    print(f"Inizializzazione database admin: {ADMIN_DB_PATH}")
    conn = sqlite3.connect(ADMIN_DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            action_details TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS chatbot_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Verifica se esiste già un utente admin
    admin_exists = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'").fetchone()[0]
    
    if admin_exists == 0:
        # Crea un utente admin predefinito
        admin_password_hash = generate_password_hash('admin123')
        conn.execute('''
            INSERT INTO users (username, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Admin', 'admin@edutools.it', admin_password_hash, 'admin', datetime.datetime.now().isoformat()))
        print("Utente admin creato con successo")
    
    conn.commit()
    conn.close()
    print("Database admin inizializzato con successo")

def initialize_riza_db():
    """Inizializza il database RIZA con le tabelle necessarie"""
    print(f"Inizializzazione database RIZA: {DB_PATH}")
    
    # Assicurati che la directory esista
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    
    # Crea la tabella rubriche se non esiste
    conn.execute('''
        CREATE TABLE IF NOT EXISTS rubriche (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disciplina TEXT,
            dimensione TEXT NOT NULL,
            processo TEXT NOT NULL,
            livello TEXT NOT NULL,
            testo_descrittore TEXT NOT NULL
        )
    ''')
    
    # Crea la tabella osservazioni se non esiste
    conn.execute('''
        CREATE TABLE IF NOT EXISTS osservazioni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            allievo TEXT NOT NULL,
            classe TEXT NOT NULL,
            disciplina TEXT NOT NULL,
            data TEXT NOT NULL,
            situazione TEXT,
            osservazione TEXT NOT NULL,
            dimensione TEXT NOT NULL,
            processo TEXT NOT NULL,
            livello TEXT NOT NULL,
            data_creazione TEXT NOT NULL
        )
    ''')
    
    # Verifica se ci sono già dati nella tabella rubriche
    rubriche_count = conn.execute("SELECT COUNT(*) FROM rubriche").fetchone()[0]
    
    if rubriche_count == 0:
        # Inserisci alcuni dati di esempio nelle rubriche
        rubriche_data = [
            # Dimensione: Risorse
            ('Matematica', 'Risorse', 'Recuperare', 'Iniziale', "L'allievo, se guidato, recupera alcune conoscenze essenziali."),
            ('Matematica', 'Risorse', 'Recuperare', 'Base', "L'allievo recupera le conoscenze fondamentali."),
            ('Matematica', 'Risorse', 'Recuperare', 'Intermedio', "L'allievo recupera le conoscenze in modo pertinente e completo."),
            ('Matematica', 'Risorse', 'Recuperare', 'Avanzato', "L'allievo recupera le conoscenze in modo pertinente, completo e approfondito."),
            
            ('Matematica', 'Risorse', 'Selezionare', 'Iniziale', "L'allievo, se guidato, seleziona alcune informazioni essenziali."),
            ('Matematica', 'Risorse', 'Selezionare', 'Base', "L'allievo seleziona le informazioni fondamentali."),
            ('Matematica', 'Risorse', 'Selezionare', 'Intermedio', "L'allievo seleziona le informazioni in modo pertinente e completo."),
            ('Matematica', 'Risorse', 'Selezionare', 'Avanzato', "L'allievo seleziona le informazioni in modo pertinente, completo e approfondito."),
            
            # Dimensione: Interpretazione
            ('Matematica', 'Interpretazione', 'Analizzare', 'Iniziale', "L'allievo, se guidato, analizza alcuni aspetti essenziali."),
            ('Matematica', 'Interpretazione', 'Analizzare', 'Base', "L'allievo analizza gli aspetti fondamentali."),
            ('Matematica', 'Interpretazione', 'Analizzare', 'Intermedio', "L'allievo analizza in modo pertinente e completo."),
            ('Matematica', 'Interpretazione', 'Analizzare', 'Avanzato', "L'allievo analizza in modo pertinente, completo e approfondito."),
            
            ('Matematica', 'Interpretazione', 'Inferire', 'Iniziale', "L'allievo, se guidato, inferisce alcune relazioni essenziali."),
            ('Matematica', 'Interpretazione', 'Inferire', 'Base', "L'allievo inferisce le relazioni fondamentali."),
            ('Matematica', 'Interpretazione', 'Inferire', 'Intermedio', "L'allievo inferisce relazioni in modo pertinente e completo."),
            ('Matematica', 'Interpretazione', 'Inferire', 'Avanzato', "L'allievo inferisce relazioni in modo pertinente, completo e approfondito."),
            
            # Dimensione: Azione
            ('Matematica', 'Azione', 'Pianificare', 'Iniziale', "L'allievo, se guidato, pianifica alcune azioni essenziali."),
            ('Matematica', 'Azione', 'Pianificare', 'Base', "L'allievo pianifica le azioni fondamentali."),
            ('Matematica', 'Azione', 'Pianificare', 'Intermedio', "L'allievo pianifica in modo pertinente e completo."),
            ('Matematica', 'Azione', 'Pianificare', 'Avanzato', "L'allievo pianifica in modo pertinente, completo e approfondito."),
            
            ('Matematica', 'Azione', 'Implementare', 'Iniziale', "L'allievo, se guidato, implementa alcune procedure essenziali."),
            ('Matematica', 'Azione', 'Implementare', 'Base', "L'allievo implementa le procedure fondamentali."),
            ('Matematica', 'Azione', 'Implementare', 'Intermedio', "L'allievo implementa procedure in modo pertinente e completo."),
            ('Matematica', 'Azione', 'Implementare', 'Avanzato', "L'allievo implementa procedure in modo pertinente, completo e approfondito."),
            
            # Dimensione: Autoregolazione
            ('Matematica', 'Autoregolazione', 'Monitorare', 'Iniziale', "L'allievo, se guidato, monitora alcuni aspetti essenziali del proprio lavoro."),
            ('Matematica', 'Autoregolazione', 'Monitorare', 'Base', "L'allievo monitora gli aspetti fondamentali del proprio lavoro."),
            ('Matematica', 'Autoregolazione', 'Monitorare', 'Intermedio', "L'allievo monitora il proprio lavoro in modo pertinente e completo."),
            ('Matematica', 'Autoregolazione', 'Monitorare', 'Avanzato', "L'allievo monitora il proprio lavoro in modo pertinente, completo e approfondito."),
            
            ('Matematica', 'Autoregolazione', 'Adattare', 'Iniziale', "L'allievo, se guidato, adatta alcuni aspetti essenziali del proprio approccio."),
            ('Matematica', 'Autoregolazione', 'Adattare', 'Base', "L'allievo adatta gli aspetti fondamentali del proprio approccio."),
            ('Matematica', 'Autoregolazione', 'Adattare', 'Intermedio', "L'allievo adatta il proprio approccio in modo pertinente e completo."),
            ('Matematica', 'Autoregolazione', 'Adattare', 'Avanzato', "L'allievo adatta il proprio approccio in modo pertinente, completo e approfondito.")
        ]
        
        conn.executemany('''
            INSERT INTO rubriche (disciplina, dimensione, processo, livello, testo_descrittore)
            VALUES (?, ?, ?, ?, ?)
        ''', rubriche_data)
        
        print(f"Inseriti {len(rubriche_data)} descrittori RIZA di esempio")
    
    conn.commit()
    conn.close()
    print("Database RIZA inizializzato con successo")

# Inizializza i database all'avvio dell'applicazione
initialize_riza_db()
initialize_admin_db()

# Funzioni di utilità per l'autenticazione
def init_session(user_id, username, email, role):
    session['user_id'] = user_id
    session['user_name'] = username
    session['user_email'] = email
    session['user_role'] = role
    session['logged_in'] = True

def is_logged_in():
    return session.get('logged_in', False)

def is_admin():
    return session.get('user_role') == 'admin'

# Middleware per richiedere autenticazione
def login_required(f):
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not is_logged_in() or not is_admin():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Funzioni di utilità per l'AI
def query_openai(prompt, model=AI_MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE):
    if not ENABLE_AI or not OPENAI_API_KEY:
        print("AI non disponibile: ENABLE_AI =", ENABLE_AI, "API_KEY presente =", bool(OPENAI_API_KEY))
        return {"error": "Funzionalità AI non disponibile. Verifica la configurazione delle variabili d'ambiente."}
    
    try:
        import openai
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": "Sei un assistente esperto in valutazione formativa e modello RIZA."},
                      {"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return {"response": response.choices[0].message.content}
    except ImportError:
        print("Errore: libreria OpenAI non disponibile")
        return {"error": "Libreria OpenAI non disponibile"}
    except Exception as e:
        print(f"Errore OpenAI: {str(e)}")
        return {"error": f"Errore durante la chiamata all'API: {str(e)}"}

def analyze_observation_with_ai(osservazione, situazione=""):
    prompt = f"""
    Analizza la seguente osservazione di un allievo e classificala secondo il modello RIZA.
    
    Osservazione: {osservazione}
    
    {f'Contesto: {situazione}' if situazione else ''}
    
    Rispondi in formato JSON con i seguenti campi:
    - dimensione: una delle seguenti (Risorse, Interpretazione, Azione, Autoregolazione)
    - processo: il processo specifico all'interno della dimensione
    - livello: uno tra (Iniziale, Base, Intermedio, Avanzato)
    - dimensione_confidence: livello di confidenza (high, medium, low)
    - processo_confidence: livello di confidenza (high, medium, low)
    - livello_confidence: livello di confidenza (high, medium, low)
    - explanation: breve spiegazione della classificazione
    
    Esempio di risposta:
    {
        "dimensione": "Interpretazione",
        "processo": "Analizzare",
        "livello": "Intermedio",
        "dimensione_confidence": "high",
        "processo_confidence": "medium",
        "livello_confidence": "medium",
        "explanation": "L'osservazione mostra che l'allievo è in grado di analizzare situazioni problematiche identificando i dati rilevanti e le relazioni tra essi."
    }
    """
    
    try:
        result = query_openai(prompt)
        if "error" in result:
            return {"success": False, "error": result["error"]}
        
        # Estrai il JSON dalla risposta
        response_text = result["response"]
        # Trova l'inizio e la fine del JSON
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            try:
                analysis = json.loads(json_str)
                analysis["success"] = True
                return analysis
            except json.JSONDecodeError:
                return {"success": False, "error": "Impossibile interpretare la risposta dell'AI"}
        else:
            return {"success": False, "error": "Formato di risposta non valido"}
    except Exception as e:
        print(f"Errore nell'analisi AI: {str(e)}")
        return {"success": False, "error": f"Errore durante l'analisi: {str(e)}"}

def get_chatbot_response(query):
    prompt = f"""
    Sei un assistente esperto in didattica e pedagogia, specializzato nel supporto ai docenti.
    
    Domanda del docente: {query}
    
    Fornisci una risposta dettagliata, professionale e utile. Includi esempi pratici quando possibile.
    Alla fine della risposta, suggerisci 3 domande correlate che il docente potrebbe voler fare come follow-up.
    """
    
    try:
        result = query_openai(prompt, max_tokens=1500)
        if "error" in result:
            return {"success": False, "error": result["error"]}
        
        response = result["response"]
        
        # Estrai suggerimenti per domande correlate
        suggestions = []
        if "domande correlate" in response.lower() or "domande di follow-up" in response.lower():
            lines = response.split('\n')
            for i, line in enumerate(lines):
                if "domande" in line.lower() and ":" in line:
                    # Cerca le domande nelle righe successive
                    j = i + 1
                    while j < len(lines) and j < i + 6:  # Cerca nelle prossime 5 righe
                        line = lines[j].strip()
                        if line and (line.startswith('-') or line.startswith('*') or line[0].isdigit() and line[1] in ['.', ')', ']']):
                            question = line.lstrip('-*0123456789.) ').strip()
                            if question and len(question) > 10:  # Ignora righe troppo corte
                                suggestions.append(question)
                        j += 1
        
        # Se non abbiamo trovato suggerimenti, genera domande generiche
        if not suggestions:
            suggestions = [
                "Come posso adattare questo approccio per studenti con bisogni speciali?",
                "Quali risorse consigli per approfondire questo argomento?",
                "Come posso valutare l'efficacia di questo metodo?"
            ]
        
        return {
            "success": True,
            "response": response,
            "suggestions": suggestions[:3]  # Limita a 3 suggerimenti
        }
    except Exception as e:
        print(f"Errore nella risposta del chatbot: {str(e)}")
        return {"success": False, "error": f"Errore durante l'elaborazione: {str(e)}"}

# Funzioni di utilità per il modello RIZA
def get_discipline():
    conn = get_db_connection()
    discipline = [row[0] for row in conn.execute('SELECT DISTINCT disciplina FROM rubriche').fetchall()]
    conn.close()
    return discipline

def get_dimensioni():
    conn = get_db_connection()
    dimensioni = [row[0] for row in conn.execute('SELECT DISTINCT dimensione FROM rubriche').fetchall()]
    conn.close()
    return dimensioni

def get_processi(dimensione):
    conn = get_db_connection()
    processi = [row[0] for row in conn.execute('SELECT DISTINCT processo FROM rubriche WHERE dimensione = ?', (dimensione,)).fetchall()]
    conn.close()
    return processi

def get_livelli(dimensione, processo):
    conn = get_db_connection()
    livelli = [row[0] for row in conn.execute('SELECT DISTINCT livello FROM rubriche WHERE dimensione = ? AND processo = ? ORDER BY CASE livello WHEN "Iniziale" THEN 1 WHEN "Base" THEN 2 WHEN "Intermedio" THEN 3 WHEN "Avanzato" THEN 4 ELSE 5 END', (dimensione, processo)).fetchall()]
    conn.close()
    return livelli

def get_descrittore(dimensione, processo, livello):
    conn = get_db_connection()
    descrittore = conn.execute('SELECT testo_descrittore FROM rubriche WHERE dimensione = ? AND processo = ? AND livello = ?', (dimensione, processo, livello)).fetchone()
    conn.close()
    return descrittore[0] if descrittore else None

def get_observation_details(observation_id):
    conn = get_db_connection()
    observation = conn.execute('SELECT * FROM osservazioni WHERE id = ?', (observation_id,)).fetchone()
    conn.close()
    
    if observation:
        # Converti Row in dict
        obs_dict = dict(observation)
        
        # Aggiungi il descrittore RIZA
        descrittore = get_descrittore(obs_dict['dimensione'], obs_dict['processo'], obs_dict['livello'])
        obs_dict['testo_descrittore'] = descrittore
        
        return obs_dict
    return None

def suggest_riza_classification(text):
    """Suggerisce una classificazione RIZA basata sul testo dell'osservazione usando TF-IDF e similarità del coseno"""
    conn = get_db_connection()
    rubriche = conn.execute('SELECT dimensione, processo, livello, testo_descrittore FROM rubriche').fetchall()
    conn.close()
    
    if not rubriche:
        return None
    
    # Prepara i dati per TF-IDF
    descrittori = [r['testo_descrittore'] for r in rubriche]
    
    # Calcola TF-IDF e similarità
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform(descrittori + [text])
        cosine_similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])[0]
        
        # Trova l'indice del descrittore più simile
        max_index = np.argmax(cosine_similarities)
        max_similarity = cosine_similarities[max_index]
        
        # Determina il livello di confidenza
        if max_similarity > 0.3:
            confidence = "high"
        elif max_similarity > 0.2:
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            "dimensione": rubriche[max_index]['dimensione'],
            "processo": rubriche[max_index]['processo'],
            "livello": rubriche[max_index]['livello'],
            "confidence": confidence,
            "similarity": max_similarity
        }
    except Exception as e:
        print(f"Errore nell'analisi TF-IDF: {str(e)}")
        return None

# Funzioni per la gestione degli utenti e delle statistiche
def log_observation(user_id, observation_data):
    """Registra una nuova osservazione nel database admin"""
    conn = get_admin_db_connection()
    conn.execute('''
        INSERT INTO activity_log (user_id, action_type, action_details, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (user_id, 'observation', json.dumps(observation_data), datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def log_chatbot_query(user_id, query, response):
    """Registra una query al chatbot nel database admin"""
    conn = get_admin_db_connection()
    conn.execute('''
        INSERT INTO chatbot_log (user_id, query, response, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (user_id, query, response, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_stats(user_id=None):
    """Ottiene statistiche di utilizzo per un utente o per tutti gli utenti"""
    conn = get_admin_db_connection()
    
    if user_id:
        # Statistiche per un singolo utente
        observations = conn.execute('SELECT COUNT(*) FROM activity_log WHERE user_id = ? AND action_type = "observation"', (user_id,)).fetchone()[0]
        chatbot_queries = conn.execute('SELECT COUNT(*) FROM chatbot_log WHERE user_id = ?', (user_id,)).fetchone()[0]
        last_activity = conn.execute('''
            SELECT MAX(timestamp) FROM (
                SELECT timestamp FROM activity_log WHERE user_id = ?
                UNION ALL
                SELECT timestamp FROM chatbot_log WHERE user_id = ?
            )
        ''', (user_id, user_id)).fetchone()[0]
        
        stats = {
            "observations": observations,
            "chatbot_queries": chatbot_queries,
            "last_activity": last_activity
        }
    else:
        # Statistiche globali
        total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        total_observations = conn.execute('SELECT COUNT(*) FROM activity_log WHERE action_type = "observation"').fetchone()[0]
        total_chatbot_queries = conn.execute('SELECT COUNT(*) FROM chatbot_log').fetchone()[0]
        active_users_today = conn.execute('''
            SELECT COUNT(DISTINCT user_id) FROM (
                SELECT user_id FROM activity_log WHERE date(timestamp) = date('now')
                UNION
                SELECT user_id FROM chatbot_log WHERE date(timestamp) = date('now')
            )
        ''').fetchone()[0]
        
        stats = {
            "total_users": total_users,
            "total_observations": total_observations,
            "total_chatbot_queries": total_chatbot_queries,
            "active_users_today": active_users_today
        }
    
    conn.close()
    return stats

# Rotte dell'applicazione
@app.route('/')
def home():
    # Reindirizza alla pagina di login se non autenticato
    if not is_logged_in():
        return redirect(url_for('login'))
    
    # Ottieni le osservazioni recenti
    conn = get_db_connection()
    recent_observations = conn.execute('SELECT * FROM osservazioni ORDER BY data_creazione DESC LIMIT 5').fetchall()
    conn.close()
    
    # Converti Row objects in dict
    recent_observations = [dict(obs) for obs in recent_observations] if recent_observations else []
    
    # Ottieni statistiche
    observation_count = len(conn.execute('SELECT id FROM osservazioni').fetchall())
    
    return render_template('home.html', 
                          recent_observations=recent_observations,
                          observation_count=observation_count)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_admin_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            init_session(user['id'], user['username'], user['email'], user['role'])
            return redirect(url_for('home'))
        else:
            error = 'Credenziali non valide. Riprova.'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')

@app.route('/chatbot_query', methods=['POST'])
@login_required
def chatbot_query():
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({"success": False, "error": "Query vuota"})
    
    # Prova prima con OpenAI
    if ENABLE_AI and OPENAI_API_KEY:
        response = get_chatbot_response(query)
        if response["success"]:
            # Log della query
            log_chatbot_query(session.get('user_id'), query, response["response"])
            return jsonify(response)
    
    # Fallback a risposte predefinite
    fallback_response = {
        "success": True,
        "response": "Mi dispiace, non sono in grado di rispondere a questa domanda al momento. Prova a riformulare la tua richiesta o contatta il supporto tecnico.",
        "suggestions": [
            "Come posso strutturare una lezione efficace?",
            "Quali sono le migliori pratiche per la valutazione formativa?",
            "Come gestire una classe con alunni di diversi livelli?"
        ]
    }
    
    # Log della query fallita
    log_chatbot_query(session.get('user_id'), query, fallback_response["response"])
    
    return jsonify(fallback_response)

@app.route('/valutazione', methods=['GET', 'POST'])
@login_required
def valutazione():
    if request.method == 'POST':
        # Raccogli i dati dal form
        allievo = request.form.get('allievo')
        classe = request.form.get('classe')
        disciplina = request.form.get('disciplina')
        data = request.form.get('data')
        situazione = request.form.get('situazione')
        osservazione = request.form.get('osservazione')
        dimensione = request.form.get('dimensione')
        processo = request.form.get('processo')
        livello = request.form.get('livello')
        
        # Validazione base
        if not all([allievo, classe, disciplina, data, osservazione, dimensione, processo, livello]):
            return render_template('index.html', 
                                  error="Tutti i campi sono obbligatori",
                                  discipline=get_discipline(),
                                  dimensioni=get_dimensioni(),
                                  today=datetime.date.today().isoformat())
        
        # Salva l'osservazione nel database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO osservazioni (allievo, classe, disciplina, data, situazione, osservazione, dimensione, processo, livello, data_creazione)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (allievo, classe, disciplina, data, situazione, osservazione, dimensione, processo, livello, datetime.datetime.now().isoformat()))
        
        observation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Log dell'attività
        observation_data = {
            "id": observation_id,
            "allievo": allievo,
            "classe": classe,
            "disciplina": disciplina,
            "dimensione": dimensione,
            "processo": processo,
            "livello": livello
        }
        log_observation(session.get('user_id'), observation_data)
        
        # Reindirizza alla pagina di visualizzazione
        return redirect(url_for('view_observations'))
    
    # GET request
    return render_template('index.html', 
                          discipline=get_discipline(),
                          dimensioni=get_dimensioni(),
                          today=datetime.date.today().isoformat())

@app.route('/view_observations')
@login_required
def view_observations():
    # Parametri di ricerca
    allievo = request.args.get('allievo', '')
    classe = request.args.get('classe', '')
    disciplina = request.args.get('disciplina', '')
    dimensione = request.args.get('dimensione', '')
    
    # Costruisci la query SQL
    query = 'SELECT * FROM osservazioni WHERE 1=1'
    params = []
    
    if allievo:
        query += ' AND allievo LIKE ?'
        params.append(f'%{allievo}%')
    
    if classe:
        query += ' AND classe LIKE ?'
        params.append(f'%{classe}%')
    
    if disciplina:
        query += ' AND disciplina = ?'
        params.append(disciplina)
    
    if dimensione:
        query += ' AND dimensione = ?'
        params.append(dimensione)
    
    query += ' ORDER BY data_creazione DESC'
    
    # Esegui la query
    conn = get_db_connection()
    observations = conn.execute(query, params).fetchall()
    conn.close()
    
    # Converti Row objects in dict
    observations = [dict(obs) for obs in observations] if observations else []
    
    return render_template('view_observations.html', 
                          observations=observations,
                          discipline=get_discipline(),
                          dimensioni=get_dimensioni())

@app.route('/get_observation_details/<int:observation_id>')
@login_required
def get_observation_details_route(observation_id):
    observation = get_observation_details(observation_id)
    
    if observation:
        return jsonify({"success": True, "observation": observation})
    else:
        return jsonify({"success": False, "error": "Osservazione non trovata"})

@app.route('/get_processi/<dimensione>')
@login_required
def get_processi_route(dimensione):
    processi = get_processi(dimensione)
    return jsonify({"success": True, "processi": processi})

@app.route('/get_livelli/<dimensione>/<processo>')
@login_required
def get_livelli_route(dimensione, processo):
    livelli = get_livelli(dimensione, processo)
    return jsonify({"success": True, "livelli": livelli})

@app.route('/get_descrittore/<dimensione>/<processo>/<livello>')
@login_required
def get_descrittore_route(dimensione, processo, livello):
    descrittore = get_descrittore(dimensione, processo, livello)
    if descrittore:
        return jsonify({"success": True, "descrittore": descrittore})
    else:
        return jsonify({"success": False, "error": "Descrittore non trovato"})

@app.route('/analyze_observation', methods=['POST'])
@login_required
def analyze_observation_route():
    data = request.get_json()
    osservazione = data.get('osservazione', '')
    situazione = data.get('situazione', '')
    
    if not osservazione:
        return jsonify({"success": False, "error": "Osservazione vuota"})
    
    # Prova prima con OpenAI
    if ENABLE_AI and OPENAI_API_KEY:
        analysis = analyze_observation_with_ai(osservazione, situazione)
        if analysis["success"]:
            return jsonify(analysis)
    
    # Fallback a TF-IDF
    suggestion = suggest_riza_classification(osservazione)
    
    if suggestion:
        return jsonify({
            "success": True,
            "dimensione": suggestion["dimensione"],
            "processo": suggestion["processo"],
            "livello": suggestion["livello"],
            "dimensione_confidence": suggestion["confidence"],
            "processo_confidence": suggestion["confidence"],
            "livello_confidence": suggestion["confidence"],
            "explanation": "Questa classificazione è basata sull'analisi del testo dell'osservazione e sulla sua similarità con i descrittori RIZA. Verifica la correttezza e modifica se necessario."
        })
    else:
        return jsonify({
            "success": False,
            "error": "Non è stato possibile analizzare l'osservazione. Inserisci manualmente la classificazione."
        })

# Rotte per l'amministrazione
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    stats = get_user_stats()
    
    # Ottieni dati per i grafici
    conn = get_admin_db_connection()
    
    # Attività per giorno (ultimi 7 giorni)
    activity_by_day = conn.execute('''
        SELECT date(timestamp) as day, COUNT(*) as count FROM (
            SELECT timestamp FROM activity_log WHERE date(timestamp) >= date('now', '-7 days')
            UNION ALL
            SELECT timestamp FROM chatbot_log WHERE date(timestamp) >= date('now', '-7 days')
        ) GROUP BY day ORDER BY day
    ''').fetchall()
    
    # Osservazioni per dimensione
    observations_by_dimension = conn.execute('''
        SELECT json_extract(action_details, '$.dimensione') as dimension, COUNT(*) as count 
        FROM activity_log 
        WHERE action_type = 'observation' 
        GROUP BY dimension
    ''').fetchall()
    
    # Utenti più attivi
    active_users = conn.execute('''
        SELECT u.username, COUNT(*) as activity_count FROM (
            SELECT user_id FROM activity_log
            UNION ALL
            SELECT user_id FROM chatbot_log
        ) as activities
        JOIN users u ON activities.user_id = u.id
        GROUP BY u.id
        ORDER BY activity_count DESC
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                          stats=stats,
                          activity_by_day=activity_by_day,
                          observations_by_dimension=observations_by_dimension,
                          active_users=active_users)

@app.route('/admin/users')
@admin_required
def admin_users():
    conn = get_admin_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY username').fetchall()
    conn.close()
    
    # Aggiungi statistiche per ogni utente
    for user in users:
        user_stats = get_user_stats(user['id'])
        user['stats'] = user_stats
    
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/add', methods=['POST'])
@admin_required
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'user')
    
    if not all([username, email, password]):
        return jsonify({"success": False, "error": "Tutti i campi sono obbligatori"})
    
    # Verifica se l'email è già in uso
    conn = get_admin_db_connection()
    existing_user = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
    
    if existing_user:
        conn.close()
        return jsonify({"success": False, "error": "Email già in uso"})
    
    # Crea il nuovo utente
    password_hash = generate_password_hash(password)
    
    conn.execute('''
        INSERT INTO users (username, email, password_hash, role, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, email, password_hash, role, datetime.datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route('/admin/users/edit/<int:user_id>', methods=['POST'])
@admin_required
def edit_user(user_id):
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')
    
    if not all([username, email, role]):
        return jsonify({"success": False, "error": "Username, email e ruolo sono obbligatori"})
    
    conn = get_admin_db_connection()
    
    # Verifica se l'utente esiste
    user = conn.execute('SELECT id FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if not user:
        conn.close()
        return jsonify({"success": False, "error": "Utente non trovato"})
    
    # Aggiorna l'utente
    if password:
        password_hash = generate_password_hash(password)
        conn.execute('''
            UPDATE users SET username = ?, email = ?, password_hash = ?, role = ?
            WHERE id = ?
        ''', (username, email, password_hash, role, user_id))
    else:
        conn.execute('''
            UPDATE users SET username = ?, email = ?, role = ?
            WHERE id = ?
        ''', (username, email, role, user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    conn = get_admin_db_connection()
    
    # Verifica se l'utente esiste
    user = conn.execute('SELECT id FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if not user:
        conn.close()
        return jsonify({"success": False, "error": "Utente non trovato"})
    
    # Elimina l'utente
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route('/admin/conversations')
@admin_required
def admin_conversations():
    conn = get_admin_db_connection()
    
    # Ottieni tutte le conversazioni
    conversations = conn.execute('''
        SELECT c.id, u.username, c.query, c.response, c.timestamp
        FROM chatbot_log c
        JOIN users u ON c.user_id = u.id
        ORDER BY c.timestamp DESC
        LIMIT 100
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_conversations.html', conversations=conversations)

# Rotta per verificare lo stato dell'API
@app.route('/api_status')
@login_required
def api_status():
    status = {
        "enable_ai": ENABLE_AI,
        "api_key_configured": bool(OPENAI_API_KEY),
        "model": AI_MODEL,
        "environment_variables": {
            "OPENAI_API_KEY": "Configurata" if OPENAI_API_KEY else "Non configurata",
            "AI_MODEL": AI_MODEL,
            "MAX_TOKENS": MAX_TOKENS,
            "TEMPERATURE": TEMPERATURE,
            "ENABLE_AI": ENABLE_AI
        }
    }
    
    # Solo per admin, mostra dettagli completi
    if is_admin():
        return jsonify(status)
    
    # Per utenti normali, mostra solo lo stato base
    return jsonify({
        "enable_ai": ENABLE_AI,
        "api_key_configured": bool(OPENAI_API_KEY)
    })

# Avvio dell'applicazione
if __name__ == '__main__':
    # Stampa informazioni di debug all'avvio
    print(f"Configurazione OpenAI:")
    print(f"- API Key configurata: {bool(OPENAI_API_KEY)}")
    print(f"- AI abilitata: {ENABLE_AI}")
    print(f"- Modello: {AI_MODEL}")
    print(f"- Max tokens: {MAX_TOKENS}")
    print(f"- Temperatura: {TEMPERATURE}")
    
    app.run(debug=True, host='0.0.0.0')
