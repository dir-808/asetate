# Asetate

A local-first DJ library manager for vinyl collectors. Syncs with Discogs, adds DJ-specific metadata (crates, BPM, playable tracks), and exports to CSV for label printing.

## Project Goals
- FOSS release (choose license: MIT or GPLv3)
- Discogs API integration for collection sync
- SQLite storage, no external database needed
- Crate and track-level organization
- CSV export for label printing workflows

## Tech Stack
- Python / Flask (or FastAPI)
- SQLite
- Minimal frontend (HTML/JS or lightweight framework)

## Discogs API
- Docs: https://www.discogs.com/developers
- User token stored in .env

## Contribution
- Keep dependencies minimal
- Document setup clearly in README
- Use environment variables for all config

---

## UI/UX Guidelines

### Design Philosophy: MPC2000 Aesthetic
Asetate channels the **Akai MPC2000** vibe - utilitarian, tactile, and unmistakably retro-digital. Think hardware sampler interfaces: LCD screens, chunky buttons, grid layouts, and immediate visual feedback. No unnecessary decoration - every element serves a function.

Key principles:
- **Hardware-inspired**: UI should feel like operating physical equipment
- **High contrast**: Clear distinction between active/inactive states
- **Grid-based**: Aligned, structured layouts like hardware button grids
- **Immediate feedback**: Actions show results instantly, no ambiguity
- **Functional density**: Pack information efficiently without clutter

### Color System

| Purpose | Color | CSS Variable | Usage |
|---------|-------|--------------|-------|
| Primary/Interactive | Orange `#F97316` | `--primary` | Buttons, links, playable highlights, active states |
| Success/Playable | Green `#22C55E` | `--success` | Playable counts, positive states |
| Warning/Notes | Amber `#FBBF24` | `--warning` | Notes indicators, caution states |
| Error | Red `#EF4444` | `--error` | Errors, high energy level |
| Borders/Muted | Grey | `--border` | Inactive borders, separators, dimmed elements |
| LCD Background | Dark green-tinted | `--lcd-bg` | Info cards, release metadata sections |
| LCD Text | Light green | `--lcd-text` | Text on LCD-style backgrounds |

**Orange = interactive/playable.** This is the primary accent. If something is clickable, toggleable, or "active", it gets orange treatment.

### Typography
- **Monospace everywhere** for that digital/hardware feel (`--font-mono`)
- Uppercase for labels and section headers (letter-spacing: 0.05-0.1em)
- Tabular numerals for BPM, counts, durations (`font-variant-numeric: tabular-nums`)
- Small, efficient text sizes - don't waste screen real estate

### Component Patterns

#### Buttons
- Use `align-items: stretch` in button groups so all buttons match height
- Discogs actions grouped separately from Asetate actions (with border divider)
- Small buttons (`btn-sm`) for most actions
- Primary (orange) for main actions, Secondary (grey) for supporting actions

```css
.action-group {
    display: flex;
    gap: var(--space-xs);
    align-items: stretch;
}
```

#### Borders
- **1px borders only** - consistent thickness throughout
- Grey (`--border`) for inactive/structural borders
- Orange for interactive/selected/playable elements
- **Never add/remove borders dynamically** - only change colors (prevents layout shift)
- 2px borders only for major containers (cards, panels, modals)

#### Track Highlighting (Playable Sections)
The playable track border system uses a specific pattern to create orange "boxes" around playable tracks without causing layout shifts:

```css
/* Base: all tracks have left/right/bottom borders (grey), first-child also has top */
/* Playable: change left/right to orange, add subtle background */
/* Orange top edge: change BOTTOM border of preceding non-playable to orange */
/* Orange bottom edge: change bottom of last playable in group to orange */
/* Grey lines between adjacent playable tracks stay grey */
```

Key rule: **Only change border colors, never add/remove borders.** Use `:has()` selector to style elements based on what follows them.

#### Cards & Panels
- Cards: 2px border, grid layout for covers + info
- Info sections use LCD-style background (`--lcd-bg`)
- Info sections should `flex: 1` to fill remaining space (no gaps)

#### Sidebar Panel (Master-Detail Pattern)
The sidebar panel pushes content rather than overlaying. Key implementation details:

