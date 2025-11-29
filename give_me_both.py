import pandas as pd
import numpy as np
import time
import threading
import cv2
import mediapipe as mp
from pythonosc import udp_client

client = udp_client.SimpleUDPClient("127.0.0.1", 57120)
df = pd.read_csv("NCD_RisC_Lancet_2020_height_child_adolescent_global.csv")

print("interactive height data sonification")
print(f"dataset loaded: {len(df)} records\n")

camera_height = None
person_was_detected = False

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
    
    current_sample = -1
    
    NUM_SAMPLES = 46  # Change to match your sample count
    MIN_HEIGHT = 115
    MAX_HEIGHT = 250
    
    last_height_send = 0  # Track when we last sent height
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        
        if results.pose_landmarks:
            nose = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
            estimated_height = 170 + (0.5 - nose.y) * 200
            
            # Map to sample
            height_clipped = np.clip(estimated_height, MIN_HEIGHT, MAX_HEIGHT)
            normalized = (height_clipped - MIN_HEIGHT) / (MAX_HEIGHT - MIN_HEIGHT)
            sample_index = int(normalized * NUM_SAMPLES)
            sample_index = min(sample_index, NUM_SAMPLES - 1)
            
            if sample_index != current_sample:
                print(f"\n🎵 Height: {estimated_height:.1f}cm → Sample {sample_index}")
                client.send_message("/sample/select", sample_index)
                current_sample = sample_index
            
            camera_height = estimated_height
            
            # Send height blips while person is detected
            current_time = time.time()
            if current_time - last_height_send > 0.2:
                freq = height_to_frequency(estimated_height)
                client.send_message("/height", [float(estimated_height), float(freq)])
                last_height_send = current_time
            
            if not person_was_detected:
                print(f"\n🎥 PERSON DETECTED!")
                client.send_message("/person/enter", 1)
                person_was_detected = True
        else:
            if person_was_detected:
                print("\n👋 Person left")
                client.send_message("/person/exit", 1)
                person_was_detected = False
                current_sample = -1
            camera_height = None
    cap.release()

def main_sonification():
    print("starting sonification with LLN progression...\n")
    
    height_column = 'Mean height'
    se_col = 'Mean height standard error'
    
    while True:
        # First 75: n=1
        print("\nSampling random heights (n=1)...\n")
        for i in range(0, 75):
            while camera_height is not None:  # WAIT while person is there
                time.sleep(0.05)
            
            sample_height = df[height_column].sample(1).values[0]
            sample_se = df[se_col].sample(1).values[0]
            freq = height_to_frequency(sample_height)
            
            print(f"Sample {i+1}: Height = {sample_height:.1f} cm → Frequency = {freq:.1f} Hz")
            client.send_message("/height", [float(sample_height), float(freq)])
            time.sleep(sample_se)
        
        # Next 75: alternate between n=1 and n=2
        for i in range(0, 75):
            while camera_height is not None:  # WAIT while person is there
                time.sleep(0.05)
            
            # n=1
            sample_height = df[height_column].sample(1).values[0]
            sample_se = df[se_col].sample(1).values[0]
            freq = height_to_frequency(sample_height)
            print(f"Sample {i+1}: Height = {sample_height:.1f} cm → Frequency = {freq:.1f} Hz")
            client.send_message("/height", [float(sample_height), float(freq)])
            time.sleep(sample_se)
            
            while camera_height is not None:  # WAIT while person is there
                time.sleep(0.05)
            
            # n=2
            heights = df[height_column].sample(2).values
            sample_height = np.mean(heights)
            ses = df[se_col].sample(2).values
            sample_se = np.mean(ses)
            freq = height_to_frequency(sample_height)
            print(f"Sample {i+1}: Height = {sample_height:.1f} cm → Frequency = {freq:.1f} Hz")
            client.send_message("/height", [float(sample_height), float(freq)])
            time.sleep(sample_se)
        
        # Gradual increase
        for i in range(2, 1000, 5):
            print(f"sample size: {i}")
            for k in range(0, 5):
                while camera_height is not None:  # WAIT while person is there
                    time.sleep(0.05)
                
                heights = df[height_column].sample(i).values
                sample_height = np.mean(heights)
                ses = df[se_col].sample(i).values
                sample_se = np.mean(ses)
                freq = height_to_frequency(sample_height)
                
                print(f"Sample {k+1}: Height = {sample_height:.1f} cm → Frequency = {freq:.1f} Hz")
                client.send_message("/height", [float(sample_height), float(freq)])
                time.sleep(sample_se)

if __name__ == "__main__":
    camera_thread = threading.Thread(target=camera_detection_thread, daemon=True)
    camera_thread.start()
    
    try:
        main_sonification()
    except KeyboardInterrupt:
        print("\n\nstopping...")