"""
Script di correzione per problemi comuni su Render
Questo script verifica e corregge i problemi più comuni che possono verificarsi
durante il deployment dell'applicazione EduTools su Render.
"""

import os
import sqlite3
import sys
from pathlib import Path
from werkzeug.security import generate_password_hash
import datetime

def main():
    print("Avvio script di correzione per EduTools su Render")
    
    # Verifica percorsi e directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    
    # Crea directory data se non esiste
    if not os.path.exists(data_dir):
        print(f"Creazione directory data: {data_dir}")
        os.makedirs(data_dir, exist_ok=True)
    
    # Percorsi database
    riza_db_path = os.path.join(data_dir, 'riza.db')
    admin_db_path = os.path.join(data_dir, 'admin.db')
    
    # Verifica e inizializza database RIZA
    initialize_riza_db(riza_db_path)
    
    # Verifica e inizializza database Admin
    initialize_admin_db(admin_db_path)
    
    # Verifica variabili d'ambiente
    check_environment_variables()
    
    print("Script di correzione completato con successo")

def initialize_riza_db(db_path):
    """Inizializza il database RIZA con le tabelle necessarie"""
    print(f"Verifica database RIZA: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
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
        print("Inserimento dati di esempio nelle rubriche...")
        # Inserisci alcuni dati di esempio nelle rubriche
        rubriche_data = [
            # Dimensione: Risorse
            ('Matematica', 'Risorse', 'Recuperare', 'Iniziale', 'L'allievo, se guidato, recupera alcune conoscenze essenziali.'),
            ('Matematica', 'Risorse', 'Recuperare', 'Base', 'L'allievo recupera le conoscenze fondamentali.'),
            ('Matematica', 'Risorse', 'Recuperare', 'Intermedio', 'L'allievo recupera le conoscenze in modo pertinente e completo.'),
            ('Matematica', 'Risorse', 'Recuperare', 'Avanzato', 'L'allievo recupera le conoscenze in modo pertinente, completo e approfondito.'),
            
            # Aggiungi altri dati di esempio come necessario
            ('Matematica', 'Interpretazione', 'Analizzare', 'Iniziale', 'L'allievo, se guidato, analizza alcuni aspetti essenziali.'),
            ('Matematica', 'Interpretazione', 'Analizzare', 'Base', 'L'allievo analizza gli aspetti fondamentali.'),
            ('Matematica', 'Interpretazione', 'Analizzare', 'Intermedio', 'L'allievo analizza in modo pertinente e completo.'),
            ('Matematica', 'Interpretazione', 'Analizzare', 'Avanzato', 'L'allievo analizza in modo pertinente, completo e approfondito.')
        ]
        
        conn.executemany('''
            INSERT INTO rubriche (disciplina, dimensione, processo, livello, testo_descrittore)
            VALUES (?, ?, ?, ?, ?)
        ''', rubriche_data)
        
        print(f"Inseriti {len(rubriche_data)} descrittori RIZA di esempio")
    else:
        print(f"Database RIZA già popolato con {rubriche_count} descrittori")
    
    conn.commit()
    conn.close()
    print("Verifica database RIZA completata")

def initialize_admin_db(db_path):
    """Inizializza il database admin con le tabelle necessarie"""
    print(f"Verifica database admin: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
    # Crea le tabelle necessarie
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
        print("Creazione utente admin predefinito...")
        # Crea un utente admin predefinito
        admin_password_hash = generate_password_hash('admin123')
        conn.execute('''
            INSERT INTO users (username, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Admin', 'admin@edutools.it', admin_password_hash, 'admin', datetime.datetime.now().isoformat()))
        print("Utente admin creato con successo")
    else:
        print("Utente admin già esistente")
    
    conn.commit()
    conn.close()
    print("Verifica database admin completata")

def check_environment_variables():
    """Verifica la presenza delle variabili d'ambiente necessarie"""
    print("Verifica variabili d'ambiente...")
    
    required_vars = [
        ('OPENAI_API_KEY', 'Chiave API OpenAI'),
        ('SECRET_KEY', 'Chiave segreta Flask'),
        ('ENABLE_AI', 'Abilitazione AI (True/False)'),
        ('AI_MODEL', 'Modello AI (default: gpt-3.5-turbo)'),
        ('MAX_TOKENS', 'Numero massimo di token (default: 1000)'),
        ('TEMPERATURE', 'Temperatura AI (default: 0.3)')
    ]
    
    missing_vars = []
    
    for var_name, var_desc in required_vars:
        if not os.environ.get(var_name):
            missing_vars.append((var_name, var_desc))
    
    if missing_vars:
        print("\nATTENZIONE: Le seguenti variabili d'ambiente non sono configurate:")
        for var_name, var_desc in missing_vars:
            print(f"- {var_name}: {var_desc}")
        print("\nConfigura queste variabili nella dashboard di Render per il corretto funzionamento dell'applicazione.")
    else:
        print("Tutte le variabili d'ambiente necessarie sono configurate.")

if __name__ == "__main__":
    main()
