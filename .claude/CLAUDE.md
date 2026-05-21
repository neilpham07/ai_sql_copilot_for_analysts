# CLAUDE.md — QueryMind AI: Project Intelligence File

> **Read this file before touching a single line of code.**
> This document is the single source of truth for architecture, design, behavior, and constraints.
> Every implementation decision must be validated against this file.

---

## 0. MISSION STATEMENT

**QueryMind AI** is an enterprise-grade AI SQL Copilot designed for non-technical Vietnamese Data Analysts. Its core purpose is to eliminate the translation barrier between business intuition and production-ready SQL. The experience must feel like having a senior data engineer on call — instantly responsive, deeply schema-aware, and fluent in Vietnamese business language.

**Tagline:** AI-Powered V1.0
**Target user:** Vietnamese-speaking Data Analysts with business context but limited SQL fluency.
**Success metric:** A user types a Vietnamese question and receives a clean, runnable SQL query in under 3 seconds, with a timeline explanation they can follow.

---

## 1. TECHNOLOGY CONSTRAINTS — NON-NEGOTIABLE

These rules are absolute. Do NOT deviate.

| Constraint | Rule |
|---|---|
| **Framework** | Modal Cloud Web Endpoint (ASGI/FastAPI built-in). Zero external web frameworks. |
| **AI SDK** | Official `anthropic` Python SDK ONLY. |
| **AI Model** | `claude-sonnet-4-6` (current). Default to latest Sonnet unless instructed otherwise. |
| **LangChain** | FORBIDDEN. Do not import or suggest it. |
| **Heavy frameworks** | FORBIDDEN. No LlamaIndex, Haystack, or similar orchestration layers. |
| **Deployment** | Single file: `app.py`. Deploy with `modal deploy app.py`. Nothing else. |
| **Language** | Python backend. All HTML/CSS/JS is rendered as inline strings within `app.py`. |
| **Dependencies** | `modal`, `anthropic`. No other pip packages. |

---

## 2. FILE ARCHITECTURE

The entire application must compile into a **single `app.py`** file with this exact internal structure:

```
app.py
├── [SECTION 1] Modal + Anthropic imports and app initialization
├── [SECTION 2] SCHEMA CONTEXT — hardcoded table metadata (merchants, transactions)
├── [SECTION 3] SYSTEM PROMPTS — translate_prompt, explain_prompt
├── [SECTION 4] BACKEND LOGIC — Claude API call functions
├── [SECTION 5] API ENDPOINTS — Modal @app.function web endpoints
├── [SECTION 6] HTML_LANDING — landing page as a Python string constant
├── [SECTION 7] HTML_WORKSPACE — workspace page as a Python string constant
└── [SECTION 8] ROUTE HANDLERS — serve landing, workspace, and API routes
```

No sub-modules. No separate HTML files. No asset pipeline. Everything self-contained.

---

## 3. DESIGN SYSTEM — "SYNTHETIX LUMINA"

This design system was derived from `./web_pic/landing_page.png` and `./web_pic/workspace.png`. Every CSS value here is **exact and mandatory**. Do not approximate or substitute.

### 3.1 Color Palette

```css
/* === FOUNDATIONS === */
--bg-base:               #0B1020;   /* Page background — deep navy/slate */
--bg-surface:            #0e1323;   /* Primary surface */
--bg-surface-low:        #161b2b;   /* Sidebar, recessed panels */
--bg-surface-mid:        #1a1f30;   /* Cards, containers */
--bg-surface-high:       #25293a;   /* Elevated containers */
--bg-surface-highest:    #2f3446;   /* Tooltips, popovers */

/* === TEXT === */
--text-primary:          #dee1f9;   /* Body text, titles */
--text-secondary:        #bbc9cd;   /* Labels, subtitles, muted */

/* === ACCENT — CYAN (Primary / Intelligence) === */
--cyan-primary:          #8aebff;   /* Active states, highlights */
--cyan-mid:              #22d3ee;   /* CTA buttons, interactive elements */
--cyan-bright:           #2fd9f4;   /* Glows, tints, surface tints */

/* === ACCENT — VIOLET (Secondary / AI Magic) === */
--violet-primary:        #d0bcff;   /* Secondary highlights */
--violet-deep:           #571bc1;   /* Gradient stops, AI features */
--violet-mid:            #c4abff;   /* Accent fills */

/* === ACCENT — BLUE (Tertiary / Information) === */
--blue-primary:          #d0ddff;   /* Info elements */
--blue-mid:              #adc6ff;   /* Tertiary fills */

/* === UTILITY === */
--error:                 #ffb4ab;
--success-green:         #4ade80;   /* Live DB status badge */
--border-subtle:         rgba(255, 255, 255, 0.08);
--border-elevated:       rgba(255, 255, 255, 0.15);
```

### 3.2 Gradient Tokens

