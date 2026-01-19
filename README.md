# Patient Allocator

A web application for allocating patients to physicians in a hospital setting. Designed to distribute new patients fairly across working physicians based on their current patient loads, team assignments, and configurable allocation parameters.

## Features

- **Password-Protected Access** - Secure login to protect patient allocation data
- **Master Physician List** - Maintain a list of all physicians that can be selected for daily allocation
- **Team-Based Organization** - Organize physicians into teams (A, B, N) with easy team switching
- **Yesterday Tracking** - Track which physicians worked yesterday for continuity
- **Excel-Like Data Entry** - AG Grid provides spreadsheet-style editing with keyboard navigation
- **Flexible Allocation Parameters** - Configure patient pools per team, minimums, maximums, and step-down patients
- **Automatic Patient Distribution** - Algorithm distributes patients fairly using round-robin allocation
- **Step-Down Allocation** - Special handling for step-down patients with team-aware distribution
- **Results Summary** - View detailed allocation results with team breakdowns and statistics
- **Print Summary** - Generate printable allocation summaries
- **Data Persistence** - All data saved automatically and persists across sessions

## How to Use

### 1. Login
Enter the password to access the application.

### 2. Select Working Physicians
- View all physicians organized by team (A, B, N)
- Check the boxes next to physicians who are working today
- Green highlighting indicates physicians who worked yesterday
- Use team buttons (A, B, N) to move physicians between teams
- Click **Add Selected to Table** to add checked physicians to the data table

### 3. Enter Physician Data
In the Physician Data Table, enter for each physician:
- **Yesterday** - Name of physician whose patients they're inheriting
- **Team** - A, B, or N
- **New Physician** - Check if this is a new physician
- **Buffer** - Check if this is a buffer physician
- **Working** - Whether the physician is working
- **Total Patients** - Current patient count
- **StepDown** - Step-down patient count
- **Traded** - Patients traded from other teams

### 4. Set Allocation Parameters
In the sidebar, configure:
- **Total New Patients** - Total patients to distribute (informational)
- **Team A Pool** - New patients for Team A (default: 10)
- **Team B Pool** - New patients for Team B (default: 8)
- **Team N Pool** - New patients for Team N (default: 2)
- **Step Down Patients** - Step-down patients to allocate
- **Minimum Total** - Minimum patients per physician
- **Maximum Total** - Maximum patients per physician
- **New Start Number** - Target patient count for new physicians

### 5. Run Allocation
Click **Run Allocation** to distribute patients. The algorithm:
1. Allocates to new physicians until they reach the start number
2. Distributes remaining patients via round-robin to non-new physicians
3. Allocates step-down patients based on team gained+traded formula
4. Redistributes if any physician is below minimum

### 6. View Results
The results section shows:
- Team breakdowns (total patients, gained, step-down, traded)
- Gain analysis and distribution
- Trade summary between teams
- Detailed results table for each physician

### 7. Save Yesterday
Click **Save Current as Yesterday** to save today's working physicians for tomorrow's reference.

## Installation

### Prerequisites
- Python 3.9+
- pip

### Local Setup

```bash
# Clone the repository
git clone https://github.com/danielwang365/ccmc_patient_allocator.git
cd ccmc_patient_allocator

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The application will be available at `http://localhost:5000`

### Deployment (Railway)

The application is configured for Railway deployment:
- `Procfile` specifies gunicorn as the web server
- `railway.toml` contains Railway-specific configuration

## Configuration

Environment variables (can be set in `.env` file):

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session secret key | `dev-secret-key-change-in-production` |
| `APP_PASSWORD` | Login password | `CRMCPATIENTS` |

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Data Grid**: AG Grid Community Edition
- **Data Storage**: CSV files
- **Deployment**: Gunicorn, Railway

## Data Files

All data is stored in CSV files in the application directory:
- `physician_data.csv` - Current physician table data
- `yesterday_physicians.csv` - Physicians who worked yesterday
- `master_physician_list.csv` - Master list of all physicians
- `team_assignments.csv` - Team assignments for physicians
- `default_parameters.csv` - Saved allocation parameters

## License

Private - CRMC Hospital Use Only
