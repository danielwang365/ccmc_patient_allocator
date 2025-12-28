import streamlit as st
import pandas as pd
import os

# Files for persistent storage
DATA_FILE = "physician_data.csv"
YESTERDAY_FILE = "yesterday_physicians.csv"
SELECTED_FILE = "selected_physicians.csv"
MASTER_LIST_FILE = "master_physician_list.csv"

def save_data(df):
    """Saves the physician table to a CSV file."""
    df.to_csv(DATA_FILE, index=False)

def load_data(default_rows):
    """Loads the physician table from a CSV file if it exists, otherwise returns default rows."""
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            # Filter out rows with empty physician names
            df = df.dropna(subset=["Physician Name"])
            df = df[df["Physician Name"].str.strip() != ""]
            # Ensure boolean columns are correctly typed
            bool_cols = ["New Physician", "Buffer", "Working"]
            for col in bool_cols:
                if col in df.columns:
                    df[col] = df[col].astype(bool)
            # Add Yesterday column if missing
            if "Yesterday" not in df.columns:
                yesterday_physicians = load_yesterday_physicians()
                # Pre-fill with physician name if they worked yesterday
                df["Yesterday"] = df["Physician Name"].apply(lambda x: x if x in yesterday_physicians else "")
            else:
                # Convert to string if it's boolean (for backward compatibility)
                if df["Yesterday"].dtype == bool:
                    yesterday_physicians = load_yesterday_physicians()
                    df["Yesterday"] = df["Physician Name"].apply(lambda x: x if x in yesterday_physicians else "")
                else:
                    df["Yesterday"] = df["Yesterday"].astype(str).replace("nan", "").replace("False", "").replace("True", "")
            # Sort alphabetically by physician name by default
            df = df.sort_values("Physician Name").reset_index(drop=True)
            # Reorder columns to put Yesterday first
            cols = df.columns.tolist()
            if "Yesterday" in cols:
                cols.remove("Yesterday")
                cols.insert(0, "Yesterday")
            df = df[cols]
            return df
        except Exception:
            df = pd.DataFrame(default_rows)
            # Add Yesterday column to default rows
            if "Yesterday" not in df.columns:
                yesterday_physicians = load_yesterday_physicians()
                # Pre-fill with physician name if they worked yesterday
                df["Yesterday"] = df["Physician Name"].apply(lambda x: x if x in yesterday_physicians else "")
            # Sort alphabetically by physician name
            df = df.sort_values("Physician Name").reset_index(drop=True)
            # Reorder columns to put Yesterday first
            cols = df.columns.tolist()
            if "Yesterday" in cols:
                cols.remove("Yesterday")
                cols.insert(0, "Yesterday")
            df = df[cols]
            return df
    df = pd.DataFrame(default_rows)
    # Add Yesterday column to default rows
    if "Yesterday" not in df.columns:
        yesterday_physicians = load_yesterday_physicians()
        # Pre-fill with physician name if they worked yesterday
        df["Yesterday"] = df["Physician Name"].apply(lambda x: x if x in yesterday_physicians else "")
    # Sort alphabetically by physician name
    df = df.sort_values("Physician Name").reset_index(drop=True)
    # Reorder columns to put Yesterday first
    cols = df.columns.tolist()
    if "Yesterday" in cols:
        cols.remove("Yesterday")
        cols.insert(0, "Yesterday")
    df = df[cols]
    return df

def save_yesterday_physicians(physician_names):
    """Saves yesterday's physician names to a file."""
    df = pd.DataFrame({"Physician Name": physician_names})
    df.to_csv(YESTERDAY_FILE, index=False)

def load_yesterday_physicians():
    """Loads yesterday's physician names from a file."""
    if os.path.exists(YESTERDAY_FILE):
        try:
            df = pd.read_csv(YESTERDAY_FILE)
            return df["Physician Name"].tolist()
        except Exception:
            return []
    return []

def save_selected_physicians(physician_names):
    """Saves selected physician names to a file."""
    df = pd.DataFrame({"Physician Name": physician_names})
    df.to_csv(SELECTED_FILE, index=False)

def load_selected_physicians():
    """Loads selected physician names from a file."""
    if os.path.exists(SELECTED_FILE):
        try:
            df = pd.read_csv(SELECTED_FILE)
            return df["Physician Name"].tolist()
        except Exception:
            return []
    return []

def save_master_list(physician_names):
    """Saves the master physician list to a file."""
    df = pd.DataFrame({"Physician Name": sorted(list(set(physician_names)))})
    df.to_csv(MASTER_LIST_FILE, index=False)

def load_master_list(default_list):
    """Loads the master physician list from a file, or returns default if file doesn't exist."""
    if os.path.exists(MASTER_LIST_FILE):
        try:
            df = pd.read_csv(MASTER_LIST_FILE)
            # Filter out empty names
            names = [name.strip() for name in df["Physician Name"].astype(str).tolist() if name.strip()]
            if names:
                return sorted(list(set(names)))
        except Exception:
            pass
    # Return default list if file doesn't exist or error occurred
    return sorted(list(set(default_list)))

