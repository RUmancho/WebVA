// Учителя
function loadTeachers() {
    fetch('/api/dashboard/teachers')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('teachersContent');
            let html = '';
            
            // Мои учителя (для ученика) или мои ученики (для учителя)
            if (data.my_teachers && data.my_teachers.length > 0) {
                html += '<h4>👨‍🏫 Мои учителя</h4>';
                html += `<p>У вас ${data.my_teachers.length} учителей:</p>`;
                data.my_teachers.forEach(teacher => {
                    html += `<div class="card mb-2">
                        <div class="card-body">
                            <h5>${teacher.first_name} ${teacher.last_name}</h5>
                            <p><strong>Предметы:</strong> ${teacher.subjects || 'Не указаны'}</p>
                            <p><strong>Школа:</strong> ${teacher.school || 'Не указана'}</p>
                            <p><strong>Город:</strong> ${teacher.city || 'Не указан'}</p>
                            <span class="badge bg-success">✅ Связан</span>
                            <span class="badge ${teacher.is_online ? 'bg-success' : 'bg-danger'}">
                                ${teacher.is_online ? '🟢 В сети' : '🔴 Не в сети'}
                            </span>
                        </div>
                    </div>`;
                });
                html += '<hr>';
            }
            
            if (data.students_tree && Object.keys(data.students_tree).length > 0) {
                html += '<h4>🌳 Мои ученики (древовидная структура)</h4>';
                html += '<div class="alert alert-info">💡 Структура: Город → Школа → Класс → Ученики. 🟢 - в сети, 🔴 - не в сети</div>';
                
                for (const [city, schools] of Object.entries(data.students_tree)) {
                    let totalStudents = 0;
                    for (const classes of Object.values(schools)) {
                        for (const students of Object.values(classes)) {
                            totalStudents += students.length;
                        }
                    }
                    
                    const cityId = city.replace(/[^a-zA-Z0-9]/g, '');
                    html += `<div class="accordion mb-2">
                        <div class="accordion-item">
                            <h2 class="accordion-header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#city-${cityId}">
                                    🏙️ ${city} (${totalStudents} учеников)
                                </button>
                            </h2>
                            <div id="city-${cityId}" class="accordion-collapse collapse">
                                <div class="accordion-body">`;
                    
                    for (const [school, classes] of Object.entries(schools)) {
                        html += `<h5>🏫 ${school}</h5>`;
                        for (const [classNum, students] of Object.entries(classes)) {
                            html += `<h6>📚 Класс ${classNum} (${students.length} учеников)</h6>`;
                            students.forEach(student => {
                                const statusIcon = student.is_online ? '🟢' : '🔴';
                                html += `<p>${statusIcon} ${student.first_name} ${student.last_name} (${student.email})</p>`;
                            });
                            html += '<hr>';
                        }
                    }
                    
                    html += `</div></div></div>`;
                }
                
                html += '<button class="btn btn-primary" onclick="autoMatch()">Запустить автоматическое прикрепление учеников</button>';
                html += '<hr>';
            }
            
            html += '<h4>🔍 Все учителя в системе</h4>';
            
            if (data.subjects && data.subjects.length > 0) {
                html += '<div class="mb-3"><label class="form-label">Фильтр по предмету:</label>';
                html += '<select class="form-select" id="subjectFilter" onchange="filterTeachers()">';
                html += '<option value="Все предметы">Все предметы</option>';
                data.subjects.forEach(subject => {
                    html += `<option value="${subject}">${subject}</option>`;
                });
                html += '</select></div>';
            }
            
            if (data.teachers && data.teachers.length > 0) {
                html += `<p>Найдено учителей: ${data.teachers.length}</p>`;
                data.teachers.forEach(teacher => {
                    html += `<div class="card mb-2">
                        <div class="card-body">
                            <h5>${teacher.first_name} ${teacher.last_name}</h5>
                            <div class="row">
                                <div class="col-md-6">
                                    <p><strong>Предметы:</strong> ${teacher.subjects || 'Не указаны'}</p>
                                    <p><strong>Город:</strong> ${teacher.city || 'Не указан'}</p>
                                </div>
                                <div class="col-md-6">
                                    <p><strong>Школа:</strong> ${teacher.school || 'Не указана'}</p>
                                </div>
                            </div>
                        </div>
                    </div>`;
                });
            } else {
                html += '<div class="alert alert-info">В системе пока нет зарегистрированных учителей.</div>';
            }
            
            container.innerHTML = html;
        })
        .catch(error => {
            console.error('Ошибка загрузки учителей:', error);
            document.getElementById('teachersContent').innerHTML = '<div class="alert alert-danger">Ошибка загрузки данных</div>';
        });
}

function filterTeachers() {
    const subject = document.getElementById('subjectFilter').value;
    const url = subject === 'Все предметы' ? '/api/dashboard/teachers' : `/api/dashboard/teachers?subject=${encodeURIComponent(subject)}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Обновляем только список всех учителей
            const container = document.getElementById('teachersContent');
            const existingContent = container.innerHTML;
            const startIndex = existingContent.indexOf('<h4>🔍 Все учителя в системе</h4>');
            const newContent = existingContent.substring(0, startIndex);
            
            let html = newContent + '<h4>🔍 Все учителя в системе</h4>';
            if (data.subjects && data.subjects.length > 0) {
                html += '<div class="mb-3"><label class="form-label">Фильтр по предмету:</label>';
                html += '<select class="form-select" id="subjectFilter" onchange="filterTeachers()">';
                html += '<option value="Все предметы">Все предметы</option>';
                data.subjects.forEach(subject => {
                    html += `<option value="${subject}" ${subject === document.getElementById('subjectFilter').value ? 'selected' : ''}>${subject}</option>`;
                });
                html += '</select></div>';
            }
            
            if (data.teachers && data.teachers.length > 0) {
                html += `<p>Найдено учителей: ${data.teachers.length}</p>`;
                data.teachers.forEach(teacher => {
                    html += `<div class="card mb-2">
                        <div class="card-body">
                            <h5>${teacher.first_name} ${teacher.last_name}</h5>
                            <div class="row">
                                <div class="col-md-6">
                                    <p><strong>Предметы:</strong> ${teacher.subjects || 'Не указаны'}</p>
                                    <p><strong>Город:</strong> ${teacher.city || 'Не указан'}</p>
                                </div>
                                <div class="col-md-6">
                                    <p><strong>Школа:</strong> ${teacher.school || 'Не указана'}</p>
                                </div>
                            </div>
                        </div>
                    </div>`;
                });
            } else {
                html += '<div class="alert alert-info">В системе пока нет зарегистрированных учителей.</div>';
            }
            
            container.innerHTML = html;
        });
}

function autoMatch() {
    if (confirm('Запустить автоматическое прикрепление учеников?')) {
        fetch('/api/dashboard/auto-match', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ ' + data.message);
                    loadTeachers();
                } else {
                    alert('❌ ' + data.message);
                }
            });
    }
}

// Загружаем при открытии вкладки
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('teachers') && document.getElementById('teachers').classList.contains('active')) {
        loadTeachers();
    }
    
    // Загружаем при переключении на вкладку
    const teachersTab = document.querySelector('button[onclick="showTab(\'teachers\')"]');
    if (teachersTab) {
        teachersTab.addEventListener('click', function() {
            setTimeout(loadTeachers, 100);
        });
    }
});

