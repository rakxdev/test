let currentPage = 1;
let recordsPerPage = 100;
let currentFilters = {};
let currentSort = { column: null, direction: 'desc' };
let recordsChart = null;

function getFilters() {
    const filters = {
        limit: recordsPerPage,
        offset: (currentPage - 1) * recordsPerPage
    };

    const modeId = document.getElementById('modeFilter').value;
    if (modeId) filters.mode_id = modeId;

    const startTime = document.getElementById('startTime').value;
    if (startTime) filters.start_time = new Date(startTime).toISOString();

    const endTime = document.getElementById('endTime').value;
    if (endTime) filters.end_time = new Date(endTime).toISOString();

    const minValue = document.getElementById('minValue').value;
    if (minValue) filters.min_value = parseFloat(minValue);

    const maxValue = document.getElementById('maxValue').value;
    if (maxValue) filters.max_value = parseFloat(maxValue);

    const aggregation = document.getElementById('aggregation').value;
    if (aggregation) filters.aggregation = aggregation;

    return filters;
}

async function loadRecords() {
    const loadingMessage = document.getElementById('loadingMessage');
    const errorMessage = document.getElementById('errorMessage');
    const tableBody = document.getElementById('recordsTableBody');

    loadingMessage.style.display = 'block';
    errorMessage.style.display = 'none';
    tableBody.innerHTML = '';

    try {
        currentFilters = getFilters();
        const queryString = new URLSearchParams(currentFilters).toString();
        const response = await fetch(`/api/records?${queryString}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to load records');
        }

        const data = await response.json();
        loadingMessage.style.display = 'none';

        const isAggregated = currentFilters.aggregation && currentFilters.aggregation !== 'raw';
        
        updateTableHeaders(isAggregated);

        if (data.records.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="no-data">
                        <div class="empty-state">
                            <div class="empty-state-icon">📊</div>
                            <div class="empty-state-title">No records found</div>
                            <div class="empty-state-description">Try adjusting your filters to see more data</div>
                        </div>
                    </td>
                </tr>
            `;
        } else {
            renderTableRows(data.records, isAggregated);
        }

        updatePagination(data.count);
    } catch (error) {
        loadingMessage.style.display = 'none';
        errorMessage.textContent = error.message;
        errorMessage.style.display = 'block';
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="no-data">
                    <div class="empty-state">
                        <div class="empty-state-icon">⚠️</div>
                        <div class="empty-state-title">Error loading records</div>
                        <div class="empty-state-description">Please try again</div>
                    </div>
                </td>
            </tr>
        `;
    }
}

function updateTableHeaders(isAggregated) {
    document.getElementById('minHeader').style.display = isAggregated ? '' : 'none';
    document.getElementById('maxHeader').style.display = isAggregated ? '' : 'none';
    document.getElementById('countHeader').style.display = isAggregated ? '' : 'none';
}

function renderTableRows(records, isAggregated) {
    const tableBody = document.getElementById('recordsTableBody');
    
    tableBody.innerHTML = records.map(record => {
        if (isAggregated) {
            return `
                <tr>
                    <td>
                        <span class="mode-badge">
                            ${record.icon} ${record.mode_name}
                        </span>
                    </td>
                    <td class="value-cell">${record.value.toFixed(2)}</td>
                    <td>${formatTimestamp(record.timestamp)}</td>
                    <td class="value-cell">${record.min_value.toFixed(2)}</td>
                    <td class="value-cell">${record.max_value.toFixed(2)}</td>
                    <td>${record.count}</td>
                </tr>
            `;
        } else {
            return `
                <tr>
                    <td>
                        <span class="mode-badge">
                            ${record.icon} ${record.mode_name}
                        </span>
                    </td>
                    <td class="value-cell">${record.value.toFixed(2)}</td>
                    <td>${formatTimestamp(record.timestamp)}</td>
                </tr>
            `;
        }
    }).join('');
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

function updatePagination(count) {
    const prevButton = document.getElementById('prevButton');
    const nextButton = document.getElementById('nextButton');
    const paginationInfo = document.getElementById('paginationInfo');

    prevButton.disabled = currentPage === 1;
    nextButton.disabled = count < recordsPerPage;
    
    const startRecord = (currentPage - 1) * recordsPerPage + 1;
    const endRecord = Math.min(currentPage * recordsPerPage, startRecord + count - 1);
    paginationInfo.textContent = count > 0 
        ? `Showing ${startRecord}-${endRecord} (Page ${currentPage})`
        : `Page ${currentPage}`;
}

function applyFilters() {
    currentPage = 1;
    loadRecords();
    loadChart();
}

function resetFilters() {
    document.getElementById('modeFilter').value = '';
    document.getElementById('startTime').value = '';
    document.getElementById('endTime').value = '';
    document.getElementById('minValue').value = '';
    document.getElementById('maxValue').value = '';
    document.getElementById('aggregation').value = 'raw';
    currentPage = 1;
    
    const tableBody = document.getElementById('recordsTableBody');
    tableBody.innerHTML = `
        <tr>
            <td colspan="6" class="no-data">
                <div class="empty-state">
                    <div class="empty-state-icon">🔍</div>
                    <div class="empty-state-title">Ready to search</div>
                    <div class="empty-state-description">Click "Apply Filters" to load records</div>
                </div>
            </td>
        </tr>
    `;
    
    document.getElementById('statisticsSection').style.display = 'none';
    document.getElementById('chartSection').style.display = 'none';
    
    if (recordsChart) {
        recordsChart.destroy();
        recordsChart = null;
    }
}

function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        loadRecords();
    }
}

function nextPage() {
    currentPage++;
    loadRecords();
}

async function loadStatistics() {
    const filters = getFilters();
    delete filters.limit;
    delete filters.offset;
    delete filters.aggregation;

    try {
        const queryString = new URLSearchParams(filters).toString();
        const response = await fetch(`/api/statistics?${queryString}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to load statistics');
        }

        const data = await response.json();
        const statsSection = document.getElementById('statisticsSection');
        const statsContent = document.getElementById('statsContent');

        if (data.statistics && (Array.isArray(data.statistics) ? data.statistics.length > 0 : data.statistics)) {
            const stats = Array.isArray(data.statistics) ? data.statistics : [data.statistics];
            
            statsContent.innerHTML = stats.map(stat => `
                <div style="margin-bottom: 1.5rem;">
                    <h3 style="margin-bottom: 1rem; color: #2c3e50;">
                        ${stat.icon} ${stat.mode_name}
                    </h3>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <h3>Count</h3>
                            <div class="stat-value">${stat.count.toLocaleString()}</div>
                        </div>
                        <div class="stat-card">
                            <h3>Average</h3>
                            <div class="stat-value">${stat.average.toFixed(2)}</div>
                        </div>
                        <div class="stat-card">
                            <h3>Minimum</h3>
                            <div class="stat-value">${stat.minimum.toFixed(2)}</div>
                        </div>
                        <div class="stat-card">
                            <h3>Maximum</h3>
                            <div class="stat-value">${stat.maximum.toFixed(2)}</div>
                        </div>
                        <div class="stat-card">
                            <h3>First Reading</h3>
                            <div class="stat-value" style="font-size: 0.9rem;">
                                ${formatTimestamp(stat.first_reading)}
                            </div>
                        </div>
                        <div class="stat-card">
                            <h3>Last Reading</h3>
                            <div class="stat-value" style="font-size: 0.9rem;">
                                ${formatTimestamp(stat.last_reading)}
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');

            statsSection.style.display = 'block';
        } else {
            statsContent.innerHTML = '<p class="no-data">No statistics available for the selected filters</p>';
            statsSection.style.display = 'block';
        }
    } catch (error) {
        showError(`Error loading statistics: ${error.message}`);
    }
}

async function loadChart() {
    const chartSection = document.getElementById('chartSection');
    const chartCanvas = document.getElementById('recordsChart');
    
    const filters = getFilters();
    delete filters.limit;
    delete filters.offset;
    
    if (!filters.aggregation || filters.aggregation === 'raw') {
        filters.aggregation = '5min';
    }
    
    filters.limit = 500;
    
    try {
        const queryString = new URLSearchParams(filters).toString();
        const response = await fetch(`/api/records?${queryString}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to load chart data');
        }

        const data = await response.json();
        
        if (data.records.length === 0) {
            chartSection.style.display = 'none';
            return;
        }

        renderChart(data.records);
        chartSection.style.display = 'block';
    } catch (error) {
        console.error('Error loading chart:', error);
        chartSection.style.display = 'none';
    }
}

