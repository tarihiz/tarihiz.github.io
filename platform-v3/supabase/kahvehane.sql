-- Yalnız tarihiz-sade-test projesinde çalıştırın. Mevcut kayıtları değiştirmez.
begin;
insert into public.tarihiz_topics(id,title,question,sources,demo,pilot)
select id,title,question,sources,demo,pilot from jsonb_to_recordset($topics$
[
  {
    "id": "20270000-0000-4000-8000-000000000004",
    "title": "Osmanlı’da Kahvehaneler ve Gündelik Yaşam",
    "question": "Bu minyatürden hareketle, kahvehanelerin Osmanlı toplumunun gündelik yaşamındaki yeri hakkında hangi çıkarımlarda bulunabiliriz?",
    "demo": false,
    "pilot": true,
    "sources": [
      {
        "id": "osmanli-kahvehane",
        "title": "Bir Osmanlı kahvehanesi tasviri",
        "image": "pilot-gorseller/osmanli-kahvehane/kaynak.jpg",
        "image_ready": true,
        "reference_url": "https://tr.wikipedia.org/wiki/Kahvehane",
        "image_credit_url": "https://commons.wikimedia.org/wiki/File:MeddahOttomman.png",
        "description": "Görsel, Vikipedi’deki Kahvehane maddesinde bir Osmanlı kahvehanesinde meddahı betimleyen minyatür olarak sunulmaktadır. Kalabalık bir iç mekânda farklı gruplar hâlindeki kişiler, fincanlar, kitap benzeri nesneler ve oyun düzenekleri görülmektedir. Eserin sanatçısı, özgün yazması ve üretim amacı başvurulan dosya kaydında belirtilmemiştir. Bir tasvirin görülebilen ayrıntılarıyla bu ayrıntılardan yapılan yorumlar birbirinden ayrılmalıdır.",
        "metadata": {
          "Kaynak türü": "Minyatürün dijital kopyası",
          "İlişkilendirilen bağlam": "Osmanlı kahvehanesi",
          "Sanatçı": "Başvurulan kayıtta belirtilmemiştir",
          "Tarih": "Kesin tarih doğrulanmamıştır; Commons açıklamasında muhtemelen 16. yüzyıl denmektedir",
          "Özgün eser / koleksiyon": "Başvurulan kayıtta belirtilmemiştir",
          "Dijital erişim": "Vikipedi / Wikimedia Commons",
          "Dosya adı": "MeddahOttomman.png",
          "Kaynak zinciri": "Commons dosya kaydı kaynak olarak bir Onedio sayfasını göstermektedir",
          "Hak bilgisi": "Commons kaydında ABD’de kamu malı etiketi bulunmaktadır",
          "Sunum": "Yüklenen PNG’den JPEG görüntüleme kopyası; kırpma veya içerik ekleme yapılmamıştır"
        }
      }
    ]
  }
]
$topics$::jsonb) as p(id uuid,title text,question text,sources jsonb,demo boolean,pilot boolean)
on conflict(id) do nothing;
commit;
