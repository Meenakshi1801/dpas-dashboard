from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# -------- PAGE CONFIGURATION --------
st.set_page_config(
    page_title="DPAS",
    page_icon="📊",
    layout="centered"
)


# -------- HEADER --------
st.title("DILP-LA Pedagogical Analytics System (DPAS)")
st.caption("A compact pedagogical decision-support dashboard for lesson planning")

photo_path = Path(__file__).parent / "profile_photo.png"

information_column, photo_column = st.columns([3, 1])

with information_column:
    st.markdown("""
    **DPAS** supports pre-service teachers in examining the coherence of lesson-design
    decisions in relation to the intended learning outcome, lesson purpose, and learner context.

    **Developer:** Dr. Meenakshi Dwivedi  
    Assistant Professor, School of Education  
    Mahatma Jyotiba Phule Rohilkhand University  
    Bareilly, Uttar Pradesh, India
    """)

with photo_column:
    if photo_path.exists():
        st.image(str(photo_path), width=165, caption="Dr. Meenakshi Dwivedi")
    else:
        st.warning("Profile photograph not found.")

st.info(
    "DPAS does not assume that a higher Bloom level, a greater number of strategies, "
    "collaborative participation, or a particular assessment type is automatically superior. "
    "The focus is on contextual fit and coherence."
)

st.markdown("---")


# -------- SECTION 1: LESSON CONTEXT --------
st.subheader("1. Lesson Context")

intended_outcome = st.text_area(
    "Intended Learning Outcome",
    placeholder="What should learners know, understand, or be able to do by the end of the lesson?",
    height=90
)

lesson_purpose = st.selectbox(
    "Lesson Purpose",
    [
        "Introduce a new concept",
        "Develop understanding",
        "Practice or apply learning",
        "Analyze or investigate",
        "Consolidate or revise",
        "Assess learning",
        "Other"
    ]
)

learner_context = st.text_area(
    "Learner / Context Consideration",
    placeholder="Mention any relevant learner need, prior knowledge, classroom condition, or contextual factor.",
    height=85
)

st.markdown("---")


# -------- SECTION 2: DESIGN DECISIONS --------
st.subheader("2. Lesson Design Decisions")

cognitive = st.selectbox(
    "Planned Cognitive Demand",
    [
        "C1 - Remember",
        "C2 - Understand",
        "C3 - Apply",
        "C4 - Analyze",
        "C5 - Evaluate",
        "C6 - Create"
    ]
)

strategy = st.selectbox(
    "Pedagogical Strategy",
    [
        "Lecture / Explanation",
        "Discussion",
        "Activity-Based",
        "Inquiry-Based",
        "Experiential / Problem-Based",
        "Demonstration",
        "Collaborative Learning",
        "Other"
    ]
)

engagement = st.selectbox(
    "Learner Engagement Mode",
    [
        "Individual",
        "Pair",
        "Small Group",
        "Whole Class",
        "Mixed / Flexible"
    ]
)

inclusivity = st.selectbox(
    "Learner Support / Inclusivity",
    [
        "No specific support required for this lesson",
        "Specific learner/context need identified and supported",
        "Differentiated support planned",
        "Flexible support depending on learner response"
    ]
)

assessment = st.selectbox(
    "Assessment Approach",
    [
        "Formative Assessment",
        "Summative Assessment",
        "Peer Assessment",
        "Self-Assessment",
        "Teacher Observation / Questioning",
        "Performance / Product Assessment",
        "Combination of approaches"
    ]
)

st.markdown("---")


# -------- SECTION 3: ALIGNMENT CHECK --------
st.subheader("3. Alignment Check")
st.write(
    "For each relationship, judge how well the selected lesson-design decision fits the "
    "intended outcome, lesson purpose, and learner context."
)

alignment_options = {
    "Strong fit": 4,
    "Appropriate fit": 3,
    "Partial fit": 2,
    "Needs reconsideration": 1
}

def alignment_item(label, key):
    choice = st.radio(
        label,
        list(alignment_options.keys()),
        horizontal=True,
        key=key
    )
    note = ""
    if choice in ["Partial fit", "Needs reconsideration"]:
        note = st.text_area(
            "What may need reconsideration?",
            key=f"{key}_note",
            placeholder="Briefly explain what you may revise or reconsider."
        )
    return choice, alignment_options[choice], note


cog_choice, cog_score, cog_note = alignment_item(
    "Outcome–Cognitive Demand Alignment",
    "cog_align"
)
str_choice, str_score, str_note = alignment_item(
    "Outcome–Strategy Alignment",
    "str_align"
)
eng_choice, eng_score, eng_note = alignment_item(
    "Engagement Appropriateness",
    "eng_align"
)
inc_choice, inc_score, inc_note = alignment_item(
    "Context / Inclusivity Appropriateness",
    "inc_align"
)
ass_choice, ass_score, ass_note = alignment_item(
    "Outcome–Assessment Alignment",
    "ass_align"
)

