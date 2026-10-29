# The Companion Room

A premium resident pet-spa concept prepared by Mel Tucker / AVC for a proposed downtown East Lansing apartment building.

Canonical share URL: https://meltckr.github.io/the-companion-room/

## Experience

- Cinematic 360-degree views rendered from the actual room geometry with Blender Cycles: arrival, wash/dry bays and finishing counter. Touch drag and pinch zoom; fixed viewpoints.
- A separate native WebGL spatial model uses the same detailed master geometry and supports free movement, five cameras, a third-bay study and PNG export. Both viewers load on demand. The movable model adds baked scene illumination, photographic material maps and softer lighting.
- Responsive plan with a labeled person-and-dog scale study, four-season operating notes, transparent demand calculator, equipment shortlist, capital and operating allowances, six-page PDF and social card.
- Native share button uses the browser share sheet when available, with copy-link fallback. No message is sent automatically.

## Basis

One approximately 14-story, 300–500-unit building, mostly studios; students and young professionals. User-provided project facts, no supplied floorplate. Self-service use and essential supplies included.

Two illustrative envelopes: compact20ft x18ft (360sqft) and premium24ft x22ft (528sqft). Both include two integrated wash/dry bays, separate low paw rinse, towel/brush counter and storage. The premium room reserves a third-bay alcove and optional retail niche. Reference equipment is Evolution mini, starting at $12,250 per unit when checked October29,2026. Exact equipment, utilities, access and building integration require current supplier/architect coordination.

Default45-minute occupancy includes washing, powered drying and reset. All demand inputs are assumptions. The model gives two bays as the baseline concept, three under its45-minute stress scenario and four when that same stress scenario uses60-minute occupancy. Paw-rinse traffic is separate.

Premium concept allowance: $121,200–$218,400 including20% contingency. It includes equipment; do not add the published pair price again. Compact construction is unpriced. Local quotations have not been obtained. No rent premium or ROI is assumed. Sources and exclusions appear in the site and PDF.

## Source and publishing

Buildless HTML/CSS/ES modules; no external runtime dependencies or tracking. `index.html`, `style.css`, `app.mjs`, `capacity.mjs`, `model.js`, `panorama.js`, `master-loader.mjs` define the experience. `DESIGN.md` is the design contract.

`python3 scripts/package-site.py` builds `dist/` using an explicit allowlist. `.github/workflows/pages.yml` validates source and capacity tests and deploys only `dist/` to GitHub Pages. Blender projects, local evidence and historical ZIPs are excluded from the public site.

`python3 build-portable.py` makes the serverless local HTML and review ZIP. Keep the three companion PDFs beside the HTML. Earlier concepts are retained locally in `archive/` and Git history.

`scripts/build-master-scene.py` creates all current renderings and geometry. `scripts/pack-master.py` merges geometry into seven browser draw groups. Material provenance is in `assets/materials/LICENSES.md`. Packed .blend files and full scene exports are retained locally. `COST-EVIDENCE.json` separates published prices and authored allowances. `PROCUREMENT-BRIEF.md` is a prepared draft, not an issued request.

## Verification and limits

Source syntax and meaningful capacity tests run with Node. Local browser checks cover all panorama/model cameras, mobile movement, capacity cases, seasonal controls, plan navigation, responsive width, images and OG metadata. Evidence retained locally. Phone touch startup is verified in Chromium and Safari-family WebKit, including slow/failed loads, retry, texture limits and landscape orientation. Native iPhone hardware testing is separate from browser emulation.

Current perspective images, 6K panorama views and browser geometry derive from one detailed Blender master. Mobile panoramas use 4K copies. Touch drag, pinch zoom, guided stops and reduced-motion behavior are supported. Earlier AI illustrations remain archived and are absent from the current presentation. Equipment is a generic visual reference. All geometry is conceptual rather than surveyed or construction-ready. No Unreal application or GPU streaming server is used.

## Reproducing the visual finish

Render the master using `scripts/build-master-scene.py --out assets/master-v4` through Blender. The scene source and licensed material maps are checked in; packed Blender files stay local. The contact-shading export is an economical fallback. `scripts/bake-browser-lightmap.py` builds an optional shared diffuse-illumination atlas from a saved master. Keep intermediate atlas/JSON exports under local evidence. Copy the selected atlas to `assets/master-v4/lighting.png`, its geometry JSON to `evidence/master-scene.json`, and run `scripts/pack-master.py`. Rendered panoramas remain 6K on desktop and are encoded to 4K for phones.

A baked illumination candidate must pass visual review in the browser before publication. The third-bay fit study uses simplified live lighting, avoiding shadows from furniture that has been removed.
