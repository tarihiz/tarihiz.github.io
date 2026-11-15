-- Idempotent catalog seed; existing content is preserved.
alter table public.tarihiz_topics add column if not exists pilot boolean not null default false;
begin;
alter table public.tarihiz_topics add column if not exists sort_order integer not null default 1000;
insert into public.tarihiz_topics(id,title,question,sources,demo,pilot,sort_order)
select id,title,question,sources,demo,pilot,sort_order from jsonb_to_recordset($topics$
[
  {
    "id": "20270000-0000-4000-8000-000000000001",
    "title": "Altın Elbiseli Adam: Giyim ve Kuşam Üzerine",
    "question": "Altın Elbiseli Adam'a ait buluntulardan hareketle, bu kişinin yaşadığı toplum hakkında neler söyleyebiliriz?",
    "sources": [
      {
        "id": "altin-elbiseli-adam",
        "title": "Altın Elbiseli Adam",
        "image": "pilot-gorseller/altin-elbiseli-adam/kaynak.jpg",
        "image_ready": true,
        "description": "Altın Elbiseli Adam, Kazakistan'daki Esik Kurganı'nda gerçekleştirilen arkeolojik kazılarda ortaya çıkarılan buluntularla tanınmaktadır. Kazakistan Cumhuriyeti Ulusal Müzesi, bu buluntuları Saka dönemiyle ilişkilendirmektedir.",
        "metadata": {
          "Konu": "Altın Elbiseli Adam",
          "Buluntu yeri": "Esik Kurganı, Kazakistan",
          "İlişkilendirildiği kültür": "Saka",
          "Kaynak kurumu": "Kazakistan Cumhuriyeti Ulusal Müzesi",
          "Sergi": "The Gold Hall No. 1",
          "Görsel türü": "Modern kıyafet rekonstrüksiyonunun fotoğrafı",
          "Rekonstrüksiyon": "Krym Altynbekov",
          "Fotoğraf": "Derzsi Elekes Andor, 13 Kasım 2012",
          "Görsel kaydı": "Wikimedia Commons · File:Sun emperor.JPG",
          "Fotoğraf lisansı": "CC BY-SA 3.0 · https://creativecommons.org/licenses/by-sa/3.0/"
        },
        "reference_url": "https://nmrk.kz/en/structure/exhibition-activities/",
        "image_credit_url": "https://commons.wikimedia.org/wiki/File:Sun_emperor.JPG"
      }
    ],
    "demo": false,
    "pilot": true,
    "sort_order": 20
  },
  {
    "id": "20270000-0000-4000-8000-000000000002",
    "title": "1914’te Doğu Karadeniz’de Eğitime Erişim",
    "question": "1914 tarihli bu haritadan hareketle Doğu Karadeniz'deki çocukların eğitim olanakları hakkında hangi çıkarımlarda bulunabiliriz?",
    "sources": [
      {
        "id": "trabzon-okul-haritasi",
        "title": "Trabzon Vilayeti okul haritası",
        "image": "pilot-gorseller/trabzon-okul-haritasi/kaynak.jpg",
        "image_ready": true,
        "description": "Bu harita, Osmanlı Devleti'nin son döneminde Trabzon Vilayeti'ndeki okulları göstermek amacıyla hazırlanmış ve Eylül 1914'te Matbaa-i Âmire tarafından yayımlanmıştır.",
        "metadata": {
          "Belge": "Trabzon Vilayeti’ndeki okulları gösteren harita, No. 13",
          "Tarih": "Eylül 1330 / Eylül 1914",
          "Yayıncı": "Matbaa-i Âmire",
          "Tür": "Tarihsel harita",
          "Arşiv": "SALT Araştırma",
          "Envanter numarası": "EPL013",
          "Görsel kaynağı": "SALT Araştırma, EPL013, No. 13",
          "Lisans": "CC BY-NC-ND 4.0 · https://creativecommons.org/licenses/by-nc-nd/4.0/"
        },
        "reference_url": "https://archives.saltresearch.org/handle/123456789/99196",
        "legend": [
          "Kırmızı daireler: Arşiv aktarımında “kable’l-inkılâb” (inkılaptan önce) var olan okullar.",
          "Siyah daireler: İnkılaptan sonra Eylül 1914’e kadar kurulan ve açılan okullar.",
          "Çift çizgili daireler: Kız okulları.",
          "Daire içindeki bölmeler: Okulun dershane sayısı.",
          "Dairenin üzerindeki rakam: Kasabada o türden kaç okul bulunduğu.",
          "Üçgenler: Numune mektepleri.",
          "Karma okullar, erkek okulları arasında gösterilmiştir."
        ]
      }
    ],
    "demo": false,
    "pilot": true,
    "sort_order": 40
  },
  {
    "id": "20270000-0000-4000-8000-000000000003",
    "title": "Göbeklitepe’de Toplumsal Yaşamın İzleri",
    "question": "Göbeklitepe’deki yapı ve buluntulardan hareketle, burada yaşayan insanların toplumsal yaşamları hakkında hangi çıkarımlarda bulunabiliriz?",
    "sources": [
      {
        "id": "gobeklitepe-13",
        "title": "Kazı alanının genel görünümü",
        "image": "pilot-gorseller/gobeklitepe-13/kaynak.jpg",
        "image_ready": true,
        "description": "Fotoğrafta taş duvarlarla çevrili alanlar ve farklı konumlarda dikilitaşlar görülmektedir. Üst örtü, yürüyüş yolu ve ziyaretçiler günümüze aittir.",
        "metadata": {
          "Yer": "Göbeklitepe, Şanlıurfa",
          "Dönem": "Çanak Çömleksiz Neolitik; yerleşim yaklaşık MÖ 9600–7750",
          "Görsel türü": "Arkeolojik kalıntıların günümüzde çekilmiş fotoğrafı",
          "Kaynak": "Taş Tepeler — Göbeklitepe",
          "Görsel kaydı": "Gobeklitepe-13",
          "Sayfadaki fotoğraf kredisi": "Moritz Kinzel ve Benny Waszk (tek tek fotoğrafların çekenleri belirtilmemiştir)",
          "Fotoğraf tarihi": "Kaynak sayfasında belirtilmemiştir",
          "Sayfa metni": "Lee Clare ve Jonas Breuers"
        },
        "reference_url": "https://tastepeler.org/yerlesmeler/gobeklitepe"
      },
      {
        "id": "gobeklitepe-10",
        "title": "Yapı kalıntılarının üstten görünümü",
        "image": "pilot-gorseller/gobeklitepe-10/kaynak.jpg",
        "image_ready": true,
        "description": "Üstten çekilmiş fotoğrafta farklı biçim ve büyüklüklerde yapı kalıntıları görülmektedir. Fotoğraftaki yürüyüş yolu günümüze aittir.",
        "metadata": {
          "Yer": "Göbeklitepe, Şanlıurfa",
          "Dönem": "Çanak Çömleksiz Neolitik; yerleşim yaklaşık MÖ 9600–7750",
          "Görsel türü": "Arkeolojik kalıntıların günümüzde çekilmiş fotoğrafı",
          "Kaynak": "Taş Tepeler — Göbeklitepe",
          "Görsel kaydı": "Gobeklitepe-10",
          "Sayfadaki fotoğraf kredisi": "Moritz Kinzel ve Benny Waszk (tek tek fotoğrafların çekenleri belirtilmemiştir)",
          "Fotoğraf tarihi": "Kaynak sayfasında belirtilmemiştir",
          "Sayfa metni": "Lee Clare ve Jonas Breuers"
        },
        "reference_url": "https://tastepeler.org/yerlesmeler/gobeklitepe"
      },
      {
        "id": "gobeklitepe-1",
        "title": "Hayvan kabartmalı dikilitaş",
        "image": "pilot-gorseller/gobeklitepe-1/kaynak.jpg",
        "image_ready": true,
        "description": "Taşın yüzeyinde yandan gösterilmiş bir hayvan kabartması görülmektedir. Taşı çevreleyen destek bandı ve fotoğraf renk kartı günümüz belgeleme ve koruma çalışmalarına aittir.",
        "metadata": {
          "Yer": "Göbeklitepe, Şanlıurfa",
          "Dönem": "Çanak Çömleksiz Neolitik; yerleşim yaklaşık MÖ 9600–7750",
          "Görsel türü": "Arkeolojik kalıntıların günümüzde çekilmiş fotoğrafı",
          "Kaynak": "Taş Tepeler — Göbeklitepe",
          "Görsel kaydı": "Gobeklitepe-1",
          "Sayfadaki fotoğraf kredisi": "Moritz Kinzel ve Benny Waszk (tek tek fotoğrafların çekenleri belirtilmemiştir)",
          "Fotoğraf tarihi": "Kaynak sayfasında belirtilmemiştir",
          "Sayfa metni": "Lee Clare ve Jonas Breuers"
        },
        "reference_url": "https://tastepeler.org/yerlesmeler/gobeklitepe"
      },
      {
        "id": "gobeklitepe-2",
        "title": "Farklı figürler taşıyan T biçimli dikilitaş",
        "image": "pilot-gorseller/gobeklitepe-2/kaynak.jpg",
        "image_ready": true,
        "description": "T biçimli taşın yüzeyinde farklı figürler ve çizgisel şekiller görülmektedir. Fotoğraf, taşın bir yüzünü göstermektedir.",
        "metadata": {
          "Yer": "Göbeklitepe, Şanlıurfa",
          "Dönem": "Çanak Çömleksiz Neolitik; yerleşim yaklaşık MÖ 9600–7750",
          "Görsel türü": "Arkeolojik kalıntıların günümüzde çekilmiş fotoğrafı",
          "Kaynak": "Taş Tepeler — Göbeklitepe",
          "Görsel kaydı": "Gobeklitepe-2",
          "Sayfadaki fotoğraf kredisi": "Moritz Kinzel ve Benny Waszk (tek tek fotoğrafların çekenleri belirtilmemiştir)",
          "Fotoğraf tarihi": "Kaynak sayfasında belirtilmemiştir",
          "Sayfa metni": "Lee Clare ve Jonas Breuers"
        },
        "reference_url": "https://tastepeler.org/yerlesmeler/gobeklitepe"
      },
      {
        "id": "gobeklitepe-7",
        "title": "Taş üzerindeki kabartmanın yakın görünümü",
        "image": "pilot-gorseller/gobeklitepe-7/kaynak.jpg",
        "image_ready": true,
        "description": "Fotoğrafta taş yüzeyinden dışarı doğru çıkıntı yapan bir hayvan betimi yakın planda görülmektedir. Bu açı yapının bütününü göstermemektedir.",
        "metadata": {
          "Yer": "Göbeklitepe, Şanlıurfa",
          "Dönem": "Çanak Çömleksiz Neolitik; yerleşim yaklaşık MÖ 9600–7750",
          "Görsel türü": "Arkeolojik kalıntıların günümüzde çekilmiş fotoğrafı",
          "Kaynak": "Taş Tepeler — Göbeklitepe",
          "Görsel kaydı": "Gobeklitepe-7",
          "Sayfadaki fotoğraf kredisi": "Moritz Kinzel ve Benny Waszk (tek tek fotoğrafların çekenleri belirtilmemiştir)",
          "Fotoğraf tarihi": "Kaynak sayfasında belirtilmemiştir",
          "Sayfa metni": "Lee Clare ve Jonas Breuers"
        },
        "reference_url": "https://tastepeler.org/yerlesmeler/gobeklitepe"
      }
    ],
    "demo": false,
    "pilot": true,
    "sort_order": 10
  },
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
    ],
    "sort_order": 30
  },
  {
    "id": "20270000-0000-4000-8000-000000000005",
    "title": "Rize’de Köyden Şehre Ulaşım ve Gündelik Yaşam",
    "question": "Bu fotoğraf ve metinden hareketle, ulaşımın Rize’de köy ve şehir arasındaki gündelik ilişkilerde nasıl bir yeri olduğunu söyleyebiliriz?",
    "demo": false,
    "pilot": true,
    "sort_order": 50,
    "sources": [
      {
        "id": "rize-kamyon-fotografi",
        "title": "Kamyonlarla yolculuk",
        "image": "pilot-gorseller/rize-ulasim/kaynak.jpg",
        "image_ready": true,
        "description": "Fotoğrafı ve Rize’de geçmişteki ulaşımı anlatan gazete metnini birlikte incele. Fotoğrafta görebildiklerinle metinden öğrendiklerini karşılaştır.",
        "metadata": {
          "Kaynak türü": "Tarihsel fotoğrafın dijital kopyası",
          "Fotoğrafçı": "Belirtilmemiştir",
          "Çekim tarihi": "Kesin tarih doğrulanmamıştır",
          "Özgün arşiv": "Belirtilmemiştir",
          "Bağlam": "Rize’de geçmişte ulaşım; kullanıcı tarafından paylaşılan görsel"
        },
        "reference_url": "https://www.tekbayrak.com.tr/Haber/TARIHE-RIZE-YOLCULUGU-24597.html",
        "companion": {
          "id": "rize-minibus-yerine-kamyon",
          "title": "Minibüs Yerine Kamyon",
          "text": "Mahalle ve köylerde yaşayan insanlar haftanın belirli günlerinde şehir merkezine gelerek eksiklerini alıyorlardı. Mahallelerden kamyonlar üzerinde seyahat eden Rizeliler balık istifi gibi kamyonlarla tarihi yollardan şehir merkezine gelirlerdi. Rize eski yolu olan İyidere tarafındaki yol ise Üniversite önünden geçerek şehir merkezine gelirlerdi.\n\nKöylerden kamyonlara binen insanlar Pazartesi ve Cuma günleri kamyonlara binerek köylerden ve ilçelerden şehir merkezine gelerek günlük alış verişlerini yaparak tekrar kamyonlarla köy ve mahallelerine dönerlerdi. Köylerden getirilen ürünler Pazar yerlerine satıldıktan sonra köy ve mahallelerden gelen Rizeliler elde ettikleri gelirler ile Tuz, Şeker gibi ihtiyaçlarını alarak dönüş yoluna geçiyorlardı.",
          "metadata": {
            "Yazar": "Tufan Kuleli",
            "Yazı": "Tarihe Rize Yolculuğu",
            "Yayın": "Tek Bayrak Gazetesi",
            "Yayın tarihi": "26 Ağustos 2024",
            "Kaynak türü": "Geçmişi anlatan, sonradan yazılmış gazete metni",
            "Not": "Yayın tarihi fotoğrafın çekim tarihi değildir. Alıntıdaki yazım korunmuştur."
          }
        }
      }
    ]
  }
]
$topics$::jsonb) as p(id uuid,title text,question text,sources jsonb,demo boolean,pilot boolean,sort_order integer)
on conflict(id) do update set sort_order=excluded.sort_order;
commit;