```css
/* Primary CTA gradient — used on "Start Querying" and "Generate Insight" buttons */
--gradient-cta:     linear-gradient(135deg, #22d3ee 0%, #8b5cf6 100%);

/* Hero ambient glow — subtle background radial blooms */
--gradient-hero-cyan:   radial-gradient(ellipse 60% 50% at 70% 40%, rgba(34,211,238,0.07) 0%, transparent 70%);
--gradient-hero-violet: radial-gradient(ellipse 50% 60% at 30% 60%, rgba(139,92,246,0.06) 0%, transparent 70%);

/* Animated AI response border */
--gradient-ai-border:   linear-gradient(90deg, #22d3ee, #8b5cf6, #22d3ee);
```

### 3.3 Typography

**Font loading (add to `<head>` of both pages):**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

| Token | Font | Size | Weight | Usage |
|---|---|---|---|---|
| `display-lg` | Inter | 48px | 700 | Hero headline |
| `headline-lg` | Inter | 32px | 600 | Section headers |
| `headline-md` | Inter | 24px | 600 | Card titles |
| `body-lg` | Inter | 18px | 400 | Hero subtext |
| `body-md` | Inter | 16px | 400 | General body |
| `label-md` | Geist Mono | 14px | 500 | Tags, metadata |
| `label-sm` | Geist Mono | 12px | 600 | Status chips (UPPERCASE) |
| `code` | Geist Mono | 13px | 400 | SQL output |

### 3.4 Spacing & Layout

```
4px base grid — all spacing must be multiples of 4px.

Container max-width:  1440px
Desktop gutters:      24px
Desktop margins:      64px
Mobile margins:       20px

Card internal padding (desktop): 24px–32px
Card internal padding (mobile):  16px
Stack SM:  8px
Stack MD:  16px
Stack LG:  32px
```

### 3.5 Border Radius

```css
--radius-sm:   4px;    /* Tooltips, tags, micro-elements */
--radius-md:  12px;    /* Standard elements */
--radius-lg:  16px;    /* Buttons, inputs */
--radius-xl:  24px;    /* Primary containers, main panels */
--radius-full: 9999px; /* Pills, badges, circular icons */
```

### 3.6 Glassmorphism System (Elevation Levels)

```css
/* LEVEL 0 — Background canvas */
background: #0B1020;
/* + ambient radial gradient blooms */

/* LEVEL 1 — Panels, sidebars, standard cards */
background: rgba(255, 255, 255, 0.03);
backdrop-filter: blur(12px);
-webkit-backdrop-filter: blur(12px);
border: 1px solid rgba(255, 255, 255, 0.08);
/* "Top-light" edge: a subtle top-border highlight */
border-top: 1px solid rgba(255, 255, 255, 0.12);

/* LEVEL 2 — Active cards, modals, result zones */
background: rgba(255, 255, 255, 0.05);
backdrop-filter: blur(20px);
-webkit-backdrop-filter: blur(20px);
border: 1px solid rgba(255, 255, 255, 0.15);
box-shadow: 0 0 24px rgba(34, 211, 238, 0.06);

/* LEVEL 3 — AI response block (special) */
/* Animated gradient border via pseudo-element */
background: rgba(255, 255, 255, 0.04);
backdrop-filter: blur(20px);
/* border animated: --gradient-ai-border */
```

### 3.7 Component Specifications

#### Primary Button ("Start Querying", "Generate Insight")
```css
background: linear-gradient(135deg, #22d3ee 0%, #8b5cf6 100%);
color: #000;           /* Black text for contrast on cyan */
font-family: Inter;
font-size: 16px;
font-weight: 600;
padding: 14px 28px;
border-radius: 16px;
border: none;
cursor: pointer;
transition: transform 0.2s ease, box-shadow 0.2s ease;

/* Hover state */
transform: translateY(-2px);
box-shadow: 0 8px 32px rgba(34, 211, 238, 0.35);
```

#### Secondary / Ghost Button ("See Demo", "Talk to Sales")
```css
background: rgba(255, 255, 255, 0.05);
color: #dee1f9;
border: 1px solid rgba(255, 255, 255, 0.15);
padding: 14px 28px;
border-radius: 16px;
transition: background 0.2s, border-color 0.2s;

/* Hover */
background: rgba(255, 255, 255, 0.08);
border-color: rgba(255, 255, 255, 0.25);
```

#### Input Field
```css
background: rgba(255, 255, 255, 0.04);
border: 1px solid rgba(255, 255, 255, 0.1);
border-radius: 16px;
color: #dee1f9;
font-family: Inter;
font-size: 16px;
padding: 16px 20px;
width: 100%;
transition: border-color 0.2s, box-shadow 0.2s;

/* Focus state */
border-color: transparent;
background-image: linear-gradient(#1a1f30, #1a1f30),
                  linear-gradient(135deg, #22d3ee, #8b5cf6);
background-origin: border-box;
background-clip: padding-box, border-box;
box-shadow: 0 0 0 1px transparent inset, 0 0 16px rgba(34,211,238,0.15);
```

