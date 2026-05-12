from __future__ import annotations

import math
import re
from difflib import SequenceMatcher
from typing import Any


Food = dict[str, Any]


def food(
    id: str,
    name: str,
    kcal: float,
    protein: float,
    carbs: float,
    fat: float,
    fiber: float,
    serving_g: float,
    cuisine: str,
    category: str,
    emoji: str,
    aliases: list[str] | None = None,
    measures: dict[str, float] | None = None,
) -> Food:
    return {
        "id": id,
        "name": name,
        "aliases": aliases or [],
        "cuisine": cuisine,
        "category": category,
        "emoji": emoji,
        "serving_g": serving_g,
        "kcal_per_100g": kcal,
        "protein_per_100g": protein,
        "carbs_per_100g": carbs,
        "fat_per_100g": fat,
        "fiber_per_100g": fiber,
        "measures": measures or {},
        "source": "local_estimate",
    }


FOODS: list[Food] = [
    food("idli", "Idli", 145, 4.5, 29, 0.7, 1.7, 39, "Indian", "Breakfast", "🍘", ["idly", "rice idli", "south indian idli"], {"piece": 39, "serving": 78}),
    food("dosa_plain", "Plain dosa", 168, 3.8, 29, 3.9, 1.8, 90, "Indian", "Breakfast", "🥞", ["dosai", "sada dosa", "dose"], {"piece": 90, "serving": 90}),
    food("masala_dosa", "Masala dosa", 185, 4.2, 30, 5.1, 2.2, 180, "Indian", "Breakfast", "🥞", ["mysore masala dosa", "potato dosa"], {"piece": 180, "serving": 180}),
    food("rava_dosa", "Rava dosa", 190, 4.0, 32, 5.0, 2.0, 120, "Indian", "Breakfast", "🥞", ["suji dosa", "semolina dosa"], {"piece": 120, "serving": 120}),
    food("uttapam", "Uttapam", 175, 4.6, 28, 4.8, 2.1, 150, "Indian", "Breakfast", "🥞", ["uthappam", "onion uttapam"], {"piece": 150, "serving": 150}),
    food("poha", "Poha", 130, 2.8, 23, 3.0, 2.0, 180, "Indian", "Breakfast", "🥣", ["aval", "flattened rice poha"], {"cup": 160, "serving": 180, "bowl": 220}),
    food("upma", "Upma", 120, 3.0, 21, 2.8, 1.8, 180, "Indian", "Breakfast", "🥣", ["rava upma", "suji upma"], {"cup": 170, "serving": 180, "bowl": 220}),
    food("pongal", "Ven pongal", 135, 4.0, 21, 4.1, 1.2, 200, "Indian", "Breakfast", "🥣", ["khara pongal", "ghee pongal"], {"cup": 190, "serving": 200, "bowl": 240}),
    food("vada", "Medu vada", 295, 11, 32, 13, 5, 55, "Indian", "Snack", "🍩", ["vada", "uddina vada", "garelu"], {"piece": 55, "serving": 110}),
    food("sambar", "Sambar", 58, 3.1, 9, 1.5, 2.6, 180, "Indian", "Curry", "🍲", ["sambhar", "lentil sambar"], {"cup": 240, "serving": 180, "bowl": 260}),
    food("coconut_chutney", "Coconut chutney", 210, 3.5, 8, 19, 5, 40, "Indian", "Side", "🥥", ["nariyal chutney"], {"tablespoon": 15, "serving": 40}),
    food("chapati", "Chapati", 265, 8.7, 49, 3.7, 7.5, 40, "Indian", "Bread", "🫓", ["roti", "phulka", "fulka"], {"piece": 40, "serving": 80}),
    food("paratha", "Plain paratha", 310, 7.5, 42, 12, 5.8, 80, "Indian", "Bread", "🫓", ["parantha", "lachha paratha"], {"piece": 80, "serving": 80}),
    food("aloo_paratha", "Aloo paratha", 240, 6.2, 37, 7.5, 4.6, 130, "Indian", "Bread", "🫓", ["potato paratha"], {"piece": 130, "serving": 130}),
    food("naan", "Naan", 310, 9, 50, 8.5, 2.5, 95, "Indian", "Bread", "🫓", ["butter naan", "plain naan"], {"piece": 95, "serving": 95}),
    food("kulcha", "Kulcha", 295, 8.2, 49, 7, 2.7, 100, "Indian", "Bread", "🫓", ["amritsari kulcha"], {"piece": 100, "serving": 100}),
    food("puri", "Puri", 330, 7.5, 43, 14, 3.8, 30, "Indian", "Bread", "🫓", ["poori"], {"piece": 30, "serving": 90}),
    food("basmati_rice", "Cooked basmati rice", 130, 2.7, 28, 0.3, 0.4, 160, "Indian", "Rice", "🍚", ["white rice", "cooked rice", "chawal"], {"cup": 160, "serving": 160, "bowl": 220}),
    food("brown_rice", "Cooked brown rice", 112, 2.6, 23, 0.9, 1.8, 160, "Global", "Rice", "🍚", ["brown chawal"], {"cup": 170, "serving": 170, "bowl": 230}),
    food("jeera_rice", "Jeera rice", 165, 3, 29, 4.1, 0.8, 180, "Indian", "Rice", "🍚", ["cumin rice"], {"cup": 170, "serving": 180, "bowl": 240}),
    food("veg_biryani", "Vegetable biryani", 155, 3.8, 24, 5.0, 2.1, 250, "Indian", "Rice", "🍛", ["veg biriyani", "vegetable biriyani"], {"cup": 190, "serving": 250, "plate": 320}),
    food("chicken_biryani", "Chicken biryani", 185, 9.5, 22, 6.3, 1.0, 300, "Indian", "Rice", "🍛", ["chicken biriyani", "hyderabadi chicken biryani"], {"cup": 200, "serving": 300, "plate": 380}),
    food("mutton_biryani", "Mutton biryani", 215, 10.5, 21, 9.2, 0.9, 300, "Indian", "Rice", "🍛", ["mutton biriyani", "goat biryani"], {"cup": 200, "serving": 300, "plate": 380}),
    food("pulao", "Vegetable pulao", 145, 3.3, 24, 4.2, 2, 220, "Indian", "Rice", "🍛", ["veg pulav", "pilaf"], {"cup": 180, "serving": 220, "plate": 300}),
    food("khichdi", "Moong dal khichdi", 105, 4.1, 18, 2.0, 2.1, 250, "Indian", "Rice", "🥣", ["khichadi", "dal khichdi"], {"cup": 220, "serving": 250, "bowl": 300}),
    food("dal_tadka", "Dal tadka", 118, 6.5, 15, 3.5, 4.3, 180, "Indian", "Dal", "🍲", ["yellow dal", "toor dal tadka"], {"cup": 220, "serving": 180, "bowl": 260}),
    food("dal_makhani", "Dal makhani", 170, 7.2, 16, 8.5, 5.5, 200, "Indian", "Dal", "🍲", ["maa ki dal"], {"cup": 220, "serving": 200, "bowl": 260}),
    food("rajma", "Rajma curry", 125, 6.8, 18, 3.0, 5.8, 200, "Indian", "Curry", "🍲", ["kidney bean curry", "rajma masala"], {"cup": 220, "serving": 200, "bowl": 260}),
    food("chole", "Chole masala", 164, 7.1, 20, 6.0, 6.5, 200, "Indian", "Curry", "🍲", ["chana masala", "chickpea curry"], {"cup": 220, "serving": 200, "bowl": 260}),
    food("palak_paneer", "Palak paneer", 160, 8.1, 6.2, 11.4, 2.4, 200, "Indian", "Curry", "🍲", ["saag paneer"], {"cup": 220, "serving": 200, "bowl": 260}),
    food("paneer_butter_masala", "Paneer butter masala", 245, 8.6, 8.2, 20, 1.8, 200, "Indian", "Curry", "🍲", ["paneer makhani", "butter paneer"], {"cup": 220, "serving": 200, "bowl": 260}),
    food("matar_paneer", "Matar paneer", 175, 8.4, 10, 11.5, 3.3, 200, "Indian", "Curry", "🍲", ["peas paneer curry"], {"cup": 220, "serving": 200, "bowl": 260}),
    food("kadai_paneer", "Kadai paneer", 210, 9.2, 9, 16.2, 2.4, 200, "Indian", "Curry", "🍲", ["karahi paneer"], {"cup": 220, "serving": 200, "bowl": 260}),
    food("butter_chicken", "Butter chicken", 210, 13.5, 5.5, 15.2, 1.0, 220, "Indian", "Curry", "🍗", ["murgh makhani"], {"cup": 220, "serving": 220, "bowl": 280}),
    food("chicken_curry", "Chicken curry", 180, 14.8, 5.2, 11.5, 1.2, 220, "Indian", "Curry", "🍗", ["murgh curry", "chicken gravy"], {"cup": 220, "serving": 220, "bowl": 280}),
    food("fish_curry", "Fish curry", 145, 15.5, 4.0, 7.5, 1.2, 220, "Indian", "Curry", "🍲", ["meen curry", "machli curry"], {"cup": 220, "serving": 220, "bowl": 280}),
    food("egg_curry", "Egg curry", 160, 10.5, 6.0, 10.0, 1.2, 200, "Indian", "Curry", "🥚", ["anda curry"], {"cup": 220, "serving": 200, "bowl": 260}),
    food("aloo_gobi", "Aloo gobi", 115, 3.0, 15, 5.0, 3.5, 180, "Indian", "Sabzi", "🥔", ["potato cauliflower curry"], {"cup": 170, "serving": 180, "bowl": 240}),
    food("bhindi_masala", "Bhindi masala", 120, 3.1, 12, 6.8, 4.0, 180, "Indian", "Sabzi", "🥘", ["okra masala"], {"cup": 160, "serving": 180, "bowl": 240}),
    food("baingan_bharta", "Baingan bharta", 105, 2.4, 12, 5.4, 4.3, 180, "Indian", "Sabzi", "🍆", ["eggplant bharta"], {"cup": 170, "serving": 180, "bowl": 240}),
    food("malai_kofta", "Malai kofta", 235, 6.2, 16, 16.5, 3.0, 220, "Indian", "Curry", "🍲", ["kofta curry"], {"cup": 220, "serving": 220, "bowl": 280}),
    food("kadhi", "Kadhi", 95, 4.2, 10, 4.0, 0.8, 200, "Indian", "Curry", "🍲", ["punjabi kadhi", "kadhi pakora"], {"cup": 220, "serving": 200, "bowl": 260}),
    food("curd", "Curd", 61, 3.5, 4.7, 3.3, 0, 100, "Indian", "Dairy", "🥛", ["dahi", "yogurt plain"], {"cup": 245, "serving": 100, "bowl": 180}),
    food("raita", "Raita", 72, 3.6, 6.3, 3.5, 0.8, 120, "Indian", "Side", "🥣", ["boondi raita", "cucumber raita"], {"cup": 220, "serving": 120, "bowl": 180}),
    food("paneer", "Paneer", 296, 18.3, 3.4, 23.8, 0, 100, "Indian", "Protein", "🧀", ["cottage cheese indian"], {"cup": 125, "serving": 100}),
    food("tofu", "Tofu", 76, 8.1, 1.9, 4.8, 0.3, 100, "Global", "Protein", "⬜", ["bean curd"], {"cup": 250, "serving": 100}),
    food("samosa", "Samosa", 308, 5.0, 32, 17, 3.5, 80, "Indian", "Snack", "🥟", ["aloo samosa"], {"piece": 80, "serving": 80}),
    food("kachori", "Kachori", 370, 7, 36, 22, 4.5, 70, "Indian", "Snack", "🥟", ["khasta kachori"], {"piece": 70, "serving": 70}),
    food("pakora", "Vegetable pakora", 315, 6.0, 29, 19, 4.2, 100, "Indian", "Snack", "🍘", ["pakoda", "bhajiya", "fritter"], {"piece": 25, "serving": 100}),
    food("pav_bhaji", "Pav bhaji", 185, 5.0, 27, 6.4, 4.0, 300, "Indian", "Street food", "🍛", ["paav bhaji"], {"serving": 300, "plate": 380}),
    food("vada_pav", "Vada pav", 290, 7.2, 39, 11, 3.8, 150, "Indian", "Street food", "🍔", ["wada pav"], {"piece": 150, "serving": 150}),
    food("pani_puri", "Pani puri", 210, 5.5, 34, 6.0, 4.5, 120, "Indian", "Street food", "🥙", ["golgappa", "puchka"], {"piece": 20, "serving": 120, "plate": 160}),
    food("bhel_puri", "Bhel puri", 160, 4.5, 28, 4.0, 3.2, 180, "Indian", "Street food", "🥣", ["bhelpuri"], {"serving": 180, "plate": 220}),
    food("sev_puri", "Sev puri", 250, 6.0, 33, 10, 3.2, 150, "Indian", "Street food", "🥙", ["sev batata puri"], {"piece": 25, "serving": 150, "plate": 180}),
    food("dhokla", "Dhokla", 160, 6.0, 25, 4.0, 3.0, 100, "Indian", "Snack", "🍰", ["khaman dhokla"], {"piece": 35, "serving": 100}),
    food("thepla", "Thepla", 285, 8.5, 43, 8.8, 6.5, 70, "Indian", "Bread", "🫓", ["methi thepla"], {"piece": 70, "serving": 140}),
    food("litti_chokha", "Litti chokha", 235, 7.5, 35, 7.0, 6.0, 250, "Indian", "Meal", "🥘", ["litti chokha"], {"piece": 90, "serving": 250, "plate": 320}),
    food("misal_pav", "Misal pav", 190, 7.0, 25, 6.8, 5.4, 300, "Indian", "Street food", "🍛", ["missal pav"], {"serving": 300, "plate": 380}),
    food("momos", "Vegetable momos", 180, 5.5, 28, 5.0, 2.8, 150, "Tibetan/Indian", "Snack", "🥟", ["veg momo", "dumplings"], {"piece": 25, "serving": 150}),
    food("gulab_jamun", "Gulab jamun", 330, 5.6, 56, 10, 0.5, 50, "Indian", "Dessert", "🍮", ["gulab jamoon"], {"piece": 50, "serving": 100}),
    food("jalebi", "Jalebi", 380, 4.0, 73, 8.0, 0.5, 50, "Indian", "Dessert", "🥨", ["jilebi"], {"piece": 25, "serving": 75}),
    food("rasgulla", "Rasgulla", 186, 4.0, 38, 2.0, 0.2, 45, "Indian", "Dessert", "🍡", ["roshogolla"], {"piece": 45, "serving": 90}),
    food("kheer", "Rice kheer", 142, 4.2, 23, 4.0, 0.3, 150, "Indian", "Dessert", "🍚", ["payasam", "rice pudding"], {"cup": 220, "serving": 150, "bowl": 220}),
    food("halwa", "Sooji halwa", 255, 4.0, 38, 10, 1.5, 100, "Indian", "Dessert", "🥣", ["sheera", "semolina halwa"], {"cup": 180, "serving": 100}),
    food("lassi", "Sweet lassi", 88, 3.0, 14, 2.2, 0, 250, "Indian", "Drink", "🥤", ["lassi sweet"], {"cup": 245, "glass": 250, "serving": 250}),
    food("masala_chai", "Masala chai", 54, 1.7, 8.5, 1.6, 0, 180, "Indian", "Drink", "☕", ["tea with milk", "chai"], {"cup": 180, "serving": 180}),
    food("filter_coffee", "Filter coffee", 58, 1.8, 8.0, 2.0, 0, 150, "Indian", "Drink", "☕", ["south indian coffee"], {"cup": 150, "serving": 150}),
    food("mango", "Mango", 60, 0.8, 15, 0.4, 1.6, 200, "Global", "Fruit", "🥭", ["aam"], {"piece": 200, "cup": 165, "serving": 200}),
    food("banana", "Banana", 89, 1.1, 23, 0.3, 2.6, 118, "Global", "Fruit", "🍌", ["kela"], {"piece": 118, "serving": 118}),
    food("apple", "Apple", 52, 0.3, 14, 0.2, 2.4, 182, "Global", "Fruit", "🍎", ["seb"], {"piece": 182, "serving": 182}),
    food("orange", "Orange", 47, 0.9, 12, 0.1, 2.4, 131, "Global", "Fruit", "🍊", ["santra"], {"piece": 131, "serving": 131}),
    food("grapes", "Grapes", 69, 0.7, 18, 0.2, 0.9, 100, "Global", "Fruit", "🍇", ["angoor"], {"cup": 151, "serving": 100}),
    food("watermelon", "Watermelon", 30, 0.6, 8, 0.2, 0.4, 280, "Global", "Fruit", "🍉", ["tarbooj"], {"cup": 152, "serving": 280}),
    food("papaya", "Papaya", 43, 0.5, 11, 0.3, 1.7, 145, "Global", "Fruit", "🍈", ["papita"], {"cup": 145, "serving": 145}),
    food("guava", "Guava", 68, 2.6, 14, 1.0, 5.4, 100, "Global", "Fruit", "🍈", ["amrood"], {"piece": 55, "serving": 100}),
    food("milk", "Whole milk", 61, 3.2, 4.8, 3.3, 0, 244, "Global", "Dairy", "🥛", ["full cream milk"], {"cup": 244, "glass": 250, "serving": 244}),
    food("oats", "Cooked oats", 71, 2.5, 12, 1.5, 1.7, 240, "Global", "Breakfast", "🥣", ["oatmeal", "porridge"], {"cup": 240, "serving": 240, "bowl": 280}),
    food("cornflakes", "Cornflakes", 357, 7.5, 84, 0.4, 3.3, 30, "Global", "Breakfast", "🥣", ["corn flakes"], {"cup": 28, "serving": 30}),
    food("boiled_egg", "Boiled egg", 155, 13, 1.1, 11, 0, 50, "Global", "Protein", "🥚", ["hard boiled egg", "egg"], {"piece": 50, "serving": 50}),
    food("omelette", "Omelette", 154, 10.6, 1.6, 12, 0, 100, "Global", "Breakfast", "🍳", ["omelet"], {"piece": 100, "serving": 100}),
    food("grilled_chicken", "Grilled chicken breast", 165, 31, 0, 3.6, 0, 120, "Global", "Protein", "🍗", ["chicken breast"], {"piece": 120, "serving": 120}),
    food("fried_chicken", "Fried chicken", 260, 22, 8, 16, 0.5, 120, "Global", "Protein", "🍗", ["crispy chicken"], {"piece": 120, "serving": 120}),
    food("salmon", "Salmon", 208, 20, 0, 13, 0, 120, "Global", "Protein", "🐟", ["grilled salmon"], {"piece": 120, "serving": 120}),
    food("tuna", "Tuna", 132, 28, 0, 1.3, 0, 100, "Global", "Protein", "🐟", ["canned tuna"], {"serving": 100, "cup": 154}),
    food("lentil_soup", "Lentil soup", 70, 4.8, 10, 1.5, 3.8, 240, "Global", "Soup", "🍲", ["dal soup"], {"cup": 240, "serving": 240, "bowl": 300}),
    food("green_salad", "Green salad", 25, 1.5, 4.2, 0.5, 2.1, 120, "Global", "Salad", "🥗", ["mixed salad"], {"cup": 85, "serving": 120, "bowl": 180}),
    food("caesar_salad", "Caesar salad", 180, 7, 8, 14, 2, 200, "Global", "Salad", "🥗", ["chicken caesar salad"], {"serving": 200, "bowl": 260}),
    food("pizza", "Cheese pizza", 266, 11, 33, 10, 2.3, 107, "Italian", "Fast food", "🍕", ["pizza slice", "margherita pizza"], {"slice": 107, "piece": 107, "serving": 107}),
    food("burger", "Cheeseburger", 295, 15, 30, 14, 1.5, 150, "American", "Fast food", "🍔", ["burger"], {"piece": 150, "serving": 150}),
    food("french_fries", "French fries", 312, 3.4, 41, 15, 3.8, 117, "Global", "Fast food", "🍟", ["fries", "chips"], {"serving": 117, "cup": 120}),
    food("pasta", "Pasta with tomato sauce", 131, 5, 25, 1.5, 2.2, 250, "Italian", "Pasta", "🍝", ["spaghetti marinara"], {"cup": 248, "serving": 250, "plate": 320}),
    food("alfredo_pasta", "Alfredo pasta", 220, 7, 23, 11, 1.5, 250, "Italian", "Pasta", "🍝", ["white sauce pasta"], {"cup": 248, "serving": 250, "plate": 320}),
    food("lasagna", "Lasagna", 163, 9, 17, 7, 1.5, 250, "Italian", "Pasta", "🍝", ["meat lasagna"], {"serving": 250, "piece": 250}),
    food("sushi", "Sushi roll", 145, 5.5, 28, 1.5, 1.0, 150, "Japanese", "Rice", "🍣", ["maki", "california roll"], {"piece": 25, "serving": 150}),
    food("ramen", "Ramen", 90, 4, 12, 3.2, 1.0, 500, "Japanese", "Noodles", "🍜", ["ramen soup"], {"bowl": 500, "serving": 500}),
    food("fried_rice", "Fried rice", 165, 4.5, 26, 5, 1.2, 250, "Chinese", "Rice", "🍚", ["chinese fried rice"], {"cup": 180, "serving": 250, "plate": 320}),
    food("noodles", "Hakka noodles", 190, 5, 29, 6, 2.2, 250, "Indo-Chinese", "Noodles", "🍜", ["chow mein", "veg noodles"], {"cup": 180, "serving": 250, "plate": 320}),
    food("manchurian", "Vegetable manchurian", 205, 5.2, 24, 10, 3.0, 220, "Indo-Chinese", "Curry", "🥘", ["gobi manchurian"], {"serving": 220, "bowl": 260}),
    food("spring_roll", "Spring roll", 250, 6, 32, 10, 3, 100, "Chinese", "Snack", "🥢", ["veg spring roll"], {"piece": 60, "serving": 120}),
    food("taco", "Taco", 226, 10, 20, 12, 3, 100, "Mexican", "Fast food", "🌮", ["beef taco"], {"piece": 100, "serving": 100}),
    food("burrito", "Burrito", 206, 8, 28, 7, 4, 250, "Mexican", "Meal", "🌯", ["bean burrito"], {"piece": 250, "serving": 250}),
    food("quesadilla", "Quesadilla", 293, 15, 24, 16, 2, 160, "Mexican", "Fast food", "🫓", ["cheese quesadilla"], {"piece": 160, "serving": 160}),
    food("falafel", "Falafel", 333, 13, 32, 18, 5, 100, "Middle Eastern", "Snack", "🧆", ["falafel balls"], {"piece": 17, "serving": 100}),
    food("hummus", "Hummus", 166, 7.9, 14, 9.6, 6, 100, "Middle Eastern", "Dip", "🥣", ["houmous"], {"tablespoon": 15, "serving": 100}),
    food("pita_bread", "Pita bread", 275, 9, 56, 1.2, 2.2, 60, "Middle Eastern", "Bread", "🫓", ["pita"], {"piece": 60, "serving": 60}),
    food("shawarma", "Chicken shawarma", 220, 12, 22, 9, 2, 250, "Middle Eastern", "Meal", "🌯", ["shawarma roll"], {"piece": 250, "serving": 250}),
    food("croissant", "Croissant", 406, 8, 45, 21, 2.6, 57, "French", "Bakery", "🥐", ["butter croissant"], {"piece": 57, "serving": 57}),
    food("bagel", "Bagel", 250, 10, 49, 1.5, 2.3, 100, "Global", "Bakery", "🥯", ["plain bagel"], {"piece": 100, "serving": 100}),
    food("bread", "White bread", 265, 9, 49, 3.2, 2.7, 25, "Global", "Bread", "🍞", ["bread slice"], {"slice": 25, "piece": 25, "serving": 50}),
    food("peanut_butter", "Peanut butter", 588, 25, 20, 50, 6, 32, "Global", "Spread", "🥜", ["groundnut butter"], {"tablespoon": 16, "serving": 32}),
    food("jam", "Fruit jam", 278, 0.4, 69, 0.1, 1.1, 20, "Global", "Spread", "🍓", ["jelly"], {"tablespoon": 20, "serving": 20}),
    food("ice_cream", "Vanilla ice cream", 207, 3.5, 24, 11, 0.7, 100, "Global", "Dessert", "🍨", ["icecream"], {"cup": 132, "serving": 100}),
    food("chocolate", "Milk chocolate", 535, 7.7, 59, 30, 3.4, 40, "Global", "Dessert", "🍫", ["chocolate bar"], {"piece": 10, "serving": 40}),
    food("cake", "Chocolate cake", 371, 5, 53, 16, 2, 100, "Global", "Dessert", "🍰", ["cake slice"], {"slice": 100, "piece": 100, "serving": 100}),
    food("donut", "Donut", 452, 4.9, 51, 25, 1.9, 60, "Global", "Dessert", "🍩", ["doughnut"], {"piece": 60, "serving": 60}),
    food("cola", "Cola", 42, 0, 10.6, 0, 0, 330, "Global", "Drink", "🥤", ["soft drink", "coke"], {"cup": 240, "glass": 250, "serving": 330}),
    food("orange_juice", "Orange juice", 45, 0.7, 10.4, 0.2, 0.2, 240, "Global", "Drink", "🧃", ["juice"], {"cup": 240, "glass": 250, "serving": 240}),
    food("beer", "Beer", 43, 0.5, 3.6, 0, 0, 330, "Global", "Drink", "🍺", ["lager"], {"glass": 330, "serving": 330}),
    food("coffee_black", "Black coffee", 1, 0.1, 0, 0, 0, 240, "Global", "Drink", "☕", ["coffee"], {"cup": 240, "serving": 240}),
    food("avocado", "Avocado", 160, 2, 9, 15, 7, 150, "Global", "Fruit", "🥑", ["avocado pear"], {"piece": 150, "serving": 150}),
    food("broccoli", "Broccoli", 35, 2.4, 7.2, 0.4, 3.3, 100, "Global", "Vegetable", "🥦", ["steamed broccoli"], {"cup": 156, "serving": 100}),
    food("potato_boiled", "Boiled potato", 87, 1.9, 20, 0.1, 1.8, 150, "Global", "Vegetable", "🥔", ["potato"], {"piece": 150, "serving": 150}),
    food("sweet_potato", "Sweet potato", 86, 1.6, 20, 0.1, 3, 130, "Global", "Vegetable", "🍠", ["shakarkandi"], {"piece": 130, "serving": 130}),
    food("corn", "Sweet corn", 96, 3.4, 21, 1.5, 2.4, 100, "Global", "Vegetable", "🌽", ["corn kernels"], {"cup": 164, "serving": 100}),
    food("almonds", "Almonds", 579, 21, 22, 50, 12.5, 28, "Global", "Nuts", "🌰", ["badam"], {"piece": 1.2, "serving": 28}),
    food("cashews", "Cashews", 553, 18, 30, 44, 3.3, 28, "Global", "Nuts", "🌰", ["kaju"], {"piece": 1.6, "serving": 28}),
    food("walnuts", "Walnuts", 654, 15, 14, 65, 6.7, 28, "Global", "Nuts", "🌰", ["akhrot"], {"piece": 2.0, "serving": 28}),
    food("dates", "Dates", 282, 2.5, 75, 0.4, 8, 24, "Global", "Dry fruit", "🌴", ["khajoor"], {"piece": 8, "serving": 24}),
]


