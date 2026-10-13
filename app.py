import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from pathlib import Path

st.set_page_config(page_title="IT Pulse | Incident Management", page_icon="🛠️", layout="wide")

DATA_FILE = Path("incidents.csv")

SEED_DATA = [
    {"Incident ID":"INC-1001","Title":"VPN connection failure","Category":"Network","Severity":"High","Priority":"P1","Status":"In Progress","Assignee":"A. Sharma","Reported By":"R. Mehta","Created Date":"2026-10-10","Resolution Hours":0,"Description":"Remote users unable to connect to corporate VPN."},
    {"Incident ID":"INC-1002","Title":"Password reset request","Category":"Access","Severity":"Low","Priority":"P3","Status":"Resolved","Assignee":"S. Khan","Reported By":"P. Verma","Created Date":"2026-10-09","Resolution Hours":1.5,"Description":"User locked out after multiple unsuccessful login attempts."},
    {"Incident ID":"INC-1003","Title":"ERP application unavailable","Category":"Application","Severity":"Critical","Priority":"P1","Status":"Open","Assignee":"N. Gupta","Reported By":"Finance Team","Created Date":"2026-10-12","Resolution Hours":0,"Description":"Finance team cannot access the ERP application."},
    {"Incident ID":"INC-1004","Title":"Printer not responding","Category":"Hardware","Severity":"Medium","Priority":"P2","Status":"Open","Assignee":"A. Sharma","Reported By":"Admin Team","Created Date":"2026-10-11","Resolution Hours":0,"Description":"Floor 3 network printer is not responding."},
    {"Incident ID":"INC-1005","Title":"Email delivery delay","Category":"Application","Severity":"Medium","Priority":"P2","Status":"Resolved","Assignee":"S. Khan","Reported By":"Sales Team","Created Date":"2026-10-08","Resolution Hours":3.0,"Description":"Outgoing emails were delayed for several users."},
    {"Incident ID":"INC-1006","Title":"Employee portal access issue","Category":"Access","Severity":"High","Priority":"P1","Status":"In Progress","Assignee":"N. Gupta","Reported By":"HR Team","Created Date":"2026-10-12","Resolution Hours":0,"Description":"HR staff receive an access-denied message in the portal."},
    {"Incident ID":"INC-1007","Title":"Laptop battery fault","Category":"Hardware","Severity":"Low","Priority":"P3","Status":"Closed","Assignee":"A. Sharma","Reported By":"M. Joshi","Created Date":"2026-10-06","Resolution Hours":5.0,"Description":"Laptop battery replaced and device returned to user."},
    {"Incident ID":"INC-1008","Title":"Intermittent Wi-Fi outage","Category":"Network","Severity":"High","Priority":"P2","Status":"Open","Assignee":"S. Khan","Reported By":"Operations","Created Date":"2026-10-13","Resolution Hours":0,"Description":"Intermittent Wi-Fi drops reported in the meeting area."},
    {"Incident ID":"INC-1009","Title":"Software installation request","Category":"Application","Severity":"Low","Priority":"P3","Status":"Resolved","Assignee":"N. Gupta","Reported By":"K. Rao","Created Date":"2026-10-07","Resolution Hours":2.0,"Description":"Approved software installed on user workstation."},
    {"Incident ID":"INC-1010","Title":"Database response time elevated","Category":"Database","Severity":"Critical","Priority":"P1","Status":"In Progress","Assignee":"A. Sharma","Reported By":"IT Monitoring","Created Date":"2026-10-13","Resolution Hours":0,"Description":"Database queries are slower than expected, affecting reporting."},
]

def load_data():
    if DATA_FILE.exists():
        try:
            df = pd.read_csv(DATA_FILE)
            if not df.empty and "Incident ID" in df.columns:
                return df
        except Exception:
            pass
    df = pd.DataFrame(SEED_DATA)
    df.to_csv(DATA_FILE, index=False)
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

