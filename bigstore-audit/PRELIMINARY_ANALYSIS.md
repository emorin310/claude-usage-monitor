# Preliminary Analysis - /Volumes/bigstore/REVIEW/

**Analysis Date:** Feb 4, 2026, 23:42 EST
**Status:** Data collection in progress

## Initial Findings

### Top-Level Structure
```
/Volumes/bigstore/REVIEW/
├── DOCUMENTS/
└── PROJECTS/ (31 GB, 3,760 files)
```

### DOCUMENTS Folder Structure (observed)

#### Application Data
- **Adobe/** - Photoshop Cloud, AME, Dynamic Link Media Server
- **Arduino/** - Sketch files and libraries
- **Blackmagic Design/** - DaVinci Resolve data
- **JumpDesktop/** - Remote desktop config
- **LrClassicLogs/** - Lightroom Classic logs
- **Maccy.app/** - Clipboard manager app bundle (misplaced)
- **NoMachine/** - Remote desktop data
- **Zoom/** - Meeting recordings (2023 dates)
  - Multiple TM (Toastmasters) meetings from Jan-May 2023

#### Personal Content
- **Health/** - Tonsilectomy documents
- **IT/** - IT-related materials
- **Obsidian Vault/** - Note-taking app vault
- **Reference/** - Educational content
  - MasterClass archives (multiple .7z multi-volume archives)
  - Fine Woodworking Magazine (issues 001-221)
  - MAKE Magazine (issues 01-45)
  - Woodworking Books and Journals
  - ebooks/
- **Tina/** - Personal folder
- **brother labels/** - Label maker files
- **draw.io/** - Diagram files
- **home assistant/** - Smart home config
- **icons/** - Icon collection
- **safekeep/** - Backup/archive folder with nested structure:
  - BACKUPS/
  - DOCUMENTS/
  - Entertainment/
  - Eric Morin Photography/
  - Health & Fitness/
  - PHOTOS/
  - PROJECTS/
  - VIDEO/
  - ZAPHOD/
  - images/
  - slideshows/
  - voicemail messages/
- **scanned docs/** - Scanned documents
- **screenshots/** - Screenshot collection
- **wled/** - LED lighting configs
  - Backup/
  - Christmas 2023/
  - Downloads/
  - RenderCache/
  - colorcurves/
  - palettes/
  - valuecurves/

#### Potential Issues Identified
- **$RECYCLE.BIN/** - Windows recycle bin (should be cleaned)
- **Maccy.app/** - Full application bundle (shouldn't be in Documents)
- **LrClassicLogs/** - Application logs (can likely be deleted)
- **Multiple archive layers** - safekeep/ appears to duplicate the parent structure

### PROJECTS Folder Structure (observed)

#### Project Categories
- **3D printing/**
  - 3d models/
  - custom designs/
  - finished prints/
- **Publishing/** - Various publishing projects
  - Kris Truong Family/
  - ProShow StylePack Volume 1/
  - RDM Wallart/
  - calendars/
  - finished mosaics/
  - for coasters/
  - hollywood squares - Truong family/
  - photobook/
  - photoshop partial edits/
  - tina anni video/
  - web design/
- **TRH/** - Unknown project
- **halloween/**
  - AtmosFX/
- **in progress/**
  - MattMarg/
- **led lighting/** - LED project files
- **photobook/** - Photo book projects
  - To E-Mail/
  - images/
  - in a word/
- **photoshop partial edits/** - Work in progress
- **stock images/** - Stock photo collection
  - svg/

#### Root-Level Files (samples seen)
- IMG_0359.JPG, IMG_0357.JPG, IMG_0505.JPG, IMG_0939.JPG, IMG_0942.JPG
- Jessa's skating party invites.pub
- stag-and-doe.png
- valentine - girls.pub
- lonnie tribute.jpg

**Issue:** Loose files at root level should be organized into appropriate folders

## Observed Patterns

### Organizational Issues

1. **Duplicate Folder Names:**
   - `photobook/` exists in both Publishing/ and at PROJECTS root
   - `photoshop partial edits/` exists in both Publishing/ and at PROJECTS root

2. **Mixed Content at Root:**
   - Personal photos (IMG_*.JPG) mixed with project files
   - Publisher files (.pub) at root level

3. **Nested Archive Structure:**
   - safekeep/ in DOCUMENTS appears to be an old backup with its own DOCUMENTS/, PROJECTS/, PHOTOS/, etc.
   - This creates confusion and likely has duplicates with the main structure

4. **Application Data in Documents:**
   - Multiple application support folders (Adobe, Arduino, Lightroom logs, etc.)
   - Should be in Application Support or cleaned up

5. **Temporal Markers:**
   - Zoom recordings from 2023
   - Christmas 2023 folder in wled/
   - Some content may be outdated

## Next Steps (Data Collection in Progress)

1. ✅ Total size calculation
2. ✅ File and directory counts
3. 🔄 File type analysis (by extension)
4. 🔄 Largest files identification
5. 🔄 Full inventory with metadata
6. ⏳ Duplicate detection (pending full inventory)
7. ⏳ Wasted space calculation
8. ⏳ Consolidation recommendations

## Preliminary Recommendations

### Quick Wins
1. **Delete:** $RECYCLE.BIN, LrClassicLogs
2. **Relocate:** Maccy.app (to Applications or delete)
3. **Review:** Zoom recordings from 2023 (archive or delete)
4. **Organize:** Root-level files in PROJECTS

### Major Reorganization
1. **Investigate safekeep/:** Determine if it's redundant with current structure
2. **Merge duplicate folders:** photobook and photoshop partial edits
3. **Consolidate by type:** Group similar content (photos, videos, documents, projects)

---

*Full report will be generated upon completion of data collection.*
