// Записи уроков
function loadLessons() {
    fetch('/api/dashboard/lessons')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('lessonsContent');
            let html = '';
            
            const userRole = document.body.dataset.userRole || '';
            
            if (userRole === 'Учитель') {
                // Форма создания записи урока для учителя
                html += '<h4>📝 Создать запись урока</h4>';
                if (!data.students || data.students.length === 0) {
                    html += '<div class="alert alert-info">У вас нет учеников для создания записей уроков.</div>';
                } else {
                    html += '<form id="createLessonForm" onsubmit="createLesson(event)">';
                    html += '<div class="row mb-3">';
                    html += '<div class="col-md-6">';
                    html += '<label class="form-label">Выберите ученика:</label>';
                    html += '<select class="form-select" id="lessonStudentSelect" required>';
                    html += '<option value="">-- Выберите ученика --</option>';
                    data.students.forEach(student => {
                        html += `<option value="${student.id}">${student.first_name} ${student.last_name}</option>`;
                    });
                    html += '</select>';
                    html += '</div>';
                    html += '<div class="col-md-6">';
                    html += '<label class="form-label">Название урока:</label>';
                    html += '<input type="text" class="form-control" id="lessonTitle" placeholder="Урок математики: Квадратные уравнения" required>';
                    html += '</div>';
                    html += '</div>';
                    html += '<div class="row mb-3">';
                    html += '<div class="col-md-4">';
                    html += '<label class="form-label">Предмет:</label>';
                    html += '<input type="text" class="form-control" id="lessonSubject" placeholder="Математика">';
                    html += '</div>';
                    html += '<div class="col-md-4">';
                    html += '<label class="form-label">Дата урока:</label>';
                    html += '<input type="date" class="form-control" id="lessonDate" required>';
                    html += '</div>';
                    html += '<div class="col-md-4">';
                    html += '<label class="form-label">Время урока:</label>';
                    html += '<input type="time" class="form-control" id="lessonTime" required>';
                    html += '</div>';
                    html += '</div>';
                    html += '<div class="mb-3">';
                    html += '<label class="form-label">Тип видео:</label>';
                    html += '<div class="form-check">';
                    html += '<input class="form-check-input" type="radio" name="videoType" id="videoUrl" value="url" checked onchange="toggleVideoType()">';
                    html += '<label class="form-check-label" for="videoUrl">Ссылка на видео</label>';
                    html += '</div>';
                    html += '<div class="form-check">';
                    html += '<input class="form-check-input" type="radio" name="videoType" id="videoFile" value="file" onchange="toggleVideoType()">';
                    html += '<label class="form-check-label" for="videoFile">Загрузка файла</label>';
                    html += '</div>';
                    html += '</div>';
                    html += '<div class="mb-3" id="videoUrlDiv">';
                    html += '<label class="form-label">Ссылка на видео (необязательно):</label>';
                    html += '<input type="url" class="form-control" id="lessonVideoUrl" placeholder="https://youtube.com/...">';
                    html += '</div>';
                    html += '<div class="mb-3" id="videoFileDiv" style="display: none;">';
                    html += '<label class="form-label">Загрузить видеофайл (необязательно):</label>';
                    html += '<input type="file" class="form-control" id="lessonVideoFile" accept="video/*">';
                    html += '<small class="form-text text-muted">Поддерживаемые форматы: MP4, AVI, MOV, MKV</small>';
                    html += '</div>';
                    html += '<div class="mb-3">';
                    html += '<label class="form-label">Описание урока:</label>';
                    html += '<textarea class="form-control" id="lessonDescription" rows="3" placeholder="Краткое описание пройденного материала..."></textarea>';
                    html += '</div>';
                    html += '<div class="mb-3">';
                    html += '<label class="form-label">Домашнее задание:</label>';
                    html += '<textarea class="form-control" id="lessonHomework" rows="3" placeholder="Задания для самостоятельного выполнения..."></textarea>';
                    html += '</div>';
                    html += '<div class="alert alert-info">💡 Ручные записи уроков сохраняются постоянно (в отличие от автоматических записей звонков)</div>';
                    html += '<button type="submit" class="btn btn-primary">💾 Создать запись урока</button>';
                    html += '</form>';
                    html += '<hr>';
                }
            }
            
            if (data.auto_records && data.auto_records.length > 0) {
                html += '<h4>📞 Записи звонков (автоматические)</h4>';
                html += '<div class="alert alert-warning">⏰ Эти записи автоматически удаляются через 2 дня</div>';
                data.auto_records.forEach(record => {
                    html += renderLessonCard(record, true, userRole);
                });
            }
            
            if (data.manual_records && data.manual_records.length > 0) {
                html += '<h4>📚 Мои записи уроков</h4>';
                data.manual_records.forEach(record => {
                    html += renderLessonCard(record, false, userRole);
                });
            }
            
            if ((!data.auto_records || data.auto_records.length === 0) && (!data.manual_records || data.manual_records.length === 0)) {
                html += '<div class="alert alert-info">У вас нет записей уроков.</div>';
            }
            
            container.innerHTML = html;
            
            // Загружаем комментарии после рендеринга
            if (data.auto_records) {
                data.auto_records.forEach(record => loadComments(record.id));
            }
            if (data.manual_records) {
                data.manual_records.forEach(record => loadComments(record.id));
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки записей уроков:', error);
            document.getElementById('lessonsContent').innerHTML = '<div class="alert alert-danger">Ошибка загрузки данных</div>';
        });
}