class Physician():
    def __init__(self, 
            name : str = "", 
            is_new : bool = False, 
            team : str = 'A', 
            n_total_patients : int = 0, 
            n_step_down_patients : int = 0, 
            n_transferred_patients : int = 0, 
            n_traded_patients : int = 0,
            is_buffer : bool = False,
            is_working : bool = True):
        
        self.name = name
        self.is_new : bool = is_new
        self.team : str = team
        self.is_buffer : bool = is_buffer
        self.is_working : bool = is_working

        self.total_patients : int = n_total_patients
        self.step_down_patients : int = n_step_down_patients

        self.transferred_patients : int = n_transferred_patients
        self.traded_patients : int = n_traded_patients

    def __repr__(self):
        return f"Physician({self.name}, {self.team}, {self.total_patients})"

    def add_patient(self, is_step_down : bool = False):
        self.total_patients += 1

        if is_step_down:
            self.step_down_patients += 1

    def remove_patient(self, is_step_down: bool = False):
        if self.total_patients < 1:
            raise Exception("You don't have any patients")

        self.total_patients -= 1
        
        if is_step_down:
            self.step_down_patients -= 1

    def set_total_patients(self, n : int):
        self.total_patients = n

    def set_step_down_patients(self, n : int):
        self.step_down_patients = n

    def set_transferred_patient(self, n : int):
        self.transferred_patients = n

    def set_traded_patients(self, n : int):
        self.traded_patients = n

