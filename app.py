from pathlib import Path
import pandas as pd
import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="DPAS V2",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1250px;}
[data-testid="stSidebar"] {min-width: 300px; max-width: 300px;}
.dpas-card {
    border: 1px solid rgba(120,120,120,.22);
    border-radius: 14px;
    padding: 1rem 1.1rem;
    margin-bottom: .8rem;
}
.dpas-kicker {font-size:.82rem; opacity:.68; margin-bottom:.15rem;}
.dpas-title {font-size:1.1rem; font-weight:650; margin-bottom:.25rem;}
.small-note {font-size:.88rem; opacity:.72;}
</style>
""", unsafe_allow_html=True)

COGNITIVE = [
    "C1 - Remember", "C2 - Understand", "C3 - Apply",
    "C4 - Analyze", "C5 - Evaluate", "C6 - Create"
]
STRATEGIES = [
    "PS1 - Lecture", "PS2 - Discussion", "PS3 - Activity-Based",
    "PS4 - Inquiry-Based", "PS5 - Experiential/Problem-Based"
]
ENGAGEMENT = ["L1 - Individual", "L2 - Pair", "L3 - Group", "L4 - Whole Class"]
ASSESSMENTS = ["A1 - Formative", "A2 - Summative", "A3 - Peer Assessment", "A4 - Self-Assessment"]
LESSON_PURPOSES = [
    "Introduce a new concept", "Develop conceptual understanding",
    "Practice / application", "Inquiry / problem solving",
    "Revision / consolidation", "Assessment / diagnosis", "Other"
]
ALIGNMENT_OPTIONS = ["Aligned", "Partially aligned", "Review needed"]
VERIFY_OPTIONS = ["Concur", "Partially concur", "Needs reconsideration"]

photo_path = Path(__file__).parent / "profile_photo.png"


def get_client():
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    client = create_client(url, key)
    access = st.session_state.get("access_token")
    refresh = st.session_state.get("refresh_token")
    if access and refresh:
        try:
            client.auth.set_session(access, refresh)
        except Exception:
            pass
    return client


supabase = get_client()


def section_header(step, title, text):
    st.markdown(f'<div class="dpas-kicker">{step}</div>', unsafe_allow_html=True)
    st.title(title)
    st.caption(text)


def alignment_points(value):
    return {"Aligned": 2, "Partially aligned": 1, "Review needed": 0}.get(value)


def compute_pas():
    judgments = {
        "Objective–Cognition": st.session_state.get("cognition_alignment"),
        "Objective–Strategy": st.session_state.get("strategy_alignment"),
        "Engagement": st.session_state.get("engagement_alignment"),
        "Inclusivity": st.session_state.get("inclusion_alignment"),
        "Assessment": st.session_state.get("assessment_alignment"),
    }
    scores = {}
    for dimension, value in judgments.items():
        pts = alignment_points(value)
        if pts is not None:
            scores[dimension] = pts
    maximum = 2 * len(scores)
    pas = (sum(scores.values()) / maximum * 100) if maximum else 0
    if pas >= 75:
        category = "Strong Alignment"
    elif pas >= 50:
        category = "Developing Alignment"
    else:
        category = "Alignment Needs Review"
    return pas, category, scores


def clear_lesson_state():
    keys = [
        "lesson_id", "subject_topic", "class_level", "learning_outcome",
        "outcome_cognitive", "lesson_purpose", "learner_context",
        "cognitive", "strategy", "engagement", "inclusion_needed",
        "inclusion_need", "inclusion_support", "assessment",
        "cognitive_rationale", "cognition_alignment",
        "strategy_rationale", "strategy_alignment",
        "engagement_rationale", "engagement_alignment",
        "inclusion_alignment", "assessment_rationale", "assessment_alignment",
        "procedure_introduction", "procedure_development", "procedure_activity",
        "procedure_assessment", "procedure_closure",
        "reflection", "revision_note", "selected_teacher_id",
    ]
    for key in keys:
        st.session_state.pop(key, None)


def current_user():
    return st.session_state.get("user")


def load_profile(user_id):
    if not supabase:
        return None
    try:
        result = supabase.table("profiles").select("*").eq("id", user_id).limit(1).execute()
        return result.data[0] if result.data else None
    except Exception:
        return None


def set_auth_session(auth_response):
    if not auth_response or not auth_response.session:
        return False

    metadata = auth_response.user.user_metadata or {}
    metadata_role = metadata.get("role", "student")

    st.session_state["access_token"] = auth_response.session.access_token
    st.session_state["refresh_token"] = auth_response.session.refresh_token
    st.session_state["user"] = {
        "id": auth_response.user.id,
        "email": auth_response.user.email,
        "role": metadata_role,
        "full_name": metadata.get("full_name", ""),
        "designation": metadata.get("designation", ""),
        "institution": metadata.get("institution", ""),
    }

    profile = load_profile(auth_response.user.id)

    # Keep the public profile synchronized with the role chosen at registration.
    # This also repairs older accounts that were accidentally stored as students.
    if profile and metadata_role and profile.get("role") != metadata_role:
        try:
            supabase.table("profiles").update({
                "role": metadata_role,
                "full_name": metadata.get("full_name", profile.get("full_name", "")),
                "designation": metadata.get("designation", profile.get("designation", "")),
                "institution": metadata.get("institution", profile.get("institution", "")),
                "email": auth_response.user.email,
            }).eq("id", auth_response.user.id).execute()
            profile = load_profile(auth_response.user.id)
        except Exception:
            pass

    if profile:
        st.session_state["profile"] = profile
    return True


def sign_out():
    try:
        if supabase:
            supabase.auth.sign_out()
    except Exception:
        pass
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def register_account():
    if not supabase:
        st.error("Supabase is not connected.")
        return
    full_name = st.session_state.get("reg_name", "").strip()
    email = st.session_state.get("reg_email", "").strip()
    password = st.session_state.get("reg_password", "")
    role = st.session_state.get("reg_role", "Student / Pre-service Teacher")
    designation = st.session_state.get("reg_designation", "").strip()
    institution = st.session_state.get("reg_institution", "").strip()

    if not full_name or not email or len(password) < 6:
        st.error("Enter your name, email, and a password of at least 6 characters.")
        return

    role_value = "teacher_educator" if role.startswith("Teacher") else "student"
    if role_value == "teacher_educator" and (not designation or not institution):
        st.error("Teacher educators should enter designation and institution.")
        return

    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name,
                    "role": role_value,
                    "designation": designation,
                    "institution": institution,
                }
            },
        })
        if response.session:
            set_auth_session(response)
            st.success("Account created and signed in.")
            st.rerun()
        else:
            st.success("Account created. Please check your email if Supabase asks you to confirm your address, then sign in.")
    except Exception as e:
        st.error(f"Could not create account: {e}")


def login_account(expected_role):
    if not supabase:
        st.error("Supabase is not connected.")
        return
    prefix = "student" if expected_role == "student" else "teacher"
    email = st.session_state.get(f"{prefix}_login_email", "").strip()
    password = st.session_state.get(f"{prefix}_login_password", "")
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if set_auth_session(response):
            profile = st.session_state.get("profile") or {}
            actual_role = profile.get("role") or st.session_state.get("user", {}).get("role", "student")
            if actual_role != expected_role:
                try:
                    supabase.auth.sign_out()
                except Exception:
                    pass
                for key in ["access_token", "refresh_token", "user", "profile"]:
                    st.session_state.pop(key, None)
                role_name = "Student / Pre-service Teacher" if expected_role == "student" else "Teacher Educator"
                st.error(f"This account is not registered as {role_name}. Please use the correct sign-in option.")
                return
            st.success("Signed in.")
            st.rerun()
    except Exception as e:
        st.error(f"Sign in failed: {e}")


def save_lesson_context():
    user = current_user()
    if not user or not supabase:
        st.error("Please sign in first.")
        return False

    required = {
        "Subject / Topic": st.session_state.get("subject_topic", "").strip(),
        "Class / Grade Level": st.session_state.get("class_level", "").strip(),
        "Intended Learning Outcome": st.session_state.get("learning_outcome", "").strip(),
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        st.error("Please complete: " + ", ".join(missing))
        return False

    payload = {
        "student_id": user["id"],
        "subject_topic": st.session_state.get("subject_topic", ""),
        "class_level": st.session_state.get("class_level", ""),
        "learning_outcome": st.session_state.get("learning_outcome", ""),
        "outcome_cognitive": st.session_state.get("outcome_cognitive", ""),
        "lesson_purpose": st.session_state.get("lesson_purpose", ""),
        "learner_context": st.session_state.get("learner_context", ""),
        "status": "draft",
    }

    try:
        lesson_id = st.session_state.get("lesson_id")
        if lesson_id:
            supabase.table("lesson_submissions").update(payload).eq("id", lesson_id).execute()
        else:
            result = supabase.table("lesson_submissions").insert(payload).execute()
            st.session_state["lesson_id"] = result.data[0]["id"]
        return True
    except Exception as e:
        st.error(f"Could not save Lesson Context: {e}")
        return False


def hydrate_saved_lesson():
    lesson_id = st.session_state.get("lesson_id")
    if not lesson_id or not supabase:
        return

    try:
        lesson_res = supabase.table("lesson_submissions").select("*").eq("id", lesson_id).limit(1).execute()
        if lesson_res.data:
            lesson = lesson_res.data[0]
            lesson_map = {
                "subject_topic": lesson.get("subject_topic", ""),
                "class_level": lesson.get("class_level", ""),
                "learning_outcome": lesson.get("learning_outcome", ""),
                "outcome_cognitive": lesson.get("outcome_cognitive", ""),
                "lesson_purpose": lesson.get("lesson_purpose", ""),
                "learner_context": lesson.get("learner_context", ""),
            }
            for key, value in lesson_map.items():
                if key not in st.session_state or st.session_state.get(key) in (None, ""):
                    st.session_state[key] = value

        design_res = supabase.table("design_decisions").select("*").eq("lesson_id", lesson_id).limit(1).execute()
        if design_res.data:
            design = design_res.data[0]
            design_map = {
                "cognitive": design.get("cognitive", ""),
                "strategy": design.get("strategy", ""),
                "engagement": design.get("engagement", ""),
                "assessment": design.get("assessment", ""),
                "inclusion_need": design.get("inclusion_need", ""),
                "inclusion_support": design.get("inclusion_support", ""),
            }
            for key, value in design_map.items():
                if key not in st.session_state or st.session_state.get(key) in (None, ""):
                    st.session_state[key] = value

            inclusion_value = (
                "Yes - a specific learner/context need has been identified"
                if design.get("inclusion_needed")
                else "No specific adaptation need identified"
            )
            if "inclusion_needed" not in st.session_state:
                st.session_state["inclusion_needed"] = inclusion_value
    except Exception:
        pass


def save_design_decisions():
    if not supabase or not st.session_state.get("lesson_id"):
        st.error("Save Lesson Context first.")
        return False

    inclusion_needed = st.session_state.get("inclusion_needed", "").startswith("Yes")
    payload = {
        "lesson_id": st.session_state["lesson_id"],
        "cognitive": st.session_state.get("cognitive", ""),
        "strategy": st.session_state.get("strategy", ""),
        "engagement": st.session_state.get("engagement", ""),
        "inclusion_needed": inclusion_needed,
        "inclusion_need": st.session_state.get("inclusion_need", "") if inclusion_needed else "",
        "inclusion_support": st.session_state.get("inclusion_support", "") if inclusion_needed else "",
        "assessment": st.session_state.get("assessment", ""),
    }
    try:
        existing = supabase.table("design_decisions").select("id").eq(
            "lesson_id", st.session_state["lesson_id"]
        ).limit(1).execute()
        if existing.data:
            supabase.table("design_decisions").update(payload).eq("id", existing.data[0]["id"]).execute()
        else:
            supabase.table("design_decisions").insert(payload).execute()

        st.session_state["saved_cognitive"] = payload["cognitive"]
        st.session_state["saved_strategy"] = payload["strategy"]
        st.session_state["saved_engagement"] = payload["engagement"]
        st.session_state["saved_assessment"] = payload["assessment"]
        st.session_state["saved_inclusion_needed"] = (
            "Yes - a specific learner/context need has been identified"
            if payload["inclusion_needed"]
            else "No specific adaptation need identified"
        )
        st.session_state["saved_inclusion_need"] = payload["inclusion_need"]
        st.session_state["saved_inclusion_support"] = payload["inclusion_support"]
        return True
    except Exception as e:
        st.error(f"Could not save Design Decisions: {e}")
        return False


def load_lesson_procedure():
    lesson_id = st.session_state.get("lesson_id")
    if not lesson_id or not supabase:
        return
    if any(st.session_state.get(k) for k in [
        "procedure_introduction", "procedure_development", "procedure_activity",
        "procedure_assessment", "procedure_closure"
    ]):
        return
    try:
        result = supabase.table("lesson_procedures").select("*").eq(
            "lesson_id", lesson_id
        ).limit(1).execute()
        if not result.data:
            return
        row = result.data[0]
        mapping = {
            "procedure_introduction": row.get("introduction", ""),
            "procedure_development": row.get("concept_development", ""),
            "procedure_activity": row.get("learning_activity", ""),
            "procedure_assessment": row.get("assessment_during_lesson", ""),
            "procedure_closure": row.get("closure_consolidation", ""),
        }
        for key, value in mapping.items():
            if value not in (None, ""):
                st.session_state[key] = value
    except Exception:
        pass


def save_lesson_procedure():
    if not supabase or not st.session_state.get("lesson_id"):
        st.error("Save Lesson Context first.")
        return False

    payload = {
        "lesson_id": st.session_state["lesson_id"],
        "introduction": st.session_state.get("procedure_introduction", ""),
        "concept_development": st.session_state.get("procedure_development", ""),
        "learning_activity": st.session_state.get("procedure_activity", ""),
        "assessment_during_lesson": st.session_state.get("procedure_assessment", ""),
        "closure_consolidation": st.session_state.get("procedure_closure", ""),
    }

    if not any(str(v).strip() for k, v in payload.items() if k != "lesson_id"):
        st.error("Please enter at least one part of the lesson procedure.")
        return False

    try:
        existing = supabase.table("lesson_procedures").select("id").eq(
            "lesson_id", st.session_state["lesson_id"]
        ).limit(1).execute()
        if existing.data:
            supabase.table("lesson_procedures").update(payload).eq(
                "id", existing.data[0]["id"]
            ).execute()
        else:
            supabase.table("lesson_procedures").insert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Could not save Lesson Procedure: {e}")
        return False


def teacher_directory():
    if not supabase:
        return []
    try:
        result = supabase.table("profiles").select(
            "id,full_name,designation,institution,email"
        ).eq("role", "teacher_educator").order("full_name").execute()
        return result.data or []
    except Exception as e:
        st.error(f"Could not load teacher directory: {e}")
        return []


def save_alignment_draft():
    if not supabase or not st.session_state.get("lesson_id"):
        st.error("Save the lesson first.")
        return False

    if not st.session_state.get("inclusion_needed", "").startswith("Yes"):
        st.session_state["inclusion_alignment"] = "Not applicable"

    payload = {
        "lesson_id": st.session_state["lesson_id"],
        "cognitive_rationale": st.session_state.get("cognitive_rationale", ""),
        "cognition_alignment": st.session_state.get("cognition_alignment", ""),
        "strategy_rationale": st.session_state.get("strategy_rationale", ""),
        "strategy_alignment": st.session_state.get("strategy_alignment", ""),
        "engagement_rationale": st.session_state.get("engagement_rationale", ""),
        "engagement_alignment": st.session_state.get("engagement_alignment", ""),
        "inclusion_alignment": st.session_state.get("inclusion_alignment", ""),
        "assessment_rationale": st.session_state.get("assessment_rationale", ""),
        "assessment_alignment": st.session_state.get("assessment_alignment", ""),
    }

    # Save PAS only when enough alignment judgments exist to calculate it meaningfully.
    core_keys = [
        "cognition_alignment",
        "strategy_alignment",
        "engagement_alignment",
        "assessment_alignment",
    ]
    if all(st.session_state.get(k) for k in core_keys):
        pas, category, _ = compute_pas()
        payload["pas_score"] = round(pas, 2)
        payload["alignment_category"] = category

    try:
        existing = supabase.table("alignment_evidence").select("id").eq(
            "lesson_id", st.session_state["lesson_id"]
        ).limit(1).execute()
        if existing.data:
            supabase.table("alignment_evidence").update(payload).eq(
                "id", existing.data[0]["id"]
            ).execute()
        else:
            supabase.table("alignment_evidence").insert(payload).execute()

        supabase.table("lesson_submissions").update({
            "status": "alignment draft"
        }).eq("id", st.session_state["lesson_id"]).execute()
        return True
    except Exception as e:
        st.error(f"Could not save alignment draft: {e}")
        return False


def load_alignment_draft():
    lesson_id = st.session_state.get("lesson_id")
    if not lesson_id or not supabase:
        return

    # Do not overwrite anything the student has already entered in this session.
    keys = [
        "cognitive_rationale", "cognition_alignment",
        "strategy_rationale", "strategy_alignment",
        "engagement_rationale", "engagement_alignment",
        "inclusion_alignment", "assessment_rationale", "assessment_alignment",
    ]
    if any(st.session_state.get(k) for k in keys):
        return

    try:
        result = supabase.table("alignment_evidence").select("*").eq(
            "lesson_id", lesson_id
        ).limit(1).execute()
        if not result.data:
            return
        row = result.data[0]
        for key in keys:
            value = row.get(key)
            if value not in (None, ""):
                st.session_state[key] = value
    except Exception:
        pass


def submit_self_analysis(teacher_id):
    if not supabase or not st.session_state.get("lesson_id"):
        st.error("Save the lesson first.")
        return False
    required = [
        "cognitive_rationale", "cognition_alignment",
        "strategy_rationale", "strategy_alignment",
        "engagement_rationale", "engagement_alignment",
        "assessment_rationale", "assessment_alignment",
    ]
    if any(not str(st.session_state.get(k, "")).strip() for k in required):
        st.error("Complete all rationale and alignment fields before submitting.")
        return False

    if st.session_state.get("inclusion_needed", "").startswith("Yes"):
        if not st.session_state.get("inclusion_alignment"):
            st.error("Complete Inclusivity Alignment.")
            return False
    else:
        st.session_state["inclusion_alignment"] = "Not applicable"

    pas, category, _ = compute_pas()
    payload = {
        "lesson_id": st.session_state["lesson_id"],
        "cognitive_rationale": st.session_state.get("cognitive_rationale", ""),
        "cognition_alignment": st.session_state.get("cognition_alignment", ""),
        "strategy_rationale": st.session_state.get("strategy_rationale", ""),
        "strategy_alignment": st.session_state.get("strategy_alignment", ""),
        "engagement_rationale": st.session_state.get("engagement_rationale", ""),
        "engagement_alignment": st.session_state.get("engagement_alignment", ""),
        "inclusion_alignment": st.session_state.get("inclusion_alignment", "Not applicable"),
        "assessment_rationale": st.session_state.get("assessment_rationale", ""),
        "assessment_alignment": st.session_state.get("assessment_alignment", ""),
        "pas_score": round(pas, 2),
        "alignment_category": category,
    }
    try:
        existing = supabase.table("alignment_evidence").select("id").eq(
            "lesson_id", st.session_state["lesson_id"]
        ).limit(1).execute()
        if existing.data:
            supabase.table("alignment_evidence").update(payload).eq("id", existing.data[0]["id"]).execute()
        else:
            supabase.table("alignment_evidence").insert(payload).execute()

        supabase.table("lesson_submissions").update({
            "reviewer_id": teacher_id,
            "status": "submitted for educator review",
        }).eq("id", st.session_state["lesson_id"]).execute()
        return True
    except Exception as e:
        st.error(f"Could not submit self-analysis: {e}")
        return False


def educator_inbox():
    user = current_user()
    if not user or not supabase:
        return []
    try:
        result = supabase.table("lesson_submissions").select("*").eq(
            "reviewer_id", user["id"]
        ).order("created_at", desc=True).execute()
        return result.data or []
    except Exception as e:
        st.error(f"Could not load submissions: {e}")
        return []


def fetch_one(table, lesson_id):
    try:
        result = supabase.table(table).select("*").eq("lesson_id", lesson_id).limit(1).execute()
        return result.data[0] if result.data else {}
    except Exception:
        return {}


def submit_educator_verification(lesson_id):
    profile = st.session_state.get("profile", {})
    payload = {
        "lesson_id": lesson_id,
        "educator_code": profile.get("email", profile.get("full_name", "")),
        "cognition_verification": st.session_state.get("verify_cognition", ""),
        "cognition_comment": st.session_state.get("verify_cognition_comment", ""),
        "strategy_verification": st.session_state.get("verify_strategy", ""),
        "strategy_comment": st.session_state.get("verify_strategy_comment", ""),
        "engagement_verification": st.session_state.get("verify_engagement", ""),
        "engagement_comment": st.session_state.get("verify_engagement_comment", ""),
        "inclusion_verification": st.session_state.get("verify_inclusion", ""),
        "inclusion_comment": st.session_state.get("verify_inclusion_comment", ""),
        "assessment_verification": st.session_state.get("verify_assessment", ""),
        "assessment_comment": st.session_state.get("verify_assessment_comment", ""),
    }
    try:
        existing = supabase.table("educator_verification").select("id").eq(
            "lesson_id", lesson_id
        ).limit(1).execute()
        if existing.data:
            supabase.table("educator_verification").update(payload).eq("id", existing.data[0]["id"]).execute()
        else:
            supabase.table("educator_verification").insert(payload).execute()
        supabase.table("lesson_submissions").update(
            {"status": "educator reviewed"}
        ).eq("id", lesson_id).execute()
        return True
    except Exception as e:
        st.error(f"Could not save verification: {e}")
        return False


def save_revision():
    if not supabase or not st.session_state.get("lesson_id"):
        st.error("No current lesson.")
        return False
    pas, category, _ = compute_pas()
    payload = {
        "lesson_id": st.session_state["lesson_id"],
        "reflection": st.session_state.get("reflection", ""),
        "revision_note": st.session_state.get("revision_note", ""),
        "revised_pas": round(pas, 2),
        "revised_category": category,
    }
    try:
        existing = supabase.table("revisions").select("id").eq(
            "lesson_id", st.session_state["lesson_id"]
        ).limit(1).execute()
        if existing.data:
            supabase.table("revisions").update(payload).eq("id", existing.data[0]["id"]).execute()
        else:
            supabase.table("revisions").insert(payload).execute()
        supabase.table("lesson_submissions").update(
            {"status": "revision submitted"}
        ).eq("id", st.session_state["lesson_id"]).execute()
        return True
    except Exception as e:
        st.error(f"Could not save revision: {e}")
        return False


def render_about():
    section_header(
        "ABOUT DPAS",
        "DILP-LA Pedagogical Analytics System (DPAS)",
        "A context-sensitive pedagogical alignment and reflection system for pre-service and novice teachers.",
    )
    left, right = st.columns([2.2, 1])
    with left:
        st.markdown("### About DPAS")
        st.write(
            "DPAS V2 supports pre-service and novice teachers in planning, justifying, analysing, "
            "and revising lesson-design decisions. The system focuses on alignment among intended "
            "learning outcomes, cognitive demand, pedagogical strategy, learner engagement, inclusivity, "
            "and assessment rather than treating any single method as inherently superior."
        )
        st.write(
            "Students can submit their lesson analysis directly to a registered teacher educator or "
            "supervisor of their choice. The selected educator receives that submission in their own DPAS inbox."
        )
        st.info(
            "DPAS is a formative decision-support and reflection system. Its alignment indicators "
            "support pedagogical reasoning; they are not a universal quality grade."
        )
        st.markdown("### Conceptualized and Developed by")
        st.markdown("""
