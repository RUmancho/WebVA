// Система тестирования
let testingState = {
    currentPage: 'subjects',
    selectedSubject: null,
    selectedSection: null,
    selectedTopic: null,
    selectedDifficulty: null,
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
            <button class="btn btn-outline-primary w-100 p-3" onclick="selectTestingSubject('${subject}')">
                <h5>${subjectData.icon || '📚'} ${subject}</h5>
            </button>
        `;
        container.appendChild(col);
    });
    
    showTestingPage('subjects');
    updateTestingBreadcrumbs(['Предметы']);
}

function selectTestingSubject(subject) {
    fetch('/api/testing/select-subject', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({subject})
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            showTestingError(data.error);
            return;
        }
        testingState.selectedSubject = subject;
        displayTestingSections(subject, data.sections || {});
    })
    .catch(err => showTestingError('Ошибка: ' + err));
}

function displayTestingSections(subject, sections) {
    const title = document.getElementById('sections-title');
    const list = document.getElementById('sections-list');
    
    title.textContent = `${subject} - Выберите раздел:`;
    list.innerHTML = '';
    
    Object.keys(sections).forEach(section => {
        const item = document.createElement('a');
        item.href = '#';
        item.className = 'list-group-item list-group-item-action';
        item.innerHTML = `📖 ${section}`;
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
    fetch('/api/testing/select-section', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({section})
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            showTestingError(data.error);
            return;
        }
        testingState.selectedSection = section;
        displayTestingTopics(data.topics || []);
    })
    .catch(err => showTestingError('Ошибка: ' + err));
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
    fetch('/api/testing/select-topic', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({topic})
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            showTestingError(data.error);
            return;
        }
        testingState.selectedTopic = topic;
        displayDifficultyLevels(data.difficulty_levels || {});
    })
    .catch(err => showTestingError('Ошибка: ' + err));
}

function displayDifficultyLevels(levels) {
    const title = document.getElementById('difficulty-title');
    const container = document.getElementById('difficulty-list');
    
    title.textContent = `${testingState.selectedSubject} → ${testingState.selectedSection} → ${testingState.selectedTopic}`;
    container.innerHTML = '';
    
    Object.keys(levels).forEach(difficulty => {
        const level = levels[difficulty];
        const card = document.createElement('div');
        card.className = 'card mb-3';
        card.innerHTML = `
            <div class="card-body">
                <div class="row">
                    <div class="col-md-2">
                        <button class="btn btn-primary w-100" onclick="selectDifficulty('${difficulty}')">
                            ${level.icon || '🟢'} ${difficulty}
                        </button>
                    </div>
                    <div class="col-md-10">
                        <strong>${difficulty}:</strong> ${level.description || ''}
                    </div>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
    
    showTestingPage('difficulty');
    updateTestingBreadcrumbs(['Предметы', testingState.selectedSubject, testingState.selectedSection, testingState.selectedTopic]);
}

function selectDifficulty(difficulty) {
    testingState.selectedDifficulty = difficulty;
    generateTest();
}

function generateTest() {
    showTestingLoading(true);
    fetch('/api/testing/generate-test', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            subject: testingState.selectedSubject,
            section: testingState.selectedSection,
            topic: testingState.selectedTopic,
            difficulty: testingState.selectedDifficulty
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
    
    title.textContent = `Тест: ${testingState.selectedTopic} (${testingState.selectedDifficulty})`;
    questionsDiv.innerHTML = '';
    
    test.questions.forEach((question, index) => {
        const card = document.createElement('div');
        card.className = 'card mb-3';
        card.innerHTML = `
            <div class="card-body">
                <h5>Вопрос ${index + 1}: ${question.question}</h5>
                <div class="form-check" id="question-${index}">
                    ${question.options.map((opt, optIndex) => `
                        <div class="form-check">
                            <input class="form-check-input" type="radio" 
                                   name="question_${index}" id="q${index}_opt${optIndex}" 
                                   value="${opt}" onchange="saveTestingAnswer(${index}, '${opt.replace(/'/g, "\\'")}')">
                            <label class="form-check-label" for="q${index}_opt${optIndex}">
                                ${opt}
                            </label>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        questionsDiv.appendChild(card);
    });
    
    showTestingPage('test');
    updateTestingProgress();
}

function saveTestingAnswer(questionIndex, answer) {
    testingState.userAnswers[questionIndex] = answer;
    updateTestingProgress();
    
    fetch('/api/testing/submit-answer', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question_index: questionIndex, answer})
    }).catch(err => console.error('Ошибка сохранения ответа:', err));
}

function updateTestingProgress() {
    if (!testingState.currentTest) return;
    
    const total = testingState.currentTest.questions.length;
    const answered = Object.keys(testingState.userAnswers).length;
    const progress = (answered / total) * 100;
    
    document.getElementById('test-progress').style.width = progress + '%';
    document.getElementById('test-progress').textContent = `${answered}/${total}`;
    
    const finishBtn = document.getElementById('finish-test-btn');
    finishBtn.style.display = (answered === total) ? 'block' : 'none';
}

function finishTest() {
    fetch('/api/testing/finish-test', {method: 'POST'})
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                showTestingError(data.error);
                return;
            }
            displayTestingResults(data.results);
        })
        .catch(err => showTestingError('Ошибка: ' + err));
}

function displayTestingResults(results) {
    const title = document.getElementById('results-title');
    const content = document.getElementById('results-content');
    
    title.textContent = `Результаты тестирования: ${testingState.selectedTopic}`;
    
    const correct = results.correct_count || 0;
    const total = results.total_count || 0;
    const percentage = total > 0 ? Math.round((correct / total) * 100) : 0;
    
    content.innerHTML = `
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h3>${correct}/${total}</h3>
                        <p>Правильных ответов</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h3>${percentage}%</h3>
                        <p>Процент выполнения</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h3>${results.grade || 'N/A'}</h3>
                        <p>Оценка</p>
                    </div>
                </div>
            </div>
        </div>
        <h5>Разбор вопросов:</h5>
        <div id="results-details"></div>
    `;
    
    const details = document.getElementById('results-details');
    if (results.details) {
        results.details.forEach((detail, index) => {
            const card = document.createElement('div');
            card.className = 'card mb-2';
            const isCorrect = detail.is_correct;
            card.innerHTML = `
                <div class="card-body">
                    <h6>Вопрос ${index + 1}: ${detail.question}</h6>
                    <p><strong>Ваш ответ:</strong> ${detail.user_answer}</p>
                    <p><strong>Правильный ответ:</strong> ${detail.correct_answer}</p>
                    <p class="text-${isCorrect ? 'success' : 'danger'}">
                        ${isCorrect ? '✅ Правильно' : '❌ Неправильно'}
                    </p>
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
        testingState = {currentPage: 'subjects', selectedSubject: null, selectedSection: null, selectedTopic: null, selectedDifficulty: null};
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
    }
}

function showTestingPage(page) {
    document.querySelectorAll('.testing-page').forEach(p => p.style.display = 'none');
    document.getElementById(`testing-${page}`).style.display = 'block';
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
    document.getElementById('testing-loading').style.display = show ? 'block' : 'none';
}

function showTestingError(message) {
    const errorDiv = document.getElementById('testing-error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

