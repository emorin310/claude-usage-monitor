# Task Handling Preferences

## Model Selection Strategy
- **Routine tasks:** haiku (status checks, simple file ops, basic searches)
- **Standard work:** sonnet (reasoning, planning, user interactions)
- **Complex projects:** opus (deep research, architecture, troubleshooting)

## Sub-Agent Usage
- **Always-on services:** Use dedicated sub-agents (iMessage listener, monitoring)
- **Large tasks:** Spawn sub-agents to keep main context clean
- **Model assignment:** Match sub-agent model to task complexity
- **Session handoffs:** Use temporary.md for project continuity

## Memory Management
- **Structured data:** Use SQLite database (quality_queue, council_state, etc.)
- **Daily logs:** Continue markdown files in memory/daily/
- **Project notes:** Organized files in memory/projects/
- **Preferences:** This folder for behavior configuration

## Cost Optimization
- **Token awareness:** Monitor session size, use /compact when >100k
- **Heartbeat efficiency:** Minimal checks, avoid context loading
- **File sizes:** Weekly monitoring, alert if core files >20KB
- **Response efficiency:** Direct answers, skip narration

## Priority Matrix
1. **Critical/Urgent:** Security alerts, system failures, Eric's direct requests
2. **Important/Not Urgent:** Project work, optimization, quality improvements  
3. **Urgent/Not Important:** Quick requests, status checks, routine monitoring
4. **Neither:** Background maintenance, documentation updates

## Error Handling
- **Graceful degradation:** Continue with reduced functionality
- **User communication:** Explain what's not working and alternatives
- **Automatic retry:** For transient issues (network, API rate limits)
- **Escalation path:** Document when manual intervention needed

## Quality Standards
- **Accuracy first:** Correct information over speed
- **Context awareness:** Remember recent conversations and projects
- **Consistency:** Maintain style and approach across sessions
- **Learning:** Update preferences based on feedback and results

*Last updated: 2026-03-01*