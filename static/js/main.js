/**
 * Main application logic for the Patient Allocator
 */

// Global state
let physicianGridApi = null;
let resultsGridApi = null;
let masterList = [];
let selectedPhysicians = [];
let teamAssignments = {};
let yesterdayPhysicians = [];
let currentResults = null;
let currentSummary = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', async () => {
    await initializeApp();
});

async function initializeApp() {
    // Load initial data
    await Promise.all([
        loadMasterList(),
        loadYesterday(),
        loadParameters(),
        loadPhysicians(),
    ]);

    // Initialize grids
    initializePhysicianGrid();
    initializeResultsGrid();

    // Setup event listeners
    setupEventListeners();

    // Render master list
    renderMasterList();
    renderMasterListManage();
}

// Load master list
async function loadMasterList() {
    masterList = await API.getMasterList();
    const selected = await API.getSelected();
    selectedPhysicians = selected || [];

    // Load saved team assignments first
    const savedAssignments = await API.getTeamAssignments();
    if (savedAssignments && Object.keys(savedAssignments).length > 0) {
        teamAssignments = savedAssignments;
    }

    // Also check current physicians for any not in saved assignments
    const physicians = await API.getPhysicians();
    physicians.forEach(p => {
        if (p.name && !teamAssignments[p.name]) {
            teamAssignments[p.name] = p.team || 'A';
        }
    });
}

// Load yesterday's physicians
async function loadYesterday() {
    yesterdayPhysicians = await API.getYesterday() || [];
    updateYesterdayDisplay();
}

// Update yesterday display
function updateYesterdayDisplay() {
    const container = document.getElementById('yesterdayInfo');
    if (container) {
        container.innerHTML = yesterdayPhysicians.length > 0
            ? `<strong>Yesterday (${yesterdayPhysicians.length}):</strong> ${yesterdayPhysicians.join(', ')}`
            : '<em>No data available</em>';
    }
}

// Load parameters
async function loadParameters() {
    const params = await API.getParameters();
    if (params) {
        const setVal = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.value = val;
        };
        setVal('n_total_new_patients', params.n_total_new_patients || 20);
        setVal('n_step_down_patients', params.n_step_down_patients || 0);
        setVal('minimum_total', params.minimum_patients || 10);
        setVal('maximum_total', params.maximum_patients || 14);
        setVal('new_start_number', params.new_start_number || 10);
        setVal('buffer_start_number', params.buffer_start_number || 12);
        setVal('non_new_start_number', params.non_new_start_number || 12);
        setVal('maximum_step_down', params.maximum_step_down || 4);
    }
}

// Load physicians
async function loadPhysicians() {
    const physicians = await API.getPhysicians();
    if (physicianGridApi && physicians) {
        physicianGridApi.setGridOption('rowData', physicians);
    }
}

// Initialize physician grid
function initializePhysicianGrid() {
    const debouncedSave = debounce(async (params) => {
        const rowData = [];
        physicianGridApi.forEachNode(node => rowData.push(node.data));
        await API.bulkUpdatePhysicians(rowData);
        showSaveIndicator();
    }, 500);

    physicianGridApi = createPhysicianGrid('physicianGrid', debouncedSave);

    // Load initial data
    loadPhysicians();
}

// Initialize results grid
function initializeResultsGrid() {
    resultsGridApi = createResultsGrid('resultsGrid', async (params) => {
        // Recalculate gained values when editable fields change
        if (['total_patients', 'step_down_patients', 'transferred_patients', 'traded_patients'].includes(params.column.getColId())) {
            const data = params.data;
            data.gained = data.total_patients - data.original_total_patients;
            data.gained_step_down = data.step_down_patients - data.original_step_down;
            data.gained_plus_traded = data.gained + data.traded_patients;
            params.api.refreshCells({ rowNodes: [params.node] });
            updateSummary();
        }
    });
}