UNIT_LABELS = {
    "g": "grams",
    "kg": "kilograms",
    "ml": "milliliters",
    "oz": "ounces",
    "lb": "pounds",
    "cup": "cups",
    "tablespoon": "tablespoons",
    "teaspoon": "teaspoons",
    "piece": "pieces",
    "slice": "slices",
    "serving": "servings",
    "bowl": "bowls",
    "plate": "plates",
    "glass": "glasses",
}


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def searchable_terms(item: Food) -> list[str]:
    return [item["name"], *item["aliases"], item["cuisine"], item["category"]]


def score_food(query: str, item: Food) -> float:
    normalized_query = normalize(query)
    if not normalized_query:
        return 0.0

    best = 0.0
    query_tokens = set(normalized_query.split())
    for term in searchable_terms(item):
        normalized_term = normalize(term)
        if not normalized_term:
            continue

        ratio = SequenceMatcher(None, normalized_query, normalized_term).ratio()
        term_tokens = set(normalized_term.split())
        overlap = len(query_tokens & term_tokens) / max(len(query_tokens | term_tokens), 1)
        substring_bonus = 0.22 if normalized_query in normalized_term or normalized_term in normalized_query else 0.0
        best = max(best, ratio * 0.6 + overlap * 0.35 + substring_bonus)

    return min(best, 1.0)


