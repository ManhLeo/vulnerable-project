# Security Platform UI Redesign Skill

## Context

Current platform functionality is strong, but the visual system still feels like an engineering prototype instead of a modern AI security platform. The redesign goal is to make the product feel closer to enterprise security tooling such as Snyk, GitHub Advanced Security, Linear, and Vercel — clean, professional, and light-first — while preserving clarity and explainability.

## Design Philosophy

The interface should feel:

- trustworthy before impressive
- precise before decorative
- fast before animated
- developer-centric before executive-centric

Every UI decision must improve:
- scan readability
- issue triage speed
- cognitive clarity
- explainability comprehension

## State System Rules

Every data surface must define:

- loading state
- empty state
- error state
- partial-data state
- success state

Never render blank containers.

Loading states should use:
- skeletons for tables/cards
- inline spinners for actions
- optimistic preservation for editor content

Errors should:
- preserve existing data when possible
- never collapse layout
- show actionable recovery messaging

## Data Visualization Rules

Charts must prioritize readability over decoration.

Rules:
- avoid 3D charts
- avoid gradients in charts
- use horizontal layouts when possible
- always label severity colors consistently
- charts should fit inside compact dashboard cards
- prefer bars over pies
- avoid oversized chart heights

Preferred chart types:
- stacked horizontal bars
- compact area charts
- minimal line charts
- table + sparkline combinations

## Interaction Density Rules

The platform should support high-density workflows.

Rules:
- avoid oversized padding
- avoid large empty hero sections
- keep primary actions visible without scrolling
- prefer inline actions over nested menus
- tables should maximize visible information
- findings should be scannable within 2-3 seconds

The UI should feel operational, not promotional.

## AI Explainability UX Rules

AI-generated findings must always appear:

- traceable
- explainable
- confidence-scored
- visually distinguishable from deterministic detections

Confidence values must:
- use mono font
- always show percentage
- never imply certainty

Risk summaries should:
- explain why risk is elevated
- correlate findings with confidence
- avoid vague AI wording

## Core Design Direction

Style:

* modern AI security platform
* **light-first interface** — white background as the primary surface
* clean and technical, not clinical
* high information density with strong visual hierarchy
* enterprise SaaS aesthetic — inspired by Linear, Vercel, Notion, and GitHub
* subtle depth through shadow and border layering, not color

Visual Priorities:

1. code analysis experience
2. explainability visualization
3. scan confidence and severity clarity
4. professional dashboard layout
5. readable data hierarchy

Avoid:

* dark panels and heavy surfaces
* neon glows or cyberpunk aesthetics
* colorful clutter or rainbow UIs
* generic startup templates
* excessive rounded cards that feel toy-like
* heavy drop shadows or aggressive depth effects

---

## Design Language

### Color System

Background:

* page: #F8F9FB
* panel: #FFFFFF
* elevated: #FFFFFF
* subtle: #F3F4F6
* border: #E5E7EB
* border-strong: #D1D5DB

Text:

* primary: #111827
* secondary: #4B5563
* muted: #9CA3AF
* placeholder: #C9CDD4

Severity Tokens:

* critical: #DC2626
* critical-bg: #FEF2F2
* high: #EA580C
* high-bg: #FFF7ED
* medium: #D97706
* medium-bg: #FFFBEB
* low: #2563EB
* low-bg: #EFF6FF
* safe: #16A34A
* safe-bg: #F0FDF4

Accent:

* primary accent: #2563EB
* hover accent: #1D4ED8
* accent-subtle: #EFF6FF

Neutral:

* gray-50: #F9FAFB
* gray-100: #F3F4F6
* gray-200: #E5E7EB
* gray-300: #D1D5DB
* gray-500: #6B7280
* gray-900: #111827

Rules:

* severity colors are used ONLY for findings, risk badges, and severity indicators
* backgrounds remain white or very light gray — never tinted
* color is used sparingly to draw attention, not decorate
* maintain high contrast between text and background (WCAG AA minimum)

---

## Typography

Fonts:

* UI text: Geist or Inter (fallback)
* Code: Geist Mono or JetBrains Mono

Hierarchy:

* page title: 28px / weight 600
* section title: 18px / weight 600
* card title: 15px / weight 600
* body: 14px / weight 400
* metadata: 12px / weight 500

Rules:

* use mono font for all code, confidence values, line numbers, and risk scores
* body text line-height: 1.6
* avoid oversized hero typography in operational interfaces
* prioritize scan readability over marketing aesthetics
* keep text tight and purposeful — every label should earn its place