function renderLessonCard(record, isAuto, userRole) {
    const titlePrefix = isAuto ? '🤖 ' : '';
    const availability = record.availability_status || 'permanent';
    let html = '';
    
    if (availability === 'expired') {
        html += `<div class="card mb-3 border-danger">`;
    } else {
        html += `<div class="card mb-3">`;
    }
    
    html += `<div class="card-body">`;
    html += `<h5>${titlePrefix}${availability === 'expired' ? '⏰ [ИСТЕКЛА] ' : ''}${record.lesson_title} - ${record.lesson_date || 'Дата не указана'}</h5>`;
    html += `<div class="row">`;
    html += `<div class="col-md-6">`;
    if (userRole === 'Ученик') {
        html += `<p><strong>Учитель:</strong> ${record.teacher_name} ${record.teacher_surname}</p>`;
    } else {
        html += `<p><strong>Ученик:</strong> ${record.student_name} ${record.student_surname}</p>`;
    }
    html += `<p><strong>Предмет:</strong> ${record.subject || 'Не указан'}</p>`;
    html += `<p><strong>Дата урока:</strong> ${record.lesson_date || 'Не указана'}</p>`;
    if (isAuto && record.expires_at) {
        html += `<p><strong>Истекает:</strong> ${record.expires_at}</p>`;
    }
    html += `</div>`;
    html += `<div class="col-md-6">`;
    if (record.description) {
        html += `<p><strong>Описание:</strong> ${record.description}</p>`;
    }
    if (record.homework) {
        html += `<p><strong>Домашнее задание:</strong> ${record.homework}</p>`;
    }
    if (record.video_url) {
        html += `<p><strong>Видео ссылка:</strong> <a href="${record.video_url}" target="_blank">Открыть</a></p>`;
    }
    html += `</div>`;
    html += `</div>`;
    
    if (record.video_file_path && availability !== 'expired') {
        html += `<button class="btn btn-primary" onclick="downloadVideo(${record.id}, '${record.video_file_path}', '${record.lesson_title}')">📥 Скачать</button>`;
    } else if (availability === 'expired') {
        html += `<p class="text-danger">❌ Недоступно</p>`;
    }
    
    html += `<hr>`;
    html += `<h6>💬 Комментарии</h6>`;
    html += `<div id="comments-${record.id}"></div>`;
    html += `<form onsubmit="addComment(event, ${record.id})">`;
    html += `<div class="mb-2">`;
    html += `<textarea class="form-control" id="comment-${record.id}" rows="2" placeholder="Напишите, что было непонятно..." required></textarea>`;
    html += `</div>`;
    html += `<div class="mb-2">`;
    html += `<input type="number" class="form-control" id="timestamp-${record.id}" min="0" value="0" placeholder="Временная метка видео (секунды, необязательно)">`;
    html += `</div>`;
    html += `<button type="submit" class="btn btn-sm btn-primary">💬 Добавить комментарий</button>`;
    html += `</form>`;
    
    html += `</div></div>`;
    
    return html;
}