#### Mode Tab Pills
```css
/* Container */
background: rgba(255, 255, 255, 0.04);
border: 1px solid rgba(255, 255, 255, 0.08);
border-radius: 9999px;
padding: 4px;
display: inline-flex;

/* Inactive tab */
.tab {
  padding: 8px 20px;
  border-radius: 9999px;
  color: #bbc9cd;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
}

/* Active tab */
.tab.active {
  background: linear-gradient(135deg, #22d3ee 0%, #8b5cf6 100%);
  color: #000;
  font-weight: 600;
  box-shadow: 0 0 20px rgba(34,211,238,0.3);
}
```

#### Toggle Switch (Schema-aware, Auto-optimize)
```css
/* Track */
width: 36px; height: 20px;
background: rgba(255,255,255,0.1);
border-radius: 9999px;

/* Thumb */
width: 16px; height: 16px;
background: #dee1f9;
border-radius: 9999px;
transition: transform 0.2s;

/* Active state */
background: linear-gradient(135deg, #22d3ee, #8b5cf6); /* track */
/* thumb translates right */
```

#### Quick Query Tags
```css
background: rgba(255, 255, 255, 0.06);
border: 1px solid rgba(255, 255, 255, 0.1);
border-radius: 9999px;
color: #bbc9cd;
font-family: Geist Mono;
font-size: 13px;
padding: 6px 14px;
cursor: pointer;
transition: background 0.2s, border-color 0.2s, color 0.2s;

/* Hover */
background: rgba(34, 211, 238, 0.08);
border-color: rgba(34, 211, 238, 0.3);
color: #8aebff;
```

#### SQL Output Terminal Card (Level 2 glass + AI border)
```css
.sql-card {
  background: rgba(8, 13, 29, 0.7);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.1);
  overflow: hidden;
}

.sql-card-header {
  padding: 12px 16px;
  background: rgba(255,255,255,0.03);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Filename dot indicator (3 colored dots like macOS terminal) */
.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot-red    { background: #ff5f57; }
.dot-yellow { background: #ffbd2e; }
.dot-green  { background: #28c840; }

.sql-filename {
  font-family: Geist Mono;
  font-size: 13px;
  color: #bbc9cd;
  margin-left: 8px;
}

.sql-code {
  padding: 20px;
  font-family: Geist Mono;
  font-size: 13px;
  line-height: 1.7;
  overflow-x: auto;
}
```

#### SQL Syntax Highlighting Colors
```
Keywords (SELECT, FROM, WHERE, JOIN, GROUP BY, ORDER BY, AS, AND, ON):
  color: #c4abff;  /* violet */

Functions (SUM, COUNT, DATE_TRUNC, AVG):
  color: #22d3ee;  /* cyan */

Strings ('completed', 'month'):
  color: #86efac;  /* soft green */

Numbers & operators:
  color: #fca5a5;  /* soft red/pink */

Table/column names:
  color: #dee1f9;  /* primary text */

Comments:
  color: #4a5568; font-style: italic;
```

#### Live DB Status Badge
```css
.db-status-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(74, 222, 128, 0.06);
  border: 1px solid rgba(74, 222, 128, 0.2);
  border-radius: 12px;
}

.pulse-dot {
  width: 8px; height: 8px;
  background: #4ade80;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%   { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.5); }
  70%  { box-shadow: 0 0 0 6px rgba(74, 222, 128, 0); }
  100% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0); }
}
```

---

## 4. PAGE 1 — LANDING PAGE (`/`)

### 4.1 Page Structure (Top → Bottom)

```
<body>                         background: #0B1020 + ambient radial gradients
  <nav>                        Fixed top, glassmorphism Level 1
  <main>
    <section.hero>             Full viewport, centered vertically
    <section.features>         3-column card grid
    <section.cta-banner>       Full-width gradient CTA strip
    <footer>                   Simple dark footer
```

### 4.2 Navigation Bar

```
[QueryMind AI logo + wordmark]    [Docs] [Features] [Customers] [Changelog]    [Sign In] [Start Free →]

Height: 64px
Background: rgba(11,16,32,0.8) with backdrop-filter: blur(20px)
Border-bottom: 1px solid rgba(255,255,255,0.06)
Position: sticky top-0 z-50
Logo: "QueryMind AI" in Inter 700, with a small cyan sparkle SVG icon
Nav links: Inter 14px, color: #bbc9cd, hover: #dee1f9
"Start Free" button: gradient CTA (smaller padding: 10px 20px)
```

### 4.3 Hero Section

