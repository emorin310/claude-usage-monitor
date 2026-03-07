# Multi-Agent Team Structure v2.0

## 🎯 Team Overview

**Date:** March 7, 2026  
**Latest Update:** Added Deap (Deep Thought) development agent  
**Goal:** Specialized agent roles with clear responsibilities

## 🤖 Agent Roster

### **Magi** - Primary Orchestrator
- **Role:** Orchestration, coordination, high-level planning
- **Model:** anthropic/claude-opus-4-6
- **Focus:** 
  - Multi-agent coordination
  - Task delegation and routing
  - Strategic planning and decision making
  - Discord communication relay
- **Workspace:** ~/clawd (primary)
- **Skills:** All orchestration and communication skills

### **Deep (Deep Thought)** - Lead Developer ⭐ NEW
- **Role:** Development, coding, GitHub management
- **Model:** anthropic/claude-opus-4-6  
- **Focus:**
  - All coding tasks and feature development
  - GitHub repository management (commits, versioning, releases)
  - Code review and quality assurance
  - Technical documentation generation
  - Development workflows and CI/CD
- **Workspace:** ~/clawd (shared development workspace)
- **Skills:** git, explain-code, documentation, test-runner

### **Marvin Jr.** - Infrastructure Builder
- **Role:** Infrastructure, monitoring, system management
- **Model:** anthropic/claude-sonnet-4-6
- **Focus:**
  - Systemd service management
  - Health monitoring and auto-restart procedures
  - Server infrastructure and networking
  - Home Assistant integration
  - Media stack management
- **Workspace:** ~/marvin-jr
- **Skills:** homelab management, monitoring, automation

### **Beeb (Beeblebrox)** - Operations Scout  
- **Role:** Operations automation, social monitoring
- **Model:** google/gemini-2.5-flash
- **Focus:**
  - Email triage and automation
  - Social media monitoring (Reddit, Twitter)
  - Deal alerts and hardware monitoring
  - Data processing and analysis
- **Workspace:** ~/beeb
- **Skills:** gmail-secretary, gog (Google Workspace), social monitoring

## 🔄 Task Delegation Flow

```
Eric's Request
      ↓
   🤖 Magi (Orchestrator)
      ↓
   Routes to:
   
🏗️ Infrastructure Task → Marvin Jr.
💻 Coding Task → Deep  
📧 Operations Task → Beeb
🤝 Coordination → Magi handles directly
```

## 📋 Specialization Matrix

| Task Type | Primary Agent | Secondary Support |
|-----------|---------------|------------------|
| **Feature Development** | Deep | Magi (oversight) |
| **Bug Fixes** | Deep | Magi (review) |
| **GitHub Management** | Deep | - |
| **System Infrastructure** | Marvin Jr. | Magi (planning) |
| **Email Automation** | Beeb | Magi (routing) |
| **Social Monitoring** | Beeb | - |
| **Multi-Agent Coordination** | Magi | All agents |
| **Discord Communication** | Magi | - |

## 🛠️ Development Workflow

### **Coding Tasks (via Deep):**
1. **Magi receives request** from Eric
2. **Magi delegates to Deep** with clear requirements  
3. **Deep develops solution** using specialized skills
4. **Deep commits to GitHub** with proper documentation
5. **Deep reports completion** back to Magi
6. **Magi confirms** with Eric

### **Infrastructure Tasks (via Marvin Jr.):**
1. **Magi receives request** from Eric
2. **Magi delegates to Marvin Jr.** with specifications
3. **Marvin Jr. implements** systemd/monitoring solution
4. **Marvin Jr. tests and validates** implementation
5. **Marvin Jr. reports status** back to Magi
6. **Magi confirms** with Eric

## 🔧 Recent Implementation

### **Deap Creation Process (March 7, 2026):**
1. **Skills installed via ClawHub:**
   - `git` - Comprehensive GitHub workflows
   - `explain-code` - Code analysis capabilities
   - `documentation` - Automated documentation  
   - `test-runner` - Multi-language testing
   
2. **Security validation:** All skills validated with skill-guard
3. **Agent spawned:** Using sessions_spawn with opus model
4. **First task assigned:** Commit Mission Control enhancements

### **Mission Control Ownership Transfer:**
- **Development:** Deap (new enhancements, features)
- **Infrastructure:** Marvin Jr. (systemd, monitoring, health checks)
- **Coordination:** Magi (task routing, oversight)

## 📈 Benefits of New Structure

### **For Magi (Orchestrator):**
- ✅ **Freed from coding tasks** - Focus on coordination
- ✅ **Strategic oversight** - High-level planning and routing  
- ✅ **Communication hub** - Discord relay and team coordination

### **For Development:**
- ✅ **Specialized focus** - Deap handles all coding with proper tools
- ✅ **GitHub expertise** - Dedicated agent with git skills
- ✅ **Quality assurance** - Testing and documentation automation

### **For Infrastructure:**
- ✅ **Marvin Jr. specialization** - Infrastructure-focused expertise
- ✅ **Service reliability** - Dedicated monitoring and maintenance
- ✅ **Operational excellence** - Health checks and auto-recovery

## 🎯 Success Metrics

- **Task completion speed** - Specialized agents working in parallel
- **Code quality** - Proper git workflows and documentation  
- **System reliability** - Infrastructure monitoring and maintenance
- **Team coordination** - Clear delegation and communication flows

## 📞 Communication Patterns

### **Agent-to-Agent:**
- **sessions_send()** for direct communication
- **State files** for coordination (~/shared/)
- **Council threads** in Todoist for formal handoffs

### **Eric Interface:**
- **Discord primary** - Magi as communication hub
- **Direct access** - Each agent available for direct tasking if needed
- **Status updates** - Regular progress reports via Magi

---

**Status:** ✅ Active deployment  
**Next Review:** March 14, 2026  
**Evolution:** Continuous optimization based on task patterns