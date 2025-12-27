// Звонки
function loadCalls() {
    fetch('/api/dashboard/calls')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('callsContent');
            let html = '';
            
            const userRole = document.body.dataset.userRole || '';
            
            if (userRole === 'Учитель') {
                // Форма создания звонка для учителя
                html += '<h4>📅 Запланировать звонок на встроенной платформе</h4>';
                if (!data.students || data.students.length === 0) {
                    html += '<div class="alert alert-info">У вас нет учеников для планирования звонков.</div>';
                } else {
                    html += '<form id="createCallForm" onsubmit="createCall(event)">';
                    html += '<div class="row mb-3">';
                    html += '<div class="col-md-6">';
                    html += '<label class="form-label">Выберите ученика:</label>';
                    html += '<select class="form-select" id="callStudentSelect" required>';
                    html += '<option value="">-- Выберите ученика --</option>';
                    data.students.forEach(student => {
                        html += `<option value="${student.id}">${student.first_name} ${student.last_name}</option>`;
                    });
                    html += '</select>';
                    html += '</div>';
                    html += '<div class="col-md-3">';
                    html += '<label class="form-label">Дата звонка:</label>';
                    html += '<input type="date" class="form-control" id="callDate" required>';
                    html += '</div>';
                    html += '<div class="col-md-3">';
                    html += '<label class="form-label">Время звонка:</label>';
                    html += '<input type="time" class="form-control" id="callTime" required>';
                    html += '</div>';
                    html += '</div>';
                    html += '<div class="row mb-3">';
                    html += '<div class="col-md-6">';
                    html += '<label class="form-label">Длительность (минуты):</label>';
                    html += '<input type="number" class="form-control" id="callDuration" min="15" max="180" value="60" required>';
                    html += '</div>';
                    html += '<div class="col-md-6">';
                    html += '<label class="form-label">Заметки (необязательно):</label>';
                    html += '<input type="text" class="form-control" id="callNotes" placeholder="Тема урока, дополнительная информация...">';
                    html += '</div>';
                    html += '</div>';
                    html += '<div class="alert alert-info">💡 Звонок будет проходить на встроенной платформе. Запись автоматически сохранится в разделе "Записи уроков" и будет доступна в течение 2 дней.</div>';
                    html += '<button type="submit" class="btn btn-primary">📞 Запланировать звонок</button>';
                    html += '</form>';
                    html += '<hr>';
                }
            }
            
            html += '<h4>📋 Мои звонки</h4>';
            
            if (data.call_groups && data.call_groups.active && data.call_groups.active.length > 0) {
                html += '<h5>🟢 Активные звонки</h5>';
                data.call_groups.active.forEach(call => {
                    html += renderCallCard(call, 'active', userRole);
                });
            }
            
            if (data.call_groups && data.call_groups.scheduled && data.call_groups.scheduled.length > 0) {
                html += '<h5>🕐 Запланированные звонки</h5>';
                data.call_groups.scheduled.forEach(call => {
                    html += renderCallCard(call, 'scheduled', userRole);
                });
            }
            
            if (data.call_groups && data.call_groups.completed && data.call_groups.completed.length > 0) {
                html += '<h5>✅ Завершенные звонки</h5>';
                data.call_groups.completed.forEach(call => {
                    html += renderCallCard(call, 'completed', userRole);
                });
            }
            
            if ((!data.call_groups || !data.call_groups.active || data.call_groups.active.length === 0) && 
                (!data.call_groups || !data.call_groups.scheduled || data.call_groups.scheduled.length === 0) && 
                (!data.call_groups || !data.call_groups.completed || data.call_groups.completed.length === 0)) {
                html += '<div class="alert alert-info">У вас нет запланированных звонков.</div>';
            }
            
            container.innerHTML = html;
        })
        .catch(error => {
            console.error('Ошибка загрузки звонков:', error);
            document.getElementById('callsContent').innerHTML = '<div class="alert alert-danger">Ошибка загрузки данных</div>';
        });
}

function renderCallCard(call, status, userRole) {
    const participantName = userRole === 'Ученик'
        ? `${call.teacher_name} ${call.teacher_surname}`
        : `${call.student_name} ${call.student_surname}`;
    
    let html = `<div class="card mb-3">
        <div class="card-body">
            <div class="row">
                <div class="col-md-8">
                    <h5>Участник: ${participantName}</h5>
                    <p><strong>Время:</strong> ${call.scheduled_time || 'Не указано'}</p>`;
    if (call.actual_start_time) {
        html += `<p><strong>Начат:</strong> ${call.actual_start_time}</p>`;
    }
    if (call.actual_end_time) {
        html += `<p><strong>Завершен:</strong> ${call.actual_end_time}</p>`;
    }
    html += `<p><strong>Длительность:</strong> ${call.duration_minutes} минут</p>`;
    html += `<p><strong>Статус:</strong> ${getStatusEmoji(call.status)} ${call.status}</p>`;
    if (call.notes) {
        html += `<p><strong>Заметки:</strong> ${call.notes}</p>`;
    }
    html += '</div>';
    html += '<div class="col-md-4 text-end">';
    
    if (status === 'scheduled') {
        html += `<button class="btn btn-success" onclick="startCall(${call.id})">🟢 Начать</button>`;
    } else if (status === 'active') {
        html += '<p class="text-danger"><strong>🔴 В эфире</strong></p>';
        html += `<button class="btn btn-danger" onclick="endCall(${call.id})">⏹️ Завершить</button>`;
    } else if (status === 'completed') {
        if (call.recording_path) {
            html += '<p>📹 Записан</p>';
        }
    }
    
    html += '</div></div></div>';
    return html;
}

function getStatusEmoji(status) {
    const emojis = {
        'scheduled': '🕐',
        'active': '🟢',
        'completed': '✅',
        'cancelled': '❌'
    };
    return emojis[status] || '❓';
}

function createCall(event) {
    event.preventDefault();
    const studentId = document.getElementById('callStudentSelect').value;
    const date = document.getElementById('callDate').value;
    const time = document.getElementById('callTime').value;
    const duration = document.getElementById('callDuration').value;
    const notes = document.getElementById('callNotes').value;
    
    const scheduledDatetime = `${date}T${time}`;
    
    fetch('/api/dashboard/calls/create', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            student_id: parseInt(studentId),
            scheduled_datetime: scheduledDatetime,
            duration: parseInt(duration),
            notes: notes
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Звонок запланирован! Уведомление отправлено ученику.');
            loadCalls();
        } else {
            alert('❌ ' + data.message);
        }
    });
}

function startCall(callId) {
    fetch(`/api/dashboard/calls/${callId}/start`, {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('✅ ' + data.message);
                loadCalls();
            } else {
                alert('❌ ' + data.message);
            }
        });
}

function endCall(callId) {
    if (confirm('Завершить звонок?')) {
        fetch(`/api/dashboard/calls/${callId}/end`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                recording_path: `/recordings/call_${callId}_${new Date().toISOString()}.mp4`
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('✅ ' + data.message);
                loadCalls();
            } else {
                alert('❌ ' + data.message);
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('calls') && document.getElementById('calls').classList.contains('active')) {
        loadCalls();
    }
    
    const callsTab = document.querySelector('button[onclick="showTab(\'calls\')"]');
    if (callsTab) {
        callsTab.addEventListener('click', function() {
            setTimeout(loadCalls, 100);
        });
    }
});

