import streamlit as st
import pandas as pd
import json
import os
import time

# --- SYSTEM CONFIGURATION ---
st.set_page_config(
    layout="wide", 
    page_title="SolarFlow Enterprise", 
    page_icon="☀️",
    initial_sidebar_state="expanded"
)

# --- RESPONSIVE PROFESSIONAL CSS ---
st.markdown("""
<style>
    html { font-size: 16px; }
    @media (max-width: 600px) { html { font-size: 14px; } }

    .stApp { background-color: #f8f9fa; }

    /* Horizontal Stepper Styling */
    .workflow-row {
        display: flex;
        flex-direction: row;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        gap: 12px;
        padding: 15px 10px;
        background: #ffffff;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
    }
    
    .step-box {
        min-width: 160px;
        max-width: 200px;
        flex: 0 0 auto;
        padding: 12px;
        border-radius: 6px;
        background: #fdfdfd;
        border: 1px solid #edf2f7;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }

    .status-badge {
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 8px;
    }
    .pending { background: #fff9db; color: #e67700; border: 1px solid #ffe066; }
    .completed { background: #f4fce3; color: #2b8a3e; border: 1px solid #b2f2bb; }
    .attention { background: #fff5f5; color: #c92a2a; border: 1px solid #ffa8a8; animation: pulse-soft 2s infinite; }
    
    @keyframes pulse-soft {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); background: #ffe3e3; }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE LOGIC ---
DB_FILE = "enterprise_final_db.json"

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

# --- AUTHENTICATION ---
def login():
    st.markdown("<h2 style='text-align: center;'>SolarFlow Portal</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([0.5, 2, 0.5])
    with col:
        with st.form("auth_form"):
            u_email = st.text_input("Email")
            u_pass = st.text_input("Password", type="password")
            u_role = st.selectbox("Role", ["Team Member", "Company Owner", "System Director"])
            if st.form_submit_button("Sign In", use_container_width=True):
                # Super Admin
                if u_role == "System Director":
                    if u_email == st.session_state.db['super_admin']['email'] and u_pass == st.session_state.db['super_admin']['password']:
                        st.session_state.user = {"role": "super", "email": u_email}
                        st.rerun()
                
                # Sub-Admin/Team
                found = False
                for c_id, c_data in st.session_state.db['companies'].items():
                    if u_role == "Company Owner":
                        if c_data['owner']['email'] == u_email and c_data['owner']['password'] == u_pass:
                            st.session_state.user = {"role": "sub", "email": u_email, "c_id": c_id}
                            found = True
                            st.rerun()
                    else: # Team Member
                        for t_member in c_data['team']:
                            if t_member['email'] == u_email and t_member['password'] == u_pass:
                                st.session_state.user = {"role": "team", "email": u_email, "c_id": c_id}
                                found = True
                                st.rerun()
                
                if not found:
                    st.error("Invalid Credentials or Account Type")

if not st.session_state.user:
    login()
    st.stop()

# --- APP NAVIGATION ---
user = st.session_state.user

# Security Check: Role access tabhi milegi jab user None nahi hoga
if user is not None:
    role = user['role']

    with st.sidebar:
        st.subheader("Account Info")
        st.write(f"Logged as: **{role.upper()}**")
        st.write(f"ID: {user['email']}")
        if st.button("Sign Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # --- 1. SUPER ADMIN VIEW ---
    if role == "super":
        st.header("Master Control Panel")
        t1, t2 = st.tabs(["Manage Companies", "Register New Business"])
        
        with t1:
            if not st.session_state.db['companies']:
                st.info("No companies registered yet.")
            for c_id, c_data in st.session_state.db['companies'].items():
                with st.expander(f"Company: {c_data['name']}"):
                    st.write(f"**Admin Email:** {c_data['owner']['email']}")
                    st.write(f"**Admin Password:** `{c_data['owner']['password']}`")
                    if c_data['team']:
                        st.write("**Team Members Details:**")
                        st.table(pd.DataFrame(c_data['team']))
                    if st.button("Delete This Company", key=f"del_{c_id}"):
                        del st.session_state.db['companies'][c_id]
                        save_db(st.session_state.db); st.rerun()

        with t2:
            with st.form("reg_new"):
                bn = st.text_input("Business Name")
                be = st.text_input("Owner Email")
                bp = st.text_input("Set Owner Password")
                if st.form_submit_button("Create Sub-Admin Account"):
                    new_id = str(int(time.time()))
                    st.session_state.db['companies'][new_id] = {
                        "name": bn, "owner": {"email": be, "password": bp},
                        "team": [], "steps": [{"name": "Lead", "role": "Admin"}],
                        "customers": []
                    }
                    save_db(st.session_state.db); st.rerun()

    # --- 2. SUB-ADMIN & TEAM VIEW ---
    else:
        c_id = user['c_id']
        comp = st.session_state.db['companies'][c_id]
        
        menu = ["Dashboard"]
        if role == "sub": menu += ["Team Management", "Workflow Setup"]
        tabs = st.tabs(menu)

        # DASHBOARD
        with tabs[0]:
            st.title(f"Dashboard - {comp['name']}")
            if role == "sub":
                with st.expander("➕ Add New Customer"):
                    with st.form("add_c"):
                        cn = st.text_input("Customer Name")
                        cr = st.text_input("Customer Phone/Ref")
                        if st.form_submit_button("Save Customer"):
                            comp['customers'].append({"name": cn, "id": cr, "stats": {s['name']: "Pending" for s in comp['steps']}})
                            save_db(st.session_state.db); st.rerun()

            st.markdown("---")
            for idx, cust in enumerate(comp['customers']):
                st.subheader(f"👤 {cust['name']} | {cust['id']}")
                
                # SWIPABLE HORIZONTAL WORKFLOW
                st.markdown('<div class="workflow-row">', unsafe_allow_html=True)
                cols = st.columns(len(comp['steps']))
                for i, step in enumerate(comp['steps']):
                    s_name = step['name']
                    cur_v = cust['stats'].get(s_name, "Pending")
                    with cols[i]:
                        st.markdown(f"""
                        <div class="step-box">
                            <div class="status-badge {cur_v.lower()}">{cur_v}</div>
                            <div style="font-weight:bold; font-size:0.85rem;">{s_name}</div>
                            <div style="font-size:0.65rem; color:#6c757d;">{step['role']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        new_v = st.selectbox("Update Status", ["Pending", "Completed", "Attention"], 
                                             index=["Pending", "Completed", "Attention"].index(cur_v),
                                             key=f"st_{idx}_{i}", label_visibility="collapsed")
                        if new_v != cur_v:
                            cust['stats'][s_name] = new_v
                            save_db(st.session_state.db); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # TEAM MANAGEMENT (Only Sub-Admin)
        if role == "sub":
            with tabs[1]:
                st.subheader("Manage Your Team")
                with st.form("staff"):
                    st.write("Create Login for Team Members")
                    tn, te, tp = st.text_input("Name"), st.text_input("Email"), st.text_input("Password")
                    if st.form_submit_button("Add Member"):
                        comp['team'].append({"name": tn, "email": te, "password": tp})
                        save_db(st.session_state.db); st.rerun()
                if comp['team']: st.dataframe(pd.DataFrame(comp['team']), use_container_width=True)

            # WORKFLOW SETUP (Only Sub-Admin)
            with tabs[2]:
                st.subheader("Design Your Workflow")
                with st.form("wf"):
                    wn = st.text_input("Step Title (e.g. Site Survey)")
                    wr = st.selectbox("Who handles this?", ["Admin", "Team", "Client", "Vendor"])
                    if st.form_submit_button("Add to Workflow"):
                        comp['steps'].append({"name": wn, "role": wr})
                        for c in comp['customers']: c['stats'][wn] = "Pending"
                        save_db(st.session_state.db); st.rerun()
                
                st.write("Current Steps:")
                for j, s in enumerate(comp['steps']):
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"**{s['name']}** ({s['role']})")
                    if c2.button("❌", key=f"ds_{j}"):
                        comp['steps'].pop(j)
                        save_db(st.session_state.db); st.rerun()
