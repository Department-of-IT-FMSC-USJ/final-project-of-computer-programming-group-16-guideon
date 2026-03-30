import streamlit as st
import pandas as pd
from storage import load_json, add_record, update_record, delete_record
from backend import verify_login, check_duplicate_account

def render_shop_login():
    """Shop Portal: Authentication and registration for vendors."""
    st.title("Shop Portal")
    tab1, tab2 = st.tabs(["🔒 Partner Login", "🤝 Join the Marketplace"])
    
    with tab1:
        with st.form("shop_login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Access Dashboard"):
                success, shop = verify_login(username, password, 'shops.json')
                if success:
                    if shop.get('status') == 'pending_approval':
                        st.warning("⏳ **Your registration is pending admin approval.**\n\nOur team is reviewing your shop details. You will be able to login once your account has been approved. Please check back later.")
                    else:
                        st.session_state.is_vendor = True
                        st.session_state.shop_data = shop
                        st.session_state.page = "shop_dashboard"
                        st.rerun()
                else:
                    st.error("Invalid credentials.")
                    
    with tab2:
        with st.form("shop_reg"):
            st.subheader("New Shop Registration")
            shop_name = st.text_input("Business Name")
            owner_name = st.text_input("Owner Name")
            contact = st.text_input("Official Contact Number")
            address = st.text_area("Shop Physical Address")
            reg_username = st.text_input("System Username")
            reg_password = st.text_input("System Password", type="password")
            if st.form_submit_button("Register Business"):
                if check_duplicate_account(reg_username, 'shops.json'):
                    st.error("Username already taken.")
                elif not all([shop_name, owner_name, contact, address, reg_username, reg_password]):
                    st.error("All fields (Business, Owner, Contact, Address, Username, Password) are required.")
                else:
                    new_shop = {
                        "name": shop_name,
                        "owner": owner_name,
                        "contact": contact,
                        "address": address,
                        "username": reg_username,
                        "password": reg_password,
                        "status": "pending_approval"
                    }
                    add_record('shops.json', new_shop)
                    st.success("Registration submitted! Our team will verify your shop shortly.")

