function goBack() {
    if (document.referrer && document.referrer.includes(window.location.host)) {
        window.history.back();
    } else {
        window.location.href = '/';
    }
}

function toggleSignupPassword() {
    const passwordInput = document.getElementById('signupPassword');
    const toggleButton = event.currentTarget;

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleButton.textContent = '🔒';
    } else {
        passwordInput.type = 'password';
        toggleButton.textContent = '👁️';
    }
}

function toggleConfirmPassword() {
    const passwordInput = document.getElementById('confirmPassword');
    const toggleButton = event.currentTarget;

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleButton.textContent = '🔒';
    } else {
        passwordInput.type = 'password';
        toggleButton.textContent = '👁️';
    }
}

function goToLogin() {
    window.location.href = '/girisyap';
}

function resetSubmitButton() {
    const submitBtn = document.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.textContent = 'Üye Ol';
        submitBtn.disabled = false;
        submitBtn.style.opacity = '1';
    }
}

function setupFormValidation() {
    const signupForm = document.getElementById('signupForm');
    const signupPassword = document.getElementById('signupPassword');
    const confirmPassword = document.getElementById('confirmPassword');

    if (signupForm && signupPassword && confirmPassword) {
        // Şifre eşleşme kontrolü
        function checkPasswordMatch() {
            const password = signupPassword.value;
            const confirm = confirmPassword.value;

            if (password && confirm) {
                if (password !== confirm) {
                    confirmPassword.style.borderColor = '#dc3545';
                } else {
                    confirmPassword.style.borderColor = '#28a745';
                }
            }
        }

        // Input event'leri
        confirmPassword.addEventListener('input', checkPasswordMatch);
        signupPassword.addEventListener('input', checkPasswordMatch);

        // Form submit event'i
        signupForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            const password = signupPassword.value;
            const confirm = confirmPassword.value;

            // Şifreler eşleşmiyorsa butonu kilitleme
            if (password !== confirm) {
                return; // Normal form gönderimine izin ver
            }

            // Şifreler eşleşiyorsa butonu kilitle
            submitBtn.textContent = 'Üye Olunuyor...';
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.7';

            // 8 saniye sonra otomatik sıfırlama (güvenlik için)
            setTimeout(resetSubmitButton, 8000);
        });
    }
}

function initializePage() {
    // Sayfa yüklendiğinde butonu sıfırla
    resetSubmitButton();

    // Form validasyonunu kur
    setupFormValidation();

    // İlk input'a odaklan
    const nameInput = document.getElementById('name');
    if (nameInput) {
        nameInput.focus();
    }

    // Flash mesajı varsa butonu sıfırla
    const flashMessages = document.querySelector('.flash-messages');
    if (flashMessages) {
        resetSubmitButton();
    }
}

// Sayfa yüklendiğinde initialize et
document.addEventListener('DOMContentLoaded', initializePage);

// Sayfa tamamen yüklendiğinde de butonu kontrol et (güvenlik için)
window.addEventListener('load', function() {
    resetSubmitButton();
});