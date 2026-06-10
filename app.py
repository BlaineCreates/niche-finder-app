import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import os

# ==============================================================================
# # CREDENTIALS VAULT
# ==============================================================================
API_KEY = st.secrets["GOOGLE_API_KEY"]

# Premium Minimalist UI Design Configuration
st.set_page_config(
    page_title="Outlier Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom High-End Styling Injection (Steve Jobs / Minimalist Dark Mode)
st.markdown("""
    <style>
    .main { background-color: #0A0F1D; color: #FFFFFF; }
    h1 { font-weight: 800; tracking: -0.05em; color: #FFFFFF; }
    .stButton>button {
        background-color: #1E293B;
        color: #FFFFFF;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2563EB;
        border-color: #3b82f6;
    }
    div[data-testid="stForm"] {
        border: 1px solid #1E293B;
        background-color: #0F172A;
        padding: 2rem;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize global authentication tracking
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ------------------------------------------------------------------------------
# THE VAULT DOOR: LOGIN SCREEN FRONTEND
# ------------------------------------------------------------------------------
if not st.session_state.authenticated:
    st.title("Outlier Intelligence")
    st.write("Please authenticate to access the market database.")
    
    with st.form("login_form", clear_on_submit=False):
        user_email = st.text_input("Authorized Email Address")
        user_password = st.text_input("Access Password", type="password")
        submit_auth = st.form_submit_button("Unlock Dashboard")
        
        if submit_auth:
            user_registry = st.secrets.get("passwords", {})
            if user_email in user_registry and user_registry[user_email] == user_password:
                st.session_state.authenticated = True
                st.success("Access Granted! Loading system...")
                st.rerun()
            else:
                st.error("Access Denied. Invalid credentials or unauthorized account.")
    st_stop = True
else:
    st_stop = False

# ------------------------------------------------------------------------------
# PREMIUM DASHBOARD APPLICATION MECHANICS
# ------------------------------------------------------------------------------
if not st_stop:
    st.title("Outlier Intelligence Dashboard")
    st.markdown("Identify high-performing content angles by uncovering videos that violently outperform their channel baseline size.")
    st.markdown("---")

    column_left, column_right = st.columns(2)

    with column_left:
        target_niche = st.text_input(
            "Target Niche / Search Query",
            value="faceless AI automation",
            help="Enter the market vertical or topic area you wish to scan."
        )

    with column_right:
        target_multiplier = st.slider(
            "Minimum Outlier Performance Multiplier",
            min_value=2.0,
            max_value=20.0,
            value=5.0,
            step=0.5,
            help="Filters for videos that pulled X times more views than the channel has subscribers."
        )

    trigger_scan = st.button("Run Market Intelligence Scan")

    def get_outlier_tier(ratio):
        if ratio >= 50.0: return f"⭐ CRITICAL HIT ({ratio:.1f}x)"
        elif ratio >= 10.0: return f"🔥 VIRAL ({ratio:.1f}x)"
        elif ratio >= 5.0: return f"🚀 STRONG ({ratio:.1f}x)"
        return f"✅ STEADY ({ratio:.1f}x)"

    if trigger_scan:
        if API_KEY == "YOUR_GOOGLE_API_KEY_HERE":
            st.error("Configuration Error: Please assign a valid Google API key inside your secrets configuration.")
        else:
            with st.spinner("Connecting to YouTube Data API v3 and processing baseline ratios..."):
                try:
                    youtube = build("youtube", "v3", developerKey=API_KEY)

                    search_response = youtube.search().list(
                        q=target_niche,
                        type="video",
                        part="id,snippet",
                        maxResults=25
                    ).execute()

                    video_items = search_response.get("items", [])
                    compiled_results = []

                    for item in video_items:
                        video_id = item["id"]["videoId"]
                        video_title = item["snippet"]["title"]
                        channel_id = item["snippet"]["channelId"]
                        channel_title = item["snippet"]["channelTitle"]
                        published_raw = item["snippet"]["publishedAt"].split("T")[0]

                        video_details = youtube.videos().list(id=video_id, part="statistics").execute()
                        stats = video_details["items"][0]["statistics"]

                        views = int(stats.get("viewCount", 0))
                        likes = int(stats.get("likeCount", 0))
                        comments = int(stats.get("commentCount", 0))

                        channel_details = youtube.channels().list(id=channel_id, part="statistics").execute()
                        subs = int(channel_details["items"][0]["statistics"].get("subscriberCount", 0))

                        if subs == 0: continue

                        outlier_ratio = views / subs

                        if outlier_ratio >= target_multiplier:
                            tier_rating = get_outlier_tier(outlier_ratio)
                            compiled_results.append({
                                "Rating": tier_rating,
                                "Multiplier": round(outlier_ratio, 1),
                                "Thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
                                "Video Title": video_title,
                                "Channel Name": channel_title,
                                "Subscribers": subs,
                                "Views": views,
                                "Likes": likes,
                                "Comments": comments,
                                "Publish Date": published_raw,
                                "URL": f"https://www.youtube.com/watch?v={video_id}"
                            })

                    if compiled_results:
                        data_table = pd.DataFrame(compiled_results)
                        data_table = data_table.sort_values(by="Multiplier", ascending=False)
                        
                        # Definitively enforce structural column order layout mapping
                        data_table = data_table[["Rating", "Multiplier", "Thumbnail", "Video Title", "Channel Name", "Subscribers", "Views", "Likes", "Comments", "Publish Date", "URL"]]

                        total_discoveries = len(data_table)
                        maximum_multiplier = data_table["Multiplier"].max()

                        metric_col_1, metric_col_2 = st.columns(2)
                        with metric_col_1:
                            st.metric("Outliers Uncovered", f"{total_discoveries} Videos")
                        with metric_col_2:
                            st.metric("Peak Multiplier Performance", f"{maximum_multiplier}x")

                        st.markdown("### Market Analysis Report")

                        st.dataframe(
                            data_table,
                            column_config={
                                "Thumbnail": st.column_config.ImageColumn("Preview"),
                                "URL": st.column_config.LinkColumn("Watch Video Link")
                            },
                            hide_index=True,
                            use_container_width=True
                        )

                        csv_bytes = data_table.to_csv(index=False, encoding='utf-8').encode('utf-8')
                        safe_filename = target_niche.replace(" ", "_").lower()

                        st.download_button(
                            label="📦 Export Intelligence Report to CSV Spreadsheet",
                            data=csv_bytes,
                            file_name=f"{safe_filename}_market_intelligence.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("No anomalies detected matching this exact performance threshold. Try expanding search query parameters.")
                except Exception as system_error:
                    st.error(f"System Core Error: {system_error}")