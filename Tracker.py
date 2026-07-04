import csv
import os
import json
from datetime import datetime, timedelta

CSV_FILE = "tracker_data.csv"
JSON_FILE = "user_settings.json"

# --- 1. IDENTITY ---
def load_settings():
    if not os.path.isfile(JSON_FILE) or os.stat(JSON_FILE).st_size == 0:
        print("\n--- 🚀 Welcome to Apex Hybrid Analytics ---")
        name = input("Before we begin, what is your name? ").strip().capitalize()
        prof = input(f"Hello {name}, what is your profession? ").strip().capitalize()
        
        default_settings = {
            "user_name": name, "profession": prof,
            "logs_completed": 0, "last_log_timestamp": None,
            "obs_steps": [], "block_active": False, "current_day": 0,
            "plan": [], "last_report": "No reports generated yet."
        }
        save_settings(default_settings)
        return default_settings
    with open(JSON_FILE, "r") as f: return json.load(f)

def save_settings(settings):
    with open(JSON_FILE, "w") as f: json.dump(settings, f, indent=4)

# --- OPTION 1: GOAL SETTER (Set 1-3 Day Block) ---
def goal_setter(settings):
    print(f"\n--- 🎯 Strategy Session, {settings['user_name']} ---")
    try:
        days = int(input("How many days is this plan for (1-3)? "))
        new_plan = []
        for i in range(1, days + 1):
            print(f"\nSetup Goals for DAY {i}:")
            s = int(input(f"  Day {i} Step Goal: "))
            w = float(input(f"  Day {i} Water Goal (L): "))
            c = int(input(f"  Day {i} Calorie Goal: "))
            sl = float(input(f"  Day {i} Sleep Goal: "))
            wk = input(f"  Day {i} Workout (Hybrid/Gym/Rest): ").capitalize()
            new_plan.append({"steps": s, "water": w, "calories": c, "sleep": sl, "workout": wk})
        
        settings["plan"] = new_plan
        settings["block_active"] = True
        settings["current_day"] = 1
        save_settings(settings)
        print(f"\n✅ {days}-Day Strategy Locked!")
    except ValueError: print("❌ Invalid input.")

# --- OPTION 2: CHECKLIST (View Targets Anytime) ---
def view_checklist(settings):
    print(f"\n--- 📋 Today's Checklist for {settings['user_name']} ---")
    if not settings["block_active"]:
        print("Status: No active strategy. Go to Option 1.")
        return
    day_idx = settings["current_day"] - 1
    t = settings["plan"][day_idx]
    print(f"Plan: Day {settings['current_day']} of {len(settings['plan'])}")
    print(f"🎯 Target: {t['steps']} Steps | {t['water']}L Water | {t['workout']}")

# --- OPTION 3: DAILY UPDATE (18-Hour Write Lock) ---
def daily_update(settings):
    if settings["last_log_timestamp"]:
        last_log = datetime.fromisoformat(settings["last_log_timestamp"])
        if datetime.now() - last_log < timedelta(hours=18):
            wait = 18 - (datetime.now() - last_log).total_seconds() / 3600
            print(f"\n⏳ Update Locked: Please wait {round(wait, 1)} hours to log again.")
            return

    print(f"\n--- ✅ Log Daily Stats: {datetime.now().strftime('%Y-%m-%d')} ---")
    try:
        # ORDER: Steps -> Calories -> Water -> Workout -> Sleep
        s = int(input("👉 Steps today: "))
        c = int(input("👉 Calories: "))
        w = float(input("👉 Water (L): "))
        while True:
            wk = input("👉 Workout Done (Hybrid/Gym/Rest): ").capitalize()
            if wk in ["Hybrid", "Gym", "Rest"]: break
        sl = float(input("👉 Sleep: "))
    except ValueError: return

    # Save to CSV
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists: writer.writerow(["Date", "Steps", "Calories", "Water", "Workout", "Sleep"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d"), s, c, w, wk, sl])

    settings["last_log_timestamp"] = datetime.now().isoformat()
    settings["logs_completed"] += 1
    settings["obs_steps"].append(s)

    # AI RE-BALANCING & SUCCESS TICKING
    if settings["block_active"]:
        day_idx = settings["current_day"] - 1
        target = settings["plan"][day_idx]
        s_tick = "✅" if s >= target["steps"] else "❌"
        w_tick = "✅" if w >= target["water"] else "❌"
        
        # Save Report to Memory
        report = f"Day {settings['current_day']} Report: Steps {s}/{target['steps']} {s_tick} | Water {w}L/{target['water']}L {w_tick}"
        settings["last_report"] = report
        print(f"\n📊 {report}")

        # AI Deficit Split
        if s < target["steps"] and settings["current_day"] < len(settings["plan"]):
            deficit = target["steps"] - s
            remaining = len(settings["plan"]) - settings["current_day"]
            adj = deficit / remaining
            for i in range(settings["current_day"], len(settings["plan"])):
                settings["plan"][i]["steps"] += int(adj)
            print(f"🤖 AI Coach: Adjusted tomorrow's goal by +{int(adj)} to keep your average.")

        settings["current_day"] += 1
        if settings["current_day"] > len(settings["plan"]):
            settings["block_active"] = False
            print("🏁 Strategy Block Complete!")

    save_settings(settings)

# --- OPTION 4: PROGRESS REPORT (Always Open) ---
def view_report(settings):
    print(f"\n--- 📈 Performance Report: {settings['user_name']} ---")
    print(f"Profession: {settings['profession']}")
    print(f"Discovery Logs: {settings['logs_completed']}/3")
    print(f"Latest Summary: {settings['last_report']}")
    
    if os.path.isfile(CSV_FILE):
        print("\nLast 3 Days of Raw History:")
        with open(CSV_FILE, 'r') as f:
            lines = f.readlines()
            for line in lines[-3:]:
                print(line.strip())
    
    print(f"\n💡 Tip: Focus on your 3-day consistency to stay 'Apex'.")

# --- MAIN MENU ---
def main():
    settings = load_settings()
    while True:
        print(f"\n--- 🚀 Apex Hybrid Analytics | Athlete: {settings['user_name']} ---")
        print("1. Goal Setter (Strategy)")
        print("2. Daily Checklist (Targets)")
        print("3. Log Daily Stats (Locked 18h)")
        print("4. Performance Report (Always Open)")
        print("5. Exit")
        
        choice = input("\nSelect: ")
        if choice == '1': goal_setter(settings); settings = load_settings()
        elif choice == '2': view_checklist(settings)
        elif choice == '3': daily_update(settings); settings = load_settings()
        elif choice == '4': view_report(settings)
        elif choice == '5': break

if __name__ == "__main__": main()