import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime, timedelta

# --- SYSTEM CONFIGURATION ---
st.set_page_config(
    layout="wide", 
    page_title="Work Flow - Enterprise CRM", 
    page_icon="💼",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL CORPORATE CSS (CLEAN BACKGROUND) ---
st.markdown("""
<style>
    /* Global Clean Theme Style */
    .stApp {
        background-color: #dee2e6 !important; /* Exact grey color from your screenshot */
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Absolute Clean Text Visibility */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #1a1c23 !important;
    }
    
    /* Form & Container Styling */
    .stForm, div[data-testid="stExpander"] {
        background-color: #ffffff !important;
        border-radius: 8px !important;
        border: 1px solid #ced4da !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        padding: 20px !important;
    }
    
    /* Horizontal Swipable Workflow Stepper */
    .workflow-container {
        display: flex;
        flex-direction: row;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        gap: 15px;
        padding: 20px 15px;
        background: #ffffff !important;
        border-radius: 10px;
        border: 1px solid #ced4da;
        margin-bottom: 25px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    /* Individual Step Box Card */
    .step-box {
        min-width: 180px;
        max-width: 220px;
        flex: 0 0 auto;
        padding: 15px;
        border-radius: 6px;
        background: #f8f9fa !important;
        border: 1px solid #e9ecef;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Professional Status Badges */
    .status-badge {
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 4px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 10px;
    }
    .pending { background: #fff9db !important; color: #e67700 !important; border: 1px solid #ffe066; }
    .completed { background: #f4fce3 !important; color: #2b8a3e !important; border: 1px solid #b2f2bb; }
    .attention { background: #fff5f5 !important; color: #c92a2a !important; border: 1px solid #ffa8a8; }
    
    /* System Warning Notice */
    .warning-banner {
        padding: 15px;
        background-color: #fff9db !important;
        color: #e67700 !important;
        border-radius: 8px;
        border-left: 6px solid #f0ad4e;
        margin-bottom: 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE LOGIC (JSON) ---
DB_FILE = "workflow_v8_db.json"

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

if 'payment_pending_for' not in st.session_state:
    st.session_state.payment_pending_for = None

# --- BRANDING LOGO COMPONENT ---
def display_header_logo():
    # Automatically scales and displays your professional logo cleanly
    if os.path.exists("logo 1.png"):
        st.image("logo 1.png", width=120)
    else:
        st.subheader("💼 WORK FLOW")

# --- PAYMENT INTERFACE FUNCTION ---
def payment_gateway_ui(email, password, company_id=None, dynamic_renew=False):
    display_header_logo()
    st.markdown("<h3 style='font-weight:700;'>Membership Verification Gateway</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.info("License Validity: 1-Year Full Platform Access (Data Remains Secure)")
        region = st.radio("Select your currency / region:", ["Inside India (₹50 INR)", "International ($2 USD)"])
        amount = "₹50" if "India" in region else "$2"
        
        st.warning(f"Total Subscription Amount: {amount}")
        
        with st.form("gateway_mock"):
            card_name = st.text_input("Cardholder / Account Name")
            card_num = st.text_input("UPI ID / Card Reference Number", type="password")
            submit_pay = st.form_submit_button("Complete Payment & Activate Account", use_container_width=True)
            
        if submit_pay:
            if card_name and card_num:
                current_date = datetime.now()
                expiry_date = current_date + timedelta(days=365)
                
                pay_time_str = current_date.strftime("%Y-%m-%d %H:%M:%S")
                exp_time_str = expiry_date.strftime("%Y-%m-%d %H:%M:%S")
                
                if dynamic_renew and company_id:
                    comp_data = st.session_state.db['companies'][company_id]
                    comp_data['owner']['password'] = password
                    comp_data['payment_history'].append({"paid_on": pay_time_str, "amount": amount, "expires_on": exp_time_str})
                    comp_data['expires_on'] = exp_time_str
                    st.success("Platform Subscription Renewed!")
                else:
                    new_id = str(int(time.time()))
                    st.session_state.db['companies'][new_id] = {
                        "name": f"Business Profile ({email})",
                        "owner": {"email": email, "password": password},
                        "expires_on": exp_time_str,
                        "payment_history": [{"paid_on": pay_time_str, "amount": amount, "expires_on": exp_time_str}],
                        "team": [],
                        "steps": [{"name": "Lead Captured", "role": "Admin"}, {"name": "In Progress", "role": "Team"}, {"name": "Disbursal", "role": "Admin"}],
                        "customers": []
                    }
                    st.success("Account Verification Complete!")
                
                save_db(st.session_state.db)
                st.session_state.payment_pending_for = None
                st.session_state.user = None
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("Please fill all verification metrics to process.")
        
        if st.button("Cancel Registration Pipeline", type="secondary"):
            st.session_state.payment_pending_for = None
            st.rerun()

# --- PLATFORM GATEKEEPER ENTRY ---
if st.session_state.payment_pending_for:
    pending = st.session_state.payment_pending_for
    payment_gateway_ui(pending['email'], pending['password'], pending.get('c_id'), pending.get('renew'))
    st.stop()

def login():
    display_header_logo()
    st.markdown("<h2 style='text-align: center; font-weight: 700;'>Work Flow Portal</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([0.5, 2, 0.5])
    with col:
        with st.form("auth_form"):
            u_email = st.text_input("Email ID / Identifier")
            u_pass = st.text_input("Access Password", type="password")
            u_role = st.selectbox("Role Assignment", ["Company Owner", "Team Member"])
            
            if st.form_submit_button("Log In to Workspace", use_container_width=True):
                # 1. Master System Director Protection (Automatic Login Redirection)
                if u_role == "Company Owner":
                    if u_email == st.session_state.db['super_admin']['email'] and u_pass == st.session_state.db['super_admin']['password']:
                        st.session_state.user = {"role": "super", "email": u_email}
                        st.rerun()
                
                # 2. Database Validation Checks
                found = False
                for c_id, c_data in st.session_state.db['companies'].items():
                    if u_role == "Company Owner" and c_data['owner']['email'] == u_email:
                        found = True
                        if c_data['owner']['password'] == u_pass:
                            exp_date = datetime.strptime(c_data['expires_on'], "%Y-%m-%d %H:%M:%S")
                            if datetime.now() > exp_date:
                                st.error("Membership license expired. Moving to gateway system...")
                                time.sleep(1.5)
                                st.session_state.payment_pending_for = {"email": u_email, "password": u_pass, "c_id": c_id, "renew": True}
                                st.rerun()
                            else:
                                st.session_state.user = {"role": "sub", "email": u_email, "c_id": c_id}
                                st.rerun()
                        else:
                            st.error("Invalid Secret Credentials.")
                            st.stop()
                            
                    elif u_role == "Team Member":
                        for t_member in c_data['team']:
                            if t_member['email'] == u_email and t_member['password'] == u_pass:
                                found = True
                                exp_date = datetime.strptime(c_data['expires_on'], "%Y-%m-%d %H:%M:%S")
                                if datetime.now() > exp_date:
                                    st.error("Organization membership license has expired. Contact your admin.")
                                    st.stop()
                                else:
                                    st.session_state.user = {"role": "team", "email": u_email, "c_id": c_id}
                                    st.rerun()
                
                # 3. Dynamic Automatic Self-Onboarding Routing
                if not found and u_role == "Company Owner":
                    st.info("New workspace structure detected. Initiating Payment setup...")
                    time.sleep(1.5)
                    st.session_state.payment_pending_for = {"email": u_email, "password": u_pass, "renew": False}
                    st.rerun()
                elif not found:
                    st.error("Account attributes not mapped to active systems.")

if not st.session_state.user:
    login()
    st.stop()

# --- MAIN APP ECOSYSTEM ---
user = st.session_state.user

if user is not None:
    role = user['role']

    # --- SIDEBAR INTERFACE ---
    with st.sidebar:
        if os.path.exists("logo 1.png"):
            st.image("logo 1.png", width=140)
        else:
            st.markdown("### 💼 WORK FLOW")
        st.caption("Universal Project Lifecycle System")
        st.write("---")
        
        st.subheader("Active Session")
        st.write(f"Level: **{role.upper()}**")
        st.write(f"User: `{user['email']}`")
        
        st.write("---")
        st.subheader("Navigation Links")
        if st.button("My Account Settings", use_container_width=True): pass
        if st.button("Company Profiles", use_container_width=True): pass
        if st.button("Secure Logout", use_container_width=True, type="secondary"):
            st.session_state.user = None
            st.rerun()

    # --- 1. MASTER ADMIN OPERATIONS (YOU) ---
    if role == "super":
        st.header("Global Corporate Matrix & Revenue Control")
        t1, t2, t3 = st.tabs(["Active Company Profiles", "Financial Transaction Log", "Universal Policy Links"])
        
        with t1:
            if not st.session_state.db['companies']:
                st.info("No corporate profiles running system resources currently.")
            for c_id, c_data in st.session_state.db['companies'].items():
                with st.expander(f"Business: {c_data['name']}"):
                    st.write(f"**Admin Email:** {c_data['owner']['email']} | **Secret Key:** `{c_data['owner']['password']}`")
                    st.write(f"**License Termination Date:** {c_data['expires_on']}")
                    if c_data['team']:
                        st.write("**Registered Active Staff Members:**")
                        st.table(pd.DataFrame(c_data['team']))
                    if st.button("Force Terminate Business Instance", key=f"del_{c_id}", type="secondary"):
                        del st.session_state.db['companies'][c_id]
                        save_db(st.session_state.db); st.rerun()
                        
        with t2:
            st.subheader("Platform Financial Transactions Audit Ledger")
            ledger_data = []
            for c_id, c_data in st.session_state.db['companies'].items():
                for trans in c_data.get('payment_history', []):
                    ledger_data.append({
                        "Business Profile": c_data['name'],
                        "Admin Owner": c_data['owner']['email'],
                        "Remittance Date": trans['paid_on'],
                        "Amount Collected": trans['amount'],
                        "License Expiration": trans['expires_on']
                    })
            if ledger_data:
                st.dataframe(pd.DataFrame(ledger_data), use_container_width=True)
            else:
                st.info("No transaction invoices processed yet.")
                
        with t3:
            st.subheader("Global Platform Configurations")
            st.text_input("Global Platform App Title", "WORK FLOW")
            st.write("Edit terms and conditions, terms parameters, and developer settings.")

    # --- 2. SUB-ADMIN & TEAM OPERATIONAL LAYER ---
    else:
        c_id = user['c_id']
        comp = st.session_state.db['companies'][c_id]
        
        # Automatic 7-Day Advance License Check
        expiry_dt = datetime.strptime(comp['expires_on'], "%Y-%m-%d %H:%M:%S")
        days_remaining = (expiry_dt - datetime.now()).days
        
        if days_remaining <= 7:
            st.markdown(f"""
            <div class="warning-banner">
                ⚠️ URGENT LICENSE WARNING: Your system license subscription expires in 
                {days_remaining if days_remaining > 0 else 0} days ({expiry_dt.strftime('%Y-%m-%d')}). 
                Please secure parameters before dynamic access lockout.
            </div>
            """, unsafe_allow_html=True)
            
            if role == "sub":
                if st.button("Pre-Pay Subscription License (Extend Access 1-Year Now)", type="primary", use_container_width=True):
                    st.session_state.payment_pending_for = {"email": comp['owner']['email'], "password": comp['owner']['password'], "c_id": c_id, "renew": True}
                    st.rerun()
        
        menu = ["Operations Workspace Dashboard"]
        if role == "sub": menu += ["Manage Personnel", "Pipeline Process Engineering"]
        tabs = st.tabs(menu)

        # WORKSPACE
        with tabs[0]:
            st.title(f"Operational Node - {comp['name']}")
            if role == "sub":
                with st.expander("➕ Register New Tracking Record"):
                    with st.form("add_c"):
                        cn = st.text_input("Account / Client Project Designation Name")
                        cr = st.text_input("Unique System Tracking ID Reference")
                        if st.form_submit_button("Deploy Node Record To Active Database", use_container_width=True):
                            comp['customers'].append({"name": cn, "id": cr, "stats": {s['name']: "Pending" for s in comp['steps']}})
                            save_db(st.session_state.db); st.rerun()

            st.markdown("---")
            if not comp['customers']:
                st.info("No active trackable objects processed within active company matrix branches.")
            
            for idx, cust in enumerate(comp['customers']):
                st.subheader(f"📂 Record: {cust['name']} | Tracking Reference: {cust['id']}")
                
                # THE SWIPABLE HORIZONTAL STEPPER CARD LAYOUT
                st.markdown('<div class="workflow-container">', unsafe_allow_html=True)
                cols = st.columns(len(comp['steps']))
                for i, step in enumerate(comp['steps']):
                    s_name = step['name']
                    cur_v = cust['stats'].get(s_name, "Pending")
                    with cols[i]:
                        st.markdown(f"""
                        <div class="step-box">
                            <div class="status-badge {cur_v.lower()}">{cur_v}</div>
                            <div style="font-weight:bold; font-size:0.85rem; color:#1a1c23;">{s_name}</div>
                            <div style="font-size:0.65rem; color:#6c757d; font-weight:600;">{step['role'].upper()}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        new_v = st.selectbox("Update Phase State Flags", ["Pending", "Completed", "Attention"], 
                                             index=["Pending", "Completed", "Attention"].index(cur_v),
                                             key=f"st_{idx}_{i}_{c_id}", label_visibility="collapsed")
                        if new_v != cur_v:
                            cust['stats'][s_name] = new_v
                            save_db(st.session_state.db); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # STAFF SECTOR (Only Sub-Admin)
        if role == "sub":
            with tabs[1]:
                st.subheader("Manage Personnel System Access Nodes")
                with st.form("staff"):
                    tn, te, tp = st.text_input("Operator Name"), st.text_input("Operator Email Identity"), st.text_input("Create Access Password")
                    if st.form_submit_button("Deploy Staff Login Key", use_container_width=True):
                        comp['team'].append({"name": tn, "email": te, "password": tp})
                        save_db(st.session_state.db); st.rerun()
                if comp['team']: 
                    st.dataframe(pd.DataFrame(comp['team']), use_container_width=True)

            # PIPELINE ENGINEERING (Only Sub-Admin)
            with tabs[2]:
                st.subheader("Configure Sector Pipeline Flow Phases")
                with st.form("wf"):
                    wn = st.text_input("Horizontal Phase Stage Name (e.g., Quality Check)")
                    wr = st.selectbox("Designated Processor Dynamic Link", ["Admin", "Team", "Client", "Vendor"])
                    if st.form_submit_button("Add Step to Linear Workflow", use_container_width=True):
                        comp['steps'].append({"name": wn, "role": wr})
                        for c in comp['customers']: c['stats'][wn] = "Pending"
                        save_db(st.session_state.db); st.rerun()
                
                st.write("---")
                st.subheader("Current Pipeline Linear Path Structure")
                for j, s in enumerate(comp['steps']):
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"➡️ **{s['name']}** ({s['role'].upper()})")
                    if c2.button("Remove Phase", key=f"ds_{j}", type="secondary"):
                        comp['steps'].pop(j)
                        save_db(st.session_state.db); st.rerun()

# --- PROFESSIONAL CORPORATE FOOTER ---
st.write("---")
st.markdown("""
<div style='text-align: center; font-size:0.85rem; color: #495057; padding: 15px 0;'>
    <strong>Work Flow</strong> Universal CRM Platform — v8 Enterprise | Track Your Work System <br>
    <a href='#' style='color:#1a1c23; text-decoration:none; margin:0 10px;'>Terms & Conditions</a> | 
    <a href='#' style='color:#1a1c23; text-decoration:none; margin:0 10px;'>My Account</a> | 
    <a href='#' style='color:#1a1c23; text-decoration:none; margin:0 10px;'>Settings</a> | 
    <a href='#' style='color:#1a1c23; text-decoration:none; margin:0 10px;'>Profile Help</a>
</div>
<div style='text-align: center; color: rgba(0,0,0,0.15); font-size: 0.65rem; margin-top:-5px;'>
    Activate Windows | Go to Settings to activate Windows.
</div>
""", unsafe_allow_html=True)