def allocate_patients(
    physicians: list['Physician'],
    n_total_new_patients: int,
    n_A_new_patients: int,
    n_B_new_patients: int,
    n_N_new_patients: int,
    new_start_number: int,
    minimum_patients: int = 10,
    n_step_down_patients: int = 0,
    maximum_patients: int = 1000
):
    # Store initial patient counts for even distribution later
    initial_counts = {p.name: p.total_patients for p in physicians}
    
    # Make team lists
    team_A = [p for p in physicians if p.team == 'A']
    team_B = [p for p in physicians if p.team == 'B']
    team_N = [p for p in physicians if p.team == 'N']
    
    # Get buffer physicians
    buffer_A = [p for p in team_A if p.is_buffer]
    buffer_B = [p for p in team_B if p.is_buffer]

    # Helper function to check if physician can take more patients
    def can_take_patient(physician):
        return physician.total_patients < maximum_patients
    
    # Store initial stepdown counts for gained calculation
    initial_stepdown_counts = {p.name: p.step_down_patients for p in physicians}
    
    # Helper function to check if physician can take a step down patient
    # Only limit the gained stepdown to 1, not the total stepdown
    def can_take_step_down(physician):
        gained_stepdown = physician.step_down_patients - initial_stepdown_counts.get(physician.name, 0)
        return gained_stepdown < 1 and can_take_patient(physician)
    
    # First, allocate step down patients: Team B first, then Team A
    # Only limit gained stepdown to 1, total stepdown can be greater
    while n_step_down_patients > 0:
        # Find Team B physicians who can take a step down patient (gained stepdown < 1)
        available_B = [p for p in team_B if can_take_step_down(p)]
        if available_B:
            # Allocate to Team B physician with lowest total patient count
            min_physician = min(available_B, key=lambda x: x.total_patients)
            min_physician.add_patient(is_step_down=True)
            n_step_down_patients -= 1
        else:
            # All Team B physicians already have gained 1 step down patient, allocate to Team A
            available_A = [p for p in team_A if can_take_step_down(p)]
            if available_A:
                # Allocate to Team A physician with lowest total patient count
                min_physician = min(available_A, key=lambda x: x.total_patients)
                min_physician.add_patient(is_step_down=True)
                n_step_down_patients -= 1
            else:
                # Both teams are full (all physicians have gained 1 step down patient)
                break
    
    # Second, fix physicians who are more than 1 less than the minimum value
    # (i.e., if minimum is 10, fix physicians with 8 or fewer patients)
    threshold = minimum_patients - 2
    for physician in physicians:
        if physician.total_patients <= threshold and can_take_patient(physician):
            needed = minimum_patients - physician.total_patients
            # Allocate from the physician's team pool
            if physician.team == 'A':
                for _ in range(min(needed, n_A_new_patients)):
                    if can_take_patient(physician):
                        physician.add_patient()
                        n_A_new_patients -= 1
                        n_total_new_patients -= 1
                    else:
                        break
            elif physician.team == 'B':
                for _ in range(min(needed, n_B_new_patients)):
                    if can_take_patient(physician):
                        physician.add_patient()
                        n_B_new_patients -= 1
                        n_total_new_patients -= 1
                    else:
                        break
            elif physician.team == 'N':
                for _ in range(min(needed, n_N_new_patients)):
                    if can_take_patient(physician):
                        physician.add_patient()
                        n_N_new_patients -= 1
                        n_total_new_patients -= 1
                    else:
                        break

    # Third, fill up new physicians to new_start_number using patients from their specific team pool
    for physician in physicians:
        if physician.is_new:
            while physician.total_patients < new_start_number and can_take_patient(physician):
                # Allocate from the physician's team pool
                if physician.team == 'A':
                    if n_A_new_patients > 0:
                        physician.add_patient()
                        n_A_new_patients -= 1
                        n_total_new_patients -= 1
                    else:
                        break
                elif physician.team == 'B':
                    if n_B_new_patients > 0:
                        physician.add_patient()
                        n_B_new_patients -= 1
                        n_total_new_patients -= 1
                    else:
                        break
                elif physician.team == 'N':
                    if n_N_new_patients > 0:
                        physician.add_patient()
                        n_N_new_patients -= 1
                        n_total_new_patients -= 1
                    else:
                        break
                else:
                    break

    # Fourth, distribute remaining patients evenly
    # Goal: All non-new physicians should get 1 or 2 patients gained
    # Physicians with step down patients should get 1, others should get 2 (if possible)
    
    # Get all non-new physicians for even distribution
    non_new_physicians = [p for p in physicians if not p.is_new]
    
    # Combine all remaining patients into a pool for even distribution
    # We'll distribute by team, but ensure even gains
    remaining_patients = n_A_new_patients + n_B_new_patients + n_N_new_patients
    
    if remaining_patients > 0 and non_new_physicians:
        # Calculate target gains: physicians with step down get 1, others get 2
        # But we need to work within available patients
        physicians_with_stepdown = [p for p in non_new_physicians if p.step_down_patients > 0]
        physicians_without_stepdown = [p for p in non_new_physicians if p.step_down_patients == 0]
        
        # Calculate how many patients we need to give each group
        # First, give 1 to physicians with step down
        # Then, give 2 to physicians without step down (if possible)
        # If not enough, give 1 to some without step down
        
        # Calculate current gains so far
        current_gains = {p.name: p.total_patients - initial_counts[p.name] for p in non_new_physicians}
        
        # Distribute Team A patients
        # Ensure all Team A patients are distributed
        team_A_non_new = [p for p in team_A if not p.is_new and can_take_patient(p)]
        while n_A_new_patients > 0:
            # Prioritize physicians without step down for 2 patients
            # But ensure all get at least 1, and difference is at most 1
            available = [p for p in team_A_non_new if can_take_patient(p)]
            if not available:
                # Team A full, try buffer
                if buffer_B:
                    available = [p for p in buffer_B if can_take_patient(p)]
                    if available:
                        min_physician = min(available, key=lambda x: (x.step_down_patients > 0, current_gains.get(x.name, 0)))
                        min_physician.add_patient()
                        n_A_new_patients -= 1
                        n_total_new_patients -= 1
                        current_gains[min_physician.name] = current_gains.get(min_physician.name, 0) + 1
                    else:
                        break
                else:
                    break
            else:
                # Find physician with lowest gain
                # Prioritize those who haven't reached their target, but continue distributing if needed
                min_physician = min(available, key=lambda x: (
                    current_gains.get(x.name, 0),  # Lowest gain first
                    1 if x.step_down_patients > 0 else 0  # Prefer those without step down (they need 2)
                ))
                
                # Always allocate if there are patients available and physician can take them
                # Don't stop just because they reached their target - continue to distribute all patients
                min_physician.add_patient()
                n_A_new_patients -= 1
                n_total_new_patients -= 1
                current_gains[min_physician.name] = current_gains.get(min_physician.name, 0) + 1
        
        # Distribute Team B patients
        # Ensure all Team B patients are distributed
        team_B_non_new = [p for p in team_B if not p.is_new and can_take_patient(p)]
        while n_B_new_patients > 0:
            available = [p for p in team_B_non_new if can_take_patient(p)]
            if not available:
                # Team B full, try buffer
                if buffer_A:
                    available = [p for p in buffer_A if can_take_patient(p)]
                    if available:
                        min_physician = min(available, key=lambda x: (x.step_down_patients > 0, current_gains.get(x.name, 0)))
                        min_physician.add_patient()
                        n_B_new_patients -= 1
                        n_total_new_patients -= 1
                        current_gains[min_physician.name] = current_gains.get(min_physician.name, 0) + 1
                    else:
                        break
                else:
                    break
            else:
                # Find physician with lowest gain
                # Prioritize those who haven't reached their target, but continue distributing if needed
                min_physician = min(available, key=lambda x: (
                    current_gains.get(x.name, 0),  # Lowest gain first
                    1 if x.step_down_patients > 0 else 0  # Prefer those without step down (they need 2)
                ))
                
                # Always allocate if there are patients available and physician can take them
                # Don't stop just because they reached their target - continue to distribute all patients
                min_physician.add_patient()
                n_B_new_patients -= 1
                n_total_new_patients -= 1
                current_gains[min_physician.name] = current_gains.get(min_physician.name, 0) + 1
        
        # Distribute Team N patients
        # Ensure all Team N patients are distributed
        team_N_non_new = [p for p in team_N if not p.is_new and can_take_patient(p)]
        while n_N_new_patients > 0:
            available = [p for p in team_N_non_new if can_take_patient(p)]
            if available:
                # Find physician with lowest gain
                # Prioritize those who haven't reached their target, but continue distributing if needed
                min_physician = min(available, key=lambda x: (
                    current_gains.get(x.name, 0),  # Lowest gain first
                    1 if x.step_down_patients > 0 else 0  # Prefer those without step down (they need 2)
                ))
                
                # Always allocate if there are patients available and physician can take them
                # Don't stop just because they reached their target - continue to distribute all patients
                min_physician.add_patient()
                n_N_new_patients -= 1
                n_total_new_patients -= 1
                current_gains[min_physician.name] = current_gains.get(min_physician.name, 0) + 1
            else:
                break

