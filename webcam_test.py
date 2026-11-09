import cv2

# Open laptop webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Webcam not detected!")
    exit()

print("Webcam connected successfully!")
print("Press Q to close the camera.")

while True:

    # Capture video frame
    success, frame = camera.read()

    if not success:
        print("Failed to capture video!")
        break

    # Display webcam
    cv2.imshow("AI Virtual Computer Controller - Webcam", frame)

    # Press Q to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release webcam
camera.release()
cv2.destroyAllWindows()

print("Webcam closed successfully!")