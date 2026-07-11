const API = 'http://127.0.0.1:8000/api';

async function loadMatchingJobs() {
  const token = localStorage.getItem('token');
  if (!token) { window.location.href = '/login/'; return; }
  
  const jobsEl = document.getElementById('matchingJobs');
  if (!jobsEl) return;
  
  jobsEl.innerHTML = '<p style="color:#64748b;">Loading recommended jobs...</p>';
  
  try {
    const res = await fetch(`${API}/jobs/recommendations/`, {
      headers: { 'Authorization': `Token ${token}` }
    });
    const data = await res.json();
    
    if (!res.ok) {
      jobsEl.innerHTML = `<p style="color:#64748b;">${data.message || 'No job recommendations yet.'}</p>`;
      return;
    }
    
    if (!data.results || data.results.length === 0) {
      jobsEl.innerHTML = '<p style="color:#64748b;">Upload certificates to get job recommendations.</p>';
      return;
    }
    
    jobsEl.innerHTML = '';
    data.results.slice(0, 6).forEach(job => {
      const eligible = job.missing_skills?.length === 0;
      const card = document.createElement('div');
      card.className = 'job-card' + (eligible ? ' eligible-card' : '');
      card.innerHTML = `
        <div class="job-header">
          <div class="company-initial">${job.company[0]}</div>
          <div><h3>${job.company}</h3><p class="job-role">${job.job_title}</p></div>
          <span class="match-badge ${eligible ? 'badge-green' : job.match_score >= 50 ? 'badge-orange' : 'badge-red'}">${job.match_score}% match</span>
        </div>
        <div class="job-meta"><span>💰 ₹${job.salary_lpa} LPA</span></div>
        <div class="skill-tags">
          ${job.skills_list.map(s => `<span class="tag ${job.missing_skills?.includes(s.toLowerCase()) ? 'tag-red' : 'tag-green'}">${s}</span>`).join('')}
        </div>
        ${job.missing_skills?.length ? `<p class="gap-note" style="margin-top:8px;">Missing: <strong>${job.missing_skills.join(', ')}</strong></p>` : '<p style="font-size:0.83rem;color:#10b981;margin-top:8px;">All skills matched ✓</p>'}
      `;
      jobsEl.appendChild(card);
    });
  } catch(e) { 
    jobsEl.innerHTML = '<p style="color:red;">Cannot connect to server.</p>'; 
  }
}

async function analyzeSkill() {
  const token = localStorage.getItem('token');
  if (!token) { window.location.href = '/login/'; return; }
  const targetRole = document.getElementById('targetRole').value.trim();
  const resultEl   = document.getElementById('skillResult');
  if (!targetRole) { resultEl.innerHTML='<p class="error-msg">Please enter a target role.</p>'; return; }
  resultEl.innerHTML='<p style="text-align:center;color:#64748b;">Analyzing...</p>';
  try {
    const res  = await fetch(`${API}/skillgap/analyze/`, {
      method:'POST', headers:{'Content-Type':'application/json','Authorization':`Token ${token}`},
      body: JSON.stringify({target_role:targetRole}),
    });
    const data = await res.json();
    if (!res.ok) { resultEl.innerHTML=`<p class="error-msg">${data.error||'Analysis failed.'}</p>`; return; }
    const c = data.readiness_percent>=80?'#10b981':data.readiness_percent>=50?'#f59e0b':'#ef4444';
    resultEl.innerHTML = `
      <div class="gap-output">
        <div class="score-ring" style="--score-color:${c}">
          <div class="score-inner"><span class="score-num">${data.readiness_percent}%</span><span class="score-label">Ready</span></div>
        </div>
        <h3>Analysis for: <em>${data.target_role}</em></h3>
        <div style="margin-top:16px;">
          <p style="font-size:0.9rem; color:#64748b;"><strong>Required Skills:</strong> ${data.total_required}</p>
          <p style="font-size:0.9rem; color:#10b981;"><strong>✅ You Have:</strong> ${data.matched_count}</p>
          <p style="font-size:0.9rem; color:#ef4444;"><strong>❌ Need to Learn:</strong> ${data.missing_count}</p>
        </div>
        ${data.matched?.length?`<div class="skill-section" style="margin-top:16px;"><h4 style="color:#10b981">✅ Skills You Have (${data.matched_count})</h4><div class="tag-row">${data.matched.map(s=>`<span class="tag tag-have">${s}</span>`).join('')}</div></div>`:''}
        ${data.missing?.length?`
          <div class="skill-section" style="margin-top:16px;"><h4 style="color:#ef4444">❌ Skills to Learn (${data.missing_count})</h4>
          <div class="tag-row">${data.missing.map(s=>`<span class="tag tag-miss">${s}</span>`).join('')}</div></div>
          <div class="resources-section" style="margin-top:20px;"><h4>📚 Learning Resources</h4>
          ${data.suggestions.map(s=>`<div class="resource-card"><div><strong>${s.skill}</strong></div><span style="font-size:0.82rem;color:#64748b;">${s.course}</span></div>`).join('')}
          </div>` : '<p class="all-clear" style="margin-top:16px;">🎉 You are fully qualified for this role!</p>'}
        ${data.error?`<p class="error-msg" style="margin-top:12px;">${data.error}</p>`:''}
      </div>`;
  } catch(e) { resultEl.innerHTML='<p class="error-msg">Cannot connect to server.</p>'; }
}

async function logout() {
  const token = localStorage.getItem('token');
  if (token) await fetch(`${API}/auth/logout/`, { method:'POST', headers:{'Authorization':`Token ${token}`} }).catch(()=>{});
  localStorage.clear();
  window.location.href = '/';
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('targetRole')?.addEventListener('keypress', e => { if(e.key==='Enter') analyzeSkill(); });
});