**Left Column (55% width):**
```
Badge pill:         "✦ AI POWERED V1.0"
                    background: rgba(34,211,238,0.08)
                    border: 1px solid rgba(34,211,238,0.2)
                    color: #22d3ee
                    font: Geist Mono 12px UPPERCASE letter-spacing: 0.1em
                    border-radius: 9999px, padding: 6px 14px

Headline (h1):      "Ask Questions in Vietnamese.
                     Get Production-Ready SQL Instantly."
                    font: Inter 48px/700, color: #dee1f9
                    letter-spacing: -0.02em, line-height: 1.1
                    Max-width: 580px

Subheadline (p):    "An AI engine designed for Data Analysts to translate business
                     questions into SQL, explain complex queries, and accelerate
                     analytics workflows."
                    font: Inter 18px/400, color: #bbc9cd
                    line-height: 1.6, max-width: 480px, margin-top: 20px

CTA Row:            [Start Querying →] [▷ See Demo]
                    gap: 12px, margin-top: 32px
```

**Right Column (45% width):**
```
Animated mockup card (Level 2 glass):
  - Shows a "Natural Language → SQL" conversion animation
  - Top: Vietnamese text input "Cho tôi thấy top 10 merchant theo doanh thu tháng này"
  - Arrow animation downward
  - Bottom: floating SQL code block with syntax highlighting
  - Background glow: radial cyan/violet at 15% opacity behind card
  - Card border: animated gradient border (--gradient-ai-border)
  - border-radius: 24px
```

### 4.4 Feature Cards Section

```
Section header:   "Engineered for Technical Depth"
                  Inter 32px/600, centered, color: #dee1f9

Sub-header:       "Three ways QueryMind AI makes every analyst a SQL expert."
                  Inter 16px/400, centered, color: #bbc9cd

Cards layout:     3 columns, gap: 24px, margin-top: 48px
Card style:       Level 1 glassmorphism, border-radius: 24px, padding: 32px
```

**Card 1 — Vietnamese → SQL**
```
Icon:    ✦ Sparkles (cyan gradient fill), 40px
Title:   "Vietnamese → SQL"  (Inter 20px/600)
Body:    "Describe your data question naturally in Vietnamese. QueryMind AI
          translates intent into optimized, production-ready SQL queries."
          (Inter 15px/400, color: #bbc9cd, line-height: 1.6)
Bottom tag: "NLP Translation" (label-sm chip, cyan tint)
```

**Card 2 — Explain Complex Queries**
```
Icon:    🧠 Brain (violet gradient fill), 40px
Title:   "Explain Complex Queries"  (Inter 20px/600)
Body:    "Paste any SQL query and receive a plain-language, step-by-step
          breakdown. Perfect for learning and query review."
          (Inter 15px/400, color: #bbc9cd)
Bottom tag: "Query Intelligence" (label-sm chip, violet tint)
```

**Card 3 — Schema-Aware Query Generation**
```
Icon:    🗄 Database (blue gradient fill), 40px
Title:   "Schema-Aware Query Generation" (Inter 20px/600)
Body:    "QueryMind AI has deep knowledge of your table schemas, column types,
          and relationships — generating queries that join correctly, every time."
          (Inter 15px/400, color: #bbc9cd)
Bottom tag: "Schema Intelligence" (label-sm chip, blue tint)
```

### 4.5 CTA Banner Section

```
Background:   radial gradient bloom + Level 1 glass card, border-radius: 24px
Headline:     "Transform your data workflow today."  (Inter 32px/700, centered)
Subtext:      "Join analysts who ship data insights 10x faster."  (Inter 16px, #bbc9cd)
Buttons:      [Start Free Trial] [Talk to Sales]  — centered row, gap: 16px
```

### 4.6 Footer

```
Left:    QueryMind AI logo + "© 2025 QueryMind AI. All rights reserved."
Center:  Privacy Policy  |  Terms of Service  |  Contact
Right:   (optional) social icon links

Background: rgba(255,255,255,0.02)
Border-top: 1px solid rgba(255,255,255,0.06)
Padding: 32px 64px
Font: Inter 14px, color: #4a5568
```

---

## 5. PAGE 2 — WORKSPACE (`/workspace`)

### 5.1 Page Layout

```
<body>
  <header.app-header>             Full-width top bar, 60px height
  <div.app-shell>
    <aside.sidebar>               28% width, full height, fixed
    <main.workspace>              72% width, scrollable
      <div.mode-tabs>
      <div.input-zone>
      <div.quick-queries>
      <div.result-zone>
```

### 5.2 App Header

```
Height: 60px
Background: rgba(11,16,32,0.9) + backdrop-filter: blur(16px)
Border-bottom: 1px solid rgba(255,255,255,0.06)
Layout: [Logo left] [Nav center: Query | Dashboards | Notebooks] [Icons right: 🔔 ⚙ 👤]

Left:   "QueryMind AI" wordmark + "AI POWERED V1.0" badge pill (cyan)
Center: Pill nav tabs — Query (active, gradient bg) | Dashboards | Notebooks
Right:  Notification bell + Settings gear + Avatar circle
```

### 5.3 Left Sidebar (28% width)

```css
.sidebar {
  width: 28%;
  min-width: 260px;
  max-width: 320px;
  background: rgba(14, 19, 35, 0.9);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  padding: 20px 16px;
  height: calc(100vh - 60px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
```

