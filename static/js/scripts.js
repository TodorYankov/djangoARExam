// static/js/scripts.js - TechShop Оптимизиран JavaScript

/* ========== UTILITY ФУНКЦИИ ========== */
const U = {
    isMob: () => /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent),
    capitalize: s => s ? s.toLowerCase().replace(/\b\w/g, c => c.toUpperCase()) : '',
    formatPhone: v => {
        v = v.replace(/\D/g, '');
        if (!v) return '';
        if (v.length <= 3) return v;
        if (v.length <= 6) return `${v.slice(0, 3)} ${v.slice(3)}`;
        return `${v.slice(0, 3)} ${v.slice(3, 6)} ${v.slice(6, 10)}`;
    },
    alert: (msg, type = 'info') => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        alertDiv.style.cssText = 'z-index: 9999; max-width: 350px;';
        alertDiv.innerHTML = `${msg}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
        document.body.appendChild(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
    },
    confirm: msg => confirm(msg || 'Сигурни ли сте?'),
    debounce: (func, delay) => {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func(...args), delay);
        };
    }
};

/* ========== ОБЩИ ФУНКЦИИ ========== */
const Common = {
    initScrollAnimation() {
        const elements = document.querySelectorAll('.fade-in, .category-card, .order-row, .stats-card');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        elements.forEach(el => observer.observe(el));
    },

    initDeleteConfirmation() {
        document.querySelectorAll('.btn-delete, .delete-btn, [data-confirm]').forEach(btn => {
            btn.addEventListener('click', e => {
                const message = btn.dataset.confirm || btn.dataset.name ?
                    `Сигурни ли сте, че искате да изтриете "${btn.dataset.name || 'този елемент'}"?` :
                    'Сигурни ли сте?';
                if (!U.confirm(message)) {
                    e.preventDefault();
                    return false;
                }
            });
        });
    },

    initPasswordToggle() {
        document.querySelectorAll('.toggle-password').forEach(btn => {
            btn.addEventListener('click', function() {
                const input = document.getElementById(this.dataset.target || 'id_password');
                if (input) {
                    const type = input.type === 'password' ? 'text' : 'password';
                    input.type = type;
                    this.classList.toggle('fa-eye-slash');
                }
            });
        });
    },

    initAutoCloseAlerts() {
        setTimeout(() => {
            document.querySelectorAll('.alert').forEach(alert => {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            });
        }, 5000);
    },

    initActiveNav() {
        const currentPath = window.location.pathname;
        document.querySelectorAll('.nav-link').forEach(link => {
            const href = link.getAttribute('href');
            if (href && href !== '#' && currentPath === href) {
                link.classList.add('active');
            }
        });
    }
};

/* ========== ФОРМУЛЯРИ ========== */
const Forms = {
    validateField(field) {
        const value = field.value.trim();
        field.classList.remove('is-invalid');

        const oldError = field.parentNode?.querySelector('.error-message');
        if (oldError) oldError.remove();

        if (field.hasAttribute('required') && !value) {
            this.showError(field, 'Това поле е задължително');
            return false;
        }

        if (field.type === 'email' && value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
            this.showError(field, 'Моля, въведете валиден имейл адрес');
            return false;
        }

        if (field.name.includes('phone') && value && !/^[\+]?[0-9\s\-\(\)]{10,15}$/.test(value.replace(/\s/g, ''))) {
            this.showError(field, 'Моля, въведете валиден телефонен номер');
            return false;
        }

        if (field.name.includes('price') && value && parseFloat(value) <= 0) {
            this.showError(field, 'Цената трябва да е положително число');
            return false;
        }

        if (field.name.includes('stock') && value && parseInt(value) < 0) {
            this.showError(field, 'Наличността не може да бъде отрицателна');
            return false;
        }

        return true;
    },

    showError(field, message) {
        field.classList.add('is-invalid');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message text-danger small mt-1';
        errorDiv.textContent = message;
        field.parentNode?.appendChild(errorDiv);
    },

    clearErrors(form) {
        form.querySelectorAll('.is-invalid').forEach(f => f.classList.remove('is-invalid'));
        form.querySelectorAll('.error-message').forEach(e => e.remove());
    },

    initFormValidation(formId) {
        const form = document.getElementById(formId);
        if (!form) return;

        form.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('blur', () => this.validateField(field));
            field.addEventListener('input', () => {
                if (field.classList.contains('is-invalid')) {
                    this.validateField(field);
                }
            });
        });

        form.addEventListener('submit', (e) => {
            let isValid = true;
            this.clearErrors(form);

            form.querySelectorAll('input[required], select[required], textarea[required], input[name*="price"], input[name*="stock"]').forEach(field => {
                if (!this.validateField(field)) isValid = false;
            });

            if (!isValid) {
                e.preventDefault();
                U.alert('Моля, поправете грешките във формата', 'warning');
            }
        });
    }
};

/* ========== ПРОДУКТИ ========== */
const Products = {
    init() {
        const imageInput = document.getElementById('id_image') || document.getElementById('id_profile_picture');
        if (imageInput) {
            imageInput.addEventListener('change', e => {
                const file = e.target.files[0];
                if (!file) return;

                const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
                if (!validTypes.includes(file.type)) {
                    U.alert('Моля, качете валидно изображение (JPG, PNG, GIF, WebP)', 'danger');
                    imageInput.value = '';
                    return;
                }

                if (file.size > 5 * 1024 * 1024) {
                    U.alert('Снимката е твърде голяма! Максимален размер: 5MB', 'danger');
                    imageInput.value = '';
                    return;
                }

                const reader = new FileReader();
                reader.onload = e => {
                    let preview = document.getElementById('image-preview');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.id = 'image-preview';
                        preview.classList.add('image-preview');
                        imageInput.parentNode.appendChild(preview);
                    }
                    preview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            });
        }

        Forms.initFormValidation('productForm');
    }
};

/* ========== ПОРЪЧКИ ========== */
const Orders = {
    init() {
        const statusFilter = document.getElementById('statusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', function() {
                const url = new URL(window.location.href);
                if (this.value) {
                    url.searchParams.set('status', this.value);
                } else {
                    url.searchParams.delete('status');
                }
                window.location.href = url.toString();
            });
        }

        document.querySelectorAll('.order-row').forEach(row => {
            row.style.cursor = 'pointer';
            row.addEventListener('click', e => {
                if (!e.target.closest('button, a')) {
                    const orderId = row.dataset.orderId;
                    if (orderId) window.location.href = `/orders/${orderId}/`;
                }
            });
        });

        this.initOrderFormset();
        Forms.initFormValidation('orderForm');
    },

    initOrderFormset() {
        const addButton = document.getElementById('add-item');
        if (!addButton) return;

        addButton.addEventListener('click', e => {
            e.preventDefault();

            const formset = document.getElementById('item-formset');
            const totalForms = document.getElementById('id_items-TOTAL_FORMS');
            const emptyTemplate = document.getElementById('item-formset-empty');

            if (!formset || !totalForms || !emptyTemplate) return;

            const formCount = parseInt(totalForms.value);
            const newRow = emptyTemplate.cloneNode(true);
            newRow.id = '';
            newRow.style.display = '';
            newRow.innerHTML = newRow.innerHTML.replace(/__prefix__/g, formCount);

            formset.querySelector('tbody').appendChild(newRow);
            totalForms.value = formCount + 1;
        });

        document.addEventListener('click', e => {
            const deleteBtn = e.target.closest('.delete-row');
            if (deleteBtn) {
                e.preventDefault();
                const row = deleteBtn.closest('tr');
                if (row) {
                    row.remove();
                    const totalForms = document.getElementById('id_items-TOTAL_FORMS');
                    const tbody = document.querySelector('#item-formset tbody');
                    if (totalForms && tbody) totalForms.value = tbody.children.length;
                }
            }
        });
    }
};

/* ========== ПОТРЕБИТЕЛИ ========== */
const Accounts = {
    init() {
        // Форматиране на телефон при въвеждане
        const phoneInput = document.querySelector('input[name="phone_number"]');
        if (phoneInput) {
            phoneInput.addEventListener('input', e => {
                e.target.value = U.formatPhone(e.target.value);
            });
        }

        // Валидация на регистрационна форма
        Forms.initFormValidation('registerForm');
        Forms.initFormValidation('profileEditForm');

        // Потвърждение при изтриване на профил
        const deleteProfileBtn = document.querySelector('a[href*="profile_delete"]');
        if (deleteProfileBtn) {
            deleteProfileBtn.addEventListener('click', e => {
                if (!U.confirm('Сигурни ли сте, че искате да изтриете профила си? Това действие е необратимо!')) {
                    e.preventDefault();
                }
            });
        }

        // Инициализация на password toggle за профила
        Common.initPasswordToggle();
    }
};

/* ========== SCROLL TO TOP ========== */
const ScrollToTop = {
    init() {
        const btn = document.createElement('button');
        btn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        btn.className = 'scroll-to-top';
        document.body.appendChild(btn);

        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                btn.classList.add('visible');
            } else {
                btn.classList.remove('visible');
            }
        });

        btn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
};

/* ========== ИНИЦИАЛИЗАЦИЯ ========== */
function initAll() {
    // Общи функционалности (винаги)
    Common.initScrollAnimation();
    Common.initDeleteConfirmation();
    Common.initAutoCloseAlerts();
    Common.initActiveNav();

    // Password toggle (общ, но ще се инициализира и в Accounts)
    Common.initPasswordToggle();

    const path = window.location.pathname;

    // Специфични за страници
    if (path.includes('product') || path.includes('product_form')) {
        Products.init();
    }

    if (path.includes('orders')) {
        Orders.init();
    }

    if (path.includes('account') || path.includes('profile') || path.includes('register')) {
        Accounts.init();
    }

    // Scroll to top (винаги)
    ScrollToTop.init();
}

// Стартиране при зареждане на страницата
document.addEventListener('DOMContentLoaded', initAll);




