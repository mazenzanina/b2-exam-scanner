import streamlit as st
import google.generativeai as genai
import pypdf
import json
import re
import hashlib
import time

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & UNIVERSAL STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Universal AI Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed" # Sidebar hidden by default for cleaner look
)

# MODERN LIQUID UI CSS
st.markdown("""
    <style>
    /* Background */
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
    }
    
    /* The "Glass" Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.90);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        padding: 30px;
        margin-bottom: 25px;
        color: #1a202c !important;
    }
    
    /* Text Styling */
    h1, h2, h3, h4, p, li { color: #2d3748 !important; font-family: 'Segoe UI', sans-serif; }
    
    /* Upload Area Styling */
    [data-testid="stFileUploader"] {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        text-align: center;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: white;
        padding: 10px;
        border-radius: 50px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 20px;
        border: none;
        font-weight: 600;
        padding: 8px 20px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #2d3748;
        color: white !important;
    }
    
    /* Chat Bubbles */
    .stChatMessage { background: white; border-radius: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
    
    /* Arabic Support */
    .rtl { direction: rtl; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. STATE MANAGEMENT
# -----------------------------------------------------------------------------
if 'library' not in st.session_state: st.session_state.library = {} 

# -----------------------------------------------------------------------------
# 3. CORE FUNCTIONS
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
        return text if len(text) > 20 else None
    except: return None

def clean_json(json_str):
    try:
        json_str = re.sub(r'```json', '', json_str)
        json_str = re.sub(r'```', '', json_str)
        return json.loads(json_str.strip())
    except: return None

def get_prompts(lang_code):
    """Adapts the interface and AI personality based on language."""
    conf = {
        "English": {
            "sys_prompt": "You are a Universal AI Assistant. Analyze the text context (is it a Book, Travel Plan, Meeting Note, Study Material?). Answer in English.",
            "ui_title": "Universal Brain AI",
            "ui_desc": "Upload anything: Books, Tickets, Notes, or Exams. I will organize it.",
            "tabs": ["📊 Overview", "💡 Key Insights", "✅ Action/Quiz", "💬 Chat"],
            "keys": ["Overview", "Insights", "Actionable"],
            "chat_welcome": "I have analyzed your file. Ask me about details, dates, or summaries!"
        },
        "Deutsch": {
            "sys_prompt": "Du bist ein universeller KI-Assistent. Analysiere den Kontext (Buch, Reise, Arbeit, Studium?). Antworte auf Deutsch.",
            "ui_title": "Universelles KI-Gehirn",
            "ui_desc": "Lade alles hoch: Bücher, Tickets, Notizen oder Prüfungen. Ich organisiere es.",
            "tabs": ["📊 Überblick", "💡 Erkenntnisse", "✅ Aufgaben/Quiz", "💬 Chat"],
            "keys": ["Overview", "Insights", "Actionable"],
            "chat_welcome": "Datei analysiert. Frag mich nach Details oder Zusammenfassungen!"
        },
        "Français": {
            "sys_prompt": "Tu es un assistant IA universel. Analyse le contexte (Livre, Voyage, Travail?). Réponds en français.",
            "ui_title": "Cerveau IA Universel",
            "ui_desc": "Téléchargez tout : Livres, Billets, Notes. J'organise tout.",
            "tabs": ["📊 Aperçu", "💡 Idées Clés", "✅ Actions/Quiz", "💬 Chat"],
            "keys": ["Overview", "Insights", "Actionable"],
            "chat_welcome": "Fichier analysé. Posez-moi des questions !"
        },
        "العربية": {
            "sys_prompt": "أنت مساعد ذكي عالمي. حلل السياق (كتاب، سفر، عمل، دراسة؟). أجب باللغة العربية.",
            "ui_title": "العقل الذكي الشامل",
            "ui_desc": "قم بتحميل أي شيء: كتب، تذاكر سفر، ملاحظات، أو اختبارات. سأقوم بتنظيمها.",
            "tabs": ["📊 نظرة عامة", "💡 أفكار رئيسية", "✅ مهام/اختبار", "💬 محادثة"],
            "keys": ["Overview", "Insights", "Actionable"],
            "chat_welcome": "تم تحليل الملف. اسألني عن التفاصيل أو التواريخ!"
        }
    }
    return conf.get(lang_code, conf["English"])

def analyze_universal_content(api_key, text, sys_prompt):
    genai.configure(api_key=api_key)
    try:
        # Find best model
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        {sys_prompt}
        
        TASK: Determine the category of the text (e.g., Study Material, Business Meeting, Novel, Travel Itinerary, Recipe, etc.).
        Then extract relevant structured data.
        
        OUTPUT JSON Structure:
        {{
            "Category": "One word category (e.g., Travel, Study, Work)",
            "Overview": {{ "Title": "Title of content", "Summary": "Brief summary", "Tags": ["Tag1", "Tag2"] }},
            "Insights": ["Key Point 1", "Key Point 2", "Key Point 3"],
            "Actionable": {{
                "Items": ["To-Do 1", "To-Do 2"], 
                "Quiz": [ {{"Q": "Question?", "A": "Answer"}} ] 
            }}
        }}
        
        Note: 
        - If it's a **Narrative/Book**: 'Actionable' items should be 'Key Themes'.
        - If it's **Travel**: 'Actionable' items should be 'Itinerary Steps'.
        - If it's **Study**: Include a 'Quiz'.
        
        TEXT CONTENT:
        {text[:30000]}
        """
        response = model.generate_content(prompt)
        return response.text
    except: return None

def ask_chat(api_key, history, context, question, sys_prompt):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    msgs = [{"role": "user", "parts": [f"System: {sys_prompt}. Context: {context[:20000]}"]}] + \
           [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in history] + \
           [{"role": "user", "parts": [question]}]
    try: return model.generate_content(msgs).text
    except: return "Connection error."

# -----------------------------------------------------------------------------
# 4. MAIN APPLICATION
# -----------------------------------------------------------------------------
def main():
    
    # --- HEADER SECTION ---
    c1, c2 = st.columns([3, 1])
    with c1:
        st.title("🧠 Universal AI Brain")
    with c2:
        lang = st.selectbox("", ["English", "Deutsch", "Français", "العربية"], label_visibility="collapsed")
    
    config = get_prompts(lang)
    is_rtl = lang == "العربية"
    
    # --- API KEY (Collapsible to save space) ---
    with st.expander("🔑 AI Settings (API Key)", expanded=False):
        api_key = st.text_input("Google API Key", type="password")
    
    # --- MAIN UPLOAD SECTION (ON HOME SCREEN) ---
    st.markdown(f"### {config['ui_desc']}")
    
    uploaded_files = st.file_uploader("", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files and api_key:
        if st.button("✨ Analyze Content", type="primary", use_container_width=True):
            with st.spinner("Reading & Organizing..."):
                processed = 0
                for up_file in uploaded_files:
                    f_hash = get_file_hash(up_file.getvalue())
                    if f_hash not in st.session_state.library:
                        txt = extract_text(up_file)
                        if txt:
                            json_res = analyze_universal_content(api_key, txt, config["sys_prompt"])
                            if json_res:
                                data = clean_json(json_res)
                                if data:
                                    st.session_state.library[f_hash] = {
                                        "name": up_file.name,
                                        "data": data,
                                        "text": txt,
                                        "chat_history": []
                                    }
                                    processed += 1
                if processed > 0:
                    st.success("Done!")
                    time.sleep(1)
                    st.rerun()

    st.markdown("---")

    # --- LIBRARY DISPLAY ---
    if not st.session_state.library:
        st.info("📂 Your library is empty. Upload a file above to start.")
    
    else:
        # File Selection Tabs (Horizontal Scroll simulation)
        file_map = {v['name']: k for k, v in st.session_state.library.items()}
        selected_name = st.selectbox("📂 Select File", list(file_map.keys()))
        
        if selected_name:
            fid = file_map[selected_name]
            f_obj = st.session_state.library[fid]
            data = f_obj["data"]
            category = data.get("Category", "General")
            
            # FILE HEADER CARD
            st.markdown(f"""
            <div class="glass-card">
                <span style="background:#e2e8f0; padding:5px 10px; border-radius:10px; font-size:0.8em; font-weight:bold; color:#4a5568;">{category.upper()}</span>
                <h2 style="margin-top:10px;">{data['Overview'].get('Title', f_obj['name'])}</h2>
                <p>{data['Overview'].get('Summary', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # TABS
            t1, t2, t3, t4 = st.tabs(config["tabs"])
            
            # 1. OVERVIEW
            with t1:
                st.markdown(f"<div class='glass-card' {'class=rtl' if is_rtl else ''}>", unsafe_allow_html=True)
                st.subheader("Tags")
                st.write(", ".join(data['Overview'].get("Tags", [])))
                st.markdown("</div>", unsafe_allow_html=True)

            # 2. INSIGHTS
            with t2:
                st.markdown(f"<div class='glass-card' {'class=rtl' if is_rtl else ''}>", unsafe_allow_html=True)
                for point in data.get("Insights", []):
                    st.markdown(f"• {point}")
                st.markdown("</div>", unsafe_allow_html=True)

            # 3. ACTION / QUIZ
            with t3:
                act = data.get("Actionable", {})
                
                # Check if it has actionable items (To-Dos)
                if act.get("Items"):
                    st.subheader("📝 Action Items / To-Do")
                    for item in act["Items"]:
                        st.checkbox(item, key=f"chk_{fid}_{item}")
                
                # Check if it has a Quiz (Study Material)
                if act.get("Quiz"):
                    st.subheader("🧠 Quiz")
                    for idx, q in enumerate(act["Quiz"]):
                        with st.expander(f"Q{idx+1}: {q['Q']}"):
                            st.markdown(f"**Answer:** {q['A']}")

            # 4. CHAT
            with t4:
                st.markdown(f"*{config['chat_welcome']}*")
                
                # Chat History
                for msg in f_obj["chat_history"]:
                    with st.chat_message(msg["role"]): st.write(msg["content"])
                
                # Chat Input
                if prompt := st.chat_input("Ask anything..."):
                    f_obj["chat_history"].append({"role": "user", "content": prompt})
                    with st.chat_message("user"): st.write(prompt)
                    
                    with st.spinner("..."):
                        reply = ask_chat(api_key, f_obj["chat_history"], f_obj["text"], prompt, config["sys_prompt"])
                    
                    f_obj["chat_history"].append({"role": "assistant", "content": reply})
                    with st.chat_message("assistant"): st.write(reply)
                    time.sleep(0.1)
                    st.rerun()
            
            st.divider()
            if st.button("🗑️ Clear Library"):
                st.session_state.library = {}
                st.rerun()

if __name__ == "__main__":
    main()