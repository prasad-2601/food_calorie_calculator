# Food Calorie Calculator

This is a full-stack food calorie calculator project. The idea is simple: the user enters a food item, selects the quantity, and the app shows the estimated calories along with protein, carbs, fat, serving weight, and the time required to burn those calories through different activities.

I mainly focused on Indian food items, but I also added many common foods from other countries so the app can be used for a wider range of meals.

## Features

- Search food items by name
- Shows matching food suggestions while typing
- Supports Indian foods like idli, dosa, biryani, chapati, rajma, chole, paneer dishes, samosa, poha, upma, and many more
- Also includes global foods like pizza, burger, pasta, sushi, fruits, nuts, drinks, and desserts
- Calculates calories based on quantity and unit
- Supports units like grams, kg, ml, cups, bowls, plates, pieces, slices, spoons, glasses, and servings
- Shows protein, carbs, fat, and fiber estimates
- Calculates approximate time needed to burn calories by walking, running, cycling, swimming, dancing, yoga, etc.
- Displays the selected food item on the frontend
- Backend and frontend are connected through APIs
- Can optionally search online food data using Open Food Facts
- Can optionally use USDA FoodData Central if an API key is provided

## Tech Stack

Backend:

- Python
- Built-in HTTP server
- JSON APIs

Frontend:

- HTML
- CSS
- JavaScript

No external package installation is required for the basic version of this project.

## Project Structure

```text
food_calorie_calculator/
  api/
    search.py
    calculate.py
    health.py
    units.py

  backend/
    app.py
    food_database.py
    burn_model.py
    open_food_facts.py
    usda_food_data.py

  frontend/
    index.html
    styles.css
    app.js

  README.md
```

## How To Run

Open the project folder in the terminal and run:

```powershell
python backend\app.py --port 8000
```

Then open this URL in the browser:

```text
http://localhost:8000
```

## Vercel Deployment

This project is configured for Vercel using `vercel.json`.

When you import the GitHub repository into Vercel, select:

```text
Application / Framework Preset: Other
```

Use these settings if Vercel asks:

```text
Framework Preset: Other
Build Command: leave empty
Install Command: leave empty
Output Directory: leave empty
```

The project is not Angular, so do not use the Angular preset. If Vercel tries to run `ng build`, change the framework preset to `Other` or keep the included `vercel.json` file in the repository.

For Vercel, the backend APIs are inside the `api/` folder:

```text
api/search.py
api/calculate.py
api/health.py
api/units.py
```

The frontend files stay inside the `frontend/` folder, and `vercel.json` routes the homepage to `frontend/index.html`.

If you want to use USDA FoodData Central on Vercel, add `FDC_API_KEY` in the Vercel project Environment Variables section.

## How It Works

1. The user enters the food name on the frontend.
2. The frontend sends the search text to the backend.
3. The backend searches the local food database and returns matching foods.
4. The user selects quantity, unit, and body weight.
5. The frontend sends this data to the calculate API.
6. The backend converts the quantity into grams.
7. Calories and nutrients are calculated using values per 100 grams.
8. The backend also calculates burn time using activity MET values.
9. The final result is displayed on the frontend.

## Optional USDA API

The app works without any API key. But if you want to use USDA FoodData Central, set the API key before starting the server:

```powershell
$env:FDC_API_KEY="your_api_key_here"
python backend\app.py --port 8000
```

## Example

If the user enters:

```text
Food: Idli
Quantity: 2
Unit: Pieces
Body weight: 65 kg
```

The app calculates the estimated calories and shows how many minutes of walking, running, cycling, and other activities may be needed to burn it.

## Accuracy Note

The calorie values are estimates. Actual calories can change depending on recipe, portion size, oil, ghee, brand, and cooking method. For packaged foods, the nutrition label is usually the best reference.

This project is made for learning and demonstration purposes.
