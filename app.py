from flask import Flask, render_template, send_from_directory, request, redirect, url_for, session, flash, jsonify
#request=Kullanıcının gönderdiği verileri alır , redirect =Kullanıcıyı başka bir sayfaya veya route’a yönlendirir
import os
from datetime import datetime
from webscraping import haberleri_getir
from veritabani import Veritabani
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import base64
import json
"""render template=Bir HTML dosyası (.html) sunmak istiyorsun. Render template" = "Şablonu işle/oluştur  Send template = Şablon dosyasını olduğu gibi gönder"""
"""send direction = HTML değil, dosya (resim, PDF, CSS, JS, vb.) göndermek istiyorsun."""
app = Flask(__name__)
app.secret_key = 'yangin_tespit_sistemi_gizli_anahtar'

# Veritabanı bağlantısı
db = Veritabani()

# Global model değişkenleri
model = None
CLASS_NAMES = ['y0', 'y1', 'y2', 'y3']  # Model 11 için 4 sınıf


def load_model():
    """Model 11'i yükle (4 sınıflı model)"""
    global model, CLASS_NAMES

    model_path = 'model_11_son.h5'
    class_names_path = 'model_11_siniflar.json'

    try:
        # Modeli yükle
        model = tf.keras.models.load_model(model_path)
        print(f" Model 11 başarıyla yüklendi: {model_path}")

        # Sınıf isimlerini JSON'dan yükle
        try:
            with open(class_names_path, 'r', encoding='utf-8') as f:
                CLASS_NAMES = json.load(f)
            print(f" Sınıf isimleri yüklendi: {CLASS_NAMES}")
        except FileNotFoundError:
            print(f" Sınıf isimleri JSON'u bulunamadı: {class_names_path}")
            CLASS_NAMES = ['y0', 'y1', 'y2', 'y3']
        except json.JSONDecodeError:
            print(f" JSON dosyası okunamadı: {class_names_path}")
            CLASS_NAMES = ['y0', 'y1', 'y2', 'y3']

        print(f" Model Bilgileri:")
        print(f"   - Sınıf Sayısı: {len(CLASS_NAMES)}")
        print(f"   - Model Doğruluğu: %82.14")
        print(f"   - Gün Doğumu Tespit Doğruluğu: %80.6")

    except Exception as e:
        print(f" Model yüklenirken hata: {e}")
        model = None
        print("️ Simülasyon modu aktif.")


def preprocess_image(image_data):
    """Base64 image verisini model için hazırla
    Base64, ikili (binary) verileri metin (text) formatına çevirmek için kullanılan bir şifreleme değil, kodlama yöntemidir.
    görsel al-> base64 ile string yap-> jsona koy backend anlasın diye-> backende yolla"""
    try:
        # Base64 ön eki varsa kaldır
        if ',' in image_data:
            image_data = image_data.split(',')[1]

        # Base64'ü decode et
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))

        # RGB'ye çevir
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Model için boyutlandır
        image = image.resize((224, 224))
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)

        return image_array
    except Exception as e:
        print(f" Görsel işleme hatası: {e}")
        raise e


