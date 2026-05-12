const state = {
  selectedFood: null,
  suggestions: [],
  lastResult: null,
};

const $ = (id) => document.getElementById(id);

const elements = {
  foodInput: $("foodInput"),
  quantityInput: $("quantityInput"),
  unitInput: $("unitInput"),
  weightInput: $("weightInput"),
  weightUnitInput: $("weightUnitInput"),
  suggestions: $("suggestions"),
  calculateBtn: $("calculateBtn"),
  globalSearchBtn: $("globalSearchBtn"),
  statusLine: $("statusLine"),
  foodVisual: $("foodVisual"),
  selectedCuisine: $("selectedCuisine"),
  selectedName: $("selectedName"),
  sourceBadge: $("sourceBadge"),
  calorieValue: $("calorieValue"),
  gramValue: $("gramValue"),
  proteinValue: $("proteinValue"),
  carbValue: $("carbValue"),
  fatValue: $("fatValue"),
  proteinBar: $("proteinBar"),
  carbBar: $("carbBar"),
  fatBar: $("fatBar"),
  burnWeight: $("burnWeight"),
  burnGrid: $("burnGrid"),
  notes: $("notes"),
};

function debounce(fn, wait = 250) {
  let timeout;
  return (...args) => {
    window.clearTimeout(timeout);
    timeout = window.setTimeout(() => fn(...args), wait);
  };
}

function setStatus(message, isError = false) {
  elements.statusLine.textContent = message;
  elements.statusLine.style.color = isError ? "#b13a5b" : "#667085";
}

function weightInKg() {
  const value = Number(elements.weightInput.value || 70);
  return elements.weightUnitInput.value === "lb" ? value * 0.453592 : value;
}

function renderFoodVisual(food) {
  const label = food?.name || elements.foodInput.value.trim() || "Your meal appears here";
  elements.selectedName.textContent = label;
  elements.selectedCuisine.textContent = food ? `${food.cuisine} · ${food.category}` : "Choose a food";

  if (food?.imageUrl) {
    elements.foodVisual.innerHTML = `<img src="${food.imageUrl}" alt="${food.name}" />`;
  } else {
    elements.foodVisual.textContent = food?.emoji || "🍽️";
  }
}

function renderSuggestions(items) {
  state.suggestions = items;
  if (!items.length) {
    elements.suggestions.innerHTML = "";
    return;
  }

  elements.suggestions.innerHTML = items
    .map(
      (item, index) => `
        <button class="suggestion ${state.selectedFood?.id === item.id ? "active" : ""}" type="button" data-index="${index}">
          <span class="suggestion-emoji">${item.emoji || "🍽️"}</span>
          <span>
            <strong>${item.name}</strong>
            <small>${item.cuisine || "Global"} · ${Math.round((item.confidence || 0) * 100)}%</small>
          </span>
        </button>
      `,
    )
    .join("");

  elements.suggestions.querySelectorAll(".suggestion").forEach((button) => {
    button.addEventListener("click", () => {
      const item = state.suggestions[Number(button.dataset.index)];
      state.selectedFood = item;
      elements.foodInput.value = item.name;
      renderFoodVisual(item);
      renderSuggestions(state.suggestions);
      setStatus("Selected from local database");
    });
  });
}

