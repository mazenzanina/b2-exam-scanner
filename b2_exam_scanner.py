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
    page_title="AI Assistant",
    page_icon="🤖",
    layout="centered", # Centered layout matches mobile app view better
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# 2. HOLO-BLUE UI (CSS)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    /* 1. THE BACKGROUND GRADIENT (Deep Blue to White) */
    .stApp {
        background: linear-gradient(180deg, #4c6ef5 0%, #859df9 40%, #dbe4ff 75%, #ffffff 100%);
        background-attachment: fixed;
    }

    /* 2. HIDE DEFAULT STREAMLIT ELEMENTS */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    
    /* 3. TYPOGRAPHY */
    h1 {
        color: white !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        font-size: 2.5rem !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 10px !important;
    }
    p {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 1.1rem !important;
        line-height: 1.5;
    }

    /* 4. THE 3D ROBOT AVATAR & GLOW */
    .robot-container {
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
        height: 300px;
        margin-top: 20px;
    }
    
    .glow-circle {
        position: absolute;
        width: 180px;
        height: 180px;
        background: radial-gradient(circle, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0) 70%);
        border-radius: 50%;
        z-index: 1;
        animation: pulse 3s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.7; }
        50% { transform: scale(1.1); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.7; }
    }

    .robot-img {
        width: 120px;
        height: 120px;
        z-index: 2;
        border-radius: 50%;
        background: white;
        padding: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }

    /* 5. FLOATING BUBBLES */
    .floating-bubble {
        position: absolute;
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
        font-size: 0.8rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        animation: float 4s ease-in-out infinite;
    }

    .bubble-left {
        width: 90px;
        height: 90px;
        top: 40px;
        left: 20px;
        animation-delay: 0s;
    }
    
    .bubble-right {
        width: 100px;
        height: 100px;
        bottom: 40px;
        right: 20px;
        animation-delay: 2s;
    }

    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }

    /* 6. SPEECH BUBBLE (CTA) */
    .speech-bubble {
        position: absolute;
        top: 20px;
        right: 50px;
        background: white;
        color: #4c6ef5;
        padding: 10px 20px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        z-index: 5;
        cursor: pointer;
    }
    .speech-bubble:after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        width: 0;
        height: 0;
        border: 10px solid transparent;
        border-top-color: white;
        border-bottom: 0;
        margin-left: -10px;
        margin-bottom: -10px;
    }

    /* 7. PREMIUM BUTTONS */
    .premium-card {
        background: linear-gradient(90deg, #2b3a6e 0%, #4c6ef5 100%);
        border-radius: 30px;
        padding: 15px;
        color: white;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 10px 25px rgba(76, 110, 245, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        font-weight: bold;
    }
    
    .pro-button {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 30px;
        padding: 10px 20px;
        color: #333;
        text-align: center;
        font-weight: bold;
        backdrop-filter: blur(5px);
        margin-bottom: 20px;
        display: inline-block;
        border: 1px solid rgba(255,255,255,0.4);
    }

    /* 8. INPUT FIELD (Floating Pill) */
    .stChatInput {
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 600px;
        z-index: 100;
    }
    .stChatInputContainer {
        background-color: white;
        border-radius: 30px !important;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        padding: 5px;
        border: none;
    }
    .stChatInputContainer textarea {
        color: #333;
    }

    /* 9. FILE UPLOADER STYLING (Hidden inside bubble concept) */
    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. LOGIC & STATE
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
    try:
        if not text: return None
        start = text.find('{')
        end = text.rfind('}') + 1
        if start == -1 or end == 0: return None
        return json.loads(text[start:end])
    except: return None

def analyze_content(api_key, text):
    genai.configure(api_key=api_key)
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        You are a Universal AI Assistant.
        TASK: Identify category (Study, Work, Novel, Travel). Extract structured data.
        OUTPUT JSON ONLY:
        {{
            "Category": "Short Name",
            "Overview": {{ "Title": "Txt", "Summary": "Txt" }},
            "Insights": ["Point 1", "Point 2"],
            "Actionable": {{ "Items": ["To-Do 1"] }}
        }}
        TEXT: {text[:25000]}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e: return f"API_ERROR: {str(e)}"

def ask_chat(api_key, history, context, question):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    msgs = [{"role": "user", "parts": [f"Context: {context[:20000]}"]}]
    for m in history:
        msgs.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})
    msgs.append({"role": "user", "parts": [question]})
    try: return model.generate_content(msgs).text
    except: return "Connection error."

