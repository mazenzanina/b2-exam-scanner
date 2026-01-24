import streamlit as st
import google.generativeai as genai
import pypdf
import json
import re
import hashlib
import time

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Universal AI Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# 2. MODERN "LIQUID CRYSTAL" UI (CSS)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    /* 1. THE MODERN BACKGROUND (Fixed Gradient) */
    .stApp {
        background: #C9D6FF;  /* Fallback */
        background: -webkit-linear-gradient(to right, #E2E2E2, #C9D6FF);  /* Chrome 10-25, Safari 5.1-6 */
        background: linear-gradient(to right, #E2E2E2, #C9D6FF); /* W3C, IE 10+/ Edge, Firefox 16+, Chrome 26+, Opera 12+, Safari 7+ */
    }

    /* 2. THE GLASS CARD (Container for content) */
    .glass-card {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 30px;
        margin-bottom: 25px;
        transition: transform 0.2s;
    }
    .glass-card:hover {
        transform: translateY(-2px);
    }

    /* 3. TEXT READABILITY ENFORCER */
    /* This ensures text inside cards is ALWAYS Dark Grey, regardless of system Dark Mode */
    .glass-card h1, .glass-card h2, .glass-card h3, .glass-card h4, 
    .glass-card p, .glass-card li, .glass-card span, .glass-card div {
        color: #2D3748 !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 4. MODERN BUTTON STYLING */
    div.stButton > button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 50px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(50, 50, 93, 0.11), 0 1px 3px rgba(0, 0, 0, 0.08);
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #182848 0%, #4b6cb7 100%);
        transform: translateY(-2px);
        box-shadow: 0 7px 14px rgba(50, 50, 93, 0.1), 0 3px 6px rgba(0, 0, 0, 0.08);
        color: white;
    }
    div.stButton > button:active {
        transform: translateY(1px);
    }

    /* 5. UPLOAD AREA STYLING */
    [data-testid="stFileUploader"] {
        background-color: rgba(255,255,255,0.8);
        border-radius: 20px;
        padding: 20px;
        border: 2px dashed #a0aec0;
    }
    
    /* 6. TABS STYLING */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.8);
        border-radius: 50px;
        padding: 8px;
        gap: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border: none;
        border-radius: 30px;
        background-color: transparent;
        color: #4a5568;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #2b6cb0;
        color: white !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    /* 7. CHAT BUBBLES */
    .stChatMessage {
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        color: #1a202c;
    }
    
    /* RTL Support */
    .rtl { direction: rtl; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. CORE LOGIC & STATE
# -----------------------------------------------------------------------------
if 'library' not in st.session_state: st.session_state.library = {} 

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
            "sys_prompt": "You are a Universal AI Assistant. Analyze text context (Study, Work, Travel?). Answer in English.",
            "ui_desc": "Upload Documents (PDF)",
            "tabs": ["📊 Overview", "💡 Insights", "✅ Action Items", "💬 Chat"],
            "chat_welcome": "Document loaded. Ask me anything!"
        },
        "Deutsch": {
            "sys_prompt": "Du bist ein universeller KI-Assistent. Analysiere den Kontext. Antworte auf Deutsch.",
            "ui_desc": "Dokumente hochladen (PDF)",
            "tabs": ["📊 Überblick", "💡 Erkenntnisse", "✅ Aufgaben", "💬 Chat"],
            "chat_welcome": "Dokument geladen. Frag mich etwas!"
        },
        "Français": {
            "sys_prompt": "Tu es un assistant IA. Analyse le contexte. Réponds en français.",
            "ui_desc": "Télécharger des documents (PDF)",
            "tabs": ["📊 Aperçu", "💡 Idées", "✅ Actions", "💬 Chat"],
            "chat_welcome": "Document chargé. Posez une question !"
        },
        "العربية": {
            "sys_prompt": "أنت مساعد ذكي. حلل السياق. أجب باللغة العربية.",
            "ui_desc": "تحميل الملفات (PDF)",
            "tabs": ["📊 نظرة عامة", "💡 أفكار", "✅ مهام", "💬 محادثة"],
            "chat_welcome": "تم تحميل الملف. اسألني أي شيء!"
        }
    }
    return conf.get(lang_code, conf["English"])

def analyze_content(api_key, text, sys_prompt):
    genai.configure(api_key=api_key)
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        {sys_prompt}
        TASK: Identify category (Study, Work, Novel, Travel, etc.). Extract structured data.
        OUTPUT JSON:
        {{
            "Category": "Short Category Name",
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
    msgs = [{"role": "user", "parts": [f"System: {sys_prompt}. Context: {context[:20000]}"]}]
    for m in history:
        msgs.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})
    msgs.append({"role": "user", "parts": [question]})
    try: return model.generate_content(msgs).text
    except: return "Connection error."

