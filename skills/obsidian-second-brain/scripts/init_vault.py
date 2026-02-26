#!/usr/bin/env python3
"""
Obsidian Vault Initializer

Creates the folder structure and templates for an Obsidian second brain vault.
Optimized for personal knowledge management with linking and organization.
"""

import os
import argparse
from pathlib import Path
from datetime import datetime

class VaultInitializer:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path).expanduser()
        self.templates_created = 0
        self.folders_created = 0
        
    def create_vault_structure(self, structure_type="personal"):
        """Create the complete vault folder structure."""
        print(f"Creating Obsidian vault at: {self.vault_path}")
        
        # Core folder structure
        folders = [
            "00-Inbox",
            "01-People",
            "01-People/Family",
            "01-People/Contacts", 
            "01-People/Professional",
            "02-Projects",
            "02-Projects/Active",
            "02-Projects/Ideas",
            "02-Projects/Completed",
            "03-Knowledge",
            "03-Knowledge/Tech",
            "03-Knowledge/Hobbies",
            "03-Knowledge/Reference",
            "04-Timeline",
            "04-Timeline/Daily-Notes",
            "04-Timeline/Life-Events",
            "05-Areas",
            "05-Areas/Health",
            "05-Areas/Finance", 
            "05-Areas/Home",
            "05-Areas/Work",
            "99-Archive",
            "_Templates",
            "_Attachments"
        ]
        
        # Create vault root
        self.vault_path.mkdir(parents=True, exist_ok=True)
        
        # Create folder structure
        for folder in folders:
            folder_path = self.vault_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            self.folders_created += 1
            print(f"Created: {folder}")
        
        # Create Obsidian config
        self._create_obsidian_config()
        
        # Create templates
        self._create_templates()
        
        # Create index files
        self._create_index_files()
        
    def _create_obsidian_config(self):
        """Create Obsidian configuration files."""
        obsidian_dir = self.vault_path / ".obsidian"
        obsidian_dir.mkdir(exist_ok=True)
        
        # Core settings
        core_plugins = {
            "file-explorer": True,
            "global-search": True,
            "switcher": True,
            "graph": True,
            "backlink": True,
            "page-preview": True,
            "note-composer": True,
            "command-palette": True,
            "markdown-importer": True,
            "word-count": True,
            "open-with-default-app": True,
            "file-recovery": True
        }
        
        app_config = {
            "legacyEditor": False,
            "livePreview": True,
            "useMarkdownLinks": True,
            "newFileLocation": "folder",
            "newFileFolderPath": "00-Inbox",
            "attachmentFolderPath": "_Attachments",
            "showLineNumber": True,
            "spellcheck": True
        }
        
        # Write config files
        import json
        
        with open(obsidian_dir / "core-plugins.json", "w") as f:
            json.dump(core_plugins, f, indent=2)
        
        with open(obsidian_dir / "app.json", "w") as f:
            json.dump(app_config, f, indent=2)
            
        print("Created Obsidian configuration")
    
    def _create_templates(self):
        """Create note templates for different content types."""
        templates_dir = self.vault_path / "_Templates"
        
        templates = {
            "Person Template.md": self._person_template(),
            "Project Template.md": self._project_template(),
            "Meeting Template.md": self._meeting_template(),
            "Daily Note Template.md": self._daily_note_template(),
            "Knowledge Note Template.md": self._knowledge_template(),
            "Document Summary Template.md": self._document_summary_template(),
            "Contact Import Template.md": self._contact_import_template()
        }
        
        for filename, content in templates.items():
            template_path = templates_dir / filename
            with open(template_path, 'w') as f:
                f.write(content)
            self.templates_created += 1
            print(f"Created template: {filename}")
    
    def _person_template(self):
        return """---
type: person
tags: [people]
created: {{date}}
---

# {{title}}

## Basic Information
- **Full Name:** 
- **Relationship:** 
- **Contact Info:** 
- **Birthday:** 
- **Location:** 

## Professional
- **Job/Role:** 
- **Company:** 
- **Industry:** 

## Personal Context
- **How We Met:** 
- **Shared Interests:** 
- **Family:** 

## Recent Interactions
- 

## Notes & Reminders
- 

## Related
- **Projects:** 
- **Events:** 
- **Documents:** 

---
*Last updated: {{date}}*
"""

    def _project_template(self):
        return """---
type: project
tags: [projects]
status: planning
priority: medium
created: {{date}}
---

# {{title}}

## Overview
**Goal:** 
**Status:** Planning
**Priority:** Medium
**Timeline:** 

## Details
### Motivation
Why is this project important?

### Success Criteria
- [ ] 
- [ ] 
- [ ] 

### Resources Needed
- **Tools:** 
- **Materials:** 
- **Budget:** 
- **Time:** 

## Progress Log
### {{date}}
- Project created

## Tasks
- [ ] Define requirements
- [ ] Gather resources
- [ ] Create timeline
- [ ] Execute plan
- [ ] Review outcomes

## Related
- **People:** [[People/]]
- **Knowledge:** [[Knowledge/]]
- **Documents:** 

## Notes
"""

    def _meeting_template(self):
        return """---
type: meeting
tags: [meetings]
date: {{date}}
---

# {{title}}

**Date:** {{date}}
**Time:** 
**Location/Platform:** 
**Duration:** 

## Attendees
- [[People/]] - 
- [[People/]] - 

## Agenda
1. 
2. 
3. 

## Discussion Notes
### Topic 1

### Topic 2

### Topic 3

## Action Items
- [ ] **Task** - Assigned to [[People/]] - Due: 
- [ ] **Task** - Assigned to [[People/]] - Due: 

## Decisions Made
- 

## Follow-up
- Next meeting: 
- Related: [[Projects/]]

## Notes
"""

    def _daily_note_template(self):
        return """---
type: daily-note
date: {{date}}
tags: [daily]
---

# {{date:YYYY-MM-DD}}

## Weather
**Temp:** °C | **Conditions:** 

## Schedule
### Morning
- 

### Afternoon
- 

### Evening
- 

## Tasks
- [ ] 
- [ ] 
- [ ] 

## Notes & Thoughts
- 

## People
Met/talked with: [[People/]]

## Projects
Worked on: [[Projects/]]

## Gratitude
- 
- 
- 

## Tomorrow's Focus
- 

---
← [[{{date-1:YYYY-MM-DD}}]] | [[{{date+1:YYYY-MM-DD}}]] →
"""

    def _knowledge_template(self):
        return """---
type: knowledge
tags: [knowledge]
topic: 
created: {{date}}
---

# {{title}}

## Overview
Brief description of the concept or topic.

## Key Points
- **Point 1:** 
- **Point 2:** 
- **Point 3:** 

## Details
### Main Content


### Examples


### Applications


## Sources
- **Original document:** [[]]
- **References:** 
- **Related notes:** [[]]

## Questions & TODO
- [ ] Question to research
- [ ] Follow-up needed

## Related
- **Projects:** [[Projects/]]
- **People:** [[People/]]
- **Tags:** #

---
*Source: Migrated from [original location]*
"""

    def _document_summary_template(self):
        return """---
type: document-summary
tags: [documents, imported]
source: 
created: {{date}}
---

# {{title}}

## Document Info
- **Original File:** 
- **Type:** 
- **Date Created:** 
- **Size:** 
- **Location:** 

## Summary
Brief description of document contents and purpose.

## Key Information
### Important Details
- 
- 
- 

### Action Items
- [ ] 
- [ ] 

### Contacts/People
- [[People/]] - 

### Dates & Deadlines
- 

## Content Highlights
> Key quotes or excerpts from the document

## Linked Content
- **Projects:** [[Projects/]]
- **People:** [[People/]]
- **Related Docs:** [[]]

## Tags
#documents #imported 

---
*Original document archived in: [file path]*
"""

    def _contact_import_template(self):
        return """---
type: contact-import
tags: [people, imported-contacts]
source: 
imported: {{date}}
---

# Imported Contacts from {{title}}

## Source Information
- **Original File:** 
- **Import Date:** {{date}}
- **Total Contacts:** 
- **Source System:** 

## Contact List
| Name | Phone | Email | Notes |
|------|--------|--------|--------|
|  |  |  |  |

## Processing Notes
- [ ] Review for duplicates
- [ ] Create individual person notes for important contacts
- [ ] Add to relevant project/area notes
- [ ] Archive original contact file

## Categories Identified
### Family
- [[People/Family/]]

### Professional
- [[People/Professional/]]

### Personal
- [[People/Contacts/]]

## Next Steps
- [ ] Create detailed notes for key contacts
- [ ] Link to existing people notes
- [ ] Update relationship information

---
*Imported from: [source system/file]*
"""

    def _create_index_files(self):
        """Create index/MOC files for major sections."""
        indices = {
            "Home.md": self._home_index(),
            "01-People/People Index.md": self._people_index(),
            "02-Projects/Projects Index.md": self._projects_index(),
            "03-Knowledge/Knowledge Index.md": self._knowledge_index(),
            "04-Timeline/Timeline Index.md": self._timeline_index()
        }
        
        for filename, content in indices.items():
            index_path = self.vault_path / filename
            with open(index_path, 'w') as f:
                f.write(content)
            print(f"Created index: {filename}")

    def _home_index(self):
        return f"""---
type: home
tags: [index, moc]
created: {datetime.now().strftime('%Y-%m-%d')}
---

# 🏠 Second Brain Home

Welcome to your Obsidian second brain! This vault contains your migrated and organized personal knowledge.

## 🚀 Quick Navigation

### 📋 Daily Workflow
- [[00-Inbox/]] - New notes start here
- [[04-Timeline/Daily-Notes/]] - Today's note
- [[02-Projects/Active/]] - Current projects

### 📚 Main Sections
- [[01-People/People Index]] - Family, friends, contacts
- [[02-Projects/Projects Index]] - All projects (active, ideas, completed)  
- [[03-Knowledge/Knowledge Index]] - Reference materials and learning
- [[04-Timeline/Timeline Index]] - Daily notes and life events
- [[05-Areas/]] - Life areas and ongoing responsibilities

### 🔧 Utilities
- [[_Templates/]] - Note templates
- [[99-Archive/]] - Completed and historical content

## 📊 Vault Statistics
- **Created:** {datetime.now().strftime('%Y-%m-%d')}
- **Total Notes:** Query: `list from "" where !startswith(file.name, ".")` 
- **Recent Notes:** Query: `list from "" sort file.mtime desc limit 10`

## 🔗 Recent Activity
*This section will auto-populate as you add content*

---

## 🎯 Getting Started
1. **Add new content** to [[00-Inbox/]]
2. **Use templates** from [[_Templates/]] for consistency
3. **Link liberally** - connections make knowledge powerful
4. **Review daily** - check recent notes and inbox

*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""

    def _people_index(self):
        return """---
