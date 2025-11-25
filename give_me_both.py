import pandas as pd
import numpy as np
import time
import threading
import cv2
import mediapipe as mp
from pythonosc import udp_client

heights = []
client = udp_client.SimpleUDPClient("127.0.0.1", 57120)
df = pd.read_csv("NCD_RisC_Lancet_2020_height_child_adolescent_global.csv")

print("interactive height data sonification")
print(f"dataset loaded: {len(df)} records\n")

camera_height = None
person_was_detected = False  # Track state changes

def height_to_frequency(height_cm, min_height=100, max_height=200):
    normalized = (height_cm - min_height) / (max_height - min_height)
    normalized = np.clip(normalized, 0, 1)
    freq = 200 * (2 ** (normalized * 4))
    return freq

def camera_detection_thread():
    global camera_height, person_was_detected
    print("initializing camera")

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("error: could not open camera")
        return
    
    print("camera initialized successfully")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        
        if results.pose_landmarks:
            nose = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
            estimated_height = 170 + (0.5 - nose.y) * 200
            camera_height = estimated_height
            
            if not person_was_detected:
                print(f"\n🎥 PERSON DETECTED! Locking to height: {estimated_height:.1f} cm")
                freq = height_to_frequency(estimated_height)
                # Send start sample message
                client.send_message("/sample/start", [float(estimated_height), float(freq)])
                person_was_detected = True
        else:
            if person_was_detected:
                print("\n👋 Person left - resuming random sampling")
                # Send stop sample message
                client.send_message("/sample/stop", 1)
                person_was_detected = False
            camera_height = None
    cap.release()

def main_sonification():
    print("starting sonification... (step in front of camera to lock your height)\n")
    i = 0
    while True:
        if camera_height is not None:
            # locked mode: person detected 
            freq = height_to_frequency(camera_height)
            print(f"🔒 LOCKED: your height = {camera_height:.1f} cm → {freq:.1f} Hz", end='\r')
            client.send_message("/height", [float(camera_height), float(freq)])
            time.sleep(0.05)  # Slower updates to avoid FIFO overload
            
        else:
            # random mode: no person detected
            height_column = 'Mean height'
            se_col = 'Mean height standard error'
            
            sample_height = df[height_column].sample(1).values[0]
            sample_se = df[se_col].sample(1).values[0]
            freq = height_to_frequency(sample_height)
            
            print(f"Sample {i}: Height = {sample_height:.1f} cm → Frequency = {freq:.1f} Hz")
            client.send_message("/height", [float(sample_height), float(freq)])
            
            time.sleep(sample_se)
            i += 1

if __name__ == "__main__":
    camera_thread = threading.Thread(target=camera_detection_thread, daemon=True)
    camera_thread.start()
    try:
        main_sonification()
    except KeyboardInterrupt:
        print("\n\nstopping...")