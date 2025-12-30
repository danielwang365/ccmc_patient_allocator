import streamlit as st
import pandas as pd
import os

# Files for persistent storage
DATA_FILE = "physician_data.csv"
YESTERDAY_FILE = "yesterday_physicians.csv"
SELECTED_FILE = "selected_physicians.csv"
MASTER_LIST_FILE = "master_physician_list.csv"
DEFAULT_PARAMS_FILE = "default_parameters.csv"
DEFAULT_PHYSICIANS_FILE = "default_physicians.csv"

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
    # Filter out NaN values and empty strings, convert to strings
    filtered_names = [str(name).strip() for name in physician_names 
                     if pd.notna(name) and str(name).strip()]
    df = pd.DataFrame({"Physician Name": filtered_names})
    df.to_csv(YESTERDAY_FILE, index=False)

def load_yesterday_physicians():
    """Loads yesterday's physician names from a file."""
    if os.path.exists(YESTERDAY_FILE):
        try:
            df = pd.read_csv(YESTERDAY_FILE)
            # Filter out NaN values and convert to strings, then filter out empty strings
            names = [str(name).strip() for name in df["Physician Name"].tolist() 
                    if pd.notna(name) and str(name).strip()]
            return names
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

def save_default_parameters(params_dict):
    """Saves default allocation parameters to a file."""
    df = pd.DataFrame([params_dict])
    df.to_csv(DEFAULT_PARAMS_FILE, index=False)

def load_default_parameters():
    """Loads default allocation parameters from a file."""
    if os.path.exists(DEFAULT_PARAMS_FILE):
        try:
            df = pd.read_csv(DEFAULT_PARAMS_FILE)
            return {
                "n_total_new_patients": int(df.iloc[0]["n_total_new_patients"]),
                "n_A_new_patients": int(df.iloc[0]["n_A_new_patients"]),
                "n_B_new_patients": int(df.iloc[0]["n_B_new_patients"]),
                "n_N_new_patients": int(df.iloc[0]["n_N_new_patients"]),
                "n_step_down_patients": int(df.iloc[0]["n_step_down_patients"]),
                "minimum_patients": int(df.iloc[0]["minimum_patients"]),
                "maximum_patients": int(df.iloc[0]["maximum_patients"]),
                "new_start_number": int(df.iloc[0]["new_start_number"]),
            }
        except Exception:
            pass
    return None

def save_default_physicians(df):
    """Saves default physician data to a file."""
    df.to_csv(DEFAULT_PHYSICIANS_FILE, index=False)

