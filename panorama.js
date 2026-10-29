/** Fixed-viewpoint photographic tour. Drag to look; scroll to zoom; arrows when focused. */
export function createPanoramaViewer(canvas, options = {}) {
  const assets = { entrance: 'assets/panorama-entrance.jpg', wash: 'assets/panorama-wash.jpg', dry: 'assets/panorama-dry.jpg', ...options.assets };
  const gl = canvas.getContext('webgl2', { alpha: false, antialias: false, preserveDrawingBuffer: true });
  const noop = { setView() {}, zoom() {}, resize() {}, getState: () => ({ view: null, yaw: 0, pitch: 0, fov: 75 }), capture: () => null, destroy() {} };
  canvas.dataset.panoReady = 'false';
  if (!gl) {
    options.onError?.(new Error('The panoramic tour needs WebGL 2. Please use the still renderings.'));
    return noop;
  }
  const clamp = (n, a, b) => Math.max(a, Math.min(b, n));
  const radians = Math.PI / 180;
  const removers = [];
  let disposed = false, lost = false, readyNotified = false, frame = 0, request = 0, pending = null;
  let program, vao, texture = null, transition = null, uniforms, view = null, requestedView = 'entrance';
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let yaw = 0, pitch = 0, fov = 75, targetYaw = 0, targetPitch = 0, targetFov = 75;
  const pointers = new Map();
  let pinchDistance = 0;
  const oldTouchAction = canvas.style.touchAction;
  const oldTabIndex = canvas.getAttribute('tabindex');
  canvas.style.touchAction = 'none';
  if (oldTabIndex === null) canvas.tabIndex = 0;
  const on = (target, event, fn, settings) => {
    target.addEventListener(event, fn, settings);
    removers.push(() => target.removeEventListener(event, fn, settings));
  };
  function shader(type, source) {
    const result = gl.createShader(type);
    gl.shaderSource(result, source);
    gl.compileShader(result);
    if (!gl.getShaderParameter(result, gl.COMPILE_STATUS)) {
      const message = gl.getShaderInfoLog(result);
      gl.deleteShader(result);
      throw new Error(message || 'Panorama shader compilation failed.');
    }
    return result;
  }
  function setup() {
    const vertex = shader(gl.VERTEX_SHADER, `#version 300 es
      out vec2 screen;
      void main() {
        vec2 p = vec2((gl_VertexID << 1) & 2, gl_VertexID & 2);
        screen = p * 2.0 - 1.0;
        gl_Position = vec4(screen, 0.0, 1.0);
      }`);
    const fragment = shader(gl.FRAGMENT_SHADER, `#version 300 es
      precision highp float;
      in vec2 screen;
      out vec4 color;
      uniform sampler2D panorama, previousPanorama;
      uniform float blend;
      uniform vec3 previousLook;
      uniform float aspect, tangent, yaw, pitch;
      const float PI = 3.141592653589793;
      vec2 project(float heading, float elevation, float scale) {
        vec3 ray = normalize(vec3(screen.x * aspect * scale, screen.y * scale, 1.0));
        ray = vec3(ray.x, cos(elevation)*ray.y + sin(elevation)*ray.z, -sin(elevation)*ray.y + cos(elevation)*ray.z);
        ray = vec3(cos(heading)*ray.x + sin(heading)*ray.z, ray.y, -sin(heading)*ray.x + cos(heading)*ray.z);
        return vec2(0.5 + atan(ray.x, ray.z)/(2.0*PI), 0.5 - asin(clamp(ray.y,-1.0,1.0))/PI);
      }
      void main() {
        vec4 current = texture(panorama, project(yaw, pitch, tangent));
        vec4 previous = texture(previousPanorama, project(previousLook.x, previousLook.y, previousLook.z));
        color = mix(previous, current, blend);
      }`);
    program = gl.createProgram();
    gl.attachShader(program, vertex);
    gl.attachShader(program, fragment);
    gl.linkProgram(program);
    gl.deleteShader(vertex);
    gl.deleteShader(fragment);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program) || 'Panorama program linking failed.');
    vao = gl.createVertexArray();
    uniforms = Object.fromEntries(['aspect', 'tangent', 'yaw', 'pitch', 'panorama', 'previousPanorama', 'previousLook', 'blend'].map(name => [name, gl.getUniformLocation(program, name)]));
  }
  function render() {
    if (disposed || lost || !texture || !canvas.clientWidth || !canvas.clientHeight) return;
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.disable(gl.DEPTH_TEST);
    gl.disable(gl.BLEND);
    gl.useProgram(program);
    gl.bindVertexArray(vao);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, transition?.texture || texture);
    gl.uniform1i(uniforms.panorama, 0);
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.uniform1i(uniforms.previousPanorama, 1);
    const oldLook = transition?.previous || { yaw, pitch, fov };
    gl.uniform3f(uniforms.previousLook, oldLook.yaw, oldLook.pitch, Math.tan(oldLook.fov*radians/2));
    const amount = transition ? clamp((performance.now()-transition.start)/450, 0, 1) : 1;
    gl.uniform1f(uniforms.blend, amount*amount*(3-2*amount));
    gl.uniform1f(uniforms.aspect, canvas.width / canvas.height);
    gl.uniform1f(uniforms.tangent, Math.tan(fov * radians / 2));
    gl.uniform1f(uniforms.yaw, yaw);
    gl.uniform1f(uniforms.pitch, pitch);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }
  function animate() {
    frame = 0;
    if (disposed || lost) return;
    yaw += (targetYaw - yaw) * .22;
    pitch += (targetPitch - pitch) * .22;
    fov += (targetFov - fov) * .22;
    if (transition && (reducedMotion.matches || performance.now()-transition.start >= 450)) commitTransition();
    render();
    if (transition || Math.abs(targetYaw-yaw) + Math.abs(targetPitch-pitch) + Math.abs(targetFov-fov) > .0001) wake();
  }
  function wake() { if (!frame && !disposed && !lost) frame = requestAnimationFrame(animate); }
  function resize() {
    if (disposed || lost) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const width = Math.max(1, Math.round(canvas.clientWidth * dpr));
    const height = Math.max(1, Math.round(canvas.clientHeight * dpr));
    if (canvas.width !== width || canvas.height !== height) { canvas.width = width; canvas.height = height; }
    render();
  }
  function cancelLoad() {
    if (!pending) return;
    pending.onload = pending.onerror = null;
    pending.src = '';
    pending = null;
  }
  function commitTransition() {
    const completed = transition;
    if (!completed) return;
    transition = null;
    if (texture) gl.deleteTexture(texture);
    texture = completed.texture;
    view = completed.view;
    resize();
    canvas.dataset.panoReady = 'true';
    canvas.dataset.panoView = view;
    if (!readyNotified) { readyNotified = true; options.onReady?.(); }
    options.onViewChange?.(view);
  }
  function cancelTransition() {
    if (!transition) return;
    gl.deleteTexture(transition.texture);
    ({ yaw, pitch, fov } = transition.previous);
    targetYaw = yaw; targetPitch = pitch; targetFov = fov;
    transition = null;
    render();
  }
  function setView(name) {
    if (disposed) return;
    const next = name === 'overview' || name === 'plan' ? 'entrance' : name;
    if (!Object.prototype.hasOwnProperty.call(assets, next)) {
      options.onError?.(new Error(`Unknown panorama viewpoint: ${name}`));
      return;
    }
    requestedView = next;
    const token = ++request;
    cancelLoad();
    if (lost) return;
    cancelTransition();
    if (next === view && texture) { options.onViewChange?.(next); return; }
    const image = new Image();
    pending = image;
    image.crossOrigin = 'anonymous';
    image.onload = () => {
      if (disposed || lost || token !== request) return;
      pending = null;
      let uploaded = null;
      try {
        const maximum = gl.getParameter(gl.MAX_TEXTURE_SIZE);
        if (image.naturalWidth > maximum || image.naturalHeight > maximum) throw new Error('This panorama exceeds the device texture size limit.');
        uploaded = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, uploaded);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, image);
        if (gl.getError() !== gl.NO_ERROR) throw new Error('The device could not upload the panorama.');
        transition = { texture: uploaded, view: next, start: performance.now(), previous: { yaw, pitch, fov } };
        yaw = targetYaw = next === 'dry' ? Math.PI / 3 : next === 'wash' ? -Math.PI / 6 : 0;
        pitch = targetPitch = (next === 'dry' ? -10 : next === 'wash' ? -8 : -5)*radians;
        fov = targetFov = 75;
        if (!texture || reducedMotion.matches) commitTransition();
        else wake();
      } catch (error) {
        if (uploaded && uploaded !== texture && uploaded !== transition?.texture) gl.deleteTexture(uploaded);
        options.onError?.(error);
      }
    };
    image.onerror = () => {
      if (disposed || token !== request) return;
      pending = null;
      options.onError?.(new Error(`Could not load the ${next} panorama.`));
    };
    image.src = assets[next];
  }
  function zoom(deltaDegrees) {
    if (disposed || !Number.isFinite(deltaDegrees)) return;
    targetFov = clamp(targetFov + deltaDegrees, 50, 95);
    wake();
  }
  function distance() {
    const points = [...pointers.values()];
    return points.length < 2 ? 0 : Math.hypot(points[0].x-points[1].x, points[0].y-points[1].y);
  }
  on(canvas, 'pointerdown', event => {
    if (pointers.size >= 2 || (event.pointerType === 'mouse' && event.button !== 0)) return;
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    pinchDistance = distance();
    canvas.focus({ preventScroll: true });
    canvas.setPointerCapture(event.pointerId);
  });
  on(canvas, 'pointermove', event => {
    const previous = pointers.get(event.pointerId);
    if (!previous) return;
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (pointers.size === 2) {
      const nextDistance = distance();
      if (pinchDistance > 0 && nextDistance > 0) {
        // Scale perspective magnification with finger separation rather than pixel travel.
        const nextFov = 2 * Math.atan(Math.tan(targetFov*radians/2) * pinchDistance/nextDistance) / radians;
        zoom(nextFov-targetFov);
      }
      pinchDistance = nextDistance;
      return;
    }
    const sensitivity = targetFov * radians / Math.max(1, canvas.clientHeight);
    targetYaw -= (event.clientX-previous.x) * sensitivity;
    targetPitch = clamp(targetPitch + (event.clientY-previous.y) * sensitivity, -80*radians, 80*radians);
    wake();
  });
  const release = event => {
    if (!pointers.has(event.pointerId)) return;
    pointers.delete(event.pointerId);
    pinchDistance = distance();
    if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
  };
  on(canvas, 'pointerup', release);
  on(canvas, 'pointercancel', release);
  on(canvas, 'lostpointercapture', release);
  on(canvas, 'wheel', event => {
    event.preventDefault();
    const delta = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? canvas.clientHeight : 1);
    zoom(delta * .035);
  }, { passive: false });
  on(canvas, 'keydown', event => {
    if (document.activeElement !== canvas || !['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) return;
    event.preventDefault();
    targetYaw += (event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0) * 4 * radians;
    targetPitch = clamp(targetPitch + (event.key === 'ArrowUp' ? 1 : event.key === 'ArrowDown' ? -1 : 0) * 4*radians, -80*radians, 80*radians);
    wake();
  });
  on(canvas, 'webglcontextlost', event => {
    event.preventDefault();
    lost = true;
    ++request;
    cancelLoad();
    cancelAnimationFrame(frame); frame = 0;
    texture = null;
    transition = null;
    canvas.dataset.panoReady = 'false';
    options.onError?.(new Error('The panoramic graphics context was interrupted. The tour will reload when graphics recover.'));
  });
  on(canvas, 'webglcontextrestored', () => {
    if (disposed) return;
    lost = false;
    try { setup(); setView(requestedView); } catch (error) { options.onError?.(error); }
  });
  const observer = typeof ResizeObserver === 'function' ? new ResizeObserver(resize) : null;
  observer?.observe(canvas);
  on(window, 'resize', resize);
  function destroy() {
    if (disposed) return;
    disposed = true;
    ++request;
    cancelLoad();
    cancelAnimationFrame(frame);
    observer?.disconnect();
    removers.forEach(remove => remove());
    for (const id of pointers.keys()) if (canvas.hasPointerCapture(id)) canvas.releasePointerCapture(id);
    pointers.clear();
    if (!lost) {
      if (texture) gl.deleteTexture(texture);
      if (transition) gl.deleteTexture(transition.texture);
      if (program) gl.deleteProgram(program);
      if (vao) gl.deleteVertexArray(vao);
    }
    canvas.style.touchAction = oldTouchAction;
    if (oldTabIndex === null) canvas.removeAttribute('tabindex'); else canvas.setAttribute('tabindex', oldTabIndex);
    canvas.dataset.panoReady = 'false';
  }
  try { setup(); resize(); setView('entrance'); } catch (error) { options.onError?.(error); }
  return { setView, zoom, resize, getState: () => ({ view, yaw, pitch, fov }), capture() {
    if (disposed || lost || !texture) return null;
    render();
    try { return canvas.toDataURL('image/png'); } catch (error) { options.onError?.(error); return null; }
  }, destroy };
}
