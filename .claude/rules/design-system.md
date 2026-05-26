---
description: Synthetix Lumina design system — exact CSS tokens, glassmorphism levels, typography, spacing, and all component specs. Every value is mandatory; do not approximate.
globs: ["**/*.html", "app.py"]
---

# Design System — "Synthetix Lumina"

Derived from `./web_pic/landing_page.png` and `./web_pic/workspace.png`. Every CSS value is **exact and mandatory**. Do not approximate or substitute.

## Color Palette

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

## Gradient Tokens

```css
/* Primary CTA gradient — used on "Start Querying" and "Generate Insight" buttons */
--gradient-cta:     linear-gradient(135deg, #22d3ee 0%, #8b5cf6 100%);

/* Hero ambient glow */
--gradient-hero-cyan:   radial-gradient(ellipse 60% 50% at 70% 40%, rgba(34,211,238,0.07) 0%, transparent 70%);
--gradient-hero-violet: radial-gradient(ellipse 50% 60% at 30% 60%, rgba(139,92,246,0.06) 0%, transparent 70%);

/* Animated AI response border */
--gradient-ai-border:   linear-gradient(90deg, #22d3ee, #8b5cf6, #22d3ee);
```

## Typography

Font loading (required in `<head>` of all pages):
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

## Spacing & Layout

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

## Border Radius

```css
--radius-sm:   4px;    /* Tooltips, tags, micro-elements */
--radius-md:  12px;    /* Standard elements */
--radius-lg:  16px;    /* Buttons, inputs */
--radius-xl:  24px;    /* Primary containers, main panels */
--radius-full: 9999px; /* Pills, badges, circular icons */
```

## Glassmorphism System (Elevation Levels)

```css
/* LEVEL 0 — Background canvas */
background: #0B1020;
/* + ambient radial gradient blooms */

/* LEVEL 1 — Panels, sidebars, standard cards */
background: rgba(255, 255, 255, 0.03);
backdrop-filter: blur(12px);
-webkit-backdrop-filter: blur(12px);
border: 1px solid rgba(255, 255, 255, 0.08);
border-top: 1px solid rgba(255, 255, 255, 0.12);  /* "Top-light" edge */

/* LEVEL 2 — Active cards, modals, result zones */
background: rgba(255, 255, 255, 0.05);
backdrop-filter: blur(20px);
-webkit-backdrop-filter: blur(20px);
border: 1px solid rgba(255, 255, 255, 0.15);
box-shadow: 0 0 24px rgba(34, 211, 238, 0.06);

/* LEVEL 3 — AI response block (special) */
background: rgba(255, 255, 255, 0.04);
backdrop-filter: blur(20px);
/* border animated via --gradient-ai-border pseudo-element */
```

## Component Specs

### Primary Button
```css
background: linear-gradient(135deg, #22d3ee 0%, #8b5cf6 100%);
color: #000;
font-family: Inter;
font-size: 16px;
font-weight: 600;
padding: 14px 28px;
border-radius: 16px;
border: none;
cursor: pointer;
transition: transform 0.2s ease, box-shadow 0.2s ease;

/* Hover */
transform: translateY(-2px);
box-shadow: 0 8px 32px rgba(34, 211, 238, 0.35);
```

### Secondary / Ghost Button
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

### Input Field
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

/* Focus */
border-color: transparent;
background-image: linear-gradient(#1a1f30, #1a1f30),
                  linear-gradient(135deg, #22d3ee, #8b5cf6);
background-origin: border-box;
background-clip: padding-box, border-box;
box-shadow: 0 0 0 1px transparent inset, 0 0 16px rgba(34,211,238,0.15);
```

### Mode Tab Pills
```css
/* Container */
background: rgba(255, 255, 255, 0.04);
border: 1px solid rgba(255, 255, 255, 0.08);
border-radius: 9999px;
padding: 4px;
display: inline-flex;

/* Inactive tab */
.tab { padding: 8px 20px; border-radius: 9999px; color: #bbc9cd; font-size: 14px; font-weight: 500; }

/* Active tab */
.tab.active {
  background: linear-gradient(135deg, #22d3ee 0%, #8b5cf6 100%);
  color: #000;
  font-weight: 600;
  box-shadow: 0 0 20px rgba(34,211,238,0.3);
}
```

### Quick Query Tags
```css
background: rgba(255, 255, 255, 0.06);
border: 1px solid rgba(255, 255, 255, 0.1);
border-radius: 9999px;
color: #bbc9cd;
font-family: Geist Mono;
font-size: 13px;
padding: 6px 14px;
cursor: pointer;

/* Hover */
background: rgba(34, 211, 238, 0.08);
border-color: rgba(34, 211, 238, 0.3);
color: #8aebff;
```

### SQL Terminal Card
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
/* macOS-style dots */
.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot-red    { background: #ff5f57; }
.dot-yellow { background: #ffbd2e; }
.dot-green  { background: #28c840; }

.sql-filename { font-family: Geist Mono; font-size: 13px; color: #bbc9cd; margin-left: 8px; }
.sql-code { padding: 20px; font-family: Geist Mono; font-size: 13px; line-height: 1.7; overflow-x: auto; }
```

### SQL Syntax Highlighting
```
.kw   { color: #c4abff; }   /* SELECT, FROM, WHERE, JOIN, GROUP BY, ORDER BY, AS, AND, ON */
.fn   { color: #22d3ee; }   /* SUM(), COUNT(), DATE_TRUNC(), AVG() */
.str  { color: #86efac; }   /* string literals */
.num  { color: #fca5a5; }   /* numbers */
.col  { color: #dee1f9; }   /* column/table names */
.cmt  { color: #4a5568; font-style: italic; }  /* -- comments */
```

### Live DB Status Badge
```css
.db-status-badge {
  display: flex; align-items: center; gap: 8px;
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

### Data Type Icons (Schema Tree)
```
INT       → "#"   color: #22d3ee
VARCHAR   → "T"   color: #d0bcff
TIMESTAMP → "⏱"  color: #fbbf24
DECIMAL   → "≈"   color: #86efac
```
