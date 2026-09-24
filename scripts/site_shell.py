"""Shared navigation, footer, and font links for the static page builders."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FONT_URL = 'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;450;500;600;650;700&amp;family=IBM+Plex+Mono:wght@400;500&amp;family=Instrument+Serif:ital@0;1&amp;display=swap'


def navigation(active_path):
    home = (ROOT / 'index.html').read_text()
    nav = re.search(r'<nav>.*?</nav>', home, re.S).group()
    return nav.replace(f'href="{active_path}"', f'href="{active_path}" class="active" aria-current="page"')


def footer():
    home = (ROOT / 'index.html').read_text()
    return re.search(r'<footer>.*?</footer>', home, re.S).group()
