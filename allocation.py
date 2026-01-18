"""
Patient allocation algorithm for the Patient Allocator application.
Implements a 5-phase allocation strategy for distributing patients to physicians.
"""

from models import Physician


def allocate_patients(
    physicians: list[Physician],
    n_total_new_patients: int,
    n_A_new_patients: int,
    n_B_new_patients: int,
    n_N_new_patients: int,
    new_start_number: int,
    minimum_patients: int = 10,
    n_step_down_patients: int = 0,
    maximum_patients: int = 1000
):
    """
    Allocate patients to physicians using a 5-phase algorithm.

    Phase 1: Step-down allocation (Team B first, then Team A)
    Phase 2: Fix below-minimum physicians
    Phase 3: Fill new physicians to new_start_number
    Phase 4: Even distribution with pattern-based allocation
    Phase 5: Final verification

    Returns a dictionary with results and summary statistics.
    """
    # Store initial patient counts for even distribution later
    initial_counts = {p.name: p.total_patients for p in physicians}

    # Make team lists
    team_A = [p for p in physicians if p.team == 'A']
    team_B = [p for p in physicians if p.team == 'B']
    team_N = [p for p in physicians if p.team == 'N']

    # Helper function to check if physician can take more patients
    def can_take_patient(physician):
        return physician.total_patients < maximum_patients

    # Store initial stepdown counts for gained calculation
    initial_stepdown_counts = {p.name: p.step_down_patients for p in physicians}

    # Helper function to check if physician can take a step down patient
    def can_take_step_down(physician):
        initial_sd = initial_stepdown_counts.get(physician.name, 0)
        gained_stepdown = physician.step_down_patients - initial_sd
        return gained_stepdown < 1

    # ========== PHASE 1: Step-down allocation ==========
    # Team B first, then Team A
    # Step-down patients do NOT count towards total new patient pools

    working_team_B = [p for p in team_B if p.is_working]
    working_team_A = [p for p in team_A if p.is_working]

    # Sort Team B physicians by INITIAL StepDown count (lowest to highest)
    team_B_sorted = sorted(working_team_B, key=lambda x: initial_stepdown_counts.get(x.name, x.step_down_patients))

    # Distribute step-down patients to Team B physicians in sorted order
    for physician in team_B_sorted:
        if n_step_down_patients <= 0:
            break
        if can_take_step_down(physician):
            physician.add_patient(is_step_down=True)
            n_step_down_patients -= 1

    # If there are still step-down patients remaining, distribute to Team A
    if n_step_down_patients > 0:
        team_A_sorted = sorted(working_team_A, key=lambda x: initial_stepdown_counts.get(x.name, x.step_down_patients))

        for physician in team_A_sorted:
            if n_step_down_patients <= 0:
                break
            if can_take_step_down(physician):
                physician.add_patient(is_step_down=True)
                n_step_down_patients -= 1

    # ========== PHASE 2: Fix below-minimum physicians ==========
    # Fix physicians who are more than 1 less than the minimum value
    # EXCLUDE new physicians - they will be handled in the next phase
    threshold = minimum_patients - 2
    for physician in physicians:
        if physician.is_new:
            continue
        if physician.total_patients <= threshold and can_take_patient(physician):
            needed = minimum_patients - physician.total_patients
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

    # ========== PHASE 3: Fill new physicians to new_start_number ==========
    # New physicians get exactly new_start_number patients (if below) or 0 (if at/above)
    for physician in physicians:
        if physician.is_new:
            needed = new_start_number - physician.total_patients
            if needed <= 0:
                continue

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

                if not allocated:
                    break

    # ========== PHASE 4: Even distribution ==========
    # Distribute remaining patients with pattern-based allocation
    non_new_physicians = [p for p in physicians if not p.is_new and can_take_patient(p)]
    non_new_physicians = [p for p in non_new_physicians if not p.is_new]  # Double-check

    current_gains = {p.name: p.total_patients - initial_counts[p.name] for p in non_new_physicians}

    # FIRST: Allocate Team N Pool to Team N physicians (priority)
    team_N_non_new = [p for p in team_N if not p.is_new and can_take_patient(p)]
    if team_N_non_new and n_N_new_patients > 0:
        team_N_sorted = sorted(team_N_non_new, key=lambda x: x.total_patients)
        for physician in team_N_sorted:
            if n_N_new_patients <= 0:
                break
            if can_take_patient(physician):
                physician.add_patient()
                n_N_new_patients -= 1
                n_total_new_patients -= 1
                current_gains[physician.name] = current_gains.get(physician.name, 0) + 1

    # Recalculate current gains
    current_gains = {p.name: p.total_patients - initial_counts[p.name] for p in non_new_physicians}

    remaining_patients = n_A_new_patients + n_B_new_patients + n_N_new_patients

    if remaining_patients > 0 and non_new_physicians:
        num_physicians = len(non_new_physicians)

        if num_physicians > 0:
            # Sort physicians by INITIAL patient count (lowest first)
            sorted_physicians = sorted(non_new_physicians, key=lambda x: (
                initial_counts.get(x.name, x.total_patients),
                x.total_patients
            ))

            target_additional_gains = {p.name: 0 for p in sorted_physicians}
            patients_to_distribute = remaining_patients

            if num_physicians > remaining_patients:
                # Fewer patients than physicians: Give +1 to each in cycles
                while patients_to_distribute > 0:
                    sorted_by_additional = sorted(sorted_physicians, key=lambda x: (
                        target_additional_gains.get(x.name, 0),
                        initial_counts.get(x.name, x.total_patients),
                        x.total_patients
                    ))
                    for physician in sorted_by_additional:
                        if patients_to_distribute <= 0:
                            break
                        target_additional_gains[physician.name] = target_additional_gains.get(physician.name, 0) + 1
                        patients_to_distribute -= 1
            else:
                # More or equal patients than physicians: Give +1 to all first
                for physician in sorted_physicians:
                    if patients_to_distribute <= 0:
                        break
                    target_additional_gains[physician.name] = target_additional_gains.get(physician.name, 0) + 1
                    patients_to_distribute -= 1

                while patients_to_distribute > 0:
                    sorted_by_additional = sorted(sorted_physicians, key=lambda x: (
                        target_additional_gains.get(x.name, 0),
                        initial_counts.get(x.name, x.total_patients),
                        x.total_patients
                    ))
                    for physician in sorted_by_additional:
                        if patients_to_distribute <= 0:
                            break
                        target_additional_gains[physician.name] = target_additional_gains.get(physician.name, 0) + 1
                        patients_to_distribute -= 1

            # Calculate target total gains
            total_current_gains_sum = sum(current_gains.get(p.name, 0) for p in sorted_physicians)
            total_final_gains_needed = total_current_gains_sum + remaining_patients

            base_final_gain = total_final_gains_needed // num_physicians
            remainder_final = total_final_gains_needed % num_physicians

            target_total_gains = {}
            for i, physician in enumerate(sorted_physicians):
                if i < remainder_final:
                    target_total_gains[physician.name] = base_final_gain + 1
                else:
                    target_total_gains[physician.name] = base_final_gain

            # Recalculate target_additional_gains based on normalized targets
            for physician in sorted_physicians:
                current_gain = current_gains.get(physician.name, 0)
                target_total = target_total_gains.get(physician.name, 0)
                target_additional_gains[physician.name] = max(0, target_total - current_gain)

            # Distribute patients according to targets
            remaining_after_targets = n_A_new_patients + n_B_new_patients + n_N_new_patients
            max_iterations = remaining_after_targets * 3
            iteration = 0

            while remaining_after_targets > 0 and iteration < max_iterations:
                iteration += 1
                made_progress = False

                for physician in sorted_physicians:
                    if physician.is_new:
                        continue

                    target_total_gain = target_total_gains.get(physician.name, 0)
                    actual_current_gain = physician.total_patients - initial_counts[physician.name]
                    needed = target_total_gain - actual_current_gain

                    if needed <= 0 or not can_take_patient(physician):
                        continue

                    # Try to allocate from physician's own team pool first
                    if physician.team == 'A' and n_A_new_patients > 0:
                        if can_take_patient(physician) and actual_current_gain < target_total_gain:
                            physician.add_patient()
                            n_A_new_patients -= 1
                            n_total_new_patients -= 1
                            remaining_after_targets -= 1
                            current_gains[physician.name] = physician.total_patients - initial_counts[physician.name]
                            made_progress = True
                            continue
                    elif physician.team == 'B' and n_B_new_patients > 0:
                        if can_take_patient(physician) and actual_current_gain < target_total_gain:
                            physician.add_patient()
                            n_B_new_patients -= 1
                            n_total_new_patients -= 1
                            remaining_after_targets -= 1
                            current_gains[physician.name] = physician.total_patients - initial_counts[physician.name]
                            made_progress = True
                            continue
                    elif physician.team == 'N' and n_N_new_patients > 0:
                        if can_take_patient(physician) and actual_current_gain < target_total_gain:
                            physician.add_patient()
                            n_N_new_patients -= 1
                            n_total_new_patients -= 1
                            remaining_after_targets -= 1
                            current_gains[physician.name] = physician.total_patients - initial_counts[physician.name]
                            made_progress = True
                            continue

                    # If own team pool exhausted, try other pools
                    actual_current_gain = physician.total_patients - initial_counts[physician.name]
                    if actual_current_gain < target_total_gain and can_take_patient(physician):
                        can_use_other_pools = (physician.is_buffer or
                                             (physician.team == 'A' and n_A_new_patients == 0) or
                                             (physician.team == 'B' and n_B_new_patients == 0) or
                                             (physician.team == 'N' and n_N_new_patients == 0))

                        if can_use_other_pools:
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

                if not made_progress:
                    break

                remaining_after_targets = n_A_new_patients + n_B_new_patients + n_N_new_patients

            # Final pass: Distribute any remaining patients
            remaining_final = n_A_new_patients + n_B_new_patients + n_N_new_patients
            if remaining_final > 0:
                sorted_by_need = sorted(sorted_physicians, key=lambda x: (
                    target_total_gains.get(x.name, 0) - (x.total_patients - initial_counts[x.name]),
                    x.total_patients
                ), reverse=True)

                for physician in sorted_by_need:
                    if physician.is_new:
                        continue

                    if remaining_final <= 0:
                        break
                    target = target_total_gains.get(physician.name, 0)
                    actual_gain = physician.total_patients - initial_counts[physician.name]
                    needed = target - actual_gain

                    if needed <= 0 or not can_take_patient(physician):
                        continue

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

    # ========== PHASE 5: Final verification ==========
    # Ensure new physicians who started at/above new_start_number have gained 0 patients
    for physician in physicians:
        if physician.is_new:
            initial_total = initial_counts.get(physician.name, physician.total_patients)
            current_total = physician.total_patients
            gained = current_total - initial_total

            if initial_total >= new_start_number:
                if gained > 0:
                    excess = gained
                    for _ in range(excess):
                        physician.remove_patient()
                    physician.set_total_patients(initial_total)

    # Calculate results with gains
    results = []
    for physician in physicians:
        original_total = initial_counts.get(physician.name, 0)
        original_stepdown = initial_stepdown_counts.get(physician.name, 0)
        gained = physician.total_patients - original_total
        gained_stepdown = physician.step_down_patients - original_stepdown

        results.append({
            "name": physician.name,
            "yesterday": physician.yesterday,
            "team": physician.team,
            "is_new": physician.is_new,
            "is_buffer": physician.is_buffer,
            "is_working": physician.is_working,
            "original_total_patients": original_total,
            "total_patients": physician.total_patients,
            "original_step_down": original_stepdown,
            "step_down_patients": physician.step_down_patients,
            "transferred_patients": physician.transferred_patients,
            "traded_patients": physician.traded_patients,
            "gained": gained,
            "gained_step_down": gained_stepdown,
            "gained_plus_traded": gained + physician.traded_patients
        })

    # Calculate summary statistics
    team_a_results = [r for r in results if r["team"] == "A"]
    team_b_results = [r for r in results if r["team"] == "B"]
    team_n_results = [r for r in results if r["team"] == "N"]

    summary = {
        "team_a_total": sum(r["total_patients"] for r in team_a_results),
        "team_b_total": sum(r["total_patients"] for r in team_b_results),
        "team_n_total": sum(r["total_patients"] for r in team_n_results),
        "team_a_gained": sum(r["gained"] for r in team_a_results),
        "team_b_gained": sum(r["gained"] for r in team_b_results),
        "team_n_gained": sum(r["gained"] for r in team_n_results),
        "team_a_stepdown_gained": sum(r["gained_step_down"] for r in team_a_results),
        "team_b_stepdown_gained": sum(r["gained_step_down"] for r in team_b_results),
        "team_n_stepdown_gained": sum(r["gained_step_down"] for r in team_n_results),
        "team_a_traded": sum(r["traded_patients"] for r in team_a_results),
        "team_b_traded": sum(r["traded_patients"] for r in team_b_results),
        "total_census": sum(r["total_patients"] for r in results),
        "total_stepdown": sum(r["step_down_patients"] for r in results),
        "total_gained": sum(r["gained"] for r in results)
    }

    return {
        "results": results,
        "summary": summary,
        "remaining_pools": {
            "n_total_new_patients": n_total_new_patients,
            "n_A_new_patients": n_A_new_patients,
            "n_B_new_patients": n_B_new_patients,
            "n_N_new_patients": n_N_new_patients,
            "n_step_down_patients": n_step_down_patients
        }
    }
