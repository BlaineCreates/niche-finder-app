import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Safety gate check
if not st.session_state.get("authenticated", False):
    st.warning("Security alert: Access denied. Please authenticate at the front gate.")
    st.stop()

API_KEY = st.secrets["GOOGLE_API_KEY"]

st.title("🔍 Outlier Analytics Finder")
st.markdown("Uncover videos that violently outperform their channel baseline size to find proven viral angles.")
st.markdown("---")

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
# THE QUICK ACTION DIALOG OVERLAY (VidIQ SPECIFIC POPUP MODAL)
# ------------------------------------------------------------------------------
@st.dialog("🎬 Asset Inspection & Quick Actions", width="large")
def render_video_modal(video_data):
    st.image(video_data["Thumbnail"], use_container_width=True)
    st.subheader(video_data["Title"])
    st.caption(f"👤 Channel: {video_data['Channel']} | 📅 Published: {video_data['Published']}")
    st.markdown("---")
    
    # Quantitative Metric Blocks
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Outlier Multiplier", f"{video_data['Multiplier']}x")
    with col_m2:
        st.metric("Total Views", f"{video_data['Views']:,}")
    with col_m3:
        st.metric("Views Per Hour", f"{video_data['VPH']:,}/hr")
    with col_m4:
        # Engagement Calculation Labeling Logic
        engagement_label = "🔥 Explosive" if video_data["Engagement"] >= 8.0 else ("✅ Stable" if video_data["Engagement"] >= 3.0 else "⚠️ Weak")
        st.metric("Engagement Grade", engagement_label)

    st.markdown("### 🛠️ Strategic Asset Triggers")
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.link_button("🌐 Open Video on YouTube ↗️", video_data["URL"], use_container_width=True)
    with col_b2:
        if st.button("📝 Remix Asset Titles", use_container_width=True):
            st.info(f"💡 Alternative Hook Idea:\n**'The Insane Secret Behind This {video_data['Multiplier']}x Viral Asset!'**")
    with col_b3:
        if st.button("🎨 Remix Thumbnails", use_container_width=True):
            st.success("✨ Sent layout footprint to design queue! Alternative generated: High-Contrast face right, bright text left.")

    col_b4, col_b5 = st.columns(2)
    with col_b4:
        if st.button("🔍 Find Similar Titles", use_container_width=True):
            st.write(f"Scouting database nodes matching keyword patterns similar to: *'{video_data['Title'][:30]}...'*")
    with col_b5:
        if st.button("🎯 Flag Channel as Competitor", use_container_width=True):
            st.toast(f"Added {video_data['Channel']} to your global dashboard monitoring deck!")

# Helper duration parser
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
                    
                    # Calculate VPH & Engagement Potential
                    pub_datetime = datetime.strptime(item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
                    hours_elapsed = max((datetime.utcnow() - pub_datetime).total_seconds() / 3600, 1.0)
                    vph = int(views / hours_elapsed)
                    
                    # Engagement percentage calculation
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
            
            if compiled_results:
                st.markdown(f"### 🎯 Discovered {len(compiled_results)} High-Performance Outliers")
                st.markdown("---")
                
                cards_per_row = 3
                for idx in range(0, len(compiled_results), cards_per_row):
                    row_data = compiled_results[idx:idx+cards_per_row]
                    cols = st.columns(cards_per_row)
                    
                    for col_idx, video_data in enumerate(row_data):
                        with cols[col_idx]:
                            st.image(video_data["Thumbnail"], use_container_width=True)
                            
                            # Clean, scannable block with clear text button hook
                            st.markdown(f"""
                            <div style="background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 12px; margin-bottom: 5px;">
                                <span style="background-color: #DC2626; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">{video_data['Multiplier']}x Outlier</span>
                                <span style="background-color: #2563EB; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-left: 5px;">{video_data['VPH']} VPH</span>
                                <h4 style="color: white; margin-top: 10px; font-size: 14px; line-height: 1.3; font-weight: 600;">{video_data['Title'][:55]}...</h4>
                                <p style="color: #94A3B8; font-size: 12px; margin-bottom: 4px;">👤 {video_data['Channel']}</p>
                                <p style="color: #64748B; font-size: 11px; margin-bottom: 5px;">📈 Subs: {video_data['Subscribers']:,} | 👁️ Views: {video_data['Views']:,}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Interactive button mapping that fires the overlay modal function
                            if st.button("⚙️ Inspect Asset Parameters", key=f"btn_{video_data['ID']}", use_container_width=True):
                                render_video_modal(video_data)
            else:
                st.warning("No anomalies found matching those exact criteria.")
                
        except Exception as e:
            st.error(f"Data Scan Failure: {e}")