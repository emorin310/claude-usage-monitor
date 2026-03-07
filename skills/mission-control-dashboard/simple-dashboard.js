const express = require('express');
const app = express();
app.use(express.json());
app.use(express.urlencoded({extended: true}));

let isAuthenticated = false;

app.get('/login', (req, res) => {
  res.send(`<html><head><title>🎛️ Mission Control</title><style>
  body{font-family:Arial,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);margin:0;padding:0;min-height:100vh;display:flex;align-items:center;justify-content:center;}
  .login{background:white;padding:2rem;border-radius:10px;box-shadow:0 10px 25px rgba(0,0,0,0.1);width:400px;}
  input{width:100%;padding:0.75rem;margin:0.5rem 0;border:2px solid #ddd;border-radius:5px;box-sizing:border-box;}
  button{width:100%;padding:0.75rem;background:#667eea;color:white;border:none;border-radius:5px;cursor:pointer;margin-top:1rem;}
  </style></head><body>
  <div class="login"><h1>🎛️ Mission Control</h1>
  <form method="post" action="/auth"><input type="text" name="user" placeholder="admin" required>
  <input type="password" name="pass" placeholder="magrathea2024!" required>
  <button type="submit">Login</button></form>
  <p style="text-align:center;margin-top:1rem;color:#666;font-size:14px;">Default: admin / magrathea2024!</p>
  </div></body></html>`);
});

app.get('/', (req, res) => {
  if (!isAuthenticated) return res.redirect('/login');
  res.send(`<html><head><title>🎛️ Mission Control Dashboard</title><style>
  body{font-family:Arial,sans-serif;margin:0;background:#f5f5f5;}
  .header{background:#667eea;color:white;padding:1rem;text-align:center;}
  .nav{background:white;padding:1rem;margin-bottom:1rem;box-shadow:0 2px 4px rgba(0,0,0,0.1);}
  .nav button{background:#667eea;color:white;border:none;padding:0.5rem 1rem;margin-right:1rem;border-radius:4px;cursor:pointer;}
  .nav button:hover{background:#5a6fd8;}
  .panel{background:white;margin:1rem;padding:2rem;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);}
  .widget-area{border:2px solid #ddd;border-radius:8px;position:relative;margin-top:1rem;}
  .live-badge{position:absolute;top:10px;right:10px;background:#10b981;color:white;padding:4px 8px;border-radius:12px;font-size:12px;z-index:10;}
  .status-dot{color:#10b981;}
  </style></head><body>
  <div class="header"><h1>🎛️ Mission Control</h1><p>Multi-Agent Management System</p></div>
  <div class="nav">
    <button onclick="show('agents')">🤖 Agents</button>
    <button onclick="show('tokens')">🔥 Token Usage</button>
    <button onclick="show('system')">📊 System</button>
    <button onclick="location.href='/logout'" style="float:right;background:#dc2626;">Logout</button>
  </div>
  <div id="agents" class="panel">
    <h2>🤖 Active Agents</h2>
    <p><span class="status-dot">●</span> <strong>Magi</strong> - Orchestrator (Opus 4.6)</p>
    <p><span class="status-dot">●</span> <strong>Beeb</strong> - Ops/Scout (Gemini Flash)</p>
    <p><span class="status-dot">●</span> <strong>Marvin Jr.</strong> - Builder/Ops (Sonnet 4.6)</p>
    <p><strong>Status:</strong> Multi-agent team operational with shared workspace coordination.</p>
    <p><strong>Skills:</strong> 24 installed (12 new from ClawHub including orchestration tools)</p>
  </div>
  <div id="tokens" class="panel" style="display:none;">
    <h2>🔥 Real-Time Token Usage Widget</h2>
    <p><strong>Your iframe widget integration area:</strong></p>
    <div class="widget-area">
      <iframe src="/demo-widget" width="100%" height="400" frameborder="0"></iframe>
      <div class="live-badge">LIVE</div>
    </div>
    <p><small><strong>To integrate your widget:</strong> Replace iframe src with your widget URL</small></p>
    <code style="background:#f0f0f0;padding:10px;display:block;margin-top:10px;">
      document.querySelector('iframe').src = 'your-widget-url-here';
    </code>
  </div>
  <div id="system" class="panel" style="display:none;">
    <h2>📊 System Status</h2>
    <p><strong>Dashboard:</strong> ✅ Online (Port 3002)</p>
    <p><strong>OpenClaw Gateway:</strong> ✅ Running (Port 18790)</p>
    <p><strong>Multi-Agent Server:</strong> ✅ Operational</p>
    <p><strong>Agents Available:</strong> 3 active</p>
    <p><strong>Skills Installed:</strong> 24 total</p>
    <p><strong>Firewall:</strong> ✅ Ports 3000-3002 open</p>
  </div>
  <script>
  function show(id){
    document.querySelectorAll('.panel').forEach(p=>p.style.display='none');
    document.getElementById(id).style.display='block';
  }
  </script>
  </body></html>`);
});