type: index
tags: [people, index, moc]
---

# 👥 People Index

Central hub for all people-related notes and relationships.

## 👨‍👩‍👧‍👦 Family
```query
list from "01-People/Family" sort file.name
```

## 💼 Professional
```query  
list from "01-People/Professional" sort file.name
```

## 👋 Personal Contacts
```query
list from "01-People/Contacts" sort file.name
```

## 🔗 Quick Add
- **New person:** Use [[_Templates/Person Template]]
- **Import contacts:** Use [[_Templates/Contact Import Template]]

## 📊 Relationship Map
*Visual relationship mapping to be added*

## 🎂 Important Dates
### Birthdays
- 

### Anniversaries
- 

---
*Total people: [auto-count pending]*
"""

    def _projects_index(self):
        return """---
type: index  
tags: [projects, index, moc]
---

# 🚀 Projects Index

## 🔥 Active Projects
```query
list from "02-Projects/Active" where contains(tags, "projects") sort priority
```

## 💡 Ideas & Someday
```query
list from "02-Projects/Ideas" sort file.name  
```

## ✅ Completed Projects
```query
list from "02-Projects/Completed" sort file.mtime desc limit 10
```

## 📊 Project Status Overview
- **Active:** [count]
- **Ideas:** [count]  
- **Completed:** [count]

