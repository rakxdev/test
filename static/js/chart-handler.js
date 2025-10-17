/**
 * Chart Handler - Shared Chart.js configuration and utilities
 * Provides common chart options, themes, and helper functions for real-time visualization
 */

const ChartHandler = {
    /**
     * Default colors for different data types
     */
    colors: {
        voltage: {
            line: '#ef4444',
            background: 'rgba(239, 68, 68, 0.1)',
            point: '#dc2626'
        },
        current: {
            line: '#3b82f6',
            background: 'rgba(59, 130, 246, 0.1)',
            point: '#2563eb'
        },
        power: {
            line: '#10b981',
            background: 'rgba(16, 185, 129, 0.1)',
            point: '#059669'
        },
        sensorValue: {
            line: '#8b5cf6',
            background: 'rgba(139, 92, 246, 0.1)',
            point: '#7c3aed'
        }
    },

    /**
     * Mode-specific color schemes
     */
    modeColors: {
        'Temperature': {
            line: '#ef4444',
            background: 'rgba(239, 68, 68, 0.1)',
            point: '#dc2626'
        },
        'Humidity': {
            line: '#3b82f6',
            background: 'rgba(59, 130, 246, 0.1)',
            point: '#2563eb'
        },
        'Pressure': {
            line: '#8b5cf6',
            background: 'rgba(139, 92, 246, 0.1)',
            point: '#7c3aed'
        },
        'Light': {
            line: '#f59e0b',
            background: 'rgba(245, 158, 11, 0.1)',
            point: '#d97706'
        }
    },

    /**
     * Get shared chart options with smooth lines, tooltips, legends, and animations
     */
    getChartOptions(title = 'Real-Time Data', yAxisLabel = 'Value') {
        return {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: {
                            size: 12,
                            family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
                        }
                    }
                },
                tooltip: {
                    enabled: true,
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        title: function(context) {
                            if (context[0].parsed.x) {
                                const date = new Date(context[0].parsed.x);
                                return date.toLocaleTimeString();
                            }
                            return '';
                        },
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y.toFixed(2);
                            }
                            return label;
                        }
                    }
                },
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'second',
                        displayFormats: {
                            second: 'HH:mm:ss'
                        },
                        tooltipFormat: 'HH:mm:ss'
                    },
                    title: {
                        display: true,
                        text: 'Time',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        maxRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 8
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: yAxisLabel,
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(2);
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            animation: {
                duration: 300,
                easing: 'easeInOutQuart'
            },
            elements: {
                line: {
                    tension: 0.4, // Smooth curves
                    borderWidth: 2
                },
                point: {
                    radius: 0, // Hide points by default for better performance
                    hitRadius: 10,
                    hoverRadius: 5,
                    hoverBorderWidth: 2
                }
            }
        };
    },

    /**
     * Create a dataset configuration with smooth line settings
     */
    createDataset(label, color, data = []) {
        const colorScheme = color || this.colors.sensorValue;
        
        return {
            label: label,
            data: data,
            borderColor: colorScheme.line,
            backgroundColor: colorScheme.background,
            pointBackgroundColor: colorScheme.point,
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            fill: true,
            tension: 0.4 // Smooth curves
        };
    },

    /**
     * Get color scheme for a specific mode
     */
    getModeColorScheme(modeName) {
        return this.modeColors[modeName] || this.colors.sensorValue;
    },

    /**
     * Remove old data points beyond the time window to maintain performance
     */
    pruneOldData(chart, timeWindowSeconds) {
        if (!chart || !chart.data || !chart.data.datasets) {
            return;
        }

        const now = Date.now();
        const cutoffTime = now - (timeWindowSeconds * 1000);

        chart.data.datasets.forEach(dataset => {
            if (dataset.data && dataset.data.length > 0) {
                // Remove data points older than cutoff
                dataset.data = dataset.data.filter(point => {
                    return point.x >= cutoffTime;
                });
            }
        });
    },

    /**
     * Add a new data point to a dataset
     */
    addDataPoint(chart, datasetIndex, timestamp, value) {
        if (!chart || !chart.data || !chart.data.datasets[datasetIndex]) {
            return;
        }

        chart.data.datasets[datasetIndex].data.push({
            x: timestamp,
            y: value
        });
    },

    /**
     * Update chart with new data and prune old data
     */
    updateChart(chart, timeWindowSeconds) {
        if (!chart) return;

        // Prune old data before updating
        this.pruneOldData(chart, timeWindowSeconds);

        // Update the chart
        chart.update('none'); // 'none' mode for better performance
    },

    /**
     * Export chart as PNG
     */
    exportChartAsPNG(chart, filename = 'chart') {
        if (!chart) return;

        const url = chart.toBase64Image();
        const link = document.createElement('a');
        link.download = `${filename}_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.png`;
        link.href = url;
        link.click();
    },

    /**
     * Clear all data from chart
     */
    clearChartData(chart) {
        if (!chart || !chart.data || !chart.data.datasets) {
            return;
        }

        chart.data.datasets.forEach(dataset => {
            dataset.data = [];
        });

        chart.update();
    },

    /**
     * Update chart time range
     */
    updateTimeRange(chart, timeWindowSeconds) {
        if (!chart) return;

        const now = Date.now();
        const minTime = now - (timeWindowSeconds * 1000);

        if (chart.options.scales.x) {
            chart.options.scales.x.min = minTime;
            chart.options.scales.x.max = now;
        }

        this.pruneOldData(chart, timeWindowSeconds);
        chart.update();
    },

    /**
     * Initialize a real-time scrolling chart
     */
    createRealtimeChart(canvasId, title, yAxisLabel, datasets) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            console.error(`Canvas element with id '${canvasId}' not found`);
            return null;
        }

        const options = this.getChartOptions(title, yAxisLabel);

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: datasets
            },
            options: options
        });

        return chart;
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChartHandler;
}
