# Note Templates for Second Brain

## Overview

Consistent templates accelerate note creation and ensure important information is captured systematically. This guide covers templates for different note types and their optimal use cases.

## Template Categories

### 1. People Templates

#### Basic Person Template
Use for: Family, friends, colleagues, contacts

```markdown
---
type: person
tags: [people]
created: {{date}}
relationship: 
status: active
---

# {{title}}

## Contact Information
- **Full Name:** 
- **Relationship:** 
- **Phone:** 
- **Email:** 
- **Location:** 

## Context
- **How we met:** 
- **Shared interests:** 
- **Professional connection:** 

## Recent Interactions
- 

## Notes & Reminders
- 

## Related
- **Projects:** [[Projects/]]
- **Family:** [[People/]]
```

#### Professional Contact Template
Use for: Work colleagues, vendors, service providers

```markdown
---
type: professional-contact
tags: [people, professional]
company: 
role: 
industry: 
---

# {{title}}

## Professional Details
- **Company:** 
- **Role/Title:** 
- **Industry:** 
- **LinkedIn:** 
- **Phone:** 
- **Email:** 

## Expertise & Services
- 

## Work History
### {{date}} - First Meeting
- Context:
- Discussion topics:
- Outcomes:

## Projects & Collaborations
- [[Projects/]]

## Communication Log
- 

## Notes
- 
```

### 2. Project Templates

#### General Project Template
Use for: Most personal projects

```markdown
---
type: project
tags: [projects]
status: planning
priority: medium
start_date: 
target_completion: 
---

# {{title}}

## Project Overview
**Goal:** 
**Status:** Planning
**Priority:** Medium
**Budget:** 
**Timeline:** 

## Success Criteria
- [ ] 
- [ ] 
- [ ] 

## Resources Required
### Tools
- 

### Materials
- 

### Skills/Knowledge
- 

### People
- [[People/]] - Role:

## Project Phases
### Phase 1: Planning
- [ ] Define requirements
- [ ] Research options
- [ ] Create detailed plan
- [ ] Gather resources

### Phase 2: Execution
- [ ] Begin implementation
- [ ] Regular progress checks
- [ ] Adjust as needed

### Phase 3: Completion
- [ ] Final review
- [ ] Document lessons learned
- [ ] Archive resources

## Progress Log
### {{date}}
- Project created

## Lessons Learned
- 

## Related
- **Knowledge:** [[Knowledge/]]
- **People:** [[People/]]
- **Areas:** [[Areas/]]
```

#### Technical Project Template
Use for: Homelab, coding, electronics projects

```markdown
---
type: technical-project
tags: [projects, tech]
category: 
difficulty: 
tools_needed: []
---

# {{title}}

## Technical Overview
**Category:** (Hardware/Software/Network/etc.)
**Difficulty:** (Beginner/Intermediate/Advanced)
**Estimated Time:** 
**Dependencies:** 

## Requirements
### Hardware
- 

### Software
- 

### Network/Connectivity
- 

### Skills Required
- 

## Architecture/Design
```
[Diagram or description]
```

## Implementation Steps
1. [ ] **Setup Environment**
   - Details:
   - Resources needed:

2. [ ] **Core Implementation**
   - Details:
   - Testing approach:

3. [ ] **Integration & Testing**
   - Integration points:
   - Test cases:

4. [ ] **Documentation & Deployment**
   - User documentation:
   - Deployment steps:

## Troubleshooting
### Common Issues
- **Problem:** 
  **Solution:** 

### Resources
- Documentation links:
- Community forums:
- Related projects: [[Projects/]]

## Code/Configuration
```
[Include key snippets or link to repos]
```

## Results
- **Performance metrics:** 
- **Lessons learned:** 
- **Future improvements:** 
```

### 3. Knowledge Templates

#### Learning Note Template
Use for: New concepts, research, study notes

```markdown
---
type: knowledge
tags: [learning]
topic: 
difficulty: 
source: 
completed: false
---

# {{title}}

## Overview
Brief description of the concept or topic.

## Key Concepts
### Concept 1
**Definition:** 
**Importance:** 
**Examples:** 

### Concept 2
**Definition:** 
**Importance:** 
**Examples:** 

## Practical Applications
- 

## Examples & Use Cases
### Example 1
**Scenario:** 
**Application:** 
**Outcome:** 

## Questions & Areas for Further Study
- [ ] Question 1
- [ ] Question 2

## Sources & References
- **Primary source:** 
- **Additional reading:** 
- **Related concepts:** [[Knowledge/]]

## Practice/Implementation
- [ ] Try example 1
- [ ] Build something with this
- [ ] Teach someone else

## Related
- **Projects:** [[Projects/]]
- **People:** [[People/]] (expert on this topic)
```

#### Reference Note Template
Use for: Technical specifications, procedures, how-to guides

```markdown
---
type: reference
tags: [reference]
category: 
last_updated: {{date}}
---

# {{title}}

## Quick Reference
*One-line summary of what this covers*

## Prerequisites
- 

## Step-by-Step Procedure
### Step 1: 
**Action:** 
**Expected result:** 
**Troubleshooting:** 

### Step 2:
**Action:** 
**Expected result:** 
**Troubleshooting:** 

## Examples
### Example 1: Common Use Case
```
[Code/commands/configuration]
```

### Example 2: Advanced Use Case
```
[Code/commands/configuration]
```

## Variations
- **For scenario X:** Modify step 2 to...
- **For scenario Y:** Add step 3.5...

## Troubleshooting
| Problem | Cause | Solution |
|---------|-------|----------|
|  |  |  |

## Related
- **Projects using this:** [[Projects/]]
- **Similar procedures:** [[Knowledge/]]
- **Dependencies:** [[Knowledge/]]

## Version History
- **{{date}}:** Created
```

