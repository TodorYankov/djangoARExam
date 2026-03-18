// static/js/order_form.js
document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('add-item');

    if (addButton) {
        addButton.addEventListener('click', function(e) {
            e.preventDefault();

            // Намиране на formset елементите
            const formset = document.getElementById('item-formset');
            const totalForms = document.getElementById('id_items-TOTAL_FORMS');
            const emptyTemplate = document.getElementById('item-formset-empty');

            if (!formset || !totalForms || !emptyTemplate) return;

            // Текущ брой форми
            const formCount = parseInt(totalForms.value);

            // Клониране на шаблона
            const newRow = emptyTemplate.cloneNode(true);
            newRow.id = '';
            newRow.style.display = '';

            // Замяна на __prefix__ с текущия индекс
            newRow.innerHTML = newRow.innerHTML.replace(/__prefix__/g, formCount);

            // Добавяне на новия ред
            formset.querySelector('tbody').appendChild(newRow);

            // Актуализиране на броя форми
            totalForms.value = formCount + 1;
        });
    }

    // Функция за изтриване на ред
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('delete-row') ||
            e.target.closest('.delete-row')) {

            e.preventDefault();
            const row = e.target.closest('tr');
            if (row) {
                row.remove();

                // Актуализиране на TOTAL_FORMS
                const totalForms = document.getElementById('id_items-TOTAL_FORMS');
                const tbody = document.querySelector('#item-formset tbody');
                if (totalForms && tbody) {
                    totalForms.value = tbody.children.length;
                }
            }
        }
    });
});