# --- Streamlit App Begins Here ---
st.set_page_config(page_title="Patient Allocator", page_icon="🩺", layout="wide")
st.title("🩺 Physician Patient Allocation")
st.write("Use the sidebar to set patient pools and parameters. Edit physician information in the table below, then click **Run Allocation** to distribute patients according to the logic.")

# Sidebar inputs
with st.sidebar:
    st.header("Allocation Parameters")
    n_total_new_patients = st.number_input("Total New Patients", min_value=0, value=20, step=1)
    n_A_new_patients = st.number_input("Team A Pool", min_value=0, value=10, step=1)
    n_B_new_patients = st.number_input("Team B Pool", min_value=0, value=8, step=1)
    n_N_new_patients = st.number_input("Team N Pool", min_value=0, value=2, step=1)
    n_step_down_patients = st.number_input("Total New Step Down Patients", min_value=0, value=0, step=1)
    minimum_patients = st.number_input("Minimum Patients", min_value=0, value=10, step=1)
    maximum_patients = st.number_input("Maximum Patients", min_value=1, value=20, step=1)
    new_start_number = st.number_input("New Start Number", min_value=0, value=5, step=1)
    st.markdown("---")
    st.info("Adjust team patient pools, step down patients, min/max patient requirements, and the number of initial patients for new physicians.")

# Default master list of all possible physicians
DEFAULT_MASTER_LIST = [
    "Adhiakha", "Wang", "Jaini", "JemJem", "Batth",
    "Rajarathinam", "Shehata", "Yousef", "Aung", "Bhogireddy",
    "Souliman", "Zaidi", "Attrapisi", "Ali", "Batlawala",
    "Sakkalaek", "Shirani", "Oladipo", "Abadi", "Kaur",
    "Narra", "Suman", "Win", "Das", "Alchi", "Reddy",
    "Hung", "Nwadei", "Lamba", "Ahir", "Mahajan", "Abukraa",
    "Keralos", "Nibber"
]

# Load master list from file or use default
MASTER_PHYSICIAN_LIST = load_master_list(DEFAULT_MASTER_LIST)

DEFAULT_ROWS = []
# Initial default setup (e.g. first 20)
for i, name in enumerate(MASTER_PHYSICIAN_LIST[:20]):
    if i < 10:
        team = "A"
        is_buf = False
    elif i == 10:
        team = "A"
        is_buf = True
    else:
        team = "B"
        is_buf = False
    
    DEFAULT_ROWS.append({
        "Yesterday": "",  # Text field for physician name who worked yesterday
        "Physician Name": name, 
        "Team": team, 
        "New Physician": False, 
        "Buffer": is_buf, 
        "Working": True, 
        "Total Patients": 0, 
        "StepDown": 0, 
        "Out of floor": 0, 
        "Traded": 0
    })

# Session state for the editable table (preserves edits/adds/removes)
if "physician_table" not in st.session_state:
    st.session_state["physician_table"] = load_data(DEFAULT_ROWS)

# Load yesterday's physicians and selected physicians
yesterday_physicians = load_yesterday_physicians()
saved_selected = load_selected_physicians()

# Initialize selected physicians in session state
if "selected_physicians" not in st.session_state:
    # Use saved selections if available, otherwise use current table physicians
    current_table_physicians = st.session_state["physician_table"]["Physician Name"].tolist() if "physician_table" in st.session_state else []
    st.session_state["selected_physicians"] = [p for p in saved_selected if p in MASTER_PHYSICIAN_LIST] if saved_selected else [p for p in current_table_physicians if p in MASTER_PHYSICIAN_LIST]

