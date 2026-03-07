const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();

app.use(express.json());
app.use(express.urlencoded({extended: true}));

let isAuthenticated = false;
const kanbanDataPath = '/home/magi/marvin-jr/memory/kanban-board-data.json';

// Mock agent data (enhanced from Marvin's implementation)
const agentsData = {
  agents: [
    {
      id: 'magi',
      name: 'Magi',
      fullName: 'Magi - Primary Orchestrator',
      type: 'orchestrator',
      model: 'anthropic/claude-opus-4-6',
      provider: 'anthropic',
      status: 'online',
      workspace: '~/clawd',
      emoji: '🤖',
      tokensToday: 15247,
      cost: '$3.21',
      lastActivity: '2 mins ago',
      capabilities: ['coordination', 'discord-relay', 'task-routing', 'memory-management']
    },
    {
      id: 'beeb',
      name: 'Beeb',
      fullName: 'Beeb (Beeblebrox) - Social Scout',
      type: 'ops-scout',
      model: 'google/gemini-2.5-flash',
      provider: 'google',
      status: 'online',
      workspace: '~/beeb',
      emoji: '🛸',
      tokensToday: 8934,
      cost: '$0.42',
      lastActivity: '5 mins ago',
      capabilities: ['social-monitoring', 'email-triage', 'deal-alerts', 'reddit-scanning']
    },
    {
      id: 'marvin-jr',
      name: 'Marvin Jr.',
      fullName: 'Marvin Jr. - Infrastructure Builder',
      type: 'builder-ops',
      model: 'anthropic/claude-sonnet-4-6',
      provider: 'anthropic',
      status: 'online',
      workspace: '~/marvin-jr',
      emoji: '🤖',
      tokensToday: 12156,
      cost: '$1.87',
      lastActivity: '1 min ago',
      capabilities: ['homelab-management', 'home-assistant', 'media-stack', 'monitoring']
    }
  ]
};

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

// Get provider logo emoji
function getProviderLogo(provider) {
  const logos = {
    'anthropic': '🔮',
    'google': '🔍',
    'openai': '🔥'
  };
  return logos[provider] || '🤖';
}

// Login page
app.get('/login', (req, res) => {
  res.send(`<html><head><title>🎛️ Mission Control</title><style>
  body{font-family:'Inter',Arial,sans-serif;background:#000;color:#fff;margin:0;padding:0;min-height:100vh;display:flex;align-items:center;justify-content:center;}
  .login{background:#1a1a1a;padding:2rem;border-radius:12px;box-shadow:0 20px 40px rgba(0,0,0,0.5);width:400px;border:1px solid #333;}
  .login h1{color:#fff;text-align:center;margin-bottom:2rem;}
  input{width:100%;padding:0.75rem;margin:0.5rem 0;border:1px solid #333;border-radius:6px;box-sizing:border-box;background:#2a2a2a;color:#fff;}
  button{width:100%;padding:0.75rem;background:#0066ff;color:white;border:none;border-radius:6px;cursor:pointer;margin-top:1rem;font-weight:500;}
  button:hover{background:#0052cc;}
  </style></head><body>
  <div class="login"><h1>🎛️ Mission Control</h1>
  <form method="post" action="/auth"><input type="text" name="user" placeholder="Username" required>
  <input type="password" name="pass" placeholder="Password" required>
  <button type="submit">Access Dashboard</button></form></div></body></html>`);
});

