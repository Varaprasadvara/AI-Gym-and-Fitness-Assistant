import cv2
import numpy as np
import random

try:
    import mediapipe as mp
    # Try different import patterns for compatibility
    try:
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
    except AttributeError:
        # Fallback for older versions
        import mediapipe.python.solutions.pose as mp_pose
        pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
    MEDIAPIPE_AVAILABLE = True
except (ImportError, AttributeError, Exception) as e:
    print(f"Warning: MediaPipe failed to load properly ({e}). Using mock pose estimation.")
    MEDIAPIPE_AVAILABLE = False
    mp_pose = None
    pose = None

def calculate_angle(a, b, c):
    """
    Calculate the angle between three points.
    a, b, c are tuples or lists of (x, y) coordinates.
    b is the vertex.
    """
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

def analyze_pose_image(image_bytes: bytes):
    """
    Processes an image byte stream, extracts pose landmarks, and provides basic feedback.
    Falls back to mock data if MediaPipe is not available.
    """
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        # Decode image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return {"status": "error", "message": "Could not decode image."}

        if not MEDIAPIPE_AVAILABLE:
            # Return mock data for demonstration purposes if MediaPipe fails
            mock_angle = random.randint(20, 170)
            mock_stage = "down" if mock_angle > 140 else ("up" if mock_angle < 40 else "curling")
            
            return {
                "status": "success",
                "pose_detected": True,
                "angle": mock_angle,
                "stage": mock_stage,
                "feedback": "Mock Mode: Keep going! (MediaPipe unavailable)",
                "landmarks": [
                    {"x": 0.5, "y": 0.3, "z": 0.0, "visibility": 0.9},
                    {"x": 0.55, "y": 0.5, "z": 0.0, "visibility": 0.9},
                    {"x": 0.6, "y": 0.3 if mock_stage == "up" else 0.7, "z": 0.0, "visibility": 0.9}
                ]
            }

        # Convert the BGR image to RGB before processing.
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image and find poses
        results = pose.process(image_rgb)
        
        if not results.pose_landmarks:
            return {"status": "success", "pose_detected": False, "message": "No pose detected in the frame."}
        
        landmarks = results.pose_landmarks.landmark
        
        # Extract coordinates for left arm (shoulder, elbow, wrist) as an example
        # MediaPipe landmarks are normalized [0.0, 1.0]
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        
        # Calculate angle
        angle = calculate_angle(shoulder, elbow, wrist)
        
        # Basic logic for a bicep curl
        feedback = "Good posture."
        if angle > 160:
            stage = "down"
            feedback = "Arm is fully extended. Ready to curl."
        elif angle < 30:
            stage = "up"
            feedback = "Good squeeze!"
        else:
            stage = "curling"
            feedback = "Keep the tension."

        # Format landmarks to send back to frontend for drawing
        formatted_landmarks = []
        for lm in landmarks:
            formatted_landmarks.append({
                "x": lm.x,
                "y": lm.y,
                "z": lm.z,
                "visibility": lm.visibility
            })

        return {
            "status": "success",
            "pose_detected": True,
            "angle": round(angle, 2),
            "stage": stage,
            "feedback": feedback,
            # Return landmarks so the frontend can draw the skeleton
            "landmarks": formatted_landmarks
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
