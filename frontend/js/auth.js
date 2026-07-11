const API = 'http://127.0.0.1:8000/api';

const signupForm = document.getElementById('signupForm');
if (signupForm) {
  signupForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const name    = document.getElementById('name').value.trim();
    const email   = document.getElementById('email').value.trim();
    const pass    = document.getElementById('password').value;
    const confirm = document.getElementById('confirmPassword').value;
    if (pass !== confirm) { showMsg('Passwords do not match!','error'); return; }
    if (pass.length < 6)  { showMsg('Password must be at least 6 characters.','error'); return; }
    showMsg('Creating account...','info');
    try {
      const res  = await fetch(`${API}/auth/signup/`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ full_name:name, email, password:pass, confirm_password:confirm }),
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('certimatch_user', JSON.stringify({name:data.full_name, email:data.email}));
        showMsg('Account created! Redirecting...','success');
        setTimeout(() => { window.location.href = '/upload/'; }, 1200);
      } else {
        const err = typeof data === 'object' ? Object.values(data).flat().join(' ') : 'Signup failed.';
        showMsg(err,'error');
      }
    } catch(e) { showMsg('Cannot connect to server. Is Django running?','error'); }
  });
}

const loginForm = document.getElementById('loginForm');
if (loginForm) {
  loginForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value.trim();
    const pass  = document.getElementById('loginPassword').value;
    showMsg('Logging in...','info');
    try {
      const res  = await fetch(`${API}/auth/login/`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ email, password:pass }),
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('certimatch_user', JSON.stringify({name:data.full_name, email:data.email, is_admin:!!data.is_admin}));
        showMsg('Login successful! Redirecting...','success');
        setTimeout(() => { window.location.href = data.is_admin ? '/admin-users/' : '/dashboard/'; }, 1200);
      } else {
        showMsg(data.error || 'Invalid email or password.','error');
      }
    } catch(e) { showMsg('Cannot connect to server. Is Django running?','error'); }
  });
}

async function logout() {
  const token = localStorage.getItem('token');
  if (token) await fetch(`${API}/auth/logout/`, { method:'POST', headers:{'Authorization':`Token ${token}`} }).catch(()=>{});
  localStorage.clear();
  window.location.href = '/';
}

function showMsg(msg, type='success') {
  let el = document.getElementById('authMessage');
  if (!el) {
    el = document.createElement('div');
    el.id = 'authMessage';
    el.style.cssText = 'margin-top:14px;padding:12px 16px;border-radius:8px;font-size:14px;font-weight:500;text-align:center;';
    const f = document.querySelector('form') || document.querySelector('.auth-container');
    if (f) f.appendChild(el);
  }
  const s = {success:['#e6f9f0','#1a7a4a','#a3e4c1'],error:['#fff0f0','#c0392b','#f5b7b1'],info:['#eff6ff','#1d4ed8','#bfdbfe']};
  const [bg,color,border] = s[type]||s.info;
  el.style.background=bg; el.style.color=color; el.style.border=`1px solid ${border}`;
  el.textContent=msg;
}
