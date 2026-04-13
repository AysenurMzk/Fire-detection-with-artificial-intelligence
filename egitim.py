import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.regularizers import l2
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
import os
import json
#resnet50 177 katman

NUM_CLASSES = 4
CLASS_NAMES = ['y0', 'y1', 'y2', 'y3']
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
INITIAL_LR = 0.0001
EPOCHS = 35

# Model numarası ve dosya isimleri
model_numara = 11
DOSYALAR = {
    'en_iyi_model': f"model_{model_numara}_en_iyi.h5",
    'final_model': f"model_{model_numara}_son.h5",
    'sinif_isimleri': f"model_{model_numara}_siniflar.json",
    'egitim_grafikleri': f"model_{model_numara}_grafik.png",
    'confusion_matrix': f"model_{model_numara}_confusion_matrix.png"
}


def create_balanced_augmentation():
    """
    Dengeli veri artırma için ImageDataGenerator oluşturur
    """
    return ImageDataGenerator(
        rescale=1. / 255,
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,#yatay ters çevirme
        zoom_range=0.15,
        brightness_range=[0.9, 1.1],#Görsellerin parlaklığını rastgele değiştirir
        fill_mode='nearest'
    )


def create_data_generators():
    """
    Eğitim, validasyon ve test veri generator'larını oluşturur
    """
    train_datagen = create_balanced_augmentation()
    val_test_datagen = ImageDataGenerator(rescale=1. / 255)

    print("VERİ GENERATOR'LARI HAZIRLANIYOR...")

    # Eğitim veri generator'ı
    train_gen = train_datagen.flow_from_directory(
        'data/train',
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True,
        seed=42#rastgeleliği kontrol etmek için kullanılan bir sabit , bu karıştırma her zaman aynı şekilde yapılır,Shuffle nasıl olursa olsun, aynı seed kullanılırsa her zaman aynı sıra oluşur
    )

    # Validasyon veri generator'ı
    val_gen = val_test_datagen.flow_from_directory(
        'data/valid',
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True,
        seed=42
    )

    # Test veri generator'ı (karıştırma yok)
    test_gen = val_test_datagen.flow_from_directory(
        'data/test',
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )

    return train_gen, val_gen, test_gen, val_test_datagen


def create_optimal_model():
    """
    Optimize edilmiş ResNet50 tabanlı model oluşturur
    """
    # ResNet50 temel modeli (önceden eğitilmiş ağırlıklar)
    base_model = ResNet50(
        weights='imagenet',
        include_top=False,#ResNet’in 1000 sınıflık ImageNet çıkışını almayacak, sadece ara katmanlar kalacak ve kendi çıkış katmanımızı ekleyeceğiz.
        input_shape=(224, 224, 3)
    )

    # Transfer Learning: İlk katmanlar dondurulur
    for layer in base_model.layers:
        layer.trainable = False

    # Son 25 katman ince ayar için eğitilebilir
    for layer in base_model.layers[-25:]:
        layer.trainable = True

    print(f"🔧 Eğitilebilir katman sayısı: {sum([l.trainable for l in base_model.layers])}")

    # Model başı ekleniyor
    x = base_model.output
    x = GlobalAveragePooling2D()(x)#3D feature map → 1D vektöre dönüştürme Bu vektör artık tam bağlı (dense) katmana girebilir

    # Tam bağlı katmanlar
    x = Dense(256, activation='relu', kernel_regularizer=l2(0.001))(x)
    #relu  aktivasyon fonksiyonu (activation function) yani Dense katmanının çıktısını işler ve bir sonraki katmana gönderir.x>0->x x<=0-> 0  - anlamsız
    x = BatchNormalization()(x)#bir katmandan çıkan veriyi normalize eder ,BatchNormalization, bu değerleri ortalama 0, standart sapma 1 civarına çekiyor
    x = Dropout(0.4)(x)

    x = Dense(128, activation='relu', kernel_regularizer=l2(0.0005))(x) # densedeki ağırlıkları kontrol altında tutar Çok büyük değerler alırlarsa cezalandırır → ağırlıklar fazla büyümez
    x = Dropout(0.3)(x)

    x = Dense(64, activation='relu')(x)
    x = Dropout(0.2)(x)

    # Çıkış katmanı (4 sınıf için)
    predictions = Dense(NUM_CLASSES, activation='softmax')(x)#Tüm sınıfların toplamı 1 olacak şekilde normalize eder

    model = Model(inputs=base_model.input, outputs=predictions)
    return model


