from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any


API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


def number(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def nutrient_amount(food: dict, *names: str) -> float:
    wanted = {name.lower() for name in names}
    for nutrient in food.get("foodNutrients", []):
        name = str(nutrient.get("nutrientName") or "").lower()
        unit = str(nutrient.get("unitName") or "").lower()
        amount = number(nutrient.get("value"))
        if amount is None:
            continue
        if name in wanted:
            if name == "energy" and unit == "kj":
                return amount / 4.184
            return amount
    return 0.0


def search_fooddata(query: str, limit: int = 3, timeout: float = 2.5) -> list[dict]:
    api_key = os.environ.get("FDC_API_KEY")
    if not api_key or not query.strip():
        return []

    params = {
        "api_key": api_key,
        "query": query,
        "pageSize": min(max(limit, 1), 10),
        "dataType": ["Foundation", "SR Legacy", "Survey (FNDDS)"],
    }
    query_parts = []
    for key, value in params.items():
        if isinstance(value, list):
            for item in value:
                query_parts.append((key, item))
        else:
            query_parts.append((key, value))
    url = f"{API_URL}?{urllib.parse.urlencode(query_parts)}"
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

    results = []
    for food in payload.get("foods", []):
        kcal = nutrient_amount(food, "Energy")
        name = str(food.get("description") or "").title()
        if not name or kcal <= 0:
            continue

        serving_size = number(food.get("servingSize")) if food.get("servingSizeUnit") == "g" else None
        results.append(
            {
                "id": f"fdc-{food.get('fdcId')}",
                "name": name,
                "brand": food.get("brandOwner"),
                "category": food.get("foodCategory") or food.get("dataType") or "FoodData Central",
                "kcal_per_100g": round(kcal, 1),
                "protein_per_100g": nutrient_amount(food, "Protein"),
                "carbs_per_100g": nutrient_amount(food, "Carbohydrate, by difference"),
                "fat_per_100g": nutrient_amount(food, "Total lipid (fat)"),
                "fiber_per_100g": nutrient_amount(food, "Fiber, total dietary"),
                "serving_g": serving_size or 100,
                "image_url": None,
                "source": "usda_fooddata_central",
                "confidence": 0.68,
            }
        )

    return results
