import streamlit as st
import google.generativeai as genai
import pypdf
import json
import re

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="🇩🇪 B2 Exam Super-Scanner (Auto-Model)",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------------------------------------------------------
# LOGIC
# -----------------------------------------------------------------------------

def get_working_model_name():
    """
    Asks Google which models are available for this API Key 
    and picks the best one (preferring Flash, then Pro).
    """
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        # Sort preferences
        if not available_models:
            return None, "No models found. Check API Key permissions."
            
        # Try to find specific strong models
        if 'models/gemini-1.5-flash' in available_models:
            return 'models/gemini-1.5-flash', available_models
        elif 'models/gemini-1.5-pro' in available_models:
            return 'models/gemini-1.5-pro', available_models
        elif 'models/gemini-pro' in available_models:
            return 'models/gemini-pro', available_models
            
        # Fallback: Just take the first one that supports text
        return available_models[0], available_models
        
    except Exception as e:
        return None, str(e)

def extract_text_from_pdfs(uploaded_files):
    combined_text = ""
    file_count = 0
    for uploaded_file in uploaded_files:
        try:
            reader = pypdf.PdfReader(uploaded_file)
            file_text = ""
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    file_text += content + "\n"
            if file_text:
                combined_text += f"\n--- FILE: {uploaded_file.name} ---\n{file_text}"
                file_count += 1
        except Exception:
            pass # Skip bad files
    return combined_text, file_count

def clean_json_string(json_str):
    json_str = re.sub(r'```json', '', json_str)
    json_str = re.sub(r'```', '', json_str)
    return json_str.strip()

def analyze_text(api_key, text):
    genai.configure(api_key=api_key)
    
    # 1. FIND A WORKING MODEL
    model_name, debug_info = get_working_model_name()
    
    if not model_name:
        st.error(f"Could not find a valid model. Google said: {debug_info}")
        return None

    # st.info(f"Using AI Model: {model_name}") # Uncomment to see which model is used

    model = genai.GenerativeModel(model_name)

    prompt = f"""
    Role: German B2 Exam Tutor.
    Task: Analyze the text and generate JSON output.
    
    OUTPUT FORMAT:
    {{
        "Lesen": {{ "CheatSheet": "bullets", "Mnemonics": "text", "Traps": "text", "SummaryTable": "markdown" }},
        "Hören": {{ "CheatSheet": "bullets", "Mnemonics": "text", "Traps": "text", "SummaryTable": "markdown" }},
        "Schreiben": {{ "CheatSheet": "bullets", "Mnemonics": "text", "Traps": "text", "SummaryTable": "markdown" }},
        "Sprechen": {{ "CheatSheet": "bullets", "Mnemonics": "text", "Traps": "text", "SummaryTable": "markdown" }}
    }}
    
    TEXT:
    {text[:25000]}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Generation Error: {e}")
        return None

# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------
def main():
    st.sidebar.header("⚙️ Settings")
    api_key = st.sidebar.text_input("Google API Key", type="password")
    
    st.title("🇩🇪 B2 Exam Scanner (Auto-Fixer)")
    
    uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

    if uploaded_files and api_key:
        if st.button("Analyze Files"):
            with st.spinner("Connecting to Google AI..."):
                text, count = extract_text_from_pdfs(uploaded_files)
                if count > 0:
                    json_response = analyze_text(api_key, text)
                    if json_response:
                        try:
                            data = json.loads(clean_json_string(json_response))
                            st.success("Success!")
                            
                            tabs = st.tabs(["Reading", "Listening", "Writing", "Speaking"])
                            keys = ["Lesen", "Hören", "Schreiben", "Sprechen"]
                            
                            for i, tab in enumerate(tabs):
                                key = keys[i]
                                with tab:
                                    if key in data:
                                        sec = data[key]
                                        c1, c2 = st.columns(2)
                                        c1.subheader("Cheat Sheet")
                                        c1.markdown(sec.get("CheatSheet", "-"))
                                        c1.subheader("Mnemonics")
                                        c1.info(sec.get("Mnemonics", "-"))
                                        c2.subheader("Traps")
                                        c2.warning(sec.get("Traps", "-"))
                                        st.subheader("Summary")
                                        st.markdown(sec.get("SummaryTable", "-"))
                        except:
                            st.error("AI output invalid. Try again.")
                            st.text(json_response)
                else:
                    st.warning("No text found in PDF.")

if __name__ == "__main__":
    main()