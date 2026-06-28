import csv
import os
from datetime import date

# --- FIX BUG #3: Integer vs Float ---
# We now have two helpers: one for whole numbers (Steps/Calories) 
# and one for decimals (Water/Sleep).
def get_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("❌ Please enter a whole number.")

def get_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("❌ Please enter a valid decimal number.")

def run_tracker():
    print("--- 🚀 Welcome to your Performance Tracker ---")
    
    # --- FIX BUG #1: Identity Crisis ---
    # .strip() removes accidental spaces, .capitalize() ensures "John"
    name = input("Before we begin, what is your name? ").strip().capitalize()
    
    print(f"\nGreat to see you, {name}! Let's log your stats for {date.today()}.")

    # Use get_int for whole numbers
    steps = get_int("👉 Enter your daily steps: ")
    calories = get_int("👉 Enter calories eaten: ")

    # Use get_float for decimals
    water = get_float("👉 Enter water intake (Liters): ")
    if water < 1.5:
        print("💡 Tip: Try to drink a bit more water to stay hydrated!")

    # --- FIX BUG #4: Rest Day Logic ---
    # Added "Rest" to the allowed options
    while True:
        workout = input("👉 Workout type (Hybrid/Gym/Rest): ").capitalize()
        if workout in ["Hybrid", "Gym", "Rest"]:
            break
        print("❌ Please choose either 'Hybrid', 'Gym', or 'Rest'.")

    sleep = get_float("👉 Enter sleep hours: ")
    if sleep < 6:
        print("💡 Note: Recovery might be lower today due to short sleep.")

    # --- STORAGE ---
    file_name = "tracker_data.csv"
    file_exists = os.path.isfile(file_name)

    with open(file_name, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Date", "Name", "Steps", "Calories", "Water", "Workout", "Sleep"])
        
        writer.writerow([date.today(), name, steps, calories, water, workout, sleep])

    # --- FEEDBACK ---
    print(f"\n--- 📊 Daily Recap for {name} ---")
    print(f"✅ Steps: {steps}")
    print(f"✅ Calories: {calories} kcal")
    print(f"✅ Water: {water}L")
    print(f"✅ Workout: {workout}")
    print(f"✅ Sleep: {sleep} hours")
    print("\nData locked in! See you tomorrow! 🔥")

if __name__ == "__main__":
    run_tracker()