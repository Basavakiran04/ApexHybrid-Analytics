# 🏋️ Apex Hybrid Analytics – V6: The Coaching Engine

A **personalized fitness intelligence platform** for Hybrid (Hyrox-style) and Gym athletes. Built with Python + Streamlit, this app combines adaptive AI logic with a professional dashboard to help athletes plan, track, and optimize their weekly performance.

---

## 🚀 What's New in V6

Version 6 transforms Apex Hybrid Analytics from a **tracker** into a **coaching engine**. This version introduces:

### 🎯 2-Step Goal Setter Wizard
- **Section 1: Base Plan** – Set 7-day targets in an Excel-style table (Steps, Water, Workout Type).
- **Section 2: Exercise Details** – Add specific exercises for Gym/Hybrid days via smart dropdowns with custom typing support.
- **Smart Validations** – Blocks all-Rest or no-Rest plans to ensure balanced weeks.
- **Edit Flow** – Grayed-out summary + "Edit Base Plan" button that auto-clears outdated exercise details.

### 📅 Custom Start Date
- Users can pick **any start date** for their 7-day plan — no more assuming "today = Day 1."

### 🏋️ Progressive Overload Tracking
- Separate `workout_data.csv` stores detailed exercise logs.
- Dashboard displays the **last logged exercise** with progression suggestions.

### 💧 AI Water Suggestion Formula
- Base: 3.5L
- +0.5L on Gym/Hybrid days
- +0.5L if previous sleep was <6 hours

### 📊 7-Day Plan Overview in Checklist
- Full weekly plan displayed as a clean table with status indicators:
  - ✅ Today
  - ✔️ Done
  - ⏳ Upcoming

### 🔀 Missed Workout Auto-Shift
- If a user skips a Gym/Hybrid workout, the AI moves it to the next available Rest day.
- If no Rest day is available, it's logged as "Missed" in the report history.

### 🎨 Enhanced UX
- **Custom exercise input** (comma-separated) alongside preset dropdowns.
- **Grayed-out state** for saved base plans (prevents accidental edits).
- **Override warning** appears only when locking a new strategy (not upfront).

---

## 📁 Project Structure