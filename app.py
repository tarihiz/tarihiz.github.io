# ============================================================
# TARİHİZ
# Tarihî İddialar İçin Kaynak Eleştirisi Tabanlı
# Yapay Zekâ Asistanı
#
# TAM ÇALIŞAN SÜRÜM
# Gemini + Tavily + OpenAlex + Gradio
# ============================================================


# ============================================================
# 0. KÜTÜPHANELER
# ============================================================

# Kurulum icin requirements.txt dosyasini kullanin.

import json
import re
import time
import random
import base64
import mimetypes
import html
import traceback
import requests

from urllib.parse import urlparse

import gradio as gr

import os
from pathlib import Path
from google import genai
from tavily import TavilyClient


# ============================================================
# 1. VARSA ESKİ GRADIO'YU KAPAT
# ============================================================

# Bagimsiz sunucuda eski Colab oturumunu kapatma gerekmiyor.


# ============================================================
# 2. API ANAHTARLARI
# ============================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY bulunamadı. "
        "Sunucunun ortam degiskenlerini kontrol edin."
    )

if not TAVILY_API_KEY:
    raise ValueError(
        "TAVILY_API_KEY bulunamadı. "
        "Sunucunun ortam degiskenlerini kontrol edin."
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)

tavily = TavilyClient(
    api_key=TAVILY_API_KEY
)

print("API bağlantıları hazır ✅")


# ============================================================
# 3. BANNER GÖRSELİ
# ============================================================

# Colab dosya yukleme penceresi yerine repodaki assets/ dosyasini kullan.
# Orijinal banner gorselini assets/banner.png olarak yukleyebilirsiniz.
assets = Path(__file__).resolve().parent / "assets"
assets.mkdir(exist_ok=True)
banner_file = next((p for p in (
    assets / "banner.png", assets / "banner.jpg", assets / "banner.jpeg", assets / "banner.webp"
) if p.is_file()), None)
if banner_file:
    mime_type = mimetypes.guess_type(str(banner_file))[0] or "image/png"
    banner_base64 = base64.b64encode(banner_file.read_bytes()).decode("ascii")
    banner_url = f"data:{mime_type};base64,{banner_base64}"
else:
    # Orijinal banner gorseli eklenene kadar gecici, yerel SVG fonu.
    fallback_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="550" viewBox="0 0 1600 550">'
        '<defs><linearGradient id="g" x2="1" y2="1"><stop stop-color="#142237"/>'
        '<stop offset="1" stop-color="#574934"/></linearGradient></defs>'
        '<rect width="1600" height="550" fill="url(#g)"/>'
        '</svg>'
    )
    banner_url = "data:image/svg+xml;base64," + base64.b64encode(fallback_svg.encode()).decode()
print("Banner konfigürasyonu hazır ✅")


# ============================================================
# 4. GEMINI GÜVENLİ ÇALIŞTIRMA
# ============================================================

def gemini_ile_calistir(prompt):

    modeller = [
        "gemini-3.8-flash",
        "gemini-3.7-flash"
    ]

    son_hata = None

    for model in modeller:

        for deneme in range(3):

            try:

                interaction = client.interactions.create(
                    model=model,
                    input=prompt
                )

                return interaction.output_text

            except Exception as e:

                son_hata = e
                hata = str(e).lower()

                if (
                    "503" in hata
                    or "service_unavailable" in hata
                    or "high demand" in hata
                    or "429" in hata
                ):

                    bekleme = (
                        (2 ** deneme) * 3
                        + random.uniform(0, 2)
                    )

                    print(
                        f"Gemini yoğun. "
                        f"{bekleme:.1f} saniye bekleniyor..."
                    )

                    time.sleep(bekleme)

                else:
                    raise e

        print(
            f"{model} kullanılamadı, "
            "diğer modele geçiliyor..."
        )

    raise RuntimeError(
        f"Gemini modellerine ulaşılamadı: {son_hata}"
    )


# ============================================================
# 5. JSON AYIKLAMA
# ============================================================

def json_ayikla(metin):

    metin = str(metin).strip()

    metin = re.sub(
        r"^```(?:json)?\s*",
        "",
        metin,
        flags=re.IGNORECASE
    )

    metin = re.sub(
        r"\s*```$",
        "",
        metin
    )

    try:
        return json.loads(metin)
    except:
        pass

    ilk = metin.find("{")
    son = metin.rfind("}")

    if ilk != -1 and son != -1:

        try:
            return json.loads(
                metin[ilk:son + 1]
            )
        except:
            pass

    ilk = metin.find("[")
    son = metin.rfind("]")

    if ilk != -1 and son != -1:

        try:
            return json.loads(
                metin[ilk:son + 1]
            )
        except:
            pass

    raise ValueError(
        "Gemini çıktısı JSON olarak çözülemedi:\n\n"
        + metin[:1500]
    )


# ============================================================
# 6. OPENALEX ABSTRACT DÖNÜŞTÜRME
# ============================================================

def abstract_olustur(inverted_index):

    if not inverted_index:
        return ""

    kelimeler = []

    for kelime, konumlar in inverted_index.items():

        for konum in konumlar:
            kelimeler.append(
                (konum, kelime)
            )

    kelimeler.sort(
        key=lambda x: x[0]
    )

    return " ".join(
        kelime
        for _, kelime in kelimeler
    )


# ============================================================
# 7. OPENALEX
# ============================================================

def openalex_akademik_ara(
    sorgu,
    sonuc_sayisi=10
):

    url = "https://api.openalex.org/works"

    params = {
        "search": sorgu,
        "per_page": sonuc_sayisi
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# 8. TAVILY
# ============================================================

def tavily_guvenli_ara(**kwargs):

    for deneme in range(4):

        try:

            return tavily.search(
                **kwargs
            )

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout
        ) as e:

            if deneme == 3:
                raise e

            bekleme = 3 * (deneme + 1)

            print(
                f"Tavily bağlantısı kesildi. "
                f"{bekleme} saniye sonra tekrar deneniyor..."
            )

            time.sleep(bekleme)


# ============================================================
# 9. AKADEMİK YAYIN TÜRÜ
# ============================================================

def akademik_tur_cevir(openalex_turu):

    eslesme = {

        "article":
            "Makale",

        "book":
            "Kitap",

        "book-chapter":
            "Kitap Bölümü",

        "dissertation":
            "Tez",

        "proceedings-article":
            "Bildiri Metni",

        "report":
            "Rapor",

        "reference-entry":
            "Ansiklopedi",

        "dataset":
            "Veri Seti",

        "review":
            "Derleme"

    }

    return eslesme.get(
        str(openalex_turu).lower(),
        "Akademik Yayın"
    )


# ============================================================
# 10. WEB KAYNAK TÜRÜ
# ============================================================

def web_turu_bul(url):

    domain = urlparse(
        str(url)
    ).netloc.lower()

    if "wikipedia.org" in domain:
        return "Ansiklopedi"

    if "britannica.com" in domain:
        return "Ansiklopedi"

    if (
        "youtube.com" in domain
        or "youtu.be" in domain
    ):
        return "Video"

    if "substack.com" in domain:
        return "Blog"

    return "Web Sayfası"


# ============================================================
# 11. KAYNAK SINIFI
# ============================================================

def kaynak_sinifi_bul(
    kaynak_turu,
    kaynak_grubu
):

    tur = str(
        kaynak_turu
    ).strip().lower()

    if tur in [
        "makale",
        "kitap",
        "kitap bölümü",
        "bildiri metni",
        "tez",
        "rapor",
        "derleme"
    ]:
        return "İkincil Kaynak"

    if tur in [
        "ansiklopedi",
        "web sayfası"
    ]:
        return "Üçüncül / Başvuru Kaynağı"

    if tur in [
        "haber",
        "blog",
        "video",
        "sosyal medya"
    ]:
        return "Popüler Kaynak"

    if kaynak_grubu == "Akademik":
        return "İkincil Kaynak"

    return "Üçüncül / Başvuru Kaynağı"


# ============================================================
# 12. AKADEMİK BAĞLANTI
# ============================================================

def akademik_baglanti_bul(eser):

    doi = eser.get("doi")

    if doi:
        return doi

    primary = (
        eser.get("primary_location")
        or {}
    )

    landing = primary.get(
        "landing_page_url"
    )

    if landing:
        return landing

    best_oa = (
        eser.get("best_oa_location")
        or {}
    )

    landing = best_oa.get(
        "landing_page_url"
    )

    if landing:
        return landing

    return eser.get(
        "id",
        ""
    )


# ============================================================
# 13. OPENALEX SONUÇLARINI HAZIRLA
# ============================================================

def akademik_kaynaklari_hazirla(
    openalex_json
):

    kaynaklar = []

    for eser in openalex_json.get(
        "results",
        []
    ):

        baslik = (
            eser.get("display_name")
            or ""
        )

        if not baslik:
            continue

        abstract = abstract_olustur(
            eser.get(
                "abstract_inverted_index"
            )
        )

        tur = akademik_tur_cevir(
            eser.get("type")
        )

        kaynaklar.append({

            "kaynak_grubu":
                "Akademik",

            "baslik":
                baslik,

            "yil":
                eser.get(
                    "publication_year",
                    ""
                ),

            "kaynak_turu":
                tur,

            "kaynak_sinifi":
                kaynak_sinifi_bul(
                    tur,
                    "Akademik"
                ),

            "ozet":
                abstract[:3500],

            "doi":
                eser.get("doi"),

            "baglanti":
                akademik_baglanti_bul(
                    eser
                ),

            "atif_sayisi":
                eser.get(
                    "cited_by_count",
                    0
                ),

            "openalex_id":
                eser.get(
                    "id",
                    ""
                )

        })

    return kaynaklar


# ============================================================
# 14. TAVILY SONUÇLARINI HAZIRLA
# ============================================================

def web_kaynaklari_hazirla(
    tavily_json
):

    kaynaklar = []

    for sonuc in tavily_json.get(
        "results",
        []
    ):

        url = sonuc.get(
            "url",
            ""
        )

        tur = web_turu_bul(
            url
        )

        kaynaklar.append({

            "kaynak_grubu":
                "Web",

            "baslik":
                sonuc.get(
                    "title",
                    ""
                ),

            "yil":
                "",

            "kaynak_turu":
                tur,

            "kaynak_sinifi":
                kaynak_sinifi_bul(
                    tur,
                    "Web"
                ),

            "ozet":
                (
                    sonuc.get(
                        "content"
                    )
                    or ""
                )[:3500],

            "baglanti":
                url,

            "atif_sayisi":
                None

        })

    return kaynaklar


