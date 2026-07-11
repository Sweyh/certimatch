const API = 'http://127.0.0.1:8000/api';

async function loadJobs(filter='all') {
  const token = localStorage.getItem('token');
  if (!token) { window.location.href = '/login/'; return; }
  const container = document.getElementById('jobList');
  container.innerHTML = '<p style="text-align:center;color:#64748b;padding:40px;">Loading jobs...</p>';
  try {
    const res  = await fetch(`${API}/jobs/recommendations/`, { headers:{'Authorization':`Token ${token}`} });
    const data = await res.json();
    if (!res.ok) { container.innerHTML = `<p style="color:red;">${data.detail||'Error.'}</p>`; return; }
    let jobs = data.results || [];
    if (filter==='eligible') jobs = jobs.filter(j => j.missing_skills.length===0);
    if (filter==='partial')  jobs = jobs.filter(j => j.missing_skills.length>0 && j.match_score>0);
    if (!jobs.length) { container.innerHTML = '<p style="text-align:center;color:#64748b;padding:40px;">No jobs found. Upload a certificate first!</p>'; return; }
    container.innerHTML = '';
    jobs.forEach(job => {
      const eligible = job.missing_skills.length===0;
      const card = document.createElement('div');
      card.className = 'job-card'+(eligible?' eligible-card':'');
      card.innerHTML = `
        <div class="job-header">
          <div class="company-initial">${job.company[0]}</div>
          <div><h3>${job.company}</h3><p class="job-role">${job.job_title}</p></div>
          <span class="match-badge ${eligible?'badge-green':job.match_score>=50?'badge-orange':'badge-red'}">${job.match_score}% match</span>
        </div>
        <div class="job-meta"><span>💰 ₹${job.salary_lpa} LPA</span></div>
        <div class="skill-tags">
          ${job.skills_list.map(s=>`<span class="tag ${job.missing_skills.includes(s.toLowerCase())?'tag-red':'tag-green'}">${s}</span>`).join('')}
        </div>
        ${job.missing_skills.length?`
          <div style="margin-top:12px; padding:10px; background:#fef3c7; border-radius:6px; border-left:4px solid #f59e0b;">
            <p style="margin:0 0 8px; font-size:0.85rem; color:#92400e;"><strong>⚠️ Skill Gap:</strong></p>
            <p style="margin:0; font-size:0.85rem; color:#b45309;"><strong>${job.missing_skills.join(', ')}</strong></p>
          </div>
        `:'<p style="font-size:0.83rem;color:#10b981;margin-top:8px;margin-bottom:8px;">✅ All skills matched!</p>'}
        <div style="margin-top:12px; display:flex; gap:8px;">
          <button class="apply-btn" ${eligible?'':'disabled'} onclick="applyJob(${job.id},'${job.company}','${job.job_title}')">
            ${eligible?'Apply Now →':'Skill Gap Detected'}
          </button>
          <button class="apply-btn" style="background:#3b82f6;" onclick="analyzeGap('${job.job_title}')">
            📊 Skill Gap
          </button>
        </div>`;
      container.appendChild(card);
    });
  } catch(e) { container.innerHTML = '<p style="color:red;text-align:center;">Cannot connect to server.</p>'; }
}

async function applyJob(id, company, role) {
  const token = localStorage.getItem('token');
  const res   = await fetch(`${API}/jobs/${id}/apply/`, { method:'POST', headers:{'Authorization':`Token ${token}`} });
  const data  = await res.json();
  alert(data.message||'Application submitted!');
}

function analyzeGap(jobTitle) {
  localStorage.setItem('targetRole', jobTitle);
  window.location.href = '/skillgap/';
}

async function logout() {
  const token = localStorage.getItem('token');
  if (token) await fetch(`${API}/auth/logout/`, { method:'POST', headers:{'Authorization':`Token ${token}`} }).catch(()=>{});
  localStorage.clear();
  window.location.href = '/';
}

document.addEventListener('DOMContentLoaded', () => {
  loadJobs('all');
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active-filter'));
      btn.classList.add('active-filter');
      loadJobs(btn.dataset.filter);
    });
  });
});
