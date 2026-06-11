import streamlit as st

# Premium Minimalist UI Design Configuration
st.set_page_config(
    page_title="Outlier Intelligence Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize global authentication tracking
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Custom Styling Injection (Minimalist Dark Mode across pages)
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

# ------------------------------------------------------------------------------
# THE VAULT DOOR: LOGIN GATEWAY
# ------------------------------------------------------------------------------
if not st.session_state.authenticated:
    st.title("Outlier Intelligence")
    st.write("Please authenticate to unlock your research master suite.")
    
    with st.form("login_form", clear_on_submit=False):
        user_email = st.text_input("Authorized Email Address")
        user_password = st.text_input("Access Password", type="password")
        submit_auth = st.form_submit_button("Unlock Platform Dashboard")
        
        if submit_auth:
            user_registry = st.secrets.get("passwords", {})
            if user_email in user_registry and user_registry[user_email] == user_password:
                st.session_state.authenticated = True
                st.success("Access Granted! Loading system architecture...")
                st.rerun()
            else:
                st.error("Access Denied. Invalid credentials or unauthorized account.")

# ------------------------------------------------------------------------------
# MULTI-PAGE PLATFORM NAVIGATION HUB (ALL 3 PAGES REGISTERED)
# ------------------------------------------------------------------------------
else:
    # Setup your native sidebar directory mapping
    outlier_page = st.Page("pages/1_Outlier_Finder.py", title="Outlier Analytics Finder", icon="🔍")
    keyword_page = st.Page("pages/2_Keyword_Research.py", title="Keyword Volume Suite", icon="📊")
    vault_page = st.Page("pages/3_Thumbnail_Vault.py", title="Thumbnail Inspiration Vault", icon="🖼️")
    
    # Run the modern sidebar multi-page engine
    navigation_hub = st.navigation([outlier_page, keyword_page, vault_page])
    navigation_hub.run()