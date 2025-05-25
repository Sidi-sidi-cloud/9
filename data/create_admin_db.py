import sqlite3
import os

# Crea la directory data se non esiste
os.makedirs(os.path.dirname(os.path.abspath(__file__)) + '/data', exist_ok=True)

# Percorso del database
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'riza.db')

# Crea una connessione al database
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Crea le tabelle necessarie per la gestione utenti e amministrazione
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'docente',
    status TEXT NOT NULL DEFAULT 'attivo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)
''')

# Crea la tabella per le attività degli utenti
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Crea la tabella per le conversazioni
cursor.execute('''
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tool TEXT NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Inserisci alcuni utenti di esempio se la tabella è vuota
cursor.execute('SELECT COUNT(*) FROM users')
if cursor.fetchone()[0] == 0:
    users = [
        ('Admin Sistema', 'admin@edutools.it', 'admin123', 'admin', 'attivo'),
        ('Marco Rossi', 'marco.rossi@scuola.edu', 'password123', 'docente', 'attivo'),
        ('Laura Bianchi', 'laura.bianchi@scuola.edu', 'password123', 'docente', 'attivo'),
        ('Giovanni Verdi', 'giovanni.verdi@scuola.edu', 'password123', 'coordinatore', 'inattivo'),
        ('Francesca Neri', 'francesca.neri@scuola.edu', 'password123', 'docente', 'sospeso'),
        ('Antonio Russo', 'antonio.russo@scuola.edu', 'password123', 'docente', 'attivo')
    ]
    
    cursor.executemany('''
    INSERT INTO users (name, email, password, role, status)
    VALUES (?, ?, ?, ?, ?)
    ''', users)
    
    print("Utenti di esempio inseriti nel database.")

# Commit delle modifiche e chiusura della connessione
conn.commit()
conn.close()

print("Database di amministrazione creato con successo.")
