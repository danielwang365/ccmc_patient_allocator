/**
 * API client functions for the Patient Allocator
 */

const API = {
    // Base fetch wrapper with JSON handling
    async fetch(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        const response = await fetch(url, { ...defaultOptions, ...options });
        if (response.status === 401) {
            window.location.href = '/login';
            return null;
        }
        return response.json();
    },

    // Physicians
    async getPhysicians() {
        return this.fetch('/api/physicians');
    },

    async createPhysician(data) {
        return this.fetch('/api/physicians', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async updatePhysician(name, data) {
        return this.fetch(`/api/physicians/${encodeURIComponent(name)}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    async deletePhysician(name) {
        return this.fetch(`/api/physicians/${encodeURIComponent(name)}`, {
            method: 'DELETE',
        });
    },

    async bulkUpdatePhysicians(physicians) {
        return this.fetch('/api/physicians/bulk', {
            method: 'POST',
            body: JSON.stringify(physicians),
        });
    },

    // Master List
    async getMasterList() {
        return this.fetch('/api/master-list');
    },

    async addToMasterList(name) {
        return this.fetch('/api/master-list', {
            method: 'POST',
            body: JSON.stringify({ name }),
        });
    },

    async removeFromMasterList(name) {
        return this.fetch(`/api/master-list/${encodeURIComponent(name)}`, {
            method: 'DELETE',
        });
    },

    // Parameters
    async getParameters() {
        return this.fetch('/api/parameters');
    },

    async updateParameters(params) {
        return this.fetch('/api/parameters', {
            method: 'PUT',
            body: JSON.stringify(params),
        });
    },

    // Yesterday
    async getYesterday() {
        return this.fetch('/api/yesterday');
    },

    async saveYesterday(names) {
        return this.fetch('/api/yesterday', {
            method: 'POST',
            body: JSON.stringify({ names }),
        });
    },

    // Selected
    async getSelected() {
        return this.fetch('/api/selected');
    },

    async saveSelected(names) {
        return this.fetch('/api/selected', {
            method: 'POST',
            body: JSON.stringify({ names }),
        });
    },

    // Allocation
    async runAllocation(physicians, parameters) {
        return this.fetch('/api/allocate', {
            method: 'POST',
            body: JSON.stringify({ physicians, parameters }),
        });
    },

    // Generate Table
    async generateTable(selections) {
        return this.fetch('/api/generate-table', {
            method: 'POST',
            body: JSON.stringify({ selections }),
        });
    },

    // Print Summary
    async getPrintSummary(results, summary) {
        return this.fetch('/api/print-summary', {
            method: 'POST',
            body: JSON.stringify({ results, summary }),
        });
    },

    async getPrintSummaryText(results) {
        return this.fetch('/api/print-summary/text', {
            method: 'POST',
            body: JSON.stringify({ results }),
        });
    },
};

// Show save indicator
function showSaveIndicator(message = 'Saved!') {
    let indicator = document.getElementById('saveIndicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'saveIndicator';
        indicator.className = 'save-indicator';
        document.body.appendChild(indicator);
    }
    indicator.textContent = message;
    indicator.classList.add('show');
    setTimeout(() => {
        indicator.classList.remove('show');
    }, 2000);
}

// Debounce function for auto-save
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
