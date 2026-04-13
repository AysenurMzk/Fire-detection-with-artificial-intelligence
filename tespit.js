                                                                                                                         //konum değiskenleri
let map = null;
let marker = null;
let selectedLat = 39.9334; // varsayılan Türkiye merkezi
let selectedLon = 32.8597;
let selectedAddress = "Konum seçilmedi";
let isUsingCurrentLocation = false;
let currentUserId = null;
let currentUserName = null;


const fileInput = document.getElementById('fileInput');
const fileUpload = document.getElementById('fileUpload');
const resultSection = document.getElementById('resultSection');
const analysisResult = document.getElementById('analysisResult');
const originalImage = document.getElementById('originalImage');
const loading = document.getElementById('loading');
const alarmSound = document.getElementById('alarmSound');


function getUserLocationKey(key) {
    if (!currentUserId) {
        console.error(' Kullanıcı ID bulunamadı!');
        return `location_guest_${key}`;
    }
    return `location_${currentUserId}_${key}`;
}


document.addEventListener('DOMContentLoaded', function() {
    console.log(' Yangın Tespit Sistemi yüklendi');

    // Kullanıcı bilgilerini al
    const userIdInput = document.getElementById('userId');
    const userNameInput = document.getElementById('userName');

    currentUserId = userIdInput ? userIdInput.value : null;
    currentUserName = userNameInput ? userNameInput.value : 'misafir';

    console.log(' Kullanıcı bilgileri:', {
        id: currentUserId,
        name: currentUserName
    });

    // elementleri kontrol et
    console.log(' Element kontrolleri:');
    console.log('- fileInput:', fileInput);
    console.log('- fileUpload:', fileUpload);
    console.log('- resultSection:', resultSection);

    // onceki konumu kontrol et kullanıcı bazlı
    checkLastLocation();

    // dosya yükleme event lerini ayarla
    setupFileUploadEvents();

    // konum modalı eventlerini ayarla
    setupModalEvents();

    // sayfa yenilenirse konumu kontrol et
    checkPageRefresh();
});

// sayfa yenileöe kontrolu
function checkPageRefresh() {
    const lastVisit = sessionStorage.getItem('lastVisit');
    const now = Date.now();

    if (lastVisit && (now - lastVisit) > 1000) {
        console.log(' Sayfa yenilendi, konum sıfırlanıyor');
        clearTemporaryLocation();
    }

    sessionStorage.setItem('lastVisit', now);
}

// dosya yukleme
function setupFileUploadEvents() {
    if (fileUpload) {
        // Tıklama event'i
        fileUpload.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log(' Dosya yükleme alanına tıklandı');

            // Konum kontrolü yap
            if (!isLocationSelected()) {
                console.log(' Konum seçilmedi, modal açılıyor');
                openLocationModal();
            } else {
                console.log(' Konum seçilmiş, dosya seçici açılıyor');
                safeTriggerFileInput();
            }
        });

        // drag and drop event'leri
        fileUpload.addEventListener('dragover', function(e) {
            e.preventDefault();
            fileUpload.classList.add('dragover');
        });

        fileUpload.addEventListener('dragleave', function() {
            fileUpload.classList.remove('dragover');
        });

        fileUpload.addEventListener('drop', function(e) {
            e.preventDefault();
            fileUpload.classList.remove('dragover');

            // konum kontrolü
            if (!isLocationSelected()) {
                alert('Lütfen önce konum seçin!');
                openLocationModal();
                return;
            }

            if (e.dataTransfer.files.length) {
                console.log(' Dosya sürüklendi:', e.dataTransfer.files[0].name);
                fileInput.files = e.dataTransfer.files;
                handleFileSelect();
            }
        });
    } else {
        console.error(' fileUpload elementi bulunamadı!');
    }

    if (fileInput) {
        // input değiştiğinde
        fileInput.addEventListener('change', function() {
            console.log(' Dosya seçildi:', this.files[0]?.name);

            // konum kontrolü
            if (!isLocationSelected()) {
                alert('Lütfen önce konum seçin!');
                this.value = '';
                openLocationModal();
                return;
            }
            handleFileSelect();
        });
    } else {
        console.error(' fileInput elementi bulunamadı!');
    }
}