**Sidebar Header:**
```
Title:   "Database Schema"  (Inter 16px/600, color: #dee1f9)
Badge:   "v2.4 Stable"      (Geist Mono 11px, color: #4ade80, bg: rgba(74,222,128,0.1),
                               border: rgba(74,222,128,0.2), border-radius: 9999px)
Layout:  Space-between row
```

**Search Input:**
```html
<input placeholder="Search tables..." />
```
```css
/* Standard input style, margin-top: 12px */
background: rgba(255,255,255,0.04);
border: 1px solid rgba(255,255,255,0.08);
border-radius: 10px;
padding: 10px 14px;
color: #dee1f9;
font-size: 14px;
width: 100%;
```

**Schema Tree — Table: `merchants`**
```
▾ merchants                          [table icon, cyan]
    id              INT              [# icon, muted]
    name            VARCHAR          [T icon, muted]
    category        VARCHAR          [T icon, muted]
    amount          DECIMAL          [≈ icon, muted]
    created_at      TIMESTAMP        [⏱ icon, muted]
```

**Schema Tree — Table: `transactions`**
```
▾ transactions                       [table icon, cyan]
    id              INT              [# icon, muted]
    merchant_id     INT              [# icon, muted]
    name            VARCHAR          [T icon, muted]
    amount          DECIMAL          [≈ icon, muted]
    status          VARCHAR          [T icon, muted]
    created_at      TIMESTAMP        [⏱ icon, muted]
```

**Tree row styling:**
```css
.tree-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}
.tree-row:hover {
  background: rgba(34, 211, 238, 0.06);
}
.field-name { font-family: Geist Mono; font-size: 13px; color: #dee1f9; }
.field-type { font-family: Geist Mono; font-size: 11px; color: #4a5568; }
```

**Data Type Icons mapping (use SVG or Unicode):**
```
INT       → "#"     color: #22d3ee
VARCHAR   → "T"     color: #d0bcff
TIMESTAMP → "⏱"    color: #fbbf24
DECIMAL   → "≈"     color: #86efac
```

**Sidebar Footer — DB Status Card:**
```css
/* Pinned to sidebar bottom */
margin-top: auto;
padding-top: 16px;
border-top: 1px solid rgba(255,255,255,0.06);
```
```
[● pulse green dot]  "Connected to Production DB"   (Inter 13px/600, color: #dee1f9)
                     "LIVE SYNC ENABLED"             (Geist Mono 10px UPPERCASE, color: #4ade80)

Below:  [Upgrade to Pro] button — full width, ghost style with violet border
```

### 5.4 Main Workspace (72% width)

```css
.workspace {
  flex: 1;
  padding: 28px 32px;
  overflow-y: auto;
  height: calc(100vh - 60px);
}
```

**Mode Tabs:**
```
Container: pill wrapper (rounded-full, glass bg)
Tab 1: "⟲ Translate Vietnamese to SQL"  — ACTIVE by default
Tab 2: "⟴ Explain SQL Query"

Active tab: gradient background (cyan→violet), black text, glow shadow
Inactive tab: transparent, muted text, hover brightens
```

**Input Zone Card (Level 1 glass):**
```css
.input-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 20px 24px;
  margin-top: 20px;
}
```
```
Textarea:     Multi-line, min-height: 80px
Placeholder (mode 1): "Ví dụ: Lấy tổng doanh thu của từng merchant trong tháng này"
Placeholder (mode 2): "Ví dụ: Dán SQL phức tạp vào đây để tôi giải thích từng bước..."
Font: Inter 16px, color: #dee1f9

Bottom row:
  Left:   [🎤 voice icon]  [📎 attachment icon]  [─ divider]  [Schema-aware toggle]  [Auto-optimize toggle]
  Right:  [Generate Insight →] gradient button

Toggle labels: Geist Mono 13px
```

**Quick Queries Row:**
```
Label:  "QUICK QUERIES:"  (Geist Mono 11px UPPERCASE, color: #4a5568, letter-spacing: 0.08em)

Tags (clickable pills):
  ⚡ "Top Merchants by GMV"
  📈 "Fast Growth List"
  ⚠  "Failure Rate Analysis"

On click: populate textarea with corresponding Vietnamese prompt
```

### 5.5 Result Zone — SQL Output Card

**Card Header:**
```
Left:   [● red dot] [● yellow dot] [● green dot]   "query_v1_insight.sql"
Right:  [Copy Code icon + label]  [↓ Download .sql icon + label]

Header bg: rgba(255,255,255,0.03)
Header border-bottom: 1px solid rgba(255,255,255,0.06)
Filename font: Geist Mono 13px, color: #bbc9cd
```

**SQL Code Block (syntax highlighted):**

