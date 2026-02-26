# Interactive Org Chart Tool - Implementation Plan

**Project:** Build an interactive, web-based org chart with expand/collapse, inline editing, drag-to-move, import/export capabilities.

**Target:** Option 2 - Web-based interactive HTML/JS solution
**Status:** Planning Phase
**Created:** 2026-02-25

---

## 1. Project Overview

### Purpose
Replace static Excalidraw org charts with a **fully interactive, browser-based org chart tool** that allows:
- **Hierarchical navigation** - Expand/collapse employee trees
- **Direct editing** - Click to edit names, titles, departments
- **Spatial manipulation** - Drag boxes to reposition
- **Data portability** - Import from text/CSV, export to PDF/JSON
- **Real-time rendering** - No plugins or external dependencies required

### Success Criteria
✅ All 4 core features working (expand/collapse, edit, move, import/export)
✅ Responsive design (desktop first, tablet-friendly)
✅ Instant visual feedback for all interactions
✅ Clean, intuitive UI (no learning curve)
✅ PDF export maintains color coding and hierarchy
✅ Can handle 50+ employees without performance issues

---

## 2. Technical Stack

### Frontend
- **HTML5 Canvas** or **SVG** (for rendering org boxes and connections)
  - *Decision: SVG* — Better for interactive elements, easier styling, text selection
- **Vanilla JavaScript** (no jQuery, no heavy frameworks)
  - Or **Preact** if state management becomes complex
- **CSS3** for styling and animations
- **D3.js** (optional) — for automatic layout if needed, otherwise custom layout engine

### Data Structure
- **JSON** as primary format (easy to import/export)
- **CSV support** for import (parse text table)
- **Hierarchical tree** with parent-child relationships

### Export
- **PDF**: Use **jsPDF** + **html2canvas** OR **pdfkit**
- **JSON**: Native stringify
- **PNG/SVG**: Canvas export or SVG snapshot

### Libraries (Minimal)
```
- svg.js (15KB) — SVG manipulation
- jsPDF (150KB) — PDF export
- papaparse (10KB) — CSV parsing
```

**Total footprint: ~400KB** (highly optimized, one-page load)

---

## 3. Feature Breakdown

### 3.1 Expand/Collapse Trees
```
Logic:
- Each node stores: { id, name, title, dept, manager, children: [], isExpanded: true }
- On toggle: Update isExpanded flag → Re-render subtree
- Animation: Slide-in/slide-out effect (CSS transition 200ms)
- Indicator: Triangle/chevron icon next to names with children
```

**Behavior:**
- Click chevron to toggle expand/collapse
- Collapsed nodes show "3 more..." count
- Smooth animation between states

### 3.2 Inline Editing
```
Logic:
- Double-click on box → Enable edit mode
- Fields editable: Name, Title, Department
- Save on blur or Enter key
- Undo/redo support (last 20 actions)
```

**UI:**
- Highlight box when in edit mode
- Text input appears in-place
- Color-coded by department (preserved during edit)

### 3.3 Drag-to-Move Boxes
```
Logic:
- Mouse down on box → Enter drag mode
- Mouse move → Update box position (x, y coordinates)
- Mouse up → Finalize position, save layout state
- Optional: Snap-to-grid (20px grid for cleanliness)
- SVG handles positioning via transform: translate()
```

**Behavior:**
- Cursor changes to grab hand on hover
- Connection lines update in real-time
- Edges highlight when dragging near boundaries

### 3.4 Import from Text
```
Supported formats:
1. CSV Table (as provided)
   - Columns: First Name | Last Name | Department | Job Title | Manager
   - Auto-parse and build hierarchy

2. JSON (flat array)
   - Array of objects with relationships

3. Plain text (copy-paste)
   - Name\nTitle\nDepartment\nManager format
```

**Process:**
- User clicks "Import"
- Paste text/upload file
- Preview parsed data
- Auto-build tree hierarchy by matching managers to names
- Confirm and load

