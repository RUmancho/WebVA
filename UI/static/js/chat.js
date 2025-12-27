// Чат с помощником
let chatMessages = [];

function loadChatHistory() {
    fetch('/api/chat/history')
        .then(response => response.json())
        .then(data => {
            if (data.messages) {
                chatMessages = data.messages;
                renderMessages();
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки истории:', error);
            // Инициализация с приветственным сообщением
            chatMessages = [{
                role: 'assistant',
                content: 'Привет! Я ваш помощник. Как дела? Чем могу помочь?',
                timestamp: new Date().toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'})
            }];
            renderMessages();
        });
}

function renderMessages() {
    const container = document.getElementById('chatMessages');
    container.innerHTML = '';
    
    chatMessages.forEach(msg => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `mb-3 ${msg.role === 'user' ? 'text-end' : ''}`;
        
        const card = document.createElement('div');
        card.className = `card ${msg.role === 'user' ? 'bg-primary text-white' : 'bg-light'}`;
        card.style.display = 'inline-block';
        card.style.maxWidth = '70%';
        
        const cardBody = document.createElement('div');
        cardBody.className = 'card-body p-2';
        
        const content = document.createElement('div');
        content.textContent = msg.content;
        content.style.whiteSpace = 'pre-wrap';
        
        const timestamp = document.createElement('small');
        timestamp.className = 'text-muted';
        timestamp.textContent = msg.timestamp || '';
        
        cardBody.appendChild(content);
        cardBody.appendChild(document.createElement('br'));
        cardBody.appendChild(timestamp);
        card.appendChild(cardBody);
        messageDiv.appendChild(card);
        container.appendChild(messageDiv);
    });
    
    // Прокрутка вниз
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Добавляем сообщение пользователя сразу
    chatMessages.push({
        role: 'user',
        content: message,
        timestamp: new Date().toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'})
    });
    renderMessages();
    input.value = '';
    
    // Отправляем на сервер
    fetch('/api/chat/send', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({message: message})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            chatMessages.push({
                role: 'assistant',
                content: data.response,
                timestamp: new Date().toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'})
            });
            renderMessages();
        } else {
            alert('Ошибка отправки сообщения');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Ошибка отправки сообщения');
    });
}

function clearChat() {
    if (confirm('Вы уверены, что хотите очистить историю чата?')) {
        fetch('/api/chat/clear', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadChatHistory();
            }
        })
        .catch(error => {
            console.error('Ошибка очистки:', error);
        });
    }
}

// Загружаем историю при загрузке страницы
document.addEventListener('DOMContentLoaded', loadChatHistory);

