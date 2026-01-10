// Калькулятор формул
let formulasState = {
    currentCategory: null,
    currentSubcategory: null,
    categories: {},
    formulas: []
};

function loadFormulas() {
    showFormulasLoading(true);
    fetch('/api/formulas/categories')
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                showFormulasError(data.error);
                return;
            }
            formulasState.categories = data.categories || {};
            if (data.current_category) {
                formulasState.currentCategory = data.current_category;
                loadSubcategories();
            }
        })
        .catch(err => showFormulasError('Ошибка загрузки: ' + err))
        .finally(() => showFormulasLoading(false));
}

function selectCategory(category) {
    showFormulasLoading(true);
    fetch('/api/formulas/select-category', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({category: category})
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            showFormulasError(data.error);
            return;
        }
        formulasState.currentCategory = category;
        displaySubcategories(data);
    })
    .catch(err => showFormulasError('Ошибка: ' + err))
    .finally(() => showFormulasLoading(false));
}

function displaySubcategories(data) {
    document.getElementById('formulas-categories').style.display = 'none';
    document.getElementById('formulas-subcategories').style.display = 'block';
    document.getElementById('category-title').textContent = data.category || formulasState.currentCategory;
    
    const select = document.getElementById('subcategory-select');
    select.innerHTML = '<option value="">-- Выберите раздел --</option>';
    
    if (data.subcategories) {
        data.subcategories.forEach(sub => {
            const option = document.createElement('option');
            option.value = sub;
            option.textContent = sub;
            if (sub === data.current_subcategory) {
                option.selected = true;
            }
            select.appendChild(option);
        });
    }
    
    if (data.current_subcategory) {
        formulasState.currentSubcategory = data.current_subcategory;
        // formulas может быть объектом или массивом
        let formulasData = data.formulas || {};
        if (typeof formulasData === 'object' && !Array.isArray(formulasData)) {
            // Преобразуем объект в массив
            formulasData = Object.values(formulasData);
        }
        displayFormulas(formulasData);
    } else {
        document.getElementById('formulas-list').innerHTML = '';
    }
}

function selectSubcategory(subcategory) {
    if (!subcategory) return;
    
    showFormulasLoading(true);
    fetch('/api/formulas/select-subcategory', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({subcategory: subcategory})
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            showFormulasError(data.error);
            return;
        }
        formulasState.currentSubcategory = subcategory;
        // Преобразуем formulas в массив если нужно
        let formulasData = data.formulas || {};
        if (typeof formulasData === 'object' && !Array.isArray(formulasData)) {
            formulasData = Object.values(formulasData);
        }
        displayFormulas(formulasData);
    })
    .catch(err => showFormulasError('Ошибка: ' + err))
    .finally(() => showFormulasLoading(false));
}

function displayFormulas(formulas) {
    const container = document.getElementById('formulas-list');
    
    // Преобразуем в массив если нужно
    let formulasArray = Array.isArray(formulas) ? formulas : (formulas ? Object.values(formulas) : []);
    
    if (!formulasArray || formulasArray.length === 0) {
        container.innerHTML = '<div class="alert alert-info">Формулы для этой подкатегории пока не добавлены.</div>';
        return;
    }
    
    formulasState.formulas = formulasArray;
    container.innerHTML = '';
    formulasArray.forEach((formula, index) => {
        const card = document.createElement('div');
        card.className = 'formula-card';
        
        // Заменяем символы для правильного отображения
        const displayFormula = formula.formula
            .replace(/π/g, '&pi;')  // Греческая пи
            .replace(/×/g, '&times;')  // Знак умножения
            .replace(/²/g, '&sup2;')   // Степень 2
            .replace(/³/g, '&sup3;');  // Степень 3
        
        card.innerHTML = `
            <div class="formula-title">
                🧮 ${formula.name}
            </div>
            <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 2px solid #667eea;">
                <h4 style="color: #667eea; text-align: center; font-family: 'Courier New', monospace; font-size: 1.5rem;">
                    ${displayFormula}
                </h4>
            </div>
            
            <div style="background: rgba(255,255,255,0.8); padding: 20px; border-radius: 10px; margin-bottom: 15px;">
                <p style="font-weight: 600; margin-bottom: 15px; font-size: 1.1rem;">📝 Введите известные значения (оставьте пустым то, что нужно найти):</p>
                <div id="formula-inputs-${index}"></div>
            </div>
            
            <button class="btn calculate-btn mt-3" onclick="calculateFormula(${index}, '${formula.name}', '${formulasState.currentCategory}', '${formulasState.currentSubcategory}')">
                🧮 ВЫЧИСЛИТЬ
            </button>
            <div id="formula-result-${index}" class="mt-3"></div>
        `;
        container.appendChild(card);
        
        // Создаем поля ввода для всех переменных
        const inputs = document.getElementById(`formula-inputs-${index}`);
        formula.fields.forEach((field, fieldIndex) => {
            const [fieldId, fieldName, unit] = field;
            const div = document.createElement('div');
            div.className = 'mb-3';
            div.innerHTML = `
                <label for="input-${index}-${fieldId}" class="form-label" style="font-weight: 600;">
                    ${fieldName}${unit ? ' [' + unit + ']' : ''}
                </label>
                <input type="number" class="form-control" id="input-${index}-${fieldId}" 
                       step="0.0001" placeholder="Оставьте пустым, если это искомая величина" data-field-id="${fieldId}"
                       style="height: 50px; border-radius: 10px; border: 2px solid #dee2e6; font-size: 1.1rem;">
            `;
            inputs.appendChild(div);
        });
    });
}