### 3.5 Export to PDF
```
Logic:
- Serialize current layout + colors
- Render to canvas (high-DPI: 300px)
- Export as PDF with page breaks for large orgs
- Preserve: Colors, hierarchy, names, titles
```

**Features:**
- Single page or multi-page (auto-detect)
- A4/Letter sizing
- Color preservation
- Optional: Include legend (department colors)

### 3.6 Additional Features
- **Undo/Redo** - Keyboard shortcuts (Ctrl+Z / Ctrl+Y)
- **Search** - Filter by name, department, title
- **Export JSON** - Save state for later editing
- **Print to HTML** - Simple print layout
- **Dark mode toggle** (nice to have)

---

## 4. UI/UX Design

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│  📊 Org Chart Tool                          [?] [⚙️]  [≡]   │
├─────────────────────────────────────────────────────────────┤
│ [Import] [Export PDF] [Export JSON] [Undo] [Redo] [Search]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│                    ┌─────────────────┐                       │
│                    │  Chris van H.   │ (Blue - Office)       │
│                    │ General Manager │                       │
│                    └────────┬────────┘                       │
│                             │                                │
│         ┌───────────────────┼───────────────────┐            │
│         │                   │                   │            │
│    ┌────▼────┐      ┌──────▼──────┐     ┌─────▼────┐       │
│    │ Nathan  │      │  Tina Park  │     │ Adam W.  │       │
│    │  Elgie  │      │ Office Mgr  │     │ Sales &  │       │
│    │Ops Mgr  │      └─────────────┘     │ Relations│       │
│    └────┬────┘                          └────┬─────┘       │
│         │                                    │              │
│    ┌────┴──────┬──────────┐          ┌──────▼──────┐       │
│    ▼ (4 more) │ [+5 hide]│          │   [+2 hide] │       │
│               │          │          │             │       │
└─────────────────────────────────────────────────────────────┘

