from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="DPAS V2",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- STYLE ----------
st.markdown("""
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1250px;}
[data-testid="stSidebar"] {min-width: 290px; max-width: 290px;}
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

# ---------- CONSTANTS ----------
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
ALIGNMENT_OPTIONS = [
    "Aligned",
    "Partially aligned",
    "Review needed"
]
VERIFY_OPTIONS = [
    "Concur",
    "Partially concur",
    "Needs reconsideration"
]

def alignment_points(value):
    return {"Aligned": 2, "Partially aligned": 1, "Review needed": 0}.get(value)

def compute_pas():
    judgments = {
        "Objective–Cognition": st.session_state.get("cognition_alignment"),
        "Objective–Strategy": st.session_state.get("strategy_alignment"),
        "Engagement": st.session_state.get("engagement_alignment"),
        "Inclusivity": st.session_state.get("inclusion_alignment"),
        "Assessment": st.session_state.get("assessment_alignment")
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

def section_header(step, title, text):
    st.markdown(f'<div class="dpas-kicker">STEP {step}</div>', unsafe_allow_html=True)
    st.title(title)
    st.caption(text)

# ---------- SIDEBAR ----------
photo_path = Path(__file__).parent / "profile_photo.png"
with st.sidebar:
    st.markdown("## 📊 DPAS V2")
    st.caption("Context-Sensitive Pedagogical Alignment & Reflection System")
    st.markdown("---")
    page = st.radio(
        "Workflow",
        [
            "1 · About DPAS",
            "2 · Lesson Context",
            "3 · Design Decisions",
            "4 · Alignment Evidence",
            "5 · Analytics",
            "6 · Educator Verification",
            "7 · Reflect & Revise",
            "8 · Report"
        ],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("Use the sections above in sequence to complete the DPAS workflow.")

# ---------- PAGE 1 ----------
if page.startswith("1"):
    section_header(
        "1 OF 8",
        "DILP-LA Pedagogical Analytics System (DPAS)",
        "A context-sensitive pedagogical alignment and reflection system for pre-service and novice teachers."
    )

    left, right = st.columns([2.2, 1])
    with left:
        st.markdown("### About DPAS")
        st.write(
            "DPAS V2 supports pre-service and novice teachers in planning, justifying, analysing, "
            "and revising lesson-design decisions. The system focuses on the alignment among intended "
            "learning outcomes, cognitive demand, pedagogical strategy, learner engagement, inclusivity, "
            "and assessment rather than treating any single method as inherently superior."
        )
        st.write(
            "The workflow guides users through lesson context, design decisions, alignment evidence, "
            "pedagogical analytics, teacher-educator verification, reflection, revision, and reporting."
        )
        st.info(
            "DPAS is intended as a formative decision-support and reflection system. "
            "Its alignment indicators support pedagogical reasoning; they are not a universal quality grade."
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
            '<div class="dpas-title">Plan → Justify → Analyse → Verify → Reflect → Revise</div>'
            '<div class="small-note">A structured workflow for pedagogical reasoning and alignment.</div></div>',
            unsafe_allow_html=True
        )

# ---------- PAGE 2 ----------
elif page.startswith("2"):
    section_header(
        "2 OF 8",
        "Lesson Context",
        "Define the lesson before making pedagogical decisions. These details provide the context for later alignment analysis."
    )
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Subject / Topic", key="subject_topic", placeholder="e.g., Science - Photosynthesis")
        st.text_area(
            "Intended Learning Outcome",
            key="learning_outcome",
            placeholder="State what learners should know, understand, or be able to do."
        )
        st.selectbox(
            "Primary Cognitive Demand of the Outcome",
            COGNITIVE,
            key="outcome_cognitive",
            help="Bloom categories are descriptive here; higher levels are not treated as inherently better."
        )
    with c2:
        st.text_input("Class / Grade Level", key="class_level", placeholder="e.g., Grade 7")
        st.selectbox("Lesson Purpose", LESSON_PURPOSES, key="lesson_purpose")
        st.text_area(
            "Learner / Context Consideration",
            key="learner_context",
            placeholder="Prior knowledge, language, accessibility, classroom conditions, or other relevant context."
        )
    st.info("DPAS interprets later choices in relation to this lesson context; it does not reward particular methods in isolation.")

# ---------- PAGE 3 ----------
elif page.startswith("3"):
    section_header(
        "3 OF 8",
        "Design Decisions",
        "Choose the lesson-design options you currently consider appropriate. No option is treated as universally superior."
    )
    a, b = st.columns(2)
    with a:
        st.markdown('<div class="dpas-card"><div class="dpas-title">🧠 Cognitive Demand</div><div class="small-note">What kind of thinking will the planned learning activity emphasize?</div></div>', unsafe_allow_html=True)
        st.selectbox("Planned Cognitive Demand", COGNITIVE, key="cognitive")
        st.markdown('<div class="dpas-card"><div class="dpas-title">👥 Learner Engagement</div><div class="small-note">How will learners participate in the activity?</div></div>', unsafe_allow_html=True)
        st.selectbox("Engagement Mode", ENGAGEMENT, key="engagement")
    with b:
        st.markdown('<div class="dpas-card"><div class="dpas-title">🎯 Pedagogical Strategy</div><div class="small-note">Which strategy best fits this lesson purpose and context?</div></div>', unsafe_allow_html=True)
        st.selectbox("Pedagogical Strategy", STRATEGIES, key="strategy")
        st.markdown('<div class="dpas-card"><div class="dpas-title">✅ Assessment</div><div class="small-note">How will evidence of learning be gathered?</div></div>', unsafe_allow_html=True)
        st.selectbox("Assessment Type", ASSESSMENTS, key="assessment")

    st.markdown("### ♿ Inclusivity & Learner Support")
    st.radio(
        "Is a specific adaptation or support needed for an identified learner/context need?",
        ["No specific adaptation need identified", "Yes - a specific learner/context need has been identified"],
        key="inclusion_needed"
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

# ---------- PAGE 4 ----------
elif page.startswith("4"):
    section_header(
        "4 OF 8",
        "Alignment Evidence",
        "Justify each pedagogical decision before judging its alignment. The purpose is reflective reasoning, not score maximization."
    )

    tabs = st.tabs(["Cognition", "Strategy", "Engagement", "Inclusivity", "Assessment"])

    with tabs[0]:
        st.write("**Outcome:**", st.session_state.get("learning_outcome", "Not entered"))
        st.write("**Outcome demand:**", st.session_state.get("outcome_cognitive", "Not selected"))
        st.write("**Planned demand:**", st.session_state.get("cognitive", "Not selected"))
        st.text_area(
            "Why is this cognitive demand appropriate for the intended learning outcome?",
            key="cognitive_rationale"
        )
        st.radio("Objective–Cognition Alignment", ALIGNMENT_OPTIONS, key="cognition_alignment", horizontal=True)

    with tabs[1]:
        st.write("**Selected strategy:**", st.session_state.get("strategy", "Not selected"))
        st.text_area(
            "How will this strategy help learners achieve the intended learning outcome?",
            key="strategy_rationale"
        )
        st.radio("Objective–Strategy Alignment", ALIGNMENT_OPTIONS, key="strategy_alignment", horizontal=True)

    with tabs[2]:
        st.write("**Selected engagement mode:**", st.session_state.get("engagement", "Not selected"))
        st.text_area(
            "Why is this engagement mode appropriate for the planned learning activity?",
            key="engagement_rationale"
        )
        st.radio("Engagement Alignment", ALIGNMENT_OPTIONS, key="engagement_alignment", horizontal=True)

    with tabs[3]:
        if st.session_state.get("inclusion_needed", "").startswith("Yes"):
            st.write("**Identified need:**", st.session_state.get("inclusion_need", ""))
            st.write("**Planned support:**", st.session_state.get("inclusion_support", ""))
            st.radio("Need–Support Alignment", ALIGNMENT_OPTIONS, key="inclusion_alignment", horizontal=True)
        else:
            st.session_state["inclusion_alignment"] = "Not applicable"
            st.info("No specific adaptation need was identified. This is treated as not applicable, not as lower quality.")

    with tabs[4]:
        st.write("**Selected assessment:**", st.session_state.get("assessment", "Not selected"))
        st.text_area(
            "How will this assessment provide evidence of the intended learning outcome?",
            key="assessment_rationale"
        )
        st.radio("Assessment–Outcome Alignment", ALIGNMENT_OPTIONS, key="assessment_alignment", horizontal=True)

    st.caption("Aligned = 2, Partially aligned = 1, Review needed = 0. These points summarize alignment judgments; they do not rank teaching methods.")

# ---------- PAGE 5 ----------
elif page.startswith("5"):
    section_header(
        "5 OF 8",
        "Pedagogical Analytics",
        "Review the coherence of the lesson design. A high score means stronger internal alignment, not a universally 'better' teaching method."
    )
    required = ["cognition_alignment", "strategy_alignment", "engagement_alignment", "assessment_alignment"]
    if not all(k in st.session_state for k in required):
        st.warning("Complete Step 4 · Alignment Evidence before viewing analytics.")
    else:
        pas, category, scores = compute_pas()
        if "initial_pas" not in st.session_state:
            st.session_state["initial_pas"] = pas
            st.session_state["initial_category"] = category

        m1, m2, m3 = st.columns(3)
        m1.metric("Pedagogical Alignment Score", f"{pas:.1f}%")
        m2.metric("Alignment Category", category)
        m3.metric("Applicable Dimensions", len(scores))

        chart = pd.DataFrame({
            "Dimension": list(scores.keys()),
            "Alignment (%)": [v / 2 * 100 for v in scores.values()]
        }).set_index("Dimension")
        st.subheader("Alignment Profile")
        st.bar_chart(chart)

        st.subheader("Decision Map")
        map_cols = st.columns(len(scores))
        for col, (dimension, value) in zip(map_cols, scores.items()):
            label = "Aligned" if value == 2 else ("Partial" if value == 1 else "Review")
            with col:
                st.markdown(
                    f'<div class="dpas-card"><div class="dpas-kicker">{dimension}</div>'
                    f'<div class="dpas-title">{label}</div></div>',
                    unsafe_allow_html=True
                )

        alerts = [d for d, v in scores.items() if v < 2]
        if alerts:
            st.warning("Review focus: " + ", ".join(alerts))
        else:
            st.success("All applicable dimensions are currently judged as aligned.")

        st.info("Why this result? PAS is the equal-contribution summary of the applicable alignment judgments. No Bloom level, strategy, engagement mode, adaptation count, or assessment type receives an inherent quality advantage.")

# ---------- PAGE 6 ----------
elif page.startswith("6"):
    section_header(
        "6 OF 8",
        "Teacher-Educator Verification",
        "An educator can independently verify the novice teacher's reasoning. Student and educator judgments remain separate."
    )
    st.info("Prototype verification layer: in a later multi-user deployment this section should be protected by teacher-educator login and persistent storage.")

    dimensions = [
        ("Objective–Cognition", "cognition_alignment", "verify_cognition"),
        ("Objective–Strategy", "strategy_alignment", "verify_strategy"),
        ("Engagement", "engagement_alignment", "verify_engagement"),
        ("Inclusivity", "inclusion_alignment", "verify_inclusion"),
        ("Assessment", "assessment_alignment", "verify_assessment")
    ]

    for title, student_key, verify_key in dimensions:
        if title == "Inclusivity" and st.session_state.get("inclusion_alignment") == "Not applicable":
            continue
        with st.expander(title, expanded=False):
            st.write("**Student judgment:**", st.session_state.get(student_key, "Not completed"))
            st.radio("Educator verification", VERIFY_OPTIONS, key=verify_key, horizontal=True)
            st.text_area("Educator comment", key=f"{verify_key}_comment")

# ---------- PAGE 7 ----------
elif page.startswith("7"):
    section_header(
        "7 OF 8",
        "Reflect & Revise",
        "Use analytics and educator feedback to reconsider one or more pedagogical decisions."
    )
    st.text_area(
        "Which pedagogical decision would you reconsider after reviewing the alignment analysis and educator feedback, and why?",
        key="reflection"
    )
    st.text_area(
        "What revision will you make to the lesson design?",
        key="revision_note"
    )

    if all(k in st.session_state for k in ["cognition_alignment", "strategy_alignment", "engagement_alignment", "assessment_alignment"]):
        current_pas, current_category, _ = compute_pas()
        initial_pas = st.session_state.get("initial_pas", current_pas)
        c1, c2, c3 = st.columns(3)
        c1.metric("Initial PAS", f"{initial_pas:.1f}%")
        c2.metric("Current PAS", f"{current_pas:.1f}%")
        c3.metric("Change", f"{current_pas - initial_pas:+.1f} points")
        st.caption("Return to Design Decisions or Alignment Evidence to revise choices; the current PAS will update when you revisit Analytics.")

# ---------- PAGE 8 ----------
elif page.startswith("8"):
    section_header(
        "8 OF 8",
        "Final Report",
        "Export a transparent record of lesson context, decisions, rationales, alignment judgments, verification, and reflection."
    )
    pas, category, _ = compute_pas()

    verification = {
        "Cognition Verification": st.session_state.get("verify_cognition", ""),
        "Strategy Verification": st.session_state.get("verify_strategy", ""),
        "Engagement Verification": st.session_state.get("verify_engagement", ""),
        "Inclusivity Verification": st.session_state.get("verify_inclusion", ""),
        "Assessment Verification": st.session_state.get("verify_assessment", "")
    }

    report = {
        "Subject / Topic": st.session_state.get("subject_topic", ""),
        "Class / Grade": st.session_state.get("class_level", ""),
        "Intended Learning Outcome": st.session_state.get("learning_outcome", ""),
        "Lesson Purpose": st.session_state.get("lesson_purpose", ""),
        "Outcome Cognitive Demand": st.session_state.get("outcome_cognitive", ""),
        "Planned Cognitive Demand": st.session_state.get("cognitive", ""),
        "Pedagogical Strategy": st.session_state.get("strategy", ""),
        "Learner Engagement": st.session_state.get("engagement", ""),
        "Assessment Type": st.session_state.get("assessment", ""),
        "Cognitive Rationale": st.session_state.get("cognitive_rationale", ""),
        "Strategy Rationale": st.session_state.get("strategy_rationale", ""),
        "Engagement Rationale": st.session_state.get("engagement_rationale", ""),
        "Assessment Rationale": st.session_state.get("assessment_rationale", ""),
        "Objective-Cognition Alignment": st.session_state.get("cognition_alignment", ""),
        "Objective-Strategy Alignment": st.session_state.get("strategy_alignment", ""),
        "Engagement Alignment": st.session_state.get("engagement_alignment", ""),
        "Inclusivity Alignment": st.session_state.get("inclusion_alignment", ""),
        "Assessment Alignment": st.session_state.get("assessment_alignment", ""),
        "Identified Learner/Context Need": st.session_state.get("inclusion_need", ""),
        "Planned Adaptation/Support": st.session_state.get("inclusion_support", ""),
        "PAS Score (V2)": round(pas, 2),
        "Alignment Category": category,
        "Reflection": st.session_state.get("reflection", ""),
        "Revision Note": st.session_state.get("revision_note", ""),
        **verification
    }

    preview = pd.DataFrame([report])
    st.dataframe(preview, use_container_width=True)
    csv = preview.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download DPAS V2 Report (CSV)",
        data=csv,
        file_name="DPAS_V2_Lesson_Alignment_Report.csv",
        mime="text/csv",
        use_container_width=True
    )
    st.caption("PAS is a formative alignment indicator. Student self-analysis and teacher-educator verification are reported separately and are not averaged into a single quality score.")