# Feature to manage master list
with st.expander("📝 Manage Master Physician List", expanded=False):
    st.markdown("**Add new physicians to the master list:**")
    new_physician_input = st.text_input(
        "New Physician Name",
        placeholder="Enter a physician name to add to the master list",
        key="new_physician_input"
    )
    
    col_master1, col_master2 = st.columns([2, 1])
    with col_master1:
        add_to_master_btn = st.button("Add to Master List", type="primary", use_container_width=True)
    
    if add_to_master_btn and new_physician_input.strip():
        new_name = new_physician_input.strip()
        if new_name not in MASTER_PHYSICIAN_LIST:
            MASTER_PHYSICIAN_LIST.append(new_name)
            MASTER_PHYSICIAN_LIST.sort()
            save_master_list(MASTER_PHYSICIAN_LIST)
            st.success(f"✅ Added '{new_name}' to the master list!")
            st.rerun()
        else:
            st.warning(f"⚠️ '{new_name}' is already in the master list.")
    
    st.markdown("---")
    st.markdown(f"**Current Master List ({len(MASTER_PHYSICIAN_LIST)} physicians):**")
    st.text(", ".join(MASTER_PHYSICIAN_LIST))

# Feature to select working doctors from the master list
with st.expander("🏥 Select Working Doctors from Master List", expanded=True):
    st.markdown("**Pick the doctors who are working today to initialize the table:**")
    
    # Show yesterday's physicians if available
    if yesterday_physicians:
        st.markdown(f"**Yesterday's Physicians ({len(yesterday_physicians)}):** {', '.join(yesterday_physicians)}")
    
    # Create checkboxes for each doctor in the master list
    st.markdown("**Select Today's Physicians:**")
    
    # Organize checkboxes in columns for better layout
    num_cols = 3
    cols = st.columns(num_cols)
    
    selected_doctors = []
    for idx, doctor_name in enumerate(MASTER_PHYSICIAN_LIST):
        col_idx = idx % num_cols
        with cols[col_idx]:
            # Check if this doctor was selected previously or is in yesterday's list
            is_checked = doctor_name in st.session_state["selected_physicians"]
            if st.checkbox(doctor_name, value=is_checked, key=f"doctor_checkbox_{doctor_name}"):
                selected_doctors.append(doctor_name)
    
    # Update session state with selected doctors
    st.session_state["selected_physicians"] = selected_doctors
    
    if st.button("Generate Table from Selection", type="primary"):
        if selected_doctors:
            # Save current physicians as yesterday's before generating new table
            current_physicians = st.session_state["physician_table"]["Physician Name"].tolist() if "physician_table" in st.session_state else []
            if current_physicians:
                save_yesterday_physicians(current_physicians)
            
            # Save selected physicians
            save_selected_physicians(selected_doctors)
            
            new_rows = []
            for i, name in enumerate(selected_doctors):
                # Simple logic to alternate teams for the new table
                team = "A" if i % 2 == 0 else "B"
                # Pre-fill Yesterday column with physician name if they worked yesterday
                yesterday_value = name if name in yesterday_physicians else ""
                new_rows.append({
                    "Yesterday": yesterday_value,
                    "Physician Name": name,
                    "Team": team,
                    "New Physician": False,
                    "Buffer": False,
                    "Working": True,
                    "Total Patients": 0,
                    "StepDown": 0,
                    "Out of floor": 0,
                    "Traded": 0
                })
            new_df = pd.DataFrame(new_rows)
            # Sort alphabetically by physician name by default
            new_df = new_df.sort_values("Physician Name").reset_index(drop=True)
            st.session_state["physician_table"] = new_df
            save_data(new_df)
            st.rerun()
        else:
            st.warning("Please select at least one doctor.")

