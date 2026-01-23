import streamlit as st
import google.generativeai as genai
import pypdf
import json
import re
import hashlib
import time

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & "LIQUID GLASS" CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Ultra Tutor AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* 1. Global Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* 2. Glass Card - High Contrast Logic */
    .glass-card {
        background: rgba(255, 255, 255, 0.90); /* High opacity for readability */
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
        padding: 25px;
        margin-bottom: 20px;
        color: #1a202c !important; /* Forces dark text */
    }
    
    /* 3. Force Dark Text Elements inside Glass Cards */
    .glass-card h1, .glass-card h2, .glass-card h3, .glass-card h4, .glass-card p, .glass-card li, .glass-card span {
        color: #1a202c !important; 
    }

    /* 4. Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.5);
        padding: 8px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: none;
        font-weight: 600;
        color: #4a5568;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #3182ce;
        color: white !important;
        border-radius: 8px;
    }
    
    /* 5. Chat Styling */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }

    /* 6. Arabic RTL Support */
    .rtl { direction: rtl; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SESSION STATE MANAGEMENT
# -----------------------------------------------------------------------------
if 'library' not in st.session_state:
    st.session_state.library = {} 
if 'current_file_id' not in st.session_state:
    st.session_state.current_file_id = None

# -----------------------------------------------------------------------------
# 3. ROBUST UTILITY FUNCTIONS
# -----------------------------------------------------------------------------

def get_file_hash(file_bytes):
    return hashlib.md5(file_bytes).hexdigest()

def extract_text(uploaded_file):
    """Safely extracts text from PDF."""
    try:
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content: text += content + "\n"
        return text if len(text) > 50 else None
    except Exception as e:
        return None

def clean_and_repair_json(json_str):
    """Aggressively cleans JSON to prevent crashes."""
    try:
        # Remove Markdown
        json_str = re.sub(r'```json', '', json_str)
        json_str = re.sub(r'```', '', json_str)
        json_str = json_str.strip()
        # Parse
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None

def get_language_config(lang_code):
    config = {
        "English": {
            "role": "You are a helpful Exam Tutor. Answer in English.",
            "tabs": ["📖 Reading", "🎧 Listening", "✍️ Writing", "🗣️ Speaking", "🧩 Grammar"],
            "keys": ["Reading", "Listening", "Writing", "Speaking", "Grammar"],
            "chat_placeholder": "Ask a question about this exam...",
            "chat_welcome": "I am your AI Study Buddy. Ask me anything!"
        },
        "Deutsch": {
            "role": "Du bist ein hilfreicher Deutschlehrer. Antworte auf Deutsch.",
            "tabs": ["📖 Lesen", "🎧 Hören", "✍️ Schreiben", "🗣️ Sprechen", "🧩 Grammatik"],
            "keys": ["Reading", "Listening", "Writing", "Speaking", "Grammar"],
            "chat_placeholder": "Stelle eine Frage zu dieser Prüfung...",
            "chat_welcome": "Ich bin dein KI-Lernpartner. Frag mich alles!"
        },
        "Français": {
            "role": "Tu es un tuteur expert. Réponds en français.",
            "tabs": ["📖 Lecture", "🎧 Écoute", "✍️ Écriture", "🗣️ Oral", "🧩 Grammaire"],
            "keys": ["Reading", "Listening", "Writing", "Speaking", "Grammar"],
            "chat_placeholder": "Posez une question...",
            "chat_welcome": "Je suis ton compagnon d'étude IA."
        },
        "العربية": {
            "role": "أنت معلم خبير. اشرح بالعربية.",
            "tabs": ["📖 القراءة", "🎧 الاستماع", "✍️ الكتابة", "🗣️ التحدث", "🧩 القواعد"],
            "keys": ["Reading", "Listening", "Writing", "Speaking", "Grammar"],
            "chat_placeholder": "اطرح سؤالاً حول هذا الامتحان...",
            "chat_welcome": "أنا رفيقك الدراسي الذكي."
        }
    }
    return config.get(lang_code, config["English"])

def analyze_pdf(api_key, text, lang_name):
    """Connects to Gemini and requests JSON structure."""
    genai.configure(api_key=api_key)
    try:
        # Attempt to find best model
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        Act as an expert Exam Tutor. Target Language: {lang_name}.
        Analyze the text below. Extract exercises, answers, and vocab.
        
        CRITICAL: Output must be valid JSON with this EXACT structure:
        {{
            "Reading": {{ "Summary": "txt", "Vocab": ["txt"], "Exercises": [{{ "Q": "txt", "A": "txt", "Tip": "txt" }}] }},
            "Listening": {{ "Summary": "txt", "Vocab": [], "Exercises": [] }},
            "Writing": {{ "Summary": "txt", "Vocab": [], "Exercises": [] }},
            "Speaking": {{ "Summary": "txt", "Vocab": [], "Exercises": [] }},
            "Grammar": {{ "Summary": "txt", "Topics": [], "Exercises": [] }}
        }}

        Text to analyze (truncated):
        {text[:30000]}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return None

def ask_chat_bot(api_key, history, context_text, user_question, lang_role):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    messages = [
        {"role": "user", "parts": [f"System: {lang_role}. Context: {context_text[:15000]}"]},
        {"role": "model", "parts": ["Understood."]}
    ]
    for msg in history:
        r = "user" if msg["role"] == "user" else "model"
        messages.append({"role": r, "parts": [msg["content"]]})
    
    messages.append({"role": "user", "parts": [user_question]})
    
    try:
        response = model.generate_content(messages)
        return response.text
    except:
        return "Connection Error. Please try again."

# -----------------------------------------------------------------------------
# 4. MAIN APP LOGIC
# -----------------------------------------------------------------------------
def main():
    
    # --- SIDEBAR -------------------------------------------------------------
    with st.sidebar:
        st.image("https://img.icons8.com/3d-fluency/94/brain.png", width=60)
        st.title("Ultra Tutor AI")
        st.caption("v5.0 | Stable Edition")
        
        # Controls
        selected_lang = st.selectbox("Language / Sprache / اللغة", ["English", "Deutsch", "Français", "العربية"])
        config = get_language_config(selected_lang)
        is_rtl = selected_lang == "العربية"
        
        api_key = st.text_input("Google API Key", type="password")
        
        st.markdown("---")
        
        # Uploader
        uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
        
        # ANALYZE BUTTON
        if uploaded_files and api_key:
            if st.button("🚀 Analyze Files", type="primary", use_container_width=True):
                with st.spinner("Processing... Please wait..."):
                    processed_count = 0
                    
                    for up_file in uploaded_files:
                        f_bytes = up_file.getvalue()
                        f_hash = get_file_hash(f_bytes)
                        
                        # Only process if not already in library
                        if f_hash not in st.session_state.library:
                            raw_text = extract_text(up_file)
                            if raw_text:
                                json_res = analyze_pdf(api_key, raw_text, selected_lang)
                                if json_res:
                                    data = clean_and_repair_json(json_res)
                                    if data:
                                        st.session_state.library[f_hash] = {
                                            "name": up_file.name,
                                            "data": data,
                                            "text": raw_text,
                                            "chat_history": []
                                        }
                                        processed_count += 1
                    
                    if processed_count > 0:
                        st.success("Success! Redirecting...")
                        time.sleep(1)
                        st.rerun() # <--- THE CRITICAL FIX FOR "STUCK ON FIRST PAGE"
                    else:
                        st.warning("Files already analyzed or empty.")

        st.markdown("---")
        if st.button("🗑️ Clear Library"):
            st.session_state.library = {}
            st.rerun()

    # --- MAIN CONTENT --------------------------------------------------------
    
    # 1. WELCOME SCREEN (If Empty)
    if not st.session_state.library:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 60px;">
            <h1 style="color:#2d3748;">👋 Welcome to Ultra Tutor</h1>
            <p style="font-size: 1.2rem; color: #4a5568;">Upload your Exam PDFs to start.</p>
            <div style="display: flex; justify-content: center; gap: 20px; margin-top: 20px;">
                <span style="background: #e2e8f0; padding: 5px 15px; border-radius: 20px;">🇩🇪 Goethe</span>
                <span style="background: #e2e8f0; padding: 5px 15px; border-radius: 20px;">🇫🇷 DALF</span>
                <span style="background: #e2e8f0; padding: 5px 15px; border-radius: 20px;">🇺🇸 TOEFL</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 2. DASHBOARD (If Data Exists)
    else:
        # File Selector
        file_map = {v['name']: k for k, v in st.session_state.library.items()}
        selected_name = st.selectbox("📚 Select Document", list(file_map.keys()))
        
        if selected_name:
            fid = file_map[selected_name]
            file_obj = st.session_state.library[fid]
            file_data = file_obj["data"]
            
            # Header Card
            st.markdown(f"<div class='glass-card'><h2>📄 {selected_name}</h2></div>", unsafe_allow_html=True)
            
            # Tabs
            tabs = st.tabs(config["tabs"])
            keys = config["keys"]
            
            for i, tab in enumerate(tabs):
                key = keys[i]
                with tab:
                    if key in file_data:
                        content = file_data[key]
                        
                        # Summary
                        st.markdown(f"""
                        <div class="glass-card" {'class="rtl"' if is_rtl else ''}>
                            <h4>📌 Summary</h4>
                            {content.get('Summary', 'No summary generated.')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Vocab
                        if content.get("Vocab"):
                            with st.expander(f"📝 {key} Vocabulary"):
                                for v in content["Vocab"]:
                                    st.write(f"• {v}")
                        
                        # Exercises
                        exercises = content.get("Exercises", [])
                        if exercises:
                            st.subheader("Interactive Exercises")
                            for idx, ex in enumerate(exercises):
                                with st.container():
                                    st.markdown(f"""
                                    <div style="background: rgba(255,255,255,0.6); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #3182ce; color: #1a202c;">
                                        <strong>Q{idx+1}:</strong> {ex.get('Q', '')}
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    c1, c2 = st.columns([1, 4])
                                    with c1:
                                        if st.button(f"👁️ Answer {idx+1}", key=f"ans_{fid}_{key}_{idx}"):
                                            st.success(ex.get('A', ''))
                                    with c2:
                                        if ex.get('Tip'):
                                            st.info(f"💡 {ex['Tip']}")
                        else:
                            st.info("No exercises found in this section.")

            # --- AI CHATBOT SECTION ---
            st.markdown("---")
            st.subheader("🤖 AI Study Buddy")
            
            chat_container = st.container()
            with chat_container:
                if not file_obj["chat_history"]:
                    st.markdown(f"*{config['chat_welcome']}*")
                
                for msg in file_obj["chat_history"]:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])

            if prompt := st.chat_input(config["chat_placeholder"]):
                # User Msg
                file_obj["chat_history"].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.write(prompt)
                
                # AI Msg
                with st.spinner("Thinking..."):
                    ai_reply = ask_chat_bot(api_key, file_obj["chat_history"], file_obj["text"], prompt, config["role"])
                
                file_obj["chat_history"].append({"role": "assistant", "content": ai_reply})
                with st.chat_message("assistant"):
                    st.write(ai_reply)
                
                # Rerun to update history properly
                time.sleep(0.1)
                st.rerun()

if __name__ == "__main__":
    main()