---
name: personal-document-search
description: Search personal documents across Google Drive and BigStore (local storage) to find identity documents (SIN, passport, driver's license), tax returns, medical records, insurance policies, and family documents. Use when users ask questions like "what is my SIN number?", "find my 2023 tax return", "show me passport documents", or need to locate specific personal/family documents by type, year, or family member name.
---

# Personal Document Search

Search and retrieve personal documents stored across Google Drive and BigStore (local file systems) using natural language queries. Handles identity documents, tax returns, medical records, insurance policies, and other family documents.

## Quick Start

Use the unified search script for natural language queries:

```bash
# Find specific documents
python3 scripts/unified_search.py "what is my SIN number"
python3 scripts/unified_search.py "find my 2023 tax return"  
python3 scripts/unified_search.py "show me passport documents"
python3 scripts/unified_search.py "find Tina's driver license"

# Search by category
python3 scripts/unified_search.py "medical documents"
python3 scripts/unified_search.py "insurance policies"
```

## Core Capabilities

### 1. Identity Document Search
Find government-issued identification:
- **SIN (Social Insurance Number):** "what is my SIN number", "find SIN card"
- **Passport:** "find passport", "show me passport documents"  
- **Driver's License:** "find driver's license", "show me license"
- **Health Card/OHIP:** "find health card", "OHIP documents"

### 2. Tax Document Retrieval
Locate tax-related documents by year:
- **Tax Returns:** "find 2023 tax return", "show me T1 for 2022"
- **Tax Slips:** "find T4 documents", "show me 2023 T5"
- **CRA Documents:** "find notice of assessment", "CRA correspondence"

### 3. Medical Document Access
Search health-related documents:
- **Prescriptions:** "find prescription documents", "medication records"
- **Lab Results:** "show me lab results", "blood test reports"  
- **Medical Records:** "find medical documents", "doctor visit records"

### 4. Insurance Document Location
Find insurance policies and claims:
- **Auto Insurance:** "find car insurance policy"
- **Home Insurance:** "find home insurance documents"
- **Life Insurance:** "show me life insurance policy"

### 5. Financial Document Search
Locate banking and investment documents:
- **Bank Statements:** "find bank statements for 2023"
- **Investment Records:** "show me investment statements"
- **Mortgage Documents:** "find mortgage papers"

### 6. Family Document Search
Search for documents belonging to family members:
- "find Tina's passport"
- "show me mom's medical documents"
- "find dad's tax return for 2022"

## Search Sources

The system searches across two main sources:

### Google Drive (Cloud Storage)
- Searches file names, metadata, and content
- Requires Google Drive API setup (see setup guide)
- Provides direct web links to found documents

### BigStore (Local Storage)  
- Searches local file systems and external drives
- Default locations: Documents, Downloads, Desktop, Google Drive folder
- Provides full file paths for local access

## Advanced Usage

### Direct Script Usage

**Google Drive only:**
```bash
python3 scripts/search_google_drive.py --terms "passport" "2023" --category identity
```

**BigStore only:**
```bash
python3 scripts/search_bigstore.py --terms "tax" "return" "2023" --category tax
```

**Custom search paths:**
```bash
python3 scripts/search_bigstore.py --paths "/Volumes/ExternalDrive" --terms "SIN"
```

### Search Query Types

**Content Search** (searches within documents):
```bash
python3 scripts/unified_search.py "social insurance number" --sources bigstore
```

**Filename Search** (default):
```bash
python3 scripts/unified_search.py "passport documents"
```

**Category Filtering:**
```bash
# Only search tax documents
python3 scripts/search_bigstore.py --terms "2023" --category tax
```

## Document Categories

The system automatically categorizes documents into:

- **identity:** SIN, passport, driver's license, health card
- **tax:** Tax returns, T4/T5 slips, CRA documents  
- **medical:** Prescriptions, lab results, medical records
- **insurance:** Auto, home, life, health insurance policies
- **financial:** Bank statements, investment records, mortgages
- **education:** Diplomas, transcripts, certificates
- **legal:** Wills, contracts, power of attorney documents

## Natural Language Processing

The unified search script understands these query patterns:

### Question Format
- "What is my SIN number?"
- "Where is my passport?"
- "Do I have my 2023 tax return?"

### Command Format  
- "Find my driver's license"
- "Show me insurance documents"
- "Get Tina's medical records"

### Year-Specific Searches
- "Find my 2023 tax return" → automatically adds "2023" to search terms
- "Show me 2022 T4 documents" → searches tax category with "2022"

### Family Member Searches
- "Find mom's passport" → adds family member name to search terms
- "Show me Tina's tax documents" → includes "tina" in search

## Setup Requirements

**First-time setup required** - See `references/setup-guide.md` for:

1. **Google Drive API setup:** OAuth credentials and authentication
2. **Python dependencies:** Install required packages
3. **Search path configuration:** Customize BigStore locations
4. **Family name configuration:** Add family member name variations

Quick setup verification:
```bash
# Test Google Drive access
python3 scripts/search_google_drive.py --terms "test" --format json

# Test local file access  
python3 scripts/search_bigstore.py --terms "pdf" --format table
```

## Output Formats

### Natural Language Answer (default)
```
Found 3 Social Insurance Number (SIN) document(s):

📁 **Local Files (BigStore):**
• **SIN-card-scan.pdf**
  📍 /Users/eric/Documents/Identity/SIN-card-scan.pdf
  📅 Modified: 2023-08-15

☁️ **Google Drive:**
• **Social Insurance Number - Eric.pdf**
  🔗 https://drive.google.com/file/d/1234567890/view
  📅 Modified: 2023-07-20
```

### JSON Output (for programmatic use)
```bash
python3 scripts/unified_search.py "find passport" --format json
```

## Error Handling

**Authentication Issues:**
- Google Drive: Clear token file and re-authenticate
- BigStore: Check file system permissions

**No Results Found:**
- Try broader search terms
- Check if documents are in expected locations  
- Verify file extensions are supported

**Performance Issues:**
- Use category filters to narrow searches
- Specify exact search paths instead of defaults
- Limit file extensions in BigStore searches

## Resources

### scripts/
- `unified_search.py` - Main natural language search interface
- `search_google_drive.py` - Google Drive API integration  
- `search_bigstore.py` - Local file system search
- All scripts are executable with `--help` for detailed usage

### references/
- `setup-guide.md` - Complete setup instructions and troubleshooting
- `document-types.md` - Detailed document categorization and search patterns

**When to load references:**
- Load `setup-guide.md` when authentication or configuration issues arise
- Load `document-types.md` when you need to understand document categories or add new document types