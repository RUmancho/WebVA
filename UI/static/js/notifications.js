// Уведомления
function loadNotifications() {
    fetch('/api/dashboard/notifications')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('notificationsContent');
            let html = '';
            
            if (data.unread_count > 0) {
                html += `<div class="alert alert-info">📬 У вас ${data.unread_count} непрочитанных уведомлений</div>`;
            }
            
            html += '<div class="form-check mb-3">';
            html += '<input class="form-check-input" type="checkbox" id="showAll" checked onchange="filterNotifications()">';
            html += '<label class="form-check-label" for="showAll">Показать все уведомления</label>';
            html += '</div>';
            
            if (!data.notifications || data.notifications.length === 0) {
                html += '<div class="alert alert-info">У вас пока нет уведомлений</div>';
            } else {
                data.notifications.forEach(notification => {
                    const icon = notification.is_read ? '✅' : '🔴';
                    html += `<div class="card mb-2">
                        <div class="card-body">
                            <h5>${icon} ${notification.title} - ${notification.created_at}</h5>
                            <p>${notification.message}</p>`;
                    if (!notification.is_read) {
                        html += `<button class="btn btn-sm btn-primary" onclick="markAsRead(${notification.id})">Отметить как прочитанное</button>`;
                    }
                    html += '</div></div>';
                });
            }
            
            container.innerHTML = html;
        })
        .catch(error => {
            console.error('Ошибка загрузки уведомлений:', error);
            document.getElementById('notificationsContent').innerHTML = '<div class="alert alert-danger">Ошибка загрузки данных</div>';
        });
}

function markAsRead(notificationId) {
    fetch(`/api/dashboard/notifications/${notificationId}/read`, {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadNotifications();
            } else {
                alert('Ошибка: ' + data.message);
            }
        });
}

function filterNotifications() {
    const showAll = document.getElementById('showAll').checked;
    loadNotifications();
}

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('notifications') && document.getElementById('notifications').classList.contains('active')) {
        loadNotifications();
    }
    
    const notificationsTab = document.querySelector('button[onclick="showTab(\'notifications\')"]');
    if (notificationsTab) {
        notificationsTab.addEventListener('click', function() {
            setTimeout(loadNotifications, 100);
        });
    }
});

