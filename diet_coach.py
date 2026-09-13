GOAL_CONFIG = {
    "lose_weight": {
        "calorie_delta": -450,
        "summary": "High-protein meals with controlled portions to support fat loss while preserving lean muscle.",
        "grocery_list": ["Chicken breast", "Greek yogurt", "Eggs", "Spinach", "Broccoli", "Brown rice", "Lentils"],
        "meals": [
            "Breakfast: Greek yogurt with oats and berries",
            "Lunch: Grilled chicken, brown rice, and vegetables",
            "Dinner: Lentil soup with eggs or paneer and salad",
            "Snack: Fruit with unsweetened yogurt"
        ],
    },
    "gain_muscle": {
        "calorie_delta": 350,
        "summary": "Protein-forward meals with enough carbohydrates to fuel progressive strength training.",
        "grocery_list": ["Lean beef", "Paneer", "Oats", "Sweet potatoes", "Whole milk", "Peanut butter", "Bananas"],
        "meals": [
            "Breakfast: Oats with milk, banana, and peanut butter",
            "Lunch: Lean protein with rice or sweet potatoes",
            "Dinner: Paneer or lean meat with vegetables and roti",
            "Snack: Milk, nuts, or a protein smoothie"
        ],
    },
    "maintain": {
        "calorie_delta": 0,
        "summary": "Balanced meals that keep calories steady while supporting daily training and recovery.",
        "grocery_list": ["Salmon", "Quinoa", "Mixed vegetables", "Almonds", "Eggs", "Apples", "Curd"],
        "meals": [
            "Breakfast: Eggs with fruit and whole-grain toast",
            "Lunch: Rice or quinoa bowl with protein and vegetables",
            "Dinner: Fish, paneer, or dal with vegetables",
            "Snack: Nuts, curd, or fresh fruit"
        ],
    },
}


def _bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "healthy"
    if bmi < 30:
        return "overweight"
    return "obese"


def generate_diet_plan(age: int, weight_kg: float, height_cm: float, goal: str):
    """
    AI Dietician module.
    Calculates BMI, estimates calories, and generates practical meal guidance.
    In a real app, this would use a generative model (like LLama or Gemini) to create dynamic meals.
    """
    if height_cm <= 0:
        raise ValueError("Height must be greater than zero.")

    height_m = height_cm / 100
    bmi = weight_kg / (height_m * height_m)

    config = GOAL_CONFIG.get(goal, GOAL_CONFIG["maintain"])
    # Mifflin-St Jeor estimate using a neutral midpoint when sex is not collected.
    base_bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 78
    maintenance_calories = int(round(base_bmr * 1.45 / 25) * 25)
    calories = max(1200, int(round((maintenance_calories + config["calorie_delta"]) / 25) * 25))

    protein_g = int(round(weight_kg * (2.0 if goal == "gain_muscle" else 1.6)))
    fat_g = int(round((calories * 0.25) / 9))
    carb_g = max(0, int(round((calories - (protein_g * 4) - (fat_g * 9)) / 4)))

    return {
        "bmi": round(bmi, 1),
        "bmi_category": _bmi_category(bmi),
        "recommended_calories": calories,
        "maintenance_calories": maintenance_calories,
        "macros": {
            "protein_g": protein_g,
            "carbs_g": carb_g,
            "fat_g": fat_g,
        },
        "plan_summary": config["summary"],
        "grocery_list": config["grocery_list"],
        "sample_meals": config["meals"],
        "hydration_tip": "Aim for 30-40 ml of water per kg of body weight, more if training hard or sweating heavily."
    }
