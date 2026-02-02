import time
import requests
from arduino.app_utils import App, Bridge

# --- PUSHOVER CONFIGURATION ---
USER_KEY = "ujp8jgveyezdejoom17dbtjx3243fi"
API_TOKEN = "agui9hrfut5x5vzgig5tnn65c8i7u8"

def send_push_alert(force):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": API_TOKEN,
        "user": USER_KEY,
        "message": f"🚨 FALL DETECTED! Impact: {force:.2f} G.",
        "title": "Patient Alert!",
        "priority": 1 
    }
    try:
        response = requests.post(url, data=data, timeout=5)
        if response.status_code == 200:
            print(">>> Success: Pushover alert delivered.")
        else:
            print(f">>> API Error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f">>> ALERT FAILED: Check internet connection. ({e})")

# --- BRIDGE CALLBACKS (Arduino to Python) ---
def on_fall_detected(force):
    print(f"\n[{time.strftime('%H:%M:%S')}] CRITICAL: Fall detected ({force:.2f} G)!")
    send_push_alert(force)

def on_manual_test(val):
    print(f"\n[{time.strftime('%H:%M:%S')}] System Check: Manual Test triggered.")

# --- MAIN LOOP ---
def main():
    print("--- Parkinson's Caregiver System: ACTIVE ---")
    
    # 1. Register listeners for events coming FROM Arduino
    Bridge.provide("report_fall", on_fall_detected)
    Bridge.provide("manual_test", on_manual_test)
    
    last_temp_check = 0
    temp_interval = 10  # Seconds between temperature checks

    while True:
        current_time = time.time()
        
        # 2. Polling Logic: Request data FROM Arduino every 10 seconds
        if current_time - last_temp_check > temp_interval:
            try:
                temp = Bridge.call("get_temp")
                
                if temp is not None:
                    temp_val = float(temp)
                    print(f"[{time.strftime('%H:%M:%S')}] Health Status - Temp: {temp_val:.2f} F")
                    
                    # Overheating logic
                    if temp_val > 100.4:
                        print("!!! WARNING: Fever Detected !!!")
                        Bridge.call("set_buzzer", True)
                    else:
                        Bridge.call("set_buzzer", False)
                
            except Exception as e:
                print(f">>> Syncing... ({e})")
            
            last_temp_check = current_time

        # Small sleep to prevent CPU spiking while allowing Bridge to stay responsive
        time.sleep(0.1)

if __name__ == "__main__":
    App.run(main)