## 🎯 Current Focus
*Update this section with your top 3 current projects*

1. 
2. 
3. 

---
*Use [[_Templates/Project Template]] for new projects*
"""

    def _knowledge_index(self):
        return """---
type: index
tags: [knowledge, index, moc]
---

# 📚 Knowledge Index

## 💻 Technology  
```query
list from "03-Knowledge/Tech" sort file.name
```

## 🛠️ Hobbies & Interests
```query
list from "03-Knowledge/Hobbies" sort file.name
```

## 📖 Reference Materials
```query
list from "03-Knowledge/Reference" sort file.name
```

## 🏷️ Knowledge by Tag
### Most Used Tags
*Will populate as content is added*

## 🔗 Cross-References
### Recently Updated
```query
list from "03-Knowledge" sort file.mtime desc limit 10
```

---
*Use [[_Templates/Knowledge Note Template]] for new knowledge entries*
"""

    def _timeline_index(self):
        return f"""---
type: index
tags: [timeline, index, moc]  
---

# ⏰ Timeline Index

## 📅 Daily Notes
### Current Week
```query
list from "04-Timeline/Daily-Notes" sort file.name desc limit 7
```

### This Month  
```query
list from "04-Timeline/Daily-Notes" where date(file.name) >= date(today) - dur(30 days) sort file.name desc
```

