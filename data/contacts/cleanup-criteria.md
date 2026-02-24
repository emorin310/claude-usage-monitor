# Contact Cleanup Criteria

**From Eric (2026-02-03):**

## Auto-Delete Rules

### 1. Delete EMAIL FIELD (not contact) if:
- Email ends in `@rdmcorp.com` (deprecated)
- Email ends in `@avotus.com` (deprecated)

**Action:** Remove the email field, keep the contact

### 2. Delete ENTIRE CONTACT if:
- Missing **BOTH** phone **AND** email (completely useless)

**From sample of 100:**
- ~2% have neither → DELETE CONTACT (~138 contacts)

**KEEP contacts with:**
- ✅ Email only (no phone) - ~16% (~1,107 contacts)
- ✅ Phone only (no email) - ~39% (~2,698 contacts)  
- ✅ Both email and phone - ~44% (~3,045 contacts)

## Last Modified Dates
- Export should include last updated/modified timestamp
- Sort by oldest first
- Eric will review very old contacts for relevance

## Known Issues
- **iCloud glitch** created many duplicates a while back
- Duplicate detection is HIGH PRIORITY
- Expect significant duplicate count

## Duplicate Handling

### Exact Duplicates (e.g., "Bryce Berry" appearing 5 times)
**Strategy:**
1. Group all contacts with identical names
2. For each duplicate group:
   - Keep the **most complete** record (most fields filled)
   - **Merge** unique phone numbers and emails into the kept record
   - **Delete** the redundant duplicates

**Example:**
```
Bryce Berry #1: phone 555-1234, no email
Bryce Berry #2: email bryce@example.com, no phone
Bryce Berry #3: phone 555-1234, email bryce@example.com (most complete)
Bryce Berry #4: no phone, no email (useless)
Bryce Berry #5: phone 555-9999 (different number!)

→ Keep #3 as base
→ Add phone 555-9999 from #5
→ Delete #1, #2, #4, #5
→ Result: 1 contact with all unique data
```

### Report Format
For each duplicate group, show:
- Name + count (e.g., "Bryce Berry: 5 duplicates")
- Which record will be kept (ID + fields)
- Which records will be deleted
- Any data that will be merged

## Priority Order
1. Find contacts with @rdmcorp.com or @avotus.com emails → REMOVE EMAIL FIELD
2. Find contacts with neither phone nor email → DELETE CONTACT
3. **Detect and merge duplicates** (exact name matches)
4. Sort by last modified date (oldest first for Eric's review)

## Expected Results
Based on sample of 100:
- **Delete entire contact:** ~2% with neither phone/email = ~138 contacts
- **Remove email field:** All @rdmcorp.com/@avotus.com addresses
- **Keep all other contacts:** ~6,781 contacts (including incomplete ones)

Minimal cleanup - mostly just removing deprecated email addresses and truly empty contacts.
