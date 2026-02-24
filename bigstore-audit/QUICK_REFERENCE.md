# Quick Reference Card - bigstore/REVIEW Audit

## 📊 The Numbers
```
Total Size:     ~90-150 GB (estimated)
Files:          5,000+ analyzed
Directories:    100+
Duplicates:     38+ confirmed
Wasted Space:   5-20 GB recoverable
```

## 🔴 Critical Issue
**safekeep/ folder** - Nested backup duplicating entire structure
- **Impact:** 5-20 GB wasted space
- **Action:** Investigate → Compare → Delete

## 🎯 Top 5 Priorities

1. **Delete cruft** ($RECYCLE.BIN, LrClassicLogs) - 5 min, 100 MB
2. **Investigate safekeep/** - 30 min analysis
3. **Delete safekeep/** - 1 hour, 5-20 GB saved
4. **Merge PROJECTS duplicates** - 1 hour, 100-500 MB saved
5. **Clean 3D archive/** - 1 hour, 500 MB saved

## 📁 Main Structure
```
/Volumes/bigstore/REVIEW/
├── DOCUMENTS/ (~60-120 GB)
│   ├── safekeep/ ⚠️ DUPLICATE STRUCTURE
│   ├── Reference/ (MasterClass archives)
│   └── Zoom/ (2023 recordings)
└── PROJECTS/ (31 GB, 3,760 files)
    ├── 3D printing/ (6.4 GB)
    ├── Publishing/ (duplicates!)
    └── halloween/AtmosFX/ (17.6 GB)
```

## 💾 Largest Files
1. stormtroopers poolhouse.psd - 1.26 GB
2. IMG_0374-Edit-Edit.tif - 840 MB
3. IMG_0374-Edit-Edit.tif (dup) - 660 MB ⚠️

## 📄 File Types (Top 5)
1. Videos (MP4) - 17.6 GB
2. 3D Models (3MF/STL) - 6.4 GB
3. PDFs - 3.7 GB
4. Photoshop (PSD) - 3.3 GB
5. Photos (JPG/PNG) - 2.6 GB

## ⏱️ Time Investment
- Phase 1 (Quick cleanup): 1 hour → 100 MB
- Phase 2 (safekeep/): 2-3 hours → 5-20 GB ⭐
- Phase 3 (Dedup): 2-3 hours → 500 MB-1 GB
- Phase 4 (Reorganize): 4-6 hours → 0 GB
**Total: 10-12 hours → 5-22 GB recovered**

## ✅ Quick Wins (Do First)
```bash
# 1. Delete Windows recycle bin
trash /Volumes/bigstore/REVIEW/DOCUMENTS/\$RECYCLE.BIN/

# 2. Delete Lightroom logs
trash /Volumes/bigstore/REVIEW/DOCUMENTS/LrClassicLogs/

# 3. Delete temp Adobe folders
trash /Volumes/bigstore/REVIEW/DOCUMENTS/Adobe/amecommand/
trash /Volumes/bigstore/REVIEW/DOCUMENTS/Adobe/dynamiclinkmediaserver/
```

## 🔍 To Investigate
```bash
# Compare safekeep/ with main structure
cd /Volumes/bigstore/REVIEW/DOCUMENTS/
find safekeep/ -type f -exec md5 {} \; > ~/safekeep_hashes.txt
find . -maxdepth 3 -type f -not -path "*/safekeep/*" -exec md5 {} \; > ~/main_hashes.txt
comm -13 <(sort ~/main_hashes.txt) <(sort ~/safekeep_hashes.txt)
```

## 📚 Read These (In Order)
1. **README.md** - Overview of all files
2. **EXECUTIVE_SUMMARY.md** - High-level findings (5 min)
3. **AUDIT_REPORT.md** - Detailed report (20 min)
4. **FOLDER_STRUCTURE_TREE.txt** - Visual map

## ⚠️ Before You Start
1. ✅ Backup current state
2. ✅ Read reports
3. ✅ Start with Phase 1 (low risk)
4. ✅ Verify before deleting

## 💡 Pro Tips
- Use `trash` instead of `rm` (recoverable)
- Move files with `mv` not `cp` (avoid duplication)
- Work in phases, verify each step
- Keep backups until certain cleanup worked

## 🎁 Biggest Wins
1. **safekeep/ cleanup** → 5-20 GB
2. **3D archive/ cleanup** → 500 MB-1 GB
3. **PROJECTS dedup** → 100-500 MB
4. **Peace of mind** → Priceless

---

**Location:** ~/clawd-magi/bigstore-audit/
**Start:** Read EXECUTIVE_SUMMARY.md
**Questions:** Ask Magi anytime!
