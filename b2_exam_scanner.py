import streamlit as st
import google.generativeai as genai
import pypdf
import json
import re
import hashlib

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & LIQUID GLASS UI
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Ultra Exam Tutor AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Liquid Glassmorphism & Arabic Support
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Liquid Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        padding: 20px;
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.1);
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.4);
        padding: 10px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: none;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #ffffff;
        border-radius: 10px;
        color: #2c3e50;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    /* Titles and text */
    h1, h2, h3 { color: #2c3e50; font-family: 'Segoe UI', sans-serif; }
    
    /* Right-to-Left support for Arabic */
    .rtl { direction: rtl; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SESSION STATE MANAGEMENT (The Memory)
# -----------------------------------------------------------------------------
if 'library' not in st.session_state:
    st.session_state.library = {}  # Stores analyzed data: {file_id: data_dict}
if 'current_file_id' not in st.session_state:
    st.session_state.current_file_id = None

# -----------------------------------------------------------------------------
# 3. HELPER FUNCTIONS
# -----------------------------------------------------------------------------

def get_file_hash(file_bytes):
    """Creates a unique ID for a file so we don't re-analyze it."""
    return hashlib.md5(file_bytes).hexdigest()

def extract_text(uploaded_file):
    try:
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content: text += content + "\n"
        return text
    except:
        return None

def clean_json(json_str):
    json_str = re.sub(r'```json', '', json_str)
    json_str = re.sub(r'```', '', json_str)
    return json_str.strip()

def get_language_prompts(lang_code):
    """Returns UI text and AI prompts based on selected language."""
    prompts = {
        "English": {
            "role": "You are a strict Exam Tutor. Output answers in English where appropriate.",
            "ui_upload": "Upload PDF Exams",
            "ui_analyze": "Analyze File",
            "tabs": ["📖 Reading", "🎧 Listening", "✍️ Writing", "🗣️ Speaking", "🧩 Grammar"],
            "keys": ["Reading", "Listening", "Writing", "Speaking", "Grammar"]
        },
        "Deutsch": {
            "role": "Du bist ein strenger Deutschlehrer. Antworte auf Deutsch.",
            "ui_upload": "PDF-Prüfungen hochladen",
            "ui_analyze": "Datei analysieren",
            "tabs": ["📖 Lesen", "🎧 Hören", "✍️ Schreiben", "🗣️ Sprechen", "🧩 Grammatik"],
            "keys": ["Reading", "Listening", "Writing", "Speaking", "Grammar"]
        },
        "Français": {
            "role": "Tu es un professeur expert. Réponds en français.",
            "ui_upload": "Télécharger des examens PDF",
            "ui_analyze": "Analyser le fichier",
            "tabs": ["📖 Lecture", "🎧 Écoute", "✍️ Écriture", "🗣️ Oral", "🧩 Grammaire"],
            "keys": ["Reading", "Listening", "Writing", "Speaking", "Grammar"]
        },
        "العربية": {
            "role": "أنت معلم خبير للامتحانات. اشرح وقدم الإجابات باللغة العربية.",
            "ui_upload": "تحميل ملفات PDF",
            "ui_analyze": "تحليل الملف",
            "tabs": ["📖 القراءة", "🎧 الاستماع", "✍️ الكتابة", "🗣️ التحدث", "🧩 القواعد"],
            "keys": ["Reading", "Listening", "Writing", "Speaking", "Grammar"]
        }
    }
    return prompts.get(lang_code, prompts["English"])

def analyze_single_file(api_key, text, lang_config, lang_name):
    """Deep analysis of a single file."""
    genai.configure(api_key=api_key)
    
    # Smart Model Selection
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        model = genai.GenerativeModel(model_name)
    except:
        return None, "API Connection Failed. Check Key."

    # The Prompt
    prompt = f"""
    {lang_config['role']}
    Target Language for Explanations: {lang_name}
    
    TASK: Analyze the provided text (Exam PDF) and extract exercises, vocab, and strategies.
    Distinguish between Reading, Listening, Writing, Speaking, and Grammar sections.

    OUTPUT: Returns ONLY valid JSON with this exact structure:
    {{
        "Reading": {{ "Summary": "text", "Vocab": ["word - definition"], "Exercises": [{{ "Q": "Question text", "A": "Answer text", "Tip": "Strategy tip" }}] }},
        "Listening": {{ "Summary": "text", "Vocab": [], "Exercises": [{{ "Q": "...", "A": "...", "Tip": "..." }}] }},
        "Writing": {{ "Summary": "text", "Vocab": [], "Exercises": [{{ "Q": "Topic...", "A": "Sample Answer...", "Tip": "Structure tip" }}] }},
        "Speaking": {{ "Summary": "text", "Vocab": [], "Exercises": [{{ "Q": "Topic...", "A": "Key points...", "Tip": "..." }}] }},
        "Grammar": {{ "Summary": "text", "Topics": ["Topic 1", "Topic 2"], "Exercises": [{{ "Q": "Fill in blank...", "A": "Correct answer", "Tip": "Rule explanation" }}] }}
    }}

    If a section is missing in the text, leave the arrays empty but keep the keys.
    Analyze the following text (truncated to 30k chars):
    {text[:30000]}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e:
        return None, str(e)

# -----------------------------------------------------------------------------
# 4. MAIN APPLICATION
# -----------------------------------------------------------------------------

def main():
    # --- Sidebar Configuration ---
    with st.sidebar:
        st.image("https://img.icons8.com/3d-fluency/94/brain.png", width=80)
        st.title("Ultra Tutor AI")
        
        # Language Selector
        selected_lang = st.selectbox("Interface Language / Sprache / اللغة", 
                                     ["English", "Deutsch", "Français", "العربية"])
        
        config = get_language_prompts(selected_lang)
        is_rtl = selected_lang == "العربية"
        
        # API Key
        api_key = st.text_input("Google API Key", type="password")
        
        st.markdown("---")
        
        # File Uploader
        uploaded_files = st.file_uploader(config["ui_upload"], type="pdf", accept_multiple_files=True)
        
        # Processing Logic
        if uploaded_files and api_key:
            if st.button(config["ui_analyze"], type="primary", use_container_width=True):
                with st.spinner("Processing... / Verarbeite... / جاري المعالجة..."):
                    for up_file in uploaded_files:
                        # 1. Read File
                        file_bytes = up_file.getvalue()
                        file_hash = get_file_hash(file_bytes)
                        
                        # Only process if not already in library
                        if file_hash not in st.session_state.library:
                            text = extract_text(up_file)
                            if text:
                                json_res, err = analyze_single_file(api_key, text, config, selected_lang)
                                if json_res:
                                    try:
                                        data = json.loads(clean_json(json_res))
                                        # Save to Library
                                        st.session_state.library[file_hash] = {
                                            "name": up_file.name,
                                            "data": data,
                                            "lang": selected_lang
                                        }
                                    except:
                                        st.error(f"Failed to parse {up_file.name}")
                    st.success(f"Library Updated! {len(st.session_state.library)} Files ready.")

    # --- Main Content Area ---
    
    # 1. Library Grid (If no file selected or just landing)
    if not st.session_state.library:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 50px;">
            <h2 style='font-size: 30px;'>👋 Welcome to Ultra Tutor</h2>
            <p style='color: #666;'>Upload your PDF Exams to create an interactive study hub.</p>
            <p style='color: #888; font-size: 0.9em;'>Supports Goethe, Telc, DALF, TOEFL and more.</p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # File Selector (The "Organizer")
        file_options = {v['name']: k for k, v in st.session_state.library.items()}
        selected_name = st.selectbox("📚 Select Document / Wähle ein Dokument / اختر ملف", list(file_options.keys()))
        
        if selected_name:
            file_id = file_options[selected_name]
            file_data = st.session_state.library[file_id]["data"]
            
            st.markdown(f"<div class='glass-card'><h2>📄 {selected_name}</h2></div>", unsafe_allow_html=True)
            
            # Display Tabs
            tabs = st.tabs(config["tabs"])
            keys = config["keys"] # Reading, Listening, etc.
            
            for i, tab in enumerate(tabs):
                section_key = keys[i]
                with tab:
                    if section_key in file_data:
                        sec_content = file_data[section_key]
                        
                        # Summary Section
                        st.markdown(f"""
                        <div class="glass-card" {'class="rtl"' if is_rtl else ''}>
                            <h4 style="margin-top:0;">📌 Summary / Überblick / ملخص</h4>
                            {sec_content.get('Summary', 'No summary available.')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Vocab Section
                        vocab = sec_content.get("Vocab", [])
                        if vocab:
                            with st.expander("📝 Vocabulary List / Wortschatz / المفردات"):
                                for v in vocab:
                                    st.markdown(f"- {v}")
                        
                        # Interactive Exercises
                        exercises = sec_content.get("Exercises", [])
                        if exercises:
                            st.subheader("🧩 Exercises / Übungen / التمارين")
                            for idx, ex in enumerate(exercises):
                                # Using container for visual separation
                                with st.container():
                                    st.markdown(f"**Q{idx+1}:** {ex.get('Q', '')}")
                                    
                                    # Tip Toggle
                                    if 'Tip' in ex and ex['Tip']:
                                        if st.toggle(f"💡 Hint/Tipp {idx+1}", key=f"tip_{file_id}_{section_key}_{idx}"):
                                            st.info(ex['Tip'])
                                            
                                    # Answer Toggle
                                    if st.button(f"👁️ Reveal Answer {idx+1}", key=f"ans_{file_id}_{section_key}_{idx}"):
                                        st.success(f"✅ {ex.get('A', '')}")
                                    
                                    st.divider()
                        else:
                            st.info("No specific exercises detected for this section.")
                    else:
                        st.warning("No data found for this section.")

if __name__ == "__main__":
    main()