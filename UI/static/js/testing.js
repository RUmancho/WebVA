// Система тестирования
let testingState = {
    currentPage: 'subjects',
    selectedSubject: null,
    selectedSection: null,
    selectedTopic: null,
    selectedDifficulty: null,
    testType: 'with_options',
    numQuestions: 5,
    currentTest: null,
    userAnswers: {}
};

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('testing-content')) {
        loadTestingState();
    }
});

function loadTestingState() {
    fetch('/api/testing/state')
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                showTestingError(data.error);
                return;
            }
            
            testingState.currentPage = data.current_page || 'subjects';
            testingState.selectedSubject = data.selected_subject;
            testingState.selectedSection = data.selected_section;
            testingState.selectedTopic = data.selected_topic;
            testingState.selectedDifficulty = data.selected_difficulty;
            testingState.testType = data.test_type || 'with_options';
            testingState.numQuestions = data.num_questions || 5;
            
            if (data.subjects) {
                displayTestingSubjects(data.subjects);
            }
        })
        .catch(err => {
            console.error('Ошибка загрузки состояния:', err);
            loadTestingSubjects();
        });
}

function loadTestingSubjects() {
    showTestingLoading(true);
    fetch('/api/testing/subjects')
        .then(r => r.json())
        .then(data => {
            showTestingLoading(false);
            if (data.error) {
                showTestingError(data.error);
                return;
            }
            displayTestingSubjects(data.subjects_structure || {});
        })
        .catch(err => {
            showTestingLoading(false);
            showTestingError('Ошибка загрузки предметов: ' + err);
        });
}

function displayTestingSubjects(subjects) {
    const container = document.getElementById('subjects-list');
    container.innerHTML = '';
    
    Object.keys(subjects).forEach(subject => {
        const subjectData = subjects[subject];
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-3';
        col.innerHTML = `
            <button class="btn btn-outline-primary w-100 p-3 subject-btn" onclick="selectTestingSubject('${subject}')">
                <h5 class="mb-0">${subjectData.icon || '📚'} ${subject}</h5>
            </button>
        `;
        container.appendChild(col);
    });
    
    showTestingPage('subjects');
    updateTestingBreadcrumbs(['Предметы']);
}

function selectTestingSubject(subject) {
    showTestingLoading(true);
    fetch('/api/testing/select-subject', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({subject})
    })
    .then(r => r.json())
    .then(data => {
        showTestingLoading(false);
        if (data.error) {
            showTestingError(data.error);
            return;
        }
        testingState.selectedSubject = subject;
        displayTestingSections(subject, data.sections || {});
    })
    .catch(err => {
        showTestingLoading(false);
        showTestingError('Ошибка: ' + err);
    });
}

function displayTestingSections(subject, sections) {
    const title = document.getElementById('sections-title');
    const list = document.getElementById('sections-list');
    
    title.textContent = `${subject} - Выберите раздел:`;
    list.innerHTML = '';
    
    Object.keys(sections).forEach(section => {
        const item = document.createElement('a');
        item.href = '#';
        item.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
        item.innerHTML = `
            <span>📖 ${section}</span>
            <span class="badge bg-secondary">${sections[section].topics ? sections[section].topics.length : 0} тем</span>
        `;
        item.onclick = (e) => {
            e.preventDefault();
            selectTestingSection(section);
        };
        list.appendChild(item);
    });
    
    showTestingPage('sections');
    updateTestingBreadcrumbs(['Предметы', subject]);
}

function selectTestingSection(section) {
    showTestingLoading(true);
    fetch('/api/testing/select-section', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({section})
    })
    .then(r => r.json())
    .then(data => {
        showTestingLoading(false);
        if (data.error) {
            showTestingError(data.error);
            return;
        }
        testingState.selectedSection = section;
        displayTestingTopics(data.topics || []);
    })
    .catch(err => {
        showTestingLoading(false);
        showTestingError('Ошибка: ' + err);
    });
}

function displayTestingTopics(topics) {
    const title = document.getElementById('topics-title');
    const list = document.getElementById('topics-list');
    
    title.textContent = `${testingState.selectedSubject} → ${testingState.selectedSection} - Выберите тему:`;
    list.innerHTML = '';
    
    topics.forEach(topic => {
        const item = document.createElement('a');
        item.href = '#';
        item.className = 'list-group-item list-group-item-action';
        item.innerHTML = `🎯 ${topic}`;
        item.onclick = (e) => {
            e.preventDefault();
            selectTestingTopic(topic);
        };
        list.appendChild(item);
    });
    
    showTestingPage('topics');
    updateTestingBreadcrumbs(['Предметы', testingState.selectedSubject, testingState.selectedSection]);
}

