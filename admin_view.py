import streamlit as st
import pandas as pd
from storage import load_json, save_json, update_record, delete_record

def render_admin_login():
    """Admin Access: Secure entry for marketplace moderators."""
    st.title("Admin Center")
    st.info("💡 **Default Credentials**: ID: `admin` | Access Token: `bridora123`")
    with st.form("admin_login"):
        username = st.text_input("Admin ID")
        password = st.text_input("Access Token", type="password")
        if st.form_submit_button("Grant Access"):
            if username == "admin" and password == "bridora123":
                st.session_state.is_admin = True
                st.session_state.page = "admin_panel"
                st.rerun()
            else:
                st.error("Invalid credentials.")

def render_admin_panel():
    """Admin Dashboard: Global oversight and partner verification."""
    st.title("Admin Panel")
    if st.button("End Session", type="primary"):
        del st.session_state.is_admin
        st.session_state.page = "home"
        st.rerun()
        
    # --- Performance Overview ---
    st.divider()
    st.subheader("Platform Performance")
    col1, col2, col3 = st.columns(3)
    shops = load_json('shops.json')
    jewelry = load_json('jewelry.json')
    bookings = load_json('bookings.json')
    
    with col1:
        st.metric("Active Partners", len(shops))
    with col2:
        st.metric("Total Inventory", len(jewelry))
    with col3:
        st.metric("Service Requests", len(bookings))

    # --- Vendor Verification ---
    st.divider()
    st.subheader("Partner Verifications")
    pending_shops = [shop for shop in shops if shop.get('status') == 'pending_approval']
    
    if pending_shops:
        for idx, shop in enumerate(pending_shops):
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{shop['name']}** | Owner: {shop['owner']} | {shop['contact']}")
                with col2:
                    if st.button("✅ Approve", key=f"approve_{shop['id']}", use_container_width=True):
                        shop['status'] = 'approved'
                        update_record('shops.json', shop['id'], shop)
                        st.success(f"Partner {shop['name']} approved!")
                        st.rerun()
                with col3:
                    if st.button("❌ Reject", key=f"reject_{shop['id']}", use_container_width=True, type="secondary"):
                        if delete_record('shops.json', shop['id']):
                            st.warning(f"Registration request for '{shop['name']}' has been rejected and deleted.")
                            st.rerun()
    else:
        st.info("All partners are currently verified.")

    # --- Catalog Governance ---
    st.divider()
    st.subheader("Inventory Oversight")
    if jewelry:
        for item in jewelry:
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    pricing = []
                    if item.get('rental_price', 0) > 0: pricing.append(f"Rent: {item['rental_price']}/d")
                    if item.get('sale_price', 0) > 0: pricing.append(f"Buy: {item['sale_price']}")
                    st.write(f"**{item['name']}** | {item.get('shop_name')} | {' & '.join(pricing) if pricing else 'N/A'}")
                with col2:
                    if st.button("Delist", key=f"admin_del_{item['id']}", use_container_width=True):
                        delete_record('jewelry.json', item['id'])
                        st.rerun()
    else:
        st.write("Marketplace inventory is currently empty.")

    # --- Vendor Directory and Governance ---
    st.divider()
    st.subheader("Partner Shops")
    if shops:
        for shop in shops:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.write(f"**{shop['name']}** | {shop['owner']} | Status: {shop.get('status', 'N/A')}")
                with c2:
                    if st.button("Delete Shop", key=f"del_shop_{shop['id']}", type="secondary", use_container_width=True):
                        # 1. Store the shop name for the success message
                        old_name = shop['name']
                        shop_id = shop['id']
                        
                        # 2. Delete all jewelry associated with this shop (Cascade Delete)
                        all_jewelry = load_json('jewelry.json')
                        updated_jewelry = [j for j in all_jewelry if j.get('shop_id') != shop_id]
                        save_json('jewelry.json', updated_jewelry)
                        
                        # 3. Delete the shop itself
                        if delete_record('shops.json', shop_id):
                            st.success(f"Shop '{old_name}' and all its products have been permanently removed.")
                            st.rerun()
    else:
        st.write("No registered partners found.")

    # --- System Monitoring & Reset ---
    st.divider()
    st.subheader("⚠️ System Maintenance")
    if st.button("Reset Marketplace (Wipe All Data)", type="primary", use_container_width=True):
        save_json('shops.json', [])
        save_json('jewelry.json', [])
        save_json('bookings.json', [])
        st.warning("All marketplace data has been wiped.")
        st.rerun()

    # --- Commission Report ---
    st.divider()
    st.subheader("Partner Commission Report (Sale: 5% | Rent: 2%)")

    approved_shops = [s for s in shops if s.get('status') == 'approved']

    if approved_shops:
        total_platform_commission = 0.0

        for shop in approved_shops:
            shop_id = shop['id']
            shop_name = shop['name']

            # Get items belonging to this shop
            shop_items = [j for j in jewelry if j.get('shop_id') == shop_id]
            shop_item_ids = {j['id'] for j in shop_items}

            # Get bookings for this shop's items (only Finished orders count as sales)
            shop_bookings = [b for b in bookings if b.get('jewelry_id') in shop_item_ids]
            finished_bookings = [b for b in shop_bookings if b.get('status') == 'Finished']
            pending_bookings  = [b for b in shop_bookings if b.get('status') not in ['Finished', 'Cancelled']]

            # Calculate commission: 5% for Buy, 2% for Rental
            commission_total = 0.0
            for b in finished_bookings:
                # If commission is already stored (new recordings)
                if b.get('commission', 0) > 0:
                    commission_total += b['commission']
                else:
                    # Fallback for old/legacy recordings
                    price_to_use = b.get('total_price', 0)
                    if price_to_use == 0:
                        item = next((j for j in shop_items if j['id'] == b.get('jewelry_id')), None)
                        if item:
                            price_to_use = item.get('rental_price', item.get('sale_price', 0))
                    
                    rate = 0.05 if b.get('fulfillment_type') == "Buy" else 0.02
                    commission_total += price_to_use * rate

            total_platform_commission += commission_total

            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3, 1, 1, 2])
                with c1:
                    st.markdown(f"**🏪 {shop_name}**")
                    st.caption(f"Owner: {shop.get('owner', 'N/A')} | Items listed: {len(shop_items)}")
                with c2:
                    st.metric("Total Orders", len(shop_bookings))
                with c3:
                    st.metric("Completed", len(finished_bookings))
                with c4:
                    st.markdown(
                        f"""<div style="padding-top:4px;">
                            <p style="font-size:0.82rem; color:#555; margin:0; padding:0;">Commission Due</p>
                            <p style="font-size:1.5rem; font-weight:700; color:#111;
                               margin:0; padding:0; overflow-wrap:break-word; white-space:normal;">
                                LKR {commission_total:,.2f}
                            </p>
                        </div>""",
                        unsafe_allow_html=True
                    )

        st.divider()
        st.success(f"🏦 **Total Platform Commission Collected: LKR {total_platform_commission:,.2f}**")
    else:
        st.info("No approved partner shops found.")
