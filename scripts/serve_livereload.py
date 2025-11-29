#!/usr/bin/env python3
"""
Development server with live reload for the personal website.
Watches for changes in HTML, CSS, and JS files and auto-refreshes the browser.
"""
from pathlib import Path
from livereload import Server


def main():
    """Run development server with live reload."""
    server = Server()

    # Watch for changes in HTML, CSS, and JS files
    server.watch("*.html")
    server.watch("css/*.css")
    server.watch("js/*.js")
    server.watch("posts/*.html")

    print("Starting development server with live reload...")
    print("Server running at http://localhost:8000/")
    print("Watching for changes in HTML, CSS, and JS files...")
    print("Press Ctrl+C to stop")

    # Serve from current directory
    server.serve(root=".", port=8000, host="localhost", open_url_delay=1)


if __name__ == "__main__":
    main()
