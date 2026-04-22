import streamlit as st
import pandas as pd
import json
import datetime
import time
import os

# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="SolarFlow | CRM", page_icon="☀️")

# --- ADVANCED PROFESSIONAL STYLING ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .status-card {
        padding: 15px; border-radius: 12px; background: white;
        text-align: center; border: 1px solid #e0e0e0; transition: transform 0.2s;
    }
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 0, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
    }
    .blink-red { background-color: #ffe5e5; color: #d9534f; border: 2px solid #d9534f; animation: pulse-red 2s infinite; font-weight: bold; padding: 2px 8px; border-radius: 10px; }
    .completed-green { background-color: #e6ffed; color: #28a745; border: 2px solid #28a745; font-weight: bold; padding: 2px 8px; border-radius: 10px; }
    .pending-yellow { background-color: #fff9e6; color: #f0ad4e; border: 2px solid #f0ad4e; font-weight: bold; padding: 2px 8px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE LOGIC ---
DATABASE_FILE = "solar_data_v3.json"

def load_data():
    if not os.path.exists(DATABASE_FILE):
        return {
            "admins": ["harshitkumawat616@gmail.com"], # Change this to your email
            "team_emails": [],
            "steps": [{"id": "1", "name": "Registration", "role": "Consumer"}],
            "customers": []
        }
    with open(DATABASE_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# --- AUTHENTICATION ---
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

with st.sidebar:
    st.title("☀️ SolarFlow")
    if not st.session_state.user_email:
        email_in = st.text_input("Enter Email to Access")
        if st.button("Login"):
            if email_in in st.session_state.db['admins'] or email_in in st.session_state.db['team_emails']:
                st.session_state.user_email = email_in
                st.rerun()
            else: st.error("Access Denied.")
        st.stop()
    else:
        st.write(f"User: **{st.session_state.user_email}**")
        is_admin = st.session_state.user_email in st.session_state.db['admins']
        if st.button("Logout"):
            st.session_state.user_email = None
            st.rerun()

tabs = st.tabs(["📊 Dashboard", "👥 Team & Workflow", "⚙️ System"])

# ==========================================
# TAB 1: DASHBOARD (CUSTOMERS)
# ==========================================
with tabs[0]:
    st.header("Application Registry")
    
    # 1. ADD CUSTOMER
    with st.expander("📝 Register New Application"):
        with st.form("new_app"):
            c1, c2, c3 = st.columns(3)
            name = c1.text_input("Consumer Name")
            app_id = c2.text_input("Application #")
            mobile = c3.text_input("Mobile")
            if st.form_submit_button("Add Record"):
                new_cust = {"name": name, "app_id": app_id, "mobile": mobile, "date": str(datetime.date.today()),
                            "status_data": {s['name']: "Pending" for s in st.session_state.db['steps']}}
                st.session_state.db['customers'].append(new_cust)
                save_data(st.session_state.db)
                st.rerun()

    # 2. EDIT/DELETE CUSTOMERS
    if st.session_state.db['customers']:
        st.subheader("Manage Records")
        for idx, cust in enumerate(st.session_state.db['customers']):
            with st.expander(f"👤 {cust['name']} | {cust['app_id']}"):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    new_n = st.text_input("Edit Name", cust['name'], key=f"edit_n_{idx}")
                    new_a = st.text_input("Edit App ID", cust['app_id'], key=f"edit_a_{idx}")
                with col2:
                    if st.button("💾 Update", key=f"up_c_{idx}"):
                        cust['name'], cust['app_id'] = new_n, new_a
                        save_data(st.session_state.db)
                        st.success("Updated!"); time.sleep(0.5); st.rerun()
                with col3:
                    if st.button("🗑️ Delete", key=f"del_c_{idx}"):
                        st.session_state.db['customers'].pop(idx)
                        save_data(st.session_state.db)
                        st.warning("Deleted!"); time.sleep(0.5); st.rerun()

        st.markdown("---")
        # 3. WORKFLOW STEPPER
        selected_name = st.selectbox("Update Workflow for:", [c['name'] for c in st.session_state.db['customers']])
        target_cust = next(item for item in st.session_state.db['customers'] if item["name"] == selected_name)
        
        cols = st.columns(len(st.session_state.db['steps']))
        for i, step in enumerate(st.session_state.db['steps']):
            s_name = step['name']
            current_s = target_cust['status_data'].get(s_name, "Pending")
            with cols[i]:
                css = "pending-yellow" if current_s == "Pending" else "completed-green" if current_s == "Completed" else "blink-red"
                st.markdown(f"<div class='status-card'><p style='font-size:0.7rem;'>{step['role']}</p><p class='{css}'>{current_s}</p><p><b>{s_name}</b></p></div>", unsafe_allow_html=True)
                new_s = st.selectbox("Set", ["Pending", "Completed", "Attention"], index=["Pending", "Completed", "Attention"].index(current_s), key=f"s_{selected_name}_{i}")
                if new_s != current_s:
                    target_cust['status_data'][s_name] = new_s
                    save_data(st.session_state.db); st.rerun()

# ==========================================
# TAB 2: TEAM & WORKFLOW (CRUD)
# ==========================================
with tabs[1]:
    if not is_admin: st.warning("Admin only."); st.stop()
    
    col_t, col_w = st.columns(2)
    
    # TEAM CRUD
    with col_t:
        st.subheader("👥 Team Access")
        t_email = st.text_input("New Member Email")
        if st.button("➕ Add Member"):
            st.session_state.db['team_emails'].append(t_email); save_data(st.session_state.db); st.rerun()
        
        for i, email in enumerate(st.session_state.db['team_emails']):
            c1, c2 = st.columns([3, 1])
            new_mail = c1.text_input(f"Member {i+1}", email, key=f"m_{i}")
            if c2.button("🗑️", key=f"del_m_{i}"):
                st.session_state.db['team_emails'].pop(i); save_data(st.session_state.db); st.rerun()
            if new_mail != email: # Auto-update on change
                st.session_state.db['team_emails'][i] = new_mail; save_data(st.session_state.db)

    # WORKFLOW CRUD
    with col_w:
        st.subheader("⛓️ Workflow Steps")
        with st.form("add_step"):
            s_id = st.text_input("Step Order (ID)")
            s_name = st.text_input("Step Name")
            s_role = st.selectbox("Role", ["Consumer", "Vendor", "Discom", "Admin"])
            if st.form_submit_button("➕ Add Step"):
                st.session_state.db['steps'].append({"id": s_id, "name": s_name, "role": s_role})
                save_data(st.session_state.db); st.rerun()
        
        for i, step in enumerate(st.session_state.db['steps']):
            with st.expander(f"Step {step['id']}: {step['name']}"):
                u_name = st.text_input("Edit Name", step['name'], key=f"un_{i}")
                u_role = st.selectbox("Edit Role", ["Consumer", "Vendor", "Discom", "Admin"], index=["Consumer", "Vendor", "Discom", "Admin"].index(step['role']), key=f"ur_{i}")
                c1, c2 = st.columns(2)
                if c1.button("💾 Save", key=f"sv_s_{i}"):
                    step['name'], step['role'] = u_name, u_role
                    save_data(st.session_state.db); st.rerun()
                if c2.button("🗑️ Delete Step", key=f"dl_s_{i}"):
                    st.session_state.db['steps'].pop(i); save_data(st.session_state.db); st.rerun()

with tabs[2]:
    if st.button("🚨 Reset System Data"):
        if st.checkbox("Confirm Deletion"):
            if os.path.exists(DATABASE_FILE): os.remove(DATABASE_FILE); st.rerun()