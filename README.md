# The Companion Room

A premium resident pet-spa concept prepared by Mel Tucker / AVC for a proposed downtown East Lansing apartment building.

Canonical share URL: https://meltckr.github.io/the-companion-room/

## Experience

- Cinematic 360-degree views rendered from the actual room geometry with Blender Cycles: arrival, wash/dry bays and finishing counter. Touch drag and pinch zoom; fixed viewpoints.
- A separate native WebGL spatial model supports free movement, five cameras, a third-bay study and PNG export.
- Responsive plan, four-season operating notes, transparent demand calculator, equipment shortlist, capital and operating allowances, six-page PDF and social card.
- Native share button uses the browser share sheet when available, with copy-link fallback. No message is sent automatically.

## Basis

One approximately 14-story, 300–500-unit building, mostly studios; students and young professionals. User-provided project facts, no supplied floorplate. Self-service use and essential supplies included.

Working concept: 24ft x22ft interior envelope (528sqft); two integrated wash/dry bays, separate low paw rinse, towel/brush counter, storage, future third-bay alcove and optional retail niche. Reference equipment is Evolution mini, starting at $12,250 per unit when checked October29,2026. Exact equipment, utilities, access and building integration require current supplier/architect coordination.

Default45-minute occupancy includes washing, powered drying and reset. All demand inputs are assumptions. The model gives two bays as the baseline concept, three under its45-minute stress scenario and four when that same stress scenario uses60-minute occupancy. Paw-rinse traffic is separate.

Concept allowance: $121,200–$218,400 including20% contingency. Local quotations have not been obtained. No rent premium or ROI is assumed. Sources and exclusions appear in the site and PDF.

## Source and publishing

Buildless HTML/CSS/ES modules; no external runtime dependencies or tracking. `index.html`, `style.css`, `app.mjs`, `capacity.mjs`, `model.js`, `panorama.js` define the experience. `DESIGN.md` is the design contract.

`python3 scripts/package-site.py` builds `dist/` using an explicit allowlist. `.github/workflows/pages.yml` validates source and capacity tests and deploys only `dist/` to GitHub Pages. Blender projects, local evidence and historical ZIPs are excluded from the public site.

`python3 build-portable.py` makes the serverless local HTML and review ZIP. Keep the companion PDF beside the HTML. The original concept is retained locally in `archive/`.

## Verification and limits

Source syntax and meaningful capacity tests run with Node. Local browser checks cover all panorama/model cameras, mobile movement, capacity cases, seasonal controls, plan navigation, responsive width, images and OG metadata. Evidence retained locally. Chromium390px phone layout verified; a standalone PlaywrightWebKit runtime was not installed. Native iPhone hardware testing is separate from browser emulation.

The photoreal perspective artwork is AI-generated concept imagery. Rendered360 views derive from the modeled geometry with added material/lighting treatments. These are conceptual visuals, with schematic equipment geometry; they are not surveyed building images or construction documentation. No Unreal application or GPU streaming server is used.
