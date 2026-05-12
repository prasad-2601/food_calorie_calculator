from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from typing import Any


API_URL = "https://world.openfoodfacts.org/cgi/search.pl"


def parse_serving_grams(serving_size: str | None) -> float | None:
    if not serving_size:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*g", serving_size.lower())
    if match:
        return float(match.group(1))
    match = re.search(r"(\d+(?:\.\d+)?)\s*ml", serving_size.lower())
    if match:
        return float(match.group(1))
    return None


def number(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def search_products(query: str, limit: int = 4, timeout: float = 2.5) -> list[dict]:
    if not query.strip():
        return []

    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": min(max(limit, 1), 10),
        "fields": "code,product_name,brands,categories,nutriments,image_url,serving_size",
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "FoodCalorieCalculator/1.0 (learning project)",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return []

    products = []
    for product in payload.get("products", []):
        nutriments = product.get("nutriments") or {}
        kcal = number(nutriments.get("energy-kcal_100g") or nutriments.get("energy-kcal"))
        if kcal is None:
            kj = number(nutriments.get("energy_100g") or nutriments.get("energy-kj_100g"))
            kcal = kj / 4.184 if kj else None
        name = (product.get("product_name") or "").strip()
        if not name or kcal is None:
            continue

        products.append(
            {
                "id": f"off-{product.get('code') or name.lower().replace(' ', '-')}",
                "name": name,
                "brand": product.get("brands"),
                "category": product.get("categories") or "Packaged food",
                "kcal_per_100g": round(kcal, 1),
                "protein_per_100g": number(nutriments.get("proteins_100g")) or 0,
                "carbs_per_100g": number(nutriments.get("carbohydrates_100g")) or 0,
                "fat_per_100g": number(nutriments.get("fat_100g")) or 0,
                "fiber_per_100g": number(nutriments.get("fiber_100g")) or 0,
                "serving_g": parse_serving_grams(product.get("serving_size")) or 100,
                "image_url": product.get("image_url"),
                "source": "open_food_facts",
                "confidence": 0.58,
            }
        )

    return products
