-- DPAS V2 authentication, teacher directory, routing and RLS migration
-- Run once in Supabase SQL Editor.

alter table public.profiles
    alter column user_code drop not null;

alter table public.profiles
    add column if not exists email text,
    add column if not exists designation text,
    add column if not exists institution text;

alter table public.profiles
    drop constraint if exists profiles_role_check;

alter table public.profiles
    add constraint profiles_role_check
    check (role in ('student','teacher_educator'));

-- Existing profile IDs were generated independently. New authenticated accounts use auth.users IDs.
-- The app writes the authenticated user ID explicitly.

alter table public.lesson_submissions
    alter column student_code drop not null;

alter table public.lesson_submissions
    add column if not exists student_id uuid references auth.users(id) on delete cascade,
    add column if not exists reviewer_id uuid references auth.users(id) on delete set null;

create index if not exists lesson_submissions_student_id_idx
    on public.lesson_submissions(student_id);

create index if not exists lesson_submissions_reviewer_id_idx
    on public.lesson_submissions(reviewer_id);

-- Automatically create/update a public profile from Supabase Auth metadata.
create or replace function public.handle_new_dpas_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, user_code, email, full_name, role, designation, institution)
  values (
    new.id,
    null,
    new.email,
    coalesce(new.raw_user_meta_data->>'full_name', ''),
    coalesce(new.raw_user_meta_data->>'role', 'student'),
    coalesce(new.raw_user_meta_data->>'designation', ''),
    coalesce(new.raw_user_meta_data->>'institution', '')
  )
  on conflict (id) do update set
    email = excluded.email,
    full_name = excluded.full_name,
    role = excluded.role,
    designation = excluded.designation,
    institution = excluded.institution;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created_dpas on auth.users;
create trigger on_auth_user_created_dpas
after insert or update of raw_user_meta_data, email on auth.users
for each row execute procedure public.handle_new_dpas_user();

-- RLS
alter table public.profiles enable row level security;
alter table public.lesson_submissions enable row level security;
alter table public.design_decisions enable row level security;
alter table public.alignment_evidence enable row level security;
alter table public.educator_verification enable row level security;
alter table public.revisions enable row level security;

drop policy if exists "profiles authenticated read" on public.profiles;
create policy "profiles authenticated read"
on public.profiles for select
to authenticated
using (true);

drop policy if exists "profiles own update" on public.profiles;
create policy "profiles own update"
on public.profiles for update
to authenticated
using (id = auth.uid())
with check (id = auth.uid());

drop policy if exists "students insert own lessons" on public.lesson_submissions;
create policy "students insert own lessons"
on public.lesson_submissions for insert
to authenticated
with check (student_id = auth.uid());

drop policy if exists "lesson participants read" on public.lesson_submissions;
create policy "lesson participants read"
on public.lesson_submissions for select
to authenticated
using (student_id = auth.uid() or reviewer_id = auth.uid());

drop policy if exists "students update own lessons" on public.lesson_submissions;
create policy "students update own lessons"
on public.lesson_submissions for update
to authenticated
using (student_id = auth.uid())
with check (student_id = auth.uid());

drop policy if exists "reviewer update assigned lesson" on public.lesson_submissions;
create policy "reviewer update assigned lesson"
on public.lesson_submissions for update
to authenticated
using (reviewer_id = auth.uid())
with check (reviewer_id = auth.uid());

drop policy if exists "student manages design decisions" on public.design_decisions;
create policy "student manages design decisions"
on public.design_decisions for all
to authenticated
using (
  exists (
    select 1 from public.lesson_submissions l
    where l.id = lesson_id and l.student_id = auth.uid()
  )
)
with check (
  exists (
    select 1 from public.lesson_submissions l
    where l.id = lesson_id and l.student_id = auth.uid()
  )
);

drop policy if exists "reviewer reads design decisions" on public.design_decisions;
create policy "reviewer reads design decisions"
on public.design_decisions for select
to authenticated
using (
  exists (
    select 1 from public.lesson_submissions l
    where l.id = lesson_id and l.reviewer_id = auth.uid()
  )
);

drop policy if exists "student manages alignment evidence" on public.alignment_evidence;
create policy "student manages alignment evidence"
on public.alignment_evidence for all
to authenticated
using (
  exists (
    select 1 from public.lesson_submissions l
    where l.id = lesson_id and l.student_id = auth.uid()
  )
)
with check (
  exists (
    select 1 from public.lesson_submissions l
    where l.id = lesson_id and l.student_id = auth.uid()
  )
);

drop policy if exists "reviewer reads alignment evidence" on public.alignment_evidence;
create policy "reviewer reads alignment evidence"
on public.alignment_evidence for select
to authenticated
using (
  exists (
    select 1 from public.lesson_submissions l
    where l.id = lesson_id and l.reviewer_id = auth.uid()
  )
);

drop policy if exists "student reads verification" on public.educator_verification;
create policy "student reads verification"
on public.educator_verification for select
to authenticated
using (
  exists (
    select 1 from public.lesson_submissions l
    where l.id = lesson_id and l.student_id = auth.uid()
  )
);

drop policy if exists "reviewer manages verification" on public.educator_verification;
create policy "reviewer manages verification"
on public.educator_verification for all
to authenticated
using (
  exists (
    select 1 from public.lesson_submissions l
    where l.id = lesson_id and l.reviewer_id = auth.uid()
  )
)
with check (
  exists (
    select 1 from public.lesson_submissions l
    where l.id = lesson_id and l.reviewer_id = auth.uid()
  )
);

drop policy if exists "student manages revisions" on public.revisions;
create policy "student manages revisions"
on public.revisions for all
to authenticated
using (
  exists (
    select 1 from public.lesson_submissions l
    where l.id = lesson_id and l.student_id = auth.uid()
  )
)
with check (
  exists (
    select 1 from public.lesson_submissions l
    where l.id = lesson_id and l.student_id = auth.uid()
  )
);

drop policy if exists "reviewer reads revisions" on public.revisions;
create policy "reviewer reads revisions"
on public.revisions for select
to authenticated
using (
  exists (
    select 1 from public.lesson_submissions l
    where l.id = lesson_id and l.reviewer_id = auth.uid()
  )
);


-- Backfill profiles for accounts that existed before this migration/trigger.
insert into public.profiles (id, user_code, email, full_name, role, designation, institution)
select
  u.id,
  null,
  u.email,
  coalesce(u.raw_user_meta_data->>'full_name', ''),
  coalesce(u.raw_user_meta_data->>'role', 'student'),
  coalesce(u.raw_user_meta_data->>'designation', ''),
  coalesce(u.raw_user_meta_data->>'institution', '')
from auth.users u
on conflict (id) do update set
  email = excluded.email,
  full_name = excluded.full_name,
  role = excluded.role,
  designation = excluded.designation,
  institution = excluded.institution;
