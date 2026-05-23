// ============================================================
// dashboard.js — Dashboard Charts and Stats Logic
// Fetches analysis data from the backend API and renders
// summary stat cards and four Chart.js visualizations.
// ============================================================

// Base URL for all backend API calls
const API_BASE = 'http://127.0.0.1:5000/api';


// ── Helper: Format numbers as FCFA currency ──────────────────
// Uses the browser's built-in Intl formatter for Cameroon CFA
const formatCFA = (val) =>
    new Intl.NumberFormat('fr-CM', {
        style:    'currency',
        currency: 'XAF'
    }).format(val);


// ── Load Summary Stats ───────────────────────────────────────
// Fetches high-level metrics and populates the stat cards
async function loadSummary() {
    const res  = await fetch(`${API_BASE}/analysis/summary`);
    const data = await res.json();

    // Populate each stat card with the returned values
    document.getElementById('total-sales').textContent
        = formatCFA(data.total_sales);

    document.getElementById('total-transactions').textContent
        = data.total_transactions;

    document.getElementById('total-products').textContent
        = data.total_products;

    document.getElementById('total-customers').textContent
        = data.total_customers;

    document.getElementById('avg-transaction').textContent
        = formatCFA(data.avg_transaction_value);
}


// ── Load Top Products Bar Chart ──────────────────────────────
// Fetches top 10 products by revenue and renders a bar chart
async function loadTopProducts() {
    const res  = await fetch(`${API_BASE}/analysis/top-products`);
    const data = await res.json();

    new Chart(document.getElementById('topProductsChart'), {
        type: 'bar',
        data: {
            labels:   data.map(d => d.Product), // Product names on X axis
            datasets: [{
                label:           'Revenue (FCFA)',
                data:            data.map(d => d.Amount), // Revenue on Y axis
                backgroundColor: '#2563eb',
                borderRadius:    6
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } } // Hide legend (only 1 dataset)
        }
    });
}


// ── Load Monthly Sales Trend Line Chart ──────────────────────
// Fetches monthly revenue totals and renders a line chart
async function loadSalesTrend() {
    const res  = await fetch(`${API_BASE}/analysis/sales-trend`);
    const data = await res.json();

    new Chart(document.getElementById('salesTrendChart'), {
        type: 'line',
        data: {
            labels:   data.map(d => d.Month),  // Month labels on X axis
            datasets: [{
                label:           'Monthly Revenue',
                data:            data.map(d => d.Amount),
                borderColor:     '#10b981',
                backgroundColor: 'rgba(16,185,129,0.1)', // Light fill under line
                fill:            true,   // Fill area under the line
                tension:         0.4     // Smooth curve (0=straight, 1=very curved)
            }]
        },
        options: { responsive: true }
    });
}


// ── Load Channel Breakdown Doughnut Chart ────────────────────
// Fetches Online vs Onsite revenue split and renders a doughnut
async function loadChannelBreakdown() {
    const res  = await fetch(`${API_BASE}/analysis/channel-breakdown`);
    const data = await res.json();

    new Chart(document.getElementById('channelChart'), {
        type: 'doughnut',
        data: {
            labels:   data.map(d => d.Channel), // Online / Onsite
            datasets: [{
                data:            data.map(d => d.Amount),
                backgroundColor: ['#2563eb', '#10b981'] // Blue and green
            }]
        },
        options: { responsive: true }
    });
}


// ── Load Category Performance Bar Chart ──────────────────────
// Fetches revenue per category and renders a colored bar chart
async function loadCategoryPerformance() {
    const res  = await fetch(`${API_BASE}/analysis/category-performance`);
    const data = await res.json();

    new Chart(document.getElementById('categoryChart'), {
        type: 'bar',
        data: {
            labels:   data.map(d => d.Category), // Category names on X axis
            datasets: [{
                label: 'Revenue (FCFA)',
                data:  data.map(d => d.Amount),
                // Each bar gets a different color for visual distinction
                backgroundColor: [
                    '#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'
                ],
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } }
        }
    });
}


// ── Initialize Dashboard ─────────────────────────────────────
// Call all functions when the page loads
// Each runs independently so one failure won't block others
loadSummary();
loadTopProducts();
loadSalesTrend();
loadChannelBreakdown();
loadCategoryPerformance();