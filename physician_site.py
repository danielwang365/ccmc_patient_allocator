import streamlit as st
import pandas as pd

class Physician():
    def __init__(self, 
            name : str = "", 
            is_new : bool = False, 
            team : str = 'A', 
            n_total_patients : int = 0, 
            n_step_down_patients : int = 0, 
            n_transferred_patients : int = 0, 
            n_traded_patients : int = 0,
            is_buffer : bool = False):
        
        self.name = name
        self.is_new : bool = is_new
        self.team : str = team
        self.is_buffer : bool = is_buffer

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
    
    # Helper function to check if physician can take a step down patient
    def can_take_step_down(physician):
        return physician.step_down_patients < 1 and can_take_patient(physician)
    
    # First, allocate step down patients: Team B first, then Team A
    # Each physician can have at most 1 step down patient
    while n_step_down_patients > 0:
        # Find Team B physicians who can take a step down patient (have 0 step down patients)
        available_B = [p for p in team_B if can_take_step_down(p)]
        if available_B:
            # Allocate to Team B physician with lowest total patient count
            min_physician = min(available_B, key=lambda x: x.total_patients)
            min_physician.add_patient(is_step_down=True)
            n_step_down_patients -= 1
        else:
            # All Team B physicians already have 1 step down patient, allocate to Team A
            available_A = [p for p in team_A if can_take_step_down(p)]
            if available_A:
                # Allocate to Team A physician with lowest total patient count
                min_physician = min(available_A, key=lambda x: x.total_patients)
                min_physician.add_patient(is_step_down=True)
                n_step_down_patients -= 1
            else:
                # Both teams are full (all physicians have 1 step down patient)
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

    # Fourth, distribute remaining A patients to Team A physicians (if any)
    while n_A_new_patients > 0:
        available_A = [p for p in team_A if can_take_patient(p)]
        if available_A:
            min_physician = min(available_A, key=lambda x: x.total_patients)
            min_physician.add_patient()
            n_A_new_patients -= 1
            n_total_new_patients -= 1
        else:
            # Team A is full, use Team B buffer if available
            if buffer_B:
                available_buffer_B = [p for p in buffer_B if can_take_patient(p)]
                if available_buffer_B:
                    min_physician = min(available_buffer_B, key=lambda x: x.total_patients)
                    min_physician.add_patient()
                    n_A_new_patients -= 1
                    n_total_new_patients -= 1
                else:
                    break
            else:
                break

    # Fifth, distribute remaining B patients to Team B physicians (if any)
    while n_B_new_patients > 0:
        available_B = [p for p in team_B if can_take_patient(p)]
        if available_B:
            min_physician = min(available_B, key=lambda x: x.total_patients)
            min_physician.add_patient()
            n_B_new_patients -= 1
            n_total_new_patients -= 1
        else:
            # Team B is full, use Team A buffer if available
            if buffer_A:
                available_buffer_A = [p for p in buffer_A if can_take_patient(p)]
                if available_buffer_A:
                    min_physician = min(available_buffer_A, key=lambda x: x.total_patients)
                    min_physician.add_patient()
                    n_B_new_patients -= 1
                    n_total_new_patients -= 1
                else:
                    break
            else:
                break

    # Sixth, distribute remaining N patients to Team N physicians (if any)
    while n_N_new_patients > 0:
        available_N = [p for p in team_N if can_take_patient(p)]
        if available_N:
            min_physician = min(available_N, key=lambda x: x.total_patients)
            min_physician.add_patient()
            n_N_new_patients -= 1
            n_total_new_patients -= 1
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

# Default initiation for editable table
DEFAULT_ROWS = []
# 10 Team A physicians
for i in range(1, 11):
    DEFAULT_ROWS.append(dict(**{"Physician Name":f"A{i}", "Team":"A", "New Physician":False, "Buffer":False, "Total Patients":0, "StepDown":0, "Transferred":0, "Traded":0}))