# Feature to add physicians from a list
with st.expander("➕ Add Physicians from List", expanded=False):
    st.markdown("Enter physician names (one per line or comma-separated):")
    physician_names_input = st.text_area(
        "Physician Names",
        placeholder="Enter names, one per line:\nDr. Smith\nDr. Jones\nDr. Brown\n\nOr comma-separated:\nDr. Smith, Dr. Jones, Dr. Brown",
        height=150,
        key="physician_names_input"
    )
    
    col_add1, col_add2 = st.columns([2, 1])
    with col_add1:
        default_team = st.selectbox("Default Team for New Physicians", options=["A", "B", "N"], index=0)
    with col_add2:
        add_physicians_btn = st.button("Add Physicians", type="primary", use_container_width=True)
    
    if add_physicians_btn and physician_names_input.strip():
        # Parse physician names (handle both newline and comma-separated)
        names_text = physician_names_input.strip()
        # Try splitting by newlines first, then by commas
        if '\n' in names_text:
            names = [name.strip() for name in names_text.split('\n') if name.strip()]
        else:
            names = [name.strip() for name in names_text.split(',') if name.strip()]
        
        if names:
            # Get current table
            current_table = st.session_state["physician_table"].copy()
            existing_names = set(current_table["Physician Name"].astype(str).tolist())
            
            # Create new rows for physicians that don't already exist
            new_rows = []
            added_count = 0
            skipped_count = 0
            
            for name in names:
                if name and name not in existing_names:
                    # Pre-fill Yesterday column with physician name if they worked yesterday
                    yesterday_value = name if name in yesterday_physicians else ""
                    new_rows.append({
                        "Yesterday": yesterday_value,
                        "Physician Name": name,
                        "Team": default_team,
                        "New Physician": False,
                        "Buffer": False,
                        "Working": True,
                        "Total Patients": 0,
                        "StepDown": 0,
                        "Out of floor": 0,
                        "Traded": 0
                    })
                    added_count += 1
                    existing_names.add(name)  # Prevent duplicates in the same batch
                else:
                    skipped_count += 1
            
            if new_rows:
                # Add new rows to the table
                new_df = pd.DataFrame(new_rows)
                updated_table = pd.concat([current_table, new_df], ignore_index=True)
                # Sort alphabetically by physician name
                updated_table = updated_table.sort_values("Physician Name").reset_index(drop=True)
                # Reorder columns to put Yesterday first
                cols = updated_table.columns.tolist()
                if "Yesterday" in cols:
                    cols.remove("Yesterday")
                    cols.insert(0, "Yesterday")
                updated_table = updated_table[cols]
                st.session_state["physician_table"] = updated_table
                save_data(updated_table)  # Persist changes
                if added_count > 0:
                    st.success(f"✅ Added {added_count} physician(s) to the table!")
                if skipped_count > 0:
                    st.warning(f"⚠️ Skipped {skipped_count} physician(s) (already exist or empty names)")
            else:
                st.warning("No new physicians were added. All names already exist in the table.")
        else:
            st.error("Please enter at least one physician name.")

# Get the current table from session state
# Ensure it has Yesterday column and is sorted alphabetically by default
current_table = st.session_state["physician_table"].copy()
if not current_table.empty:
    # Add Yesterday column if missing
    if "Yesterday" not in current_table.columns:
        # Pre-fill with physician name if they worked yesterday
        current_table["Yesterday"] = current_table["Physician Name"].apply(lambda x: x if x in yesterday_physicians else "")
    # Reorder columns to put Yesterday first
    cols = current_table.columns.tolist()
    if "Yesterday" in cols:
        cols.remove("Yesterday")
        cols.insert(0, "Yesterday")
    current_table = current_table[cols]

# Display yesterday's and today's physicians
if yesterday_physicians or current_table is not None:
    st.markdown("### 📋 Physician Information")
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        if yesterday_physicians:
            st.markdown(f"**Yesterday's Physicians ({len(yesterday_physicians)}):**")
            st.text(", ".join(yesterday_physicians))
        else:
            st.markdown("**Yesterday's Physicians:** *No data available*")
    with info_col2:
        if current_table is not None and not current_table.empty:
            today_physicians = current_table["Physician Name"].tolist()
            st.markdown(f"**Today's Physicians ({len(today_physicians)}):**")
            st.text(", ".join(today_physicians))
        else:
            st.markdown("**Today's Physicians:** *No data available*")
    st.markdown("---")

# Ensure table has Yesterday column and reorder columns
if not current_table.empty:
    # Add Yesterday column if missing
    if "Yesterday" not in current_table.columns:
        # Pre-fill with physician name if they worked yesterday
        current_table["Yesterday"] = current_table["Physician Name"].apply(lambda x: x if x in yesterday_physicians else "")
    # Reorder columns to put Yesterday first
    cols = current_table.columns.tolist()
    if "Yesterday" in cols:
        cols.remove("Yesterday")
        cols.insert(0, "Yesterday")
    current_table = current_table[cols]

# Add sorting option for the input table
sort_input_table = st.checkbox("Sort by Total Patients (Lowest to Highest) for Team A & B", value=False, key="sort_input_table")

# Apply sorting based on checkbox
if not current_table.empty:
    if sort_input_table:
        # Sort by Team first, then by Total Patients (ascending) within each team
        current_table = current_table.copy()
        current_table["Total Patients"] = pd.to_numeric(current_table["Total Patients"], errors='coerce')
        current_table = current_table.sort_values(
            by=["Team", "Total Patients"], 
            ascending=[True, True], 
            na_position='last'
        ).reset_index(drop=True)
    else:
        # Default: sort alphabetically by physician name
        current_table = current_table.sort_values("Physician Name").reset_index(drop=True)

