#!/usr/bin/env python3

# 1) Global in-memory store (SINGLE variable)
MEAL_ENTRIES = []  # list of dicts

from datetime import datetime

def _input_nonempty(prompt: str) -> str:
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Value cannot be empty. Please try again.")

def _input_date_iso(prompt: str) -> str:
    """Read date as YYYY-MM-DD."""
    while True:
        val = input(prompt).strip()
        try:
            datetime.strptime(val, "%Y-%m-%d")
            return val
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD (e.g., 2026-02-03).")

def _input_float(prompt: str) -> float:
    while True:
        val = input(prompt).strip()
        try:
            return float(val)
        except ValueError:
            print("Please enter a valid number (e.g., 450 or 450.0).")

def _input_choice(prompt: str, choices) -> str:
    choices_lower = [c.lower() for c in choices]
    while True:
        val = input(f"{prompt} {choices}: ").strip().lower()
        if val in choices_lower:
            return val
        print(f"Please choose one of {choices}.")

import uuid
from datetime import datetime, timezone
import json
import os

DATA_FILE = "data.json"

def load_data():
    """Load MEAL_ENTRIES from data.json if it exists; otherwise start empty."""
    global MEAL_ENTRIES
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Basic sanity check: ensure it's a list of dicts
            if isinstance(data, list):
                MEAL_ENTRIES = data
            else:
                print("Data file is not a list. Starting with empty data.")
                MEAL_ENTRIES = []
        except (json.JSONDecodeError, OSError) as e:
            print(f"Could not read data.json ({e}). Starting with empty data.")
            MEAL_ENTRIES = []
    else:
        MEAL_ENTRIES = []

def save_data():
    """Write MEAL_ENTRIES to data.json (pretty JSON)."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(MEAL_ENTRIES, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"Error saving data: {e}")
def add_item():
    """Create a structured MealPlanEntry dict and append to MEAL_ENTRIES."""
    print("\nAdd Meal Entry")
    print("----------------")

    date = _input_date_iso("Date (YYYY-MM-DD): ")
    meal_type = _input_choice("Meal type", ["breakfast", "lunch", "dinner", "snack"])
    meal_name = _input_nonempty("Meal name (e.g., 'Grilled Chicken Salad', 'yoghurt', 'garden salad', 'fruit salad'): ")
    serving_size = _input_nonempty("Serving size (e.g., '1 bowl', '200 g', '1 plate'): ")
    calories = _input_float("Estimated calories (kcal): ")

    flags_raw = input("Dietary flags (optional, comma-separated; e.g., vegan, halal, kosher, vegetarian): ").strip()
    dietary_flags = sorted({f.strip().lower() for f in flags_raw.split(',') if f.strip()}) if flags_raw else []

    notes = input("Notes (optional): ").strip()

    # timestamp for record keeping
    now_iso = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')

    # THIS is the new structured dictionary
    entry = {
        "entryId": str(uuid.uuid4()),
        "userId": "demo-user",
        "date": date,
        "mealType": meal_type,
        "mealName": meal_name,
        "servingSize": serving_size,
        "ingredients": [],
        "calories": calories,
        "targets": {},
        "substitutions": [],
        "dietaryFlags": dietary_flags,
        "isFavorite": False,
        "notes": notes,
        "createdAt": now_iso,
        "updatedAt": now_iso,
    }

    # Add the dictionary to the master list
    MEAL_ENTRIES.append(entry)

    save_data()
    
    print("\n✅ Meal added successfully! Entry ID:", entry["entryId"])


def list_items():
    """Iterate through the list of dictionaries and print a readable summary."""
    print("\nYour Meal Entries")
    print("-----------------")
    if not MEAL_ENTRIES:
        print("(No entries yet.)")
        return

    for i, e in enumerate(MEAL_ENTRIES, start=1):
        print(f"{i}. {e['date']} | {e['mealType'].title()} | {e['mealName']} | {e['servingSize']} | {e['calories']} kcal")

        if e.get('dietaryFlags'):
            print(f"   Tags: {', '.join(e['dietaryFlags'])}")
        if e.get('notes'):
            print(f"   Notes: {e['notes']}")
            
def main():
    MENU = (
        "\nNutriLogic (CLI Prototype)\n"
        "=========================\n"
        "1) Add new meal\n"
        "2) List all meals\n"
        "3) Exit\n"
    )

    while True:
        print(MENU)
        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            add_item()
        elif choice == "2":
            list_items()
        elif choice == "3":
            print("Goodbye! 👋")
            break
        else:
            print("Please choose a valid option (1-3).")

if __name__ == "__main__":
    load_data()  # NEW: try to load existing meals from data.json
    main()