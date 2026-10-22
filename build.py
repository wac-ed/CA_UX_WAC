"""Build index.html: a full-screen presenter for every slide in deck/slides,
in deck/deck.json order. Slides turn with a glass page-peel from the
bottom-right corner.

Run:  python3 build.py
"""
import html as htmllib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
deck = json.loads((ROOT / "deck" / "deck.json").read_text(encoding="utf-8"))

fonts = "".join(
    f'<link rel="stylesheet" href="{face["href"]}">\n'
    for face in deck.get("faces", {}).values()
    if face.get("href")
)

pages = []
for i, slide_id in enumerate(deck["order"]):
    src = (ROOT / "deck" / "slides" / f"{slide_id}.html").read_text(encoding="utf-8")
    # Uploaded images live in deck/assets/<id>.png in this repo
    src = re.sub(r'src="/_blob/([0-9a-f]+)"', r'src="deck/assets/\1.png"', src)
    pages.append(f'<div class="page" data-i="{i}">{src}</div>')

title = htmllib.escape(deck["title"])

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
{fonts}<style>
  * {{ box-sizing: border-box; margin: 0; }}
  html, body {{ height: 100%; }}
  body {{
    overflow: hidden; font-family: 'DM Sans', Arial, sans-serif; color: #F6F4EF;
    background:
      radial-gradient(60% 80% at 85% 90%, rgba(224,122,79,.28), transparent 60%),
      radial-gradient(50% 70% at 10% 10%, rgba(91,120,190,.25), transparent 60%),
      #0B1222;
  }}

  /* Stage: a 1920x1080 canvas scaled to fit the window, centred */
  #viewport {{ position: fixed; inset: 0; overflow: hidden; }}
  #stage {{ position: absolute; left: 50%; top: 50%; width: 1920px; height: 1080px; transform-origin: center; }}
  .page {{ position: absolute; inset: 0; visibility: hidden; overflow: hidden; border-radius: 6px;
           box-shadow: 0 40px 120px rgba(0,0,0,.5); }}
  .page.on {{ visibility: visible; }}

  /* Peel layers, drawn in stage coordinates */
  .fx {{ position: absolute; inset: 0; pointer-events: none; display: none; }}
  #fold-shade {{ z-index: 3; }}
  #flap-shadow {{ z-index: 4; filter: blur(22px); opacity: .55; }}
  #flap-shadow div {{ position: absolute; inset: 0; background: #000; transform: translate(18px, 22px); }}
  #flap {{ z-index: 5; backdrop-filter: blur(18px) saturate(160%) brightness(1.06);
           -webkit-backdrop-filter: blur(18px) saturate(160%) brightness(1.06); }}
  #flap-edge {{ z-index: 6; }}

  /* Slide content (subset of the Slides format) */
  section {{ position: relative; width: 1920px; height: 1080px; box-sizing: border-box; overflow: hidden; }}
  section aside {{ display: none; }}
  section ul, section ol {{ padding-left: 1.2em; }}
  section a {{ color: inherit; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ text-align: left; padding: .35em .6em; border-bottom: 1px solid #D6CFC1; }}
  th {{ border-bottom: 2px solid #16213A; }}
  x-icon {{ display: inline-block; border-radius: 50%; background: currentColor; opacity: .3; }}
  x-shape {{ display: inline-block; }}
  x-shape[kind="arrow-right"] {{ clip-path: polygon(0 30%, 60% 30%, 60% 0, 100% 50%, 60% 100%, 60% 70%, 0 70%); }}

  /* Glass controls; they fade out when the mouse is idle */
  .glass {{ background: rgba(22,33,58,.42); border: 1px solid rgba(255,255,255,.28);
            box-shadow: inset 0 1px 0 rgba(255,255,255,.35), 0 8px 24px rgba(0,0,0,.25);
            backdrop-filter: blur(16px) saturate(160%); -webkit-backdrop-filter: blur(16px) saturate(160%); }}
  #bar {{ position: fixed; left: 0; bottom: 0; height: 3px; width: 0; z-index: 10;
          background: linear-gradient(90deg, #F0A07C, #E07A4F); box-shadow: 0 0 12px rgba(240,160,124,.8);
          transition: width .6s cubic-bezier(.2,.8,.2,1); }}
  #hud {{ position: fixed; right: 18px; bottom: 16px; display: flex; gap: 8px; align-items: center;
          z-index: 10; transition: opacity .4s ease, transform .4s ease; }}
  body.idle #hud {{ opacity: 0; transform: translateY(8px); }}
  body.idle {{ cursor: none; }}
  #hud button, #count {{ font: 600 14px/1 'DM Sans', Arial, sans-serif; color: #F6F4EF;
          border-radius: 999px; padding: 10px 15px; }}
  #hud button {{ cursor: pointer; transition: background .2s ease, transform .2s ease; }}
  #hud button:hover {{ background: rgba(224,122,79,.55); transform: translateY(-1px); }}
  #hud button:focus-visible {{ outline: 2px solid #F0A07C; outline-offset: 2px; }}
  #hint {{ position: fixed; left: 50%; top: 18px; transform: translateX(-50%); z-index: 10;
           font: 500 14px/1.4 'DM Sans', Arial, sans-serif; padding: 9px 18px; border-radius: 999px;
           transition: opacity .6s ease; white-space: nowrap; }}
  #hint.gone {{ opacity: 0; pointer-events: none; }}