def render_shop_dashboard():
    """Shop Dashboard: Inventory and order management."""
    if 'shop_data' not in st.session_state:
        st.session_state.page = "shop_login"
        st.rerun()
        
    shop = st.session_state.shop_data
    st.title(f"Dashboard")
    st.write(f"Welcome back, **{shop['name']}**!")
    
    if st.button("Logout", type="primary"):
        del st.session_state.is_vendor
        del st.session_state.shop_data
        st.session_state.page = "shop_login"
        st.rerun()
        
    st.divider()
    
    # Inventory Controls
    st.subheader("Inventory Management")
    jewelry_data = load_json('jewelry.json')
    shop_items = [item for item in jewelry_data if item.get('shop_id') == shop['id']]
    
    with st.expander("➕ List New Collection"):
        with st.form("add_item", clear_on_submit=True):
            name = st.text_input("Jewelry Item Name")
            style = st.selectbox("Style Category", ["Temple", "Gold", "Modern"])
            quantity = st.number_input("Quantity Available", min_value=1, max_value=100, value=1, step=1)
            st.markdown("**Fulfillment & Pricing**")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                offer_rental = st.checkbox("🔄 Available for Rental")
                rental_price = st.number_input("Rental Price (LKR / Day)", min_value=0, value=0)
            with col_p2:
                offer_buy = st.checkbox("🛒 Available for Purchase (Buy)")
                sale_price = st.number_input("Selling Price (LKR)", min_value=0, value=0)
            image_url = st.text_input("Image URL", help="Provide a link to the jewelry image or use a local path like assets/custom.png")
            if st.form_submit_button("Publish Listing"):
                fulfillment = []
                if offer_rental: fulfillment.append("Rental")
                if offer_buy:    fulfillment.append("Buy")
                if not fulfillment:
                    st.error("Please select at least one fulfillment option (Rental or Buy).")
                elif not name:
                    st.error("Please enter a jewelry item name.")
                else:
                    item = {
                        "name": name,
                        "style": style,
                        "rental_price": rental_price if offer_rental else 0,
                        "sale_price": sale_price if offer_buy else 0,
                        "quantity": int(quantity),
                        "type": fulfillment,
                        "image_url": image_url if image_url else "https://via.placeholder.com/300x300?text=No+Preview",
                        "shop_id": shop.get('id'),
                        "shop_name": shop.get('name'),
                        "availability": "Yes"
                    }
                    add_record('jewelry.json', item)
                    st.success("New item published to marketplace!")
                    st.rerun()

    if shop_items:
        for item in shop_items:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"#### {item['name']}")
                    pricing_text = []
                    if item.get('rental_price', 0) > 0: pricing_text.append(f"Rental: LKR {item['rental_price']}/day")
                    if item.get('sale_price', 0) > 0: pricing_text.append(f"Buy: LKR {item['sale_price']}")
                    st.write(f"{item['style']} | {' & '.join(pricing_text) if pricing_text else 'Price N/A'}")
                with col2:
                    avail = st.checkbox("Available", value=(item.get('availability') == 'Yes'), key=f"avail_{item['id']}")
                    if avail != (item.get('availability') == 'Yes'):
                        item['availability'] = 'Yes' if avail else 'No'
                        update_record('jewelry.json', item['id'], item)
                        st.rerun()
                with col3:
                    if st.button("Remove", key=f"del_{item['id']}", type="secondary"):
                        delete_record('jewelry.json', item['id'])
                        st.rerun()
    else:
        st.info("You haven't listed any items yet.")

    st.divider()
    st.subheader("Customer Booking Requests")
    bookings = load_json('bookings.json')
    my_bookings = [b for b in bookings if any(item['id'] == b['jewelry_id'] for item in shop_items)]
    
    if my_bookings:
        for booking in my_bookings:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Customer:** {booking.get('customer_name', booking.get('name', 'N/A'))}")
                    st.write(f"**Email:** {booking.get('customer_email', 'N/A')} | 📞 **Contact:** {booking.get('contact', 'N/A')}")
                    if booking.get('customer_address'):
                        st.write(f"**Delivery Address:** {booking['customer_address']}")
                    
                    if booking.get('fulfillment_type') == 'Rental' and booking.get('start_date'):
                        st.write(f"**Item:** {booking.get('item_name', 'N/A')} | 📅 **Renting:** {booking['start_date']} to {booking['end_date']}")
                        from datetime import datetime
                        try:
                            d1 = datetime.strptime(booking['start_date'], "%Y-%m-%d")
                            d2 = datetime.strptime(booking['end_date'], "%Y-%m-%d")
                            st.write(f"🕒 **Duration:** {(d2 - d1).days} Days")
                        except: pass
                    else:
                        st.write(f"**Item:** {booking.get('item_name', 'N/A')} | 📅 **Date:** {booking.get('wedding_date', 'N/A')}")
                    ft = booking.get('fulfillment_type', '')
                    if ft:
                        label = "🛒 Buy" if ft == "Buy" else "🔄 Rental"
                        st.write(f"**Order Type:** {label}")
                    if booking.get('special_notes'):
                        st.caption(f"📝 Notes: {booking['special_notes']}")
                    st.info(f"Status: **{booking.get('status', 'Pending')}**")
                with col2:
                    current_status = booking.get('status', 'Pending')
                    status_options = ["Pending", "Ready to Collect", "Finished", "Cancelled"]
                    if current_status not in status_options:
                        current_status = "Pending"
                    
                    new_status = st.selectbox(
                        "Update Status", 
                        status_options,
                        index=status_options.index(current_status),
                        key=f"status_select_{booking['id']}"
                    )
                    if new_status != booking.get('status'):
                        booking['status'] = new_status
                        update_record('bookings.json', booking['id'], booking)
                        st.success(f"Status updated to {new_status}")
                        st.rerun()
    else:
        st.write("No active bookings found.")