function loadComments(lessonId) {
    fetch(`/api/dashboard/lessons/${lessonId}/comments`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById(`comments-${lessonId}`);
            if (!container) return;
            
            if (!data.comments || data.comments.length === 0) {
                container.innerHTML = '<p class="text-muted">Комментариев пока нет</p>';
            } else {
                let html = `<p>Комментариев: ${data.comments.length}</p>`;
                data.comments.forEach(comment => {
                    html += `<div class="card mb-2">`;
                    html += `<div class="card-body p-2">`;
                    html += `<strong>${comment.user_name} (${comment.user_role})</strong> - ${comment.created_at}`;
                    if (comment.timestamp) {
                        html += `<br><small>⏱️ Временная метка: ${comment.timestamp} сек</small>`;
                    }
                    html += `<p class="mb-0">${comment.comment_text}</p>`;
                    html += `</div></div>`;
                });
                container.innerHTML = html;
            }
        });
}

function addComment(event, lessonId) {
    event.preventDefault();
    const commentText = document.getElementById(`comment-${lessonId}`).value;
    const timestamp = parseInt(document.getElementById(`timestamp-${lessonId}`).value) || 0;
    
    fetch(`/api/dashboard/lessons/${lessonId}/comments`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            comment_text: commentText,
            timestamp: timestamp > 0 ? timestamp : null
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById(`comment-${lessonId}`).value = '';
            document.getElementById(`timestamp-${lessonId}`).value = '0';
            loadComments(lessonId);
        } else {
            alert('Ошибка: ' + data.message);
        }
    });
}

function downloadVideo(lessonId, videoPath, lessonTitle) {
    alert(`✅ Скачивание начато!\n📁 Файл: ${videoPath.split('/').pop()}\n📝 Урок: ${lessonTitle}\n💾 Путь: ${videoPath}\n💡 В реальной системе здесь будет прямое скачивание файла`);
}

function toggleVideoType() {
    const videoUrl = document.getElementById('videoUrl').checked;
    document.getElementById('videoUrlDiv').style.display = videoUrl ? 'block' : 'none';
    document.getElementById('videoFileDiv').style.display = videoUrl ? 'none' : 'block';
}

function createLesson(event) {
    event.preventDefault();
    const studentId = document.getElementById('lessonStudentSelect').value;
    const lessonTitle = document.getElementById('lessonTitle').value;
    const subject = document.getElementById('lessonSubject').value;
    const date = document.getElementById('lessonDate').value;
    const time = document.getElementById('lessonTime').value;
    const description = document.getElementById('lessonDescription').value;
    const homework = document.getElementById('lessonHomework').value;
    
    const videoType = document.querySelector('input[name="videoType"]:checked').value;
    let videoUrl = '';
    let videoFilePath = '';
    
    if (videoType === 'url') {
        videoUrl = document.getElementById('lessonVideoUrl').value;
    } else {
        const fileInput = document.getElementById('lessonVideoFile');
        if (fileInput.files.length > 0) {
            videoFilePath = `/uploads/lessons/${fileInput.files[0].name}`;
            alert(`Файл ${fileInput.files[0].name} готов к загрузке`);
        }
    }
    
    const lessonDatetime = `${date}T${time}`;
    
    fetch('/api/dashboard/lessons/create', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            student_id: parseInt(studentId),
            lesson_title: lessonTitle,
            lesson_datetime: lessonDatetime,
            subject: subject,
            video_url: videoUrl,
            video_file_path: videoFilePath,
            description: description,
            homework: homework
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ ' + data.message);
            loadLessons();
        } else {
            alert('❌ ' + data.message);
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('lessons') && document.getElementById('lessons').classList.contains('active')) {
        loadLessons();
    }
    
    const lessonsTab = document.querySelector('button[onclick="showTab(\'lessons\')"]');
    if (lessonsTab) {
        lessonsTab.addEventListener('click', function() {
            setTimeout(loadLessons, 100);
        });
    }
});