def public_food(item: Food, confidence: float | None = None) -> dict:
    data = {
        "id": item["id"],
        "name": item["name"],
        "aliases": item["aliases"],
        "cuisine": item["cuisine"],
        "category": item["category"],
        "emoji": item["emoji"],
        "servingGrams": item["serving_g"],
        "caloriesPer100g": item["kcal_per_100g"],
        "proteinPer100g": item["protein_per_100g"],
        "carbsPer100g": item["carbs_per_100g"],
        "fatPer100g": item["fat_per_100g"],
        "fiberPer100g": item["fiber_per_100g"],
        "source": item.get("source", "local_estimate"),
    }
    if confidence is not None:
        data["confidence"] = round(confidence, 3)
    return data


def search_foods(query: str, limit: int = 8) -> list[dict]:
    matches = []
    for item in FOODS:
        score = score_food(query, item)
        if score >= 0.18:
            matches.append((score, item))

    matches.sort(key=lambda match: (match[0], -len(match[1]["name"])), reverse=True)
    return [public_food(item, score) for score, item in matches[:limit]]


def get_food_by_id(food_id: str) -> Food | None:
    return next((item for item in FOODS if item["id"] == food_id), None)


def best_match(query: str) -> tuple[Food | None, float]:
    matches = search_foods(query, limit=1)
    if not matches:
        return None, 0.0
    item = get_food_by_id(matches[0]["id"])
    return item, float(matches[0]["confidence"])