def get_optimal_callbacks():
    """
    Optimize edilmiş eğitim callback'leri
    """
    return [
        EarlyStopping(
            monitor='val_accuracy',
            patience=15,#Val_accuracy 15 epoch boyunca artmadı → eğitim durdurulur
            restore_best_weights=True,#eğitim sonunda model en iyi öğrendiği haliyle kalır, son epoch’ta oluşan kötü ağırlıklar değil.
            mode='max',#Val_accuracy artmazsa bekle, ama en yüksek değeri bulana kadar sabret. En yüksek değeri yakaladığında onu geri yükle
            verbose=1,#Model eğitilirken başlangıç, her epoch sonrası kayıp ve doğruluk değerleri konsola yazı
            min_delta=0.001#Val_accuracy bir epoch’tan diğerine 0.001’den (yani %0.1’den) az artarsa bunu gerçek bir gelişme sayma
            #15 epochta gelişme olmazsa duracak %0.1 i de saymayacak
        ),

        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,#lr yarıya düşür
            patience=8,
            min_lr=1e-7,
            verbose=1,
            min_delta=0.001
        ),

        ModelCheckpoint(
            DOSYALAR['en_iyi_model'],
            monitor='val_accuracy',
            save_best_only=True,#en iyi" performansı gösterdiğinde kayded
            mode='max',
            verbose=1
        )
    ]


def calculate_light_class_weights():
    """
    Dengeli sınıf ağırlıkları hesaplar
    """
    print("HAFİF CLASS WEIGHTS HESAPLANIYOR...")

    train_dir = 'data/train'
    class_counts = []

    # Her sınıftaki görsel sayısını say
    for class_name in CLASS_NAMES:
        class_path = os.path.join(train_dir, class_name)
        count = len([f for f in os.listdir(class_path) if f.endswith(('.jpg', '.png', '.jpeg'))])
        class_counts.append(count)

    total = sum(class_counts)
    class_weights = {}

    # Her sınıf için ağırlık hesapla
    for i, count in enumerate(class_counts):
        weight = total / (len(class_counts) * count)#ağırlık = toplam / (sınıf_sayısı * ilgili_sınıfın_örnek_sayısı)

        # Sınıfa özel ağırlık ayarlamaları
        if CLASS_NAMES[i] == 'y2':
            weight *= 1.2  # Büyük yangın sınıfı
        elif CLASS_NAMES[i] == 'y0':
            weight *= 1.1  # Yangın yok sınıfı
        elif CLASS_NAMES[i] == 'y3':
            weight *= 0.85  # Gün doğumu sınıfı

        class_weights[i] = round(weight, 3)

    print("HAFİF CLASS WEIGHTS:")
    for i, class_name in enumerate(CLASS_NAMES):
        print(f"   {class_name}: {class_counts[i]} görsel -> weight: {class_weights[i]}")

    return class_weights