### 4. Meeting Templates

#### General Meeting Template
Use for: Most meetings, calls, discussions

```markdown
---
type: meeting
tags: [meetings]
date: {{date}}
meeting_type: 
attendees: []
---

# {{title}}

## Meeting Details
- **Date:** {{date}}
- **Time:** 
- **Duration:** 
- **Location/Platform:** 
- **Meeting type:** (Planning/Review/Discussion/etc.)

## Attendees
- [[People/]] - Role/Reason
- [[People/]] - Role/Reason

## Agenda
1. **Topic 1** (5 min) - Purpose
2. **Topic 2** (15 min) - Purpose
3. **Topic 3** (10 min) - Purpose

## Discussion Notes
### Topic 1: 
**Key points:**
- 

**Decisions:**
- 

### Topic 2:
**Key points:**
- 

**Decisions:**
- 

## Action Items
- [ ] **Task description** - Assigned to: [[People/]] - Due: 
- [ ] **Task description** - Assigned to: [[People/]] - Due: 

## Decisions Made
- **Decision 1:** Rationale:
- **Decision 2:** Rationale:

## Follow-up Required
- **Next meeting:** Date/Purpose
- **Documents to create:** 
- **People to contact:** [[People/]]

## Related
- **Project:** [[Projects/]]
- **Previous meeting:** [[]]
- **Next meeting:** [[]]
```

### 5. Daily Note Templates

#### Standard Daily Note
Use for: Regular daily tracking

```markdown
---
type: daily-note
date: {{date}}
tags: [daily]
weather: 
mood: 
---

# {{date:YYYY-MM-DD}} - {{date:dddd}}

## Weather
**Temperature:** °C | **Conditions:** 

## Daily Focus
**Top 3 priorities:**
1. 
2. 
3. 

## Schedule
### Morning (6-12)
- 

### Afternoon (12-17)
- 

### Evening (17-22)
- 

## Tasks Completed
- [x] 
- [x] 

## People
**Talked with:** [[People/]]
**Context:** 

## Projects
**Worked on:** [[Projects/]]
**Progress:** 

## Learning
**New knowledge:** 
**Source:** [[Knowledge/]]

## Gratitude
- 
- 
- 

## Tomorrow's Prep
**Key tasks for tomorrow:**
- 

**Reminders:**
- 

## Notes & Reflections
*End-of-day thoughts*

---
← [[{{date-1:YYYY-MM-DD}}]] | [[{{date+1:YYYY-MM-DD}}]] →
```

#### Travel Daily Note
Use for: Days involving travel, trips

```markdown
---
type: daily-note
tags: [daily, travel]
location: 
trip: 
---

# {{date:YYYY-MM-DD}} - Travel Day

## Trip Details
**Trip:** [[Projects/Travel-]]
**Location:** 
**Weather:** 

## Itinerary
### Morning
- 

### Afternoon
- 

### Evening
- 

## Transportation
**Method:** 
**Duration:** 
**Notes:** 

## Accommodations
**Where:** 
**Check-in/out:** 
**Rating:** 

## Meals
**Breakfast:** 
**Lunch:** 
**Dinner:** 

## Highlights
- 

## Photos/Media
- 

## People Met
- [[People/]]

## Expenses
| Item | Amount | Category |
|------|--------|----------|
|  |  |  |

## Tomorrow's Plan
- 

---
← [[{{date-1:YYYY-MM-DD}}]] | [[{{date+1:YYYY-MM-DD}}]] →
```

### 6. Area Templates

#### Life Area Template
Use for: Health, Finance, Home, Work areas

```markdown
---
type: area
tags: [areas]
area: 
review_frequency: monthly
---

# {{title}}

## Area Overview
**Purpose:** What this area encompasses
**Current status:** 
**Last review:** 

## Goals & Objectives
### Short-term (3 months)
- [ ] 
- [ ] 

### Medium-term (1 year)
- [ ] 
- [ ] 

### Long-term (3+ years)
- [ ] 
- [ ] 

## Current Projects
- [[Projects/]] - Status: 
- [[Projects/]] - Status: 

## Recurring Tasks
### Daily
- 

### Weekly
- 

### Monthly
- 

### Quarterly
- 

## Key Metrics/KPIs
- **Metric 1:** Current value, Target
- **Metric 2:** Current value, Target

## Resources & References
- **Key documents:** [[]]
- **Helpful contacts:** [[People/]]
- **Reference materials:** [[Knowledge/]]

## Review Questions
*Use during regular area reviews*

1. What's working well?
2. What needs improvement?
3. What obstacles am I facing?
4. What support do I need?
5. Are my goals still relevant?

## Recent Updates
### {{date}}
- 

## Action Items
- [ ] 
- [ ] 

---
*Next review: [Date]*
```

## Template Usage Guidelines

### When to Create New Templates
- Recurring patterns in your note-taking
- Specific workflows that require consistency
- Complex information structures you use repeatedly

### Template Customization
- Adapt existing templates to your specific needs
- Add fields that matter to your workflow
- Remove sections that aren't relevant
- Create variations for different contexts

### Template Organization
- Store all templates in `_Templates/` folder
- Use clear, descriptive names
- Include usage instructions at the top
- Version templates if they evolve significantly

### Automation Tips
- Use Obsidian's Templater plugin for dynamic content
- Set up hotkeys for frequently used templates
- Create template picker for quick access
- Use folder templates for automatic application

### Best Practices
- Keep templates focused and purposeful
- Include linking prompts to encourage connections
- Use consistent formatting and structure
- Review and update templates periodically

The goal is to reduce cognitive load while ensuring important information is captured consistently across your second brain.