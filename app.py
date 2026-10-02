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
        ("C1 - Remember", 1),
        ("C2 - Understand", 2),
        ("C3 - Apply", 3),
        ("C4 - Analyze", 4),
        ("C5 - Evaluate", 5),
        ("C6 - Create", 6)
    ],
    format_func=lambda option: option[0]
)

strategy = st.selectbox(
    "Pedagogical Strategy",
    [
        ("PS1 - Lecture", 1),
        ("PS2 - Discussion", 2),
        ("PS3 - Activity-Based", 3),
        ("PS4 - Inquiry-Based", 4),
        ("PS5 - Experiential/Problem-Based", 5)
    ],
    format_func=lambda option: option[0]
)

engagement = st.selectbox(
    "Learner Engagement Mode",
    [
        ("L1 - Individual", 1),
        ("L2 - Pair", 2),
        ("L3 - Group", 3),
        ("L4 - Whole Class", 4)
    ],
    format_func=lambda option: option[0]
)

inclusivity = st.selectbox(
    "Inclusivity Marker",
    [
        ("I1 - No Inclusion", 1),
        ("I2 - Minimal Inclusion", 2),
        ("I3 - Moderate Inclusion", 3),
        ("I4 - High Inclusion", 4)
    ],
    format_func=lambda option: option[0]
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
    "Calculate Pedagogical Alignment Score (PAS)",
    type="primary",
    use_container_width=True
):

    # Calculate normalized dimension scores
    norm_scores = [
        cognitive[1] / 6,
        strategy[1] / 5,
        engagement[1] / 4,
        inclusivity[1] / 4,
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
            label="Pedagogical Alignment Score",
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
            title={"text": "Pedagogical Alignment Score (PAS)"},
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
            "Cognitive",
            "Strategy",
            "Engagement",
            "Inclusivity",
            "Assessment"
        ],
        "Alignment (%)": percentages
    }).set_index("Dimension")

    st.bar_chart(df_chart)

    # Export results
    st.markdown("---")
    st.subheader("Export Results")

    report_data = {
        "Cognitive Level": [cognitive[0]],
        "Pedagogical Strategy": [strategy[0]],
        "Learner Engagement": [engagement[0]],
        "Inclusivity": [inclusivity[0]],
        "Assessment Type": [assessment[0]],
        "PAS Score": [round(pas, 2)],
        "Alignment Category": [category]
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