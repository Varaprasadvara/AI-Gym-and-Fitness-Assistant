import random

SAFETY_NOTE = "If you feel chest pain, dizziness, faintness, or sharp pain, stop training and get medical help."


def get_chatbot_response(message: str) -> str:
    """
    Enhanced AI Chatbot for Virtual Gym Buddy.
    In a real application, this would pass the user's message to an LLM like OpenAI or Google Gemini
    along with a system prompt detailing the bot's persona.
    """
    msg = message.strip().lower()

    # Safety first - medical emergencies
    if any(term in msg for term in ["chest pain", "dizzy", "faint", "sharp pain", "injury", "injured", "emergency"]):
        return f"⚠️ This sounds serious. {SAFETY_NOTE} Please seek immediate medical attention if you're experiencing these symptoms."
    
    # Pain and discomfort
    if any(term in msg for term in ["pain", "hurts", "sore", "ache", "cramp"]):
        responses = [
            "Pain during exercise isn't normal. Stop what you're doing and assess. Is it sharp or dull? Where exactly?",
            "Listen to your body. If something hurts, it's trying to tell you something. Rest and recover.",
            "Muscle soreness is different from injury pain. Soreness improves with movement, injury pain gets worse."
        ]
        return random.choice(responses)
        
    # Tiredness and fatigue
    if "tired" in msg or "exhausted" in msg or "fatigue" in msg:
        responses = [
            "Fatigue is your body's signal to rest. Take a recovery day - your muscles grow when you sleep, not when you train.",
            "Quality over quantity. A short, focused session is better than a long, exhausted one.",
            "Hydration and nutrition first. Sometimes 'tired' is just 'dehydrated' or 'hungry'."
        ]
        return random.choice(responses)
        
    # Motivation and mental barriers
    elif any(term in msg for term in ["motivation", "lazy", "skip", "procrastinate", "unmotivated"]):
        responses = [
            "Start with the smallest step: put on your workout clothes. Momentum builds from there.",
            "Remember why you started. What's one goal that excites you right now?",
            "Every expert was once a beginner. Every champion was once afraid to start. You've got this!"
        ]
        return random.choice(responses)
        
    # Diet and nutrition
    elif any(term in msg for term in ["lose weight", "weight loss", "lose", "weight", "diet", "eat", "food", "protein", "calorie", "calories", "nutrition"]):
        if "gain muscle" in msg or ("gain" in msg and "muscle" in msg):
            return "💪 For muscle gain: Focus on protein (1.6-2.2g per kg bodyweight), progressive overload in training, and a slight calorie surplus. The Dietician tab can calculate your exact needs."
        if "lose weight" in msg or "weight loss" in msg or ("lose" in msg and "weight" in msg):
            return "⚖️ For fat loss: Create a moderate calorie deficit (300-500 kcal/day), prioritize protein and vegetables, stay hydrated, and be patient. Sustainable changes last."
        if "protein" in msg:
            return "🥩 Protein sources: Chicken, turkey, fish, eggs, dairy, legumes, tofu, nuts. Aim for 20-40g per meal for muscle maintenance and growth."
        return "🍎 Build meals around whole foods: vegetables, lean proteins, whole grains, healthy fats. The AI Dietician can create a personalized plan based on your stats."
        
    # Workout planning and exercise
    elif any(term in msg for term in ["workout", "routine", "exercise", "training", "lift", "cardio", "strength"]):
        if "beginner" in msg or "new" in msg or "start" in msg:
            return "🏃‍♂️ As a beginner: Start with 2-3 full-body sessions per week. Focus on learning proper form with bodyweight exercises. Consistency beats intensity."
        if "cardio" in msg or "running" in msg or "bike" in msg:
            return "❤️ Cardio benefits: Heart health, endurance, calorie burn. Mix steady-state (brisk walking) with intervals. Find activities you enjoy!"
        if "strength" in msg or "weights" in msg or "lift" in msg:
            return "🏋️ Strength training: Builds muscle, boosts metabolism, strengthens bones. Start with compound movements like squats, push-ups, rows."
        return "💪 A balanced routine includes: Warm-up (5-10 min), main workout (20-45 min), cool-down (5-10 min). Rest 1-2 minutes between sets. Quality form prevents injury."
        
    # Recovery and rest
    elif any(term in msg for term in ["rest", "recovery", "sleep", "overtraining"]):
        return "😴 Recovery is when gains happen! Aim for 7-9 hours sleep, eat enough protein, stay hydrated, and include rest days. Your body adapts during recovery, not during workouts."
        
    # Hydration
    elif any(term in msg for term in ["water", "hydrate", "hydration", "thirsty", "drink"]):
        return "💧 Hydration goal: 30-40ml water per kg bodyweight daily, more on training days. Signs of dehydration: dark urine, fatigue, headache. Keep a water bottle handy!"
        
    # Progress and tracking
    elif any(term in msg for term in ["progress", "results", "plateau", "stuck", "gains"]):
        return "📈 Progress takes time. Track consistency over perfection. Take progress photos, measurements, and strength numbers weekly. Small daily improvements compound into big results."
        
    # General encouragement and conversation
    else:
        responses = [
            "I'm here to support your fitness journey! What's your main goal right now - building muscle, losing fat, improving health, or something else?",
            "Every step counts. Whether it's a walk around the block or a tough workout, you're building habits that will serve you for life.",
            "What's one thing you'd like to improve in your fitness routine? I can give specific advice.",
            "Remember: Progress over perfection. Some movement is always better than no movement.",
            "How are you feeling about your training this week? Any wins to celebrate or challenges to overcome?"
        ]
        return random.choice(responses)
