# Tarihİz yayın hazırlığı

Kaynak: ercankocan/tarihiz-v2, feature/tarihiz-sade dalı.
Uygulama platform-v3/ altındadır. Kök index.html buraya yönlendirir.
Bu dal main ile birleştirilmeden yayınlanmaz. Eski Render dosyaları ve eski assets/banner.png korunmuştur; arayüz Supabase kullanır.

Supabase projesi: tarihiz-sade-test, akfkogdwfcpuyoksiuia.
Kullanıcı Edge Function güncellemesini, ANONYMOUS_ENTRY_ENABLED=true ve ALLOWED_ORIGINS içine https://tarihiz.github.io eklediğini bildirdi.
Anket: https://forms.gle/6Lq6VD2SU8MMCKp26

Test: node --test platform-v3/tests/*.test.cjs (23 test).
Yayın öncesi gerçek tarayıcıdan kodsuz giriş, kaynak görselleri, Gemini yanıtı, son değerlendirme ve bütün konular sonrası anket kontrol edilmelidir.
GitHub Pages mevcut main yayın ayarı korunur; bu PR otomatik birleştirilmez. Supabase SQL dosyaları tekrar çalıştırılmaz, mevcut öğrenci verileri korunur.