The backend must return SQL pre-wrapped in `<span>` tags with these classes, rendered in the card:
```
.kw   { color: #c4abff; }   /* SELECT, FROM, WHERE, JOIN, GROUP BY, ORDER BY, AS, AND, ON */
.fn   { color: #22d3ee; }   /* SUM(), COUNT(), DATE_TRUNC(), AVG() */
.str  { color: #86efac; }   /* 'completed', 'month' */
.num  { color: #fca5a5; }   /* numbers */
.col  { color: #dee1f9; }   /* column and table names */
.cmt  { color: #4a5568; font-style: italic; } /* -- comments */
```

**Action Row (below code block):**
```
[Copy Code]       ghost button
[Download .sql]   ghost button
[Explain Every Step ▾]  toggle — expands the explanation timeline
```

### 5.6 Step-by-Step Explanation Timeline

Rendered below the SQL card when "Explain Every Step" is toggled ON. The backend must return structured explanation data parseable into this format.

```
Step 1 ─── [icon] [Title]
              Body text explanation of this SQL clause
              (highlighted keywords in cyan)

Step 2 ─── [icon] [Title]
              ...

Step 3 ─── [icon] [Title]
              ...

Step 4 ─── [icon] [Title]
              ...
```

```css
.timeline { border-left: 2px solid rgba(34,211,238,0.2); padding-left: 20px; margin-top: 20px; }
.step     { position: relative; margin-bottom: 20px; }
.step-dot {
  position: absolute; left: -26px; top: 4px;
  width: 10px; height: 10px; border-radius: 50%;
  background: linear-gradient(135deg, #22d3ee, #8b5cf6);
}
.step-title { Inter 14px/600, color: #dee1f9; }
.step-body  { Inter 14px/400, color: #bbc9cd; margin-top: 4px; line-height: 1.6; }
```

---

## 6. BACKEND — SCHEMA CONTEXT (HARDCODED)

This Python dict must be defined at module level and injected into every system prompt. It is the schema contract that makes the AI schema-aware. Do not read from a DB at runtime.

```python
SCHEMA_CONTEXT = {
    "merchants": {
        "description": "Stores merchant profile and business information",
        "columns": {
            "id":         {"type": "INT",       "description": "Primary key, unique merchant identifier"},
            "name":       {"type": "VARCHAR",   "description": "Merchant display name"},
            "category":   {"type": "VARCHAR",   "description": "Business category (e.g., F&B, Retail, Services)"},
            "amount":     {"type": "DECIMAL",   "description": "Aggregated transaction volume for this merchant"},
            "created_at": {"type": "TIMESTAMP", "description": "Account creation timestamp"},
        },
        "sample_values": {
            "category": ["F&B", "Retail", "Services", "E-commerce"],
        }
    },
    "transactions": {
        "description": "Records every payment transaction processed through the platform",
        "columns": {
            "id":          {"type": "INT",       "description": "Primary key, unique transaction identifier"},
            "merchant_id": {"type": "INT",       "description": "Foreign key referencing merchants.id"},
            "name":        {"type": "VARCHAR",   "description": "Transaction reference name or label"},
            "amount":      {"type": "DECIMAL",   "description": "Transaction amount in local currency (VND)"},
            "status":      {"type": "VARCHAR",   "description": "Transaction status: completed | pending | failed"},
            "created_at":  {"type": "TIMESTAMP", "description": "Transaction timestamp in UTC"},
        },
        "sample_values": {
            "status": ["completed", "pending", "failed"],
        },
        "relationships": {
            "merchant_id": "REFERENCES merchants(id)"
        }
    }
}
```

---

## 7. SYSTEM PROMPTS — EXACT SPECIFICATIONS

### 7.1 Translate Vietnamese → SQL (System Prompt)

```python
TRANSLATE_SYSTEM_PROMPT = f"""
You are QueryMind AI, an expert SQL engineer embedded inside an analytics platform.
Your job is to translate Vietnamese business questions into production-ready SQL queries.

DATABASE SCHEMA:
You are working with a PostgreSQL database containing these tables:
{format_schema(SCHEMA_CONTEXT)}

RULES — FOLLOW STRICTLY:
1. Output ONLY a single SQL code block. Format: ```sql\\n<query>\\n```
2. Do NOT output any explanation, preamble, or commentary outside the code block.
3. Do NOT output markdown prose. Only the code block.
4. Use proper SQL formatting: each clause on a new line, uppercase keywords.
5. Prefer DATE_TRUNC for time-based grouping. Use 'month' granularity by default.
6. Always use explicit JOIN conditions, never implicit comma joins.
7. Add a single-line SQL comment at the top of the query: -- Generated by QueryMind AI
8. If the question is ambiguous, make the most reasonable business assumption and proceed.
9. Filter transactions to status = 'completed' unless the user asks otherwise.
10. Always alias aggregation columns descriptively (e.g., SUM(t.amount) AS total_revenue).
"""
```

### 7.2 Explain SQL Query (System Prompt)

