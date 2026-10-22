"""Build index.html: a full-screen presenter for every slide in deck/slides,
in deck/deck.json order, with a page-turn animation between slides.

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
    pages.append(f'<div class="page" data-i="{i}">{src}<div class="shade"></div></div>')

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
  body {{ background: #0B1222; overflow: hidden; font-family: 'DM Sans', Arial, sans-serif; }}

  /* Stage: a 1920x1080 canvas scaled to fit the window, centred */
  #viewport {{ position: fixed; inset: 0; overflow: hidden; }}
  #stage {{ position: absolute; left: 50%; top: 50%; width: 1920px; height: 1080px;
            transform-origin: center center; perspective: 3600px; }}
  .page {{ position: absolute; inset: 0; visibility: hidden; transform-origin: left center;
           backface-visibility: hidden; will-change: transform; overflow: hidden;
           box-shadow: 0 30px 80px rgba(0,0,0,.45); }}
  .page.on {{ visibility: visible; }}
  .shade {{ position: absolute; inset: 0; pointer-events: none; opacity: 0;
            background: linear-gradient(90deg, rgba(0,0,0,0) 0%, rgba(0,0,0,.35) 100%); }}

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

  /* Controls: progress bar, counter, buttons; they fade out when the mouse is idle */
  #bar {{ position: fixed; left: 0; bottom: 0; height: 4px; background: #E07A4F; width: 0;
          transition: width .5s ease; z-index: 10; }}
  #hud {{ position: fixed; right: 16px; bottom: 14px; display: flex; gap: 8px; align-items: center;
          z-index: 10; transition: opacity .4s ease; }}
  body.idle #hud {{ opacity: 0; }}
  body.idle {{ cursor: none; }}
  #hud button, #count {{ font: 600 14px/1 'DM Sans', Arial, sans-serif; color: #F6F4EF;
          background: rgba(22,33,58,.8); border: 1px solid rgba(246,244,239,.2); border-radius: 999px;
          padding: 9px 14px; }}
  #hud button {{ cursor: pointer; }}
  #hud button:hover {{ background: #B8461F; }}
  #hud button:focus-visible {{ outline: 2px solid #F0A07C; outline-offset: 2px; }}
  #hint {{ position: fixed; left: 50%; top: 18px; transform: translateX(-50%); z-index: 10;
           font: 500 14px/1.4 'DM Sans', Arial, sans-serif; color: #F6F4EF; background: rgba(22,33,58,.85);
           padding: 8px 16px; border-radius: 999px; transition: opacity .6s ease; }}
  #hint.gone {{ opacity: 0; pointer-events: none; }}
</style>
</head>
<body>
<div id="viewport"><div id="stage">
{chr(10).join(pages)}
</div></div>
<div id="bar"></div>
<div id="hud">
  <button id="prev" aria-label="Previous slide">&#8592;</button>
  <span id="count" aria-live="polite"></span>
  <button id="next" aria-label="Next slide">&#8594;</button>
  <button id="fs" aria-label="Toggle full screen">Full screen</button>
</div>
<div id="hint">&#8592; &#8594; or click to turn pages &middot; F for full screen</div>
<script>
(() => {{
  const pages = [...document.querySelectorAll('.page')];
  const stage = document.getElementById('stage');
  const N = pages.length;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const DUR = 900;
  let cur = 0, busy = false;

  function fit() {{
    const s = Math.min(innerWidth / 1920, innerHeight / 1080);
    stage.style.transform = `translate(-50%, -50%) scale(${{s}})`;
  }}
  addEventListener('resize', fit); fit();

  function hud() {{
    document.getElementById('count').textContent = `${{cur + 1}} / ${{N}}`;
    document.getElementById('bar').style.width = `${{(cur + 1) / N * 100}}%`;
    history.replaceState(null, '', '#' + (cur + 1));
  }}

  function show(i) {{
    pages.forEach((p, k) => {{ p.classList.toggle('on', k === i); p.style.zIndex = k === i ? 1 : 0; p.style.transform = ''; }});
    cur = i; hud();
  }}

  function go(to) {{
    to = Math.max(0, Math.min(N - 1, to));
    if (to === cur || busy) return;
    const from = pages[cur], dest = pages[to], forward = to > cur;
    busy = true;
    dest.classList.add('on');

    if (reduce) {{
      dest.style.zIndex = 2;
      dest.animate([{{opacity: 0}}, {{opacity: 1}}], {{duration: 300}}).onfinish = done;
    }} else if (forward) {{
      // The current page lifts off its left edge and turns away, revealing the next one
      from.style.zIndex = 2; dest.style.zIndex = 1;
      from.animate([
        {{transform: 'rotateY(0deg)'}},
        {{transform: 'rotateY(-35deg)', offset: .35}},
        {{transform: 'rotateY(-100deg)'}}
      ], {{duration: DUR, easing: 'cubic-bezier(.45,.05,.35,1)'}}).onfinish = done;
      from.querySelector('.shade').animate([{{opacity: 0}}, {{opacity: .9}}], {{duration: DUR}});
      dest.querySelector('.shade').animate([{{opacity: .6}}, {{opacity: 0}}], {{duration: DUR}});
    }} else {{
      // The previous page swings back in from the left edge, over the current one
      dest.style.zIndex = 2; from.style.zIndex = 1;
      dest.animate([
        {{transform: 'rotateY(-100deg)'}},
        {{transform: 'rotateY(-35deg)', offset: .65}},
        {{transform: 'rotateY(0deg)'}}
      ], {{duration: DUR, easing: 'cubic-bezier(.45,.05,.35,1)'}}).onfinish = done;
      dest.querySelector('.shade').animate([{{opacity: .9}}, {{opacity: 0}}], {{duration: DUR}});
      from.querySelector('.shade').animate([{{opacity: 0}}, {{opacity: .6}}], {{duration: DUR}});
    }}
    function done() {{ busy = false; show(to); }}
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
