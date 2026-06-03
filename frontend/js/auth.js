// ============================================================
// auth.js — Authentication Guard & Navbar User Display
//
// NOTE: API_BASE is NOT declared here to avoid conflicts
// with other JS files loaded on the same page.
// It uses its own local constant instead.
// ============================================================

// Local API URL — not exported to avoid duplicate declaration AUTH_API
var AUTH_API = (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost')
    ? 'http://127.0.0.1:5000/api'
    : '/api';

async function checkAuth() {
    const savedUser = localStorage.getItem('bizuser');

    if (!savedUser) {
        window.location.href = 'login.html';
        return;
    }

    try {
        const res  = await fetch(`${AUTH_API}/auth/status`, {
            credentials: 'include'
        });
        const data = await res.json();
        showUserInNavbar(JSON.parse(savedUser));
    } catch (err) {
        const user = JSON.parse(savedUser);
        showUserInNavbar(user);
    }
}

function showUserInNavbar(user) {
    const navLinks = document.querySelector('.nav-links');
    if (!navLinks) return;

    const userEl = document.createElement('div');
    userEl.className = 'nav-user';
    userEl.innerHTML = `
        <span class="nav-username">
            <i class="fas fa-user-circle"></i>
            ${user.name}
        </span>
        <button class="nav-logout-btn" onclick="handleLogout()">
            <i class="fas fa-sign-out-alt"></i> Logout
        </button>
    `;
    navLinks.appendChild(userEl);
}

async function handleLogout() {
    try {
        await fetch(`${AUTH_API}/auth/logout`, {
            method:      'POST',
            credentials: 'include'
        });
    } catch (err) {}

    localStorage.removeItem('bizuser');
    window.location.href = 'login.html';
}

checkAuth();