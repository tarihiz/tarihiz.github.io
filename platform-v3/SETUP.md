# Tarihİz · Konu Başlıkları

Öğrenci kod veya e-posta girmeden anonim oturum açar, konu başlığını seçer ve kaynağı inceler. İlk yanıt gönderildikten sonra kilitlenir. Gemini soruları ve öğrenci yanıtları ayrı zaman damgalarıyla tutulur. Bir soruyu yanıtladıktan sonra öğrenci son değerlendirmeye geçebilir. Tamamlanmış bir konu yalnızca okunabilir. Yazı alanları kısa bir duraklamadan sonra taslak olarak kaydedilir.

Güncel çalışan projede kodsuz girişe geçiş için [ANONIM_GIRIS_KURULUM.md](ANONIM_GIRIS_KURULUM.md) adımlarını izleyin. Aşağıdaki bölüm ilk veritabanı kurulumuna aittir; çalışan projede SQL dosyalarını tekrar çalıştırmayın.

## Ayrı test ortamında ilk kurulum

1. Boş bir test Supabase projesinde SQL Editor ile `supabase/schema.sql` çalıştırın. Önceki şemayı içeren bir test projesinde **yalnız** `supabase/migrations/001_topics.sql` kullanın. Yeni tablolar `tarihiz_topics` ve `tarihiz_topic_works`. Eski çalışmalar kendi tablosunda kalır.
2. Aşağıdaki pilot SQL dosyasını uygulayın.
3. Test projesinin Edge Secrets alanında `GEMINI_API_KEY`, `GEMINI_MODEL`, `CODE_PEPPER` ve arayüzün origin değerini içeren `ALLOWED_ORIGINS` ayarlayın. Oturum ve kod doğrulama için mevcut pepper korunmalıdır. Kodsuz giriş için `ANONYMOUS_ENTRY_ENABLED=true` ekleyin. `api/provision_codes.py` eski kodlu akış için korunmuştur. Veritabanı erişimi yalnızca Edge Function'ın service role anahtarıyla yapılır.
4. Test projesinde `supabase/functions/tarihiz-api/index.ts` dosyasını `tarihiz-api` olarak kurun. Bu işlev kendi anonim oturumunu doğruladığı için **yalnız bu işlevde** ağ geçidinin legacy JWT doğrulamasını kapatın. `config.js` içindeki `apiBase` değerini test işlevinin tam HTTPS adresine ayarlayın. Mevcut config.js çalışan tarihiz-sade-test işlevine yönelir. Depo kökünden statik sunucu çalıştırıp `/platform-v3/` sayfasını açın. Bu dal dağıtım yapmaz.
5. Pilot öncesinde gerçek belgeleri ve künyelerini, anonim oturumu, model erişimini ve mobil görünümü test projesinde deneyin. İki ayrı tarayıcı ve iki konu ile kayıt yalıtımını, sohbeti, yenileme sonrası devam etmeyi ve tamamlanan yanıtlardaki kilidi kontrol edin.

## Araştırma kayıtları

`participant_id` öğrencinin tüm konularını birleştirir. `topic_id` aynı konuya ikinci çalışma açılmasını engelleyen bileşik anahtarın diğer parçasıdır. `activity_snapshot` özgün başlık, soru, kaynak kimlikleri ve kullanılan içerikleri saklar. `state` içinde aşama, taslak, zamanlı ilk ve son yanıtlar, sıralı konuşma ve bitirme zamanı bulunur. `created_at` ve `updated_at` çalışma kaydına aittir.

## Test

`platform-v3/` içinde `node --test tests/*.test.cjs` çalıştırın (Node 20+). HTTP testleri gerçek Edge giriş noktasını çağırır. Veritabanı ve Gemini ağ sınırları bellek içi benzetimlerdir. Python dosyaları ve önceki testleri eski API için korunur.

## İki pilot etkinlik

Var olan test projesinde (konu tabloları kuruluysa) yalnızca **supabase/pilot.sql** dosyasını çalıştırın. Dosya iki etkinliği sabit kimliklerle ekler. Eski konular ve öğrenci çalışmaları silinmez. Pilot kataloğu yalnız `pilot=true` satırlarını sunar. Boş test projesinde önce schema.sql gerekir. Yeniden çalıştırmak elle doğrulanan künye ve görsel durumunu ezmez. JSON taslak ve SQL içeriğinin eşitliği test edilir.

- `pilot-gorseller/altin-elbiseli-adam/kaynak.jpg`: müze görselinin özgün eser fotoğrafı mı, modern rekonstrüksiyon mu olduğunu ve fotoğrafın kaynağını önce doğrulayın. Table Editor → tarihiz_topics → ilgili satır → sources[0].metadata içindeki “Görsel türü”nü, gerekirse açıklamayı güncelleyin.
- `pilot-gorseller/trabzon-okul-haritasi/kaynak.jpg`: EPL013’ün tam, kırpılmamış taramasını koyun; yazı, alt not veya işaret silmeyin. Lejant SALT kaydındaki Osmanlıca aktarım üzerinden hazırlanmıştır. “İnkılaptan önce/sonra” ayrımını özgün belgeyle karşılaştırın; kayıtta doğrudan 1908 yazmıyor. Kaynak kaydındaki kullanım koşullarını yükleme öncesinde gözden geçirin.
- Yollar platform-v3 klasörüne göredir. İki satırda da `sources[0].image` önceden tanımlıdır. Dosya sunucuda erişilebilir ve künyesi doğrulanmış olduğunda ilgili satırın `sources[0].image_ready` değerini true yapın; diğer JSON alanlarını koruyun. Her yeni çalışma kaynağın o andaki kopyasını alır. Daha önce açılmış uzman denemesini değiştirmeden yeni görüntü durumunu denemek için yeni bir test kodu kullanın.
- Gold Hall No. 1: https://nmrk.kz/en/structure/exhibition-activities/ ; SALT EPL013: https://archives.saltresearch.org/handle/123456789/99196 . Bu sayfalar bilgi/künye referansıdır; dış görsel bağlantıları kullanılmaz.
- Uzman incelemesinde test koduyla giriş yapın, iki konuyu iki farklı sırada deneyin. Telefonda Kaynağı İncele / Değerlendirmem arasında geçiş yapıp taslağın kaldığını, ilk ve son sorunun aynı olduğunu kontrol edin. Model metin tabanlıdır; görsel baytları gönderilmez.
