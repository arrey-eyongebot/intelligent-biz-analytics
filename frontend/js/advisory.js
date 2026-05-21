const API_BASE = 'http://127.0.0.1:5000/api';

const icons = {
    'Top Product':        'fas fa-trophy',
    'Slow Moving Product':'fas fa-box',
    'Best Channel':       'fas fa-store',
    'Peak Sales Period':  'fas fa-calendar-alt',
    'Top Category':       'fas fa-tags'
};

async function loadAdvisory() {
    const container = document.getElementById('advisory-content');

    try {
        const res  = await fetch(`${API_BASE}/advisory/recommendations`);
        const data = await res.json();

        if (!res.ok) {
            container.innerHTML = `<p style="color:red">${data.error}</p>`;
            return;
        }

        container.innerHTML = data.recommendations.map(advice => `
            <div class="advice-card">
                <i class="${icons[advice.type] || 'fas fa-lightbulb'}"></i>
                <div>
                    <h4>${advice.type}</h4>
                    <p>${advice.message}</p>
                </div>
            </div>
        `).join('');

    } catch (err) {
        container.innerHTML = `<p style="color:red">Could not connect to server.</p>`;
    }
}

loadAdvisory();