@app.route('/')
def giris():
    resim_dosyalari = [f for f in os.listdir('resimler') if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    return render_template('giris.html', resimler=resim_dosyalari)


@app.route('/resimler/<path:filename>')
def serve_resimler(filename):
    return send_from_directory('resimler', filename)


@app.route('/blog')
def blog():
    haberler = haberleri_getir()
    return render_template('blog.html', haberler=haberler)


@app.route('/tespit')
def tespit_sayfasi():
    if 'kullanici_id' not in session:
        flash('Lütfen önce giriş yapın!', 'warning')
        return redirect(url_for('girisyap'))

    return render_template('tespit.html')


@app.route('/analyze', methods=['POST'])
def analyze_image():
    """Görsel analizi"""
    try:#Kullanıcı JSON ile bir image alanı göndermiş mi kontrol ediyoruz.
        if model is None:
            return jsonify({'error': 'Model yüklenemedi. Lütfen daha sonra tekrar deneyin.'}), 503

        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'Görsel verisi bulunamadı'}), 400

        image_data = data['image']#JSON içinden "image" alanını alıyor

        # konum bilgisi
        location_data = data.get('location', {})#Kullanıcı konum göndermemişse program hata vermesin diye varsayılan boş obje koyuyoruz.
        lat = location_data.get('lat')#location_data dictionary’sinden "lat" (enlem) değerini alıyor.
        lon = location_data.get('lon')#location_data dictionary’sinden "lon" (boylam) değerini alıyor.
        address = location_data.get('address', 'Bilinmiyor')#Eğer "address" yoksa varsayılan olarak 'Bilinmiyor' yazıyor.
        timestamp = location_data.get('time', datetime.now().isoformat())#"time" alanını alıyor, yani görselin gönderildiği zamanı.Eğer gönderilmemişse, şu anki zamanı ISO formatında (YYYY-MM-DDTHH:MM:SS) kullanıyor.

        # Konum bilgisi varsa logla
        if lat and lon:
            print("\n" + "=" * 50)
            print(" KONUM BİLGİSİ ALINDI:")
            print(f"   • Enlem: {lat}")
            print(f"   • Boylam: {lon}")
            print(f"   • Adres: {address[:80]}{'...' if len(address) > 80 else ''}")
            print(f"   • Zaman: {timestamp}")
            print("=" * 50 + "\n")
        else:
            print("️ Konum bilgisi bulunamadı veya eksik")
        # konum bilgisi sonu

        processed_image = preprocess_image(image_data)

        #Model output’u alınıyor (her sınıf için olasılık).
        #En yüksek olasılığı (argmax) tahmin edilen sınıf olarak seçiyoruz.
        #Bu sınıfın güven skorunu (confidence) alıyoruz.

        predictions = model.predict(processed_image, verbose=0)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])

        # Sınıf adını al
        if predicted_class_idx < len(CLASS_NAMES):
            predicted_class = CLASS_NAMES[predicted_class_idx]
        else:
            predicted_class = 'unknown'

        # Tüm tahminleri topla
        all_predictions = {}
        for i, class_name in enumerate(CLASS_NAMES):
            if i < len(predictions[0]):
                all_predictions[class_name] = float(predictions[0][i])
            else:
                all_predictions[class_name] = 0.0


        if predicted_class == 'y3':
            print(f" GÜN DOĞUMU TESPİTİ: {confidence:.3f} güven")

        # Sonuç oluştur
        result = {
            'class': predicted_class,  # y0, y1, y2, y3
            'confidence': confidence,
            'all_predictions': all_predictions,
            'location': {  # Konum bilgisini yanıta da ekleyelim
                'lat': lat,
                'lon': lon,
                'address': address
            } if lat and lon else None
        }

        # Analiz sonucunu logla
        print(f"\n ANALİZ SONUCU:")
        print(f"   • Tahmin: {predicted_class}")
        print(f"   • Güven: {confidence:.3f} ({confidence * 100:.1f}%)")

        if lat and lon:
            print(f"   • Konum: {lat}, {lon}")
        else:
            print(f"   • Konum: Bilinmiyor")

        if predicted_class == 'y2':
            print(f"    BÜYÜK YANGIN ALARMI!")
        elif predicted_class == 'y1':
            print(f"   ️  KÜÇÜK YANGIN UYARISI!")

        print("=" * 50 + "\n")

        return jsonify(result)

    except Exception as e:
        print(f" Analiz hatası: {e}")
        return jsonify({'error': f'Analiz sırasında hata oluştu: {str(e)}'}), 500


@app.route('/girisyap', methods=['GET', 'POST'])
def girisyap():
    if request.method == 'POST':
        email = request.form['email']
        sifre = request.form['password']
        kullanici = db.kullanici_kontrol(email, sifre)

        if kullanici:
            session['kullanici_id'] = kullanici[0]
            session['kullanici_adi'] = f"{kullanici[1]} {kullanici[2]}"
            session['email'] = email
            return redirect(url_for('blog'))
        else:
            flash('E-posta veya şifre hatalı!', 'error')

    return render_template('girisyap.html')