# ============================================================
# 15. TEKRARLARI TEMİZLE
# ============================================================

def akademik_tekrarlari_temizle(
    kaynaklar
):

    temiz = []
    gorulen = set()

    for k in kaynaklar:

        anahtar = (
            k.get("doi")
            or k.get("openalex_id")
            or k.get(
                "baslik",
                ""
            ).lower().strip()
        )

        if not anahtar:
            continue

        if anahtar in gorulen:
            continue

        gorulen.add(
            anahtar
        )

        temiz.append(
            k
        )

    return temiz


def web_tekrarlari_temizle(
    kaynaklar
):

    temiz = []
    gorulen = set()

    for k in kaynaklar:

        anahtar = (
            k.get(
                "baglanti",
                ""
            )
            .split("#")[0]
            .rstrip("/")
            .lower()
        )

        if not anahtar:
            continue

        if anahtar in gorulen:
            continue

        gorulen.add(
            anahtar
        )

        temiz.append(
            k
        )

    return temiz


# ============================================================
# 16. GEMINI ARAMA SORGUSU
# ============================================================

def arama_sorgulari_olustur(
    iddia
):

    prompt = f"""
Sen Tarihİz adlı tarih araştırma sisteminin
arama sorgusu hazırlayan modülüsün.

Tarihî iddia:

"{iddia}"

Bu iddiayı araştırmak için iki sorgu üret:

1. web_query:
Genel web araştırması için kısa ve ayırt edici sorgu.

2. academic_query:
OpenAlex akademik literatür araması için,
tercihen İngilizce ve akademik kavramlar içeren sorgu.

Kurallar:

- İddianın doğru olduğunu varsayma.
- İddianın yanlış olduğunu varsayma.
- Destekleyen ve çelişen kanıtların bulunmasına izin ver.
- Gereksiz uzun sorgu üretme.
- Sadece JSON döndür.
- Markdown kullanma.

{{
  "web_query": "...",
  "academic_query": "..."
}}
"""

    cevap = gemini_ile_calistir(
        prompt
    )

    return json_ayikla(
        cevap
    )


# ============================================================
# 17. AKADEMİK SORGUYU İYİLEŞTİR
# ============================================================

def akademik_sorguyu_iyilestir(
    iddia,
    web_kaynaklari,
    ilk_akademik_kaynaklar
):

    web_ozet = [

        {
            "baslik":
                k["baslik"],

            "ozet":
                k["ozet"][:800]
        }

        for k in web_kaynaklari[:5]
    ]

    akademik_ozet = [

        {
            "baslik":
                k["baslik"],

            "ozet":
                k["ozet"][:500]
        }

        for k in ilk_akademik_kaynaklar[:6]
    ]


    prompt = f"""
Aşağıdaki tarihî iddia için OpenAlex'te
ikinci ve daha isabetli bir akademik arama yapılacaktır.

İddia:

"{iddia}"

İlk web sonuçlarından ipuçları:

{json.dumps(web_ozet, ensure_ascii=False)}

İlk akademik sonuçlar:

{json.dumps(akademik_ozet, ensure_ascii=False)}

İddiayı doğrudan test etmeye yarayabilecek akademik
çalışmaları bulduracak daha iyi bir OpenAlex sorgusu üret.

Kurallar:

- Genel ve belirsiz ifadelerden kaçın.
- Kişi, olay, yer, dönem, arkeolojik alan,
  belge türü veya teknik kavramları gerektiğinde kullan.
- Mümkünse İngilizce yaz.
- Sadece JSON döndür.

{{
  "academic_query_refined": "..."
}}
"""

    cevap = gemini_ile_calistir(
        prompt
    )

    veri = json_ayikla(
        cevap
    )

    return veri.get(
        "academic_query_refined",
        ""
    )


# ============================================================
# 18. KAYNAK ELEŞTİRİSİ
# SIKI FİLTRE SÜRÜMÜ
# ============================================================

def kaynaklari_degerlendir(
    iddia,
    kaynaklar
):

    if not kaynaklar:
        return []

    adaylar = []

    for i, k in enumerate(
        kaynaklar
    ):

        adaylar.append({

            "id":
                i,

            "baslik":
                k.get(
                    "baslik",
                    ""
                ),

            "kaynak_grubu":
                k.get(
                    "kaynak_grubu",
                    ""
                ),

            "kaynak_turu":
                k.get(
                    "kaynak_turu",
                    ""
                ),

            "ozet":
                k.get(
                    "ozet",
                    ""
                )[:2000]

        })


    prompt = f"""
Sen Tarihİz adlı tarih araştırma sisteminin
kaynak eleştirisi modülüsün.

Tarihî iddia:

"{iddia}"

Aday kaynaklar:

{json.dumps(adaylar, ensure_ascii=False)}

Her kaynağı yalnızca başlık benzerliğine göre değil,
bu tarihî iddianın değerlendirilmesinde gerçekten
kanıt değeri taşıyıp taşımadığına göre sınıflandır.

--------------------------------------------------
1. İLGİ DÜZEYİ
--------------------------------------------------

Sadece:

"DOĞRUDAN İLGİLİ"
"DOLAYLI İLGİLİ"
"İLGİSİZ"

değerlerinden birini kullan.


DOĞRUDAN İLGİLİ:

Kaynağın temel araştırma konusu, kullandığı tarihî
veya arkeolojik veriler ya da ana bulguları
iddianın merkezindeki önermeyi doğrudan
değerlendirmeye yarıyorsa kullan.


DOLAYLI İLGİLİ:

Kaynak iddiayı tek başına doğrulamaz veya çürütmez;
ancak iddianın kanıt zincirine somut ve anlamlı
bir tarihsel katkı sağlar.

Sadece aynı kişi, dönem, coğrafya veya kavramın
geçmesi dolaylı ilgi için yeterli değildir.


İLGİSİZ:

Aşağıdaki türden çalışmalar tarihî iddianın
kanıtlanmasına ayrıca somut veri sağlamıyorsa
İLGİSİZ kabul edilmelidir:

- tarihsel anlatının sonraki dönemlerde algılanışı,
- popüler kültürdeki temsili,
- edebî veya kültürel kabul tarihi,
- öğretimi veya ders kitaplarındaki yeri,
- tarih yazımındaki popülerleşmesi,
- genel tarih listeleri,
- yalnızca aynı kişi, yer veya dönemden söz eden yayınlar,
- iddiaya ilişkin somut tarihsel veri sunmayan içerikler.


ÖNEMLİ:

Bir kaynak konu hakkında ilginç olabilir ancak
iddianın değerlendirilmesine kanıt sağlamıyorsa
kullanıcıya gösterilmemelidir.


--------------------------------------------------
2. İDDİAYLA İLİŞKİ
--------------------------------------------------

Sadece:

"DESTEKLİYOR"
"ÇELİŞİYOR"
"BELİRSİZ"

değerlerinden birini kullan.


DESTEKLİYOR:

Kaynakta verilen bilgi veya bulgu iddianın
merkezindeki önermeye olumlu kanıt sağlıyorsa.


ÇELİŞİYOR:

Kaynakta verilen bilgi veya bulgu iddiaya
karşı kanıt sağlıyorsa.


BELİRSİZ:

Verilen başlık ve özet bilgisiyle destek veya
çelişki yönü güvenilir biçimde belirlenemiyorsa.


--------------------------------------------------
KURALLAR
--------------------------------------------------

- İddianın doğru olduğunu önceden varsayma.
- İddianın yanlış olduğunu önceden varsayma.
- Sadece anahtar kelime benzerliğini kullanma.
- Başlık yeterli değilse verilen özet bilgisini dikkate al.
- Özet yeterli değilse tahmin etme; BELİRSİZ kullan.
- Atıf sayısını doğruluk ölçütü olarak kullanma.
- Kaynağın itibarı ile iddiayla ilişkisini karıştırma.
- İLGİSİZ kaynakların iddiayla_iliskisi BELİRSİZ olmalıdır.
- DOĞRUDAN İLGİLİ sınıfını ihtiyatlı kullan.
- Uydurma bilgi ekleme.
- Sadece verilen kaynak bilgilerine dayan.
- Sadece JSON döndür.


{{
  "sources": [
    {{
      "id": 0,
      "ilgi_duzeyi": "DOĞRUDAN İLGİLİ",
      "iddiayla_iliskisi": "DESTEKLİYOR",
      "kisa_gerekce": "..."
    }}
  ]
}}
"""

    cevap = gemini_ile_calistir(
        prompt
    )

    veri = json_ayikla(
        cevap
    )

    degerlendirmeler = {

        x.get("id"): x

        for x in veri.get(
            "sources",
            []
        )
    }

    sonuc = []

    for i, kaynak in enumerate(
        kaynaklar
    ):

        d = degerlendirmeler.get(
            i,
            {}
        )

        yeni = kaynak.copy()

        yeni[
            "ilgi_duzeyi"
        ] = d.get(
            "ilgi_duzeyi",
            "İLGİSİZ"
        )

        yeni[
            "iddiayla_iliskisi"
        ] = d.get(
            "iddiayla_iliskisi",
            "BELİRSİZ"
        )

        yeni[
            "degerlendirme_gerekcesi"
        ] = d.get(
            "kisa_gerekce",
            ""
        )

        sonuc.append(
            yeni
        )

    return sonuc


# ============================================================
# 19. NİHAİ DEĞERLENDİRME
# ============================================================

