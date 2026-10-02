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

outcome_cognitive = st.selectbox(
    "Primary Cognitive Demand of the Intended Learning Outcome",
    [
        "C1 - Remember",
        "C2 - Understand",
        "C3 - Apply",
        "C4 - Analyze",
        "C5 - Evaluate",
        "C6 - Create"
    ],
    help=(
        "Classify the primary cognitive process required by the intended learning outcome. "
        "This is a descriptive classification, not a quality ranking."
    )
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

strategy_rationale = st.text_area(
    "Why is this strategy appropriate for the intended learning outcome?",
    placeholder=(
        "Briefly explain how the selected strategy will help learners achieve the stated outcome "
        "in this lesson context."
    )
)

strategy_alignment = st.radio(
    "Objective–Strategy Alignment",
    [
        "Aligned - the strategy directly supports the intended learning outcome",
        "Partially aligned - the strategy supports the outcome but needs adjustment or supplementation",
        "Review needed - the connection between the strategy and the intended outcome is unclear"
    ],
    help=(
        "Judge the fit between the strategy and the intended learning outcome. "
        "Do not rate the strategy itself as better or worse than other strategies."
    )
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

engagement_rationale = st.text_area(
    "Why is this engagement mode appropriate for the planned learning activity?",
    placeholder=(
        "Briefly explain why individual, pair, group, or whole-class participation "
        "fits the task, lesson purpose, and learner context."
    )
)

engagement_alignment = st.radio(
    "Engagement Alignment",
    [
        "Aligned - the engagement mode appropriately supports the planned learning activity",
        "Partially aligned - the engagement mode is usable but may need adjustment",
        "Review needed - the fit between the engagement mode and planned activity is unclear"
    ],
    help=(
        "Judge the fit between the participation structure and the planned learning activity. "
        "Do not rate one engagement mode as inherently better than another."
    )
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
    inclusion_alignment = st.radio(
        "Inclusivity Alignment",
        [
            "Aligned - the planned support appropriately addresses the identified need",
            "Partially aligned - the support may help but requires refinement",
            "Review needed - the planned support does not clearly address the identified need"
        ],
        help=(
            "Judge the fit between the identified learner/context need and the planned support. "
            "Do not rate the number or intensity of adaptations."
        )
    )
else:
    inclusion_need = ""
    inclusion_support = ""
    inclusion_alignment = "Not applicable - no specific adaptation need identified"

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
        "A1 - Formative",
        "A2 - Summative",
        "A3 - Peer Assessment",
        "A4 - Self-Assessment"
    ],
    help=(
        "Assessment types are descriptive categories, not quality levels. "
        "Formative, summative, peer, and self-assessment may each be appropriate "
        "depending on the intended learning outcome and lesson purpose."
    )
)

st.caption(
    "Assessment type is treated as a classification. "
    "No assessment type is assumed to be inherently superior to another."
)

assessment_rationale = st.text_area(
    "Why is this assessment appropriate for the intended learning outcome?",
    placeholder=(
        "Briefly explain how the selected assessment will provide evidence that learners "
        "have achieved the stated outcome."
    )
)

assessment_alignment = st.radio(
    "Assessment Alignment",
    [
        "Aligned - the assessment directly measures the intended learning outcome",
        "Partially aligned - the assessment provides some evidence but needs refinement",
        "Review needed - the assessment does not clearly measure the intended learning outcome"
    ],
    help=(
        "Judge the fit between the assessment method and the intended learning outcome. "
        "Do not rate formative, summative, peer, or self-assessment as inherently better or worse."
    )
)

st.markdown("---")


# -------- CALCULATION AND VISUALIZATION --------
if st.button(
    "Calculate Provisional Pedagogical Alignment Score",
    type="primary",
    use_container_width=True
):

    # All five original dimensions have now been removed from hierarchical scoring.
    # V2 will compute PAS only after explicit alignment logic is added in later steps.
    pas = None

    # Display current V2 status
    st.subheader("Results")
    st.info(
        "Numerical PAS is temporarily disabled in V2 because the original hierarchical "
        "scoring has been removed. A new alignment-based PAS will be introduced only after "
        "objective–cognition, objective–strategy, engagement, inclusivity, and "
        "assessment-alignment rules are defined."
    )

    # Objective–Cognition Alignment
    st.markdown("#### Objective–Cognition Alignment")

    if cognitive == outcome_cognitive:
        cognition_alignment = "Aligned"
        st.success(
            f"Aligned: the intended learning outcome and the planned lesson both emphasize "
            f"{cognitive}."
        )
    else:
        cognition_alignment = "Review needed"
        st.warning(
            f"Review needed: the intended learning outcome is coded as {outcome_cognitive}, "
            f"while the planned lesson emphasizes {cognitive}. This difference is not "
            "automatically poor pedagogy; review whether the planned cognitive demand "
            "appropriately supports the stated outcome and lesson purpose."
        )

    st.caption(
        "This indicator checks correspondence between the stated outcome and the planned "
        "cognitive demand. It does not assume that higher Bloom levels are better."
    )

    st.markdown("#### Objective–Strategy Alignment")

    st.info(
        f"Selected strategy: {strategy}\n\n"
        f"Alignment judgment: {strategy_alignment}"
    )

    if strategy_alignment.startswith("Aligned"):
        st.success(
            "The selected strategy has been judged to directly support the intended learning outcome."
        )
    elif strategy_alignment.startswith("Partially"):
        st.warning(
            "The selected strategy appears to support the outcome only partially. "
            "Review whether an adjustment or complementary strategy is needed."
        )
    else:
        st.warning(
            "Review the connection between the selected strategy and the intended learning outcome "
            "before finalizing the lesson plan."
        )

    st.caption(
        "This indicator evaluates strategy–outcome fit. It does not assume that lecture, "
        "discussion, activity-based, inquiry-based, or experiential/problem-based teaching "
        "is inherently superior."
    )

    st.markdown("#### Engagement Alignment")

    st.info(
        f"Selected engagement mode: {engagement}\n\n"
        f"Alignment judgment: {engagement_alignment}"
    )

    if engagement_alignment.startswith("Aligned"):
        st.success(
            "The selected engagement mode has been judged to appropriately support the planned learning activity."
        )
    elif engagement_alignment.startswith("Partially"):
        st.warning(
            "The engagement mode may work, but review whether the participation structure "
            "needs adjustment for the task, lesson purpose, or learner context."
        )
    else:
        st.warning(
            "Review whether the selected engagement mode appropriately supports the planned "
            "learning activity before finalizing the lesson plan."
        )

    st.caption(
        "This indicator evaluates engagement–activity fit. It does not assume that individual, "
        "pair, group, or whole-class participation is inherently superior."
    )

    st.markdown("#### Assessment Alignment")

    st.info(
        f"Selected assessment type: {assessment}\n\n"
        f"Alignment judgment: {assessment_alignment}"
    )

    if assessment_alignment.startswith("Aligned"):
        st.success(
            "The selected assessment has been judged to directly measure the intended learning outcome."
        )
    elif assessment_alignment.startswith("Partially"):
        st.warning(
            "The assessment provides only partial evidence of the intended learning outcome. "
            "Review whether the task, criteria, or evidence should be refined."
        )
    else:
        st.warning(
            "Review whether the selected assessment actually measures the intended learning outcome "
            "before finalizing the lesson plan."
        )

    st.caption(
        "This indicator evaluates assessment–outcome fit. It does not assume that formative, "
        "summative, peer, or self-assessment is inherently superior."
    )

    st.markdown("#### Inclusivity Alignment")

    if inclusion_needed.startswith("Yes"):
        st.info(
            f"Identified need: {inclusion_need or 'Not entered'}\n\n"
            f"Planned support: {inclusion_support or 'Not entered'}\n\n"
            f"Alignment judgment: {inclusion_alignment}"
        )
        if inclusion_alignment.startswith("Aligned"):
            st.success(
                "The planned support has been judged to appropriately address the identified learner/context need."
            )
        elif inclusion_alignment.startswith("Partially"):
            st.warning(
                "The planned support may address the need only partially. "
                "Review whether the adaptation should be refined."
            )
        else:
            st.warning(
                "Review the connection between the identified need and the planned support "
                "before finalizing the lesson plan."
            )
    else:
        st.info(
            "No specific adaptation need was identified for this lesson. "
            "This is not treated as a lower-quality choice by itself."
        )

    st.caption(
        "This indicator evaluates need–support fit rather than the amount of inclusion activity."
    )

    # Export results
    st.markdown("---")
    st.subheader("Export Results")

    report_data = {
        "Intended Outcome": [learning_outcome],
        "Outcome Cognitive Demand": [outcome_cognitive],
        "Planned Cognitive Level": [cognitive],
        "Objective-Cognition Alignment": [cognition_alignment],
        "Pedagogical Strategy": [strategy],
        "Strategy Rationale": [strategy_rationale],
        "Objective-Strategy Alignment": [strategy_alignment],
        "Learner Engagement": [engagement],
        "Engagement Rationale": [engagement_rationale],
        "Engagement Alignment": [engagement_alignment],
        "Inclusivity": [inclusivity],
        "Identified Learner/Context Need": [inclusion_need],
        "Planned Adaptation/Support": [inclusion_support],
        "Inclusivity Alignment": [inclusion_alignment],
        "Assessment Type": [assessment],
        "Assessment Rationale": [assessment_rationale],
        "Assessment Alignment": [assessment_alignment],
        "PAS Status": ["Numerical PAS temporarily disabled during V2 redesign"],
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
        ],
        "Assessment Scoring Note": [
            "Assessment type is descriptive and excluded from numerical scoring in V2."
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