from pathlib import Path

import streamlit as st
import numpy as np
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
st.write("Data-Informed Lesson Planning Dashboard")

st.markdown("### About This Application")

# Photograph location
photo_path = Path(__file__).parent / "profile_photo.png"

# About and developer section
information_column, photo_column = st.columns([3, 1])

with information_column:
    st.markdown("""
    **DILP-LA Pedagogical Analytics System (DPAS)** is developed to support
    data-informed lesson planning and pedagogical alignment analysis.

    **Developer:** Dr. Meenakshi Dwivedi  
    Assistant Professor, School of Education  
    Mahatma Jyotiba Phule Rohilkhand University  
    Bareilly, Uttar Pradesh, India
    """)

with photo_column:
    if photo_path.exists():
        st.image(
            str(photo_path),
            width=165,
            caption="Dr. Meenakshi Dwivedi"
        )
    else:
        st.warning("Profile photograph not found.")

st.markdown("---")


# -------- LESSON CONTEXT AND PURPOSE --------
st.subheader("Lesson Context and Purpose")
st.caption(
    "These details provide the pedagogical context for interpreting lesson-design choices. "
    "They do not yet affect the PAS calculation in this version."
)

subject_topic = st.text_input(
    "Subject / Topic",
    placeholder="e.g., Science - Photosynthesis"
)

class_level = st.text_input(
    "Class / Grade Level",
    placeholder="e.g., Grade 7 / B.Ed. practicum class"
)

learning_outcome = st.text_area(
    "Intended Learning Outcome",
    placeholder="State what learners should know, understand, or be able to do by the end of the lesson."
)

lesson_purpose = st.selectbox(
    "Lesson Purpose",
    [
        "Introduce a new concept",
        "Develop conceptual understanding",
        "Practice / application",
        "Inquiry / problem solving",
        "Revision / consolidation",
        "Assessment / diagnosis",
        "Other"
    ]
)

learner_context = st.text_area(
    "Learner / Context Consideration",
    placeholder=(
        "Optional: note relevant learner needs, prior knowledge, language, "
        "classroom conditions, accessibility needs, or other contextual factors."
    )
)

st.markdown("---")


# -------- INPUT SECTION --------
cognitive = st.selectbox(
    "Cognitive Level",
    [
        "C1 - Remember",
        "C2 - Understand",
        "C3 - Apply",
        "C4 - Analyze",
        "C5 - Evaluate",
        "C6 - Create"
    ],
    help=(
        "Bloom's cognitive levels are used here as descriptive categories, "
        "not as a quality hierarchy. C6 is not assumed to be better than C1."
    )
)

st.caption(
    "Bloom's taxonomy is used as a classification framework. "
    "The appropriateness of a cognitive level depends on the intended learning outcome "
    "and lesson purpose."
)

strategy = st.selectbox(
    "Pedagogical Strategy",
    [
        "PS1 - Lecture",
        "PS2 - Discussion",
        "PS3 - Activity-Based",
        "PS4 - Inquiry-Based",
        "PS5 - Experiential/Problem-Based"
    ],
    help=(
        "Pedagogical strategies are used here as descriptive categories, "
        "not as a quality hierarchy. Experiential/problem-based teaching is not "
        "assumed to be inherently better than lecture, discussion, activity-based, "
        "or inquiry-based teaching."
    )
)

st.caption(
    "Pedagogical strategy is treated as a classification. Its quality depends on "
    "how well it fits the intended learning outcome, lesson purpose, content, and learner context."
)

engagement = st.selectbox(
    "Learner Engagement Mode",
    [
        "L1 - Individual",
        "L2 - Pair",
        "L3 - Group",
        "L4 - Whole Class"
    ],
    help=(
        "Learner engagement modes are descriptive categories, not quality levels. "
        "Individual, pair, group, and whole-class participation may each be appropriate "
        "depending on the intended learning outcome, lesson purpose, task, and classroom context."
    )
)

st.caption(
    "Learner engagement mode is treated as a classification. "
    "No mode is assumed to be inherently superior to another."
)

st.markdown("#### Inclusivity and Learner Support")

inclusion_needed = st.radio(
    "Does this lesson require a specific adaptation or support for identified learner/context needs?",
    [
        "No specific adaptation need identified for this lesson",
        "Yes - a specific learner/context need has been identified"
    ],
    help=(
        "Inclusivity is not treated as a simple 'low-to-high' quantity. "
        "The focus is on whether relevant learner needs are identified and appropriately addressed."
    )
)

if inclusion_needed.startswith("Yes"):
    inclusion_need = st.text_area(
        "Identified learner/context need",
        placeholder=(
            "e.g., language support, accessibility need, prior-learning gap, "
            "participation barrier, sensory need, or other relevant consideration."
        )
    )
    inclusion_support = st.text_area(
        "Planned adaptation / support",
        placeholder=(
            "Describe the specific instructional adaptation or support planned "
            "to address the identified need."
        )
    )
else:
    inclusion_need = ""
    inclusion_support = ""

