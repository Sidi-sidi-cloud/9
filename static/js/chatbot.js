document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const suggestions = document.getElementById('suggestions');

    // Gestione dell'invio del messaggio
    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;

        // Aggiungi il messaggio dell'utente alla chat
        addUserMessage(message);
        
        // Pulisci l'input
        userInput.value = '';
        
        // Mostra l'indicatore di digitazione
        showTypingIndicator();
        
        // Invia la richiesta al server
        fetch('/chatbot_query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: message }),
        })
        .then(response => response.json())
        .then(data => {
            // Rimuovi l'indicatore di digitazione
            removeTypingIndicator();
            
            // Aggiungi la risposta del bot
            addBotMessage(data.response);
            
            // Aggiorna i suggerimenti se presenti
            if (data.suggestions && data.suggestions.length > 0) {
                updateSuggestions(data.suggestions);
            }
        })
        .catch(error => {
            console.error('Errore:', error);
            removeTypingIndicator();
            addBotMessage('Mi dispiace, si è verificato un errore. Riprova più tardi.');
        });
    }

    // Aggiungi un messaggio dell'utente alla chat
    function addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `<p>${escapeHtml(message)}</p>`;
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    // Aggiungi un messaggio del bot alla chat
    function addBotMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.innerHTML = `<p>${formatMessage(message)}</p>`;
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    // Mostra l'indicatore di digitazione
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }

    // Rimuovi l'indicatore di digitazione
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // Aggiorna i suggerimenti
    function updateSuggestions(suggestionList) {
        suggestions.innerHTML = '';
        suggestionList.forEach(suggestion => {
            const chip = document.createElement('div');
            chip.className = 'suggestion-chip';
            chip.textContent = suggestion;
            chip.onclick = function() {
                selectSuggestion(suggestion);
            };
            suggestions.appendChild(chip);
        });
    }

    // Seleziona un suggerimento
    window.selectSuggestion = function(suggestion) {
        userInput.value = suggestion;
        userInput.focus();
    };

    // Formatta il messaggio (converte markdown semplice)
    function formatMessage(message) {
        // Converti gli asterischi in grassetto
        message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Converti gli underscore in corsivo
        message = message.replace(/\_(.*?)\_/g, '<em>$1</em>');
        
        // Converti le newline in <br>
        message = message.replace(/\n/g, '<br>');
        
        // Converti gli elenchi puntati
        message = message.replace(/- (.*?)(?:\n|$)/g, '<li>$1</li>');
        message = message.replace(/<li>(.*?)<\/li>(?:<li>.*?<\/li>)+/g, '<ul>$&</ul>');
        
        return message;
    }

    // Escape HTML per prevenire XSS
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Scroll alla fine della chat
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Event listener per il pulsante di invio
    sendButton.addEventListener('click', sendMessage);

    // Event listener per il tasto Invio
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Metti il focus sull'input all'avvio
    userInput.focus();
});