// dosya secme
function safeTriggerFileInput() {
    if (!fileInput) {
        console.error(' fileInput elementi bulunamadı!');
        return;
    }

    console.log(' Güvenli dosya seçici tetikleniyor...');

    // 1önce inputu temizle
    fileInput.value = '';

    // 2küçük bir gecikme ile tetikle
    setTimeout(() => {
        try {
            fileInput.click();
            console.log(' Dosya seçici tetiklendi');
        } catch (error) {
            console.error(' Dosya seçici tetiklenemedi:', error);
        }
    }, 50);
}

// konum kontrol
function isLocationSelected() {
    const lat = localStorage.getItem(getUserLocationKey('lat'));
    const lon = localStorage.getItem(getUserLocationKey('lon'));
    return lat && lon && lat !== 'null' && lon !== 'null';
}

function checkLastLocation() {
    if (isLocationSelected()) {
        const lat = localStorage.getItem(getUserLocationKey('lat'));
        const lon = localStorage.getItem(getUserLocationKey('lon'));
        const address = localStorage.getItem(getUserLocationKey('address')) || "Adres kaydedilmemiş";

        selectedLat = parseFloat(lat);
        selectedLon = parseFloat(lon);
        selectedAddress = address;

        // ekranda göster
        updateLocationDisplay();
        console.log(' Son konum yüklendi:', {
            lat: selectedLat,
            lon: selectedLon,
            user: currentUserName
        });
    } else {
        console.log(' Bu kullanıcı için son konum bulunamadı, varsayılan kullanılıyor');
        // varsayılan değerlere dön
        selectedLat = 39.9334;
        selectedLon = 32.8597;
        selectedAddress = "Konum seçilmedi";
    }
}

function updateLocationDisplay() {
    const locationDisplay = document.getElementById('currentLocationDisplay');
    const locationResult = document.getElementById('locationResult');
    const locationHint = document.getElementById('locationHint');
    const selectedLocationDisplay = document.getElementById('selectedLocationDisplay');

    if (isLocationSelected()) {
        const shortAddress = selectedAddress.length > 80
            ? selectedAddress.substring(0, 80) + '...'
            : selectedAddress;

        if (locationDisplay) {
            locationDisplay.textContent = `${selectedLat.toFixed(6)}, ${selectedLon.toFixed(6)} - ${shortAddress}`;
        }

        if (locationResult) {
            locationResult.textContent = shortAddress;
        }

        if (locationHint) {
            locationHint.textContent = ` ${currentUserName} için konum seçildi, şimdi fotoğraf yükleyebilirsiniz!`;
            locationHint.style.color = '#2ecc71';
        }

        if (selectedLocationDisplay) {
            selectedLocationDisplay.style.display = 'block';
        }
    } else {
        if (locationHint) {
            locationHint.textContent = ' ÖNEMLİ: Analiz için önce konum seçmelisiniz!';
            locationHint.style.color = '#e74c3c';
        }

        if (selectedLocationDisplay) {
            selectedLocationDisplay.style.display = 'none';
        }
    }
}

//
function setupModalEvents() {
    // modal dışına tıklanınca kapat
    const modal = document.getElementById('locationModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeLocationModal();
            }
        });
    }

    // ESC tuşu ile kapat
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeLocationModal();
        }
    });
}

function openLocationModal() {
    console.log(' Konum modalı açılıyor');
    const modal = document.getElementById('locationModal');
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Haritayı başlat
        setTimeout(initMap, 100);
    }
}

