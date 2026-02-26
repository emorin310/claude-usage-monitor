---
name: obsidian-second-brain
description: Build and manage comprehensive Obsidian second brain by harvesting data from scattered sources (BigStore archives, emails, OneNote, documents, contacts) and converting to linked markdown. Use when creating knowledge vaults, organizing personal archives, building connected note systems, migrating from various data sources to Obsidian, or establishing cross-referenced personal knowledge bases.
---

# Obsidian Second Brain Builder

Transform scattered personal data into a comprehensive, linked Obsidian knowledge vault. This skill orchestrates the migration and organization of data from multiple sources into an intelligently connected second brain.

## Quick Start

### 1. Initialize Vault Structure
```bash
python3 scripts/init_vault.py --vault-path ~/Documents/ObsidianVault --structure personal
```

### 2. Discover Data Sources
```bash
python3 scripts/discover_data.py --scan-paths "/mnt/bigstore,~/Documents,~/Downloads" --output data-inventory.json
```

### 3. Convert and Link Content
```bash
python3 scripts/harvest_documents.py --source-path /mnt/bigstore/REVIEW --target-vault ~/Documents/ObsidianVault
python3 scripts/create_links.py --vault-path ~/Documents/ObsidianVault --strategy people,projects,timeline
```

## Core Capabilities

### Data Harvesting
- **Document Conversion**: PDF, Word, text files → structured markdown
- **Email Mining**: Extract conversations, contacts, actionable items
- **OneNote Migration**: Preserve structure while converting to linked notes
- **Photo Curation**: Extract metadata, create visual timelines
- **Contact Synthesis**: Merge contact lists, build relationship maps

### Intelligent Linking
- **People Networks**: Auto-link family, contacts, colleagues
- **Project Connections**: Link related files, timelines, outcomes
- **Topic Clustering**: Group related content with tag-based organization
- **Timeline Building**: Chronological connections across life events
- **Location Mapping**: Geographic and contextual relationships

### Vault Organization
- **Template System**: Pre-built note templates for people, projects, events
- **Folder Structures**: Logical hierarchies with cross-cutting links
- **Index Generation**: Auto-created MOCs (Maps of Content)
- **Tag Ontologies**: Structured tagging systems

## Vault Structure

### Core Folders
```
ObsidianVault/
├── 00-Inbox/              # New, unprocessed notes
├── 01-People/              # Family, contacts, relationships
├── 02-Projects/            # Homelab, woodworking, photography
├── 03-Knowledge/           # Technical notes, references
├── 04-Timeline/            # Daily notes, life events
├── 05-Areas/               # Ongoing responsibilities
├── 99-Archive/             # Completed, historical content
└── _Templates/             # Note templates
```

### Template Examples
- **Person Template**: Contact info, relationships, interaction history
- **Project Template**: Goals, timeline, files, outcomes
- **Meeting Template**: Attendees, agenda, action items, follow-ups
- **Daily Note Template**: Weather, events, tasks, reflections

## Migration Strategies

### Phase 1: Foundation (Days 1-2)
1. Create vault structure and templates
2. Scan and inventory all data sources
3. Extract high-value content (contacts, recent projects)

### Phase 2: Bulk Migration (Weeks 1-4)
1. **Deploy specialized sub-agents** for different data types:
   - Document Processor (PDFs, Word docs)
   - Email Archaeologist (Gmail, archived emails)
   - Photo Curator (image collections with metadata)
   - Contact Synthesizer (multiple address books)

### Phase 3: Link Intelligence (Ongoing)
1. Run relationship detection algorithms
2. Create topic clusters and knowledge maps
3. Build timeline connections
4. Establish maintenance routines

## Sub-Agent Coordination

### Document Processor Agent
```bash
sessions_spawn --task "Process all PDFs and Word docs in BigStore DOCUMENTS folder. Convert to markdown, extract key info, create person/project links." --label "doc-processor" --agentId "magi"
```

### Email Archaeologist Agent  
```bash
sessions_spawn --task "Scan Gmail archives for important conversations, extract contact info, create relationship timeline notes." --label "email-miner" --agentId "magi"
```

### Photo Timeline Curator
```bash
sessions_spawn --task "Process photo collections, extract EXIF data, create timeline entries, link to people and events." --label "photo-curator" --agentId "magi"
```

## Advanced Features

### Auto-Linking Algorithms
- **Name Recognition**: Detect person references across documents
- **Project References**: Link files to project notes automatically
- **Date Correlation**: Connect events by timestamps
- **Location Mapping**: Geographic context for notes and files

### Maintenance Automation
- **Daily Cleanup**: Process inbox, suggest links, update indexes
- **Weekly Reviews**: Generate connection reports, identify gaps
- **Monthly Archives**: Move completed content, update structure

## Data Source Handlers

### BigStore Archives
- **Target**: `/mnt/bigstore/REVIEW/DOCUMENTS/`
- **Strategy**: Recursive scan, categorize by type, extract metadata
- **Output**: Structured markdown with auto-generated frontmatter

### Email Integration
- **Sources**: Gmail, archived .mbox files
- **Extraction**: Contact details, important threads, attachments
- **Links**: Auto-connect to people notes, create conversation timelines

### OneNote Migration
- **Process**: Export → HTML → Markdown conversion
- **Preservation**: Maintain section hierarchy, embedded files
- **Enhancement**: Add Obsidian-style linking, improve navigation

## Scripts Overview

- `init_vault.py` - Create vault structure and templates
- `discover_data.py` - Scan and inventory available data sources
- `harvest_documents.py` - Convert documents to linked markdown
- `extract_contacts.py` - Build comprehensive contact database
- `create_links.py` - Generate intelligent cross-references
- `generate_mocs.py` - Create Maps of Content (index pages)
- `timeline_builder.py` - Build chronological relationship maps

## References

- **Advanced Linking**: See `references/linking-strategies.md`
- **Template Library**: See `references/templates.md`
- **Data Conversion**: See `references/conversion-patterns.md`
- **Sub-Agent Coordination**: See `references/agent-workflows.md`

## Getting Started

Ready to build your second brain? Start with data discovery:

```bash
python3 scripts/discover_data.py --quick-scan
```

This will identify your available data sources and recommend the best migration path.