st.caption(
    "Inclusivity is evaluated in relation to relevant learner needs and planned support. "
    "More adaptations are not automatically better; appropriateness and relevance matter."
)

inclusivity = (
    "Specific learner/context need identified"
    if inclusion_needed.startswith("Yes")
    else "No specific adaptation need identified"
)

assessment = st.selectbox(
    "Assessment Type",
    [
        ("A1 - Formative", 1),
        ("A2 - Summative", 2),
        ("A3 - Peer Assessment", 3),
        ("A4 - Self-Assessment", 4)
    ],
    format_func=lambda option: option[0]
)

st.markdown("---")


# -------- CALCULATION AND VISUALIZATION --------
if st.button(
    "Calculate Provisional Pedagogical Alignment Score",
    type="primary",
    use_container_width=True
):

    # Provisional scoring during V2 redesign.
    # Cognitive level, pedagogical strategy, learner engagement mode, and inclusivity
    # are intentionally excluded from numerical scoring while their alignment logic
    # is being redesigned.
    norm_scores = [
        assessment[1] / 4
    ]

    percentages = [score * 100 for score in norm_scores]
    pas = np.mean(percentages)

    # Determine alignment category
    if pas >= 75:
        category = "High Alignment"
    elif pas >= 50:
        category = "Moderate Alignment"
    else:
        category = "Low Alignment"

    # Display results
    st.subheader("Results")

    result_column1, result_column2 = st.columns(2)

    with result_column1:
        st.metric(
            label="Provisional Alignment Score",
            value=f"{pas:.2f}%"
        )

    with result_column2:
        st.metric(
            label="Alignment Category",
            value=category
        )

    # Gauge chart
    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=pas,
            number={"suffix": "%"},
            title={"text": "Provisional Alignment Score"},
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
                    "value": pas
                }
            }
        )
    )

    fig_gauge.update_layout(
        height=350,
        margin={"l": 30, "r": 30, "t": 70, "b": 20}
    )

    st.plotly_chart(
        fig_gauge,
        use_container_width=True
    )

    st.info(
        f"Selected cognitive category: {cognitive}. "
        "This category is not scored numerically in V2. Its alignment with the intended "
        "learning outcome will be evaluated in a later redesign step."
    )

    st.info(
        f"Selected pedagogical strategy: {strategy}. "
        "This strategy is not scored numerically in V2. Its appropriateness will later be "
        "evaluated against the intended learning outcome, lesson purpose, and learner context."
    )

    st.info(
        f"Selected learner engagement mode: {engagement}. "
        "This mode is not scored numerically in V2. Its appropriateness will later be "
        "evaluated in relation to the planned learning activity and lesson purpose."
    )

    if inclusion_needed.startswith("Yes"):
        st.info(
            "Inclusivity note: a specific learner/context need has been identified. "
            "The planned support is recorded for later appropriateness-based evaluation; "
            "it is not scored by quantity or intensity."
        )
    else:
        st.info(
            "Inclusivity note: no specific adaptation need was identified for this lesson. "
            "This is not treated as a lower-quality choice by itself."
        )

    # Feedback message
    if pas < 50:
        st.error(
            "Low Alignment: Lesson components require stronger "
            "pedagogical alignment."
        )
    elif pas < 75:
        st.warning(
            "Moderate Alignment: Some instructional elements can be improved."
        )
    else:
        st.success(
            "High Alignment: Lesson design demonstrates strong "
            "pedagogical alignment."
        )

    # Dimension-wise chart
    st.subheader("Dimension-wise Alignment")

    df_chart = pd.DataFrame({
        "Dimension": [
            "Assessment"
        ],
        "Alignment (%)": percentages
    }).set_index("Dimension")

    st.bar_chart(df_chart)

    # Export results
    st.markdown("---")
    st.subheader("Export Results")

    report_data = {
        "Cognitive Level": [cognitive],
        "Pedagogical Strategy": [strategy],
        "Learner Engagement": [engagement],
        "Inclusivity": [inclusivity],
        "Identified Learner/Context Need": [inclusion_need],
        "Planned Adaptation/Support": [inclusion_support],
        "Assessment Type": [assessment[0]],
        "Provisional PAS Score": [round(pas, 2)],
        "Alignment Category": [category],
        "Cognitive Scoring Note": [
            "Bloom category is descriptive and excluded from numerical scoring in V2."
        ],
        "Strategy Scoring Note": [
            "Pedagogical strategy is descriptive and excluded from numerical scoring in V2."
        ],
        "Engagement Scoring Note": [
            "Learner engagement mode is descriptive and excluded from numerical scoring in V2."
        ],
        "Inclusivity Scoring Note": [
            "Inclusivity is recorded through identified need and planned support, "
            "and is excluded from numerical scoring during V2 redesign."
        ]
    }

    report_df = pd.DataFrame(report_data)
    csv = report_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download PAS Report (CSV)",
        data=csv,
        file_name="PAS_Lesson_Plan_Report.csv",
        mime="text/csv",
        use_container_width=True
    )