if "incidents" not in st.session_state:
    st.session_state.incidents = load_data()

df = st.session_state.incidents.copy()
st.title("🛠️ IT Pulse")
st.caption("IT Incident Management Simulator · Track, prioritize, and resolve service incidents")
st.markdown("---")

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Dashboard", "Incident Register", "Log an Incident", "Escalation Guide"])
    st.markdown("---")
    st.caption("Demo environment · Sample records are simulated")
    if st.button("Reset demo data", use_container_width=True):
        st.session_state.incidents = pd.DataFrame(SEED_DATA)
        save_data(st.session_state.incidents)
        st.rerun()

if page == "Dashboard":
    st.subheader("Operations Overview")
    total = len(df)
    open_count = int(df["Status"].isin(["Open", "In Progress"]).sum())
    critical = int(((df["Severity"] == "Critical") & (df["Status"].isin(["Open", "In Progress"]))).sum())
    resolved = int(df["Status"].isin(["Resolved", "Closed"]).sum())
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Incidents", total)
    c2.metric("Open / In Progress", open_count)
    c3.metric("Active Critical", critical)
    c4.metric("Resolved / Closed", resolved)

    left, right = st.columns(2)
    with left:
        st.markdown("#### Incidents by Severity")
        sev_order = ["Critical","High","Medium","Low"]
        sev = df["Severity"].value_counts().reindex(sev_order, fill_value=0).rename_axis("Severity").reset_index(name="Count")
        st.plotly_chart(px.bar(sev, x="Severity", y="Count", color="Severity", category_orders={"Severity":sev_order}), use_container_width=True)
    with right:
        st.markdown("#### Incidents by Status")
        status = df["Status"].value_counts().rename_axis("Status").reset_index(name="Count")
        st.plotly_chart(px.pie(status, names="Status", values="Count", hole=0.45), use_container_width=True)

    st.markdown("#### Active High-Priority Queue")
    active = df[(df["Status"].isin(["Open","In Progress"])) & (df["Priority"].isin(["P1","P2"]))].copy()
    if active.empty:
        st.success("No active P1/P2 incidents.")
    else:
        st.dataframe(active[["Incident ID","Title","Severity","Priority","Status","Assignee","Created Date"]], use_container_width=True, hide_index=True)
    st.info("Demo note: the included records are simulated for portfolio demonstration, not real company incidents.")

elif page == "Incident Register":
    st.subheader("Incident Register")
    f1,f2,f3 = st.columns(3)
    with f1:
        status_filter = st.multiselect("Status", sorted(df["Status"].dropna().unique()), default=sorted(df["Status"].dropna().unique()))
    with f2:
        severity_filter = st.multiselect("Severity", ["Critical","High","Medium","Low"], default=["Critical","High","Medium","Low"])
    with f3:
        search = st.text_input("Search ID, title, or assignee")
    filtered = df[df["Status"].isin(status_filter) & df["Severity"].isin(severity_filter)]
    if search:
        mask = filtered.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        filtered = filtered[mask]
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export visible records to CSV", filtered.to_csv(index=False).encode("utf-8"), file_name="it_pulse_incidents.csv", mime="text/csv")
    st.markdown("#### Update an incident")
    ids = df["Incident ID"].astype(str).tolist()
    selected_id = st.selectbox("Incident ID", ids)
    selected_row = df[df["Incident ID"].astype(str) == selected_id].iloc[0]
    with st.form("update_form"):
        new_status = st.selectbox("New status", ["Open","In Progress","Resolved","Closed"], index=["Open","In Progress","Resolved","Closed"].index(selected_row["Status"]))
        new_assignee = st.text_input("Assignee", str(selected_row.get("Assignee","")))
        resolution_hours = st.number_input("Resolution hours (0 if unresolved)", min_value=0.0, value=float(selected_row.get("Resolution Hours",0) or 0), step=0.5)
        submitted = st.form_submit_button("Save incident update")
    if submitted:
        idx = st.session_state.incidents.index[st.session_state.incidents["Incident ID"].astype(str) == selected_id][0]
        st.session_state.incidents.loc[idx, "Status"] = new_status
        st.session_state.incidents.loc[idx, "Assignee"] = new_assignee
        st.session_state.incidents.loc[idx, "Resolution Hours"] = resolution_hours
        save_data(st.session_state.incidents)
        st.success(f"{selected_id} updated.")
        st.rerun()