app.post('/auth', (req, res) => {
  if (req.body.user === 'admin' && req.body.pass === 'magrathea2024!') {
    isAuthenticated = true;
    res.redirect('/');
  } else {
    res.redirect('/login');
  }
});

app.get('/logout', (req, res) => {
  isAuthenticated = false;
  res.redirect('/login');
});

app.get('/demo-widget', (req, res) => {
  res.send(`<html><head><style>
  body{font-family:Arial;margin:10px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:20px;border-radius:8px;min-height:350px;}
  .metrics{display:flex;justify-content:space-around;margin:20px 0;}
  .metric{background:rgba(255,255,255,0.15);padding:15px;border-radius:8px;text-align:center;min-width:100px;}
  .value{font-size:24px;font-weight:bold;margin-bottom:5px;}
  .label{font-size:12px;opacity:0.8;}
  .agent-list{background:rgba(255,255,255,0.1);padding:15px;border-radius:8px;margin-top:20px;}
  .agent{display:flex;justify-content:space-between;padding:5px 0;}
  </style></head><body>
  <h3>🔥 Real-Time Token Usage (Demo)</h3>
  <div class="metrics">
    <div class="metric"><div class="value" id="total">5,247</div><div class="label">Total Today</div></div>
    <div class="metric"><div class="value" id="cost">$2.14</div><div class="label">Cost Today</div></div>
    <div class="metric"><div class="value" id="rate">67</div><div class="label">Rate/min</div></div>
  </div>
  <div class="agent-list">
    <h4>Agent Usage:</h4>
    <div class="agent"><span>🤖 Magi</span><span id="magi">1,247 tokens</span></div>
    <div class="agent"><span>🛸 Beeb</span><span id="beeb">834 tokens</span></div>
    <div class="agent"><span>🤖 Marvin Jr.</span><span id="marvin">592 tokens</span></div>
  </div>
  <p style="margin-top:20px;font-size:12px;text-align:center;opacity:0.7;">
    <strong>Replace this demo with your actual token usage widget</strong>
  </p>
  <script>
  setInterval(() => {
    document.getElementById('total').textContent = (Math.floor(Math.random() * 3000) + 5000).toLocaleString();
    document.getElementById('cost').textContent = '$' + (Math.random() * 5 + 1).toFixed(2);
    document.getElementById('rate').textContent = Math.floor(Math.random() * 50) + 30;
    document.getElementById('magi').textContent = (Math.floor(Math.random() * 500) + 1000).toLocaleString() + ' tokens';
    document.getElementById('beeb').textContent = (Math.floor(Math.random() * 300) + 500).toLocaleString() + ' tokens';
    document.getElementById('marvin').textContent = (Math.floor(Math.random() * 400) + 300).toLocaleString() + ' tokens';
  }, 3000);
  </script>
  </body></html>`);
});

app.listen(3002, '0.0.0.0', () => {
  console.log('🎛️ Mission Control Dashboard running at http://0.0.0.0:3002');
  console.log('Login: admin / magrathea2024!');
});