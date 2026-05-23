// ============================================================
// transactions.js — Manual Transaction Recording Logic
// Handles the transaction form, auto-calculates totals,
// saves transactions to the backend, and displays all
// previously recorded transactions in a table.
// ============================================================

const API_BASE = 'http://127.0.0.1:5000/api';


// ── Auto-calculate Total Amount ───────────────────────────────
// Updates the total display whenever quantity or price changes
function updateTotal() {
    const qty   = parseFloat(document.getElementById('quantity').value)   || 0;
    const price = parseFloat(document.getElementById('unit_price').value) || 0;
    const total = qty * price;

    document.getElementById('total-amount').textContent =
        new Intl.NumberFormat('fr-CM').format(total) + ' FCFA';
}

document.getElementById('quantity').addEventListener('input', updateTotal);
document.getElementById('unit_price').addEventListener('input', updateTotal);


// ── Save Transaction ──────────────────────────────────────────
document.getElementById('save-btn').addEventListener('click', async () => {
    const formStatus = document.getElementById('form-status');

    // Collect form values
    const transaction = {
        Customer_Name: document.getElementById('customer_name').value,
        Sex:           document.getElementById('sex').value,
        Product:       document.getElementById('product').value.trim(),
        Category:      document.getElementById('category').value,
        Quantity:      document.getElementById('quantity').value,
        Unit_Price:    document.getElementById('unit_price').value,
        Channel:       document.getElementById('channel').value,
        Date:          document.getElementById('date').value ||
                       new Date().toISOString().split('T')[0] // Default to today
    };

    // Validate required fields
    const required = ['Product', 'Category', 'Quantity', 'Unit_Price', 'Channel'];
    const missing  = required.filter(f => !transaction[f]);
    if (missing.length > 0) {
        formStatus.innerHTML = `
            <p class="status-error">
                Please fill in: ${missing.join(', ')}
            </p>`;
        return;
    }

    formStatus.innerHTML = '<div class="spinner"></div>';

    try {
        const res = await fetch(`${API_BASE}/transactions/add`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(transaction)
        });

        const data = await res.json();

        if (res.ok) {
            formStatus.innerHTML = `
                <p class="status-success">
                    <i class="fas fa-check-circle"></i>
                    Transaction saved! Total records: ${data.total_records}
                </p>`;
            clearForm();        // Reset form fields
            loadTransactions(); // Refresh the table
        } else {
            formStatus.innerHTML = `
                <p class="status-error">Error: ${data.error}</p>`;
        }
    } catch (err) {
        formStatus.innerHTML = `
            <p class="status-error">Could not connect to server.</p>`;
    }
});


// ── Clear Form After Save ─────────────────────────────────────
function clearForm() {
    ['customer_name','sex','product','category',
     'quantity','unit_price','channel','date'].forEach(id => {
        document.getElementById(id).value = '';
    });
    document.getElementById('total-amount').textContent = '0 FCFA';
}


// ── Load All Transactions ─────────────────────────────────────
// Fetches and displays all recorded transactions in a table
async function loadTransactions() {
    const container = document.getElementById('transactions-table');
    const countEl   = document.getElementById('total-count');

    try {
        const res  = await fetch(`${API_BASE}/transactions/all`);
        const data = await res.json();

        countEl.textContent = `${data.total} records`;

        if (data.total === 0) {
            container.innerHTML = `
                <p style="color:#64748b; text-align:center; padding:2rem">
                    No transactions recorded yet.
                </p>`;
            return;
        }

        // Build HTML table from transactions
        container.innerHTML = `
            <div style="overflow-x:auto">
                <table class="mapping-tbl">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Date</th>
                            <th>Product</th>
                            <th>Category</th>
                            <th>Qty</th>
                            <th>Unit Price</th>
                            <th>Amount</th>
                            <th>Channel</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.transactions.map((t, i) => `
                            <tr>
                                <td>${i + 1}</td>
                                <td>${t.Date}</td>
                                <td>${t.Product}</td>
                                <td>${t.Category}</td>
                                <td>${t.Quantity}</td>
                                <td>${Number(t.Unit_Price).toLocaleString()} FCFA</td>
                                <td>${Number(t.Amount).toLocaleString()} FCFA</td>
                                <td>${t.Channel}</td>
                                <td>
                                    <button
                                        class="delete-btn"
                                        onclick="deleteTransaction(${i})">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>`;

    } catch (err) {
        container.innerHTML = `
            <p class="status-error">Could not load transactions.</p>`;
    }
}


// ── Delete Transaction ────────────────────────────────────────
async function deleteTransaction(index) {
    if (!confirm('Are you sure you want to delete this transaction?')) return;

    try {
        const res = await fetch(`${API_BASE}/transactions/delete/${index}`, {
            method: 'DELETE'
        });
        if (res.ok) loadTransactions();
    } catch (err) {
        alert('Could not delete transaction.');
    }
}


// ── Load on Page Open ─────────────────────────────────────────
loadTransactions();