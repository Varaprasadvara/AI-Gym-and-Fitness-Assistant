# AI Gym & Fitness Assistant

A comprehensive AI-powered fitness application with pose estimation, diet planning, virtual coaching, and IoT integration.

## Features

- **AI Pose Estimation**: Real-time form analysis using MediaPipe
- **Diet Planning**: Personalized meal plans based on BMI and goals
- **Virtual Gym Buddy**: AI chatbot for motivation and advice
- **User Profiles**: Track fitness levels, goals, and progress
- **IoT Integration**: Connect with smart gym equipment
- **Analytics Dashboard**: Performance tracking and habit prediction

## Project Structure

```
major project/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── requirements.txt        # Python dependencies
│   ├── mock_iot_sensor.py      # IoT simulator
│   └── ai_modules/
│       ├── pose_estimation.py  # AI pose analysis
│       ├── diet_coach.py       # Diet planning AI
│       └── chatbot.py          # Virtual assistant
└── frontend/
    ├── index.html              # Main UI
    ├── css/
    │   ├── style.css           # Main styles
    │   └── chatbot_style.css   # Chat styles
    └── js/
        └── app.js              # Frontend logic
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the FastAPI server:
   ```bash
   python main.py
   ```

The server will start on `http://localhost:8000`

### Frontend Access

The frontend is automatically served by the FastAPI backend. Open your browser and go to:

```
http://localhost:8000
```

**Important**: Do not open `index.html` directly in the browser (file:// protocol) as it will cause API connection issues.

### IoT Simulator (Optional)

To simulate IoT device data:

1. Open a new terminal
2. Navigate to backend directory
3. Run:
   ```bash
   python mock_iot_sensor.py
   ```

This will send mock heart rate and treadmill data to the backend every 5 seconds.

## API Endpoints

- `GET /` - Serve frontend
- `POST /api/trainer/analyze-pose` - Pose analysis
- `POST /api/dietician/recommend` - Diet recommendations
- `POST /api/chatbot/chat` - Chat with AI buddy
- `GET/POST /api/users/{user_id}` - User profiles
- `POST /api/iot/receive-data` - IoT data ingestion
- `GET /api/analytics/summary` - Dashboard analytics

## Technologies Used

- **Backend**: FastAPI, Python
- **AI/ML**: MediaPipe (pose estimation)
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **Icons**: Font Awesome

## Troubleshooting

### MediaPipe Issues
If you see MediaPipe import errors, the app will automatically fall back to mock pose estimation for demonstration purposes.

### Port Conflicts
If port 8000 is busy, modify the port in `main.py`:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

### CORS Issues
The backend is configured to allow all origins for development. For production, restrict the origins in `main.py`.

## Development

To modify the AI modules, edit files in `backend/ai_modules/`. The server auto-reloads on changes.

For frontend changes, edit files in `frontend/` and refresh the browser.