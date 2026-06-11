import streamlit as st
import json
from datetime import datetime

# Page Layout configuration
st.set_page_config(
    page_title="AEO Schema Architect", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit Default Branding safely while preserving sidebar accessibility
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden;}
       footer {visibility: hidden;}
       header {visibility: hidden;}
       div[data-testid="collapsedControl"] {display: block !important; visibility: visible !important;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

st.title("🤖 AEO Schema & Extractability Architect")
st.markdown("Transform conversational video assets into structured engine-readable markup to maximize AI Search citation velocity.")

# Sidebar Navigation Status
st.sidebar.success("AEO Optimization Engine Active")

# App Interface Split
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Video Baseline Parameters")
    video_title = st.text_input("Video Title", placeholder="e.g., How to Build a Faceless AI Channel")
    video_url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
    thumb_url = st.text_input("Thumbnail Image URL", placeholder="https://img.youtube.com/vi/...")
    
    st.subheader("📝 Target Conversational Queries (From Research)")
    raw_chapters = st.text_area(
        "Enter Video Timestamps & Focus Questions (One per line)",
        placeholder="00:00 - Introduction to Faceless Automation\n02:15 - What is the best AI video generator?\n06:40 - How to monetize synthetic content without penalties",
        height=150
    )
    
    generate_btn = st.button("🚀 Synthesize AI-Engine Search Schema", type="primary")

with col2:
    st.subheader("📦 Generated JSON-LD AI-Extraction Engine Code")
    st.caption("Embed this explicit schema structure on your blog, portfolio, or video landing pages to earn zero-click AI answers.")
    
    if generate_btn:
        if not video_title or not video_url:
            st.error("Please provide at least a Video Title and URL to build the structural object container.")
        else:
            try:
                # Parsing chapters text into structural clips
                lines = [line.strip() for line in raw_chapters.split('\n') if line.strip()]
                clips = []
                
                for index, line in enumerate(lines):
                    # Splitting timestamps from queries
                    parts = line.split('-', 1)
                    if len(parts) == 2:
                        time_str = parts[0].strip()
                        query_str = parts[1].strip()
                        
                        # Basic timeline handling
                        clips.append({
                            "@type": "Clip",
                            "name": query_str,
                            "startOffset": f"PT{time_str.replace(':', 'M')}S", # Simplified ISO duration mapping
                            "url": f"{video_url}&t={time_str.replace(':', 'm')}"
                        })
                
                # Master VideoObject Configuration Block
                schema_data = {
                    "@context": "https://schema.org",
                    "@type": "VideoObject",
                    "name": video_title,
                    "description": f"Structured video extraction resource optimized for AEO targeting focus entities.",
                    "thumbnailUrl": thumb_url if thumb_url else "https://example.com/default-thumb.jpg",
                    "uploadDate": datetime.today().strftime('%Y-%m-%d'),
                    "contentUrl": video_url,
                    "embedUrl": video_url.replace("watch?v=", "embed/"),
                    "hasPart": clips
                }
                
                # Render Clean Format
                pretty_json = json.dumps(schema_data, indent=4)
                st.code(pretty_json, language="json")
                st.success("JSON-LD VideoObject and Clip schema rendered perfectly!")
                
            except Exception as e:
                st.error(f"Syntax translation anomaly: {str(e)}")
    else:
        st.info("Awaiting structural parameters. Fill out your video milestones to generate the schema matrix.")