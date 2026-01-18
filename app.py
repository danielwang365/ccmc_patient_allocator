"""
Flask application for the Patient Allocator.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
import config
from models import Physician
from data_manager import (
    load_physicians, save_physicians,
    load_yesterday, save_yesterday,
    load_master_list, save_master_list,
    load_parameters, save_parameters,
    load_selected, save_selected,
    load_team_assignments, save_team_assignments
)
from allocation import allocate_patients

app = Flask(__name__)
app.secret_key = config.SECRET_KEY


def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            if request.is_json:
                return jsonify({'error': 'Not authenticated'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Auth routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == config.APP_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout and redirect to login."""
    session.pop('logged_in', None)
    return redirect(url_for('login'))


# Main routes
@app.route('/')
@login_required
def index():
    """Main application page."""
    return render_template('index.html')


# Physician API routes
@app.route('/api/physicians', methods=['GET'])
@login_required
def get_physicians():
    """Get all physicians."""
    physicians = load_physicians()
    return jsonify([p.to_dict() for p in physicians])


@app.route('/api/physicians', methods=['POST'])
@login_required
def create_physician():
    """Create a new physician."""
    data = request.json
    physicians = load_physicians()

    new_physician = Physician(
        name=data.get('name', ''),
        yesterday=data.get('yesterday', ''),
        team=data.get('team', 'A'),
        is_new=data.get('is_new', False),
        is_buffer=data.get('is_buffer', False),
        is_working=data.get('is_working', True),
        total_patients=data.get('total_patients', 0),
        step_down_patients=data.get('step_down_patients', 0),
        transferred_patients=data.get('transferred_patients', 0),
        traded_patients=data.get('traded_patients', 0),
    )

    physicians.append(new_physician)
    save_physicians(physicians)
    return jsonify(new_physician.to_dict()), 201


@app.route('/api/physicians/<name>', methods=['PUT'])
@login_required
def update_physician(name):
    """Update a physician."""
    data = request.json
    physicians = load_physicians()

    for i, p in enumerate(physicians):
        if p.name == name:
            physicians[i] = Physician(
                name=data.get('name', p.name),
                yesterday=data.get('yesterday', p.yesterday),
                team=data.get('team', p.team),
                is_new=data.get('is_new', p.is_new),
                is_buffer=data.get('is_buffer', p.is_buffer),
                is_working=data.get('is_working', p.is_working),
                total_patients=data.get('total_patients', p.total_patients),
                step_down_patients=data.get('step_down_patients', p.step_down_patients),
                transferred_patients=data.get('transferred_patients', p.transferred_patients),
                traded_patients=data.get('traded_patients', p.traded_patients),
            )
            save_physicians(physicians)
            return jsonify(physicians[i].to_dict())

    return jsonify({'error': 'Physician not found'}), 404


@app.route('/api/physicians/<name>', methods=['DELETE'])
@login_required
def delete_physician(name):
    """Delete a physician."""
    physicians = load_physicians()
    physicians = [p for p in physicians if p.name != name]
    save_physicians(physicians)
    return jsonify({'success': True})


@app.route('/api/physicians/bulk', methods=['POST'])
@login_required
def bulk_update_physicians():
    """Bulk update all physicians."""
    data = request.json
    physicians = [
        Physician(
            name=p.get('name', ''),
            yesterday=p.get('yesterday', ''),
            team=p.get('team', 'A'),
            is_new=p.get('is_new', False),
            is_buffer=p.get('is_buffer', False),
            is_working=p.get('is_working', True),
            total_patients=p.get('total_patients', 0),
            step_down_patients=p.get('step_down_patients', 0),
            transferred_patients=p.get('transferred_patients', 0),
            traded_patients=p.get('traded_patients', 0),
        )
        for p in data
    ]
    save_physicians(physicians)
    return jsonify({'success': True, 'count': len(physicians)})


# Master list API routes
@app.route('/api/master-list', methods=['GET'])
@login_required
def get_master_list():
    """Get the master list of physicians."""
    return jsonify(load_master_list())


@app.route('/api/master-list', methods=['POST'])
@login_required
def add_to_master_list():
    """Add a physician to the master list."""
    data = request.json
    name = data.get('name', '').strip()

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    master_list = load_master_list()
    if name not in master_list:
        master_list.append(name)
        save_master_list(master_list)

    return jsonify({'master_list': master_list})


@app.route('/api/master-list/<name>', methods=['DELETE'])
@login_required
def remove_from_master_list(name):
    """Remove a physician from the master list."""
    master_list = load_master_list()
    master_list = [n for n in master_list if n != name]
    save_master_list(master_list)
    return jsonify({'master_list': master_list})


# Parameters API routes
@app.route('/api/parameters', methods=['GET'])
@login_required
def get_parameters():
    """Get allocation parameters."""
    return jsonify(load_parameters())


@app.route('/api/parameters', methods=['PUT'])
@login_required
def update_parameters():
    """Update allocation parameters."""
    data = request.json
    save_parameters(data)
    return jsonify(data)


