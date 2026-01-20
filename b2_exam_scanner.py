import streamlit as st
import google.generativeai as genai
import pypdf
import json
import re
import hashlib
import time

# -----------------------------------------------------------------------------
# 1. INTERNAL KNOWLEDGE BASE (Simulating the Drive Content)
# -----------------------------------------------------------------------------
# This data is injected into every analysis to "back it" with expert info.
B2_KNOWLEDGE_BASE = """
    STANDARD B2 EXAM STRATEGIES (GOETHE & TELC):
    
    1. SCHREIBEN (WRITING):
       - Structure: Introduction (Refer to topic) -> Argument 1 -> Argument 2 -> Personal Experience -> Conclusion.
       - Connectors (High Value): Des Weiteren, Darüber hinaus, Einerseits... andererseits, Im Gegensatz dazu, Nichtsdestotrotz.
       - Redemittel (Complaint): "Hiermit möchte ich mich über... beschweren", "Ich fordere eine angemessene Entschädigung."
       - Redemittel (Opinion): "Meiner Auffassung nach...", "Ich stehe auf dem Standpunkt, dass..."

    2. SPRECHEN (SPEAKING):
       - Teil 1 (Presentation): Introduction -> Structure -> Content -> Conclusion -> Thank you.
       - Teil 2 (Discussion): "Das ist ein guter Punkt, aber...", "Da muss ich widersprechen...", "Habe ich Sie richtig verstanden, dass..."
       
    3. HÖREN (LISTENING):
       - Trap Alert: Distractors often use synonyms or antonyms. If you hear the exact word, it's often a trap.
       
    4. LESEN (READING):
       - Strategy: Read questions FIRST, then the text. Look for keywords (Schlüsselwörter).
"""

