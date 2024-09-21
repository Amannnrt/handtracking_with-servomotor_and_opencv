import cv2
import mediapipe as mp
import socket

# Initialize MediaPipe Hand Detection
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Initialize the video capture
cap = cv2.VideoCapture(1)

# Set up socket connection to Pico W
pico_ip = "192.168.1.4"  # Replace with your Pico W's IP address
pico_port = 8769
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Failed to capture image.")
        continue
    image = cv2.flip(image, 1)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image.flags.writeable = False
    results = hands.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Calculate center of the palm (average of landmark positions)
            ih, iw, _ = image.shape
            center_x = int(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * iw)
            center_y = int(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y * ih)

            # Send coordinates to Pico W
            message = f"{center_x},{center_y},{iw},{ih}"
            print(f"Sending: {message}")  # Debug print
            sock.sendto(message.encode(), (pico_ip, pico_port))

            # Draw lines for both x and y axes
            cv2.line(image, (center_x, 0), (center_x, ih), (0, 255, 0), 2)  # Vertical line
            cv2.line(image, (0, center_y), (iw, center_y), (255, 0, 0), 2)  # Horizontal line

    cv2.imshow('MediaPipe Hand Detection', image)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
sock.close()
