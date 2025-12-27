// Теоретические материалы
let theoryState = {
    currentPage: 'subjects',
    selectedSubject: null,
    selectedSection: null,
    selectedTopic: null
};

// Загрузка состояния при открытии вкладки
document.addEventListener('DOMContentLoaded', function() {
    console.log('[Theory] DOM загружен, проверяем наличие контейнера...');
    const theoryContent = document.getElementById('theory-content');
    if (theoryContent) {
        console.log('[Theory] Контейнер найден, загружаем состояние...');
        // Проверяем, видна ли вкладка теории
        const theoryTab = document.getElementById('theory');
        if (theoryTab && theoryTab.classList.contains('active')) {
            console.log('[Theory] Вкладка теории активна, загружаем данные...');
            loadTheoryState();
        } else {
            console.log('[Theory] Вкладка теории не активна, ждем открытия...');
        }
    } else {
        console.warn('[Theory] Контейнер theory-content не найден!');
    }
});

// Также инициализируем при показе вкладки (на случай, если она была скрыта при DOMContentLoaded)
const theoryObserver = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
            const theoryTab = document.getElementById('theory');
            if (theoryTab && theoryTab.classList.contains('active')) {
                const theoryContent = document.getElementById('theory-content');
                if (theoryContent && !theoryContent.querySelector('#subjects-list').hasChildNodes()) {
                    console.log('[Theory] Вкладка стала активной, загружаем данные...');
                    loadTheoryState();
                }
            }
        }
    });
});

// Наблюдаем за изменениями вкладки теории
document.addEventListener('DOMContentLoaded', function() {
    const theoryTab = document.getElementById('theory');
    if (theoryTab) {
        theoryObserver.observe(theoryTab, { attributes: true });
    }
});

function loadTheoryState() {
    // Сначала загружаем предметы
    loadTheorySubjects();
    
    // Затем проверяем состояние для восстановления навигации
    fetch('/api/theory/state')
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                console.warn('Ошибка загрузки состояния:', data.error);
                return;
            }
            
            theoryState = {
                currentPage: data.current_page || 'subjects',
                selectedSubject: data.selected_subject,
                selectedSection: data.selected_section,
                selectedTopic: data.selected_topic
            };
            
            // Восстанавливаем навигацию если есть сохраненное состояние
            if (theoryState.currentPage === 'sections' && theoryState.selectedSubject) {
                loadTheorySections(theoryState.selectedSubject);
            } else if (theoryState.currentPage === 'topics' && theoryState.selectedSubject && theoryState.selectedSection) {
                loadTheoryTopics(theoryState.selectedSubject, theoryState.selectedSection);
            } else if (theoryState.currentPage === 'explanation' && theoryState.selectedSubject && theoryState.selectedSection && theoryState.selectedTopic) {
                loadExplanation(theoryState.selectedSubject, theoryState.selectedSection, theoryState.selectedTopic);
            }
        })
        .catch(err => {
            console.warn('Ошибка загрузки состояния:', err);
            // Игнорируем ошибку, предметы уже загружены
        });
}

function loadTheorySubjects() {
    showTheoryLoading(true);
    console.log('[Theory] Загрузка предметов...');
    fetch('/api/theory/subjects')
        .then(r => {
            console.log('[Theory] Ответ от /api/theory/subjects:', r.status);
            if (!r.ok) {
                throw new Error(`HTTP ${r.status}: ${r.statusText}`);
            }
            return r.json();
        })
        .then(data => {
            showTheoryLoading(false);
            console.log('[Theory] Данные предметов:', data);
            if (data.error) {
                console.error('[Theory] Ошибка API:', data.error);
                showTheoryError(data.error);
                return;
            }
            // Используем subjects_structure если есть, иначе subjects
            const subjectsData = data.subjects_structure || data.subjects || {};
            console.log('[Theory] Отображаем предметы:', Object.keys(subjectsData));
            if (Object.keys(subjectsData).length === 0) {
                showTheoryError('Предметы не найдены. Проверьте структуру данных.');
                return;
            }
            displayTheorySubjects(subjectsData);
        })
        .catch(err => {
            showTheoryLoading(false);
            console.error('[Theory] Ошибка загрузки предметов:', err);
            showTheoryError('Ошибка загрузки предметов: ' + err.message);
        });
}

