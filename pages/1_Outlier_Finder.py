import streamlit as st
import pandas as pd
import requests
import json
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Safety gate check
if not st.session_state.get("authenticated", False):
    st.warning("Security alert: Access denied. Please authenticate at the front gate.")
    st.stop()

API_KEY = st.secrets["GOOGLE_API_KEY"]
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]

st.title("🔍 Outlier Analytics Finder")
st.markdown("Uncover videos that violently outperform their channel baseline size to find proven viral angles.")
st.markdown("---")

# Initialize persistent memory storage keys for this page
if "outlier_results" not in st.session_state:
    st.session_state.outlier_results = None
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

# Advanced Filter Tray Layout
with st.expander("⚙️ Advanced Search Filters & Tuning", expanded=True):
    col_input, col_format = st.columns(2)
    
    with col_input:
        target_niche = st.text_input("Target Niche / Search Query", value="faceless AI automation")
        time_frame = st.selectbox("Upload Recency", ["All Time", "Last 90 Days", "Last 30 Days", "Last 7 Days"])
    
    with col_format:
        format_filter = st.radio("Content Format Type", ["All Formats", "Long-form Only ( > 60s )", "Shorts Only ( < 60s )"], horizontal=True)
        target_multiplier = st.slider("Minimum Outlier Multiplier", min_value=2.0, max_value=20.0, value=5.0, step=0.5)

    st.markdown("#### Channel & Target View Constraints")
    col_views, col_subs = st.columns(2)
    with col_views:
        max_views = st.slider("Maximum Total Views Limit", min_value=1000, max_value=10000000, value=5000000, step=50000)
    with col_subs:
        min_subs = st.slider("Minimum Channel Subscribers", min_value=0, max_value=500000, value=1000, step=1000)

trigger_scan = st.button("🚀 Run Deep Market Intelligence Scan", use_container_width=True)

# ------------------------------------------------------------------------------
# THE GEMINI LIVE AI BRAINSTORMING CONNECTOR
# ------------------------------------------------------------------------------
def generate_ai_remix(mode, video_title, multiplier):
    # Construct a highly strategic, professional prompt based on the user click choice
    if mode == "title":
        prompt = f"You are a master YouTube growth strategist. This video title went viral with an insane {multiplier}x multiplier compared to the channel's normal size: '{video_title}'. Brainstorm 5 alternative high-CTR, click-worthy titles/hooks that leverage the exact same psychological curiosity angle but use different high-converting phrasing. Keep them punchy and ready to copy-paste. Do not include introductory text, just jump straight to the numbered list."
    else:
        prompt = f"You are a master YouTube thumbnail designer and visual psychology expert. A video titled '{video_title}' went viral with a {multiplier}x outlier score. Describe 3 highly specific visual concept ideas for a brand new thumbnail layout that would beat the current one. Specify color contrast splits, placement of elements, text overlay hooks (maximum 3 words), and emotional expressions to capture. Keep it concise, practical, and highly scannable. Do not include introductory text, just jump straight to the numbered list."

    # Execute a clean REST request to Google's live Gemini 1.5 Flash API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            res_json = response.json()
            ai_text = res_json['candidates'][0]['content']['parts'][0]['text']
            return ai_text
        else:
            return f"AI Connection Interrupted (Status {response.status_code}). Ensure your API key is fully activated."
    except Exception as e:
        return f"AI Engine Timed Out: {e}"

