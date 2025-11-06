#!/usr/bin/env python3
"""
Simple HTTP Server for viewing the movies page
"""

import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

def main():
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    Handler = MyHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print("="*60)
        print("🎬 Movie Showcase Server")
        print("="*60)
        print(f"\n✅ Server running at: {url}")
        print(f"\n💡 Opening browser automatically...")
        print(f"\n⌨️  Press Ctrl+C to stop the server\n")
        print("="*60 + "\n")

        # Open browser
        webbrowser.open(url)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✅ Server stopped.")
            sys.exit(0)

if __name__ == "__main__":
    main()
