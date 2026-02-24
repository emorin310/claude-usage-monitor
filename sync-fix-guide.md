# iCloud + Google Drive Sync Conflict Fix

## Diagnosis Summary
- **Issue**: iCloud Desktop & Documents sync is enabled but only 8KB synced (should be 1GB+)
- **Cause**: Google Drive activity in Documents folder interferes with iCloud sync
- **Evidence**: `.tmp.drivedownload` folder, sync-up status stuck

## Recommended Solution: Disable iCloud Desktop & Documents

### Steps:

1. **System Settings → Apple ID → iCloud**
2. Click **iCloud Drive → Options**
3. **Uncheck "Desktop & Documents Folders"**
4. **Choose** "Keep a Copy on This Mac" when prompted

This will:
- Stop the sync conflict loop
- Keep all files locally
- Let Google Drive be your primary cloud sync
- Free up iCloud storage

### Alternative: Keep iCloud but exclude Google Drive temp folders

If you want to keep iCloud Desktop & Documents:

1. Move Google Drive downloads OUT of Desktop/Documents
2. In Google Drive settings, change download location to `~/Downloads` or `~/Google Drive/Downloads`
3. Restart both Google Drive and iCloud sync

## Verification After Fix:

```bash
# Check iCloud sync size (should be 0 if disabled)
du -sh ~/Library/Mobile\ Documents/com~apple~CloudDocs/

# Check for remaining Google Drive temp folders
find ~/Desktop ~/Documents -name ".tmp.drivedownload" -o -name ".tmp*"

# Monitor iCloud status
brctl status | head -40
```

## Notes:
- Google Drive alone is sufficient for Desktop/Documents backup
- Saves iCloud storage quota
- Eliminates sync conflicts
- Improves battery/CPU (one less sync engine running)
