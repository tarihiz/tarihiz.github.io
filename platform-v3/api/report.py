from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

LABELS={'evidence':'Kaynağın sunduğu kanıtlar','strengths':'Kanıtların güçlü yönleri','limits':'Kanıtların sınırlılıkları','judgment':'Genel değerlendirme / gerekçeli karar','support':'Kaynaklar hangi noktalarda birbirini destekliyor?','conflict':'Kaynaklar arasında hangi farklılıklar veya çelişkiler bulunuyor?','result':'Kaynakların güçlü ve sınırlı yönlerini dikkate alarak nasıl bir sonuca ulaşıyorsun?'}

def make_pdf(work,activity):
    font=Path(__file__).resolve().parent.parent/'vendor/DejaVuSans.ttf'
    if 'TarihIz' not in pdfmetrics.getRegisteredFontNames():pdfmetrics.registerFont(TTFont('TarihIz',str(font)))
    styles=getSampleStyleSheet()
    for name in ['Normal','Title','Heading1','Heading2']:
        styles[name].fontName='TarihIz';styles[name].textColor=colors.HexColor('#163643')
    styles['Normal'].fontSize=10;styles['Normal'].leading=15;styles['Normal'].wordWrap='CJK'
    styles['Title'].fontSize=23;styles['Title'].leading=30
    styles['Heading1'].fontSize=16;styles['Heading1'].leading=22
    styles['Heading2'].fontSize=12;styles['Heading2'].leading=18
    story=[]
    def p(text,style='Normal'):
        story.append(Paragraph(escape(str(text)).replace('\n','<br/>'),styles[style]));story.append(Spacer(1,7))
    p('Tarihİz · Çalışma Raporu','Title');p('Yapay Zekâ Destekli Tarihsel Kaynak Değerlendirme Platformu')
    p(activity['question'],'Heading1');p('Çalışma kimliği: '+work['id']);p('Başlangıç: '+work['created_at'])
    s=work['state'];p('Belge öncesi değerlendirme','Heading1');p(s['answers']['meta'])
    for key, label in [('metaAddendum','Sonradan eklenen not'),('documentNote','Belge inceleme notları')]:
        if s['answers'].get(key):
            p(label,'Heading2');p(s['answers'][key])
    for group,title in [('single','Tek Kaynak Değerlendirme'),('multi','Çoklu Kaynak Karşılaştırma')]:
        p(title,'Heading1')
        for suffix,phase in [('First','İlk değerlendirme'),('Final','Son değerlendirme')]:
            p(phase,'Heading2')
            for key,value in s['answers'][group+suffix].items():p(LABELS[key],'Heading2');p(value)
        p('Yapay Zekâ ile Sorgulama','Heading2')
        for m in s['chats'][group]['messages']:
            p(('Öğrenci: ' if m['role']=='student' else 'Yapay zekâ: ')+m['text'])
    p('Nihai tarihsel sonuç','Heading1');p(s['answers']['conclusion'])
    p('Kaynak künyeleri','Heading1')
    for source in activity['sources']:
        p(source['title'],'Heading2')
        for key,label in [('creator','Oluşturan'),('date','Tarih'),('place','Yer'),('purpose','Amaç'),('type','Belge türü'),('reference','Kaynak')]:p(label+': '+source[key])
    stream=BytesIO()
    def footer(canvas,doc):
        canvas.setFont('TarihIz',8);canvas.setFillColor(colors.HexColor('#677577'));canvas.drawString(45,27,'Tarihİz · Öğrenme süreci raporu');canvas.drawRightString(550,27,str(doc.page))
    SimpleDocTemplate(stream,pagesize=(595.28,841.89),rightMargin=45,leftMargin=45,topMargin=42,bottomMargin=45).build(story,onFirstPage=footer,onLaterPages=footer)
    return stream.getvalue()
