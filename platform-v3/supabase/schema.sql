-- Supabase SQL Editor; yalnızca yeni tarihiz_* tablolarını oluşturur.
begin;
create table public.tarihiz_participants (
 id uuid primary key default gen_random_uuid(),
 code_hash text not null unique check (length(code_hash)=64),
 label text not null,
 active boolean not null default true,
 created_at timestamptz not null default now()
);
create table public.tarihiz_sessions (
 token_hash text primary key,
 participant_id uuid not null references public.tarihiz_participants(id),
 expires_at timestamptz not null
);
create table public.tarihiz_works (
 id uuid primary key default gen_random_uuid(),
 participant_id uuid not null references public.tarihiz_participants(id),
 activity_id text not null,
 activity_snapshot jsonb not null,
 state jsonb not null,
 revision integer not null default 0,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now()
);
create index tarihiz_works_participant on public.tarihiz_works(participant_id,created_at desc);
create table public.tarihiz_rate_limits (
 bucket text primary key,
 window_start timestamptz not null default now(),
 hits integer not null default 1
);
alter table public.tarihiz_participants enable row level security;
alter table public.tarihiz_sessions enable row level security;
alter table public.tarihiz_works enable row level security;
alter table public.tarihiz_rate_limits enable row level security;
-- Öğrencinin tarayıcısı tablolara doğrudan erişmez. Tüm istekler API'de katılım oturumuyla kapsamlanır.
revoke all on public.tarihiz_participants, public.tarihiz_sessions, public.tarihiz_works, public.tarihiz_rate_limits from anon, authenticated;
grant select,insert,update,delete on public.tarihiz_participants, public.tarihiz_sessions, public.tarihiz_works, public.tarihiz_rate_limits to service_role;
create function public.tarihiz_rate_allow(p_key text,p_limit integer,p_seconds integer) returns boolean
language plpgsql security definer set search_path=public as $$
declare n integer;
begin
 if p_limit<1 or p_seconds<1 then return false; end if;
 insert into public.tarihiz_rate_limits(bucket,window_start,hits) values(p_key,now(),1)
 on conflict(bucket) do update set
 hits=case when tarihiz_rate_limits.window_start < now()-make_interval(secs=>p_seconds) then 1 else tarihiz_rate_limits.hits+1 end,
 window_start=case when tarihiz_rate_limits.window_start < now()-make_interval(secs=>p_seconds) then now() else tarihiz_rate_limits.window_start end
 returning hits into n;
 return n<=p_limit;
end $$;
revoke all on function public.tarihiz_rate_allow(text,integer,integer) from public, anon, authenticated;
grant execute on function public.tarihiz_rate_allow(text,integer,integer) to service_role;
commit;
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

alter table public.tarihiz_topics add column if not exists pilot boolean not null default false;

-- Display order, independent of stable topic identities.
alter table public.tarihiz_topics add column if not exists sort_order integer not null default 1000;
