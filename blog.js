// Haber açıklamalarını genişletmek/daraltmak için
function toggleAciklama(haberIndex) {
    const haberElement = document.querySelectorAll('.blog-post')[haberIndex];
    const kisaAciklama = haberElement.querySelector('.kisa-aciklama');
    const tumAciklama = haberElement.querySelector('.tum-aciklama');
    const button = haberElement.querySelector('.daha-fazla-btn');
    
    if (tumAciklama.style.display === 'none') {
        // Açık duruma getir
        tumAciklama.style.display = 'block';
        kisaAciklama.style.display = 'none';
        button.textContent = 'Daha Az Göster';
        button.style.background = '#636e72';
    } else {
        // Kapalı duruma getir
        tumAciklama.style.display = 'none';
        kisaAciklama.style.display = 'block';
        button.textContent = 'Daha Fazla Göster';
        button.style.background = '#ff6b6b';
    }
}

// Sayfa yüklendiğinde çalışacak fonksiyonlar
document.addEventListener('DOMContentLoaded', function() {
    console.log('Yangın haberleri blog sayfası yüklendi');
    
    // Haber kartlarına hover efekti
    const blogPosts = document.querySelectorAll('.blog-post');
    blogPosts.forEach(post => {
        post.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 5px 20px rgba(255, 107, 107, 0.2)';
        });
        
        post.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 2px 15px rgba(0,0,0,0.1)';
        });
    });
    
    // Otomatik yenileme (5 dakikada bir)
    setTimeout(() => {
        window.location.reload();
    }, 300000); // 5 dakika
});

// Haber başlıklarını kısaltma (gerekiyorsa)
function kisaltMetin(metin, maxUzunluk) {
    if (metin.length > maxUzunluk) {
        return metin.substring(0, maxUzunluk) + '...';
    }
    return metin;
}