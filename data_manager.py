"""
Data persistence manager for the Patient Allocator application.
Handles all CSV file I/O operations using standard library.
"""

import os
import csv
from config import (
    DATA_FILE, YESTERDAY_FILE, SELECTED_FILE,
    MASTER_LIST_FILE, DEFAULT_PARAMS_FILE, DEFAULT_PHYSICIANS_FILE,
    TEAM_ASSIGNMENTS_FILE, DEFAULT_MASTER_LIST, DEFAULT_PARAMETERS
)
from models import Physician


def _str_to_bool(value):
    """Convert string to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes')
    return bool(value)


def _safe_int(value, default=0):
    """Safely convert value to int."""
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def save_physicians(physicians_list):
    """Saves the physician table to a CSV file from a list of Physician objects."""
    if not physicians_list:
        # Write empty file with headers
        fieldnames = ["Yesterday", "Physician Name", "Team", "New Physician", "Buffer",
                      "Working", "Total Patients", "StepDown", "Out of floor", "Traded"]
        with open(DATA_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
        return

    fieldnames = ["Yesterday", "Physician Name", "Team", "New Physician", "Buffer",
                  "Working", "Total Patients", "StepDown", "Out of floor", "Traded"]

    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in physicians_list:
            # Handle both Physician objects and dicts
            if isinstance(p, Physician):
                writer.writerow({
                    "Yesterday": p.yesterday,
                    "Physician Name": p.name,
                    "Team": p.team,
                    "New Physician": p.is_new,
                    "Buffer": p.is_buffer,
                    "Working": p.is_working,
                    "Total Patients": p.total_patients,
                    "StepDown": p.step_down_patients,
                    "Out of floor": p.transferred_patients,
                    "Traded": p.traded_patients
                })
            else:
                writer.writerow({
                    "Yesterday": p.get("yesterday", ""),
                    "Physician Name": p.get("name", ""),
                    "Team": p.get("team", "A"),
                    "New Physician": p.get("is_new", False),
                    "Buffer": p.get("is_buffer", False),
                    "Working": p.get("is_working", True),
                    "Total Patients": p.get("total_patients", 0),
                    "StepDown": p.get("step_down_patients", 0),
                    "Out of floor": p.get("transferred_patients", 0),
                    "Traded": p.get("traded_patients", 0)
                })


def load_physicians():
    """Loads the physician table from a CSV file. Returns list of Physician objects."""
    yesterday_physicians = load_yesterday_physicians()

    if not os.path.exists(DATA_FILE):
        return []

    try:
        physicians = []
        with open(DATA_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = str(row.get("Physician Name", "")).strip()
                if not name:
                    continue

                yesterday = str(row.get("Yesterday", "")).strip()
                if yesterday in ("nan", "False", "True", "None"):
                    yesterday = ""
                if not yesterday and name in yesterday_physicians:
                    yesterday = name

                physicians.append(Physician(
                    name=name,
                    yesterday=yesterday,
                    team=str(row.get("Team", "A")).strip() or "A",
                    is_new=_str_to_bool(row.get("New Physician", False)),
                    is_buffer=_str_to_bool(row.get("Buffer", False)),
                    is_working=_str_to_bool(row.get("Working", True)),
                    total_patients=_safe_int(row.get("Total Patients", 0)),
                    step_down_patients=_safe_int(row.get("StepDown", 0)),
                    transferred_patients=_safe_int(row.get("Out of floor", 0)),
                    traded_patients=_safe_int(row.get("Traded", 0))
                ))

        # Sort alphabetically by physician name
        physicians.sort(key=lambda p: p.name)
        return physicians
    except Exception as e:
        print(f"Error loading physicians: {e}")
        return []


def save_yesterday_physicians(physician_names):
    """Saves yesterday's physician names to a file."""
    filtered_names = [str(name).strip() for name in physician_names
                     if name and str(name).strip()]

    with open(YESTERDAY_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Physician Name"])
        for name in filtered_names:
            writer.writerow([name])


def load_yesterday_physicians():
    """Loads yesterday's physician names from a file."""
    if not os.path.exists(YESTERDAY_FILE):
        return []

    try:
        names = []
        with open(YESTERDAY_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = str(row.get("Physician Name", "")).strip()
                if name and name not in ("nan", "None"):
                    names.append(name)
        return names
    except Exception:
        return []


def save_selected_physicians(physician_names):
    """Saves selected physician names to a file."""
    with open(SELECTED_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Physician Name"])
        for name in physician_names:
            writer.writerow([name])


def load_selected_physicians():
    """Loads selected physician names from a file."""
    if not os.path.exists(SELECTED_FILE):
        return []

    try:
        names = []
        with open(SELECTED_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("Physician Name", "")
                if name:
                    names.append(name)
        return names
    except Exception:
        return []


def save_master_list(physician_names):
    """Saves the master physician list to a file."""
    unique_sorted = sorted(list(set(physician_names)))

    with open(MASTER_LIST_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Physician Name"])
        for name in unique_sorted:
            writer.writerow([name])


def load_master_list():
    """Loads the master physician list from a file, or returns default if file doesn't exist."""
    if not os.path.exists(MASTER_LIST_FILE):
        return sorted(list(set(DEFAULT_MASTER_LIST)))

    try:
        names = []
        with open(MASTER_LIST_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = str(row.get("Physician Name", "")).strip()
                if name and name not in ("nan", "None"):
                    names.append(name)
        if names:
            return sorted(list(set(names)))
    except Exception:
        pass

    return sorted(list(set(DEFAULT_MASTER_LIST)))


def save_parameters(params_dict):
    """Saves allocation parameters to a file."""
    fieldnames = list(params_dict.keys())

    with open(DEFAULT_PARAMS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(params_dict)


def load_parameters():
    """Loads allocation parameters from a file."""
    if not os.path.exists(DEFAULT_PARAMS_FILE):
        return DEFAULT_PARAMETERS.copy()

    try:
        with open(DEFAULT_PARAMS_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            row = next(reader, None)
            if row:
                return {
                    "n_total_new_patients": _safe_int(row.get("n_total_new_patients", 20), 20),
                    "n_A_new_patients": _safe_int(row.get("n_A_new_patients", 0), 0),
                    "n_B_new_patients": _safe_int(row.get("n_B_new_patients", 0), 0),
                    "n_N_new_patients": _safe_int(row.get("n_N_new_patients", 0), 0),
                    "n_step_down_patients": _safe_int(row.get("n_step_down_patients", 0), 0),
                    "minimum_patients": _safe_int(row.get("minimum_patients", 10), 10),
                    "maximum_patients": _safe_int(row.get("maximum_patients", 14), 14),
                    "new_start_number": _safe_int(row.get("new_start_number", 10), 10),
                }
    except Exception:
        pass

    return DEFAULT_PARAMETERS.copy()


def save_default_physicians(physicians_list):
    """Saves physician data as the default template."""
    save_physicians_to_file(physicians_list, DEFAULT_PHYSICIANS_FILE)


def save_physicians_to_file(physicians_list, filepath):
    """Saves physician list to a specific file."""
    if not physicians_list:
        return

    fieldnames = ["Yesterday", "Physician Name", "Team", "New Physician", "Buffer",
                  "Working", "Total Patients", "StepDown", "Out of floor", "Traded"]

    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in physicians_list:
            writer.writerow({
                "Yesterday": p.get("yesterday", ""),
                "Physician Name": p.get("name", ""),
                "Team": p.get("team", "A"),
                "New Physician": p.get("is_new", False),
                "Buffer": p.get("is_buffer", False),
                "Working": p.get("is_working", True),
                "Total Patients": p.get("total_patients", 0),
                "StepDown": p.get("step_down_patients", 0),
                "Out of floor": p.get("transferred_patients", 0),
                "Traded": p.get("traded_patients", 0)
            })


def load_default_physicians():
    """Loads default physician data from a file."""
    if not os.path.exists(DEFAULT_PHYSICIANS_FILE):
        return []

    try:
        physicians = []
        with open(DEFAULT_PHYSICIANS_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = str(row.get("Physician Name", "")).strip()
                if not name:
                    continue

                yesterday = str(row.get("Yesterday", "")).strip()
                if yesterday in ("nan", "False", "True", "None"):
                    yesterday = ""

                physicians.append({
                    "name": name,
                    "yesterday": yesterday,
                    "team": str(row.get("Team", "A")).strip() or "A",
                    "is_new": _str_to_bool(row.get("New Physician", False)),
                    "is_buffer": _str_to_bool(row.get("Buffer", False)),
                    "is_working": _str_to_bool(row.get("Working", True)),
                    "total_patients": _safe_int(row.get("Total Patients", 0)),
                    "step_down_patients": _safe_int(row.get("StepDown", 0)),
                    "transferred_patients": _safe_int(row.get("Out of floor", 0)),
                    "traded_patients": _safe_int(row.get("Traded", 0))
                })
        return physicians
    except Exception:
        return []


def update_physician(name, updated_data):
    """Update a single physician's data by name."""
    physicians = load_physicians()
    for i, p in enumerate(physicians):
        if p.name == name:
            # Update attributes
            for key, value in updated_data.items():
                if hasattr(p, key):
                    setattr(p, key, value)
            break
    save_physicians(physicians)
    return physicians


def add_physician(physician_data):
    """Add a new physician to the table."""
    physicians = load_physicians()
    existing_names = [p.name for p in physicians]
    name = physician_data.get("name") if isinstance(physician_data, dict) else physician_data.name
    if name not in existing_names:
        if isinstance(physician_data, dict):
            physician_data = Physician(**physician_data)
        physicians.append(physician_data)
        save_physicians(physicians)
    return physicians


def delete_physician(name):
    """Delete a physician from the table by name."""
    physicians = load_physicians()
    physicians = [p for p in physicians if p.name != name]
    save_physicians(physicians)
    return physicians


# Alias functions for app.py compatibility
def load_yesterday():
    """Alias for load_yesterday_physicians."""
    return load_yesterday_physicians()


def save_yesterday(names):
    """Alias for save_yesterday_physicians."""
    save_yesterday_physicians(names)


def load_selected():
    """Alias for load_selected_physicians."""
    return load_selected_physicians()


def save_selected(names):
    """Alias for save_selected_physicians."""
    save_selected_physicians(names)


def save_team_assignments(assignments):
    """Save team assignments to a CSV file. assignments is a dict {name: team}."""
    with open(TEAM_ASSIGNMENTS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Physician Name", "Team"])
        for name, team in assignments.items():
            writer.writerow([name, team])


def load_team_assignments():
    """Load team assignments from a CSV file. Returns a dict {name: team}."""
    if not os.path.exists(TEAM_ASSIGNMENTS_FILE):
        return {}

    try:
        assignments = {}
        with open(TEAM_ASSIGNMENTS_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = str(row.get("Physician Name", "")).strip()
                team = str(row.get("Team", "A")).strip()
                if name:
                    assignments[name] = team if team in ("A", "B", "N") else "A"
        return assignments
    except Exception:
        return {}
