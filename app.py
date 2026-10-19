from __future__ import annotations

import csv
import io
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st


APP_NAME = "CONCORD-Teach"
APP_VERSION = "1.1.0-pilot"
APP_SUBTITLE = "A Context-Sensitive Reflective Lesson-Planning Environment"

LESSON_PURPOSES = [
    "Introduce a new concept",
    "Develop conceptual understanding",
    "Practice or apply learning",
    "Analyse or investigate",
    "Consolidate or revise",
    "Assess learning",
    "Other (describe in the activity)",
]
COGNITIVE_LEVELS = [
    "C1 - Remember", "C2 - Understand", "C3 - Apply",
    "C4 - Analyse", "C5 - Evaluate", "C6 - Create",
]
STRATEGIES = [
    "Lecture / Explanation", "Discussion", "Activity-Based",
    "Inquiry-Based", "Experiential / Problem-Based",
    "Demonstration", "Collaborative Learning", "Other (describe below)",
]
ENGAGEMENT_MODES = [
    "Individual", "Pair", "Small Group", "Whole Class", "Mixed / Flexible",
]
SUPPORT_OPTIONS = [
    "No specific support currently identified (explain why)",
    "Specific learner/context need identified and supported",
    "Differentiated support planned",
    "Flexible support depending on learner response",
]
ASSESSMENT_OPTIONS = [
    "Formative Assessment", "Summative Assessment", "Peer Assessment",
    "Self-Assessment", "Teacher Observation / Questioning",
    "Performance / Product Assessment", "Combination of approaches",
]

# Deliberately categorical, not a numerical rating scale.
ALIGNMENT_RESPONSES = [
    "I can justify the alignment.",
    "I see partial alignment and scope for refinement.",
    "I identify a mismatch requiring revision.",
    "I cannot yet judge the alignment; more planning detail is needed.",
]
REASONING_PROMPTS = {
    ALIGNMENT_RESPONSES[0]:
        "Explain why this choice fits the intended outcome, purpose, and context.",
    ALIGNMENT_RESPONSES[1]:
        "Identify what fits, what does not fully fit, and what might be refined.",
    ALIGNMENT_RESPONSES[2]:
        "Describe the mismatch and a contextually appropriate alternative.",
    ALIGNMENT_RESPONSES[3]:
        "Specify the information or planning detail needed before you can judge.",
}
DIMENSIONS = [
    (
        "cognitive", "Outcome–Cognitive Demand Alignment",
        "Does the cognitive work actually required by the planned activity match the intended learning outcome?",
    ),
    (
        "strategy", "Outcome–Strategy Alignment",
        "Will this strategy provide a suitable learning opportunity for the outcome, purpose and learners?",
    ),
    (
        "engagement", "Engagement-Mode Appropriateness",
        "Does the participation arrangement help learners undertake the intended learning activity?",
    ),
    (
        "context", "Context/Inclusivity Appropriateness",
        "Are relevant prior knowledge, learner barriers, supports, and classroom conditions appropriately considered?",
    ),
    (
        "assessment", "Outcome–Assessment Alignment",
        "Will the specific assessment task generate evidence of the intended learning outcome?",
    ),
]
TEXT_FIELDS = [
    ("topic", "Subject and lesson topic"),
    ("class_level", "Class / grade / stage"),
    ("intended_outcome", "Intended Learning Outcome"),
    ("learner_context", "Learner and classroom context"),
    ("resources", "Resources, time and contextual constraints"),
    ("activity", "Planned learning activity and procedure"),
    ("engagement_plan", "What learners will actually do"),
    ("support_plan", "Planned learner support / inclusion rationale"),
    ("assessment_evidence", "Specific assessment task and expected evidence"),
]
CHOICE_FIELDS = [
    ("lesson_purpose", "Lesson Purpose", LESSON_PURPOSES),
    ("cognitive", "Planned Cognitive Demand", COGNITIVE_LEVELS),
    ("strategy", "Pedagogical Strategy", STRATEGIES),
    ("engagement", "Learner Engagement Mode", ENGAGEMENT_MODES),
    ("inclusivity", "Learner Support / Inclusivity", SUPPORT_OPTIONS),
    ("assessment", "Assessment Approach", ASSESSMENT_OPTIONS),
]
LESSON_FIELDS = [
    "topic", "class_level", "intended_outcome", "lesson_purpose",
    "learner_context", "resources", "cognitive", "strategy", "engagement",
    "inclusivity", "assessment", "activity", "engagement_plan",
    "support_plan", "assessment_evidence",
]
FIELD_LABELS = {
    **{key: label for key, label in TEXT_FIELDS},
    **{key: label for key, label, _ in CHOICE_FIELDS},
}
INITIAL_WIDGET_KEYS = (
    ["participant_code", "cycle_number"]
    + [f"initial_{key}" for key in LESSON_FIELDS]
    + [f"judgment_{code}" for code, _, _ in DIMENSIONS]
    + [f"reason_{code}" for code, _, _ in DIMENSIONS]
)
REVISION_WIDGET_KEYS = (
    [f"revised_{key}" for key in LESSON_FIELDS]
    + ["overall_reflection", "revision_explanation"]
)


