// ============================================================
// transactions.js — Manual Transaction Recording Logic
// ============================================================

var API_BASE = (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost')
    ? 'http://127.0.0.1:5000/api'
    : '/api';

function updateTotal() {
    var qty   = parseFloat(document.getElementById('quantity').value)   || 0;
    var price = parseFloat(document.getElementById('unit_price').value) || 0;
    var total = qty * price;
    document.getElementById('total-amount').textContent =
        new Intl.NumberFormat('fr-CM').format(total) + ' FCFA';
}

document.getElementById('quantity').addEventListener('input', updateTotal);
document.getElementById('unit_price').addEventListener('input', updateTotal);

document.getElementById('save-btn').addEventListener('click', async function() {
    var formStatus = document.getElementById('form-status');

    var transaction = {
        Customer_Name: document.getElementById('customer_name').value.trim(),
        Sex:           document.getElementById('sex').value,
        Product:       document.getElementById('product').value.trim(),
        Category:      document.getElementById('category').value,
        Quantity:      document.getElementById('quantity').value,
        Unit_Price:    document.getElementById('unit_price').value,
        Channel:       document.getElementById('channel').value,
        Date:          document.getElementById('date').value ||
                       new Date().toISOString().split('T')[0]
    };

    var required = ['Product', 'Category', 'Quantity', 'Unit_Price', 'Channel'];
    var missing  = required.filter(function(f) { return !transaction[f]; });

    if (missing.length > 0) {
        formStatus.innerHTML =
            '<p class="status-error">' +
            '<i class="fas fa-times-circle"></i> ' +
            'Please fill in: <strong>' + missing.join(', ') + '</strong></p>';
        return;
    }

    formStatus.innerHTML = '<div class="spinner"></div>';

    try {
        var res  = await fetch(API_BASE + '/transactions/add', {
            method:      'POST',
            headers:     { 'Content-Type': 'application/json' },
            credentials: 'include',
            body:        JSON.stringify(transaction)
        });
        var data = await res.json();

        if (res.ok) {
            formStatus.innerHTML =
                '<p class="status-success">' +
                '<i class="fas fa-check-circle"></i> ' +
                'Transaction saved! Total records: ' +
                data.total_records + '</p>';
            clearForm();
            loadTransactions();
        } else {
            formStatus.innerHTML =
                '<p class="status-error">Error: ' + data.error + '</p>';
        }
    } catch(err) {
        formStatus.innerHTML =
            '<p class="status-error">Could not connect to server.</p>';
    }
});

function clearForm() {
    ['customer_name','sex','product','category',
     'quantity','unit_price','channel','date'].forEach(function(id) {
        document.getElementById(id).value = '';
    });
    document.getElementById('total-amount').textContent = '0 FCFA';
}

async function loadTransactions() {
    var container = document.getElementById('transactions-table');
    var countEl   = document.getElementById('total-count');

    try {
        var res  = await fetch(API_BASE + '/transactions/all',
            { credentials: 'include' });
        var data = await res.json();

        countEl.textContent = data.total +
            (data.total !== 1 ? ' records' : ' record');

        if (data.total === 0) {
            container.innerHTML =
                '<p style="color:#64748b;text-align:center;padding:2rem">' +
                '<i class="fas fa-inbox" style="font-size:2rem;' +
                'display:block;margin-bottom:0.5rem"></i>' +
                'No transactions recorded yet.</p>';
            return;
        }

        container.innerHTML =
            '<div style="overflow-x:auto">' +
            '<table class="mapping-tbl"><thead><tr>' +
            '<th>#</th><th>Date</th><th>Customer</th>' +
            '<th>Product</th><th>Category</th><th>Qty</th>' +
            '<th>Unit Price</th><th>Amount</th>' +
            '<th>Channel</th><th>Action</th>' +
            '</tr></thead><tbody>' +
            data.transactions.map(function(t, i) {
                return '<tr>' +
                    '<td>' + (i + 1) + '</td>' +
                    '<td>' + (t.Date || '—') + '</td>' +
                    '<td>' + (t.Customer_Name || '—') + '</td>' +
                    '<td>' + t.Product + '</td>' +
                    '<td>' + t.Category + '</td>' +
                    '<td>' + t.Quantity + '</td>' +
                    '<td>' + Number(t.Unit_Price).toLocaleString('fr-CM') +
                    ' FCFA</td>' +
                    '<td>' + Number(t.Amount).toLocaleString('fr-CM') +
                    ' FCFA</td>' +
                    '<td>' + t.Channel + '</td>' +
                    '<td><button class="delete-btn" onclick="deleteTransaction(' +
                    i + ')" title="Delete">' +
                    '<i class="fas fa-trash"></i></button></td>' +
                    '</tr>';
            }).join('') +
            '</tbody></table></div>';

    } catch(err) {
        container.innerHTML =
            '<p class="status-error">Could not load transactions.</p>';
    }
}

async function deleteTransaction(index) {
    if (!confirm('Delete this transaction?')) return;
    try {
        var res = await fetch(
            API_BASE + '/transactions/delete/' + index,
            { method: 'DELETE', credentials: 'include' }
        );
        if (res.ok) loadTransactions();
    } catch(err) {
        alert('Could not delete transaction.');
    }
}

loadTransactions();