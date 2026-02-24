# Setup Guide for Personal Document Search

This guide covers the initial setup required to enable document search across Google Drive and BigStore.

## Google Drive Setup

### 1. Google Cloud Console Setup
To search Google Drive, you need to set up Google Drive API credentials:

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Name it something like "Personal Document Search"

2. **Enable Google Drive API:**
   - In the Cloud Console, go to APIs & Services → Library
   - Search for "Google Drive API" and enable it

3. **Create Credentials:**
   - Go to APIs & Services → Credentials
   - Click "Create Credentials" → "OAuth client ID"
   - Select "Desktop application"
   - Name it "Document Search Client"
   - Download the JSON file

4. **Install Credentials:**
   ```bash
   # Create OpenClaw config directory
   mkdir -p ~/.config/openclaw
   
   # Copy the downloaded JSON file
   cp ~/Downloads/client_secret_*.json ~/.config/openclaw/google_drive_credentials.json
   ```

### 2. Python Dependencies
Install required Python packages:

```bash
# Google API client
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# PDF processing (optional but recommended)
pip install pdfplumber

# Word document processing (optional)
pip install python-docx
```

### 3. Initial Authentication
Run the Google Drive search script once to complete OAuth flow:

```bash
python3 scripts/search_google_drive.py --terms "test" --format json
```

This will:
- Open your browser for Google authentication
- Save the token to `~/.config/openclaw/google_drive_token.json`
- Future searches will use the saved token

## BigStore Setup

### 1. Default Search Locations
The BigStore script searches these default locations (if they exist):

**macOS/Linux:**
- `~/Documents`
- `~/Downloads`
- `~/Desktop`
- `~/Google Drive`
- `~/Dropbox`
- `~/OneDrive`

**External Drives:**
- `/Volumes/BigStore` (macOS)
- `/mnt/bigstore` (Linux)

### 2. Custom Search Paths
Add your specific document locations by:

1. **Editing the script defaults** in `search_bigstore.py`:
   ```python
   # Add your custom paths to the default_paths list
   default_paths = [
       home / "Documents",
       home / "Your-Custom-Path",
       Path("/path/to/external/drive"),
       # ... existing paths
   ]
   ```

2. **Using command-line arguments:**
   ```bash
   python3 scripts/search_bigstore.py --paths "/path/to/docs" "/another/path" --terms "passport"
   ```

### 3. File System Permissions
Ensure the script has read access to your document directories:

```bash
# Check permissions
ls -la ~/Documents

# Fix permissions if needed (macOS)
chmod -R +r ~/Documents
```

## Optional Dependencies

### PDF Text Extraction
For content search within PDFs, install one of these:

**Option 1: pdfplumber (recommended)**
```bash
pip install pdfplumber
```

**Option 2: poppler-utils (system package)**
```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils

# CentOS/RHEL
sudo yum install poppler-utils
```

### Word Document Support
For searching within .docx files:
```bash
pip install python-docx
```

## Configuration Files

### Document Categories
Edit `references/document-types.md` to customize:
- Document type definitions
- Search term patterns
- File naming conventions
- Family member name variations

### Search Paths
Create a config file for persistent search paths:

```bash
# Create config file
cat > ~/.config/openclaw/document_search.json << EOF
{
  "bigstore_paths": [
    "/Volumes/MyExternalDrive/Documents",
    "/Users/username/MyDocuments",
    "/path/to/family/files"
  ],
  "family_names": {
    "spouse": ["tina", "christina", "tina morin"],
    "parent1": ["mom", "mother", "actual name"],
    "parent2": ["dad", "father", "actual name"]
  }
}
EOF
```

## Testing the Setup

### Test Google Drive Search
```bash
# Search for any PDF files
python3 scripts/search_google_drive.py --terms "pdf" --format table

# Search by category
python3 scripts/search_google_drive.py --terms "tax" --category tax --format table
```

### Test BigStore Search  
```bash
# Search local files
python3 scripts/search_bigstore.py --terms "passport" --format table

# Search specific paths
python3 scripts/search_bigstore.py --paths ~/Documents --terms "2023" --format table
```

### Test Unified Search
```bash
# Natural language queries
python3 scripts/unified_search.py "what is my SIN number"
python3 scripts/unified_search.py "find my 2023 tax return"
python3 scripts/unified_search.py "show me passport documents"
```

## Troubleshooting

### Google Drive Authentication Issues
```bash
# Clear saved tokens and re-authenticate
rm ~/.config/openclaw/google_drive_token.json
python3 scripts/search_google_drive.py --terms "test"
```

### Permission Errors
```bash
# macOS: Grant Full Disk Access to Terminal/OpenClaw
# System Preferences → Security & Privacy → Privacy → Full Disk Access

# Linux: Check file permissions
sudo chmod -R +r /path/to/documents
```

### Missing Dependencies
```bash
# Check if required packages are installed
python3 -c "import googleapiclient, google.auth"
python3 -c "import pdfplumber"  # Optional
```

### Performance Issues
For large document collections:

1. **Index specific directories** instead of entire home folder
2. **Use category filters** to narrow searches
3. **Limit file extensions** to reduce scan time
4. **Exclude cache directories** in the search script

### Content Search Not Working
If PDF content search fails:

1. **Check PDF text extraction:**
   ```bash
   python3 -c "import pdfplumber; print('pdfplumber available')"
   ```

2. **Try alternative extraction:**
   ```bash
   pdftotext sample.pdf -
   ```

3. **Check file permissions** on PDF files

## Security Considerations

### Google Drive Access
- The OAuth token provides **read-only** access to your Google Drive
- Token is stored locally in `~/.config/openclaw/`
- Revoke access anytime from [Google Account settings](https://myaccount.google.com/permissions)

### Local File Access
- Scripts only read file metadata and content
- No files are modified or moved
- Search history is not logged
- Consider encrypting sensitive document directories

### Family Privacy
- Be mindful when sharing search results
- Configure family member patterns appropriately
- Consider separate searches for different family members' documents