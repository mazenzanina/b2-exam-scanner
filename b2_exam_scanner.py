import streamlit as st
import google.generativeai as genai
import pypdf
import json
import re

# -----------------------------------------------------------------------------
# 1. MODERN UI CONFIGURATION & CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Pro B2 Exam Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a modern, clean look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 10px 10px 0px 0px;
        padding: 10px 20px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #e3f2fd;
        border-bottom: 2px solid #1976d2;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. CORE LOGIC
# -----------------------------------------------------------------------------

def get_working_model_name():
    """Finds the best available model for the user's API key."""
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not models: return None, "No models found."
        
        # Priority list
        priority = ['models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'models/gemini-pro']
        for p in priority:
            if p in models: return p, "OK"
        return models[0], "OK"
    except Exception as e:
        return None, str(e)

def extract_text_from_pdfs(uploaded_files):
    combined_text = ""
    total_pages = 0
    
    for uploaded_file in uploaded_files:
        try:
            reader = pypdf.PdfReader(uploaded_file)
            file_text = ""
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    file_text += content + "\n"
            if file_text:
                combined_text += f"\n--- SOURCE: {uploaded_file.name} ---\n{file_text}"
                total_pages += len(reader.pages)
        except:
            pass
            
    return combined_text, total_pages

def clean_json_string(json_str):
    json_str = re.sub(r'```json', '', json_str)
    json_str = re.sub(r'```', '', json_str)
    return json_str.strip()

def analyze_with_ai(api_key, text):
    genai.configure(api_key=api_key)
    model_name, status = get_working_model_name()
    
    if not model_name:
        return None, f"API Error: {status}"
        
    model = genai.GenerativeModel(model_name)
    
    # Updated Prompt for Exercise Extraction
    prompt = f"""
    Role: Senior German B2 Exam Tutor (Goethe/Telc).
    Task: deeply analyze the provided text.
    
    REQUIREMENTS:
    1. Identify the section (Reading, Listening, Writing, Speaking).
    2. Extract specific **Exercises** found in the text.
    3. If answers are in the text (key), use them. If not, SOLVE the exercise yourself.
    
    OUTPUT FORMAT: Return ONLY valid JSON.
    {{
        "Lesen": {{
            "Stats": "e.g., 2 Texts analyzed",
            "CheatSheet": "markdown bullets of vocab",
            "Mnemonics": "strategy string",
            "Traps": "common mistakes",
            "Exercises": [
                {{ "Question": "Brief context or question text", "Answer": "The correct answer with brief explanation" }},
                {{ "Question": "...", "Answer": "..." }}
            ]
        }},
        "Hören": {{ ... same structure ... }},
        "Schreiben": {{ ... same structure ... }},
        "Sprechen": {{ ... same structure ... }}
    }}
    
    INPUT TEXT (Truncated for context):
    {text[:30000]}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e:
        return None, str(e)

# -----------------------------------------------------------------------------
# 3. UI LAYOUT
# -----------------------------------------------------------------------------

def main():
    # --- SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Settings")
        api_key = st.text_input("Google API Key", type="password", help="Get one from aistudio.google.com")
        st.divider()
        st.info("💡 **Tip:** Upload chapters or single practice tests for the best extraction accuracy.")
        st.caption("v2.0 | Modern UI Edition")

    # --- MAIN HEADER ---
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🇩🇪 Pro B2 Exam Tutor")
        st.markdown("**AI-Powered Analysis, Strategy & Exercise Solver**")
    with col2:
        st.image("https://img.icons8.com/color/96/germany.png", width=60)

    # --- UPLOAD SECTION ---
    uploaded_files = st.file_uploader("", type="pdf", accept_multiple_files=True, help="Drop your B2 PDFs here")

    if uploaded_files and api_key:
        if st.button("🚀 Analyze & Solve", use_container_width=True, type="primary"):
            
            with st.status("Processing documents...", expanded=True) as status:
                st.write("📂 Reading PDFs...")
                raw_text, page_count = extract_text_from_pdfs(uploaded_files)
                
                if page_count > 0:
                    st.write("🧠 Consulting AI Tutor...")
                    json_str, error = analyze_with_ai(api_key, raw_text)
                    
                    if error:
                        status.update(label="Error!", state="error")
                        st.error(error)
                    else:
                        try:
                            data = json.loads(clean_json_string(json_str))
                            status.update(label="Analysis Complete!", state="complete")
                            
                            # --- RESULTS DISPLAY ---
                            st.divider()
                            
                            # Tabs
                            tabs = st.tabs(["📖 Lesen (Reading)", "🎧 Hören (Listening)", "✍️ Schreiben (Writing)", "🗣️ Sprechen (Speaking)"])
                            sections = ["Lesen", "Hören", "Schreiben", "Sprechen"]
                            
                            for i, tab in enumerate(tabs):
                                section_key = sections[i]
                                with tab:
                                    if section_key in data:
                                        content = data[section_key]
                                        
                                        # Top Info Cards
                                        c1, c2, c3 = st.columns(3)
                                        with c1: st.info(f"**Strategy:**\n{content.get('Mnemonics', 'N/A')}")
                                        with c2: st.warning(f"**Traps:**\n{content.get('Traps', 'N/A')}")
                                        with c3: st.success(f"**Focus:**\n{content.get('Stats', 'General Analysis')}")
                                        
                                        st.markdown("### 📝 Vocabulary & Phrases")
                                        with st.expander("View Cheat Sheet", expanded=False):
                                            st.markdown(content.get("CheatSheet", "No data found."))

                                        st.markdown("### 🧩 Extracted Exercises & Answers")
                                        exercises = content.get("Exercises", [])
                                        
                                        if exercises:
                                            for idx, ex in enumerate(exercises):
                                                with st.expander(f"Exercise {idx+1}: {ex.get('Question', '')[:50]}..."):
                                                    st.markdown(f"**❓ Question / Context:**\n\n{ex.get('Question', 'N/A')}")
                                                    st.divider()
                                                    st.markdown(f"**✅ Solution:**\n\n{ex.get('Answer', 'N/A')}")
                                        else:
                                            st.caption("No specific exercises detected in this section.")
                                    else:
                                        st.warning(f"No content detected for {section_key}")
                        
                        except json.JSONDecodeError:
                            st.error("The AI response was not valid JSON. Please try again with a smaller file.")
                else:
                    st.error("Could not read text from the uploaded files.")

    elif not api_key:
        st.info("👈 Please enter your Google API Key in the sidebar to start.")

if __name__ == "__main__":
    main()