function selectTestingTopic(topic) {
    showTestingLoading(true);
    fetch('/api/testing/select-topic', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({topic})
    })
    .then(r => r.json())
    .then(data => {
        showTestingLoading(false);
        if (data.error) {
            showTestingError(data.error);
            return;
        }
        testingState.selectedTopic = topic;
        displayDifficultyLevels(data);
    })
    .catch(err => {
        showTestingLoading(false);
        showTestingError('Ошибка: ' + err);
    });
}

function displayDifficultyLevels(data) {
    const levels = data.difficulty_levels || {};
    const title = document.getElementById('difficulty-title');
    const container = document.getElementById('difficulty-list');
    const generatorInfo = document.getElementById('generator-info');
    
    title.textContent = `${testingState.selectedSubject} → ${testingState.selectedSection} → ${testingState.selectedTopic}`;
    
    // Показываем информацию о генераторе
    if (data.generator_info) {
        generatorInfo.textContent = data.generator_info;
        generatorInfo.style.display = 'block';
    } else {
        generatorInfo.style.display = 'none';
    }
    
    // Устанавливаем текущие значения настроек
    const testTypeRadio = document.querySelector(`input[name="test_type"][value="${data.current_test_type || 'with_options'}"]`);
    if (testTypeRadio) testTypeRadio.checked = true;
    
    const numQuestionsInput = document.getElementById('num_questions');
    if (numQuestionsInput) {
        numQuestionsInput.value = data.current_num_questions || 5;
        numQuestionsInput.min = data.min_questions || 3;
        numQuestionsInput.max = data.max_questions || 20;
    }
    
    container.innerHTML = '';
    
    Object.keys(levels).forEach(difficulty => {
        const level = levels[difficulty];
        const card = document.createElement('div');
        card.className = 'card mb-3 difficulty-card';
        card.innerHTML = `
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col-md-3">
                        <button class="btn btn-primary btn-lg w-100" onclick="selectDifficulty('${difficulty}')">
                            ${level.icon || '🟢'} ${difficulty}
                        </button>
                    </div>
                    <div class="col-md-9">
                        <strong>${difficulty}:</strong> ${level.description || ''}
                        <br><small class="text-muted">${level.style || ''}</small>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
    
    showTestingPage('difficulty');
    updateTestingBreadcrumbs(['Предметы', testingState.selectedSubject, testingState.selectedSection, testingState.selectedTopic]);
}

function getTestSettings() {
    const testTypeRadio = document.querySelector('input[name="test_type"]:checked');
    const numQuestionsInput = document.getElementById('num_questions');
    
    return {
        test_type: testTypeRadio ? testTypeRadio.value : 'with_options',
        num_questions: numQuestionsInput ? parseInt(numQuestionsInput.value) || 5 : 5
    };
}

function selectDifficulty(difficulty) {
    testingState.selectedDifficulty = difficulty;
    const settings = getTestSettings();
    testingState.testType = settings.test_type;
    testingState.numQuestions = settings.num_questions;
    generateTest();
}

function generateTest() {
    showTestingLoading(true);
    const settings = getTestSettings();
    
    fetch('/api/testing/generate-test', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            subject: testingState.selectedSubject,
            section: testingState.selectedSection,
            topic: testingState.selectedTopic,
            difficulty: testingState.selectedDifficulty,
            test_type: settings.test_type,
            num_questions: settings.num_questions
        })
    })
    .then(r => r.json())
    .then(data => {
        showTestingLoading(false);
        if (data.error) {
            showTestingError(data.error);
            return;
        }
        testingState.currentTest = data.test;
        testingState.testType = data.test.test_type || settings.test_type;
        testingState.userAnswers = {};
        displayTest(data.test);
    })
    .catch(err => {
        showTestingLoading(false);
        showTestingError('Ошибка генерации теста: ' + err);
    });
}

function displayTest(test) {
    const title = document.getElementById('test-title');
    const questionsDiv = document.getElementById('test-questions');
    const testTypeBadge = document.getElementById('test-type-badge');
    const generatorBadge = document.getElementById('test-generator-badge');
    
    title.textContent = `Тест: ${testingState.selectedTopic} (${testingState.selectedDifficulty})`;
    
    // Показываем информацию о тесте
    const isWithOptions = test.test_type === 'with_options';
    testTypeBadge.innerHTML = isWithOptions 
        ? '<span class="badge bg-primary">📝 С вариантами</span>'
        : '<span class="badge bg-info">✍️ Свободный ввод</span>';
    
    if (test.generator) {
        const generatorNames = {
            'algebra_dll': '🚀 DLL генератор',
            'llm': '🤖 AI генератор',
            'local': '📚 Локальная база'
        };
        generatorBadge.innerHTML = `<span class="badge bg-secondary">${generatorNames[test.generator] || test.generator}</span>`;
    }
    
    questionsDiv.innerHTML = '';
    
    test.questions.forEach((question, index) => {
        const card = document.createElement('div');
        card.className = 'card mb-3 question-card';
        card.id = `question-card-${index}`;
        
        let optionsHtml = '';
        
        if (isWithOptions && question.options) {
            // Тест с вариантами ответов
            optionsHtml = `
                <div class="form-check" id="question-${index}">
                    ${question.options.map((opt, optIndex) => `
                        <div class="form-check">
                            <input class="form-check-input" type="radio" 
                                   name="question_${index}" id="q${index}_opt${optIndex}" 
                                   value="${escapeHtml(opt)}" 
                                   onchange="saveTestingAnswer(${index}, this.value)">
                            <label class="form-check-label" for="q${index}_opt${optIndex}">
                                ${escapeHtml(opt)}
                            </label>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            // Тест без вариантов - свободный ввод
            optionsHtml = `
                <div class="mt-3">
                    <label for="answer_${index}" class="form-label">Ваш ответ:</label>
                    <input type="text" class="form-control test-input" 
                           id="answer_${index}" 
                           placeholder="Введите ответ (например: x = 5 или просто 5)"
                           onchange="saveTestingAnswer(${index}, this.value)"
                           onkeyup="saveTestingAnswer(${index}, this.value)">
                    <small class="text-muted">Для уравнений можно вводить в формате "x = значение" или просто "значение"</small>
                </div>
            `;
        }
        
        card.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">Вопрос ${index + 1} из ${test.questions.length}</h5>
                <p class="card-text fs-5">${escapeHtml(question.question)}</p>
                ${optionsHtml}
            </div>
        `;
        questionsDiv.appendChild(card);
    });
    
    showTestingPage('test');
    updateTestingProgress();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function saveTestingAnswer(questionIndex, answer) {
    testingState.userAnswers[questionIndex] = answer;
    
    // Подсвечиваем отвеченный вопрос
    const card = document.getElementById(`question-card-${questionIndex}`);
    if (card && answer) {
        card.classList.add('answered');
    } else if (card) {
        card.classList.remove('answered');
    }
    
    updateTestingProgress();
    
    // Сохраняем на сервере
    fetch('/api/testing/submit-answer', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question_index: questionIndex, answer})
    }).catch(err => console.error('Ошибка сохранения ответа:', err));
}

