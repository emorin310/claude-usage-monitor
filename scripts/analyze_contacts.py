#!/usr/bin/env python3
"""
Analyze exported contacts for:
1. Deprecated email detection (@rdmcorp.com, @avotus.com)
2. Completely empty contacts (no email, no phone)
3. Duplicate detection (exact name matches)
4. Completeness analysis
5. Sort by modification date
"""
import json
import re
from datetime import datetime
from collections import defaultdict
import os

def load_contacts(filepath):
    """Load contacts from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def find_deprecated_emails(contacts):
    """Find contacts with deprecated email domains."""
    deprecated_domains = ['@rdmcorp.com', '@avotus.com']
    deprecated_contacts = []
    
    for contact in contacts:
        deprecated_emails = []
        for email in contact['emails']:
            email_lower = email.lower()
            for domain in deprecated_domains:
                if email_lower.endswith(domain):
                    deprecated_emails.append(email)
        
        if deprecated_emails:
            deprecated_contacts.append({
                'contact': contact,
                'deprecatedEmails': deprecated_emails
            })
    
    return deprecated_contacts

def find_empty_contacts(contacts):
    """Find contacts with neither email nor phone."""
    empty = []
    for contact in contacts:
        if not contact['emails'] and not contact['phones']:
            empty.append(contact)
    return empty

def find_duplicates(contacts):
    """Find duplicate contacts by exact name match."""
    name_to_contacts = defaultdict(list)
    
    for contact in contacts:
        name = contact['fullName'].strip()
        if name:  # Only consider contacts with names
            name_to_contacts[name].append(contact)
    
    # Filter to only names with multiple contacts
    duplicates = {name: contacts for name, contacts in name_to_contacts.items() 
                  if len(contacts) > 1}
    
    return duplicates

def analyze_completeness(contacts):
    """Analyze completeness of contacts."""
    stats = {
        'total': len(contacts),
        'hasEmail': 0,
        'hasPhone': 0,
        'hasBoth': 0,
        'hasNeither': 0,
        'hasEmailOnly': 0,
        'hasPhoneOnly': 0,
        'hasName': 0,
        'hasNote': 0
    }
    
    for contact in contacts:
        has_email = len(contact['emails']) > 0
        has_phone = len(contact['phones']) > 0
        has_name = bool(contact['fullName'].strip())
        has_note = bool(contact['note'].strip())
        
        if has_email:
            stats['hasEmail'] += 1
        if has_phone:
            stats['hasPhone'] += 1
        if has_email and has_phone:
            stats['hasBoth'] += 1
        if not has_email and not has_phone:
            stats['hasNeither'] += 1
        if has_email and not has_phone:
            stats['hasEmailOnly'] += 1
        if has_phone and not has_email:
            stats['hasPhoneOnly'] += 1
        if has_name:
            stats['hasName'] += 1
        if has_note:
            stats['hasNote'] += 1
    
    # Calculate percentages
    for key in list(stats.keys()):
        if key != 'total':
            stats[f'{key}Pct'] = (stats[key] / stats['total']) * 100
    
    return stats

def sort_by_modification_date(contacts):
    """Sort contacts by modification date (oldest first)."""
    # Parse dates if available
    def parse_date(date_str):
        if not date_str:
            return datetime.min
        try:
            # Try various date formats
            for fmt in ['%Y-%m-%d %H:%M:%S %z', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M:%S']:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
            # If all fail, return min date
            return datetime.min
        except:
            return datetime.min
    
    return sorted(contacts, key=lambda x: parse_date(x.get('modificationDate', '')))

def generate_reports(contacts, output_dir):
    """Generate all reports."""
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Deprecated emails report
    deprecated = find_deprecated_emails(contacts)
    with open(os.path.join(output_dir, 'deprecated-emails.md'), 'w') as f:
        f.write(f"# Deprecated Email Report\n\n")
        f.write(f"**Total contacts with deprecated emails:** {len(deprecated)}\n\n")
        f.write("| Name | Deprecated Emails | Other Emails | Phones |\n")
        f.write("|------|-------------------|--------------|--------|\n")
        for item in deprecated[:100]:  # First 100 only
            contact = item['contact']
            dep_emails = ', '.join(item['deprecatedEmails'])
            other_emails = ', '.join([e for e in contact['emails'] if e not in item['deprecatedEmails']])
            phones = ', '.join(contact['phones'][:3])
            if len(contact['phones']) > 3:
                phones += f"... (+{len(contact['phones'])-3} more)"
            f.write(f"| {contact['fullName']} | {dep_emails} | {other_emails} | {phones} |\n")
        
        if len(deprecated) > 100:
            f.write(f"\n*... and {len(deprecated) - 100} more contacts*\n")
    
    # 2. Empty contacts report
    empty = find_empty_contacts(contacts)
    with open(os.path.join(output_dir, 'empty-contacts.md'), 'w') as f:
        f.write(f"# Empty Contacts Report\n\n")
        f.write(f"**Total contacts with neither email nor phone:** {len(empty)}\n\n")
        f.write("| Name | Note | Modification Date |\n")
        f.write("|------|------|-------------------|\n")
        for contact in empty[:100]:
            note_preview = contact['note'][:50] + "..." if len(contact['note']) > 50 else contact['note']
            f.write(f"| {contact['fullName']} | {note_preview} | {contact.get('modificationDate', 'N/A')} |\n")
        
        if len(empty) > 100:
            f.write(f"\n*... and {len(empty) - 100} more contacts*\n")
    
    # 3. Duplicates report
    duplicates = find_duplicates(contacts)
    with open(os.path.join(output_dir, 'duplicates-report.md'), 'w') as f:
        f.write(f"# Duplicate Contacts Report\n\n")
        f.write(f"**Total duplicate names:** {len(duplicates)}\n")
        f.write(f"**Total contacts involved in duplicates:** {sum(len(v) for v in duplicates.values())}\n\n")
        
        # Sort by count (most duplicates first)
        sorted_duplicates = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)
        
        for name, dup_contacts in sorted_duplicates[:50]:  # Top 50 only
            f.write(f"## {name} ({len(dup_contacts)} duplicates)\n\n")
            
            # Find the most complete contact
            dup_contacts_sorted = sorted(dup_contacts, 
                                        key=lambda x: len(x['emails']) + len(x['phones']), 
                                        reverse=True)
            best_contact = dup_contacts_sorted[0]
            
            f.write(f"**Keep:** {best_contact['fullName']} ")
            if best_contact['emails']:
                f.write(f"(emails: {', '.join(best_contact['emails'][:3])}) ")
            if best_contact['phones']:
                f.write(f"(phones: {', '.join(best_contact['phones'][:3])})")
            f.write("\n\n")
            
            f.write("**Merge from others:**\n")
            for contact in dup_contacts_sorted[1:]:
                unique_emails = [e for e in contact['emails'] if e not in best_contact['emails']]
                unique_phones = [p for p in contact['phones'] if p not in best_contact['phones']]
                if unique_emails or unique_phones:
                    f.write(f"- Add emails: {', '.join(unique_emails)}\n")
                    f.write(f"- Add phones: {', '.join(unique_phones)}\n")
            
            f.write("\n**Delete:**\n")
            for contact in dup_contacts_sorted[1:]:
                f.write(f"- {contact['fullName']} ")
                if not contact['emails'] and not contact['phones']:
                    f.write("(empty)")
                f.write("\n")
            
            f.write("\n---\n\n")
        
        if len(sorted_duplicates) > 50:
            f.write(f"\n*... and {len(sorted_duplicates) - 50} more duplicate groups*\n")
    
    # 4. Completeness report
    stats = analyze_completeness(contacts)
    with open(os.path.join(output_dir, 'completeness-report.md'), 'w') as f:
        f.write(f"# Contact Completeness Analysis\n\n")
        f.write(f"**Total contacts:** {stats['total']:,}\n\n")
        f.write("## Field Presence\n\n")
        f.write("| Field | Count | Percentage |\n")
        f.write("|-------|-------|------------|\n")
        f.write(f"| Has email | {stats['hasEmail']:,} | {stats['hasEmailPct']:.1f}% |\n")
        f.write(f"| Has phone | {stats['hasPhone']:,} | {stats['hasPhonePct']:.1f}% |\n")
        f.write(f"| Has both email and phone | {stats['hasBoth']:,} | {stats['hasBothPct']:.1f}% |\n")
        f.write(f"| Has email only | {stats['hasEmailOnly']:,} | {stats['hasEmailOnlyPct']:.1f}% |\n")
        f.write(f"| Has phone only | {stats['hasPhoneOnly']:,} | {stats['hasPhoneOnlyPct']:.1f}% |\n")
        f.write(f"| Has neither email nor phone | {stats['hasNeither']:,} | {stats['hasNeitherPct']:.1f}% |\n")
        f.write(f"| Has name | {stats['hasName']:,} | {stats['hasNamePct']:.1f}% |\n")
        f.write(f"| Has note | {stats['hasNote']:,} | {stats['hasNotePct']:.1f}% |\n")
    
    # 5. Oldest contacts report
    sorted_contacts = sort_by_modification_date(contacts)
    oldest = [c for c in sorted_contacts if c.get('modificationDate')][:100]
    with open(os.path.join(output_dir, 'oldest-contacts.md'), 'w') as f:
        f.write(f"# Oldest Contacts by Modification Date\n\n")
        f.write(f"Showing oldest 100 contacts with modification dates\n\n")
        f.write("| Name | Emails | Phones | Modification Date |\n")
        f.write("|------|--------|--------|-------------------|\n")
        for contact in oldest:
            email_preview = ', '.join(contact['emails'][:2])
            if len(contact['emails']) > 2:
                email_preview += f"... (+{len(contact['emails'])-2})"
            
            phone_preview = ', '.join(contact['phones'][:2])
            if len(contact['phones']) > 2:
                phone_preview += f"... (+{len(contact['phones'])-2})"
            
            f.write(f"| {contact['fullName']} | {email_preview} | {phone_preview} | {contact.get('modificationDate', 'N/A')} |\n")
    
    # 6. Summary report
    with open(os.path.join(output_dir, 'cleanup-priority.md'), 'w') as f:
        f.write(f"# Contact Cleanup Priority\n\n")
        f.write(f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Contacts:** {stats['total']:,}\n\n")
        
        f.write("## Priority Actions\n\n")
        f.write("### 1. Remove Deprecated Email Addresses\n")
        f.write(f"- **Affects:** {len(deprecated)} contacts\n")
        f.write(f"- **Action:** Remove @rdmcorp.com and @avotus.com email addresses (keep contacts)\n")
        f.write(f"- **File:** `deprecated-emails.md` for full list\n\n")
        
        f.write("### 2. Delete Completely Empty Contacts\n")
        f.write(f"- **Affects:** {len(empty)} contacts\n")
        f.write(f"- **Action:** Delete contacts with neither email nor phone\n")
        f.write(f"- **File:** `empty-contacts.md` for full list\n\n")
        
        f.write("### 3. Merge Duplicates\n")
        f.write(f"- **Affects:** {len(duplicates)} duplicate groups, {sum(len(v) for v in duplicates.values())} total contacts\n")
        f.write(f"- **Action:** Merge duplicates, keep most complete record\n")
        f.write(f"- **File:** `duplicates-report.md` for detailed merge plan\n\n")
        
        f.write("### 4. Review Old Contacts\n")
        f.write(f"- **Action:** Review oldest 100 contacts for relevance\n")
        f.write(f"- **File:** `oldest-contacts.md` for list\n\n")
        
        f.write("## Expected Impact\n\n")
        f.write(f"- **Contacts to delete (empty):** {len(empty)} ({stats['hasNeitherPct']:.1f}%)\n")
        f.write(f"- **Contacts to keep:** {stats['total'] - len(empty)} ({100 - stats['hasNeitherPct']:.1f}%)\n")
        f.write(f"- **Email addresses to remove (deprecated domains):** {sum(len(item['deprecatedEmails']) for item in deprecated)}\n")
    
    return {
        'deprecatedCount': len(deprecated),
        'emptyCount': len(empty),
        'duplicateGroups': len(duplicates),
        'duplicateContacts': sum(len(v) for v in duplicates.values()),
        'stats': stats
    }

def main():
    input_file = os.path.expanduser('~/clawd-magi/data/contacts/contacts-export.json')
    output_dir = os.path.expanduser('~/clawd-magi/data/contacts')
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        print("Please run the export script first.")
        sys.exit(1)
    
    print(f"Loading contacts from {input_file}")
    contacts = load_contacts(input_file)
    print(f"Loaded {len(contacts)} contacts")
    
    print("Generating reports...")
    results = generate_reports(contacts, output_dir)
    
    print("\n=== ANALYSIS COMPLETE ===\n")
    print(f"Deprecated email contacts: {results['deprecatedCount']}")
    print(f"Empty contacts: {results['emptyCount']}")
    print(f"Duplicate groups: {results['duplicateGroups']}")
    print(f"Contacts in duplicates: {results['duplicateContacts']}")
    print(f"\nReports saved to {output_dir}/")
    print("- deprecated-emails.md")
    print("- empty-contacts.md")
    print("- duplicates-report.md")
    print("- completeness-report.md")
    print("- oldest-contacts.md")
    print("- cleanup-priority.md")

if __name__ == '__main__':
    main()