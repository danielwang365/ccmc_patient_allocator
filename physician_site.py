import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json
from datetime import datetime

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
    
    # Store initial pool sizes for tracking
    initial_A_pool = n_A_new_patients
    initial_B_pool = n_B_new_patients
    initial_N_pool = n_N_new_patients
    
    # Track pool allocations: how many from each pool went to each team
    # Format: pool_allocations[pool_team][target_team] = count
    pool_allocations = {
        'A': {'A': 0, 'B': 0, 'N': 0},
        'B': {'A': 0, 'B': 0, 'N': 0},
        'N': {'A': 0, 'B': 0, 'N': 0}
    }
    
    # Helper function to track pool allocation
    def track_pool_allocation(pool_team, target_team):
        """Track that a patient from pool_team was allocated to target_team"""
        if pool_team in pool_allocations and target_team in pool_allocations[pool_team]:
            pool_allocations[pool_team][target_team] += 1
    
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
    
    # Check if it's Wednesday
    current_date = datetime.now()
    is_wednesday = current_date.strftime("%A") == "Wednesday"
    
    print(f"\n=== ALLOCATION DEBUG ===")
    print(f"Today is: {current_date.strftime('%A, %B %d, %Y')}")
    print(f"Is Wednesday: {is_wednesday}")
    
    # ========== WEDNESDAY ALLOCATION LOGIC ==========
    if is_wednesday:
        # Wednesday: Simple round-robin distribution
        # GOAL: Treat all physicians as starting at 0, distribute total patients equally
        # IMPORTANT: Wednesday uses COMPLETELY DIFFERENT logic
        # - NO new_start_number constraint
        # - NO minimum_patients constraint
        # - Only maximum_patients constraint applies (via can_take_patient)
        
        print(f"\n=== WEDNESDAY ALLOCATION ===")
        print(f"Team A Pool: {n_A_new_patients}")
        print(f"Team B Pool: {n_B_new_patients}")
        print(f"Team N Pool: {n_N_new_patients}")
        print(f"Step Down: {n_step_down_patients}")
        
        # Get all working physicians
        all_working = [p for p in physicians if p.is_working]
        num_working = len(all_working)
        
        if num_working > 0:
            # Step 1: Calculate total_all_patients = current_total + new_regular + stepdown
            total_current_patients = sum(p.total_patients for p in all_working)
            regular_patients = n_A_new_patients + n_B_new_patients + n_N_new_patients
            total_all_patients = total_current_patients + regular_patients + n_step_down_patients
            
            print(f"Total current patients: {total_current_patients}")
            print(f"Regular patients (A+B+N): {regular_patients}")
            print(f"Step Down patients: {n_step_down_patients}")
            print(f"Total all patients: {total_all_patients}")
            print(f"Number of working physicians: {num_working}")
            
            # Step 2: Reset all physicians to 0 (as if they all started with no patients)
            for physician in all_working:
                physician.set_total_patients(0)
            
            print(f"\nReset all physicians to 0 total patients")
            
            # Step 3: Separate into non-new and new physicians for priority
            non_new_physicians = [p for p in all_working if not p.is_new]
            new_physicians = [p for p in all_working if p.is_new]
            
            print(f"Non-new physicians: {len(non_new_physicians)}, New physicians: {len(new_physicians)}")
            
            # Step 4: Simple round-robin distribution
            # Give +1 to all physicians who can take a patient, repeat until out of patients
            remaining_patients = total_all_patients
            round_num = 0
            
            while remaining_patients > 0:
                round_num += 1
                patients_given_this_round = 0
                
                # Full round: give +1 to all physicians who can take a patient
                # Priority: non-new first, then new
                for physician in non_new_physicians + new_physicians:
                    if remaining_patients <= 0:
                        break
                    if can_take_patient(physician):
                        physician.add_patient()
                        remaining_patients -= 1
                        patients_given_this_round += 1
                
                # If we couldn't give any patients this round, break
                if patients_given_this_round == 0:
                    print(f"  Round {round_num}: No more patients can be given (remaining: {remaining_patients})")
                    break
                else:
                    if round_num <= 5 or round_num % 10 == 0:  # Log first 5 and every 10th
                        print(f"  Round {round_num}: Gave +1 to {patients_given_this_round} physicians ({remaining_patients} remaining)")
            
            # Print final results
            print(f"\nFinal allocation results:")
            final_totals = [p.total_patients for p in all_working]
            min_total = min(final_totals)
            max_total = max(final_totals)
            variance = max_total - min_total
            
            # Sort by Team (A, B, N) then by total patients
            for physician in sorted(all_working, key=lambda x: (x.team, x.total_patients)):
                print(f"  {physician.name} (Team {physician.team}): {physician.total_patients} (is_new={physician.is_new})")
            
            print(f"\nFinal variance: {variance} (min={min_total}, max={max_total}, should be <= 1)")
            print(f"Remaining patients: {remaining_patients}")
        
        # Continue to step-down allocation (same as regular days) - will run after this block
        print(f"\n=== END WEDNESDAY REGULAR ALLOCATION ===\n")
    
    # ========== REGULAR ALLOCATION LOGIC (Non-Wednesday) ==========
    else:
        # Step 1: Calculate total patients to distribute
        # Total = Team A Pool + Team B Pool + Step Down (trades added separately)
        total_to_distribute = n_A_new_patients + n_B_new_patients + n_step_down_patients
        
        print(f"Team A Pool: {n_A_new_patients}")
        print(f"Team B Pool: {n_B_new_patients}")
        print(f"Step Down: {n_step_down_patients}")
        print(f"Total to distribute: {total_to_distribute}")
        
        # Step 2: Get all working physicians and sort by total patients (low to high)
        all_working = [p for p in physicians if p.is_working]
        all_working.sort(key=lambda x: x.total_patients)
        
        print(f"All working physicians (sorted by total, low to high):")
        for p in all_working:
            print(f"  {p.name}: total={p.total_patients}, is_new={p.is_new}")
        
        remaining = total_to_distribute
        
        # Step 3: Allocate to new physicians until they reach new_start_number
        # Do NOT include them in the general distribution afterward
        new_physicians = [p for p in all_working if p.is_new]
        print(f"\nStep 3: New physician allocation (new_start_number={new_start_number})")
        for physician in new_physicians:
            if physician.total_patients >= new_start_number:
                print(f"  {physician.name}: already at {physician.total_patients}, skip")
                continue
            needed = new_start_number - physician.total_patients
            to_give = min(needed, remaining)
            for _ in range(to_give):
                physician.add_patient()
                remaining -= 1
            print(f"  {physician.name}: gave {to_give}, now at {physician.total_patients}")
        
        # Step 4: Get non-new physicians for general distribution
        non_new = [p for p in all_working if not p.is_new]
        num_non_new = len(non_new)
        
        print(f"\nStep 4: General distribution (round-robin)")
        print(f"Non-new physicians: {num_non_new}")
        print(f"Remaining patients: {remaining}")
        
        if remaining > 0 and num_non_new > 0:
            round_num = 0
            
            # Round-robin: while remaining >= num_non_new, give +1 to ALL non-new physicians
            while remaining >= num_non_new:
                round_num += 1
                print(f"  Round {round_num}: giving +1 to all {num_non_new} physicians")
                for physician in non_new:
                    if can_take_patient(physician):
                        physician.add_patient()
                        remaining -= 1
            
            print(f"  After full rounds: remaining={remaining}")
            
            # Now remaining < num_non_new
            # First, give to physicians below minimum
            if remaining > 0:
                below_min = [p for p in non_new if p.total_patients < minimum_patients and can_take_patient(p)]
                below_min.sort(key=lambda x: x.total_patients)  # Lowest first
                
                print(f"  Physicians below minimum ({minimum_patients}): {len(below_min)}")
                for physician in below_min:
                    if remaining <= 0:
                        break
                    physician.add_patient()
                    remaining -= 1
                    print(f"    {physician.name}: +1 (below min), now at {physician.total_patients}")
            
            # Then, give remaining to physicians with lowest totals
            if remaining > 0:
                non_new.sort(key=lambda x: x.total_patients)  # Re-sort by current totals
                print(f"  Distributing final {remaining} patients to lowest totals:")
                for physician in non_new:
                    if remaining <= 0:
                        break
                    if can_take_patient(physician):
                        physician.add_patient()
                        remaining -= 1
                        print(f"    {physician.name}: +1, now at {physician.total_patients}")
            
            print(f"After distribution: remaining={remaining}")
        
        print(f"=== END REGULAR ALLOCATION DEBUG ===\n")
    
    # ========== STEP-DOWN ALLOCATION ==========
    # Step 1: Calculate "Gained + Traded" for each team (after regular allocation)
    # Step 2: Calculate trades between teams
    # Step 3: StepDown for Team A = (Gained + Traded for Team A) - (Traded B→A + Team A Pool)
    # Step 4: Remaining StepDown goes to Team B and Team N
    # Step 5: Allocate to physicians with lowest stepdown count (max 1 per physician)
    
    print(f"\n=== STEP-DOWN ALLOCATION ===")
    print(f"Total step-down patients to allocate: {n_step_down_patients}")
    
    # Filter to only working physicians
    working_team_A = [p for p in team_A if p.is_working]
    working_team_B = [p for p in team_B if p.is_working]
    working_team_N = [p for p in team_N if p.is_working]
    
    # Calculate gained for each physician (current total - initial total)
    # Note: At this point, regular patients have been allocated
    team_A_gained = sum(p.total_patients - initial_counts.get(p.name, p.total_patients) for p in working_team_A)
    team_B_gained = sum(p.total_patients - initial_counts.get(p.name, p.total_patients) for p in working_team_B)
    
    # Calculate traded patients
    traded_A_to_B = sum(p.traded_patients for p in working_team_B)  # B received from A
    traded_B_to_A = sum(p.traded_patients for p in working_team_A)  # A received from B
    
    # Total "Gained + Traded" for each team
    team_A_gained_plus_traded = team_A_gained + traded_B_to_A
    team_B_gained_plus_traded = team_B_gained + traded_A_to_B
    
    print(f"Team A: Gained={team_A_gained}, Traded B→A={traded_B_to_A}, Total={team_A_gained_plus_traded}")
    print(f"Team B: Gained={team_B_gained}, Traded A→B={traded_A_to_B}, Total={team_B_gained_plus_traded}")
    print(f"Team A Pool: {n_A_new_patients}")
    print(f"StepDown for A = {team_A_gained_plus_traded} - ({traded_B_to_A} + {n_A_new_patients}) = {team_A_gained_plus_traded - (traded_B_to_A + n_A_new_patients)}")
    
    # Calculate how many step-down patients Team A should get
    # StepDown for Team A = (Gained + Traded for Team A) - (Traded B→A + Team A Pool)
    stepdown_for_A = team_A_gained_plus_traded - (traded_B_to_A + n_A_new_patients)
    stepdown_for_A = max(0, min(stepdown_for_A, n_step_down_patients))  # Clamp to valid range
    
    # Remaining goes to Team B and Team N
    stepdown_for_B_and_N = n_step_down_patients - stepdown_for_A
    
    print(f"StepDown for Team A: {stepdown_for_A}")
    print(f"StepDown for Team B and N: {stepdown_for_B_and_N}")
    
    # Allocate step-down to Team A (sorted by lowest stepdown count)
    team_A_sorted = sorted(working_team_A, key=lambda x: initial_stepdown_counts.get(x.name, x.step_down_patients))
    remaining_A = stepdown_for_A
    
    print(f"\nAllocating {remaining_A} step-down to Team A:")
    for physician in team_A_sorted:
        if remaining_A <= 0:
            break
        if can_take_step_down(physician):
            physician.add_patient(is_step_down=True)
            remaining_A -= 1
            print(f"  {physician.name}: +1 stepdown, now at {physician.step_down_patients}")
    
    # Allocate step-down to Team B and Team N (combined, sorted by lowest stepdown count)
    team_B_and_N = working_team_B + working_team_N
    team_B_and_N_sorted = sorted(team_B_and_N, key=lambda x: initial_stepdown_counts.get(x.name, x.step_down_patients))
    remaining_B_N = stepdown_for_B_and_N
    
    print(f"\nAllocating {remaining_B_N} step-down to Team B and N:")
    for physician in team_B_and_N_sorted:
        if remaining_B_N <= 0:
            break
        if can_take_step_down(physician):
            physician.add_patient(is_step_down=True)
            remaining_B_N -= 1
            print(f"  {physician.name} (Team {physician.team}): +1 stepdown, now at {physician.step_down_patients}")
    
    print(f"\n=== END STEP-DOWN ALLOCATION ===\n")
    
    # Final verification: Ensure new physicians who started at/above new_start_number have gained 0 patients
    # This is a safety check to catch any bugs where new physicians incorrectly received patients
    # SKIP THIS VERIFICATION ON WEDNESDAY - Wednesday doesn't use new_start_number
    if not is_wednesday:
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
        
        # Check if any physicians are below minimum_patients and redistribute if needed
        print(f"\n=== MINIMUM PATIENTS CHECK ===")
        all_working = [p for p in physicians if p.is_working]
        below_minimum = [p for p in all_working if p.total_patients < minimum_patients]
        
        if below_minimum:
            print(f"Found {len(below_minimum)} physicians below minimum ({minimum_patients}):")
            for p in below_minimum:
                print(f"  {p.name} (Team {p.team}): {p.total_patients} patients")
            
            # Calculate total shortfall
            total_shortfall = sum(minimum_patients - p.total_patients for p in below_minimum)
            print(f"Total shortfall: {total_shortfall} patients")
            
            # Find non-new physicians who gained the most patients (sorted by gained descending)
            # Exclude physicians who are at or below minimum (they can't afford to lose patients)
            non_new_working = [p for p in all_working if not p.is_new]
            physicians_with_gains = []
            for p in non_new_working:
                # Only consider physicians who are above minimum (can afford to lose one)
                if p.total_patients > minimum_patients:
                    gained = p.total_patients - initial_counts.get(p.name, p.total_patients)
                    if gained > 0:
                        physicians_with_gains.append((p, gained))
            
            # Sort by gained (highest first)
            physicians_with_gains.sort(key=lambda x: x[1], reverse=True)
            
            print(f"Non-new physicians with gains above minimum (sorted by highest gained):")
            for p, gained in physicians_with_gains[:10]:  # Show top 10
                print(f"  {p.name} (Team {p.team}): gained {gained}, current total={p.total_patients}")
            
            # Iteratively redistribute until all physicians are at or above minimum
            # or until we can't find any more sources
            iteration = 0
            max_iterations = 100  # Safety limit to prevent infinite loops
            
            while total_shortfall > 0 and iteration < max_iterations:
                iteration += 1
                print(f"\n  Redistribution iteration {iteration}:")
                
                # Recalculate below_minimum (in case it changed)
                below_minimum = [p for p in all_working if p.total_patients < minimum_patients]
                if not below_minimum:
                    print("    All physicians now at or above minimum")
                    break
                
                # Recalculate total shortfall
                total_shortfall = sum(minimum_patients - p.total_patients for p in below_minimum)
                print(f"    Total shortfall: {total_shortfall} patients")
                
                # Recalculate physicians_with_gains (exclude those now at or below minimum)
                physicians_with_gains = []
                for p in non_new_working:
                    if p.total_patients > minimum_patients:
                        gained = p.total_patients - initial_counts.get(p.name, p.total_patients)
                        if gained > 0:
                            physicians_with_gains.append((p, gained))
                
                # Sort by gained (highest first)
                physicians_with_gains.sort(key=lambda x: x[1], reverse=True)
                
                if not physicians_with_gains:
                    print("    No more physicians available to take patients from")
                    break
                
                # Take no more than one patient from each physician, starting with highest gained
                patients_removed_this_iteration = 0
                for physician, gained in physicians_with_gains:
                    if total_shortfall <= 0:
                        break
                    # Double-check they're still above minimum before removing
                    if physician.total_patients > minimum_patients:
                        physician.remove_patient()
                        patients_removed_this_iteration += 1
                        total_shortfall -= 1
                        print(f"    Removed 1 patient from {physician.name} (Team {physician.team}), now at {physician.total_patients}")
                
                # Redistribute the removed patients to physicians below minimum
                if patients_removed_this_iteration > 0:
                    print(f"    Redistributing {patients_removed_this_iteration} patients to physicians below minimum:")
                    below_minimum_sorted = sorted(below_minimum, key=lambda x: x.total_patients)  # Lowest first
                    for physician in below_minimum_sorted:
                        if patients_removed_this_iteration <= 0:
                            break
                        if physician.total_patients < minimum_patients and can_take_patient(physician):
                            physician.add_patient()
                            patients_removed_this_iteration -= 1
                            print(f"      Added 1 patient to {physician.name} (Team {physician.team}), now at {physician.total_patients}")
                else:
                    print("    No patients could be removed this iteration")
                    break
            
            # Final check
            below_minimum_final = [p for p in all_working if p.total_patients < minimum_patients]
            if below_minimum_final:
                print(f"\n  WARNING: {len(below_minimum_final)} physicians still below minimum after redistribution:")
                for p in below_minimum_final:
                    print(f"    {p.name} (Team {p.team}): {p.total_patients} patients")
            else:
                print(f"\n  SUCCESS: All physicians are now at or above minimum ({minimum_patients})")
        else:
            print(f"All physicians are at or above minimum ({minimum_patients})")
        
        print(f"=== END MINIMUM PATIENTS CHECK ===\n")