def load_default_physicians():
    """Loads default physician data from a file."""
    if os.path.exists(DEFAULT_PHYSICIANS_FILE):
        try:
            df = pd.read_csv(DEFAULT_PHYSICIANS_FILE)
            # Ensure boolean columns are correctly typed
            bool_cols = ["New Physician", "Buffer", "Working"]
            for col in bool_cols:
                if col in df.columns:
                    df[col] = df[col].astype(bool)
            # Handle Yesterday column
            if "Yesterday" in df.columns:
                df["Yesterday"] = df["Yesterday"].astype(str).replace("nan", "").replace("False", "").replace("True", "")
            return df
        except Exception:
            pass
    return None

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
        # IMPORTANT: Step-down patients do NOT count towards total_patients
        # They are tracked separately in step_down_patients
        if is_step_down:
            # Step-down patient: only increment step_down_patients, NOT total_patients
            self.step_down_patients += 1
        else:
            # Regular patient: increment total_patients
            self.total_patients += 1

    def remove_patient(self, is_step_down: bool = False):
        # IMPORTANT: Step-down patients do NOT count towards total_patients
        if is_step_down:
            # Step-down patient: only decrement step_down_patients, NOT total_patients
            if self.step_down_patients < 1:
                raise Exception("You don't have any step-down patients")
            self.step_down_patients -= 1
        else:
            # Regular patient: decrement total_patients
            if self.total_patients < 1:
                raise Exception("You don't have any patients")
            self.total_patients -= 1

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
    # DO NOT check total patient count - only check if they've already gained a step-down
    def can_take_step_down(physician):
        initial_sd = initial_stepdown_counts.get(physician.name, 0)
        gained_stepdown = physician.step_down_patients - initial_sd
        # Only check if they've already gained a step-down (gained_stepdown < 1)
        # DO NOT check total patients for step-down allocation
        return gained_stepdown < 1
    
    # First, allocate step down patients: Team B first, then Team A
    # IMPORTANT: Step-down patients do NOT count towards total new patient pools
    # They only reduce n_step_down_patients, NOT n_total_new_patients, n_A_new_patients, n_B_new_patients, or n_N_new_patients
    # Simple algorithm:
    # 1. Get all Team B physicians (working only)
    # 2. Sort by INITIAL StepDown count (lowest to highest) - use initial_stepdown_counts
    # 3. Assign one step-down patient to each in sorted order
    # DO NOT consider total patient count for step-down allocation
    
    # Filter to only working physicians (do NOT filter by can_take_patient for step-down)
    working_team_B = [p for p in team_B if p.is_working]
    working_team_A = [p for p in team_A if p.is_working]
    
    # DEBUG: Show initial stepdown counts
    print(f"\n=== STEP-DOWN ALLOCATION TRACE ===")
    print(f"Step 1: Captured initial_stepdown_counts:")
    for name, count in sorted(initial_stepdown_counts.items()):
        if any(p.name == name and p.team == 'B' for p in working_team_B):
            print(f"  {name}: {count}")
    
    print(f"\nStep 2: Team B working physicians: {[p.name for p in working_team_B]}")
    
    # Sort Team B physicians by INITIAL StepDown count (lowest to highest)
    # Use initial_stepdown_counts to get the original value before any allocation
    team_B_sorted = sorted(working_team_B, key=lambda x: initial_stepdown_counts.get(x.name, x.step_down_patients))
    
    print(f"\nStep 3: Team B sorted by INITIAL StepDown (lowest to highest):")
    for p in team_B_sorted:
        initial_sd = initial_stepdown_counts.get(p.name, p.step_down_patients)
        current_sd = p.step_down_patients
        print(f"  {p.name}: initial={initial_sd}, current={current_sd}")
    
    print(f"\nStep 4: Distributing {n_step_down_patients} step-down patients...")
    # Distribute step-down patients to Team B physicians in sorted order
    for physician in team_B_sorted:
        if n_step_down_patients <= 0:
            print(f"  Pool exhausted. Remaining: {n_step_down_patients}")
            break
        # Only give if they haven't already gained a step-down (check gained, not total)
        initial_sd = initial_stepdown_counts.get(physician.name, 0)
        current_sd = physician.step_down_patients
        gained = current_sd - initial_sd
        can_take = can_take_step_down(physician)
        print(f"  Processing {physician.name}: initial={initial_sd}, current={current_sd}, gained={gained}, can_take={can_take}, pool={n_step_down_patients}")
        if can_take:
            physician.add_patient(is_step_down=True)
            n_step_down_patients -= 1
            print(f"    ✓ GAVE step-down to {physician.name}. New StepDown={physician.step_down_patients}, pool={n_step_down_patients}")
        else:
            print(f"    ✗ SKIPPED {physician.name} (cannot take step-down)")
    
    # If there are still step-down patients remaining, then distribute to Team A
    if n_step_down_patients > 0:
        print(f"\nStep 5: Remaining step-down patients: {n_step_down_patients}, distributing to Team A...")
        # Sort Team A physicians by INITIAL StepDown count (lowest to highest)
        # Use initial_stepdown_counts to get the original value before any allocation
        team_A_sorted = sorted(working_team_A, key=lambda x: initial_stepdown_counts.get(x.name, x.step_down_patients))
        
        print(f"Team A sorted by INITIAL StepDown (lowest to highest):")
        for p in team_A_sorted:
            initial_sd = initial_stepdown_counts.get(p.name, p.step_down_patients)
            current_sd = p.step_down_patients
            print(f"  {p.name}: initial={initial_sd}, current={current_sd}")
        
        # Distribute step-down patients to Team A physicians in sorted order
        for physician in team_A_sorted:
            if n_step_down_patients <= 0:
                print(f"  Pool exhausted. Remaining: {n_step_down_patients}")
                break
            # Only give if they haven't already gained a step-down (check gained, not total)
            initial_sd = initial_stepdown_counts.get(physician.name, 0)
            current_sd = physician.step_down_patients
            gained = current_sd - initial_sd
            can_take = can_take_step_down(physician)
            print(f"  Processing {physician.name}: initial={initial_sd}, current={current_sd}, gained={gained}, can_take={can_take}, pool={n_step_down_patients}")
            if can_take:
                physician.add_patient(is_step_down=True)
                n_step_down_patients -= 1
                print(f"    ✓ GAVE step-down to {physician.name}. New StepDown={physician.step_down_patients}, pool={n_step_down_patients}")
            else:
                print(f"    ✗ SKIPPED {physician.name} (cannot take step-down)")
    
    print(f"\n=== END STEP-DOWN ALLOCATION TRACE ===\n")
    
    # Second, fix physicians who are more than 1 less than the minimum value
    # (i.e., if minimum is 10, fix physicians with 8 or fewer patients)
    # EXCLUDE new physicians - they will be handled in the next phase
    threshold = minimum_patients - 2
    for physician in physicians:
        # Skip new physicians - they get exactly new_start_number in the next phase
        if physician.is_new:
            continue
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

    # Third, fill up new physicians to EXACTLY new_start_number
    # IMPORTANT: New physicians get exactly new_start_number patients (if below it) or 0 (if already at/above it)
    # They do NOT participate in the general distribution cycle
    # Priority: own team pool first, then other pools if needed
    for physician in physicians:
        if physician.is_new:
            # Calculate how many patients are needed to reach new_start_number
            needed = new_start_number - physician.total_patients
            # If already at or above new_start_number, needed will be <= 0, so skip allocation
            # This ensures new physicians who are already at new_start_number get 0 patients
            if needed <= 0:
                continue  # Skip - already at or above new_start_number, should get 0
            # Allocate exactly the number needed to reach new_start_number
            while needed > 0 and can_take_patient(physician):
                allocated = False
                
                # First, try to allocate from physician's own team pool
                if physician.team == 'A' and n_A_new_patients > 0:
                    physician.add_patient()
                    n_A_new_patients -= 1
                    n_total_new_patients -= 1
                    needed -= 1
                    allocated = True
                elif physician.team == 'B' and n_B_new_patients > 0:
                    physician.add_patient()
                    n_B_new_patients -= 1
                    n_total_new_patients -= 1
                    needed -= 1
                    allocated = True
                elif physician.team == 'N' and n_N_new_patients > 0:
                    physician.add_patient()
                    n_N_new_patients -= 1
                    n_total_new_patients -= 1
                    needed -= 1
                    allocated = True
                
                # If own team pool is exhausted, try other pools
                if not allocated:
                    if n_A_new_patients > 0:
                        physician.add_patient()
                        n_A_new_patients -= 1
                        n_total_new_patients -= 1
                        needed -= 1
                        allocated = True
                    elif n_B_new_patients > 0:
                        physician.add_patient()
                        n_B_new_patients -= 1
                        n_total_new_patients -= 1
                        needed -= 1
                        allocated = True
                    elif n_N_new_patients > 0:
                        physician.add_patient()
                        n_N_new_patients -= 1
                        n_total_new_patients -= 1
                        needed -= 1
                        allocated = True
                
                # If no pools have patients available, break (can't allocate more)
                if not allocated:
                    break

    # Fourth, distribute remaining patients with pattern-based allocation
    # Team N physicians get priority from Team N Pool first
    # Then calculate distribution pattern (e.g., for 47 patients: 5 get 3, 16 get 2)
    # Physicians with fewer patients get higher numbers
    
    # Get all non-new physicians for distribution
    # CRITICAL: New physicians must be completely excluded from general distribution
    # They only get patients to reach new_start_number (or 0 if already at/above it)
    non_new_physicians = [p for p in physicians if not p.is_new and can_take_patient(p)]
    
    # Double-check: Ensure no new physicians are included
    non_new_physicians = [p for p in non_new_physicians if not p.is_new]
    
    # Calculate current gains so far (only for non-new physicians)
    current_gains = {p.name: p.total_patients - initial_counts[p.name] for p in non_new_physicians}
    
    # FIRST: Allocate Team N Pool to Team N physicians (priority)
    team_N_non_new = [p for p in team_N if not p.is_new and can_take_patient(p)]
    if team_N_non_new and n_N_new_patients > 0:
        # Sort Team N physicians by current patient count (lowest first)
        team_N_sorted = sorted(team_N_non_new, key=lambda x: x.total_patients)
        
        # Distribute Team N Pool to Team N physicians
        for physician in team_N_sorted:
            if n_N_new_patients <= 0:
                break
            if can_take_patient(physician):
                physician.add_patient()
                n_N_new_patients -= 1
                n_total_new_patients -= 1
                current_gains[physician.name] = current_gains.get(physician.name, 0) + 1
    
    # If Team N Pool is exhausted but Team N physicians still need patients,
    # they can get from other pools in the general distribution below
    
    # Recalculate current gains right before final distribution to ensure accuracy
    # This accounts for any allocations made in earlier phases
    current_gains = {p.name: p.total_patients - initial_counts[p.name] for p in non_new_physicians}
    
    # Calculate remaining patients across all pools
    remaining_patients = n_A_new_patients + n_B_new_patients + n_N_new_patients
    
    # Store for verification
    initial_remaining = remaining_patients
    
    if remaining_patients > 0 and non_new_physicians:
        # New algorithm: Ensure gained patients differ by at most 1
        # If physician number < patient number: assign +1 to all physicians
        # If not: assign +1 to physicians with lowest patients
        # Maximum difference in gained patients is 1
        num_physicians = len(non_new_physicians)
        
        if num_physicians > 0:
            # Sort physicians by INITIAL patient count (lowest first) - determines who gets patients first
            sorted_physicians = sorted(non_new_physicians, key=lambda x: (
                initial_counts.get(x.name, x.total_patients),  # Sort by INITIAL total patients (lowest first)
                x.total_patients  # Then by current total patients as tiebreaker
            ))
            
            # NEW ALGORITHM:
            # If num_physicians > remaining_patients: Give +1 to each physician in cycles until remaining = 0
            # If num_physicians <= remaining_patients: Give +1 to all physicians, then continue with lowest totals
            
            # Initialize additional gains to 0 for all
            target_additional_gains = {p.name: 0 for p in sorted_physicians}
            
            patients_to_distribute = remaining_patients
            
            if num_physicians > remaining_patients:
                # Fewer patients than physicians: Give +1 to each physician in cycles (round-robin)
                # Continue until all patients are distributed
                while patients_to_distribute > 0:
                    # Sort by: current additional gain (lowest first), then initial total patients (lowest first)
                    sorted_by_additional = sorted(sorted_physicians, key=lambda x: (
                        target_additional_gains.get(x.name, 0),  # Lowest additional gain first
                        initial_counts.get(x.name, x.total_patients),  # Then lowest initial totals
                        x.total_patients  # Then current totals
                    ))
                    
                    # Give +1 to up to 'patients_to_distribute' physicians in this cycle
                    for physician in sorted_by_additional:
                        if patients_to_distribute <= 0:
                            break
                        # Give this physician +1 additional
                        target_additional_gains[physician.name] = target_additional_gains.get(physician.name, 0) + 1
                        patients_to_distribute -= 1
            else:
                # More or equal patients than physicians: Give +1 to all physicians first
                for physician in sorted_physicians:
                    if patients_to_distribute <= 0:
                        break
                    target_additional_gains[physician.name] = target_additional_gains.get(physician.name, 0) + 1
                    patients_to_distribute -= 1
                
                # Then continue giving +1 to physicians with lowest totals until remaining = 0
                while patients_to_distribute > 0:
                    # Sort by: current additional gain (lowest first), then initial total patients (lowest first)
                    sorted_by_additional = sorted(sorted_physicians, key=lambda x: (
                        target_additional_gains.get(x.name, 0),  # Lowest additional gain first
                        initial_counts.get(x.name, x.total_patients),  # Then lowest initial totals
                        x.total_patients  # Then current totals
                    ))
                    
                    # Give +1 to physicians with lowest totals
                    for physician in sorted_by_additional:
                        if patients_to_distribute <= 0:
                            break
                        # Give this physician +1 additional
                        target_additional_gains[physician.name] = target_additional_gains.get(physician.name, 0) + 1
                        patients_to_distribute -= 1
            
            # Calculate target total gains (current + additional) for allocation
            # BUT ensure all FINAL total gains differ by at most 1
            # Calculate based on: sum of current_gains + remaining_patients
            total_current_gains_sum = sum(current_gains.get(p.name, 0) for p in sorted_physicians)
            total_final_gains_needed = total_current_gains_sum + remaining_patients
            
            # Calculate base and remainder for final gains
            base_final_gain = total_final_gains_needed // num_physicians
            remainder_final = total_final_gains_needed % num_physicians
            
            # Assign final gains - those with lowest initial totals get the higher amount
            target_total_gains = {}
            for i, physician in enumerate(sorted_physicians):
                if i < remainder_final:
                    # First 'remainder_final' physicians (lowest INITIAL totals) get base_final_gain + 1
                    target_total_gains[physician.name] = base_final_gain + 1
                else:
                    # Rest get base_final_gain
                    target_total_gains[physician.name] = base_final_gain
            
            # Recalculate target_additional_gains based on normalized targets
            for physician in sorted_physicians:
                current_gain = current_gains.get(physician.name, 0)
                target_total = target_total_gains.get(physician.name, 0)
                target_additional_gains[physician.name] = max(0, target_total - current_gain)
            
            # Now distribute patients according to targets, respecting team pools
            # Allocate one patient at a time in rounds until ALL targets are met or pools exhausted
            # CRITICAL: Never exceed target_total_gain - this ensures all gains differ by at most 1
            # Continue allocating until all physicians reach their targets or pools are exhausted
            remaining_after_targets = n_A_new_patients + n_B_new_patients + n_N_new_patients
            max_iterations = remaining_after_targets * 3  # Safety limit (increased to ensure completion)
            iteration = 0
            
            # Continue until all targets are met or no more patients available
            while remaining_after_targets > 0 and iteration < max_iterations:
                iteration += 1
                made_progress = False
                
                for physician in sorted_physicians:
                    # CRITICAL: Skip new physicians - they should never be in sorted_physicians, but double-check
                    if physician.is_new:
                        continue
                    
                    target_total_gain = target_total_gains.get(physician.name, 0)
                    # Always calculate current gain from actual physician state, not dictionary
                    actual_current_gain = physician.total_patients - initial_counts[physician.name]
                    needed = target_total_gain - actual_current_gain
                    
                    # CRITICAL: Don't exceed target - this ensures gains differ by at most 1
                    if needed <= 0 or not can_take_patient(physician):
                        continue
                    
                    # Try to allocate 1 patient from physician's own team pool first
                    if physician.team == 'A' and n_A_new_patients > 0:
                        if can_take_patient(physician) and actual_current_gain < target_total_gain:
                            physician.add_patient()
                            n_A_new_patients -= 1
                            n_total_new_patients -= 1
                            remaining_after_targets -= 1
                            current_gains[physician.name] = physician.total_patients - initial_counts[physician.name]
                            made_progress = True
                            continue  # Move to next physician
                    elif physician.team == 'B' and n_B_new_patients > 0:
                        if can_take_patient(physician) and actual_current_gain < target_total_gain:
                            physician.add_patient()
                            n_B_new_patients -= 1
                            n_total_new_patients -= 1
                            remaining_after_targets -= 1
                            current_gains[physician.name] = physician.total_patients - initial_counts[physician.name]
                            made_progress = True
                            continue  # Move to next physician
                    elif physician.team == 'N' and n_N_new_patients > 0:
                        if can_take_patient(physician) and actual_current_gain < target_total_gain:
                            physician.add_patient()
                            n_N_new_patients -= 1
                            n_total_new_patients -= 1
                            remaining_after_targets -= 1
                            current_gains[physician.name] = physician.total_patients - initial_counts[physician.name]
                            made_progress = True
                            continue  # Move to next physician
                    
                    # If own team pool exhausted, try other pools to reach target
                    # Recalculate actual gain in case it changed
                    actual_current_gain = physician.total_patients - initial_counts[physician.name]
                    if actual_current_gain < target_total_gain and can_take_patient(physician):
                        # Try other pools if own team is exhausted or if buffer
                        can_use_other_pools = (physician.is_buffer or 
                                             (physician.team == 'A' and n_A_new_patients == 0) or
                                             (physician.team == 'B' and n_B_new_patients == 0) or
                                             (physician.team == 'N' and n_N_new_patients == 0))
                        
                        if can_use_other_pools:
                            # Try all pools in order to reach target
                            if n_A_new_patients > 0:
                                actual_current_gain = physician.total_patients - initial_counts[physician.name]
                                if can_take_patient(physician) and actual_current_gain < target_total_gain:
                                    physician.add_patient()
                                    n_A_new_patients -= 1
                                    n_total_new_patients -= 1
                                    remaining_after_targets -= 1
                                    current_gains[physician.name] = physician.total_patients - initial_counts[physician.name]
                                    made_progress = True
                                    continue
                            if n_B_new_patients > 0:
                                actual_current_gain = physician.total_patients - initial_counts[physician.name]
                                if can_take_patient(physician) and actual_current_gain < target_total_gain:
                                    physician.add_patient()
                                    n_B_new_patients -= 1
                                    n_total_new_patients -= 1
                                    remaining_after_targets -= 1
                                    current_gains[physician.name] = physician.total_patients - initial_counts[physician.name]
                                    made_progress = True
                                    continue
                            if n_N_new_patients > 0:
                                actual_current_gain = physician.total_patients - initial_counts[physician.name]
                                if can_take_patient(physician) and actual_current_gain < target_total_gain:
                                    physician.add_patient()
                                    n_N_new_patients -= 1
                                    n_total_new_patients -= 1
                                    remaining_after_targets -= 1
                                    current_gains[physician.name] = physician.total_patients - initial_counts[physician.name]
                                    made_progress = True
                                    continue
                
                # If no progress was made, break to avoid infinite loop
                if not made_progress:
                    break
                
                # Update remaining count
                remaining_after_targets = n_A_new_patients + n_B_new_patients + n_N_new_patients
            
            # Final pass: Distribute any remaining patients to physicians who haven't reached their target
            # This ensures we use all available patients while respecting targets
            remaining_final = n_A_new_patients + n_B_new_patients + n_N_new_patients
            if remaining_final > 0:
                # Sort by how far they are from target (those furthest below target get priority)
                sorted_by_need = sorted(sorted_physicians, key=lambda x: (
                    target_total_gains.get(x.name, 0) - (x.total_patients - initial_counts[x.name]),  # How many below target
                    x.total_patients  # Then by total patients (lowest first)
                ), reverse=True)  # Reverse so those furthest below target come first
                
                for physician in sorted_by_need:
                    # CRITICAL: Skip new physicians - they should never be in sorted_physicians, but double-check
                    if physician.is_new:
                        continue
                    
                    if remaining_final <= 0:
                        break
                    target = target_total_gains.get(physician.name, 0)
                    actual_gain = physician.total_patients - initial_counts[physician.name]
                    needed = target - actual_gain
                    
                    if needed <= 0 or not can_take_patient(physician):
                        continue
                    
                    # Try any available pool
                    if n_A_new_patients > 0 and actual_gain < target:
                        physician.add_patient()
                        n_A_new_patients -= 1
                        n_total_new_patients -= 1
                        remaining_final -= 1
                    elif n_B_new_patients > 0 and actual_gain < target:
                        physician.add_patient()
                        n_B_new_patients -= 1
                        n_total_new_patients -= 1
                        remaining_final -= 1
                    elif n_N_new_patients > 0 and actual_gain < target:
                        physician.add_patient()
                        n_N_new_patients -= 1
                        n_total_new_patients -= 1
                        remaining_final -= 1
                
                # Safety check: Ensure no physician has exceeded their target
                for physician in sorted_physicians:
                    target = target_total_gains.get(physician.name, 0)
                    actual_gain = physician.total_patients - initial_counts[physician.name]
                    if actual_gain > target:
                        # This shouldn't happen, but if it does, we've found a bug
                        # In production, we might want to log this or handle it differently
                        pass  # For now, just note it - the checks above should prevent this
    
    # Final verification: Ensure new physicians who started at/above new_start_number have gained 0 patients
    # This is a safety check to catch any bugs where new physicians incorrectly received patients
    for physician in physicians:
        if physician.is_new:
            initial_total = initial_counts.get(physician.name, physician.total_patients)
            current_total = physician.total_patients
            gained = current_total - initial_total
            
            # If physician was already at or above new_start_number initially, they should have gained 0
            if initial_total >= new_start_number:
                if gained > 0:
                    # BUG DETECTED: New physician at new_start_number got patients they shouldn't have
                    # Reset them to their initial total (they should have gained 0)
                    excess = gained
                    for _ in range(excess):
                        physician.remove_patient()
                    # Force their total to be exactly what it should be (no gain)
                    physician.set_total_patients(initial_total)
                # If gained == 0, that's correct - they should get 0 patients
            # If initial_total < new_start_number, they should have gained to reach new_start_number
            # (This is handled in the "Third" phase above)

