// Задания
let currentAssignmentId = null;
let currentTest = null;
let testStartTime = null;
let testTimerInterval = null;
let userAnswers = {};

// Инициализация при загрузке вкладки
function initAssignments() {
    loadAssignments();
}

// Загрузка заданий
async function loadAssignments() {
    try {
        const response = await fetch('/api/assignments');
        const data = await response.json();
        
        if (data.error) {
            showAssignmentsError(data.error);
            return;
        }
        
        renderAssignments(data);
    } catch (error) {
        console.error('Ошибка загрузки заданий:', error);
        showAssignmentsError('Не удалось загрузить задания');
    }
}

// Отображение заданий
function renderAssignments(data) {
    const container = document.getElementById('assignmentsContent');
    const actions = document.getElementById('assignmentsActions');
    
    if (data.role === 'teacher') {
        // Интерфейс учителя
        actions.innerHTML = `
            <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createAssignmentModal">
                ➕ Создать задание
            </button>
        `;
        
        if (!data.assignments || data.assignments.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <h4>📋 У вас пока нет заданий</h4>
                    <p class="text-muted">Создайте первое задание для ваших учеников</p>
                </div>
            `;
            return;
        }
        
        let html = '<div class="table-responsive"><table class="table table-hover">';
        html += '<thead><tr><th>Название</th><th>Предмет</th><th>Класс</th><th>Ответов</th><th>Ср. балл</th><th>Статус</th><th>Действия</th></tr></thead><tbody>';
        
        for (const a of data.assignments) {
            const statusBadge = a.is_active 
                ? '<span class="badge bg-success">Активно</span>' 
                : '<span class="badge bg-secondary">Неактивно</span>';
            
            html += `
                <tr>
                    <td><strong>${a.title}</strong><br><small class="text-muted">${a.topic || ''}</small></td>
                    <td>${a.subject}</td>
                    <td>${a.target_class || 'Все'}</td>
                    <td>${a.submissions_count}</td>
                    <td>${a.avg_score.toFixed(1)}%</td>
                    <td>${statusBadge}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="showAssignmentStats(${a.id})">📊</button>
                        <button class="btn btn-sm btn-outline-warning" onclick="toggleAssignment(${a.id})">${a.is_active ? 'Пауза' : 'Запуск'}</button>
                    </td>
                </tr>
            `;
        }
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
        
    } else {
        // Интерфейс ученика
        actions.innerHTML = '';
        
        if (!data.assignments || data.assignments.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <h4>📭 Нет доступных заданий</h4>
                    <p class="text-muted">Когда учитель назначит вам задание, оно появится здесь</p>
                </div>
            `;
            return;
        }
        
        let html = '<div class="row">';
        
        for (const a of data.assignments) {
            const difficultyBadge = {
                'Лёгкий': 'bg-success',
                'Средний': 'bg-warning',
                'Хардкор': 'bg-danger'
            }[a.difficulty] || 'bg-secondary';
            
            const statusHtml = a.is_submitted
                ? `<div class="alert alert-success mb-0"><strong>✅ Выполнено!</strong><br>Результат: ${a.submission.percentage}%</div>`
                : `<button class="btn btn-primary w-100" onclick="startTest(${a.id})">Выполнить</button>`;
            
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card h-100">
                        <div class="card-header d-flex justify-content-between">
                            <span>${a.subject}</span>
                            <span class="badge ${difficultyBadge}">${a.difficulty}</span>
                        </div>
                        <div class="card-body">
                            <h5 class="card-title">${a.title}</h5>
                            <p class="card-text text-muted">${a.description || ''}</p>
                            <p class="mb-1"><small>👨‍🏫 ${a.teacher_name}</small></p>
                            ${a.deadline ? `<p class="mb-1"><small>⏰ До: ${a.deadline}</small></p>` : ''}
                        </div>
                        <div class="card-footer">
                            ${statusHtml}
                        </div>
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        container.innerHTML = html;
    }
}

// Показать ошибку
function showAssignmentsError(message) {
    document.getElementById('assignmentsContent').innerHTML = `
        <div class="alert alert-danger">${message}</div>
    `;
}

// Переключение типа генерации
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input[name="generationType"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const manualSection = document.getElementById('manualQuestionsSection');
            const countSection = document.getElementById('questionCountSection');
            
            if (this.value === 'manual') {
                manualSection.style.display = 'block';
                countSection.style.display = 'none';
            } else {
                manualSection.style.display = 'none';
                countSection.style.display = 'block';
            }
        });
    });
});

