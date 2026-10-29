export async function loadMasterGeometry({base='assets/master'}={}){
  if(window.MASTER_GEOMETRY){
    const encoded=atob(window.MASTER_GEOMETRY.vertices);
    const bytes=Uint8Array.from(encoded,c=>c.charCodeAt(0));
    const buffer=window.MASTER_GEOMETRY.compression==='gzip'?await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer():bytes.buffer;
    return {vertices:new Float32Array(buffer),items:window.MASTER_GEOMETRY.items,stride:window.MASTER_GEOMETRY.stride||11};
  }
  const metadata=await fetch(`${base}/scene-meta.json`);
  if(!metadata.ok)throw new Error('The room geometry metadata could not load.');
  const meta=await metadata.json();let buffer;
  if(typeof DecompressionStream==='function'){
    const response=await fetch(`${base}/scene.bin.gz`);
    if(!response.ok)throw new Error('The room geometry could not load.');
    buffer=response.headers.get('content-encoding')?.includes('gzip')?await response.arrayBuffer():await new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
  }else{
    const response=await fetch(`${base}/scene.bin`);
    if(!response.ok)throw new Error('The room geometry could not load.');
    buffer=await response.arrayBuffer();
  }
  const vertices=new Float32Array(buffer);
  if(vertices.length!==meta.vertices*meta.stride)throw new Error('The room geometry is incomplete.');
  return {vertices,items:meta.items,stride:meta.stride};
}
