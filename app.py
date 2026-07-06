import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px

# --- 1. SETTINGS & STYLING ---
CSV_FILE = "tracker_data.csv"
JSON_FILE = "user_settings.json"

st.set_page_config(page_title="Apex Hybrid Analytics", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .app-title {
        text-align: center;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-top: -10px;
        margin-bottom: 8px;
        color: #F5F5F5;
    }

    .app-subtitle {
        text-align: center;
        font-size: 13px;
        color: #A0A0A0;
        margin-bottom: 25px;
    }

    .title-divider {
        border-bottom: 1px solid #2f3338;
        margin-bottom: 30px;
    }

    .profession-box {
        background-color: #1e3a8a;
        color: #60a5fa;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-weight: bold;
    }

    .timer-box {
        background-color: #424211;
        color: #d4d444;
        padding: 10px;
        border-radius: 8px;
        font-weight: bold;
    }

    .status-line {
        font-size: 24px;
        font-weight: bold;
        margin-top: 25px;
        margin-bottom: 35px;
    }

    .report-box {
        background-color: #111827;
        border: 1px solid #374151;
        padding: 14px;
        border-radius: 8px;
        margin-top: 12px;
        color: #E5E7EB;
    }
    </style>
""", unsafe_allow_html=True)


# --- 2. DATA HELPERS ---
def load_settings():
    if not os.path.isfile(JSON_FILE) or os.stat(JSON_FILE).st_size == 0:
        return None

    try:
        with open(JSON_FILE, "r") as f:
            settings = json.load(f)
    except json.JSONDecodeError:
        return None

    # Backward compatibility for older JSON files
    settings.setdefault("logs_completed", 0)
    settings.setdefault("last_log_timestamp", None)
    settings.setdefault("obs_steps", [])
    settings.setdefault("block_active", False)
    settings.setdefault("current_day", 0)
    settings.setdefault("plan", [])
    settings.setdefault("last_report", "No reports generated yet.")
    settings.setdefault("reports", [])

    return settings


def save_settings(settings):
    with open(JSON_FILE, "w") as f:
        json.dump(settings, f, indent=4)


def format_wait_time(hours_decimal):
    """
    Converts decimal hours like 0.7 into professional time:
    0.7 -> 42m left
    1.2 -> 1h 12m left
    """
    if hours_decimal <= 0:
        return "Ready"

    total_minutes = int(round(hours_decimal * 60))
    hours = total_minutes // 60
    minutes = total_minutes % 60

    if hours == 0:
        return f"{minutes}m left"
    elif minutes == 0:
        return f"{hours}h left"
    else:
        return f"{hours}h {minutes}m left"


def get_wait_time(settings):
    if not settings.get("last_log_timestamp"):
        return 0

    last_log = datetime.fromisoformat(settings["last_log_timestamp"])
    time_diff = datetime.now() - last_log

    if time_diff < timedelta(hours=18):
        return round(18 - (time_diff.total_seconds() / 3600), 2)

    return 0


def add_report(settings, report_type, summary, details=None):
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "type": report_type,
        "summary": summary,
        "details": details or {}
    }

    settings.setdefault("reports", [])
    settings["reports"].append(report)
    settings["last_report"] = summary


# --- 3. ONBOARDING ---
settings = load_settings()

if settings is None:
    st.markdown('<div class="app-title">APEX HYBRID ANALYTICS</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Precision training intelligence for hybrid athletes</div>', unsafe_allow_html=True)
    st.markdown('<div class="title-divider"></div>', unsafe_allow_html=True)

    st.title("Welcome")
    st.write("Create your athlete profile to begin.")

    with st.form("onboarding"):
        name = st.text_input("What is your name?").strip().capitalize()
        prof = st.text_input("What is your profession?").strip().capitalize()

        confirm_profile = st.checkbox("I am ready to create my profile.")

        if st.form_submit_button("Initialize Profile") and name and prof and confirm_profile:
            new_settings = {
                "user_name": name,
                "profession": prof,
                "logs_completed": 0,
                "last_log_timestamp": None,
                "obs_steps": [],
                "block_active": False,
                "current_day": 0,
                "plan": [],
                "last_report": "Profile initialized. Set your first 3-day strategy.",
                "reports": []
            }

            add_report(
                new_settings,
                "Profile Created",
                "Profile initialized. Set your first 3-day strategy."
            )

            save_settings(new_settings)
            st.rerun()

else:
    # --- MAIN TITLE ---
    st.markdown('<div class="app-title">APEX HYBRID ANALYTICS</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Hybrid performance tracking and adaptive strategy management</div>', unsafe_allow_html=True)
    st.markdown('<div class="title-divider"></div>', unsafe_allow_html=True)

    # --- SIDEBAR ---
    st.sidebar.title(f"💪 {settings['user_name']}")
    st.sidebar.markdown(
        f'<div class="profession-box">Profession: {settings["profession"]}</div>',
        unsafe_allow_html=True
    )

    wait = get_wait_time(settings)

    if wait > 0:
        readable_wait = format_wait_time(wait)
        st.sidebar.markdown(
            f'<div class="timer-box">🕒 Next Log in: {readable_wait}</div>',
            unsafe_allow_html=True
        )
    else:
        st.sidebar.success("Ready for Daily Update")

    # --- TABS ---
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Dashboard", "🎯 Goal Setter", "📋 Checklist", "📝 Daily Log"]
    )

    # --- TAB 1: DASHBOARD ---
    with tab1:
        st.header(f"Athlete Performance: {settings['user_name']}")

        kpi1, kpi2, kpi3 = st.columns(3)

        if os.path.isfile(CSV_FILE):
            df = pd.read_csv(CSV_FILE)

            if not df.empty:
                avg_s = int(df["Steps"].tail(7).mean())
                last_wk = df["Workout"].iloc[-1]

                kpi1.metric("7-Day Avg Steps", avg_s)
                kpi2.metric("Total Logs", settings["logs_completed"])
                kpi3.metric("Last Workout", last_wk)
            else:
                kpi1.metric("7-Day Avg Steps", 0)
                kpi2.metric("Total Logs", settings["logs_completed"])
                kpi3.metric("Last Workout", "-")
        else:
            kpi1.metric("7-Day Avg Steps", 0)
            kpi2.metric("Total Logs", settings["logs_completed"])
            kpi3.metric("Last Workout", "-")

        # Status line
        if settings["block_active"] and settings["plan"]:
            target = settings["plan"][settings["current_day"] - 1]
            st.markdown(
                f'<div class="status-line">📍 Day {settings["current_day"]} of 3 | Target: {target["steps"]} Steps</div>',
                unsafe_allow_html=True
            )
        elif settings["logs_completed"] < 3:
            st.info(
                f"Discovery Phase: Day {settings['logs_completed']}/3. "
                "The system is learning your baseline."
            )
        else:
            st.warning("No active strategy. Use the Goal Setter to start a new 3-day block.")

        # Step chart
        if os.path.isfile(CSV_FILE):
            df = pd.read_csv(CSV_FILE)

            if not df.empty:
                st.subheader("Step Consistency Trend")
                fig = px.line(df, x="Date", y="Steps", markers=True)
                fig.update_traces(line_color="#00FFCC")
                fig.update_layout(
                    plot_bgcolor="#0E1117",
                    paper_bgcolor="#0E1117",
                    font_color="#FFFFFF",
                    xaxis_title="Date",
                    yaxis_title="Steps"
                )
                st.plotly_chart(fig, use_container_width=True)

        # Latest report
        st.markdown("### Latest Report")
        st.markdown(
            f'<div class="report-box">{settings.get("last_report", "No reports generated yet.")}</div>',
            unsafe_allow_html=True
        )

        # Report history
        if settings.get("reports"):
            with st.expander("View Report History"):
                for report in reversed(settings["reports"][-5:]):
                    st.write(f"**{report['timestamp']}** — {report['type']}")
                    st.write(report["summary"])
                    st.write("---")

    # --- TAB 2: GOAL SETTER ---
    with tab2:
        st.header("Strategy Session")

        can_set = True
        override_confirmed = False
        previous_block_was_active = settings["block_active"]

        if settings["block_active"]:
            st.warning("You have a 3-Day Block currently in progress.")

            current_day = settings["current_day"]
            total_days = len(settings["plan"])

            st.write(f"Current progress: Day {current_day} of {total_days}")

            with st.expander("View Current Active Plan"):
                for idx, day in enumerate(settings["plan"], start=1):
                    st.write(
                        f"Day {idx}: {day['steps']} steps | "
                        f"{day['water']}L water | {day['workout']}"
                    )

            override = st.checkbox(
                "I want to cancel my current goals and start a new strategy."
            )

            if not override:
                st.info("Finish your current 3-day cycle to maintain your average.")
                can_set = False
            else:
                st.error(
                    "Warning: This will mark your current block as incomplete "
                    "and store it in your report history."
                )
                override_confirmed = True

        if can_set:
            with st.form("goal_setter"):
                cols = st.columns(3)
                new_plan = []

                for i in range(1, 4):
                    cols[i - 1].subheader(f"Day {i}")

                    s = cols[i - 1].number_input(
                        f"Steps (Day {i})",
                        value=10000,
                        step=500,
                        key=f"s{i}"
                    )

                    w = cols[i - 1].number_input(
                        f"Water L (Day {i})",
                        value=3.0,
                        step=0.5,
                        key=f"w{i}"
                    )

                    wk = cols[i - 1].selectbox(
                        f"Workout (Day {i})",
                        ["Hybrid", "Gym", "Rest"],
                        key=f"wk{i}"
                    )

                    new_plan.append({
                        "steps": s,
                        "water": w,
                        "workout": wk
                    })

                confirm_strategy = st.checkbox("I verify these targets for the next 3 days.")
                if st.form_submit_button("Lock 3-Day Strategy") and confirm_strategy:

                    if previous_block_was_active and override_confirmed:
                        incomplete_details = {
                            "cancelled_on_day": settings["current_day"],
                            "remaining_plan": settings["plan"][settings["current_day"] - 1:]
                        }

                        add_report(
                            settings,
                            "Incomplete Block",
                            f"Previous block cancelled on Day {settings['current_day']} of 3.",
                            incomplete_details
                        )

                    settings["plan"] = new_plan
                    settings["block_active"] = True
                    settings["current_day"] = 1

                    if previous_block_was_active and override_confirmed:
                        add_report(
                            settings,
                            "New Strategy Started",
                            "New 3-day strategy started after cancelling previous block."
                        )
                    else:
                        add_report(
                            settings,
                            "New Strategy Started",
                            "Fresh 3-day strategy started."
                        )

                    save_settings(settings)
                    st.success("Strategy Locked. Check your Checklist.")
                    st.rerun()

    # --- TAB 3: CHECKLIST ---
    with tab3:
        st.header("Daily Strategy")

        if not settings["block_active"]:
            st.info("Set your goals in the Goal Setter to see your checklist.")
        else:
            t = settings["plan"][settings["current_day"] - 1]

            st.subheader(f"Strategy for Today — Day {settings['current_day']}")
            st.write(f"Walk **{t['steps']}** steps.")
            st.write(f"Drink **{t['water']}L** of water.")
            st.write(f"Complete your **{t['workout']}** session.")

            st.markdown("---")
            st.subheader(f"Profession Advice ({settings['profession']})")

            if "Desk" in settings["profession"] or "Student" in settings["profession"]:
                st.info("Focus on posture, hip mobility, and short movement breaks during the day.")
            else:
                st.info("Prioritize hydration, recovery, and sleep quality after high-activity work.")

    # --- TAB 4: DAILY LOG ---
    with tab4:
        st.header("End-of-Day Update")

        if wait > 0:
            st.error(
                f"Access Denied: Please wait {format_wait_time(wait)} before updating your stats."
            )
        else:
            with st.form("daily_update"):
                # STRICT SEQUENCE: Steps -> Calories -> Water -> Workout -> Sleep
                s_act = st.number_input("Actual Steps", value=None, placeholder="Enter steps...")
                c_act = st.number_input("Actual Calories", value=None, placeholder="Enter calories...")
                w_act = st.number_input("Actual Water (L)", value=None, placeholder="Enter liters...")
                wk_act = st.selectbox("Actual Workout Done", ["Hybrid", "Gym", "Rest"])
                sl_act = st.number_input("Actual Sleep Hours", value=None, placeholder="Enter hours...")

                verify_data = st.checkbox("I verify today's data is accurate.")

                if st.form_submit_button("Submit & Generate Report"):
                    if not verify_data:
                        st.error("Please check the verification box before submitting.")
                    elif any(v is None for v in [s_act, c_act, w_act, sl_act]):
                        st.error("Please fill in all data points.")
                    else:
                    # 1. SAVE TO CSV
                        file_exists = os.path.isfile(CSV_FILE)

                        new_row = pd.DataFrame(
                            [[
                                datetime.now().strftime("%Y-%m-%d"),
                                settings["user_name"],
                                s_act,
                                c_act,
                                w_act,
                                wk_act,
                                sl_act
                            ]],
                            columns=[
                                "Date",
                                "Name",
                                "Steps",
                                "Calories",
                                "Water",
                                "Workout",
                                "Sleep"
                            ]
                        )

                        new_row.to_csv(
                            CSV_FILE,
                            mode="a",
                            header=not file_exists,
                            index=False
                        )

                        # 2. OBSERVATION HISTORY
                        settings["logs_completed"] += 1
                        settings["obs_steps"].append(int(s_act))
                        settings["last_log_timestamp"] = datetime.now().isoformat()

                        # 3. REPORT & AI RE-BALANCE
                        if settings["block_active"]:
                            target = settings["plan"][settings["current_day"] - 1]

                            s_tick = "Achieved" if s_act >= target["steps"] else "Missed"
                            w_tick = "Achieved" if w_act >= target["water"] else "Missed"
                            wk_tick = "Achieved" if wk_act == target["workout"] else "Missed"

                            report_summary = (
                                f"Day {settings['current_day']} Report — "
                                f"Steps: {s_act}/{target['steps']} ({s_tick}), "
                                f"Water: {w_act}L/{target['water']}L ({w_tick}), "
                                f"Workout: {wk_act}/{target['workout']} ({wk_tick})."
                            )

                            add_report(
                                settings,
                                "Daily Performance Report",
                                report_summary
                            )

                            # Deficit Re-balancing
                            if s_act < target["steps"] and settings["current_day"] < len(settings["plan"]):
                                deficit = target["steps"] - s_act
                                remaining_days = len(settings["plan"]) - settings["current_day"]
                                adjustment = int(deficit / remaining_days)

                                for i in range(settings["current_day"], len(settings["plan"])):
                                    settings["plan"][i]["steps"] += adjustment

                                add_report(
                                    settings,
                                    "AI Rebalance",
                                    f"Step deficit of {deficit} redistributed. "
                                    f"Remaining days increased by {adjustment} steps each."
                                )

                            settings["current_day"] += 1

                            if settings["current_day"] > len(settings["plan"]):
                                settings["block_active"] = False

                                add_report(
                                    settings,
                                    "Block Complete",
                                    "3-day strategy block completed."
                                )

                        else:
                            add_report(
                                settings,
                                "Daily Log",
                                "Daily stats logged without an active strategy block."
                            )

                        save_settings(settings)
                        st.success("Stats submitted. Report generated.")
                        st.rerun()