# Kodsuz giriş ve tamamlanma ekranı

Bu değişiklik yalnız geliştirme dalındadır. main birleştirilmez, GitHub Pages ve canlı Edge Function otomatik güncellenmez.

## Kullanıcının yapacağı adımlar
1. Çalışan tarihiz-sade-test projesinde mevcut Edge Function kodu, bu daldaki supabase/functions/tarihiz-api/index.ts ile güncellenir. SQL veya tablo silme gerekmez.
2. Edge Functions → Secrets: ANONYMOUS_ENTRY_ENABLED = true eklenir. CODE_PEPPER değiştirilmez; GEMINI_API_KEY ve GEMINI_MODEL korunur.
3. ALLOWED_ORIGINS içinde yerel deneme adresi ve kesinleşecek organizasyon yayın adresi bulunur. Adres https://organizasyon.github.io biçimindedir; depo yolu eklenmez.
4. Anket bağlantısı config.js içindeki feedbackFormUrl alanına eklenir. Google Forms yanıtlayıcılardan oturum/e-posta istemeyecek şekilde ayarlanır. Alan boşken tamamlanma ekranındaki buton devre dışıdır.
5. Yerel test: depo kökünde python -m http.server 8000 --bind 127.0.0.1, sonra http://localhost:8000/platform-v3/. Önceden indirilen tek HTML otomatik güncellenmez; bu dalın dosyaları kullanılmalıdır.
6. Aynı tarayıcıda sayfa yenileme, iki farklı tarayıcıda farklı öğrenci, son etkinlikten tamamlanma ekranı ve yeni katılımcı geçişi denenir. Yayın adresi kesinleşmeden yayın yapılmaz.

## Oturum ve veri
Öğrenci kod veya e-posta girmez. Tarayıcı ilk başlangıçta kriptografik rastgele 256 bit özel devam anahtarı üretir ve API adresine göre localStorage’da saklar. Sunucu anahtarın HMAC özetini mevcut code_hash sütununda saklar; UUID öğrenci kimliğini sunucu oluşturur. Aynı anahtar aynı öğrenciye döner; mükerrer oluşturma unique kısıtı ve conflict-ignore ile önlenir. Her açılışta altı saatlik erişim oturumu alınır. Süresi dolan ekranda sayfa yenilenerek aynı öğrenciye dönülür. Oturum anahtarı URL’ye, loglara veya anket bağlantısına eklenmez.

Depolamaya izin verilmeyen tarayıcıda öğrenci oluşturulmadan hata gösterilir. Tarayıcı verileri silinir veya cihaz değişirse eski öğrenciye otomatik dönüş mümkün değildir. Ortak cihazda Oturumu Kapat / Yeni Katılımcı onaylanmalı; eski öğrenci kayıtları silinmez. Bir cihazda aynı anda tek öğrenci ve tek sekme kullanılmalıdır.

Eski kodlu katılımcılar ve test kayıtları korunur; eski /session API yolu geriye dönük uyumluluk için kalır, öğrenci arayüzünde kod girişi yoktur. Kod üretme Python dosyası korunmuştur. Yeni kayıtların label alanı Anonim-UUID biçimindedir. Yeni giriş özelliği Secrets üzerinden kapatılabilir; genel oturum, sahiplik ve RLS kontrolleri devam eder. Aynı okul IP’si için başlangıç sınırı 5 dakikada 120, aynı devam anahtarı için 20 istektir.

Anket yalnız tüm mevcut konular done durumundaysa ayrı Sorgulamayı Tamamladın ekranında görünür. Konu listesinde ve tek etkinlik özetinde anket yoktur. Bitiren öğrenci tekrar açınca tamamlanma ekranına döner; çalışmalarını salt okunur inceleyebilir. Yeni konu eklendiğinde tamamlanma koşulu yeniden hesaplanır. Anket yanıtlarıyla öğrenci kimliğini otomatik eşleştirme bu değişikliğe dahil değildir. Yapay zekâ tur sayısı değiştirilmemiştir.
