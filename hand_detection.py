import cv2
import mediapipe as mp
import time

# Model path
MODEL_PATH = "models/hand_landmarker.task"

# MediaPipe configuration
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

# Hand connections
connections = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]

# Open webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Webcam not detected!")
    exit()

print("Hand Detection Started!")
print("Press Q to exit.")

start_time = time.perf_counter()

# Create hand detector
with HandLandmarker.create_from_options(options) as detector:

    while True:

        success, frame = camera.read()

        if not success:
            print("Camera frame failed!")
            break

        # Mirror webcam
        frame = cv2.flip(frame, 1)

        height, width, _ = frame.shape

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(
            frame, cv2.COLOR_BGR2RGB
        )

        # Create MediaPipe image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Timestamp for video processing
        timestamp_ms = int(
            (time.perf_counter() - start_time) * 1000
        )

        # Detect hands
        results = detector.detect_for_video(
            mp_image, timestamp_ms
        )

        hand_count = 0

        if results.hand_landmarks:

            hand_count = len(results.hand_landmarks)

            for hand_landmarks in results.hand_landmarks:

                points = []

                # Get 21 hand landmarks
                for landmark in hand_landmarks:

                    x = int(landmark.x * width)
                    y = int(landmark.y * height)

                    points.append((x, y))

                    cv2.circle(
                        frame,
                        (x, y),
                        6,
                        (0, 255, 0),
                        -1
                    )

                # Draw hand connections
                for start, end in connections:

                    cv2.line(
                        frame,
                        points[start],
                        points[end],
                        (255, 0, 255),
                        2
                    )

        # Display hand count
        cv2.putText(
            frame,
            f"Hands Detected: {hand_count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.imshow(
            "AI Virtual Computer Controller - Hand Detection",
            frame
        )

        # Exit with Q
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release resources
camera.release()
cv2.destroyAllWindows()

print("Hand Detection Stopped!")