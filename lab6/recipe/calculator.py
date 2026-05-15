# recipe_package/calculator.py
from .ingredients import INGREDIENTS

RECIPES = {
    "Вок": {
        "рис": 150,
        "куриное филе": 100,
        "помидор": 50,
        "огурец": 50,
        "кетчуп": 30
    },
    "Бургер": {
        "булочка": 1,      # штука, пересчитается в граммы
        "говядина": 120,
        "сыр": 30,
        "салат": 20,
        "помидор": 30,
        "кетчуп": 20
    },
    "Пицца": {
        "тесто для пиццы": 200,
        "сыр": 100,
        "помидор": 80,
        "куриное филе": 70
    }
}

# Вес одной единицы, если количество указано в штуках
UNIT_WEIGHT = {
    "булочка": 60  # 1 булочка ≈ 60 г
}

def calculate(recipe_name, custom_amounts=None):
    """
    Возвращает словарь с общей калорийностью, БЖУ и стоимостью.
    custom_amounts: dict, переопределяет стандартные веса (граммы).
    """
    if recipe_name not in RECIPES:
        raise ValueError(f"Рецепт '{recipe_name}' не найден")

    base_recipe = RECIPES[recipe_name]
    if custom_amounts is None:
        custom_amounts = {}

    total_kcal = 0.0
    total_protein = 0.0
    total_fat = 0.0
    total_carbs = 0.0
    total_price = 0.0
    breakdown = {}  # ингредиент -> (грамм, ккал, цена)

    for ing_name, base_amount in base_recipe.items():
        # Получаем количество из custom_amounts, иначе используем базовое
        amount = custom_amounts.get(ing_name, base_amount)

        # Если ингредиент может быть в штуках и значение — не число (т.е. оставили как есть)
        if ing_name in UNIT_WEIGHT and not isinstance(amount, (int, float)):
            amount = UNIT_WEIGHT[ing_name]
        elif ing_name in UNIT_WEIGHT and isinstance(amount, (int, float)):
            # Если передали число, считаем, что это граммы
            pass

        ing_data = INGREDIENTS.get(ing_name)
        if not ing_data:
            print(f"Ингредиент {ing_name} отсутствует в базе")
            continue

        factor = amount / 100.0
        kcal = ing_data["kcal"] * factor
        protein = ing_data["protein"] * factor
        fat = ing_data["fat"] * factor
        carbs = ing_data["carbs"] * factor
        price = ing_data["price"] * factor

        total_kcal += kcal
        total_protein += protein
        total_fat += fat
        total_carbs += carbs
        total_price += price
        breakdown[ing_name] = (amount, kcal, price)

    result = {
        "recipe": recipe_name,
        "kcal": round(total_kcal, 1),
        "protein": round(total_protein, 1),
        "fat": round(total_fat, 1),
        "carbs": round(total_carbs, 1),
        "price": round(total_price, 2),
        "breakdown": breakdown
    }
    return result