**Grid items must NOT resize when panel opens:**
```css
/* BAD: items stretch to fill, causing resize on panel open */
grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));

/* GOOD: items have fixed max-width, only reflow (wrap) on panel open */
grid-template-columns: repeat(auto-fill, minmax(160px, 200px));
```

**Panel animation approach:**
- Panel slides with `transform: translateX()` (GPU-accelerated, no layout reflow)
- Main content uses `margin-right` transition to make room
- Items reflow (fewer per row) but don't individually resize

**State management:**
- URL reflects selection (`?r=releaseId`) for browser back/forward
- Clear old panel content before loading new (prevent stale data/buttons)
- Use `panelContent.querySelector()` not `document.getElementById()` to find elements in freshly loaded AJAX content

Reference: [Every Layout - Sidebar](https://every-layout.dev/layouts/sidebar/)

#### Inputs & Forms
- Minimal styling - transparent background until hover/focus
- 1px border on focus (orange)
- Monospace font for data entry (BPM, Key, etc.)
- Debounced auto-save (no explicit save buttons where possible)

#### Energy Bars
- 5-segment horizontal bar
- Click AND drag to set value
- Color progression: green → lime → yellow → orange → red
- Use global state pattern for drag handling across AJAX-loaded content

#### Navigation Bar

The nav bar should feel like the MPC's top control panel - a functional toolbar, not a decorative header.

**Structure:**
```
[Brand/Logo] | [Main Nav Links] | [User/Settings]
```

**Styling approach:**
- Subtle panel depth via border colors (light top edge, dark bottom edge)
- Nav links styled as chunky rectangular "buttons" (generous padding, uppercase, letter-spacing)
- Active state: orange text + LED indicator dot (small colored circle)
- Hover state: subtle background change, no shadows
- Keep brand simple - solid orange text, no glow effects

**LED indicator pattern:**
```css
.nav-link.active::after {
    content: '';
    position: absolute;
    bottom: 4px;
    left: 50%;
    transform: translateX(-50%);
    width: 6px;
    height: 6px;
    background: var(--primary);
    border-radius: 50%; /* Only rounded element allowed - mimics actual LED */
}
```

**Why rounded LED is OK:** Physical LEDs are round. This is the one exception to "no rounded corners" because it mimics actual hardware indicators.

#### Settings Page

Settings should feel like the MPC's "GLOBAL PROGRAM" or "MIDI/SYNC" parameter screens - organized banks of labeled parameters.

**Structure:**
- Grouped sections (cards) for related settings
- Each section has a clear header (uppercase, letter-spacing, border below)
- Form inputs styled as LCD-like fields (subtle inset shadow)
- Toggle switches as chunky buttons with LED indicators

**Section headers:**
```css
.settings-section-header {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding-bottom: var(--space-sm);
    border-bottom: 2px solid var(--border);
    margin-bottom: var(--space-md);
}
```

**Toggle switches:**
- Rectangular buttons (not pill-shaped iOS toggles)
- LED dot that "lights up" green when active
- Text label inside the button
- Press effect via inset shadow on active state

```css
.toggle-switch {
    padding: var(--space-sm) var(--space-md);
    border: 2px solid var(--border);
    background: transparent;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: var(--space-sm);
}

.toggle-switch.active {
    border-color: var(--success);
}

.toggle-switch .led {
    width: 8px;
    height: 8px;
    background: var(--border);
    border-radius: 50%;
}

.toggle-switch.active .led {
    background: var(--success);
}
```

**Collapsible sections:**
- Use `<details>/<summary>` elements
- Style summary as a clickable row with rotation indicator
- Don't animate height (layout property) - use opacity transitions if needed
- Consider these as "parameter pages" like MPC's SHIFT+page navigation

### Interaction Patterns

#### Hover States
- Subtle background color change
- Border color intensification (not addition)
- `transition: 0.15s` for smooth but snappy feedback

#### Toggle/Selection
- Immediate visual feedback before API response
- Dimmed state (`opacity: 0.5`) for inactive/non-playable
- No "saving..." indicators - trust the auto-save

#### Panels & Navigation
- Sidebar panel pushes content, doesn't overlay
- URL reflects current selection (`?r=releaseId`)
- Browser back/forward works correctly
- Clear old state when loading new content (prevent stale data)

### Spacing
Use CSS variables consistently:
- `--space-xs`: 4px - tight gaps (between related items)
- `--space-sm`: 8px - standard component padding
- `--space-md`: 16px - section spacing
- `--space-lg`: 24px - major section breaks
- `--space-xl`: 32px - page-level spacing

### Future Enhancement Ideas (MPC2000 Vibe)

1. **Pad Grid View**: Display crates/releases as a grid of pads (like MPC pads), clickable with visual feedback
2. **LCD Display Component**: Dedicated component for key info display with that classic LCD look (scanlines optional)
3. **Transport Controls**: Play/cue visual metaphors for export/print actions
4. **Bank/Program Selectors**: A-H, 1-16 style navigation for browsing large collections
5. **Waveform Hints**: Subtle visual indication of track energy/intensity
6. **Tactile Button Shadows**: Inset shadows to make buttons feel "pressable" *(see "Shadows: Functional vs Decorative" section)*
7. **LED Indicators**: Small colored dots for status (synced, has notes, in crate) *(pattern documented in Navigation Bar & Settings Page sections)*
8. **Flip/Reverse Animations**: Page transitions that feel like changing LCD screens
9. **Click Sounds**: Optional subtle UI sounds for that hardware feedback feel
10. **Keyboard Shortcuts**: Power-user shortcuts displayed in a hardware-manual style

### Animation & Performance

**Only animate `transform` and `opacity`** - these are GPU-accelerated and don't trigger layout reflow.

```css
/* BAD: triggers layout reflow every frame */
.panel { transition: margin-left 0.3s; }
.element { transition: width 0.3s, height 0.3s; }

/* GOOD: GPU-accelerated, no reflow */
.panel { transition: transform 0.3s; }
.element { transition: opacity 0.15s; }
```

**Avoid animating:** `width`, `height`, `margin`, `padding`, `top/left/right/bottom`, `font-size`, `border-width`

**Use `will-change` sparingly** for elements you know will animate:
```css
.release-panel { will-change: transform; }
```

**Transitions:** Keep to 0.15s for micro-interactions, 0.3s max for larger movements.

Reference: [MDN - CSS/JS Animation Performance](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/CSS_JavaScript_animation_performance)

### Shadows: Functional vs Decorative

The MPC2000 has physical depth - raised buttons, recessed LCD screens, beveled panel edges. We can use shadows to recreate this tactile feel, but must distinguish:

**Functional shadows (allowed):**
```css
/* Inset shadow for "recessed screen" effect on inputs/displays */
.lcd-input {
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.2);
}

/* Subtle depth on nav/toolbar containers */
.nav-container {
    border-top: 1px solid rgba(255,255,255,0.05);
    border-bottom: 1px solid rgba(0,0,0,0.2);
}

/* Button press effect */
.btn:active {
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.3);
}
```

**Decorative shadows (avoid):**
```css
/* NO - ambient drop shadow for aesthetics */
.card { box-shadow: 0 4px 12px rgba(0,0,0,0.3); }

/* NO - glow effects for "pretty" */
.brand { text-shadow: 0 0 10px var(--primary); }

/* NO - multiple layered shadows */
.element { box-shadow: 0 2px 4px rgba(0,0,0,0.1), 0 8px 16px rgba(0,0,0,0.1); }
```

**Rule of thumb:** If the shadow mimics physical hardware depth (buttons, screens, panel seams), it's functional. If it's ambient/floating/glowing, it's decorative.

### Anti-Patterns (Avoid These)

**Visual:**
- Rounded corners (MPC is angular/rectangular)
- Decorative shadows (drop shadows, glows, ambient shadows)
- Thin/light fonts
- Animations longer than 0.3s

**Interaction:**
- Confirmation dialogs for reversible actions
- Loading spinners (prefer skeleton states or instant feedback)
- Tooltips for essential information
- Nested dropdowns or complex menus

**Technical:**
- Animating layout properties (`width`, `height`, `margin`, `padding`)
- Using `1fr` in grids where items shouldn't resize
- Adding/removing borders dynamically (change colors instead)
- `document.getElementById()` for elements in AJAX-loaded content
- Multiple elements with same ID (breaks getElementById reliability)
