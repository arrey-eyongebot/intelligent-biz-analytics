const API_BASE = 'http://127.0.0.1:5000/api';

document.getElementById('predict-btn').addEventListener('click', async () => {
    const product    = document.getElementById('product').value.trim();
    const category   = document.getElementById('category').value;
    const channel    = document.getElementById('channel').value;
    const unit_price = document.getElementById('unit_price').value;
    const month      = document.getElementById('month').value;

    if (!product || !category || !channel || !unit_price || !month) {
        alert('Please fill in all fields.');
        return;
    }

    const resultBox     = document.getElementById('result-box');
    const resultContent = document.getElementById('result-content');
    resultBox.style.display  = 'block';
    resultContent.innerHTML  = '<div class="spinner"></div>';

    try {
        const res = await fetch(`${API_BASE}/predict/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ product, category, channel, unit_price, month })
        });

        const data = await res.json();

        if (res.ok) {
            resultContent.innerHTML = `
                <p><strong>Product:</strong> ${data.product}</p>
                <p><strong>Predicted Demand:</strong> ${data.predicted_demand} units</p>
                <p><strong>Advice:</strong> ${data.restock_advice}</p>
            `;
        } else {
            resultContent.innerHTML = `<p style="color:red">${data.error}</p>`;
        }
    } catch (err) {
        resultContent.innerHTML = `<p style="color:red">Could not connect to server.</p>`;
    }
});