function renderChart(records) {
    const chartCanvas = document.getElementById('recordsChart');
    const ctx = chartCanvas.getContext('2d');
    
    if (recordsChart) {
        recordsChart.destroy();
    }
    
    const groupedByMode = records.reduce((acc, record) => {
        const modeKey = `${record.mode_id}_${record.mode_name}`;
        if (!acc[modeKey]) {
            acc[modeKey] = {
                mode_name: record.mode_name,
                icon: record.icon,
                data: []
            };
        }
        acc[modeKey].data.push({
            x: new Date(record.timestamp),
            y: record.value
        });
        return acc;
    }, {});
    
    const colors = [
        { bg: 'rgba(52, 152, 219, 0.2)', border: 'rgba(52, 152, 219, 1)' },
        { bg: 'rgba(46, 204, 113, 0.2)', border: 'rgba(46, 204, 113, 1)' },
        { bg: 'rgba(231, 76, 60, 0.2)', border: 'rgba(231, 76, 60, 1)' },
        { bg: 'rgba(241, 196, 15, 0.2)', border: 'rgba(241, 196, 15, 1)' },
        { bg: 'rgba(155, 89, 182, 0.2)', border: 'rgba(155, 89, 182, 1)' },
        { bg: 'rgba(52, 73, 94, 0.2)', border: 'rgba(52, 73, 94, 1)' }
    ];
    
    const datasets = Object.values(groupedByMode).map((mode, index) => {
        const colorSet = colors[index % colors.length];
        return {
            label: `${mode.icon} ${mode.mode_name}`,
            data: mode.data,
            borderColor: colorSet.border,
            backgroundColor: colorSet.bg,
            borderWidth: 2,
            tension: 0.3,
            fill: true,
            pointRadius: 3,
            pointHoverRadius: 5
        };
    });
    
    recordsChart = new Chart(ctx, {
        type: 'line',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Sensor Readings Over Time',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.parsed.y.toFixed(2);
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        displayFormats: {
                            minute: 'HH:mm',
                            hour: 'MMM D, HH:mm',
                            day: 'MMM D',
                            week: 'MMM D',
                            month: 'MMM YYYY'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Time'
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 0
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Value'
                    },
                    beginAtZero: false
                }
            }
        }
    });
}

