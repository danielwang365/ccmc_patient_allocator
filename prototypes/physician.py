class Physician():
    def __init__(self, 
            name : str = "", 
            is_new : bool = False, 
            team : str = 'A', 
            n_total_patients : int = 0, 
            n_step_down_patients : int = 0, 
            n_transferred_patients : int = 0, 
            n_traded_patients : int = 0):
        
        self.name = name
        self.is_new : bool = is_new
        self.team : str = team

        self.total_patients : int = n_total_patients
        self.step_down_patients : int = n_step_down_patients

        self.transferred_patients : int = n_transferred_patients
        self.traded_patients : int = n_traded_patients

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



if __name__ == "__main__":

    n_total_new_patients = 32
    n_A_new_patients = 18
    n_B_new_patients = 13
    n_N_new_patients = 1

    n_A_physicians = 5
    n_B_physicians = 5
    n_N_physicians = 1

    A_team = []
    B_team = []

    new_start_number = 14
    
    for _ in range(n_A_physicians):
        A_team.append(Physician())

    for _ in range(n_B_physicians):
        B_team.append(Physician())


    A1 = Physician()

    print(A1.total_patients)
    print(A1.step_down_patients)



