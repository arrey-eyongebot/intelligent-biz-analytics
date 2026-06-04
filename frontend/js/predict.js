// ============================================================
// predict.js — Demand Prediction Form Logic
//
// Handles the prediction page form:
// 1. Collects user input (product, category, channel, price, month)
// 2. Validates that all fields are filled
// 3. Sends the data as JSON to POST /api/predict/
// 4. Displays the predicted demand and restocking advice
// ============================================================

// Base URL for all API calls
var API_BASE = (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost')
    ? 'http://127.0.0.1:5000/api'
    : 'https://bizanalytics-production-66f5.up.railway.app/api';

// ── Predict Button Click ──────────────────────────────────────
document.getElementById('predict-btn').addEventListener('click', async () => {

    // Collect values from all form fields
    const product    = document.getElementById('product').value.trim();
    const category   = document.getElementById('category').value;
    const channel    = document.getElementById('channel').value;
    const unit_price = document.getElementById('unit_price').value;
    const month      = document.getElementById('month').value;

    // Validate: all fields must be filled before sending
    if (!product || !category || !channel || !unit_price || !month) {
        alert('Please fill in all fields before predicting.');
        return;
    }

    // Show spinner in the result box while waiting
    const resultBox     = document.getElementById('result-box');
    const resultContent = document.getElementById('result-content');
    resultBox.style.display = 'block';
    resultContent.innerHTML = '<div class="spinner"></div>';

    try {
        // Send prediction request as JSON to the backend ML endpoint
        const res = await fetch(`${API_BASE}/predict/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                product,
                category,
                channel,
                unit_price,  // Backend converts to float
                month        // Backend converts to int
            })
        });

        const data = await res.json();

        if (res.ok) {
            // Display the prediction result and advice
            resultContent.innerHTML = `
                <p>
                    <strong>Product:</strong> ${data.product}
                </p>
                <p>
                    <strong>Category:</strong> ${data.category}
                </p>
                <p>
                    <strong>Channel:</strong> ${data.channel}
                </p>
                <p>
                    <strong>Month:</strong> ${data.month}
                </p>
                <hr style="margin:0.75rem 0; border-color:#e2e8f0">
                <p style="font-size:1.1rem">
                    <strong>Predicted Demand:</strong>
                    <span style="color:#2563eb; font-size:1.3rem">
                        ${data.predicted_demand} units
                    </span>
                </p>
                <p style="margin-top:0.5rem">
                    <strong>Restock Advice:</strong><br>
                    ${data.restock_advice}
                </p>
            `;
        } else {
            // Show error from backend
            resultContent.innerHTML = `
                <p class="status-error">${data.error}</p>`;
        }

    } catch (err) {
        // Network or server error
        resultContent.innerHTML = `
            <p class="status-error">
                Could not connect to server.
                Make sure the backend is running.
            </p>`;
    }
});
