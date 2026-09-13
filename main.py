# pyrefly: ignore [missing-import]
from fastapi import FastAPI, UploadFile, File
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from fastapi.responses import FileResponse, JSONResponse
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles
# pyrefly: ignore [missing-import]
import uvicorn
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
import sys
import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))

# Add the current directory to the path so we can import modules
sys.path.append(BASE_DIR)

from ai_modules.pose_estimation import analyze_pose_image
from ai_modules.diet_coach import generate_diet_plan
from ai_modules.chatbot import get_chatbot_response

app = FastAPI(title="AI Gym & Fitness Assistant API")

# Configure CORS for Chrome and all browsers - development friendly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    max_age=3600,
)

if os.path.isdir(os.path.join(FRONTEND_DIR, "css")):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")

if os.path.isdir(os.path.join(FRONTEND_DIR, "js")):
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")

@app.get("/")
def read_root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to the AI Gym & Fitness Assistant API"}

@app.get("/api")
def read_api_root():
    return {"message": "Welcome to the AI Gym & Fitness Assistant API"}

@app.post("/api/trainer/analyze-pose")
async def analyze_pose(file: UploadFile = File(...)):
    """
    Endpoint to receive an image frame from the frontend,
    process it using MediaPipe, and return posture feedback.
    """
    try:
        if not file or not file.filename:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "No file provided"}
            )
        
        contents = await file.read()
        if not contents:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Empty file received"}
            )
        
        # In a real app, we'd process the byte stream.
        # For now, we'll pass it to our module.
        result = analyze_pose_image(contents)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Processing error: {str(e)}"}
        )

class DietRequest(BaseModel):
    age: int = Field(..., ge=10, le=120)
    weight_kg: float = Field(..., ge=30, le=300)
    height_cm: float = Field(..., ge=100, le=250)
    goal: str = Field(..., pattern="^(lose_weight|maintain|gain_muscle)$")

@app.post("/api/dietician/recommend")
async def recommend_diet(request: DietRequest):
    """
    Endpoint for diet recommendations based on basic BMI calculations.
    """
    return generate_diet_plan(request.age, request.weight_kg, request.height_cm, request.goal)

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)

@app.post("/api/chatbot/chat")
async def chat_with_bot(chat: ChatMessage):
    """
    Endpoint to interact with the Virtual Gym Buddy AI.
    """
    response_text = get_chatbot_response(chat.message)
    return {"reply": response_text}

class UserProfileUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    age: int = Field(..., ge=10, le=120)
    weight_kg: float = Field(..., ge=30, le=300)
    height_cm: float = Field(..., ge=100, le=250)
    fitness_level: str = Field(...)
    goals: list = Field(default=[])

@app.post("/api/users/{user_id}")
async def update_user_profile(user_id: str, profile: UserProfileUpdate):
    """
    Updates user profile with new details from form.
    """
    if user_id not in user_profiles:
        user_profiles[user_id] = {
            "name": profile.name,
            "email": profile.email,
            "avatar": f"https://ui-avatars.com/api/?name={profile.name.replace(' ', '+')}&background=0D8ABC&color=fff",
            "joined_date": "2024-01-01",
            "fitness_level": profile.fitness_level,
            "goals": profile.goals,
            "dashboard": {
                "weekly_performance_score": 85,
                "total_calories": 0,
                "hours_trained": 0,
                "average_heart_rate": 100,
                "workouts_this_week": 0,
                "personal_best": "Just started!"
            },
            "habit_prediction": "Start your fitness journey today!",
            "iot_status": [
                {"label": "Treadmill 1", "status": "Offline"},
                {"label": "Smart Dumbbells", "status": "Offline"},
                {"label": "Heart Rate Monitor", "status": "Offline"}
            ],
            "recent_workouts": []
        }
    else:
        user_profiles[user_id]["name"] = profile.name
        user_profiles[user_id]["email"] = profile.email
        user_profiles[user_id]["fitness_level"] = profile.fitness_level
        user_profiles[user_id]["goals"] = profile.goals
        user_profiles[user_id]["avatar"] = f"https://ui-avatars.com/api/?name={profile.name.replace(' ', '+')}&background=0D8ABC&color=fff"
    
    return {
        "status": "success",
        "message": "Profile updated successfully",
        "user": user_profiles[user_id]
    }

@app.get("/api/users/{user_id}")
async def get_user_profile(user_id: str):
    """
    Get user profile by ID.
    """
    if user_id in user_profiles:
        return user_profiles[user_id]
    else:
        return {"error": "User not found"}

# --- IoT Integration ---
# Simple in-memory storage for demonstration
iot_data_store = []

class IoTData(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=80)
    sensor_type: str = Field(..., min_length=1, max_length=40)
    heart_rate_bpm: int = Field(..., ge=35, le=220)
    speed_kmh: float = Field(..., ge=0, le=30)
    incline_percent: int = Field(..., ge=0, le=40)
    timestamp: float = Field(..., gt=0)

@app.post("/api/iot/receive-data")
async def receive_iot_data(data: IoTData):
    """
    Receives data from mock IoT devices.
    """
    iot_data_store.append(data.model_dump())
    # Keep only the last 50 entries to prevent memory leak
    if len(iot_data_store) > 50:
        iot_data_store.pop(0)
    return {"status": "success", "message": "Data recorded"}

