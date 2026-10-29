# Asset provenance — Concept 03

All current perspective images, guided panorama views and free-movement browser geometry derive from one detailed Blender master created by `scripts/build-master-scene.py`. There is no AI-generated perspective illustration in the current presentation.

Blender 5.2.2 / Cycles / Metal produced `assets/master-v4/hero.jpg`, `closeup.jpg`, `rinse.jpg`, `overview.jpg` and 6K equirectangular views `entrance.jpg`, `wash.jpg`, `dry.jpg`. The master manifest records scene and rendering settings. WebP stills and 4K mobile JPEGs are resolution/format derivatives of those renders. The packed .blend source is retained locally and excluded from the public site.

Native geometry includes rounded wash tubs, ramps, hoses, dividers, cabinetry, hardware, towels, tile joints and architectural lighting. Equipment is a generic reference; no exact manufacturer geometry, certified installation or surveyed building is represented. `scripts/pack-master.py` produces the same scene's browser mesh, grouped for efficient rendering. The movable browser model is a spatial planning view with simpler real-time shading than the Cycles renderings.

Stone and oak material maps come from Poly Haven under CC0. Exact source URLs and license are in `assets/materials/LICENSES.md`. Other material colors and geometry are authored in the scene script.

The current social card is deterministically composed in `scripts/og-card.html` and rendered by `scripts/render-og.cjs` at 1200x630. Its background is the current master-scene hero. Output: `assets/companion-room-og-v4.jpg`. Exact typography and wording are composed as HTML.

Earlier AI-generated Concept 02 illustrations and simpler cinematic renderings remain in Git history/local archives. Their old public asset URLs remain available for cached previews. They are absent from the current site, PDFs and share card.

Version 4 refines the same scene with varied stone sampling, satin millwork, linen sheen and a cooler daylight/warm cove balance. An alternate contact-occlusion export is available using eight distance-limited BVH rays per cached surface sample. The current release uses the diffuse-lighting atlas described below. The default two-bay arrangement is the shading basis; the optional third-bay study remains an approximation. The browser also samples the licensed oak and stone photographs. The person-and-dog scale diagram is authored SVG with explicit illustrative dimensions. No person or animal photograph is represented.

The selected movable-model illumination is baked from the same clean-stone master using Cycles diffuse direct, indirect and material-color passes at 2048 pixels and 32 samples. An image-only OpenImageDenoise compositor pass removes sampling noise without resizing or changing UV coordinates. The raw atlas and linear EXR remain local. The browser combines the denoised atlas with live material reflections. Its 1024-pixel environment-reflection map is encoded from the final entrance panorama. Glass and emission retain live shading. Optional third-bay studies use simplified live lighting.