# --- Streamlit App Begins Here ---
st.set_page_config(page_title="Patient Allocator", page_icon="🩺", layout="wide")
st.title("🩺 Physician Patient Allocation")
st.write("Use the sidebar to set patient pools and parameters. Edit physician information in the table below, then click **Run Allocation** to distribute patients according to the logic.")

# Load default parameters if available
default_params = load_default_parameters()
default_param_values = {
    "n_total_new_patients": default_params["n_total_new_patients"] if default_params else 20,
    "n_A_new_patients": default_params["n_A_new_patients"] if default_params else 10,
    "n_B_new_patients": default_params["n_B_new_patients"] if default_params else 8,
    "n_N_new_patients": default_params["n_N_new_patients"] if default_params else 2,
    "n_step_down_patients": default_params["n_step_down_patients"] if default_params else 0,
    "minimum_patients": default_params["minimum_patients"] if default_params else 10,
    "maximum_patients": default_params["maximum_patients"] if default_params else 20,
    "new_start_number": default_params["new_start_number"] if default_params else 5,
}

# Sidebar inputs
with st.sidebar:
    st.header("Allocation Parameters")
    n_total_new_patients = st.number_input("Total New Patients", min_value=0, value=default_param_values["n_total_new_patients"], step=1)
    n_A_new_patients = st.number_input("Team A Pool", min_value=0, value=default_param_values["n_A_new_patients"], step=1)
    n_B_new_patients = st.number_input("Team B Pool", min_value=0, value=default_param_values["n_B_new_patients"], step=1)
    n_N_new_patients = st.number_input("Team N Pool", min_value=0, value=default_param_values["n_N_new_patients"], step=1)
    n_step_down_patients = st.number_input("Total New Step Down Patients", min_value=0, value=default_param_values["n_step_down_patients"], step=1)
    minimum_patients = st.number_input("Minimum Patients", min_value=0, value=default_param_values["minimum_patients"], step=1)
    maximum_patients = st.number_input("Maximum Patients", min_value=1, value=default_param_values["maximum_patients"], step=1)
    new_start_number = st.number_input("New Start Number", min_value=0, value=default_param_values["new_start_number"], step=1)
    st.markdown("---")
    st.info("Adjust team patient pools, step down patients, min/max patient requirements, and the number of initial patients for new physicians.")
    
    # Add button to save current setup as default
    st.markdown("---")
    st.markdown("### 💾 Save Current Setup")
    if st.button("Save as Default Demo", use_container_width=True, type="secondary"):
        # Save current parameters
        params_dict = {
            "n_total_new_patients": int(n_total_new_patients),
            "n_A_new_patients": int(n_A_new_patients),
            "n_B_new_patients": int(n_B_new_patients),
            "n_N_new_patients": int(n_N_new_patients),
            "n_step_down_patients": int(n_step_down_patients),
            "minimum_patients": int(minimum_patients),
            "maximum_patients": int(maximum_patients),
            "new_start_number": int(new_start_number),
        }
        save_default_parameters(params_dict)
        
        # Save current physician table
        if "physician_table" in st.session_state and not st.session_state["physician_table"].empty:
            save_default_physicians(st.session_state["physician_table"])
            st.success("✅ Current setup saved as default demo!")
        else:
            st.warning("⚠️ No physician data to save. Please add physicians first.")
        st.rerun()

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

