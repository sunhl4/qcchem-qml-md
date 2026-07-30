#!/usr/bin/env python3
"""Serve Docusaurus build with no-cache headers and baseUrl /qcchem-qml-md/."""
from __future__ import annotations

import http.server
import os
import urllib.parse

ROOT = os.path.join(os.path.dirname(__file__), "build")
BASE = "/qcchem-qml-md"
PORT = 3010


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def _rewrite(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = ("?" + parsed.query) if parsed.query else ""
        if path in ("/", ""):
            self.path = BASE + "/" + qs
            return
        if path == BASE or path == BASE + "/":
            self.path = "/index.html" + qs
        elif path.startswith(BASE + "/"):
            rest = path[len(BASE) :] or "/index.html"
            self.path = rest + qs

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", ""):
            self.send_response(302)
            self.send_header("Location", BASE + "/")
            self.end_headers()
            return
        self._rewrite()
        return super().do_GET()

    def do_HEAD(self) -> None:  # noqa: N802
        self._rewrite()
        return super().do_HEAD()


if __name__ == "__main__":
    os.chdir(ROOT)
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Serving {ROOT} at http://0.0.0.0:{PORT}{BASE}/ (no-cache)", flush=True)
    server.serve_forever()