</style>
</head>
<body>
<div id="viewport"><div id="stage">
{chr(10).join(pages)}
<div id="fold-shade" class="fx"></div>
<div id="flap-shadow" class="fx"><div></div></div>
<div id="flap" class="fx"></div>
<div id="flap-edge" class="fx"></div>
</div></div>
<div id="bar"></div>
<div id="hud">
  <button id="home" class="glass" aria-label="Go to the first slide">&#8962; Home</button>
  <button id="prev" class="glass" aria-label="Previous slide">&#8592;</button>
  <span id="count" class="glass" aria-live="polite"></span>
  <button id="next" class="glass" aria-label="Next slide">&#8594;</button>
  <button id="fs" class="glass" aria-label="Toggle full screen">Full screen</button>
</div>
<div id="hint" class="glass">&#8592; &#8594; or click to turn pages &middot; F for full screen</div>
<script>
(() => {{
  const W = 1920, H = 1080, D = W + H;
  const pages = [...document.querySelectorAll('.page')];
  const stage = document.getElementById('stage');
  const shade = document.getElementById('fold-shade');
  const flapShadow = document.getElementById('flap-shadow');
  const flapShadowInner = flapShadow.firstElementChild;
  const flap = document.getElementById('flap');
  const edge = document.getElementById('flap-edge');
  const N = pages.length;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const DUR = 1150;
  let cur = 0, busy = false;

  function fit() {{
    const s = Math.min(innerWidth / W, innerHeight / H) * 0.96;
    stage.style.transform = `translate(-50%, -50%) scale(${{s}})`;
  }}
  addEventListener('resize', fit); fit();

  function hud() {{
    document.getElementById('count').textContent = `${{cur + 1}} / ${{N}}`;
    document.getElementById('bar').style.width = `${{(cur + 1) / N * 100}}%`;
    history.replaceState(null, '', '#' + (cur + 1));
  }}

  function show(i) {{
    pages.forEach((p, k) => {{
      p.classList.toggle('on', k === i);
      p.style.zIndex = k === i ? 1 : 0; p.style.clipPath = ''; p.style.opacity = '';
    }});
    cur = i; hud();
  }}

  // ---- Geometry of a 45-degree fold line x + y = c across the page ----
  const RECT = [[0, 0], [W, 0], [W, H], [0, H]];
  function clip(poly, c, keepBelow) {{
    // Sutherland-Hodgman against the half-plane x + y <= c (or >= c)
    const inside = p => keepBelow ? p[0] + p[1] <= c : p[0] + p[1] >= c;
    const out = [];
    for (let i = 0; i < poly.length; i++) {{
      const a = poly[i], b = poly[(i + 1) % poly.length];
      const ia = inside(a), ib = inside(b);
      if (ia) out.push(a);
      if (ia !== ib) {{
        const fa = a[0] + a[1] - c, fb = b[0] + b[1] - c, t = fa / (fa - fb);
        out.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]);
      }}
    }}
    return out;
  }}
  const poly = pts => pts.length < 3 ? 'polygon(0 0, 0 0, 0 0)'
    : 'polygon(' + pts.map(p => `${{p[0].toFixed(1)}}px ${{p[1].toFixed(1)}}px`).join(',') + ')';
  const pct = v => (Math.max(0, Math.min(1, v)) * 100).toFixed(2) + '%';

  // Draw one frame: `top` is the sheet being peeled, folded along x + y = c
  function frame(top, c) {{
    const kept = clip(RECT, c, true);            // part of the sheet still lying flat
    const lifted = clip(RECT, c, false);         // part lifted off, beyond the fold
    const flapPts = lifted.map(([x, y]) => [c - y, c - x]);  // reflected over the fold
    const f = c / D;                             // fold position along a 135deg gradient

    top.style.clipPath = poly(kept);
    shade.style.clipPath = poly(lifted);
    shade.style.background = `linear-gradient(135deg, rgba(11,18,34,.45) ${{pct(f)}}, rgba(11,18,34,0) ${{pct(f + .12)}})`;
    flapShadowInner.style.clipPath = poly(flapPts);
    flap.style.clipPath = poly(flapPts);
    flap.style.background = `linear-gradient(135deg,
      rgba(255,255,255,.10) ${{pct(f - .45)}},
      rgba(255,255,255,.22) ${{pct(f - .16)}},
      rgba(240,160,124,.18) ${{pct(f - .05)}},
      rgba(255,255,255,.70) ${{pct(f - .004)}},
      rgba(255,255,255,.95) ${{pct(f)}})`;
    // a thin bright rim along the fold
    edge.style.clipPath = poly(flapPts);
    edge.style.background = `linear-gradient(135deg, transparent ${{pct(f - .004)}}, rgba(255,255,255,.95) ${{pct(f - .0008)}}, transparent ${{pct(f)}})`;
    edge.style.filter = 'drop-shadow(0 0 6px rgba(255,255,255,.6))';
  }}

  const ease = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;

  function peel(top, under, from, to, done) {{
    top.style.zIndex = 2; under.style.zIndex = 1;
    edge.style.display = 'block';
    const t0 = performance.now();
    (function step(now) {{
      const t = Math.min(1, (now - t0) / DUR);
      frame(top, from + (to - from) * ease(t));
      if (t < 1) requestAnimationFrame(step);
      else {{
        edge.style.display = 'none';
        done();
      }}
    }})(t0);
  }}

  function go(to) {{
    to = Math.max(0, Math.min(N - 1, to));
    if (to === cur || busy) return;
    const from = pages[cur], dest = pages[to];
    busy = true;
    dest.classList.add('on');
    const finish = () => {{ busy = false; show(to); }};

    if (reduce) {{
      dest.style.zIndex = 2;
      dest.animate([{{opacity: 0}}, {{opacity: 1}}], {{duration: 300}}).onfinish = finish;
    }} else if (to > cur) {{
      // Current page peels away from the bottom-right corner, revealing the next
      peel(from, dest, D + 40, -40, finish);
    }} else {{
      // Previous page lays back down from the top-left, over the current one
      peel(dest, from, -40, D + 40, finish);
    }}
  }}

  // Keyboard
  addEventListener('keydown', e => {{
    if (['ArrowRight', 'ArrowDown', 'PageDown', ' ', 'Enter'].includes(e.key)) {{ e.preventDefault(); go(cur + 1); }}
    else if (['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace'].includes(e.key)) {{ e.preventDefault(); go(cur - 1); }}
    else if (e.key === 'Home') go(0);
    else if (e.key === 'End') go(N - 1);
    else if (e.key === 'f' || e.key === 'F') toggleFs();
  }});

  // Click: right two-thirds forward, left third back; links on slides still work
  document.getElementById('viewport').addEventListener('click', e => {{
    if (e.target.closest('a')) return;
    go(e.clientX < innerWidth / 3 ? cur - 1 : cur + 1);
  }});

  // Swipe
  let x0 = null;
  addEventListener('touchstart', e => {{ x0 = e.touches[0].clientX; }}, {{passive: true}});
  addEventListener('touchend', e => {{
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 40) go(dx < 0 ? cur + 1 : cur - 1);
  }});

  // Buttons
  document.getElementById('home').onclick = e => {{ e.stopPropagation(); go(0); }};
  document.getElementById('prev').onclick = e => {{ e.stopPropagation(); go(cur - 1); }};
  document.getElementById('next').onclick = e => {{ e.stopPropagation(); go(cur + 1); }};
  const fsBtn = document.getElementById('fs');
  function toggleFs() {{
    if (!document.fullscreenElement) document.documentElement.requestFullscreen?.().catch(() => {{}});
    else document.exitFullscreen?.();
  }}
  fsBtn.onclick = e => {{ e.stopPropagation(); toggleFs(); }};
  document.addEventListener('fullscreenchange', () => {{
    fsBtn.textContent = document.fullscreenElement ? 'Exit full screen' : 'Full screen';
  }});

  // Hide controls and cursor when idle; hide the hint after a few seconds
  let t;
  function wake() {{ document.body.classList.remove('idle'); clearTimeout(t); t = setTimeout(() => document.body.classList.add('idle'), 2500); }}
  addEventListener('mousemove', wake); wake();
  setTimeout(() => document.getElementById('hint').classList.add('gone'), 4000);

  // Start at #n if given
  const start = parseInt(location.hash.slice(1), 10);
  show(Number.isFinite(start) ? Math.max(0, Math.min(N - 1, start - 1)) : 0);
}})();
</script>
</body>
</html>
"""

(ROOT / "index.html").write_text(page, encoding="utf-8")
print(f"index.html: {len(pages)} slides")
