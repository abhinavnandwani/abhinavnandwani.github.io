# Personal Website

A minimal personal website for Abhinav Nandwani, hosted on GitHub Pages.

## Site Structure

```
abhinavnandwani.github.io/
├── index.html          # Home page with bio
├── resume.html         # Resume/CV page
├── blog.html           # Blog listing
├── css/
│   └── style.css       # Stylesheet
├── js/                 # JavaScript (if needed)
├── posts/              # Individual blog posts
├── images/             # Images and favicon
│   ├── profile.png
│   └── favicon.ico
├── files/              # Downloadable files
│   └── Resume-v2-RTL.pdf
└── CNAME               # Custom domain config
```

## Local Development

### Option 1: Using uv (Recommended)

This project uses [uv](https://github.com/astral-sh/uv) for Python dependency management.

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run development server with simple HTTP server
uv run serve

# OR run with live reload (auto-refreshes on file changes) - RECOMMENDED
uv run serve-reload
```

The `serve-reload` command watches for changes in HTML, CSS, and JS files and automatically refreshes your browser.

You can also run the scripts directly:
```bash
uv run python scripts/serve.py          # Simple server
uv run python scripts/serve_livereload.py  # Live reload server
```

### Option 2: Without uv

Simply open `index.html` in a browser, or use Python's built-in server:

```bash
python -m http.server 8000
```

Then visit `http://localhost:8000`

## Adding Blog Posts

1. Create a new HTML file in the `posts/` directory (e.g., `my-first-post.html`)
2. Use this template:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Post Title - Abhinav Nandwani</title>
    <meta name="description" content="Post description">
    <link rel="icon" href="/images/favicon.ico">
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <nav>
        <div class="container">
            <a href="/" class="nav-home">Abhinav Nandwani</a>
            <ul class="nav-links">
                <li><a href="/resume.html">Resume</a></li>
                <li><a href="/blog.html">Blog</a></li>
            </ul>
        </div>
    </nav>

    <main class="container">
        <article>
            <header class="page-header">
                <h1>Post Title</h1>
                <div class="post-meta">
                    <time datetime="2025-01-15">January 15, 2025</time>
                </div>
            </header>

            <section>
                <!-- Your post content here -->
                <p>Your content...</p>
            </section>

            <div class="back-link">
                <a href="/blog.html">← Back to Blog</a>
            </div>
        </article>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 Abhinav Nandwani</p>
        </div>
    </footer>
</body>
</html>
```

3. Update `blog.html` to add a link to your new post:

```html
<article class="blog-post-preview">
    <h2><a href="/posts/my-first-post.html">Post Title</a></h2>
    <time datetime="2025-01-15">January 15, 2025</time>
    <p>Brief excerpt of the post...</p>
</article>
```

## Deployment

This site is automatically deployed via GitHub Pages. Just push to the `master` branch:

```bash
git add .
git commit -m "Update site"
git push origin master
```

Changes will be live at https://abhinavnandwani.com in a few minutes.

## Custom Domain

The custom domain is configured via the `CNAME` file. Current domain: `abhinavnandwani.com`

## Technologies

- Plain HTML5
- CSS3
- No build process
- No dependencies
- GitHub Pages hosting

## License

© 2025 Abhinav Nandwani