// Render master list checkboxes - segregated by team
function renderMasterList() {
    const containerA = document.getElementById('masterListTeamA');
    const containerB = document.getElementById('masterListTeamB');
    const containerN = document.getElementById('masterListTeamN');

    if (!containerA || !containerB || !containerN) return;

    containerA.innerHTML = '';
    containerB.innerHTML = '';
    containerN.innerHTML = '';

    let countA = 0, countB = 0, countN = 0;

    masterList.forEach(name => {
        const isChecked = selectedPhysicians.includes(name);
        const team = teamAssignments[name] || 'A';
        const wasYesterday = yesterdayPhysicians.includes(name);

        const item = document.createElement('div');
        item.className = 'master-list-item';
        if (wasYesterday) item.classList.add('yesterday');
        if (isChecked) item.classList.add('selected');

        // Determine which buttons to show based on current team
        let moveButtons = '';
        if (team === 'A') {
            moveButtons = `
                <button class="move-team-btn" data-target="B" title="Move to Team B">→B</button>
                <button class="move-team-btn" data-target="N" title="Move to Team N">→N</button>
            `;
        } else if (team === 'B') {
            moveButtons = `
                <button class="move-team-btn" data-target="A" title="Move to Team A">→A</button>
                <button class="move-team-btn" data-target="N" title="Move to Team N">→N</button>
            `;
        } else {
            moveButtons = `
                <button class="move-team-btn" data-target="A" title="Move to Team A">→A</button>
                <button class="move-team-btn" data-target="B" title="Move to Team B">→B</button>
            `;
        }

        item.innerHTML = `
            <input type="checkbox" id="check_${name}" ${isChecked ? 'checked' : ''}>
            <label for="check_${name}">${name}</label>
            ${moveButtons}
        `;

        // Checkbox change handler
        const checkbox = item.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', () => {
            if (checkbox.checked) {
                if (!selectedPhysicians.includes(name)) {
                    selectedPhysicians.push(name);
                }
                item.classList.add('selected');
            } else {
                selectedPhysicians = selectedPhysicians.filter(n => n !== name);
                item.classList.remove('selected');
            }
            updateSelectedCounts();
        });

        // Move team button handlers
        item.querySelectorAll('.move-team-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const targetTeam = btn.dataset.target;
                teamAssignments[name] = targetTeam;
                // Save team assignments to backend
                await API.saveTeamAssignments(teamAssignments);
                showSaveIndicator('Team updated!');
                renderMasterList(); // Re-render to move item to new column
            });
        });

        // Add to appropriate container and count
        if (team === 'A') {
            containerA.appendChild(item);
            if (isChecked) countA++;
        } else if (team === 'B') {
            containerB.appendChild(item);
            if (isChecked) countB++;
        } else {
            containerN.appendChild(item);
            if (isChecked) countN++;
        }
    });

    // Update selected counts
    document.getElementById('teamASelectedCount').textContent = `${countA} selected`;
    document.getElementById('teamBSelectedCount').textContent = `${countB} selected`;
    document.getElementById('teamNSelectedCount').textContent = `${countN} selected`;
}

// Update selected counts display
function updateSelectedCounts() {
    let countA = 0, countB = 0, countN = 0;
    selectedPhysicians.forEach(name => {
        const team = teamAssignments[name] || 'A';
        if (team === 'A') countA++;
        else if (team === 'B') countB++;
        else countN++;
    });
    document.getElementById('teamASelectedCount').textContent = `${countA} selected`;
    document.getElementById('teamBSelectedCount').textContent = `${countB} selected`;
    document.getElementById('teamNSelectedCount').textContent = `${countN} selected`;
}