# -----------------------------------------------------------------------------
# 4. MAIN UI
# -----------------------------------------------------------------------------
def main():
    
    # -- TOP BAR --
    c1, c2 = st.columns([4, 1])
    with c1: 
        st.markdown("<h1 style='color: #1a202c;'>🧠 Universal AI Brain</h1>", unsafe_allow_html=True)
    with c2: 
        lang = st.selectbox("", ["English", "Deutsch", "Français", "العربية"], label_visibility="collapsed")
    
    config = get_prompts(lang)
    is_rtl = lang == "العربية"
    
    # -- SETTINGS --
    with st.expander("🔐 AI Settings (Click to Open)", expanded=False):
        api_key = st.text_input("Enter Google API Key", type="password")

    # -- UPLOAD SECTION --
    st.markdown(f"### {config['ui_desc']}")
    uploaded_files = st.file_uploader("", type=["pdf"], accept_multiple_files=True)
    
    # -- ACTION BUTTON --
    if uploaded_files and api_key:
        if st.button("✨ Analyze Files", use_container_width=True):
            
            # THE "SHOW" (Visual Process)
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            with st.spinner("Initializing Neural Core..."):
                processed = 0
                total_files = len(uploaded_files)
                
                for idx, up_file in enumerate(uploaded_files):
                    f_hash = get_file_hash(up_file.getvalue())
                    
                    if f_hash not in st.session_state.library:
                        # Step 1: Read
                        status_text.markdown(f"**📄 Reading file: {up_file.name}...**")
                        txt = extract_text(up_file)
                        progress_bar.progress((idx * 30) // total_files + 10)
                        
                        if txt:
                            # Step 2: AI Thinking
                            status_text.markdown(f"**🧠 AI is Analyzing Context & Category...**")
                            json_res = analyze_content(api_key, txt, config["sys_prompt"])
                            progress_bar.progress((idx * 70) // total_files + 30)
                            
                            # Step 3: Extracting
                            status_text.markdown(f"**💡 Extracting Insights...**")
                            if json_res:
                                data = clean_json(json_res)
                                if data:
                                    st.session_state.library[f_hash] = {
                                        "name": up_file.name, "data": data, 
                                        "text": txt, "chat_history": []
                                    }
                                    processed += 1
                                    
                progress_bar.progress(100)
                status_text.success("✅ Analysis Complete!")
                time.sleep(1)
                st.rerun()

    st.markdown("---")

    # -- RESULTS LIBRARY --
    if not st.session_state.library:
        st.info("👋 Ready to process. Upload a file above.")
    
    else:
        file_map = {v['name']: k for k, v in st.session_state.library.items()}
        selected_name = st.selectbox("📂 Select Document", list(file_map.keys()))
        
        if selected_name:
            fid = file_map[selected_name]
            f_obj = st.session_state.library[fid]
            data = f_obj["data"]
            cat = data.get("Category", "General")
            
            # HEADER CARD
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="background:#4b6cb7; color:white; padding:5px 15px; border-radius:20px; font-size:0.85em; font-weight:bold;">{cat.upper()}</span>
                </div>
                <h2 style="margin-top:15px; margin-bottom:10px;">{data['Overview'].get('Title', f_obj['name'])}</h2>
                <p style="font-size:1.1em; opacity:0.8; line-height:1.6;">{data['Overview'].get('Summary', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # TABS
            t1, t2, t3, t4 = st.tabs(config["tabs"])
            
            # TAB 1: OVERVIEW
            with t1:
                st.markdown(f"<div class='glass-card' {'class=rtl' if is_rtl else ''}>", unsafe_allow_html=True)
                st.subheader("🏷️ Tags")
                tags = data['Overview'].get("Tags", [])
                st.markdown(" ".join([f"`{t}`" for t in tags]) if tags else "No tags")
                st.markdown("</div>", unsafe_allow_html=True)

            # TAB 2: INSIGHTS
            with t2:
                st.markdown(f"<div class='glass-card' {'class=rtl' if is_rtl else ''}>", unsafe_allow_html=True)
                st.subheader("💡 Key Insights")
                for p in data.get("Insights", []): 
                    st.markdown(f"**•** {p}")
                st.markdown("</div>", unsafe_allow_html=True)

            # TAB 3: ACTION / QUIZ
            with t3:
                act = data.get("Actionable", {})
                
                # To-Do List
                if act.get("Items"):
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    st.subheader("📝 Action Items")
                    for item in act["Items"]: 
                        st.checkbox(item, key=f"{fid}_{item}")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Quiz
                if act.get("Quiz"):
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    st.subheader("🧠 Quiz / Knowledge Check")
                    for i, q in enumerate(act["Quiz"]):
                        with st.expander(f"Q{i+1}: {q.get('Q','?')}"): 
                            st.info(f"Answer: {q.get('A','')}")
                    st.markdown("</div>", unsafe_allow_html=True)

            # TAB 4: CHAT
            with t4:
                st.markdown(f"*{config['chat_welcome']}*")
                for m in f_obj["chat_history"]:
                    with st.chat_message(m["role"]): st.write(m["content"])
                
                if prompt := st.chat_input("Type your question..."):
                    f_obj["chat_history"].append({"role": "user", "content": prompt})
                    with st.chat_message("user"): st.write(prompt)
                    
                    with st.spinner("AI Thinking..."):
                        reply = ask_chat(api_key, f_obj["chat_history"], f_obj["text"], prompt, config["sys_prompt"])
                    
                    f_obj["chat_history"].append({"role": "assistant", "content": reply})
                    with st.chat_message("assistant"): st.write(reply)
                    time.sleep(0.1)
                    st.rerun()

            st.divider()
            if st.button("🗑️ Clear Library", type="secondary"):
                st.session_state.library = {}
                st.rerun()

if __name__ == "__main__":
    main()