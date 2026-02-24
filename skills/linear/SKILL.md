# Linear Skill

Track infrastructure alerts and issues via Linear.

## Auth
- API key in `~/.env` as `LINEAR_API_KEY`
- Authenticates as `magi-homelab@agentmail.to`

## Usage
```bash
node skills/linear/scripts/linear.js list
node skills/linear/scripts/linear.js create --title "Alert: X" --priority 2 --team LAB
node skills/linear/scripts/linear.js ack LAB-3
node skills/linear/scripts/linear.js close LAB-3
node skills/linear/scripts/linear.js comment LAB-3 "Fixed by restarting service"
```

## Priority Levels
1 = Urgent | 2 = High | 3 = Medium | 4 = Low

## Teams
- **LAB** - homelab
- **ERI** - Erichomelab

## When to Use
- Infrastructure alerts worth tracking
- Issues needing acknowledgment/resolution workflow
- Anything to ping Eric about that should be logged
