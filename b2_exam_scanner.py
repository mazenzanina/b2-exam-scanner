import streamlit as st
import google.generativeai as genai
import pypdf
import json
import re
import hashlib

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & THEME-ADAPTIVE CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Ultra Exam Tutor AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ULTRA-CONTRAST CSS
# This CSS enforces dark text inside the glass cards to ensure readability 
# regardless of whether the user is in Light Mode or Dark Mode.
st.markdown("""
    <style>
    /* Global Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* THE GLASS CARD - High Contrast Enforced */
    .glass-card {
        background: rgba(255, 255, 255, 0.85); /* More opaque for better contrast */
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        padding: 25px;
        margin-bottom: 25px;
        color: #1E1E1E !important; /* Forces Dark Text inside cards always */
    }
    
    /* Ensure headers inside glass cards are also dark */
    .glass-card h1, .glass-card h2, .glass-card h3, .glass-card h4, .glass-card h5, .glass-card p, .glass-card li {
        color: #1E1E1E !important;
    }

    /* Hover Effect */
    .glass-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
    }

    /* Tab Styling - High Visibility */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.8);
        padding: 10px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: none;
        font-weight: 700;
        color: #555;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #2b6cb0; /* Strong Blue for Active Tab */
        color: white !important;
        border-radius: 10px;
    }
    
    /* Chat Message Styling */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        border: 1px solid #ddd;
    }

    /* Arabic RTL Support */
    .rtl { direction: rtl; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SESSION STATE (MEMORY & CHAT)
# -----------------------------------------------------------------------------
if 'library' not in st.session_state:
    st.session_state.library = {}  # {file_id: {data:..., text:..., chat_history: []}}
if 'current_file_id' not in st.session_state:
    st.session_state.current_file_id = None

# -----------------------------------------------------------------------------
# 3. HELPER FUNCTIONS
# -----------------------------------------------------------------------------

def get_file_hash(file_bytes):
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

def get_language_config(lang_code):
    config = {
        "English": {
            "role": "You are a helpful Exam Tutor. Answer in English.",
            "tabs": ["📖 Reading", "🎧 Listening", "✍️ Writing", "🗣️ Speaking", "🧩 Grammar"],
            "keys": ["Reading", "Listening", "Writing", "Speaking", "Grammar"],
            "chat_placeholder": "Ask a question about this exam... (e.g. 'Explain Q3')",
            "chat_welcome": "I am your AI Study Buddy. Ask me anything about this file!"
        },
        "Deutsch": {
            "role": "Du bist ein hilfreicher Deutschlehrer. Antworte auf Deutsch.",
            "tabs": ["📖 Lesen", "🎧 Hören", "✍️ Schreiben", "🗣️ Sprechen", "🧩 Grammatik"],
            "keys": ["Reading", "Listening", "Writing", "Speaking", "Grammar"],
            "chat_placeholder": "Stelle eine Frage zu dieser Prüfung...",
            "chat_welcome": "Ich bin dein KI-Lernpartner. Frag mich alles zu diesem Dokument!"
        },
        "Français": {
            "role": "Tu es un tuteur expert. Réponds en français.",
            "tabs": ["📖 Lecture", "🎧 Écoute", "✍️ Écriture", "🗣️ Oral", "🧩 Grammaire"],
            "keys": ["Reading", "Listening", "Writing", "Speaking", "Grammar"],
            "chat_placeholder": "Posez une question sur cet examen...",
            "chat_welcome": "Je suis ton compagnon d'étude IA. Pose-moi des questions !"
        },
        "العربية": {
            "role": "أنت معلم خبير. اشرح بالعربية.",
            "tabs": ["📖 القراءة", "🎧 الاستماع", "✍️ الكتابة", "🗣️ التحدث", "🧩 القواعد"],
            "keys": ["Reading", "Listening", "Writing", "Speaking", "Grammar"],
            "chat_placeholder": "اطرح سؤالاً حول هذا الامتحان...",
            "chat_welcome": "أنا رفيقك الدراسي الذكي. اسألني أي شيء عن هذا الملف!"
        }
    }
    return config.get(lang_code, config["English"])

def analyze_pdf_structure(api_key, text, lang_config, lang_name):
    """Initial analysis to build the dashboard."""
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Target Language: {lang_name}
        Task: Analyze this Exam PDF text. Extract exercises and vocabulary.
        
        OUTPUT JSON Structure (Strict):
        {{
            "Reading": {{ "Summary": "txt", "Vocab": ["word"], "Exercises": [{{ "Q": "txt", "A": "txt", "Tip": "txt" }}] }},
            "Listening": {{ "Summary": "txt", "Vocab": [], "Exercises": [] }},
            "Writing": {{ "Summary": "txt", "Vocab": [], "Exercises": [] }},
            "Speaking": {{ "Summary": "txt", "Vocab": [], "Exercises": [] }},
            "Grammar": {{ "Summary": "txt", "Topics": [], "Exercises": [] }}
        }}
        
        Text (truncated): {text[:30000]}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return None

def ask_chat_bot(api_key, history, context_text, user_question, lang_role):
    """Handles the Chat interaction."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Construct conversation
    messages = [
        {"role": "user", "parts": [f"System Instruction: {lang_role}. Context from PDF: {context_text[:20000]}"]},
        {"role": "model", "parts": ["Understood. I am ready to help based on the PDF."]}
    ]
    
    # Add history
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        messages.append({"role": role, "parts": [msg["content"]]})
    
    # Add current question
    messages.append({"role": "user", "parts": [user_question]})
    
    try:
        response = model.generate_content(messages)
        return response.text
    except:
        return "Sorry, I lost connection. Please try again."

# -----------------------------------------------------------------------------
# 4. MAIN APP LOGIC
# -----------------------------------------------------------------------------

def main():
    # --- Sidebar ---
    with st.sidebar:
        st.image("https://img.icons8.com/3d-fluency/94/brain.png", width=60)
        st.title("Ultra Tutor AI")
        st.caption("v4.0 | Adaptive Contrast & Chat")
        
        selected_lang = st.selectbox("Language / Sprache / اللغة", ["English", "Deutsch", "Français", "العربية"])
        config = get_language_config(selected_lang)
        is_rtl = selected_lang == "العربية"
        
        api_key = st.text_input("Google API Key", type="password")
        
        st.markdown("---")
        uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
        
        if uploaded_files and api_key:
            if st.button("🚀 Analyze New Files", type="primary", use_container_width=True):
                with st.spinner("Processing..."):
                    for up_file in uploaded_files:
                        f_bytes = up_file.getvalue()
                        f_hash = get_file_hash(f_bytes)
                        if f_hash not in st.session_state.library:
                            raw_text = extract_text(up_file)
                            if raw_text:
                                json_res = analyze_pdf_structure(api_key, raw_text, config, selected_lang)
                                if json_res:
                                    try:
                                        data = json.loads(clean_json(json_res))
                                        st.session_state.library[f_hash] = {
                                            "name": up_file.name,
                                            "data": data,
                                            "text": raw_text, # Save text for Chatbot
                                            "chat_history": []
                                        }
                                    except:
                                        st.error(f"Error parsing {up_file.name}")
                    st.success("Library Updated!")

    # --- Main Area ---
    if not st.session_state.library:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 60px;">
            <h1>👋 Welcome to Ultra Tutor</h1>
            <p>Upload your B2/C1 Exams to begin.</p>
            <p style="font-size: 0.9rem; color: #555;">Fully compatible with Light & Dark Mode.</p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # File Selector
        file_map = {v['name']: k for k, v in st.session_state.library.items()}
        selected_name = st.selectbox("📚 Select Document", list(file_map.keys()))
        
        if selected_name:
            fid = file_map[selected_name]
            file_obj = st.session_state.library[fid]
            file_data = file_obj["data"]
            
            # --- DASHBOARD (Glass Card) ---
            st.markdown(f"<div class='glass-card'><h2>📄 {selected_name}</h2></div>", unsafe_allow_html=True)
            
            # --- TABS ---
            tabs = st.tabs(config["tabs"])
            keys = config["keys"]
            
            for i, tab in enumerate(tabs):
                key = keys[i]
                with tab:
                    if key in file_data:
                        content = file_data[key]
                        
                        # Summary Card
                        st.markdown(f"""
                        <div class="glass-card" {'class="rtl"' if is_rtl else ''}>
                            <h4>📌 Summary</h4>
                            {content.get('Summary', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Vocab Expander
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
                                    # Exercise Card
                                    st.markdown(f"""
                                    <div style="background: rgba(255,255,255,0.7); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #2b6cb0;">
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

            # --- AI STUDY BUDDY CHAT (Fixed at bottom) ---
            st.markdown("---")
            st.subheader("🤖 AI Study Buddy")
            
            # Display Chat History
            chat_container = st.container()
            with chat_container:
                if not file_obj["chat_history"]:
                    st.markdown(f"*{config['chat_welcome']}*")
                
                for msg in file_obj["chat_history"]:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])

            # Chat Input
            if prompt := st.chat_input(config["chat_placeholder"]):
                # 1. Show User Message
                with st.chat_message("user"):
                    st.write(prompt)
                
                # 2. Add to history
                file_obj["chat_history"].append({"role": "user", "content": prompt})
                
                # 3. Get AI Response
                with st.spinner("Thinking..."):
                    ai_reply = ask_chat_bot(api_key, file_obj["chat_history"], file_obj["text"], prompt, config["role"])
                
                # 4. Show AI Message
                with st.chat_message("assistant"):
                    st.write(ai_reply)
                
                # 5. Save to history
                file_obj["chat_history"].append({"role": "assistant", "content": ai_reply})
                
                # Force refresh to update history view
                st.rerun()

if __name__ == "__main__":
    main()