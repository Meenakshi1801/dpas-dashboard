-- DPAS V2 cleanup: remove legacy percentage-scoring fields.
-- Run once in Supabase SQL Editor after the V2 app deployment.

alter table if exists public.alignment_evidence
    drop column if exists pas_score,
    drop column if exists alignment_category;

alter table if exists public.revisions
    drop column if exists revised_pas,
    drop column if exists revised_category;
