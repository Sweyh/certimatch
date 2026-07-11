/**
 * auth.js — CertiMatch
 * Connects Signup/Login forms to the Django REST API.
 */

const API_BASE = 'http://localhost:8000/api';

/* ─── Helper ───────────────────────────────────────────── */
function saveAuth(token, email, fullName) {
    localStorage.setItem('authToken', token);
    localStorage.setItem('userEmail', email);
    localStorage.setItem('userName', fullName || email);
}

function getToken() {
    return localStorage.getItem('authToken');
}

function requireAuth() {
    if (!getToken()) {
        window.location.href = 'login.html';
    }
}

function logout() {
    fetch(`${API_BASE}/auth/logout/`, {
        method: 'POST',
        headers: { 'Authorization': `Token ${getToken()}` }
    }).finally(() => {
        localStorage.clear();
        window.location.href = 'index.html';
    });
}

/* ─── Signup ────────────────────────────────────────────── */
document.getElementById('signupForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();

    const name     = document.getElementById('name')?.value.trim();
    const email    = document.getElementById('email')?.value.trim();
    const password = document.getElementById('password')?.value;
    const confirm  = document.getElementById('confirmPassword')?.value;

    if (password !== confirm) {
        alert('Passwords do not match!');
        return;
    }

    const btn = this.querySelector('button[type="submit"]');
    btn.textContent = 'Creating account...';
    btn.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/auth/signup/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                full_name: name,
                email,
                password,
                confirm_password: confirm,
            }),
        });

        const data = await res.json();

        if (res.ok) {
            saveAuth(data.token, data.email, data.full_name);
            alert('Account created! Redirecting to upload...');
            window.location.href = 'upload.html';
        } else {
            const errors = Object.values(data).flat().join('\n');
            alert('Signup failed:\n' + errors);
        }
    } catch (err) {
        alert('Server error. Is Django running? (python manage.py runserver)');
    } finally {
        btn.textContent = 'Create Account';
        btn.disabled = false;
    }
});

/* ─── Login ─────────────────────────────────────────────── */
document.getElementById('loginForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();

    const email    = document.getElementById('loginEmail')?.value.trim();
    const password = document.getElementById('loginPassword')?.value;

    const btn = this.querySelector('button[type="submit"]');
    btn.textContent = 'Logging in...';
    btn.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });

        const data = await res.json();

        if (res.ok) {
            saveAuth(data.token, data.email, data.full_name);
            window.location.href = 'upload.html';
        } else {
            alert(data.error || 'Invalid email or password.');
        }
    } catch (err) {
        alert('Server error. Is Django running? (python manage.py runserver)');
    } finally {
        btn.textContent = 'Login';
        btn.disabled = false;
    }
});
