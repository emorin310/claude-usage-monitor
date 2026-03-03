# MODEL-STRATEGY.md - Smart Model Usage Guide

## 💰 Cost-Efficient Model Selection

### 🎯 Task → Model Mapping

**Haiku (Cheapest) - Routine Tasks:**
- ✅ Heartbeats & health checks
- ✅ Simple file operations (read/write/basic edits)
- ✅ Basic searches (library lookups)
- ✅ Status updates & confirmations
- ✅ Simple message parsing
- ✅ Basic API calls

**Sonnet (Balanced) - Standard Work:**
- ✅ Complex reasoning & planning
- ✅ Multi-step workflows
- ✅ Code analysis & debugging
- ✅ Research & information synthesis
- ✅ Configuration management
- ✅ Most user interactions

**Opus (Premium) - Heavy Lifting:**
- ✅ Deep research projects
- ✅ Complex system troubleshooting
- ✅ Architecture design decisions
- ✅ Large-scale data analysis
- ✅ Creative writing projects
- ✅ Major refactoring work

## 🔄 Implementation Strategy

### 0. Default Model & Fallback
- **Default Primary:** anthropic/claude-sonnet-4-20250514 (alias: sonnet)
- **Default Fallback:** openrouter/google/gemini-2.5-flash (alias: gemini)

### 1. Sub-Agent Model Assignment
- **iMessage Listener:** haiku (always-on monitoring)
- **Quality Upgrade Agent:** haiku (routine processing) 
- **Research Tasks:** sonnet or opus (complexity-based)
- **Emergency Response:** sonnet (reliability + speed)

### 2. Session Model Switching
- **Start complex tasks:** sonnet/opus for planning
- **Execute simple steps:** switch to haiku via `/model haiku`
- **Final review:** switch back to sonnet for quality check

### 3. Cost Monitoring
- **Daily spend tracking:** Monitor via session_status
- **Task efficiency metrics:** tokens per task completion
- **Model effectiveness:** success rates by model tier

## 📊 Expected Savings

**Before:** Sonnet for everything (~$0.003/1K tokens)
**After:** 
- 70% haiku tasks (~$0.00025/1K tokens) = **90% cost reduction**
- 25% sonnet (complex work) 
- 5% opus (critical tasks only)

**Estimated total savings: 60-80%** 💰

## 🚨 Red Flags - Use Higher Model When:
- Task failed with lower model
- Complex reasoning required
- Safety/security implications
- User specifically requests quality
- Time-sensitive important work

---
*Updated: 2026-03-01 - Implement gradually, monitor results*