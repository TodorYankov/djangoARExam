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
        this.initAddToCartButtons();
    },

    initAddToCartButtons() {
        const addToCartButtons = document.querySelectorAll('.add-to-cart-btn, .add-to-cart-form');
        addToCartButtons.forEach(button => {
            if (button.classList.contains('add-to-cart-form')) {
                button.addEventListener('submit', function(e) {
                    e.preventDefault();
                    const productId = this.dataset.productId;
                    const quantity = this.querySelector('input[name="quantity"]')?.value || 1;
                    if (typeof addToCart === 'function') {
                        addToCart(productId, quantity);
                    }
                });
            } else if (button.classList.contains('add-to-cart-btn')) {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    const productId = this.dataset.productId;
                    const quantity = this.dataset.quantity || 1;
                    if (typeof addToCart === 'function') {
                        addToCart(productId, quantity);
                    }
                });
            }
        });
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
                if (!e.target.closest('button, a, form, input, select, textarea')) {
                    const orderId = row.dataset.orderId;
                    if (orderId) window.location.href = `/orders/${orderId}/`;
                }
            });
        });

        this.initOrderFormset();
        Forms.initFormValidation('orderForm');
        this.initCartHandlers();
        this.initOrderFormHandlers();
    },

    initOrderFormHandlers() {
        if (window.location.pathname.includes('/orders/create/')) {
            const shippingAddressField = document.querySelector('textarea[name="shipping_address"]');
            const phoneField = document.querySelector('input[name="guest_phone"]');

            if (shippingAddressField && phoneField) {
                const hasAddress = shippingAddressField.value.trim();
                const hasPhone = phoneField.value.trim();

                if (!hasAddress && !hasPhone) {
                    setTimeout(() => {
                        if (!document.getElementById('profileDataModal')) {
                            const modalHtml = `
                                <div class="modal fade" id="profileDataModal" tabindex="-1" data-bs-backdrop="static">
                                    <div class="modal-dialog modal-dialog-centered">
                                        <div class="modal-content">
                                            <div class="modal-header bg-warning">
                                                <h5 class="modal-title">
                                                    <i class="fas fa-info-circle me-2"></i>
                                                    За по-лесно пазаруване
                                                </h5>
                                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                            </div>
                                            <div class="modal-body">
                                                <div class="text-center mb-3">
                                                    <i class="fas fa-user-edit fa-4x text-warning"></i>
                                                </div>
                                                <p>За да улесните поръчките си в бъдеще, моля, попълнете в профила:</p>
                                                <ul class="list-unstyled">
                                                    <li class="mb-2">
                                                        <i class="fas fa-map-marker-alt text-primary me-2"></i>
                                                        <strong>Адрес за доставка</strong> - улица, номер, вход, етаж
                                                    </li>
                                                    <li class="mb-2">
                                                        <i class="fas fa-phone text-primary me-2"></i>
                                                        <strong>Телефон</strong> - за връзка при доставка
                                                    </li>
                                                </ul>
                                                <div class="alert alert-info small mt-3 mb-0">
                                                    <i class="fas fa-info-circle me-1"></i>
                                                    Можете да въведете данни директно в тази форма за текущата поръчка.
                                                </div>
                                            </div>
                                            <div class="modal-footer">
                                                <a href="/accounts/profile/" class="btn btn-warning">
                                                    <i class="fas fa-edit me-1"></i>
                                                    Към профила за попълване
                                                </a>
                                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                                    <i class="fas fa-times me-1"></i>
                                                    Затвори
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `;
                            document.body.insertAdjacentHTML('beforeend', modalHtml);

                            const modal = new bootstrap.Modal(document.getElementById('profileDataModal'));
                            modal.show();

                            localStorage.setItem('profileDataModalShown', 'true');
                        }
                    }, 1000);
                }
            }

            const phoneInput = document.querySelector('input[name="guest_phone"]');
            if (phoneInput) {
                phoneInput.addEventListener('input', function(e) {
                    let value = e.target.value.replace(/\D/g, '');
                    if (value.length > 0) {
                        if (value.length <= 3) {
                            value = value;
                        } else if (value.length <= 6) {
                            value = value.slice(0, 3) + ' ' + value.slice(3);
                        } else {
                            value = value.slice(0, 3) + ' ' + value.slice(3, 6) + ' ' + value.slice(6, 10);
                        }
                        e.target.value = value;
                    }
                });
            }

            const orderForm = document.getElementById('orderForm');
            if (orderForm) {
                orderForm.addEventListener('submit', function(e) {
                    const address = document.querySelector('textarea[name="shipping_address"]')?.value.trim();
                    const phone = document.querySelector('input[name="guest_phone"]')?.value.trim();

                    if (!address) {
                        e.preventDefault();
                        U.alert('Моля, въведете адрес за доставка.', 'warning');
                        document.querySelector('textarea[name="shipping_address"]')?.focus();
                        return false;
                    }

                    if (!phone) {
                        e.preventDefault();
                        U.alert('Моля, въведете телефон за връзка.', 'warning');
                        document.querySelector('input[name="guest_phone"]')?.focus();
                        return false;
                    }

                    // Вземи правилната обща сума
                    let totalText = '';
                    const orderTotal = document.getElementById('order-total');
                    if (orderTotal) {
                        totalText = orderTotal.innerText;
                    } else {
                        const summaryTotal = document.querySelector('.order-summary .text-primary.fw-bold');
                        totalText = summaryTotal ? summaryTotal.innerText : '';
                    }

                    if (U.confirm('Сигурни ли сте, че искате да потвърдите поръчката на стойност ' + totalText + '?')) {
                        return true;
                    }

                    e.preventDefault();
                    return false;
                });
            }
        }
    },

    initCartHandlers() {
        if (!window.location.pathname.includes('/orders/cart/')) return;

        const updateForms = document.querySelectorAll('.update-cart-form');
        updateForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();

                const productId = this.dataset.productId;
                const quantityInput = this.querySelector('input[name="quantity"]');
                const quantity = quantityInput ? quantityInput.value : 1;

                fetch(`/orders/cart/update/${productId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': cartConfig.csrfToken || window.djangoData?.csrfToken || '',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: new URLSearchParams({ quantity: quantity })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        updateCartCount();
                        if (window.location.pathname === '/orders/') {
                            fetchStatistics();
                        }
                        U.alert('Количеството беше обновено успешно.', 'success');
                    } else {
                        U.alert('Възникна грешка при обновяването.', 'danger');
                    }
                })
                .catch(error => {
                    console.error('Грешка при обновяване:', error);
                    U.alert('Възникна грешка. Моля, опитайте отново.', 'danger');
                });
            });
        });

        const removeForms = document.querySelectorAll('.remove-from-cart');
        removeForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();

                const productId = this.dataset.productId;
                if (!productId) {
                    console.error('Product ID not found!');
                    return;
                }

                if (U.confirm('Сигурни ли сте, че искате да премахнете този продукт?')) {
                    fetch(this.action, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': cartConfig.csrfToken || window.djangoData?.csrfToken || '',
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.success) {
                            updateCartCount();
                            if (window.location.pathname === '/orders/') {
                                fetchStatistics();
                            }
                            U.alert('Продуктът беше премахнат от количката.', 'success');
                        } else {
                            U.alert('Възникна грешка при премахване.', 'danger');
                        }
                    })
                    .catch(error => {
                        console.error('Грешка при премахване:', error);
                        U.alert('Възникна грешка. Моля, опитайте отново.', 'danger');
                    });
                }
            });
        });
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

/* ========== ФУНКЦИИ ЗА КОЛИЧКАТА ========== */
const djangoData = window.djangoData || {};

const cartConfig = {
    csrfToken: djangoData.csrfToken || '',
    cartApiUrl: djangoData.cartApiUrl || '/orders/cart/api/',
    addToCartUrl: djangoData.addToCartUrl || '/orders/add-to-cart/'
};

/**
 * Обновява статистиката на страницата с поръчки без презареждане
 */
function fetchStatistics() {
    fetch('/orders/stats/api/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const totalOrdersEl = document.getElementById('total-orders');
            const pendingOrdersEl = document.getElementById('pending-orders');
            const totalRevenueEl = document.getElementById('total-revenue');
            const avgOrderValueEl = document.getElementById('avg-order-value');

            if (totalOrdersEl) totalOrdersEl.textContent = data.total_orders;
            if (pendingOrdersEl) pendingOrdersEl.textContent = data.pending_orders;
            if (totalRevenueEl) totalRevenueEl.textContent = data.total_revenue.toFixed(2) + ' €';
            if (avgOrderValueEl) avgOrderValueEl.textContent = data.avg_order_value.toFixed(2) + ' €';
        })
        .catch(error => console.error('Грешка при обновяване на статистиката:', error));
}

/**
 * Обновява броя на артикулите в количката
 */
function updateCartCount() {
    fetch(cartConfig.cartApiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
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

            if (window.location.pathname === '/orders/') {
                fetchStatistics();
            }
        })
        .catch(error => console.error('Грешка при обновяване на количката:', error));
}

/**
 * Добавя продукт в количката чрез AJAX
 * @param {number} productId - ID на продукта
 * @param {number} quantity - Количество (по подразбиране 1)
 */
function addToCart(productId, quantity = 1) {
    const url = `${cartConfig.addToCartUrl}${productId}/`;

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': cartConfig.csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ quantity: Number(quantity) })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            updateCartCount();
            if (window.location.pathname === '/orders/') {
                fetchStatistics();
            }
            U.alert(data.message || 'Продуктът беше добавен в количката!', 'success');
        } else {
            U.alert('Възникна грешка при добавянето на продукта.', 'danger');
        }
    })
    .catch(error => {
        console.error('Грешка при добавяне в количката:', error);
        U.alert('Възникна грешка. Моля, опитайте отново.', 'danger');
    });
}

/* ========== ИНИЦИАЛИЗАЦИЯ ========== */
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

    if (window.location.pathname === '/orders/') {
        fetchStatistics();
    }

    window.addEventListener('cartUpdated', function() {
        updateCartCount();
        if (window.location.pathname === '/orders/') {
            fetchStatistics();
        }
    });
}

document.addEventListener('DOMContentLoaded', initAll);