elif page == "Log an Incident":
    st.subheader("Log a New Incident")
    with st.form("new_incident", clear_on_submit=True):
        title = st.text_input("Short incident title", placeholder="e.g., Shared drive unavailable", max_chars=100)
        description = st.text_area("Description", placeholder="What is affected? What is the user experiencing?")
        a,b = st.columns(2)
        with a:
            category = st.selectbox("Category", ["Application","Network","Hardware","Access","Database","Other"])
            severity = st.selectbox("Severity", ["Critical","High","Medium","Low"])
            priority_map = {"Critical":"P1","High":"P1","Medium":"P2","Low":"P3"}
            priority = st.selectbox("Priority", ["P1","P2","P3"], index=["P1","P2","P3"].index(priority_map[severity]))
        with b:
            reported_by = st.text_input("Reported by", placeholder="Team or requester")
            assignee = st.text_input("Assigned to", placeholder="IT support owner")
            created = st.date_input("Date reported", value=date.today())
        submit = st.form_submit_button("Create incident")
    if submit:
        if not title.strip():
            st.error("Please enter an incident title.")
        else:
            existing = st.session_state.incidents["Incident ID"].astype(str).tolist()
            nums = [int(x.split("-")[1]) for x in existing if x.startswith("INC-") and x.split("-")[1].isdigit()]
            incident_id = f"INC-{max(nums+[1000])+1}"
            new_row = {"Incident ID":incident_id,"Title":title.strip(),"Category":category,"Severity":severity,"Priority":priority,"Status":"Open","Assignee":assignee.strip() or "Unassigned","Reported By":reported_by.strip() or "Not specified","Created Date":created.isoformat(),"Resolution Hours":0,"Description":description.strip()}
            st.session_state.incidents = pd.concat([st.session_state.incidents, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.incidents)
            st.success(f"Incident created successfully: {incident_id}")
            st.rerun()

elif page == "Escalation Guide":
    st.subheader("Escalation & Handling Guide")
    st.caption("Illustrative rules for this simulator; adapt to an organization's approved ITIL/SLA policy.")
    rules = pd.DataFrame([
        {"Level":"P1 / Critical","Example":"Core application outage, major business impact","Suggested action":"Notify IT lead immediately; assign owner; frequent updates"},
        {"Level":"P2 / High","Example":"Multiple users affected; major function degraded","Suggested action":"Prioritize queue; notify support lead if not progressing"},
        {"Level":"P3 / Medium","Example":"Limited impact or workaround available","Suggested action":"Assign to relevant support team; track against target"},
        {"Level":"P4 / Low","Example":"Routine request or minor inconvenience","Suggested action":"Handle in normal queue; document completion"},
    ])
    st.dataframe(rules, use_container_width=True, hide_index=True)
    st.markdown("#### Suggested incident lifecycle")
    st.write("**Log → Categorize → Prioritize → Assign → Investigate → Resolve → Validate with requester → Close → Document lessons learned**")
    st.markdown("#### Closure checklist")
    st.checkbox("Resolution steps documented")
    st.checkbox("Requester or service owner informed")
    st.checkbox("Root cause / workaround captured where relevant")
    st.checkbox("Incident status updated and closure validated")

st.markdown("---")
st.caption("IT Pulse · Portfolio project · Python · Streamlit · Pandas · Plotly")