# --- Streamlit App Begins Here ---
st.set_page_config(page_title="Patient Allocator", page_icon="🩺", layout="wide")
st.title("🩺 Physician Patient Allocation")

# Check current day of the week
current_date = datetime.now()
day_of_week = current_date.strftime("%A")
is_wednesday = day_of_week == "Wednesday"
date_str = current_date.strftime("%B %d, %Y")

# Display day of week prominently
if is_wednesday:
    st.success(f"📅 **Today is {day_of_week}, {date_str}**")
else:
    st.info(f"📅 **Today is {day_of_week}, {date_str}**")

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
    st.session_state["step_down_patients_input"] = int(n_step_down_patients)  # Store step-down input
    # Store pool input parameters for allocation summary
    st.session_state["pool_inputs"] = {
        "team_a_pool": int(n_A_new_patients),
        "team_b_pool": int(n_B_new_patients),
        "team_n_pool": int(n_N_new_patients),
    }
    
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
        "team_n_stepdown_gained": sum(p.step_down_patients - initial_step_down_counts[p.name] for p in working_physicians if p.team == 'N'),
        "team_a_traded": sum(p.traded_patients for p in working_physicians if p.team == 'A'),
        "team_b_traded": sum(p.traded_patients for p in working_physicians if p.team == 'B'),
        "total_traded": total_traded,
        "total_census": total_census,
        "total_gained": total_gained,
    }

