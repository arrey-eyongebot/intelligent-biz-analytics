const API_BASE = 'http://127.0.0.1:5000/api';

// Format currency in FCFA
const formatCFA = (val) =>
    new Intl.NumberFormat('fr-CM', { style: 'currency', currency: 'XAF' }).format(val);

async function loadSummary() {
    const res  = await fetch(`${API_BASE}/analysis/summary`);
    const data = await res.json();

    document.getElementById('total-sales').textContent        = formatCFA(data.total_sales);
    document.getElementById('total-transactions').textContent = data.total_transactions;
    document.getElementById('total-products').textContent     = data.total_products;
    document.getElementById('total-customers').textContent    = data.total_customers;
    document.getElementById('avg-transaction').textContent    = formatCFA(data.avg_transaction_value);
}

async function loadTopProducts() {
    const res  = await fetch(`${API_BASE}/analysis/top-products`);
    const data = await res.json();

    new Chart(document.getElementById('topProductsChart'), {
        type: 'bar',
        data: {
            labels:   data.map(d => d.Product),
            datasets: [{
                label:           'Revenue (FCFA)',
                data:            data.map(d => d.Amount),
                backgroundColor: '#2563eb',
                borderRadius:    6
            }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });
}

async function loadSalesTrend() {
    const res  = await fetch(`${API_BASE}/analysis/sales-trend`);
    const data = await res.json();

    new Chart(document.getElementById('salesTrendChart'), {
        type: 'line',
        data: {
            labels:   data.map(d => d.Month),
            datasets: [{
                label:           'Monthly Revenue',
                data:            data.map(d => d.Amount),
                borderColor:     '#10b981',
                backgroundColor: 'rgba(16,185,129,0.1)',
                fill:            true,
                tension:         0.4
            }]
        },
        options: { responsive: true }
    });
}

async function loadChannelBreakdown() {
    const res  = await fetch(`${API_BASE}/analysis/channel-breakdown`);
    const data = await res.json();

    new Chart(document.getElementById('channelChart'), {
        type: 'doughnut',
        data: {
            labels:   data.map(d => d.Channel),
            datasets: [{
                data:            data.map(d => d.Amount),
                backgroundColor: ['#2563eb', '#10b981']
            }]
        },
        options: { responsive: true }
    });
}

async function loadCategoryPerformance() {
    const res  = await fetch(`${API_BASE}/analysis/category-performance`);
    const data = await res.json();

    new Chart(document.getElementById('categoryChart'), {
        type: 'bar',
        data: {
            labels:   data.map(d => d.Category),
            datasets: [{
                label:           'Revenue (FCFA)',
                data:            data.map(d => d.Amount),
                backgroundColor: ['#2563eb','#10b981','#f59e0b','#ef4444','#8b5cf6'],
                borderRadius:    6
            }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });
}

// Load everything
loadSummary();
loadTopProducts();
loadSalesTrend();
loadChannelBreakdown();
loadCategoryPerformance();