# -----------------------------------------------------------------------------
# 2. PAGE CONFIG & MODERN UI
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Ultra Tutor AI (Knowledge Base)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Global Gradient */
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    
    /* Glass Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 8px 32px rgba(0,0,0,0.05);
        padding: 25px;
        margin-bottom: 20px;
        color: #1a202c !important;
    }
    .glass-card h1, .glass-card h2, .glass-card h3, .glass-card p, .glass-card li { color: #1a202c !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background: rgba(255,255,255,0.6); padding: 8px; border-radius: 12px; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #3182ce; color: white !important; }
    
    /* RTL Support */
    .rtl { direction: rtl; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. STATE MANAGEMENT
# -----------------------------------------------------------------------------
if 'library' not in st.session_state: st.session_state.library = {} 

# -----------------------------------------------------------------------------
# 4. LOGIC
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
        return text if len(text) > 50 else None
    except: return None

def clean_and_repair_json(json_str):
    try:
        json_str = re.sub(r'```json', '', json_str)
        json_str = re.sub(r'```', '', json_str)
        return json.loads(json_str.strip())
    except: return None

def get_language_config(lang_code):
    config = {
        "English": {
            "role": "You are a helpful Exam Tutor. Answer in English.",
            "tabs": ["📖 Reading", "🎧 Listening", "✍️ Writing", "🗣️ Speaking", "🧩 Grammar"],
            "keys": ["Reading", "Listening", "Writing", "Speaking", "Grammar"],
            "chat_welcome": "I am your AI Study Buddy. I have access to B2 Exam Strategies."
        },
        "Deutsch": {
            "role": "Du bist ein hilfreicher Deutschlehrer. Antworte auf Deutsch.",
            "tabs": ["📖 Lesen", "🎧 Hören", "✍️ Schreiben", "🗣️ Sprechen", "🧩 Grammatik"],
            "keys": ["Reading", "Listening", "Writing", "Speaking", "Grammar"],
            "chat_welcome": "Ich bin dein KI-Partner. Ich kenne die B2-Prüfungsstrategien."
        },
        "Français": {
            "role": "Tu es un tuteur expert. Réponds en français.",
            "tabs": ["📖 Lecture", "🎧 Écoute", "✍️ Écriture", "🗣️ Oral", "🧩 Grammaire"],
            "keys": ["Reading", "Listening", "Writing", "Speaking", "Grammar"],
            "chat_welcome": "Je suis ton compagnon d'étude IA."
        },
        "العربية": {
            "role": "أنت معلم خبير. اشرح بالعربية.",
            "tabs": ["📖 القراءة", "🎧 الاستماع", "✍️ الكتابة", "🗣️ التحدث", "🧩 القواعد"],
            "keys": ["Reading", "Listening", "Writing", "Speaking", "Grammar"],
            "chat_welcome": "أنا رفيقك الدراسي الذكي."
        }
    }
    return config.get(lang_code, config["English"])

def analyze_pdf(api_key, text, lang_name):
    genai.configure(api_key=api_key)
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        model = genai.GenerativeModel(model_name)
        
        # INJECTED KNOWLEDGE PROMPT
        prompt = f"""
        Role: Senior German Exam Tutor (B2/C1 Level).
        Target Language for Explanation: {lang_name}.
        
        INTERNAL KNOWLEDGE BASE (Use this to grade/analyze):
        {B2_KNOWLEDGE_BASE}
        
        TASK: 
        Analyze the uploaded PDF text. Extract exercises, provide answers, and warn about specific traps based on the Knowledge Base.
        
        OUTPUT JSON (Strict):
        {{
            "Reading": {{ "Summary": "txt", "Vocab": ["txt"], "Exercises": [{{ "Q": "txt", "A": "txt", "Tip": "txt" }}] }},
            "Listening": {{ "Summary": "txt", "Vocab": [], "Exercises": [] }},
            "Writing": {{ "Summary": "txt", "Vocab": [], "Exercises": [] }},
            "Speaking": {{ "Summary": "txt", "Vocab": [], "Exercises": [] }},
            "Grammar": {{ "Summary": "txt", "Topics": [], "Exercises": [] }}
        }}

        PDF TEXT:
        {text[:35000]}
        """
        response = model.generate_content(prompt)
        return response.text
    except: return None

def ask_chat_bot(api_key, history, context_text, user_question, lang_role):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prepend Knowledge Base to Chat Context
    messages = [
        {"role": "user", "parts": [f"System: {lang_role}. \nKnowledge Base: {B2_KNOWLEDGE_BASE} \nPDF Context: {context_text[:15000]}"]},
        {"role": "model", "parts": ["Understood. I will use the PDF and the B2 Knowledge Base."]}
    ]
    for msg in history:
        r = "user" if msg["role"] == "user" else "model"
        messages.append({"role": r, "parts": [msg["content"]]})
    
    messages.append({"role": "user", "parts": [user_question]})
    
    try:
        response = model.generate_content(messages)
        return response.text
    except: return "Connection Error."

# -----------------------------------------------------------------------------
# 5. APP UI
# -----------------------------------------------------------------------------
def main():
    
    with st.sidebar:
        st.image("https://img.icons8.com/3d-fluency/94/brain.png", width=60)
        st.title("Ultra Tutor AI")
        st.caption("v6.0 | Knowledge Base Included")
        
        selected_lang = st.selectbox("Language / Sprache", ["English", "Deutsch", "Français", "العربية"])
        config = get_language_config(selected_lang)
        is_rtl = selected_lang == "العربية"
        api_key = st.text_input("Google API Key", type="password")
        
        # BUILT-IN REFERENCE LIBRARY (New Feature)
        with st.expander("📚 Quick B2 Reference"):
            st.markdown("**Connectors:**\n- *Außerdem* (Furthermore)\n- *Jedoch* (However)\n- *Obwohl* (Although)")
            st.markdown("**Essay Structure:**\n1. Einleitung\n2. Argumente\n3. Fazit")
        
        st.markdown("---")
        uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
        
        if uploaded_files and api_key:
            if st.button("🚀 Analyze with AI", type="primary", use_container_width=True):
                with st.spinner("Accessing Knowledge Base & Analyzing..."):
                    processed = 0
                    for up_file in uploaded_files:
                        f_hash = get_file_hash(up_file.getvalue())
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
                                        processed += 1
                    if processed > 0:
                        st.success("Analysis Complete!")
                        time.sleep(1)
                        st.rerun()

        if st.button("🗑️ Reset"):
            st.session_state.library = {}
            st.rerun()

    # MAIN CONTENT
    if not st.session_state.library:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 60px;">
            <h1 style="color:#2d3748;">👋 Ultra Tutor AI</h1>
            <p>Upload your PDF files.</p>
            <p style="font-size: 0.9em; color: #666;">
                <b>Powered by Internal Knowledge Base:</b><br>
                Includes strategies from Werkstatt B2, Aspekte Neu, and Telc Standards.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        file_map = {v['name']: k for k, v in st.session_state.library.items()}
        selected_name = st.selectbox("📚 Current Document", list(file_map.keys()))
        
        if selected_name:
            fid = file_map[selected_name]
            file_obj = st.session_state.library[fid]
            file_data = file_obj["data"]
            
            st.markdown(f"<div class='glass-card'><h2>📄 {selected_name}</h2></div>", unsafe_allow_html=True)
            
            tabs = st.tabs(config["tabs"])
            keys = config["keys"]
            
            for i, tab in enumerate(tabs):
                key = keys[i]
                with tab:
                    if key in file_data:
                        content = file_data[key]
                        st.markdown(f"""
                        <div class="glass-card" {'class="rtl"' if is_rtl else ''}>
                            <h4>📌 Summary</h4> {content.get('Summary', '-')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if content.get("Vocab"):
                            with st.expander(f"📝 {key} Vocabulary"):
                                for v in content["Vocab"]: st.write(f"• {v}")
                        
                        exercises = content.get("Exercises", [])
                        if exercises:
                            st.subheader("Interactive Exercises")
                            for idx, ex in enumerate(exercises):
                                with st.container():
                                    st.markdown(f"""
                                    <div style="background: rgba(255,255,255,0.7); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #3182ce;">
                                        <strong>Q{idx+1}:</strong> {ex.get('Q', '')}
                                    </div>
                                    """, unsafe_allow_html=True)
                                    c1, c2 = st.columns([1, 4])
                                    with c1:
                                        if st.button(f"Answer {idx+1}", key=f"a_{fid}_{key}_{idx}"):
                                            st.success(ex.get('A', ''))
                                    with c2:
                                        if ex.get('Tip'): st.info(f"💡 {ex['Tip']}")
                        else: st.info("No specific exercises detected here.")

            st.markdown("---")
            st.subheader("🤖 AI Study Buddy")
            
            # Chat Interface
            for msg in file_obj["chat_history"]:
                with st.chat_message(msg["role"]): st.write(msg["content"])

            if prompt := st.chat_input("Ask about this document..."):
                file_obj["chat_history"].append({"role": "user", "content": prompt})
                with st.chat_message("user"): st.write(prompt)
                
                with st.spinner("Thinking..."):
                    ai_reply = ask_chat_bot(api_key, file_obj["chat_history"], file_obj["text"], prompt, config["role"])
                
                file_obj["chat_history"].append({"role": "assistant", "content": ai_reply})
                with st.chat_message("assistant"): st.write(ai_reply)
                time.sleep(0.1)
                st.rerun()

if __name__ == "__main__":
    main()