# Default rows with specific physician data
DEFAULT_ROWS = [
    {"Yesterday": "Abadi", "Physician Name": "Abadi", "Team": "A", "New Physician": False, "Buffer": False, "Working": True, "Total Patients": 9, "StepDown": 1, "Out of floor": 0, "Traded": 0},
    {"Yesterday": "Adhiakha", "Physician Name": "Adhiakha", "Team": "B", "New Physician": False, "Buffer": False, "Working": True, "Total Patients": 10, "StepDown": 2, "Out of floor": 0, "Traded": 0},
    {"Yesterday": "", "Physician Name": "Ahir", "Team": "A", "New Physician": False, "Buffer": False, "Working": True, "Total Patients": 10, "StepDown": 3, "Out of floor": 0, "Traded": 0},
    {"Yesterday": "Ali", "Physician Name": "Ali", "Team": "B", "New Physician": False, "Buffer": False, "Working": True, "Total Patients": 6, "StepDown": 1, "Out of floor": 0, "Traded": 0},
    {"Yesterday": "Arora", "Physician Name": "Arora", "Team": "A", "New Physician": False, "Buffer": False, "Working": True, "Total Patients": 12, "StepDown": 3, "Out of floor": 0, "Traded": 0},
    {"Yesterday": "Attrabala", "Physician Name": "Attrabala", "Team": "B", "New Physician": False, "Buffer": False, "Working": True, "Total Patients": 9, "StepDown": 1, "Out of floor": 0, "Traded": 0},
    {"Yesterday": "Attrapisi", "Physician Name": "Attrapisi", "Team": "A", "New Physician": False, "Buffer": False, "Working": True, "Total Patients": 9, "StepDown": 3, "Out of floor": 0, "Traded": 0},
    {"Yesterday": "Aung", "Physician Name": "Aung", "Team": "B", "New Physician": False, "Buffer": False, "Working": True, "Total Patients": 10, "StepDown": 0, "Out of floor": 0, "Traded": 0},
    {"Yesterday": "Batlawala", "Physician Name": "Batlawala", "Team": "A", "New Physician": False, "Buffer": False, "Working": True, "Total Patients": 9, "StepDown": 2, "Out of floor": 0, "Traded": 0},
    {"Yesterday": "Batth", "Physician Name": "Batth", "Team": "B", "New Physician": False, "Buffer": False, "Working": True, "Total Patients": 9, "StepDown": 2, "Out of floor": 0, "Traded": 0},
    {"Yesterday": "Bhogireddy", "Physician Name": "Bhogireddy", "Team": "A", "New Physician": False, "Buffer": False, "Working": True, "Total Patients": 10, "StepDown": 2, "Out of floor": 0, "Traded": 0},
]

