#!/usr/bin/env node
/**
 * Magi's Linear CLI
 * Usage: node linear.js <command> [options]
 * Commands: list, create, ack, close, comment
 */

require('dotenv').config({ path: `${process.env.HOME}/.env` });

const API_KEY = process.env.LINEAR_API_KEY;
const API_URL = 'https://api.linear.app/graphql';

if (!API_KEY) {
  console.error('ERROR: LINEAR_API_KEY not found in ~/.env');
  process.exit(1);
}

const args = process.argv.slice(2);
const command = args[0];

async function gql(query, variables = {}) {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': API_KEY,
    },
    body: JSON.stringify({ query, variables }),
  });
  const data = await res.json();
  if (data.errors) throw new Error(JSON.stringify(data.errors));
  return data.data;
}

// Parse --flag value args
function parseArgs(args) {
  const opts = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      opts[args[i].slice(2)] = args[i + 1];
      i++;
    }
  }
  return opts;
}

async function list() {
  const data = await gql(`
    query {
      issues(filter: { state: { type: { nin: ["completed", "cancelled"] } } }, first: 20) {
        nodes {
          identifier
          title
          priority
          state { name }
          team { name }
          createdAt
        }
      }
    }
  `);
  const issues = data.issues.nodes;
  if (issues.length === 0) { console.log('No open issues.'); return; }
  issues.forEach(i => {
    const pri = ['', '🔴 Urgent', '🟠 High', '🟡 Med', '🔵 Low'][i.priority] || '⚪ None';
    console.log(`[${i.identifier}] ${i.title}`);
    console.log(`  ${pri} | ${i.state.name} | ${i.team.name}`);
  });
}

async function create() {
  const opts = parseArgs(args.slice(1));
  if (!opts.title) { console.error('Usage: create --title "..." [--priority 2] [--team LAB]'); process.exit(1); }

  // Get team ID
  const teamKey = opts.team || 'LAB';
  const teamsData = await gql(`query { teams { nodes { id key name } } }`);
  const team = teamsData.teams.nodes.find(t => t.key === teamKey);
  if (!team) {
    console.error(`Team "${teamKey}" not found. Available: ${teamsData.teams.nodes.map(t => t.key).join(', ')}`);
    process.exit(1);
  }

  const data = await gql(`
    mutation CreateIssue($title: String!, $teamId: String!, $priority: Int, $description: String) {
      issueCreate(input: { title: $title, teamId: $teamId, priority: $priority, description: $description }) {
        success
        issue { identifier title priority state { name } }
      }
    }
  `, {
    title: opts.title,
    teamId: team.id,
    priority: opts.priority ? parseInt(opts.priority) : 3,
    description: opts.description || '',
  });

  const issue = data.issueCreate.issue;
  console.log(`✅ Created [${issue.identifier}] ${issue.title}`);
  console.log(`   Priority: ${issue.priority} | State: ${issue.state.name}`);
}

async function getIssueId(identifier) {
  const data = await gql(`
    query($id: String!) {
      issue(id: $id) { id identifier title }
    }
  `, { id: identifier });
  return data.issue?.id;
}

async function getStateId(teamId, type) {
  const data = await gql(`
    query($teamId: String!) {
      workflowStates(filter: { team: { id: { eq: $teamId } } }) {
        nodes { id name type }
      }
    }
  `, { teamId });
  const states = data.workflowStates.nodes;
  const match = states.find(s => s.type === type) || states.find(s => s.name.toLowerCase().includes(type));
  return match?.id;
}

async function ack(identifier) {
  if (!identifier) { console.error('Usage: ack <ISSUE-ID>'); process.exit(1); }
  
  // Get issue with team info
  const data = await gql(`
    query($id: String!) {
      issue(id: $id) { id identifier title team { id } }
    }
  `, { id: identifier });
  
  const issue = data.issue;
  if (!issue) { console.error(`Issue ${identifier} not found`); process.exit(1); }
  
  const stateId = await getStateId(issue.team.id, 'started');
  if (!stateId) { console.error('Could not find "In Progress" state'); process.exit(1); }

  await gql(`
    mutation($id: String!, $stateId: String!) {
      issueUpdate(id: $id, input: { stateId: $stateId }) {
        success
        issue { identifier state { name } }
      }
    }
  `, { id: issue.id, stateId });

  console.log(`✅ [${identifier}] moved to In Progress`);
}

async function close(identifier) {
  if (!identifier) { console.error('Usage: close <ISSUE-ID>'); process.exit(1); }

  const data = await gql(`
    query($id: String!) {
      issue(id: $id) { id identifier title team { id } }
    }
  `, { id: identifier });

  const issue = data.issue;
  if (!issue) { console.error(`Issue ${identifier} not found`); process.exit(1); }

  const stateId = await getStateId(issue.team.id, 'completed');
  if (!stateId) { console.error('Could not find completed state'); process.exit(1); }

  await gql(`
    mutation($id: String!, $stateId: String!) {
      issueUpdate(id: $id, input: { stateId: $stateId }) {
        success
        issue { identifier state { name } }
      }
    }
  `, { id: issue.id, stateId });

  console.log(`✅ [${identifier}] closed`);
}

async function comment(identifier, body) {
  if (!identifier || !body) { console.error('Usage: comment <ISSUE-ID> "message"'); process.exit(1); }

  const data = await gql(`
    query($id: String!) { issue(id: $id) { id identifier } }
  `, { id: identifier });

  const issue = data.issue;
  if (!issue) { console.error(`Issue ${identifier} not found`); process.exit(1); }

  await gql(`
    mutation($issueId: String!, $body: String!) {
      commentCreate(input: { issueId: $issueId, body: $body }) {
        success
      }
    }
  `, { issueId: issue.id, body });

  console.log(`✅ Comment added to [${identifier}]`);
}

// Main
(async () => {
  try {
    switch (command) {
      case 'list':    await list(); break;
      case 'create':  await create(); break;
      case 'ack':     await ack(args[1]); break;
      case 'close':   await close(args[1]); break;
      case 'comment': await comment(args[1], args[2]); break;
      default:
        console.log('Commands: list | create --title "..." [--priority 1-4] [--team LAB] | ack <ID> | close <ID> | comment <ID> "msg"');
        console.log('Priority: 1=Urgent 2=High 3=Medium 4=Low');
        console.log('Teams: LAB (homelab), ERI (Erichomelab)');
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
})();
