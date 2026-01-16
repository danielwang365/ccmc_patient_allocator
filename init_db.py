"""
Database initialization script for CCMC Patient Allocator.
Creates tables and seeds default data.
Run this script before first deployment or to reset the database.
"""

from database import (
    init_database, get_db,
    MasterPhysician, Parameter, DefaultPhysician, DataVersion
)


# Default master list of all possible physicians
DEFAULT_MASTER_LIST = [
    "Adhlakha", "Wang", "Jaini", "JemJem", "Batth",
    "Rajarathinam", "Shehata", "Yousef", "Aung", "Bhogireddy",
    "Souliman", "Zaidi", "Attraplsi", "Ali", "Batlawala",
    "Sakkalaek", "Shirani", "Oladipo", "Abadi", "Kaur",
    "Narra", "Suman", "Lwin", "Das", "Alchi", "Reddy",
    "Hung", "Nwadei", "Lamba", "Ahir", "Mahajan", "Abukraa",
    "Keralos", "Nibber"
]

# Default physician configuration for demo
DEFAULT_PHYSICIANS = [
    {"name": "Abadi", "team": "A", "is_new": False, "is_buffer": False, "is_working": True, "total_patients": 9, "step_down_patients": 1, "traded_patients": 0},
    {"name": "Adhiakha", "team": "B", "is_new": False, "is_buffer": False, "is_working": True, "total_patients": 10, "step_down_patients": 2, "traded_patients": 0},
    {"name": "Ahir", "team": "A", "is_new": False, "is_buffer": False, "is_working": True, "total_patients": 10, "step_down_patients": 3, "traded_patients": 0},
    {"name": "Ali", "team": "B", "is_new": False, "is_buffer": False, "is_working": True, "total_patients": 6, "step_down_patients": 1, "traded_patients": 0},
    {"name": "Arora", "team": "A", "is_new": False, "is_buffer": False, "is_working": True, "total_patients": 12, "step_down_patients": 3, "traded_patients": 0},
    {"name": "Attrabala", "team": "B", "is_new": False, "is_buffer": False, "is_working": True, "total_patients": 9, "step_down_patients": 1, "traded_patients": 0},
    {"name": "Attrapisi", "team": "A", "is_new": False, "is_buffer": False, "is_working": True, "total_patients": 9, "step_down_patients": 3, "traded_patients": 0},
    {"name": "Aung", "team": "B", "is_new": False, "is_buffer": False, "is_working": True, "total_patients": 10, "step_down_patients": 0, "traded_patients": 0},
    {"name": "Batlawala", "team": "A", "is_new": False, "is_buffer": False, "is_working": True, "total_patients": 9, "step_down_patients": 2, "traded_patients": 0},
    {"name": "Batth", "team": "B", "is_new": False, "is_buffer": False, "is_working": True, "total_patients": 9, "step_down_patients": 2, "traded_patients": 0},
    {"name": "Bhogireddy", "team": "A", "is_new": False, "is_buffer": False, "is_working": True, "total_patients": 10, "step_down_patients": 2, "traded_patients": 0},
]


def seed_master_physicians():
    """Seed the master physician list."""
    with get_db() as db:
        existing = {p.name for p in db.query(MasterPhysician).all()}
        for name in DEFAULT_MASTER_LIST:
            if name not in existing:
                db.add(MasterPhysician(name=name, default_team='A'))
        print(f"Master physicians seeded: {len(DEFAULT_MASTER_LIST)} total")


def seed_default_parameters():
    """Seed default allocation parameters."""
    with get_db() as db:
        existing = db.query(Parameter).filter(Parameter.name == 'default').first()
        if not existing:
            db.add(Parameter(
                name='default',
                n_total_new_patients=20,
                n_A_new_patients=10,
                n_B_new_patients=8,
                n_N_new_patients=2,
                n_step_down_patients=0,
                minimum_patients=10,
                maximum_patients=20,
                new_start_number=5
            ))
            print("Default parameters seeded")
        else:
            print("Default parameters already exist")


def seed_default_physicians():
    """Seed default physician configuration for demo/reset."""
    with get_db() as db:
        existing = db.query(DefaultPhysician).count()
        if existing == 0:
            for phys in DEFAULT_PHYSICIANS:
                db.add(DefaultPhysician(**phys))
            print(f"Default physicians seeded: {len(DEFAULT_PHYSICIANS)} total")
        else:
            print(f"Default physicians already exist: {existing} records")


def seed_data_version():
    """Initialize data version for conflict detection."""
    with get_db() as db:
        existing = db.query(DataVersion).first()
        if not existing:
            db.add(DataVersion(id=1, version=1))
            print("Data version initialized")
        else:
            print(f"Data version already exists: v{existing.version}")


def main():
    """Initialize database and seed all default data."""
    print("Initializing database...")
    init_database()
    print("Database tables created")

    print("\nSeeding default data...")
    seed_master_physicians()
    seed_default_parameters()
    seed_default_physicians()
    seed_data_version()

    print("\nDatabase initialization complete!")


if __name__ == "__main__":
    main()