# Try to load default physicians first, otherwise use hardcoded defaults
default_physicians_df = load_default_physicians()
if default_physicians_df is not None and not default_physicians_df.empty:
    DEFAULT_ROWS = default_physicians_df.to_dict('records')

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

# Initialize team assignments for master list physicians
if "master_team_assignments" not in st.session_state:
    st.session_state["master_team_assignments"] = {}
    # If we have a current table, initialize team assignments from it
    if "physician_table" in st.session_state and not st.session_state["physician_table"].empty:
        for _, row in st.session_state["physician_table"].iterrows():
            name = str(row.get("Physician Name", ""))
            team = str(row.get("Team", "A"))
            if name and name in MASTER_PHYSICIAN_LIST:
                st.session_state["master_team_assignments"][name] = team if team in ["A", "B", "N"] else "A"

# Initialize checkbox reset counter
if "checkbox_reset_counter" not in st.session_state:
    st.session_state["checkbox_reset_counter"] = 0

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
        # Ensure all values are strings for join operation
        yesterday_str = [str(name) for name in yesterday_physicians if name]
        st.markdown(f"**Yesterday's Physicians ({len(yesterday_str)}):** {', '.join(yesterday_str)}")
    
    # Create checkboxes for each doctor in the master list
    st.markdown("**Select Today's Physicians:**")
    
    # Organize checkboxes in columns for better layout (column-wise, not row-wise)
    # Each column should read alphabetically from top to bottom
    num_cols = 3
    cols = st.columns(num_cols)
    
    # Calculate number of items per column (ceiling division)
    items_per_col = (len(MASTER_PHYSICIAN_LIST) + num_cols - 1) // num_cols
    
    # Split the alphabetically sorted list into columns
    # Column 0 gets first items_per_col items, Column 1 gets next items_per_col, etc.
    column_lists = []
    for col_idx in range(num_cols):
        start_idx = col_idx * items_per_col
        end_idx = min(start_idx + items_per_col, len(MASTER_PHYSICIAN_LIST))
        column_lists.append(MASTER_PHYSICIAN_LIST[start_idx:end_idx])
    
    selected_doctors = []
    # Display checkboxes column by column (top to bottom in each column)
    for col_idx in range(num_cols):
        with cols[col_idx]:
            for doctor_name in column_lists[col_idx]:
                # Create a container with checkbox and team selector side by side
                checkbox_col, team_col = st.columns([3, 1])
                
                with checkbox_col:
                    # Check if this doctor was selected previously or is in yesterday's list
                    # Use reset counter in key to force checkbox reset when "Uncheck All" is clicked
                    reset_counter = st.session_state.get("checkbox_reset_counter", 0)
                    is_checked = doctor_name in st.session_state["selected_physicians"]
                    checkbox_value = st.checkbox(doctor_name, value=is_checked, key=f"doctor_checkbox_{doctor_name}_{reset_counter}")
                    if checkbox_value:
                        selected_doctors.append(doctor_name)
                
                with team_col:
                    # Get current team assignment or default to "A"
                    current_team = st.session_state["master_team_assignments"].get(doctor_name, "A")
                    team_index = ["A", "B", "N"].index(current_team) if current_team in ["A", "B", "N"] else 0
                    selected_team = st.selectbox(
                        "Team",
                        options=["A", "B", "N"],
                        index=team_index,
                        key=f"team_select_{doctor_name}",
                        label_visibility="collapsed"
                    )
                    # Update session state with team assignment
                    st.session_state["master_team_assignments"][doctor_name] = selected_team
    
    # Update session state with selected doctors
    st.session_state["selected_physicians"] = selected_doctors
    
    # Add buttons for clearing selections and generating table
    button_col1, button_col2 = st.columns([1, 1])
    with button_col1:
        if st.button("Uncheck All", use_container_width=True):
            st.session_state["selected_physicians"] = []
            # Increment reset counter to force all checkboxes to reset
            st.session_state["checkbox_reset_counter"] = st.session_state.get("checkbox_reset_counter", 0) + 1
            st.rerun()
    with button_col2:
        generate_btn = st.button("Generate Table from Selection", type="primary", use_container_width=True)
    
    if generate_btn:
        # Get selected doctors again in case they changed
        selected_doctors = st.session_state.get("selected_physicians", [])
        if selected_doctors:
            # Save current physicians as yesterday's before generating new table
            if "physician_table" in st.session_state:
                # Filter out NaN values and convert to strings
                current_physicians = [str(name).strip() for name in st.session_state["physician_table"]["Physician Name"].tolist() 
                                    if pd.notna(name) and str(name).strip()]
            else:
                current_physicians = []
            if current_physicians:
                save_yesterday_physicians(current_physicians)
            
            # Save selected physicians
            save_selected_physicians(selected_doctors)
            
            new_rows = []
            for i, name in enumerate(selected_doctors):
                # Use team assignment from master list, or default to "A" if not set
                team = st.session_state["master_team_assignments"].get(name, "A")
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
            # Ensure all values are strings for join operation
            yesterday_str = [str(name) for name in yesterday_physicians if name]
            st.markdown(f"**Yesterday's Physicians ({len(yesterday_str)}):**")
            st.text(", ".join(yesterday_str))
        else:
            st.markdown("**Yesterday's Physicians:** *No data available*")
    with info_col2:
        if current_table is not None and not current_table.empty:
            # Filter out NaN values and convert to strings
            today_physicians = [str(name).strip() for name in current_table["Physician Name"].tolist() 
                              if pd.notna(name) and str(name).strip()]
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
    # Filter out NaN values and convert to strings
    current_physician_names = [str(name).strip() for name in edited_phys["Physician Name"].tolist() 
                              if pd.notna(name) and str(name).strip()]
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
            "Original Total Patients": initial_counts[p.name],
            "Total Patients": p.total_patients,
            "Original StepDown": initial_step_down_counts[p.name],
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
    st.session_state["total_new_patients_input"] = int(n_total_new_patients)  # Store for display
    
    # Calculate and store allocation details for debugging
    total_gained_calc = sum(p.total_patients - initial_counts[p.name] for p in working_physicians)
    gain_distribution = {}
    for p in working_physicians:
        gain = p.total_patients - initial_counts[p.name]
        gain_distribution[gain] = gain_distribution.get(gain, 0) + 1
    st.session_state["allocation_debug"] = {
        "total_gained": total_gained_calc,
        "expected_total": int(n_total_new_patients),
        "gain_distribution": gain_distribution
    }
    
    # Calculate team totals
    team_a_total = sum(p.total_patients for p in working_physicians if p.team == 'A')
    team_b_total = sum(p.total_patients for p in working_physicians if p.team == 'B')
    team_n_total = sum(p.total_patients for p in working_physicians if p.team == 'N')
    total_traded = sum(p.traded_patients for p in working_physicians)
    
    # Calculate total census: Team A + Team B + Team N + Total Traded patients
    total_census = team_a_total + team_b_total + team_n_total + total_traded
    
    # Calculate team gains
    team_a_gained = sum(p.total_patients - initial_counts[p.name] for p in working_physicians if p.team == 'A')
    team_b_gained = sum(p.total_patients - initial_counts[p.name] for p in working_physicians if p.team == 'B')
    team_n_gained = sum(p.total_patients - initial_counts[p.name] for p in working_physicians if p.team == 'N')
    
    # Calculate total gained: Team A + Team B + Team N + Total Traded patients
    total_gained = team_a_gained + team_b_gained + team_n_gained + total_traded
    
    st.session_state["allocation_summary"] = {
        "team_a_total": team_a_total,
        "team_b_total": team_b_total,
        "team_n_total": team_n_total,
        "team_a_gained": team_a_gained,
        "team_b_gained": team_b_gained,
        "team_n_gained": team_n_gained,
        "team_a_stepdown_gained": sum(p.step_down_patients - initial_step_down_counts[p.name] for p in working_physicians if p.team == 'A'),
        "team_b_stepdown_gained": sum(p.step_down_patients - initial_step_down_counts[p.name] for p in working_physicians if p.team == 'B'),
        "team_a_traded": sum(p.traded_patients for p in working_physicians if p.team == 'A'),
        "team_b_traded": sum(p.traded_patients for p in working_physicians if p.team == 'B'),
        "total_traded": total_traded,
        "total_census": total_census,
        "total_gained": total_gained,
    }