Drag to move • Double-click to edit • Click ▶ to expand
```

### Color Scheme
- **Office** — #ADD8E6 (Light Blue)
- **Plumbing** — #90EE90 (Light Green)
- **General Contracting** — #FFB347 (Light Orange)
- **HVAC** — #FFB6C6 (Light Pink)
- **Hydronics** — #DDA0DD (Light Purple)

### Box Design
```
┌──────────────────────────────┐
│ ▶ Chris van Herksen         │  ← Chevron (if children)
│   General Manager            │
│   Office | Manager           │  ← Dept | Role (small text)
└──────────────────────────────┘
```
Hover state: Slight shadow/outline, cursor changes to grab

---

## 5. Data Structure (JSON Schema)

```json
{
  "organization": {
    "name": "Company Name",
    "lastUpdated": "2026-02-25T19:30:00Z",
    "employees": [
      {
        "id": "cvh_001",
        "firstName": "Chris",
        "lastName": "van Herksen",
        "title": "General Manager",
        "department": "Office",
        "managerId": null,
        "position": { "x": 500, "y": 50 },
        "isExpanded": true
      },
      {
        "id": "ne_001",
        "firstName": "Nathan",
        "lastName": "Elgie",
        "title": "Operations Manager",
        "department": "Office",
        "managerId": "cvh_001",
        "position": { "x": 300, "y": 150 },
        "isExpanded": false
      }
    ]
  }
}
```

---

## 6. Implementation Phases

### Phase 1: Core Rendering (Week 1)
- [ ] SVG canvas setup
- [ ] Parse employee data (JSON input)
- [ ] Render boxes with hierarchy
- [ ] Draw connection lines
- [ ] Color-coding by department

**Deliverable:** Static org chart on page

### Phase 2: Interactivity (Week 2)
- [ ] Expand/collapse toggle (with animation)
- [ ] Drag-to-move functionality
- [ ] Inline editing (name, title)
- [ ] Undo/redo stack

**Deliverable:** Fully interactive, editable chart

### Phase 3: Import/Export (Week 3)
- [ ] CSV import parser
- [ ] JSON import/export
- [ ] PDF export (jsPDF integration)
- [ ] File upload UI

**Deliverable:** Complete data portability

### Phase 4: Polish & Testing (Week 4)
- [ ] Responsive design (tablet)
- [ ] Keyboard shortcuts (Ctrl+Z, etc.)
- [ ] Search/filter functionality
- [ ] Performance optimization (50+ employees)
- [ ] Cross-browser testing

**Deliverable:** Production-ready tool

---

## 7. File Structure

```
/home/magi/clawd/projects/org-chart-tool/
├── index.html                 # Main entry point
├── css/
│   ├── styles.css            # Core styling
│   └── themes.css            # Dark mode, color schemes
├── js/
│   ├── app.js                # Main controller
│   ├── orgchart.js           # Chart rendering engine
│   ├── editor.js             # Edit mode handlers
│   ├── dragdrop.js           # Drag/move logic
│   ├── io.js                 # Import/export (CSV, JSON, PDF)
│   └── utils.js              # Helper functions
├── lib/
│   ├── svg.min.js            # SVG library
│   ├── jspdf.min.js          # PDF export
│   └── papaparse.min.js      # CSV parsing
├── data/
│   ├── sample.json           # Sample org data
│   └── sample.csv            # Sample CSV import
├── README.md                 # Documentation
└── package.json              # Dependencies (if using npm)
```

---

## 8. Mockup/Wireframe

### Desktop View (1920x1080)
```
┌──────────────────────────────────────────────────────────────────────┐
│ Org Chart Tool v1.0                    [?] [⚙] [🌙] [≡]             │
├──────────────────────────────────────────────────────────────────────┤
│ [📥 Import] [📤 Export PDF] [💾 Export JSON] [↶ Undo] [↷ Redo]      │
│ [🔍 Search by name/dept...]                                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│                   ┌───────────────────────┐                          │
│                   │   Chris van Herksen   │ ← Blue (Office)          │
│                   │   General Manager     │                          │
│                   │   Office | Executive  │                          │
│                   └───────────┬───────────┘                          │
│                               │                                       │
│              ┌────────────────┼────────────────┐                     │
│              │                │                │                     │
│         ┌────▼─────┐   ┌─────▼────┐   ┌──────▼─────┐               │
│         │ Nathan   │   │ Tina     │   │ Adam       │               │
│         │ Elgie    │   │ Park     │   │ Weller     │               │
│         │ Ops Mgr  │   │ Office M │   │ Sales &    │               │
│         │Office    │   │ Office   │   │ Relations  │               │
│         └────┬─────┘   └────┬─────┘   │ Office     │               │
│              │              │         └──────┬─────┘               │
│         ┌────┴────┐    ┌────▼────┐         │                      │
│         │ [+4 ▼] │    │ [+ 4▼]  │    ┌────▼────┐                 │
│         └─────────┘    └─────────┘    │ [+2▼]  │                 │
│                                        └────────┘                 │
│                                                                        │
│  Legend: [Blue] Office  [Green] Plumbing  [Orange] Contracting       │
│          [Pink] HVAC    [Purple] Hydronics                           │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘
```

### Mobile View (375x667)
```
┌────────────────────────────────┐
│ Org Chart         [≡]          │
├────────────────────────────────┤
│ [📥] [📤] [↶] [↷]             │
│ [🔍 Search...]                 │
├────────────────────────────────┤
│                                │
│     ┌──────────────────┐      │
│     │ Chris van Herksen│      │
│     │ General Manager  │      │
│     │ Office           │      │
│     └────────┬─────────┘      │
│              │                │
│         ┌────┴────────┐       │
│         ▼             ▼       │
│    ┌─────────┐  ┌─────────┐  │
│    │ Nathan  │  │ Tina    │  │
│    │ Elgie   │  │ Park    │  │
│    │ Ops Mgr │  │ Off Mgr │  │
│    └─────────┘  └─────────┘  │
│                               │
└────────────────────────────────┘
```

---

## 9. Key Algorithms

### 9.1 Hierarchy Building
```
Input: Flat array of employees with manager IDs
Output: Tree structure with parent-child relationships