function sortTable(column) {
    const tableBody = document.getElementById('recordsTableBody');
    const rows = Array.from(tableBody.querySelectorAll('tr'));
    
    if (rows.length === 0 || rows[0].querySelector('.no-data')) {
        return;
    }
    
    if (currentSort.column === column) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.column = column;
        currentSort.direction = 'asc';
    }
    
    updateSortIndicators();
    
    const columnIndex = getColumnIndex(column);
    
    rows.sort((a, b) => {
        const aValue = a.querySelectorAll('td')[columnIndex]?.textContent.trim();
        const bValue = b.querySelectorAll('td')[columnIndex]?.textContent.trim();
        
        let comparison = 0;
        
        if (column === 'value' || column === 'min' || column === 'max' || column === 'count') {
            const aNum = parseFloat(aValue);
            const bNum = parseFloat(bValue);
            comparison = aNum - bNum;
        } else if (column === 'timestamp') {
            const aDate = new Date(aValue);
            const bDate = new Date(bValue);
            comparison = aDate - bDate;
        } else {
            comparison = aValue.localeCompare(bValue);
        }
        
        return currentSort.direction === 'asc' ? comparison : -comparison;
    });
    
    rows.forEach(row => tableBody.appendChild(row));
}

function getColumnIndex(column) {
    const columnMap = {
        'mode': 0,
        'value': 1,
        'timestamp': 2,
        'min': 3,
        'max': 4,
        'count': 5
    };
    return columnMap[column] || 0;
}

function updateSortIndicators() {
    const headers = document.querySelectorAll('.records-table th.sortable');
    headers.forEach(header => {
        header.classList.remove('sort-asc', 'sort-desc');
        const column = header.getAttribute('data-column');
        if (column === currentSort.column) {
            header.classList.add(`sort-${currentSort.direction}`);
        }
    });
}

function changeRecordsPerPage() {
    const select = document.getElementById('recordsPerPageSelect');
    recordsPerPage = parseInt(select.value);
    currentPage = 1;
    loadRecords();
}

function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

function initializeSortHandlers() {
    const headers = document.querySelectorAll('.records-table th.sortable');
    headers.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.getAttribute('data-column');
            sortTable(column);
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initializeSortHandlers();
    
    const applyBtn = document.getElementById('applyFiltersBtn');
    if (applyBtn) {
        applyBtn.addEventListener('click', applyFilters);
    }
    
    const resetBtn = document.getElementById('resetFiltersBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetFilters);
    }
    
    const statsBtn = document.getElementById('loadStatisticsBtn');
    if (statsBtn) {
        statsBtn.addEventListener('click', loadStatistics);
    }
    
    const recordsPerPageSelect = document.getElementById('recordsPerPageSelect');
    if (recordsPerPageSelect) {
        recordsPerPageSelect.addEventListener('change', changeRecordsPerPage);
    }
});
