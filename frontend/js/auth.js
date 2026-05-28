// ============================================================
// auth.js — Authentication Guard & Navbar User Display
//
// This file is included in every protected page
// (index, dashboard, predict, advisory, transactions).
//
// It does three things:
// 1. Checks if the user is logged in via the backend session
// 2. Redirects to login.html if they are not logged in
// 3. Shows the logged-in user's name and a logout button
//    in the navbar of every protected page
// ============================================================

const API_BASE = 'http://127.0.0.1:5000/api';


// ── Check Auth Status on Page Load ───────────────────────────
// Called automatically when any protected page loads.
// Redirects to login if session is not active.
async function checkAuth() {
    try {
        const res  = await fetch(`${API_BASE}/auth/status`, {
            credentials: 'include'  // Send session cookie with request
        });
        const data = await res.json();

        if (!data.logged_in) {
            // Not logged in — redirect to login page
            window.location.href = 'login.html';
            return;
        }

        // Logged in — show user info in navbar
        showUserInNavbar(data.user);

    } catch (err) {
        // If backend is unreachable, redirect to login
        window.location.href = 'login.html';
    }
}


// ── Show User Name and Logout in Navbar ───────────────────────
// Appends the user's name and a logout button to the navbar
function showUserInNavbar(user) {
    const navLinks = document.querySelector('.nav-links');
    if (!navLinks) return;

    // Create user info element
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
// Calls the logout endpoint, clears local storage,
// and redirects the user to the login page
async function handleLogout() {
    try {
        await fetch(`${API_BASE}/auth/logout`, {
            method:      'POST',
            credentials: 'include'
        });
    } catch (err) { /* Ignore errors on logout */ }

    // Clear any locally stored user data
    localStorage.removeItem('bizuser');

    // Redirect to login page
    window.location.href = 'login.html';
}


// ── Run Auth Check When Page Loads ───────────────────────────
checkAuth();
