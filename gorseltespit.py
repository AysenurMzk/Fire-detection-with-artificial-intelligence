# hizli_kontrol.py
import os
from PIL import Image
#görseli açmaya çalış açamıyorsa bozuk verify() ile bakılır convert('RGB') ile renk kanalları düzgün çalışıyor mu bakılır

def hizli_kontrol():
    base_path = 'data'
    bozuklar = []



    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(root, file)
                try:
                    with Image.open(file_path) as img:
                        img.verify()
                    with Image.open(file_path) as img:
                        img.convert('RGB')
                except:
                    bozuklar.append(file_path)
                    print(f"❌ {file_path}")

    print(f"\n SONUÇ: {len(bozuklar)} bozuk görsel bulundu")
    return bozuklar


if __name__ == "__main__":
    hizli_kontrol()# bozuk_tespit.py
import os
from PIL import Image
import pandas as pd
from collections import defaultdict

def bozuk_gorselleri_tespit_et():
    """
    Tüm data klasöründeki bozuk görselleri tespit eder ve raporlar
    """
    base_path = 'data'
    bozuk_dosyalar = []
    klasor_istatistikleri = defaultdict(lambda: {'toplam': 0, 'bozuk': 0, 'dosyalar': []})

    print(" BOZUK GÖRSEL TESPİTİ BAŞLATILIYOR...")
    print("=" * 60)

    # Tüm ana klasörleri kontrol et
    ana_klasorler = ['train', 'valid', 'test']

    for ana_klasor in ana_klasorler:
        ana_klasor_yolu = os.path.join(base_path, ana_klasor)

        if not os.path.exists(ana_klasor_yolu):
            print(f"  {ana_klasor} klasörü bulunamadı: {ana_klasor_yolu}")
            continue

        print(f"\n {ana_klasor.upper()} KLASÖRÜ TARANIYOR...")
        print("-" * 40)

        # Her bir sınıf klasörünü kontrol et
        for sinif_klasoru in os.listdir(ana_klasor_yolu):
            sinif_yolu = os.path.join(ana_klasor_yolu, sinif_klasoru)

            if not os.path.isdir(sinif_yolu):
                continue

            sinif_toplam = 0
            sinif_bozuk = 0

            # Görselleri tek tek kontrol et
            for dosya in os.listdir(sinif_yolu):
                if dosya.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')):
                    sinif_toplam += 1
                    klasor_istatistikleri[ana_klasor]['toplam'] += 1

                    dosya_yolu = os.path.join(sinif_yolu, dosya)

                    try:
                        # Görseli aç ve kontrol et
                        with Image.open(dosya_yolu) as img:
                            img.verify()  # Bütünlük kontrolü

                        # Tekrar aç ve format kontrolü yap
                        with Image.open(dosya_yolu) as img:
                            img.convert('RGB')

                    except Exception as e:
                        # Bozuk görsel bulundu
                        sinif_bozuk += 1
                        klasor_istatistikleri[ana_klasor]['bozuk'] += 1

                        bozuk_bilgisi = {
                            'ana_klasor': ana_klasor,
                            'sinif_klasoru': sinif_klasoru,
                            'dosya_yolu': dosya_yolu,
                            'dosya_adi': dosya,
                            'hata': str(e)
                        }
                        bozuk_dosyalar.append(bozuk_bilgisi)
                        klasor_istatistikleri[ana_klasor]['dosyalar'].append(bozuk_bilgisi)

                        # Ekrana yazdır
                        print(f" {ana_klasor}/{sinif_klasoru}/{dosya}")

            # Sınıf bazlı sonuç
            if sinif_bozuk > 0:
                print(f"   {sinif_klasoru}: {sinif_bozuk} bozuk / {sinif_toplam} toplam")

    return bozuk_dosyalar, klasor_istatistikleri

