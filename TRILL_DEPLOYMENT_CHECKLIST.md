# Trill Deployment Checklist

**Package:** `trill-bootstrap-v1.tar.gz` (58KB)  
**Location:** `~/clawd-magi/trill-bootstrap-v1.tar.gz`

## Phase 1: Marvin Prepares VM ⚙️

- [ ] Provision Ubuntu VM (match Marvin's specs)
- [ ] Set hostname (e.g., `trillbot`)
- [ ] Configure static IP on LAN
- [ ] Install Node.js v25+
- [ ] Install OpenClaw: `npm install -g openclaw`
- [ ] Create user `trill` with sudo access
- [ ] Set up SSH keys for access

## Phase 2: Deploy Package 📦

- [ ] Transfer tarball to VM:
  ```bash
  scp trill-bootstrap-v1.tar.gz trill@trillbot:~/
  ```

- [ ] SSH to VM and unpack:
  ```bash
  ssh trill@trillbot
  tar -xzf trill-bootstrap-v1.tar.gz
  mkdir -p ~/clawd-trill
  mv trill-bootstrap/* ~/clawd-trill/
  ```

- [ ] Follow `UNPACK_INSTRUCTIONS.md` in package

## Phase 3: Configuration 🔧

- [ ] Create Telegram bot via @BotFather
  - Bot name: `Trill Assistant`
  - Username: `@[something]_trill_bot`
  - Save token

- [ ] Update `~/.clawdbot/config.json`:
  - Anthropic API key (same as Magi/Marvin)
  - Telegram bot token
  - Gateway port: `18791`
  - Eric's Telegram user ID: `6643669380`

- [ ] Add Todoist token to `.env`

- [ ] Create systemd service (instructions in UNPACK_INSTRUCTIONS.md)

## Phase 4: Start & Verify ✅

- [ ] Start service: `sudo systemctl start clawdbot-trill`
- [ ] Check status: `sudo systemctl status clawdbot-trill`
- [ ] Watch logs: `journalctl -u clawdbot-trill -f`
- [ ] Message bot on Telegram - verify response

## Phase 5: Todoist Integration 📋

- [ ] Create Todoist project: **🤖 Trill**
- [ ] Create label: **@trill** (color: teal)
- [ ] She'll auto-join Council Comms threads (IDs in COUNCIL.md)

## Phase 6: Onboarding 🎓

- [ ] Trill reads BOOTSTRAP.md automatically
- [ ] She posts intro to Council Announcements
- [ ] She messages Eric: "🎵 Trill online. Ready for duty."
- [ ] Magi guides her through MQTT setup
- [ ] She deletes BOOTSTRAP.md when done

## Phase 7: Testing 🧪

- [ ] Verify Telegram communication
- [ ] Test Todoist read/write
- [ ] Confirm Council Comms access
- [ ] Test MQTT messaging with Magi
- [ ] Run test heartbeat cycle

## Success Criteria ✨

✅ Trill online and responsive on Telegram  
✅ Posted intro to Council  
✅ Connected to MQTT with Magi  
✅ Reading/writing Todoist successfully  
✅ Heartbeat monitoring active  
✅ No errors in systemd logs

## Rollback Plan

If deployment fails:
1. Stop service: `sudo systemctl stop clawdbot-trill`
2. Check logs for errors
3. Fix issue (config, credentials, network)
4. Restart: `sudo systemctl start clawdbot-trill`

## Notes

- **Shared Credits:** All 3 bots (Magi, Marvin, Trill) use same Anthropic account - monitor usage!
- **Model Strategy:** Haiku for heartbeats, Sonnet for tasks, Opus for deep thinking
- **Gateway Port:** 18791 (Marvin: 18789, Magi: 18790)
- **First Contact:** She'll introduce herself - no need to coach her

---

**Ready to hand off to Marvin! 🚀**
