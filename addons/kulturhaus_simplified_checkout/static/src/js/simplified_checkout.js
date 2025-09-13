/* Kulturhaus Simplified Checkout JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Kulturhaus Simplified Checkout loaded');
    
    // Initialize checkout enhancements
    initKulturhausCheckout();
});

function initKulturhausCheckout() {
    // Add German validation messages
    const form = document.querySelector('.kulturhaus-checkout-form');
    if (\!form) return;
    
    // Email validation
    const emailField = form.querySelector('input[name="email"]');
    if (emailField) {
        emailField.addEventListener('blur', function() {
            validateEmail(this);
        });
    }
    
    // Name validation
    const nameField = form.querySelector('input[name="name"]');
    if (nameField) {
        nameField.addEventListener('blur', function() {
            validateName(this);
        });
    }
    
    // Phone formatting
    const phoneField = form.querySelector('input[name="phone"]');
    if (phoneField) {
        phoneField.addEventListener('input', function() {
            formatGermanPhone(this);
        });
    }
}

function validateEmail(field) {
    const email = field.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && \!emailRegex.test(email)) {
        showError(field, 'Bitte geben Sie eine gueltige E-Mail Adresse ein');
        return false;
    }
    
    hideError(field);
    return true;
}

function validateName(field) {
    const name = field.value.trim();
    
    if (name.length < 2) {
        showError(field, 'Bitte geben Sie Ihren vollstaendigen Namen ein');
        return false;
    }
    
    hideError(field);
    return true;
}

function formatGermanPhone(field) {
    let phone = field.value.replace(/[^\d+]/g, '');
    
    if (phone.startsWith('0')) {
        phone = '+49' + phone.substring(1);
    }
    
    field.value = phone;
}

function showError(field, message) {
    hideError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'text-danger small mt-1';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
    field.classList.add('is-invalid');
}

function hideError(field) {
    const errorDiv = field.parentNode.querySelector('.text-danger');
    if (errorDiv) {
        errorDiv.remove();
    }
    field.classList.remove('is-invalid');
}
