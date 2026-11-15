-- Yalnız test projesinde çalıştırın. Mevcut konuları ve öğrenci kayıtlarını değiştirmez.
begin;
insert into public.tarihiz_topics(id,title,question,sources,demo,pilot)
select id,title,question,sources,demo,pilot from jsonb_to_recordset($topics$
[
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
    "pilot": true
  }
]
$topics$::jsonb) as p(id uuid,title text,question text,sources jsonb,demo boolean,pilot boolean)
on conflict(id) do nothing;
commit;
