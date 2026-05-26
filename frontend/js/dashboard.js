// ============================================================
// dashboard.js — Dashboard Charts and Summary Stats
//
// Fetches data from five backend analysis endpoints and
// renders them on the dashboard page:
//
// 1. loadSummary()           — 5 key metric stat cards
// 2. loadTopProducts()       — Bar chart: top 10 products
// 3. loadSalesTrend()        — Line chart: monthly revenue
// 4. loadChannelBreakdown()  — Doughnut: online vs onsite
// 5. loadCategoryPerformance()— Bar chart: revenue by category
//
// All functions run independently on page load so one
// failure does not prevent the others from rendering.
// ============================================================

// Base URL for all API calls
const API_BASE = 'http://127.0.0.1:5000/api';


// ── Currency Formatter ────────────────────────────────────────
// Formats a number as Cameroonian CFA Franc (FCFA)
// e.g. 1500000 → "1 500 000 FCFA"
const formatCFA = (val) =>
    new Intl.NumberFormat('fr-CM', {
        style:    'currency',
        currency: 'XAF'
    }).format(val);


// ── 1. Load Summary Stat Cards ────────────────────────────────
// Fetches high-level business metrics and fills in the 5
// stat card elements on the dashboard
async function loadSummary() {
    try {
        const res  = await fetch(`${API_BASE}/analysis/summary`);
        const data = await res.json();

        document.getElementById('total-sales').textContent
            = formatCFA(data.total_sales);

        document.getElementById('total-transactions').textContent
            = data.total_transactions.toLocaleString();

        document.getElementById('total-products').textContent
            = data.total_products;

        document.getElementById('total-customers').textContent
            = data.total_customers.toLocaleString();

        document.getElementById('avg-transaction').textContent
            = formatCFA(data.avg_transaction_value);

    } catch (err) {
        console.error('Failed to load summary:', err);
    }
}


// ── 2. Load Top Products Bar Chart ───────────────────────────
// Fetches top 10 products by revenue and renders a bar chart
async function loadTopProducts() {
    try {
        const res  = await fetch(`${API_BASE}/analysis/top-products`);
        const data = await res.json();

        new Chart(document.getElementById('topProductsChart'), {
            type: 'bar',
            data: {
                labels:   data.map(d => d.Product),  // Product names on X axis
                datasets: [{
                    label:           'Revenue (FCFA)',
                    data:            data.map(d => d.Amount),
                    backgroundColor: '#2563eb',  // Blue bars
                    borderRadius:    6            // Rounded bar tops
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } }  // No legend needed
            }
        });
    } catch (err) {
        console.error('Failed to load top products:', err);
    }
}


// ── 3. Load Monthly Sales Trend Line Chart ────────────────────
// Fetches monthly revenue totals and renders a filled line chart
async function loadSalesTrend() {
    try {
        const res  = await fetch(`${API_BASE}/analysis/sales-trend`);
        const data = await res.json();

        new Chart(document.getElementById('salesTrendChart'), {
            type: 'line',
            data: {
                labels:   data.map(d => d.Month),  // Month strings on X axis
                datasets: [{
                    label:           'Monthly Revenue',
                    data:            data.map(d => d.Amount),
                    borderColor:     '#10b981',               // Green line
                    backgroundColor: 'rgba(16,185,129,0.1)',  // Light fill
                    fill:            true,    // Fill area under the line
                    tension:         0.4      // Smooth curved line
                }]
            },
            options: { responsive: true }
        });
    } catch (err) {
        console.error('Failed to load sales trend:', err);
    }
}


// ── 4. Load Channel Breakdown Doughnut Chart ──────────────────
// Fetches Online vs Onsite revenue split and renders a doughnut
async function loadChannelBreakdown() {
    try {
        const res  = await fetch(`${API_BASE}/analysis/channel-breakdown`);
        const data = await res.json();

        new Chart(document.getElementById('channelChart'), {
            type: 'doughnut',
            data: {
                labels:   data.map(d => d.Channel),
                datasets: [{
                    data:            data.map(d => d.Amount),
                    backgroundColor: ['#2563eb', '#10b981']  // Blue and green
                }]
            },
            options: { responsive: true }
        });
    } catch (err) {
        console.error('Failed to load channel breakdown:', err);
    }
}


// ── 5. Load Category Performance Bar Chart ───────────────────
// Fetches revenue per category and renders a multi-color bar chart
async function loadCategoryPerformance() {
    try {
        const res  = await fetch(`${API_BASE}/analysis/category-performance`);
        const data = await res.json();

        new Chart(document.getElementById('categoryChart'), {
            type: 'bar',
            data: {
                labels:   data.map(d => d.Category),
                datasets: [{
                    label: 'Revenue (FCFA)',
                    data:  data.map(d => d.Amount),
                    // Each category bar gets a different color
                    backgroundColor: [
                        '#2563eb', '#10b981', '#f59e0b',
                        '#ef4444', '#8b5cf6', '#06b6d4'
                    ],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } }
            }
        });
    } catch (err) {
        console.error('Failed to load category performance:', err);
    }
}


// ── Initialize All Dashboard Components ──────────────────────
// Call all loader functions when the page opens.
// Each runs independently — one error won't break the others.
loadSummary();
loadTopProducts();
loadSalesTrend();
loadChannelBreakdown();
loadCategoryPerformance();