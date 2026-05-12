from __future__ import annotations

import argparse
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from burn_model import burn_times
from food_database import (
    UNIT_LABELS,
    best_match,
    external_food_to_local,
    grams_for_quantity,
    nutrition_for,
    public_food,
    search_foods,
)
from open_food_facts import search_products
from usda_food_data import search_fooddata


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"


class ApiError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status


def json_response(handler: SimpleHTTPRequestHandler, payload: dict | list, status: int = 200) -> None:
    body = json.dumps(payload, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(body)


def read_json(handler: SimpleHTTPRequestHandler) -> dict:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
        body = handler.rfile.read(length).decode("utf-8")
        return json.loads(body or "{}")
    except json.JSONDecodeError as exc:
        raise ApiError("Invalid JSON request body.", 400) from exc


def calculate(payload: dict) -> dict:
    food_name = str(payload.get("foodName") or "").strip()
    food_id = str(payload.get("foodId") or "").strip()
    quantity = payload.get("quantity", 1)
    unit = str(payload.get("unit") or "serving").strip()
    weight_kg = float(payload.get("weightKg") or 70)
    include_external = bool(payload.get("includeExternal", True))

    try:
        quantity = float(quantity)
    except (TypeError, ValueError) as exc:
        raise ApiError("Quantity must be a number.", 400) from exc

    if quantity <= 0:
        raise ApiError("Quantity must be greater than zero.", 400)
    if not food_name and not food_id:
        raise ApiError("Food item is required.", 400)
    if unit not in UNIT_LABELS:
        raise ApiError(f"Unsupported unit: {unit}", 400)

    item = None
    confidence = 0.0
    if food_id:
        from food_database import get_food_by_id

        item = get_food_by_id(food_id)
        confidence = 1.0 if item else 0.0
    if item is None:
        item, confidence = best_match(food_name)

    warnings = []
    external_candidates = []
    if (item is None or confidence < 0.47) and include_external:
        external_candidates = [
            *search_fooddata(food_name, limit=3),
            *search_products(food_name, limit=3),
        ]
        if external_candidates:
            item = external_food_to_local(external_candidates[0])
            confidence = external_candidates[0].get("confidence", 0.58)

    if item is None:
        raise ApiError("Food not found. Try a simpler name like 'idli', 'rice', or 'chicken biryani'.", 404)

    grams, conversion_note = grams_for_quantity(item, quantity, unit)
    nutrition = nutrition_for(item, grams)
    if conversion_note:
        warnings.append(conversion_note)
    if confidence < 0.65:
        warnings.append("This is a lower-confidence match; check the food name or package label.")
    if item.get("source") == "open_food_facts":
        warnings.append("Online product data can be incomplete because it is community contributed.")
    if item.get("source") == "usda_fooddata_central":
        warnings.append("USDA values are per 100 g estimates; recipe and serving differences still matter.")

    return {
        "food": {
            **public_food(item, confidence),
            "imageUrl": item.get("image_url"),
            "brand": item.get("brand"),
        },
        "quantity": {
            "value": quantity,
            "unit": unit,
            "unitLabel": UNIT_LABELS[unit],
            "estimatedGrams": nutrition["grams"],
        },
        "nutrition": nutrition,
        "burn": burn_times(nutrition["calories"], weight_kg),
        "weightKg": weight_kg,
        "warnings": warnings,
        "externalAlternatives": external_candidates[1:],
    }


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND), **kwargs)

    def end_headers(self) -> None:
        if self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            return json_response(self, {"ok": True, "app": "Food Calorie Calculator"})

        if parsed.path == "/api/units":
            return json_response(self, {"units": UNIT_LABELS})

        if parsed.path == "/api/search":
            params = parse_qs(parsed.query)
            query = params.get("q", [""])[0]
            limit = int(params.get("limit", ["8"])[0])
            include_external = params.get("external", ["0"])[0] in {"1", "true", "yes"}
            local_matches = search_foods(query, limit=limit)
            external_matches = []
            if include_external and len(query.strip()) >= 3:
                external_matches = [
                    *search_fooddata(query, limit=3),
                    *search_products(query, limit=3),
                ][:6]
            return json_response(
                self,
                {
                    "query": query,
                    "local": local_matches,
                    "external": external_matches,
                },
            )

        if parsed.path.startswith("/api/"):
            return json_response(self, {"error": "Not found"}, 404)

        return super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/calculate":
            return json_response(self, {"error": "Not found"}, 404)

        try:
            payload = read_json(self)
            result = calculate(payload)
        except ApiError as exc:
            return json_response(self, {"error": exc.message}, exc.status)
        except Exception as exc:
            return json_response(self, {"error": f"Unexpected server error: {exc}"}, 500)

        return json_response(self, result)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Food Calorie Calculator")
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", default=int(os.environ.get("PORT", "8000")), type=int)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Food Calorie Calculator running at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