# Simple mock dashboard data keyed by user ID
user_profiles = {
    "athlete": {
        "name": "Athlete",
        "email": "athlete@fitai.com",
        "avatar": "https://ui-avatars.com/api/?name=Athlete&background=0D8ABC&color=fff",
        "joined_date": "2024-01-15",
        "fitness_level": "Intermediate",
        "goals": ["Build Muscle", "Improve Endurance"],
        "dashboard": {
            "weekly_performance_score": 92,
            "total_calories": 1240,
            "hours_trained": 4.3,
            "average_heart_rate": 110,
            "workouts_this_week": 5,
            "personal_best": "Deadlift: 200kg"
        },
        "habit_prediction": "You have a 65% chance of skipping tomorrow's leg day based on your past patterns.",
        "iot_status": [
            {"label": "Treadmill 1", "status": "Online"},
            {"label": "Smart Dumbbells", "status": "Synced"},
            {"label": "Heart Rate Monitor", "status": "Offline"}
        ],
        "recent_workouts": [
            {"date": "2024-05-09", "exercise": "Bench Press", "reps": 8, "weight": "90kg"},
            {"date": "2024-05-08", "exercise": "Squats", "reps": 10, "weight": "120kg"},
            {"date": "2024-05-07", "exercise": "Deadlifts", "reps": 5, "weight": "160kg"}
        ]
    },
    "fitness_enthusiast": {
        "name": "Fitness Enthusiast",
        "email": "enthusiast@fitai.com",
        "avatar": "https://ui-avatars.com/api/?name=Fitness+Enthusiast&background=EC4899&color=fff",
        "joined_date": "2023-06-20",
        "fitness_level": "Advanced",
        "goals": ["Lose Weight", "Increase Flexibility"],
        "dashboard": {
            "weekly_performance_score": 88,
            "total_calories": 2100,
            "hours_trained": 6.5,
            "average_heart_rate": 125,
            "workouts_this_week": 6,
            "personal_best": "10K Run: 42 min"
        },
        "habit_prediction": "Great consistency! 92% chance you'll complete tomorrow's cardio session.",
        "iot_status": [
            {"label": "Treadmill 2", "status": "Online"},
            {"label": "Bike Machine", "status": "Online"},
            {"label": "Heart Rate Monitor", "status": "Synced"}
        ],
        "recent_workouts": [
            {"date": "2024-05-09", "exercise": "Morning Run", "reps": 10, "weight": "10km"},
            {"date": "2024-05-08", "exercise": "Cycling", "reps": 45, "weight": "minutes"},
            {"date": "2024-05-07", "exercise": "Yoga", "reps": 60, "weight": "minutes"}
        ]
    },
    "beginner": {
        "name": "Beginner",
        "email": "beginner@fitai.com",
        "avatar": "https://ui-avatars.com/api/?name=Beginner&background=10B981&color=fff",
        "joined_date": "2024-03-01",
        "fitness_level": "Beginner",
        "goals": ["Get Fit", "Build Confidence"],
        "dashboard": {
            "weekly_performance_score": 75,
            "total_calories": 650,
            "hours_trained": 2.5,
            "average_heart_rate": 95,
            "workouts_this_week": 3,
            "personal_best": "5K Walk: 28 min"
        },
        "habit_prediction": "Keep it up! You're building a strong habit. Only 30% chance of skipping.",
        "iot_status": [
            {"label": "Treadmill 1", "status": "Online"},
            {"label": "Smart Dumbbells", "status": "Offline"},
            {"label": "Heart Rate Monitor", "status": "Synced"}
        ],
        "recent_workouts": [
            {"date": "2024-05-09", "exercise": "Walking", "reps": 30, "weight": "minutes"},
            {"date": "2024-05-07", "exercise": "Light Strength", "reps": 20, "weight": "minutes"},
            {"date": "2024-05-05", "exercise": "Stretching", "reps": 15, "weight": "minutes"}
        ]
    }
}

@app.get("/api/users")
async def get_all_users():
    """
    Returns list of available users for selection.
    """
    users = []
    for user_id, profile in user_profiles.items():
        users.append({
            "id": user_id,
            "name": profile["name"],
            "avatar": profile["avatar"],
            "fitness_level": profile["fitness_level"]
        })
    return {"users": users}

@app.get("/api/analytics/summary")
async def get_analytics_summary(user_id: str = "athlete"):
    """
    Returns analytics summary for the frontend dashboard.
    """
    profile = user_profiles.get(user_id, user_profiles["athlete"])
    recent = iot_data_store[-10:]
    avg_heart_rate = round(
        sum(item["heart_rate_bpm"] for item in recent) / len(recent),
        1
    ) if recent else profile["dashboard"]["average_heart_rate"]
    peak_speed = max((item["speed_kmh"] for item in recent), default=0)

    return {
        "user": {
            "id": user_id,
            "name": profile["name"],
            "email": profile["email"],
            "avatar": profile["avatar"],
            "fitness_level": profile["fitness_level"],
            "goals": profile["goals"],
            "joined_date": profile["joined_date"]
        },
        "habit_prediction": profile["habit_prediction"],
        "iot_status": profile["iot_status"],
        "weekly_performance_score": profile["dashboard"]["weekly_performance_score"],
        "total_calories": profile["dashboard"]["total_calories"],
        "hours_trained": profile["dashboard"]["hours_trained"],
        "avg_heart_rate_bpm": avg_heart_rate,
        "peak_speed_kmh": peak_speed,
        "workouts_this_week": profile["dashboard"]["workouts_this_week"],
        "personal_best": profile["dashboard"]["personal_best"],
        "recent_workouts": profile["recent_workouts"],
        "recent_iot_data": recent
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
