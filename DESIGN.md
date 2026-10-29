# Design
## Source of truth
Active, October 29, 2026. Private local concept presentation, architectural model, capacity calculator, and print brief. User brief: downtown East Lansing; one approximately 14-story building, 300–500 apartments, mostly studios, proposed rents $1,500–$3,000/month, students and young professionals. Self-service pet washing included as an amenity. Site acquired; floor plan and allotted room area unknown. No existing pet-spa project found in workspace.
## Brand
Working concept name: The Companion Room. Warm boutique hospitality, forest green, stone, wood-look warmth. Prepared for discussion by Mel Tucker / AVC. No implication of an approved building name or developer endorsement. Avoid cartoon pet-store styling and ornate luxury.
## Product goals
Make a premium amenity tangible, explore the same working geometry in 3D, and explain its sizing and operating assumptions. Success: user can tour, compare seasons, explore a third bay, change capacity assumptions, and print a brief. Public share link is authorized. No outreach, actual booking, payment processing, or construction-ready claims.
## Personas and jobs
Mel: demonstrate thoughtful consulting to prospective developer clients. Developer: understand resident value, space, capacity and cost. Residents: convenient self-service washing. Operations: cleaning, laundry, supplies, equipment service.
## Information architecture
Single page: concept, interactive tour, diagram, capacity, four seasons, operating/supply model, investment, sources. Navigation anchors and print/save controls. Six-page PDF brief, public GitHub Pages site and local offline package.
## Design principles
Lead with imagery; follow with decisions. Label assumptions where read. Integrated wash/dry at each bay; separate towel-and-brush counter. All product essentials remain included; optional retail niche is an upgrade. Capacity follows explicit assumptions, not an invented apartment-unit ratio.
## Visual language
Ivory #f5f2e9, forest #173e35, ink #20362f, warm brass #b99b6b. Georgia editorial headlines, system sans body. Large imagery, broad whitespace, thin rules, restrained rounded controls. No decorative motion.
## Components
Hero, evidence strip, cinematic rendered 360 tour plus native WebGL model with presets, interactive SVG plan, labeled range inputs, season selector, cost table, source disclosures. Tokens owned by style.css. Capacity math owned by capacity.mjs; geometry owned by model.js.
## Accessibility
Keyboard focus, semantic landmarks, native labels and controls, minimum 44px targets. SVG plan has descriptive title. WebGL canvas keyboard focus and visible controls plus text and SVG equivalents. No claim of certified physical accessibility; architect must review route, controls, clearances and applicable scoping. Respect reduced motion.
## Responsive behavior
Desktop two-column editorial sections; below 900px stack. Tour height 560px desktop / 420px mobile; buttons wrap. No required hover interaction or horizontal page scrolling.
## Interaction states
Tour loading, ready and WebGL unavailable (show plan and imagery). Seasons change view daylight and operational copy, not facility weatherproofing. Third-bay toggle shows expansion tradeoff in spatial-model mode. Cinematic mode offers three fixed 360 viewpoints with pan/zoom, distinct from free movement in the model. Save current view gives PNG. Capacity calculations update live. Print hides controls and prints current assumptions.
## Content voice
Calm, specific, client-ready Mel voice. Recommendations marked as recommendations. Price quotes separate from authored allowances; cite primary sources. No promised rent uplift or ROI.
## Implementation constraints
Buildless HTML/CSS/ES modules; dependency-free native WebGL. All imagery local. No CDN, external scripts, tracking, credentials or payment integrations. GitHub Pages is the canonical share URL; local preview and portable copy retained. Room envelope 24ft x22ft =528sqft illustrative; walls/utilities and building integration unresolved. AI perspective art is illustrative; Blender-rendered 360 viewpoints derive from model geometry; dimensional model/plan define schematic layout. No surveyed site context.
## Open questions
- [ ] Developer/architect: final floorplate, frontage, exit routes, adjacency, structural/MEP and fire protection.
- [ ] Operator: dog policy, demand, hours/noise controls, booking and towel-laundry model.
- [ ] Contractor: local quotes and allowances; no quotes obtained.
- [ ] Developer: final amenity branding, optional retail servicing and budget.

## Release update, October 29
Integrated-wash/dry reference: Evolution mini, starting $12,250 each; supplier final submittals and free-use setup required. Default cycle 45min =15 wash+20 dry+10 arrival/reset (assumptions). Stress45min needs3bays; stress60min needs4 at chosen80% ceiling. Equipment allowance30–42k, total121.2–218.4k incl20% concept contingency. Public social card1200x630 with absolute OG/Twitter/canonical metadata. Mobile touch controls and genuine rendered panoramas; no claim that Unreal is used.
