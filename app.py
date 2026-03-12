import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# -------- PAGE CONFIGURATION & HEADER --------
st.set_page_config(page_title="DPAS", layout="centered")

st.title("DILP-LA Pedagogical Analytics System (DPAS)")
st.write("Data-Informed Lesson Planning Dashboard")

st.markdown("### About This Application")

st.write("""
**DILP-LA Pedagogical Analytics System (DPAS)** Developed to support data-informed lesson planning and pedagogical alignment analysis.
""")

st.markdown("""
**Developer:** Dr. Meenakshi Dwivedi  
Assistant Professor, School of Education  
Mahatma Jyotiba Phule Rohilkhand University  
Bareilly, Uttar Pradesh, India
""")

st.markdown("---")

# -------- INPUT SECTION --------
cognitive = st.selectbox("Cognitive Level",
    [("C1 - Remember",1), ("C2 - Understand",2), ("C3 - Apply",3),
     ("C4 - Analyze",4), ("C5 - Evaluate",5), ("C6 - Create",6)])

strategy = st.selectbox("Pedagogical Strategy",
    [("PS1 - Lecture",1), ("PS2 - Discussion",2),
     ("PS3 - Activity-Based",3), ("PS4 - Inquiry-Based",4),
     ("PS5 - Experiential/Problem-Based",5)])

engagement = st.selectbox("Learner Engagement Mode",
    [("L1 - Individual",1), ("L2 - Pair",2),
     ("L3 - Group",3), ("L4 - Whole Class",4)])

inclusivity = st.selectbox("Inclusivity Marker",
    [("I1 - No Inclusion",1), ("I2 - Minimal Inclusion",2),
     ("I3 - Moderate Inclusion",3), ("I4 - High Inclusion",4)])

assessment = st.selectbox("Assessment Type",
    [("A1 - Formative",1), ("A2 - Summative",2),
     ("A3 - Peer Assessment",3), ("A4 - Self-Assessment",4)])

st.markdown("---")

# -------- CALCULATION & VISUALIZATION --------
if st.button("Calculate Pedagogical Alignment Score (PAS)"):

    # 1. Calculate Scores
    norm_scores = [
        cognitive[1]/6,
        strategy[1]/5,
        engagement[1]/4,
        inclusivity[1]/4,
        assessment[1]/4
    ]

    percentages = [score * 100 for score in norm_scores]
    pas = np.mean(percentages)

    if pas >= 75:
        category = "High Alignment"
    elif pas >= 50:
        category = "Moderate Alignment"
    else:
        category = "Low Alignment"

    # 2. Display Text Results
    st.subheader("Results")