# -----------------------------------------------------------------------------
# 4. MAIN UI STRUCTURE
# -----------------------------------------------------------------------------
def main():
    
    # --- HEADER ---
    st.markdown("<h1>Hey! I'm your AI<br>Brain Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p>Based on your uploaded documents, I've analyzed your possible needs. Click to generate solutions.</p>", unsafe_allow_html=True)

    # --- API KEY (Hidden in expander for clean look) ---
    with st.expander("🔐 Setup API Key (Click Here)", expanded=False):
        api_key = st.text_input("Google API Key", type="password")

    # --- VISUAL CENTERPIECE (Robot + Bubbles) ---
    # Using HTML/CSS to replicate the image layout exactly
    st.markdown("""
        <div class="robot-container">
            <!-- Left Bubble -->
            <div class="floating-bubble bubble-left">
                <span style="font-size: 20px;">📄</span>
                <span>Docs</span>
            </div>
            
            <!-- Center Robot -->
            <div class="glow-circle"></div>
            <img src="https://img.icons8.com/3d-fluency/375/robot-2.png" class="robot-img">
            
            <!-- Speech Bubble CTA -->
            <div class="speech-bubble">
                Click me! Upload PDF
            </div>
            
            <!-- Right Bubble -->
            <div class="floating-bubble bubble-right">
                <span style="font-size: 20px;">🎓</span>
                <span>Study</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- UPLOAD SECTION (Visual integration) ---
    # We place the uploader here. In a real app, clicking the speech bubble would trigger this.
    # Here we put it below to mimic the flow.
    uploaded_files = st.file_uploader("Upload your files here", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")

    # --- PROCESS LOGIC ---
    if uploaded_files and api_key and st.button("✨ Analyze Files", type="primary", use_container_width=True):
        with st.status("🧠 Processing...", expanded=True) as status:
            processed = 0
            for up_file in uploaded_files:
                f_hash = get_file_hash(up_file.getvalue())
                if f_hash not in st.session_state.library:
                    st.write(f"Reading {up_file.name}...")
                    txt = extract_text(up_file)
                    if txt:
                        st.write(f"Analyzing content...")
                        raw = analyze_content(api_key, txt)
                        data = robust_json_extractor(raw)
                        if data:
                            st.session_state.library[f_hash] = {
                                "name": up_file.name, "data": data, "text": txt, "chat_history": []
                            }
                            processed += 1
            if processed > 0:
                status.update(label="Done!", state="complete")
                st.rerun()

    # --- PREMIUM BUTTONS ---
    st.markdown("""
        <div class="premium-card">
            <span>✨ Get a free trial of the premium version</span>
        </div>
        <div style="text-align: left;">
            <span class="pro-button">✨ Upgrade to Pro</span>
        </div>
    """, unsafe_allow_html=True)

    # --- RESULTS AREA (If data exists) ---
    if st.session_state.library:
        file_map = {v['name']: k for k, v in st.session_state.library.items()}
        # Use a simpler selector for this UI
        selected_name = st.selectbox("Select File to Chat", list(file_map.keys()))
        
        if selected_name:
            fid = file_map[selected_name]
            f_obj = st.session_state.library[fid]
            
            # Show Chat History just above the input
            for m in f_obj["chat_history"]:
                with st.chat_message(m["role"]): st.write(m["content"])

            # --- FLOATING CHAT INPUT ---
            if prompt := st.chat_input("Please enter your requirements..."):
                if api_key:
                    f_obj["chat_history"].append({"role": "user", "content": prompt})
                    with st.chat_message("user"): st.write(prompt)
                    
                    with st.spinner("..."):
                        reply = ask_chat(api_key, f_obj["chat_history"], f_obj["text"], prompt)
                    
                    f_obj["chat_history"].append({"role": "assistant", "content": reply})
                    with st.chat_message("assistant"): st.write(reply)
                    st.rerun()
                else:
                    st.error("Please enter API Key above.")

if __name__ == "__main__":
    main()