def grams_for_quantity(item: Food, quantity: float, unit: str) -> tuple[float, str]:
    safe_quantity = max(float(quantity), 0)
    unit = unit or "g"
    measures = item.get("measures", {})
    note = ""

    if unit == "g":
        grams = safe_quantity
    elif unit == "kg":
        grams = safe_quantity * 1000
    elif unit == "ml":
        grams = safe_quantity
        note = "Using 1 ml ≈ 1 g unless the food has a specific density."
    elif unit == "oz":
        grams = safe_quantity * 28.3495
    elif unit == "lb":
        grams = safe_quantity * 453.592
    elif unit == "tablespoon":
        grams = safe_quantity * measures.get("tablespoon", 15)
        note = "Spoon measures are approximate and vary by ingredient."
    elif unit == "teaspoon":
        grams = safe_quantity * measures.get("teaspoon", 5)
        note = "Spoon measures are approximate and vary by ingredient."
    elif unit in measures:
        grams = safe_quantity * measures[unit]
    elif unit == "cup":
        grams = safe_quantity * 240
        note = "Cup conversion uses a generic 240 g estimate for this item."
    elif unit == "piece":
        grams = safe_quantity * item["serving_g"]
        note = "Piece size uses this food's default serving estimate."
    elif unit == "slice":
        grams = safe_quantity * measures.get("slice", item["serving_g"])
        note = "Slice size uses this food's default serving estimate."
    elif unit == "bowl":
        grams = safe_quantity * measures.get("bowl", item["serving_g"] * 1.25)
        note = "Bowl size is an estimate based on common serving weight."
    elif unit == "plate":
        grams = safe_quantity * measures.get("plate", item["serving_g"] * 1.5)
        note = "Plate size is an estimate based on common serving weight."
    elif unit == "glass":
        grams = safe_quantity * measures.get("glass", 250)
    else:
        grams = safe_quantity * item["serving_g"]
        note = "Unknown unit; using default serving size."

    return grams, note