def timestamp_utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def collect_initial_lesson():
    return {
        key: st.session_state.get(f"initial_{key}", "")
        for key in LESSON_FIELDS
    }


def collect_revised_lesson():
    return {
        key: st.session_state.get(f"revised_{key}", "")
        for key in LESSON_FIELDS
    }


def collect_judgments():
    return {
        code: {
            "dimension": label,
            "judgment": st.session_state.get(f"judgment_{code}", ""),
            "justification": st.session_state.get(f"reason_{code}", "").strip(),
        }
        for code, label, _ in DIMENSIONS
    }


def validate_initial(participant, cycle, lesson, judgments):
    errors = []
    if not re.fullmatch(r"[A-Za-z0-9_-]{3,24}", participant or ""):
        errors.append("Enter a pseudonymous participant code of 3–24 letters, digits, hyphens or underscores.")
    if cycle not in (1, 2, 3):
        errors.append("Select intervention cycle 1, 2 or 3.")
    mandatory_text = {
        "topic": 3,
        "class_level": 1,
        "intended_outcome": 15,
        "learner_context": 12,
        "activity": 30,
        "engagement_plan": 12,
        "support_plan": 12,
        "assessment_evidence": 20,
    }
    for field, minimum in mandatory_text.items():
        if len(str(lesson.get(field) or "").strip()) < minimum:
            errors.append(f"Provide a meaningful response for '{FIELD_LABELS[field]}' (at least {minimum} characters).")
    for field, _, _ in CHOICE_FIELDS:
        if lesson.get(field) in ("", None):
            errors.append(f"Select '{FIELD_LABELS[field]}'.")
    for code, title, _ in DIMENSIONS:
        result = judgments[code]
        if result["judgment"] not in ALIGNMENT_RESPONSES:
            errors.append(f"Select an appraisal response for '{title}'.")
        if len(result["justification"]) < 20:
            errors.append(f"Justify your response for '{title}' (at least 20 characters).")
    for existing in st.session_state["saved_records"]:
        if existing["participant_code"] == participant and existing["cycle_number"] == cycle:
            errors.append("This participant and cycle are already recorded in this browser session. Select a different cycle or participant.")
            break
    return errors


def seed_revision_inputs(original):
    if st.session_state.get("revision_seeded"):
        return
    for key in LESSON_FIELDS:
        st.session_state[f"revised_{key}"] = original.get(key, "")
    st.session_state["revision_seeded"] = True


def changes_between(before, after):
    return [
        FIELD_LABELS[key] for key in LESSON_FIELDS
        if str(before.get(key, "")).strip() != str(after.get(key, "")).strip()
    ]


