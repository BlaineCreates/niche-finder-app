import streamlit as st
import google.generativeai as genai
import json

# Page Layout configuration
st.set_page_config(page_title="Retention Simulator", page_icon="⏱️", layout="wide", initial_sidebar_state="expanded")

# Hide Streamlit Default Branding safely
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden;}
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

st.title("⏱️ Pre-Production Retention Simulator")
st.markdown("Analyze your script's pacing, hook structure, and AI extractability before you record a single frame.")

st.sidebar.info("Live Gemini AI Engine Active")

# Configure Live Gemini API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("API Key missing or invalid. Please check your secrets vault.")

# Main Interface
script_text = st.text_area(
    "Paste your raw video script here:", 
    height=300, 
    placeholder="Hey guys, welcome back to the channel. Today we are going to talk about..."
)

if st.button("🚀 Run Live AI Script Analysis", type="primary"):
    if len(script_text) < 100:
        st.warning("Please paste a longer script (at least 100 characters) for an accurate analysis.")
    else:
        with st.spinner("Gemini is analyzing structural pacing and semantic density..."):
            try:
                # The strict prompt to force data formatting
                prompt = f"""
                You are an elite YouTube retention analyzer. Analyze this script.
                Return exactly a JSON object with NO markdown formatting, NO backticks, and NO other text.
                It must contain exactly these 4 keys:
                "hook_score": An integer (0-100) grading the first 30 seconds.
                "pacing_score": An integer (0-100) grading the flow.
                "extractability_score": An integer (0-100) grading how easily Perplexity/AI can extract facts.
                "ai_feedback": A brief string (under 30 words) explaining the biggest flaw or strength.
                
                Script to analyze:
                {script_text}
                """
                
                # Call Gemini
                response = model.generate_content(prompt)
                
                # Clean the response in case Gemini sneaks in markdown backticks
                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                ai_data = json.loads(clean_json)
                
                # Extract Live Scores
                hook_score = int(ai_data.get("hook_score", 0))
                pacing_score = int(ai_data.get("pacing_score", 0))
                extractability_score = int(ai_data.get("extractability_score", 0))
                ai_feedback = ai_data.get("ai_feedback", "No feedback provided.")
                
                st.divider()
                st.subheader("📊 Live Predictive Script Analytics")
                
                # Visual Scorecards
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Hook Retention Prediction", f"{hook_score}/100")
                    st.progress(hook_score / 100.0)
                    
                with col2:
                    st.metric("Narrative Pacing Score", f"{pacing_score}/100")
                    st.progress(pacing_score / 100.0)
                    
                with col3:
                    st.metric("AI Extractability Index", f"{extractability_score}/100")
                    st.progress(extractability_score / 100.0)
                
                st.markdown("### 🚩 Engine Flag Reports")
                if hook_score < 60:
                    st.error(f"**Critical Hook Warning:** {ai_feedback}")
                else:
                    st.success(f"**Engine Cleared:** {ai_feedback}")
                    
            except Exception as e:
                st.error(f"Engine parsing failure. The AI returned an unexpected format. Error: {e}")