# Yesterday API routes
@app.route('/api/yesterday', methods=['GET'])
@login_required
def get_yesterday():
    """Get yesterday's physicians."""
    return jsonify(load_yesterday())


@app.route('/api/yesterday', methods=['POST'])
@login_required
def save_yesterday_list():
    """Save yesterday's physicians."""
    data = request.json
    names = data.get('names', [])
    save_yesterday(names)
    return jsonify({'success': True, 'names': names})


# Selected API routes
@app.route('/api/selected', methods=['GET'])
@login_required
def get_selected():
    """Get selected physicians."""
    return jsonify(load_selected())


@app.route('/api/selected', methods=['POST'])
@login_required
def save_selected_list():
    """Save selected physicians."""
    data = request.json
    names = data.get('names', [])
    save_selected(names)
    return jsonify({'success': True, 'names': names})


# Team assignments API routes
@app.route('/api/team-assignments', methods=['GET'])
@login_required
def get_team_assignments():
    """Get team assignments."""
    return jsonify(load_team_assignments())


@app.route('/api/team-assignments', methods=['POST'])
@login_required
def save_team_assignments_route():
    """Save team assignments."""
    data = request.json
    assignments = data.get('assignments', {})
    save_team_assignments(assignments)
    return jsonify({'success': True, 'assignments': assignments})


# Generate table API route
@app.route('/api/generate-table', methods=['POST'])
@login_required
def generate_table():
    """Generate physician table from selections."""
    data = request.json
    selections = data.get('selections', [])
    yesterday_list = load_yesterday()

    physicians = []
    for sel in selections:
        name = sel.get('name', '')
        team = sel.get('team', 'A')
        was_yesterday = name in yesterday_list

        physicians.append(Physician(
            name=name,
            yesterday=name if was_yesterday else '',
            team=team,
            is_new=False,
            is_buffer=False,
            is_working=True,
            total_patients=0,
            step_down_patients=0,
            transferred_patients=0,
            traded_patients=0,
        ))

    save_physicians(physicians)
    return jsonify({'physicians': [p.to_dict() for p in physicians]})


# Allocation API route
@app.route('/api/allocate', methods=['POST'])
@login_required
def run_allocation():
    """Run the allocation algorithm."""
    data = request.json
    physician_data = data.get('physicians', [])
    parameters = data.get('parameters', {})

    # Convert to Physician objects
    physicians = [
        Physician(
            name=p.get('name', ''),
            yesterday=p.get('yesterday', ''),
            team=p.get('team', 'A'),
            is_new=p.get('is_new', False),
            is_buffer=p.get('is_buffer', False),
            is_working=p.get('is_working', True),
            total_patients=p.get('total_patients', 0),
            step_down_patients=p.get('step_down_patients', 0),
            transferred_patients=p.get('transferred_patients', 0),
            traded_patients=p.get('traded_patients', 0),
        )
        for p in physician_data
    ]

    # Run allocation
    try:
        results, summary = allocate_patients(physicians, parameters)
        return jsonify({
            'results': [r.to_dict() for r in results],
            'summary': summary,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Print summary API routes
@app.route('/api/print-summary', methods=['POST'])
@login_required
def get_print_summary():
    """Get print summary HTML."""
    data = request.json
    results = data.get('results', [])
    summary = data.get('summary', {})

    return render_template('print_summary.html',
                          results=results,
                          summary=summary)


@app.route('/api/print-summary/text', methods=['POST'])
@login_required
def get_print_summary_text():
    """Get print summary as plain text."""
    data = request.json
    results = data.get('results', [])

    # Group by team
    team_a = [r for r in results if r.get('team') == 'A']
    team_b = [r for r in results if r.get('team') == 'B']
    team_n = [r for r in results if r.get('team') == 'N']

    def format_team(team_name, team_data):
        lines = [f"=== Team {team_name} ==="]
        for r in sorted(team_data, key=lambda x: x.get('name', '')):
            lines.append(f"{r.get('name')}: {r.get('total_patients', 0)} patients, {r.get('step_down_patients', 0)} SD, Gained: {r.get('gained', 0)}")
        total = sum(r.get('total_patients', 0) for r in team_data)
        gained = sum(r.get('gained', 0) for r in team_data)
        lines.append(f"Team {team_name} Total: {total} patients, Gained: {gained}")
        return '\n'.join(lines)

    text_parts = []
    text_parts.append("PATIENT ALLOCATION SUMMARY")
    text_parts.append("=" * 40)

    if team_a:
        text_parts.append(format_team('A', team_a))
    if team_b:
        text_parts.append(format_team('B', team_b))
    if team_n:
        text_parts.append(format_team('N', team_n))

    # Grand total
    all_results = team_a + team_b + team_n
    grand_total = sum(r.get('total_patients', 0) for r in all_results)
    grand_gained = sum(r.get('gained', 0) for r in all_results)
    text_parts.append("=" * 40)
    text_parts.append(f"GRAND TOTAL: {grand_total} patients, Gained: {grand_gained}")

    return jsonify({'text': '\n\n'.join(text_parts)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
