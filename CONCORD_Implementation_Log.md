# CONCORD-Teach | Research-design implementation log

**Application version:** 1.1.0-pilot  
**Code branch used by the renamed deployment:** `v1-revised-study`  
**Parallel development branch:** `concord-teach`  
**Implementation date:** 19 October 2026

## Purpose
This log records implementation responses to the seven-expert appraisal and the subsequent researcher revision report. It is not proof of software validation, validated measurement, or intervention effectiveness. The original rated specifications, signed forms, and ratings matrix remain separate source records.

## Mapping to proposed revision register

| ID | What changed or remains outstanding | Status |
| --- | --- | --- |
| RV-01 / A01 | About text now defines context-sensitive lesson-planning coherence as reasoned fit among outcome, cognitive demands, activities, participation, supports and assessment evidence. | Implemented in copy; wording still requires acceptance/review. |
| RV-02 / A02, A04 | Introduced a frozen initial plan, formative judgments, a profile, reflection and a revised lesson plan. Explicitly distinguishes self-report from independent lesson-quality and teaching-performance outcomes. | Workflow implemented; proposed learning mechanism remains untested. |
| RV-03 / B03, C04 | Added prior knowledge, classroom context, resource/constraint and learner-support rationale prompts; no intrinsically preferred support or engagement option. | Implemented; user comprehension untested. |
| RV-04 / E01–E06 | Replaced four numeric fit ratings with four non-numeric judgments, dimension-specific questions, and mandatory textual justification for every dimension. | Implemented; pilot-test wording. |
| RV-05 / E07, A02 | Removed the numerical 0–100 gauge, arbitrary cut-offs and overall grade. Profile displays each dimension's response and rationale. | Implemented; usability review pending. |
| RV-06 / E08, F07 | Added substantive activity, learner participation, assessment task/evidence, full initial-plan freeze, editable revised plan, original–revised differences and written retention/revision rationale. | Implemented; test sample lesson plans. |
| RV-07 / F03 | Added pseudonymous participant codes, cycle 1–3, UTC timestamps, app version, record ID, and per-lesson/session CSV export. | **Partially implemented.** No secure persistent database, login, server-side access controls, central longitudinal record reconciliation, or automatic backups. Not yet appropriate for live main-study data. |
| RV-08 / B02, C02, C03 | Clarified purpose, strategy, and engagement prompts, including what learners will actually do. | Implemented; pilot comprehension testing pending. |
| RV-09 / F01 | Usability, accessibility, data-completeness, timing, functionality, and prospective participant testing with pre-service teachers. | **Not yet conducted**. |
| RV-10 / review record gaps | Verify signed original expert responses, scenario/overall responses, reviewer dates and version exposure; finalise revisions register with approval. | **Researcher action pending**. |

## Record handling and important limitation
- Data are retained in Streamlit `st.session_state`, not a protected server-side research database.
- Each completed cycle can be exported to a CSV containing the initial and final lesson plans, five judgments and explanations, reflection and metadata.
- Refreshing/reopening a browser may reset the current session. The researcher must retrieve the exported data in accordance with an approved retention plan.
- Do **not** enter personally identifying information, deploy this as a production participant data system, or assume that a public deployment provides access controls.
- Before the main study, implement secure per-participant persistence, restricted researcher access, data integrity checks, backup and restoration tests, and a documented data-retention plan.

## Verification required before participant pilot
1. Confirm the deployed Streamlit app successfully runs version `1.1.0-pilot` with both branches synchronized.
2. Test all four response options for each of the five dimensions, including uncertainty and mandatory justifications.
3. Test incomplete input handling, empty options, long responses, revising and retaining a plan, and CSV exports.
4. Confirm that duplicate participant+cycle records are not saved within a single session.
5. Test flow cycle 1 to 2 to 3, including closure/reloading and loss-of-session warnings.
6. Confirm accessibility, instructions and concept interpretation with target pre-service teachers.
7. Validate the **independent** lesson-plan-quality rubric and teaching-performance observation schedule separately.

## Reporting boundary
Expert content appraisal (seven experts, 36 items) concerned the **proposed conceptual and design specification**. This log records a software implementation response; it does not imply that experts tested the revised running software or that any empirical outcomes have improved.
