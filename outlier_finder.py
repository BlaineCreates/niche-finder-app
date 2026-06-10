import os
import csv
from datetime import datetime
from googleapiclient.discovery import build

# =====================================================================
# CONFIGURATION
# Paste your secure Google API Key inside the quotes below.
# =====================================================================
API_KEY = "AIzaSyAmj1qpr1V9IPF7BxFGO_xYaXcumY84IYE"

# ADJUSTABLE FILTER: Set this to 2.0 for steady hits, 5.0 for viral, or 10.0 for extreme outliers
TARGET_MULTIPLIER = 5.0 

def get_outlier_tier(ratio):
    """Assigns a professional visual tier rating based on the performance multiplier."""
    if ratio >= 50.0:
        return f"⭐ CRITICAL HIT ({ratio:.1f}x)"
    elif ratio >= 10.0:
        return f"🔥 VIRAL ({ratio:.1f}x)"
    elif ratio >= 5.0:
        return f"🚀 STRONG ({ratio:.1f}x)"
    return f"✅ STEADY ({ratio:.1f}x)"

def find_niche_outliers(niche_keyword):
    """
    Scans a niche, analyzes advanced metrics (views, likes, comments, age),
    calculates outlier scores, and exports a comprehensive spreadsheet report.
    """
    youtube = build("youtube", "v3", developerKey=API_KEY)
    print(f"\n[Engine] Initializing Master Scan for niche: '{niche_keyword}'")
    print(f"[Engine] Filtering for content performing >= {TARGET_MULTIPLIER}x channel baseline...\n")
    
    # 1. Fetch recent top videos in the selected niche
    search_response = youtube.search().list(
        q=niche_keyword,
        type="video",
        part="id,snippet",
        maxResults=20  # Increased for a more thorough niche analysis
    ).execute()
    
    video_items = search_response.get("items", [])
    outliers_found = []
    
    print("===================== MASTER VIRAL REPORT =====================")
    
    for item in video_items:
        video_id = item["id"]["videoId"]
        video_title = item["snippet"]["title"]
        channel_id = item["snippet"]["channelId"]
        channel_title = item["snippet"]["channelTitle"]
        published_raw = item["snippet"]["publishedAt"]
        
        # Format the ISO timestamp into a clean, readable date (YYYY-MM-DD)
        clean_date = published_raw.split("T")[0]
        
        # 2. Extract advanced video statistics (Views, Likes, Comments)
        video_details = youtube.videos().list(id=video_id, part="statistics").execute()
        stats = video_details["items"][0]["statistics"]
        
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))
        
        # 3. Extract channel subscriber baseline
        channel_details = youtube.channels().list(id=channel_id, part="statistics").execute()
        subs = int(channel_details["items"][0]["statistics"].get("subscriberCount", 0))
        
        if subs == 0:
            continue
            
        # 4. Execute Core Math Engine
        outlier_ratio = views / subs
        
        # 5. Filter and Structure Master Data
        if outlier_ratio >= TARGET_MULTIPLIER:
            tier_rating = get_outlier_tier(outlier_ratio)
            
            print(f"{tier_rating} Performance!")
            print(f"   Video:   {video_title}")
            print(f"   Channel: {channel_title} ({subs:,} Subs)")
            print(f"   Metrics: {views:,} Views | {likes:,} Likes | {comments:,} Comments")
            print(f"   Posted:  {clean_date}")
            print("-" * 64)
            
            outliers_found.append({
                "Outlier Rating": tier_rating,
                "Multiplier Ratio": round(outlier_ratio, 2),
                "Video Title": video_title,
                "Channel Name": channel_title,
                "Subscribers": subs,
                "Views": views,
                "Likes": likes,
                "Comments": comments,
                "Publish Date": clean_date,
                "YouTube URL": f"https://www.youtube.com/watch?v={video_id}"
            })

    # ==========================================
    # ENTERPRISE SPREADSHEET EXPORT ENGINE
    # ==========================================
    if outliers_found:
        # Sort data automatically so the highest outlier is always at the very top of the spreadsheet
        outliers_found = sorted(outliers_found, key=lambda x: x["Multiplier Ratio"], reverse=True)
        
        safe_filename = niche_keyword.replace(" ", "_").lower()
        filename = f"{safe_filename}_master_outliers.csv"
        headers = outliers_found[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=headers)
            dict_writer.writeheader()
            dict_writer.writerows(outliers_found)
            
        print(f"\n✅ SUCCESS: Compiled {len(outliers_found)} premium concepts into '{filename}'!")
        print("[Engine] Data sorted by maximum performance multiplier. Ready for user download.")
    else:
        print("\nScan complete. No extreme anomalies detected. Consider adjusting target multiplier parameters.")

if __name__ == "__main__":
    target_niche = "faceless AI automation"
    
    if API_KEY == "YOUR_GOOGLE_API_KEY_HERE":
        print("Configuration Error: Please assign a valid Google API key to line 11.")
    else:
        find_niche_outliers(target_niche)