def detayli_rapor_olustur(klasor_istatistikleri, bozuk_dosyalar):
    """
    Detaylı analiz raporu oluşturur
    """
    print("\n" + "=" * 60)
    print(" DETAYLI TESPİT RAPORU")
    print("=" * 60)

    toplam_gorsel = 0
    toplam_bozuk = 0

    for klasor, istatistik in klasor_istatistikleri.items():
        toplam_gorsel += istatistik['toplam']
        toplam_bozuk += istatistik['bozuk']

        if istatistik['toplam'] > 0:
            bozuk_orani = (istatistik['bozuk'] / istatistik['toplam']) * 100
        else:
            bozuk_orani = 0

        print(f"\n {klasor.upper()} KLASÖRÜ:")
        print(f"   ├─ Toplam Görsel: {istatistik['toplam']}")
        print(f"   ├─ Bozuk Görsel: {istatistik['bozuk']}")
        print(f"   └─ Bozuk Oranı: {bozuk_orani:.2f}%")

        # Sınıf bazlı detaylar
        if istatistik['bozuk'] > 0:
            sinif_istatistikleri = defaultdict(int)
            for dosya_bilgisi in istatistik['dosyalar']:
                sinif_istatistikleri[dosya_bilgisi['sinif_klasoru']] += 1

            print("   └─ 📋 Sınıf Bazlı Dağılım:")
            for sinif_adi, sayi in sinif_istatistikleri.items():
                print(f"      ├─ {sinif_adi}: {sayi} bozuk görsel")

    # GENEL ÖZET
    print("\n" + "=" * 60)
    print("🎯 GENEL ÖZET")
    print("=" * 60)
    print(f"    Toplam Görsel Sayısı: {toplam_gorsel}")
    print(f"    Toplam Bozuk Görsel: {toplam_bozuk}")

    if toplam_gorsel > 0:
        genel_oran = (toplam_bozuk / toplam_gorsel) * 100
        print(f"    Genel Bozuk Oranı: {genel_oran:.2f}%")

        if genel_oran == 0:
            print("\n    MÜKEMMEL! Hiç bozuk görsel bulunamadı!")
        elif genel_oran < 0.1:
            print("\n    ÇOK İYİ! Çok az bozuk görsel var")
        elif genel_oran < 1:
            print("\n     İYİ! Az sayıda bozuk görsel var")
        elif genel_oran < 5:
            print("\n    ORTA! Makul sayıda bozuk görsel var")
        else:
            print("\n    DİKKAT! Çok fazla bozuk görsel var!")
    else:
        print("    Hiç görsel bulunamadı!")

