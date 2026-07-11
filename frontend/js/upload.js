const API = 'http://127.0.0.1:8000/api';

document.getElementById('certInput')?.addEventListener('change', function() {
  document.getElementById('fileName').textContent = this.files[0]?.name ? `Selected: ${this.files[0].name}` : '';
});

async function extractSkills() {
  const token = localStorage.getItem('token');
  if (!token) { window.location.href = '/login/'; return; }
  const fileInput = document.getElementById('certInput');
  if (!fileInput.files.length) { alert('Please upload a certificate first!'); return; }

  const skillsBox  = document.getElementById('skillsBox');
  const skillsList = document.getElementById('skillsList');
  skillsList.innerHTML = '';
  skillsBox.style.display = 'none';

  const btn = document.querySelector('.upload-card button');
  if (btn) { btn.textContent = 'Extracting...'; btn.disabled = true; }

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  try {
    const res  = await fetch(`${API}/certificates/upload/`, {
      method:'POST', headers:{'Authorization':`Token ${token}`}, body:formData,
    });
    const data = await res.json();
    if (res.ok) {
      const skills = data.skills || [];
      localStorage.setItem('userSkills', JSON.stringify(skills));
      if (skills.length === 0) {
        skillsList.innerHTML = '<p style="color:#f59e0b;">⚠️ No skills detected. Try a clearer PDF.</p>';
      } else {
        skills.forEach(skill => {
          const span = document.createElement('span');
          span.className = 'skill-tag';
          span.textContent = skill;
          skillsList.appendChild(span);
        });
      }
      skillsBox.style.display = 'block';
    } else {
      alert(data.error || 'Upload failed.');
    }
  } catch(e) {
    alert('Cannot connect to server. Make sure Django is running!');
  } finally {
    if (btn) { btn.textContent = 'Extract Skills'; btn.disabled = false; }
  }
}

function goToDashboard() { window.location.href = '/dashboard/'; }

async function logout() {
  const token = localStorage.getItem('token');
  if (token) await fetch(`${API}/auth/logout/`, { method:'POST', headers:{'Authorization':`Token ${token}`} }).catch(()=>{});
  localStorage.clear();
  window.location.href = '/';
}