// Предпросмотр теста
async function generateTestPreview() {
    const subject = document.getElementById('assignmentSubject').value;
    const topic = document.getElementById('assignmentTopic').value;
    const difficulty = document.getElementById('assignmentDifficulty').value;
    const genType = document.querySelector('input[name="generationType"]:checked').value;
    const count = document.getElementById('questionCount').value;
    
    if (!subject) {
        alert('Выберите предмет');
        return;
    }
    
    const preview = document.getElementById('testPreview');
    const content = document.getElementById('testPreviewContent');
    preview.style.display = 'block';
    content.innerHTML = '<div class="text-center"><div class="spinner-border text-primary"></div><p>Генерация вопросов...</p></div>';
    
    try {
        const response = await fetch('/api/assignments/generate-test', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                subject, topic, difficulty, 
                generation_type: genType, 
                count: parseInt(count)
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            content.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            return;
        }
        
        currentTest = data.test;
        let html = '';
        
        for (let i = 0; i < data.test.questions.length; i++) {
            const q = data.test.questions[i];
            html += `
                <div class="mb-3 p-3 border rounded">
                    <strong>${i + 1}. ${q.question}</strong>
                    <ul class="list-unstyled mt-2">
                        ${q.options.map((opt, j) => `
                            <li class="${opt === q.correct_answer ? 'text-success fw-bold' : ''}">
                                ${String.fromCharCode(65 + j)}) ${opt}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }
        
        content.innerHTML = html;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Ошибка: ${error.message}</div>`;
    }
}

// Создание задания
async function createAssignment() {
    const title = document.getElementById('assignmentTitle').value;
    const subject = document.getElementById('assignmentSubject').value;
    const topic = document.getElementById('assignmentTopic').value;
    const difficulty = document.getElementById('assignmentDifficulty').value;
    const description = document.getElementById('assignmentDescription').value;
    const targetCity = document.getElementById('targetCity').value;
    const targetSchool = document.getElementById('targetSchool').value;
    const targetClass = document.getElementById('targetClass').value;
    const deadline = document.getElementById('assignmentDeadline').value;
    const genType = document.querySelector('input[name="generationType"]:checked').value;
    
    if (!title || !subject) {
        alert('Заполните обязательные поля');
        return;
    }
    
    let questions = currentTest?.questions;
    
    if (genType === 'manual') {
        try {
            questions = JSON.parse(document.getElementById('manualQuestions').value);
        } catch (e) {
            alert('Неверный формат JSON вопросов');
            return;
        }
    }
    
    if (!questions || questions.length === 0) {
        // Генерируем тест если его нет
        await generateTestPreview();
        questions = currentTest?.questions;
        
        if (!questions) {
            alert('Сначала сгенерируйте или введите вопросы');
            return;
        }
    }
    
    try {
        const response = await fetch('/api/assignments/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                title, subject, topic, difficulty, description,
                target_city: targetCity,
                target_school: targetSchool,
                target_class: targetClass,
                deadline: deadline || null,
                questions
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ Задание успешно создано!');
            bootstrap.Modal.getInstance(document.getElementById('createAssignmentModal')).hide();
            document.getElementById('createAssignmentForm').reset();
            currentTest = null;
            document.getElementById('testPreview').style.display = 'none';
            loadAssignments();
        } else {
            alert('Ошибка: ' + data.error);
        }
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
}

// Показать статистику задания
async function showAssignmentStats(assignmentId) {
    const modal = new bootstrap.Modal(document.getElementById('assignmentStatsModal'));
    modal.show();
    
    const content = document.getElementById('assignmentStatsContent');
    content.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';
    
    try {
        const response = await fetch(`/api/assignments/${assignmentId}/statistics`);
        const data = await response.json();
        
        if (data.error) {
            content.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            return;
        }
        
        let html = `
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3>${data.total_submissions}</h3>
                            <small class="text-muted">Всего ответов</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3>${data.avg_percentage}%</h3>
                            <small class="text-muted">Средний балл</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3>${data.max_score}%</h3>
                            <small class="text-muted">Лучший</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3>${Math.round(data.avg_time / 60)} мин</h3>
                            <small class="text-muted">Ср. время</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <h5>📋 Результаты учеников</h5>
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr><th>Ученик</th><th>Класс</th><th>Баллы</th><th>%</th><th>Время</th><th>Дата</th></tr>
                    </thead>
                    <tbody>
        `;
        
        for (const s of data.submissions) {
            const percentClass = s.percentage >= 70 ? 'text-success' : (s.percentage >= 50 ? 'text-warning' : 'text-danger');
            html += `
                <tr>
                    <td>${s.student_name}</td>
                    <td>${s.student_class}</td>
                    <td>${s.score}/${s.max_score}</td>
                    <td class="${percentClass} fw-bold">${s.percentage}%</td>
                    <td>${Math.round(s.time_spent / 60)} мин</td>
                    <td>${s.submitted_at}</td>
                </tr>
            `;
        }
        
        html += '</tbody></table></div>';
        content.innerHTML = html;
        
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Ошибка: ${error.message}</div>`;
    }
}

