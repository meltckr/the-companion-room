"""Create the static public site from an explicit file allowlist."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parent.parent
dist=root/'dist'
dist.mkdir(exist_ok=True)
for name in ['index.html','style.css','app.mjs','capacity.mjs','model.js','panorama.js','master-loader.mjs','The-Companion-Room-Concept-Brief.pdf','Developer-Decision-Brief.pdf','Procurement-Scope.pdf']:
    shutil.copy2(root/name,dist/name)
(dist/'assets/master').mkdir(parents=True,exist_ok=True)
for name in ['companion-room-og-v3.jpg']:
    shutil.copy2(root/'assets'/name,dist/'assets'/name)
for name in ['entrance.jpg','wash.jpg','dry.jpg','hero.jpg','hero.webp','detail.webp','scene.bin','scene.bin.gz','scene-meta.json','entrance-mobile.jpg','wash-mobile.jpg','dry-mobile.jpg']:
    shutil.copy2(root/'assets/master'/name,dist/'assets/master'/name)
(dist/'.nojekyll').write_text('')
print('Static release packaged in dist/.')

# Keep the previous public image URLs usable for older cached previews.
(dist/'assets/cinematic').mkdir(parents=True,exist_ok=True)
for name in ['spa-hero-v2.webp','spa-detail-v2.webp','companion-room-og.jpg']:
    shutil.copy2(root/'assets'/name,dist/'assets'/name)
for name in ['entrance.jpg','wash.jpg','dry.jpg','hero.jpg']:
    shutil.copy2(root/'assets/cinematic'/name,dist/'assets/cinematic'/name)
