-- DPAS V2 lesson procedure migration
create table if not exists public.lesson_procedures (
    id uuid primary key default gen_random_uuid(),
    lesson_id uuid not null references public.lesson_submissions(id) on delete cascade,
    introduction text,
    concept_development text,
    learning_activity text,
    assessment_during_lesson text,
    closure_consolidation text,
    created_at timestamptz default now(),
    updated_at timestamptz default now(),
    unique (lesson_id)
);

alter table public.lesson_procedures enable row level security;

drop policy if exists "student manages lesson procedure" on public.lesson_procedures;
create policy "student manages lesson procedure"
on public.lesson_procedures
for all
to authenticated
using (
    exists (
        select 1
        from public.lesson_submissions l
        where l.id = lesson_id
          and l.student_id = auth.uid()
    )
)
with check (
    exists (
        select 1
        from public.lesson_submissions l
        where l.id = lesson_id
          and l.student_id = auth.uid()
    )
);

drop policy if exists "reviewer reads lesson procedure" on public.lesson_procedures;
create policy "reviewer reads lesson procedure"
on public.lesson_procedures
for select
to authenticated
using (
    exists (
        select 1
        from public.lesson_submissions l
        where l.id = lesson_id
          and l.reviewer_id = auth.uid()
    )
);