edited_phys = st.data_editor(
    current_table,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "Yesterday": st.column_config.TextColumn(
            "Yesterday",
            help="Enter the name of the physician who worked yesterday"
        ),
        "Physician Name": st.column_config.TextColumn("Physician Name", help="e.g. A1, B2"),
        "Team": st.column_config.SelectboxColumn(
            "Team", options=["A","B","N"]
        ),
        "New Physician": st.column_config.CheckboxColumn(
            "New Physician"
        ),
        "Buffer": st.column_config.CheckboxColumn(
            "Buffer"
        ),
        "Working": st.column_config.CheckboxColumn(
            "Working"
        ),
        "Total Patients": st.column_config.NumberColumn(
            "Total Patients", min_value=0, step=1, format="%d"
        ),
        "StepDown": st.column_config.NumberColumn(
            "StepDown", min_value=0, step=1, format="%d"
        ),
        "Out of floor": st.column_config.NumberColumn(
            "Out of floor", min_value=0, step=1, format="%d"
        ),
        "Traded": st.column_config.NumberColumn(
            "Traded", min_value=0, step=1, format="%d"
        ),
        "Gained": st.column_config.NumberColumn(
            "Gained", min_value=0, step=1, format="%d"
        ),
    },
    hide_index=True,
    key="physician_table_editor",
    on_change=None,  # Don't use on_change to avoid conflicts
)

run = st.button("Run Allocation", use_container_width=True, type="primary")

if run:
    # Update session state with latest edits when button is clicked
    # This is the only place we update session state from the data editor
    # The widget's key maintains state between renders
    st.session_state["physician_table"] = edited_phys.copy()
    save_data(edited_phys)  # Persist changes
    
    # Save current physicians as yesterday's for next time
    current_physician_names = edited_phys["Physician Name"].tolist()
    save_yesterday_physicians(current_physician_names)
    
    current_table = edited_phys.copy()
    
    # Convert table rows into Physician objects
    physicians = []
    for _, row in current_table.dropna(subset=["Physician Name", "Team"]).iterrows():
        # Defensive parsing for blank/empty
        try:
            tp = int(row["Total Patients"])
        except Exception:
            tp = 0
        try:
            sdp = int(row["StepDown"])
        except Exception:
            sdp = 0
        # Handle both "Out of floor" and "Transferred" for backward compatibility
        try:
            if "Out of floor" in row.index:
                tfp = int(row["Out of floor"])
            elif "Transferred" in row.index:
                tfp = int(row["Transferred"])
            else:
                tfp = 0
        except Exception:
            tfp = 0
        try:
            tdp = int(row["Traded"])
        except Exception:
            tdp = 0
        try:
            is_buf = bool(row.get("Buffer", False))
        except Exception:
            is_buf = False
        try:
            is_working = bool(row.get("Working", True))  # Default to True if not specified
        except Exception:
            is_working = True
        physicians.append(
            Physician(
                name=str(row["Physician Name"]),
                is_new=bool(row["New Physician"]),
                team=str(row["Team"]),
                n_total_patients=tp,
                n_step_down_patients=sdp,
                n_transferred_patients=tfp,
                n_traded_patients=tdp,
                is_buffer=is_buf,
                is_working=is_working
            )
        )
    
    # Filter to only working physicians for allocation
    working_physicians = [p for p in physicians if p.is_working]
    
    # Store initial patient counts before allocation (for all physicians, but only allocate to working ones)
    initial_counts = {p.name: p.total_patients for p in physicians}
    initial_step_down_counts = {p.name: p.step_down_patients for p in physicians}
    # Run allocation logic - only on working physicians
    allocate_patients(
        working_physicians,
        int(n_total_new_patients),
        int(n_A_new_patients),
        int(n_B_new_patients),
        int(n_N_new_patients),
        int(new_start_number),
        int(minimum_patients),
        int(n_step_down_patients),
        int(maximum_patients)
    )
    
    # Prepare results - only show working physicians, exclude Working column
    results_df = pd.DataFrame([
        {
            "Physician Name": p.name,
            "Team": p.team,
            "New Physician": p.is_new,
            "Buffer": p.is_buffer,
            "Total Patients": p.total_patients,
            "StepDown": p.step_down_patients,
            "Out of floor": p.transferred_patients,
            "Traded": p.traded_patients,
            "Gained": p.total_patients - initial_counts[p.name],
            "Gained StepDown": p.step_down_patients - initial_step_down_counts[p.name],
            "Gained + Traded": p.traded_patients + (p.total_patients - initial_counts[p.name]),
        }
        for p in working_physicians
    ])
    
    # Store results in session state so they persist across reruns
    st.session_state["allocation_results"] = results_df.copy()
    st.session_state["allocation_summary"] = {
        "team_a_total": sum(p.total_patients for p in working_physicians if p.team == 'A'),
        "team_b_total": sum(p.total_patients for p in working_physicians if p.team == 'B'),
        "team_a_gained": sum(p.total_patients - initial_counts[p.name] for p in working_physicians if p.team == 'A'),
        "team_b_gained": sum(p.total_patients - initial_counts[p.name] for p in working_physicians if p.team == 'B'),
        "team_a_stepdown_gained": sum(p.step_down_patients - initial_step_down_counts[p.name] for p in working_physicians if p.team == 'A'),
        "team_b_stepdown_gained": sum(p.step_down_patients - initial_step_down_counts[p.name] for p in working_physicians if p.team == 'B'),
        "team_a_traded": sum(p.traded_patients for p in working_physicians if p.team == 'A'),
        "team_b_traded": sum(p.traded_patients for p in working_physicians if p.team == 'B'),
        "total_census": sum(p.total_patients for p in working_physicians),
        "total_gained": sum(p.total_patients - initial_counts[p.name] for p in working_physicians),
    }

