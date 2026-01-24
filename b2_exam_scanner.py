import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Official IQ Test",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS to hide Streamlit branding and make it look like a standalone app
st.markdown("""
<style>
    /* Hide Streamlit default menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Modern Font & Colors */
    body {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        background-color: #f5f7fa;
    }

    /* Card Styling */
    .stApp {
        background-color: #f5f7fa;
    }
    
    div[data-testid="stVerticalBlock"] > div {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* Button Styling */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #007AFF;
        color: white;
        border: none;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #0056b3;
        box-shadow: 0 4px 8px rgba(0,122,255,0.3);
    }

    /* Option Buttons (Secondary) */
    .option-btn > button {
        background-color: #f0f2f6;
        color: #333;
    }
    
    h1, h2, h3 {
        color: #2c3e50;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA MODELS & MOCK QUESTIONS
# -----------------------------------------------------------------------------

# We generate mock "Matrix" questions. 
# In a real app, these would be paths to images (e.g., 'assets/q1.png').
QUESTIONS = [
    {
        "id": 1,
        "text": "Which shape completes the pattern?",
        "pattern_type": "progression", # Mock type
        "options": ["⚪ Circle", "⬛ Square", "🔺 Triangle", "⭐ Star"],
        "answer": 1 # Index of correct answer
    },
    {
        "id": 2,
        "text": "Logic: 1 -> 2 -> 4 -> ?",
        "pattern_type": "math",
        "options": ["6", "8", "7", "5"],
        "answer": 1
    },
    {
        "id": 3,
        "text": "Select the missing piece.",
        "pattern_type": "visual",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "answer": 2
    },
    {
        "id": 4,
        "text": "Which object does not belong?",
        "pattern_type": "visual",
        "options": ["Apple", "Banana", "Carrot", "Grape"],
        "answer": 2 # Carrot is a vegetable
    },
    {
        "id": 5,
        "text": "Complete the sequence: A, C, E, G, ...",
        "pattern_type": "logic",
        "options": ["H", "I", "J", "K"],
        "answer": 1
    }
]

# -----------------------------------------------------------------------------
# 3. SESSION STATE MANAGEMENT
# -----------------------------------------------------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# -----------------------------------------------------------------------------
# 4. HELPER FUNCTIONS
# -----------------------------------------------------------------------------

def start_quiz():
    st.session_state.page = 'quiz'
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.start_time = time.time()
    st.rerun()

def submit_answer(option_index):
    # Record answer
    q_index = st.session_state.current_q
    correct_index = QUESTIONS[q_index]['answer']
    
    st.session_state.answers[q_index] = option_index
    
    if option_index == correct_index:
        st.session_state.score += 1
    
    # Move to next or finish
    if st.session_state.current_q < len(QUESTIONS) - 1:
        st.session_state.current_q += 1
        st.rerun()
    else:
        st.session_state.page = 'result'
        st.rerun()

def calculate_iq(raw_score, total_questions):
    # Mock Formula: Baseline 70 + (Percentage * 70) 
    # Creates a range of ~70 to 140
    percentage = raw_score / total_questions
    iq = 70 + (percentage * 75)
    return int(iq)

# -----------------------------------------------------------------------------
# 5. PAGE VIEWS
# -----------------------------------------------------------------------------

def show_home():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🧠")
        st.title("Standardized IQ Test")
        st.markdown(
            "<p style='text-align: center; color: #666;'>Determine your cognitive potential with our Raven's Matrices inspired test.</p>", 
            unsafe_allow_html=True
        )
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.info("**⏱️ Duration**\n\n15-20 Minutes")
        with c2:
            st.info("**❓ Questions**\n\n30 Items")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("START CERTIFICATION START"):
            start_quiz()
            
        st.markdown(
            "<p style='text-align: center; font-size: 0.8em; color: #999; margin-top: 20px;'>Scientific calculation • Instant results • Mobile optimized</p>", 
            unsafe_allow_html=True
        )

def show_quiz():
    q_index = st.session_state.current_q
    question = QUESTIONS[q_index]
    total = len(QUESTIONS)
    
    # Progress Bar
    progress = (q_index + 1) / total
    st.progress(progress)
    
    # Header info
    c1, c2 = st.columns([3, 1])
    with c1:
        st.caption(f"Question {q_index + 1} of {total}")
    with c2:
        # Simple timer calculation (mock display as Streamlit doesn't auto-update seconds)
        elapsed = int(time.time() - st.session_state.start_time)
        mins, secs = divmod(elapsed, 60)
        st.caption(f"⏱️ {mins:02}:{secs:02}")

    st.markdown("---")

    # VISUAL QUESTION PLACEHOLDER
    # In a real app, use st.image("assets/q1.png")
    st.markdown(f"""
    <div style="background-color: #eef2f5; height: 200px; display: flex; align-items: center; justify-content: center; border-radius: 10px; margin-bottom: 20px; border: 2px dashed #cbd5e0;">
        <h3 style="color: #6c757d;">{question['text']}</h3>
        <!-- You would put your IQ Matrix Image here -->
    </div>
    """, unsafe_allow_html=True)

    # Options Grid
    opts = question['options']
    
    # Create a 2x2 grid for buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(opts[0], key=f"q{q_index}_opt0"): submit_answer(0)
        if st.button(opts[2], key=f"q{q_index}_opt2"): submit_answer(2)
        
    with col2:
        if st.button(opts[1], key=f"q{q_index}_opt1"): submit_answer(1)
        if