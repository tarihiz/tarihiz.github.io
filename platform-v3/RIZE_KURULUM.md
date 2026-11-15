RİZE VE NUMARALI KONU LİSTESİ — TEST KURULUMU

1. Supabase tarihiz-sade-test → SQL Editor → New query: rize-ve-siralama.sql içeriğini yapıştırıp Run. Eski konuların içerikleri ve öğrenci kayıtları korunur; yalnız sıraları güncellenir. Eksik pilot konular eklenir.
2. Aynı TEST projesinde Edge Functions → mevcut fonksiyon → Code → index.ts içeriğini paketteki index.ts ile tamamen değiştirip Deploy updates. Yeni fonksiyon oluşturmayın. Mevcut URL /super-worker ve Secrets aynı kalsın. SQL adımını önce yapın.
3. TarihIz_Pilot.html dosyasını mevcut HTML’nin yerine koyun. pilot-gorseller klasörünü HTML ile AYNI klasöre çıkarın, mevcut klasörle birleştirin. Araya yeni Rize veya paket klasörü koymayın. Paket beş konunun bütün görsellerini içerir.
4. Tarihİz klasöründe PowerShell: py -m http.server 8000 --bind 127.0.0.1
Sunucu açıksa tekrar başlatmayın. http://localhost:8000/TarihIz_Pilot.html sayfasını Ctrl+F5 ile yenileyip aynı kodla giriş yapın.

Doğru Rize görsel yolu: Tarihİz/pilot-gorseller/rize-ulasim/kaynak.jpg
SQL tekrar çalıştırılabilir. Canlı projeye uygulamayın.
Yeni konuların sırasını Supabase tarihiz_topics tablosundaki sort_order alanıyla yönetin (10,20,30...). Ekran numarası 1,2,3... otomatik oluşur; etkinlik kimlikleri değişmez.
Rize fotoğrafının kesin tarihi bilinmiyor; listedeki yeri Cumhuriyet dönemi bağlamındaki editoryal sıralamadır. 2024 gazete metninin yayın tarihidir.
