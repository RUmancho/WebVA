// Регистрация
function toggleRoleFields() {
    const role = document.getElementById('role').value;
    const studentFields = document.getElementById('student_fields');
    const teacherFields = document.getElementById('teacher_fields');
    
    if (role === 'Ученик') {
        studentFields.style.display = 'block';
        teacherFields.style.display = 'none';
        // Делаем поля обязательными
        document.getElementById('city').required = true;
        document.getElementById('school').required = true;
        document.getElementById('class_number').required = true;
        document.getElementById('city_teacher').required = false;
        document.getElementById('school_teacher').required = false;
        document.getElementById('subjects').required = false;
    } else if (role === 'Учитель') {
        studentFields.style.display = 'none';
        teacherFields.style.display = 'block';
        // Делаем поля обязательными
        document.getElementById('city').required = false;
        document.getElementById('school').required = false;
        document.getElementById('class_number').required = false;
        document.getElementById('city_teacher').required = true;
        document.getElementById('school_teacher').required = true;
        document.getElementById('subjects').required = true;
    } else {
        studentFields.style.display = 'none';
        teacherFields.style.display = 'none';
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    toggleRoleFields();
});

