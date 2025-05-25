# Guida al Deployment su Render per EduTools

Questa guida fornisce istruzioni dettagliate per garantire il corretto funzionamento dell'applicazione EduTools su Render.

## Problemi comuni e soluzioni

### 1. Variabili d'ambiente

Le variabili d'ambiente sono fondamentali per il funzionamento dell'applicazione, specialmente per l'integrazione con OpenAI. Assicurati di configurare correttamente le seguenti variabili nella dashboard di Render:

- `OPENAI_API_KEY`: La tua chiave API di OpenAI
- `SECRET_KEY`: Una chiave segreta per Flask (può essere qualsiasi stringa complessa)
- `ENABLE_AI`: Impostato su "True" per abilitare le funzionalità AI
- `AI_MODEL`: Impostato su "gpt-3.5-turbo" (o altro modello supportato)
- `MAX_TOKENS`: Impostato su "1000" (o altro valore numerico)
- `TEMPERATURE`: Impostato su "0.3" (o altro valore tra 0 e 1)

### 2. Inizializzazione del database

L'applicazione è configurata per inizializzare automaticamente i database necessari al primo avvio. Tuttavia, in alcuni casi potrebbero verificarsi problemi di permessi. Se riscontri errori relativi ai database:

- Verifica che il servizio su Render abbia i permessi di scrittura nella directory `/data`
- Se necessario, puoi forzare la reinizializzazione dei database eliminando i file `.db` esistenti tramite la console di Render

### 3. Compatibilità delle dipendenze

L'applicazione utilizza librerie come `scikit-learn`, `numpy` e `openai` che potrebbero richiedere tempo per l'installazione su Render. Assicurati che:

- Il build command includa l'installazione delle dipendenze: `pip install -r requirements.txt`
- Il timeout per il build sia sufficientemente lungo (almeno 15 minuti)

## Configurazione su Render

### Impostazioni consigliate

1. **Tipo di servizio**: Web Service
2. **Runtime**: Python 3
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `gunicorn app:app`
5. **Piano**: Free (sufficiente per test e demo)

### Variabili d'ambiente

Configura le seguenti variabili d'ambiente nella dashboard di Render:

```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
SECRET_KEY=chiave_segreta_edutools_2025
ENABLE_AI=True
AI_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000
TEMPERATURE=0.3
```

## Verifica del deployment

Dopo il deployment, verifica che:

1. La pagina di login sia accessibile
2. Sia possibile accedere con le credenziali predefinite (admin@edutools.it / admin123)
3. La dashboard e le funzionalità principali siano operative
4. L'integrazione con OpenAI funzioni correttamente

## Risoluzione problemi

### Errore di login

Se riscontri errori durante il login:
- Verifica che il database `admin.db` sia stato creato correttamente
- Controlla i log di Render per errori specifici
- Se necessario, accedi alla console di Render ed esegui manualmente lo script `data/create_admin_db.py`

### Errore di integrazione OpenAI

Se l'integrazione con OpenAI non funziona:
- Verifica che la variabile `OPENAI_API_KEY` sia configurata correttamente
- Controlla che la chiave API sia valida e attiva
- Verifica nei log se ci sono errori specifici relativi all'API

### Errori di database

Se riscontri errori relativi ai database:
- Verifica che le directory necessarie esistano e siano scrivibili
- Controlla i log per errori specifici di SQLite
- Se necessario, reinizializza i database tramite la console di Render

## Contatti e supporto

Per ulteriore assistenza, contatta il team di sviluppo di EduTools.