```python
EXPLAIN_SYSTEM_PROMPT = f"""
You are QueryMind AI, a friendly and precise SQL instructor.
Your job is to explain SQL queries to non-technical Vietnamese Data Analysts.

DATABASE SCHEMA:
{format_schema(SCHEMA_CONTEXT)}

RULES — FOLLOW STRICTLY:
1. Structure your explanation into EXACTLY 4 steps.
2. Format MUST be:
   STEP 1: [Title in Vietnamese]
   [2-3 sentence explanation in Vietnamese, plain language, no jargon]

   STEP 2: [Title in Vietnamese]
   [explanation]

   STEP 3: [Title in Vietnamese]
   [explanation]

   STEP 4: [Title in Vietnamese]
   [explanation]

3. Use the format above verbatim. The frontend will parse "STEP N:" as a delimiter.
4. Reference actual column names from the schema where relevant.
5. Do NOT add any text before STEP 1 or after STEP 4.
6. Use simple, encouraging Vietnamese. Avoid "complex", "advanced", or intimidating language.
"""
```

### 7.3 `format_schema()` Helper Function

```python
def format_schema(schema: dict) -> str:
    lines = []
    for table, meta in schema.items():
        lines.append(f"TABLE: {table}")
        lines.append(f"  Description: {meta['description']}")
        for col, info in meta["columns"].items():
            lines.append(f"  - {col} ({info['type']}): {info['description']}")
        if "relationships" in meta:
            for col, ref in meta["relationships"].items():
                lines.append(f"  - {col} {ref}")
        lines.append("")
    return "\n".join(lines)
```

---

## 8. API ENDPOINTS

| Method | Path | Handler | Description |
|---|---|---|---|
| `GET` | `/` | `serve_landing` | Serve landing page HTML |
| `GET` | `/workspace` | `serve_workspace` | Serve workspace HTML |
| `POST` | `/api/translate` | `api_translate` | Vietnamese → SQL |
| `POST` | `/api/explain` | `api_explain` | SQL → Step explanation |

### 8.1 Request / Response Contracts

**POST `/api/translate`**
```python
# Request body
{"question": "string"}  # Vietnamese question from user

# Success response
{
  "sql": "SELECT ...",           # raw SQL string (no markdown fencing)
  "mode": "translate"
}

# Error response
{"error": "string", "code": 400}
```

**POST `/api/explain`**
```python
# Request body
{"sql": "string"}  # raw SQL to explain

# Success response
{
  "steps": [
    {"number": 1, "title": "...", "body": "..."},
    {"number": 2, "title": "...", "body": "..."},
    {"number": 3, "title": "...", "body": "..."},
    {"number": 4, "title": "...", "body": "..."},
  ],
  "mode": "explain"
}
```

### 8.2 Claude API Call Pattern

```python
import anthropic

client = anthropic.Anthropic()

def call_claude(system_prompt: str, user_message: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return message.content[0].text

def parse_sql_from_response(raw: str) -> str:
    """Strip ```sql fencing from Claude's output."""
    import re
    match = re.search(r"```sql\s*([\s\S]*?)\s*```", raw)
    return match.group(1).strip() if match else raw.strip()

def parse_steps_from_response(raw: str) -> list[dict]:
    """Parse STEP N: Title / body format into structured list."""
    import re
    steps = []
    pattern = r"STEP (\d+):\s*(.+?)\n([\s\S]*?)(?=STEP \d+:|$)"
    for match in re.finditer(pattern, raw.strip(), re.MULTILINE):
        steps.append({
            "number": int(match.group(1)),
            "title":  match.group(2).strip(),
            "body":   match.group(3).strip()
        })
    return steps
```

---

## 9. FRONTEND JAVASCRIPT BEHAVIOR

All JavaScript must be inline `<script>` within the HTML strings. No external JS files.

### 9.1 Mode Tab Switching
```javascript
// On tab click: update active class, change textarea placeholder, clear results
function switchMode(mode) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(`tab-${mode}`).classList.add('active');
  currentMode = mode;
  const placeholders = {
    translate: "Ví dụ: Lấy tổng doanh thu của từng merchant trong tháng này...",
    explain:   "Ví dụ: Dán SQL phức tạp vào đây để tôi giải thích từng bước..."
  };
  document.getElementById('main-input').placeholder = placeholders[mode];
}
```

### 9.2 Generate Insight Button
```javascript
async function generateInsight() {
  const input = document.getElementById('main-input').value.trim();
  if (!input) return;

  setLoading(true);

  try {
    if (currentMode === 'translate') {
      const res = await fetch('/api/translate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question: input})
      });
      const data = await res.json();
      renderSQL(data.sql);
    } else {
      const res = await fetch('/api/explain', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({sql: input})
      });
      const data = await res.json();
      renderExplanation(data.steps);
    }
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
}
```

### 9.3 Quick Query Tags
```javascript
const QUICK_QUERIES = {
  "Top Merchants by GMV":   "Cho tôi thấy top 10 merchant có tổng giá trị giao dịch (GMV) cao nhất trong tháng này",
  "Fast Growth List":       "Liệt kê các merchant có tốc độ tăng trưởng doanh thu nhanh nhất so với tháng trước",
  "Failure Rate Analysis":  "Phân tích tỷ lệ giao dịch thất bại theo từng merchant, sắp xếp từ cao đến thấp"
};