function displayTheorySubjects(subjects) {
    const container = document.getElementById('subjects-list');
    if (!container) {
        console.error('[Theory] Контейнер subjects-list не найден!');
        return;
    }
    
    container.innerHTML = '';
    
    if (!subjects || typeof subjects !== 'object') {
        console.error('[Theory] Некорректные данные предметов:', subjects);
        showTheoryError('Ошибка: некорректные данные предметов');
        return;
    }
    
    const subjectsList = Object.keys(subjects);
    console.log('[Theory] Отображаем предметы:', subjectsList);
    
    if (subjectsList.length === 0) {
        console.warn('[Theory] Список предметов пуст');
        showTheoryError('Предметы не найдены');
        return;
    }
    
    subjectsList.forEach(subject => {
        const subjectData = subjects[subject];
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-3';
        
        const icon = (subjectData && subjectData.icon) ? subjectData.icon : '📚';
        
        // Создаем кнопку с обработчиком события
        const button = document.createElement('button');
        button.className = 'btn btn-outline-primary w-100 p-3';
        button.innerHTML = `<h5>${icon} ${subject}</h5>`;
        button.onclick = function() {
            console.log('[Theory] Клик по предмету:', subject);
            selectTheorySubject(subject);
        };
        
        col.appendChild(button);
        container.appendChild(col);
    });
    
    showTheoryPage('subjects');
    updateTheoryBreadcrumbs(['Предметы']);
}

function selectTheorySubject(subject) {
    console.log('[Theory] Выбран предмет:', subject);
    theoryState.selectedSubject = subject;
    theoryState.currentPage = 'sections';
    loadTheorySections(subject);
}

function loadTheorySections(subject) {
    showTheoryLoading(true);
    console.log('[Theory] Загрузка разделов для предмета:', subject);
    const url = `/api/theory/sections?subject=${encodeURIComponent(subject)}`;
    console.log('[Theory] URL запроса:', url);
    fetch(url)
        .then(r => {
            console.log('[Theory] Ответ от /api/theory/sections:', r.status);
            if (!r.ok) {
                throw new Error(`HTTP ${r.status}: ${r.statusText}`);
            }
            return r.json();
        })
        .then(data => {
            showTheoryLoading(false);
            console.log('[Theory] Данные разделов:', data);
            if (data.error) {
                console.error('[Theory] Ошибка API:', data.error);
                showTheoryError(data.error);
                return;
            }
            const sections = data.sections || {};
            console.log('[Theory] Отображаем разделы:', Object.keys(sections));
            if (Object.keys(sections).length === 0) {
                showTheoryError('Разделы не найдены для предмета: ' + subject);
                return;
            }
            displayTheorySections(subject, sections);
        })
        .catch(err => {
            showTheoryLoading(false);
            console.error('[Theory] Ошибка загрузки разделов:', err);
            showTheoryError('Ошибка загрузки разделов: ' + err.message);
        });
}

function displayTheorySections(subject, sections) {
    const title = document.getElementById('sections-title');
    const list = document.getElementById('sections-list');
    
    title.textContent = `📚 ${subject} - Выберите раздел:`;
    list.innerHTML = '';
    
    Object.keys(sections).forEach(section => {
        const item = document.createElement('a');
        item.href = '#';
        item.className = 'list-group-item list-group-item-action';
        item.innerHTML = `📖 ${section}`;
        item.onclick = (e) => {
            e.preventDefault();
            selectTheorySection(subject, section);
        };
        list.appendChild(item);
    });
    
    showTheoryPage('sections');
    updateTheoryBreadcrumbs(['Предметы', subject]);
}

function selectTheorySection(subject, section) {
    theoryState.selectedSection = section;
    theoryState.currentPage = 'topics';
    loadTheoryTopics(subject, section);
}

