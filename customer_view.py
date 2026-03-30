import streamlit as st
import pandas as pd
from storage import load_json, add_record
from backend import submit_booking, verify_login, check_duplicate_account

def render_home():
    """Home View: Welcome page for brides."""
    # ABSOLUTE MASTER CENTERING SYSTEM
    st.markdown("""
        <style>
        /* Force main container to use flex centering */
        .main .block-container {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            padding-top: 5rem !important;
            width: 100% !important;
        }

        /* Target Streamlit's internal vertical block to center children */
        .main [data-testid="stVerticalBlock"], 
        .main [data-testid="stVerticalBlock"] > div,
        .main [data-testid="element-container"] {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            text-align: center !important;
        }

        /* Center all text specifically */
        .main h1, .main h2, .main h3, .main .stMarkdown, .main p, .main .stCaption, .main .stSubheader {
            text-align: center !important;
            width: 100% !important;
        }

        /* Logo Perfection */
        .main [data-testid="stImage"] img { 
            border-radius: 50% !important; 
            border: 3px solid #FF69B4 !important;
            aspect-ratio: 1/1 !important;
            object-fit: cover !important;
            width: 250px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15) !important;
            margin-bottom: 20px !important;
        }

        /* Button Perfection */
        .main .stButton button {
            width: 300px !important;
            margin-top: 30px !important;
            color: white !important;
            border: 1px solid #000000 !important;
            padding: 10px 20px !important;
            font-weight: bold !important;
        }
        </style>
        """, unsafe_allow_html=True)

    import base64, os
    logo_path = "assets/bridoralogo.jpeg"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <div style="display:flex; flex-direction:column; align-items:center; width:100%; margin-bottom:20px;">
                <img src="data:image/jpeg;base64,{logo_b64}"
                     style="width:250px; height:250px; border-radius:50%; 
                            border:5px solid #FF69B4; object-fit:cover;
                            box-shadow: 0 10px 30px rgba(0,0,0,0.2);" />
            </div>
        """, unsafe_allow_html=True)

    # Branding Text — all centered via inline styles
    st.markdown('<h1 style="text-align:center;">💖 Bridora</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align:center; font-weight:400;">Your Dream Wedding, Found One Set at a Time.</h3>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:gray;">Sri Lanka\'s Exclusive Bridal Jewelry Marketplace</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; max-width:600px; margin:0 auto;">Bridora is a specialized platform for brides and jewelry shops in Sri Lanka. Browse through extensive collections of the finest Gold sets.</p>', unsafe_allow_html=True)

    # Centered Browse Button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Browse Catalog", key="master_center_btn", use_container_width=True):
            st.session_state.page = "browse"
            st.rerun()


def render_browse():
    """Catalog View: Jewelry Gallery and Filtering."""
    st.title("Browse Jewelry")
    jewelry_data = load_json('jewelry.json')
    shops_data = load_json('shops.json')
    
    # 1. Presence Check: Only show items from shops that still exist
    active_shop_ids = [s.get('id') for s in shops_data]
    jewelry_data = [item for item in jewelry_data if item.get('shop_id') in active_shop_ids]
    
    if not jewelry_data:
        st.info("No jewelry items available right now. Check back later!")
        return

    # Filter Bar
    col1, col2, col3 = st.columns(3)
    with col1:
        price_range = st.slider("Max Price (LKR)", 1000, 500000, 500000)
    with col2:
        style_choice = st.multiselect("Styles", ["Temple", "Gold", "Modern"], default=["Temple", "Gold", "Modern"])
    with col3:
        available_only = st.checkbox("Available Only", value=True)
    
    # Filter Logic
    filtered_items = [
        item for item in jewelry_data 
        if (item.get('rental_price', 0) <= price_range or item.get('sale_price', 0) <= price_range)
        and item.get('style') in style_choice
        and (not available_only or item.get('availability', 'Yes') == 'Yes')
    ]
    
    if not filtered_items:
        st.warning("No items match your filters.")
    else:
        # Force uniform image height in gallery
        st.markdown("""
            <style>
            [data-testid="stImage"] img {
                height: 280px !important;
                object-fit: cover !important;
                width: 100% !important;
                border-radius: 8px !important;
            }
            </style>
        """, unsafe_allow_html=True)
        # Gallery Grid
        for i in range(0, len(filtered_items), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(filtered_items):
                    item = filtered_items[i+j]
                    with cols[j]:
                        img_path = item.get('image_url', "https://via.placeholder.com/300x300?text=No+Preview")
                        st.image(img_path, use_container_width=True)
                        st.subheader(item['name'])
                        st.write(f"**Style:** {item['style']}")
                        prices = []
                        if item.get('rental_price', 0) > 0: prices.append(f"Rent: LKR {item['rental_price']}/d")
                        if item.get('sale_price', 0) > 0: prices.append(f"Buy: LKR {item['sale_price']}")
                        st.write(f"**{" & ".join(prices) if prices else 'Enquire for Price'}**")
                        st.write(f"**Shop:** {item.get('shop_name', 'Verified Shop')}")
                        if st.button(f"View Details", key=f"details_{item['id']}", use_container_width=False):
                            st.session_state.selected_item = item
                            st.session_state.page = "details"
                            st.rerun()

def render_details():
    """Details View: Full item info and booking form."""
    if 'selected_item' not in st.session_state:
        st.session_state.page = "browse"
        st.rerun()
        
    item = st.session_state.selected_item
    st.title(f"{item['name']}")
    col1, col2 = st.columns(2)
    with col1:
        img_path = item.get('image_url', "https://via.placeholder.com/600x400?text=Premium+Bridal+Set")
        st.image(img_path, use_container_width=True)
    with col2:
        pricing_info = ""
        if item.get('rental_price', 0) > 0: pricing_info += f"### Rental: LKR {item['rental_price']} / day\n"
        if item.get('sale_price', 0) > 0: pricing_info += f"### Buy: LKR {item['sale_price']}\n"
        st.markdown(pricing_info)
        st.write(f"**Style:** {item['style']}")
        st.write(f"**Shop:** {item.get('shop_name', 'Verified Vendor')}")
        
        # Pull shop address
        shops_data = load_json('shops.json')
        shop_info = next((s for s in shops_data if s.get('id') == item.get('shop_id')), None)
        if shop_info and shop_info.get('address'):
            st.write(f"📍 **Shop Address:** {shop_info['address']}")

        # Handle type as list or string
        item_type_raw = item.get('type', [])
        if isinstance(item_type_raw, list):
            type_label = " & ".join(item_type_raw)
        else:
            type_label = item_type_raw
        st.write(f"**Available for:** {type_label if type_label else 'N/A'}")

        qty = item.get('quantity', None)
        if qty is not None:
            qty_color = "green" if qty > 0 else "red"
            qty_label = f"{qty} in stock" if qty > 0 else "Out of stock"
            st.markdown(f"**Quantity:** :{qty_color}[{qty_label}]")

        st.write(f"**Status:** {item.get('availability', 'Available')}")
        st.info("Perfect for: Wedding ceremonies, engagements, and formal events.")
        
        if st.button("⬅️ Back to Browse"):
            st.session_state.page = "browse"
            st.rerun()
            
    st.divider()
    st.subheader("📅 Reserve This Set")

    # Require customer login to proceed
    if 'customer' not in st.session_state:
        st.warning("🔒 You need to be logged in as a customer to make a reservation.")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔑 Login / Register", use_container_width=True):
                st.session_state.page = "customer_login"
                st.rerun()
        with col_b:
            if st.button("⬅️ Back to Browse", key="back_login", use_container_width=True):
                st.session_state.page = "browse"
                st.rerun()
        return

    customer = st.session_state.customer
    st.success(f"Logged in as **{customer['full_name']}** ({customer['email']})")

    # Show what the shop offers — handle list or string
    item_type_raw = item.get('type', [])
    if isinstance(item_type_raw, list):
        fulfillment_options = item_type_raw if item_type_raw else ["Rental", "Buy"]
        type_display = " & ".join(item_type_raw)
    elif item_type_raw in ["Rental", "Buy"]:
        fulfillment_options = [item_type_raw]
        type_display = item_type_raw
    else:
        fulfillment_options = ["Rental", "Buy"]
        type_display = "Rental & Buy"

    st.info(f"🏷️ This item is available for: **{type_display}**")

    with st.form("booking_form", clear_on_submit=True):
        # Auto-fill from logged-in customer
        st.text_input("Your Full Name", value=customer['full_name'], disabled=True)
        st.text_input("Contact Number", value=customer['contact'], disabled=True)
        delivery_address = st.text_area("Delivery Address", value=customer.get('address', ''), placeholder="Enter the address where you want the items delivered...")
        wedding_date = None
        start_date = None
        end_date = None
        total_price = 0

        # Show fulfillment choice only if more than one option
        if len(fulfillment_options) > 1:
            fulfillment_choice = st.radio(
                "How would you like this item?",
                fulfillment_options,
                horizontal=True
            )
        else:
            fulfillment_choice = fulfillment_options[0]
            st.write(f"📦 **Order Type:** {fulfillment_choice}")
        
        if fulfillment_choice == "Rental":
            st.markdown("**Select Renting Period**")
            cols_r = st.columns(2)
            with cols_r[0]:
                start_date = st.date_input("From Date", key="rent_from")
            with cols_r[1]:
                end_date   = st.date_input("To Date", key="rent_to")
            
            from datetime import date
            if start_date and end_date:
                days = (end_date - start_date).days
                if days < 1:
                    st.error("❌ Rental must be at least 1 day.")
                    total_price = 0
                else:
                    total_price = days * item.get('rental_price', 0)
                    st.info(f"💎 Renting for **{days} days**. Total Rental: **LKR {total_price:,.0f}**")
        else:
            wedding_date = st.date_input("Purchase/Event Date")
            total_price = item.get('sale_price', 0)
            st.info(f"💎 Purchase Price: **LKR {total_price:,.0f}**")

        special_notes = st.text_area("Special Notes (optional)", placeholder="Any special requests or preferences...")

        if st.form_submit_button("✨ Confirm Reservation"):
            if fulfillment_choice == "Rental" and (not start_date or not end_date or (end_date - start_date).days < 1):
                st.error("Please provide a valid rental period.")
            else:
                success, msg = submit_booking(
                    customer_name=customer['full_name'],
                    contact=customer['contact'],
                    wedding_date=wedding_date or start_date, # Fallback
                    jewelry_id=item['id'],
                    customer_id=customer['id'],
                    customer_email=customer['email'],
                    customer_address=delivery_address,
                    shop_id=item.get('shop_id'),
                    shop_name=item.get('shop_name'),
                    item_name=item.get('name'),
                    special_notes=special_notes,
                    fulfillment_type=fulfillment_choice,
                    start_date=start_date,
                    end_date=end_date,
                    total_price=total_price
                )
            if success:
                st.success(msg)
                st.balloons()
            else:
                st.error(msg)


def render_customer_login():
    """Customer Login & Registration Portal."""
    st.title("Customer Portal")

    # ── LOGGED IN VIEW ──────────────────────────────────────────────────────
    if 'customer' in st.session_state:
        customer = st.session_state.customer
        tab_profile, tab_settings = st.tabs(["👤 My Profile", "⚙️ Account Settings"])

        with tab_profile:
            st.subheader(f"Welcome, {customer['full_name']}!")
            st.write(f"**Email:** {customer['email']}")
            st.write(f"**Contact:** {customer['contact']}")
            if customer.get('address'):
                st.write(f"**Address:** {customer['address']}")
            st.write(f"**Username:** {customer['username']}")
            st.divider()
            if st.button("🚪 Logout", type="primary"):
                del st.session_state.customer
                if 'confirm_delete' in st.session_state:
                    del st.session_state.confirm_delete
                st.session_state.page = "home"
                st.rerun()

        with tab_settings:
            st.subheader("Account Settings")
            st.divider()

            # Delete Account section
            st.markdown("#### Delete My Account")
            st.warning("This will permanently delete your account and all your booking history.")

            # Two-step confirmation using session state
            if not st.session_state.get('confirm_delete', False):
                if st.button("Delete My Account", type="primary", use_container_width=True):
                    st.session_state.confirm_delete = True
                    st.rerun()
            else:
                st.error("Are you sure? This action **cannot be undone**.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, Delete My Account", type="primary", use_container_width=True):
                        from storage import delete_record, save_json
                        # Cascade: remove all their bookings
                        bookings = load_json('bookings.json')
                        updated = [b for b in bookings if b.get('customer_id') != customer['id']]
                        save_json('bookings.json', updated)
                        # Delete the customer record
                        delete_record('customers.json', customer['id'])
                        del st.session_state.customer
                        del st.session_state.confirm_delete
                        st.session_state.page = "home"
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.confirm_delete = False
                        st.rerun()
        return

    # ── NOT LOGGED IN VIEW ─────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    with tab1:
        with st.form("customer_login_form"):
            st.subheader("Welcome Back!")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                success, customer = verify_login(username, password, 'customers.json')
                if success:
                    st.session_state.customer = customer
                    st.session_state.page = st.session_state.get('pre_login_page', 'browse')
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with tab2:
        with st.form("customer_register_form", clear_on_submit=True):
            st.subheader("Create Your Account")
            full_name = st.text_input("Full Name")
            email    = st.text_input("Email Address")
            contact  = st.text_input("Contact Number")
            address  = st.text_area("Your Physical Address")
            username = st.text_input("Choose a Username")
            password = st.text_input("Choose a Password", type="password")
            if st.form_submit_button("Create Account", use_container_width=True):
                if not all([full_name, email, contact, address, username, password]):
                    st.error("All fields are required.")
                elif check_duplicate_account(username, 'customers.json'):
                    st.error("Username already taken. Please choose another.")
                else:
                    new_customer = {
                        "full_name": full_name,
                        "email": email,
                        "contact": contact,
                        "address": address,
                        "username": username,
                        "password": password
                    }
                    saved = add_record('customers.json', new_customer)
                    st.session_state.customer = saved
                    st.success("Account created! You are now logged in.")
                    st.session_state.page = st.session_state.get('pre_login_page', 'browse')
                    st.rerun()
