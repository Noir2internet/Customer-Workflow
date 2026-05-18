import streamlit as st
import pandas as pd
import json
import os
import time
import datetime

# --- SYSTEM CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SolarFlow Enterprise", page_icon="☀️")

# --- PROFESSIONAL CSS (HORIZONTAL COMPACT UI) ---
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    
    /* Horizontal Stepper Styling */
    .workflow-row {
        display: flex;
        flex-direction: row;
        overflow-x: auto;
        gap: 8px;
        padding: 10px 5px;
        background: #ffffff;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }
    .step-box {
        min-width: 140px;
        flex: 1;
        padding: 8px;
        border-radius: 4px;
        border-left: 4px solid #dee2e6;
        background: #f1f3f5;
        text-align: left;
    }
    .status-badge {
        font-size: 0.65rem;
        font-weight: 800;
        padding: 2px 6px;
        border-radius: 3px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 4px;
    }
    .pending { background: #fff9db; color: #e67700; }
    .completed { background: #f4fce3; color: #2b8a3e; }
    .attention { background: #fff5f5; color: #c92a2a; border: 1px solid #ffa8a8; animation: pulse 2s infinite; }
    
    @keyframes pulse {
        0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; }
    }

    /* Admin UI Enhancements */
    .admin-card {
        padding: 15px;
        background: white;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- SECURE DATABASE LOGIC ---
DB_FILE = "enterprise_v5_db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {
            "super_admin": {"email": "harshitkumawat616@gmail.com", "password": "MasterSolarAdmin2026"},
            "companies": {} 
        }
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = load_db()

if 'user' not in st.session_state:
    st.session_state.user = None

# --- AUTHENTICATION SYSTEM ---
def login():
    st.markdown("<h2 style='text-align: center; color: #212529;'>SolarFlow Portal</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        with st.form("auth_form"):
            u_email = st.text_input("Email")
            u_pass = st.text_input("Password", type="password")
            u_role = st.selectbox("Account Type", ["Team Member", "Company Owner (Sub-Admin)", "System Director (Super Admin)"])
            if st.form_submit_button("Sign In"):
                # 1. Super Admin Check
                if u_role == "System Director (Super Admin)":
                    if u_email == st.session_state.db['super_admin']['email'] and u_pass == st.session_state.db['super_admin']['password']:
                        st.session_state.user = {"role": "super", "email": u_email}
                        st.rerun()
                
                # 2. Sub-Admin & Team Check
                for c_id, c_data in st.session_state.db['companies'].items():
                    if u_role == "Company Owner (Sub-Admin)":
                        if c_data['owner']['email'] == u_email and c_data['owner']['password'] == u_pass:
                            st.session_state.user = {"role": "sub", "email": u_email, "c_id": c_id}
                            st.rerun()
                    else: # Team
                        for t_member in c_data['team']:
                            if t_member['email'] == u_email and t_member['password'] == u_pass:
                                st.session_state.user = {"role": "team", "email": u_email, "c_id": c_id}
                                st.rerun()
                st.error("Invalid credentials or account type.")

if not st.session_state.user:
    login()
    st.stop()

# --- MAIN NAVIGATION ---
user = st.session_state.user
role = user['role']

with st.sidebar:
    st.title("SOLARFLOW")
    st.write(f"Level: **{role.upper()}**")
    if st.button("Log Out"):
        st.session_state.user = None
        st.rerun()

# ==========================================
# 1. SUPER ADMIN VIEW (YOUR VIEW)
# ==========================================
if role == "super":
    st.header("System Director Dashboard")
    t1, t2 = st.tabs(["Company Ecosystem", "Global Controls"])
    
    with t1:
        st.subheader("Active Company Tenants")
        for c_id, c_data in st.session_state.db['companies'].items():
            with st.expander(f"Company: {c_data['name']} (Owner: {c_data['owner']['email']})"):
                st.write(f"**Owner Password:** `{c_data['owner']['password']}`")
                st.markdown("---")
                st.write("**Staff Accounts:**")
                if c_data['team']:
                    st.table(pd.DataFrame(c_data['team']))
                else:
                    st.write("No staff registered.")
                
                if st.button(f"Terminate License for {c_data['name']}", key=f"del_{c_id}"):
                    del st.session_state.db['companies'][c_id]
                    save_db(st.session_state.db); st.rerun()

    with t2:
        st.subheader("Register New Company Tenant")
        with st.form("new_corp"):
            new_c_name = st.text_input("New Company Name")
            new_o_email = st.text_input("Owner Email")
            new_o_pass = st.text_input("Initial Owner Password")
            if st.form_submit_button("Launch Instance"):
                c_id = str(int(time.time()))
                st.session_state.db['companies'][c_id] = {
                    "name": new_c_name,
                    "owner": {"email": new_o_email, "password": new_o_pass},
                    "team": [],
                    "steps": [{"id": "1", "name": "Lead Captured", "role": "Admin"}],
                    "customers": []
                }
                save_db(st.session_state.db); st.rerun()

# ==========================================
# 2. SUB-ADMIN & TEAM VIEW
# ==========================================
else:
    c_id = user['c_id']
    comp = st.session_state.db['companies'][c_id]
    
    menu = ["Dashboard"]
    if role == "sub":
        menu += ["Staff Management", "Workflow Designer"]
    
    tabs = st.tabs(menu)

    # DASHBOARD
    with tabs[0]:
        st.subheader(f"{comp['name']} Operations")
        
        if role == "sub":
            with st.expander("Register New Application"):
                with st.form("reg_app"):
                    c_name = st.text_input("Customer Name")
                    c_num = st.text_input("Reference ID")
                    if st.form_submit_button("Create Entry"):
                        comp['customers'].append({
                            "name": c_name, "id": c_num,
                            "statuses": {s['name']: "Pending" for s in comp['steps']}
                        })
                        save_db(st.session_state.db); st.rerun()

        st.markdown("---")
        for idx, cust in enumerate(comp['customers']):
            col_info, col_flow = st.columns([1, 4])
            with col_info:
                st.write(f"**{cust['name']}**")
                st.caption(f"Ref: {cust['id']}")
                if role == "sub" and st.button("Delete", key=f"dc_{idx}"):
                    comp['customers'].pop(idx)
                    save_db(st.session_state.db); st.rerun()
            
            with col_flow:
                # HORIZONTAL STEPPER
                st.markdown('<div class="workflow-row">', unsafe_allow_html=True)
                step_cols = st.columns(len(comp['steps']))
                for i, step in enumerate(comp['steps']):
                    s_name = step['name']
                    current_val = cust['statuses'].get(s_name, "Pending")
                    status_cls = current_val.lower()
                    
                    with step_cols[i]:
                        st.markdown(f"""
                        <div class="step-box">
                            <span class="status-badge {status_cls}">{current_val}</span>
                            <div style="font-size:0.8rem; font-weight:600;">{s_name}</div>
                            <div style="font-size:0.6rem; color:#868e96;">{step['role'].upper()}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Status Update
                        new_stat = st.selectbox("Update", ["Pending", "Completed", "Attention"], 
                                               index=["Pending", "Completed", "Attention"].index(current_val),
                                               key=f"up_{idx}_{i}")
                        if new_stat != current_val:
                            cust['statuses'][s_name] = new_stat
                            save_db(st.session_state.db); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    # STAFF MANAGEMENT (SUB-ADMIN ONLY)
    if role == "sub":
        with tabs[1]:
            st.subheader("Manage Company Staff")
            with st.form("add_staff"):
                s_name = st.text_input("Staff Name")
                s_email = st.text_input("Staff Login Email")
                s_pass = st.text_input("Staff Login Password")
                if st.form_submit_button("Add Staff Account"):
                    comp['team'].append({"name": s_name, "email": s_email, "password": s_pass})
                    save_db(st.session_state.db); st.rerun()
            
            if comp['team']:
                st.table(pd.DataFrame(comp['team']))

        # WORKFLOW DESIGNER (SUB-ADMIN ONLY)
        with tabs[2]:
            st.subheader("Workflow Configuration")
            with st.form("add_step_form"):
                st.write("Add Step to your Business Process")
                n_name = st.text_input("Process Name")
                n_role = st.selectbox("Responsible Party", ["Admin", "Vendor", "Consumer", "Utility"])
                if st.form_submit_button("Confirm Step"):
                    comp['steps'].append({"id": str(len(comp['steps'])+1), "name": n_name, "role": n_role})
                    for c in comp['customers']: # Sync existing
                        if n_name not in c['statuses']: c['statuses'][n_name] = "Pending"
                    save_db(st.session_state.db); st.rerun()
            
            st.markdown("---")
            for j, step in enumerate(comp['steps']):
                c1, c2, c3 = st.columns([3, 2, 1])
                new_n = c1.text_input("Step Name", step['name'], key=f"wf_n_{j}")
                new_r = c2.selectbox("Role", ["Admin", "Vendor", "Consumer", "Utility"], index=["Admin", "Vendor", "Consumer", "Utility"].index(step['role']), key=f"wf_r_{j}")
                if c3.button("Delete", key=f"wf_d_{j}"):
                    comp['steps'].pop(j)
                    save_db(st.session_state.db); st.rerun()
                if new_n != step['name'] or new_r != step['role']:
                    step['name'], step['role'] = new_n, new_r
                    save_db(st.session_state.db)