function loadTheoryTopics(subject, section) {
    showTheoryLoading(true);
    fetch(`/api/theory/topics?subject=${encodeURIComponent(subject)}&section=${encodeURIComponent(section)}`)
        .then(r => r.json())
        .then(data => {
            showTheoryLoading(false);
            if (data.error) {
                showTheoryError(data.error);
                return;
            }
            displayTheoryTopics(subject, section, data.topics || []);
        })
        .catch(err => {
            showTheoryLoading(false);
            showTheoryError('Ошибка загрузки тем: ' + err);
        });
}

function displayTheoryTopics(subject, section, topics) {
    const title = document.getElementById('topics-title');
    const list = document.getElementById('topics-list');
    
    title.textContent = `📚 ${subject} → ${section} - Выберите тему:`;
    list.innerHTML = '';
    
    topics.forEach(topic => {
        const item = document.createElement('a');
        item.href = '#';
        item.className = 'list-group-item list-group-item-action';
        item.innerHTML = `🎯 ${topic}`;
        item.onclick = (e) => {
            e.preventDefault();
            selectTheoryTopic(subject, section, topic);
        };
        list.appendChild(item);
    });
    
    showTheoryPage('topics');
    updateTheoryBreadcrumbs(['Предметы', subject, section]);
}

function selectTheoryTopic(subject, section, topic) {
    theoryState.selectedTopic = topic;
    theoryState.currentPage = 'explanation';
    loadExplanation(subject, section, topic);
}

function loadExplanation(subject, section, topic, regenerate = false) {
    const title = document.getElementById('explanation-title');
    const loading = document.getElementById('explanation-loading');
    const text = document.getElementById('explanation-text');
    
    title.textContent = `📚 ${subject} → ${section} → ${topic}`;
    loading.style.display = 'block';
    text.style.display = 'none';
    
    showTheoryPage('explanation');
    updateTheoryBreadcrumbs(['Предметы', subject, section, topic]);
    
    fetch('/api/theory/explanation', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({subject, section, topic, regenerate})
    })
    .then(r => r.json())
    .then(data => {
        loading.style.display = 'none';
        if (data.error) {
            showTheoryError(data.error);
            return;
        }
        
        text.innerHTML = data.explanation || 'Объяснение не сгенерировано';
        text.style.display = 'block';
    })
    .catch(err => {
        loading.style.display = 'none';
        showTheoryError('Ошибка генерации объяснения: ' + err);
    });
}

function regenerateExplanation() {
    if (theoryState.selectedSubject && theoryState.selectedSection && theoryState.selectedTopic) {
        loadExplanation(theoryState.selectedSubject, theoryState.selectedSection, theoryState.selectedTopic, true);
    }
}

function theoryNavigate(page) {
    if (page === 'subjects') {
        theoryState = {currentPage: 'subjects', selectedSubject: null, selectedSection: null, selectedTopic: null};
        loadTheorySubjects();
    } else if (page === 'sections' && theoryState.selectedSubject) {
        theoryState.currentPage = 'sections';
        loadTheorySections(theoryState.selectedSubject);
    } else if (page === 'topics' && theoryState.selectedSubject && theoryState.selectedSection) {
        theoryState.currentPage = 'topics';
        loadTheoryTopics(theoryState.selectedSubject, theoryState.selectedSection);
    }
}

function showTheoryPage(page) {
    document.querySelectorAll('.theory-page').forEach(p => p.style.display = 'none');
    document.getElementById(`theory-${page}`).style.display = 'block';
    theoryState.currentPage = page;
}

function updateTheoryBreadcrumbs(items) {
    const breadcrumbs = document.getElementById('theory-breadcrumbs');
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
                if (index === 0) theoryNavigate('subjects');
                else if (index === 1) theoryNavigate('sections');
                else if (index === 2) theoryNavigate('topics');
            };
            li.appendChild(a);
        } else {
            li.textContent = item;
        }
        ol.appendChild(li);
    });
    
    breadcrumbs.style.display = items.length > 1 ? 'block' : 'none';
}

function showTheoryLoading(show) {
    document.getElementById('theory-loading').style.display = show ? 'block' : 'none';
}

function showTheoryError(message) {
    const errorDiv = document.getElementById('theory-error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

