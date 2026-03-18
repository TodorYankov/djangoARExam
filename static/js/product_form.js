// static/js/product_form.js

/**
 * Деактивира бутона за запис, ако няма категории
 */
function disableSubmitButton() {
    const submitBtn = document.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.classList.add('disabled', 'opacity-50');
        submitBtn.title = 'Първо трябва да създадете категория';
    }
}

/**
 * Предварителен преглед на снимката преди качване
 */
function setupImagePreview() {
    const imageInput = document.getElementById('id_image');
    if (!imageInput) return;

    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Проверка за тип на файла
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        if (!validTypes.includes(file.type)) {
            alert('Моля, качете снимка във формат JPG, JPEG или PNG!');
            this.value = ''; // Изчистване на полето
            return;
        }

        // Проверка за размер (макс 5MB)
        const maxSize = 5 * 1024 * 1024; // 5MB в байтове
        if (file.size > maxSize) {
            alert('Снимката е твърде голяма! Максимален размер: 5MB');
            this.value = ''; // Изчистване на полето
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            // Премахване на стария преглед ако съществува
            const oldPreview = document.getElementById('image-preview');
            if (oldPreview) {
                oldPreview.remove();
            }

            // Създаване на нов преглед
            const preview = document.createElement('img');
            preview.src = e.target.result;
            preview.id = 'image-preview';
            preview.alt = 'Преглед на снимка';
            preview.style.maxWidth = '200px';
            preview.style.maxHeight = '200px';
            preview.style.marginTop = '10px';
            preview.style.borderRadius = '5px';
            preview.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';

            // Добавяне на прегледа след полето за снимка
            imageInput.parentNode.appendChild(preview);
        }
        reader.readAsDataURL(file);
    });
}

/**
 * Валидация на формата преди изпращане
 */
function setupFormValidation() {
    const form = document.getElementById('productForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        const price = document.getElementById('id_price');
        const stock = document.getElementById('id_stock_quantity');

        if (price && parseFloat(price.value) <= 0) {
            e.preventDefault();
            alert('Цената трябва да бъде положително число!');
            price.focus();
            return;
        }

        if (stock && parseInt(stock.value) < 0) {
            e.preventDefault();
            alert('Наличността не може да бъде отрицателна!');
            stock.focus();
            return;
        }
    });
}

/**
 * Инициализация при зареждане на страницата
 */
document.addEventListener('DOMContentLoaded', function() {
    // Проверка дали има променлива no_categories (предадена от Django)
    if (typeof noCategories !== 'undefined' && noCategories) {
        disableSubmitButton();
    }

    setupImagePreview();
    setupFormValidation();
});