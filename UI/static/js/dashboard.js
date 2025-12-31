// Управление вкладками дашборда
function showTab(tabName) {
    // Скрыть все вкладки
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    // Убрать active со всех кнопок
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Показать выбранную вкладку
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    
    // Обновить URL без перезагрузки страницы
    const url = new URL(window.location);
    url.searchParams.set('tab', tabName);
    window.history.pushState({}, '', url);
    
    // Инициализация специфичных вкладок
    if (tabName === 'assignments') {
        if (typeof initAssignments === 'function') initAssignments();
    } else if (tabName === 'settings') {
        if (typeof initSettings === 'function') initSettings();
    } else if (tabName === 'theory') {
        // Инициализация теории при открытии вкладки
        setTimeout(() => {
            if (typeof loadTheoryState === 'function') {
                console.log('[Dashboard] Инициализация теории...');
                loadTheoryState();
            } else if (typeof loadSubjects === 'function') {
                console.log('[Dashboard] Загрузка предметов...');
                loadSubjects();
            } else {
                console.warn('[Dashboard] Функции теории не найдены');
            }
        }, 100);
    } else if (tabName === 'testing') {
        // Инициализация тестирования при открытии вкладки
        setTimeout(() => {
            if (typeof loadTestingState === 'function') {
                console.log('[Dashboard] Инициализация тестирования...');
                loadTestingState();
            } else if (typeof loadTestingSubjects === 'function') {
                console.log('[Dashboard] Загрузка предметов тестирования...');
                loadTestingSubjects();
            } else {
                console.warn('[Dashboard] Функции тестирования не найдены');
            }
        }, 100);
    }
}

