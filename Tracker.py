import csv
import os
import json
from datetime import date

CSV_FILE = "tracker_data.csv"
JSON_FILE = "user_settings.json"

# --- PART 1: IDENTITY & GOAL MANAGER ---
def load_settings():
    """Load settings. If new user, ask for Name and set Base Goals."""
    if not os.path.isfile(JSON_FILE):
        print("--- 🚀 Welcome to ApexHybrid-Analytics Performance Analytics ---")
        name = input("Before we begin, what is your name? ").strip().capitalize()
        
        default_settings = {
            "user_name": name,
            "base_goals": {
                "steps": 10000,
                "water": 3.0
            },
            "tomorrow_adjusted": {
                "steps": 10000,
                "water": 3.0
            }
        }
        with open(JSON_FILE, "w") as f:
            json.dump(default_settings, f, indent=4)
        return default_settings
    
    with open(JSON_FILE, "r") as f:
        return json.load(f)

def save_settings(settings):
    with open(JSON_FILE, "w") as f:
        json.dump(settings, f, indent=4)

# --- PART 2: DATA VALIDATION (From V1) ---
def get_int(prompt):
    while True:
        try: return int(input(prompt))
        except ValueError: print("❌ Please enter a whole number.")

def get_float(prompt):
    while True:
        try: return float(input(prompt))
        except ValueError: print("❌ Please enter a decimal number.")

# --- PART 3: THE AI RE-BALANCER ---
def ai_rebalance(actual_steps, actual_water, settings):
    # Calculate Deficits
    step_diff = settings["tomorrow_adjusted"]["steps"] - actual_steps
    water_diff = settings["tomorrow_adjusted"]["water"] - actual_water
    
    # Update tomorrow's goals automatically
    settings["tomorrow_adjusted"]["steps"] = max(5000, settings["base_goals"]["steps"] + step_diff)
    settings["tomorrow_adjusted"]["water"] = max(1.5, settings["base_goals"]["water"] + water_diff)
    
    save_settings(settings)
    
    print(f"\n🤖 AI Coach Analysis for tomorrow:")
    if step_diff > 0 or water_diff > 0:
        print(f"⚠️ Tomorrow's Goal adjusted: {settings['tomorrow_adjusted']['steps']} steps and {settings['tomorrow_adjusted']['water']}L water.")
    else:
        print("🌟 Goals met! Tomorrow is reset to your baseline targets.")

# --- MAIN ENGINE ---
def run_tracker():
    settings = load_settings()
    user = settings["user_name"]
    
    print(f"\n--- 📈 Welcome back, {user}! ---")
    print(f"Log for {date.today()} | 🎯 Target: {settings['tomorrow_adjusted']['steps']} Steps")

    # Sequential Inputs (Matches V1 Order)
    steps = get_int("👉 Steps: ")
    calories = get_int("👉 Calories: ")
    water = get_float("👉 Water (L): ")
    
    while True:
        workout = input("👉 Workout (Hybrid/Gym/Rest): ").capitalize()
        if workout in ["Hybrid", "Gym", "Rest"]: break
        print("❌ Invalid type.")

    sleep = get_float("👉 Sleep: ")

    # --- SAVE TO CSV (Name column restored!) ---
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Date", "Name", "Steps", "Calories", "Water", "Workout", "Sleep"])
        writer.writerow([date.today(), user, steps, calories, water, workout, sleep])

    # --- AI ADVICE ---
    ai_rebalance(steps, water, settings)
    
    print(f"\n✅ Stats locked in, {user}! See you tomorrow. 💪")

if __name__ == "__main__":
    run_tracker()