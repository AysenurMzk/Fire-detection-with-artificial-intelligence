// Arka plan resim değiştirme - Yumuşak geçiş
document.addEventListener('DOMContentLoaded', function() {
    const resimler = document.querySelectorAll('.arkaplan-resim');
    let aktifResim = 0;

    console.log('Toplam resim sayısı:', resimler.length);

    // İlk resmi göster
    if (resimler.length > 0) {
        resimler[aktifResim].classList.add('aktif');
        console.log('İlk resim aktif edildi');
    }

    // Her 4 saniyede bir resim değiştir (daha yavaş)
    setInterval(function() {
        if (resimler.length > 1) { // En az 2 resim varsa değiştir
            // Mevcut resmi yavaşça gizle
            resimler[aktifResim].classList.remove('aktif');

            // Sonraki resmi seç
            let oncekiResim = aktifResim;
            aktifResim = (aktifResim + 1) % resimler.length;

            // Yeni resmi yavaşça göster
            setTimeout(() => {
                resimler[aktifResim].classList.add('aktif');
            }, 100);

            console.log('Resim değiştirildi:', oncekiResim, '->', aktifResim);
        }
    }, 4000); // 4000ms = 4 saniye
});

// Buton tıklama fonksiyonu - Blog sayfasına yönlendir
function butonaTiklandi() {
    // Butona tıklandığında butonu sallama efekti
    const buton = document.querySelector('.giris-butonu');
    buton.style.transform = 'translateX(10px)';

    setTimeout(() => {
        buton.style.transform = 'translateX(-10px)';
    }, 100);

    setTimeout(() => {
        buton.style.transform = 'translateX(0)';
    }, 200);

    // 300ms sonra blog sayfasına yönlendir (efektin bitmesini bekler)
    setTimeout(() => {
        window.location.href = '/blog';
    }, 300);
}

function yanginTespitTiklandi() {
    // Butona tıklandığında butonu sallama efekti
    const buton = document.querySelectorAll('.giris-butonu')[1];
    buton.style.transform = 'translateX(10px)';

    setTimeout(() => {
        buton.style.transform = 'translateX(-10px)';
    }, 100);

    setTimeout(() => {
        buton.style.transform = 'translateX(0)';
    }, 200);

    // 300ms sonra tespit sayfasına yönlendir
    setTimeout(() => {
        window.location.href = '/tespit';
    }, 300);
}

// Sayfa yüklendiğinde efekt
window.onload = function() {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 1.5s ease-in-out';

    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);

    // Resim URL'lerini kontrol et
    const resimler = document.querySelectorAll('.arkaplan-resim');
    resimler.forEach((resim, index) => {
        const bgImage = resim.style.backgroundImage;
        console.log(`Resim ${index + 1}:`, bgImage);
    });
};