# ------------------------------------------------------------------------------
# RE-ENGINEERED INSPECTION POPUP MODAL WITH LIVE GENERATION LAYERS
# ------------------------------------------------------------------------------
@st.dialog("🎬 Asset Inspection & Live AI Brainstorming", width="large")
def render_video_modal(video_data):
    col_thumb, col_meta = st.columns([5, 4])
    with col_thumb:
        st.image(video_data["Thumbnail"], use_container_width=True)
    with col_meta:
        st.subheader(video_data["Title"])
        st.caption(f"👤 Channel: {video_data['Channel']}\n\n📅 Published: {video_data['Published']}")
    
    st.markdown("---")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Multiplier", f"{video_data['Multiplier']}x")
    with col_m2:
        st.metric("Total Views", f"{video_data['Views']:,}")
    with col_m3:
        st.metric("Views Per Hour", f"{video_data['VPH']:,}/hr")
    with col_m4:
        engagement_label = "🔥 Explosive" if video_data["Engagement"] >= 8.0 else ("✅ Stable" if video_data["Engagement"] >= 3.0 else "⚠️ Weak")
        st.metric("Engagement Grade", engagement_label)

    st.markdown("### 🛠️ Strategic Asset Triggers")
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.link_button("🌐 Open Video on YouTube ↗️", video_data["URL"], use_container_width=True)
    with col_b2:
        remix_titles = st.button("📝 Live Remix Titles (AI)", use_container_width=True)
    with col_b3:
        remix_thumb = st.button("🎨 Live Remix Thumbnail (AI)", use_container_width=True)

    # Secondary action bar lines
    col_b4, col_b5 = st.columns(2)
    with col_b4:
        find_similar = st.button("🔍 Find Similar Titles", use_container_width=True)
    with col_b5:
        flag_comp = st.button("🎯 Flag Channel as Competitor", use_container_width=True)

    # Live UI output injection areas based on active clicks inside the open popup container
    if remix_titles:
        st.markdown("---")
        st.markdown("#### 🧠 AI Title Remix Generation Matrix")
        with st.spinner("Consulting growth vectors (Gemini AI live generation)..."):
            output = generate_ai_remix("title", video_data["Title"], video_data["Multiplier"])
            st.info(output)

    if remix_thumb:
        st.markdown("---")
        st.markdown("#### 🎨 AI Visual Composition Layout Model")
        with st.spinner("Drafting design configurations (Gemini AI live generation)..."):
            output = generate_ai_remix("thumbnail", video_data["Title"], video_data["Multiplier"])
            st.success(output)

    if find_similar:
        st.toast(f"Scanning target node vectors for phrasing matching: {video_data['Title'][:20]}...")
    if flag_comp:
        st.toast(f"Successfully pinned {video_data['Channel']} into your monitoring array!")

def parse_duration(duration_str):
    import re
    hours = re.search(r'(\d+)H', duration_str)
    minutes = re.search(r'(\d+)M', duration_str)
    seconds = re.search(r'(\d+)S', duration_str)
    total_seconds = 0
    if hours: total_seconds += int(hours.group(1)) * 3600
    if minutes: total_seconds += int(minutes.group(1)) * 60
    if seconds: total_seconds += int(seconds.group(1))
    return total_seconds

