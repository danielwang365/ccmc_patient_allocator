from flask import Flask, render_template, request, jsonify
from physician import Physician

app = Flask(__name__)

# In-memory storage for physicians
physicians: dict[str, Physician] = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/physicians', methods=['GET'])
def get_physicians():
    """Get all physicians"""
    return jsonify([
        {
            'id': pid,
            'name': p.name,
            'team': p.team,
            'is_new': p.is_new,
            'total_patients': p.total_patients,
            'step_down_patients': p.step_down_patients
        }
        for pid, p in physicians.items()
    ])

@app.route('/api/physicians', methods=['POST'])
def add_physician():
    """Add a new physician"""
    data = request.json
    name = data.get('name', '').strip()
    team = data.get('team', 'A')
    is_new = data.get('is_new', False)
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    # Generate a simple ID
    pid = f"{team}_{len([p for p in physicians.values() if p.team == team]) + 1}"
    
    physician = Physician(name=name, team=team, is_new=is_new)
    physicians[pid] = physician
    
    return jsonify({
        'id': pid,
        'name': physician.name,
        'team': physician.team,
        'is_new': physician.is_new,
        'total_patients': physician.total_patients,
        'step_down_patients': physician.step_down_patients
    }), 201

@app.route('/api/physicians/<pid>/add-patient', methods=['POST'])
def add_patient_to_physician(pid):
    """Add a patient to a physician"""
    if pid not in physicians:
        return jsonify({'error': 'Physician not found'}), 404
    
    data = request.json or {}
    is_step_down = data.get('is_step_down', False)
    
    physician = physicians[pid]
    physician.add_patient(is_step_down=is_step_down)
    
    return jsonify({
        'id': pid,
        'name': physician.name,
        'team': physician.team,
        'total_patients': physician.total_patients,
        'step_down_patients': physician.step_down_patients
    })

@app.route('/api/physicians/<pid>/remove-patient', methods=['POST'])
def remove_patient_from_physician(pid):
    """Remove a patient from a physician"""
    if pid not in physicians:
        return jsonify({'error': 'Physician not found'}), 404
    
    data = request.json or {}
    is_step_down = data.get('is_step_down', False)
    
    physician = physicians[pid]
    try:
        physician.remove_patient(is_step_down=is_step_down)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    return jsonify({
        'id': pid,
        'name': physician.name,
        'team': physician.team,
        'total_patients': physician.total_patients,
        'step_down_patients': physician.step_down_patients
    })

@app.route('/api/physicians/<pid>', methods=['DELETE'])
def delete_physician(pid):
    """Delete a physician"""
    if pid not in physicians:
        return jsonify({'error': 'Physician not found'}), 404
    
    del physicians[pid]
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