def flattened_record(record):
    flat = {
        "App Version": record["app_version"],
        "Participant Code": record["participant_code"],
        "Intervention Cycle": record["cycle_number"],
        "Lesson Record ID": record["lesson_id"],
        "Initial Plan Timestamp UTC": record["initial_timestamp_utc"],
        "Revision Timestamp UTC": record["revision_timestamp_utc"],
    }
    for key in LESSON_FIELDS:
        label = FIELD_LABELS[key]
        flat[f"Initial — {label}"] = record["original_lesson"].get(key, "")
        flat[f"Revised — {label}"] = record["revised_lesson"].get(key, "")
    for code, label, _ in DIMENSIONS:
        response = record["judgments"][code]
        flat[f"{label} — self-reported judgment"] = response["judgment"]
        flat[f"{label} — justification"] = response["justification"]
    flat["Overall Reflection"] = record["overall_reflection"]
    flat["Revision / Retention Explanation"] = record["revision_explanation"]
    flat["Changed Fields"] = "; ".join(record["changed_fields"])
    flat["Number of Changed Fields (descriptive only)"] = len(record["changed_fields"])
    return flat


def export_csv(records):
    if not records:
        return ""
    flattened = [flattened_record(record) for record in records]
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=list(flattened[0].keys()))
    writer.writeheader()
    writer.writerows(flattened)
    return stream.getvalue().encode("utf-8-sig")


def reset_lesson(next_cycle=False):
    previous = st.session_state.get("initial_snapshot") or {}
    previous_code = previous.get("participant_code", "")
    previous_cycle = previous.get("cycle_number")
    for key in INITIAL_WIDGET_KEYS + REVISION_WIDGET_KEYS:
        st.session_state.pop(key, None)
    st.session_state["initial_snapshot"] = None
    st.session_state["saved_current"] = False
    st.session_state["revision_seeded"] = False
    if next_cycle:
        st.session_state["participant_code"] = previous_code
        if previous_cycle in (1, 2):
            st.session_state["cycle_number"] = previous_cycle + 1


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧭",
    layout="centered",
)
st.session_state.setdefault("saved_records", [])
st.session_state.setdefault("initial_snapshot", None)
st.session_state.setdefault("saved_current", False)
st.session_state.setdefault("revision_seeded", False)

st.title(APP_NAME)
st.caption(APP_SUBTITLE)

photo_path = Path(__file__).parent / "profile_photo.png"
information_column, photo_column = st.columns([3, 1])
with information_column:
    st.write(
        "CONCORD-Teach scaffolds pre-service teachers' **context-sensitive lesson-planning "
        "coherence**: the reasoned fit among intended outcomes, cognitive demands, "
        "instructional activities, learner participation and supports, and assessment "
        "evidence for a particular teaching context."
    )
    st.markdown(
        "**Conceptualized and developed by:** Dr. Meenakshi Dwivedi  \n"
        "Assistant Professor, School of Education  \n"
        "Mahatma Jyotiba Phule Rohilkhand University  \n"
        "Bareilly, Uttar Pradesh, India"
    )
with photo_column:
    if photo_path.exists():
        st.image(str(photo_path), width=165, caption="Dr. Meenakshi Dwivedi")

st.info(
    "No cognitive level, teaching method, engagement format, support label, or "
    "assessment type is automatically superior. Appropriateness depends on the "
    "outcome, lesson purpose, learner needs and teaching context."
)
st.caption(
    f"{APP_VERSION} · Pilot implementation. Self-reported judgments are formative, "
    "not objective measures of lesson-plan quality or teaching performance."
)
st.warning(
    "**Research-data limitation:** This prototype retains completed records only "
    "in the current browser session. It does not yet have secure, persistent "
    "research storage, participant authentication or server-side access controls. "
    "Download a copy before closing or refreshing your session. Do not enter "
    "participant names or other identifying information. Do not use this build "
    "for the main experiment until its data-management process has been approved and tested."
)