def nihai_degerlendirme(
    iddia,
    kaynaklar
):

    ozet_kaynaklar = []

    for i, k in enumerate(
        kaynaklar
    ):

        ozet_kaynaklar.append({

            "id":
                i,

            "baslik":
                k.get("baslik"),

            "yil":
                k.get("yil"),

            "kaynak_turu":
                k.get(
                    "kaynak_turu"
                ),

            "kaynak_sinifi":
                k.get(
                    "kaynak_sinifi"
                ),

            "ilgi_duzeyi":
                k.get(
                    "ilgi_duzeyi"
                ),

            "iddiayla_iliskisi":
                k.get(
                    "iddiayla_iliskisi"
                ),

            "atif_sayisi":
                k.get(
                    "atif_sayisi"
                ),

            "ozet":
                k.get(
                    "ozet",
                    ""
                )[:1300]

        })


    prompt = f"""
Sen Tarihİz adlı kaynak eleştirisi tabanlı
tarih araştırma sisteminin nihai değerlendirme modülüsün.

Tarihî iddia:

"{iddia}"

Değerlendirilmiş kaynaklar:

{json.dumps(ozet_kaynaklar, ensure_ascii=False)}

Nihai sonuç yalnızca şu dört değerden biri olabilir:

"DESTEKLENİYOR"
"ÇELİŞİYOR"
"TARTIŞMALI"
"YETERLİ KANIT YOK"


Kurallar:

1. İddianın doğru veya yanlış olduğunu önceden varsayma.

2. Kaynak sayısını doğruluk ölçütü olarak kullanma.

3. DOĞRUDAN İLGİLİ kaynaklara,
   DOLAYLI İLGİLİ kaynaklardan daha fazla önem ver.

4. Birincil tarihî kanıt varsa özel önem ver.

5. Doğrudan ilgili akademik ikincil kaynaklar,
   genel başvuru ve popüler kaynaklardan genellikle
   daha yüksek kanıt değeri taşır.

6. Aynı çalışmayı aktaran farklı web sayfalarını
   bağımsız kanıtlar olarak sayma.

7. Atıf sayısını doğruluk ölçütü olarak kullanma.

8. Yüksek atıf sayısı tek başına kaynağı doğru yapmaz.

9. Kaynakların DESTEKLİYOR / ÇELİŞİYOR / BELİRSİZ
   sınıflandırmalarını dikkate al.

10. Güçlü ve anlamlı kaynaklar iki farklı yönde
    sonuç veriyorsa TARTIŞMALI sonucunu kullan.

11. Doğrudan ilgili ve yeterli kanıt yoksa
    YETERLİ KANIT YOK sonucunu kullan.

12. Tarih araştırmasına uygun ihtiyatlı dil kullan.
    "Kesin olarak kanıtlanmıştır",
    "tartışmasızdır" gibi mutlak ifadelerden kaçın.

13. Sadece verilen kaynaklardan hareket et.
    Dışarıdan bilgi ekleme.

14. En güçlü kaynakları seçerken sadece atıf sayısına
    değil doğrudan ilgisine, kaynak türüne ve
    iddiayla ilişkisine bak.

Sadece JSON döndür.

{{
  "sonuc": "...",
  "gerekce": "...",
  "en_guclu_kaynaklar": [0, 1],
  "sinirlayici_noktalar": [
    "...",
    "..."
  ]
}}
"""

    cevap = gemini_ile_calistir(
        prompt
    )

    return json_ayikla(
        cevap
    )


# ============================================================
# 20. TARİHİZ GERÇEK ARAŞTIRMA MOTORU
# ============================================================

def tarihiz_arastir(
    iddia,
    web_sayisi=5,
    akademik_sayisi=10
):

    iddia = str(
        iddia
    ).strip()

    if not iddia:
        raise ValueError(
            "Lütfen bir tarihî iddia yazın."
        )


    print("\n" + "=" * 72)
    print("TARİHİZ GERÇEK ARAŞTIRMASI")
    print("=" * 72)

    print(
        "\nİddia:",
        iddia
    )


    # --------------------------------------------------------
    # 1. SORGU
    # --------------------------------------------------------

    print(
        "\n[1/7] Gemini arama sorgularını hazırlıyor..."
    )

    sorgular = arama_sorgulari_olustur(
        iddia
    )

    web_query = sorgular.get(
        "web_query",
        iddia
    )

    academic_query = sorgular.get(
        "academic_query",
        iddia
    )

    print(
        "Web sorgusu:",
        web_query
    )

    print(
        "Akademik sorgu:",
        academic_query
    )


    # --------------------------------------------------------
    # 2. WEB
    # --------------------------------------------------------

    print(
        "\n[2/7] Tavily web taraması yapılıyor..."
    )

    tavily_json = tavily_guvenli_ara(

        query=web_query,

        search_depth="advanced",

        max_results=web_sayisi,

        include_answer=False,

        include_images=True

    )

    web_kaynaklari = web_kaynaklari_hazirla(
        tavily_json
    )

    web_kaynaklari = web_tekrarlari_temizle(
        web_kaynaklari
    )

    print(
        f"{len(web_kaynaklari)} web kaynağı bulundu."
    )


    # --------------------------------------------------------
    # 3. OPENALEX İLK ARAMA
    # --------------------------------------------------------

    print(
        "\n[3/7] OpenAlex ilk akademik taramayı yapıyor..."
    )

    oa1 = openalex_akademik_ara(
        academic_query,
        akademik_sayisi
    )

    akademik_1 = akademik_kaynaklari_hazirla(
        oa1
    )

    print(
        f"{len(akademik_1)} ilk akademik aday bulundu."
    )


    # --------------------------------------------------------
    # 4. İYİLEŞTİRİLMİŞ OPENALEX
    # --------------------------------------------------------

    print(
        "\n[4/7] Akademik sorgu iyileştiriliyor..."
    )

    refined_query = akademik_sorguyu_iyilestir(
        iddia,
        web_kaynaklari,
        akademik_1
    )

    print(
        "İyileştirilmiş sorgu:",
        refined_query
    )

    akademik_2 = []

    if refined_query:

        oa2 = openalex_akademik_ara(
            refined_query,
            akademik_sayisi
        )

        akademik_2 = akademik_kaynaklari_hazirla(
            oa2
        )


    akademik_tumu = akademik_tekrarlari_temizle(
        akademik_1
        + akademik_2
    )

    print(
        f"Toplam {len(akademik_tumu)} "
        "benzersiz akademik aday var."
    )


    # --------------------------------------------------------
    # 5. AKADEMİK KAYNAK ELEŞTİRİSİ
    # --------------------------------------------------------

    print(
        "\n[5/7] Akademik kaynakların ilgisi değerlendiriliyor..."
    )

    akademik_degerlendirilmis = kaynaklari_degerlendir(
        iddia,
        akademik_tumu
    )


    # --------------------------------------------------------
    # 6. WEB KAYNAK ELEŞTİRİSİ
    # --------------------------------------------------------

    print(
        "[6/7] Web kaynaklarının ilgisi değerlendiriliyor..."
    )

    web_degerlendirilmis = kaynaklari_degerlendir(
        iddia,
        web_kaynaklari
    )


    akademik_filtreli = [

        k
        for k in akademik_degerlendirilmis

        if k.get(
            "ilgi_duzeyi"
        ) in [
            "DOĞRUDAN İLGİLİ",
            "DOLAYLI İLGİLİ"
        ]

    ]


    web_filtreli = [

        k
        for k in web_degerlendirilmis

        if k.get(
            "ilgi_duzeyi"
        ) in [
            "DOĞRUDAN İLGİLİ",
            "DOLAYLI İLGİLİ"
        ]

    ]


    print(
        f"Akademik: "
        f"{len(akademik_filtreli)} ilgili kaynak kaldı."
    )

    print(
        f"Web: "
        f"{len(web_filtreli)} ilgili kaynak kaldı."
    )


    # --------------------------------------------------------
    # 7. NİHAİ DEĞERLENDİRME
    # --------------------------------------------------------

    print(
        "\n[7/7] Nihai tarihî değerlendirme hazırlanıyor..."
    )

    tum_ilgili = (
        akademik_filtreli
        + web_filtreli
    )


    if tum_ilgili:

        final = nihai_degerlendirme(
            iddia,
            tum_ilgili
        )

    else:

        final = {

            "sonuc":
                "YETERLİ KANIT YOK",

            "gerekce":
                (
                    "Araştırmada iddiayı değerlendirmek için "
                    "yeterli düzeyde doğrudan veya dolaylı "
                    "ilgili kaynak belirlenemedi."
                ),

            "en_guclu_kaynaklar":
                [],

            "sinirlayici_noktalar":
                [
                    "İlgili kaynak sayısı yetersizdir."
                ]

        }


    # --------------------------------------------------------
    # GÜÇLÜ KAYNAKLARI EŞLEŞTİR
    # --------------------------------------------------------

    guclu_kaynaklar = []

    for idx in final.get(
        "en_guclu_kaynaklar",
        []
    ):

        if (
            isinstance(idx, int)
            and
            0 <= idx < len(tum_ilgili)
        ):

            guclu_kaynaklar.append(
                tum_ilgili[idx]
            )


    # --------------------------------------------------------
    # GÖRSELLER
    # --------------------------------------------------------

    gorseller = []

    for g in tavily_json.get(
        "images",
        []
    ):

        if isinstance(g, str):

            gorseller.append({

                "url":
                    g,

                "aciklama":
                    ""

            })

        elif isinstance(g, dict):

            gorseller.append({

                "url":
                    g.get(
                        "url",
                        ""
                    ),

                "aciklama":
                    (
                        g.get(
                            "description"
                        )
                        or
                        g.get(
                            "alt"
                        )
                        or
                        ""
                    )

            })


    sonuc = {

        "iddia":
            iddia,

        "sorgular": {

            "web":
                web_query,

            "akademik_ilk":
                academic_query,

            "akademik_iyilestirilmis":
                refined_query

        },

        "sonuc":
            final.get(
                "sonuc",
                "YETERLİ KANIT YOK"
            ),

        "gerekce":
            final.get(
                "gerekce",
                ""
            ),

        "sinirlayici_noktalar":
            final.get(
                "sinirlayici_noktalar",
                []
            ),

        "en_guclu_kaynaklar":
            guclu_kaynaklar,

        "akademik_kaynaklar":
            akademik_filtreli,

        "web_kaynaklari":
            web_filtreli,

        "gorseller":
            gorseller

    }


    print("\n" + "=" * 72)

    print(
        "SONUÇ:",
        sonuc["sonuc"]
    )

    print("=" * 72)

    print(
        "\nGEREKÇE:\n",
        sonuc["gerekce"]
    )

    print(
        "\nAkademik ilgili kaynak sayısı:",
        len(
            sonuc["akademik_kaynaklar"]
        )
    )

    print(
        "Web ilgili kaynak sayısı:",
        len(
            sonuc["web_kaynaklari"]
        )
    )

    print(
        "\nAraştırma tamamlandı ✅"
    )

    return sonuc


