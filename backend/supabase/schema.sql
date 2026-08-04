-- OpportunityOS AI — Supabase schema
-- Run this in the Supabase SQL editor (Project > SQL Editor > New query).

create extension if not exists vector;

-- ─────────────────────────────────────────────────────────────────────────
-- PROFILES
-- ─────────────────────────────────────────────────────────────────────────
create table if not exists profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  full_name text not null,
  country text not null,
  education_level text not null,
  skills text[] default '{}',
  interests text[] default '{}',
  goals text default '',
  preferred_industries text[] default '{}',
  preferred_countries text[] default '{}',
  availability text default '',
  expected_salary text,
  languages text[] default '{}',
  resume_text text,
  opportunity_dna jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  unique (user_id)
);

alter table profiles enable row level security;

create policy "profiles_select_own" on profiles for select using (auth.uid() = user_id);
create policy "profiles_insert_own" on profiles for insert with check (auth.uid() = user_id);
create policy "profiles_update_own" on profiles for update using (auth.uid() = user_id);
create policy "profiles_delete_own" on profiles for delete using (auth.uid() = user_id);

-- ─────────────────────────────────────────────────────────────────────────
-- OPPORTUNITIES  (shared knowledge base — readable by all authenticated users)
-- ─────────────────────────────────────────────────────────────────────────
create table if not exists opportunities (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  organization text not null,
  description text not null,
  country text default 'Global',
  category text not null check (category in (
    'Scholarships','Jobs','Internships','Grants','Competitions',
    'Accelerators','Fellowships','Conferences','Events','Volunteering'
  )),
  deadline date,
  eligibility text default '',
  skills text[] default '{}',
  url text not null,
  embedding vector(384),
  created_by uuid references auth.users(id),
  created_at timestamptz default now()
);

alter table opportunities enable row level security;

create policy "opportunities_select_all" on opportunities for select using (true);
create policy "opportunities_insert_auth" on opportunities for insert with check (auth.uid() is not null);

create index if not exists opportunities_embedding_idx
  on opportunities using ivfflat (embedding vector_cosine_ops) with (lists = 100);

create index if not exists opportunities_category_idx on opportunities (category);
create index if not exists opportunities_deadline_idx on opportunities (deadline);

-- Semantic search RPC used by /recommend. Returns the closest N opportunities
-- to a query embedding by cosine distance.
create or replace function match_opportunities(
  query_embedding vector(384),
  match_count int default 20
)
returns setof opportunities
language sql stable
as $$
  select *
  from opportunities
  order by embedding <=> query_embedding
  limit match_count;
$$;

-- ─────────────────────────────────────────────────────────────────────────
-- SAVED OPPORTUNITIES
-- ─────────────────────────────────────────────────────────────────────────
create table if not exists saved_opportunities (
  user_id uuid not null references auth.users(id) on delete cascade,
  opportunity_id uuid not null references opportunities(id) on delete cascade,
  created_at timestamptz default now(),
  primary key (user_id, opportunity_id)
);

alter table saved_opportunities enable row level security;

create policy "saved_select_own" on saved_opportunities for select using (auth.uid() = user_id);
create policy "saved_insert_own" on saved_opportunities for insert with check (auth.uid() = user_id);
create policy "saved_delete_own" on saved_opportunities for delete using (auth.uid() = user_id);

-- ─────────────────────────────────────────────────────────────────────────
-- APPLICATIONS  (tracks "Applied" state for the dashboard)
-- ─────────────────────────────────────────────────────────────────────────
create table if not exists applications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  opportunity_id uuid not null references opportunities(id) on delete cascade,
  status text default 'applied' check (status in ('applied','interviewing','offered','rejected')),
  notes text,
  created_at timestamptz default now(),
  unique (user_id, opportunity_id)
);

alter table applications enable row level security;

create policy "applications_select_own" on applications for select using (auth.uid() = user_id);
create policy "applications_insert_own" on applications for insert with check (auth.uid() = user_id);
create policy "applications_update_own" on applications for update using (auth.uid() = user_id);

-- ─────────────────────────────────────────────────────────────────────────
-- RECOMMENDATIONS  (cached AI matching results, powers the dashboard card)
-- ─────────────────────────────────────────────────────────────────────────
create table if not exists recommendations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  results jsonb not null,
  created_at timestamptz default now()
);

alter table recommendations enable row level security;

create policy "recommendations_select_own" on recommendations for select using (auth.uid() = user_id);
create policy "recommendations_insert_own" on recommendations for insert with check (auth.uid() = user_id);

-- ─────────────────────────────────────────────────────────────────────────
-- ROADMAPS
-- ─────────────────────────────────────────────────────────────────────────
create table if not exists roadmaps (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  goal text not null,
  plan jsonb not null,
  created_at timestamptz default now()
);

alter table roadmaps enable row level security;

create policy "roadmaps_select_own" on roadmaps for select using (auth.uid() = user_id);
create policy "roadmaps_insert_own" on roadmaps for insert with check (auth.uid() = user_id);

-- ─────────────────────────────────────────────────────────────────────────
-- DOCUMENTS  (generated CVs and cover letters — history for /documents)
-- ─────────────────────────────────────────────────────────────────────────
create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  doc_type text not null check (doc_type in ('cv', 'cover_letter')),
  description text default '',
  opportunity_id uuid references opportunities(id) on delete set null,
  content jsonb not null,
  created_at timestamptz default now()
);

alter table documents enable row level security;

create policy "documents_select_own" on documents for select using (auth.uid() = user_id);
create policy "documents_insert_own" on documents for insert with check (auth.uid() = user_id);
create policy "documents_delete_own" on documents for delete using (auth.uid() = user_id);

create index if not exists documents_user_type_idx on documents (user_id, doc_type, created_at desc);

-- ─────────────────────────────────────────────────────────────────────────
-- updated_at trigger for profiles
-- ─────────────────────────────────────────────────────────────────────────
create or replace function set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists profiles_set_updated_at on profiles;
create trigger profiles_set_updated_at
  before update on profiles
  for each row execute function set_updated_at();