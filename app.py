import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="PAS Dashboard", layout="centered")

st.title("Pedagogical Alignment Score Dashboard")

# --- USER INPUTS (From your screenshots) ---
# Assuming these selectboxes contain a tuple: (Label, Score Value)
cognitive = st.selectbox("Cognitive Level", [('C1 - Remember', 1), ('C2 - Understand', 2), ('C3 - Apply', 3), ('C4 - Analyze', 4), ('C5 - Evaluate', 5), ('C6 - Create', 6)])
strategy = st.selectbox("Pedagogical Strategy", [('PS1 - Lecture', 1), ('PS2 - Interactive', 2), ('PS3 - Project Based', 3)])
engagement = st.selectbox("Learner Engagement Mode", [('L1 - Individual', 1), ('L2 - Small Group', 2), ('L3 - Whole Class', 3)])
inclusivity = st.selectbox("Inclusivity Marker", [('I1 - Standard', 1), ('I2 - Differentiated', 2), ('I3 - Highly Accessible', 3)])
assessment = st.selectbox("Assessment Type", [('A1 - Formative', 1), ('A2 - Summative', 2)])

st.divider()

# --- BUTTON & LOGIC ---
if st.button("Calculate Pedagogical Alignment Score (PAS)"):
    
    # 1. CALCULATE YOUR SCORES HERE
    # (Note: Replace this dummy math with your actual PAS formula!)
    
    # Extracting the number from the selected tuple
    c_score = cognitive[1]
    s_score = strategy[1]
    e_score = engagement[1]
    i_score = inclusivity[1]
    a_score = assessment[1]
    
    # Dummy calculation for the final 0-100 score
    total_points = c_score + s_score + e_score + i_score + a_score
    pas_score = (total_points / 17) * 100 
    
    # Dummy percentages for the bar chart
    percentages = [
        (c_score / 6) * 100, 
        (s_score / 3) * 100, 
        (e_score / 3) * 100, 
        (i_score / 3) * 100, 
        (a_score / 2) * 100
    ]
    
    # Creating the components dataframe for the bar chart
    components = pd.DataFrame({
        "Category": ["Cognitive", "Strategy", "Engagement", "Inclusivity", "Assessment"],
        "Alignment (%)": percentages
    }).set_index("Category")

    # 2. DRAW THE GAUGE CHART
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pas_score,
        title={'text': "Pedagogical Alignment Score (PAS)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "black"}, # Added a black bar indicator 
            'steps': [
                {'range': [0, 49], 'color': "lightcoral"},
                {'range': [50, 74], 'color': "khaki"},
                {'range': [75, 100], 'color': "lightgreen"}
            ]
        }
    ))
    st.plotly_chart(fig)

    # 3. SHOW THE TEXT FEEDBACK
    if pas_score < 50:
        st.error("Low Alignment: Lesson components require stronger pedagogical alignment.")
    elif pas_score < 75:
        st.warning("Moderate Alignment: Good, but there is room for improvement.")
    else:
        st.success("High Alignment: Excellent pedagogical structure!")

    # 4. DRAW THE BAR CHART
    st.markdown("### Component Breakdown")
    st.bar_chart(components)