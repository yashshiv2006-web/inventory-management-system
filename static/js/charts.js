/**
 * Retail Stock Optimization and Sales Intelligence Platform
 * Charts Module (Chart.js Integration)
 *
 * Why this file exists:
 * Charts translate raw database numbers into intuitive visual insights.
 * This script initializes 4 distinct visualizations:
 * 1. Line Chart: 30-Day Revenue Trend
 * 2. Bar Chart: Sales Volume by Category
 * 3. Doughnut/Pie Chart: Inventory Health Distribution
 * 4. Horizontal Bar Chart: Top Selling Products
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Revenue Trend Line Chart
    initRevenueTrendChart();

    // 2. Inventory Health Doughnut/Pie Chart
    initInventoryHealthChart();

    // 3. Category Sales Bar Chart
    initCategorySalesChart();

    // 4. Top Selling Products Chart
    initTopProductsChart();
});

/**
 * Initializes the Revenue Trend Line Chart.
 */
function initRevenueTrendChart() {
    const ctx = document.getElementById('revenueTrendChart');
    if (!ctx) return;

    // Simulated 14-day rolling revenue trend for retail analytics
    const labels = [
        'Oct 25', 'Oct 27', 'Oct 29', 'Oct 31',
        'Nov 02', 'Nov 04', 'Nov 06', 'Nov 07'
    ];
    const revenueData = [120, 240, 180, 420, 310, 520, 460, 680];

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Revenue ($)',
                data: revenueData,
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 2.5,
                fill: true,
                tension: 0.35,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#2563eb'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return ` Revenue: $${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#f1f5f9' },
                    ticks: {
                        callback: function (val) { return '$' + val; }
                    }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

/**
 * Initializes the Inventory Health Pie/Doughnut Chart.
 */
function initInventoryHealthChart() {
    const ctx = document.getElementById('inventoryHealthChart');
    if (!ctx) return;

    // Read data attributes if injected by Jinja template or use defaults
    const inStock = parseInt(ctx.dataset.inStock || '4');
    const lowStock = parseInt(ctx.dataset.lowStock || '2');
    const outStock = parseInt(ctx.dataset.outStock || '0');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['In Stock', 'Low Stock Alert', 'Out of Stock'],
            datasets: [{
                data: [inStock, lowStock, outStock],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                hoverOffset: 4,
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 12, padding: 15 }
                }
            },
            cutout: '65%'
        }
    });
}

/**
 * Initializes the Monthly Category Sales Bar Chart.
 */
function initCategorySalesChart() {
    const ctx = document.getElementById('categorySalesChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Electronics', 'Furniture', 'Accessories', 'Audio', 'Wearables'],
            datasets: [{
                label: 'Units Sold',
                data: [15, 6, 22, 11, 8],
                backgroundColor: [
                    'rgba(37, 99, 235, 0.85)',
                    'rgba(139, 92, 246, 0.85)',
                    'rgba(6, 182, 212, 0.85)',
                    'rgba(16, 185, 129, 0.85)',
                    'rgba(245, 158, 11, 0.85)'
                ],
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#f1f5f9' },
                    ticks: { precision: 0 }
                },
                x: { grid: { display: false } }
            }
        }
    });
}

/**
 * Initializes the Top Selling Products Horizontal Bar Chart.
 */
function initTopProductsChart() {
    const ctx = document.getElementById('topProductsChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [
                'Logitech MX Master 3S',
                'Dell 4K Monitor',
                'Keychron K2 Keyboard',
                'Anker 100W Fast Charger',
                'Office Ergonomic Chair'
            ],
            datasets: [{
                label: 'Revenue ($)',
                data: [479.95, 449.99, 341.96, 399.92, 339.15],
                backgroundColor: 'rgba(59, 130, 246, 0.85)',
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y', // Makes it a horizontal bar chart
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return ` Revenue: $${context.parsed.x.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { color: '#f1f5f9' },
                    ticks: {
                        callback: function (val) { return '$' + val; }
                    }
                },
                y: { grid: { display: false } }
            }
        }
    });
}
