function goBack() {
    if (document.referrer && document.referrer.includes(window.location.host)) {
        window.history.back();
    } else {
        window.location.href = '/';
    }
}

function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleButton = document.querySelector('.toggle-password');

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleButton.textContent = '🔒';
    } else {
        passwordInput.type = 'password';
        toggleButton.textContent = '👁️';
    }
}

function goToSignUp() {
    window.location.href = '/uyeol';
}

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        // Form submit event'ini KALDIRIYORUZ çünkü artık Flask işliyor
        // Sadece otomatik odaklanma ve diğer işlevler kalıyor

        // Input alanlarına otomatik odaklanma
        document.getElementById('email').focus();

        // Form gönderildiğinde loading state ekleyebilirsiniz (isteğe bağlı)
        loginForm.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.textContent = 'Giriş Yapılıyor...';
            submitBtn.disabled = true;
        });
    }
});