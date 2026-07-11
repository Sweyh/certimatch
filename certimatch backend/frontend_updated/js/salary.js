/**
 * salary.js — CertiMatch
 * Calls Django /api/salary/predict/ which uses the ML model dataset.
 */

const API_BASE = 'http://localhost:8000/api';

document.getElementById('salaryForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();

    const token = localStorage.getItem('authToken');
    if (!token) { window.location.href = 'login.html'; return; }

    const role       = document.getElementById('role').value.trim();
    const skills     = document.getElementById('skills').value.trim();
    const experience = parseInt(document.getElementById('experience').value) || 0;
    const location   = document.getElementById('location').value.trim();
    const result     = document.getElementById('salaryResult');

    const btn = this.querySelector('button[type="submit"]');
    btn.textContent = 'Predicting...';
    btn.disabled = true;
    result.innerHTML = '';

    try {
        const res = await fetch(`${API_BASE}/salary/predict/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${token}`,
            },
            body: JSON.stringify({ role, skills, experience, location }),
        });

        const data = await res.json();

        if (res.ok) {
            result.innerHTML = `
                <div style="background:#f0f8ff; padding:16px; border-radius:8px; margin-top:16px;">
                    <h3>💰 Salary Prediction for <em>${role}</em></h3>
                    <p><strong>Predicted:</strong> ₹${data.predicted_lpa} LPA</p>
                    <p><strong>Range:</strong> ₹${data.min_lpa} LPA — ₹${data.max_lpa} LPA</p>
                    <p style="font-size:12px; color:#888;">${data.note}</p>
                </div>
            `;
        } else {
            result.innerHTML = `<p style="color:red;">${data.error || 'Prediction failed.'}</p>`;
        }
    } catch (err) {
        result.innerHTML = '<p style="color:red;">Server error. Is Django running?</p>';
    } finally {
        btn.textContent = 'Predict Salary';
        btn.disabled = false;
    }
});
