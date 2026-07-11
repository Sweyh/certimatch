/**
 * jobs.js — CertiMatch
 * Loads AI-recommended jobs from Django backend using TF-IDF model.
 */

const API_BASE = 'http://localhost:8000/api';

async function loadRecommendedJobs() {
    const token = localStorage.getItem('authToken');
    if (!token) { window.location.href = 'login.html'; return; }

    const jobList = document.getElementById('jobList');
    jobList.innerHTML = '<p style="color:#888">Loading AI-matched jobs...</p>';

    try {
        const res = await fetch(`${API_BASE}/jobs/recommendations/`, {
            headers: { 'Authorization': `Token ${token}` }
        });
        const data = await res.json();

        if (!res.ok) {
            jobList.innerHTML = `<p style="color:red">${data.error || 'Failed to load jobs.'}</p>`;
            return;
        }

        if (!data.results || data.results.length === 0) {
            jobList.innerHTML = '<p>No recommendations yet. <a href="upload.html">Upload a certificate</a> first!</p>';
            return;
        }

        jobList.innerHTML = '';
        data.results.forEach(job => {
            const card = document.createElement('div');
            card.className = 'job-card';

            const matchColor = job.match_score >= 70 ? 'green' : job.match_score >= 40 ? 'orange' : '#c0392b';

            card.innerHTML = `
                <h3>${job.job_title}</h3>
                <p><strong>Company:</strong> ${job.company}</p>
                <p class="match" style="color:${matchColor}; font-weight:bold;">
                    Match: ${job.match_score}%
                </p>
                <p><strong>Salary:</strong> ₹${job.salary_lpa.toFixed(1)} LPA</p>
                ${job.missing_skills?.length
                    ? `<p style="font-size:13px; color:#e67e22;"><strong>Missing:</strong> ${job.missing_skills.join(', ')}</p>`
                    : `<p style="font-size:13px; color:green;">✅ All skills matched!</p>`
                }
                <div style="margin-top:12px; display:flex; gap:8px;">
                    <button onclick="applyJob(${job.id}, '${job.job_title}', '${job.company}', this)">Apply</button>
                    <button onclick="viewSkillGap('${job.job_title}')">Skill Gap</button>
                </div>
            `;
            jobList.appendChild(card);
        });

    } catch (err) {
        jobList.innerHTML = '<p style="color:red">Server error. Is Django running?</p>';
    }
}

async function applyJob(jobId, role, company, btn) {
    const token = localStorage.getItem('authToken');
    btn.disabled = true;
    btn.textContent = 'Applying...';

    try {
        const res = await fetch(`${API_BASE}/jobs/${jobId}/apply/`, {
            method: 'POST',
            headers: { 'Authorization': `Token ${token}` }
        });
        const data = await res.json();
        alert(data.message || `Applied to ${role} at ${company}!`);
        btn.textContent = 'Applied ✓';
    } catch (err) {
        alert('Failed to apply. Try again.');
        btn.disabled = false;
        btn.textContent = 'Apply';
    }
}

function viewSkillGap(role) {
    localStorage.setItem('targetRole', role);
    window.location.href = 'skillgap.html';
}

// Auto-load on page ready
document.addEventListener('DOMContentLoaded', loadRecommendedJobs);
