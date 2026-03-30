import streamlit as st
import startup  # Runs once per server process — writes a fresh server_run.id
import customer_view as customer
import shop_view as vendor
import chatbot as assistant
import admin_view as admin
import base64
import session_manager as sm

# Set Page Config
st.set_page_config(
    page_title="Bridora | Bridal Jewels", 
    page_icon="💍", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Background and Glassmorphism System
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_global_styles():
    try:
        bg_img = get_base64('assets/bgimg3.jpeg')
        style = f'''
        <style>
        
/* SIDEBAR FONT & ALIGNMENT UPGRADE */
        [data-testid="stSidebar"] label p {{
            font-family: 'Playfair Display', serif !important;
            font-size: 1.15rem !important;
            font-weight: 600 !important;
            text-align: left !important;
            padding-left: 10px !important;
            color: #000000 !important;
            letter-spacing: 1px !important;
        }}
        [data-testid="stSidebar"] .st-emotion-cache-1px78p {{
              padding-left: 0px !important;
        }}
        
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bg_img}");
            background-size: cover;
            background-attachment: fixed;
            color: #000000 !important;
        }}
        /* High-Contrast Light Overlay for Black Text */
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.85);
            border-radius: 20px;
            padding: 3rem;
            margin-top: 3rem;
            margin-bottom: 3rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
            border: 1px solid rgba(0, 0, 0, 0.1);
            color: #000000 !important;
        }}
        /* High Contrast Buttons */
        .stButton>button {{ 
            border-radius: 8px;
            background-color: rgba(0, 0, 0, 0.05);
            color: #000000;
            border: 1px solid rgba(0, 0, 0, 0.2);
        }}
        /* Force Black Text everywhere */
        h1, h2, h3, h4, p, span, caption, label, .stMarkdown, .stSubheader {{
            color: #000000 !important;
        }}
        </style>
        '''
        st.markdown(style, unsafe_allow_html=True)
    except:
        # Fallback if image not found
        st.markdown("<style>.main { background-color: #fafafa; color: black; }</style>", unsafe_allow_html=True)

set_global_styles()

# Detect fresh browser load vs Streamlit rerun
# On a fresh load, session_state has zero keys.
# On a rerun (e.g. after logout), it already has keys like 'page'.
_is_fresh_load = len(st.session_state.to_dict()) == 0

# Initialize page state
if 'page' not in st.session_state:
    st.session_state.page = "home"

# Only restore saved sessions on a fresh page load.
# On reruns (e.g. logout click), we skip restore so the logout sticks.
if _is_fresh_load:
    sm.restore_sessions()

# --- Main Navigation (Sidebar Restoration) ---
# Small Round Logo for Sidebar
st.sidebar.markdown("""
    <style>
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        border-radius: 50% !important;
        border: 2px solid #fec5d1 !important;
        width: 80px !important;
        height: 80px !important;
        object-fit: cover !important;
        margin-left: auto;
        margin-right: auto;
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.image("assets/bridoralogo.jpeg")
    st.title("Bridora")

    # Customer login/logout status indicator
    if 'customer' in st.session_state:
        cust = st.session_state.customer
        st.sidebar.success(f"{cust['full_name']}")
        if st.sidebar.button("👤 My Account", key="cust_account_btn", use_container_width=True):
            st.session_state.page = "customer_login"
            st.rerun()
        if st.sidebar.button("🚪 Logout", key="cust_logout", use_container_width=True):
            del st.session_state.customer
            st.session_state.page = "home"
            st.rerun()
    else:
        if st.sidebar.button("Customer Login", key="cust_login_btn"):
            st.session_state.pre_login_page = st.session_state.get('page', 'browse')
            st.session_state.page = "customer_login"
            st.rerun()

menu_options = ["Home", "Browse", "Shops", "Admin", "Help"]

current_menu_choice = st.sidebar.radio("Main Menu", menu_options)

# Handle Navigation
if "last_choice" not in st.session_state:
    st.session_state.last_choice = current_menu_choice

if current_menu_choice != st.session_state.last_choice:
    if current_menu_choice == "Home": st.session_state.page = "home"
    elif current_menu_choice == "Browse": st.session_state.page = "browse"
    elif current_menu_choice == "Shops": 
        if 'is_vendor' in st.session_state: st.session_state.page = "shop_dashboard"
        else: st.session_state.page = "shop_login"
    elif current_menu_choice == "Admin": 
        if 'is_admin' in st.session_state: st.session_state.page = "admin_panel"
        else: st.session_state.page = "admin_login"
    elif current_menu_choice == "Help": st.session_state.page = "chatbot"
    st.session_state.last_choice = current_menu_choice
    st.rerun()

# Page Routing
if st.session_state.page == "home":
    customer.render_home()
elif st.session_state.page == "browse":
    customer.render_browse()
elif st.session_state.page == "details":
    customer.render_details()
elif st.session_state.page == "customer_login":
    customer.render_customer_login()
elif st.session_state.page == "shop_login":
    vendor.render_shop_login()
elif st.session_state.page == "shop_dashboard":
    vendor.render_shop_dashboard()
elif st.session_state.page == "admin_login":
    admin.render_admin_login()
elif st.session_state.page == "admin_panel":
    admin.render_admin_panel()
elif st.session_state.page == "chatbot":
    assistant.render_chatbot_ui()

# Shared Footer
st.sidebar.divider()
st.sidebar.caption("© 2026 Bridora | Sri Lankan Bridal Excellence")

# Persist current login state to file (survives page refresh)
sm.sync_sessions()
