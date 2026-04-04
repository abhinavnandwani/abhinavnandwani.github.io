# Personal Website

A minimal personal website for Abhinav Nandwani, hosted on GitHub Pages with custom domain `abhinavnandwani.com` (see `CNAME`).

## Site structure

```
abhinavnandwani.github.io/
├── favicon.ico             # Root copy (browsers request /favicon.ico); keep in sync with images/favicon.ico
├── index.html              # Home
├── resume.html             # Resume (embeds /files/resume.pdf)
├── blog.html               # Blog index
├── CNAME                   # Custom domain
├── css/style.css
├── js/theme.js             # Light/dark preference (localStorage + system)
├── posts/
│   ├── template.html       # Starting point for new posts
│   └── rlvr-training-costs.html  # Generated; see scripts/build_rlvr_post.py
├── content/notes/          # Source markdown + dashboard HTML for the RLVR post
├── images/                 # profile.png, favicon.ico, favicon.svg, PNG sizes
└── files/                  # resume.pdf, posters, legacy PDFs
```

## Local development

### Option 1: uv (recommended)

This project uses [uv](https://github.com/astral-sh/uv) for Python dependency management (dev server only; the live site has no runtime dependencies).

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # install uv once
uv sync
uv run serve-reload    # or: uv run serve
```

Then open `http://localhost:8000`.

### Option 2: no Python

```bash
python -m http.server 8000
```

## RLVR blog post (regenerate)

After editing `content/notes/rlvr-gpu-costs.md` or `content/notes/rlvr-dashboard-source.html`:

```bash
python3 scripts/build_rlvr_post.py
```

## Adding blog posts

1. Copy `posts/template.html` to `posts/your-slug.html`.
2. Update the copy in the new file: `<title>`, `meta description`, Open Graph tags, `link rel="canonical"`, `<h1>`, `<time>`, and body content. Replace every `my-post` / placeholder string that matches the template.
3. Add a preview block to `blog.html` (see existing `blog-post-preview` styles in `css/style.css`).

## Deployment

Push to `master`; GitHub Pages deploys automatically. The site is served at `https://abhinavnandwani.com` (allow a minute or two).

## Technologies

- HTML, CSS, and a small amount of vanilla JavaScript
- No build step for production assets
- GitHub Pages + `CNAME` for the custom domain

## License

© 2026 Abhinav Nandwani