// Setup event listeners
function setupEventListeners() {
    // Generate table button
    document.getElementById('generateTableBtn')?.addEventListener('click', generateTable);

    // Select all / Deselect all buttons
    document.getElementById('selectAllBtn')?.addEventListener('click', selectAll);
    document.getElementById('deselectAllBtn')?.addEventListener('click', uncheckAll);

    // Add physician button - opens modal
    document.getElementById('addPhysicianBtn')?.addEventListener('click', () => {
        if (typeof openAddPhysicianModal === 'function') {
            openAddPhysicianModal();
        } else {
            addPhysician();
        }
    });

    // Delete physician button
    document.getElementById('deletePhysicianBtn')?.addEventListener('click', deleteSelectedPhysician);

    // Run allocation button
    document.getElementById('runAllocationBtn')?.addEventListener('click', runAllocation);

    // Save yesterday button
    document.getElementById('saveYesterdayBtn')?.addEventListener('click', saveAsYesterday);

    // Add to master list button
    document.getElementById('addToMasterBtn')?.addEventListener('click', addToMasterList);

    // Print buttons
    document.getElementById('printSummaryBtn')?.addEventListener('click', openPrintPreview);
    document.getElementById('copySummaryBtn')?.addEventListener('click', copyTextSummary);
}

// Generate table from selection
async function generateTable() {
    console.log('generateTable called');
    console.log('selectedPhysicians:', selectedPhysicians);
    console.log('teamAssignments:', teamAssignments);

    const selections = selectedPhysicians.map(name => ({
        name,
        team: teamAssignments[name] || 'A',
    }));

    console.log('selections:', selections);

    if (selections.length === 0) {
        alert('Please select at least one physician.');
        return;
    }

    try {
        const result = await API.generateTable(selections);
        console.log('API result:', result);
        if (result && result.physicians) {
            physicianGridApi.setGridOption('rowData', result.physicians);
            showSaveIndicator('Table generated!');
        } else {
            console.error('No physicians in result:', result);
            alert('Error generating table. Check console for details.');
        }
    } catch (error) {
        console.error('Error in generateTable:', error);
        alert('Error generating table: ' + error.message);
    }
}

// Select all physicians in master list
function selectAll() {
    selectedPhysicians = [...masterList];
    renderMasterList();
    showSaveIndicator('All selected');
}

// Uncheck all physicians
function uncheckAll() {
    selectedPhysicians = [];
    renderMasterList();
    showSaveIndicator('All deselected');
}

// Delete selected physician from grid
async function deleteSelectedPhysician() {
    const selectedRows = physicianGridApi.getSelectedRows();
    if (selectedRows.length === 0) {
        alert('Please select a physician to delete.');
        return;
    }

    const name = selectedRows[0].name;
    if (!confirm(`Are you sure you want to delete ${name}?`)) {
        return;
    }

    await API.deletePhysician(name);
    await loadPhysicians();
    showSaveIndicator('Physician deleted!');
}

// Save current physicians as yesterday
async function saveAsYesterday() {
    const physicians = [];
    physicianGridApi.forEachNode(node => physicians.push(node.data));

    const names = physicians.map(p => p.name);
    await API.saveYesterday(names);

    yesterdayPhysicians = names;
    updateYesterdayDisplay();
    showSaveIndicator('Saved as yesterday!');
}

// Add physician manually
async function addPhysician() {
    const name = prompt('Enter physician name:');
    if (!name || !name.trim()) return;

    const team = prompt('Enter team (A, B, or N):', 'A');
    if (!['A', 'B', 'N'].includes(team?.toUpperCase())) {
        alert('Invalid team. Please enter A, B, or N.');
        return;
    }

    const newPhysician = {
        name: name.trim(),
        yesterday: '',
        team: team.toUpperCase(),
        is_new: false,
        is_buffer: false,
        is_working: true,
        total_patients: 0,
        step_down_patients: 0,
        transferred_patients: 0,
        traded_patients: 0,
    };

    await API.createPhysician(newPhysician);
    await loadPhysicians();
    showSaveIndicator('Physician added!');
}

