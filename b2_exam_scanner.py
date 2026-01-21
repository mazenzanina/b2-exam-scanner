import streamlit as st
import google.generativeai as genai
import pypdf
import json
import re
import hashlib
import time

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & HIGH-CONTRAST CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Universal AI Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS FIXES FOR DARK MODE & CONTRAST
st.markdown("""
    <style>
    /* 1. Force a Light Theme Background for Consistency */
    .stApp {
        background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
        background-attachment: fixed;
    }
    
    /* 2. Glass Card - High Contrast Enforced */
    .glass-card {
        background: rgba(255, 255, 255, 0.95); /* High opacity */
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 1);
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        padding: 30px;
        margin-bottom: 25px;
    }
    
    /* 3. Aggressive Text Coloring (Overrides Dark Mode Defaults) */
    .glass-card h1, .glass-card h2, .glass-card h3, 
    .glass-card h4, .glass-card h5, .glass-card p, 
    .glass-card li, .glass-card span, .glass-card div {
        color: #1a202c !important; /* Always Dark Grey/Black */
        text-shadow: none !important;
    }
    
    /* 4. Upload Area Styling */
    [data-testid="stFileUploader"] {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        border: 2px dashed #cbd5e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    [data-testid="stFileUploader"] section {
        background-color: transparent !important;
    }
    [data-testid="stFileUploader"] span {
        color: #4a5568 !important;
    }

    /* 5. Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 10px;
        border-radius: 50px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 20px;
        border: none;
        font-weight: 700;
        color: #718096;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #2b6cb0;
        color: white !important;
    }
    
    /* 6. Chat Bubbles */
    .stChatMessage {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        color: #2d3748;
    }

    /* Arabic Support */
    .rtl { direction: rtl; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. STATE MANAGEMENT
# -----------------------------------------------------------------------------
if 'library' not in st.session_state: st.session_state.library = {} 

# -----------------------------------------------------------------------------
# 3. CORE LOGIC
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
    conf = {
        "English": {
            "sys_prompt": "You are a Universal AI Assistant. Analyze the text context (is it a Book, Travel Plan, Meeting Note, Study Material?). Answer in English.",
            "ui_desc": "Universal Brain: Upload anything (Books, Travel, Work).",
            "tabs": ["📊 Overview", "💡 Insights", "✅ Action/Quiz", "💬 Chat"],
            "chat_welcome": "I have analyzed your file. Ask me about details!"
        },
        "Deutsch": {
            "sys_prompt": "Du bist ein universeller KI-Assistent. Analysiere den Kontext (Buch, Reise, Arbeit?). Antworte auf Deutsch.",
            "ui_desc": "Universal Brain: Lade alles hoch (Bücher, Reisen, Arbeit).",
            "tabs": ["📊 Überblick", "💡 Erkenntnisse", "✅ Aufgaben", "💬 Chat"],
            "chat_welcome": "Datei analysiert. Frag mich nach Details!"
        },
        "Français": {
            "sys_prompt": "Tu es un assistant IA universel. Analyse le contexte. Réponds en français.",
            "ui_desc": "Cerveau Universel: Téléchargez tout (Livres, Voyage, Travail).",
            "tabs": ["📊 Aperçu", "💡 Idées", "✅ Actions", "💬 Chat"],
            "chat_welcome": "Fichier analysé. Posez-moi des questions !"
        },
        "العربية": {
            "sys_prompt": "أنت مساعد ذكي عالمي. حلل السياق (كتاب، سفر، عمل؟). أجب باللغة العربية.",
            "ui_desc": "العقل الشامل: قم بتحميل أي شيء (كتب، سفر، عمل).",
            "tabs": ["📊 نظرة عامة", "💡 أفكار", "✅ مهام", "💬 محادثة"],
            "chat_welcome": "تم تحليل الملف. اسألني عن التفاصيل!"
        }
    }
    return conf.get(lang_code, conf["English"])

def analyze_universal_content(api_key, text, sys_prompt):
    genai.configure(api_key=api_key)
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        {sys_prompt}
        TASK: Identify category (Study, Work, Novel, Travel, Receipt, etc.). Extract key data.
        OUTPUT JSON:
        {{
            "Category": "Category Name",
            "Overview": {{ "Title": "Txt", "Summary": "Txt", "Tags": ["Tag1", "Tag2"] }},
            "Insights": ["Point 1", "Point 2", "Point 3"],
            "Actionable": {{ "Items": ["To-Do 1"], "Quiz": [ {{"Q": "Txt", "A": "Txt"}} ] }}
        }}
        TEXT: {text[:30000]}
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
# 4. MAIN APP UI
# -----------------------------------------------------------------------------
def main():
    
    # Header
    c1, c2 = st.columns([3, 1])
    with c1: st.title("🧠 Universal AI Brain")
    with c2: lang = st.selectbox("", ["English", "Deutsch", "Français", "العربية"], label_visibility="collapsed")
    
    config = get_prompts(lang)
    is_rtl = lang == "العربية"
    
    with st.expander("🔑 AI Settings (API Key)", expanded=False):
        api_key = st.text_input("Google API Key", type="password")

    # UPLOAD AREA
    st.markdown(f"### {config['ui_desc']}")
    uploaded_files = st.file_uploader("", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files and api_key:
        if st.button("✨ Analyze Content", type="primary", use_container_width=True):
            
            # --- THE "SHOW" (Visual Processing Steps) ---
            with st.status("🧠 Neural Network Active...", expanded=True) as status:
                processed = 0
                for up_file in uploaded_files:
                    f_hash = get_file_hash(up_file.getvalue())
                    if f_hash not in st.session_state.library:
                        
                        st.write(f"📂 Reading **{up_file.name}**...")
                        txt = extract_text(up_file)
                        time.sleep(0.5) # User Experience Pause
                        
                        if txt:
                            st.write("🔍 Detecting Document Type & Context...")
                            json_res = analyze_universal_content(api_key, txt, config["sys_prompt"])
                            
                            st.write("💡 Extracting Key Insights & Action Items...")
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
                    status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
                    time.sleep(1)
                    st.rerun()
                else:
                    status.update(label="⚠️ No new files or empty content.", state="error")

    st.markdown("---")

    # LIBRARY & RESULTS
    if not st.session_state.library:
        st.info("👋 Upload a file to see the magic happen.")
    else:
        file_map = {v['name']: k for k, v in st.session_state.library.items()}
        selected_name = st.selectbox("📂 Select File", list(file_map.keys()))
        
        if selected_name:
            fid = file_map[selected_name]
            f_obj = st.session_state.library[fid]
            data = f_obj["data"]
            cat = data.get("Category", "General")
            
            # RESULT CARD
            st.markdown(f"""
            <div class="glass-card">
                <span style="background:#2d3748; color:white; padding:5px 12px; border-radius:15px; font-size:0.8em; font-weight:bold;">{cat.upper()}</span>
                <h2 style="margin-top:15px;">{data['Overview'].get('Title', f_obj['name'])}</h2>
                <p style="font-size:1.1em; opacity:0.8;">{data['Overview'].get('Summary', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # TABS
            t1, t2, t3, t4 = st.tabs(config["tabs"])
            
            with t1: # Overview
                st.markdown(f"<div class='glass-card' {'class=rtl' if is_rtl else ''}>", unsafe_allow_html=True)
                st.subheader("🏷️ Tags")
                tags = data['Overview'].get("Tags", [])
                st.write(" • ".join(tags) if tags else "No tags")
                st.markdown("</div>", unsafe_allow_html=True)

            with t2: # Insights
                st.markdown(f"<div class='glass-card' {'class=rtl' if is_rtl else ''}>", unsafe_allow_html=True)
                for p in data.get("Insights", []): st.markdown(f"**•** {p}")
                st.markdown("</div>", unsafe_allow_html=True)

            with t3: # Actions
                act = data.get("Actionable", {})
                if act.get("Items"):
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    st.subheader("📝 Action Items")
                    for item in act["Items"]: st.checkbox(item, key=f"{fid}_{item}")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                if act.get("Quiz"):
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    st.subheader("🧠 Knowledge Check")
                    for i, q in enumerate(act["Quiz"]):
                        with st.expander(f"Q{i+1}: {q['Q']}"): st.write(f"**Answer:** {q['A']}")
                    st.markdown("</div>", unsafe_allow_html=True)

            with t4: # Chat
                st.markdown(f"*{config['chat_welcome']}*")
                for m in f_obj["chat_history"]:
                    with st.chat_message(m["role"]): st.write(m["content"])
                
                if prompt := st.chat_input("Ask..."):
                    f_obj["chat_history"].append({"role": "user", "content": prompt})
                    with st.chat_message("user"): st.write(prompt)
                    with st.spinner("Thinking..."):
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