# Display results if they exist in session state
if "allocation_results" in st.session_state and st.session_state["allocation_results"] is not None:
    # Initialize print summary state
    if "print_summary" not in st.session_state:
        st.session_state["print_summary"] = False
    
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
            "Gained StepDown": st.column_config.NumberColumn("⭐ Gained StepDown", min_value=0, step=1, format="%d", disabled=True),
            "Gained + Traded": st.column_config.NumberColumn("⭐ Gained + Traded", min_value=0, step=1, format="%d", disabled=True),
        },
        hide_index=True,
        use_container_width=True,
        key="results_editor",
        num_rows="fixed"
    )
    
    # Display highlighted summary of key columns
    st.markdown("#### ⭐ Key Metrics (Highlighted)")
    highlight_df = display_df[["Physician Name", "Team", "Gained + Traded", "Gained StepDown"]].copy()
    
    def highlight_cols(x):
        return ['background-color: #fff3cd; font-weight: bold' if col in ['Gained StepDown', 'Gained + Traded'] else '' for col in x.index]
    
    styled_df = highlight_df.style.apply(highlight_cols, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # Update session state with edited results
    if not edited_results.equals(display_df):
        st.session_state["allocation_results"] = edited_results.copy()
    
    # Add export and print options
    st.markdown("---")
    st.markdown("### 📄 Export & Print Options")
    col_export1, col_export2, col_export3 = st.columns(3)
    
    with col_export1:
        # Download CSV button
        csv = edited_results.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"patient_allocation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            help="Download the results table as a CSV file that can be opened in Excel or printed"
        )
    
    with col_export2:
        # Show printable view
        show_printable = st.button("🖨️ Show Printable View", help="Display a formatted, print-friendly version of the results")
    
    with col_export3:
        # Copy to clipboard option (using text area that can be copied)
        copy_text = st.button("📋 Copy to Clipboard", help="Generate text that can be easily copied")
    
    # Display printable view if requested
    if show_printable:
        st.markdown("---")
        st.markdown("### 🖨️ Printable Results Table")
        
        # Create a nicely formatted HTML table
        html_table = edited_results.to_html(index=False, classes='printable-table', table_id='results-table')
        
        # Add custom styling for printing
        print_style = """
        <style>
        @media print {
            body * {
                visibility: hidden;
            }
            .printable-section, .printable-section * {
                visibility: visible;
            }
            .printable-section {
                position: absolute;
                left: 0;
                top: 0;
                width: 100%;
            }
            table.printable-table {
                border-collapse: collapse;
                width: 100%;
                font-size: 12pt;
            }
            table.printable-table th, table.printable-table td {
                border: 1px solid #000;
                padding: 8px;
                text-align: left;
            }
            table.printable-table th {
                background-color: #f0f0f0;
                font-weight: bold;
            }
        }
        .printable-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 11pt;
        }
        .printable-table th, .printable-table td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }
        .printable-table th {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }
        .printable-table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .printable-table tr:hover {
            background-color: #e8f5e9;
        }
        </style>
        """
        
        st.markdown(print_style, unsafe_allow_html=True)
        st.markdown(f'<div class="printable-section">{html_table}</div>', unsafe_allow_html=True)
        
        # Add print button - use Streamlit button that triggers JavaScript on next render
        if 'trigger_print' not in st.session_state:
            st.session_state.trigger_print = False
        
        print_btn = st.button("🖨️ Print This Page", key="print_page_btn",
                             help="Click to open your browser's print dialog")
        
        if print_btn:
            st.session_state.trigger_print = True
            st.rerun()
        
        # Inject print JavaScript if button was clicked
        if st.session_state.get('trigger_print', False):
            st.markdown("""
            <script>
                setTimeout(function() {
                    window.print();
                }, 100);
            </script>
            """, unsafe_allow_html=True)
            st.session_state.trigger_print = False  # Reset after triggering
        
        # Also add instructions
        st.info("💡 **Tip:** Click the button above or use your browser's print function (Ctrl+P or Cmd+P) to print this page. The table above is optimized for printing.")
    
    # Display copy-friendly text view if requested
    if copy_text:
        st.markdown("---")
        st.markdown("### 📋 Copy-Friendly Text View")
        st.markdown("**Copy the text below:**")
        
        # Create a text representation
        text_output = "PATIENT ALLOCATION RESULTS\n"
        text_output += "=" * 80 + "\n\n"
        
        # Add summary if available
        if "allocation_summary" in st.session_state:
            summary = st.session_state["allocation_summary"]
            text_output += "ALLOCATION SUMMARY\n"
            text_output += "-" * 80 + "\n"
            text_output += f"Team A Total Patients: {summary['team_a_total']}\n"
            text_output += f"Team B Total Patients: {summary['team_b_total']}\n"
            text_output += f"Team N Total Patients: {summary.get('team_n_total', 0)}\n"
            text_output += f"Total Census: {summary['total_census']}\n"
            text_output += f"Total Patients Gained: {summary['total_gained']}\n"
            text_output += f"Total Traded: {summary.get('total_traded', 0)}\n\n"
        
        text_output += "PHYSICIAN DETAILS\n"
        text_output += "-" * 80 + "\n"
        
        # Format table as text with proper column widths
        col_widths = {}
        for col in edited_results.columns:
            # Calculate max width needed for this column
            max_val_len = max(len(str(col)), edited_results[col].astype(str).str.len().max() if len(edited_results) > 0 else 0)
            col_widths[col] = max(max_val_len + 2, 15)  # Minimum width of 15, add 2 for padding
        
        # Header row
        for col in edited_results.columns:
            text_output += f"{col:<{col_widths[col]}}"
        text_output += "\n" + "-" * sum(col_widths.values()) + "\n"
        
        # Data rows
        for _, row in edited_results.iterrows():
            for col in edited_results.columns:
                value = str(row[col]) if pd.notna(row[col]) else ""
                text_output += f"{value:<{col_widths[col]}}"
            text_output += "\n"
        
        st.text_area("Results (Select All and Copy)", text_output, height=400, key="copy_text_area")
    
    # Calculate and display total gained patients and distribution
    if "allocation_results" in st.session_state and st.session_state["allocation_results"] is not None:
        # Calculate total gained: just regular patients (step-down is already included in the pool)
        total_gained_regular = display_df["Gained"].sum()
        total_gained_stepdown = display_df["Gained StepDown"].sum()
        total_gained = total_gained_regular  # Don't add step-down again, it's already in the pool
        
        gain_counts = display_df["Gained"].value_counts().sort_index()
        expected_total = st.session_state.get("total_new_patients_input", 0)
        num_physicians_shown = len(display_df)
        
        st.markdown("### 📈 Gain Distribution Analysis")
        col_analysis1, col_analysis2 = st.columns(2)
        with col_analysis1:
            st.metric("Total Patients Gained (Sum)", int(total_gained))
            st.caption(f"(Step-down tracked separately: {int(total_gained_stepdown)})")
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
        
        # Add custom CSS for highlighted metrics
        st.markdown("""
        <style>
        .highlight-metric {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
            border: 2px solid #ffc107;
            border-radius: 10px;
            padding: 10px;
            margin-top: 10px;
        }
        .highlight-metric-label {
            font-size: 14px;
            font-weight: bold;
            color: #856404;
            margin-bottom: 5px;
        }
        .highlight-metric-value {
            font-size: 28px;
            font-weight: bold;
            color: #856404;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Team-specific information
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("#### Team A")
            st.metric("Total Patients", summary["team_a_total"])
            st.metric("Total Patients Without Trade", summary["team_a_gained"])
            st.metric("Step Down Patients Gained", summary["team_a_stepdown_gained"])
            st.markdown(f"""
            <div class="highlight-metric">
                <div class="highlight-metric-label">⭐ Total Patients Gained + Traded</div>
                <div class="highlight-metric-value">{int(team_a_gained_traded)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("#### Team B")
            st.metric("Total Patients", summary["team_b_total"])
            st.metric("Total Patients Without Trade", summary["team_b_gained"])
            st.metric("Step Down Patients Gained", summary["team_b_stepdown_gained"])
            st.markdown(f"""
            <div class="highlight-metric">
                <div class="highlight-metric-label">⭐ Total Patients Gained + Traded</div>
                <div class="highlight-metric-value">{int(team_b_gained_traded)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("#### Team N")
            st.metric("Total Patients", summary.get("team_n_total", 0))
            st.metric("Total Patients Without Trade", summary.get("team_n_gained", 0))
            st.metric("Step Down Patients Gained", summary.get("team_n_stepdown_gained", 0))
            team_n_gained_traded = summary.get("team_n_gained", 0)
            st.markdown(f"""
            <div class="highlight-metric">
                <div class="highlight-metric-label">⭐ Total Patients Gained + Traded</div>
                <div class="highlight-metric-value">{int(team_n_gained_traded)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Step-Down Calculation Breakdown
        st.markdown("---")
        st.markdown("### 🔢 Step-Down Calculation")
        
        # Get input values from Allocation Parameters (stored in pool_inputs)
        pool_inputs = st.session_state.get("pool_inputs", {})
        team_a_pool = pool_inputs.get("team_a_pool", 0)
        total_stepdown = st.session_state.get("step_down_patients_input", 0)
        traded_b_to_a = summary["team_b_traded"]  # Traded FROM B TO A
        
        # Calculate step-down allocation
        # StepDown for Team A = (Gained + Traded for A) - (Traded B→A + Team A Pool)
        stepdown_for_A = team_a_gained_traded - (traded_b_to_a + team_a_pool)
        stepdown_for_A = max(0, min(stepdown_for_A, total_stepdown))  # Clamp to valid range
        stepdown_for_B_N = total_stepdown - stepdown_for_A
        
        col_sd1, col_sd2 = st.columns(2)
        with col_sd1:
            st.markdown("**Calculation for Team A Step-Down:**")
            st.markdown(f"- Team A Gained + Traded = {int(team_a_gained_traded)}")
            st.markdown(f"- Traded B→A = {int(traded_b_to_a)}")
            st.markdown(f"- Team A Pool = {int(team_a_pool)}")
            raw_stepdown_A = team_a_gained_traded - (traded_b_to_a + team_a_pool)
            st.markdown(f"- **StepDown for A** = {int(team_a_gained_traded)} - ({int(traded_b_to_a)} + {int(team_a_pool)})")
            display_stepdown_A = max(0, raw_stepdown_A)  # Show 0 if negative
            st.markdown(f"- **StepDown for A** = {int(team_a_gained_traded)} - {int(traded_b_to_a + team_a_pool)} = **{int(display_stepdown_A)}**")
            if raw_stepdown_A < 0:
                st.info(f"ℹ️ Team A Pool ({int(team_a_pool)}) > Team A Gained + Traded ({int(team_a_gained_traded)}). All step-down patients go to Team B and N.")
        with col_sd2:
            st.markdown("**Step-Down Distribution:**")
            st.metric("Team A Step-Down", int(stepdown_for_A))
            st.metric("Team B + N Step-Down", int(stepdown_for_B_N))
            st.markdown(f"Total: {int(stepdown_for_A)} + {int(stepdown_for_B_N)} = {int(total_stepdown)}")
        
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
        
        # Patient allocation summary by team (from pools + traded)
        st.markdown("---")
        st.markdown("#### 📋 Patient Allocation by Team")
        st.markdown("**Summary of patients allocated to each team (from pools and traded):**")
        
        # Get pool input parameters (these are the actual pool sizes)
        pool_inputs = st.session_state.get("pool_inputs", {})
        team_a_pool_size = pool_inputs.get("team_a_pool", 0)
        team_b_pool_size = pool_inputs.get("team_b_pool", 0)
        team_n_pool_size = pool_inputs.get("team_n_pool", 0)
        
        # "From Pool" should show how many patients from each pool were allocated
        # Since we don't track this during allocation, we'll use the pool input sizes
        # as these represent the total patients available in each pool
        # The actual allocation may distribute these across teams, but for display purposes,
        # we show the pool size as "From Pool" for the respective team
        team_a_from_pool = team_a_pool_size
        team_b_from_pool = team_b_pool_size
        team_n_from_pool = team_n_pool_size
        
        # Calculate total patients going to each team
        # Total = From Pool + From Trade
        patients_to_team_a = team_a_from_pool + trade_info['B_to_A']
        patients_to_team_b = team_b_from_pool + trade_info['A_to_B']
        patients_to_team_n = team_n_from_pool
        
        col_alloc1, col_alloc2, col_alloc3 = st.columns(3)
        with col_alloc1:
            st.markdown("##### Team A")
            st.metric("From Pool", team_a_from_pool)
            st.metric("From Trade (B→A)", trade_info['B_to_A'])
            st.markdown("---")
            st.metric("**Total to Team A**", patients_to_team_a)
        with col_alloc2:
            st.markdown("##### Team B")
            st.metric("From Pool", team_b_from_pool)
            st.metric("From Trade (A→B)", trade_info['A_to_B'])
            st.markdown("---")
            st.metric("**Total to Team B**", patients_to_team_b)
        with col_alloc3:
            st.markdown("##### Team N")
            st.metric("From Pool", team_n_from_pool)
            st.metric("From Trade", 0)
            st.markdown("---")
            st.metric("**Total to Team N**", patients_to_team_n)
        
        # Print Summary button
        st.markdown("---")
        print_summary_btn = st.button("🖨️ Print Summary (Key Metrics + Analysis + Allocation)", 
                                     use_container_width=True, 
                                     type="primary",
                                     help="Print Key Metrics, Gain Distribution Analysis, and Allocation Summary on one page")
        
        if print_summary_btn:
            st.session_state["print_summary"] = True
            st.rerun()
        
        # Display printable summary if button was clicked
        if st.session_state.get("print_summary", False):
            st.markdown("---")
            st.markdown("### 🖨️ Printable Summary")
            
            # Get variables from session state or recalculate
            if "allocation_results" in st.session_state and st.session_state["allocation_results"] is not None:
                print_display_df = st.session_state["allocation_results"].copy()
                print_highlight_df = print_display_df[["Physician Name", "Team", "Gained + Traded", "Gained StepDown"]].copy()
                # Sort by Team (A, B, N) then by Physician Name
                print_highlight_df = print_highlight_df.sort_values(by=["Team", "Physician Name"], ascending=[True, True]).reset_index(drop=True)
                print_total_gained_regular = print_display_df["Gained"].sum()
                print_total_gained_stepdown = print_display_df["Gained StepDown"].sum()
                print_total_gained = print_total_gained_regular
                print_gain_counts = print_display_df["Gained"].value_counts().sort_index()
                print_expected_total = st.session_state.get("total_new_patients_input", 0)
                print_num_physicians_shown = len(print_display_df)
                print_min_gain = int(print_display_df["Gained"].min())
                print_max_gain = int(print_display_df["Gained"].max())
                print_gain_diff = print_max_gain - print_min_gain
            else:
                st.error("No allocation results available for printing.")
                st.session_state["print_summary"] = False
                st.stop()
            
            # Create printable HTML content
            print_html = """
            <style>
            @media print {
                body * {
                    visibility: hidden;
                }
                .printable-summary, .printable-summary * {
                    visibility: visible;
                }
                .printable-summary {
                    position: absolute;
                    left: 0;
                    top: 0;
                    width: 100%;
                }
            }
            .printable-summary {
                font-family: Arial, sans-serif;
                padding: 10px;
                font-size: 11pt;
            }
            .printable-summary h2 {
                color: #333;
                border-bottom: 2px solid #333;
                padding-bottom: 5px;
                margin-top: 15px;
                margin-bottom: 10px;
                font-size: 16pt;
            }
            .printable-summary h3 {
                color: #555;
                margin-top: 12px;
                margin-bottom: 8px;
                font-size: 13pt;
            }
            .printable-summary h4 {
                margin-top: 8px;
                margin-bottom: 5px;
                font-size: 11pt;
            }
            .printable-summary table {
                width: 100%;
                border-collapse: collapse;
                margin: 8px 0;
                font-size: 10pt;
            }
            /* Make Key Metrics table text bigger for easier reading */
            .printable-summary h2:first-of-type + table.printable-table,
            .printable-summary h2:contains("Key Metrics") + table.printable-table {
                font-size: 12pt !important;
            }
            /* Alternative selector for Key Metrics table */
            .printable-summary table.printable-table:first-of-type {
                font-size: 12pt !important;
            }
            .printable-summary table.printable-table:first-of-type th,
            .printable-summary table.printable-table:first-of-type td {
                font-size: 12pt !important;
                padding: 6px !important;
            }
            .printable-summary th, .printable-summary td {
                border: 1px solid #ddd;
                padding: 5px;
                text-align: left;
            }
            /* Make Key Metrics table columns tighter, especially last two columns (Gained + Traded and Gained StepDown) */
            .printable-summary table.printable-table th:nth-last-child(1),
            .printable-summary table.printable-table td:nth-last-child(1),
            .printable-summary table.printable-table th:nth-last-child(2),
            .printable-summary table.printable-table td:nth-last-child(2) {
                width: auto;
                min-width: 60px;
                max-width: 70px;
                white-space: nowrap;
            }
            .printable-summary table.printable-table th:first-child,
            .printable-summary table.printable-table td:first-child {
                width: auto;
                min-width: 120px;
            }
            .printable-summary table.printable-table th:nth-child(2),
            .printable-summary table.printable-table td:nth-child(2) {
                width: auto;
                min-width: 60px;
            }
            .printable-summary th {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
            }
            .printable-summary tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            .printable-summary p {
                margin: 5px 0;
            }
            .printable-summary ul {
                margin: 5px 0;
                padding-left: 20px;
            }
            .highlight-cell {
                background-color: #fff3cd !important;
                font-weight: bold !important;
            }
            .metric-box {
                border: 2px solid #ffc107;
                background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
                padding: 8px;
                margin: 5px 0;
                border-radius: 3px;
            }
            </style>
            <div class="printable-summary">
            """
            
            # Add Key Metrics
            print_html += "<h2>⭐ Key Metrics</h2>"
            print_html += print_highlight_df.to_html(index=False, classes='printable-table')
            print_html += "<br>"
            
            # Add Gain Distribution Analysis (condensed)
            print_html += "<h2>📈 Gain Distribution Analysis</h2>"
            print_html += f"<p><strong>Total Gained:</strong> {int(print_total_gained)} | <strong>Step-down:</strong> {int(print_total_gained_stepdown)} | <strong>Physicians:</strong> {int(print_num_physicians_shown)}</p>"
            print_html += "<p><strong>Distribution:</strong> "
            dist_list = []
            for gain_amount in sorted(print_gain_counts.index):
                count = int(print_gain_counts[gain_amount])
                dist_list.append(f"{count} physician(s) gained {int(gain_amount)}")
            print_html += " | ".join(dist_list) + "</p>"
            
            if print_expected_total > 0 and print_num_physicians_shown > 0:
                base_expected = print_expected_total // print_num_physicians_shown
                remainder_expected = print_expected_total % print_num_physicians_shown
                print_html += f"<p><strong>Expected:</strong> Base = {base_expected} | {remainder_expected} get {base_expected + 1} | {print_num_physicians_shown - remainder_expected} get {base_expected}</p>"
            
            # Recalculate values for print
            print_team_a_gained_traded = summary["team_a_gained"] + summary["team_b_traded"]
            print_team_b_gained_traded = summary["team_b_gained"] + summary["team_a_traded"]
            print_team_n_gained_traded = summary.get("team_n_gained", 0)
            print_trade_info = {'A_to_B': summary["team_a_traded"], 'B_to_A': summary["team_b_traded"]}
            
            # Add Allocation Summary (condensed table format)
            print_html += "<h2>📊 Allocation Summary</h2>"
            print_html += "<table style='width:100%; margin-top:10px;'>"
            print_html += "<tr><th>Team</th><th>Gained (No Trade)</th><th>Step Down Gained</th><th>⭐ Gained + Traded</th></tr>"
            print_html += f"<tr><td><strong>Team A</strong></td><td>{summary['team_a_gained']}</td><td>{summary['team_a_stepdown_gained']}</td><td style='background-color:#fff3cd; font-weight:bold;'>{int(print_team_a_gained_traded)}</td></tr>"
            print_html += f"<tr><td><strong>Team B</strong></td><td>{summary['team_b_gained']}</td><td>{summary['team_b_stepdown_gained']}</td><td style='background-color:#fff3cd; font-weight:bold;'>{int(print_team_b_gained_traded)}</td></tr>"
            print_html += f"<tr><td><strong>Team N</strong></td><td>{summary.get('team_n_gained', 0)}</td><td>{summary.get('team_n_stepdown_gained', 0)}</td><td style='background-color:#fff3cd; font-weight:bold;'>{int(print_team_n_gained_traded)}</td></tr>"
            print_html += "</table>"
            
            # Overall census (condensed)
            print_html += "<h3>Overall Summary</h3>"
            print_html += f"<p><strong>Total Census:</strong> {summary['total_census']}</p>"
            print_html += f"<p><strong>Total Patients Gained from Yesterday:</strong> {summary['total_gained']}</p>"
            
            print_html += "</div>"
            
            # Display the printable content
            st.markdown(print_html, unsafe_allow_html=True)
            
            # Add print instructions and download option
            st.markdown("---")
            st.markdown("### 🖨️ Print Options")
            
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                # Download as HTML file that can be printed
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Patient Allocation Summary</title>
                    <style>
                        @media print {{
                            body * {{
                                visibility: hidden;
                            }}
                            .printable-summary, .printable-summary * {{
                                visibility: visible;
                            }}
                            .printable-summary {{
                                position: absolute;
                                left: 0;
                                top: 0;
                                width: 100%;
                            }}
                        }}
                        body {{
                            font-family: Arial, sans-serif;
                            padding: 20px;
                        }}
                        .printable-summary {{
                            font-family: Arial, sans-serif;
                            padding: 20px;
                        }}
                        .printable-summary h2 {{
                            color: #333;
                            border-bottom: 2px solid #333;
                            padding-bottom: 10px;
                        }}
                        .printable-summary h3 {{
                            color: #555;
                            margin-top: 20px;
                        }}
                        .printable-summary table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin: 15px 0;
                        }}
                        /* Make Key Metrics table text bigger for easier reading */
                        .printable-summary table.printable-table:first-of-type {{
                            font-size: 12pt !important;
                        }}
                        .printable-summary table.printable-table:first-of-type th,
                        .printable-summary table.printable-table:first-of-type td {{
                            font-size: 12pt !important;
                            padding: 6px !important;
                        }}
                        .printable-summary th, .printable-summary td {{
                            border: 1px solid #ddd;
                            padding: 8px;
                            text-align: left;
                        }}
                        .printable-summary th {{
                            background-color: #4CAF50;
                            color: white;
                            font-weight: bold;
                        }}
                        .printable-summary tr:nth-child(even) {{
                               background-color: #f2f2f2;
                        }}
                        /* Make Key Metrics table columns tighter, especially last two columns (Gained + Traded and Gained StepDown) */
                        .printable-summary table.printable-table th:nth-last-child(1),
                        .printable-summary table.printable-table td:nth-last-child(1),
                        .printable-summary table.printable-table th:nth-last-child(2),
                        .printable-summary table.printable-table td:nth-last-child(2) {{
                            width: auto;
                            min-width: 60px;
                            max-width: 70px;
                            white-space: nowrap;
                        }}
                        .printable-summary table.printable-table th:first-child,
                        .printable-summary table.printable-table td:first-child {{
                            width: auto;
                            min-width: 120px;
                        }}
                        .printable-summary table.printable-table th:nth-child(2),
                        .printable-summary table.printable-table td:nth-child(2) {{
                            width: auto;
                            min-width: 60px;
                        }}
                        .metric-box {{
                            border: 2px solid #ffc107;
                            background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
                            padding: 15px;
                            margin: 10px 0;
                            border-radius: 5px;
                        }}
                        .print-btn {{
                            text-align: center;
                            margin: 20px 0;
                        }}
                        button {{
                            background-color: #4CAF50;
                            color: white;
                            padding: 12px 24px;
                            font-size: 16px;
                            font-weight: bold;
                            border: none;
                            border-radius: 5px;
                            cursor: pointer;
                        }}
                    </style>
                </head>
                <body>
                    {print_html}
                    <div class="print-btn">
                        <button onclick="window.print()">🖨️ Print This Page</button>
                    </div>
                </body>
                </html>
                """
                st.download_button(
                    label="📥 Download HTML for Printing",
                    data=html_content,
                    file_name=f"allocation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    use_container_width=True,
                    help="Download an HTML file that you can open in your browser and print"
                )
            
            with col_btn2:
                st.markdown("**Or use keyboard shortcut:**")
                st.markdown("**Ctrl+P** (Windows/Linux)  \n**Cmd+P** (Mac)")
                st.markdown("*(While viewing the content above)*")
            
            with col_btn3:
                if st.button("❌ Close Print View", key="close_print_btn", use_container_width=True):
                    st.session_state["print_summary"] = False
                    st.rerun()
            
            st.info("💡 **Tip:** The content above is optimized for printing. **Option 1:** Download the HTML file and open it in your browser to print. **Option 2:** Press **Ctrl+P** (Windows) or **Cmd+P** (Mac) while viewing the content above.")
        
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
    
    /* Highlight Gained StepDown and Gained + Traded columns in results table */
    /* Target the last two data columns (11th and 12th) */
    div[data-testid="stDataEditor"] [data-testid="StyledDataGrid"] div[role="gridcell"]:nth-last-child(1),
    div[data-testid="stDataEditor"] [data-testid="StyledDataGrid"] div[role="gridcell"]:nth-last-child(2) {
        background-color: #fff3cd !important;
        font-weight: bold !important;
    }
    
    /* Also highlight column headers */
    div[data-testid="stDataEditor"] [data-testid="StyledDataGrid"] div[role="columnheader"]:nth-last-child(1),
    div[data-testid="stDataEditor"] [data-testid="StyledDataGrid"] div[role="columnheader"]:nth-last-child(2) {
        background-color: #ffc107 !important;
        font-weight: bold !important;
        color: #000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
