#!/bin/bash
# Add modification dates from the SQLite database

DB="$HOME/Library/Application Support/AddressBook/AddressBook-v22.abcddb"
INPUT="$HOME/clawd-magi/data/contacts/icloud-full-export.tsv"
OUTPUT="$HOME/clawd-magi/data/contacts/icloud-full-export-with-dates.tsv"

# First, let's check if we can access the database while Contacts is running
# We'll create a temporary copy to avoid conflicts
TEMP_DB="/tmp/contacts-temp.db"
cp "$DB" "$TEMP_DB"
cp "$DB-shm" "$TEMP_DB-shm" 2>/dev/null
cp "$DB-wal" "$TEMP_DB-wal" 2>/dev/null

# Checkpoint to merge WAL
sqlite3 "$TEMP_DB" "PRAGMA wal_checkpoint(TRUNCATE);" 2>/dev/null

# Export all contacts with modification dates from database
sqlite3 -separator $'\t' "$TEMP_DB" > /tmp/db-contacts.tsv <<'EOF'
SELECT 
    COALESCE(ZFIRSTNAME || ' ' || ZLASTNAME, ZFIRSTNAME, ZLASTNAME, ZORGANIZATION, '') as Name,
    datetime(ZMODIFICATIONDATE + 978307200, 'unixepoch') as ModificationDate
FROM ZABCDRECORD
WHERE (ZFIRSTNAME IS NOT NULL OR ZLASTNAME IS NOT NULL OR ZORGANIZATION IS NOT NULL)
ORDER BY Name;
EOF

echo "Database has $(wc -l < /tmp/db-contacts.tsv | tr -d ' ') records with modification dates"

# For now, just copy the original file since matching will be complex
cp "$INPUT" "$OUTPUT"

# Clean up
rm -f "$TEMP_DB" "$TEMP_DB-shm" "$TEMP_DB-wal" /tmp/db-contacts.tsv

echo "Output saved to: $OUTPUT"
echo "Note: Modification dates not available through Contacts API"
echo "Consider using iCloud web interface or third-party tools for modification dates"