@app.route('/uyeol', methods=['GET', 'POST'])
def uyeol():
    if request.method == 'POST':
        isim = request.form['name']
        soyisim = request.form['surname']
        email = request.form['signupEmail']
        sifre = request.form['signupPassword']
        confirm_password = request.form['confirmPassword']

        if sifre != confirm_password:
            flash('Şifreler eşleşmiyor!', 'error')
            return render_template('uyeol.html')

        if len(sifre) < 6:
            flash('Şifre en az 6 karakter olmalıdır!', 'error')
            return render_template('uyeol.html')

        if not any(char.isalpha() for char in sifre):
            flash('Şifre en az bir harf içermelidir!', 'error')
            return render_template('uyeol.html')

        if not any(char.isdigit() for char in sifre):
            flash('Şifre en az bir sayı içermelidir!', 'error')
            return render_template('uyeol.html')

        if any(str(i) * 4 in sifre for i in range(10)):
            flash('Şifre 4 veya daha fazla ardışık sayı içeremez!', 'error')
            return render_template('uyeol.html')

        if any(char * 4 in sifre for char in set(sifre)):
            flash('Şifre 4 veya daha fazla aynı karakter içeremez!', 'error')
            return render_template('uyeol.html')

        if db.kullanici_ekle(isim, soyisim, email, sifre):
            flash('Üyeliğiniz başarıyla oluşturuldu! Lütfen giriş yapın.', 'success')
            return redirect(url_for('girisyap'))
        else:
            flash('Bu e-posta adresi zaten kayıtlı!', 'error')

    return render_template('uyeol.html')


@app.route('/sifre', methods=['GET', 'POST'])
def sifre():
    email = request.args.get('email', '')

    if request.method == 'POST':
        if email:
            yeni_sifre = request.form['new_password']
            confirm_password = request.form['confirm_password']

            if yeni_sifre != confirm_password:
                flash('Şifreler eşleşmiyor!', 'error')
                return render_template('sifre.html', email=email)

            if len(yeni_sifre) < 6:
                flash('Şifre en az 6 karakter olmalıdır!', 'error')
                return render_template('sifre.html', email=email)

            if not any(char.isalpha() for char in yeni_sifre) or not any(char.isdigit() for char in yeni_sifre):
                flash('Şifre en az bir harf ve bir sayı içermelidir!', 'error')
                return render_template('sifre.html', email=email)

            if db.sifre_guncelle(email, yeni_sifre):
                flash('Şifreniz başarıyla sıfırlandı!', 'success')
                return redirect(url_for('girisyap'))
            else:
                flash('Şifre güncellenirken hata oluştu!', 'error')
                return render_template('sifre.html', email=email)

        else:
            email = request.form['email']
            if db.email_kontrol(email):
                return redirect(url_for('sifre', email=email))
            else:
                flash('Bu email adresi kayıtlı değil!', 'error')
                return render_template('sifre.html')

    return render_template('sifre.html', email=email)


@app.route('/cikis')
def cikis():
    session.clear()
    return redirect(url_for('giris'))


@app.route('/misafir_giris')
def misafir_giris():
    session.clear()
    return redirect(url_for('blog'))


@app.route('/profil')
def profil():
    if 'kullanici_id' not in session:
        flash('Lütfen önce giriş yapın!', 'warning')
        return redirect(url_for('girisyap'))

    return render_template('profil.html',
                           kullanici_adi=session['kullanici_adi'],
                           email=session['email'])


@app.errorhandler(404)
def sayfa_bulunamadi(e):
    return "Sayfa bulunamadı - 404", 404


@app.errorhandler(500)
def sunucu_hatasi(e):
    return "Sunucu hatası - 500", 500


@app.route('/favicon.ico')
def favicon():
    return "", 200


if __name__ == '__main__':
    load_model()
    app.run(debug=True)