# Display results if they exist in session state
if "allocation_results" in st.session_state and st.session_state["allocation_results"] is not None:
    st.markdown("### :clipboard: Results")
    
    # Add sorting option
    sort_by_total = st.checkbox("Sort by Total Patients (Lowest to Highest)", value=False, key="sort_results")
    
    # Get results from session state
    display_df = st.session_state["allocation_results"].copy()
    
    # Apply sorting if requested
    if sort_by_total:
        # Sort by Team first, then by Total Patients (ascending) within each team
        # This keeps Team A and Team B grouped separately, each sorted low to high
        # Convert to numeric to ensure proper numeric sorting
        display_df["Total Patients"] = pd.to_numeric(display_df["Total Patients"], errors='coerce')
        display_df = display_df.sort_values(
            by=["Team", "Total Patients"], 
            ascending=[True, True], 
            na_position='last'
        ).reset_index(drop=True)
    
    st.dataframe(display_df, hide_index=True, use_container_width=True)
    
    # Display summary if it exists
    if "allocation_summary" in st.session_state:
        summary = st.session_state["allocation_summary"]
        
        # Calculate trades
        trade_info = {'A_to_B': summary["team_a_traded"], 'B_to_A': summary["team_b_traded"]}
        team_a_gained_traded = summary["team_a_gained"] + summary["team_b_traded"]
        team_b_gained_traded = summary["team_b_gained"] + summary["team_a_traded"]
        
        st.markdown("### 📊 Allocation Summary")
        
        # Team-specific information
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Team A")
            st.metric("Total Patients", summary["team_a_total"])
            st.metric("Total Patients Gained", summary["team_a_gained"])
            st.metric("Step Down Patients Gained", summary["team_a_stepdown_gained"])
            st.metric("Total Patients Gained + Traded", team_a_gained_traded)
        with col2:
            st.markdown("#### Team B")
            st.metric("Total Patients", summary["team_b_total"])
            st.metric("Total Patients Gained", summary["team_b_gained"])
            st.metric("Step Down Patients Gained", summary["team_b_stepdown_gained"])
            st.metric("Total Patients Gained + Traded", team_b_gained_traded)
        
        # Overall census information
        st.markdown("---")
        col3, col4 = st.columns(2)
        with col3:
            st.metric("Total Census", summary["total_census"])
        with col4:
            st.metric("Total Patients Gained from Yesterday", summary["total_gained"])
        
        # Trade information
        st.markdown("---")
        st.markdown("#### 🔄 Trade Summary")
        col5, col6 = st.columns(2)
        with col5:
            st.metric("Patients Traded from Team A to Team B", trade_info['A_to_B'])
        with col6:
            st.metric("Patients Traded from Team B to Team A", trade_info['B_to_A'])
        
# Handle structure changes and show info when no results exist  
if "allocation_results" not in st.session_state or st.session_state["allocation_results"] is None:
    # Check if structure changed (rows/columns added/removed via data editor)
    # Only update session state for structure changes, not value changes
    # This prevents the double-entry bug while still persisting structural changes
    if (current_table.shape != edited_phys.shape or 
        list(current_table.columns) != list(edited_phys.columns)):
        # Structure changed - update session state and rerun
        # This is necessary to persist row additions/deletions
        st.session_state["physician_table"] = edited_phys.copy()
        save_data(edited_phys)  # Persist changes
        st.rerun()
    
    # For value changes, don't update session state here
    # The widget's key maintains the state, and we'll update session state
    # when the button is clicked (handled in the if block above)
    st.markdown(
        '<div style="margin-top:1.5em;"></div>',
        unsafe_allow_html=True
    )
    st.info("Adjust the data above and click **Run Allocation** to see results.")

# Style tweaks for look & feel
st.markdown(
    """
    <style>
    .stDataFrame table {font-size: 1.08em;}
    .stButton>button {height: 2.7em; font-size:1.13em}
    .st-emotion-cache-ocqkz7 {background-color: #f6fbff}
    </style>
    """,
    unsafe_allow_html=True
)
