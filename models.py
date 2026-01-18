"""
Physician data model for the Patient Allocator application.
"""

class Physician:
    def __init__(self,
            name: str = "",
            is_new: bool = False,
            team: str = 'A',
            n_total_patients: int = 0,
            n_step_down_patients: int = 0,
            n_transferred_patients: int = 0,
            n_traded_patients: int = 0,
            is_buffer: bool = False,
            is_working: bool = True,
            yesterday: str = ""):

        self.name = name
        self.is_new: bool = is_new
        self.team: str = team
        self.is_buffer: bool = is_buffer
        self.is_working: bool = is_working
        self.yesterday: str = yesterday

        self.total_patients: int = n_total_patients
        self.step_down_patients: int = n_step_down_patients

        self.transferred_patients: int = n_transferred_patients
        self.traded_patients: int = n_traded_patients

    def __repr__(self):
        return f"Physician({self.name}, {self.team}, {self.total_patients})"

    def add_patient(self, is_step_down: bool = False):
        """Add a patient. Step-down patients do NOT count towards total_patients."""
        if is_step_down:
            self.step_down_patients += 1
        else:
            self.total_patients += 1

    def remove_patient(self, is_step_down: bool = False):
        """Remove a patient. Step-down patients do NOT count towards total_patients."""
        if is_step_down:
            if self.step_down_patients < 1:
                raise Exception("You don't have any step-down patients")
            self.step_down_patients -= 1
        else:
            if self.total_patients < 1:
                raise Exception("You don't have any patients")
            self.total_patients -= 1

    def set_total_patients(self, n: int):
        self.total_patients = n

    def set_step_down_patients(self, n: int):
        self.step_down_patients = n

    def set_transferred_patient(self, n: int):
        self.transferred_patients = n

    def set_traded_patients(self, n: int):
        self.traded_patients = n

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "yesterday": self.yesterday,
            "team": self.team,
            "is_new": self.is_new,
            "is_buffer": self.is_buffer,
            "is_working": self.is_working,
            "total_patients": self.total_patients,
            "step_down_patients": self.step_down_patients,
            "transferred_patients": self.transferred_patients,
            "traded_patients": self.traded_patients
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create a Physician from a dictionary."""
        return cls(
            name=data.get("name", ""),
            yesterday=data.get("yesterday", ""),
            team=data.get("team", "A"),
            is_new=data.get("is_new", False),
            is_buffer=data.get("is_buffer", False),
            is_working=data.get("is_working", True),
            n_total_patients=data.get("total_patients", 0),
            n_step_down_patients=data.get("step_down_patients", 0),
            n_transferred_patients=data.get("transferred_patients", 0),
            n_traded_patients=data.get("traded_patients", 0)
        )
