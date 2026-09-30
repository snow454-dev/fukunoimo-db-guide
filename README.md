# ふくのいもDB ガイド

生産管理システム「ふくのいもDB」の使い方ガイドです。読む人によって2種類に分かれています。

| ガイド | 対象 | ファイル |
| --- | --- | --- |
| 作業実績の入力ガイド | 現場で実績を入力する方 | `staff.html` / `pdf/staff-guide.pdf` |
| 管理者ガイド | 商品・スタッフを登録し、集計を見る方 | `admin.html` / `pdf/admin-guide.pdf` |

Web版はスマートフォンでも読めます。現場の方はアプリを使う端末でそのまま開けます。
PDF版はA4縦で、印刷して掲示・配布するためのものです。

---

## GitHub Pages で公開する

1. GitHub で新しいリポジトリを作る（公開範囲は用途に合わせて選ぶ）
2. このフォルダの中身をそのまま push する

   ```bash
   git init
   git add .
   git commit -m "ふくのいもDB ガイド 第1版"
   git branch -M main
   git remote add origin https://github.com/<ユーザー名>/<リポジトリ名>.git
   git push -u origin main
   ```

3. リポジトリの **Settings → Pages** を開く
4. **Source** を `Deploy from a branch`、**Branch** を `main` / `/ (root)` にして Save
5. 1〜2分待つと `https://<ユーザー名>.github.io/<リポジトリ名>/` で公開される

公開後、現場にはこのURLを共有してください。スマートフォンのホーム画面に追加しておくと、アプリと並べて開けます。

> **公開範囲について**
> Public リポジトリにすると、URLを知らない人でも検索などから到達できる可能性があります。社外に出したくない場合は Private リポジトリ＋GitHub Pages の公開制限（有料プランが必要）を検討するか、PDFの配布のみにしてください。

---

## ファイル構成

```
.
├── index.html          2つのガイドへの入口
├── staff.html          現場スタッフ向け（Web版）
├── admin.html          管理者向け（Web版）
├── assets/
│   └── style.css       Web版の共通スタイル
├── pdf/
│   ├── staff-guide.pdf 現場スタッフ向け（印刷用・A4 3ページ）
│   └── admin-guide.pdf 管理者向け（印刷用・A4 4ページ）
├── print/
│   ├── print.css       印刷用スタイル
│   ├── staff-print.html   ← build_pdf.py が自動生成
│   ├── admin-print.html   ← build_pdf.py が自動生成
│   └── build_pdf.py    PDF再生成スクリプト
├── .nojekyll           GitHub Pages のJekyll処理を無効化
└── README.md
```

---

## 内容を修正したいとき

**Web版**は `staff.html` / `admin.html` を直接編集します。見た目は `assets/style.css` で調整します。

**PDF**は手で作り直さず、Web版を編集したあとにスクリプトで再生成します。

```bash
pip install playwright
playwright install chromium
python3 print/build_pdf.py
```

`print/build_pdf.py` は Web版から目次やリンクを取り除いた印刷用HTMLを組み直し、A4のPDFとして `pdf/` に書き出します。印刷時の余白・文字サイズ・改ページは `print/print.css` で調整してください。

> 日本語が豆腐（□）になる場合は、実行環境に日本語フォントが入っていません。
> Ubuntu なら `sudo apt install fonts-noto-cjk` で入ります。

---

## デザインについて

2つのガイドは同じ設計で、見出し帯の色だけが違います。現場で紙を取り違えないためです。

- 現場スタッフ向け … 藍色
- 管理者向け … 金茶

色は `assets/style.css`（Web）と `print/print.css`（印刷）の `--indigo` / `--bronze` で定義しています。管理者向けは `<body class="admin">` を指定することで入れ替わります。

Web版はダークモードにも対応しています。閲覧する端末の設定に合わせて自動で切り替わります。

---

## 版数

第1版（2026年9月）

内容を更新したときは、各HTMLの末尾にある版表記と、`print/build_pdf.py` の `PAGES` に書かれたフッター文言を合わせて直してください。
