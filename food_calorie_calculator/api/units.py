from http.server import BaseHTTPRequestHandler
import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from food_database import UNIT_LABELS


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({"units": UNIT_LABELS}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
