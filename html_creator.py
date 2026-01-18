import re
import html
import shutil
from pathlib import Path
import pandas as pd

INPUT_XLSX = "apps.xlsx"
CONTENT_DIR = Path("apps_content")

OUT_DIR = Path("site")
ASSETS_DIR = OUT_DIR / "assets"
OUTPUT_HTML = OUT_DIR / "index.html"
OUTPUT_CSS = OUT_DIR / "styles.css"

PAGE_TITLE = "Apps I’ve Worked On"
PAGE_SUBTITLE = (
    "A curated list of mobile apps where I contributed to development "
    "(Unity/C#). Use the buttons to open the store page and browse screenshots."
)
PAGE_NOTE = "This page is generated automatically."

ICON_SIZE = 72
SCREENSHOT_W = 220
SCREENSHOT_H = 390

def sanitize_title(title: str) -> str:
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", title)
    if sanitized.startswith("."):
        sanitized = "_" + sanitized[1:]
    return sanitized

def safe_copy(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def normalize_track_id(x) -> str:
    if x is None:
        return ""
    s = str(x).strip()
    if s.endswith(".0"):
        s = s[:-2]
    s = re.sub(r"\D", "", s)
    return s

def is_url(s: str) -> bool:
    return isinstance(s, str) and (s.startswith("http://") or s.startswith("https://"))

def esc(s) -> str:
    return html.escape("" if s is None else str(s))

def pick_column(df, *candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

def row_str(r, col):
    if not col:
        return ""
    v = r.get(col)
    return "" if pd.isna(v) else str(v)


def pretty_date(s: str) -> str:
    if not s:
        return ""
    dt = pd.to_datetime(str(s), errors="coerce")
    if pd.isna(dt):
        return str(s)
    return f"{dt.strftime('%b')} {dt.day}, {dt.year}"

def content_key_from_row(google_id: str, apple_id: str, title: str) -> str:
    if google_id:
        return google_id
    if apple_id:
        return f"apple_{apple_id}"
    return sanitize_title(title) if title else "unknown"

CSS = f"""
:root {{
  --bg: #ffffff;
  --text: #111827;
  --muted: #6b7280;
  --border: #e5e7eb;
  --card: #ffffff;
  --shadow: 0 6px 24px rgba(0,0,0,.06);
  --radius: 16px;
}}

* {{ box-sizing: border-box; }}

body {{
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Arial,sans-serif;
}}

.wrap {{
  max-width: 1120px;
  margin: 0 auto;
  padding: 28px 18px 48px;
}}

header {{
  display: grid;
  gap: 10px;
  margin-bottom: 18px;
}}

h1 {{
  font-size: 28px;
  margin: 0;
  letter-spacing: -0.02em;
}}

.subtitle {{
  color: var(--muted);
  margin: 0;
  line-height: 1.45;
  max-width: 80ch;
}}

.note {{
  color: var(--muted);
  font-size: 13px;
  margin-top: 6px;
}}

.toolbar {{
  display: flex;
  gap: 12px;
  align-items: center;
  margin: 18px 0 18px;
}}

.search {{
  flex: 1;
  max-width: 520px;
  padding: 12px 14px;
  border: 1px solid var(--border);
  border-radius: 12px;
  outline: none;
  font-size: 14px;
}}

.count {{
  color: var(--muted);
  font-size: 14px;
}}

.grid {{
  display: grid;
  gap: 16px;
}}

.card {{
  border: 1px solid var(--border);
  background: var(--card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow: hidden;
}}

.meta {{
  display: grid;
  grid-template-columns: {ICON_SIZE}px 1fr;
  gap: 14px;
  padding: 16px;
  align-items: center;
}}

.icon img {{
  width: {ICON_SIZE}px;
  height: {ICON_SIZE}px;
  object-fit: contain;
  border-radius: 16px;
  display: block;
  border: 1px solid var(--border);
  background: #fff;
}}

.icon-ph {{
  width: {ICON_SIZE}px;
  height: {ICON_SIZE}px;
  border-radius: 16px;
  border: 1px dashed var(--border);
  background: #fafafa;
}}

.title {{
  margin: 0;
  font-size: 18px;
  line-height: 1.2;
  letter-spacing: -0.01em;
}}

.sub {{
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}}

.chip {{
  display: inline-flex;
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: 999px;
  font-size: 12px;
  background: #fafafa;
}}

.ids {{
  margin-top: 8px;
  font-size: 13px;
  color: var(--muted);
  display: grid;
  gap: 4px;
}}

.actions {{
  margin-top: 12px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}}

.btn {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid #111827;
  background: #111827;
  color: #fff;
  text-decoration: none;
  font-size: 13px;
  white-space: nowrap;
}}

.btn:hover {{ opacity: .92; }}

.btn.apple {{
  background: #fff;
  color: #111827;
  border: 1px solid var(--border);
}}

.btn.apple:hover {{
  background: #fafafa;
}}

.shots {{
  display: flex;
  gap: 10px;
  padding: 0 16px 16px;
  overflow-x: auto;
}}

.shots.empty {{
  color: var(--muted);
  font-size: 13px;
}}

.shot img {{
  width: {SCREENSHOT_W}px;
  height: {SCREENSHOT_H}px;
  object-fit: cover;
  border-radius: 14px;
  border: 1px solid var(--border);
  display: block;
  background: #fff;
}}

@media (max-width: 720px) {{
  .shot img {{ width: 180px; height: 320px; }}
}}
"""

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    OUTPUT_CSS.write_text(CSS.strip() + "\n", encoding="utf-8")

    df = pd.read_excel(INPUT_XLSX, skiprows=1, engine="openpyxl").dropna(how="all")

    col_title = pick_column(df, "Title")
    col_genre = pick_column(df, "Genre")
    col_installs = pick_column(df, "Installs")
    col_release = pick_column(df, "Release Date", "Released", "ReleaseDate")

    col_google_id = pick_column(df, "Google App ID", "App ID")
    col_apple_id = pick_column(df, "Apple Track ID", "Apple ID", "Apple App ID")

    col_google_url = pick_column(df, "Google Url", "Google URL", "Url", "URL")
    col_apple_url = pick_column(df, "Apple Url", "Apple URL", "App Store Url", "App Store URL")

    if not col_title:
        raise RuntimeError(f"Missing 'Title' column. Found: {list(df.columns)}")

    if col_installs:
        def installs_to_int(x):
            if pd.isna(x): return 0
            s = str(x).replace(",", "").replace("+", "").strip()
            return int(s) if s.isdigit() else 0
        df["_installs_num"] = df[col_installs].apply(installs_to_int)
        df = df.sort_values(by="_installs_num", ascending=False).drop(columns=["_installs_num"])

    cards_html = []

    missing_assets = 0

    for _, r in df.iterrows():
        title = row_str(r, col_title)
        genre = row_str(r, col_genre)
        installs = row_str(r, col_installs)
        release = pretty_date(row_str(r, col_release))

        apple_id = normalize_track_id(row_str(r, col_apple_id))
        google_id = row_str(r, col_google_id).strip()

        google_url = row_str(r, col_google_url)
        apple_url = row_str(r, col_apple_url)

        key = content_key_from_row(google_id, apple_id, title)
        app_folder = CONTENT_DIR / key

        icon_src = app_folder / "icon.png"
        ss_srcs = [app_folder / f"screenshot{i}.png" for i in range(3)]

        icon_dst = ASSETS_DIR / key / "icon.png"
        ss_dsts = [ASSETS_DIR / key / f"screenshot{i}.png" for i in range(3)]

        icon_rel = ""
        if safe_copy(icon_src, icon_dst):
            icon_rel = icon_dst.relative_to(OUT_DIR).as_posix()
        else:
            missing_assets += 1

        ss_rel = []
        for src, dst in zip(ss_srcs, ss_dsts):
            if safe_copy(src, dst):
                ss_rel.append(dst.relative_to(OUT_DIR).as_posix())

        screenshots_html = (
            "<div class='shots'>"
            + "".join(
                [f"<a class='shot' href='{esc(p)}' target='_blank' rel='noopener noreferrer'><img src='{esc(p)}' alt='' loading='lazy'/></a>"
                 for p in ss_rel]
            )
            + "</div>"
        ) if ss_rel else "<div class='shots empty'>No screenshots</div>"

        buttons = []
        if is_url(google_url):
            buttons.append(f"<a class='btn' href='{esc(google_url)}' target='_blank' rel='noopener noreferrer'>Google Play</a>")
        if is_url(apple_url):
            buttons.append(f"<a class='btn apple' href='{esc(apple_url)}' target='_blank' rel='noopener noreferrer'>App Store</a>")
        buttons_html = "".join(buttons)

        ids_html = []
        if google_id:
            ids_html.append(f"<div>Google: {esc(google_id)}</div>")
        if apple_id:
            ids_html.append(f"<div>Apple: {esc(apple_id)}</div>")

        chips = []
        if genre:
            chips.append(f"<span class='chip'>{esc(genre)}</span>")
        if installs:
            chips.append(f"<span class='chip'>{esc(installs)} installs</span>")
        if release:
            chips.append(f"<span class='chip'>Released: {esc(release)}</span>")

        cards_html.append(f"""
<article class="card" data-search="{esc((title+' '+google_id+' '+apple_id+' '+genre).lower())}">
  <div class="meta">
    <div class="icon">
      {"<img src='"+esc(icon_rel)+"' alt='' loading='lazy'/>" if icon_rel else "<div class='icon-ph'></div>"}
    </div>
    <div class="info">
      <h2 class="title">{esc(title)}</h2>
      <div class="sub">{''.join(chips) if chips else "<span class='chip'>—</span>"}</div>
      <div class="ids">{''.join(ids_html) if ids_html else ""}</div>
      <div class="actions">{buttons_html}</div>
    </div>
  </div>
  {screenshots_html}
</article>
""")

    page = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{esc(PAGE_TITLE)}</title>
  <link rel="stylesheet" href="styles.css"/>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>{esc(PAGE_TITLE)}</h1>
      <p class="subtitle">{esc(PAGE_SUBTITLE)}</p>
      <div class="note">{esc(PAGE_NOTE)}</div>
    </header>

    <div class="toolbar">
      <input id="q" class="search" placeholder="Search by title / ids / genre..." />
      <div id="count" class="count"></div>
    </div>

    <section id="grid" class="grid">
      {''.join(cards_html)}
    </section>

    
  </div>

<script>
  const q = document.getElementById('q');
  const cards = Array.from(document.querySelectorAll('.card'));
  const count = document.getElementById('count');

  function update() {{
    const term = (q.value || '').toLowerCase().trim();
    let shown = 0;
    for (const c of cards) {{
      const hay = c.getAttribute('data-search') || '';
      const ok = !term || hay.includes(term);
      c.style.display = ok ? '' : 'none';
      if (ok) shown++;
    }}
    count.textContent = shown + ' shown';
  }}

  q.addEventListener('input', update);
  update();
</script>
</body>
</html>
"""
    OUTPUT_HTML.write_text(page, encoding="utf-8")
    print(f"Written: {OUTPUT_HTML}")
    print(f"Written: {OUTPUT_CSS}")

if __name__ == "__main__":
    main()
