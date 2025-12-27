// Личный чат
let selectedUserId = null;
let personalChatMessages = [];

function loadPersonalChatUsers() {
    fetch('/api/dashboard/personal-chat/users')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('personalChatContent');
            let html = '';
            
            if (!data.users || data.users.length === 0) {
                html += '<div class="alert alert-info">У вас пока нет пользователей для чата. Прикрепите учителей или учеников!</div>';
                container.innerHTML = html;
                return;
            }
            
            html += '<div class="row">';
            html += '<div class="col-md-3">';
            html += '<label class="form-label">Выберите собеседника:</label>';
            html += '<select class="form-select" id="userSelector" onchange="selectChatUser()">';
            html += '<option value="">-- Выберите --</option>';
            data.users.forEach(user => {
                const statusIcon = user.is_online ? '🟢' : '🔴';
                html += `<option value="${user.id}">${statusIcon} ${user.name} (${user.role})</option>`;
            });
            html += '</select>';
            html += '</div>';
            html += '<div class="col-md-9">';
            html += '<div id="chatArea"></div>';
            html += '</div>';
            html += '</div>';
            
            container.innerHTML = html;
            
            // Если есть выбранный пользователь, загружаем его чат
            if (selectedUserId) {
                loadPersonalChatMessages(selectedUserId);
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки пользователей:', error);
            document.getElementById('personalChatContent').innerHTML = '<div class="alert alert-danger">Ошибка загрузки данных</div>';
        });
}

function selectChatUser() {
    const selector = document.getElementById('userSelector');
    selectedUserId = selector.value;
    if (selectedUserId) {
        loadPersonalChatMessages(selectedUserId);
    } else {
        document.getElementById('chatArea').innerHTML = '';
    }
}

function loadPersonalChatMessages(userId) {
    fetch(`/api/dashboard/personal-chat/${userId}/messages`)
        .then(response => response.json())
        .then(data => {
            personalChatMessages = data.messages || [];
            renderPersonalChatMessages(userId);
        })
        .catch(error => {
            console.error('Ошибка загрузки сообщений:', error);
        });
}

function renderPersonalChatMessages(userId) {
    const chatArea = document.getElementById('chatArea');
    const userSelector = document.getElementById('userSelector');
    const selectedOption = userSelector.options[userSelector.selectedIndex];
    const userName = selectedOption ? selectedOption.text.replace(/[🟢🔴]/g, '').trim() : 'Пользователь';
    
    // Получаем ID текущего пользователя из data-атрибута
    const currentUserId = document.body.dataset.userId || 0;
    
    let html = `<h5>Чат с: ${userName}</h5>`;
    html += '<div class="border rounded p-3 mb-3" style="height: 400px; overflow-y: auto; background: var(--bg-sidebar);">';
    
    if (personalChatMessages.length === 0) {
        html += '<div class="alert alert-info">Начните разговор!</div>';
    } else {
        personalChatMessages.forEach(message => {
            const isSender = message.sender_id == currentUserId;
            html += `<div class="mb-3 ${isSender ? 'text-end' : ''}">`;
            html += `<div class="card ${isSender ? 'bg-primary text-white' : 'bg-light'}" style="display: inline-block; max-width: 70%;">`;
            html += '<div class="card-body p-2">';
            html += `<strong>${isSender ? 'Вы' : userName}</strong> (${message.created_at})<br>`;
            html += `<div>${message.message_text}</div>`;
            html += '</div></div></div>';
        });
    }
    
    html += '</div>';
    html += `<form onsubmit="sendPersonalMessage(event, ${userId})">`;
    html += '<div class="input-group">';
    html += '<input type="text" class="form-control" id="personalMessageInput" placeholder="Введите сообщение..." required>';
    html += '<button class="btn btn-primary" type="submit">📤 Отправить</button>';
    html += '</div>';
    html += '</form>';
    
    chatArea.innerHTML = html;
    
    // Прокрутка вниз
    const chatContainer = chatArea.querySelector('.border.rounded');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

function sendPersonalMessage(event, userId) {
    event.preventDefault();
    const input = document.getElementById('personalMessageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    fetch(`/api/dashboard/personal-chat/${userId}/messages`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: message})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            input.value = '';
            loadPersonalChatMessages(userId);
        } else {
            alert('Ошибка отправки: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Ошибка отправки:', error);
        alert('Ошибка отправки сообщения');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('personal_chat') && document.getElementById('personal_chat').classList.contains('active')) {
        loadPersonalChatUsers();
    }
    
    const personalChatTab = document.querySelector('button[onclick="showTab(\'personal_chat\')"]');
    if (personalChatTab) {
        personalChatTab.addEventListener('click', function() {
            setTimeout(loadPersonalChatUsers, 100);
        });
    }
});

