# 🚀 Apex Hybrid Analytics: Performance Intelligence

Apex Hybrid Analytics is an end-to-end data science project designed for athletes balancing **Strength Training** and **Hyrox Functional Endurance**. 

## 🛠 Current Version: V3 (The Performance Management System)
This version transforms the application into a professional "Command Center," separating data entry, strategy planning, and performance reporting.

### 🌟 Key Features:
- **3-Day Strategy Blocks:** Users define their own multi-day training strategy (1-3 days) with specific goals for each day.
- **AI Performance Management:** If a target is missed, the AI automatically calculates the deficit and redistributes it across the remaining days of the block to protect the weekly average.
- **Intelligent Time-Locking:** Implements an 18-hour "Write-Lock" on data entry to ensure time-series integrity, while keeping "Read" access open 24/7.
- **Context-Aware Personalization:** Tracks user professions (e.g., Engineer, Sales) to provide occupation-specific recovery and mobility tips.
- **Ticking Report System:** Provides instant `✅/❌` visual feedback comparing planned vs. actual performance across Steps, Calories, Water, Workout, and Sleep.

### 📂 Data Architecture
- `tracker.py`: Main engine featuring the AI re-balancing logic and multi-state menu.
- `tracker_data.csv`: Historical database (Time-Series logs).
- `user_settings.json`: System "Brain" (Identity, Strategy State, and AI Adjustments).

## 📊 V3 Menu Structure
1. **Goal Setter:** Set your 1-3 day performance strategy.
2. **Daily Checklist:** View your targets and professional tips anytime.
3. **Log Daily Stats:** Sequential data entry (18h lock for data quality).
4. **Performance Report:** View historical success ticks and AI insights.

---
### ⚖️ Legal Disclaimer
Educational purpose only. Not medical advice. "HYROX" is a trademark of its respective owners. This is an unofficial community project.