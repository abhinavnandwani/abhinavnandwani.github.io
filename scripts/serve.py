#!/usr/bin/env python3
"""
Development server with live reload for the personal website.
"""
import http.server
import socketserver
import sys
from pathlib import Path


def main():
    """Run a simple HTTP server with live reload."""
    PORT = 8000
    DIRECTORY = Path(__file__).parent.parent

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(DIRECTORY), **kwargs)

        def end_headers(self):
            # Add CORS headers for local development
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Expires", "0")
            super().end_headers()

    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Server running at http://localhost:{PORT}/")
            print("Press Ctrl+C to stop")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Port {PORT} is already in use. Try closing other servers.")
            sys.exit(1)
        raise


if __name__ == "__main__":
    main()
