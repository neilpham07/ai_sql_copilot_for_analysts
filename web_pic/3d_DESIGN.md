---
name: AI SQL Copilot For Analysts
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#bdc8d1'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#87929a'
  outline-variant: '#3e484f'
  surface-tint: '#7bd0ff'
  primary: '#8ed5ff'
  on-primary: '#00354a'
  primary-container: '#38bdf8'
  on-primary-container: '#004965'
  inverse-primary: '#00668a'
  secondary: '#ddb7ff'
  on-secondary: '#490080'
  secondary-container: '#6f00be'
  on-secondary-container: '#d6a9ff'
  tertiary: '#3ce0fb'
  on-tertiary: '#00363e'
  tertiary-container: '#00c3dd'
  on-tertiary-container: '#004b56'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#c4e7ff'
  primary-fixed-dim: '#7bd0ff'
  on-primary-fixed: '#001e2c'
  on-primary-fixed-variant: '#004c69'
  secondary-fixed: '#f0dbff'
  secondary-fixed-dim: '#ddb7ff'
  on-secondary-fixed: '#2c0051'
  on-secondary-fixed-variant: '#6900b3'
  tertiary-fixed: '#a2eeff'
  tertiary-fixed-dim: '#2fd9f4'
  on-tertiary-fixed: '#001f25'
  on-tertiary-fixed-variant: '#004e5a'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  display-lg:
    fontFamily: Geist
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Geist
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '450'
    lineHeight: 24px
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '450'
    lineHeight: 18px
  label-caps:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 40px
  xl: 64px
  gutter: 20px
  container-max: 1440px
---

## Brand & Style
The design system is engineered for the modern data analyst, balancing technical power with an intuitive, approachable interface. The brand personality is "The Intelligent Partner"—expert, precise, and forward-thinking.

The visual style is **Corporate Modern with a "Tech-Luxe" edge**, utilizing elements of **Glassmorphism** and subtle **Neon-Brutalism**. It avoids the intimidating complexity of traditional database IDEs by using generous white space (negative space), soft depth through backdrop blurs, and vibrant accent glows that signify AI activity. The interface should feel like a high-end command center that reduces cognitive load rather than adding to it.

## Colors
The palette is rooted in deep, immersive dark tones to reduce eye strain during long analytical sessions. 

- **Base Layer:** The deepest slate (#0f172a) is used for the primary application background and sidebars.
- **Surface Layer:** Midnight blue (#1e293b) defines cards, panels, and elevated surfaces.
- **AI Accents:** Neon Blue (#38bdf8) and Purple (#a855f7) are reserved for primary actions and AI-generated content. These are often used as gradients to represent the "flow" of data.
- **Semantic Colors:** Cyan (#22d3ee) serves as the primary status indicator for active queries, while Emerald (#10b981) confirms successful executions and data exports.

## Typography
This design system utilizes **Geist** for all UI elements to ensure maximum clarity and a distinctively modern, technical feel. Its high x-height and geometric construction make it ideal for data-dense applications.

**JetBrains Mono** is employed for all SQL input, output, and data schema references. It provides the necessary rhythmic spacing required to scan complex queries efficiently. 

- Use **Display** styles for empty-state messaging or landing dashboards.
- Use **Code-md** for the primary SQL editor.
- Use **Label-caps** (uppercase) for table headers and metadata descriptors.

## Layout & Spacing
The layout follows a **Fixed-Fluid Hybrid** model. The sidebar and query-builder panels occupy fixed widths (280px and 400px respectively), while the central SQL editor and results grid expand to fill the remaining viewport.

- **Rhythm:** A strict 8px grid governs all component dimensions.
- **Padding:** We use "Generous Breathing Room." Editor panels should have a minimum of 24px (md) internal padding to separate the code from the UI chrome.
- **Margins:** 20px gutters are used between primary workspace modules to allow for subtle "glow" shadows to bleed without overlapping.
- **Mobile/Tablet:** On smaller screens, sidebars collapse into a drawer, and the data results grid enables horizontal scrolling with pinned ID columns.

## Elevation & Depth
Depth is created through **Tonal Layering** and **Luminescent Outlines** rather than heavy black shadows.

1.  **Level 0 (Base):** #0f172a.
2.  **Level 1 (Panels):** #1e293b with a 1px solid border at 10% white opacity.
3.  **Level 2 (Modals/Popovers):** #1e293b with a 1px solid border at 20% white opacity and a 40px blur shadow with 5% primary color tint.
4.  **AI State:** Components currently processing or suggesting code receive a 1px "Glow Border" using a linear gradient of Neon Blue to Purple.
5.  **Backdrop:** Use a 12px blur on all modal overlays to maintain context while focusing the analyst.

## Shapes
The shape language is sophisticated and friendly. We use **Rounded (2)** as the standard to soften the "hard" nature of data and code.

- **Cards & Panels:** Use `rounded-xl` (1.5rem / 24px) to create a containerized, "app-like" feel.
- **Buttons & Inputs:** Use `rounded-lg` (1rem / 16px) for a modern, tactile interaction surface.
- **Code Blocks:** Use `rounded-md` (0.5rem / 8px) to keep the internal code structure feeling organized.
- **Tabs:** Use top-only rounding for active tab states to anchor them to their respective panels.

## Components

### Buttons
- **Primary:** Gradient background (Neon Blue to Purple), white text, `rounded-lg`. On hover, add a 4px outer glow of the primary color.
- **Secondary:** Transparent background with a 1px border (#38bdf8), text in Neon Blue.
- **Ghost:** No border or background; subtle #1e293b background appear on hover.

### Terminal Cards
The SQL editor and result sets are housed in "Terminal Cards." These feature a darker header (#0f172a) with `rounded-t-xl` corners and 3 window control dots (Mac-style) for a professional IDE aesthetic.

### Chips & Badges
Used for SQL Keywords and Table Names. Use a high-alpha background of the secondary color (e.g., Purple at 15% opacity) with solid colored text. Sharp `rounded-md` for these smaller elements.

### Inputs & SQL Editor
Text inputs use the Surface color (#1e293b) with a subtle 1px border. When focused, the border transitions to a Neon Blue glow. The SQL editor must feature line numbers and a vertical "indentation guide" line in a muted slate.

### Tab Navigation
Large, pill-like tabs for switching between "Query Editor," "Schema Browser," and "Execution History." The active tab should have a subtle bottom-glow using the Primary color.

### Data Grid
The results table uses `body-sm` typography. Alternating row colors (Zebra striping) is avoided in favor of 1px horizontal dividers at 5% opacity to keep the look clean and professional.