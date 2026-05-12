from http.server import BaseHTTPRequestHandler
import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app import ApiError, calculate


def send_json(handler, payload, status=200):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            send_json(self, calculate(payload))
        except ApiError as exc:
            send_json(self, {"error": exc.message}, exc.status)
        except json.JSONDecodeError:
            send_json(self, {"error": "Invalid JSON request body."}, 400)
        except Exception as exc:
            send_json(self, {"error": f"Unexpected server error: {exc}"}, 500)