# Display results if they exist in session state
if "allocation_results" in st.session_state and st.session_state["allocation_results"] is not None:
    st.markdown("### :clipboard: Results")
    
    # Explain how Total Patients is calculated
    st.info("ℹ️ **Total Patients Calculation:** Total Patients = Original Total Patients + Regular Patients Gained. "
            "Step-down patients are tracked separately and do NOT count towards Total Patients. "
            "**Total Census** = Team A + Team B + Team N + Total Traded patients. "
            "**Total Patients Gained** = Team A Gained + Team B Gained + Team N Gained + Total Traded patients.")
    
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
    
    # Make the results editable using st.data_editor
    edited_results = st.data_editor(
        display_df,
        column_config={
            "Physician Name": st.column_config.TextColumn("Physician Name", disabled=True),
            "Team": st.column_config.TextColumn("Team", disabled=True),
            "New Physician": st.column_config.CheckboxColumn("New Physician", disabled=True),
            "Buffer": st.column_config.CheckboxColumn("Buffer", disabled=True),
            "Original Total Patients": st.column_config.NumberColumn("Original Total Patients", min_value=0, step=1, format="%d", disabled=True),
            "Total Patients": st.column_config.NumberColumn("Total Patients", min_value=0, step=1, format="%d"),
            "Original StepDown": st.column_config.NumberColumn("Original StepDown", min_value=0, step=1, format="%d", disabled=True),
            "StepDown": st.column_config.NumberColumn("StepDown", min_value=0, step=1, format="%d"),
            "Out of floor": st.column_config.NumberColumn("Out of floor", min_value=0, step=1, format="%d"),
            "Traded": st.column_config.NumberColumn("Traded", min_value=0, step=1, format="%d"),
            "Gained": st.column_config.NumberColumn("Gained", min_value=0, step=1, format="%d", disabled=True),
            "Gained StepDown": st.column_config.NumberColumn("Gained StepDown", min_value=0, step=1, format="%d", disabled=True),
            "Gained + Traded": st.column_config.NumberColumn("Gained + Traded", min_value=0, step=1, format="%d", disabled=True),
        },
        hide_index=True,
        use_container_width=True,
        key="results_editor",
        num_rows="fixed"
    )
    
    # Update session state with edited results
    if not edited_results.equals(display_df):
        st.session_state["allocation_results"] = edited_results.copy()
    
    # Calculate and display total gained patients and distribution
    if "allocation_results" in st.session_state and st.session_state["allocation_results"] is not None:
        total_gained = display_df["Gained"].sum()
        gain_counts = display_df["Gained"].value_counts().sort_index()
        expected_total = st.session_state.get("total_new_patients_input", 0)
        num_physicians_shown = len(display_df)
        
        st.markdown("### 📈 Gain Distribution Analysis")
        col_analysis1, col_analysis2 = st.columns(2)
        with col_analysis1:
            st.metric("Total Patients Gained (Sum)", int(total_gained))
            st.metric("Expected Total (Total New Patients)", int(expected_total))
            st.metric("Number of Physicians", int(num_physicians_shown))
            if total_gained != expected_total:
                st.error(f"⚠️ Mismatch! Gained ({int(total_gained)}) ≠ Expected ({int(expected_total)})")
            else:
                st.success("✅ Total gained matches expected!")
        with col_analysis2:
            st.markdown("**Distribution by Gain Amount:**")
            for gain_amount in sorted(gain_counts.index):
                count = int(gain_counts[gain_amount])
                st.markdown(f"- **{count}** physician(s) gained **{int(gain_amount)}** patient(s)")
            
            # Show expected distribution calculation
            if expected_total > 0 and num_physicians_shown > 0:
                st.markdown("---")
                st.markdown("**Expected Distribution:**")
                base_expected = expected_total // num_physicians_shown
                remainder_expected = expected_total % num_physicians_shown
                st.markdown(f"- Base: {base_expected} patients per physician")
                st.markdown(f"- Remainder: {remainder_expected} physicians should get {base_expected + 1}")
                st.markdown(f"- Rest: {num_physicians_shown - remainder_expected} physicians should get {base_expected}")
        
        # Show min and max gains
        min_gain = int(display_df["Gained"].min())
        max_gain = int(display_df["Gained"].max())
        gain_diff = max_gain - min_gain
        st.markdown(f"**Gain Range:** Minimum = {min_gain}, Maximum = {max_gain}, Difference = {gain_diff}")
        if gain_diff > 1:
            st.warning(f"⚠️ Gain difference is {gain_diff}, should be at most 1!")
    else:
            st.success("✅ All gains differ by at most 1!")
    
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
            # Show breakdown of total census calculation
            st.caption(f"Team A ({summary['team_a_total']}) + Team B ({summary['team_b_total']}) + "
                      f"Team N ({summary.get('team_n_total', 0)}) + Total Traded ({summary.get('total_traded', 0)}) = {summary['total_census']}")
        with col4:
            st.metric("Total Patients Gained from Yesterday", summary["total_gained"])
            # Show breakdown of total gained calculation
            st.caption(f"Team A Gained ({summary['team_a_gained']}) + Team B Gained ({summary['team_b_gained']}) + "
                      f"Team N Gained ({summary.get('team_n_gained', 0)}) + Total Traded ({summary.get('total_traded', 0)}) = {summary['total_gained']}")
        
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
    /* Highlight and bold Gained StepDown and Gained + Traded columns */
    div[data-testid="stDataEditor"] table th:has-text("Gained StepDown"),
    div[data-testid="stDataEditor"] table th:has-text("Gained + Traded"),
    div[data-testid="stDataEditor"] table td:nth-child(12),
    div[data-testid="stDataEditor"] table td:nth-child(13) {
        background-color: #fff3cd !important;
        font-weight: bold !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
