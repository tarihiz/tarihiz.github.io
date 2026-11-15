-- Existing installations: run this migration only.
begin;
create table if not exists public.tarihiz_topics (
 id uuid primary key default gen_random_uuid(),
 title text not null check (length(trim(title)) > 0),
 question text not null check (length(trim(question)) > 0),
 sources jsonb not null check (jsonb_typeof(sources) = 'array' and jsonb_array_length(sources) > 0),
 demo boolean not null default false
);
create table if not exists public.tarihiz_topic_works (
 id uuid primary key default gen_random_uuid(),
 participant_id uuid not null references public.tarihiz_participants(id),
 topic_id uuid not null references public.tarihiz_topics(id),
 activity_snapshot jsonb not null,
 state jsonb not null,
 revision integer not null default 0,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now(),
 unique (participant_id, topic_id)
);
alter table public.tarihiz_topics enable row level security;
alter table public.tarihiz_topic_works enable row level security;
revoke all on public.tarihiz_topics, public.tarihiz_topic_works from public, anon, authenticated;
grant select on public.tarihiz_topics to service_role;
grant select,insert,update on public.tarihiz_topic_works to service_role;
commit;
