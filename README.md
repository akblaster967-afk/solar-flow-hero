# Solar Flow: Animated Hero Infographic

A full-width, animated infographic hero for a solar-energy website, designed to
drop straight into an Elementor HTML widget. It visualizes the **"How Solar
Works"** flow: **Sunlight → Solar Panels → Inverter → Your Home → Bill Savings**.

## Deliverables

| File | What it is |
|------|------------|
| `solar-flow-elementor.html` | **The drop-in file.** Paste the entire contents into an Elementor HTML widget. All CSS + SVG are inline. No external requests, no JS dependencies. |
| `solar-flow-source.svg` | **Editable vector source** for the static artwork. Open in Adobe Illustrator or import into Figma to edit shapes, colors, and labels. |
| `src/SolarHero.jsx` + `src/hero.css` | React (JSX) + CSS source used for the live dev preview (same artwork/animation as the drop-in file). |
| `index.html`, `src/main.jsx`, `vite.config.ts`, `package.json` | Vite project scaffolding for the live preview (plain JSX, no TypeScript). |

## How the animation works

- **Entrance (loops once):** Each node (sun, panel, inverter, home, savings)
  pops in with a spring ease, staggered ~0.2s apart. Connectors and labels
  fade in between nodes. Total reveal ~1.5s, then it settles.
- **Ambient (continuous, subtle):** sun glow pulses, rays slowly rotate and
  twinkle, energy-flow dashes travel along each connector, the inverter
  waveform pulses, and the savings coin gently bobs. All driven by pure CSS
  `@keyframes`. No JavaScript.
- **Accessibility:** `prefers-reduced-motion` disables every animation and
  shows the static infographic instantly.

## Performance

- No images, no fonts, no JS framework, no external requests.
- The entire drop-in is a single self-contained HTML snippet (~15 KB, < 4 KB gzipped).
- Works in all modern browsers; the SVG scales fluidly via `viewBox` so it is
  responsive from mobile to desktop with no media-query hacks.

## Using in Elementor

1. Add a new Section (1 column, full width / content width).
2. Drag an **HTML** widget into the column.
3. Open `solar-flow-elementor.html`, copy the **entire** file, paste into the
   HTML widget's code field.
4. Update / publish. Done.

## Editing the artwork

- **Vector art:** open `solar-flow-source.svg` in Illustrator or Figma. Edit
  colors, shapes, icons, or labels, then re-export as SVG.
- **Animation:** timing lives in the `@keyframes` and `animation` rules near
  the top of `solar-flow-elementor.html` (inside `<style>`). Adjust durations
  / delays there, or re-create the same layer animation in After Effects by
  importing the SVG and animating the matching groups (sun-glow, sun-rays,
  flow lines, wave, coin).
- **Copy:** the heading, subtitle, and per-node labels are plain text in the
  HTML. Edit them in place.

## Live preview (local)

```
npm install
npm run dev
```
