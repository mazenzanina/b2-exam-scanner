import streamlit as st
import google.generativeai as genai
import pypdf
import json
import re
import hashlib
import time

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & "TELC/VERCEL" CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Digital Exam Simulator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* Clean, flat design mimicking modern React/Vercel apps */
    .stApp {
        background-color: #f7f9fa;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Login & Main Cards */
    .exam-card {
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
        border-radius: 8px;
        padding: 40px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-top: 5vh;
    }
    
    /* Typography */
    h1, h2, h3 {
        color: #1a202c !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    p, span, label {
        color: #4a5568 !important;
    }
    
    /* Primary Buttons (The "Telc/Vercel" Blue/Black) */
    div.stButton > button {
        background-color: #1a202c;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #2d3748;
        color: white;
        transform: translateY(-1px);
    }
    
    /* Secondary Action Button (Submit/Grade) */
    .btn-grade > button {
        background-color: #0070f3 !important; /* Vercel Blue */
    }
    .btn-grade > button:hover {
        background-color: #0051a2 !important;
    }

    /* Radio buttons & Inputs (Exam feel) */
    .stRadio > div {
        background: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin-bottom: 10px;
    }
    .stTextArea textarea {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        background: #fdfdfd;
    }
    
    /* Timer / Header Banner */
    .exam-header {
        background: #ffffff;
        border-bottom: 1px solid #e2e8f0;
        padding: 15px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
        border-radius: 8px;
    }
    .exam-header h3 { margin: 0; font-size: 1.2rem; }
    .timer { font-family: monospace; font-size: 1.2rem; color: #e53e3e !important; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. STATE MANAGEMENT (Login, Dashboard, Exam)
# -----------------------------------------------------------------------------
if 'page' not in st.session_state:
    st.session_state.page = "login" # login, dashboard, exam, results
if 'exam_data' not in st.session_state:
    st.session_state.exam_data = None
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}

# -----------------------------------------------------------------------------
# 3. CORE LOGIC & AI ENGINE
# -----------------------------------------------------------------------------
def robust_json_extractor(text):
    try:
        if not text: return None
        start = text.find('{')
        end = text.rfind('}') + 1
        if start == -1 or end == 0: return None
        return json.loads(text[start:end])
    except: return None

def extract_text(uploaded_file):
    try:
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content: text += content + "\n"
        return text if len(text) > 20 else None
    except: return None

def generate_interactive_exam(api_key, text):
    """
    Turns the PDF into an interactive JSON test format.
    """
    genai.configure(api_key=api_key)
    models =[m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    You are an expert German B2/C1 Exam Creator (Telc/Goethe standard).
    Analyze the uploaded text. If it is a mock exam, extract the reading questions and writing prompts.
    If it is just a text, CREATE 3 Multiple Choice Questions and 1 Writing Prompt based on the topic.
    
    OUTPUT EXACTLY IN THIS JSON FORMAT:
    {{
        "Lesen": {{
            "Text_Context": "Summary or specific paragraph to read.",
            "Questions":[
                {{
                    "id": "q1",
                    "question": "The question text?",
                    "options":["Option A", "Option B", "Option C"],
                    "correct": "Option A"
                }},
                {{
                    "id": "q2",
                    "question": "Next question?",
                    "options":["A", "B", "C"],
                    "correct": "B"
                }}
            ]
        }},
        "Schreiben": {{
            "Prompt": "Write an email/essay about..."
        }}
    }}
    
    TEXT: {text[:25000]}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"API_ERROR: {str(e)}"

def evaluate_writing(api_key, prompt, user_text):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    sys_prompt = f"Grade this B2 German text. Prompt: {prompt}. User Text: {user_text}. Give a score (out of 10) and 2 sentences of feedback."
    try:
        return model.generate_content(sys_prompt).text
    except:
        return "Evaluation failed."

# -----------------------------------------------------------------------------
# 4. VIEWS (Login -> Dashboard -> Exam Simulator)
# -----------------------------------------------------------------------------

def view_login():
    """Mock Login Screen matching the portal vibe."""
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div class="exam-card">
            <div style="text-align: center; margin-bottom: 30px;">
                <img src="https://img.icons8.com/color/96/germany.png" width="60">
                <h2>Digital Exam Portal</h2>
                <p>Please log in to access your modules</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Streamlit inputs just below the HTML card to keep functionality
        email = st.text_input("Email / Candidate ID", placeholder="candidate@exam.com")
        pwd = st.text_input("Password", type="password", placeholder="••••••••")
        
        if st.button("Log In"):
            st.session_state.page = "dashboard"
            st.rerun()

def view_dashboard():
    """File Upload and Exam Generation."""
    st.markdown("""
        <div class="exam-header">
            <h3>🎓 Candidate Dashboard</h3>
            <span style="color: #4a5568;">Status: Ready</span>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Prepare Your Exam Session")
        st.write("Upload a PDF (Textbook, Mock Exam, or Article). The AI will construct a simulated test environment from it.")
        
        uploaded_file = st.file_uploader("Upload Exam Material (PDF)", type=["pdf"])
        api_key = st.text_input("Enter your AI Key to initialize Simulator", type="password")
        
        if uploaded_file and api_key:
            if st.button("🚀 Start Simulator Session"):
                with st.spinner("Analyzing text and generating exam environment..."):
                    txt = extract_text(uploaded_file)
                    if txt:
                        raw_json = generate_interactive_exam(api_key, txt)
                        data = robust_json_extractor(raw_json)
                        if data:
                            st.session_state.exam_data = data
                            st.session_state.user_answers = {}
                            st.session_state.api_key = api_key # save for grading
                            st.session_state.page = "exam"
                            st.rerun()
                        else:
                            st.error("Failed to generate exam structure. Please try a different PDF.")
                    else:
                        st.error("Could not read text from PDF.")

    with col2:
        st.info("**Instructions:**\n1. Ensure stable connection.\n2. Once started, the timer will begin.\n3. Complete Reading and Writing sections.")

def view_exam():
    """The Interactive Exam Environment."""
    st.markdown("""
        <div class="exam-header">
            <h3>📝 Module: Lesen & Schreiben</h3>
            <div class="timer">⏱️ 45:00</div>
        </div>
    """, unsafe_allow_html=True)
    
    data = st.session_state.exam_data
    
    # --- LESEN (Reading Section) ---
    st.markdown("## Teil 1: Leseverstehen")
    lesen = data.get("Lesen", {})
    
    st.info(f"**Context / Text:**\n{lesen.get('Text_Context', 'Read the uploaded document.')}")
    st.markdown("---")
    
    for q in lesen.get("Questions", []):
        st.markdown(f"**{q['question']}**")
        # Radio button for options
        choice = st.radio("Select answer:", q['options'], key=q['id'], index=None)
        st.session_state.user_answers[q['id']] = choice
        st.write("") # spacing
        
    # --- SCHREIBEN (Writing Section) ---
    st.markdown("---")
    st.markdown("## Teil 2: Schriftlicher Ausdruck")
    schreiben = data.get("Schreiben", {})
    prompt = schreiben.get("Prompt", "Write a short essay.")
    
    st.warning(f"**Aufgabe:** {prompt}")
    writing_ans = st.text_area("Type your text here...", height=250, key="writing_task")
    st.session_state.user_answers["writing"] = writing_ans
    
    # --- SUBMIT ---
    st.markdown("---")
    st.markdown("<div class='btn-grade'>", unsafe_allow_html=True)
    if st.button("Submit Exam & View Results"):
        st.session_state.page = "results"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def view_results():
    """Evaluation Screen."""
    st.markdown("""
        <div class="exam-header">
            <h3>📊 Evaluation Report</h3>
        </div>
    """, unsafe_allow_html=True)
    
    data = st.session_state.exam_data
    answers = st.session_state.user_answers
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Reading Results")
        score = 0
        total = len(data.get("Lesen", {}).get("Questions",[]))
        
        for q in data.get("Lesen", {}).get("Questions", []):
            user_choice = answers.get(q['id'])
            correct = q.get('correct')
            
            if user_choice == correct:
                score += 1
                st.success(f"**Q: {q['question']}**\n\n✅ You chose: {user_choice}")
            else:
                st.error(f"**Q: {q['question']}**\n\n❌ You chose: {user_choice} (Correct: {correct})")
                
        st.metric("Reading Score", f"{score} / {total}")

    with col2:
        st.markdown("### Writing Evaluation")
        user_text = answers.get("writing", "")
        if not user_text.strip():
            st.warning("No text submitted.")
        else:
            with st.spinner("AI Examiner is reading your text..."):
                prompt = data.get("Schreiben", {}).get("Prompt", "")
                feedback = evaluate_writing(st.session_state.api_key, prompt, user_text)
                
                st.info("**Your Text:**\n" + user_text[:150] + "...")
                st.markdown("### 🤖 Examiner Feedback:")
                st.write(feedback)

    if st.button("Return to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# -----------------------------------------------------------------------------
# 5. ROUTER
# -----------------------------------------------------------------------------
def main():
    if st.session_state.page == "login":
        view_login()
    elif st.session_state.page == "dashboard":
        view_dashboard()
    elif st.session_state.page == "exam":
        view_exam()
    elif st.session_state.page == "results":
        view_results()

if __name__ == "__main__":
    main()