// Add to master list
async function addToMasterList() {
    const input = document.getElementById('newMasterName');
    const name = input?.value?.trim();

    if (!name) {
        alert('Please enter a name.');
        return;
    }

    const result = await API.addToMasterList(name);
    if (result && result.master_list) {
        masterList = result.master_list;
        renderMasterList();
        renderMasterListManage();
        input.value = '';
        showSaveIndicator('Added to master list!');
    }
}

// Render master list management section
function renderMasterListManage() {
    const container = document.getElementById('masterListManage');
    if (!container) return;

    container.innerHTML = masterList.map(name => `
        <div class="master-list-manage-item">
            <span>${name}</span>
            <button onclick="removeFromMasterList('${name}')" title="Remove">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        </div>
    `).join('');
}

// Remove from master list
async function removeFromMasterList(name) {
    if (!confirm(`Remove ${name} from master list?`)) return;

    const result = await API.removeFromMasterList(name);
    if (result && result.master_list) {
        masterList = result.master_list;
        selectedPhysicians = selectedPhysicians.filter(n => n !== name);
        renderMasterList();
        renderMasterListManage();
        showSaveIndicator('Removed from master list!');
    }
}

// Run allocation
async function runAllocation() {
    const physicians = [];
    physicianGridApi.forEachNode(node => physicians.push(node.data));

    if (physicians.length === 0) {
        alert('No physicians in the table. Please add physicians first.');
        return;
    }

    const getVal = (id, def) => parseInt(document.getElementById(id)?.value) || def;
    const parameters = {
        n_total_new_patients: getVal('n_total_new_patients', 20),
        n_step_down_patients: getVal('n_step_down_patients', 0),
        minimum_patients: getVal('minimum_total', 10),
        maximum_patients: getVal('maximum_total', 14),
        new_start_number: getVal('new_start_number', 10),
        buffer_start_number: getVal('buffer_start_number', 12),
        non_new_start_number: getVal('non_new_start_number', 12),
        maximum_step_down: getVal('maximum_step_down', 4),
    };

    const result = await API.runAllocation(physicians, parameters);

    if (result && result.results) {
        currentResults = result.results;
        currentSummary = result.summary;

        // Update results grid
        resultsGridApi.setGridOption('rowData', result.results);

        // Update summary display
        updateSummary();

        // Show results section
        document.getElementById('resultsSection').style.display = 'block';

        // Scroll to results
        document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });

        showSaveIndicator('Allocation complete!');
    } else if (result && result.error) {
        alert('Error: ' + result.error);
    }
}

