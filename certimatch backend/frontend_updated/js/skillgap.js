/**
 * skillgap.js — CertiMatch
 * Calls Django /api/skillgap/analyze/ using user's real extracted skills.
 */

const API_BASE = 'http://localhost:8000/api';

// Pre-fill from jobs page if redirected
document.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('targetRole');
    if (saved) {
        const input = document.getElementById('targetRole');
        if (input) input.value = saved;
        localStorage.removeItem('targetRole');
    }
});

async function analyzeSkill() {
    const token = localStorage.getItem('authToken');
    if (!token) { window.location.href = 'login.html'; return; }

    const role   = document.getElementById('targetRole').value.trim();
    const result = document.getElementById('skillResult');

    if (!role) {
        result.innerHTML = '<p style="color:red;">Please enter a target role.</p>';
        return;
    }

    result.innerHTML = '<p style="color:#888;">Analyzing...</p>';

    try {
        const res = await fetch(`${API_BASE}/skillgap/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${token}`,
            },
            body: JSON.stringify({ target_role: role }),
        });

        const data = await res.json();

        if (!res.ok || data.error) {
            result.innerHTML = `<p style="color:#e74c3c;">❌ ${data.error || 'Analysis failed.'}</p>`;
            return;
        }

        const readinessColor = data.readiness_percent >= 70 ? 'green'
                             : data.readiness_percent >= 40 ? 'orange' : '#c0392b';

        const missingSuggestionsHTML = data.suggestions?.length
            ? `<div style="margin-top:16px;">
                <strong>📚 Suggested Courses:</strong>
                <ul style="margin-top:8px; padding-left:20px;">
                    ${data.suggestions.map(s =>
                        `<li><strong>${s.skill}:</strong> ${s.course}</li>`
                    ).join('')}
                </ul>
               </div>`
            : '';

        result.innerHTML = `
            <div style="background:#f9f9f9; padding:16px; border-radius:8px; margin-top:16px;">
                <h3>📊 Skill Gap: <em>${data.target_role}</em></h3>

                <p><strong>Readiness:</strong>
                    <span style="color:${readinessColor}; font-size:20px; font-weight:bold;">
                        ${data.readiness_percent}%
                    </span>
                </p>

                <div style="background:#eee; border-radius:8px; height:12px; margin:8px 0;">
                    <div style="background:${readinessColor}; width:${data.readiness_percent}%;
                                height:100%; border-radius:8px;"></div>
                </div>

                ${data.matched?.length
                    ? `<p>✅ <strong>You have:</strong> ${data.matched.join(', ')}</p>`
                    : ''}

                ${data.missing?.length
                    ? `<p>⚠️ <strong>Missing:</strong> ${data.missing.join(', ')}</p>`
                    : '<p style="color:green;">🎉 You have all required skills!</p>'}

                ${missingSuggestionsHTML}

                ${data.user_skills?.length
                    ? `<p style="font-size:12px; color:#888; margin-top:12px;">
                        Your skills from certificates: ${data.user_skills.join(', ')}
                       </p>`
                    : `<p style="font-size:12px; color:#e67e22;">
                        <a href="upload.html">Upload a certificate</a> for personalized analysis.
                       </p>`}
            </div>
        `;

    } catch (err) {
        result.innerHTML = '<p style="color:red;">Server error. Is Django running?</p>';
    }
}
