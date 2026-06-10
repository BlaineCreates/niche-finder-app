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

# ------------------------------------------------------------------------------
# PREMIUM ADVANCED FILTER TRAY
# ------------------------------------------------------------------------------
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
        max_views = st.slider("Maximum Total Views Limit", min_value=1000, max_value=10000000, value=5000000, step=50000, help="Helps filter out mega-viral anomalies if you want low-hanging fruit.")
    with col_subs:
        min_subs = st.slider("Minimum Channel Subscribers", min_value=0, max_value=500000, value=1000, step=1000, help="Filters out brand new channels with 0-10 subscribers that distort ratios.")

trigger_scan = st.button("🚀 Run Deep Market Intelligence Scan", use_container_width=True)

# Helper function to convert ISO 8601 duration string (PT1M30S) to total seconds
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
    with st.spinner("Executing Deep-Page Sweep (Scanning 100+ items deep for hidden anomalies)..."):
        try:
            youtube = build("youtube", "v3", developerKey=API_KEY)
            compiled_results = []
            next_page_token = None
            
            # Dynamic date cutoff calculation
            published_after = None
            if time_frame == "Last 7 Days":
                published_after = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"
            elif time_frame == "Last 30 Days":
                published_after = (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"
            elif time_frame == "Last 90 Days":
                published_after = (datetime.utcnow() - timedelta(days=90)).isoformat() + "Z"

            # Execute 2 structural sequential page sweeps (50 results per page max = 100 deep scans)
            for loop_page in range(2):
                search_kwargs = {
                    "q": target_niche,
                    "type": "video",
                    "part": "id,snippet",
                    "maxResults": 50,
                    "pageToken": next_page_token
                }
                if published_after:
                    search_kwargs["publishedAfter"] = published_after
                    
                search_response = youtube.search().list(**search_kwargs).execute()
                video_items = search_response.get("items", [])
                next_page_token = search_response.get("nextPageToken")
                
                if not video_items:
                    break

                # Extract IDs for batch processing metrics
                v_ids = [item["id"]["videoId"] for item in video_items]
                
                # Fetch Video statistics AND contentDetails (durations) concurrently
                v_details = youtube.videos().list(id=",".join(v_ids), part="statistics,contentDetails").execute()
                v_dict = {v["id"]: v for v in v_details.get("items", [])}
                
                # Extract distinct channel IDs for batch processing subscription metrics
                c_ids = list(set([item["snippet"]["channelId"] for item in video_items]))
                c_details = youtube.channels().list(id=",".join(c_ids), part="statistics").execute()
                c_dict = {c["id"]: c for c in c_details.get("items", [])}

                for item in video_items:
                    video_id = item["id"]["videoId"]
                    video_title = item["snippet"]["title"]
                    channel_id = item["snippet"]["channelId"]
                    channel_title = item["snippet"]["channelTitle"]
                    published_raw = item["snippet"]["publishedAt"].split("T")[0]

                    # Match stats
                    v_meta = v_dict.get(video_id)
                    if not v_meta: continue
                    
                    stats = v_meta["statistics"]
                    duration_raw = v_meta["contentDetails"]["duration"]
                    duration_seconds = parse_duration(duration_raw)

                    # Format Type Filtering
                    if format_filter == "Long-form Only ( > 60s )" and duration_seconds <= 60: continue
                    if format_filter == "Shorts Only ( < 60s )" and duration_seconds > 60: continue

                    views = int(stats.get("viewCount", 0))
                    likes = int(stats.get("likeCount", 0))
                    comments = int(stats.get("commentCount", 0))

                    # View Threshold Check
                    if views > max_views: continue

                    # Match channel stats
                    c_meta = c_dict.get(channel_id)
                    if not c_meta: continue
                    subs = int(c_meta["statistics"].get("subscriberCount", 0))

                    # Subscriber Boundary Check
                    if subs < min_subs or subs == 0: continue

                    # Calculate precise metrics
                    outlier_ratio = views / subs
                    
                    # Calculate Views Per Hour (VPH)
                    pub_datetime = datetime.strptime(item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
                    hours_elapsed = max((datetime.utcnow() - pub_datetime).total_seconds() / 3600, 1.0)
                    vph = int(views / hours_elapsed)

                    if outlier_ratio >= target_multiplier:
                        compiled_results.append({
                            "Multiplier": round(outlier_ratio, 1),
                            "VPH": vph,
                            "Thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
                            "Title": video_title,
                            "Channel": channel_title,
                            "Subscribers": subs,
                            "Views": views,
                            "URL": f"https://www.youtube.com/watch?v={video_id}"
                        })
            
            # ------------------------------------------------------------------
            # UI GRID CARD RENDERING (VidIQ INSPIRED LAYOUT)
            # ------------------------------------------------------------------
            if compiled_results:
                df = pd.DataFrame(compiled_results).sort_values(by="Multiplier", ascending=False)
                
                st.markdown(f"### 🎯 Discovered {len(df)} High-Performance Outliers")
                st.markdown("---")
                
                # Render clean 3-column responsive card layouts
                cards_per_row = 3
                for idx in range(0, len(df), cards_per_row):
                    row_data = df.iloc[idx:idx+cards_per_row]
                    cols = st.columns(cards_per_row)
                    
                    for col_idx, (_, row) in enumerate(row_data.iterrows()):
                        with cols[col_idx]:
                            # High Impact Image Card Presentation Wrapper
                            st.image(row["Thumbnail"], use_container_width=True)
                            
                            # Custom metric micro-badges using clean markup
                            st.markdown(f"""
                            <div style="background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 12px; margin-bottom: 20px;">
                                <span style="background-color: #DC2626; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">{row['Multiplier']}x Outlier</span>
                                <span style="background-color: #2563EB; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-left: 5px;">{row['VPH']} VPH</span>
                                <h4 style="color: white; margin-top: 10px; font-size: 15px; line-height: 1.3; font-weight: 600;">{row['Title'][:65]}...</h4>
                                <p style="color: #94A3B8; font-size: 13px; margin-bottom: 4px;">👤 {row['Channel']}</p>
                                <p style="color: #64748B; font-size: 12px; margin-bottom: 12px;">📈 Subs: {row['Subscribers']:,} | 👁️ Views: {row['Views']:,}</p>
                                <a href="{row['URL']}" target="_blank" style="display: block; text-align: center; background-color: #1E293B; color: white; border: 1px solid #334155; padding: 6px; border-radius: 6px; font-weight: 500; text-decoration: none; font-size: 13px;">Open Video Link ↗️</a>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.warning("No anomalies found matching those exact limits. Try decreasing the outlier threshold or widening your criteria.")
                
        except Exception as e:
            st.error(f"Data Scan Failure: {e}")