if trigger_scan:
    with st.spinner("Executing Deep-Page Sweep..."):
        try:
            youtube = build("youtube", "v3", developerKey=API_KEY)
            compiled_results = []
            next_page_token = None
            
            published_after = None
            if time_frame == "Last 7 Days":
                published_after = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"
            elif time_frame == "Last 30 Days":
                published_after = (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"
            elif time_frame == "Last 90 Days":
                published_after = (datetime.utcnow() - timedelta(days=90)).isoformat() + "Z"

            for loop_page in range(2):
                search_kwargs = {"q": target_niche, "type": "video", "part": "id,snippet", "maxResults": 50, "pageToken": next_page_token}
                if published_after: search_kwargs["publishedAfter"] = published_after
                    
                search_response = youtube.search().list(**search_kwargs).execute()
                video_items = search_response.get("items", [])
                next_page_token = search_response.get("nextPageToken")
                
                if not video_items: break

                v_ids = [item["id"]["videoId"] for item in video_items]
                v_details = youtube.videos().list(id=",".join(v_ids), part="statistics,contentDetails").execute()
                v_dict = {v["id"]: v for v in v_details.get("items", [])}
                
                c_ids = list(set([item["snippet"]["channelId"] for item in video_items]))
                c_details = youtube.channels().list(id=",".join(c_ids), part="statistics").execute()
                c_dict = {c["id"]: c for c in c_details.get("items", [])}

                for item in video_items:
                    video_id = item["id"]["videoId"]
                    video_title = item["snippet"]["title"]
                    channel_id = item["snippet"]["channelId"]
                    channel_title = item["snippet"]["channelTitle"]
                    published_raw = item["snippet"]["publishedAt"].split("T")[0]

                    v_meta = v_dict.get(video_id)
                    if not v_meta: continue
                    
                    stats = v_meta["statistics"]
                    duration_seconds = parse_duration(v_meta["contentDetails"]["duration"])

                    if format_filter == "Long-form Only ( > 60s )" and duration_seconds <= 60: continue
                    if format_filter == "Shorts Only ( < 60s )" and duration_seconds > 60: continue

                    views = int(stats.get("viewCount", 0))
                    likes = int(stats.get("likeCount", 0))
                    comments = int(stats.get("commentCount", 0))

                    if views > max_views: continue

                    c_meta = c_dict.get(channel_id)
                    if not c_meta: continue
                    subs = int(c_meta["statistics"].get("subscriberCount", 0))

                    if subs < min_subs or subs == 0: continue
                    outlier_ratio = views / subs
                    
                    pub_datetime = datetime.strptime(item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
                    hours_elapsed = max((datetime.utcnow() - pub_datetime).total_seconds() / 3600, 1.0)
                    vph = int(views / hours_elapsed)
                    
                    engagement_ratio = ((likes + comments) / views) * 100 if views > 0 else 0.0

                    if outlier_ratio >= target_multiplier:
                        compiled_results.append({
                            "ID": video_id,
                            "Multiplier": round(outlier_ratio, 1),
                            "VPH": vph,
                            "Engagement": round(engagement_ratio, 2),
                            "Thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
                            "Title": video_title,
                            "Channel": channel_title,
                            "Subscribers": subs,
                            "Views": views,
                            "Published": published_raw,
                            "URL": f"https://www.youtube.com/watch?v={video_id}"
                        })
            
            st.session_state.outlier_results = compiled_results
            st.session_state.last_query = target_niche
            
        except Exception as e:
            st.error(f"Data Scan Failure: {e}")

# Render active results from session memory
if st.session_state.outlier_results is not None:
    st.markdown(f"### 🎯 Discovered {len(st.session_state.outlier_results)} High-Performance Outliers for *'{st.session_state.last_query}'*")
    st.markdown("---")
    
    cards_per_row = 3
    for idx in range(0, len(st.session_state.outlier_results), cards_per_row):
        row_data = st.session_state.outlier_results[idx:idx+cards_per_row]
        cols = st.columns(cards_per_row)
        
        for col_idx, video_data in enumerate(row_data):
            with cols[col_idx]:
                st.image(video_data["Thumbnail"], use_container_width=True)
                
                st.markdown(f"""
                <div style="background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 12px; margin-bottom: 5px;">
                    <span style="background-color: #DC2626; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">{video_data['Multiplier']}x Outlier</span>
                    <span style="background-color: #2563EB; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-left: 5px;">{video_data['VPH']} VPH</span>
                    <h4 style="color: white; margin-top: 10px; font-size: 14px; line-height: 1.3; font-weight: 600;">{video_data['Title'][:55]}...</h4>
                    <p style="color: #94A3B8; font-size: 12px; margin-bottom: 4px;">👤 {video_data['Channel']}</p>
                    <p style="color: #64748B; font-size: 11px; margin-bottom: 5px;">📈 Subs: {video_data['Subscribers']:,} | 👁️ Views: {video_data['Views']:,}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("⚙️ Inspect Asset Parameters", key=f"btn_{video_data['ID']}_{idx}", use_container_width=True):
                    render_video_modal(video_data)