# ============================================================
# 21. ARAYÜZ YARDIMCI FONKSİYONLARI
# ============================================================

def temiz_deger(
    deger,
    varsayilan="—"
):

    if deger is None:
        return varsayilan

    deger = str(
        deger
    ).strip()

    if not deger:
        return varsayilan

    return deger


def guvenli_url(url):

    url = str(
        url
        or ""
    ).strip()

    if (
        url.startswith("http://")
        or
        url.startswith("https://")
    ):

        return html.escape(
            url,
            quote=True
        )

    return ""


# ============================================================
# 22. BOŞ DURUM
# ============================================================

def bos_sonuc():

    return """
    <div class="empty-card">

        <div class="empty-symbol">
            ◌
        </div>

        <div>

            <strong>
                Henüz bir araştırma yapılmadı.
            </strong>

            <span>
                Tarihî iddianızı yazın ve
                “Kaynakları Araştır” düğmesine basın.
            </span>

        </div>

    </div>
    """


# ============================================================
# 23. ARAŞTIRMA DEVAM EDİYOR
# ============================================================

def arastirma_suruyor_html():

    return """
    <div class="research-running">

        <div class="running-top">

            <div class="running-orbit">
                ✦
            </div>

            <div>

                <strong>
                    Tarihİz araştırıyor...
                </strong>

                <span>
                    Akademik literatür ve web kaynakları
                    gerçek zamanlı olarak inceleniyor.
                </span>

            </div>

        </div>


        <div class="running-steps">

            <div class="running-step s1">
                <span>01</span>
                Web taraması
            </div>

            <div class="running-step s2">
                <span>02</span>
                Akademik tarama
            </div>

            <div class="running-step s3">
                <span>03</span>
                Kaynak eleştirisi
            </div>

            <div class="running-step s4">
                <span>04</span>
                Kanıt analizi
            </div>

            <div class="running-step s5">
                <span>05</span>
                Tarihî sentez
            </div>

        </div>

        <div class="research-warning">

            Araştırma süresi konuya, kaynak sayısına
            ve API yoğunluğuna göre değişebilir.

        </div>

    </div>
    """


def arastirma_tamam_html():

    return """
    <div class="process-finished">

        <div class="finished-icon">
            ✓
        </div>

        <div>

            <strong>
                Araştırma tamamlandı
            </strong>

            <span>
                İlgili kaynaklar seçildi,
                kanıtlar karşılaştırıldı ve
                tarihî değerlendirme oluşturuldu.
            </span>

        </div>

    </div>
    """


# ============================================================
# 24. SONUÇ KARTI
# ============================================================

def sonuc_karti(
    sonuc,
    akademik_sayi,
    web_sayi
):

    ayarlar = {

        "DESTEKLENİYOR":
            ("✓", "supported"),

        "ÇELİŞİYOR":
            ("✕", "contradicted"),

        "TARTIŞMALI":
            ("◐", "debated"),

        "YETERLİ KANIT YOK":
            ("?", "insufficient")

    }

    ikon, css = ayarlar.get(
        sonuc,
        ("?", "insufficient")
    )

    return f"""
    <div class="result-card {css}">

        <div class="result-seal">
            <span>{ikon}</span>
        </div>

        <div class="result-info">

            <div class="eyebrow">
                TARİHÎ DEĞERLENDİRME
            </div>

            <div class="result-title">
                {html.escape(str(sonuc))}
            </div>

            <div class="result-counts">

                <span>
                    ▤ <b>{akademik_sayi}</b>
                    akademik kaynak
                </span>

                <span>•</span>

                <span>
                    ◎ <b>{web_sayi}</b>
                    web kaynağı
                </span>

            </div>

        </div>

    </div>
    """


# ============================================================
# 25. KAYNAK KARTI
# ============================================================

def kaynak_karti(
    no,
    kaynak
):

    baslik = temiz_deger(
        kaynak.get("baslik")
    )

    yil = temiz_deger(
        kaynak.get("yil")
    )

    tur = temiz_deger(
        kaynak.get("kaynak_turu")
    )

    sinif = temiz_deger(
        kaynak.get("kaynak_sinifi")
    )

    ilgi = temiz_deger(
        kaynak.get("ilgi_duzeyi")
    )

    iliski = temiz_deger(
        kaynak.get("iddiayla_iliskisi")
    )

    gerekce = temiz_deger(
        kaynak.get(
            "degerlendirme_gerekcesi"
        ),
        ""
    )

    baglanti = guvenli_url(
        kaynak.get("baglanti")
    )

    atif = kaynak.get(
        "atif_sayisi"
    )


    link_html = ""

    if baglanti:

        link_metni = (
            "DOI'yi Aç ↗"
            if "doi.org" in baglanti.lower()
            else "Kaynağı Aç ↗"
        )

        link_html = f"""
        <a
            href="{baglanti}"
            target="_blank"
            rel="noopener noreferrer"
            class="source-link"
        >
            {link_metni}
        </a>
        """


    atif_html = ""

    if (
        atif is not None
        and str(atif) != ""
    ):

        atif_html = f"""
        <div class="source-stat">
            <span>Atıf Sayısı</span>
            <b>{html.escape(str(atif))}</b>
        </div>
        """


    gerekce_html = ""

    if gerekce:

        gerekce_html = f"""
        <div class="source-reason">

            <span>
                Değerlendirme
            </span>

            <p>
                {html.escape(gerekce)}
            </p>

        </div>
        """


    if iliski == "DESTEKLİYOR":
        relation_class = "rel-support"

    elif iliski == "ÇELİŞİYOR":
        relation_class = "rel-oppose"

    else:
        relation_class = "rel-neutral"


    return f"""
    <details class="source-card">

        <summary>

            <div class="source-number">
                {no}
            </div>


            <div class="source-main">

                <div class="source-title">
                    {html.escape(baslik)}
                </div>


                <div class="badges">

                    <span>
                        {html.escape(tur)}
                    </span>

                    <span class="important">
                        {html.escape(ilgi)}
                    </span>

                    <span>
                        {html.escape(sinif)}
                    </span>

                </div>

            </div>


            <div class="relation {relation_class}">
                {html.escape(iliski)}
            </div>


            <div class="plus">
                ＋
            </div>

        </summary>


        <div class="source-details">


            <div class="source-meta-row">

                <div class="source-stat">
                    <span>Yıl</span>
                    <b>{html.escape(yil)}</b>
                </div>


                <div class="source-stat">
                    <span>Kaynak Türü</span>
                    <b>{html.escape(tur)}</b>
                </div>


                <div class="source-stat">
                    <span>İlgi Düzeyi</span>
                    <b>{html.escape(ilgi)}</b>
                </div>


                <div class="source-stat">
                    <span>İddiayla İlişkisi</span>
                    <b>{html.escape(iliski)}</b>
                </div>


                {atif_html}

            </div>


            {gerekce_html}

            {link_html}

        </div>

    </details>
    """


# ============================================================
# 26. KAYNAK LİSTESİ
# ============================================================

def kaynak_listesi_html(
    kaynaklar
):

    if not kaynaklar:

        return """
        <div class="small-placeholder">

            Bu kategoride kullanıcıya gösterilecek
            yeterli düzeyde ilgili kaynak bulunamadı.

        </div>
        """


    ilgi_sirasi = {

        "DOĞRUDAN İLGİLİ":
            0,

        "DOLAYLI İLGİLİ":
            1

    }


    kaynaklar = sorted(

        kaynaklar,

        key=lambda x: (

            ilgi_sirasi.get(
                x.get(
                    "ilgi_duzeyi"
                ),
                9
            ),

            -int(
                x.get(
                    "atif_sayisi"
                )
                or 0
            )

        )

    )


    kartlar = ""

    for i, kaynak in enumerate(
        kaynaklar,
        1
    ):

        kartlar += kaynak_karti(
            i,
            kaynak
        )


    return f"""
    <div class="source-list">
        {kartlar}
    </div>
    """


# ============================================================
# 27. EN GÜÇLÜ KAYNAK
# ============================================================

def en_guclu_kaynak_html(
    sonuc
):

    gucluler = sonuc.get(
        "en_guclu_kaynaklar",
        []
    )

    kaynak = None


    if gucluler:
        kaynak = gucluler[0]


    if kaynak is None:

        for k in sonuc.get(
            "akademik_kaynaklar",
            []
        ):

            if (
                k.get("ilgi_duzeyi")
                ==
                "DOĞRUDAN İLGİLİ"
            ):

                kaynak = k
                break


    if kaynak is None:

        akademik = sonuc.get(
            "akademik_kaynaklar",
            []
        )

        if akademik:
            kaynak = akademik[0]


    if kaynak is None:

        web = sonuc.get(
            "web_kaynaklari",
            []
        )

        if web:
            kaynak = web[0]


    if kaynak is None:

        return """
        <div class="small-placeholder">
            En güçlü kaynak belirlenemedi.
        </div>
        """


    baslik = temiz_deger(
        kaynak.get("baslik")
    )

    yil = temiz_deger(
        kaynak.get("yil")
    )

    tur = temiz_deger(
        kaynak.get("kaynak_turu")
    )

    sinif = temiz_deger(
        kaynak.get("kaynak_sinifi")
    )

    ilgi = temiz_deger(
        kaynak.get("ilgi_duzeyi")
    )

    iliski = temiz_deger(
        kaynak.get("iddiayla_iliskisi")
    )

    atif = kaynak.get(
        "atif_sayisi"
    )

    baglanti = guvenli_url(
        kaynak.get("baglanti")
    )


    atif_metni = ""

    if atif is not None:

        atif_metni = f"""
        <i>•</i>

        <span>
            {html.escape(str(atif))} atıf
        </span>
        """


    link_html = ""

    if baglanti:

        link_metni = (
            "DOI'yi Aç ↗"
            if "doi.org" in baglanti.lower()
            else "Kaynağı Aç ↗"
        )

        link_html = f"""
        <a
            href="{baglanti}"
            target="_blank"
            rel="noopener noreferrer"
            class="strong-link"
        >
            {link_metni}
        </a>
        """


    return f"""
    <div class="strong-source">

        <div class="strong-symbol">
            ✦
        </div>

        <div class="strong-body">

            <div class="eyebrow">
                EN GÜÇLÜ KAYNAK
            </div>

            <div class="strong-title">
                {html.escape(baslik)}
            </div>

            <div class="strong-meta">

                <span>
                    {html.escape(yil)}
                </span>

                <i>•</i>

                <span>
                    {html.escape(tur)}
                </span>

                <i>•</i>

                <span>
                    {html.escape(ilgi)}
                </span>

                <i>•</i>

                <span>
                    {html.escape(sinif)}
                </span>

                <i>•</i>

                <span>
                    {html.escape(iliski)}
                </span>

                {atif_metni}

            </div>

            {link_html}

        </div>

    </div>
    """