def plot_training_history(history, model, test_gen):
    """
    Eğitim geçmişini görselleştirir
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Loss grafiği
    axes[0].plot(history.history['loss'], label='Eğitim Loss', linewidth=2)
    axes[0].plot(history.history['val_loss'], label='Validation Loss', linewidth=2)
    axes[0].set_title('Eğitim vs Validation Loss', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Loss', fontsize=12)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    final_train_loss = history.history['loss'][-1]
    final_val_loss = history.history['val_loss'][-1]
    axes[0].text(0.02, 0.95, f'Son Eğitim Loss: {final_train_loss:.4f}',
                 transform=axes[0].transAxes, fontsize=10,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    axes[0].text(0.02, 0.88, f'Son Validation Loss: {final_val_loss:.4f}',
                 transform=axes[0].transAxes, fontsize=10,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

    # Accuracy grafiği
    axes[1].plot(history.history['accuracy'], label='Eğitim Accuracy', linewidth=2)
    axes[1].plot(history.history['val_accuracy'], label='Validation Accuracy', linewidth=2)
    axes[1].set_title('Eğitim vs Validation Accuracy', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('Accuracy', fontsize=12)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    final_train_acc = history.history['accuracy'][-1]
    final_val_acc = history.history['val_accuracy'][-1]
    best_val_epoch = np.argmax(history.history['val_accuracy'])
    best_val_acc = history.history['val_accuracy'][best_val_epoch]

    axes[1].text(0.02, 0.95, f'Son Eğitim Acc: {final_train_acc * 100:.2f}%',
                 transform=axes[1].transAxes, fontsize=10,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    axes[1].text(0.02, 0.88, f'Son Validation Acc: {final_val_acc * 100:.2f}%',
                 transform=axes[1].transAxes, fontsize=10,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    axes[1].text(0.02, 0.81, f'En İyi Val Acc: {best_val_acc * 100:.2f}% (Epoch {best_val_epoch + 1})',
                 transform=axes[1].transAxes, fontsize=10,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

    # Overfitting analizi
    overfitting_gap = history.history['accuracy'][best_val_epoch] - best_val_acc
    if overfitting_gap > 0.1:
        overfit_color = 'red'
    elif overfitting_gap > 0.05:
        overfit_color = 'orange'
    else:
        overfit_color = 'green'

    axes[1].text(0.02, 0.74, f'Overfitting Gap: {overfitting_gap * 100:.2f}%',
                 transform=axes[1].transAxes, fontsize=10, color=overfit_color,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))

    plt.suptitle(f'Model {model_numara} - Eğitim Geçmişi (4 Sınıf)', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(DOSYALAR['egitim_grafikleri'], dpi=150, bbox_inches='tight')
    plt.show()

    # Confusion Matrix oluştur
    print("\nCONFUSION MATRIX HAZIRLANIYOR...")

    test_gen.reset()
    y_pred = model.predict(test_gen, verbose=0)
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_true = test_gen.classes

    cm = confusion_matrix(y_true, y_pred_classes)

    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
    plt.title(f'Model {model_numara} - Confusion Matrix (4 Sınıf)', fontsize=16, fontweight='bold')
    plt.ylabel('Gerçek Değer', fontsize=12)
    plt.xlabel('Tahmin Edilen Değer', fontsize=12)
    plt.tight_layout()
    plt.savefig(DOSYALAR['confusion_matrix'], dpi=150, bbox_inches='tight')
    plt.show()

    return cm, y_true, y_pred_classes


def main():
    """
    Ana eğitim fonksiyonu
    """
    print("=" * 60)
    print("  4 SINIFLI YANGIN TESPİTİ MODELİ EĞİTİMİ")
    print("=" * 60)
    print(f"  Sınıflar: {CLASS_NAMES}")
    print(f"  Sınıf 0 (y0): Yangın Yok")
    print(f"  Sınıf 1 (y1): Küçük Yangın")
    print(f"  Sınıf 2 (y2): Büyük Yangın")
    print(f"  Sınıf 3 (y3): Gün Doğumu/Batımı")
    print("=" * 60)
    print("  HEDEF: Val Accuracy > %75, Loss < 2.0")
    print("  STRATEJİ: Dengeli Regularization, Optimal LR")
    print("  STRATEJİ: Hafif Class Weights, Transfer Learning")
    print("=" * 60)

    # Veri generator'larını oluştur
    train_gen, val_gen, test_gen, _ = create_data_generators()

    # Sınıf ağırlıklarını hesapla
    class_weights = calculate_light_class_weights()

    # Modeli oluştur
    print("\nOPTİMAL MODEL OLUŞTURULUYOR...")
    model = create_optimal_model()

    # Modeli derle
    model.compile(
        optimizer=Adam(#optimizasyon algoritması
            learning_rate=INITIAL_LR,
            beta_1=0.9,#geçmiş gradientleri(yön ve büyüklük) hatırlayıp güncellemede kullanmak gradientin yönünü düzleştirir
            beta_2=0.999#gradientin büyüklüğünü stabilize eder (learning rate’i uyarlamak için)
        ),
        loss='categorical_crossentropy',#Modelin tahmini ile gerçek sınıf arasındaki farkı ölçer.
        metrics=['accuracy']
    )

    # Callback'leri al
    callbacks = get_optimal_callbacks()

    # Model özeti
    print("\nMODEL ÖZETİ:")
    model.summary()

    # Eğitim
    print("\n" + "=" * 60)
    print("  EĞİTİM BAŞLIYOR...")
    print(f"  Batch Size: {BATCH_SIZE}")
    print(f"  Learning Rate: {INITIAL_LR}")
    print(f"  Epochs: {EPOCHS}")
    print(f"  Class Weights: Aktif")
    print("=" * 60)

    history = model.fit(
        train_gen,
        epochs=EPOCHS,
        validation_data=val_gen,
        callbacks=callbacks,
        class_weight=class_weights,
        verbose=1
    )

    print("\n✓ EĞİTİM TAMAMLANDI!")

    # Grafikleri çiz
    print("\nGRAFİKLER OLUŞTURULUYOR...")
    cm, y_true, y_pred_classes = plot_training_history(history, model, test_gen)

    # Performans değerlendirme
    print("\n" + "=" * 60)
    print("  PERFORMANS DEĞERLENDİRME")
    print("=" * 60)

    test_loss, test_accuracy = model.evaluate(test_gen, verbose=0)
    print(f"  Test Doğruluğu: {test_accuracy * 100:.2f}%")
    print(f"  Test Kaybı: {test_loss:.4f}")

    final_train_loss = history.history['loss'][-1]
    final_val_loss = history.history['val_loss'][-1]
    print(f"  Son Eğitim Kaybı: {final_train_loss:.4f}")
    print(f"  Son Validation Kaybı: {final_val_loss:.4f}")

    best_val_epoch = np.argmax(history.history['val_accuracy'])
    best_val_acc = history.history['val_accuracy'][best_val_epoch]
    overfitting_gap = history.history['accuracy'][best_val_epoch] - best_val_acc

    print(f"  En İyi Val Doğruluğu: {best_val_acc * 100:.2f}%")
    print(f"  Overfitting Oranı: {overfitting_gap * 100:.2f}%")

    # Sınıf bazlı performans
    print("\n" + "=" * 60)
    print("  SINIF BAZINDA PERFORMANS")
    print("=" * 60)
    print(classification_report(y_true, y_pred_classes, target_names=CLASS_NAMES, digits=4))

    # Y3 (gün doğumu) özel analizi
    print("\n" + "=" * 60)
    print("  Y3 (GÜN DOĞUMU) ÖZEL ANALİZİ")
    print("=" * 60)

    y3_index = CLASS_NAMES.index('y3')
    y3_correct = cm[y3_index, y3_index]
    y3_total = sum(cm[y3_index, :])
    y3_accuracy = y3_correct / y3_total if y3_total > 0 else 0

    print(f"  Y3 Doğruluk: {y3_accuracy * 100:.2f}% ({y3_correct}/{y3_total})")

    # Yanlış sınıflandırmaları analiz et
    print(f"\n  Y3 Yanlış Sınıflandırmaları:")
    for i, class_name in enumerate(CLASS_NAMES):
        if i != y3_index and cm[y3_index, i] > 0:
            print(f"    -> {class_name}: {cm[y3_index, i]} görsel")

    # Modeli kaydet
    print("\n" + "=" * 60)
    print("  MODEL KAYDEDİLİYOR...")
    print("=" * 60)

    model.save(DOSYALAR['final_model'])
    with open(DOSYALAR['sinif_isimleri'], 'w', encoding='utf-8') as f:
        json.dump(CLASS_NAMES, f, ensure_ascii=False, indent=2)

    print(f"✓ Final model kaydedildi: {DOSYALAR['final_model']}")
    print(f"✓ Sınıf isimleri kaydedildi: {DOSYALAR['sinif_isimleri']}")
    print(f"✓ Eğitim grafikleri kaydedildi: {DOSYALAR['egitim_grafikleri']}")
    print(f"✓ Confusion matrix kaydedildi: {DOSYALAR['confusion_matrix']}")

    # Sonuç özeti
    print("\n" + "=" * 60)
    print("  EĞİTİM SONUÇ ÖZETİ")
    print("=" * 60)
    print(f"  Model: {model_numara}")
    print(f"  Sınıf Sayısı: {NUM_CLASSES}")
    print(f"  Test Doğruluğu: {test_accuracy * 100:.2f}%")
    print(f"  Test Kaybı: {test_loss:.4f}")

    # Loss değerlendirmesi
    if test_loss < 1.0:
        print("  MÜKEMMEL: Loss değeri çok iyi!")
    elif test_loss < 2.0:
        print("   İYİ: Loss değeri kabul edilebilir seviyede.")
    else:
        print("   ORTA: Loss değeri yüksek, iyileştirilebilir.")

    # Gün doğumu performansı
    if y3_accuracy > 0.85:
        print(f"   GÜN DOĞUMU TESPİTİ: Çok iyi ({y3_accuracy * 100:.1f}%)")
    elif y3_accuracy > 0.70:
        print(f"   GÜN DOĞUMU TESPİTİ: İyi ({y3_accuracy * 100:.1f}%)")
    else:
        print(f"    GÜN DOĞUMU TESPİTİ: Geliştirilmeli ({y3_accuracy * 100:.1f}%)")

    print("=" * 60)
    print("  EĞİTİM TAMAMLANMIŞTIR ✓")
    print("=" * 60)


if __name__ == "__main__":
    main()