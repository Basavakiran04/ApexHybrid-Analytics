# 🚀 Apex Hybrid Analytics: Performance Intelligence

Apex Hybrid Analytics is an end-to-end data project designed for athletes balancing **Strength Training** and **Hyrox Functional Endurance**.

## 🛠 Current Version: V2 (The Adaptive AI Coach)
This version introduces **Adaptive Goal Re-balancing**, transforming the project from a simple logger into an intelligent performance management system.

### Key Features:
- **Identity Memory (JSON):** Remembers user profiles and base targets across sessions.
- **AI Re-balancer:** Automatically calculates "Goal Deficits" (e.g., missed steps or water) and adjusts tomorrow's targets to maintain weekly averages.
- **Dual-Stream Data:** Uses **CSV** for long-term historical logs and **JSON** for real-time state management.
- **Smart Validation:** Sanitizes inputs (Name casing, Integer/Float checks) to ensure high-quality data for future modeling.

## 📂 Project Structure
- `tracker.py`: Main application logic & AI Re-balancer.
- `tracker_data.csv`: Historical performance database (Hidden).
- `user_settings.json`: User profile and adaptive goal state (Hidden).
- `.gitignore`: Ensures personal athlete data stays private.

## 📈 Roadmap
- **Version 3:** PowerBI-style Analytics Dashboard using Streamlit.
- **Version 4:** Machine Learning-powered "Hyrox Race Time" predictor.

---
### ⚖️ Legal Disclaimer
This project is for educational and portfolio purposes only. The data and advice provided are not a substitute for professional medical or fitness consultation. "HYROX" is a trademark of its respective owners. This is an unofficial community project.