---

## Layout System

### Global Shell

Desktop:

* left sidebar navigation — white background with subtle right border
* top compact status/header bar — white, bottom border only
* content area max-width: 1440px, centered

Sidebar:

* width: 240px
* white surface, border-right: 1px solid #E5E7EB
* icon + label navigation
* active route: accent-blue text + #EFF6FF pill highlight
* hover: #F3F4F6 background

Topbar:

* compact, white, border-bottom: 1px solid #E5E7EB
* project status pill
* model status indicator
* scan activity badge

### Spacing

Scale: 4 / 8 / 12 / 16 / 24 / 32 / 48

Rules:

* dense but breathable
* section gaps: 24–32px
* component internal padding: 12–16px
* align all panels to the grid
* avoid huge empty whitespace; don't pad for padding's sake

---

## Scan Workspace Redesign

### Main Layout

Desktop:

* left: Monaco code editor (65%)
* right: findings and explainability panel (35%)
* divider: 1px solid #E5E7EB

Mobile:

* stacked vertical layout — editor on top, findings below

### Monaco Area

Requirements:

* light editor theme (GitHub Light or custom matching the palette)
* full-height professional editor feel
* subtle focus border: 1px solid #2563EB on active
* sticky action bar above editor with white background + bottom border

Toolbar Contains:

* language selector (compact dropdown, #F3F4F6 background)
* upload button (ghost/secondary style)
* scan button (primary blue action)
* scan status text (muted, animated during scan)

Scan Button States:

* idle: #2563EB background, white text
* loading: spinner + "Scanning…" text, disabled interaction
* complete: returns to idle state

### Line Highlighting

* active finding highlight: light yellow (#FFFBEB) background on Monaco line
* selected finding gutter dot matches severity color

---

## Explainability Panel

### Findings List

Each finding card contains:

* severity badge (pill style with colored background + text)
* issue title (15px / semibold)
* line number in mono font (muted)
* vulnerable code snippet (mono, #F3F4F6 background, rounded)
* pattern type tag (gray pill)

Severity badge styles:

* CRITICAL: #DC2626 text, #FEF2F2 background
* HIGH: #EA580C text, #FFF7ED background
* MEDIUM: #D97706 text, #FFFBEB background
* LOW: #2563EB text, #EFF6FF background

Card style:

* white background
* 1px solid #E5E7EB border
* 6px border-radius
* left accent bar (3px) matching severity color
* subtle hover: #F9FAFB background

Behavior:

* click finding → scroll Monaco to that line
* selected card: #EFF6FF background + #2563EB left border
* keyboard navigable (arrow keys through findings list)

### Risk Summary Panel

Display:

* vulnerability status (pill)
* confidence score (mono, large)
* risk level (color-coded label)
* finding count (by severity breakdown)

Layout:

* compact metrics row at top of panel
* 2×2 stat grid or horizontal inline bar
* white background, subtle border-bottom separating from findings list

---

## Dashboard Redesign

### Dashboard Goals

The dashboard should feel like:

* a clean security operations overview
* a professional vulnerability monitoring interface
* an AI-assisted analysis control center

Think: Linear meets GitHub Insights meets Vercel Analytics.

### Dashboard Sections

**1. Overview Stats**

4 metric cards in a horizontal row:

* total scans
* vulnerable scans
* average confidence
* critical findings

Card style: white background, 1px border, 8px radius, gray label, large mono number

**2. Recent Scans**

Compact table:

* white background
* sticky header row: #F9FAFB, 12px uppercase labels
* row hover: #F3F4F6
* severity badge per row (pill)
* sortable columns (icon indicator)
* alternating row tint optional (very subtle)

**3. Risk Distribution**

Horizontal stacked severity bar:

* total width fills card
* segments colored by severity token
* legend below bar with counts
* compact — no oversized charts

**4. Activity Feed**

* latest scan events
* timestamp in mono/muted
* severity dot indicator
* compact list, no cards per item

---

## History Page Redesign

### Table Style

Columns:

* filename (primary, semibold)
* language (gray pill tag)
* risk (severity badge)
* confidence (mono value)
* findings (count)
* created_at (muted mono)

Requirements:

* white table background
* sticky header: #F9FAFB background, border-bottom
* row hover: #F3F4F6
* severity badge per row
* compact pagination (prev / page numbers / next)
* search bar + filter dropdowns above table

---

## Component Design Rules

### Cards

* background: #FFFFFF
* border: 1px solid #E5E7EB
* border-radius: 8px
* padding: 16px
* shadow: none (or `0 1px 3px rgba(0,0,0,0.06)` for elevated cards)
* no colored card backgrounds — color goes in badges and labels only

### Severity Badges / Pills

```
background: {severity}-bg token
color: {severity} token
font-size: 12px
font-weight: 500
padding: 2px 8px
border-radius: 999px
```

### Buttons

Primary:

* background: #2563EB
* text: white
* hover: #1D4ED8
* border-radius: 6px
* height: 36px
* padding: 0 16px

Secondary / Ghost:

* background: transparent
* border: 1px solid #D1D5DB
* text: #374151
* hover: #F3F4F6 background

Danger:

* background: #DC2626
* reserved ONLY for destructive actions (delete, clear, reset)

Disabled:

* opacity: 0.5
* cursor: not-allowed

### Inputs / Selects

* background: #FFFFFF
* border: 1px solid #D1D5DB
* border-radius: 6px
* height: 36px
* padding: 0 12px
* focus: border-color #2563EB, box-shadow 0 0 0 3px rgba(37,99,235,0.12)
* placeholder: #9CA3AF

### Tags / Pills

* gray by default: #F3F4F6 background, #374151 text
* colored variants only for severity or status

---

## Motion Rules

Allowed:

* subtle hover transitions (150ms ease)
* panel fade-in (200ms)
* Monaco code reveal on scan complete
* loading shimmer on skeleton states
* scan button spinner

Avoid:

* bouncy or spring animations in an enterprise context
* excessive motion that distracts from content
* page-level transitions that delay perceived speed

---

## Accessibility

Requirements:

* WCAG AA contrast for all text/background combinations
* keyboard navigable findings list (arrow keys, enter to select)
* visible focus ring on all interactive elements (blue outline)
* semantic HTML: `<button>`, `<nav>`, `<main>`, `<aside>`, `<table>`
* screen-reader-friendly status announcements during scan

---

## Frontend Architecture Rules

* feature-based folder organization
* no monolithic page components — split into focused sections
* centralized design tokens (CSS variables or a tokens file)
* no inline hardcoded colors — reference tokens only
* no duplicated severity mapping — one source of truth
* reusable primitives: `<Badge>`, `<Button>`, `<Card>`, `<MetricCard>`, `<FindingCard>`

---

## Implementation Recommendation

Use:

* **Tailwind CSS** — with a custom config extending the design tokens
* **shadcn/ui** — for accessible primitives (Dialog, Select, Table, Popover)
* **Lucide icons** — consistent, clean icon set
* **Recharts** — lightweight chart library for risk distribution and history
* **Monaco Editor** — with a custom light theme matching the color system
* **Framer Motion** — light usage only (fade, slide-in for panels)

Config overrides (tailwind.config.js):

```js
colors: {
  border: '#E5E7EB',
  background: '#F8F9FB',
  panel: '#FFFFFF',
  accent: { DEFAULT: '#2563EB', hover: '#1D4ED8', subtle: '#EFF6FF' },
  severity: {
    critical: '#DC2626',
    high: '#EA580C',
    medium: '#D97706',
    low: '#2563EB',
    safe: '#16A34A',
  }
}
```

Prioritize:

1. visual hierarchy and clarity
2. scan readability
3. explainability panel usability
4. responsive layout correctness
5. performance (avoid heavy animations on large finding sets)

---

## Inspiration References

Target feeling:

* **Linear** — clean sidebar, compact tables, precise typography
* **Vercel Dashboard** — white surfaces, minimal shadows, strong data hierarchy
* **GitHub Advanced Security** — professional, trust-inspiring, readable tables
* **Snyk** — severity clarity, developer-focused UI
* **Notion** — whitespace discipline, understated design
* **Retool** — information density done right

The core principle: enterprise clarity through restraint. Every pixel earns its place.

---

## Recommended Priority Order

**Priority 1 — Core Surfaces:**

* app shell (sidebar + topbar on white)
* scan workspace (light Monaco + findings panel)
* severity badge system

**Priority 2 — Data Surfaces:**

* dashboard stats and table
* history table with search/filter
* improved loading skeleton states

**Priority 3 — Polish:**

* risk distribution chart
* animated scan progress
* activity feed transitions
* potential live scan updates via WebSocket