---
description: Full spec for the workspace page at GET /workspace. Header, sidebar schema tree, mode tabs, input zone, SQL output card, and explanation timeline.
globs: ["app.py", "workspace.html"]
---

# Workspace Page Spec (`/workspace`)

## Page Layout

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

## App Header

```
Height: 60px
Background: rgba(11,16,32,0.9) + backdrop-filter: blur(16px)
Border-bottom: 1px solid rgba(255,255,255,0.06)
Layout: [Logo left] [Nav center] [Icons right]

Left:    "QueryMind AI" wordmark + "AI POWERED V1.0" badge pill (cyan)
Center:  Pill nav — Query (active, gradient bg) | Dashboards | Notebooks
Right:   Notification bell + Settings gear + Avatar circle
```

## Left Sidebar

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
- Title: "Database Schema" (Inter 16px/600, #dee1f9)
- Badge: "v2.4 Stable" (Geist Mono 11px, #4ade80, bg: rgba(74,222,128,0.1), border: rgba(74,222,128,0.2))
- Layout: space-between row

**Search input:**
```css
background: rgba(255,255,255,0.04);
border: 1px solid rgba(255,255,255,0.08);
border-radius: 10px;
padding: 10px 14px;
color: #dee1f9;
font-size: 14px;
width: 100%;
```

**Schema Tree:**
```
▾ merchants
    id            INT        [# cyan]
    name          VARCHAR    [T violet]
    category      VARCHAR    [T violet]
    amount        DECIMAL    [≈ green]
    created_at    TIMESTAMP  [⏱ amber]

▾ transactions
    id            INT
    merchant_id   INT
    name          VARCHAR
    amount        DECIMAL
    status        VARCHAR
    created_at    TIMESTAMP
```

Tree row hover: `background: rgba(34, 211, 238, 0.06)`

**Sidebar Footer (pinned bottom):**
- `margin-top: auto; border-top: 1px solid rgba(255,255,255,0.06);`
- Pulse green dot + "Connected to Production DB" + "LIVE SYNC ENABLED"
- [Upgrade to Pro] ghost button with violet border, full width

## Main Workspace

```css
.workspace {
  flex: 1;
  padding: 28px 32px;
  overflow-y: auto;
  height: calc(100vh - 60px);
}
```

## Mode Tabs

```
Pill container (glass bg, border-radius: 9999px)
Tab 1: "⟲ Translate Vietnamese to SQL"  — ACTIVE by default
Tab 2: "⟴ Explain SQL Query"

Active:   gradient bg (cyan→violet), black text, glow shadow
Inactive: transparent, muted text
```

## Input Zone Card

```css
.input-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 20px 24px;
  margin-top: 20px;
}
```

- Textarea: multi-line, min-height 80px, Inter 16px, #dee1f9
- Placeholder mode 1: `"Ví dụ: Lấy tổng doanh thu của từng merchant trong tháng này"`
- Placeholder mode 2: `"Ví dụ: Dán SQL phức tạp vào đây để tôi giải thích từng bước..."`
- Bottom row left: 🎤 voice | 📎 attachment | divider | Schema-aware toggle | Auto-optimize toggle
- Bottom row right: [Generate Insight →] gradient button

## Quick Queries Row

```
Label: "QUICK QUERIES:"  Geist Mono 11px UPPERCASE, #4a5568, letter-spacing: 0.08em

Clickable pills:
  ⚡ "Top Merchants by GMV"
  📈 "Fast Growth List"
  ⚠  "Failure Rate Analysis"
```

On click: populate textarea + switch to translate mode.

## SQL Output Card

**Header:**
- Left: ● red ● yellow ● green + filename `"query_v1_insight.sql"`
- Right: [Copy Code] [↓ Download .sql]
- `border-bottom: 1px solid rgba(255,255,255,0.06)`

**SQL code block:** syntax-highlighted with `.kw`, `.fn`, `.str`, `.num`, `.col`, `.cmt` classes.

**Action row:**
- [Copy Code] [Download .sql] [Explain Every Step ▾] — ghost buttons

## Step-by-Step Explanation Timeline

Shown below SQL card when "Explain Every Step" is active.

```css
.timeline { border-left: 2px solid rgba(34,211,238,0.2); padding-left: 20px; margin-top: 20px; }
.step     { position: relative; margin-bottom: 20px; }
.step-dot {
  position: absolute; left: -26px; top: 4px;
  width: 10px; height: 10px; border-radius: 50%;
  background: linear-gradient(135deg, #22d3ee, #8b5cf6);
}
.step-title { font: Inter 14px/600; color: #dee1f9; }
.step-body  { font: Inter 14px/400; color: #bbc9cd; margin-top: 4px; line-height: 1.6; }
```

Always renders exactly **4 steps** from the explain endpoint response.