# ============================================================
# 28. SINIRLAYICI NOKTALAR
# ============================================================

def sinirlamalar_markdown(
    sonuc
):

    maddeler = sonuc.get(
        "sinirlayici_noktalar",
        []
    )

    if not maddeler:

        return (
            "Bu araştırma için sistem tarafından "
            "ayrıca bir sınırlayıcı nokta belirtilmedi."
        )

    return "\n".join(
        f"- {m}"
        for m in maddeler
    )


# ============================================================
# 29. GÖRSEL ARŞİV
# ============================================================

def gorsel_arsivi_html(
    sonuc
):

    gorseller = sonuc.get(
        "gorseller",
        []
    )

    if not gorseller:

        return """
        <div class="small-placeholder">

            Bu araştırmada kullanılabilir
            ilgili görsel bulunamadı.

        </div>
        """


    kartlar = ""


    for g in gorseller[:8]:

        url = guvenli_url(
            g.get("url")
        )

        if not url:
            continue

        aciklama = temiz_deger(
            g.get("aciklama"),
            "İlgili tarihî görsel"
        )


        kartlar += f"""
        <article class="archive-card">

            <div class="archive-image">

                <img
                    src="{url}"
                    alt="{html.escape(aciklama, quote=True)}"
                    loading="lazy"
                >

            </div>


            <div class="archive-caption">

                <b>
                    {html.escape(aciklama)}
                </b>

                <span>
                    Görsel araştırma desteği
                </span>

                <a
                    href="{url}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Görseli Aç ↗
                </a>

            </div>

        </article>
        """


    if not kartlar:

        return """
        <div class="small-placeholder">
            Görseller görüntülenemedi.
        </div>
        """


    return f"""
    <div class="archive-note">

        Görseller tarihî iddianın doğruluğuna ilişkin
        kanıt olarak kullanılmaz; konunun görsel olarak
        incelenmesini desteklemek amacıyla sunulur.

    </div>

    <div class="archive-track">
        {kartlar}
    </div>
    """


# ============================================================
# 30. GRADIO GERÇEK ARAŞTIRMA
# ============================================================

def gradio_gercek_arastir(
    iddia
):

    iddia = str(
        iddia
        or ""
    ).strip()


    if not iddia:

        yield (

            """
            <div class="small-placeholder">
                Lütfen önce bir tarihî iddia yazın.
            </div>
            """,

            bos_sonuc(),

            "",

            """
            <div class="small-placeholder">
                Henüz kaynak seçilmedi.
            </div>
            """,

            """
            <div class="small-placeholder">
                Henüz araştırma yapılmadı.
            </div>
            """,

            """
            <div class="small-placeholder">
                Henüz araştırma yapılmadı.
            </div>
            """,

            "",

            """
            <div class="small-placeholder">
                Henüz araştırma yapılmadı.
            </div>
            """

        )

        return


    yield (

        arastirma_suruyor_html(),

        """
        <div class="research-waiting">

            <div class="waiting-spinner"></div>

            <div>

                <strong>
                    Kaynaklar değerlendiriliyor
                </strong>

                <span>
                    Nihai sonuç araştırma tamamlandığında
                    burada görüntülenecektir.
                </span>

            </div>

        </div>
        """,

        (
            "Gerçek kaynak araştırması devam ediyor. "
            "Sonuç oluşturulduğunda bu bölüm otomatik "
            "olarak güncellenecektir."
        ),

        """
        <div class="small-placeholder">
            En güçlü kaynak araştırma sonunda belirlenecektir.
        </div>
        """,

        """
        <div class="small-placeholder">
            Akademik literatür araştırılıyor...
        </div>
        """,

        """
        <div class="small-placeholder">
            Web kaynakları araştırılıyor...
        </div>
        """,

        "Araştırma devam ediyor...",

        """
        <div class="small-placeholder">
            İlgili görseller araştırılıyor...
        </div>
        """

    )


    try:

        sonuc = tarihiz_arastir(
            iddia
        )


        akademik = sonuc.get(
            "akademik_kaynaklar",
            []
        )

        web = sonuc.get(
            "web_kaynaklari",
            []
        )

        final_sonuc = sonuc.get(
            "sonuc",
            "YETERLİ KANIT YOK"
        )

        gerekce = sonuc.get(
            "gerekce",
            ""
        )


        gerekce_md = f"""
### Kaynaklara Dayalı Tarihî Sentez

{gerekce}

---

*Tarihİz, bu değerlendirmeyi araştırma sırasında elde edilen
ve ilgili olarak sınıflandırılan kaynaklara dayanarak üretmiştir.
Sonuç mutlak bir doğruluk hükmü değildir.*
"""


        yield (

            arastirma_tamam_html(),

            sonuc_karti(
                final_sonuc,
                len(akademik),
                len(web)
            ),

            gerekce_md,

            en_guclu_kaynak_html(
                sonuc
            ),

            kaynak_listesi_html(
                akademik
            ),

            kaynak_listesi_html(
                web
            ),

            sinirlamalar_markdown(
                sonuc
            ),

            gorsel_arsivi_html(
                sonuc
            )

        )


    except Exception as e:

        hata = html.escape(
            str(e)
        )

        traceback.print_exc()


        yield (

            """
            <div class="error-process">

                <strong>
                    Araştırma tamamlanamadı
                </strong>

                <span>
                    API bağlantısı veya araştırma
                    motorunda geçici bir sorun oluştu.
                </span>

            </div>
            """,

            f"""
            <div class="error-card">

                <div class="error-icon">
                    !
                </div>

                <div>

                    <strong>
                        Araştırma sırasında hata oluştu
                    </strong>

                    <span>
                        {hata}
                    </span>

                </div>

            </div>
            """,

            (
                "İddianızı değiştirmeden tekrar deneyebilirsiniz. "
                "Sorun devam ederse Colab hata çıktısını inceleyin."
            ),

            "",

            "",

            "",

            "",

            ""

        )


# ============================================================
# 31. ÖRNEK İDDİALAR
# ============================================================

ORNEK_VIKING = (
    "Vikingler Amerika kıtasına "
    "Kristof Kolomb'dan önce ulaştı."
)

ORNEK_FATIH = (
    "Fatih Sultan Mehmed, doktoru tarafından "
    "zehirlenerek öldürüldü."
)

ORNEK_LOZAN = (
    "Lozan Barış Antlaşması'nın 100 yıllık bir geçerlilik "
    "süresi vardır ve Türkiye'nin yeraltı kaynaklarını "
    "çıkarmasını engelleyen gizli maddeleri vardır."
)


# ============================================================
# 32. CSS
# ============================================================

