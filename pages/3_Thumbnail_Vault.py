import streamlit as st
from googleapiclient.discovery import build

# Safety gate check
if not st.session_state.get("authenticated", False):
    st.warning("Security alert: Access denied. Please authenticate at the front gate.")
    st.stop()

API_KEY = st.secrets["GOOGLE_API_KEY"]

st.title("🖼️ Thumbnail Inspiration Vault")
st.markdown("Type any topic or niche below to pull up a massive visual wall of high-performing thumbnails to inspire your next layout.")
st.markdown("---")

# User Interface
search_query = st.text_input("Enter Niche / Content Angle for Visual Inspection", value="faceless AI automation style")
col_sc1, col_sc2 = st.columns(2)
with col_sc1:
    search_depth = st.slider("Visual Scan Depth (Total Thumbnails)", min_value=12, max_value=48, value=24, step=6)
with col_sc2:
    sort_order = st.selectbox("Rank Baseline Alignment", ["Most Relevant", "Highest Total Views"])

trigger_vault_scan = st.button("🔥 Generate Visual Inspiration Wall", use_container_width=True)

if trigger_vault_scan:
    with st.spinner("Harvesting thumbnail textures and compiling visual layout array..."):
        try:
            youtube = build("youtube", "v3", developerKey=API_KEY)
            
            # Map user sorting parameters to API keys
            api_order = "relevance" if sort_order == "Most Relevant" else "viewCount"
            
            # Execute batch search request
            search_response = youtube.search().list(
                q=search_query,
                type="video",
                part="id,snippet",
                maxResults=search_depth,
                order=api_order
            ).execute()
            
            video_items = search_response.get("items", [])
            
            if video_items:
                st.markdown(f"### 🎯 Showing {len(video_items)} Top Layouts for *'{search_query}'*")
                st.markdown("---")
                
                # Render clean, massive 3-column responsive thumbnail cards
                cols_per_row = 3
                for idx in range(0, len(video_items), cols_per_row):
                    chunk = video_items[idx:idx+cols_per_row]
                    cols = st.columns(cols_per_row)
                    
                    for col_idx, item in enumerate(chunk):
                        video_id = item["id"]["videoId"]
                        title = item["snippet"]["title"]
                        channel = item["snippet"]["channelTitle"]
                        
                        # Fetch the high-quality maxres thumbnail resolution string
                        hq_thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                        fallback_thumbnail_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                        
                        with cols[col_idx]:
                            # Try loading MaxRes, fallback to standard if user upload duration dictates it
                            try:
                                st.image(hq_thumbnail_url, use_container_width=True)
                            except:
                                st.image(fallback_thumbnail_url, use_container_width=True)
                                
                            # Minimalist typography to keep absolute focus on the thumbnail graphics
                            st.markdown(f"""
                            <div style="margin-bottom: 25px; margin-top: -5px; padding: 5px;">
                                <h5 style="color: #E2E8F0; font-size: 13px; line-height: 1.3; font-weight: 500; margin-bottom: 2px;">{title[:55]}...</h5>
                                <p style="color: #64748B; font-size: 11px;">👤 {channel}</p>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.warning("No visual elements discovered for this specific search string.")
                
        except Exception as err:
            st.error(f"Visual Vault Core Error: {err}")