// Переключить активность задания
async function toggleAssignment(assignmentId) {
    try {
        const response = await fetch(`/api/assignments/${assignmentId}/toggle`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            loadAssignments();
        } else {
            alert('Ошибка: ' + data.error);
        }
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
}

// Начать тест (для ученика)
async function startTest(assignmentId) {
    currentAssignmentId = assignmentId;
    userAnswers = {};
    testStartTime = Date.now();
    
    const modal = new bootstrap.Modal(document.getElementById('takeTestModal'));
    modal.show();
    
    const content = document.getElementById('takeTestContent');
    content.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';
    
    // Запускаем таймер
    testTimerInterval = setInterval(updateTimer, 1000);
    
    try {
        const response = await fetch(`/api/assignments/${assignmentId}`);
        const data = await response.json();
        
        if (data.error) {
            content.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            return;
        }
        
        document.getElementById('takeTestTitle').textContent = `📝 ${data.title}`;
        
        const questions = JSON.parse(data.questions_json);
        let html = '';
        
        for (let i = 0; i < questions.length; i++) {
            const q = questions[i];
            html += `
                <div class="mb-4 p-3 border rounded question-block" data-index="${i}">
                    <h6><strong>${i + 1}. ${q.question}</strong></h6>
                    <div class="mt-2">
                        ${q.options.map((opt, j) => `
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="q${i}" id="q${i}o${j}" 
                                    value="${opt}" onchange="selectAnswer(${i}, '${opt.replace(/'/g, "\\'")}')">
                                <label class="form-check-label" for="q${i}o${j}">
                                    ${String.fromCharCode(65 + j)}) ${opt}
                                </label>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        content.innerHTML = html;
        
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Ошибка: ${error.message}</div>`;
    }
}

// Обновить таймер
function updateTimer() {
    const elapsed = Math.floor((Date.now() - testStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    document.getElementById('testTimer').textContent = 
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

// Выбрать ответ
function selectAnswer(questionIndex, answer) {
    userAnswers[questionIndex] = answer;
    
    // Проверяем, все ли вопросы отвечены
    const totalQuestions = document.querySelectorAll('.question-block').length;
    const answeredCount = Object.keys(userAnswers).length;
    
    document.getElementById('submitTestBtn').disabled = answeredCount < totalQuestions;
}

// Отправить тест
async function submitTest() {
    clearInterval(testTimerInterval);
    const timeSpent = Math.floor((Date.now() - testStartTime) / 1000);
    
    try {
        const response = await fetch(`/api/assignments/${currentAssignmentId}/submit`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                answers: userAnswers,
                time_spent: timeSpent
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const content = document.getElementById('takeTestContent');
            content.innerHTML = `
                <div class="text-center py-4">
                    <h2 class="${data.percentage >= 70 ? 'text-success' : (data.percentage >= 50 ? 'text-warning' : 'text-danger')}">
                        ${data.percentage}%
                    </h2>
                    <p class="lead">Правильных ответов: ${data.score} из ${data.max_score}</p>
                    <p>Время выполнения: ${Math.round(timeSpent / 60)} мин ${timeSpent % 60} сек</p>
                    <hr>
                    <button class="btn btn-primary" onclick="closeTestModal()">Закрыть</button>
                </div>
            `;
            document.getElementById('submitTestBtn').style.display = 'none';
            document.querySelector('#takeTestModal .btn-danger').style.display = 'none';
        } else {
            alert('Ошибка: ' + data.error);
        }
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
}

// Отменить тест
function cancelTest() {
    if (confirm('Вы уверены, что хотите отменить тест? Ваши ответы не будут сохранены.')) {
        clearInterval(testTimerInterval);
        bootstrap.Modal.getInstance(document.getElementById('takeTestModal')).hide();
    }
}

// Закрыть модальное окно теста
function closeTestModal() {
    bootstrap.Modal.getInstance(document.getElementById('takeTestModal')).hide();
    document.getElementById('submitTestBtn').style.display = 'block';
    document.querySelector('#takeTestModal .btn-danger').style.display = 'block';
    document.getElementById('submitTestBtn').disabled = true;
    loadAssignments();
}

// Инициализация при показе вкладки
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('assignmentsContent')) {
        initAssignments();
    }
});

