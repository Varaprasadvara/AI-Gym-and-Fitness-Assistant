import time
import random
import requests

API_URL = "http://localhost:8000/api/iot/receive-data"

def simulate_iot_device():
    """
    Simulates a Smart Gym IoT Device (e.g., Smart Dumbbell or Treadmill).
    Sends mock heart rate and resistance data to the backend.
    """
    print("Starting Smart Gym IoT Simulator...")
    
    device_id = "smart_treadmill_01"
    
    while True:
        # Mock data generation
        heart_rate = random.randint(90, 150)
        speed = round(random.uniform(5.0, 12.0), 1)
        incline = random.randint(0, 15)
        
        payload = {
            "device_id": device_id,
            "sensor_type": "treadmill",
            "heart_rate_bpm": heart_rate,
            "speed_kmh": speed,
            "incline_percent": incline,
            "timestamp": time.time()
        }
        
        try:
            # Send to backend
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                print(f"Sent: {payload} -> {response.json()}")
            else:
                print(f"Failed to send data. Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Connection refused. Is the server running? ({e})")
            
        time.sleep(5) # Send data every 5 seconds

if __name__ == "__main__":
    simulate_iot_device()
