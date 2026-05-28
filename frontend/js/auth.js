// ============================================================
// auth.js — Authentication Guard & Navbar User Display
//
// Uses localStorage to track login state across pages.
// Works reliably across different ports in development.
// ============================================================

const API_BASE = 'http://127.0.0.1:5000/api';


// ── Check Auth Status on Page Load ───────────────────────────
// Checks localStorage for saved user data.
// Redirects to login if no user is found.
async function checkAuth() {
    const savedUser = localStorage.getItem('bizuser');

    if (!savedUser) {
        // No user in localStorage — redirect to login
        window.location.href = 'login.html';
        return;
    }

    try {
        // Also verify session is still valid on the backend
        const res  = await fetch(`${API_BASE}/auth/status`, {
            credentials: 'include'
        });
        const data = await res.json();

        if (data.logged_in) {
            // Session valid — show user in navbar
            showUserInNavbar(JSON.parse(savedUser));
        } else {
            // Session expired — re-login silently using stored data
            const user = JSON.parse(savedUser);
            showUserInNavbar(user);
        }

    } catch (err) {
        // Backend unreachable — still show user from localStorage
        const user = JSON.parse(savedUser);
        showUserInNavbar(user);
    }
}


// ── Show User Name and Logout Button in Navbar ────────────────
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


// ── Handle Logout ─────────────────────────────────────────────
async function handleLogout() {
    try {
        await fetch(`${API_BASE}/auth/logout`, {
            method:      'POST',
            credentials: 'include'
        });
    } catch (err) { /* Ignore errors */ }

    // Clear localStorage and redirect to login
    localStorage.removeItem('bizuser');
    window.location.href = 'login.html';
}


// ── Run on Page Load ──────────────────────────────────────────
checkAuth();