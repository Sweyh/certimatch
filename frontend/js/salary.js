const API = 'http://127.0.0.1:8000/api';

document.addEventListener('DOMContentLoaded', () => {
  const token = localStorage.getItem('token');
  if (!token) { window.location.href = '/login/'; return; }
  const saved = JSON.parse(localStorage.getItem('userSkills')||'[]');
  if (saved.length) { const el = document.getElementById('skills'); if(el) el.value = saved.join(', '); }

  document.getElementById('salaryForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    const role = document.getElementById('role').value.trim();
    const skills = document.getElementById('skills').value.trim();
    const experience = document.getElementById('experience').value;
    const location = document.getElementById('location').value.trim();
    const resultEl = document.getElementById('salaryResult');
    resultEl.style.display='block';
    resultEl.innerHTML='<p style="text-align:center;color:#64748b;">Predicting salary...</p>';
    try {
      const res  = await fetch(`${API}/salary/predict/`, {
        method:'POST', headers:{'Content-Type':'application/json','Authorization':`Token ${token}`},
        body: JSON.stringify({role, skills, experience:parseInt(experience), location}),
      });
      const data = await res.json();
      if (res.ok) {
        resultEl.innerHTML = `
          <div class="salary-output">
            <h3>💰 Estimated Salary Range</h3>
            <div class="salary-range">
              <div class="range-item low"><span class="label">Minimum</span><span class="amount">₹${data.min_lpa} LPA</span></div>
              <div class="range-item mid highlighted"><span class="label">Expected</span><span class="amount">₹${data.predicted_lpa} LPA</span></div>
              <div class="range-item high"><span class="label">Maximum</span><span class="amount">₹${data.max_lpa} LPA</span></div>
            </div>
            <div class="salary-meta">
              <p>📍 Location: <strong>${location}</strong></p>
              <p>📅 Experience: <strong>${experience} year(s)</strong></p>
              <p style="font-size:0.8rem;color:#94a3b8;margin-top:8px;">${data.note||''}</p>
            </div>
          </div>`;
      } else {
        resultEl.innerHTML = `<p style="color:red;">${data.error||'Prediction failed.'}</p>`;
      }
    } catch(e) { resultEl.innerHTML='<p style="color:red;">Cannot connect to server.</p>'; }
  });
});

async function logout() {
  const token = localStorage.getItem('token');
  if (token) await fetch(`${API}/auth/logout/`, { method:'POST', headers:{'Authorization':`Token ${token}`} }).catch(()=>{});
  localStorage.clear();
  window.location.href = '/';
}
