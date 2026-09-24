"""Shared navigation, footer, fonts, and social metadata for static page builders."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FONT_URL = 'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;450;500;600;650;700&amp;family=IBM+Plex+Mono:wght@400;500&amp;family=Instrument+Serif:ital@0;1&amp;display=swap'
SOCIAL_IMAGE_META = '''<meta property="og:image" content="https://abhinavnandwani.com/images/social-preview-v1.png">
    <meta property="og:image:type" content="image/png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="Abhinav Nandwani. Silicon, software and everything between.">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="https://abhinavnandwani.com/images/social-preview-v1.png">
    <meta name="twitter:image:alt" content="Abhinav Nandwani. Silicon, software and everything between.">'''


def navigation(active_path):
    home = (ROOT / 'index.html').read_text()
    nav = re.search(r'<nav>.*?</nav>', home, re.S).group()
    return nav.replace(f'href="{active_path}"', f'href="{active_path}" class="active" aria-current="page"')


def footer():
    home = (ROOT / 'index.html').read_text()
    return re.search(r'<footer>.*?</footer>', home, re.S).group()
