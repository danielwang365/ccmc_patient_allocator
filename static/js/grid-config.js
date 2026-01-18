/**
 * AG Grid configuration for the Patient Allocator
 */

// Team cell renderer
function teamCellRenderer(params) {
    const team = params.value;
    const classes = {
        'A': 'team-badge team-badge-a',
        'B': 'team-badge team-badge-b',
        'N': 'team-badge team-badge-n',
    };
    return `<span class="${classes[team] || ''}">${team}</span>`;
}

// Checkbox cell renderer
function checkboxRenderer(params) {
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.checked = params.value === true;
    input.style.cssText = 'width: 18px; height: 18px; cursor: pointer; accent-color: #667eea;';

    input.addEventListener('change', () => {
        params.setValue(input.checked);
    });

    return input;
}

// Main physician table column definitions
const physicianColumnDefs = [
    {
        field: 'yesterday',
        headerName: 'Yesterday',
        editable: true,
        width: 120,
    },
    {
        field: 'name',
        headerName: 'Physician Name',
        editable: true,
        width: 150,
    },
    {
        field: 'team',
        headerName: 'Team',
        editable: true,
        width: 80,
        cellEditor: 'agSelectCellEditor',
        cellEditorParams: { values: ['A', 'B', 'N'] },
        cellRenderer: teamCellRenderer,
    },
    {
        field: 'is_new',
        headerName: 'New',
        width: 70,
        cellRenderer: checkboxRenderer,
        editable: false,
    },
    {
        field: 'is_buffer',
        headerName: 'Buffer',
        width: 80,
        cellRenderer: checkboxRenderer,
        editable: false,
    },
    {
        field: 'is_working',
        headerName: 'Working',
        width: 90,
        cellRenderer: checkboxRenderer,
        editable: false,
    },
    {
        field: 'total_patients',
        headerName: 'Total Patients',
        editable: true,
        width: 120,
        type: 'numericColumn',
        valueParser: params => Number(params.newValue) || 0,
    },
    {
        field: 'step_down_patients',
        headerName: 'StepDown',
        editable: true,
        width: 100,
        type: 'numericColumn',
        valueParser: params => Number(params.newValue) || 0,
    },
    {
        field: 'transferred_patients',
        headerName: 'Out of floor',
        editable: true,
        width: 110,
        type: 'numericColumn',
        valueParser: params => Number(params.newValue) || 0,
    },
    {
        field: 'traded_patients',
        headerName: 'Traded',
        editable: true,
        width: 90,
        type: 'numericColumn',
        valueParser: params => Number(params.newValue) || 0,
    },
];

// Results table column definitions
const resultsColumnDefs = [
    {
        field: 'name',
        headerName: 'Physician Name',
        width: 140,
        pinned: 'left',
    },
    {
        field: 'team',
        headerName: 'Team',
        width: 70,
        cellRenderer: teamCellRenderer,
    },
    {
        field: 'is_new',
        headerName: 'New',
        width: 60,
        cellRenderer: params => params.value ? 'Yes' : '',
    },
    {
        field: 'is_buffer',
        headerName: 'Buffer',
        width: 70,
        cellRenderer: params => params.value ? 'Yes' : '',
    },
    {
        field: 'original_total_patients',
        headerName: 'Original Total',
        width: 110,
        type: 'numericColumn',
    },
    {
        field: 'total_patients',
        headerName: 'Total Patients',
        width: 120,
        type: 'numericColumn',
        editable: true,
        valueParser: params => Number(params.newValue) || 0,
        cellStyle: { backgroundColor: '#f0f9ff' },
    },
    {
        field: 'original_step_down',
        headerName: 'Original SD',
        width: 100,
        type: 'numericColumn',
    },
    {
        field: 'step_down_patients',
        headerName: 'StepDown',
        width: 100,
        type: 'numericColumn',
        editable: true,
        valueParser: params => Number(params.newValue) || 0,
        cellStyle: { backgroundColor: '#f0f9ff' },
    },
    {
        field: 'transferred_patients',
        headerName: 'Out of floor',
        width: 100,
        type: 'numericColumn',
        editable: true,
        valueParser: params => Number(params.newValue) || 0,
        cellStyle: { backgroundColor: '#f0f9ff' },
    },
    {
        field: 'traded_patients',
        headerName: 'Traded',
        width: 80,
        type: 'numericColumn',
        editable: true,
        valueParser: params => Number(params.newValue) || 0,
        cellStyle: { backgroundColor: '#f0f9ff' },
    },
    {
        field: 'gained',
        headerName: 'Gained',
        width: 80,
        type: 'numericColumn',
        cellStyle: params => ({
            color: params.value > 0 ? '#059669' : '#6b7280',
            fontWeight: params.value > 0 ? '600' : '400',
        }),
    },
    {
        field: 'gained_step_down',
        headerName: 'Gained SD',
        width: 90,
        type: 'numericColumn',
        cellStyle: { backgroundColor: '#fef3c7' },
    },
    {
        field: 'gained_plus_traded',
        headerName: 'Gained + Traded',
        width: 130,
        type: 'numericColumn',
        cellStyle: { backgroundColor: '#fef3c7', fontWeight: '600' },
    },
];

