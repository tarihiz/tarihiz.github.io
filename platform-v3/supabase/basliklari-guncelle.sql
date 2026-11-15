-- Yalnız tarihiz-sade-test projesinde SQL Editor > New query ile çalıştırın.
-- Sadece konu başlıkları değişir. Kimlikler, sıra, sorular, kaynaklar ve yanıtlar korunur.
-- Açık öğrenci oturumlarını kapatıp çalıştırın; sonra sayfayı yenileyin.
begin;
with titles(id,title) as (values
    ('20270000-0000-4000-8000-000000000003'::uuid, 'Göbeklitepe’de Toplumsal Yaşamın İzleri'),
    ('20270000-0000-4000-8000-000000000001'::uuid, 'Altın Elbiseli Adam: Giyim ve Kuşam Üzerine'),
    ('20270000-0000-4000-8000-000000000004'::uuid, 'Osmanlı’da Kahvehaneler ve Gündelik Yaşam'),
    ('20270000-0000-4000-8000-000000000002'::uuid, '1914’te Doğu Karadeniz’de Eğitime Erişim'),
    ('20270000-0000-4000-8000-000000000005'::uuid, 'Rize’de Köyden Şehre Ulaşım ve Gündelik Yaşam')
), updated_topics as (
  update public.tarihiz_topics t
  set title=n.title
  from titles n
  where t.id=n.id
  returning t.id,t.title
)
update public.tarihiz_topic_works w
set activity_snapshot=jsonb_set(w.activity_snapshot,'{title}',to_jsonb(t.title),true)
from updated_topics t
where w.topic_id=t.id
  and w.activity_snapshot->>'title' is distinct from t.title;
commit;

-- Beş başlığı sıralı olarak kontrol edin.
select id,title,sort_order from public.tarihiz_topics
where id in (
  '20270000-0000-4000-8000-000000000003'::uuid,
  '20270000-0000-4000-8000-000000000001'::uuid,
  '20270000-0000-4000-8000-000000000004'::uuid,
  '20270000-0000-4000-8000-000000000002'::uuid,
  '20270000-0000-4000-8000-000000000005'::uuid
) order by sort_order;
