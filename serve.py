#!/usr/bin/env python3
"""Simple HTTP server to serve the conference session browser."""
import http.server
import socketserver
import webbrowser
import os

PORT = 8000
os.chdir(os.path.dirname(__file__))

Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    print("Opening browser...")
    webbrowser.open(f"http://localhost:{PORT}")
    httpd.serve_forever()