function updateTestingProgress() {
    if (!testingState.currentTest) return;
    
    const total = testingState.currentTest.questions.length;
    const answered = Object.keys(testingState.userAnswers).filter(k => testingState.userAnswers[k]).length;
    const progress = (answered / total) * 100;
    
    const progressBar = document.getElementById('test-progress');
    progressBar.style.width = progress + '%';
    progressBar.textContent = `${answered}/${total}`;
    progressBar.className = 'progress-bar';
    
    if (progress === 100) {
        progressBar.classList.add('bg-success');
    } else if (progress >= 50) {
        progressBar.classList.add('bg-info');
    }
    
    const finishBtn = document.getElementById('finish-test-btn');
    finishBtn.style.display = (answered === total) ? 'inline-block' : 'none';
}

function finishTest() {
    showTestingLoading(true);
    fetch('/api/testing/finish-test', {method: 'POST'})
        .then(r => r.json())
        .then(data => {
            showTestingLoading(false);
            if (data.error) {
                showTestingError(data.error);
                return;
            }
            displayTestingResults(data.results);
        })
        .catch(err => {
            showTestingLoading(false);
            showTestingError('Ошибка: ' + err);
        });
}

function displayTestingResults(results) {
    const title = document.getElementById('results-title');
    const content = document.getElementById('results-content');
    
    title.textContent = `${results.grade_icon || '📊'} Результаты: ${testingState.selectedTopic}`;
    
    const correct = results.correct_count || 0;
    const total = results.total_questions || 0;
    const percentage = results.percentage || 0;
    
    // Определяем цвет в зависимости от результата
    let resultColor = 'danger';
    if (percentage >= 90) resultColor = 'success';
    else if (percentage >= 70) resultColor = 'primary';
    else if (percentage >= 50) resultColor = 'warning';
    
    content.innerHTML = `
        <div class="text-center mb-4">
            <h1 class="display-1">${results.celebration_emojis || '🎉'}</h1>
            <h2 class="text-${resultColor}">${results.grade || 'N/A'}</h2>
            <p class="lead">${results.congratulations || ''}</p>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card text-center border-${resultColor}">
                    <div class="card-body">
                        <h3 class="text-${resultColor}">${correct}/${total}</h3>
                        <p class="mb-0">Правильных ответов</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center border-${resultColor}">
                    <div class="card-body">
                        <h3 class="text-${resultColor}">${Math.round(percentage)}%</h3>
                        <p class="mb-0">Процент выполнения</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center border-${resultColor}">
                    <div class="card-body">
                        <h3>${results.grade_icon || '📊'}</h3>
                        <p class="mb-0">${results.grade || 'Оценка'}</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="progress mb-4" style="height: 25px;">
            <div class="progress-bar bg-${resultColor}" role="progressbar" 
                 style="width: ${percentage}%" aria-valuenow="${percentage}">
                ${Math.round(percentage)}%
            </div>
        </div>
        
        <h5 class="mb-3">📋 Разбор вопросов:</h5>
        <div id="results-details"></div>
    `;
    
    const details = document.getElementById('results-details');
    if (results.detailed_results) {
        results.detailed_results.forEach((detail, index) => {
            const card = document.createElement('div');
            const isCorrect = detail.is_correct;
            card.className = `card mb-2 result-card ${isCorrect ? 'correct' : 'incorrect'}`;
            card.innerHTML = `
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1">Вопрос ${index + 1}: ${escapeHtml(detail.question)}</h6>
                            <p class="mb-1"><strong>Ваш ответ:</strong> ${escapeHtml(detail.user_answer) || '<em class="text-muted">Нет ответа</em>'}</p>
                            ${!isCorrect ? `<p class="mb-0 text-success"><strong>Правильный ответ:</strong> ${escapeHtml(detail.correct_answer)}</p>` : ''}
                        </div>
                        <span class="badge bg-${isCorrect ? 'success' : 'danger'} fs-6">
                            ${isCorrect ? '✅' : '❌'}
                        </span>
                    </div>
                </div>
            `;
            details.appendChild(card);
        });
    }
    
    showTestingPage('results');
}

