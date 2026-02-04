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

## Local Development (VS Code)

The user runs the app locally using VS Code. When giving instructions, always provide VS Code-friendly guidance (GUI-based, not terminal commands).

### Running the App

1. Open the project folder in VS Code
2. Press **F5** (or click the green play button in "Run and Debug" sidebar)
3. App runs at `http://localhost:5001`
4. Press **Shift+F5** to stop

### Switching Branches

When the user wants to preview changes from a different branch:

1. Click the **branch name** in the bottom-left corner of VS Code
2. Select the branch from the dropdown (e.g., `claude/feature-name`)
3. If the branch doesn't appear, tell them to: **Ctrl+Shift+P** → "Git: Fetch" → then try again
4. After switching, press **F5** to run and test

### Workflow for Previewing Changes

When making changes for the user to review:

1. Push changes to a feature branch (e.g., `claude/feature-name-xyz`)
2. Tell the user to switch to that branch in VS Code (instructions above)
3. They can test locally before deciding to merge
4. If approved, create a PR or merge to main

### Important Notes

- **Port 5001**: The app runs on port 5001 (not 5000) to avoid macOS AirPlay conflict
- **User is not comfortable with terminal**: Always provide GUI-based instructions
- **.env file required**: The app needs a `.env` file with Discogs credentials to work

---

## CSS Architecture

> ⚠️ **ALWAYS put CSS in `static/css/style.css`** - never in template `<style>` blocks. This ensures consistency, easier maintenance, and better caching.

### Token-First Philosophy

> 🔥 **EVERYTHING IS A TOKEN. NO EXCEPTIONS (unless explicitly documented below).**
>
> This is the #1 rule of this codebase. Hardcoded values break the design system.

**CRITICAL RULE: Every CSS value MUST use a design token.**

If you're writing a CSS property that uses a numeric value, color, or dimension - it MUST be a token.

**Before writing any CSS, follow this decision tree:**

1. **Does a token exist for this value?** → Use it
2. **No token exists but I need this value?** → **Create a new token first**, then use it
3. **This is truly a one-off documented exception?** → Hardcode ONLY with a comment explaining why (see Exceptions below)

**Why "tokenize everything":**
- **Consistency**: Change `--space-md` once, update everywhere instantly
- **Maintainability**: No hunting through 5000+ lines of CSS for hardcoded `16px`
- **Intent**: `--opacity-disabled` communicates purpose, `0.4` doesn't
- **Future-proofing**: Entire UI can be adjusted from the :root section
- **Industry standard**: Tailwind, Material Design, IBM Carbon, Shopify Polaris all do this

**This is not over-engineering.** Every major design system in production follows this pattern.

**When adding new features:**
```css
/* WRONG - hardcoded values (NEVER do this) */
.new-component {
    padding: 16px;
    opacity: 0.5;
    z-index: 100;
    max-height: 250px;
    transition: opacity 0.15s;
}

/* RIGHT - tokens communicate intent and enable central updates */
.new-component {
    padding: var(--space-md);
    opacity: var(--opacity-dim);
    z-index: var(--z-sticky);
    max-height: var(--dropdown-max-height);
    transition: opacity var(--duration-base);
}

/* ADDING A NEW TOKEN when needed */
/* 1. First, add to :root in DESIGN TOKENS section */
:root {
    --my-new-height: 180px;  /* Component-specific height */
}
/* 2. Then use the token */
.new-component {
    height: var(--my-new-height);
}
```

### File Structure
- **`static/css/style.css`** - Single source of truth for ALL CSS
- Templates should have **no** `<style>` blocks (legacy ones are being migrated)

### Organization (CUBE CSS)
style.css is organized using the CUBE CSS methodology:

1. **DESIGN TOKENS** - CSS custom properties (colors, spacing, borders)
2. **COMPOSITION** - Layout primitives (navigation, grids, page structure)
3. **BLOCKS** - Component styles (buttons, cards, panels, forms)
4. **UTILITIES** - Single-purpose helpers (spacing, text, flex, display)
5. **EXCEPTIONS** - State variations (.is-loading, .has-error)

When adding new styles, find the appropriate CUBE layer and section within it.

### Design Tokens Quick Reference

> ⚠️ **CRITICAL: ALWAYS use design tokens. NEVER hardcode pixel values, colors, or sizes.**
>
> Before writing any CSS value, check if a token exists. If you need a value not covered by tokens, consider if it should be added as a new token.

#### Colors
| Token | Value | Usage |
|-------|-------|-------|
| `--primary` | #f97316 | Orange - interactive elements, playable |
| `--primary-hover` | #ea580c | Orange hover state |
| `--primary-dim` | #7c2d12 | Dimmed orange background |
| `--success` | #4ade80 | Green - positive states, playable counts |
| `--lime` | #84cc16 | Lime - energy level 2 |
| `--warning` | #fbbf24 | Amber - notes, caution |
| `--error` | #ef4444 | Red - errors, high energy |
| `--tag-default` | #E07A5F | Default tag color (terracotta) |
| `--color-none` | #e0e0e0 | "No color" option in color pickers |
| `--lcd-bg` | #0a1210 | LCD background |
| `--lcd-text` | #4ade80 | LCD text (bright green) |
| `--lcd-muted` | #52a872 | LCD secondary text (darker but readable) |
| `--lcd-dim` | #22543d | LCD decorative/dim text (low contrast) |
| `--border` | #2a2a2a | Standard border color |
| `--border-light` | #3a3a3a | Lighter border |

