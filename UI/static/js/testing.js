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
    userAnswers: {},
    pendingSaves: new Map(),
    saveDebounceTimers: {},
    progressUpdatePending: false  // Флаг для throttle обновления прогресса
};

// Кэшированные DOM элементы для оптимизации
const domCache = {};

// Статический элемент для escapeHtml (переиспользуемый)
const escapeDiv = document.createElement('div');

// Функция получения элемента из кэша
function getElement(id) {
    if (!domCache[id]) {
        domCache[id] = document.getElementById(id);
    }
    return domCache[id];
}

// Очистка кэша (при необходимости)
function clearDomCache() {
    for (const key in domCache) {
        delete domCache[key];
    }
}

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('testing-content')) {
        loadTestingState();
    }
});

function loadTestingState() {
    console.log('[Testing] Загрузка состояния тестирования...');
    fetch('/api/testing/state')
        .then(r => r.json())
        .then(data => {
            console.log('[Testing] Получены данные:', data);
            if (data.error) {
                console.error('[Testing] Ошибка в данных:', data.error);
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
                console.log('[Testing] Предметы найдены, количество:', Object.keys(data.subjects).length);
                displayTestingSubjects(data.subjects);
            } else {
                console.warn('[Testing] Предметы не найдены в ответе!');
            }
        })
        .catch(err => {
            console.error('[Testing] Ошибка загрузки состояния:', err);
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
    const container = getElement('testing-subjects-list');
    if (!container) return;
    
    // Используем DocumentFragment для батчевой вставки
    const fragment = document.createDocumentFragment();
    const subjectKeys = Object.keys(subjects);
    
    subjectKeys.forEach(subject => {
        const subjectData = subjects[subject];
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-3';
        
        const btn = document.createElement('button');
        btn.className = 'btn btn-outline-primary w-100 p-3 subject-btn';
        btn.onclick = () => selectTestingSubject(subject);
        
        const h5 = document.createElement('h5');
        h5.className = 'mb-0';
        h5.textContent = `${subjectData.icon || '📚'} ${subject}`;
        
        btn.appendChild(h5);
        col.appendChild(btn);
        fragment.appendChild(col);
    });
    
    container.innerHTML = '';
    container.appendChild(fragment);
    
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
    const title = getElement('testing-sections-title');
    const list = getElement('testing-sections-list');
    
    title.textContent = `${subject} - Выберите раздел:`;
    
    const fragment = document.createDocumentFragment();
    
    Object.keys(sections).forEach(section => {
        const item = document.createElement('a');
        item.href = '#';
        item.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
        
        const span1 = document.createElement('span');
        span1.textContent = section;
        
        const span2 = document.createElement('span');
        span2.className = 'badge bg-secondary';
        span2.textContent = `${sections[section].topics ? sections[section].topics.length : 0} тем`;
        
        item.appendChild(span1);
        item.appendChild(span2);
        item.onclick = (e) => {
            e.preventDefault();
            selectTestingSection(section);
        };
        fragment.appendChild(item);
    });
    
    list.innerHTML = '';
    list.appendChild(fragment);
    
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
    const title = getElement('testing-topics-title');
    const list = getElement('testing-topics-list');
    
    title.textContent = `${testingState.selectedSubject} → ${testingState.selectedSection} - Выберите тему:`;
    
    const fragment = document.createDocumentFragment();
    
    topics.forEach(topic => {
        const item = document.createElement('a');
        item.href = '#';
        item.className = 'list-group-item list-group-item-action';
        item.textContent = topic;
        item.onclick = (e) => {
            e.preventDefault();
            selectTestingTopic(topic);
        };
        fragment.appendChild(item);
    });
    
    list.innerHTML = '';
    list.appendChild(fragment);
    
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
    const title = getElement('difficulty-title');
    const container = getElement('difficulty-list');
    const generatorInfo = getElement('generator-info');
    
    title.textContent = `${testingState.selectedSubject} → ${testingState.selectedSection} → ${testingState.selectedTopic}`;
    
    if (generatorInfo) generatorInfo.style.display = 'none';
    
    const testTypeRadio = document.querySelector(`input[name="test_type"][value="${data.current_test_type || 'with_options'}"]`);
    if (testTypeRadio) testTypeRadio.checked = true;
    
    const numQuestionsInput = getElement('num_questions');
    if (numQuestionsInput) {
        numQuestionsInput.value = data.current_num_questions || 5;
        numQuestionsInput.min = data.min_questions || 3;
        numQuestionsInput.max = data.max_questions || 20;
    }
    
    const fragment = document.createDocumentFragment();
    
    Object.keys(levels).forEach(difficulty => {
        const level = levels[difficulty];
        const card = document.createElement('div');
        card.className = 'card mb-3 difficulty-card';
        
        const btn = document.createElement('button');
        btn.className = 'btn btn-primary btn-lg w-100';
        btn.textContent = `${level.icon || '🟢'} ${difficulty}`;
        btn.onclick = () => selectDifficulty(difficulty);
        
        card.innerHTML = `
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col-md-3"></div>
                    <div class="col-md-9">
                        <strong>${escapeHtml(difficulty)}:</strong> ${escapeHtml(level.description || '')}
                        <br><small class="text-muted">${escapeHtml(level.style || '')}</small>
                    </div>
                </div>
            </div>
        `;
        card.querySelector('.col-md-3').appendChild(btn);
        fragment.appendChild(card);
    });
    
    container.innerHTML = '';
    container.appendChild(fragment);
    
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
    const title = getElement('test-title');
    const questionsDiv = getElement('test-questions');
    const testTypeBadge = getElement('test-type-badge');
    const generatorBadge = getElement('test-generator-badge');
    
    title.textContent = `Тест: ${testingState.selectedTopic} (${testingState.selectedDifficulty})`;
    
    const isWithOptions = test.test_type === 'with_options';
    testTypeBadge.innerHTML = isWithOptions 
        ? '<span class="badge bg-primary">📝 С вариантами</span>'
        : '<span class="badge bg-info">✍️ Свободный ввод</span>';
    
    generatorBadge.innerHTML = '';
    
    const fragment = document.createDocumentFragment();
    const totalQuestions = test.questions.length;
    
    test.questions.forEach((question, index) => {
        const card = document.createElement('div');
        card.className = 'card mb-3 question-card';
        card.id = `question-card-${index}`;
        
        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';
        
        const titleEl = document.createElement('h5');
        titleEl.className = 'card-title';
        titleEl.textContent = `Вопрос ${index + 1} из ${totalQuestions}`;
        
        const questionText = document.createElement('p');
        questionText.className = 'card-text fs-5';
        questionText.textContent = question.question;
        
        cardBody.appendChild(titleEl);
        cardBody.appendChild(questionText);
        
        if (isWithOptions && question.options) {
            const optionsDiv = document.createElement('div');
            optionsDiv.className = 'form-check';
            optionsDiv.id = `question-${index}`;
            
            question.options.forEach((opt, optIndex) => {
                const checkDiv = document.createElement('div');
                checkDiv.className = 'form-check';
                
                const input = document.createElement('input');
                input.className = 'form-check-input';
                input.type = 'radio';
                input.name = `question_${index}`;
                input.id = `q${index}_opt${optIndex}`;
                input.value = opt;
                input.onchange = function() { saveTestingAnswer(index, this.value); };
                
                const label = document.createElement('label');
                label.className = 'form-check-label';
                label.htmlFor = `q${index}_opt${optIndex}`;
                label.textContent = opt;
                
                checkDiv.appendChild(input);
                checkDiv.appendChild(label);
                optionsDiv.appendChild(checkDiv);
            });
            
            cardBody.appendChild(optionsDiv);
        } else {
            const inputDiv = document.createElement('div');
            inputDiv.className = 'mt-3';
            
            const label = document.createElement('label');
            label.className = 'form-label';
            label.htmlFor = `answer_${index}`;
            label.textContent = 'Ваш ответ:';
            
            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'form-control test-input';
            input.id = `answer_${index}`;
            input.placeholder = 'Введите ответ (например: x = 5 или просто 5)';
            // Используем только oninput с дебаунсингом (более эффективно чем onkeyup)
            input.oninput = function() { saveTestingAnswer(index, this.value); };
            
            const small = document.createElement('small');
            small.className = 'text-muted';
            small.textContent = 'Для уравнений можно вводить в формате "x = значение" или просто "значение"';
            
            inputDiv.appendChild(label);
            inputDiv.appendChild(input);
            inputDiv.appendChild(small);
            cardBody.appendChild(inputDiv);
        }
        
        card.appendChild(cardBody);
        fragment.appendChild(card);
    });
    
    questionsDiv.innerHTML = '';
    questionsDiv.appendChild(fragment);
    
    showTestingPage('test');
    updateTestingProgress();
}

function escapeHtml(text) {
    if (!text) return '';
    escapeDiv.textContent = text;
    return escapeDiv.innerHTML;
}

function saveTestingAnswer(questionIndex, answer) {
    testingState.userAnswers[questionIndex] = answer;
    
    // Подсвечиваем отвеченный вопрос (без querySelector, напрямую по ID)
    const card = document.getElementById(`question-card-${questionIndex}`);
    if (card) {
        if (answer) {
            card.classList.add('answered');
        } else {
            card.classList.remove('answered');
        }
    }
    
    // Throttle обновления прогресса - не чаще чем раз в 100мс
    if (!testingState.progressUpdatePending) {
        testingState.progressUpdatePending = true;
        requestAnimationFrame(() => {
            updateTestingProgress();
            testingState.progressUpdatePending = false;
        });
    }
    
    // Дебаунсинг сохранения на сервер: 500мс задержка
    if (testingState.saveDebounceTimers[questionIndex]) {
        clearTimeout(testingState.saveDebounceTimers[questionIndex]);
    }
    
    testingState.saveDebounceTimers[questionIndex] = setTimeout(() => {
        saveAnswerToServer(questionIndex, answer);
    }, 500);
}

function saveAnswerToServer(questionIndex, answer) {
    // Создаём промис для отслеживания запроса
    const savePromise = fetch('/api/testing/submit-answer', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question_index: questionIndex, answer})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            console.error('Ошибка сохранения ответа:', data.error);
        } else {
            console.log(`[Testing] Ответ ${questionIndex} сохранён`);
        }
    })
    .catch(err => {
        console.error('Ошибка сохранения ответа:', err);
    })
    .finally(() => {
        testingState.pendingSaves.delete(questionIndex);
    });
    
    testingState.pendingSaves.set(questionIndex, savePromise);
}

