"""Package the local presentation for direct browser opening without a server."""
from pathlib import Path
import base64
import zipfile
import json
root=Path(__file__).resolve().parent
page=(root/'index.html').read_text()
page=page.replace('<link rel="stylesheet" href="style.css">','<style>'+(root/'style.css').read_text()+'</style>')
script=(root/'app.mjs').read_text().replace("import {capacity, defaults} from './capacity.mjs';",(root/'capacity.mjs').read_text().replace('export ',''))
module=base64.b64encode((root/'model.js').read_bytes()).decode()
script=script.replace("import('./model.js')",f"import('data:text/javascript;base64,{module}')")
panorama=base64.b64encode((root/'panorama.js').read_bytes()).decode()
script=script.replace("import('./panorama.js')",f"import('data:text/javascript;base64,{panorama}')")
images={name:'data:image/jpeg;base64,'+base64.b64encode((root/'assets/cinematic'/(name+'.jpg')).read_bytes()).decode() for name in ['entrance','wash','dry']}
script='window.CINEMATIC_ASSETS='+json.dumps(images)+';\n'+script
page=page.replace('<script type="module" src="app.mjs"></script>','<script type="module">'+script+'</script>')
for asset in ['spa-hero-v2.webp','spa-detail-v2.webp']:
    data=base64.b64encode((root/'assets'/asset).read_bytes()).decode()
    page=page.replace('assets/'+asset,'data:image/webp;base64,'+data)
output=root/'Open-The-Companion-Room.html'
output.write_text(page)
with zipfile.ZipFile(root/'Companion-Room-Review-Package.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for name in ['Open-The-Companion-Room.html','The-Companion-Room-Concept-Brief.pdf']:
        archive.write(root/name,name)
print('Portable presentation and review ZIP created.')