# 1 Team A buffer
DEFAULT_ROWS.append(dict(**{"Physician Name":"A_Buffer", "Team":"A", "New Physician":False, "Buffer":True, "Total Patients":0, "StepDown":0, "Transferred":0, "Traded":0}))
# 10 Team B physicians
for i in range(1, 11):
    DEFAULT_ROWS.append(dict(**{"Physician Name":f"B{i}", "Team":"B", "New Physician":False, "Buffer":False, "Total Patients":0, "StepDown":0, "Transferred":0, "Traded":0}))
# 1 Neuro physician
DEFAULT_ROWS.append(dict(**{"Physician Name":"N1", "Team":"N", "New Physician":False, "Buffer":False, "Total Patients":0, "StepDown":0, "Transferred":0, "Traded":0}))

# Session state for the editable table (preserves edits/adds/removes)
if "physician_table" not in st.session_state:
    st.session_state["physician_table"] = pd.DataFrame(DEFAULT_ROWS)

edited_phys = st.data_editor(
    st.session_state["physician_table"],
    use_container_width=True,
    num_rows="dynamic",
    column_config={
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
        "Total Patients": st.column_config.NumberColumn(
            "Total Patients", min_value=0, step=1, format="%d"
        ),
        "StepDown": st.column_config.NumberColumn(
            "StepDown", min_value=0, step=1, format="%d"
        ),
        "Transferred": st.column_config.NumberColumn(
            "Transferred", min_value=0, step=1, format="%d"
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
)

# Don't update session state immediately - this causes the double-entry bug
# The data editor manages its own state through the key parameter
# We'll update session state only when the button is clicked

run = st.button("Run Allocation", use_container_width=True, type="primary")

if run:
    # Update session state with latest edits when button is clicked
    st.session_state["physician_table"] = edited_phys.copy()
    current_table = edited_phys.copy()
    
    # Convert table rows into Physician objects
    physicians = []
    for _, row in current_table.dropna(subset=["Physician Name", "Team"]).iterrows():
        # Defensive parsing for blank/empty
        try:
            tp = int(row["Total Patients"])
            sdp = int(row["StepDown"])
            tfp = int(row["Transferred"])
            tdp = int(row["Traded"])
            is_buf = bool(row.get("Buffer", False))
        except Exception:
            tp, sdp, tfp, tdp = 0,0,0,0
            is_buf = False
        physicians.append(
            Physician(
                name=str(row["Physician Name"]),
                is_new=bool(row["New Physician"]),
                team=str(row["Team"]),
                n_total_patients=tp,
                n_step_down_patients=sdp,
                n_transferred_patients=tfp,
                n_traded_patients=tdp,
                is_buffer=is_buf
            )
        )
    # Store initial patient counts before allocation
    initial_counts = {p.name: p.total_patients for p in physicians}
    initial_step_down_counts = {p.name: p.step_down_patients for p in physicians}
    # Run allocation logic
    allocate_patients(
        physicians,
        int(n_total_new_patients),
        int(n_A_new_patients),
        int(n_B_new_patients),
        int(n_N_new_patients),
        int(new_start_number),
        int(minimum_patients),
        int(n_step_down_patients),
        int(maximum_patients)
    )
    # Prepare results
    results_df = pd.DataFrame([
        {
            "Physician Name": p.name,
            "Team": p.team,
            "New Physician": p.is_new,
            "Buffer": p.is_buffer,
            "Total Patients": p.total_patients,
            "StepDown": p.step_down_patients,
            "Transferred": p.transferred_patients,
            "Traded": p.traded_patients,
            "Gained": p.total_patients - initial_counts[p.name],
            "Gained StepDown": p.step_down_patients - initial_step_down_counts[p.name],
            "Traded + Gained": p.traded_patients + (p.total_patients - initial_counts[p.name]),
        }
        for p in physicians
    ])
    st.markdown("### :clipboard: Results")
    st.dataframe(results_df, hide_index=True, use_container_width=True)
    st.success("Allocation complete! Review the results above.", icon="✅")
else:
    # Update session state only when rows are added/removed (structure change)
    # This preserves dynamic row operations without causing the double-entry bug
    if st.session_state["physician_table"].shape != edited_phys.shape:
        st.session_state["physician_table"] = edited_phys.copy()
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
