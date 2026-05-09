-- CuidarBem - Modo Família Sincronizado via Supabase
-- Rode este arquivo em Supabase > SQL Editor > New query > Run.

create table if not exists public.cuidarbem_family_state (
  id uuid primary key default gen_random_uuid(),
  family_code text not null unique,
  family_secret text not null,
  state jsonb not null default '{}'::jsonb,
  updated_by text,
  updated_at_client text,
  updated_at timestamptz not null default now()
);

alter table public.cuidarbem_family_state enable row level security;

drop policy if exists "CuidarBem family select by secret" on public.cuidarbem_family_state;
drop policy if exists "CuidarBem family insert by secret" on public.cuidarbem_family_state;
drop policy if exists "CuidarBem family update by secret" on public.cuidarbem_family_state;

create policy "CuidarBem family select by secret"
on public.cuidarbem_family_state
for select
to anon
using (
  family_secret = coalesce((current_setting('request.headers', true)::json ->> 'x-cb-family-secret'), '')
);

create policy "CuidarBem family insert by secret"
on public.cuidarbem_family_state
for insert
to anon
with check (
  family_secret = coalesce((current_setting('request.headers', true)::json ->> 'x-cb-family-secret'), '')
);

create policy "CuidarBem family update by secret"
on public.cuidarbem_family_state
for update
to anon
using (
  family_secret = coalesce((current_setting('request.headers', true)::json ->> 'x-cb-family-secret'), '')
)
with check (
  family_secret = coalesce((current_setting('request.headers', true)::json ->> 'x-cb-family-secret'), '')
);

create or replace function public.set_cuidarbem_family_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_cuidarbem_family_updated_at on public.cuidarbem_family_state;
create trigger trg_cuidarbem_family_updated_at
before update on public.cuidarbem_family_state
for each row
execute function public.set_cuidarbem_family_updated_at();
