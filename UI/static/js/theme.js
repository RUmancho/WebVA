// Управление темой
const ThemeManager = {
    init() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
    },
    
    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Обновляем иконку
        const lightIcon = document.querySelector('.theme-icon-light');
        const darkIcon = document.querySelector('.theme-icon-dark');
        if (lightIcon && darkIcon) {
            if (theme === 'dark') {
                lightIcon.style.display = 'none';
                darkIcon.style.display = 'inline';
            } else {
                lightIcon.style.display = 'inline';
                darkIcon.style.display = 'none';
            }
        }
    },
    
    toggle() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
        
        // Сохраняем на сервере (если пользователь авторизован)
        fetch('/api/settings/theme', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({theme: newTheme})
        }).catch(e => console.log('Тема сохранена локально'));
    },
    
    getTheme() {
        return document.documentElement.getAttribute('data-theme');
    }
};

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
});

