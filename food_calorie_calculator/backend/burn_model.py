"""Activity calorie burn estimates.

Formula:
    kcal/min = MET * 3.5 * body_weight_kg / 200

MET values are common compendium-style estimates. They vary by speed,
fitness, terrain, body composition, and individual physiology.
"""

ACTIVITIES = [
    {
        "id": "walk",
        "name": "Moderate walk",
        "met": 3.8,
        "pace": "4.5-5.5 km/h",
    },
    {
        "id": "brisk_walk",
        "name": "Brisk walk",
        "met": 4.8,
        "pace": "5.6-6.3 km/h",
    },
    {
        "id": "run",
        "name": "Running",
        "met": 9.8,
        "pace": "9.7 km/h",
    },
    {
        "id": "cycle",
        "name": "Cycling",
        "met": 7.5,
        "pace": "moderate",
    },
    {
        "id": "swim",
        "name": "Swimming",
        "met": 6.0,
        "pace": "moderate",
    },
    {
        "id": "dance",
        "name": "Dancing",
        "met": 5.5,
        "pace": "active",
    },
    {
        "id": "strength",
        "name": "Strength training",
        "met": 6.0,
        "pace": "vigorous",
    },
    {
        "id": "yoga",
        "name": "Yoga",
        "met": 2.5,
        "pace": "hatha",
    },
]


def burn_times(calories: float, weight_kg: float = 70.0) -> list[dict]:
    """Return minutes needed to burn calories for each configured activity."""
    safe_weight = min(max(float(weight_kg or 70), 30), 250)
    results = []
    for activity in ACTIVITIES:
        kcal_per_min = activity["met"] * 3.5 * safe_weight / 200
        minutes = calories / kcal_per_min if kcal_per_min else 0
        results.append(
            {
                **activity,
                "minutes": round(minutes, 1),
                "caloriesPerMinute": round(kcal_per_min, 2),
            }
        )
    return results
