GÖBEKLİTEPE — TEST KURULUMU

1. ZIP içindeki TarihIz_Pilot.html dosyasını ve pilot-gorseller klasörünü mevcut Tarihİz klasörüne çıkarın. HTML dosyasını değiştirin; klasörleri birleştirin. Önceki iki konunun görsellerini silmeyin.
2. Supabase tarihiz-sade-test projesinde SQL Editor açın. Paketteki gobeklitepe.sql metnini yapıştırıp Run düğmesine basın. Bu dosya yalnızca Göbeklitepe konusunu ekler; mevcut kayıtları silmez. Tekrar çalıştırılması aynı konuyu çoğaltmaz.
3. Tarihİz klasöründe PowerShell açın:
   py -m http.server 8000 --bind 127.0.0.1
   Sunucu zaten açıksa tekrar çalıştırmayın.
4. Tarayıcıda http://localhost:8000/TarihIz_Pilot.html adresini açın ve Ctrl+F5 ile yenileyin. Daha önce çalışan aynı katılım koduyla giriş yapın.
5. Göbeklitepe konusunu seçin. Görsel 1–5 düğmeleriyle fotoğraflar arasında geçiş yapın. Her fotoğraf büyütülebilir.

Bu paket test API’sini kullanır. Yeni Edge Function dağıtımı gerekmez. Canlı projeye uygulanmamalıdır.
Kaynak: https://tastepeler.org/yerlesmeler/gobeklitepe
Sayfadaki fotoğraf kredisi: Moritz Kinzel ve Benny Waszk. Tek fotoğraf bazında çeken kişi ve çekim tarihi belirtilmemiştir.
Gemini’ye kaynakların açıklamaları aktarılır; bu sürümde fotoğraf dosyaları Gemini’ye gönderilmez.