snapshot = st.session_state["initial_snapshot"]

if snapshot is None:
    st.markdown("---")
    st.subheader("1. Research Record and Lesson Context")
    st.text_input(
        "Pseudonymous Participant Code",
        key="participant_code",
        placeholder="e.g., CT-P001 (not a student's name)",
        help="Use an approved coded identifier. Avoid names, emails or enrollment numbers.",
    )
    st.selectbox(
        "Intervention Cycle",
        options=[1, 2, 3],
        index=None,
        key="cycle_number",
        placeholder="Select a cycle",
    )
    st.text_input("Subject and Lesson Topic", key="initial_topic")
    st.text_input("Class / Grade / Stage", key="initial_class_level")
    st.text_area(
        "Intended Learning Outcome",
        key="initial_intended_outcome",
        placeholder="What should students demonstrably know, understand or be able to do?",
        height=95,
    )
    st.selectbox(
        "Lesson Purpose",
        LESSON_PURPOSES,
        index=None,
        key="initial_lesson_purpose",
        placeholder="Select the immediate instructional purpose",
    )
    st.text_area(
        "Learner and Classroom Context",
        key="initial_learner_context",
        placeholder="Prior knowledge, learner differences, likely barriers, class characteristics...",
        height=90,
    )
    st.text_area(
        "Resources, Time and Contextual Constraints (if relevant)",
        key="initial_resources",
        placeholder="For example, available materials, teaching time, language or space.",
        height=70,
    )

    st.markdown("---")
    st.subheader("2. Pedagogical Choices and Substantive Lesson Plan")
    st.caption("Choose pedagogical approaches and describe what will actually happen in the lesson.")
    for key, label, options in CHOICE_FIELDS:
        st.selectbox(label, options, index=None, key=f"initial_{key}", placeholder="Select an option")
    st.text_area(
        "Planned Learning Activity and Procedure",
        key="initial_activity",
        placeholder="Describe the planned learning sequence, teacher actions and learning tasks.",
        height=130,
    )
    st.text_area(
        "What Learners Will Actually Do",
        key="initial_engagement_plan",
        placeholder="Specify the student participation and cognitive activity, not merely 'group work'.",
        height=95,
    )
    st.text_area(
        "Planned Learner Support / Inclusion Rationale",
        key="initial_support_plan",
        placeholder="Describe support in relation to identified need. If no support is needed, justify that judgment.",
        height=95,
    )
    st.text_area(
        "Specific Assessment Task and Expected Evidence",
        key="initial_assessment_evidence",
        placeholder="Describe what learners will say, write, make or do to demonstrate the intended outcome.",
        height=100,
    )

    st.markdown("---")
    st.subheader("3. Context-Sensitive Alignment Appraisal")
    st.caption(
        "For each relationship, select a statement about your own judgment and provide "
        "a written justification. 'Cannot yet judge' expresses uncertainty, not low quality."
    )
    for code, label, question in DIMENSIONS:
        st.markdown(f"**{label}**")
        st.write(question)
        selected = st.radio(
            f"Appraisal for {label}",
            ALIGNMENT_RESPONSES,
            index=None,
            key=f"judgment_{code}",
            label_visibility="collapsed",
        )
        if selected:
            st.caption(REASONING_PROMPTS[selected])
        st.text_area(
            f"Explain your judgment — {label}",
            key=f"reason_{code}",
            placeholder="Link your reasoning to the intended outcome, activity, purpose and learner context.",
            height=95,
        )

    if st.button("Generate Profile and Freeze Initial Plan", type="primary", use_container_width=True):
        participant = st.session_state.get("participant_code", "").strip()
        cycle = st.session_state.get("cycle_number")
        lesson = collect_initial_lesson()
        judgments = collect_judgments()
        errors = validate_initial(participant, cycle, lesson, judgments)
        if errors:
            st.error("Please address these points before proceeding:")
            for error in errors:
                st.write("• " + error)
        else:
            st.session_state["initial_snapshot"] = {
                "participant_code": participant,
                "cycle_number": cycle,
                "lesson_id": uuid.uuid4().hex[:12],
                "initial_timestamp_utc": timestamp_utc(),
                "app_version": APP_VERSION,
                "lesson": lesson,
                "judgments": judgments,
            }
            st.rerun()
