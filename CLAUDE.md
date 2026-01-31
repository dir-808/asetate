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

## CSS Architecture

> ⚠️ **ALWAYS put CSS in `static/css/style.css`** - never in template `<style>` blocks. This ensures consistency, easier maintenance, and better caching.

### File Structure
- **`static/css/style.css`** - Single source of truth for ALL CSS
- Templates should have **no** `<style>` blocks (legacy ones are being migrated)

### Organization in style.css
style.css is organized into sections:
- **NAVIGATION** - Nav bar styles
- **BUTTONS** - All button variants
- **FORMS** - Inputs, selects, textareas
- **COLLECTION PAGE** - Grid, cards, filters
- **RELEASE DETAIL PAGE** - Track table, header layout
- **SIDE PANEL** - Panel positioning, content
- **SHARED COMPONENTS** - Components used across multiple pages

When adding new styles, find the appropriate section or create a new one.

### Naming Conventions
- **Base class**: `.component` (e.g., `.energy-bar`)
- **Size variants**: `.component--sm`, `.component--lg`
- **State variants**: `.component.active`, `.component.selected`

### Key Shared Components
These are used across multiple pages - changes apply everywhere:

| Component | Classes |
|-----------|---------|
| **Energy Bar** | `.energy-bar`, `.energy-bar--sm` |
| **Track Row Highlighting** | `.track-row.track-playable`, `.panel-track-row.track-dimmed` |
| **Action Groups** | `.action-group`, `.action-group--discogs` |
| **Crate Dropdown** | `.crate-dropdown`, `.crate-dropdown-wrapper` |
| **Notes Textarea** | `.notes-textarea`, `.notes-textarea--lg` |
| **Side Panel** | `.release-panel`, `.panel-header-bar`, `.panel-content` |

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

**Activity LED (blinking indicator for long-running operations):**
Use `.activity-led` for any button where the user waits for a process to complete. The LED is hidden by default and appears blinking when the button enters a loading state.

**When to use:**
- Sync operations (collection sync, inventory sync, release sync)
- Import/export operations
- Any async action that takes noticeable time

**When NOT to use:**
- Instant actions (Save, Cancel, Delete)
- Navigation (handled by nav link `.led` pattern)

```html
<button class="btn btn-secondary btn-sm" id="btn-sync">
    <span class="activity-led"></span>
    <span class="btn-text">Sync</span>
</button>
```

```css
/* Activity LED - hidden by default, shows blinking when loading */
.activity-led {
    display: none;
    width: 8px;
    height: 8px;
    background: currentColor;
    border-radius: 50%; /* LED dots mimic hardware */
    margin-right: var(--space-xs);
    animation: led-blink 0.6s ease-in-out infinite;
}

.btn.is-loading .activity-led {
    display: inline-block;
}

@keyframes led-blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}
```

**JavaScript pattern:**
```javascript
const btn = document.getElementById('btn-sync');
const btnText = btn.querySelector('.btn-text');

// Start loading - LED appears and blinks
btn.classList.add('is-loading');
btnText.textContent = 'Processing...';

// Stop loading - LED disappears
btn.classList.remove('is-loading');
btnText.textContent = 'Sync';
```

#### Borders
- **1px borders only** - consistent thickness throughout
- Grey (`--border`) for inactive/structural borders
- Orange for interactive/selected/playable elements
- **Never add/remove borders dynamically** - only change colors (prevents layout shift)
- 2px borders only for major containers (cards, panels, modals)

#### Track Highlighting (Playable Sections)
The playable track border system creates orange "boxes" around playable tracks. This pattern is shared between:
- **`.panel-track-row`** (sidebar) - the **blueprint**, uses `.track-dimmed` on non-playable
- **`.track-row`** (full release page) - uses `.track-playable` on playable

**Both must behave identically.** When updating one, update both.

```css
/* Base: all tracks have left/right/bottom borders (grey), first-child also has top */
/* Playable: change left/right to orange, add subtle background */
/* Orange top edge: change BOTTOM border of preceding non-playable to orange */
/* Orange bottom edge: change bottom of last playable in group to orange */
/* Adjacent playable tracks: use ::after pseudo-element for inset gray separator */
```

**Adjacent playable tracks fix:**
Gray separator between adjacent playable tracks uses a pseudo-element positioned inside the border box, so it doesn't overlap the orange side borders:

```css
.track-row.track-playable:has(+ .track-row.track-playable) {
    position: relative;
    border-bottom-color: transparent;
}

.track-row.track-playable:has(+ .track-row.track-playable)::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: var(--border);
}
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

**Discogs Card (clickable metadata section):**
The Discogs card groups release metadata and Discogs actions at the top of the sidebar panel. The entire card is clickable to navigate to the full release page.

Structure:
```html
<div class="panel-discogs-card" id="panel-discogs-card"
     data-href="{{ url_for('releases.view_release', release_id=release.id) }}">
    <header class="panel-header">
        <!-- Cover, title, artist, stats -->
    </header>
    <div class="panel-discogs-actions">
        <!-- Buttons with onclick="event.stopPropagation();" -->
        <a href="..." onclick="event.stopPropagation();">View</a>
        <button onclick="event.stopPropagation();">Sync</button>
    </div>
</div>
```

Styling:
```css
.panel-discogs-card {
    background-color: var(--lcd-bg);
    border: 2px solid var(--border);
    padding: var(--space-md);
    cursor: pointer;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3); /* Recessed LCD effect */
}

.panel-discogs-card:hover {
    border-color: var(--primary);
}

/* Text uses LCD colors */
.panel-discogs-card .panel-info h2,
.panel-discogs-card .panel-artist,
.panel-discogs-card .panel-meta,
.panel-discogs-card .panel-stats {
    color: var(--lcd-text);
}
```

JavaScript:
```javascript
const discogsCard = document.getElementById('panel-discogs-card');
if (discogsCard) {
    discogsCard.addEventListener('click', () => {
        window.location.href = discogsCard.dataset.href;
    });
}
```

Key points:
- Buttons inside must have `onclick="event.stopPropagation();"` to prevent card navigation
- Uses `data-href` attribute for the destination URL
- LCD-style background and text colors
- Orange border on hover indicates interactivity

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
- Active state: orange text + border + LED indicator lights up
- Hover state: subtle background change, no shadows
- Keep brand simple - solid orange text, no glow effects

**Nav link HTML structure:**
```html
<a href="/collection" class="active">
    <span class="led"></span>Collection
</a>
```

**LED indicator pattern:**
```css
/* Chunky rectangular nav buttons with LED indicator */
.nav-links a {
    display: inline-flex;
    align-items: center;
    gap: var(--space-sm);
    /* ... other styles */
}

/* LED indicator inside nav link - always visible */
.nav-links a .led {
    width: 8px;
    height: 8px;
    background: var(--border); /* Grey when inactive */
    border-radius: 50%; /* LEDs are round - mimics hardware */
}

/* Active state - LED lights up orange */
.nav-links a.active .led {
    background: var(--primary);
}
```

**Why inline LED (not ::after):** Consistent with toggle-btn and btn-led patterns. LED is part of the button content, not a decorative overlay. This makes it easier to maintain and keeps the visual language consistent across all MPC-style controls.

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
