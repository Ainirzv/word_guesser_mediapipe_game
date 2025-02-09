import cv2
import mediapipe as mp
import numpy as np
import random
import time

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Start Video Capture
cap = cv2.VideoCapture(0)

# Easy Word List with Simple Hand and Shoulder Gestures
words = {
    "Tree": "Raise both hands up like branches",
    "Book": "Hold hands together like an open book",
    "Bird": "Flap arms like wings",
    "House": "Make a triangle over your head with hands",
    "Wave": "Raise one hand and wave",
}

# Choose a Random Word
current_word = random.choice(list(words.keys()))
start_time = time.time()
score = 0
pose_done = False  # Flag to prevent repeated scoring

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert Frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect Pose
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        h, w, _ = frame.shape

        # Get Key Points
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
        right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]

        # Convert to Pixels
        left_wrist_y = int(left_wrist.y * h)
        right_wrist_y = int(right_wrist.y * h)
        left_elbow_y = int(left_elbow.y * h)
        right_elbow_y = int(right_elbow.y * h)

        # Check Pose Conditions
        correct_pose = False
        if current_word == "Tree" and left_wrist_y < h // 3 and right_wrist_y < h // 3:
            correct_pose = True
        elif current_word == "Book" and abs(left_wrist.x - right_wrist.x) < 0.1:
            correct_pose = True
        elif current_word == "Bird" and left_elbow_y < left_wrist_y and right_elbow_y < right_wrist_y:
            correct_pose = True
        elif current_word == "House" and abs(left_wrist.x - right_wrist.x) < 0.2 and left_wrist_y < h // 3:
            correct_pose = True
        elif current_word == "Wave" and left_wrist_y < h // 3:
            correct_pose = True

        # Prevent Continuous Scoring
        if correct_pose and not pose_done:
            pose_done = True
            score += 1
            current_word = random.choice(list(words.keys()))
            start_time = time.time()
        elif not correct_pose:
            pose_done = False  # Reset when out of pose

        # Display Pose Instructions
        color = (0, 255, 0) if correct_pose else (0, 0, 255)
        cv2.putText(frame, f"Word: {current_word}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, f"Instruction: {words[current_word]}", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Score: {score}", (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Show Frame
    cv2.imshow("Word Guessing Game", frame)

    # Exit on 'q' Key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