else:
    st.markdown("---")
    st.subheader("4. Self-Reported Alignment Profile")
    st.caption(
        f"Participant: {snapshot['participant_code']}  ·  "
        f"Cycle: {snapshot['cycle_number']}  ·  "
        f"Lesson record: {snapshot['lesson_id']}"
    )
    st.info(
        "This profile describes your own judgments. It is not a numerical score, "
        "an expert evaluation, a grade or an independent measure of lesson quality."
    )
    profile_rows = []
    for code, label, _ in DIMENSIONS:
        response = snapshot["judgments"][code]
        profile_rows.append({
            "Alignment dimension": label,
            "Self-reported judgment": response["judgment"],
            "Your justification": response["justification"],
        })
    st.dataframe(pd.DataFrame(profile_rows), use_container_width=True, hide_index=True)
    with st.expander("View the original (frozen) lesson plan", expanded=False):
        for key in LESSON_FIELDS:
            st.markdown(f"**{FIELD_LABELS[key]}:** {snapshot['lesson'].get(key, '')}")

    if not st.session_state["saved_current"]:
        st.markdown("---")
        st.subheader("5. Reflection and Lesson Refinement")
        st.write(
            "Compare your original pedagogical choices against the alignment judgments. "
            "Make changes where justified; retaining an appropriate decision is also "
            "acceptable when supported by an explanation."
        )
        seed_revision_inputs(snapshot["lesson"])
        st.text_area(
            "Overall Reflection: What did you learn by examining the five relationships?",
            key="overall_reflection",
            placeholder="Identify tensions, remaining questions and contextual reasoning.",
            height=105,
        )
        st.markdown("#### Revised Lesson Plan")
        st.caption(
            "The fields below initially reproduce your original plan. Revise any elements "
            "that warrant change. The original is preserved for comparison."
        )
        st.text_input("Revised Subject and Lesson Topic", key="revised_topic")
        st.text_input("Revised Class / Grade / Stage", key="revised_class_level")
        st.text_area("Revised Intended Learning Outcome", key="revised_intended_outcome", height=90)
        st.selectbox("Revised Lesson Purpose", LESSON_PURPOSES, key="revised_lesson_purpose")
        st.text_area("Revised Learner and Classroom Context", key="revised_learner_context", height=90)
        st.text_area("Revised Resources, Time and Constraints", key="revised_resources", height=70)
        for key, label, options in CHOICE_FIELDS:
            if key == "lesson_purpose":
                continue
            st.selectbox(f"Revised {label}", options, key=f"revised_{key}")
        st.text_area("Revised Learning Activity and Procedure", key="revised_activity", height=120)
        st.text_area("Revised Learner Participation Description", key="revised_engagement_plan", height=90)
        st.text_area("Revised Learner Support / Inclusion Rationale", key="revised_support_plan", height=90)
        st.text_area("Revised Assessment Task and Evidence", key="revised_assessment_evidence", height=95)
        st.text_area(
            "Explain your revisions or why you retained your original decisions.",
            key="revision_explanation",
            placeholder="Refer to specific alignment relationships and the teaching context.",
            height=120,
        )

        revised = collect_revised_lesson()
        changed = changes_between(snapshot["lesson"], revised)
        st.markdown("**Comparison with the initial plan**")
        if changed:
            st.write("Fields changed: " + ", ".join(changed))
            with st.expander("Inspect original and revised content", expanded=False):
                for key in LESSON_FIELDS:
                    if FIELD_LABELS[key] in changed:
                        st.markdown(f"**{FIELD_LABELS[key]}**")
                        left, right = st.columns(2)
                        with left:
                            st.caption("Original")
                            st.write(snapshot["lesson"][key])
                        with right:
                            st.caption("Revised")
                            st.write(revised[key])
        else:
            st.info(
                "No field has changed yet. This is acceptable only if you provide a "
                "reasoned explanation for retaining the original lesson plan."
            )

        if st.button("Save Final Reflection and Revision Record", type="primary", use_container_width=True):
            reflection = st.session_state.get("overall_reflection", "").strip()
            explanation = st.session_state.get("revision_explanation", "").strip()
            errors = []
            if len(reflection) < 25:
                errors.append("Write an overall reflection of at least 25 characters.")
            if len(explanation) < 25:
                errors.append("Explain changes or justify retention in at least 25 characters.")
            if len(str(revised.get("intended_outcome") or "").strip()) < 15:
                errors.append("Retain a meaningful intended learning outcome.")
            if len(str(revised.get("activity") or "").strip()) < 30:
                errors.append("The revised lesson must retain a substantive learning activity.")
            if len(str(revised.get("assessment_evidence") or "").strip()) < 20:
                errors.append("The revised lesson must specify the assessment evidence.")
            if errors:
                for error in errors:
                    st.error(error)
            else:
                record = {
                    "participant_code": snapshot["participant_code"],
                    "cycle_number": snapshot["cycle_number"],
                    "lesson_id": snapshot["lesson_id"],
                    "app_version": snapshot["app_version"],
                    "initial_timestamp_utc": snapshot["initial_timestamp_utc"],
                    "revision_timestamp_utc": timestamp_utc(),
                    "original_lesson": dict(snapshot["lesson"]),
                    "judgments": {k: dict(v) for k, v in snapshot["judgments"].items()},
                    "revised_lesson": dict(revised),
                    "overall_reflection": reflection,
                    "revision_explanation": explanation,
                    "changed_fields": changed,
                }
                st.session_state["saved_records"].append(record)
                st.session_state["saved_current"] = True
                st.rerun()
    else:
        st.success(
            "This lesson's original plan, alignment justifications, reflection "
            "and revised plan have been recorded in the current browser session."
        )
        record = st.session_state["saved_records"][-1]
        st.write(
            "**Changes in this cycle:** "
            + (", ".join(record["changed_fields"]) if record["changed_fields"] else
               "No changes; original choices retained with a written justification.")
        )
        st.download_button(
            "Download This Lesson Record (CSV)",
            data=export_csv([record]),
            file_name=f"CONCORD_Teach_{record['participant_code']}_Cycle_{record['cycle_number']}.csv",
            mime="text/csv",
            use_container_width=True,
        )
        if st.button("Start Next Cycle / New Lesson", use_container_width=True):
            reset_lesson(next_cycle=True)
            st.rerun()

st.markdown("---")
st.subheader("Session Research Records")
records = st.session_state["saved_records"]
st.write(f"**Completed lessons in this browser session:** {len(records)}")
if records:
    st.dataframe(
        pd.DataFrame([
            {
                "Participant Code": record["participant_code"],
                "Cycle": record["cycle_number"],
                "Lesson ID": record["lesson_id"],
                "Completed (UTC)": record["revision_timestamp_utc"],
            }
            for record in records
        ]),
        hide_index=True,
        use_container_width=True,
    )
    st.download_button(
        "Download All Completed Session Records (CSV)",
        data=export_csv(records),
        file_name="CONCORD_Teach_Session_Records.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.caption(
        "The exported CSV includes the complete initial and revised lesson plans, "
        "five categorical judgments and explanations, reflection, timestamps, "
        "and app version. Store it according to your institution's approved research-data plan."
    )
else:
    st.caption("No completed records yet. Draft inputs are not persisted or stored on a server.")

st.caption(
    "Research boundary: independent lesson-plan quality ratings, independent teaching "
    "observations, and pre/post assessments must be conducted outside this formative application."
)