function closeLocationModal() {
    console.log('✖ Konum modalı kapatılıyor');
    const modal = document.getElementById('locationModal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
    isUsingCurrentLocation = false;
}

// harita islemleri
function initMap() {
    console.log(' Harita başlatılıyor...');

    const mapContainer = document.getElementById('mapContainer');
    if (!mapContainer) {
        console.error(' Harita konteyneri bulunamadı!');
        return;
    }

    // harita yükleniyor göster
    showMapLoading(true);

    // eski haritayı temizle
    if (map) {
        map.remove();
        map = null;
    }

    // yeni harita oluştur
    setTimeout(() => {
        try {
            map = L.map('mapContainer').setView([selectedLat, selectedLon], isUsingCurrentLocation ? 13 : 6);

            // OpenStreetMap katmanı
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
                maxZoom: 19
            }).addTo(map);

            // isaretçi oluştur
            marker = L.marker([selectedLat, selectedLon], {
                draggable: true,
                title: 'Konumunuzu sürükleyin'
            }).addTo(map);

            // koordinatları göster
            updateMapCoordinates();

            // adres al
            getAddress(selectedLat, selectedLon);

            // işaretçi sürüklendiğinde
            marker.on('dragend', function() {
                const pos = marker.getLatLng();
                selectedLat = pos.lat;
                selectedLon = pos.lng;
                updateMapCoordinates();
                getAddress(selectedLat, selectedLon);
                isUsingCurrentLocation = false;
                hideCurrentLocationBadge();
            });

            // haritaya tıklandığında
            map.on('click', function(e) {
                marker.setLatLng(e.latlng);
                selectedLat = e.latlng.lat;
                selectedLon = e.latlng.lng;
                updateMapCoordinates();
                getAddress(selectedLat, selectedLon);
                isUsingCurrentLocation = false;
                hideCurrentLocationBadge();
            });

            // harita yüklendi
            setTimeout(() => {
                showMapLoading(false);
                console.log(' Harita başarıyla yüklendi');
            }, 300);

        } catch (error) {
            console.error(' Harita başlatma hatası:', error);
            showMapLoading(false);
            alert('Harita yüklenirken hata oluştu: ' + error.message);
        }
    }, 100);
}

function updateMapCoordinates() {
    const latDisplay = document.getElementById('selectedLatDisplay');
    const lonDisplay = document.getElementById('selectedLonDisplay');

    if (latDisplay) latDisplay.textContent = selectedLat.toFixed(6);
    if (lonDisplay) lonDisplay.textContent = selectedLon.toFixed(6);
}

