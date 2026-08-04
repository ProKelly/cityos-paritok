-- Migration: adds career-chat tables (multi-turn conversation with the AI
-- career coach). Real accumulating history — the other content type
-- Paritok's compressor targets (old turns beyond a recent window), alongside
-- the tool_result content from the /recommend agent rewrite.
-- Safe to run on an existing project — only touches new objects.

create table if not exists chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text default 'Career chat',
  opportunity_id uuid references opportunities(id) on delete set null,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

alter table chat_sessions enable row level security;

create policy "chat_sessions_select_own" on chat_sessions for select using (auth.uid() = user_id);
create policy "chat_sessions_insert_own" on chat_sessions for insert with check (auth.uid() = user_id);
create policy "chat_sessions_update_own" on chat_sessions for update using (auth.uid() = user_id);
create policy "chat_sessions_delete_own" on chat_sessions for delete using (auth.uid() = user_id);

create table if not exists chat_messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references chat_sessions(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('user', 'assistant')),
  content text not null,
  created_at timestamptz default now()
);

alter table chat_messages enable row level security;

create policy "chat_messages_select_own" on chat_messages for select using (auth.uid() = user_id);
create policy "chat_messages_insert_own" on chat_messages for insert with check (auth.uid() = user_id);

create index if not exists chat_messages_session_idx on chat_messages (session_id, created_at);

drop trigger if exists chat_sessions_set_updated_at on chat_sessions;
create trigger chat_sessions_set_updated_at
  before update on chat_sessions
  for each row execute function set_updated_at();
