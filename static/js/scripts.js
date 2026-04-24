// static/js/scripts.js - TechShop Optimized JavaScript

/* ========== UTILITY FUNCTIONS ========== */
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

/* ========== COMMON FUNCTIONS ========== */
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

/* ========== FORMS ========== */
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

/* ========== CART FUNCTIONS ========== */

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Update quantity
function updateQuantity(productId, newQuantity) {
    const row = document.querySelector(`.cart-item[data-product-id="${productId}"]`);
    if (!row) return;

    const input = row.querySelector('.quantity-input');
    const spinner = row.querySelector('.loading-spinner');
    const decreaseBtn = row.querySelector('.btn-decrease');
    const increaseBtn = row.querySelector('.btn-increase');

    if (spinner) spinner.style.display = 'inline-block';
    if (decreaseBtn) decreaseBtn.disabled = true;
    if (increaseBtn) increaseBtn.disabled = true;
    if (input) input.disabled = true;

    fetch(`/orders/cart/update/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `quantity=${newQuantity}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (input) {
                input.value = data.quantity;
                input.defaultValue = data.quantity;
            }

            const price = parseFloat(row.dataset.price);
            const itemTotal = price * data.quantity;
            const subtotalElement = row.querySelector('.item-subtotal');
            if (subtotalElement) {
                subtotalElement.textContent = itemTotal.toFixed(2) + ' €';
            }

            updateCartSummary();
            updateCartCount();
            showMessage('Количеството беше обновено успешно', 'success');
        } else {
            showMessage('Грешка: ' + (data.error || 'Неуспешна актуализация'), 'danger');
            if (input) input.value = input.defaultValue;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Възникна грешка. Моля, опитайте отново.', 'danger');
        if (input) input.value = input.defaultValue;
    })
    .finally(() => {
        if (spinner) spinner.style.display = 'none';
        if (decreaseBtn) decreaseBtn.disabled = false;
        if (increaseBtn) increaseBtn.disabled = false;
        if (input) input.disabled = false;
    });
}