st.markdown("---")


# -------- SECTION 4: ANALYSIS --------
if st.button("Analyze Lesson Alignment", type="primary", use_container_width=True):
    if not intended_outcome.strip():
        st.error("Please enter the Intended Learning Outcome before analyzing the lesson.")
        st.stop()

    scores = [cog_score, str_score, eng_score, inc_score, ass_score]
    profile_score = ((sum(scores) / len(scores)) - 1) / 3 * 100

    if profile_score >= 75:
        profile_label = "Strong self-reported coherence"
    elif profile_score >= 50:
        profile_label = "Generally appropriate with some review"
    else:
        profile_label = "Substantial reconsideration indicated"

    st.subheader("Dashboard Results")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Self-Reported Alignment Profile", f"{profile_score:.1f}%")
    with col2:
        st.metric("Profile Interpretation", profile_label)

    # Attractive gauge retained from the original dashboard
    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=profile_score,
            number={"suffix": "%"},
            title={"text": "Self-Reported Lesson Alignment Profile"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#1F77B4"},
                "steps": [
                    {"range": [0, 50], "color": "lightcoral"},
                    {"range": [50, 75], "color": "khaki"},
                    {"range": [75, 100], "color": "lightgreen"}
                ],
                "threshold": {
                    "line": {"color": "black", "width": 4},
                    "thickness": 0.75,
                    "value": profile_score
                }
            }
        )
    )
    fig_gauge.update_layout(
        height=340,
        margin={"l": 30, "r": 30, "t": 70, "b": 20}
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    st.subheader("Dimension-wise Alignment Profile")

    chart_df = pd.DataFrame({
        "Dimension": [
            "Cognitive",
            "Strategy",
            "Engagement",
            "Inclusivity / Context",
            "Assessment"
        ],
        "Alignment (%)": [
            ((cog_score - 1) / 3) * 100,
            ((str_score - 1) / 3) * 100,
            ((eng_score - 1) / 3) * 100,
            ((inc_score - 1) / 3) * 100,
            ((ass_score - 1) / 3) * 100
        ]
    }).set_index("Dimension")

    st.bar_chart(chart_df)

    st.subheader("Design Snapshot")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Cognitive demand:** {cognitive}")
        st.markdown(f"**Strategy:** {strategy}")
        st.markdown(f"**Engagement:** {engagement}")
    with c2:
        st.markdown(f"**Learner support:** {inclusivity}")
        st.markdown(f"**Assessment:** {assessment}")
        st.markdown(f"**Lesson purpose:** {lesson_purpose}")

    reconsider = []
    for dimension, choice in [
        ("Cognitive demand", cog_choice),
        ("Strategy", str_choice),
        ("Engagement", eng_choice),
        ("Inclusivity / context", inc_choice),
        ("Assessment", ass_choice),
    ]:
        if choice in ["Partial fit", "Needs reconsideration"]:
            reconsider.append(dimension)

    if reconsider:
        st.warning(
            "Areas identified for review: " + ", ".join(reconsider) + "."
        )
    else:
        st.success(
            "No dimension was marked for immediate reconsideration. Review the lesson as a whole "
            "before finalizing it."
        )

    st.caption(
        "This profile represents the student's structured self-appraisal of alignment. "
        "It is a formative decision-support output and is not an independent measure of lesson quality."
    )

    st.markdown("---")
    st.subheader("Export Results")

    report_df = pd.DataFrame({
        "Intended Learning Outcome": [intended_outcome],
        "Lesson Purpose": [lesson_purpose],
        "Learner / Context Consideration": [learner_context],
        "Cognitive Demand": [cognitive],
        "Pedagogical Strategy": [strategy],
        "Learner Engagement": [engagement],
        "Learner Support / Inclusivity": [inclusivity],
        "Assessment Approach": [assessment],
        "Cognitive Alignment": [cog_choice],
        "Strategy Alignment": [str_choice],
        "Engagement Appropriateness": [eng_choice],
        "Context / Inclusivity Appropriateness": [inc_choice],
        "Assessment Alignment": [ass_choice],
        "Self-Reported Alignment Profile": [round(profile_score, 2)],
        "Cognitive Reflection": [cog_note],
        "Strategy Reflection": [str_note],
        "Engagement Reflection": [eng_note],
        "Inclusivity Reflection": [inc_note],
        "Assessment Reflection": [ass_note]
    })

    csv = report_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Lesson Alignment Report (CSV)",
        data=csv,
        file_name="DPAS_Lesson_Alignment_Report.csv",
        mime="text/csv",
        use_container_width=True
    )
