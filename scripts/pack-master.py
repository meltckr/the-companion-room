"""Pack the master export into a small compressed browser mesh and shared imagery."""
from pathlib import Path
from array import array
import gzip,json,sys
root=Path(__file__).resolve().parent.parent
out=root/'assets/master-v4';out.mkdir(parents=True,exist_ok=True)
data=json.loads((root/'evidence/master-scene.json').read_text())
source=data['vertices'];stride=data.get('stride',11);groups={}
for item in data['items']:groups.setdefault(item['group'],[]).append(item)
packed=array('f');items=[]
for group,entries in groups.items():
    start=len(packed)//stride
    for item in entries:
        a=item['start']*stride;b=(item['start']+item['count'])*stride
        packed.extend(source[a:b])
    items.append({'start':start,'count':len(packed)//stride-start,'group':group})
if sys.byteorder!='little':packed.byteswap()
raw=packed.tobytes()
(out/'scene.bin').write_bytes(raw)
(out/'scene.bin.gz').write_bytes(gzip.compress(raw,compresslevel=9,mtime=0))
(out/'scene-meta.json').write_text(json.dumps({'stride':stride,'vertices':len(packed)//stride,'items':items,'source':'One detailed room master; optimized browser geometry.','bakedLighting':bool(data.get('lightmap'))},separators=(',',':')))
print(f'Master browser geometry: {len(packed)//stride:,} vertices, {len(items)} draw groups; {len(raw):,} raw / {len(gzip.compress(raw)):,} compressed bytes.')