async function searchFoods(includeExternal = false) {
  const query = elements.foodInput.value.trim();
  state.selectedFood = null;
  renderFoodVisual(null);

  if (query.length < 2) {
    renderSuggestions([]);
    setStatus("Ready");
    return;
  }

  setStatus(includeExternal ? "Searching local and global data..." : "Searching local data...");
  const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&limit=6&external=${includeExternal ? 1 : 0}`);
  const data = await response.json();
  const local = data.local || [];
  const external = (data.external || []).map((item) => ({
    ...item,
    emoji: "🍽️",
    cuisine: "Global",
    category: item.category || "Packaged food",
    caloriesPer100g: item.kcal_per_100g,
    imageUrl: item.image_url,
  }));
  const merged = [...local, ...external].slice(0, 6);
  renderSuggestions(merged);

  if (merged[0]) {
    state.selectedFood = merged[0];
    renderFoodVisual(merged[0]);
  }

  setStatus(merged.length ? `${merged.length} match${merged.length === 1 ? "" : "es"} found` : "No matches yet");
}

function renderMacros(macros) {
  const protein = macros.protein || 0;
  const carbs = macros.carbs || 0;
  const fat = macros.fat || 0;
  const maxMacro = Math.max(protein, carbs, fat, 1);

  elements.proteinValue.textContent = `${protein} g`;
  elements.carbValue.textContent = `${carbs} g`;
  elements.fatValue.textContent = `${fat} g`;
  elements.proteinBar.style.width = `${Math.min((protein / maxMacro) * 100, 100)}%`;
  elements.carbBar.style.width = `${Math.min((carbs / maxMacro) * 100, 100)}%`;
  elements.fatBar.style.width = `${Math.min((fat / maxMacro) * 100, 100)}%`;
}

function renderBurn(items) {
  elements.burnGrid.innerHTML = items
    .map(
      (item) => `
        <article class="burn-card">
          <span>${item.name}</span>
          <strong>${item.minutes} min</strong>
          <span>${item.pace} · ${item.caloriesPerMinute} kcal/min</span>
        </article>
      `,
    )
    .join("");
}

function renderNotes(warnings = [], error = "") {
  const notes = error ? [error] : warnings;
  elements.notes.innerHTML = notes
    .map((note) => `<div class="note ${error ? "error" : ""}">${note}</div>`)
    .join("");
}

async function calculate() {
  const foodName = elements.foodInput.value.trim();
  if (!foodName) {
    setStatus("Enter a food item", true);
    renderNotes([], "Enter a food item first.");
    return;
  }

  setStatus("Calculating...");
  renderNotes();

  const payload = {
    foodName,
    foodId: state.selectedFood?.source === "local_estimate" ? state.selectedFood.id : "",
    quantity: Number(elements.quantityInput.value || 1),
    unit: elements.unitInput.value,
    weightKg: weightInKg(),
    includeExternal: true,
  };

  try {
    const response = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Unable to calculate");
    }

    state.lastResult = data;
    state.selectedFood = data.food;
    elements.sourceBadge.textContent =
      data.food.source === "open_food_facts"
        ? "Open Food Facts"
        : data.food.source === "usda_fooddata_central"
          ? "USDA FDC"
          : "Local estimate";
    renderFoodVisual(data.food);
    elements.calorieValue.textContent = data.nutrition.calories.toLocaleString();
    elements.gramValue.textContent = `${data.quantity.estimatedGrams} g estimated`;
    renderMacros(data.nutrition.macros);
    renderBurn(data.burn);
    elements.burnWeight.textContent = `Based on ${Math.round(data.weightKg * 10) / 10} kg`;
    renderNotes(data.warnings);
    setStatus(`Calculated ${data.food.name}`);
  } catch (error) {
    setStatus(error.message, true);
    renderNotes([], error.message);
  }
}

const debouncedSearch = debounce(() => searchFoods(false), 220);

elements.foodInput.addEventListener("input", debouncedSearch);
elements.foodInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    calculate();
  }
});
elements.calculateBtn.addEventListener("click", calculate);
elements.globalSearchBtn.addEventListener("click", () => searchFoods(true));
elements.weightInput.addEventListener("input", () => {
  if (state.lastResult) {
    calculate();
  }
});
elements.weightUnitInput.addEventListener("change", () => {
  if (state.lastResult) {
    calculate();
  }
});

renderSuggestions([
  { id: "seed-1", name: "Chicken biryani", cuisine: "Indian", category: "Rice", emoji: "🍛", confidence: 1 },
  { id: "seed-2", name: "Masala dosa", cuisine: "Indian", category: "Breakfast", emoji: "🥞", confidence: 1 },
  { id: "seed-3", name: "Rajma curry", cuisine: "Indian", category: "Curry", emoji: "🍲", confidence: 1 },
  { id: "seed-4", name: "Paneer butter masala", cuisine: "Indian", category: "Curry", emoji: "🍲", confidence: 1 },
]);
