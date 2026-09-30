#!/usr/bin/env python3
"""Web版のガイド(staff.html / admin.html)から印刷用HTMLとA4 PDFを生成する。

使い方:
    python3 print/build_pdf.py

前提:
    pip install playwright && playwright install chromium
    日本語フォント(Noto Sans CJK JP など)がインストールされていること

Web版のHTMLを編集したあとにこれを実行すると、pdf/ 配下のPDFが更新される。
印刷用の見た目は print/print.css で調整する。
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PDF_DIR = ROOT / "pdf"

# (Web版, 印刷用HTML, 出力PDF, フッターに出す文書名, 1行にする見出し)
PAGES = [
    ("staff.html", "staff-print.html", "staff-guide.pdf",
     "ふくのいもDB 入力ガイド／第1版",
     [("作業実績の<br>入力ガイド", "作業実績の入力ガイド")]),
    ("admin.html", "admin-print.html", "admin-guide.pdf",
     "ふくのいもDB 管理者ガイド／第1版",
     []),
]

FOOTER = """
<div style="width:100%;font-family:'Noto Sans CJK JP',sans-serif;font-size:7pt;
            color:#8b95a6;padding:0 12mm;display:flex;justify-content:space-between;">
  <span>{label}</span><span class="pageNumber"></span>
</div>
"""
EMPTY_HEADER = '<div style="display:none"></div>'


def find_chrome() -> str | None:
    """Playwright同梱のChromiumか、システムのChrome/Chromiumを探す。"""
    for pattern in ("chromium-*/chrome-linux/chrome", "chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium"):
        for base in (Path("/opt/pw-browsers"), Path.home() / ".cache/ms-playwright"):
            hits = sorted(base.glob(pattern)) if base.exists() else []
            if hits:
                return str(hits[-1])
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        found = shutil.which(name)
        if found:
            return found
    return None


def to_print_html(web_html: str, title: str, replacements: list[tuple[str, str]]) -> str:
    """Web版のbodyを取り出し、印刷用の外枠に入れ直す。"""
    match = re.search(r"<body[^>]*>(.*)</body>", web_html, re.S)
    if not match:
        raise ValueError("bodyが見つかりません")
    body = match.group(1)
    body_tag = re.search(r"<body([^>]*)>", web_html).group(1)

    body = re.sub(r'<nav class="toc".*?</nav>', "", body, flags=re.S)
    body = re.sub(r'\s*<a class="backlink".*?</a>', "", body, flags=re.S)
    body = body.replace('<div class="wrap">', "").replace('<div class="inner">', "")
    body = re.sub(r"\n\s*</div>\s*\n\s*</header>", "\n</header>", body)

    body = body.rstrip()
    if not body.endswith("</div>"):
        raise ValueError("wrapの閉じタグが見つかりません")
    body = body[: body.rfind("</div>")].rstrip()

    for old, new in replacements:
        body = body.replace(old, new)

    return (
        "<!doctype html>\n<html lang=\"ja\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>{title}</title>\n"
        '<link rel="stylesheet" href="print.css">\n</head>\n'
        f"<body{body_tag}>\n{body}\n</body>\n</html>\n"
    )


def main() -> int:
    chrome = find_chrome()
    if not chrome:
        print("Chromiumが見つかりません。playwright install chromium を実行してください。", file=sys.stderr)
        return 1

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwrightが未導入です。pip install playwright を実行してください。", file=sys.stderr)
        return 1

    PDF_DIR.mkdir(exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=chrome, args=["--no-sandbox"])
        page = browser.new_page()

        for web_name, print_name, pdf_name, label, replacements in PAGES:
            web_path = ROOT / web_name
            if not web_path.exists():
                print(f"skip: {web_name} がありません", file=sys.stderr)
                continue

            print_path = HERE / print_name
            title = label.split("／")[0].replace("ふくのいもDB ", "")
            print_path.write_text(
                to_print_html(web_path.read_text(encoding="utf-8"), title, replacements),
                encoding="utf-8",
            )

            out = PDF_DIR / pdf_name
            page.goto(print_path.as_uri(), wait_until="networkidle")
            page.emulate_media(media="print")
            page.wait_for_timeout(400)
            page.pdf(
                path=str(out),
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                display_header_footer=True,
                header_template=EMPTY_HEADER,
                footer_template=FOOTER.format(label=label),
                margin={"top": "13mm", "bottom": "16mm", "left": "12mm", "right": "12mm"},
            )
            print(f"OK: {out.relative_to(ROOT)}")

        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