Algorithm:
1. Create a map: managerId → [children]
2. Find root (no manager)
3. Recursively build tree by following manager relationships
4. Set isExpanded based on saved state (from localStorage)
```

### 9.2 Auto-Layout (if not manual positioning)
```
Algorithm: Hierarchical tree layout (Reingold-Tilford)
1. Calculate width of subtrees recursively
2. Position children evenly below parent
3. Offset by accumulated width
4. Adjust vertical spacing based on tree depth

Result: Balanced, visually pleasing hierarchy
```

### 9.3 Line Routing
```
Draw connections:
- Start: Bottom center of parent box
- End: Top center of child box
- Path: Cubic Bezier curve (SVG path)
- Color: Fade to lighter shade of parent's department color
- Animation: Animate on expand (line grows)
```

---

## 10. Development Tips

### State Management
Use a single **state object** to track:
- Org data (employees, relationships)
- UI state (expanded nodes, selected node, edit mode)
- Layout (box positions)
- History (undo/redo stack)

```javascript
const state = {
  org: { employees: [...] },
  ui: { expandedNodes: new Set(), selectedId: null, editMode: null },
  layout: { positions: {} },
  history: []
};
```

### Event Handling
Use event delegation on SVG:
```javascript
svg.addEventListener('click', (e) => {
  if (e.target.classList.contains('expand-toggle')) handleExpand(e);
  if (e.target.classList.contains('org-box')) handleSelect(e);
});
```

### Persistence
Save state to **localStorage** after each change:
```javascript
localStorage.setItem('orgChartState', JSON.stringify(state));
```

Load on startup:
```javascript
const saved = localStorage.getItem('orgChartState');
if (saved) state = JSON.parse(saved);
```

---

## 11. Testing Checklist

- [ ] 50 employees load without lag
- [ ] Expand/collapse smooth and instant
- [ ] Drag repositioning works on touch devices
- [ ] PDF export maintains color, hierarchy, readability
- [ ] CSV import parses complex names correctly
- [ ] Search filters by name, title, department
- [ ] Undo/redo works correctly (20 action stack)
- [ ] Responsive at 375px, 768px, 1920px widths
- [ ] Safari, Chrome, Firefox, Edge compatible
- [ ] Keyboard shortcuts work (Ctrl+Z, Ctrl+Y, Ctrl+S)

---

## 12. Estimated Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1: Rendering | 5-7 days | Not started |
| Phase 2: Interactivity | 5-7 days | Not started |
| Phase 3: Import/Export | 3-5 days | Not started |
| Phase 4: Polish | 3-5 days | Not started |
| **Total** | **~3-4 weeks** | |

---

## 13. Success Metrics

- ✅ Tool loads in <2 seconds
- ✅ All interactions responsive (<100ms)
- ✅ PDF exports are pixel-perfect
- ✅ No console errors
- ✅ User can accomplish core tasks in <5 clicks
- ✅ Can handle 100+ employees without performance degradation

---

## Appendix: Sample Import CSV

```csv
First Name,Last Name,Department,Job Title,Manager
Chris,van Herksen,Office,General Manager,
Nathan,Elgie,Office,Operations Manager,Chris van Herksen
Tina,Park,Office,Office Manager,Chris van Herksen
Adam,Weller,Office,Sales & Client Relations,Chris van Herksen
Faith,Schoenemann,Office,Marketing / Operations Coordinator,Adam Weller
Marissa,Schoenemann,Office,Key Account Manager,Adam Weller
Jeff,Skinner,Office,Plumbing Field Supervisor,Nathan Elgie
...
```

---

**Next Step:** Start Phase 1 when approved. Recommend: Create index.html skeleton + SVG setup first.
