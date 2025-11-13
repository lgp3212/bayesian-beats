import cv2
import mediapipe as mp
from pythonosc import udp_client

# OSC setup
client = udp_client.SimpleUDPClient("127.0.0.1", 57120)  # sc default port

# mediapipe pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5)

# camera setup
cap = cv2.VideoCapture(0)

# config
CAMERA_HEIGHT_CM = 50  # height of laptop camera from ground
KNOWN_DISTANCE_CM = 150  # distance person stands from camera

person_detected = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # convert to rgb for mediapipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)
    
    if results.pose_landmarks:
        # get head top (nose landmark as proxy)
        nose = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
        head_y_pixel = nose.y * frame.shape[0]
        
        # simple mapping: pixel position to height estimate
        # calibrate with known heights 
        estimated_height = 170 + (0.5 - nose.y) * 200  # rough estimate
        
        if not person_detected:
            print(f"Person detected! Height: {estimated_height:.1f} cm")
            client.send_message("/height", [float(estimated_height), float(estimated_height)])
            person_detected = True
        
    else:
        if person_detected:
            print("Person left")
            client.send_message("/nodetection", 1)
            person_detected = False
    
    # Display
    cv2.imshow('Height Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()