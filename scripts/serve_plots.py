#!/usr/bin/env python3
"""Simple HTTP server to view plots in browser."""

import http.server
import socketserver
import os

PORT = 8000
os.chdir("examples/output")

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving plots at http://localhost:{PORT}")
    print("Available plots:")
    for f in os.listdir("."):
        if f.endswith(".png"):
            print(f"  http://localhost:{PORT}/{f}")
    print("\nPress Ctrl+C to stop")
    httpd.serve_forever()