// Update summary display
function updateSummary() {
    // Recalculate from current results grid data
    const results = [];
    resultsGridApi.forEachNode(node => results.push(node.data));

    if (results.length === 0) return;

    const teamA = results.filter(r => r.team === 'A');
    const teamB = results.filter(r => r.team === 'B');
    const teamN = results.filter(r => r.team === 'N');

    // Calculate all summary values
    const summary = {
        team_a_total: teamA.reduce((sum, r) => sum + (r.total_patients || 0), 0),
        team_b_total: teamB.reduce((sum, r) => sum + (r.total_patients || 0), 0),
        team_n_total: teamN.reduce((sum, r) => sum + (r.total_patients || 0), 0),
        team_a_gained: teamA.reduce((sum, r) => sum + (r.gained || 0), 0),
        team_b_gained: teamB.reduce((sum, r) => sum + (r.gained || 0), 0),
        team_n_gained: teamN.reduce((sum, r) => sum + (r.gained || 0), 0),
        team_a_stepdown: teamA.reduce((sum, r) => sum + (r.gained_step_down || 0), 0),
        team_b_stepdown: teamB.reduce((sum, r) => sum + (r.gained_step_down || 0), 0),
        team_n_stepdown: teamN.reduce((sum, r) => sum + (r.gained_step_down || 0), 0),
        team_a_traded: teamA.reduce((sum, r) => sum + (r.traded_patients || 0), 0),
        team_b_traded: teamB.reduce((sum, r) => sum + (r.traded_patients || 0), 0),
        team_n_traded: teamN.reduce((sum, r) => sum + (r.traded_patients || 0), 0),
    };

    const totalTraded = summary.team_a_traded + summary.team_b_traded + summary.team_n_traded;
    const totalCensus = summary.team_a_total + summary.team_b_total + summary.team_n_total + totalTraded;
    const totalGained = summary.team_a_gained + summary.team_b_gained + summary.team_n_gained + totalTraded;

    currentSummary = summary;

    // Update Team Summary Cards
    const setVal = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };

    setVal('teamATotalPatients', summary.team_a_total);
    setVal('teamAGained', summary.team_a_gained);
    setVal('teamAStepDown', summary.team_a_stepdown);
    setVal('teamAGainedTraded', summary.team_a_gained + summary.team_b_traded);

    setVal('teamBTotalPatients', summary.team_b_total);
    setVal('teamBGained', summary.team_b_gained);
    setVal('teamBStepDown', summary.team_b_stepdown);
    setVal('teamBGainedTraded', summary.team_b_gained + summary.team_a_traded);

    setVal('teamNTotalPatients', summary.team_n_total);
    setVal('teamNGained', summary.team_n_gained);
    setVal('teamNStepDown', summary.team_n_stepdown);
    setVal('teamNGainedTraded', summary.team_n_gained);

    // Update Trade Summary
    setVal('teamATraded', summary.team_a_traded);
    setVal('teamBTraded', summary.team_b_traded);
    setVal('totalCensus', totalCensus);
    setVal('totalGainedYesterday', totalGained);

    // Update Gain Analysis
    const expectedTotal = parseInt(document.getElementById('n_total_new_patients')?.value) || 0;
    const gains = results.map(r => r.gained || 0);
    const minGain = Math.min(...gains);
    const maxGain = Math.max(...gains);

    setVal('totalGainedSum', results.reduce((sum, r) => sum + (r.gained || 0), 0));
    setVal('expectedTotal', expectedTotal);
    setVal('numPhysicians', results.length);
    setVal('gainRange', `${minGain} - ${maxGain}`);

    // Update Gain Distribution
    const gainCounts = {};
    gains.forEach(g => {
        gainCounts[g] = (gainCounts[g] || 0) + 1;
    });

    const distributionContainer = document.getElementById('gainDistribution');
    if (distributionContainer) {
        distributionContainer.innerHTML = Object.keys(gainCounts)
            .sort((a, b) => parseInt(a) - parseInt(b))
            .map(gain => `
                <div class="gain-distribution-item">
                    <span class="count">${gainCounts[gain]} physician(s)</span>
                    <span class="amount">gained ${gain} patient(s)</span>
                </div>
            `).join('');
    }

    // Update top summary stats
    const summaryContainer = document.getElementById('summaryStats');
    if (summaryContainer) {
        summaryContainer.innerHTML = `
            <div class="summary-card">
                <div class="summary-card-label">Total Census</div>
                <div class="summary-card-value" style="color: #667eea;">${totalCensus}</div>
            </div>
            <div class="summary-card">
                <div class="summary-card-label">Total Gained</div>
                <div class="summary-card-value" style="color: #059669;">${totalGained}</div>
            </div>
            <div class="summary-card">
                <div class="summary-card-label">Physicians</div>
                <div class="summary-card-value">${results.length}</div>
            </div>
            <div class="summary-card">
                <div class="summary-card-label">Team A</div>
                <div class="summary-card-value">${teamA.length}</div>
            </div>
            <div class="summary-card">
                <div class="summary-card-label">Team B</div>
                <div class="summary-card-value">${teamB.length}</div>
            </div>
            <div class="summary-card">
                <div class="summary-card-label">Team N</div>
                <div class="summary-card-value">${teamN.length}</div>
            </div>
        `;
    }
}