## 🎉 Life Events
```query
list from "04-Timeline/Life-Events" sort file.name desc
```

## 📊 Timeline Statistics
- **First entry:** [auto-calculate]
- **Latest entry:** [auto-calculate]  
- **Total daily notes:** [count]

## 🔗 Quick Navigation
- **Today:** [[{datetime.now().strftime('%Y-%m-%d')}]]
- **Yesterday:** [[{(datetime.now()).strftime('%Y-%m-%d')}]]
- **New daily note:** Use [[_Templates/Daily Note Template]]

---
*Timeline spans from [earliest] to [latest]*
"""

def main():
    parser = argparse.ArgumentParser(description="Initialize Obsidian vault structure")
    parser.add_argument("--vault-path", default="~/Documents/ObsidianVault",
                       help="Path where vault should be created")
    parser.add_argument("--structure", default="personal", 
                       choices=["personal", "professional", "academic"],
                       help="Type of vault structure")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be created without actually creating")
    
    args = parser.parse_args()
    
    initializer = VaultInitializer(args.vault_path)
    
    if args.dry_run:
        print(f"DRY RUN: Would create vault at {initializer.vault_path}")
        print("Folders and templates would be created...")
        return
    
    try:
        initializer.create_vault_structure(args.structure)
        
        print("\n" + "="*50)
        print("VAULT CREATION COMPLETE")
        print("="*50)
        print(f"Vault created at: {initializer.vault_path}")
        print(f"Folders created: {initializer.folders_created}")
        print(f"Templates created: {initializer.templates_created}")
        print("\nNext steps:")
        print("1. Open vault in Obsidian")
        print("2. Run data discovery: python3 scripts/discover_data.py")
        print("3. Begin migration: python3 scripts/harvest_documents.py")
        print("4. Start using templates in _Templates/ folder")
        
    except Exception as e:
        print(f"Error creating vault: {e}")
        return 1

if __name__ == "__main__":
    main()