CSS = f"""

:root {{

    --ink:#172238;
    --ink-soft:#5d6673;
    --gold:#aa7e36;
    --gold-light:#e7c57e;
    --navy:#172c49;
    --paper:#f5f0e6;
    --green:#426b52;
    --red:#7c4742;
    --line:rgba(155,120,66,.22);

}}


/* FONT */

.gradio-container,
.gradio-container *,
.gradio-container button,
.gradio-container input,
.gradio-container textarea {{

    font-family:
        "Segoe UI Variable",
        "Segoe UI",
        Arial,
        sans-serif !important;

}}


/* ARKA PLAN */

body,
.gradio-container {{

    color:
        var(--ink) !important;

    background:
        linear-gradient(
            180deg,
            #f7f3ea 0%,
            #eee6d8 48%,
            #f7f3eb 100%
        ) !important;

}}


.gradio-container {{

    max-width:
        1340px !important;

    margin:
        auto !important;

    padding-bottom:
        80px !important;

    position:
        relative;

    isolation:
        isolate;

}}


.gradio-container::before {{

    content:"";

    position:fixed;

    inset:0;

    z-index:-2;

    pointer-events:none;

    background-image:
        url("{banner_url}");

    background-size:
        cover;

    background-position:
        center;

    opacity:.055;

    filter:
        grayscale(35%)
        sepia(20%)
        contrast(.88);

}}


.gradio-container::after {{

    content:"";

    position:fixed;

    inset:0;

    z-index:-1;

    pointer-events:none;

    background-image:

        radial-gradient(
            circle at 13% 20%,
            rgba(176,128,52,.15),
            transparent 25%
        ),

        radial-gradient(
            circle at 88% 16%,
            rgba(39,70,108,.12),
            transparent 22%
        ),

        linear-gradient(
            rgba(43,69,98,.027) 1px,
            transparent 1px
        ),

        linear-gradient(
            90deg,
            rgba(43,69,98,.027) 1px,
            transparent 1px
        );

    background-size:
        auto,
        auto,
        110px 110px,
        110px 110px;

}}


/* HERO */

.hero {{

    position:relative;

    min-height:440px;

    overflow:hidden;

    margin-bottom:20px;

    border-radius:30px;

    box-shadow:
        0 22px 55px
        rgba(16,28,46,.20);

}}


.hero-image {{

    position:absolute;

    inset:-5%;

    width:110%;

    height:110%;

    object-fit:cover;

    animation:
        heroMotion
        22s
        ease-in-out
        infinite alternate;

}}


.hero-shade {{

    position:absolute;

    inset:0;

    background:
        linear-gradient(
            90deg,
            rgba(5,11,21,.96) 0%,
            rgba(7,15,28,.83) 35%,
            rgba(8,17,31,.49) 62%,
            rgba(7,13,23,.08) 100%
        );

}}


.hero-content {{

    position:relative;

    z-index:2;

    min-height:440px;

    max-width:850px;

    padding:48px 50px;

    display:flex;

    flex-direction:column;

    justify-content:center;

}}


.hero-title {{

    color:#fff !important;

    font-size:60px;

    font-weight:850;

    letter-spacing:-1.7px;

    line-height:1;

}}


.hero-project-title {{

    max-width:790px;

    margin-top:17px;

    color:
        rgba(255,255,255,.95) !important;

    font-size:20px;

    line-height:1.5;

    font-weight:600;

}}


.hero-tags {{

    display:flex;

    flex-wrap:wrap;

    gap:9px;

    margin-top:25px;

}}


.hero-tag {{

    display:inline-flex;

    align-items:center;

    gap:7px;

    min-height:39px;

    padding:7px 13px;

    border-radius:999px;

    color:#fff !important;

    background:
        rgba(255,255,255,.11);

    border:
        1px solid
        rgba(255,255,255,.23);

    backdrop-filter:
        blur(7px);

    font-size:12px;

    font-weight:700;

}}


.hero-tag,
.hero-tag span {{

    color:#fff !important;

}}


.hero-tag svg {{

    width:18px;

    height:18px;

    fill:none !important;

    stroke:#e7c57e !important;

    stroke-width:1.7;

    stroke-linecap:round;

    stroke-linejoin:round;

}}


.star-icon {{

    color:#e7c57e !important;

    font-size:18px;

}}


.smart-tag {{

    background:
        rgba(177,133,58,.18);

    border-color:
        rgba(231,197,126,.40);

    animation:
        smartPulse
        2.8s infinite;

}}


/* PANELLER */

.about-box,
.search-area {{

    padding:25px;

    border-radius:22px;

    background:
        rgba(255,255,255,.67);

    border:
        1px solid var(--line);

    backdrop-filter:
        blur(12px);

    box-shadow:
        0 8px 30px
        rgba(21,34,54,.055);

}}


.about-grid {{

    display:grid;

    grid-template-columns:
        62px minmax(0,1fr);

    gap:20px;

}}


.about-icon {{

    width:58px;

    height:58px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:18px;

    color:#946b2f;

    background:
        rgba(255,248,231,.74);

    border:
        1px solid
        rgba(174,131,60,.34);

    font-weight:850;

}}


.about-title {{

    font-size:21px;

    font-weight:850;

    margin-bottom:10px;

}}


.about-text {{

    color:var(--ink-soft);

    font-size:14px;

    line-height:1.77;

}}


.about-warning {{

    margin-top:15px;

    padding:11px 14px;

    border-left:
        3px solid #ac813d;

    background:
        rgba(181,138,58,.075);

    color:#665a47;

    font-size:12px;

    line-height:1.6;

}}


/* NASIL KULLANILIR */

.usage-grid {{

    display:grid;

    grid-template-columns:
        repeat(4,1fr);

    gap:13px;

}}


.usage-card {{

    min-height:145px;

    padding:18px;

    border-radius:19px;

    background:
        rgba(255,255,255,.68);

    border:
        1px solid var(--line);

    transition:.22s ease;

}}


.usage-card:hover {{

    transform:
        translateY(-3px);

}}


.usage-number {{

    width:34px;

    height:34px;

    margin-bottom:12px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    color:#fff;

    background:#967036;

    font-weight:800;

}}


.usage-card b {{

    display:block;

    margin-bottom:7px;

}}


.usage-card span {{

    color:#626b76;

    font-size:12px;

    line-height:1.58;

}}


/* ARAMA */

.search-area {{

    margin-top:25px;

}}


.search-area textarea {{

    background:
        rgba(255,255,255,.87) !important;

    border:
        1px solid
        rgba(148,112,56,.22) !important;

    border-radius:
        15px !important;

}}


.example-heading {{

    margin:
        17px 0 9px;

    color:#6e665a;

    font-size:12px;

    font-weight:750;

}}


.example-claim,
.example-claim button,
button.example-claim {{

    min-height:
        112px !important;

    height:
        auto !important;

    padding:
        16px !important;

    white-space:
        normal !important;

    text-align:
        left !important;

    justify-content:
        flex-start !important;

    color:
        #263347 !important;

    background:
        rgba(255,255,255,.75) !important;

    border:
        1px solid
        rgba(162,126,65,.20) !important;

    border-radius:
        17px !important;

    font-size:
        12px !important;

    line-height:
        1.55 !important;

    font-weight:
        650 !important;

}}


.research-btn,
.research-btn button,
button.research-btn {{

    min-height:
        52px !important;

    border-radius:
        14px !important;

    border:
        1px solid
        #c69b50 !important;

    color:
        #fff !important;

    background:
        linear-gradient(
            135deg,
            #223b5d 0%,
            #172c49 75%
        ) !important;

    font-weight:
        850 !important;

}}


/* BAŞLIKLAR */

.section-head {{

    margin:
        38px 0 14px;

}}


.section-kicker {{

    color:#987033;

    font-size:10px;

    font-weight:850;

    letter-spacing:1.8px;

}}


.section-title {{

    margin-top:4px;

    font-size:29px;

    font-weight:850;

}}


/* ARAŞTIRMA */

.research-running {{

    padding:23px;

    border-radius:22px;

    background:
        rgba(255,255,255,.65);

    border:
        1px solid var(--line);

}}


.running-top {{

    display:flex;

    align-items:center;

    gap:14px;

}}


.running-top strong,
.running-top span {{

    display:block;

}}


.running-top span {{

    margin-top:4px;

    color:#6a7079;

    font-size:12px;

}}


.running-orbit {{

    width:45px;

    height:45px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    color:#9b7131;

    border:
        1px solid
        rgba(170,126,54,.4);

    animation:
        orbitPulse
        1.5s infinite;

}}


.running-steps {{

    display:grid;

    grid-template-columns:
        repeat(5,1fr);

    gap:9px;

    margin-top:20px;

}}


.running-step {{

    min-height:72px;

    padding:11px;

    border-radius:14px;

    color:#6b717a;

    background:
        rgba(255,255,255,.58);

    border:
        1px solid
        rgba(102,101,96,.14);

    font-size:11px;

    animation:
        researchStep
        5s infinite;

}}


.running-step span {{

    display:block;

    margin-bottom:4px;

    color:#997035;

    font-size:9px;

    font-weight:850;

}}


.s2 {{ animation-delay:1s; }}
.s3 {{ animation-delay:2s; }}
.s4 {{ animation-delay:3s; }}
.s5 {{ animation-delay:4s; }}


.research-warning {{

    margin-top:14px;

    color:#847a6d;

    font-size:10px;

}}


/* BEKLEME */

.research-waiting {{

    display:flex;

    align-items:center;

    gap:14px;

    padding:21px;

    border-radius:20px;

    background:
        rgba(255,255,255,.61);

    border:
        1px solid var(--line);

}}


.waiting-spinner {{

    width:38px;

    height:38px;

    border-radius:50%;

    border:
        3px solid
        rgba(167,123,54,.18);

    border-top-color:
        #a77b36;

    animation:
        spin 1s linear infinite;

}}


.process-finished {{

    padding:18px 21px;

    display:flex;

    align-items:center;

    gap:13px;

    border-radius:20px;

    background:
        rgba(237,247,240,.78);

    border:
        1px solid
        rgba(66,107,82,.22);

}}


.finished-icon {{

    width:38px;

    height:38px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    color:white;

    background:#4c7059;

    font-weight:850;

}}


/* SONUÇ */

.result-card {{

    padding:25px;

    display:flex;

    align-items:center;

    gap:21px;

    border-radius:23px;

    animation:
        resultEnter
        .65s ease-out;

}}


.supported {{

    color:#315f48;

    background:
        rgba(237,247,240,.85);

    border:
        1px solid
        rgba(62,112,79,.23);

}}


.contradicted {{

    color:#78413e;

    background:
        rgba(252,240,239,.85);

    border:
        1px solid
        rgba(151,69,63,.20);

}}


.debated {{

    color:#816326;

    background:
        rgba(255,248,227,.86);

    border:
        1px solid
        rgba(160,125,46,.24);

}}


.insufficient {{

    color:#566071;

    background:
        rgba(242,245,248,.86);

    border:
        1px solid
        rgba(89,103,125,.19);

}}


.result-seal {{

    width:92px;

    height:92px;

    flex:0 0 92px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    border:
        4px double currentColor;

    animation:
        stamp .8s ease-out;

}}


.result-seal span {{

    font-size:38px;

    font-weight:900;

}}


.eyebrow {{

    color:#987032;

    font-size:10px;

    font-weight:850;

    letter-spacing:1.55px;

}}


.result-title {{

    margin-top:3px;

    font-size:30px;

    font-weight:850;

}}


.result-counts {{

    display:flex;

    flex-wrap:wrap;

    gap:8px;

    margin-top:9px;

    font-size:12px;

}}


/* EN GÜÇLÜ KAYNAK */

.strong-source {{

    padding:22px;

    display:flex;

    align-items:center;

    gap:17px;

    border-radius:21px;

    background:
        rgba(255,248,230,.74);

    border:
        1px solid
        rgba(192,151,76,.36);

}}


.strong-symbol {{

    width:53px;

    height:53px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:16px;

    color:#987032;

    border:
        1px solid
        rgba(190,146,68,.50);

}}


.strong-title {{

    margin-top:5px;

    color:#28303d;

    font-size:19px;

    font-weight:850;

}}


.strong-meta {{

    display:flex;

    flex-wrap:wrap;

    gap:7px;

    margin-top:7px;

    color:#746f67;

    font-size:12px;

}}


.strong-link,
.source-link {{

    display:inline-block;

    margin-top:10px;

    color:
        #75551d !important;

    text-decoration:none;

    font-size:12px;

    font-weight:850;

}}


/* KAYNAKLAR */

.source-list {{

    display:grid;

    gap:10px;

}}


.source-card {{

    overflow:hidden;

    border-radius:17px;

    background:
        rgba(255,255,255,.68);

    border:
        1px solid
        rgba(112,105,94,.17);

    transition:.22s ease;

}}


.source-card:hover {{

    transform:
        translateY(-3px);

    border-color:
        rgba(181,138,58,.42);

}}


.source-card summary {{

    list-style:none;

    cursor:pointer;

    display:grid;

    grid-template-columns:
        36px
        minmax(0,1fr)
        auto
        32px;

    gap:11px;

    align-items:center;

    padding:16px;

}}


.source-card summary::-webkit-details-marker {{

    display:none;

}}


.source-number {{

    width:33px;

    height:33px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:11px;

    color:#70572f;

    background:
        rgba(239,233,222,.82);

    font-weight:850;

}}


.source-title {{

    color:#252e3b;

    font-size:14px;

    font-weight:850;

}}


.badges {{

    display:flex;

    flex-wrap:wrap;

    gap:5px;

    margin-top:7px;

}}


.badges span {{

    padding:3px 7px;

    border-radius:999px;

    color:#595c62;

    background:
        rgba(250,248,244,.76);

    border:
        1px solid
        rgba(191,184,171,.62);

    font-size:9px;

    font-weight:700;

}}


.badges span.important {{

    color:#765923;

    background:
        rgba(255,248,226,.82);

}}


.relation {{

    font-size:10px;

    font-weight:850;

}}


.rel-support {{
    color:#3d6a50;
}}

.rel-oppose {{
    color:#8a4944;
}}

.rel-neutral {{
    color:#717680;
}}


.plus {{

    font-size:18px;

}}


.source-card[open]
.plus {{

    transform:
        rotate(45deg);

}}


.source-details {{

    padding:
        15px 17px 18px 63px;

    border-top:
        1px solid
        rgba(110,105,95,.11);

}}


.source-meta-row {{

    display:flex;

    flex-wrap:wrap;

    gap:20px;

}}


.source-stat {{

    display:flex;

    flex-direction:column;

    font-size:11px;

}}


.source-stat span {{

    color:#858079;

}}


.source-reason {{

    margin-top:15px;

    padding:12px 14px;

    border-radius:12px;

    background:
        rgba(242,238,229,.60);

}}


.source-reason span {{

    color:#8e6a30;

    font-size:9px;

    font-weight:850;

}}


.source-reason p {{

    margin:
        5px 0 0;

    color:#5e6570;

    font-size:11px;

    line-height:1.6;

}}


/* GÖRSELLER */

.archive-note {{

    margin-bottom:11px;

    color:#79756e;

    font-size:11px;

}}


.archive-track {{

    display:flex;

    gap:14px;

    overflow-x:auto;

    padding:
        2px 2px 14px;

}}


.archive-card {{

    flex:
        0 0 min(370px,82%);

    overflow:hidden;

    border-radius:19px;

    background:
        rgba(255,255,255,.68);

    border:
        1px solid var(--line);

}}


.archive-image {{

    height:215px;

    overflow:hidden;

}}


.archive-image img {{

    width:100%;

    height:100%;

    object-fit:cover;

}}


.archive-caption {{

    padding:13px 14px;

}}


.archive-caption b,
.archive-caption span,
.archive-caption a {{

    display:block;

}}


.archive-caption span {{

    margin-top:4px;

    font-size:10px;

    color:#797a7c;

}}


.archive-caption a {{

    margin-top:7px;

    color:
        #75551d !important;

    font-size:10px;

    font-weight:800;

    text-decoration:none;

}}


/* BOŞ DURUM */

.empty-card,
.small-placeholder,
.error-card,
.error-process {{

    padding:20px;

    border-radius:19px;

    background:
        rgba(255,255,255,.60);

    border:
        1px dashed
        rgba(166,124,56,.31);

}}


.empty-card,
.error-card {{

    display:flex;

    align-items:center;

    gap:13px;

}}


.empty-symbol,
.error-icon {{

    width:38px;

    height:38px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:13px;

    color:#9a7236;

    background:
        rgba(174,128,52,.09);

}}


/* ANİMASYON */

@keyframes heroMotion {{

    from {{
        transform:
            scale(1.02)
            translateX(-1%);
    }}

    to {{
        transform:
            scale(1.09)
            translateX(1%);
    }}

}}


@keyframes smartPulse {{

    50% {{
        box-shadow:
            0 0 18px
            rgba(230,195,122,.19);
    }}

}}


@keyframes orbitPulse {{

    50% {{
        transform:
            scale(1.12);
    }}

}}


@keyframes researchStep {{

    0%,
    100% {{
        opacity:.48;
    }}

    15%,
    35% {{
        opacity:1;
        transform:
            translateY(-3px);

        background:
            rgba(255,248,229,.87);
    }}

}}


@keyframes spin {{

    to {{
        transform:
            rotate(360deg);
    }}

}}


@keyframes resultEnter {{

    from {{
        opacity:0;
        transform:
            translateY(18px);
    }}

    to {{
        opacity:1;
        transform:
            translateY(0);
    }}

}}


@keyframes stamp {{

    from {{
        opacity:0;
        transform:
            rotate(-12deg)
            scale(1.38);
    }}

    to {{
        opacity:1;
        transform:
            rotate(0)
            scale(1);
    }}

}}


/* MOBİL */

@media (max-width:900px) {{

    .hero-content {{
        padding:34px 27px;
    }}

    .hero-title {{
        font-size:44px;
    }}

    .usage-grid {{
        grid-template-columns:
            repeat(2,1fr);
    }}

    .running-steps {{
        grid-template-columns:
            1fr;
    }}

}}


@media (max-width:650px) {{

    .hero {{
        min-height:410px;
        border-radius:22px;
    }}

    .hero-content {{
        min-height:410px;
        padding:26px 21px;
    }}

    .hero-title {{
        font-size:38px;
    }}

    .hero-project-title {{
        font-size:15px;
    }}

    .about-grid {{
        grid-template-columns:1fr;
    }}

    .usage-grid {{
        grid-template-columns:1fr;
    }}

    .result-card {{
        flex-direction:column;
        align-items:flex-start;
    }}

    .source-card summary {{

        grid-template-columns:
            34px
            minmax(0,1fr)
            30px;

    }}

    .relation {{

        grid-column:
            2 / 3;

    }}

    .source-details {{
        padding-left:59px;
    }}

}}
"""


