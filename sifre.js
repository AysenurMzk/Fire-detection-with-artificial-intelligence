function goBack() {
    if (document.referrer && document.referrer.includes(window.location.host)) {
        window.history.back();
    } else {
        window.location.href = '/girisyap';
    }
}

function goToLogin() {
    window.location.href = '/girisyap';
}

function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const toggleButton = event.currentTarget;

    if (input.type === 'password') {
        input.type = 'text';
        toggleButton.textContent = '🔒';
    } else {
        input.type = 'password';
        toggleButton.textContent = '👁️';
    }
}

function resetSubmitButton() {
    const submitBtn = document.querySelector('button[type="submit"]');
    if (submitBtn) {
        if (window.location.search.includes('email=')) {
            submitBtn.textContent = 'Şifreyi Sıfırla';
        } else {
            submitBtn.textContent = 'Devam Et';
        }
        submitBtn.disabled = false;
        submitBtn.style.opacity = '1';
    }
}

function checkPasswordRequirements(sifre) {
    if (sifre.length < 6) {
        return "Şifre en az 6 karakter olmalıdır!";
    }
    if (!/[a-zA-Z]/.test(sifre)) {
        return "Şifre en az bir harf içermelidir!";
    }
    if (!/\d/.test(sifre)) {
        return "Şifre en az bir sayı içermelidir!";
    }
    return "";
}

function setupPasswordValidation() {
    const passwordForm = document.getElementById('passwordForm');
    const newPassword = document.getElementById('new_password');
    const confirmPassword = document.getElementById('confirm_password');

    if (passwordForm && newPassword && confirmPassword) {
        // Şifre eşleşme kontrolü
        function checkPasswordMatch() {
            const password = newPassword.value;
            const confirm = confirmPassword.value;

            if (password && confirm) {
                if (password !== confirm) {
                    confirmPassword.style.borderColor = '#dc3545';
                } else {
                    confirmPassword.style.borderColor = '#28a745';
                }
            }
        }

        // Şifre gereksinim kontrolü
        function checkPasswordStrength() {
            const sifre = newPassword.value;
            const hataElement = document.getElementById('sifreHata');

            if (sifre.length >= 1) {
                const hata = checkPasswordRequirements(sifre);

                if (hata) {
                    if (!hataElement) {
                        const hataDiv = document.createElement('div');
                        hataDiv.id = 'sifreHata';
                        hataDiv.style.color = '#dc3545';
                        hataDiv.style.fontSize = '12px';
                        hataDiv.style.marginTop = '5px';
                        hataDiv.style.fontWeight = '500';
                        newPassword.parentNode.appendChild(hataDiv);
                    }
                    document.getElementById('sifreHata').textContent = hata;
                    newPassword.style.borderColor = '#dc3545';
                } else {
                    if (hataElement) {
                        hataElement.remove();
                    }
                    newPassword.style.borderColor = '#28a745';
                }
            } else {
                if (hataElement) {
                    hataElement.remove();
                }
                newPassword.style.borderColor = '#e1e5e9';
            }
        }

        // Input event'leri
        newPassword.addEventListener('input', checkPasswordStrength);
        confirmPassword.addEventListener('input', checkPasswordMatch);

        // Form submit event'i
        passwordForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            const hasEmail = window.location.search.includes('email=');

            if (hasEmail) {
                const sifre = newPassword.value;
                const confirmSifre = confirmPassword.value;
                const hata = checkPasswordRequirements(sifre);

                if (hata) {
                    e.preventDefault();
                    alert(hata);
                    return;
                }

                if (sifre !== confirmSifre) {
                    e.preventDefault();
                    alert('Şifreler eşleşmiyor!');
                    return;
                }

                // Her şey doğruysa butonu kilitle
                submitBtn.textContent = 'Sıfırlanıyor...';
                submitBtn.disabled = true;
                submitBtn.style.opacity = '0.7';

                // 8 saniye sonra otomatik sıfırlama
                setTimeout(resetSubmitButton, 8000);
            } else {
                // Email kontrolü sayfasında butonu kilitle
                submitBtn.textContent = 'Kontrol Ediliyor...';
                submitBtn.disabled = true;
                submitBtn.style.opacity = '0.7';

                // 5 saniye sonra otomatik sıfırlama
                setTimeout(resetSubmitButton, 5000);
            }
        });
    }
}

function initializePage() {
    // Sayfa yüklendiğinde butonu sıfırla
    resetSubmitButton();

    // Şifre validasyonunu kur
    setupPasswordValidation();

    // İlk input'a odaklan
    const firstInput = document.querySelector('.form-input');
    if (firstInput) {
        firstInput.focus();
    }

    // Flash mesajı varsa butonu sıfırla
    const flashMessages = document.querySelector('.flash-messages');
    if (flashMessages) {
        resetSubmitButton();
    }
}

// Sayfa yüklendiğinde initialize et
document.addEventListener('DOMContentLoaded', initializePage);

// Sayfa tamamen yüklendiğinde de butonu kontrol et
window.addEventListener('load', function() {
    resetSubmitButton();
});