// Default grid options
const defaultGridOptions = {
    defaultColDef: {
        sortable: true,
        filter: true,
        resizable: true,
        suppressMovable: true,
    },
    animateRows: true,
    rowSelection: 'single',
    suppressCellFocus: false,
    enableCellTextSelection: true,
    ensureDomOrder: true,
    // Keyboard navigation
    navigateToNextHeader: () => null,
    tabToNextHeader: () => null,
    navigateToNextCell: (params) => {
        const { key, previousCellPosition } = params;
        const { rowIndex, column } = previousCellPosition;
        const columns = params.api.getAllDisplayedColumns();
        const colIndex = columns.indexOf(column);

        switch (key) {
            case 'ArrowUp':
                return rowIndex > 0 ? { rowIndex: rowIndex - 1, column } : null;
            case 'ArrowDown':
                return { rowIndex: rowIndex + 1, column };
            case 'ArrowLeft':
                return colIndex > 0 ? { rowIndex, column: columns[colIndex - 1] } : null;
            case 'ArrowRight':
                return colIndex < columns.length - 1 ? { rowIndex, column: columns[colIndex + 1] } : null;
            default:
                return null;
        }
    },
    tabToNextCell: (params) => {
        const { backwards, previousCellPosition } = params;
        const { rowIndex, column } = previousCellPosition;
        const columns = params.api.getAllDisplayedColumns();
        const colIndex = columns.indexOf(column);

        if (backwards) {
            if (colIndex > 0) {
                return { rowIndex, column: columns[colIndex - 1] };
            } else if (rowIndex > 0) {
                return { rowIndex: rowIndex - 1, column: columns[columns.length - 1] };
            }
        } else {
            if (colIndex < columns.length - 1) {
                return { rowIndex, column: columns[colIndex + 1] };
            } else {
                return { rowIndex: rowIndex + 1, column: columns[0] };
            }
        }
        return null;
    },
};

// Create physician grid
function createPhysicianGrid(containerId, onCellValueChanged) {
    const gridOptions = {
        ...defaultGridOptions,
        columnDefs: physicianColumnDefs,
        rowData: [],
        onCellValueChanged: onCellValueChanged,
        getRowId: params => params.data.name,
    };

    const gridDiv = document.getElementById(containerId);
    const gridApi = agGrid.createGrid(gridDiv, gridOptions);

    return gridApi;
}

// Create results grid
function createResultsGrid(containerId, onCellValueChanged) {
    const gridOptions = {
        ...defaultGridOptions,
        columnDefs: resultsColumnDefs,
        rowData: [],
        onCellValueChanged: onCellValueChanged,
        getRowId: params => params.data.name,
    };

    const gridDiv = document.getElementById(containerId);
    const gridApi = agGrid.createGrid(gridDiv, gridOptions);

    return gridApi;
}