# SON GORSEL ARSIVI GUNCELLEMESI (not defteri hucre 60)
import base64
import requests
import html


# ============================================================
# HARİCÎ GÖRSELİ GÜVENLİ ŞEKİLDE İNDİR
# ============================================================

def resmi_data_uri_yap(url):

    try:

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120 Safari/537.36"
            ),
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,"
                      "image/*,*/*;q=0.8"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10,
            allow_redirects=True
        )

        response.raise_for_status()

        content_type = (
            response.headers.get("Content-Type", "")
            .split(";")[0]
            .strip()
            .lower()
        )

        # Gerçekten görsel mi?
        if not content_type.startswith("image/"):
            return None

        # Aşırı büyük görselleri alma
        if len(response.content) > 8 * 1024 * 1024:
            return None

        encoded = base64.b64encode(
            response.content
        ).decode("utf-8")

        return (
            f"data:{content_type};base64,{encoded}"
        )

    except Exception:
        return None


# ============================================================
# GÖRSEL ARŞİVİ - YENİ SÜRÜM
# ============================================================

def gorsel_arsivi_html(sonuc):

    gorseller = sonuc.get(
        "gorseller",
        []
    )

    if not gorseller:

        return """
        <div class="small-placeholder">
            Bu araştırmada kullanılabilir
            ilgili görsel bulunamadı.
        </div>
        """


    kartlar = ""
    gosterilen = 0


    for g in gorseller:

        # En fazla 8 başarılı görsel göster
        if gosterilen >= 8:
            break

        orijinal_url = str(
            g.get("url") or ""
        ).strip()

        if not (
            orijinal_url.startswith("http://")
            or orijinal_url.startswith("https://")
        ):
            continue


        aciklama = str(
            g.get("aciklama")
            or "İlgili tarihî görsel"
        ).strip()


        # Görseli sunucu tarafında indir
        data_uri = resmi_data_uri_yap(
            orijinal_url
        )


        # İndirilemeyen görseli boş kart olarak gösterme
        if not data_uri:
            continue


        guvenli_link = html.escape(
            orijinal_url,
            quote=True
        )

        guvenli_aciklama = html.escape(
            aciklama
        )

        guvenli_alt = html.escape(
            aciklama,
            quote=True
        )


        kartlar += f"""
        <article class="archive-card">

            <div class="archive-image">

                <img
                    src="{data_uri}"
                    alt="{guvenli_alt}"
                    loading="lazy"
                >

            </div>


            <div class="archive-caption">

                <b>
                    {guvenli_aciklama}
                </b>

                <span>
                    Görsel araştırma desteği
                </span>

                <a
                    href="{guvenli_link}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Görseli Aç ↗
                </a>

            </div>

        </article>
        """

        gosterilen += 1


    if not kartlar:

        return """
        <div class="small-placeholder">

            İlgili görseller bulundu ancak kaynak siteler
            görsellerin başka sayfalarda görüntülenmesine
            izin vermedi.

        </div>
        """


    return f"""
    <div class="archive-note">

        Görseller tarihî iddianın doğruluğuna ilişkin
        kanıt olarak kullanılmaz; konunun görsel olarak
        incelenmesini desteklemek amacıyla sunulur.

    </div>

    <div class="archive-track">
        {kartlar}
    </div>
    """


print("Tarihİz görsel yükleme sistemi güncellendi ✅")

# ============================================================
# 33. GRADIO ARAYÜZÜ
# ============================================================

