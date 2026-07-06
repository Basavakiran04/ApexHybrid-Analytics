# 🚀 Apex Hybrid Analytics: Performance Intelligence Dashboard

Apex Hybrid Analytics is a professional end-to-end performance management platform designed for athletes balancing **Strength Training** and **Hyrox Functional Endurance**. 

Moving beyond simple tracking, this system utilizes **Adaptive AI Logic** to manage training blocks, ensure data integrity, and protect performance averages.

## 🛠 Current Version: V4 (The Master Web Edition)
Version 4 transitions the project into a high-end **Streamlit Web Application**, featuring a professional UI and "Hardened" data logic.

### 🌟 Key Engineering & AI Features:
- **Adaptive AI Re-balancing:** If an athlete misses a target (e.g., Steps), the AI automatically calculates the deficit and redistributes it across the remaining days of the active 3-day block to maintain the weekly average.
- **Data Integrity Write-Lock:** Implements a strict **18-hour interval lock** on data entry to maintain time-series quality.
- **Human-Centric UX:** Features a professional, centered brand UI with human-readable countdown timers (e.g., "42m left" vs "0.7h").
- **Safety Gate Verification:** All data entry forms (Onboarding, Goal Setting, Daily Logging) include manual verification checkboxes to prevent accidental "Enter-key" submissions.
- **State-Aware Memory:** Utilizes a dual-layer data architecture: **CSV** for long-term historical performance and **JSON** for real-time state management.

### 📂 Technical Stack
- **Frontend:** Streamlit (High-Performance Data Dashboard)
- **Visualization:** Plotly (Interactive Time-Series Trends)
- **Data Handling:** Pandas (Schema validation and metric calculation)
- **Storage:** JSON (System State) & CSV (Performance Ledger)

## 📊 Core Workflow
1. **Strategy Session:** Define a 3-day performance block (Steps, Water, Workouts).
2. **Execution:** Daily Checklist provides context-aware tips based on user profession.
3. **Validation:** End-of-day logging with strict sequential input and safety confirmation.
4. **Analysis:** Professional dashboard showing 7-day averages, success ticks, and AI insights.

## 📈 Project Evolution
- **V1 - V2:** Terminal-based data collection and basic goal logic.
- **V3:** Implementation of 3-Day Blocks and AI deficit management.
- **V4:** Migration to Web UI, Human-readable time, and Input Safety Hardening.
- **V5 (Upcoming):** 7-Day Weekly Blocks and standardized strategy templates.

---
### ⚖️ Legal Disclaimer
This project is for educational and portfolio purposes only. It is not a substitute for professional medical or fitness advice. "HYROX" is a trademark of its respective owners. This is an unofficial community project.