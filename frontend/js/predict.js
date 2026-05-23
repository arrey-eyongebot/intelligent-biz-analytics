// ============================================================
// predict.js — Demand Prediction Form Logic
// Collects user input from the prediction form, sends it to
// the backend ML endpoint, and displays the prediction result
// with restocking advice.
// ============================================================

// Base URL for all backend API calls
const API_BASE = 'http://127.0.0.1:5000/api';


// ── Event: Predict Button Clicked ────────────────────────────
// Fires when the user clicks "Predict Demand"
document.getElementById('predict-btn').addEventListener('click', async () => {

    // ── Collect Form Values ──────────────────────────────────
    const product    = document.getElementById('product').value.trim();
    const category   = document.getElementById('category').value;
    const channel    = document.getElementById('channel').value;
    const unit_price = document.getElementById('unit_price').value;
    const month      = document.getElementById('month').value;

    // ── Validate: All fields must be filled ─────────────────
    if (!product || !category || !channel || !unit_price || !month) {
        alert('Please fill in all fields.');
        return;
    }

    // ── Show Loading Spinner ─────────────────────────────────
    const resultBox     = document.getElementById('result-box');
    const resultContent = document.getElementById('result-content');
    resultBox.style.display = 'block';
    resultContent.innerHTML = '<div class="spinner"></div>';

    try {
        // ── Send POST request to the prediction endpoint ─────
        // We send JSON data (not FormData) since it's structured input
        const res = await fetch(`${API_BASE}/predict/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                product,
                category,
                channel,
                unit_price, // Backend converts this to float
                month       // Backend converts this to int
            })
        });

        const data = await res.json(); // Parse response

        if (res.ok) {
            // ── Success: Display prediction results ──────────
            resultContent.innerHTML = `
                <p>
                    <strong>Product:</strong>
                    ${data.product}
                </p>
                <p>
                    <strong>Predicted Demand:</strong>
                    ${data.predicted_demand} units
                </p>
                <p>
                    <strong>Advice:</strong>
                    ${data.restock_advice}
                </p>
            `;
        } else {
            // ── Backend returned an error ────────────────────
            resultContent.innerHTML = `
                <p style="color:red">${data.error}</p>
            `;
        }

    } catch (err) {
        // ── Network error: server not reachable ──────────────
        resultContent.innerHTML = `
            <p style="color:red">Could not connect to server.</p>
        `;
    }
});