function fillQuery(label) {
  document.getElementById('main-input').value = QUICK_QUERIES[label];
  switchMode('translate');
}
```

### 9.4 Copy Code Action
```javascript
function copySQL() {
  const code = document.getElementById('sql-output').innerText;
  navigator.clipboard.writeText(code).then(() => {
    showToast('Copied to clipboard!');
  });
}
```

### 9.5 Download .sql Action
```javascript
function downloadSQL() {
  const code = document.getElementById('sql-output').innerText;
  const blob = new Blob([code], {type: 'text/plain'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'query_v1_insight.sql';
  a.click();
}
```

---

## 10. MODAL CLOUD CONFIGURATION

```python
import modal

app = modal.App("querymind-ai")

# Secrets: Anthropic API key must be set in Modal dashboard as secret "anthropic-api-key"
# Access via: os.environ["ANTHROPIC_API_KEY"]

@app.function(
    secrets=[modal.Secret.from_name("anthropic-api-key")],
    # No image customization needed — use default Modal image
)
@modal.asgi_app()
def fastapi_app():
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse, JSONResponse
    app = FastAPI()
    # ... routes attached here
    return app
```

**Deploy command (exactly this, nothing else):**
```bash
modal deploy app.py
```

---

## 11. IMPLEMENTATION CHECKLIST

Before marking `app.py` complete, verify every item:

### Structure
- [ ] Single `app.py` file, no imports from sub-modules
- [ ] Sections ordered per Section 2 architecture map
- [ ] `modal deploy app.py` succeeds without errors

### Design Fidelity
- [ ] Background is `#0B1020`, not `#000` or `#111`
- [ ] All glassmorphism panels use `rgba(255,255,255,0.03–0.08)` + `backdrop-filter: blur(12–20px)`
- [ ] All border-radius values match Section 3.5 tokens
- [ ] Primary buttons use `linear-gradient(135deg, #22d3ee 0%, #8b5cf6 100%)`
- [ ] Inter loaded for UI, Geist Mono for code/labels
- [ ] SQL syntax highlighting uses the exact color tokens from Section 3.7
- [ ] Pulse animation on DB status dot is present
- [ ] Active mode tab has glow box-shadow

### Backend
- [ ] `SCHEMA_CONTEXT` dict is hardcoded with all fields from Section 6
- [ ] `format_schema()` helper is defined
- [ ] Both system prompts are implemented verbatim
- [ ] `parse_sql_from_response()` strips ```sql fencing
- [ ] `parse_steps_from_response()` returns list of 4 dicts
- [ ] `/api/translate` returns `{"sql": "...", "mode": "translate"}`
- [ ] `/api/explain` returns `{"steps": [...], "mode": "explain"}`

### Pages
- [ ] Landing page has: nav, hero (left copy + right animated card), 3 feature cards, CTA banner, footer
- [ ] Workspace has: header, sidebar with schema tree + DB status, mode tabs, input zone, quick queries, SQL card with terminal header, step timeline
- [ ] "Start Querying" button on landing navigates to `/workspace`
- [ ] Sidebar schema tree correctly shows all columns with type icons

### UX Details
- [ ] Quick Query tags pre-fill the textarea on click
- [ ] Mode switch changes placeholder text
- [ ] Copy Code writes to clipboard
- [ ] Download .sql triggers file download as `query_v1_insight.sql`
- [ ] "Explain Every Step" toggle shows/hides the timeline section
- [ ] Loading state on Generate Insight button (spinner or animated gradient)

---

## 12. STRICT RULES FOR CLAUDE CODE

These rules apply when Claude Code generates code for this project:

1. **Never invent colors.** Always use exact hex/rgba values from Section 3.1.
2. **Never use Tailwind utility classes.** Write all CSS as inline styles or `<style>` blocks within the HTML strings.
3. **Never break the single-file constraint.** All HTML, CSS, JS, and Python live in `app.py`.
4. **Never use LangChain, LlamaIndex, or any orchestration framework.**
5. **Never use `requests` or `httpx` to call Claude.** Use the `anthropic` SDK exclusively.
6. **Never hardcode the Anthropic API key** in the source. Always use `os.environ["ANTHROPIC_API_KEY"]`.
7. **Never remove the schema context** from system prompts. Every Claude call must be schema-aware.
8. **Never output SQL without stripping fencing.** The API must return raw SQL strings.
9. **Always return exactly 4 steps** from the explain endpoint.
10. **Match the mockup images** in `./web_pic/` as the final visual reference. When in doubt, look at the image.

---

*End of CLAUDE.md — QueryMind AI v1.0*
*Generated by analysis of: `./web_pic/landing_page.png`, `./web_pic/workspace.png`, `./web_pic/landing_page_DESIGN.md`, `./web_pic/workspace_DESIGN.md`, and PRD specification.*
