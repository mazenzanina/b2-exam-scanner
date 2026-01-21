import streamlit as st
import google.generativeai as genai
import pypdf
import json
import re
import hashlib
import time
import random

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION (Crucial: Must be "centered" to match the screenshot)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Holo AI v12",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# 2. HOLO-BLUE UI CSS (Forced Override)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    /* 1. BACKGROUND: Exact gradient from the screenshot */
    .stApp {
        background: linear-gradient(180deg, #4c6ef5 0%, #748ffc 30%, #bac8ff 60%, #ffffff 100%);
        background-attachment: fixed;
    }

    /* 2. HIDE DEFAULT ELEMENTS (Clean look) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    
    /* 3. TYPOGRAPHY */
    h1 {
        color: white !important;
        font-family: sans-serif;
        font-weight: 700;
        text-align: center;
        text-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    p {
        color: rgba(255,255,255,0.95) !important;
        text-align: center;
        font-size: 1.1rem;
    }

    /* 4. THE 3D AVATAR CONTAINER */
    .avatar-container {
        position: relative;
        height: 350px;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }

    /* The Robot Image */
    .robot-img {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        background: white;
        padding: 10px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        z-index: 10;
        animation: float 6s ease-in-out infinite;
    }

    /* The Glow behind robot */
    .glow {
        position: absolute;
        width: 250px;
        height: 250px;
        background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0) 70%);
        border-radius: 50%;
        animation: pulse 4s infinite;
    }

    /* Floating Bubbles (Left/Right) */
    .bubble {
        position: absolute;
        background: rgba(255,255,255,0.2);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.4);
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
        font-weight: bold;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .b-left { width: 100px; height: 100px; top: 50px; left: 10%; animation: float 5s infinite 1s; }
    .b-right { width: 110px; height: 110px; bottom: 50px; right: 10%; animation: float 7s infinite 2s; }

    /* The "Click Me" Speech Bubble */
    .cta-bubble {
        position: absolute;
        top: 30px;
        right: 25%;
        background: white;
        color: #4c6ef5;
        padding: 10px 20px;
        border-radius: 20px;
        font-weight: bold;
        box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        z-index: 20;
        animation: pop 0.5s ease-out;
    }
    .cta-bubble::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 20px;
        border-width: 10px 10px 0;
        border-style: solid;
        border-color: white transparent;
    }

    /* Animations */
    @keyframes float { 0%{transform: translateY(0px);} 50%{transform: translateY(-15px);} 100%{transform: translateY(0px);} }
    @keyframes pulse { 0%{transform: scale(0.9); opacity:0.6;} 50%{transform: scale(1.1); opacity:1;} 100%{transform: scale(0.9); opacity:0.6;} }

    /* 5. INPUT FIELD (Floating at bottom) */
    .stChatInput {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 600px;
        z-index: 999;
    }
    .stChatInputContainer {
        background: white;
        border-radius: 40px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        padding: 5px 10px;
    }

    /* 6. UPLOAD BOX (Styled to blend in) */
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.9);
        border-radius: 15px;
        padding: 15px;
        margin-top: -20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    /* 7. PREMIUM BUTTONS */
    .premium-btn {
        background: rgba(255,255,255,0.25);
        border: 1px solid rgba(255,255,255,0.5);
        border-radius: 30px;
        padding: 12px;
        color: white;
        text-align: center;
        font-weight: 600;
        margin: 10px 0;
        cursor: pointer;
        backdrop-filter: blur(5px);
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. ROBUST API LOGIC (With Exponential Backoff)
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

def analyze_with_backoff(api_key, text):
    """
    Tries to call Google API. If rate limited (429), waits longer and retries.
    """
    genai.configure(api_key=api_key)
    # Prefer Flash model for speed/allowance
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    You are a helpful AI Assistant.
    TASK: Analyze context (Study, Work, Travel).
    OUTPUT: Valid JSON ONLY.
    {{
        "Category": "Short Name",
        "Overview": {{ "Title": "Txt", "Summary": "Txt" }},
        "Insights": ["Point 1", "Point 2"]
    }}
    TEXT: {text[:20000]}
    """
    
    # RETRY LOGIC
    max_retries = 3
    base_delay = 10 # Start with 10 seconds wait
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e): # Rate Limit Error
                wait_time = base_delay * (2 ** attempt) + random.randint(1, 5) # 10s -> 20s -> 40s
                with st.spinner(f"⚠️ High Traffic. Waiting {wait_time}s to ensure success..."):
                    time.sleep(wait_time)
                continue # Retry loop
            else:
                return f"API_ERROR: {str(e)}"
    
    return "API_ERROR: Failed after multiple retries."

def ask_chat(api_key, history, context, question):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    msgs = [{"role": "user", "parts": [f"Context: {context[:15000]}"]}]
    for m in history:
        msgs.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})
    msgs.append({"role": "user", "parts": [question]})
    try: return model.generate_content(msgs).text
    except: return "Connection error."

# -----------------------------------------------------------------------------
# 4. UI LAYOUT
# -----------------------------------------------------------------------------
def main():
    
    # HEADER
    st.markdown("<h1>Hey! I'm your AI<br>Brain Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p>I've analyzed your space and device information. Click to generate solutions.</p>", unsafe_allow_html=True)

    # API KEY (Collapsible)
    with st.expander("🔐 Setup Key", expanded=False):
        api_key = st.text_input("API Key", type="password", label_visibility="collapsed")

    # THE VISUAL SCENE
    st.markdown("""
        <div class="avatar-container">
            <div class="bubble b-left">
                <span style="font-size:24px;">📄</span>
                <span>Docs</span>
            </div>
            
            <div class="glow"></div>
            <img src="https://img.icons8.com/3d-fluency/375/robot-2.png" class="robot-img">
            
            <div class="cta-bubble">Click below!</div>
            
            <div class="bubble b-right">
                <span style="font-size:24px;">💡</span>
                <span>Ideas</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # FILE UPLOADER (Acts as the interaction point)
    uploaded_files = st.file_uploader("Upload Here", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")

    # ANALYZE BUTTON
    if uploaded_files and api_key and st.button("✨ Analyze Now", use_container_width=True, type="primary"):
        processed = 0
        for up_file in uploaded_files:
            f_hash = get_file_hash(up_file.getvalue())
            if f_hash not in st.session_state.library:
                st.info(f"Reading {up_file.name}...")
                txt = extract_text(up_file)
                if txt:
                    # Uses the new Backoff function
                    raw = analyze_with_backoff(api_key, txt)
                    if "API_ERROR" not in raw:
                        data = robust_json_extractor(raw)
                        if data:
                            st.session_state.library[f_hash] = {
                                "name": up_file.name, "data": data, "text": txt, "chat_history": []
                            }
                            processed += 1
                    else:
                        st.error(raw)
        
        if processed > 0:
            st.success("Done! Chat below.")
            time.sleep(1)
            st.rerun()

    # PREMIUM MOCKUPS
    st.markdown("""
        <div class="premium-btn">✨ Get a free trial of Premium</div>
        <div class="premium-btn" style="background:rgba(0,0,0,0.1);">✨ Upgrade to Pro</div>
    """, unsafe_allow_html=True)

    # CHAT INTERFACE
    if st.session_state.library:
        # File selector styled simply
        file_map = {v['name']: k for k, v in st.session_state.library.items()}
        selected = st.selectbox("Select File", list(file_map.keys()), label_visibility="collapsed")
        
        if selected:
            fid = file_map[selected]
            f_obj = st.session_state.library[fid]
            
            # Show history
            for m in f_obj["chat_history"]:
                with st.chat_message(m["role"]): st.write(m["content"])
            
            # Floating Input
            if prompt := st.chat_input("Enter your requirements..."):
                if api_key:
                    f_obj["chat_history"].append({"role": "user", "content": prompt})
                    with st.chat_message("user"): st.write(prompt)
                    
                    with st.spinner("..."):
                        reply = ask_chat(api_key, f_obj["chat_history"], f_obj["text"], prompt)
                    
                    f_obj["chat_history"].append({"role": "assistant", "content": reply})
                    with st.chat_message("assistant"): st.write(reply)
                    st.rerun()

if __name__ == "__main__":
    main()