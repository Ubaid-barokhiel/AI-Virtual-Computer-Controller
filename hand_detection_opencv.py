
import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Webcam not detected!")
    exit()

print("OpenCV Hand Detection Started!")
print("Show your hand in front of the camera.")
print("Press Q to exit.")

while True:
    success, frame = camera.read()

    if not success:
        print("Camera frame failed!")
        break

    frame = cv2.flip(frame, 1)

    # Convert image to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Detect skin-colored areas
    lower_skin = (0, 20, 70)
    upper_skin = (20, 255, 255)

    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    # Remove small noise
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (5, 5)
    )

    mask = cv2.morphologyEx(
        mask, cv2.MORPH_OPEN, kernel
    )

    # Ignore upper 35% of the frame
    height, width = mask.shape
    mask[:int(height * 0.35), :] = 0

    # Find contours
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # Detect largest skin-colored area
    if contours:
        largest_contour = max(
            contours,
            key=cv2.contourArea
        )

        area = cv2.contourArea(largest_contour)

        if area > 10000:
            x, y, w, h = cv2.boundingRect(
                largest_contour
            )

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                "Hand Detected",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

    # Display camera window
    cv2.imshow("OpenCV Hand Detection", frame)

    # Display skin mask
    cv2.imshow("Skin Detection Mask", mask)

    # Exit using Q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()

print("Detection Stopped!")