**Dr. Meenakshi Dwivedi**  
Assistant Professor  
School of Education  
Mahatma Jyotiba Phule Rohilkhand University  
Bareilly, Uttar Pradesh, India
""")
    with right:
        if photo_path.exists():
            st.image(str(photo_path), width=250, caption="Dr. Meenakshi Dwivedi")
        st.markdown(
            '<div class="dpas-card"><div class="dpas-kicker">DPAS V2</div>'
            '<div class="dpas-title">Plan → Justify → Analyse → Submit → Verify → Reflect → Revise</div>'
            '<div class="small-note">A structured workflow for pedagogical reasoning and supervised lesson planning.</div></div>',
            unsafe_allow_html=True,
        )


# ---------- AUTH / SIDEBAR ----------
profile = st.session_state.get("profile")
user = current_user()

with st.sidebar:
    st.markdown("## 📊 DPAS V2")
    st.caption("Context-Sensitive Pedagogical Alignment & Reflection System")
    st.markdown("---")

    if not user:
        page = st.radio("Navigation", ["About DPAS", "Sign in / Register"], label_visibility="collapsed")
    else:
        if not profile:
            profile = load_profile(user["id"])
            if profile:
                st.session_state["profile"] = profile

        role = (profile or {}).get("role") or user.get("role", "student")
        display_name = (profile or {}).get("full_name") or user.get("full_name") or user.get("email", "")
        st.success(f"Signed in as **{display_name}**")
        st.caption("Teacher Educator" if role == "teacher_educator" else "Pre-service / Novice Teacher")

        if role == "teacher_educator":
            page = st.radio(
                "Navigation",
                ["About DPAS", "Submissions Sent to Me"],
                label_visibility="collapsed",
            )
        else:
            page = st.radio(
                "Workflow",
                [
                    "1 · About DPAS",
                    "2 · Lesson Context",
                    "3 · Design Decisions",
                    "4 · Lesson Procedure",
                    "5 · Alignment Evidence & Submit",
                    "6 · Analytics",
                    "7 · Educator Feedback",
                    "8 · Reflect & Revise",
                    "9 · Report",
                ],
                label_visibility="collapsed",
            )
            if st.button("＋ Start New Lesson", use_container_width=True):
                clear_lesson_state()
                st.success("Ready for a new lesson.")

        st.markdown("---")
        if st.button("Sign out", use_container_width=True):
            sign_out()


# ---------- PUBLIC ----------
if not user:
    if page == "About DPAS":
        render_about()
    else:
        section_header(
            "ACCOUNT",
            "Sign in or Create Account",
            "Choose the appropriate role. Students and teacher educators use separate sign-in paths."
        )

        sign_in_tab, create_tab = st.tabs(["Sign in", "Create account"])

        with sign_in_tab:
            st.markdown("### Sign in as Student / Pre-service Teacher")
            st.text_input("Student email", key="student_login_email")
            st.text_input("Student password", type="password", key="student_login_password")
            if st.button("Sign in as Student", type="primary", use_container_width=True):
                login_account("student")

            st.markdown("---")

            st.markdown("### Sign in as Teacher Educator")
            st.text_input("Teacher educator email", key="teacher_login_email")
            st.text_input("Teacher educator password", type="password", key="teacher_login_password")
            if st.button("Sign in as Teacher Educator", use_container_width=True):
                login_account("teacher_educator")

        with create_tab:
            st.text_input("Full name", key="reg_name")
            st.text_input("Email address", key="reg_email")
            st.text_input("Create password", type="password", key="reg_password")
            st.selectbox(
                "Register as",
                ["Student / Pre-service Teacher", "Teacher Educator / Supervisor"],
                key="reg_role",
            )
            if st.session_state.get("reg_role", "").startswith("Teacher"):
                st.text_input("Designation", key="reg_designation", placeholder="e.g., Assistant Professor")
                st.text_input("Institution", key="reg_institution", placeholder="e.g., School of Education, MJPRU")
            if st.button("Create account", type="primary", use_container_width=True):
                register_account()
    st.stop()


# ---------- TEACHER EDUCATOR ----------
active_role = (profile or {}).get("role") or (user or {}).get("role", "student")

if active_role == "teacher_educator":
    if page == "About DPAS":
        render_about()
    else:
        section_header(
            "TEACHER-EDUCATOR WORKSPACE",
            "Submissions Sent to Me",
            "Only lesson analyses that students have deliberately submitted to you appear here.",
        )
        inbox = educator_inbox()
        if not inbox:
            st.info("No student submissions have been sent to you yet.")
        else:
            profile_rows = supabase.table("profiles").select("id,full_name,email").execute().data or []
            names = {p["id"]: p.get("full_name") or p.get("email") for p in profile_rows}
            labels = {
                row["id"]: f"{names.get(row.get('student_id'), 'Student')} · {row.get('subject_topic','Untitled')} · {row.get('status','')}"
                for row in inbox
            }
            lesson_id = st.selectbox(
                "Select a submission",
                options=list(labels.keys()),
                format_func=lambda x: labels[x],
            )
            lesson = next(r for r in inbox if r["id"] == lesson_id)
            design = fetch_one("design_decisions", lesson_id)
            procedure = fetch_one("lesson_procedures", lesson_id)
            evidence = fetch_one("alignment_evidence", lesson_id)

            st.markdown("### Lesson submitted for review")
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Student:**", names.get(lesson.get("student_id"), "Student"))
                st.write("**Subject / Topic:**", lesson.get("subject_topic", ""))
                st.write("**Class / Grade:**", lesson.get("class_level", ""))
                st.write("**Lesson Purpose:**", lesson.get("lesson_purpose", ""))
            with c2:
                st.write("**Intended Learning Outcome:**", lesson.get("learning_outcome", ""))
                st.write("**Outcome Cognitive Demand:**", lesson.get("outcome_cognitive", ""))
                st.write("**Strategy:**", design.get("strategy", ""))
                st.write("**Assessment:**", design.get("assessment", ""))

            st.markdown("### Lesson Procedure")
            if procedure:
                st.write("**Introduction / Set Induction:**", procedure.get("introduction", ""))
                st.write("**Concept Development / Teacher–Learner Interaction:**", procedure.get("concept_development", ""))
                st.write("**Learning Activity / Practice:**", procedure.get("learning_activity", ""))
                st.write("**Assessment During the Lesson:**", procedure.get("assessment_during_lesson", ""))
                st.write("**Closure / Consolidation:**", procedure.get("closure_consolidation", ""))
            else:
                st.caption("No lesson procedure was saved for this submission.")

            st.info(
                "For independent verification, review the student's lesson decisions, lesson procedure, and written rationales first. "
                "The student's own alignment selections are not displayed on this screen."
            )

            reviews = [
                ("Objective–Cognition", "cognitive_rationale", "verify_cognition"),
                ("Objective–Strategy", "strategy_rationale", "verify_strategy"),
                ("Engagement", "engagement_rationale", "verify_engagement"),
                ("Inclusivity", None, "verify_inclusion"),
                ("Assessment", "assessment_rationale", "verify_assessment"),
            ]
            for title, rationale_key, verify_key in reviews:
                if title == "Inclusivity" and evidence.get("inclusion_alignment") == "Not applicable":
                    continue
                with st.expander(title):
                    if rationale_key:
                        st.write("**Student rationale:**", evidence.get(rationale_key, ""))
                    elif title == "Inclusivity":
                        st.write("**Identified need:**", design.get("inclusion_need", ""))
                        st.write("**Planned support:**", design.get("inclusion_support", ""))
                    st.radio("Educator verification", VERIFY_OPTIONS, key=verify_key, horizontal=True)
                    st.text_area("Educator comment", key=f"{verify_key}_comment")

            if st.button("Submit Teacher-Educator Verification", type="primary", use_container_width=True):
                if submit_educator_verification(lesson_id):
                    st.success("Verification submitted. The student can now view your feedback.")
    st.stop()


# ---------- STUDENT WORKFLOW ----------
if page.startswith("1"):
    render_about()

elif page.startswith("2"):
    section_header(
        "STEP 2 OF 9",
        "Lesson Context",
        "Define the lesson before making pedagogical decisions.",
    )
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Subject / Topic", key="subject_topic", placeholder="e.g., Mathematics - Ratio")
        st.text_area("Intended Learning Outcome", key="learning_outcome")
        st.selectbox("Primary Cognitive Demand of the Outcome", COGNITIVE, key="outcome_cognitive")
    with c2:
        st.text_input("Class / Grade Level", key="class_level", placeholder="e.g., Grade 6")
        st.selectbox("Lesson Purpose", LESSON_PURPOSES, key="lesson_purpose")
        st.text_area("Learner / Context Consideration", key="learner_context")
    if st.button("💾 Save Lesson Context", type="primary", use_container_width=True):
        if save_lesson_context():
            st.success("Lesson Context saved. Continue to Design Decisions.")

elif page.startswith("3"):
    hydrate_saved_lesson()
    if "inclusion_needed" not in st.session_state and "saved_inclusion_needed" in st.session_state:
        st.session_state["inclusion_needed"] = st.session_state["saved_inclusion_needed"]
    for key in ["cognitive", "strategy", "engagement", "assessment", "inclusion_need", "inclusion_support"]:
        saved_key = f"saved_{key}"
        if key not in st.session_state and saved_key in st.session_state:
            st.session_state[key] = st.session_state[saved_key]
    section_header(
        "STEP 3 OF 9",
        "Design Decisions",
        "Choose the options you currently consider appropriate. No option is treated as universally superior.",
    )
    a, b = st.columns(2)
    with a:
        st.selectbox("Planned Cognitive Demand", COGNITIVE, key="cognitive")
        st.selectbox("Learner Engagement Mode", ENGAGEMENT, key="engagement")
    with b:
        st.selectbox("Pedagogical Strategy", STRATEGIES, key="strategy")
        st.selectbox("Assessment Type", ASSESSMENTS, key="assessment")
    st.markdown("### Inclusivity & Learner Support")
    st.radio(
        "Is a specific adaptation or support needed?",
        ["No specific adaptation need identified", "Yes - a specific learner/context need has been identified"],
        key="inclusion_needed",
    )
    if st.session_state.get("inclusion_needed", "").startswith("Yes"):
        x, y = st.columns(2)
        with x:
            st.text_area("Identified learner/context need", key="inclusion_need")
        with y:
            st.text_area("Planned adaptation / support", key="inclusion_support")
    else:
        st.session_state["inclusion_need"] = ""
        st.session_state["inclusion_support"] = ""
    if st.button("💾 Save Design Decisions", type="primary", use_container_width=True):
        if save_design_decisions():
            st.success("Design Decisions saved. Continue to Lesson Procedure.")

elif page.startswith("4"):
    load_lesson_procedure()
    section_header(
        "STEP 4 OF 9",
        "Lesson Procedure",
        "Describe how the lesson will unfold in the classroom. This gives the teacher educator concrete evidence of how your design decisions will be enacted.",
    )
    st.text_area(
        "Introduction / Set Induction",
        key="procedure_introduction",
        placeholder="How will you introduce the topic, activate prior knowledge, or gain learners' attention?",
    )
    st.text_area(
        "Concept Development / Teacher–Learner Interaction",
        key="procedure_development",
        placeholder="Describe the main teaching-learning sequence, explanations, examples, questions, and interaction.",
    )
    st.text_area(
        "Learning Activity / Practice",
        key="procedure_activity",
        placeholder="Describe what learners will do individually, in pairs, groups, or as a class.",
    )
    st.text_area(
        "Assessment During the Lesson",
        key="procedure_assessment",
        placeholder="Describe the evidence of learning you will gather during the lesson.",
    )
    st.text_area(
        "Closure / Consolidation",
        key="procedure_closure",
        placeholder="How will the lesson be summarized, consolidated, or brought to closure?",
    )
    if st.button("💾 Save Lesson Procedure", type="primary", use_container_width=True):
        if save_lesson_procedure():
            st.success("Lesson Procedure saved. Continue to Alignment Evidence & Submit.")

elif page.startswith("5"):
    hydrate_saved_lesson()
    if "inclusion_needed" not in st.session_state and "saved_inclusion_needed" in st.session_state:
        st.session_state["inclusion_needed"] = st.session_state["saved_inclusion_needed"]
    for key in ["cognitive", "strategy", "engagement", "assessment", "inclusion_need", "inclusion_support"]:
        saved_key = f"saved_{key}"
        if key not in st.session_state and saved_key in st.session_state:
            st.session_state[key] = st.session_state[saved_key]
    load_lesson_procedure()
    load_alignment_draft()
    section_header(
        "STEP 5 OF 9",
        "Alignment Evidence & Submit",
        "Justify each pedagogical decision, then choose the teacher educator or supervisor who should review this lesson.",
    )
    tabs = st.tabs(["Cognition", "Strategy", "Engagement", "Inclusivity", "Assessment"])
    with tabs[0]:
        st.write("**Outcome:**", st.session_state.get("learning_outcome", ""))
        st.write("**Planned cognitive demand:**", st.session_state.get("cognitive", ""))
        st.text_area("Why is this cognitive demand appropriate?", key="cognitive_rationale")
        st.radio("Objective–Cognition Alignment", ALIGNMENT_OPTIONS, key="cognition_alignment", horizontal=True)
    with tabs[1]:
        st.write("**Selected strategy:**", st.session_state.get("strategy", ""))
        st.text_area("How will this strategy help learners achieve the outcome?", key="strategy_rationale")
        st.radio("Objective–Strategy Alignment", ALIGNMENT_OPTIONS, key="strategy_alignment", horizontal=True)
    with tabs[2]:
        st.write("**Selected engagement mode:**", st.session_state.get("engagement", ""))
        st.text_area("Why is this engagement mode appropriate?", key="engagement_rationale")
        st.radio("Engagement Alignment", ALIGNMENT_OPTIONS, key="engagement_alignment", horizontal=True)
    with tabs[3]:
        inclusion_choice = st.session_state.get(
            "inclusion_needed",
            st.session_state.get("saved_inclusion_needed", "")
        )
        if str(inclusion_choice).startswith("Yes"):
            st.write("**Identified need:**", st.session_state.get("inclusion_need", st.session_state.get("saved_inclusion_need", "")))
            st.write("**Planned support:**", st.session_state.get("inclusion_support", st.session_state.get("saved_inclusion_support", "")))
            st.radio("Need–Support Alignment", ALIGNMENT_OPTIONS, key="inclusion_alignment", horizontal=True)
        else:
            st.session_state["inclusion_alignment"] = "Not applicable"
            st.info("No specific adaptation need identified; this dimension is not applicable.")
    with tabs[4]:
        st.write("**Selected assessment:**", st.session_state.get("assessment", ""))
        st.text_area("How will this assessment provide evidence of the outcome?", key="assessment_rationale")
        st.radio("Assessment–Outcome Alignment", ALIGNMENT_OPTIONS, key="assessment_alignment", horizontal=True)

    st.markdown("---")
    draft_col, _ = st.columns([1, 2])
    with draft_col:
        if st.button("💾 Save Alignment Draft", use_container_width=True):
            if save_alignment_draft():
                st.success("Draft saved. You can move to another section and return later without losing this work.")

    st.markdown("### Submit to your teacher educator / supervisor")
    teachers = teacher_directory()
    if not teachers:
        st.warning("No teacher educator has registered yet. Ask your supervisor to create a Teacher Educator account in DPAS.")
    else:
        teacher_map = {
            t["id"]: " — ".join(
                [x for x in [t.get("full_name"), t.get("designation"), t.get("institution")] if x]
            )
            for t in teachers
        }
        selected_teacher = st.selectbox(
            "Select Teacher Educator / Supervisor",
            options=list(teacher_map.keys()),
            format_func=lambda x: teacher_map[x],
            key="selected_teacher_id",
        )
        st.info(f"You are submitting this lesson to: **{teacher_map[selected_teacher]}**")
        if st.button("Confirm & Submit for Teacher Review", type="primary", use_container_width=True):
            if submit_self_analysis(selected_teacher):
                st.success("Submitted successfully. This lesson now appears in your selected teacher educator's DPAS inbox.")

elif page.startswith("6"):
    section_header(
        "STEP 6 OF 9",
        "Pedagogical Analytics",
        "Review the coherence of your lesson design.",
    )
    required = ["cognition_alignment", "strategy_alignment", "engagement_alignment", "assessment_alignment"]
    if not all(st.session_state.get(k) for k in required):
        st.warning("Complete Alignment Evidence first.")
    else:
        pas, category, scores = compute_pas()
        m1, m2, m3 = st.columns(3)
        m1.metric("Pedagogical Alignment Score", f"{pas:.1f}%")
        m2.metric("Alignment Category", category)
        m3.metric("Applicable Dimensions", len(scores))
        chart = pd.DataFrame({
            "Dimension": list(scores.keys()),
            "Alignment (%)": [v / 2 * 100 for v in scores.values()],
        }).set_index("Dimension")
        st.subheader("Alignment Profile")
        st.bar_chart(chart)
        st.info(
            "PAS summarizes explicit alignment judgments. It does not reward higher Bloom levels, "
            "a particular teaching strategy, a particular engagement mode, more adaptations, or a particular assessment type."
        )

elif page.startswith("7"):
    section_header(
        "STEP 7 OF 9",
        "Educator Feedback",
        "Feedback appears here after your selected teacher educator completes verification.",
    )
    lesson_id = st.session_state.get("lesson_id")
    if not lesson_id:
        st.info("No current lesson has been saved.")
    else:
        verification = fetch_one("educator_verification", lesson_id)
        if not verification:
            st.info("Your teacher educator has not submitted feedback yet.")
        else:
            rows = [
                ("Objective–Cognition", verification.get("cognition_verification"), verification.get("cognition_comment")),
                ("Objective–Strategy", verification.get("strategy_verification"), verification.get("strategy_comment")),
                ("Engagement", verification.get("engagement_verification"), verification.get("engagement_comment")),
                ("Inclusivity", verification.get("inclusion_verification"), verification.get("inclusion_comment")),
                ("Assessment", verification.get("assessment_verification"), verification.get("assessment_comment")),
            ]
            for title, judgment, comment in rows:
                if not judgment and not comment:
                    continue
                with st.expander(title, expanded=True):
                    st.write("**Teacher-educator verification:**", judgment or "—")
                    st.write("**Comment:**", comment or "—")

elif page.startswith("8"):
    section_header(
        "STEP 8 OF 9",
        "Reflect & Revise",
        "Use the analytics and teacher-educator feedback to reconsider your lesson design.",
    )
    st.text_area(
        "Which pedagogical decision would you reconsider after reviewing the feedback, and why?",
        key="reflection",
    )
    st.text_area("What revision will you make to the lesson design?", key="revision_note")
    if st.button("Submit Reflection & Revision", type="primary", use_container_width=True):
        if save_revision():
            st.success("Reflection and revision saved.")

elif page.startswith("9"):
    load_lesson_procedure()
    section_header(
        "STEP 9 OF 9",
        "Final Report",
        "Export a transparent record of lesson context, procedure, decisions, alignment judgments, verification, and reflection.",
    )
    if not st.session_state.get("lesson_id"):
        st.info("Complete and save a lesson first.")
    else:
        pas, category, _ = compute_pas()
        report = {
            "Student": (profile or {}).get("full_name", ""),
            "Subject / Topic": st.session_state.get("subject_topic", ""),
            "Class / Grade": st.session_state.get("class_level", ""),
            "Intended Learning Outcome": st.session_state.get("learning_outcome", ""),
            "Lesson Purpose": st.session_state.get("lesson_purpose", ""),
            "Planned Cognitive Demand": st.session_state.get("cognitive", ""),
            "Pedagogical Strategy": st.session_state.get("strategy", ""),
            "Learner Engagement": st.session_state.get("engagement", ""),
            "Assessment Type": st.session_state.get("assessment", ""),
            "Introduction / Set Induction": st.session_state.get("procedure_introduction", ""),
            "Concept Development": st.session_state.get("procedure_development", ""),
            "Learning Activity / Practice": st.session_state.get("procedure_activity", ""),
            "Assessment During Lesson": st.session_state.get("procedure_assessment", ""),
            "Closure / Consolidation": st.session_state.get("procedure_closure", ""),
            "PAS Score (V2)": round(pas, 2),
            "Alignment Category": category,
            "Reflection": st.session_state.get("reflection", ""),
            "Revision Note": st.session_state.get("revision_note", ""),
        }
        preview = pd.DataFrame([report])
        st.dataframe(preview, use_container_width=True)
        csv = preview.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download DPAS V2 Report (CSV)",
            data=csv,
            file_name="DPAS_V2_Lesson_Alignment_Report.csv",
            mime="text/csv",
            use_container_width=True,
        )
