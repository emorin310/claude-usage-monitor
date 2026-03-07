const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();

app.use(express.json());
app.use(express.urlencoded({extended: true}));

let isAuthenticated = false;
const kanbanDataPath = '/home/magi/marvin-jr/memory/kanban-board-data.json';

// Helper to read Kanban data
function getKanbanData() {
  try {
    if (fs.existsSync(kanbanDataPath)) {
      return JSON.parse(fs.readFileSync(kanbanDataPath, 'utf8'));
    }
  } catch (error) {
    console.log('Error reading Kanban data:', error);
  }
  return { columns: [], cards: [] };
}

// Login page
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
  <button type="submit">Login</button></form></div></body></html>`);
});

// Main dashboard with 3 tabs: Agents, Tokens, Kanban
app.get('/', (req, res) => {
  if (!isAuthenticated) return res.redirect('/login');
  res.send(`<html><head><title>🎛️ Mission Control Dashboard</title><style>
  body{font-family:Arial,sans-serif;margin:0;background:#f5f5f5;}
  .header{background:#667eea;color:white;padding:1rem;text-align:center;}
  .nav{background:white;padding:1rem;margin-bottom:1rem;box-shadow:0 2px 4px rgba(0,0,0,0.1);}
  .nav button{background:#667eea;color:white;border:none;padding:0.75rem 1.5rem;margin-right:1rem;border-radius:4px;cursor:pointer;font-size:14px;}
  .nav button:hover{background:#5a6fd8;}
  .nav button.active{background:#4f46e5;}
  .panel{background:white;margin:1rem;padding:2rem;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);}
  .widget-area{border:2px solid #ddd;border-radius:8px;position:relative;margin-top:1rem;}
  .live-badge{position:absolute;top:10px;right:10px;background:#10b981;color:white;padding:4px 8px;border-radius:12px;font-size:12px;}
  .kanban-container{display:flex;gap:1rem;overflow-x:auto;padding:1rem 0;}
  .kanban-column{min-width:280px;background:#f8f9fa;border-radius:8px;padding:1rem;}
  .column-header{font-weight:bold;margin-bottom:1rem;padding:0.5rem;border-radius:4px;color:white;text-align:center;}
  .kanban-card{background:white;margin-bottom:0.75rem;padding:1rem;border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,0.1);border-left:4px solid #ddd;}
  .card-title{font-weight:bold;margin-bottom:0.5rem;}
  .card-desc{font-size:13px;color:#666;margin-bottom:0.5rem;max-height:60px;overflow:hidden;}
  .card-meta{font-size:11px;color:#999;display:flex;justify-content:space-between;}
  .priority-high{border-left-color:#ef4444;}
  .priority-medium{border-left-color:#f59e0b;}
  .priority-low{border-left-color:#10b981;}
  </style></head><body>
  <div class="header"><h1>🎛️ Mission Control</h1><p>Multi-Agent Management System</p></div>
  <div class="nav">
    <button onclick="showPanel('agents')" class="active" id="btn-agents">🤖 Agents</button>
    <button onclick="showPanel('tokens')" id="btn-tokens">🔥 Token Usage</button>
    <button onclick="showPanel('kanban')" id="btn-kanban">📋 Kanban Board</button>
    <button onclick="window.location='/logout'" style="float:right;background:#dc2626;">Logout</button>
  </div>
  <div id="agents" class="panel">
    <h2>🤖 Active Agents</h2>
    <p><span style="color:#10b981;">●</span> <b>Magi</b> - Orchestrator (Opus 4.6)</p>
    <p><span style="color:#10b981;">●</span> <b>Beeb</b> - Ops/Scout (Gemini Flash)</p>
    <p><span style="color:#10b981;">●</span> <b>Marvin Jr.</b> - Builder (Sonnet 4.6)</p>
    <p><b>Multi-Agent Coordination:</b> ✅ Operational</p>
    <p><b>Skills Installed:</b> 24 total (including 12 new from ClawHub)</p>
  </div>
  <div id="tokens" class="panel" style="display:none;">
    <h2>🔥 Real-Time Token Usage Widget</h2>
    <div class="widget-area">
      <iframe id="token-iframe" src="http://192.168.1.132:3333/" width="100%" height="400" frameborder="0"></iframe>
      <div class="live-badge">LIVE</div>
    </div>
    <p><small><b>Replace iframe src with your token widget URL</b></small></p>
    <button onclick="setTokenWidget()" style="background:#10b981;color:white;border:none;padding:0.5rem 1rem;border-radius:4px;margin-top:1rem;">🔧 Set Widget URL</button>
  </div>
  <div id="kanban" class="panel" style="display:none;">
    <h2>📋 Kanban Board - Marvin's Tasks</h2>
    <div id="kanban-board">Loading Kanban data...</div>
    <button onclick="refreshKanban()" style="background:#667eea;color:white;border:none;padding:0.5rem 1rem;border-radius:4px;margin-top:1rem;">🔄 Refresh</button>
  </div>
  <script>
    function showPanel(id) {
      document.querySelectorAll('.panel').forEach(p => p.style.display = 'none');
      document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
      document.getElementById(id).style.display = 'block';
      document.getElementById('btn-' + id).classList.add('active');
      if (id === 'kanban') loadKanban();
    }
    
    function setTokenWidget() {
      const url = prompt('Enter your token widget URL:');
      if (url) {
        document.getElementById('token-iframe').src = url;
        localStorage.setItem('tokenWidgetUrl', url);
      }
    }
    
    function loadKanban() {
      fetch('/api/kanban').then(r => r.json()).then(data => {
        renderKanban(data);
      }).catch(e => {
        document.getElementById('kanban-board').innerHTML = '<p style="color:red;">Error loading Kanban data: ' + e.message + '</p>';
      });
    }
    
    function renderKanban(data) {
      const container = document.getElementById('kanban-board');
      let html = '<div class="kanban-container">';
      
      data.columns.forEach(column => {
        const columnCards = data.cards.filter(card => card.column === column.id);
        html += \`<div class="kanban-column">
          <div class="column-header" style="background:\${column.color}">\${column.title}</div>\`;
        
        columnCards.forEach(card => {
          const shortDesc = card.description ? card.description.substring(0, 100) + (card.description.length > 100 ? '...' : '') : '';
          const cardDate = new Date(card.created).toLocaleDateString();
          const commentCount = card.comments ? card.comments.length : 0;
          
          html += \`<div class="kanban-card priority-\${card.priority || 'medium'}">
            <div class="card-title">\${card.title}</div>
            <div class="card-desc">\${shortDesc}</div>
            <div class="card-meta">
              <span>\${cardDate}</span>
              <span>\${commentCount}💬 \${card.priority || 'medium'}</span>
            </div>
          </div>\`;
        });
        
        html += '</div>';
      });
      
      html += '</div>';
      container.innerHTML = html;
    }
    
    function refreshKanban() {
      document.getElementById('kanban-board').innerHTML = 'Refreshing...';
      loadKanban();
    }
    
    // Load saved token widget URL
    window.onload = function() {
      const savedUrl = localStorage.getItem('tokenWidgetUrl');
      if (savedUrl) {
        document.getElementById('token-iframe').src = savedUrl;
      }
    };
  </script>
  </body></html>`);
});

// API endpoint for Kanban data
app.get('/api/kanban', (req, res) => {
  const kanbanData = getKanbanData();
  res.json(kanbanData);
});

// Authentication
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

// Demo token widget
app.get('/demo-widget', (req, res) => {
  res.send(`<html><head><style>body{font-family:Arial;margin:10px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:20px;border-radius:8px;}.metric{display:inline-block;background:rgba(255,255,255,0.15);margin:10px;padding:15px;border-radius:8px;text-align:center;}.value{font-size:24px;font-weight:bold;}</style></head><body><h3>🔥 Token Usage Dashboard</h3><div class="metric"><div class="value" id="total">5,247</div><div>Tokens Today</div></div><div class="metric"><div class="value" id="cost">$2.14</div><div>Cost Today</div></div><div class="metric"><div class="value" id="agents">3</div><div>Active Agents</div></div><p><small><b>PLACEHOLDER:</b> Replace with your real token widget</small></p><script>setInterval(()=>{document.getElementById('total').textContent=(Math.floor(Math.random()*10000)+5000).toLocaleString();document.getElementById('cost').textContent='$'+(Math.random()*10).toFixed(2);},5000);</script></body></html>`);
});

app.listen(3002, '0.0.0.0', () => {
  console.log('🎛️ Enhanced Mission Control Dashboard: http://192.168.1.132:3002');
  console.log('✅ Features: Agent Status, Token Widget Area, Kanban Board');
  console.log('🔑 Login: admin / magrathea2024!');
});
