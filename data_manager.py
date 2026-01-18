"""
Data persistence manager for the Patient Allocator application.
Handles all CSV file I/O operations using standard library.
"""

import os
import csv
from config import (
    DATA_FILE, YESTERDAY_FILE, SELECTED_FILE,
    MASTER_LIST_FILE, DEFAULT_PARAMS_FILE, DEFAULT_PHYSICIANS_FILE,
    DEFAULT_MASTER_LIST, DEFAULT_PARAMETERS
)


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
    """Saves the physician table to a CSV file from a list of dicts."""
    if not physicians_list:
        return

    fieldnames = ["Yesterday", "Physician Name", "Team", "New Physician", "Buffer",
                  "Working", "Total Patients", "StepDown", "Out of floor", "Traded"]

    with open(DATA_FILE, 'w', newline='') as f:
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


def load_physicians():
    """Loads the physician table from a CSV file. Returns list of dicts."""
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

        # Sort alphabetically by physician name
        physicians.sort(key=lambda p: p["name"])
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
        if p["name"] == name:
            physicians[i].update(updated_data)
            break
    save_physicians(physicians)
    return physicians


def add_physician(physician_data):
    """Add a new physician to the table."""
    physicians = load_physicians()
    existing_names = [p["name"] for p in physicians]
    if physician_data.get("name") not in existing_names:
        physicians.append(physician_data)
        save_physicians(physicians)
    return physicians


def delete_physician(name):
    """Delete a physician from the table by name."""
    physicians = load_physicians()
    physicians = [p for p in physicians if p["name"] != name]
    save_physicians(physicians)
    return physicians