// Main dashboard with mega dark mode
app.get('/', (req, res) => {
  if (!isAuthenticated) return res.redirect('/login');
  res.send(`<html><head><title>🎛️ Mission Control Dashboard</title><style>
  * { box-sizing: border-box; }
  body { font-family:'Inter',Arial,sans-serif; margin:0; background:#0a0a0a; color:#fff; min-height:100vh; }
  
  /* Header */
  .header { background:linear-gradient(135deg,#1a1a1a,#2a2a2a); color:#fff; padding:1.5rem; text-align:center; border-bottom:1px solid #333; }
  .header h1 { margin:0; font-size:2rem; font-weight:700; }
  .header p { margin:0.5rem 0 0; opacity:0.8; }
  
  /* Navigation */
  .nav { background:#1a1a1a; padding:1rem; border-bottom:1px solid #333; }
  .nav button { background:#2a2a2a; color:#fff; border:1px solid #444; padding:0.75rem 1.5rem; margin-right:1rem; border-radius:6px; cursor:pointer; font-size:14px; transition:all 0.2s; }
  .nav button:hover { background:#3a3a3a; border-color:#555; }
  .nav button.active { background:#0066ff; border-color:#0066ff; }
  .nav .logout { float:right; background:#dc2626; border-color:#dc2626; }
  .nav .logout:hover { background:#b91c1c; }
  
  /* Panels */
  .panel { background:#1a1a1a; margin:1.5rem; padding:2rem; border-radius:12px; border:1px solid #333; }
  .panel h2 { margin-top:0; color:#fff; font-weight:600; }
  
  /* Agent Cards */
  .agent-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:1.5rem; margin-top:1.5rem; }
  .agent-card { background:#2a2a2a; border:1px solid #444; border-radius:8px; padding:1.5rem; transition:transform 0.2s; }
  .agent-card:hover { transform:translateY(-2px); border-color:#555; }
  .agent-header { display:flex; align-items:center; gap:1rem; margin-bottom:1rem; }
  .agent-emoji { font-size:2rem; }
  .agent-info h3 { margin:0; font-weight:600; }
  .agent-info p { margin:0; opacity:0.7; font-size:0.9rem; }
  .agent-metrics { display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin:1rem 0; }
  .metric { text-align:center; }
  .metric-value { font-size:1.5rem; font-weight:bold; color:#0066ff; }
  .metric-label { font-size:0.8rem; opacity:0.7; }
  .agent-capabilities { margin-top:1rem; }
  .capability-tag { display:inline-block; background:#333; color:#fff; padding:0.2rem 0.5rem; border-radius:4px; font-size:0.7rem; margin:0.2rem 0.2rem 0 0; }
  .status-online { color:#10b981; }
  .status-offline { color:#ef4444; }
  
  /* Token Widget */
  .widget-area { border:1px solid #333; border-radius:8px; position:relative; margin-top:1rem; background:#2a2a2a; }
  .live-badge { position:absolute; top:10px; right:10px; background:#10b981; color:#fff; padding:4px 8px; border-radius:12px; font-size:12px; z-index:10; }
  
  /* Kanban Board */
  .kanban-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem; }
  .kanban-container { display:flex; gap:1.5rem; overflow-x:auto; padding:1rem 0; }
  .kanban-column { min-width:300px; background:#2a2a2a; border:1px solid #444; border-radius:8px; padding:1rem; }
  .column-header { font-weight:600; margin-bottom:1rem; padding:0.75rem; border-radius:6px; color:#fff; text-align:center; }
  .kanban-card { background:#1a1a1a; margin-bottom:1rem; padding:1rem; border-radius:6px; border-left:4px solid #666; border:1px solid #333; transition:all 0.2s; }
  .kanban-card:hover { border-color:#555; transform:translateY(-1px); }
  .card-title { font-weight:600; margin-bottom:0.5rem; color:#fff; }
  .card-desc { font-size:13px; color:#ccc; margin-bottom:0.75rem; max-height:60px; overflow:hidden; line-height:1.4; }
  .card-meta { font-size:11px; color:#999; display:flex; justify-content:space-between; align-items:center; }
  .priority-high { border-left-color:#ef4444; }
  .priority-medium { border-left-color:#f59e0b; }
  .priority-low { border-left-color:#10b981; }
  
  /* Kanban Controls */
  .kanban-controls { display:flex; gap:1rem; }
  .btn-primary { background:#0066ff; color:#fff; border:none; padding:0.5rem 1rem; border-radius:6px; cursor:pointer; font-weight:500; }
  .btn-secondary { background:#2a2a2a; color:#fff; border:1px solid #444; padding:0.5rem 1rem; border-radius:6px; cursor:pointer; }
  .btn-primary:hover { background:#0052cc; }
  .btn-secondary:hover { background:#3a3a3a; }
  
  /* Footer */
  .kanban-footer { position:fixed; bottom:0; left:0; right:0; background:#1a1a1a; border-top:1px solid #333; padding:1rem; display:flex; justify-content:center; gap:1rem; }
  .footer-btn { background:#2a2a2a; color:#fff; border:1px solid #444; padding:0.75rem 1.5rem; border-radius:6px; cursor:pointer; }
  .footer-btn:hover { background:#3a3a3a; }
  
  /* Provider Logos */
  .provider-logo { font-size:1.2rem; margin-right:0.5rem; }
  
  /* Tree View for Agent Types */
  .agent-tree { margin-top:1rem; }
  .agent-type { margin-bottom:1rem; }
  .agent-type-header { background:#333; color:#fff; padding:0.5rem 1rem; border-radius:4px; cursor:pointer; }
  .agent-type-content { margin-left:1rem; margin-top:0.5rem; }
  .agent-type-content.collapsed { display:none; }
  
  /* Scrollbar Styling */
  ::-webkit-scrollbar { width:8px; height:8px; }
  ::-webkit-scrollbar-track { background:#2a2a2a; }
  ::-webkit-scrollbar-thumb { background:#555; border-radius:4px; }
  ::-webkit-scrollbar-thumb:hover { background:#666; }
  
  /* Hidden panels */
  .panel-hidden { display:none; }
  </style></head><body>
  
  <div class="header">
    <h1>🎛️ Mission Control</h1>
    <p>Multi-Agent Command & Control Center</p>
  </div>
  
  <div class="nav">
    <button onclick="showPanel('agents')" class="active" id="btn-agents">🤖 Agent Fleet</button>
    <button onclick="showPanel('tokens')" id="btn-tokens">🔥 Token Analytics</button>
    <button onclick="showPanel('kanban')" id="btn-kanban">📋 Mission Board</button>
    <button onclick="window.location='/logout'" class="logout">🚪 Logout</button>
  </div>
  
  <!-- Enhanced Agents Panel -->
  <div id="agents" class="panel">
    <h2>🤖 Agent Fleet Status</h2>
    <div id="agent-fleet">Loading agent data...</div>
  </div>
  
  <!-- Token Usage Panel -->
  <div id="tokens" class="panel panel-hidden">
    <h2>🔥 Real-Time Token Analytics</h2>
    <div class="widget-area">
      <iframe id="token-iframe" src="http://192.168.1.132:3847" width="100%" height="500" frameborder="0" style="border-radius:8px;"></iframe>
      <div class="live-badge">LIVE</div>
    </div>
    <p style="opacity:0.7;margin-top:1rem;"><strong>Real-time token usage monitoring</strong> across all agents</p>
    <button onclick="refreshTokenWidget()" class="btn-secondary">🔄 Refresh Widget</button>
  </div>
  
  <!-- Enhanced Kanban Panel -->
  <div id="kanban" class="panel panel-hidden">
    <div class="kanban-header">
      <h2>📋 Mission Board</h2>
      <div class="kanban-controls">
        <button onclick="createNewCard()" class="btn-primary">➕ New Card</button>
        <button onclick="refreshKanban()" class="btn-secondary">🔄 Refresh</button>
      </div>
    </div>
    <div id="kanban-board">Loading mission data...</div>
  </div>
  
  <!-- Footer (appears only on Kanban) -->
  <div id="kanban-footer" class="kanban-footer" style="display:none;">
    <button class="footer-btn" onclick="showArchived()">📁 Archived</button>
    <button class="footer-btn" onclick="showAgentSidebar()">🤖 Agents</button>
  </div>
  
  <script>
    // Panel Management
    function showPanel(id) {
      document.querySelectorAll('.panel').forEach(p => p.classList.add('panel-hidden'));
      document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
      document.getElementById(id).classList.remove('panel-hidden');
      document.getElementById('btn-' + id).classList.add('active');
      
      // Show/hide footer
      const footer = document.getElementById('kanban-footer');
      footer.style.display = (id === 'kanban') ? 'flex' : 'none';
      
      if (id === 'agents') loadAgents();
      if (id === 'kanban') loadKanban();
    }
    
    // Load enhanced agent data
    function loadAgents() {
      fetch('/api/agents').then(r => r.json()).then(data => {
        renderAgents(data);
      });
    }
    
    function renderAgents(data) {
      const container = document.getElementById('agent-fleet');
      let html = '<div class="agent-grid">';
      
      data.agents.forEach(agent => {
        const providerLogo = getProviderLogo(agent.provider);
        html += \`
          <div class="agent-card">
            <div class="agent-header">
              <div class="agent-emoji">\${agent.emoji}</div>
              <div class="agent-info">
                <h3>\${agent.name} <span class="provider-logo">\${providerLogo}</span></h3>
                <p>\${agent.fullName}</p>
                <p class="status-\${agent.status}">● \${agent.status.toUpperCase()} • \${agent.lastActivity}</p>
              </div>
            </div>
            <div class="agent-metrics">
              <div class="metric">
                <div class="metric-value">\${agent.tokensToday.toLocaleString()}</div>
                <div class="metric-label">Tokens Today</div>
              </div>
              <div class="metric">
                <div class="metric-value">\${agent.cost}</div>
                <div class="metric-label">Cost Today</div>
              </div>
            </div>
            <div class="agent-capabilities">
              \${agent.capabilities.map(cap => \`<span class="capability-tag">\${cap}</span>\`).join('')}
            </div>
            <div style="margin-top:1rem;font-size:0.8rem;opacity:0.7;">
              <strong>Model:</strong> \${agent.model}<br>
              <strong>Workspace:</strong> \${agent.workspace}
            </div>
          </div>
        \`;
      });
      
      html += '</div>';
      container.innerHTML = html;
    }
    
    function getProviderLogo(provider) {
      const logos = { 'anthropic': '🔮', 'google': '🔍', 'openai': '🔥' };
      return logos[provider] || '🤖';
    }
    
    // Kanban functions
    function loadKanban() {
      fetch('/api/kanban').then(r => r.json()).then(data => {
        renderKanban(data);
      });
    }
    
    function renderKanban(data) {
      const container = document.getElementById('kanban-board');
      let html = '<div class="kanban-container">';
      
      data.columns.forEach(column => {
        const columnCards = data.cards.filter(card => card.column === column.id);
        html += \`
          <div class="kanban-column">
            <div class="column-header" style="background:\${column.color}">\${column.title}</div>
        \`;
        
        columnCards.forEach(card => {
          const shortDesc = card.description ? card.description.substring(0, 120) + (card.description.length > 120 ? '...' : '') : '';
          const cardDate = new Date(card.created).toLocaleDateString();
          const commentCount = card.comments ? card.comments.length : 0;
          
          html += \`
            <div class="kanban-card priority-\${card.priority || 'medium'}" onclick="viewCard('\${card.id}')">
              <div class="card-title">\${card.title}</div>
              <div class="card-desc">\${shortDesc}</div>
              <div class="card-meta">
                <span>\${cardDate}</span>
                <span>\${commentCount}💬 \${card.priority || 'medium'}</span>
              </div>
            </div>
          \`;
        });
        
        html += '</div>';
      });
      
      html += '</div>';
      container.innerHTML = html;
    }
    
    // Kanban actions
    function createNewCard() {
      const title = prompt('Card title:');
      if (title) {
        const description = prompt('Description (optional):');
        alert('New card feature coming soon: "' + title + '"');
      }
    }
    
    function refreshKanban() {
      document.getElementById('kanban-board').innerHTML = 'Refreshing mission data...';
      loadKanban();
    }
    
    function viewCard(cardId) {
      alert('Viewing card: ' + cardId + '\\n\\nFull card details coming soon.');
    }
    
    function showArchived() {
      alert('📁 Archived cards view coming soon');
    }
    
    function showAgentSidebar() {
      alert('🤖 Agent sidebar view coming soon');
    }
    
    function refreshTokenWidget() {
      const iframe = document.getElementById('token-iframe');
      iframe.src = iframe.src;
    }
    
    // Initialize
    window.onload = function() {
      loadAgents();
    };
  </script>
  </body></html>`);
});

// API endpoints
app.get('/api/agents', (req, res) => {
  res.json(agentsData);
});

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

app.listen(3002, '0.0.0.0', () => {
  console.log('🌙 Mega Dark Mission Control Dashboard: http://192.168.1.132:3002');
  console.log('✅ Features: Enhanced Agents, Token Widget, Dark Kanban Board');
  console.log('🔑 Login: admin / magrathea2024!');
});
