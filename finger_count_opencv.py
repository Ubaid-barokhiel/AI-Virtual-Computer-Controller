import cv2
import numpy as np
import math

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Webcam not detected!")
    exit()

print("Finger Counting Started!")
print("Show your palm to the camera.")
print("Press Q to exit.")

while True:
    success, frame = camera.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)

    # Convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Skin color detection
    lower_skin = np.array([0, 20, 70])
    upper_skin = np.array([20, 255, 255])

    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    # Remove noise
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (5, 5)
    )

    mask = cv2.morphologyEx(
        mask, cv2.MORPH_OPEN, kernel
    )

    # Ignore upper 35% of frame
    height, width = mask.shape
    mask[:int(height * 0.35), :] = 0

    # Find contours
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if contours:

        hand = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(hand)

        if area > 10000:

            # Draw hand contour
            cv2.drawContours(
                frame, [hand], -1, (0, 255, 0), 2
            )

            # Find convex hull
            hull = cv2.convexHull(
                hand, returnPoints=False
            )

            finger_count = 0

            if hull is not None and len(hull) >= 3:

                try:
                    defects = cv2.convexityDefects(
                        hand, hull
                    )

                    if defects is not None:

                        for i in range(defects.shape[0]):

                            s, e, f, d = np.asarray(defects[i]).flatten()
                            start = tuple(hand[s][0])
                            end = tuple(hand[e][0])
                            far = tuple(hand[f][0])

                            a = math.dist(start, far)
                            b = math.dist(end, far)
                            c = math.dist(start, end)

                            if a > 0 and b > 0:

                                angle = math.degrees(
                                    math.acos(
                                        max(-1, min(
                                            1,
                                            (a*a + b*b - c*c)
                                            / (2*a*b)
                                        ))
                                    )
                                )

                                depth = d / 256.0

                                if angle < 90 and depth > 20:
                                    finger_count += 1

                                    cv2.circle(
                                        frame,
                                        far,
                                        8,
                                        (255, 0, 0),
                                        -1
                                    )

                    # Estimate fingers from gaps
                    if finger_count > 0:
                        finger_count += 1

                    cv2.putText(
                        frame,
                        f"Fingers: {finger_count}",
                        (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )

                except cv2.error:
                    pass

    else:
        cv2.putText(
            frame,
            "No Hand Detected",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

    # Display windows
    cv2.imshow("Finger Counting", frame)
    cv2.imshow("Hand Mask", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()

print("Finger Counting Stopped!")