function calculateFormula(index, formulaName, category, subcategory) {
    const inputs = document.querySelectorAll(`#formula-inputs-${index} input`);
    const values = {};
    let emptyFields = [];
    
    // Собираем значения и находим пустые поля
    inputs.forEach(input => {
        const fieldId = input.dataset.fieldId;
        if (input.value && input.value.trim() !== '') {
            values[fieldId] = parseFloat(input.value);
        } else {
            emptyFields.push({
                id: fieldId,
                name: input.previousElementSibling.textContent.trim()
            });
        }
    });
    
    // Проверяем, что пустое ровно одно поле (искомая величина)
    if (emptyFields.length === 0) {
        alert('⚠️ Пожалуйста, оставьте пустым поле с искомой величиной!');
        return;
    }
    
    if (emptyFields.length > 1) {
        alert('⚠️ Заполните все известные значения! Пустым должно остаться только одно поле (искомая величина).');
        return;
    }
    
    // Искомая величина - это единственное пустое поле
    const target = emptyFields[0].id;
    const targetName = emptyFields[0].name;
    
    // Проверяем, что все остальные поля заполнены
    const formula = formulasState.formulas[index];
    const requiredFields = formula.fields.filter(f => f[0] !== target);
    if (requiredFields.length !== Object.keys(values).length) {
        alert('⚠️ Пожалуйста, заполните все известные значения');
        return;
    }
    
    showFormulasLoading(true);
    fetch('/api/formulas/calculate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            formula_name: formulaName,
            category: category,
            subcategory: subcategory,
            values: values,
            target: target
        })
    })
    .then(r => r.json())
    .then(data => {
        const resultDiv = document.getElementById(`formula-result-${index}`);
        if (data.error) {
            resultDiv.innerHTML = `<div class="result-error">❌ <strong>Ошибка:</strong> ${data.error}</div>`;
        } else if (data.success) {
            const fieldInfo = formula.fields.find(f => f[0] === target);
            const fieldName = fieldInfo[1];
            const unit = fieldInfo[2];
            resultDiv.innerHTML = `
                <div class="result-success">
                    ✅ <strong>Результат:</strong><br>
                    <div style="font-size: 1.5rem; margin-top: 10px;">
                        ${fieldName} = <strong>${data.result.toFixed(4)}</strong>${unit ? ' ' + unit : ''}
                    </div>
                </div>
            `;
        }
    })
    .catch(err => {
        document.getElementById(`formula-result-${index}`).innerHTML = 
            `<div class="alert alert-danger">❌ Ошибка: ${err}</div>`;
    })
    .finally(() => showFormulasLoading(false));
}

function resetFormulas() {
    formulasState.currentCategory = null;
    formulasState.currentSubcategory = null;
    document.getElementById('formulas-categories').style.display = 'block';
    document.getElementById('formulas-subcategories').style.display = 'none';
    document.getElementById('formulas-list').innerHTML = '';
}

function showFormulasLoading(show) {
    document.getElementById('formulas-loading').style.display = show ? 'block' : 'none';
}

function showFormulasError(message) {
    const errorDiv = document.getElementById('formulas-error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// Загружаем формулы при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    loadFormulas();
});

