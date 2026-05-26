---
description: Full spec for the landing page at GET /. Structure, nav, hero section, feature cards, CTA banner, and footer.
globs: ["app.py"]
---

# Landing Page Spec (`/`)

## Page Structure (Top → Bottom)

```
<body>                         background: #0B1020 + ambient radial gradients
  <nav>                        Fixed top, glassmorphism Level 1
  <main>
    <section.hero>             Full viewport, centered vertically
    <section.features>         3-column card grid
    <section.cta-banner>       Full-width gradient CTA strip
    <footer>                   Simple dark footer
```

## Navigation Bar

```
[QueryMind AI logo + wordmark]    [Docs] [Features] [Customers] [Changelog]    [Sign In] [Start Free →]

Height: 64px
Background: rgba(11,16,32,0.8) with backdrop-filter: blur(20px)
Border-bottom: 1px solid rgba(255,255,255,0.06)
Position: sticky top-0 z-50
Logo: "QueryMind AI" Inter 700, with small cyan sparkle SVG icon
Nav links: Inter 14px, color: #bbc9cd, hover: #dee1f9
"Start Free" button: gradient CTA (smaller padding: 10px 20px)
```

## Hero Section

**Left Column (55% width):**
```
Badge pill:    "✦ AI POWERED V1.0"
               bg: rgba(34,211,238,0.08), border: 1px solid rgba(34,211,238,0.2)
               color: #22d3ee, font: Geist Mono 12px UPPERCASE letter-spacing: 0.1em
               border-radius: 9999px, padding: 6px 14px

Headline (h1): "Ask Questions in Vietnamese.
                Get Production-Ready SQL Instantly."
               Inter 48px/700, color: #dee1f9, letter-spacing: -0.02em, line-height: 1.1
               max-width: 580px

Subheadline:   "An AI engine designed for Data Analysts..."
               Inter 18px/400, color: #bbc9cd, line-height: 1.6, max-width: 480px, margin-top: 20px

CTA Row:       [Start Querying →] [▷ See Demo]   gap: 12px, margin-top: 32px
```

**Right Column (45% width):**
```
Animated mockup card (Level 2 glass):
  - Shows Vietnamese text input → SQL conversion animation
  - Top: "Cho tôi thấy top 10 merchant theo doanh thu tháng này"
  - Arrow animation downward
  - Bottom: SQL code block with syntax highlighting
  - Background glow: radial cyan/violet at 15% opacity
  - Card border: animated --gradient-ai-border
  - border-radius: 24px
```

## Feature Cards Section

```
Header:    "Engineered for Technical Depth"   Inter 32px/600, centered, #dee1f9
Sub:       "Three ways QueryMind AI makes every analyst a SQL expert."  Inter 16px/400, #bbc9cd
Layout:    3 columns, gap: 24px, margin-top: 48px
Card:      Level 1 glassmorphism, border-radius: 24px, padding: 32px
```

**Card 1 — Vietnamese → SQL**
- Icon: ✦ Sparkles (cyan gradient fill), 40px
- Title: "Vietnamese → SQL" (Inter 20px/600)
- Body: "Describe your data question naturally in Vietnamese..." (Inter 15px/400, #bbc9cd, line-height: 1.6)
- Tag: "NLP Translation" (label-sm chip, cyan tint)

**Card 2 — Explain Complex Queries**
- Icon: 🧠 Brain (violet gradient fill), 40px
- Title: "Explain Complex Queries" (Inter 20px/600)
- Body: "Paste any SQL query and receive a plain-language, step-by-step breakdown..."
- Tag: "Query Intelligence" (label-sm chip, violet tint)

**Card 3 — Schema-Aware Query Generation**
- Icon: 🗄 Database (blue gradient fill), 40px
- Title: "Schema-Aware Query Generation" (Inter 20px/600)
- Body: "QueryMind AI has deep knowledge of your table schemas..."
- Tag: "Schema Intelligence" (label-sm chip, blue tint)

## CTA Banner Section

```
Background:  radial gradient bloom + Level 1 glass card, border-radius: 24px
Headline:    "Transform your data workflow today."  Inter 32px/700, centered
Subtext:     "Join analysts who ship data insights 10x faster."  Inter 16px, #bbc9cd
Buttons:     [Start Free Trial] [Talk to Sales]  — centered row, gap: 16px
```

## Footer

```
Left:    QueryMind AI logo + "© 2025 QueryMind AI. All rights reserved."
Center:  Privacy Policy | Terms of Service | Contact
Right:   (optional) social icon links

Background: rgba(255,255,255,0.02)
Border-top: 1px solid rgba(255,255,255,0.06)
Padding: 32px 64px
Font: Inter 14px, color: #4a5568
```

## Navigation Behavior

"Start Querying" button → navigates to `/workspace`
