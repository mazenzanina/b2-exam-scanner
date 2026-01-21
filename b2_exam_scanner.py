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
# 2. MODERN UI (CSS)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    /* Background */
    .stApp {
        background: linear-gradient(to right, #E2E2E2, #C9D6FF);
    }

    /* Glass Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 30px;
        margin-bottom: 25px;
    }

    /* Text Color Enforcer (Dark Grey) */
    .glass-card h1, .glass-card h2, .glass-card h3, .glass-card h4, 
    .glass-card p, .glass-card li, .glass-card span, .glass-card div {
        color: #2D3748 !important; 
    }
    
    /* Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 50px;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #182848 0%, #4b6cb7 100%);
        color: white;
        transform: translateY(-2px);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.8);
        border-radius: 50px;
        padding: 8px;
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #2b6cb0;
        color: white !important;
    }
    
    .rtl { direction: rtl; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. CORE LOGIC
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

def robust_json_extractor(text):
    """
    Surgically extracts JSON object from text containing other chatty output.
    Finds the first '{' and the last '}'.
    """
    try:
        if not text: return None
        # Find start and end of JSON structure
        start = text.find('{')
        end = text.rfind('}') + 1
        
        if start == -1 or end == 0:
            return None
            
        json_str = text[start:end]
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None

def get_prompts(lang_code):
    conf = {
        "English": {
            "sys_prompt": "You are a Universal AI Assistant. Analyze text context (Study, Work, Travel?). Answer in English.",
            "ui_desc": "Upload Documents (PDF)",
            "tabs": ["📊 Overview", "💡 Insights", "✅ Action Items", "💬 Chat"],
            "chat_welcome": "Document loaded. Ask me anything!",
            "btn_label": "✨ Analyze Files"
        },
        "Deutsch": {
            "sys_prompt": "Du bist ein universeller KI-Assistent. Analysiere den Kontext. Antworte auf Deutsch.",
            "ui_desc": "Dokumente hochladen (PDF)",
            "tabs": ["📊 Überblick", "💡 Erkenntnisse", "✅ Aufgaben", "💬 Chat"],
            "chat_welcome": "Dokument geladen. Frag mich etwas!",
            "btn_label": "✨ Analysieren"
        },
        "Français": {
            "sys_prompt": "Tu es un assistant IA. Analyse le contexte. Réponds en français.",
            "ui_desc": "Télécharger des documents (PDF)",
            "tabs": ["📊 Aperçu", "💡 Idées", "✅ Actions", "💬 Chat"],
            "chat_welcome": "Document chargé. Posez une question !",
            "btn_label": "✨ Analyser"
        },
        "العربية": {
            "sys_prompt": "أنت مساعد ذكي. حلل السياق. أجب باللغة العربية.",
            "ui_desc": "تحميل الملفات (PDF)",
            "tabs": ["📊 نظرة عامة", "💡 أفكار", "✅ مهام", "💬 محادثة"],
            "chat_welcome": "تم تحميل الملف. اسألني أي شيء!",
            "btn_label": "✨ تحليل الملفات"
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
        
        CRITICAL: Return ONLY valid JSON. No markdown formatting.
        
        OUTPUT FORMAT:
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
    except Exception as e:
        return f"API_ERROR: {str(e)}"

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
    with st.expander("🔐 AI Settings (API Key)", expanded=False):
        api_key = st.text_input("Enter Google API Key", type="password")

    # -- UPLOAD --
    st.markdown(f"### {config['ui_desc']}")
    uploaded_files = st.file_uploader("", type=["pdf"], accept_multiple_files=True)
    
    # -- ANALYZE BUTTON --
    if uploaded_files and api_key:
        if st.button(config["btn_label"], use_container_width=True):
            
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            processed_count = 0
            errors = []
            
            with st.spinner("Initializing Neural Core..."):
                total_files = len(uploaded_files)
                
                for idx, up_file in enumerate(uploaded_files):
                    f_hash = get_file_hash(up_file.getvalue())
                    
                    if f_hash not in st.session_state.library:
                        status_text.markdown(f"**📄 Reading file: {up_file.name}...**")
                        txt = extract_text(up_file)
                        progress_bar.progress((idx * 30) // total_files + 10)
                        
                        if txt:
                            status_text.markdown(f"**🧠 Analyzing: {up_file.name}...**")
                            raw_response = analyze_content(api_key, txt, config["sys_prompt"])
                            progress_bar.progress((idx * 70) // total_files + 30)
                            
                            if raw_response and "API_ERROR" not in raw_response:
                                data = robust_json_extractor(raw_response)
                                if data:
                                    st.session_state.library[f_hash] = {
                                        "name": up_file.name, "data": data, 
                                        "text": txt, "chat_history": []
                                    }
                                    processed_count += 1
                                else:
                                    errors.append(f"JSON Parse Error in {up_file.name}. Raw Output: {raw_response[:100]}...")
                            else:
                                errors.append(f"API Error in {up_file.name}: {raw_response}")
                        else:
                            errors.append(f"Could not read text from {up_file.name}")
                    else:
                        processed_count += 1 # Already exists, count as success
                        
                progress_bar.progress(100)
                
                if processed_count > 0:
                    status_text.success(f"✅ Analysis Complete! {processed_count} files ready.")
                    time.sleep(1)
                    st.rerun()
                else:
                    status_text.error("❌ Analysis Failed. See details below.")
                    if errors:
                        for e in errors: st.error(e)

    st.markdown("---")

    # -- LIBRARY VIEW --
    if not st.session_state.library:
        st.info("👋 Ready. Upload a PDF to begin.")
    
    else:
        file_map = {v['name']: k for k, v in st.session_state.library.items()}
        selected_name = st.selectbox("📂 Select Document", list(file_map.keys()))
        
        if selected_name:
            fid = file_map[selected_name]
            f_obj = st.session_state.library[fid]
            data = f_obj["data"]
            cat = data.get("Category", "General")
            
            # HEADER
            st.markdown(f"""
            <div class="glass-card">
                <span style="background:#4b6cb7; color:white; padding:5px 15px; border-radius:20px; font-size:0.85em; font-weight:bold;">{cat.upper()}</span>
                <h2 style="margin-top:15px; margin-bottom:10px;">{data['Overview'].get('Title', f_obj['name'])}</h2>
                <p style="font-size:1.1em; opacity:0.8; line-height:1.6;">{data['Overview'].get('Summary', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # TABS
            t1, t2, t3, t4 = st.tabs(config["tabs"])
            
            with t1:
                st.markdown(f"<div class='glass-card' {'class=rtl' if is_rtl else ''}>", unsafe_allow_html=True)
                st.subheader("🏷️ Tags")
                tags = data['Overview'].get("Tags", [])
                st.markdown(" ".join([f"`{t}`" for t in tags]) if tags else "No tags")
                st.markdown("</div>", unsafe_allow_html=True)

            with t2:
                st.markdown(f"<div class='glass-card' {'class=rtl' if is_rtl else ''}>", unsafe_allow_html=True)
                st.subheader("💡 Key Insights")
                for p in data.get("Insights", []): st.markdown(f"**•** {p}")
                st.markdown("</div>", unsafe_allow_html=True)

            with t3:
                act = data.get("Actionable", {})
                if act.get("Items"):
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    st.subheader("📝 Action Items")
                    for item in act["Items"]: st.checkbox(item, key=f"{fid}_{item}")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                if act.get("Quiz"):
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    st.subheader("🧠 Quiz / Knowledge Check")
                    for i, q in enumerate(act["Quiz"]):
                        with st.expander(f"Q{i+1}: {q.get('Q','?')}"): st.info(f"Answer: {q.get('A','')}")
                    st.markdown("</div>", unsafe_allow_html=True)

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
            if st.button("🗑️ Clear Library", type="primary"):
                st.session_state.library = {}
                st.rerun()

if __name__ == "__main__":
    main()