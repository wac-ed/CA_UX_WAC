"""Build index.html: every slide in deck/slides, in deck/deck.json order, on one page.

Run:  python3 build.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).parent
deck = json.loads((ROOT / "deck" / "deck.json").read_text(encoding="utf-8"))

fonts = "".join(
    f'<link rel="stylesheet" href="{face["href"]}">\n'
    for face in deck.get("faces", {}).values()
    if face.get("href")
)

slides = []
for i, slide_id in enumerate(deck["order"], start=1):
    html = (ROOT / "deck" / "slides" / f"{slide_id}.html").read_text(encoding="utf-8")
    slides.append(
        f'<div class="frame" id="s{i}"><div class="stage">{html}</div>'
        f'<a class="num" href="#s{i}">{i} / {len(deck["order"])}</a></div>'
    )

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{deck["title"]}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
{fonts}<style>
  :root {{ --page: #E4E0D7; --ink: #16213A; }}
  * {{ box-sizing: border-box; margin: 0; }}
  body {{ background: var(--page); font-family: 'DM Sans', Arial, sans-serif; padding: 32px 16px 64px; }}
  .frame {{ position: relative; width: min(1280px, 100%); aspect-ratio: 16 / 9; margin: 0 auto 32px;
           overflow: hidden; border-radius: 12px; box-shadow: 0 8px 32px rgba(22,33,58,.18); container-type: inline-size; }}
  .stage {{ width: 1920px; height: 1080px; transform-origin: 0 0; transform: scale(calc(100cqw / 1920px)); }}
  @supports not (width: 1cqw) {{ .stage {{ transform: scale(.6667); }} }}
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
  .num {{ position: absolute; right: 12px; bottom: 8px; font-size: 12px; color: #5E6371; text-decoration: none; }}
</style>
</head>
<body>
{chr(10).join(slides)}
</body>
</html>
"""

(ROOT / "index.html").write_text(page, encoding="utf-8")
print(f"index.html: {len(slides)} slides")