function updateTestingProgress() {
    if (!testingState.currentTest) return;
    
    const total = testingState.currentTest.questions.length;
    let answered = 0;
    
    // Более эффективный подсчёт без создания массива
    for (const k in testingState.userAnswers) {
        if (testingState.userAnswers[k]) answered++;
    }
    
    const progress = (answered / total) * 100;
    
    const progressBar = getElement('test-progress');
    if (!progressBar) return;
    
    // Минимизируем DOM-операции
    progressBar.style.width = progress + '%';
    progressBar.textContent = `${answered}/${total}`;
    
    // Устанавливаем класс за одну операцию
    const newClass = progress === 100 ? 'progress-bar bg-success' : 
                     progress >= 50 ? 'progress-bar bg-info' : 'progress-bar';
    if (progressBar.className !== newClass) {
        progressBar.className = newClass;
    }
    
    const finishBtn = getElement('finish-test-btn');
    if (finishBtn) {
        const shouldShow = answered === total;
        const currentlyShown = finishBtn.style.display === 'inline-block';
        if (shouldShow !== currentlyShown) {
            finishBtn.style.display = shouldShow ? 'inline-block' : 'none';
        }
    }
}

async function finishTest() {
    showTestingLoading(true);
    
    // Сначала отменяем все дебаунс-таймеры и сохраняем все ответы немедленно
    for (const questionIndex in testingState.saveDebounceTimers) {
        clearTimeout(testingState.saveDebounceTimers[questionIndex]);
        const answer = testingState.userAnswers[questionIndex];
        if (answer !== undefined) {
            saveAnswerToServer(parseInt(questionIndex), answer);
        }
    }
    testingState.saveDebounceTimers = {};
    
    // Ждём завершения всех незавершённых запросов сохранения
    if (testingState.pendingSaves.size > 0) {
        console.log(`[Testing] Ожидание сохранения ${testingState.pendingSaves.size} ответов...`);
        try {
            await Promise.all(testingState.pendingSaves.values());
        } catch (err) {
            console.error('Ошибка при ожидании сохранения ответов:', err);
        }
    }
    
    // Перед отправкой на проверку, отправляем все ответы ещё раз для надёжности
    try {
        await fetch('/api/testing/submit-all-answers', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({answers: testingState.userAnswers})
        });
    } catch (err) {
        console.error('Ошибка при отправке всех ответов:', err);
    }
    
    // Теперь завершаем тест
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
    const title = getElement('results-title');
    const content = getElement('results-content');
    
    title.textContent = `${results.grade_icon || '📊'} Результаты: ${testingState.selectedTopic}`;
    
    const correct = results.correct_count || 0;
    const total = results.total_questions || 0;
    const percentage = results.percentage || 0;
    const roundedPercentage = Math.round(percentage);
    
    let resultColor = 'danger';
    if (percentage >= 90) resultColor = 'success';
    else if (percentage >= 70) resultColor = 'primary';
    else if (percentage >= 50) resultColor = 'warning';
    
    // Создаём разметку результатов и деталей за один раз
    let detailsHtml = '';
    if (results.detailed_results) {
        detailsHtml = results.detailed_results.map((detail, index) => {
            const isCorrect = detail.is_correct;
            const userAnswer = detail.user_answer ? escapeHtml(detail.user_answer) : '<em class="text-muted">Нет ответа</em>';
            const correctAnswer = !isCorrect ? `<p class="mb-0 text-success"><strong>Правильный ответ:</strong> ${escapeHtml(detail.correct_answer)}</p>` : '';
            
            return `
                <div class="card mb-2 result-card ${isCorrect ? 'correct' : 'incorrect'}">
                    <div class="card-body py-2">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="mb-1">Вопрос ${index + 1}: ${escapeHtml(detail.question)}</h6>
                                <p class="mb-1"><strong>Ваш ответ:</strong> ${userAnswer}</p>
                                ${correctAnswer}
                            </div>
                            <span class="badge bg-${isCorrect ? 'success' : 'danger'} fs-6">
                                ${isCorrect ? '✅' : '❌'}
                            </span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    content.innerHTML = `
        <div class="text-center mb-4">
            <h1 class="display-1">${results.celebration_emojis || '🎉'}</h1>
            <h2 class="text-${resultColor}">${escapeHtml(results.grade) || 'N/A'}</h2>
            <p class="lead">${escapeHtml(results.congratulations) || ''}</p>
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
                        <h3 class="text-${resultColor}">${roundedPercentage}%</h3>
                        <p class="mb-0">Процент выполнения</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center border-${resultColor}">
                    <div class="card-body">
                        <h3>${results.grade_icon || '📊'}</h3>
                        <p class="mb-0">${escapeHtml(results.grade) || 'Оценка'}</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="progress mb-4" style="height: 25px;">
            <div class="progress-bar bg-${resultColor}" role="progressbar" 
                 style="width: ${percentage}%" aria-valuenow="${percentage}">
                ${roundedPercentage}%
            </div>
        </div>
        
        <h5 class="mb-3">📋 Разбор вопросов:</h5>
        <div id="results-details">${detailsHtml}</div>
    `;
    
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
            userAnswers: {},
            pendingSaves: new Map(),
            saveDebounceTimers: {},
            progressUpdatePending: false
        };
        clearDomCache();  // Очищаем кэш при полной навигации
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
    const loadingEl = getElement('testing-loading');
    if (loadingEl) {
        loadingEl.style.display = show ? 'block' : 'none';
    }
}

function showTestingError(message) {
    const errorDiv = getElement('testing-error');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

