from http.server import BaseHTTPRequestHandler
import json
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from food_database import search_foods
from open_food_facts import search_products
from usda_food_data import search_fooddata


def send_json(handler, payload, status=200):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)
        query = params.get("q", [""])[0]
        limit = int(params.get("limit", ["8"])[0])
        include_external = params.get("external", ["0"])[0] in {"1", "true", "yes"}

        external_matches = []
        if include_external and len(query.strip()) >= 3:
            external_matches = [
                *search_fooddata(query, limit=3),
                *search_products(query, limit=3),
            ][:6]

        send_json(
            self,
            {
                "query": query,
                "local": search_foods(query, limit=limit),
                "external": external_matches,
            },
        )
