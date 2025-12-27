// Заявки
function loadRequests() {
    fetch('/api/dashboard/requests')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('requestsContent');
            let html = '';
            
            const userRole = document.body.dataset.userRole || '';
            
            if (userRole === 'Ученик') {
                // Для ученика - входящие заявки
                html += '<h4>📨 Входящие заявки от учителей</h4>';
                if (!data.requests || data.requests.length === 0) {
                    html += '<div class="alert alert-info">У вас нет новых заявок от учителей.</div>';
                } else {
                    html += `<p>У вас ${data.requests.length} новых заявок:</p>`;
                    data.requests.forEach(req => {
                        html += `<div class="card mb-3">
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-8">
                                        <h5>Учитель: ${req.first_name} ${req.last_name}</h5>
                                        <p><strong>Предметы:</strong> ${req.subjects || 'Не указаны'}</p>
                                        <p><strong>Школа:</strong> ${req.school || 'Не указана'}</p>
                                        ${req.message ? `<p><strong>Сообщение:</strong> ${req.message}</p>` : ''}
                                        <p><strong>Дата:</strong> ${req.created_at}</p>
                                    </div>
                                    <div class="col-md-4 text-end">
                                        <button class="btn btn-success mb-2" onclick="acceptRequest(${req.id})">✅ Принять</button><br>
                                        <button class="btn btn-danger" onclick="rejectRequest(${req.id})">❌ Отклонить</button>
                                    </div>
                                </div>
                            </div>
                        </div>`;
                    });
                }
            } else if (userRole === 'Учитель') {
                // Для учителя - отправка заявок
                html += '<h4>📤 Отправка заявок ученикам</h4>';
                if (!data.all_students || data.all_students.length === 0) {
                    html += '<div class="alert alert-info">В системе нет зарегистрированных учеников.</div>';
                } else {
                    html += '<form id="sendRequestForm" onsubmit="sendRequest(event)">';
                    html += '<div class="mb-3">';
                    html += '<label class="form-label">Выберите ученика:</label>';
                    html += '<select class="form-select" id="studentSelect" required>';
                    html += '<option value="">-- Выберите ученика --</option>';
                    data.all_students.forEach(student => {
                        html += `<option value="${student.id}">${student.first_name} ${student.last_name} (${student.email})</option>`;
                    });
                    html += '</select>';
                    html += '</div>';
                    html += '<div class="mb-3">';
                    html += '<label class="form-label">Сообщение (необязательно):</label>';
                    html += '<textarea class="form-control" id="requestMessage" rows="3" placeholder="Напишите короткое сообщение ученику..."></textarea>';
                    html += '</div>';
                    html += '<button type="submit" class="btn btn-primary">📤 Отправить заявку</button>';
                    html += '</form>';
                    html += '<hr>';
                    html += '<h4>📋 Мои отправленные заявки</h4>';
                    if (!data.sent_requests || data.sent_requests.length === 0) {
                        html += '<div class="alert alert-info">Вы не отправляли заявок ученикам.</div>';
                    } else {
                        data.sent_requests.forEach(req => {
                            html += `<div class="card mb-2">
                                <div class="card-body">
                                    <p><strong>Ученик:</strong> ${req.student_name} ${req.student_surname}</p>
                                    <p><strong>Статус:</strong> ${req.status}</p>
                                    <p><strong>Дата отправки:</strong> ${req.created_at}</p>
                                    ${req.message ? `<p><strong>Сообщение:</strong> ${req.message}</p>` : ''}
                                </div>
                            </div>`;
                        });
                    }
                }
            }
            
            container.innerHTML = html;
        })
        .catch(error => {
            console.error('Ошибка загрузки заявок:', error);
            document.getElementById('requestsContent').innerHTML = '<div class="alert alert-danger">Ошибка загрузки данных</div>';
        });
}

function acceptRequest(requestId) {
    if (confirm('Принять заявку от учителя?')) {
        fetch(`/api/dashboard/requests/${requestId}/accept`, {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ ' + data.message);
                    loadRequests();
                } else {
                    alert('❌ ' + data.message);
                }
            });
    }
}

function rejectRequest(requestId) {
    if (confirm('Отклонить заявку от учителя?')) {
        fetch(`/api/dashboard/requests/${requestId}/reject`, {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ ' + data.message);
                    loadRequests();
                } else {
                    alert('❌ ' + data.message);
                }
            });
    }
}

function sendRequest(event) {
    event.preventDefault();
    const studentId = document.getElementById('studentSelect').value;
    const message = document.getElementById('requestMessage').value;
    
    fetch('/api/dashboard/requests/create', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({student_id: parseInt(studentId), message: message})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ ' + data.message);
            loadRequests();
        } else {
            alert('❌ ' + data.message);
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('requests') && document.getElementById('requests').classList.contains('active')) {
        loadRequests();
    }
    
    const requestsTab = document.querySelector('button[onclick="showTab(\'requests\')"]');
    if (requestsTab) {
        requestsTab.addEventListener('click', function() {
            setTimeout(loadRequests, 100);
        });
    }
});