//NOMŞTANİM
async function getAddress(lat, lon) {
    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=16`
        );
        const data = await response.json();
        if (data.display_name) {
            selectedAddress = data.display_name;
            const addressElement = document.getElementById('addressDisplay');
            if (addressElement) {
                // adresi kısalt
                const shortAddress = selectedAddress.length > 80
                    ? selectedAddress.substring(0, 80) + '...'
                    : selectedAddress;
                addressElement.textContent = shortAddress;
            }
        }
    } catch (error) {
        console.warn(' Adres alınamadı:', error);
        selectedAddress = 'Adres alınamadı';
        const addressElement = document.getElementById('addressDisplay');
        if (addressElement) {
            addressElement.textContent = 'Adres alınamadı';
        }
    }
}

function showMapLoading(show) {
    const loadingElement = document.getElementById('mapLoading');
    const confirmBtn = document.getElementById('confirmBtn');

    if (loadingElement) {
        loadingElement.style.display = show ? 'flex' : 'none';
    }

    if (confirmBtn) {
        confirmBtn.disabled = show;
    }
}

//konum islemleri
function useCurrentLocation() {
    if (navigator.geolocation) {
        console.log(' Mevcut konum alınıyor...');
        const confirmBtn = document.getElementById('confirmBtn');
        if (confirmBtn) confirmBtn.disabled = true;

        navigator.geolocation.getCurrentPosition(
            position => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                console.log(` Mevcut konum alındı: ${lat.toFixed(6)}, ${lon.toFixed(6)}`);

                if (map && marker) {
                    map.setView([lat, lon], 13);
                    marker.setLatLng([lat, lon]);
                    selectedLat = lat;
                    selectedLon = lon;
                    updateMapCoordinates();
                    getAddress(lat, lon);
                    isUsingCurrentLocation = true;
                    showCurrentLocationBadge();

                    if (confirmBtn) confirmBtn.disabled = false;
                }
            },
            error => {
                console.warn('️ Konum alınamadı:', error);
                alert('Konumunuz alınamadı. Lütfen haritadan seçim yapın.');
                if (confirmBtn) confirmBtn.disabled = false;
            }
        );
    } else {
        alert('Tarayıcınız konum desteği sağlamıyor.');
    }
}

function showCurrentLocationBadge() {
    const badge = document.getElementById('currentLocationBadge');
    if (badge) {
        badge.style.display = 'inline-block';
    }
}

function hideCurrentLocationBadge() {
    const badge = document.getElementById('currentLocationBadge');
    if (badge) {
        badge.style.display = 'none';
    }
}

function confirmLocation() {
    if (!selectedLat || !selectedLon) {
        alert('Lütfen bir konum seçin!');
        return;
    }

    console.log(` Konum onaylandı: ${selectedLat.toFixed(6)}, ${selectedLon.toFixed(6)}`);

    // konumu kaydet kullanıcı bazlı
    saveLocation();

    // eodalı kapat
    closeLocationModal();

    // ekranı güncelle
    updateLocationDisplay();
}

function saveLocation() {
    localStorage.setItem(getUserLocationKey('lat'), selectedLat);
    localStorage.setItem(getUserLocationKey('lon'), selectedLon);
    localStorage.setItem(getUserLocationKey('address'), selectedAddress);
    localStorage.setItem(getUserLocationKey('time'), new Date().toISOString());

    console.log(' Konum kaydedildi:', {
        lat: selectedLat,
        lon: selectedLon,
        address: selectedAddress,
        user: currentUserName
    });
}

function showLastLocation() {
    if (isLocationSelected()) {
        const lat = localStorage.getItem(getUserLocationKey('lat'));
        const lon = localStorage.getItem(getUserLocationKey('lon'));
        alert(` ${currentUserName} için son seçilen konum:\nEnlem: ${lat}\nBoylam: ${lon}`);
    } else {
        alert('Henüz bir konum seçilmemiş.');
    }
}

// konum temizleme
function clearUserLocation() {
    console.log(' Kullanıcı konumu temizleniyor:', currentUserName);

    localStorage.removeItem(getUserLocationKey('lat'));
    localStorage.removeItem(getUserLocationKey('lon'));
    localStorage.removeItem(getUserLocationKey('address'));
    localStorage.removeItem(getUserLocationKey('time'));

    // session storageı da temizle
    sessionStorage.clear();

    console.log(' Kullanıcı konumu temizlendi');
}

function clearTemporaryLocation() {
    console.log(' Geçici konum temizleniyor');

    // varsayılan değerlere dön
    selectedLat = 39.9334;
    selectedLon = 32.8597;
    selectedAddress = "Konum seçilmedi";

    // ekranı güncelle
    updateLocationDisplay();
}


function goBack() {
    console.log('↩ Geri butonuna tıklandı');
    if (document.referrer && document.referrer.includes(window.location.host)) {
        window.history.back();
    } else {
        window.location.href = '/';
    }
}

// dosya seçildiğinde
function handleFileSelect() {
    console.log(' handleFileSelect çağrıldı');
    const file = fileInput.files[0];
    if (!file) {
        console.log(' Dosya seçilmedi');
        return;
    }

    console.log(` Dosya seçildi: ${file.name}, ${file.size} bytes, ${file.type}`);

    if (!file.type.match('image.*')) {
        alert('Lütfen sadece resim dosyası seçin! (PNG, JPG, JPEG)');
        fileInput.value = '';
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        alert('Dosya boyutu 5MB\'dan küçük olmalıdır!');
        fileInput.value = '';
        return;
    }

    if (loading) {
        loading.style.display = 'block';
        console.log(' Loading gösteriliyor');
    }

    if (resultSection) {
        resultSection.style.display = 'none';
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        console.log(' Dosya başarıyla okundu');
        if (originalImage) {
            originalImage.src = e.target.result;
        }
        analyzeImage(e.target.result);
    };

    reader.onerror = function(e) {
        console.error(' Dosya okuma hatası:', e);
        if (loading) loading.style.display = 'none';
        alert('Dosya okunurken hata oluştu!');
    };

    reader.readAsDataURL(file);
}

// görsel analiz et
async function analyzeImage(imageSrc) {
    console.log(' analyzeImage başladı');
    const img = new Image();
    img.onload = function() {
        console.log(' Görsel yüklendi, boyutlar:', img.width, 'x', img.height);

        // Backend'e gönder
        console.log(' Backend\'e gönderiliyor...');
        sendToBackend(imageSrc);
    };

    img.onerror = function() {
        console.error(' Görsel yüklenemedi');
        if (loading) loading.style.display = 'none';
        alert('Görsel yüklenirken hata oluştu!');
    };

    img.src = imageSrc;
}

// backende istek gönder
async function sendToBackend(imageData) {
    try {
        console.log(' Model analizi başlatılıyor...');

        // konum verisini hazırla
        const locationData = isLocationSelected() ? {
            lat: localStorage.getItem(getUserLocationKey('lat')),
            lon: localStorage.getItem(getUserLocationKey('lon')),
            address: localStorage.getItem(getUserLocationKey('address')),
            time: localStorage.getItem(getUserLocationKey('time')),
            user: currentUserName
        } : null;

        const requestBody = {
            image: imageData,
            location: locationData
        };

        console.log(' Gönderilen veri:', {
            hasImage: !!imageData,
            hasLocation: !!locationData,
            location: locationData
        });

        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });

        console.log(' Yanıt alındı, status:', response.status);

        if (!response.ok) {
            const errorText = await response.text();
            console.error(' Sunucu hatası:', errorText);
            throw new Error(`Sunucu hatası: ${response.status}`);
        }

        const result = await response.json();
        console.log(' Model analizi tamamlandı:', result);

        if (result.error) {
            throw new Error(result.error);
        }

        displayResults(result);

        if (loading) {
            loading.style.display = 'none';
        }

        if (resultSection) {
            resultSection.style.display = 'block';
            console.log(' Sonuçlar gösteriliyor');
        }

    } catch (error) {
        console.error(' Analiz hatası:', error);
        if (loading) loading.style.display = 'none';
        alert('Analiz sırasında hata oluştu: ' + error.message);
    }
}

// sınıflar
function getClassDisplayName(className) {
    switch(className) {
        case 'y0': return 'Yangın Yok';
        case 'y1': return 'Küçük Yangın';
        case 'y2': return 'Büyük Yangın';
        case 'y3': return 'Yangın Yok';
        default: return className;
    }
}

// sonucar
function displayResults(result) {
    console.log(' displayResults çağrıldı:', result);

    const originalClass = result.class;
    const displayClass = getClassDisplayName(originalClass);
    const confidence = result.confidence;
    const confidencePercent = (confidence * 100).toFixed(1);

    let resultText, resultClass, riskScore, flameDetection, smokeDensity, heatLevel, recommendedAction;


    if (originalClass === 'y2') {
        resultText = ` BÜYÜK YANGIN TESPİT EDİLDİ!  (${confidencePercent}% güven)`;
        resultClass = 'result-buyuk';
        riskScore = `${Math.round(confidence * 100)}%`;
        flameDetection = 'Yüksek';
        smokeDensity = 'Yoğun';
        heatLevel = 'Tehlikeli';
        recommendedAction = 'Hemen tahliye ve itfaiye çağırın (110)';

        if (alarmSound) {
            alarmSound.play().catch(e => console.log(' Alarm sesi çalınamadı:', e));
        }

    } else if (originalClass === 'y1') {
        resultText = ` KÜÇÜK YANGIN TESPİT EDİLDİ (${confidencePercent}% güven)`;
        resultClass = 'result-kucuk';
        riskScore = `${Math.round(confidence * 100)}%`;
        flameDetection = 'Orta';
        smokeDensity = 'Hafif';
        heatLevel = 'Yüksek';
        recommendedAction = 'Yangın söndürücü ile müdahale edin';

    } else if (originalClass === 'y0' || originalClass === 'y3') {
        resultText = ` YANGIN TESPİT EDİLMEDİ (${confidencePercent}% güven)`;
        resultClass = 'result-yok';
        riskScore = `${Math.round(confidence * 100)}%`;
        flameDetection = 'Yok';
        smokeDensity = 'Yok';
        heatLevel = 'Normal';
        recommendedAction = 'Güvendesiniz, rutin kontrollere devam edin';

        if (originalClass === 'y3') {
            console.log(' Model: Gün doğumu/batımı görüntüsü tespit edildi (y3 sınıfı).');
        }

    } else {
        resultText = ` ANALİZ SONUCU: ${displayClass.toUpperCase()} (${confidencePercent}% güven)`;
        resultClass = 'result-yok';
        riskScore = `${Math.round(confidence * 100)}%`;
        flameDetection = 'Belirsiz';
        smokeDensity = 'Belirsiz';
        heatLevel = 'Belirsiz';
        recommendedAction = 'Lütfen daha net bir fotoğraf deneyin';
    }

    // Sonuçları ekranda göster
    if (analysisResult) {
        analysisResult.textContent = resultText;
        analysisResult.className = `analysis-result ${resultClass}`;
        console.log(' Sonuç yazısı güncellendi');
    }

    // detayları güncelle
    const flameEl = document.getElementById('flameDetection');
    const smokeEl = document.getElementById('smokeDensity');
    const heatEl = document.getElementById('heatLevel');
    const riskEl = document.getElementById('riskScore');
    const actionEl = document.getElementById('recommendedAction');

    if (flameEl) flameEl.textContent = flameDetection;
    if (smokeEl) smokeEl.textContent = smokeDensity;
    if (heatEl) heatEl.textContent = heatLevel;
    if (riskEl) riskEl.textContent = riskScore;
    if (actionEl) actionEl.textContent = recommendedAction;

    // düsük güven uyarısı
    if (confidence < 0.6 && (originalClass === 'y1' || originalClass === 'y2')) {
        setTimeout(() => {
            alert(` Model bu tahminden çok emin değil (%${confidencePercent} güven). Lütfen daha net bir fotoğraf deneyin.`);
        }, 500);
    }
}

// yeni analiz
function analyzeNewImage() {
    console.log(' Yeni analiz başlatılıyor');
    if (fileInput) fileInput.value = '';
    if (resultSection) resultSection.style.display = 'none';
    stopAlarm();
}

// alarmı durdur
function stopAlarm() {
    if (alarmSound) {
        alarmSound.pause();
        alarmSound.currentTime = 0;
    }
}

// rapor indir
function downloadReport() {
    console.log(' Rapor indiriliyor');
    const resultText = analysisResult ? analysisResult.textContent : 'Sonuç bulunamadı';
    const confidenceMatch = resultText.match(/\((\d+\.?\d*)% güven\)/);
    const confidence = confidenceMatch ? confidenceMatch[1] : 'N/A';

    let resultClass = '';
    if (analysisResult) {
        resultClass = analysisResult.className.replace('analysis-result ', '');
    }

    let severity = '';
    if (resultClass.includes('buyuk')) severity = 'YÜKSEK';
    else if (resultClass.includes('kucuk')) severity = 'ORTA';
    else severity = 'DÜŞÜK';

    // konum bilgisi
    let locationInfo = 'Konum bilgisi bulunamadı';
    if (isLocationSelected()) {
        const lat = localStorage.getItem(getUserLocationKey('lat'));
        const lon = localStorage.getItem(getUserLocationKey('lon'));
        const address = localStorage.getItem(getUserLocationKey('address')) || 'Adres kaydedilmemiş';
        locationInfo = `${lat}, ${lon} - ${address}`;
    }

    const details = `
YANGIN ANALİZ RAPORU
====================
Sonuç: ${resultText}
Tarih: ${new Date().toLocaleString('tr-TR')}
Kullanıcı: ${currentUserName}
Model: Model 11 (4 Sınıflı)
Model Genel Doğruluk: %88

📍 KONUM BİLGİSİ:
${locationInfo}

DETAYLI ANALİZ:
- Güven Skoru: %${confidence}
- Tehlike Seviyesi: ${severity}
- Alev Tespiti: ${document.getElementById('flameDetection')?.textContent || 'N/A'}
- Duman Yoğunluğu: ${document.getElementById('smokeDensity')?.textContent || 'N/A'}
- Isı Seviyesi: ${document.getElementById('heatLevel')?.textContent || 'N/A'}
- Yangın Risk Puanı: ${document.getElementById('riskScore')?.textContent || 'N/A'}
- Önerilen Müdahale: ${document.getElementById('recommendedAction')?.textContent || 'N/A'}

Acil durumlarda 110'u arayınız.
    `.trim();

    const blob = new Blob([details], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `yangin-analiz-raporu-${currentUserName}-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// konumu değiştir
function changeLocation() {
    console.log(' Konum değiştirme isteği');
    openLocationModal();
}


function testFileSelection() {
    console.log(' Dosya seçimi test ediliyor...');
    safeTriggerFileInput();
}