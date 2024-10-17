document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');

    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = userInput.value.trim();
        if (query) {
            addMessage('user', query);
            fetchResponse(query);
            userInput.value = '';
        }
    });

    function addMessage(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}-message`;
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function fetchResponse(query) {
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                addMessage('bot', `Error: ${data.error}`);
            } else {
                addMessage('bot', formatResponse(data.result));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('bot', 'Sorry, an error occurred while processing your request.');
        });
    }

    function formatResponse(result) {
        if (typeof result === 'object') {
            return JSON.stringify(result, null, 2);
        }
        return result;
    }
});