// Remove from cart
function removeFromCart(productId) {
    if (!confirm('Сигурни ли сте, че искате да премахнете този продукт?')) return;

    fetch(`/orders/cart/remove/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const row = document.querySelector(`.cart-item[data-product-id="${productId}"]`);
            if (row) row.remove();
            updateCartSummary();
            updateCartCount();

            if (document.querySelectorAll('.cart-item').length === 0) {
                location.reload();
            }
            showMessage('Продуктът беше премахнат от количката', 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Грешка при премахване на продукта', 'danger');
    });
}

// Update cart summary
function updateCartSummary() {
    const items = document.querySelectorAll('.cart-item');
    let totalQuantity = 0;
    let totalAmount = 0;

    items.forEach(item => {
        const quantity = parseInt(item.querySelector('.quantity-input')?.value || 0);
        const price = parseFloat(item.dataset.price || 0);
        totalQuantity += quantity;
        totalAmount += price * quantity;
    });

    const itemsCountElem = document.getElementById('summary-items-count');
    const totalQuantityElem = document.getElementById('summary-total-quantity');
    const cartTotalElem = document.getElementById('cart-total');

    if (itemsCountElem) itemsCountElem.textContent = items.length;
    if (totalQuantityElem) totalQuantityElem.textContent = totalQuantity;
    if (cartTotalElem) cartTotalElem.textContent = totalAmount.toFixed(2) + ' €';

    const shippingMsg = document.getElementById('shipping-message');
    if (shippingMsg && totalAmount < 100) {
        shippingMsg.innerHTML = `
            <div class="alert alert-info small mb-3">
                <i class="fas fa-truck me-2"></i>
                Добавете още <strong>${(100 - totalAmount).toFixed(2)} €</strong> за безплатна доставка!
            </div>
        `;
    } else if (shippingMsg && totalAmount >= 100) {
        shippingMsg.innerHTML = `
            <div class="alert alert-success small mb-3">
                <i class="fas fa-truck me-2"></i>
                Безплатна доставка! 🎉
            </div>
        `;
    }
}

// Show message
function showMessage(message, type) {
    let msgDiv = document.querySelector('.floating-message');
    if (msgDiv) msgDiv.remove();

    msgDiv = document.createElement('div');
    msgDiv.className = `floating-message alert alert-${type} alert-dismissible fade show`;
    msgDiv.style.position = 'fixed';
    msgDiv.style.top = '20px';
    msgDiv.style.right = '20px';
    msgDiv.style.zIndex = '9999';
    msgDiv.style.minWidth = '300px';
    msgDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(msgDiv);

    setTimeout(() => msgDiv.remove(), 3000);
}

// Initialize cart handlers
function initCartHandlers() {
    if (!window.location.pathname.includes('/orders/cart/')) return;

    document.querySelectorAll('.btn-increase').forEach(btn => {
        btn.removeEventListener('click', handleIncrease);
        btn.addEventListener('click', handleIncrease);
    });

    document.querySelectorAll('.btn-decrease').forEach(btn => {
        btn.removeEventListener('click', handleDecrease);
        btn.addEventListener('click', handleDecrease);
    });

    document.querySelectorAll('.quantity-input').forEach(input => {
        input.removeEventListener('change', handleQuantityChange);
        input.addEventListener('change', handleQuantityChange);
    });

    document.querySelectorAll('.btn-remove').forEach(btn => {
        btn.removeEventListener('click', handleRemove);
        btn.addEventListener('click', handleRemove);
    });
}

// Handler functions
function handleIncrease(e) {
    const productId = parseInt(this.dataset.id);
    const input = document.querySelector(`.quantity-input[data-id="${productId}"]`);
    if (input) {
        const newValue = parseInt(input.value) + 1;
        updateQuantity(productId, newValue);
    }
}

function handleDecrease(e) {
    const productId = parseInt(this.dataset.id);
    const input = document.querySelector(`.quantity-input[data-id="${productId}"]`);
    if (input && parseInt(input.value) > 1) {
        const newValue = parseInt(input.value) - 1;
        updateQuantity(productId, newValue);
    }
}

function handleQuantityChange(e) {
    const productId = parseInt(this.dataset.id);
    let newValue = parseInt(this.value);
    if (isNaN(newValue) || newValue < 1) newValue = 1;
    if (newValue > 99) newValue = 99;
    updateQuantity(productId, newValue);
}

function handleRemove(e) {
    const productId = parseInt(this.dataset.id);
    removeFromCart(productId);
}

// Update cart count in navbar
function updateCartCount() {
    fetch('/orders/cart/api/')
        .then(response => response.json())
        .then(data => {
            const cartCountElement = document.getElementById('cart-count');
            if (cartCountElement) {
                if (data.cart_count > 0) {
                    cartCountElement.textContent = data.cart_count;
                    cartCountElement.style.display = 'inline-block';
                } else {
                    cartCountElement.style.display = 'none';
                }
            }
        })
        .catch(error => console.error('Грешка при обновяване на количката:', error));
}

/* ========== PRODUCTS ========== */
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

/* ========== ORDERS ========== */
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
                if (!e.target.closest('button, a, form, input, select, textarea')) {
                    const orderId = row.dataset.orderId;
                    if (orderId) window.location.href = `/orders/${orderId}/`;
                }
            });
        });

        this.initOrderFormset();
        Forms.initFormValidation('orderForm');
        initCartHandlers();
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

/* ========== ACCOUNTS ========== */
const Accounts = {
    init() {
        const phoneInput = document.querySelector('input[name="phone_number"]');
        if (phoneInput) {
            phoneInput.addEventListener('input', e => {
                e.target.value = U.formatPhone(e.target.value);
            });
        }

        Forms.initFormValidation('registerForm');
        Forms.initFormValidation('profileEditForm');

        const deleteProfileBtn = document.querySelector('a[href*="profile_delete"]');
        if (deleteProfileBtn) {
            deleteProfileBtn.addEventListener('click', e => {
                if (!U.confirm('Сигурни ли сте, че искате да изтриете профила си? Това действие е необратимо!')) {
                    e.preventDefault();
                }
            });
        }

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

/* ========== INITIALIZATION ========== */
function initAll() {
    Common.initScrollAnimation();
    Common.initDeleteConfirmation();
    Common.initAutoCloseAlerts();
    Common.initActiveNav();
    Common.initPasswordToggle();

    const path = window.location.pathname;

    if (path.includes('product') || path.includes('product_form')) {
        Products.init();
    }

    if (path.includes('orders')) {
        Orders.init();
    }

    if (path.includes('account') || path.includes('profile') || path.includes('register')) {
        Accounts.init();
    }

    ScrollToTop.init();
    updateCartCount();
}

document.addEventListener('DOMContentLoaded', initAll);
