# Development Guide

## Quick Start

### Install uv (one-time setup)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Run Development Server

**Option 1: Using installed commands (recommended)**
```bash
uv run serve          # Simple HTTP server
uv run serve-reload   # Live reload server (RECOMMENDED)
```

**Option 2: Run scripts directly**
```bash
uv run python scripts/serve.py          # Simple server
uv run python scripts/serve_livereload.py  # Live reload server
```

The live reload server automatically refreshes your browser when you edit HTML, CSS, or JS files.

Visit: http://localhost:8000

## Project Structure

```
abhinavnandwani.github.io/
├── index.html
├── resume.html
├── blog.html
├── CNAME                   # abhinavnandwani.com
├── css/style.css
├── js/theme.js
├── posts/
│   └── template.html
├── images/
├── files/                  # resume.pdf, assets
├── scripts/                # Dev-only Python servers
│   ├── serve.py
│   └── serve_livereload.py
└── pyproject.toml
```

## Common Tasks

### Adding a Blog Post

1. Copy `posts/template.html` to `posts/your-post-name.html`
2. Edit the new file with your content
3. Update `blog.html` to add a link to your post
4. The live reload server will automatically refresh your browser

### Editing Styles

1. Edit `css/style.css`
2. Save the file
3. Browser refreshes automatically (if using live reload server)

### Testing Before Deploy

```bash
# Start dev server
uv run python scripts/serve_livereload.py

# Test in browser at http://localhost:8000
# Check all pages:
# - http://localhost:8000/
# - http://localhost:8000/resume.html
# - http://localhost:8000/blog.html
```

## Deployment

### Learning Resources

The canonical CAE guide manuscripts, PDFs, and lab live in
[cae-synopsys-guides](https://github.com/abhinavnandwani/cae-synopsys-guides).
Regenerate the web editions with:

```bash
python3 scripts/build_learning.py --source ../cae-synopsys-guides
```

The renderer uses Python's standard library. It reads the same manuscripts and
image crop definitions as the document builders, copies the existing PDFs and
original screenshots, and writes five static pages under `learning/`.
`learning/cae-synopsys/source-manifest.json` records content hashes. Update the
canonical manuscripts and rebuild their PDFs first; never edit the generated
guide HTML independently. Check desktop and narrow layouts, copy buttons,
section links, screenshots, and downloads after rebuilding.

### Shared design and résumé preview

`css/style.css` defines the shared palette, typography, and homepage layouts.
`css/article.css` keeps the article and estimator rules separate. The two page
builders use `scripts/site_shell.py` to read navigation and footer markup from
`index.html`. Update the hand-authored blog, résumé, and post template shells
alongside it, then run both builders.

The homepage portrait uses a square CSS crop of `images/abhinav-lakeside.jpg`.

Shared-link previews use `images/social-preview-v1.png`, exported at 1200 × 630
from the adjacent SVG. After changing the artwork, export a new PNG and update
the image URL in the hand-authored page heads and `scripts/site_shell.py`.
Use a new filename when replacing the image because sharing apps cache previews.

The résumé page shows a rendered preview with a direct link to the PDF, so it
does not depend on an embedded browser PDF viewer. After replacing
`files/resume.pdf`, regenerate its preview with Poppler:

```sh
pdftoppm -f 1 -singlefile -scale-to 1800 -png files/resume.pdf images/resume-preview
```

Check the preview against the current PDF. If the résumé gains additional
pages, include those pages in the preview as well.

### Analytics

Umami tracks production pageviews across the site. The tracker is restricted to
`abhinavnandwani.com` and `www.abhinavnandwani.com`, so localhost previews do not
record traffic. Hash changes from guide section links are excluded.

Dashboard:
https://cloud.umami.is/analytics/us/websites/296d775c-3d14-4127-9e02-99e92e9e109f

- Use Pages to compare the three guide paths and Sources for referrers.
- Events records `PDF download`, `GitHub click`, and successful `Copy command`.
- Filter the event's `guide` property by `verification`, `rtl`, or `pd`.
  Overview links use `all`. Copy events also include the section and block number.
- A PDF event counts a download click, not completion or an offline read.
  A GitHub click does not establish a clone. Visitors are estimates, not a list
  of students or proof that someone completed a guide.
- Add UTM parameters to shared page links when useful, for example
  `?utm_source=discord&utm_medium=community&utm_campaign=cae-guides`.

No API key or login credential is embedded in the site. The website ID in the
public tracking snippet identifies the analytics destination. Guide controls
remain usable if analytics is blocked. The reading pages also work without JS.

```bash
# Commit changes
git add .
git commit -m "Your commit message"

# Push to GitHub Pages
git push origin master
```

Site will be live at https://abhinavnandwani.com in ~1-2 minutes.

## Troubleshooting

### Port already in use
If port 8000 is already in use, kill the existing process:
```bash
lsof -ti:8000 | xargs kill -9
```

### Dependencies not found
Make sure uv installs dependencies on first run:
```bash
uv sync
```

### Live reload not working
- Make sure you're using `serve_livereload.py`, not `serve.py`
- Check that the browser console doesn't show connection errors
- Try hard-refreshing the page (Cmd+Shift+R on Mac)

### Theme always dark
Older builds wrote your OS theme into `localStorage` on every load, which could make the site feel stuck. Clear stored data for this site, or use the theme button once to set light/dark explicitly. Default for new visitors is **light**; only a **click** on the theme control persists dark (or light) for return visits.
