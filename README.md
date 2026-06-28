# 🚀 ApexHybrid-Analytics: Performance Analytics

ApexHybrid-Analytics is an end-to-end data project designed for athletes who balance **Strength Training (Gym)** and **Functional Endurance (Hyrox)**. 

This project tracks daily health metrics and performance data to provide personalized recovery advice and progress analytics.

## 🛠 Current Version: V1 (The Daily Logger)
In the first version, I have implemented a professional command-line interface to capture clean, validated data.

### Key Features:
- **Sequential Data Entry:** User-friendly flow (Name -> Steps -> Calories -> Water -> Workout Type -> Sleep).
- **Data Validation:** Ensures all inputs are correctly formatted (Integers/Floats) to prevent "dirty data" for future ML models.
- **Smart Feedback:** Real-time health tips based on water intake and sleep quality.
- **CSV Storage:** Data is indexed by date to ensure seamless scaling for future versions.

## 📂 Project Structure
- `tracker.py`: The main application logic.
- `tracker_data.csv`: Local database storing historical athlete data.
- `.gitignore`: Configured to keep personal athlete data private.

## 📈 Roadmap
- **Version 2:** Interactive Weekly Timetables (Planned vs. Actual).
- **Version 3:** PowerBI-style Analytics Dashboard using Streamlit.
- **Version 4:** ML-powered "AI Coach" for personalized workout advice.

---
*Built with Python 🐍*