def raporlari_kaydet(bozuk_dosyalar, klasor_istatistikleri):
    """
    Tüm raporları dosyalara kaydeder
    """
    if not bozuk_dosyalar:
        print("\n Kayıt: Bozuk görsel olmadığı için rapor oluşturulmadı")
        return None

    print("\n RAPORLAR KAYDEDİLİYOR...")

    # 1. TÜM BOZUK GÖRSELLERİN LİSTESİ (CSV)
    df_tum = pd.DataFrame(bozuk_dosyalar)
    df_tum.to_csv('TUM_BOZUK_GORSELLER.csv', index=False, encoding='utf-8')
    print(" 'TUM_BOZUK_GORSELLER.csv' kaydedildi")

    # 2. KLASÖR BAZLI LİSTELER
    for klasor, istatistik in klasor_istatistikleri.items():
        if istatistik['bozuk'] > 0:
            klasor_dosyalari = [d for d in bozuk_dosyalar if d['ana_klasor'] == klasor]
            df_klasor = pd.DataFrame(klasor_dosyalari)
            df_klasor.to_csv(f'BOZUK_GORSELLER_{klasor.upper()}.csv', index=False, encoding='utf-8')
            print(f" 'BOZUK_GORSELLER_{klasor.upper()}.csv' kaydedildi")

    # 3. DETAYLI RAPOR (TXT)
    with open('BOZUK_GORSELLER_DETAYLI_RAPOR.txt', 'w', encoding='utf-8') as f:
        f.write("BOZUK GÖRSEL TESPİT RAPORU\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Rapor Tarihi: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Toplam Görsel: {sum([istatistik['toplam'] for istatistik in klasor_istatistikleri.values()])}\n")
        f.write(f"Toplam Bozuk: {len(bozuk_dosyalar)}\n\n")

        for klasor, istatistik in klasor_istatistikleri.items():
            if istatistik['toplam'] > 0:
                oran = (istatistik['bozuk'] / istatistik['toplam']) * 100
            else:
                oran = 0

            f.write(f"{klasor.upper()} KLASÖRÜ:\n")
            f.write(f"  Toplam: {istatistik['toplam']}\n")
            f.write(f"  Bozuk: {istatistik['bozuk']}\n")
            f.write(f"  Oran: {oran:.2f}%\n")

            if istatistik['bozuk'] > 0:
                f.write("  Bozuk Görseller:\n")
                for dosya in istatistik['dosyalar']:
                    f.write(f"    - {dosya['sinif_klasoru']}/{dosya['dosya_adi']}\n")
                    f.write(f"      Hata: {dosya['hata']}\n")
            f.write("\n")

    print(" 'BOZUK_GORSELLER_DETAYLI_RAPOR.txt' kaydedildi")

    # 4. ÖZET TABLO (CSV)
    ozet_veri = []
    for klasor, istatistik in klasor_istatistikleri.items():
        if istatistik['toplam'] > 0:
            oran = (istatistik['bozuk'] / istatistik['toplam']) * 100
        else:
            oran = 0

        ozet_veri.append({
            'Klasor': klasor,
            'Toplam_Gorsel': istatistik['toplam'],
            'Bozuk_Gorsel': istatistik['bozuk'],
            'Bozuk_Orani_%': oran
        })

    df_ozet = pd.DataFrame(ozet_veri)
    df_ozet.to_csv('BOZUK_GORSELLER_OZET.csv', index=False, encoding='utf-8')
    print(" 'BOZUK_GORSELLER_OZET.csv' kaydedildi")

    return df_tum

def main():
    """
    Ana fonksiyon - sadece tespit ve raporlama yapar
    """
    print(" BOZUK GÖRSEL TESPİT PROGRAMI")
    print(" Sadece tespit edecek, hiçbir şey silmeyecek!")
    print("=" * 60)

    base_path = 'data'

    if not os.path.exists(base_path):
        print("❌ 'data' klasörü bulunamadı!")
        return

    # 1. Bozuk görselleri tespit et
    bozuk_dosyalar, klasor_istatistikleri = bozuk_gorselleri_tespit_et()

    # 2. Detaylı rapor oluştur
    detayli_rapor_olustur(klasor_istatistikleri, bozuk_dosyalar)

    # 3. Raporları kaydet
    if bozuk_dosyalar:
        df = raporlari_kaydet(bozuk_dosyalar, klasor_istatistikleri)

        print(f"\n BİLGİ: {len(bozuk_dosyalar)} bozuk görsel tespit edildi.")
        print("   Bu görseller eğitim sırasında sorun çıkarabilir.")
        print("   Rapor dosyaları oluşturuldu, inceleyebilirsiniz.")
    else:
        print("\n🎉 MÜKEMMEL! Hiç bozuk görsel bulunamadı.")
        print(" Eğitime hemen başlayabilirsiniz!")

    print("\n OLUŞTURULAN DOSYALAR:")
    if bozuk_dosyalar:
        print("   - TUM_BOZUK_GORSELLER.csv")
        print("   - BOZUK_GORSELLER_OZET.csv")
        print("   - BOZUK_GORSELLER_DETAYLI_RAPOR.txt")
        for klasor in klasor_istatistikleri.keys():
            if klasor_istatistikleri[klasor]['bozuk'] > 0:
                print(f"   - BOZUK_GORSELLER_{klasor.upper()}.csv")
    else:
        print("   - Bozuk görsel olmadığı için rapor oluşturulmadı")

if __name__ == "__main__":
    main()