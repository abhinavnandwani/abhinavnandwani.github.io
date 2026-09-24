# Abhinav Nandwani

Personal website at [abhinavnandwani.com](https://abhinavnandwani.com): engineering work, research, writing, and practical learning resources.

The site uses static HTML, CSS, and vanilla JavaScript. GitHub Pages serves the `master` branch.

## Development

```sh
python3 -m http.server 8000
```

Open `http://localhost:8000`. For live reload, use `uv run serve-reload`.

## Structure

- `index.html`: homepage and the canonical navigation and footer used by the page builders.
- `blog.html`, `resume.html`: writing index and résumé viewer.
- `css/style.css`: shared design and homepage styles.
- `css/article.css`, `css/learning.css`: article, estimator, and guide layouts.
- `js/theme.js`: saved light/dark preference, defaulting to light.
- `js/home.js`: homepage interest controls.
- `posts/`: articles and a template for new posts.
- `content/notes/`: the RLVR article and interactive estimator sources.
- `learning/`: generated reading pages, guide PDFs, and original screenshots.
- `scripts/`: static page builders and development servers.
- `images/`, `files/`: photography, icons, research poster, and résumé PDFs.

## Generated pages

Rebuild the RLVR article after editing its Markdown or estimator source:

```sh
python3 scripts/build_rlvr_post.py
```

The CAE guide manuscripts and PDFs live in [cae-synopsys-guides](https://github.com/abhinavnandwani/cae-synopsys-guides). Rebuild their web editions with:

```sh
python3 scripts/build_learning.py --source ../cae-synopsys-guides
```

Both builders use `scripts/site_shell.py` for shared navigation, footer, and fonts. Update the matching navigation and footer in the hand-authored pages when changing them. See [DEVELOPMENT.md](DEVELOPMENT.md) for the guide publishing workflow and analytics configuration.

## Validation and deployment

Check desktop and mobile layouts in both themes. Exercise the interest controls, guide section links and copy buttons, PDF links, and RLVR estimator. Guide text and commands should match the canonical manuscripts; screenshots should remain unchanged.

Push to `master` to deploy through GitHub Pages. Verify the deployment and live pages after publishing.

© 2026 Abhinav Nandwani
