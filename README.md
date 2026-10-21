# Tarihİz – Gradio uygulamasını yayınlama paketi

Kaynak: Kullanıcının Colab not defterindeki **59. hücre (indeks 58)**, görsel arşivi güncellemesi için **60. hücre (indeks 59)**.

## İçerik

- `app.py`: Gemini + Tavily + OpenAlex + Gradio, son bütünleşik sürümden aktarıldı.
- `requirements.txt`: Sunucu Python bağımlılıkları.
- `.python-version`: Render için Python 3.12.
- `render.yaml`: Render Blueprint ayarları (isteğe bağlı).
- `assets/`: Kendi orijinal banner görselinizi buraya `banner.png` adıyla yükleyin. Yoksa geçici bir arka plan görüntüsü kullanılır.

## GitHub'a yükleme

1. `https://github.com/tarihiz/tarihiz.github.io` deposunu açın.
2. ZIP'i bilgisayarınızda açın. `app.py`, `requirements.txt`, `.python-version`, `render.yaml` ve `.gitignore` dosyalarını deponun **ana dizinine** yükleyin. `assets/` klasörünü de ekleyin.
3. `index.html` dosyasını şimdilik **silmeden ve değiştirmeden** bırakın; mevcut GitHub Pages sitesi çalışmaya devam eder.
4. `GEMINI_API_KEY` ve `TAVILY_API_KEY` değerlerini asla GitHub'a ya da `app.py` içine yazmayın.

## Render'a bağlama

1. Render Dashboard > New > Web Service'den GitHub deposunu bağlayın.
2. Ortamı `Python`, Build Command'i `pip install -r requirements.txt`, Start Command'i `python app.py` seçin. Ücretsiz planı pilot amaçlı kullanabilirsiniz.
3. Environment kısmında `GEMINI_API_KEY` ve `TAVILY_API_KEY` değerlerini gizli ortam değişkenleri olarak girin.
4. İsterseniz öğrencilerin erişimini pilot için sınırlamak üzere `TARIHIZ_USERNAME` ve `TARIHIZ_PASSWORD` değerlerini birlikte tanımlayın.
5. Deploy loglarını kontrol edin; web servisinin verdiği HTTPS adresine giderek deneyin.

## GitHub Pages entegrasyonu

Render üzerinde çalışan gerçek URL belirlendikten sonra mevcut `index.html` dosyasına şu tür bir entegrasyon eklenebilir:

```html
<iframe src="RENDER_ADRESI_BURAYA" title="Tarihİz uygulaması" style="width:100%;height:92vh;border:0"></iframe>
```

Bu adım, çalışan uygulamanın URL'si alındıktan sonra yapılmalıdır. GitHub Pages Python çalıştırmaz.

## Test ve önemli sınırlar

- Kod Python sözdizimi bakımından kontrol edildi; Google/Tavily API anahtarları olmadan gerçek bir iddia değerlendirmesi uçtan uca doğrulanmadı.
- Colab'ın dosya yükleme adımı kaldırıldı. **Orijinal banner dosyası not defterinde bulunmadığı için** ayrıca yüklenmesi gerekiyor.
- Gradio sürüm farkları, Gemini/Tavily ücret ve limitleri, genel erişimde kötüye kullanım ve dış görsel adreslerinin sunucudan indirilmesi pilot uygulamadan önce kontrol edilmelidir.
- Öğrenci verisi toplanacaksa uygun gizlilik, izin ve veri saklama koşulları belirlenmelidir.
- Render'ın ücretsiz sunucusu kullanılmadığında uykuya geçebilir; gerçek kullanım için plan ve kota ihtiyacı ayrıca değerlendirilmelidir.