with gr.Blocks(
    title="Tarihİz"
) as demo:


    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    gr.HTML(
        f"""
        <section class="hero">

            <img
                class="hero-image"
                src="{banner_url}"
                alt="Tarihİz"
            >

            <div class="hero-shade"></div>


            <div class="hero-content">


                <div class="hero-title">
                    Tarihİz
                </div>


                <div class="hero-project-title">

                    Tarihî İddialar İçin
                    Kaynak Eleştirisi Tabanlı
                    Yapay Zekâ Asistanı

                </div>


                <div class="hero-tags">


                    <div class="hero-tag">

                        <svg viewBox="0 0 24 24">

                            <path
                                d="M3 5.5c2.8-.8 5.3-.4 9 1.7v12c-3.7-2.1-6.2-2.5-9-1.7z"
                            />

                            <path
                                d="M21 5.5c-2.8-.8-5.3-.4-9 1.7v12c3.7-2.1 6.2-2.5 9-1.7z"
                            />

                        </svg>

                        <span>
                            Akademik Literatür
                        </span>

                    </div>


                    <div class="hero-tag">

                        <svg viewBox="0 0 24 24">

                            <circle
                                cx="12"
                                cy="12"
                                r="9"
                            />

                            <path d="M3 12h18"/>

                            <path
                                d="M12 3c3 3.2 4.2 6.2 4.2 9S15 17.8 12 21"
                            />

                            <path
                                d="M12 3C9 6.2 7.8 9.2 7.8 12S9 17.8 12 21"
                            />

                            <path d="M5.4 7.3h13.2"/>
                            <path d="M5.4 16.7h13.2"/>

                        </svg>

                        <span>
                            Web Kaynakları
                        </span>

                    </div>


                    <div class="hero-tag">

                        <svg viewBox="0 0 24 24">

                            <circle
                                cx="10.5"
                                cy="10.5"
                                r="6.5"
                            />

                            <path
                                d="M15.5 15.5L21 21"
                            />

                            <path
                                d="M8 10.5l1.6 1.6 3.4-3.6"
                            />

                        </svg>

                        <span>
                            Kaynak Eleştirisi
                        </span>

                    </div>


                    <div class="hero-tag smart-tag">

                        <span class="star-icon">
                            ✦
                        </span>

                        <span>
                            Akıllı Analiz
                        </span>

                    </div>


                </div>

            </div>

        </section>
        """
    )


    # --------------------------------------------------------
    # HAKKINDA
    # --------------------------------------------------------

    with gr.Tabs():


        with gr.Tab(
            "Hakkında"
        ):

            gr.HTML(
                """
                <div class="about-box">

                    <div class="about-grid">

                        <div class="about-icon">
                            Tİ
                        </div>


                        <div>

                            <div class="about-title">
                                Tarihİz Nedir?
                            </div>


                            <div class="about-text">

                                <strong>Tarihİz</strong>,
                                TÜBİTAK 2204-A Lise Öğrencileri
                                Araştırma Projeleri Yarışması kapsamında
                                Tarih alanında geliştirilen yapay zekâ
                                destekli bir araştırma aracıdır.

                                <br><br>

                                Sistem akademik literatürü ve genel web
                                kaynaklarını araştırır; elde edilen aday
                                kaynakların tarihî iddiayla ilgisini
                                değerlendirir, ilgisiz kaynakları eler,
                                ilgili kaynakların iddiayı destekleme veya
                                iddiayla çelişme durumunu inceler ve
                                kaynaklara dayalı bir tarihî sentez oluşturur.

                            </div>


                            <div class="about-warning">

                                Tarihİz mutlak doğruluk belirleyen
                                bir araç değildir. Uzman değerlendirmesinin
                                veya akademik araştırmanın yerine geçmez;
                                tarih araştırmasını destekler.

                            </div>

                        </div>

                    </div>

                </div>
                """
            )


        # ----------------------------------------------------
        # NASIL KULLANILIR
        # ----------------------------------------------------

        with gr.Tab(
            "Nasıl Kullanılır?"
        ):

            gr.HTML(
                """
                <div class="usage-grid">


                    <div class="usage-card">

                        <div class="usage-number">
                            1
                        </div>

                        <b>
                            İddianızı yazın
                        </b>

                        <span>
                            Araştırılabilir bir tarihî iddiayı
                            açık bir cümle olarak girin.
                        </span>

                    </div>


                    <div class="usage-card">

                        <div class="usage-number">
                            2
                        </div>

                        <b>
                            Araştırmayı başlatın
                        </b>

                        <span>
                            Tarihİz akademik literatürü ve
                            web kaynaklarını gerçek zamanlı tarar.
                        </span>

                    </div>


                    <div class="usage-card">

                        <div class="usage-number">
                            3
                        </div>

                        <b>
                            Kanıtları inceleyin
                        </b>

                        <span>
                            Kaynakların ilgisini ve
                            iddiayla ilişkisini karşılaştırın.
                        </span>

                    </div>


                    <div class="usage-card">

                        <div class="usage-number">
                            4
                        </div>

                        <b>
                            Kaynaklara ulaşın
                        </b>

                        <span>
                            DOI ve internet bağlantıları üzerinden
                            kaynakların asıllarını inceleyin.
                        </span>

                    </div>


                </div>
                """
            )


    # --------------------------------------------------------
    # ARAMA ALANI
    # --------------------------------------------------------

    with gr.Group(
        elem_classes="search-area"
    ):


        iddia_kutusu = gr.Textbox(

            label=(
                "Araştırmak istediğiniz tarihî iddia"
            ),

            placeholder=(
                "Bir tarihî iddiayı açık bir cümle hâlinde yazınız..."
            ),

            lines=3

        )


        gr.HTML(
            """
            <div class="example-heading">
                Örnek tarihî iddialar
            </div>
            """
        )


        with gr.Row(
            equal_height=True
        ):


            ornek1 = gr.Button(
                ORNEK_VIKING,
                elem_classes="example-claim"
            )


            ornek2 = gr.Button(
                ORNEK_FATIH,
                elem_classes="example-claim"
            )


            ornek3 = gr.Button(
                ORNEK_LOZAN,
                elem_classes="example-claim"
            )


        arastir_butonu = gr.Button(

            "✦  Kaynakları Araştır",

            variant="primary",

            size="lg",

            elem_classes="research-btn"

        )


    # --------------------------------------------------------
    # ARAŞTIRMA SÜRECİ
    # --------------------------------------------------------

    gr.HTML(
        """
        <div class="section-head">

            <div class="section-kicker">
                ARAŞTIRMA MOTORU
            </div>

            <div class="section-title">
                Araştırma Süreci
            </div>

        </div>
        """
    )


    ilerleme_alani = gr.HTML(
        """
        <div class="small-placeholder">

            Araştırma başlatıldığında gerçek
            araştırma süreci burada gösterilecektir.

        </div>
        """
    )


    # --------------------------------------------------------
    # SONUÇ
    # --------------------------------------------------------

    gr.HTML(
        """
        <div class="section-head">

            <div class="section-kicker">
                SONUÇ
            </div>

            <div class="section-title">
                Tarihî Değerlendirme
            </div>

        </div>
        """
    )


    sonuc_html = gr.HTML(
        bos_sonuc()
    )


    gerekce = gr.Markdown(
        ""
    )


    # --------------------------------------------------------
    # EN GÜÇLÜ KAYNAK
    # --------------------------------------------------------

    gr.HTML(
        """
        <div class="section-head">

            <div class="section-kicker">
                KANIT
            </div>

            <div class="section-title">
                En Güçlü Kaynak
            </div>

        </div>
        """
    )


    guclu_kaynak = gr.HTML(
        """
        <div class="small-placeholder">

            Araştırma tamamlandığında
            en güçlü kaynak burada gösterilecektir.

        </div>
        """
    )


    # --------------------------------------------------------
    # KAYNAKLAR
    # --------------------------------------------------------

    gr.HTML(
        """
        <div class="section-head">

            <div class="section-kicker">
                KAYNAK ELEŞTİRİSİ
            </div>

            <div class="section-title">
                İncelenen Kaynaklar
            </div>

        </div>
        """
    )


    with gr.Tabs():


        with gr.Tab(
            "▤ Akademik Kaynaklar"
        ):

            akademik_html = gr.HTML(
                """
                <div class="small-placeholder">
                    Akademik kaynaklar burada gösterilecektir.
                </div>
                """
            )


        with gr.Tab(
            "◎ Genel Web Kaynakları"
        ):

            web_html = gr.HTML(
                """
                <div class="small-placeholder">
                    Web kaynakları burada gösterilecektir.
                </div>
                """
            )


    # --------------------------------------------------------
    # SINIRLAMALAR
    # --------------------------------------------------------

    with gr.Accordion(
        "Sınırlayıcı Noktalar",
        open=False
    ):

        sinirlamalar = gr.Markdown(
            ""
        )


    # --------------------------------------------------------
    # GÖRSELLER
    # --------------------------------------------------------

    gr.HTML(
        """
        <div class="section-head">

            <div class="section-kicker">
                GÖRSEL ARŞİV
            </div>

            <div class="section-title">
                İlgili Görseller
            </div>

        </div>
        """
    )


    gorsel_arsivi = gr.HTML(
        """
        <div class="small-placeholder">

            Araştırma yapıldığında
            ilgili görseller burada gösterilecektir.

        </div>
        """
    )


    # --------------------------------------------------------
    # ÖRNEK BUTONLAR
    # --------------------------------------------------------

    ornek1.click(
        lambda: ORNEK_VIKING,
        outputs=iddia_kutusu
    )


    ornek2.click(
        lambda: ORNEK_FATIH,
        outputs=iddia_kutusu
    )


    ornek3.click(
        lambda: ORNEK_LOZAN,
        outputs=iddia_kutusu
    )


    # --------------------------------------------------------
    # GERÇEK ARAŞTIRMA
    # --------------------------------------------------------

    arastir_butonu.click(

        fn=gradio_gercek_arastir,

        inputs=iddia_kutusu,

        outputs=[

            ilerleme_alani,

            sonuc_html,

            gerekce,

            guclu_kaynak,

            akademik_html,

            web_html,

            sinirlamalar,

            gorsel_arsivi

        ]

    )


# ============================================================
# 34. KUYRUK
# ============================================================

demo.queue()


# ============================================================
# 35. BAŞLAT
# ============================================================

print("\nTarihİz başlatılıyor...")

if __name__ == "__main__":
    # Istege bagli pilot erisimi: TARIHIZ_USERNAME ve TARIHIZ_PASSWORD
    # ortam degiskenleri birlikte tanimlandiysa sifre istenir.
    username = os.environ.get("TARIHIZ_USERNAME")
    password = os.environ.get("TARIHIZ_PASSWORD")
    auth = (username, password) if username and password else None
    demo.launch(
        share=False,
        debug=False,
        css=CSS,
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", "7860")),
        auth=auth
    )