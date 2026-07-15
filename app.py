import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta, date
import plotly.express as px
import plotly.graph_objects as go

# --- 1. SETTINGS & STYLING ---
CSV_FILE = "tracker_data.csv"
WORKOUT_CSV = "workout_data.csv"
JSON_FILE = "user_settings.json"

st.set_page_config(page_title="Apex Hybrid Analytics", layout="wide")

# Custom CSS (Identical to V5)
st.markdown("""
    <style>
    .app-title { text-align: center; font-size: 28px; font-weight: 700; letter-spacing: 1.5px; margin-top: -10px; margin-bottom: 8px; color: #F5F5F5; }
    .app-subtitle { text-align: center; font-size: 13px; color: #A0A0A0; margin-bottom: 25px; }
    .title-divider { border-bottom: 1px solid #2f3338; margin-bottom: 30px; }
    .profession-box { background-color: #1e3a8a; color: #60a5fa; padding: 10px; border-radius: 8px; margin-bottom: 10px; font-weight: bold; }
    .timer-box { background-color: #424211; color: #d4d444; padding: 10px; border-radius: 8px; font-weight: bold; }
    .status-line { font-size: 24px; font-weight: bold; margin-top: 25px; margin-bottom: 35px; }
    .report-box { background-color: #111827; border: 1px solid #374151; padding: 14px; border-radius: 8px; margin-top: 12px; color: #E5E7EB; }
    .suggestion-card { background-color: #1f2937; padding: 15px; border-radius: 8px; border-left: 4px solid #00FFCC; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA HELPERS ---
GYM_EXERCISES = ["Squats", "Bench Press", "Deadlift", "Overhead Press", "Barbell Row", "Custom"]
HYBRID_EXERCISES = ["Sled Push", "Wall Balls", "1km Run", "Burpee Broad Jump", "Farmers Carry", "Custom"]

def load_settings():
    if not os.path.isfile(JSON_FILE) or os.stat(JSON_FILE).st_size == 0: return None
    try:
        with open(JSON_FILE, "r") as f: settings = json.load(f)
    except json.JSONDecodeError: return None
    # Backward Compatibility (V1-V6)
    settings.setdefault("logs_completed", 0); settings.setdefault("last_log_timestamp", None)
    settings.setdefault("obs_steps", []); settings.setdefault("block_active", False)
    settings.setdefault("current_day", 0); settings.setdefault("plan", [])
    settings.setdefault("last_report", "No reports generated yet."); settings.setdefault("reports", [])
    settings.setdefault("best_week_steps", [0]*7); settings.setdefault("start_date", None)
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
    if datetime.now() - last_log < timedelta(hours=18):
        return round(18 - ((datetime.now() - last_log).total_seconds() / 3600), 2)
    return 0

def add_report(settings, r_type, summary):
    report = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "type": r_type, "summary": summary}
    settings.setdefault("reports", []).append(report)
    settings["last_report"] = summary

def suggest_water(workout_type, last_sleep):
    """AI Water Formula: 3.5L base + bonuses"""
    water = 3.5
    if workout_type in ["Hybrid", "Gym"]: water += 0.5
    if last_sleep and last_sleep < 6: water += 0.5
    return water

def get_last_exercise_weight(exercise_name, user_name):
    """Retrieves the last recorded weight for an exercise from workout CSV"""
    if not os.path.isfile(WORKOUT_CSV): return None
    try:
        df = pd.read_csv(WORKOUT_CSV)
        history = df[(df['Exercise'] == exercise_name) & (df['User'] == user_name)]
        if not history.empty: return history.iloc[-1]['Actual_Weight']
    except: pass
    return None

# --- 3. ONBOARDING ---
settings = load_settings()
if settings is None:
    st.markdown('<div class="app-title">APEX HYBRID ANALYTICS</div>', unsafe_allow_html=True)
    with st.form("onboarding"):
        name = st.text_input("What is your name?").strip().capitalize()
        prof = st.text_input("What is your profession?").strip().capitalize()
        confirm = st.checkbox("I am ready to create my profile.")
        if st.form_submit_button("Initialize Profile") and name and prof and confirm:
            new_settings = {
                "user_name": name, "profession": prof, "logs_completed": 0, "last_log_timestamp": None,
                "obs_steps": [], "block_active": False, "current_day": 0, "plan": [],
                "last_report": "Profile initialized. Please set your weekly goals!", "reports": [],
                "best_week_steps": [0]*7, "start_date": None
            }
            save_settings(new_settings); st.rerun()
else:
    st.markdown('<div class="app-title">APEX HYBRID ANALYTICS</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Hybrid performance tracking and adaptive strategy management</div>', unsafe_allow_html=True)
    st.markdown('<div class="title-divider"></div>', unsafe_allow_html=True)

    # --- SIDEBAR (UNTOUCHED) ---
    st.sidebar.title(f"💪 {settings['user_name']}")
    st.sidebar.markdown(f'<div class="profession-box">Profession: {settings["profession"]}</div>', unsafe_allow_html=True)
    wait = get_wait_time(settings)
    if wait > 0:
        st.sidebar.markdown(f'<div class="timer-box">🕒 Next Log in: {format_wait_time(wait)}</div>', unsafe_allow_html=True)
    else: st.sidebar.success("Ready for Daily Update")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🎯 Goal Setter", "📋 Checklist", "📝 Daily Log"])

    # --- TAB 1: DASHBOARD ---
    with tab1:
        st.header(f"Athlete Performance: {settings['user_name']}")
        
        # Suggestion for new user
        if not settings["block_active"] and settings["logs_completed"] == 0:
            st.info("👋 Welcome! Head over to the **Goal Setter** tab to plan your first 7-day performance block.")

        kpi1, kpi2, kpi3 = st.columns(3)
        if os.path.isfile(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            if not df.empty:
                kpi1.metric("7-Day Avg Steps", int(df["Steps"].tail(7).mean()))
                kpi2.metric("Total Logs", settings["logs_completed"])
                kpi3.metric("Last Workout", df["Workout"].iloc[-1])

        # NEW: Progressive Overload Card (Below KPIs)
        if os.path.isfile(WORKOUT_CSV):
            wdf = pd.read_csv(WORKOUT_CSV)
            if not wdf.empty:
                last_ex = wdf.iloc[-1]
                st.markdown(f'''<div class="suggestion-card">
                <b>🏋️ Progressive Overload Tracker:</b><br>
                Last {last_ex['Exercise']}: <b>{last_ex['Actual_Weight']}kg</b> x {last_ex['Actual_Reps']} reps.<br>
                <i>Suggestion: Try {float(last_ex['Actual_Weight']) + 2.5}kg or add 1 rep next time.</i>
                </div>''', unsafe_allow_html=True)

        if settings["block_active"] and settings["plan"]:
            target = settings["plan"][settings["current_day"] - 1]
            st.markdown(f'<div class="status-line">📍 Day {settings["current_day"]} of 7 | Target: {target["steps"]} Steps</div>', unsafe_allow_html=True)
        
        # Comparison Chart
        if os.path.isfile(CSV_FILE):
            df_chart = pd.read_csv(CSV_FILE).tail(7)
            if not df_chart.empty:
                st.subheader("Performance Comparison: Current vs Best Week")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=list(range(1, len(df_chart)+1)), y=df_chart["Steps"], name="Current Week", line=dict(color='#00FFCC', width=3), mode='lines+markers'))
                fig.add_trace(go.Scatter(x=list(range(1, 8)), y=settings["best_week_steps"], name="Best Week", line=dict(color='rgba(255, 255, 255, 0.2)', width=2, dash='dash'), mode='lines'))
                fig.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117", font_color="#FFFFFF")
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Latest Intelligence")
        st.markdown(f'<div class="report-box">{settings.get("last_report")}</div>', unsafe_allow_html=True)
        if settings.get("reports"):
            with st.expander("View Report History"):
                for r in reversed(settings["reports"][-5:]):
                    st.write(f"**{r['timestamp']}** — {r['type']}: {r['summary']}")

    # --- TAB 2: GOAL SETTER (Excel Style) ---

    with tab2:
        st.header("Weekly Strategy Session")
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Initialize session state for the 2-step wizard
        if "base_plan_saved" not in st.session_state:
            st.session_state.base_plan_saved = False
        if "base_plan_data" not in st.session_state:
            st.session_state.base_plan_data = None
        if "exercise_data" not in st.session_state:
            st.session_state.exercise_data = {}

        # ============ SECTION 1: BASE PLAN ============
        st.subheader("Section 1: Base Weekly Plan")

        if not st.session_state.base_plan_saved:
            # EDITABLE MODE
            start_date_input = st.date_input("📅 Choose the start date of your 7-day plan", value=date.today(), key="start_date_picker")
            
            with st.form("base_plan_form"):
                h = st.columns([1.5, 1, 1, 1])
                h[0].markdown("**Day / Date**")
                h[1].markdown("**Steps Target**")
                h[2].markdown("**Water (L)**")
                h[3].markdown("**Workout Type**")
                
                temp_plan = []
                for i in range(7):
                    day_date = start_date_input + timedelta(days=i)
                    date_label = f"{days[day_date.weekday()]}\n{day_date.strftime('%b %d')}"
                    
                    row = st.columns([1.5, 1, 1, 1])
                    row[0].markdown(f"**{date_label}**")
                    steps = row[1].number_input(f"s{i}", value=10000, step=500, label_visibility="collapsed", key=f"s_{i}")
                    water = row[2].number_input(f"w{i}", value=3.5, step=0.1, label_visibility="collapsed", key=f"w_{i}")
                    workout = row[3].selectbox(f"wk{i}", ["Rest", "Hybrid", "Gym"], label_visibility="collapsed", key=f"wk_{i}")
                    
                    temp_plan.append({
                        "date": str(day_date),
                        "day_name": days[day_date.weekday()],
                        "steps": steps,
                        "water": water,
                        "workout": workout,
                        "exercises": []
                    })
                
                if st.form_submit_button("Save Base Plan"):
                    # Blocking validations
                    workout_days = [d for d in temp_plan if d["workout"] in ["Gym", "Hybrid"]]
                    rest_days = [d for d in temp_plan if d["workout"] == "Rest"]
                    
                    if len(workout_days) == 0:
                        st.error("⚠️ All days are Rest — this plan won't be worth it. Please add some workout days.")
                    elif len(rest_days) == 0:
                        st.error("⚠️ You need at least one Rest day for recovery.")
                    else:
                        st.session_state.base_plan_data = temp_plan
                        st.session_state.base_plan_saved = True
                        st.session_state.exercise_data = {}  # reset exercises when new base plan is saved
                        st.rerun()
        else:
            # READ-ONLY MODE (Grayed out summary)
            st.info("✅ Base Plan Saved. Review it below or click 'Edit Base Plan' to change.")
            summary_df = pd.DataFrame([
                {"Day": f"{d['day_name']}, {d['date']}", "Steps": d["steps"], "Water (L)": d["water"], "Workout": d["workout"]}
                for d in st.session_state.base_plan_data
            ])
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
            
            if st.button("✏️ Edit Base Plan"):
                st.session_state.base_plan_saved = False
                st.session_state.exercise_data = {}  # auto-clear exercises
                st.rerun()

        # ============ SECTION 2: EXERCISE DETAILS ============
        st.markdown("---")
        st.subheader("Section 2: Exercise Details")
        
        if not st.session_state.base_plan_saved:
            st.info("👆 Please save your Base Plan in Section 1 first to unlock Exercise Details.")
        else:
            base_plan = st.session_state.base_plan_data
            workout_indices = [i for i, d in enumerate(base_plan) if d["workout"] in ["Gym", "Hybrid"]]
            
            if not workout_indices:
                st.info("No Gym/Hybrid days in your plan.")
            else:
                st.write("Add specific exercises for your workout days:")
                for i in workout_indices:
                    day = base_plan[i]
                    with st.expander(f"{day['day_name']}, {day['date']} — {day['workout']} Details"):
                        options = GYM_EXERCISES if day["workout"] == "Gym" else HYBRID_EXERCISES
                        selected = st.multiselect(f"Exercises", options, key=f"ex_{i}")
                        custom = st.text_input(f"Custom exercises (comma separated)", key=f"cust_{i}")
                        custom_list = [c.strip() for c in custom.split(",") if c.strip()]
                        st.session_state.exercise_data[i] = selected + custom_list
            
            # Lock Weekly Strategy Button
            st.markdown("---")
            if st.button("🔒 Lock Weekly Strategy"):
                # Merge exercises into base plan
                final_plan = st.session_state.base_plan_data.copy()
                for i, exs in st.session_state.exercise_data.items():
                    final_plan[i]["exercises"] = exs
                
                # OVERRIDE WARNING (appears only if block is active)
                if settings["block_active"]:
                    st.session_state.pending_plan = final_plan
                    st.session_state.show_override = True
                    st.rerun()
                else:
                    # No active block — save directly
                    settings["plan"] = final_plan
                    settings["block_active"] = True
                    settings["current_day"] = 1
                    settings["start_date"] = final_plan[0]["date"]
                    save_settings(settings)
                    st.success("✅ Weekly Strategy Locked!")
                    # Reset wizard state
                    st.session_state.base_plan_saved = False
                    st.session_state.base_plan_data = None
                    st.session_state.exercise_data = {}
                    st.rerun()
            
            # Override confirmation (appears after Lock button if block is active)
            if st.session_state.get("show_override", False):
                st.warning(f"⚠️ A 7-Day Block is currently in progress (Day {settings['current_day']} of 7).")
                st.error("Overriding will mark this current week as 'Incomplete' in your history.")
                confirm_override = st.checkbox("I understand and want to override the current plan.")
                if st.button("Confirm Override"):
                    if confirm_override:
                        add_report(settings, "Incomplete Block", f"Previous block cancelled on Day {settings['current_day']}.")
                        settings["plan"] = st.session_state.pending_plan
                        settings["block_active"] = True
                        settings["current_day"] = 1
                        settings["start_date"] = st.session_state.pending_plan[0]["date"]
                        save_settings(settings)
                        st.success("✅ New Weekly Strategy Locked!")
                        # Reset wizard state
                        st.session_state.base_plan_saved = False
                        st.session_state.base_plan_data = None
                        st.session_state.exercise_data = {}
                        st.session_state.show_override = False
                        st.rerun()
                    else:
                        st.error("Please check the confirmation box to override.")

    # --- TAB 3: CHECKLIST ---
    with tab3:
        st.header("Daily Strategy")
        if not settings["block_active"]:
            st.info("Set your goals in the Goal Setter tab.")
        else:
            t = settings["plan"][settings["current_day"] - 1]
            st.subheader(f"Strategy for Today — {t.get('day_name', 'Day')}, {t.get('date', '')} (Day {settings['current_day']} of 7)")
            st.write(f"✅ Walk **{t['steps']}** steps.")
            st.write(f"✅ Drink **{t['water']}L** water.")
            st.write(f"✅ Complete **{t['workout']}** workout.")
            if t.get('exercises'):
                st.write("**Specific Exercises:**")
                for ex in t['exercises']: st.write(f"- {ex}")
            
            # ======= 7-DAY PLAN OVERVIEW (Excel Sheet) =======
            st.markdown("---")
            st.subheader("📅 Your Current 7-Day Plan")
            plan_df = pd.DataFrame([
                {
                    "Day": f"{d['day_name']}, {d['date']}",
                    "Steps": d["steps"],
                    "Water (L)": d["water"],
                    "Workout": d["workout"],
                    "Exercises": ", ".join(d.get("exercises", [])) if d.get("exercises") else "-",
                    "Status": "✅ Today" if idx == settings["current_day"] - 1 else ("✔️ Done" if idx < settings["current_day"] - 1 else "⏳ Upcoming")
                }
                for idx, d in enumerate(settings["plan"])
            ])
            st.dataframe(plan_df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader(f"Profession Advice ({settings['profession']})")
            if "Desk" in settings['profession'] or "Student" in settings['profession']:
                st.info("Focus on posture, hip mobility, and short movement breaks.")
            else:
                st.info("Prioritize hydration and recovery after high-activity work.")

    # --- TAB 4: DAILY LOG ---
    with tab4:
        st.header("End-of-Day Update")
        if wait > 0: st.error(f"Access Denied: Please wait {format_wait_time(wait)}.")
        else:
            with st.form("daily_update"):
                s_act = st.number_input("Actual Steps", value=None, placeholder="Enter steps...")
                c_act = st.number_input("Actual Calories", value=None, placeholder="Enter calories...")
                w_act = st.number_input("Actual Water (L)", value=None, placeholder="Enter liters...")
                wk_act = st.selectbox("Actual Workout Done", ["Hybrid", "Gym", "Rest", "Skipped"])
                sl_act = st.number_input("Actual Sleep Hours", value=None, placeholder="Enter hours...")

                # Specific Exercise Logging
                exercise_logs = []
                if settings["block_active"]:
                    today_plan = settings["plan"][settings["current_day"] - 1]
                    if today_plan.get('exercises'):
                        st.markdown("---")
                        st.subheader("Log Your Workout Performance")
                        for ex in today_plan['exercises']:
                            last_wt = get_last_exercise_weight(ex, settings["user_name"])
                            hint = f"Last time: {last_wt}kg" if last_wt else "First time logging"
                            st.caption(f"**{ex}** — {hint}")
                            col1, col2 = st.columns(2)
                            wt = col1.number_input(f"Weight (kg) - {ex}", value=None, key=f"wt_{ex}")
                            rp = col2.number_input(f"Reps - {ex}", value=None, key=f"rp_{ex}")
                            exercise_logs.append({"name": ex, "weight": wt, "reps": rp})
                
                verify = st.checkbox("I verify today's data is accurate.")
                if st.form_submit_button("Submit & Generate Report"):
                    if not verify: st.error("Please check the verification box.")
                    elif any(v is None for v in [s_act, c_act, w_act, sl_act]): st.error("Please fill in all main fields.")
                    else:
                        # Save Main CSV
                        file_exists = os.path.isfile(CSV_FILE)
                        new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), settings["user_name"], s_act, c_act, w_act, wk_act, sl_act]], 
                                             columns=["Date", "Name", "Steps", "Calories", "Water", "Workout", "Sleep"])
                        new_row.to_csv(CSV_FILE, mode="a", header=not file_exists, index=False)
                        
                        # Save Workout CSV (V6)
                        if exercise_logs:
                            wfile_exists = os.path.isfile(WORKOUT_CSV)
                            for log in exercise_logs:
                                if log["weight"] is not None:
                                    wrow = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), settings["user_name"], log["name"], log["weight"], log["reps"]]], 
                                                       columns=["Date", "User", "Exercise", "Actual_Weight", "Actual_Reps"])
                                    wrow.to_csv(WORKOUT_CSV, mode="a", header=not wfile_exists, index=False)
                                    wfile_exists = True
                        
                        settings["logs_completed"] += 1
                        settings["last_log_timestamp"] = datetime.now().isoformat()
                        
                        if settings["block_active"]:
                            target = settings["plan"][settings["current_day"] - 1]
                            deficit = target["steps"] - s_act
                            
                            # AI RE-BALANCER (V5 Logic)
                            if deficit > 0 and settings["current_day"] < 7:
                                if deficit > 3000: 
                                    found_rest = False
                                    for i in range(settings["current_day"], 7):
                                        if settings["plan"][i]["workout"] == "Rest":
                                            settings["plan"][i]["steps"] += deficit
                                            found_rest = True; break
                                    if not found_rest:
                                        adj = int(deficit / (7 - settings["current_day"]))
                                        for i in range(settings["current_day"], 7): settings["plan"][i]["steps"] += adj
                                else:
                                    adj = int(deficit / (7 - settings["current_day"]))
                                    for i in range(settings["current_day"], 7): settings["plan"][i]["steps"] += adj
                            
                            # Missed Workout Logic (V6)
                            if wk_act == "Skipped" and target["workout"] != "Rest":
                                shifted = False
                                for i in range(settings["current_day"], 7):
                                    if settings["plan"][i]["workout"] == "Rest":
                                        settings["plan"][i]["workout"] = target["workout"]
                                        settings["plan"][i]["exercises"] = target.get("exercises", [])
                                        shifted = True
                                        add_report(settings, "Workout Shifted", f"Missed {target['workout']} moved to {settings['plan'][i]['day_name']}.")
                                        break
                                if not shifted:
                                    add_report(settings, "Workout Missed", f"{target['workout']} could not be rescheduled (No rest days left).")
                            
                            add_report(settings, "Daily Log", f"Day {settings['current_day']} Report: {'✅ Success' if deficit <= 0 else '⚠️ Adjusted'}")
                            settings["current_day"] += 1
                            if settings["current_day"] > 7:
                                week_total = sum(d['steps'] for d in settings["plan"])
                                if week_total > sum(settings["best_week_steps"]):
                                    settings["best_week_steps"] = [d['steps'] for d in settings["plan"]]
                                settings["block_active"] = False
                        
                        save_settings(settings); st.success("Stats submitted!"); st.rerun()