# Trill Bootstrap Package

**Version:** 1.0  
**Created:** 2026-02-09  
**For:** Trill (Eric's backup AI assistant)

## Contents

```
trill-bootstrap/
├── BOOTSTRAP.md              # Trill's first-run instructions (she deletes after reading)
├── UNPACK_INSTRUCTIONS.md    # For Marvin: deployment steps
├── README.md                 # This file
├── SOUL.md                   # Personality and values
├── USER.md                   # About Eric
├── AGENTS.md                 # Operating manual
├── TOOLS.md                  # Infrastructure notes
├── MEMORY.md                 # Shared long-term memory
├── HEARTBEAT.md              # Monitoring duties
├── COUNCIL.md                # Multi-agent coordination protocol
├── kba/                      # Knowledge base (user interests, family)
│   ├── user-interests.md
│   └── user-family.md
└── memory/                   # Daily logs and state files
    ├── 2026-02-*.md
    ├── council-state.json
    └── archive/
```

## Deployment Workflow

1. **Marvin** provisions VM and installs OpenClaw base
2. **Marvin** follows `UNPACK_INSTRUCTIONS.md`
3. **Trill** comes online, reads `BOOTSTRAP.md`
4. **Trill** posts intro to Council, notifies Eric
5. **Magi** guides Trill through MQTT setup
6. **Trill** deletes `BOOTSTRAP.md` and begins normal ops

## Key Details

- **Name:** Trill
- **Role:** Backup & new projects
- **Emoji:** 🎵
- **Todoist:** Project `🤖 Trill`, label `@trill` (teal)
- **Gateway Port:** 18791 (avoid Marvin's 18789)
- **Credits:** Shared Anthropic pool with Magi & Marvin

## Contact

Questions? Reach Magi via:
- Telegram (Eric's chat)
- Council Handoffs thread (Todoist)
- MQTT (once Trill is connected)

---

**Ready to deploy!** 🚀