function regenerateTest() {
    generateTest();
}

function testingNavigate(page) {
    if (page === 'subjects') {
        testingState = {
            currentPage: 'subjects', 
            selectedSubject: null, 
            selectedSection: null, 
            selectedTopic: null, 
            selectedDifficulty: null,
            testType: 'with_options',
            numQuestions: 5,
            currentTest: null,
            userAnswers: {}
        };
        loadTestingSubjects();
    } else if (page === 'sections' && testingState.selectedSubject) {
        testingState.currentPage = 'sections';
        fetch('/api/testing/select-subject', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({subject: testingState.selectedSubject})
        })
        .then(r => r.json())
        .then(data => displayTestingSections(testingState.selectedSubject, data.sections || {}))
        .catch(err => showTestingError('Ошибка: ' + err));
    } else if (page === 'topics' && testingState.selectedSubject && testingState.selectedSection) {
        testingState.currentPage = 'topics';
        fetch('/api/testing/select-section', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({section: testingState.selectedSection})
        })
        .then(r => r.json())
        .then(data => displayTestingTopics(data.topics || []))
        .catch(err => showTestingError('Ошибка: ' + err));
    } else if (page === 'difficulty' && testingState.selectedTopic) {
        testingState.currentPage = 'difficulty';
        fetch('/api/testing/select-topic', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({topic: testingState.selectedTopic})
        })
        .then(r => r.json())
        .then(data => displayDifficultyLevels(data))
        .catch(err => showTestingError('Ошибка: ' + err));
    }
}

function showTestingPage(page) {
    document.querySelectorAll('.testing-page').forEach(p => p.style.display = 'none');
    const pageEl = document.getElementById(`testing-${page}`);
    if (pageEl) {
        pageEl.style.display = 'block';
    }
    testingState.currentPage = page;
}

function updateTestingBreadcrumbs(items) {
    const breadcrumbs = document.getElementById('testing-breadcrumbs');
    const ol = breadcrumbs.querySelector('ol');
    ol.innerHTML = '';
    
    items.forEach((item, index) => {
        const li = document.createElement('li');
        li.className = 'breadcrumb-item' + (index === items.length - 1 ? ' active' : '');
        if (index < items.length - 1) {
            const a = document.createElement('a');
            a.href = '#';
            a.textContent = item;
            a.onclick = (e) => {
                e.preventDefault();
                if (index === 0) testingNavigate('subjects');
                else if (index === 1) testingNavigate('sections');
                else if (index === 2) testingNavigate('topics');
                else if (index === 3) testingNavigate('difficulty');
            };
            li.appendChild(a);
        } else {
            li.textContent = item;
        }
        ol.appendChild(li);
    });
    
    breadcrumbs.style.display = items.length > 1 ? 'block' : 'none';
}

function showTestingLoading(show) {
    const loadingEl = document.getElementById('testing-loading');
    if (loadingEl) {
        loadingEl.style.display = show ? 'block' : 'none';
    }
}

function showTestingError(message) {
    const errorDiv = document.getElementById('testing-error');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

