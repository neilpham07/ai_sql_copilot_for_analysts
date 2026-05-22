---
name: Synthetix Lumina
colors:
  surface: '#0e1323'
  surface-dim: '#0e1323'
  surface-bright: '#34394a'
  surface-container-lowest: '#080d1d'
  surface-container-low: '#161b2b'
  surface-container: '#1a1f30'
  surface-container-high: '#25293a'
  surface-container-highest: '#2f3446'
  on-surface: '#dee1f9'
  on-surface-variant: '#bbc9cd'
  inverse-surface: '#dee1f9'
  inverse-on-surface: '#2b3041'
  outline: '#859397'
  outline-variant: '#3c494c'
  surface-tint: '#2fd9f4'
  primary: '#8aebff'
  on-primary: '#00363e'
  primary-container: '#22d3ee'
  on-primary-container: '#005763'
  inverse-primary: '#006877'
  secondary: '#d0bcff'
  on-secondary: '#3c0091'
  secondary-container: '#571bc1'
  on-secondary-container: '#c4abff'
  tertiary: '#d0ddff'
  on-tertiary: '#002e6a'
  tertiary-container: '#a5c1ff'
  on-tertiary-container: '#004ba5'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#a2eeff'
  primary-fixed-dim: '#2fd9f4'
  on-primary-fixed: '#001f25'
  on-primary-fixed-variant: '#004e5a'
  secondary-fixed: '#e9ddff'
  secondary-fixed-dim: '#d0bcff'
  on-secondary-fixed: '#23005c'
  on-secondary-fixed-variant: '#5516be'
  tertiary-fixed: '#d8e2ff'
  tertiary-fixed-dim: '#adc6ff'
  on-tertiary-fixed: '#001a42'
  on-tertiary-fixed-variant: '#004395'
  background: '#0e1323'
  on-background: '#dee1f9'
  surface-variant: '#2f3446'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-max: 1440px
  gutter: 24px
  margin-desktop: 64px
  margin-mobile: 20px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style
The design system embodies a "Hyper-Functional Futurism" aesthetic, blending the systematic precision of developer tools with the ethereal quality of advanced intelligence. It is designed for high-performance AI SaaS environments where clarity, speed, and technical depth are paramount.

The style is rooted in **Glassmorphism** and **Modern Minimalism**. It utilizes deep obsidian surfaces to provide a high-contrast stage for vibrant, neon-tinted data and interactive elements. The emotional response should be one of "infinite capability"—the UI feels like a sophisticated HUD that is both powerful and unobtrusive. Heavy use of background blurs, semi-transparent strokes, and subtle radial gradients creates a sense of spatial depth without visual clutter.

## Colors
The palette is anchored in a deep navy/slate foundation (#0B1020), providing a near-black canvas that preserves organic depth. 

- **Primary (Cyan):** Used for primary actions and active states, representing "Intelligence."
- **Secondary (Violet):** Used for generative AI features, magic moments, and accent gradients.
- **Tertiary (Blue):** Used for information density, links, and steady-state UI.
- **Glass Surfaces:** Layers are constructed using white alphas (3%–8%) rather than solid greys to maintain the glass effect when overlapping gradients.
- **Accents:** Neon accents should be applied via `box-shadow` glows or `linear-gradient` borders to simulate light emission.

## Typography
This design system utilizes **Inter** for all core interface elements to ensure maximum legibility and a neutral, professional tone. To lean into the "Developer/SaaS" aesthetic, **Geist** (or a clean monospaced alternative) is introduced for labels, metadata, and code snippets to provide a technical edge.

- **Headlines:** Use tight letter spacing and semi-bold weights to create a "locked-in" look.
- **Body:** Standardized on 16px for optimal readability against dark backgrounds.
- **Labels:** Use uppercase for small labels (`label-sm`) with increased tracking to improve scannability in dense dashboards.

## Layout & Spacing
The layout follows a **12-column fluid grid** for desktop, transitioning to a **4-column grid** for mobile. The philosophy is "Dense but Breathable"—information is packed efficiently, but separated by generous outer margins and clear stack heights.

- **Grid:** Use a 24px gutter to allow the glassmorphic panels enough negative space to let the background gradients "breathe" through the gaps.
- **Padding:** Internal card padding should scale from 16px (mobile) to 24px or 32px (desktop) to maintain a premium, spacious feel.
- **Alignment:** Strict adherence to a 4px baseline grid for all vertical rhythm.

## Elevation & Depth
Depth is not communicated through traditional black shadows, but through **Tonal Layering** and **Backdrop Filtering**.

- **Level 0 (Background):** Solid #0B1020 with occasional deep-seated radial gradients (Cyan/Violet at 5% opacity).
- **Level 1 (Panels):** `background: rgba(255, 255, 255, 0.03)`, `backdrop-filter: blur(12px)`, and a 1px border of `rgba(255, 255, 255, 0.08)`.
- **Level 2 (Popovers/Modals):** Same as Level 1 but with a 1px border of `rgba(255, 255, 255, 0.15)` and a subtle outer glow using the primary color at 10% opacity.
- **Edge Lighting:** Use a "top-light" effect—a subtle linear gradient on the border (from transparent to white-alpha to transparent) to simulate light hitting the top edge of the glass.

## Shapes
The shape language is characterized by "Large-Radius Sophistication." 

- **Primary Containers:** Use `rounded-xl` (24px) for main dashboard cards and large panels to create a soft, friendly container for technical data.
- **Standard Components:** Buttons and input fields use `rounded-lg` (16px) to maintain a consistent language with the containers.
- **Micro-Elements:** Tooltips and tags use `rounded-sm` (4px) to remain distinct from larger structural elements.

## Components
- **Buttons:** 
  - *Primary:* Solid Cyan gradient with black text for high contrast. 
  - *Secondary:* Glass background with a white 1px border and white text.
  - *Ghost:* No background, Cyan text, appears on hover with a 5% alpha background.
- **Input Fields:** Semi-transparent dark fills with a 1px border. On focus, the border transitions to a Cyan/Violet gradient and the field gains a subtle inner glow.
- **Chips/Tags:** Rounded-pill shapes with a low-opacity tint of the category color (e.g., a green tint for "Success" labels).
- **Glass Cards:** The signature component. Must include `backdrop-filter: blur(20px)` and a subtle inner shadow (1px) to define the edge.
- **AI Response Block:** Distinguished by a very subtle animated border-gradient (Cyan to Violet) and a unique "magic" icon prefix.
- **Lists:** Separated by low-opacity horizontal lines (10% white) with high-contrast Inter typography for titles.