#### 3D Depth Colors (Button Edges)
| Token | Value | Usage |
|-------|-------|-------|
| `--primary-light` | #fb923c | Primary button light edge (top) |
| `--primary-dark` | #c2410c | Primary button dark edge (bottom) |
| `--primary-lighter` | #fdba74 | Primary hover light edge |
| `--primary-darker` | #9a3412 | Primary hover dark edge |
| `--error-light` | #f87171 | Danger button light edge (top) |
| `--error-dark` | #991b1b | Danger button dark edge (bottom) |
| `--error-lighter` | #fca5a5 | Danger hover light edge |
| `--error-darker` | #7f1d1d | Danger hover dark edge |
| `--neutral-light` | #525252 | Secondary button light edge (top) |
| `--neutral-dark` | #262626 | Secondary button dark edge (bottom) |
| `--neutral-lighter` | #6b7280 | Secondary hover light edge |
| `--neutral-darker` | #1f2937 | Secondary hover dark edge |

#### 3D Button Framework (Formula-based MPC-style beveled edges)

This framework uses alpha values with CSS calc() to create consistent 3D depth effects on ANY background color. Light source is top-left, so top/left edges get white overlay (highlight) and bottom/right edges get black overlay (shadow).

**Base Alpha Values (adjust these to tune all buttons at once):**
| Token | Value | Usage |
|-------|-------|-------|
| `--btn-3d-highlight` | 0.15 | White overlay intensity for light edges |
| `--btn-3d-shadow` | 0.25 | Black overlay intensity for dark edges |
| `--btn-3d-boost` | 0.08 | Additional depth on hover |
| `--btn-3d-press-alpha` | 0.25 | Press effect intensity |
| `--btn-3d-bg-hover` | 0.1 | Background lightening on hover |
| `--btn-3d-bg-hover-strong` | 0.15 | Stronger hover for dropdowns |

**Derived Edge Tokens (use these in components):**
| Token | Derived From | Usage |
|-------|--------------|-------|
| `--btn-3d-light-top` | highlight alpha | Top edge (normal) |
| `--btn-3d-light-left` | highlight alpha | Left edge (normal) |
| `--btn-3d-dark-bottom` | shadow alpha | Bottom edge (normal) |
| `--btn-3d-dark-right` | shadow alpha | Right edge (normal) |
| `--btn-3d-light-top-hover` | highlight + boost | Top edge (hover) |
| `--btn-3d-light-left-hover` | highlight + boost | Left edge (hover) |
| `--btn-3d-dark-bottom-hover` | shadow + boost | Bottom edge (hover) |
| `--btn-3d-dark-right-hover` | shadow + boost | Right edge (hover) |
| `--btn-press-shadow` | press alpha | Pressed top/left edges |
| `--btn-press-highlight` | press * 0.4 | Pressed bottom/right edges |
| `--btn-press-bg` | press * 0.2 | Pressed background |
| `--btn-hover-bg` | bg-hover alpha | Subtle hover background |
| `--btn-hover-bg-strong` | bg-hover-strong alpha | Stronger hover background |

**Usage pattern for 3D buttons:**
```css
.my-button {
    border-style: solid;
    border-width: var(--border-width-md);
    border-top-color: var(--btn-3d-light-top);
    border-left-color: var(--btn-3d-light-left);
    border-right-color: var(--btn-3d-dark-right);
    border-bottom-color: var(--btn-3d-dark-bottom);
}

.my-button:hover {
    background-color: var(--btn-hover-bg);
    border-top-color: var(--btn-3d-light-top-hover);
    border-left-color: var(--btn-3d-light-left-hover);
    border-right-color: var(--btn-3d-dark-right-hover);
    border-bottom-color: var(--btn-3d-dark-bottom-hover);
}

.my-button:active {
    border-top-color: var(--btn-press-shadow);
    border-left-color: var(--btn-press-shadow);
    border-right-color: var(--btn-press-highlight);
    border-bottom-color: var(--btn-press-highlight);
    background-color: var(--btn-press-bg);
}
```

**Choosing the right hover background:**

The press effect (`--btn-press-bg`) applies a consistent alpha darkening, but the *perceived* intensity depends on the hover state's starting point. Use this guide:

| Hover Token | When to Use |
|-------------|-------------|
| `--btn-hover-bg` | **Default choice.** Buttons that may have colored OR neutral backgrounds (e.g., crate buttons that change color when assigned). Keeps press effect feeling consistent across all states. |
| `--btn-hover-bg-strong` | Dropdown triggers or buttons that need more prominent hover feedback. |
| Solid color (e.g., `--border`) | **Avoid for 3D buttons.** Makes grey buttons feel heavier on press compared to colored buttons. Only use for non-3D components. |