def nutrition_for(item: Food, grams: float) -> dict:
    multiplier = grams / 100
    calories = item["kcal_per_100g"] * multiplier
    macros = {
        "protein": item["protein_per_100g"] * multiplier,
        "carbs": item["carbs_per_100g"] * multiplier,
        "fat": item["fat_per_100g"] * multiplier,
        "fiber": item["fiber_per_100g"] * multiplier,
    }
    return {
        "calories": round(calories),
        "grams": round(grams, 1),
        "macros": {key: round(value, 1) for key, value in macros.items()},
        "caloriesPer100g": item["kcal_per_100g"],
    }


def external_food_to_local(payload: dict) -> Food:
    return {
        "id": payload.get("id", "external"),
        "name": payload["name"],
        "aliases": [],
        "cuisine": "Global",
        "category": payload.get("category", "Packaged food"),
        "emoji": "🍽️",
        "serving_g": payload.get("serving_g") or 100,
        "kcal_per_100g": payload["kcal_per_100g"],
        "protein_per_100g": payload.get("protein_per_100g", 0),
        "carbs_per_100g": payload.get("carbs_per_100g", 0),
        "fat_per_100g": payload.get("fat_per_100g", 0),
        "fiber_per_100g": payload.get("fiber_per_100g", 0),
        "measures": {"serving": payload.get("serving_g") or 100},
        "source": payload.get("source", "open_food_facts"),
        "image_url": payload.get("image_url"),
        "brand": payload.get("brand"),
    }


def round_half_up(value: float) -> int:
    return int(math.floor(value + 0.5))
