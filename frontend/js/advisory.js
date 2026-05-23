// ============================================================
// advisory.js — Business Advisory Page Logic
// Fetches rule-based business recommendations from the backend
// and renders them as styled advice cards on the page.
// ============================================================

// Base URL for all backend API calls
const API_BASE = 'http://127.0.0.1:5000/api';


// ── Icon Mapping ─────────────────────────────────────────────
// Maps each advice type to a Font Awesome icon class
// These icons are displayed on each advice card
const icons = {
    'Top Product':         'fas fa-trophy',       // Best seller
    'Slow Moving Product': 'fas fa-box',           // Low sales
    'Best Channel':        'fas fa-store',         // Online/Onsite
    'Peak Sales Period':   'fas fa-calendar-alt',  // Best month
    'Top Category':        'fas fa-tags'           // Best category
};


// ── Load Advisory Recommendations ────────────────────────────
// Fetches recommendations from the backend and renders cards
async function loadAdvisory() {
    const container = document.getElementById('advisory-content');

    try {
        // Fetch recommendations from backend advisory endpoint
        const res  = await fetch(`${API_BASE}/advisory/recommendations`);
        const data = await res.json();

        if (!res.ok) {
            // Show error if backend returned a problem
            container.innerHTML = `
                <p style="color:red">${data.error}</p>
            `;
            return;
        }

        // ── Render Each Recommendation as a Card ─────────────
        // We use .map() to convert each advice object into HTML
        // then .join('') to combine them into one string
        container.innerHTML = data.recommendations.map(advice => `
            <div class="advice-card">
                <!-- Icon based on advice type, fallback to lightbulb -->
                <i class="${icons[advice.type] || 'fas fa-lightbulb'}"></i>
                <div>
                    <!-- Advice type as card title -->
                    <h4>${advice.type}</h4>
                    <!-- Advice message as card body -->
                    <p>${advice.message}</p>
                </div>
            </div>
        `).join('');

    } catch (err) {
        // ── Network error: backend not running ───────────────
        container.innerHTML = `
            <p style="color:red">Could not connect to server.</p>
        `;
    }
}


// ── Initialize Page ──────────────────────────────────────────
// Load advisory content as soon as the page opens
loadAdvisory();