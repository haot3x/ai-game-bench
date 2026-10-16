/* Original, dependency-free calibration fixtures. No network, storage or debug API.
 * Mutation selection happens at load only. Tests use keyboard/buttons and visible UI,
 * never evaluate this closure or mutate the clock, physics or game state.
 */
(() => {
  'use strict';
  const params = new URLSearchParams(location.search);
  const game = params.get('game') === 'racing' ? 'racing' : 'platformer';
  const defect = params.get('defect') || 'none';
  const $ = id => document.getElementById(id);
  const keys = new Set();
  let state = 'Ready', elapsed = 0, previous = performance.now(), accumulator = 0;
  let round, step, draw;
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const TAU = 2 * Math.PI;
  const wrap = a => Math.atan2(Math.sin(a), Math.cos(a));
  const held = (...names) => names.some(n => keys.has(n));
  function status(s, message = '') { state = s; $('state').textContent = s; $('message').textContent = message; }
  function reset() { keys.clear(); elapsed = 0; round(); status('Playing'); $('restart').disabled = false; }
  $('start').onclick = () => { if (state === 'Ready') reset(); };
  $('restart').onclick = reset;
  window.addEventListener('keydown', e => {
    if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Space','KeyA','KeyD','KeyW','KeyS'].includes(e.code)) {
      e.preventDefault(); keys.add(e.code);
    }
  });
  window.addEventListener('keyup', e => keys.delete(e.code));
  window.addEventListener('blur', () => keys.clear());

  if (game === 'platformer') {
    $('title').textContent = 'Platformer reference';
    $('instructions').textContent = '← → / A D move · Space jumps · Collect coins · Cross the pit to the flag.';
    $('stage').innerHTML = `<svg id="world" viewBox="0 0 1000 500" role="img" aria-label="Platformer level">
      <rect width="1000" height="500" fill="#d7edff"/>
      <path d="M0 280L120 180L250 280L420 160L610 280L790 150L1000 280V500H0Z" fill="#c6dae8"/>
      <rect x="0" y="420" width="390" height="80" fill="#537d38"/>
      <rect x="520" y="420" width="480" height="80" fill="#537d38"/>
      <rect id="platform" x="180" y="335" width="120" height="18" fill="#537d38"/>
      <path d="M400 500L420 470L440 500L460 470L480 500L500 470L515 500" fill="#b23e47"/>
      <path d="M930 420V325H975L930 350" stroke="#315227" stroke-width="5" fill="#31a47b"/>
      <g id="coins"></g><rect id="player" width="26" height="34" fill="#154bdb"/>
    </svg>`;
    const coins = [{x:100,y:395},{x:245,y:310},{x:600,y:395}];
    const collected = new Set(), touching = new Set();
    let x = 50, y = 420, vy = 0, count = 0, grounded = true, jumpHeld = false;
    round = () => {
      x = 50; y = 420; vy = 0; grounded = true; jumpHeld = false; touching.clear();
      if (defect !== 'stale-reset') { count = 0; collected.clear(); }
    };
    step = dt => {
      if (defect === 'premature-win') { status('Won', 'Goal reached'); return; }
      const direction = Number(held('ArrowRight','KeyD')) - Number(held('ArrowLeft','KeyA'));
      const oldY = y;
      if (defect !== 'frozen-player') x = clamp(x + direction * 280 * dt, 13, 987);
      const jumping = held('Space');
      if (jumping && !jumpHeld && grounded && defect !== 'cosmetic-jump') { vy = -530; grounded = false; }
      jumpHeld = jumping;
      vy += 1200 * dt; y += vy * dt; grounded = false;
      const surfaces = [{x:0,w:390,y:420},{x:520,w:480,y:420}];
      if (defect !== 'decorative-platform') surfaces.push({x:180,w:120,y:335});
      for (const p of surfaces) {
        if (vy >= 0 && oldY <= p.y + 0.1 && y >= p.y && x+12 > p.x && x-12 < p.x+p.w) {
          y = p.y; vy = 0; grounded = true;
        }
      }
      coins.forEach((c,i) => {
        const hit = Math.abs(x-c.x) < 22 && c.y > y-44 && c.y < y+10;
        if (hit && !touching.has(i) && (!collected.has(i) || defect === 'duplicate-coin')) {
          count++; collected.add(i); $('message').textContent = 'Coin collected';
        }
        if (hit) touching.add(i); else touching.delete(i);
      });
      if (y > 560 && defect !== 'no-loss') status('Lost', 'Fell into the pit. Restart to try again.');
      if (x >= 930 && y <= 421) status('Won', 'Goal reached. Restart for another round.');
    };
    draw = () => {
      $('player').setAttribute('x', x-13); $('player').setAttribute('y', y-34);
      $('player').setAttribute('fill', defect === 'cosmetic-jump' && held('Space') ? '#9b55db' : '#154bdb');
      $('coins').innerHTML = coins.map((c,i) => collected.has(i) ? '' : `<rect x="${c.x-9}" y="${c.y-9}" width="18" height="18" fill="#e5a900"/>`).join('');
      $('counter').textContent = `Coins: ${count}`;
    };
  } else {
    $('title').textContent = '3D racing reference';
    $('instructions').textContent = '↑ / W accelerate · ↓ / S brake then reverse · ← → / A D steer · Pass gates 1, 2, 3, then finish clockwise.';
    $('stage').innerHTML = `<canvas id="world" width="1000" height="560" aria-label="Perspective racing scene"></canvas>
      <svg id="map" viewBox="-90 -90 180 180" role="img" aria-label="Visible route map">
      <circle r="60" fill="none" stroke="#46546a" stroke-width="24"/>
      <path d="M48 0H72 M0 48V72 M-48 0H-72 M0 -48V-72" stroke="#f2aa22" stroke-width="4"/>
      <g fill="#101a30" font-size="13"><text x="75" y="4">1</text><text x="-4" y="87">2</text><text x="-86" y="4">3</text><text x="5" y="-73">FINISH →</text></g>
      <line id="heading" stroke="#d92828" stroke-width="3"/><circle id="car" r="4" fill="#fc3e35" stroke="white" stroke-width="1"/>
      </svg>`;
    const ctx = $('world').getContext('2d');
    let x=0,z=-60,heading=0,v=0,progress=0,lastPhase=0,contact=false;
    round = () => { x=0; z=-60; heading=0; v=0; lastPhase=0; contact=false; if(defect !== 'stale-reset') progress=0; };
    step = dt => {
      const throttle=held('ArrowUp','KeyW'), brake=held('ArrowDown','KeyS');
      v += (throttle ? 18 : brake && defect !== 'no-brakes' ? -32 : -Math.sign(v)*3) * dt;
      v = clamp(v, -22, 40); if (!throttle && !brake && Math.abs(v)<0.1) v=0;
      const steering=Number(held('ArrowRight','KeyD'))-Number(held('ArrowLeft','KeyA'));
      if (defect !== 'no-steering') heading += steering * v / 60 * dt;
      if (defect !== 'hud-only-speed') { x += Math.cos(heading)*v*dt; z += Math.sin(heading)*v*dt; }
      let radius = Math.hypot(x,z); contact=radius<48 || radius>72;
      if (contact && defect !== 'no-boundaries') { const limit=clamp(radius,48,72); x*=limit/radius; z*=limit/radius; v*=0.97; }
      const phase=Math.atan2(z,x)+Math.PI/2;
      for(let gate=0;gate<4;gate++) {
        const a=wrap(lastPhase-gate*Math.PI/2), b=wrap(phase-gate*Math.PI/2);
        const forward=a<0 && b>=0 && Math.abs(a-b)<Math.PI;
        const reverse=a>=0 && b<0 && Math.abs(a-b)<Math.PI;
        if (!forward && !reverse) continue;
        if (gate===0) {
          if (defect==='unordered-checkpoints' || (forward && progress===3)) status('Finished', 'Legal lap complete. Restart for a new race.');
          else $('message').textContent='Finish rejected: complete ordered gates in the correct direction.';
        } else if (forward && gate===progress+1) { progress++; $('message').textContent=`Gate ${gate} accepted`; }
        else if (defect==='unordered-checkpoints') { progress=gate; }
        else $('message').textContent='Gate rejected: wrong direction or order.';
      }
      lastPhase=phase;
      if(contact) $('message').textContent='Track boundary';
    };
    function render3D() {
      ctx.fillStyle='#afdbf3'; ctx.fillRect(0,0,1000,560);
      ctx.fillStyle='#6b9b58'; ctx.fillRect(0,260,1000,300);
      const camera=defect==='fixed-camera' ? {x:0,z:-88,h:0} : {x:x-Math.cos(heading)*18,z:z-Math.sin(heading)*18,h:heading};
      const project = ([px,py,pz]) => {
        const dx=px-camera.x,dz=pz-camera.z, forward=dx*Math.cos(camera.h)+dz*Math.sin(camera.h);
        const side=-dx*Math.sin(camera.h)+dz*Math.cos(camera.h);
        const depth=forward*0.94+(9-py)*0.342;
        return depth>1 ? [500+side*520/depth,280+((9-py)*0.94-forward*0.342)*520/depth,depth] : null;
      };
      const polygons=[];
      const poly=(points,color)=>{const ps=points.map(project); if(ps.every(Boolean)) polygons.push({ps,color,depth:ps.reduce((s,p)=>s+p[2],0)/ps.length});};
      for(let i=0;i<120;i++) {
        const a=i*TAU/120,b=(i+1)*TAU/120;
        const point=(r,t,y=0)=>[Math.cos(t)*r,y,Math.sin(t)*r];
        poly([point(48,a),point(72,a),point(72,b),point(48,b)],i%2?'#48556a':'#4d5b70');
        for(const r of [48,72]) poly([point(r,a),point(r,b),point(r,b,2),point(r,a,2)],i%2?'#eeece4':'#c44e41');
        if(i%4===0) poly([point(59.6,a),point(60.4,a),point(60.4,b),point(59.6,b)],'#f4eed7');
      }
      for(let g=0;g<4;g++) {
        const a=g*Math.PI/2-Math.PI/2;
        const point=(r,t,y=0.08)=>[Math.cos(t)*r,y,Math.sin(t)*r];
        poly([point(48,a-.018),point(72,a-.018),point(72,a+.018),point(48,a+.018)],g?'#ffd34e':'#ffffff');
      }
      const carPoint=(f,s,y)=>[x+Math.cos(heading)*f-Math.sin(heading)*s,y,z+Math.sin(heading)*f+Math.cos(heading)*s];
      poly([carPoint(-2,-1,0.3),carPoint(2,-1,0.3),carPoint(2,-1,1.6),carPoint(-2,-1,1.6)],'#bc272e');
      poly([carPoint(-2,1,0.3),carPoint(2,1,0.3),carPoint(2,1,1.6),carPoint(-2,1,1.6)],'#b72630');
      poly([carPoint(-2,-1,1.6),carPoint(2,-1,1.6),carPoint(2,1,1.6),carPoint(-2,1,1.6)],'#fa5549');
      poly([carPoint(-2,-1,0.3),carPoint(-2,1,0.3),carPoint(-2,1,1.6),carPoint(-2,-1,1.6)],'#a41f31');
      polygons.sort((a,b)=>b.depth-a.depth).forEach(({ps,color})=>{ctx.fillStyle=color;ctx.beginPath();ps.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.closePath();ctx.fill();});
    }
    draw = () => {
      render3D();
      $('car').setAttribute('cx',x); $('car').setAttribute('cy',z);
      $('heading').setAttribute('x1',x); $('heading').setAttribute('y1',z);
      $('heading').setAttribute('x2',x+Math.cos(heading)*10); $('heading').setAttribute('y2',z+Math.sin(heading)*10);
      $('counter').textContent=`Checkpoints: ${progress} / 3`;
      $('timer').textContent=`Time: ${elapsed.toFixed(2)} s`;
      $('speed').textContent=`Speed: ${Math.abs(v).toFixed(1)}`;
    };
  }
  round(); draw();
  function frame(now) {
    accumulator += Math.min((now-previous)/1000, 0.05); previous=now;
    while(accumulator>=1/120) {
      if(state==='Playing') { elapsed+=1/120; step(1/120); }
      else if(game==='racing' && state==='Finished' && defect==='running-finish-clock') elapsed+=1/120;
      accumulator-=1/120;
    }
    draw(); requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
