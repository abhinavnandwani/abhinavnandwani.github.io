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
├── index.html              # Home page
├── resume.html             # Resume page
├── blog.html               # Blog listing
├── css/style.css          # Styles
├── posts/                 # Blog posts
│   └── template.html      # Template for new posts
├── images/                # Images
├── files/                 # Downloadable files
├── scripts/               # Python dev scripts
│   ├── serve.py          # Simple server
│   └── serve_livereload.py  # Live reload server
└── pyproject.toml        # Python project config
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
