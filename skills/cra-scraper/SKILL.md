---
name: cra-scraper
description: Scrape and extract Canadian tax information from canada.ca using Playwright, with intelligent parsing of CRA deductions, credits, and tax rules. Use when Magi needs to: (1) Extract current CRA tax deduction rules and eligibility, (2) Retrieve Ontario provincial tax credits and deductions, (3) Build searchable reference databases of tax information, or (4) Keep CRA knowledge current with latest federal/provincial tax changes.
---

# CRA Scraper Skill

Extract and structure Canadian tax information from canada.ca using headless browser automation.

## Quick Start

### Basic Scraping

```bash
python3 scripts/scrape_cra.py \
  --url https://www.canada.ca/en/revenue-agency/ \
  --output cra-data.json
```

### Extract Deductions

```bash
python3 scripts/scrape_cra.py \
  --target deductions \
  --year 2025 \
  --province ontario \
  --output deductions-2025.json
```

### Build Knowledge Database

```bash
python3 scripts/scrape_cra.py \
  --target all \
  --build-index \
  --output cra-knowledge.json
```

## Key Features

- **Playwright-based**: Handles JavaScript-heavy pages that simple HTTP fetching can't access
- **Structured extraction**: Parses tax rules into searchable JSON format
- **Multi-target support**: Deductions, credits, income types, filing requirements
- **Change detection**: Compare against previous scrapes to identify new rules
- **Searchable index**: Build full-text searchable database of tax information

## Usage Patterns

### Pattern 1: Check Current Deductions
```python
from scrape_cra import CRAScraper

scraper = CRAScraper()
deductions = scraper.get_deductions(year=2025, province='ontario')
# Returns: [{title, description, eligibility, limit, notes}, ...]
```

### Pattern 2: Search by Keyword
```python
scraper = CRAScraper()
results = scraper.search("home office deduction")
# Returns: Relevant deductions, credits, rules matching query
```

### Pattern 3: Validate Tax Item
```python
scraper = CRAScraper()
is_eligible = scraper.validate_deduction("home office", {
    "self_employed": True,
    "square_feet": 200,
    "total_home_sqft": 1000
})
```

## Configuration

Set Playwright headless mode, timeout, and proxy in `scripts/scrape_cra.py`:

```python
browser_config = {
    "headless": True,
    "timeout": 30000,
    "viewport": {"width": 1280, "height": 720}
}
```

## Reference Files

See [CRA Deductions](references/cra-deductions.md) for structured list of common deductions.

See [CRA Credits](references/cra-credits.md) for provincial and federal credits.

## Notes

- CRA updates tax rules annually; re-scrape each tax year for current information
- Some pages require JavaScript execution; Playwright handles this automatically
- Output is validated against CRA schema before storage
- Sensitive information is redacted (personal examples, social numbers, etc.)