// Open print preview
async function openPrintPreview() {
    if (!currentResults) {
        alert('No results to print. Run allocation first.');
        return;
    }

    const results = [];
    resultsGridApi.forEachNode(node => results.push(node.data));

    // Group by team
    const teamA = results.filter(r => r.team === 'A').sort((a, b) => a.name.localeCompare(b.name));
    const teamB = results.filter(r => r.team === 'B').sort((a, b) => a.name.localeCompare(b.name));
    const teamN = results.filter(r => r.team === 'N').sort((a, b) => a.name.localeCompare(b.name));

    // Build print HTML
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Patient Allocation Summary</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                h1 { text-align: center; margin-bottom: 20px; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f5f5f5; font-weight: bold; }
                .team-header { background-color: #e0e0e0; font-weight: bold; }
                .subtotal { background-color: #f0f0f0; font-weight: bold; }
                .grand-total { background-color: #333; color: white; font-weight: bold; }
                @media print {
                    body { padding: 0; }
                    button { display: none; }
                }
            </style>
        </head>
        <body>
            <h1>Patient Allocation Summary</h1>
            <table>
                <thead>
                    <tr>
                        <th>Physician</th>
                        <th>Starting</th>
                        <th>Total</th>
                        <th>StepDown</th>
                        <th>New SD</th>
                        <th>New Patients</th>
                    </tr>
                </thead>
                <tbody>
                    ${generateTeamRows('A', teamA)}
                    ${generateTeamRows('B', teamB)}
                    ${generateTeamRows('N', teamN)}
                    ${generateGrandTotal([...teamA, ...teamB, ...teamN])}
                </tbody>
            </table>
            <button onclick="window.print()">Print</button>
        </body>
        </html>
    `);
    printWindow.document.close();
}

function generateTeamRows(team, data) {
    if (data.length === 0) return '';

    let html = `<tr class="team-header"><td colspan="6">Team ${team}</td></tr>`;

    let totalStart = 0, totalPatients = 0, totalSD = 0, totalNewSD = 0, totalNew = 0;

    data.forEach(r => {
        totalStart += r.original_total_patients || 0;
        totalPatients += r.total_patients || 0;
        totalSD += r.step_down_patients || 0;
        totalNewSD += r.gained_step_down || 0;
        totalNew += r.gained || 0;

        html += `
            <tr>
                <td>${r.name}</td>
                <td>${r.original_total_patients || 0}</td>
                <td>${r.total_patients || 0}</td>
                <td>${r.step_down_patients || 0}</td>
                <td>${r.gained_step_down || 0}</td>
                <td>${r.gained || 0}</td>
            </tr>
        `;
    });

    html += `
        <tr class="subtotal">
            <td>Subtotal Team ${team}</td>
            <td>${totalStart}</td>
            <td>${totalPatients}</td>
            <td>${totalSD}</td>
            <td>${totalNewSD}</td>
            <td>${totalNew}</td>
        </tr>
    `;

    return html;
}

function generateGrandTotal(data) {
    let totalStart = 0, totalPatients = 0, totalSD = 0, totalNewSD = 0, totalNew = 0;

    data.forEach(r => {
        totalStart += r.original_total_patients || 0;
        totalPatients += r.total_patients || 0;
        totalSD += r.step_down_patients || 0;
        totalNewSD += r.gained_step_down || 0;
        totalNew += r.gained || 0;
    });

    return `
        <tr class="grand-total">
            <td>GRAND TOTAL</td>
            <td>${totalStart}</td>
            <td>${totalPatients}</td>
            <td>${totalSD}</td>
            <td>${totalNewSD}</td>
            <td>${totalNew}</td>
        </tr>
    `;
}

// Copy text summary
async function copyTextSummary() {
    if (!currentResults) {
        alert('No results to copy. Run allocation first.');
        return;
    }

    const results = [];
    resultsGridApi.forEachNode(node => results.push(node.data));

    const response = await API.getPrintSummaryText(results);
    if (response && response.text) {
        await navigator.clipboard.writeText(response.text);
        showSaveIndicator('Copied to clipboard!');
    }
}
