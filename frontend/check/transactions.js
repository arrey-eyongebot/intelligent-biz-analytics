// ============================================================
// transactions.js — Manual Transaction Recording Logic
//
// Handles the Record Sale page:
//
// - Auto-calculates Amount (Quantity × Unit Price) as user types
// - Validates required fields before saving
// - Sends transaction to POST /api/transactions/add
// - Loads all recorded transactions into a history table
// - Allows deleting individual transactions
//
// Saved transactions are automatically merged into the
// main cleaned_data.csv by the backend, so the dashboard
// and analysis always include manually recorded sales.
// ============================================================

// Base URL for all API calls
const API_BASE = 'http://127.0.0.1:5000/api';


// ── Auto-Calculate Total Amount ───────────────────────────────
// Updates the total display in real-time as the user types
// quantity or unit price values in the form.
function updateTotal() {
    const qty   = parseFloat(document.getElementById('quantity').value)   || 0;
    const price = parseFloat(document.getElementById('unit_price').value) || 0;
    const total = qty * price;

    // Format as FCFA and show in the total display box
    document.getElementById('total-amount').textContent =
        new Intl.NumberFormat('fr-CM').format(total) + ' FCFA';
}

// Listen for changes in quantity and unit price fields
document.getElementById('quantity').addEventListener('input', updateTotal);
document.getElementById('unit_price').addEventListener('input', updateTotal);


// ── Save Transaction ──────────────────────────────────────────
// Validates form, sends transaction to backend, refreshes table
document.getElementById('save-btn').addEventListener('click', async () => {
    const formStatus = document.getElementById('form-status');

    // Collect all form values
    const transaction = {
        Customer_Name: document.getElementById('customer_name').value.trim(),
        Sex:           document.getElementById('sex').value,
        Product:       document.getElementById('product').value.trim(),
        Category:      document.getElementById('category').value,
        Quantity:      document.getElementById('quantity').value,
        Unit_Price:    document.getElementById('unit_price').value,
        Channel:       document.getElementById('channel').value,
        // Default to today's date if none selected
        Date: document.getElementById('date').value ||
              new Date().toISOString().split('T')[0]
    };

    // Check all required fields are filled
    const required = ['Product', 'Category', 'Quantity', 'Unit_Price', 'Channel'];
    const missing  = required.filter(f => !transaction[f]);

    if (missing.length > 0) {
        formStatus.innerHTML = `
            <p class="status-error">
                <i class="fas fa-times-circle"></i>
                Please fill in: <strong>${missing.join(', ')}</strong>
            </p>`;
        return;
    }

    // Show spinner while saving
    formStatus.innerHTML = '<div class="spinner"></div>';

    try {
        const res = await fetch(`${API_BASE}/transactions/add`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(transaction)
        });

        const data = await res.json();

        if (res.ok) {
            // Show success message and refresh the transactions table
            formStatus.innerHTML = `
                <p class="status-success">
                    <i class="fas fa-check-circle"></i>
                    Transaction saved! Total records: ${data.total_records}
                </p>`;
            clearForm();         // Reset all form fields
            loadTransactions();  // Reload the history table
        } else {
            formStatus.innerHTML = `
                <p class="status-error">Error: ${data.error}</p>`;
        }

    } catch (err) {
        formStatus.innerHTML = `
            <p class="status-error">Could not connect to server.</p>`;
    }
});


// ── Clear Form Fields ─────────────────────────────────────────
// Resets all input fields after a successful save
function clearForm() {
    const fields = [
        'customer_name', 'sex', 'product', 'category',
        'quantity', 'unit_price', 'channel', 'date'
    ];
    fields.forEach(id => { document.getElementById(id).value = ''; });
    document.getElementById('total-amount').textContent = '0 FCFA';
}


// ── Load All Transactions ─────────────────────────────────────
// Fetches all recorded transactions and renders them in a table
async function loadTransactions() {
    const container = document.getElementById('transactions-table');
    const countEl   = document.getElementById('total-count');

    try {
        const res  = await fetch(`${API_BASE}/transactions/all`);
        const data = await res.json();

        // Update the record count badge
        countEl.textContent = `${data.total} record${data.total !== 1 ? 's' : ''}`;

        if (data.total === 0) {
            // Show a friendly empty state message
            container.innerHTML = `
                <p style="color:#64748b; text-align:center; padding:2rem">
                    <i class="fas fa-inbox"
                       style="font-size:2rem; display:block; margin-bottom:0.5rem">
                    </i>
                    No transactions recorded yet.<br>
                    Use the form above to add your first sale.
                </p>`;
            return;
        }

        // Build a scrollable HTML table from the transactions array
        container.innerHTML = `
            <div style="overflow-x:auto">
                <table class="mapping-tbl">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Date</th>
                            <th>Customer</th>
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
                                <td>${t.Date || '—'}</td>
                                <td>${t.Customer_Name || '—'}</td>
                                <td>${t.Product}</td>
                                <td>${t.Category}</td>
                                <td>${t.Quantity}</td>
                                <td>
                                    ${Number(t.Unit_Price)
                                        .toLocaleString('fr-CM')} FCFA
                                </td>
                                <td>
                                    ${Number(t.Amount)
                                        .toLocaleString('fr-CM')} FCFA
                                </td>
                                <td>${t.Channel}</td>
                                <td>
                                    <button
                                        class="delete-btn"
                                        onclick="deleteTransaction(${i})"
                                        title="Delete this transaction">
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
            <p class="status-error">
                Could not load transactions. Is the backend running?
            </p>`;
    }
}


// ── Delete Transaction ────────────────────────────────────────
// Sends a DELETE request for a transaction by its row index,
// then refreshes the table to reflect the deletion.
async function deleteTransaction(index) {
    if (!confirm('Are you sure you want to delete this transaction?')) return;

    try {
        const res = await fetch(
            `${API_BASE}/transactions/delete/${index}`,
            { method: 'DELETE' }
        );

        if (res.ok) {
            loadTransactions();  // Refresh table after deletion
        } else {
            alert('Failed to delete transaction.');
        }
    } catch (err) {
        alert('Could not connect to server.');
    }
}


// ── Initialize Page ───────────────────────────────────────────
// Load the existing transactions table when the page opens
loadTransactions();