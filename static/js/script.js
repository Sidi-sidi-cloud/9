document.addEventListener('DOMContentLoaded', function() {
    // Elementi del DOM
    const getSuggestionsBtn = document.getElementById('getSuggestionsBtn');
    const saveObservationBtn = document.getElementById('saveObservationBtn');
    const suggestionsContainer = document.getElementById('suggestionsContainer');
    const suggestionsList = document.getElementById('suggestionsList');
    
    // Campi del form
    const classeInput = document.getElementById('classe');
    const allievoInput = document.getElementById('allievo');
    const disciplinaSelect = document.getElementById('disciplina');
    const situazioneInput = document.getElementById('situazione');
    const osservazioneTextarea = document.getElementById('osservazione');
    
    // Campi per il salvataggio
    const dimensioneInput = document.getElementById('dimensione');
    const processoInput = document.getElementById('processo');
    const livelloInput = document.getElementById('livello');
    const idDescrittoreInput = document.getElementById('id_descrittore');
    
    // Gestione click sul pulsante "Ottieni Suggerimenti"
    if (getSuggestionsBtn) {
        getSuggestionsBtn.addEventListener('click', function() {
            // Visualizza indicatore di caricamento
            getSuggestionsBtn.disabled = true;
            getSuggestionsBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Elaborazione in corso...';
            
            // Validazione dei campi obbligatori
            if (!classeInput.value || !allievoInput.value || !disciplinaSelect.value || !osservazioneTextarea.value) {
                alert('Compila tutti i campi obbligatori');
                getSuggestionsBtn.disabled = false;
                getSuggestionsBtn.innerHTML = 'Ottieni Suggerimenti';
                return;
            }
            
            // Richiesta dei suggerimenti
            fetch('/get_suggestions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    osservazione: osservazioneTextarea.value,
                    disciplina: disciplinaSelect.value
                }),
            })
            .then(response => response.json())
            .then(data => {
                // Ripristina il pulsante
                getSuggestionsBtn.disabled = false;
                getSuggestionsBtn.innerHTML = 'Ottieni Suggerimenti';
                
                if (data.error) {
                    alert(data.error);
                    return;
                }
                
                // Visualizza i suggerimenti
                displaySuggestions(data.suggestions);
                suggestionsContainer.style.display = 'block';
                
                // Scroll ai suggerimenti
                suggestionsContainer.scrollIntoView({ behavior: 'smooth' });
            })
            .catch(error => {
                // Ripristina il pulsante
                getSuggestionsBtn.disabled = false;
                getSuggestionsBtn.innerHTML = 'Ottieni Suggerimenti';
                
                console.error('Errore:', error);
                alert('Si è verificato un errore durante la richiesta dei suggerimenti');
            });
        });
    }
    
    // Funzione per visualizzare i suggerimenti
    function displaySuggestions(suggestions) {
        suggestionsList.innerHTML = '';
        
        if (suggestions.length === 0) {
            suggestionsList.innerHTML = '<div class="alert alert-warning">Nessun suggerimento trovato per questa osservazione.</div>';
            return;
        }
        
        suggestions.forEach((suggestion, index) => {
            const similarityPercentage = Math.round(suggestion.similarita * 100);
            
            const suggestionItem = document.createElement('div');
            suggestionItem.className = 'list-group-item suggestion-item';
            suggestionItem.dataset.id = suggestion.id;
            suggestionItem.dataset.dimensione = suggestion.dimensione_riza;
            suggestionItem.dataset.processo = suggestion.processo_specifico_verbo;
            suggestionItem.dataset.livello = suggestion.livello;
            
            suggestionItem.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <div>
                        <span class="badge bg-primary dimension-badge">${suggestion.dimensione_riza}</span>
                        <span class="badge bg-secondary process-badge">${suggestion.processo_specifico_verbo}</span>
                        <span class="badge bg-info level-badge">${suggestion.livello}</span>
                    </div>
                    <span class="badge bg-dark similarity-badge">Pertinenza: ${similarityPercentage}%</span>
                </div>
                <p class="mb-1"><strong>Descrittore:</strong> ${suggestion.testo_descrittore}</p>
                ${suggestion.spiegazione ? `<p class="text-muted small mb-0"><strong>Motivazione:</strong> ${suggestion.spiegazione}</p>` : ''}
            `;
            
            // Gestione click sul suggerimento
            suggestionItem.addEventListener('click', function() {
                // Rimuovi la selezione da tutti i suggerimenti
                document.querySelectorAll('.suggestion-item').forEach(item => {
                    item.classList.remove('selected');
                });
                
                // Seleziona questo suggerimento
                this.classList.add('selected');
                
                // Compila i campi del form di salvataggio
                dimensioneInput.value = suggestion.dimensione_riza;
                processoInput.value = suggestion.processo_specifico_verbo;
                livelloInput.value = suggestion.livello;
                idDescrittoreInput.value = suggestion.id;
            });
            
            suggestionsList.appendChild(suggestionItem);
            
            // Seleziona automaticamente il primo suggerimento
            if (index === 0) {
                suggestionItem.click();
            }
        });
    }
    
    // Gestione click sul pulsante "Salva Osservazione"
    if (saveObservationBtn) {
        saveObservationBtn.addEventListener('click', function() {
            // Visualizza indicatore di caricamento
            saveObservationBtn.disabled = true;
            saveObservationBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Salvataggio...';
            
            // Validazione dei campi obbligatori
            if (!classeInput.value || !allievoInput.value || !disciplinaSelect.value || 
                !osservazioneTextarea.value || !dimensioneInput.value || 
                !processoInput.value || !livelloInput.value) {
                alert('Compila tutti i campi obbligatori');
                saveObservationBtn.disabled = false;
                saveObservationBtn.innerHTML = 'Salva Osservazione';
                return;
            }
            
            // Richiesta di salvataggio
            fetch('/save_observation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    classe: classeInput.value,
                    allievo: allievoInput.value,
                    disciplina: disciplinaSelect.value,
                    situazione: situazioneInput.value,
                    osservazione: osservazioneTextarea.value,
                    dimensione: dimensioneInput.value,
                    processo: processoInput.value,
                    livello: livelloInput.value,
                    id_descrittore: idDescrittoreInput.value
                }),
            })
            .then(response => response.json())
            .then(data => {
                // Ripristina il pulsante
                saveObservationBtn.disabled = false;
                saveObservationBtn.innerHTML = 'Salva Osservazione';
                
                if (data.error) {
                    alert(data.error);
                    return;
                }
                
                alert('Osservazione salvata con successo!');
                
                // Reset del form
                document.getElementById('observationForm').reset();
                suggestionsContainer.style.display = 'none';
                
                // Scroll all'inizio della pagina
                window.scrollTo({ top: 0, behavior: 'smooth' });
            })
            .catch(error => {
                // Ripristina il pulsante
                saveObservationBtn.disabled = false;
                saveObservationBtn.innerHTML = 'Salva Osservazione';
                
                console.error('Errore:', error);
                alert('Si è verificato un errore durante il salvataggio dell\'osservazione');
            });
        });
    }
});
