import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# --- 1. SETTINGS & STYLING ---
CSV_FILE = "tracker_data.csv"
JSON_FILE = "user_settings.json"

st.set_page_config(page_title="Apex Hybrid Analytics", layout="wide")

# Custom CSS (Identical to your V4)
st.markdown("""
    <style>
    .app-title { text-align: center; font-size: 28px; font-weight: 700; letter-spacing: 1.5px; margin-top: -10px; margin-bottom: 8px; color: #F5F5F5; }
    .app-subtitle { text-align: center; font-size: 13px; color: #A0A0A0; margin-bottom: 25px; }
    .title-divider { border-bottom: 1px solid #2f3338; margin-bottom: 30px; }
    .profession-box { background-color: #1e3a8a; color: #60a5fa; padding: 10px; border-radius: 8px; margin-bottom: 10px; font-weight: bold; }
    .timer-box { background-color: #424211; color: #d4d444; padding: 10px; border-radius: 8px; font-weight: bold; }
    .status-line { font-size: 24px; font-weight: bold; margin-top: 25px; margin-bottom: 35px; }
    .report-box { background-color: #111827; border: 1px solid #374151; padding: 14px; border-radius: 8px; margin-top: 12px; color: #E5E7EB; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA HELPERS ---
def load_settings():
    if not os.path.isfile(JSON_FILE) or os.stat(JSON_FILE).st_size == 0: return None
    try:
        with open(JSON_FILE, "r") as f: settings = json.load(f)
    except json.JSONDecodeError: return None
    settings.setdefault("logs_completed", 0); settings.setdefault("last_log_timestamp", None)
    settings.setdefault("obs_steps", []); settings.setdefault("block_active", False)
    settings.setdefault("current_day", 0); settings.setdefault("plan", [])
    settings.setdefault("last_report", "No reports generated yet."); settings.setdefault("reports", [])
    settings.setdefault("best_week_steps", [0]*7) # Stores the 7-day step counts of the best week
    return settings

def save_settings(settings):
    with open(JSON_FILE, "w") as f: json.dump(settings, f, indent=4)

def format_wait_time(hours_decimal):
    if hours_decimal <= 0: return "Ready"
    total_minutes = int(round(hours_decimal * 60))
    h, m = total_minutes // 60, total_minutes % 60
    return f"{m}m left" if h == 0 else f"{h}h {m}m left"

def get_wait_time(settings):
    if not settings.get("last_log_timestamp"): return 0
    last_log = datetime.fromisoformat(settings["last_log_timestamp"])
    time_diff = datetime.now() - last_log
    if time_diff < timedelta(hours=18): return round(18 - (time_diff.total_seconds() / 3600), 2)
    return 0

def add_report(settings, report_type, summary, details=None):
    report = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "type": report_type, "summary": summary}
    settings.setdefault("reports", []); settings["reports"].append(report)
    settings["last_report"] = summary

# --- 3. ONBOARDING ---
settings = load_settings()

if settings is None:
    st.markdown('<div class="app-title">APEX HYBRID ANALYTICS</div>', unsafe_allow_html=True)
    with st.form("onboarding"):
        name = st.text_input("What is your name?").strip().capitalize()
        prof = st.text_input("What is your profession?").strip().capitalize()
        confirm_profile = st.checkbox("I am ready to create my profile.")
        if st.form_submit_button("Initialize Profile") and name and prof and confirm_profile:
            new_settings = {"user_name": name, "profession": prof, "logs_completed": 0,
                            "last_log_timestamp": None, "obs_steps": [], "block_active": False,
                            "current_day": 0, "plan": [], "last_report": "Profile initialized.",
                            "reports": [], "best_week_steps": [0]*7}
            save_settings(new_settings);
            st.rerun()
else:
    st.markdown('<div class="app-title">APEX HYBRID ANALYTICS</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Hybrid performance tracking and adaptive strategy management</div>', unsafe_allow_html=True)
    st.markdown('<div class="title-divider"></div>', unsafe_allow_html=True)

    # --- SIDEBAR ---
    st.sidebar.title(f"💪 {settings['user_name']}")
    st.sidebar.markdown(f'<div class="profession-box">Profession: {settings["profession"]}</div>', unsafe_allow_html=True)
    wait = get_wait_time(settings)
    if wait > 0:
        st.sidebar.markdown(f'<div class="timer-box">🕒 Next Log in: {format_wait_time(wait)}</div>', unsafe_allow_html=True)
    else:
        st.sidebar.success("Ready for Daily Update")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🎯 Goal Setter", "📋 Checklist", "📝 Daily Log"])

    # --- TAB 1: DASHBOARD (Updated with Best Week Comparison) ---
    with tab1:
        st.header(f"Athlete Performance: {settings['user_name']}")
        
        # 1. KPI Metrics
        kpi1, kpi2, kpi3 = st.columns(3)
        if os.path.isfile(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            if not df.empty:
                kpi1.metric("7-Day Avg Steps", int(df["Steps"].tail(7).mean()))
                kpi2.metric("Total Logs", settings["logs_completed"])
                kpi3.metric("Last Workout", df["Workout"].iloc[-1])

        # 2. The Status Line
        if settings["block_active"] and settings["plan"]:
            target = settings["plan"][settings["current_day"] - 1]
            st.markdown(f'<div class="status-line">📍 Day {settings["current_day"]} of 7 | Target: {target["steps"]} Steps</div>', unsafe_allow_html=True)
        
        if os.path.isfile(CSV_FILE):
            df = pd.read_csv(CSV_FILE).tail(7)
            if not df.empty:
                st.subheader("Performance Comparison: Current vs Best Week")
                fig = go.Figure()
                # Current Week Line
                fig.add_trace(go.Scatter(x=list(range(1, len(df)+1)), y=df["Steps"], name="Current Week", line=dict(color='#00FFCC', width=3), mode='lines+markers'))
                # Best Week Line (The Shadow)
                fig.add_trace(go.Scatter(x=list(range(1, 8)), y=settings["best_week_steps"], name="Best Week (Peak)", line=dict(color='rgba(255, 255, 255, 0.2)', width=2, dash='dash'), mode='lines'))
                fig.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117", font_color="#FFFFFF", xaxis_title="Day of Week", yaxis_title="Steps")
                st.plotly_chart(fig, use_container_width=True)
        st.markdown(f'<div class="report-box">{settings.get("last_report", "No reports generated yet.")}</div>', unsafe_allow_html=True)

                # 4. The Latest Report Box (RESTORED)
        st.markdown("### Latest Intelligence")
        st.markdown(f'<div class="report-box">{settings.get("last_report", "No reports generated yet.")}</div>', unsafe_allow_html=True)

        # 5. The Report History Expander (RESTORED)
        if settings.get("reports"):
            with st.expander("View Weekly Performance History"):
                for report in reversed(settings["reports"][-5:]): # Shows last 5 events
                    st.write(f"**{report['timestamp']}** — {report['type']}")
                    st.write(report["summary"])
                    st.write("---")
                    
    # --- TAB 2: GOAL SETTER (Updated to 7 Days + Template Logic) ---
    with tab2:
        st.header("Weekly Strategy Session")
        
        can_set = True
        if settings["block_active"]:
            # Display warning if the 7-day block is not yet finished
            st.warning(f"⚠️ A 7-Day Block is currently in progress (Day {settings['current_day']} of 7).")
            
            override = st.checkbox("I want to cancel my current goals and start a new strategy.")
            
            if not override:
                st.info("Complete your current 7-day cycle to maintain a perfect performance average!")
                can_set = False
            else:
                st.error("Warning: Overriding will mark this current week as 'Incomplete' in your history.")

        if can_set:
            use_template = st.button("Reload Previous 7-Day Plan as Template")
            with st.form("goal_setter"):

                st.write("Plan your full Monday - Sunday routine:")
                new_plan = []
                # 7 Day Grid Layout
                row1 = st.columns(4)
                row2 = st.columns(3)
                all_cols = row1 + row2
                
                for i in range(1, 8):
                    all_cols[i-1].subheader(f"Day {i}")
                    # Pre-fill if template used, else use defaults
                    def_steps = settings["plan"][i-1]["steps"] if use_template and len(settings["plan"]) >= 7 else 10000
                    def_water = settings["plan"][i-1]["water"] if use_template and len(settings["plan"]) >= 7 else 3.0
                    
                    s = all_cols[i-1].number_input(f"Steps", value=def_steps, step=500, key=f"s{i}")
                    w = all_cols[i-1].number_input(f"Water (L)", value=def_water, step=0.5, key=f"w{i}")
                    wk = all_cols[i-1].selectbox(f"Workout", ["Hybrid", "Gym", "Rest"], key=f"wk{i}")
                    new_plan.append({"steps": s, "water": w, "workout": wk})

                confirm_strategy = st.checkbox("Confirm: I verify this 7-day performance strategy.")
                if st.form_submit_button("Lock Weekly Strategy") and confirm_strategy:
                    settings["plan"] = new_plan; settings["block_active"] = True; settings["current_day"] = 1
                    save_settings(settings); st.success("Weekly Strategy Locked!"); st.rerun()

    # --- TAB 3: CHECKLIST (Identical Structure) ---
    with tab3:
        st.header("Daily Strategy")
        if settings["block_active"]:
            t = settings["plan"][settings["current_day"] - 1]
            st.subheader(f"Strategy for Today — Day {settings['current_day']} of 7")
            st.write(f"✅ Walk **{t['steps']}** steps. | ✅ Drink **{t['water']}L** water. | ✅ Complete **{t['workout']}** workout.")

    # --- TAB 4: DAILY LOG (Updated with Tiered 3000 Step AI Logic) ---
    with tab4:
        st.header("End-of-Day Update")
        if wait > 0: st.error(f"Access Denied: Please wait {format_wait_time(wait)}.")
        else:
            with st.form("daily_update"):
                s_act = st.number_input("Actual Steps", value=None, placeholder="Enter steps...")
                c_act = st.number_input("Actual Calories", value=None, placeholder="Enter calories...")
                w_act = st.number_input("Actual Water (L)", value=None, placeholder="Enter liters...")
                wk_act = st.selectbox("Actual Workout Done", ["Hybrid", "Gym", "Rest"])
                sl_act = st.number_input("Actual Sleep Hours", value=None, placeholder="Enter hours...")
                verify = st.checkbox("I verify today's data is accurate.")

                if st.form_submit_button("Submit & Generate Report"):
                    if not verify: st.error("Please check the verification box.")
                    elif any(v is None for v in [s_act, c_act, w_act, sl_act]): st.error("Please fill in all fields.")
                    else:
                        file_exists = os.path.isfile(CSV_FILE)
                        new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), settings["user_name"], s_act, c_act, w_act, wk_act, sl_act]], columns=["Date", "Name", "Steps", "Calories", "Water", "Workout", "Sleep"])
                        new_row.to_csv(CSV_FILE, mode="a", header=not file_exists, index=False)
                        
                        settings["logs_completed"] += 1; settings["last_log_timestamp"] = datetime.now().isoformat()
                        
                        if settings["block_active"]:
                            target = settings["plan"][settings["current_day"] - 1]
                            deficit = target["steps"] - s_act
                            
                            # AI RE-BALANCER (Tiered Logic)
                            if deficit > 0 and settings["current_day"] < 7:
                                if deficit > 3000: # HEAVY DEFICIT: Hunt for Rest Day
                                    found_rest = False
                                    for i in range(settings["current_day"], 7):
                                        if settings["plan"][i]["workout"] == "Rest":
                                            settings["plan"][i]["steps"] += deficit
                                            found_rest = True; break
                                    if not found_rest: # No rest day left, distribute as average
                                        adj = int(deficit / (7 - settings["current_day"]))
                                        for i in range(settings["current_day"], 7): settings["plan"][i]["steps"] += adj
                                else: # MINOR DEFICIT: Spred across all days
                                    adj = int(deficit / (7 - settings["current_day"]))
                                    for i in range(settings["current_day"], 7): settings["plan"][i]["steps"] += adj
                            
                            report_summary = f"Day {settings['current_day']} Report: {'✅ Success' if deficit <= 0 else '⚠️ Adjusted'}"
                            add_report(settings, "Daily Log", report_summary)
                            
                            settings["current_day"] += 1
                            if settings["current_day"] > 7:
                                # End of week: Check if this is the new "Best Week"
                                week_total = sum(d['steps'] for d in settings["plan"])
                                if week_total > sum(settings["best_week_steps"]):
                                    settings["best_week_steps"] = [d['steps'] for d in settings["plan"]]
                                settings["block_active"] = False
                        
                        save_settings(settings); st.success("Stats submitted."); st.rerun()