**Why this matters:** A button starting from a dark solid hover (like `--border` #2a2a2a) will feel much darker when pressed than a button starting from a subtle overlay. Using alpha-based hover backgrounds ensures the press effect feels uniform regardless of the button's base color.

#### Discogs Brand Colors
| Token | Value | Usage |
|-------|-------|-------|
| `--discogs-bg` | #333333 | Discogs button background |
| `--discogs-bg-hover` | #444444 | Discogs button hover |
| `--discogs-border` | #444444 | Discogs button border |
| `--discogs-border-hover` | #555555 | Discogs button border hover |
| `--discogs-text` | #ffffff | Discogs button text |

#### Background Tints (Semi-transparent)
| Token | Value | Usage |
|-------|-------|-------|
| `--primary-bg-faint` | rgba(249,115,22,0.03) | Very subtle primary bg |
| `--primary-bg-subtle` | rgba(249,115,22,0.06) | Subtle primary bg |
| `--primary-bg-muted` | rgba(249,115,22,0.08) | Muted primary bg |
| `--primary-bg-light` | rgba(249,115,22,0.1) | Light primary bg |
| `--primary-bg-medium` | rgba(249,115,22,0.15) | Medium primary bg |
| `--primary-border-alpha` | rgba(249,115,22,0.4) | Semi-transparent primary border |
| `--success-bg-faint` | rgba(74,222,128,0.05) | Very subtle success bg |
| `--success-bg-light` | rgba(74,222,128,0.1) | Light success bg |
| `--success-bg-medium` | rgba(74,222,128,0.15) | Medium success bg |
| `--warning-bg-light` | rgba(251,191,36,0.1) | Light warning bg |
| `--warning-bg-medium` | rgba(251,191,36,0.15) | Medium warning bg |
| `--warning-bg-strong` | rgba(251,191,36,0.3) | Strong warning bg |
| `--error-bg-light` | rgba(239,68,68,0.1) | Light error bg |
| `--error-bg-medium` | rgba(239,68,68,0.2) | Medium error bg |
| `--overlay-light` | rgba(0,0,0,0.3) | Light overlay |
| `--overlay-medium` | rgba(0,0,0,0.5) | Medium overlay |
| `--overlay-heavy` | rgba(0,0,0,0.7) | Heavy overlay |
| `--overlay-strong` | rgba(0,0,0,0.8) | Strong overlay |
| `--lcd-dim-alpha` | rgba(34,84,61,0.5) | LCD dim at 50% |

#### Spacing (8pt grid)
| Token | Value | Usage |
|-------|-------|-------|
| `--space-2xs` | 2px | Fine detail: segment gaps, icon spacing |
| `--space-xs` | 4px | Tight: tag gaps, inline spacing |
| `--space-sm` | 8px | Standard: component padding, gaps |
| `--space-md` | 16px | Section: card padding, form groups |
| `--space-lg` | 24px | Major: section gaps, large padding |
| `--space-xl` | 32px | Page: main content padding |
| `--space-2xl` | 48px | Hero: dashboard spacing |

#### Borders
| Context | Width | Token |
|---------|-------|-------|
| Containers (cards, panels, buttons, modals) | 2px | `--border-width-md` |
| Internal (separators, inputs, table cells) | 1px | `--border-width-sm` |
| Accent/indicator borders | 3px | `--border-width-accent` |

#### Icon Sizes
| Token | Value | Usage |
|-------|-------|-------|
| `--icon-sm` | 14px | Crate badges on cards |
| `--icon-base` | 16px | Inline icons, dropdown emoji |
| `--icon-md` | 18px | Action buttons, inline icons |
| `--icon-lg` | 20px | Standalone icons, grid pickers |
| `--icon-xl` | 24px | Large icon display |
| `--icon-2xl` | 32px | Icon buttons, emoji grid items |
| `--icon-3xl` | 40px | Icon previews |
| `--icon-4xl` | 64px | Large icons, avatars |
| `--swatch-size` | 22px | Color picker swatches, small buttons |

#### Component Sizes
| Token | Value | Usage |
|-------|-------|-------|
| `--btn-sm-size` | 28px | Small square buttons |
| `--btn-discogs-width` | 40px | Discogs action button width |
| `--input-sm-width` | 36px | BPM/Key input fields |
| `--track-toggle-width` | 30px | Toggle checkbox area width |
| `--track-indent` | calc | Fields indentation (toggle + gap) |
| `--sidebar-width` | 450px | Release panel sidebar |
| `--crate-panel-width` | 420px | Crate edit panel |
| `--led-size` | 8px | LED indicator dots, scrollbar |
| `--led-size-sm` | 6px | Small LED indicators |

#### Toggle Sizes
| Token | Value | Usage |
|-------|-------|-------|
| `--toggle-width` | 44px | Standard toggle width |
| `--toggle-height` | 24px | Standard toggle height |
| `--toggle-thumb` | 16px | Toggle knob size |
| `--toggle-travel` | 20px | Knob travel distance |
| `--toggle-mini-width` | 28px | Mini toggle width |
| `--toggle-mini-height` | 16px | Mini toggle height |
| `--toggle-mini-thumb` | 10px | Mini toggle knob |
| `--toggle-mini-travel` | 12px | Mini knob travel |

#### Max-Width Constraints
| Token | Value | Usage |
|-------|-------|-------|
| `--max-width-page` | 1400px | Page content max width |
| `--max-width-narrow` | 600px | Narrow forms/pages (sync, settings) |
| `--max-width-sidebar` | 400px | Sidebar dropdowns, modals |
| `--max-width-card` | 280px | Card min-width |

#### Grid Card Sizing
| Token | Value | Usage |
|-------|-------|-------|
| `--grid-card-min` | 160px | Standard card min width |
| `--grid-card-max` | 200px | Standard card max width |
| `--grid-card-sm-min` | 130px | Small card min (responsive) |
| `--grid-card-sm-max` | 160px | Small card max (responsive) |
| `--grid-card-lg-min` | 200px | Large card min (crates) |
| `--grid-card-lg-max` | 260px | Large card max (crates) |
| `--grid-dashboard-min` | 180px | Dashboard card min |
| `--grid-dashboard-max` | 240px | Dashboard card max |
| `--grid-picker-min` | 32px | Color/emoji picker item |

#### Table Column Widths
| Token | Value | Usage |
|-------|-------|-------|
| `--col-pos-width` | 60px | Track position column |
| `--col-duration-width` | 70px | Duration column |
| `--col-field-width` | 80px | BPM, Key, Energy columns |
| `--col-playable-width` | 70px | Playable toggle column |
| `--col-title-min` | 200px | Minimum title column width |
| `--col-tags-min` | 150px | Minimum tags column width |

#### Energy Bar Sizes
| Token | Value | Usage |
|-------|-------|-------|
| `--energy-bar-height` | 18px | Standard energy bar height |
| `--energy-bar-sm-height` | 14px | Small energy bar height |
| `--energy-segment-width` | 14px | Energy segment width |
| `--energy-segment-sm-width` | 10px | Small energy segment |

#### Cover/Image Sizes
| Token | Value | Usage |
|-------|-------|-------|
| `--cover-lg` | 250px | Large cover (release detail) |
| `--cover-md` | 200px | Medium cover (responsive) |
| `--cover-sm` | 100px | Small cover (sidebar) |
| `--cover-xs` | 50px | Mini cover (list items) |

#### Font Sizes
| Token | Size | Usage |
|-------|------|-------|
| `--text-4xs` | 0.5rem | Extreme tiny (rare) |
| `--text-3xs` | 0.55rem | Micro labels, tiny tags |
| `--text-micro` | 0.6rem | Micro UI text |
| `--text-2xs` | 0.65rem | Tiny labels, badge text |
| `--text-xxs` | 0.7rem | Very small UI text |
| `--text-xs` | 0.75rem | Small text, badges |
| `--text-caption` | 0.8rem | Captions, stats |
| `--text-sm` | 0.85rem | Secondary text |
| `--text-body` | 0.9rem | Small body text, inputs |
| `--text-base` | 1rem | Body text |
| `--text-md` | 1.1rem | Slightly larger body |
| `--text-lg` | 1.125rem | Emphasis |
| `--text-subhead` | 1.2rem | Subheadings |
| `--text-heading` | 1.25rem | Small headings |
| `--text-xl` | 1.5rem | Headings |
| `--text-2xl` | 2rem | Page titles, large icons |

#### Letter Spacing
| Token | Value | Usage |
|-------|-------|-------|
| `--tracking-tight` | 0.02em | Dense text, position labels |
| `--tracking-normal` | 0.05em | Standard uppercase labels, buttons |
| `--tracking-wide` | 0.08em | Nav links, small caps |
| `--tracking-wider` | 0.1em | Section headings, emphasis |

#### Line Height (Leading)
| Token | Value | Usage |
|-------|-------|-------|
| `--leading-none` | 1 | Icons, single-line elements |
| `--leading-tight` | 1.2 | Compact text, headings |
| `--leading-snug` | 1.3 | Slightly tight text |
| `--leading-normal` | 1.5 | Standard readable text |
| `--leading-relaxed` | 1.6 | Body text, long-form reading |

#### Font Weights
| Token | Value | Usage |
|-------|-------|-------|
| `--weight-normal` | 400 | Normal/regular text |
| `--weight-medium` | 500 | Medium emphasis |
| `--weight-semibold` | 600 | Semi-bold, labels, buttons |
| `--weight-bold` | 700 | Bold, headings, strong emphasis |

#### Breakpoints
| Token | Value | Usage |
|-------|-------|-------|
| `--bp-sm` | 768px | Mobile/small screens |
| `--bp-md` | 900px | Tablets/medium screens |
| `--bp-lg` | 1100px | Small desktop |
| `--bp-xl` | 1200px | Large desktop |

> ⚠️ **Note**: CSS custom properties cannot be used in `@media` queries. These tokens serve as documentation and a single source of truth. When changing a breakpoint, update both the token AND the media query. Media queries include comments referencing their token (e.g., `/* --bp-md */`).

#### Z-Index Scale
| Token | Value | Usage |
|-------|-------|-------|
| `--z-base` | 0 | Base level, resets stacking |
| `--z-raised` | 1 | Slightly raised elements |
| `--z-above` | 5 | Above siblings (tabs, positioned) |
| `--z-dropdown` | 10 | Dropdowns, tooltips |
| `--z-popover` | 20 | Popovers, floating elements |
| `--z-fixed` | 50 | Fixed position elements |
| `--z-sticky` | 100 | Sticky headers, toolbars |
| `--z-overlay` | 900 | Overlays, side panels |
| `--z-modal` | 1000 | Modals, dialogs (highest) |

#### Shadows
| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-inset-sm` | inset 0 1px 2px rgba(0,0,0,0.2) | Light inset effect |
| `--shadow-inset` | inset 0 1px 2px rgba(0,0,0,0.3) | Standard pressed/inset |
| `--shadow-inset-lcd` | inset 0 1px 3px rgba(0,0,0,0.3) | LCD/recessed screen effect |
| `--shadow-edge` | 0 1px 0 rgba(0,0,0,0.2) | Bottom edge depth |
| `--shadow-focus` | 0 0 0 1px var(--primary-dim) | Focus ring (primary) |
| `--shadow-focus-success` | 0 0 0 1px var(--success) | Focus ring (success) |

#### Filters
| Token | Value | Usage |
|-------|-------|-------|
| `--filter-invert` | invert(1) | White icons on dark background |

#### Transition Durations
| Token | Value | Usage |
|-------|-------|-------|
| `--duration-fast` | 0.1s | Micro interactions, quick feedback |
| `--duration-base` | 0.15s | Standard transitions |
| `--duration-moderate` | 0.2s | Slightly longer animations |
| `--duration-slow` | 0.3s | Large movements, panels |
| `--duration-blink` | 0.6s | LED blink, activity indicators |
| `--duration-spin` | 1s | Spin/rotation animations |
| `--duration-pulse` | 2s | Slow pulse animations |

#### Transforms
| Token | Value | Usage |
|-------|-------|-------|
| `--scale-hover` | 1.1 | Standard hover scale effect |
| `--scale-hover-lg` | 1.2 | Larger hover scale effect |
| `--scale-hover-y` | 1.15 | Vertical scale (energy bars) |
| `--lift-hover` | -4px | Hover lift effect |
| `--lift-hover-lg` | -8px | Larger hover lift |
| `--tilt-crate-lid` | -75deg | Crate lid rotation |

#### Opacity
| Token | Value | Usage |
|-------|-------|-------|
| `--opacity-disabled` | 0.4 | Disabled buttons, inactive controls |
| `--opacity-dim` | 0.5 | Dimmed/inactive elements, separators |
| `--opacity-faded` | 0.6 | Slightly faded labels, secondary info |
| `--opacity-muted` | 0.7 | Muted text, hover states, loading |
| `--opacity-moderate` | 0.75 | Between muted and subtle |
| `--opacity-subtle` | 0.9 | Nearly full, subtle fade |

#### Constraints (Max/Min Dimensions)
| Token | Value | Usage |
|-------|-------|-------|
| `--header-offset` | 150px | Header + toolbar offset for layouts |
| `--dropdown-min-width` | 180px | Standard dropdown min-width |
| `--dropdown-lg-min-width` | 200px | Large dropdown min-width |
| `--dropdown-max-height` | 250px | Standard dropdown height |
| `--dropdown-lg-max-height` | 300px | Large dropdown height |
| `--textarea-min-height` | 60px | Minimum textarea height |
| `--textarea-max-height` | 100px | Maximum textarea height |
| `--textarea-base-height` | 80px | Standard textarea height |
| `--icon-grid-max-height` | 180px | Icon/emoji picker grid |
| `--icon-grid-sm-max-height` | 140px | Small icon grid |
| `--list-max-height` | 200px | Scrollable list sections |
| `--notes-compact-max-height` | 120px | Compact notes areas |
| `--modal-sm-max-height` | 120px | Small modal/content area |
| `--panel-loading-height` | 200px | Panel loading placeholder |
| `--notes-lg-height` | 250px | Large notes textarea |
| `--export-min-height` | 400px | Export preview min height |
| `--table-cell-max-width` | 200px | Table cell truncation |
| `--modal-panel-max-width` | 350px | Panel notes modal width |
| `--setting-max-width` | 500px | Toggle setting row width |
| `--crate-name-max-width` | 120px | Crate name in cards |
| `--energy-val-min-width` | 12px | Energy value display |

### Token Usage Rules

**DO:**
```css
/* Use spacing tokens */
padding: var(--space-md);
gap: var(--space-sm);

/* Use border tokens */
border: var(--border-width-sm) solid var(--border);

/* Use color tokens */
color: var(--error);
background: var(--lcd-bg);

/* Use size tokens */
width: var(--icon-xl);
max-width: var(--max-width-sidebar);

/* Use shadow tokens */
box-shadow: var(--shadow-inset-lcd);
box-shadow: var(--shadow-focus);

/* Use z-index tokens */
z-index: var(--z-modal);
z-index: var(--z-overlay);

/* Use transition duration tokens */
transition: opacity var(--duration-base) ease;
transition: transform var(--duration-slow) ease;

/* Use line-height tokens */
line-height: var(--leading-normal);
line-height: var(--leading-none);

/* Use opacity tokens */
opacity: var(--opacity-disabled);
opacity: var(--opacity-dim);
opacity: var(--opacity-muted);

/* Use constraint tokens */
max-height: var(--dropdown-max-height);
min-height: var(--textarea-min-height);
```

**DON'T:**
```css
/* NO hardcoded pixels */
padding: 16px;           /* Use var(--space-md) */
width: 24px;             /* Use var(--icon-xl) */
border: 1px solid #2a2a2a; /* Use var(--border-width-sm) solid var(--border) */

/* NO hardcoded colors */
color: #ef4444;          /* Use var(--error) */
background: #0a1210;     /* Use var(--lcd-bg) */

/* NO hardcoded shadows */
box-shadow: inset 0 1px 3px rgba(0,0,0,0.3); /* Use var(--shadow-inset-lcd) */

/* NO hardcoded z-index */
z-index: 1000;           /* Use var(--z-modal) */
z-index: 900;            /* Use var(--z-overlay) */

/* NO hardcoded durations */
transition: opacity 0.15s ease; /* Use var(--duration-base) */

/* NO hardcoded opacity */
opacity: 0.5;            /* Use var(--opacity-dim) */
opacity: 0.7;            /* Use var(--opacity-muted) */

/* NO hardcoded constraints */
max-height: 250px;       /* Use var(--dropdown-max-height) */
```

**Exceptions (OK to hardcode):**
- `font-size: 14px` on `html` element (root font size)
- Responsive breakpoint values in `@media` queries
- Third-party brand colors (e.g., Discogs button) with a comment explaining why
- Component-internal z-index layering (e.g., z-index: 3 for stacking within a single component)
- Keyframe animation intermediate values (e.g., `opacity: 0.3` in blink animation)

### Utility Classes
Use utility classes instead of inline styles. Full list available in style.css.

**Spacing:**
```
.m{t|b|l|r|x|y}-{2xs|xs|sm|md|lg|xl}  /* margin */
.p{t|b|l|r|x|y}-{2xs|xs|sm|md|lg|xl}  /* padding */
.gap-{2xs|xs|sm|md|lg}                 /* flex/grid gap */
```

**Flexbox:**
```
.flex, .flex-col, .flex-row
.items-{start|center|end|stretch}
.justify-{start|center|end|between}
.flex-center, .flex-between  /* common patterns */
```

**Text:**
```
.text-{2xs|xs|sm|base|lg|xl}   /* size */
.text-{primary|secondary|muted|accent|success|warning|error|lcd}  /* color */
.font-{normal|medium|semibold|bold}
.truncate, .uppercase
```

**Display & Position:**
```
.hidden, .block, .inline-flex
.relative, .absolute, .fixed
```

**Prefer utility classes over inline styles** for spacing and text. Keep `style="display: none;"` for JS-toggled elements.

### Naming Conventions
- **Base class**: `.component` (e.g., `.energy-bar`)
- **Size variants**: `.component--sm`, `.component--lg`
- **State variants**: `.component.active`, `.component.selected`

### When to Use What

| Need | Use | Example |
|------|-----|---------|
| Spacing (margin, padding, gap) | Utility class OR token | `.mt-md` or `margin-top: var(--space-md)` |
| Text color | Utility class | `.text-muted`, `.text-lcd` |
| Flex container | Utility class | `.flex`, `.flex-center`, `.items-center` |
| Display toggle | Utility class | `.hidden` |
| Component-specific layout | Component class | `.panel-track-row`, `.energy-bar` |
| Interactive element | Component class + state | `.btn.is-loading`, `.track-row.track-playable` |
| One-off styling | Inline style (rarely) | Only for JS-computed values |

**Decision flow:**
1. Can a utility class do this? → Use utility class
2. Is this a reusable component pattern? → Create/use component class
3. Is this computed by JavaScript? → Use inline style

### Key Shared Components
These are used across multiple pages - changes apply everywhere:

| Component | Classes |
|-----------|---------|
| **Energy Bar** | `.energy-bar`, `.energy-bar--sm` |
| **Track Row Highlighting** | `.track-row.track-playable`, `.panel-track-row.track-dimmed` |
| **Action Groups** | `.action-group`, `.action-group--discogs` |
| **Emoji Icons** | `.emoji-icon` (Noto Emoji font) |
| **Crate Badges** | `.crate-badge`, `.crate-badge-panel`, `.crate-badge-name` |
| **Crate Dropdown** | `.crate-dropdown`, `.crate-dropdown-wrapper`, `.crate-dropdown-emoji` |
| **Notes Textarea** | `.notes-textarea`, `.panel-notes-lcd` |
| **Side Panel** | `.release-panel`, `.panel-content`, `.panel-discogs-card` |
| **Panel Toolbar** | `.panel-toolbar`, `.panel-toolbar-actions`, `.panel-toolbar-crates` |
| **Panel Track Row** | `.panel-track-row`, `.panel-track-main`, `.panel-track-fields` |
| **Editable Inputs** | `.panel-input`, `.panel-input--editable` |
| **Buttons** | `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-danger`, `.btn-sm` |
| **Playable Toggle** | `.toggle`, `.toggle-slider`, `.toggle--mini` |
| **Toggle Button (Settings)** | `.toggle-btn`, `.toggle-btn .led` |

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
    width: var(--led-size);
    height: var(--led-size);
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

**Danger Button (destructive actions):**
Use `.btn-danger` for delete/remove actions. Red border with hover fill.

```html
<button class="btn btn-danger">Delete</button>
```

**Playable Toggle (track checkbox):**
The sliding toggle used for marking tracks as playable. Square knob (no border-radius) to maintain MPC aesthetic.

```html
<label class="toggle">
    <input type="checkbox" class="track-playable">
    <span class="toggle-slider"></span>
</label>
```

Key points:
- `.toggle` is the outer container with fixed width
- `.toggle-slider` is the track background
- `::before` pseudo-element creates the sliding knob
- Square corners throughout - no border-radius

#### Borders
- **1px borders only** - consistent thickness throughout
- Grey (`--border`) for inactive/structural borders
- Orange for interactive/selected/playable elements
- **Never add/remove borders dynamically** - only change colors (prevents layout shift)
- 2px borders only for major containers (cards, panels, modals)

#### Track Highlighting (Playable Sections)
The playable track border system creates colored "boxes" around playable tracks. This pattern is shared between:
- **`.panel-track-row`** (sidebar) - the **blueprint**, uses `.track-dimmed` on non-playable
- **`.track-row`** (full release page) - uses `.track-playable` on playable

**Both must behave identically.** When updating one, update both.

**Tracklist Grey Theme (Release Detail Page):**
The tracklist area uses a grey color scheme (not LCD green) to visually separate it from the release info card:

| Element | Token | Notes |
|---------|-------|-------|
| Table background | `--bg-primary` | Grey background for entire tracklist |
| Header background | `--bg-surface` | Slightly elevated surface for thead |
| Header text | `--text-secondary` | Brighter grey for column labels |
| Columns button | `--text-muted` / `--text-secondary` | Normal / hover states |

**Dynamic Crate Colors (Release Detail Page):**
On the release detail page, playable highlighting uses the assigned crate's color instead of orange. Custom properties on `.detail-tracks-wrapper` control this:

| Property | Default | Description |
|----------|---------|-------------|
| `--playable-color` | `--primary` | Solid color for toggle |
| `--playable-dim` | `--primary-dim` | Dimmed background for checked toggle |
| `--playable-bg-faint` | `--primary-bg-faint` | Very faint track background (3% alpha) |
| `--playable-bg-subtle` | `--primary-bg-subtle` | Hover background (6% alpha) |
| `--playable-border` | `--primary-border-alpha` | Border color (40% alpha) |
| `--playable-accent` | `--primary` | Side column color for playable tracks |
| `--playable-muted` | `--text-muted` | Side column color for non-playable tracks |

**Luminance-based accent colors:**
The Side column uses the crate color, but dark crates need a brighter accent for readability. JavaScript calculates this based on WCAG luminance:

```javascript
// getAccentColor() lightens dark colors for readability
// - Very dark (luminance < 0.15): lighten by 50%
// - Dark (luminance < 0.3): lighten by 35%
// - Medium (luminance < 0.5): lighten by 20%
// - Light: use color directly

// getMutedColor() returns a grayed-out version for non-playable tracks
// Uses reduced opacity (0.4-0.5) based on luminance
```

JavaScript updates these when a crate is assigned:
```javascript
// When crate selected
wrapper.style.setProperty('--playable-color', crateColor);
wrapper.style.setProperty('--playable-dim', darkenColor(crateColor, 0.5));
wrapper.style.setProperty('--playable-bg-faint', hexToRgba(crateColor, 0.03));
wrapper.style.setProperty('--playable-bg-subtle', hexToRgba(crateColor, 0.06));
wrapper.style.setProperty('--playable-border', hexToRgba(crateColor, 0.4));
wrapper.style.setProperty('--playable-accent', getAccentColor(crateColor));
wrapper.style.setProperty('--playable-muted', getMutedColor(crateColor));

// When no crate - reset to defaults
wrapper.style.removeProperty('--playable-color');
// ... etc
```

```css
/* Base: all tracks have left/right/bottom borders (grey), first-child also has top */
/* Playable: change left/right to crate color, add subtle background */
/* Top edge: change BOTTOM border of preceding non-playable to crate color */
/* Bottom edge: change bottom of last playable in group to crate color */
/* Adjacent playable tracks: use ::after pseudo-element for inset gray separator */
```

**Adjacent playable tracks fix:**
Gray separator between adjacent playable tracks uses a pseudo-element positioned inside the border box, so it doesn't overlap the colored side borders:

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

#### Emoji Icons (Noto Emoji Font)

> ⚠️ **ALWAYS render icons via centralized files** - never hardcode emoji characters directly in templates or JS. This ensures all icons update from a single source.

All icons in Asetate use Google's Noto Emoji font (monochrome, medium weight). Icons are stored in the database as `emoji:HEXCODE` format (e.g., `emoji:1F4C1`, `emoji:1F3B5`). Legacy `pixel:` and `emoji:name` formats are also supported.

**Emoji filtering:** The emoji picker API (`/crates/api/emoji`) only returns emoji that are confirmed to render correctly in Noto Emoji font. This is controlled by the `NOTO_EMOJI_SUPPORTED` whitelist in `models/emoji_icons.py`. If adding support for new emoji, add their hexcodes to this set.

**Centralized Icon Files (Single Source of Truth):**
- **`templates/_icons.html`** - Jinja2 macros for server-side rendering
- **`static/js/icons.js`** - ES6 module for client-side rendering

**Adding a new icon:** Update BOTH files with the new icon name and Unicode character. Also update the fallback in `releases/panel.html` (EMOJI_CHARS_FALLBACK).

**Jinja2 Macros (templates/_icons.html):**
```jinja2
{# Import at top of template #}
{% from "_icons.html" import emoji_icon, crate_icon %}

{# Render a basic emoji icon (size = modifier, not pixels!) #}
{{ emoji_icon('vinyl', size='xl', color='#F97316') }}

{# Render a crate's icon with its color #}
{{ crate_icon(crate, size='2xl') }}
```

**JavaScript Module (static/js/icons.js):**
```javascript
// ES6 module import (for type="module" scripts)
import { renderEmojiIcon, renderCrateIcon, renderEmojiIconGrid, EMOJI_ICONS, EMOJI_CHARS } from '/static/js/icons.js';

// Or use global (for AJAX-loaded content)
const icon = window.AsetateIcons.renderCrateIcon(crate, 'xl');
```

**Available functions:**
| Function | Description |
|----------|-------------|
| `renderEmojiIcon(name, size, color)` | Render icon by name (size = modifier string) |
| `renderCrateIcon(crate, size)` | Render crate's icon with color |
| `renderEmojiIconGrid(container, onSelect, selected)` | Render icon picker grid |
| `getIconName(iconField)` | Extract icon name from `emoji:name` or `pixel:name` format |
| `formatIconForStorage(name)` | Format name as `emoji:name` for storage |

**Size modifiers (use these, NOT pixel values):**
| Modifier | Token | Value |
|----------|-------|-------|
| `'sm'` | `--icon-sm` | 14px |
| `'base'` | `--icon-base` | 16px |
| `'md'` | `--icon-md` | 18px |
| `'lg'` | `--icon-lg` | 20px |
| `'xl'` | `--icon-xl` | 24px (default) |
| `'2xl'` | `--icon-2xl` | 32px |
| `'3xl'` | `--icon-3xl` | 40px |
| `'4xl'` | `--icon-4xl` | 64px |

**Common size usage:**
| Modifier | Usage |
|----------|-------|
| `'sm'` (14px) | Crate badges on cards, small icons |
| `'base'` (16px) | Crate badges in panel, inline icons |
| `'md'` (18px) | Discogs action buttons |
| `'lg'` (20px) | Emoji picker grid items |
| `'xl'` (24px) | Icon grid picker, default size |
| `'2xl'` (32px) | Icon preview in forms, crate cards |
| `'3xl'` (40px) | Large icon previews |
| `'4xl'` (64px) | Crate detail header, avatars |

**Available icons:**

| Name | Character | Description |
|------|-----------|-------------|
| `folder` | 📁 | Default crate icon |
| `vinyl` | 💿 | Optical disc (records) |
| `headphones` | 🎧 | Listening |
| `music` | 🎵 | Musical note |
| `speaker` | 🔊 | Sound/audio |
| `disco` | 🪩 | Mirror ball (party) |
| `wave` | 🌊 | Water wave (ambient) |
| `fire` | 🔥 | Flame (hot/trending) |
| `bolt` | ⚡ | Lightning (energy) |
| `star` | ⭐ | Favorites |
| `heart` | ❤ | Loved |
| `diamond` | 💎 | Premium/special |
| `crown` | 👑 | Top/best |
| `sun` | 🌞 | Daytime/upbeat |
| `moon` | 🌙 | Nighttime/moody |
| `globe` | 🌍 | World/international |
| `clock` | 🕰 | Time-based |
| `skull` | 💀 | Dark/heavy |
| `box` | 📦 | Archive/storage |
| `check` | ✔ | Complete/verified |
| `plus` | ➕ | Add/new |
| `link` | 🔗 | View on Discogs |
| `edit` | ✏ | Edit on Discogs |
| `sync` | 🔄 | Sync button |
| `notes` | 📝 | Track notes |
| `tag` | 🏷 | Add tag |

**Icon picker grid:**
Use `.emoji-icon-grid` class for icon selection interfaces:
```html
<div class="emoji-icon-grid" id="icon-grid">
    <!-- Populated via JavaScript -->
</div>
```

```javascript
import { renderEmojiIconGrid } from '/static/js/icons.js';

function onIconSelect(iconName) {
    console.log('Selected:', iconName);
}

renderEmojiIconGrid(document.getElementById('icon-grid'), onIconSelect, 'folder');
```

**How it works:**
1. Icons render as Unicode emoji characters using Noto Emoji font
2. CSS `color` property controls the icon color (monochrome font)
3. `font-size` controls the icon size
4. Font loaded from Google Fonts CDN in base.html (`font-family: 'Noto Emoji'`)

**Icon sizing and centering (IMPORTANT):**
> ⚠️ **NEVER use `width`/`height` to size `.emoji-icon` elements.** Always use `font-size`. The emoji-icon class uses a font-based approach, not image dimensions.

```css
/* BAD - width/height don't work properly with font-based icons */
.my-button .emoji-icon {
    width: 18px;
    height: 18px;
}

/* GOOD - use font-size for sizing */
.my-button .emoji-icon {
    font-size: 18px;
    line-height: 1;
}
```

For centering icons in buttons:
- Parent container should use `display: flex; align-items: center; justify-content: center;`
- Icon should have `line-height: 1;` to ensure proper vertical centering
- The `.emoji-icon` base class already includes `vertical-align: middle;` for inline contexts

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

**Panel Track Row (compact 2-row layout):**
The sidebar track list uses a space-efficient 2-row layout per track with LCD styling:

```
┌────────────────────────────────────────────┐
│ [□] A1 │ Track Title              3:45    │  ← Row 1
├────────────────────────────────────────────┤
│       [120] [8A] [█████] [+] [tag]       │  ← Row 2
└────────────────────────────────────────────┘
```

Structure:
```html
<div class="panel-track-row">
    <!-- Row 1: Toggle, Position, Title, Duration -->
    <div class="panel-track-main">
        <label class="toggle toggle--mini">...</label>
        <span class="panel-track-pos">A1</span>
        <span class="panel-track-title">Track Title</span>
        <span class="panel-track-duration">3:45</span>
    </div>
    <!-- Row 2: Editable fields + Notes + Tags -->
    <div class="panel-track-fields">
        <input class="panel-input panel-input--editable panel-bpm" ...>
        <input class="panel-input panel-input--editable panel-key" ...>
        <div class="energy-bar energy-bar--sm">...</div>
        <button class="panel-notes-btn">...</button>
        <div class="panel-track-tags">...</div>
    </div>
</div>
```

Key design decisions:
- **Toggle on left**: Allows quick scanning of playable tracks
- **Row 1**: Toggle + read-only info (position, title, duration)
- **Row 2**: Editable fields (BPM, Key, Energy) + notes + tags, aligned with title
- **LCD colors**: Track titles use `--lcd-text`, positions/durations use `--lcd-dim`
- **Mini toggle**: Uses `.toggle--mini` (28x16px) for compact rows
- **No labels**: Inputs use placeholder text (e.g., "BPM", "Key")

Editable input styling (LCD variant):
```css
.panel-input--editable {
    border: 1px dashed var(--lcd-dim);
    color: var(--lcd-text);
}

.panel-input--editable:focus {
    background: rgba(74, 222, 128, 0.15);
    border-color: var(--success);
}
```

---

### Sidebar Design Standards

The sidebar panel follows these standards for consistency:

**1. Spacing:**
- Container gap: `var(--space-sm)` (8px) between sections
- Content padding: `var(--space-sm) var(--space-md)` (8px 16px) for rows
- Compact padding: `var(--space-xs) var(--space-sm)` (4px 8px) for track rows

**2. Visual Zones:**
The sidebar has distinct visual zones with consistent styling:

| Zone | Background | Border | Text Color |
|------|------------|--------|------------|
| LCD Card (Discogs info) | `--lcd-bg` | 2px `--border` | `--lcd-text` |
| LCD Notes | `--lcd-bg` | 2px `--border` (no top) | `--lcd-text` |
| Toolbar (actions) | `--bg-elevated` | 1px bottom | Default |
| LCD Tracks | `--lcd-bg` | 2px `--border` | `--lcd-text` |

**3. Alignment Rules:**
- All horizontal padding uses `--space-md` (16px) consistently
- Track fields row aligns with title using `padding-left: 32px` (toggle width + gap)
- Crate badges flow inline with action buttons

**4. Empty States:**
- Don't show empty containers - hide them entirely
- Don't show placeholder text like "Not in any crate"

**5. Component Sizes:**
| Component | Width | Height |
|-----------|-------|--------|
| Cover image | 100px | 100px |
| Mini toggle | 28px | 16px |
| BPM/Key inputs | 36px | auto |
| Discogs buttons | 40px | flex (full height) |

**6. Color Usage in LCD zones:**
- Primary text: `--lcd-text` (green #4ade80)
- Secondary/muted: `--lcd-dim` (dark green #22543d)
- Interactive hover: `rgba(74, 222, 128, 0.1)` background
- Focus: `--success` border with subtle glow

**7. Compact Stats Format:**
Use abbreviated stats with symbols instead of words:
```html
<span title="Total tracks">5T</span>
<span title="Playable">3▶</span>
<span title="Average BPM">120</span>
```

**8. Indicators:**
- Notes indicator: 📝 emoji next to title when release has notes
- Has-notes button: Amber border + background highlight

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
    width: var(--led-size);
    height: var(--led-size);
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
    border: var(--border-width-md) solid var(--border);
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
    width: var(--led-size);
    height: var(--led-size);
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
.element { transition: width 0.3s, height 0.3s; }

/* GOOD: GPU-accelerated, no reflow */
.panel { transition: transform 0.3s; }
.element { transition: opacity 0.15s; }
```

**Avoid animating:** `width`, `height`, `margin`, `padding`, `top/left/right/bottom`, `font-size`, `border-width`

**Exception - Sidebar Panel:** The sidebar uses `margin-right` transition on the main content area to push content aside. This is acceptable because:
1. It only affects one container (not many items)
2. Grid items have fixed max-width so they reflow, not resize
3. The alternative (transform) would require complex layout changes

```css
/* Sidebar exception - acceptable margin animation */
.collection-main { transition: margin-right 0.3s ease; }
```

**Use `will-change` sparingly** for elements you know will animate:
```css
.release-panel { will-change: transform; }
```

**Transitions:** Keep to 0.15s for micro-interactions, 0.3s max for larger movements.

**Transition property specificity:** Never use `transition: all`. Always specify exact properties:
```css
/* BAD */
.btn { transition: all 0.15s; }

/* GOOD */
.btn { transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease; }
```

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
