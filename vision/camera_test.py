import cv2

# Your phone's IP Webcam address
url = "http://192.168.100.103:8080/video"

# Connect OpenCV to the phone camera
cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("❌ Could not connect to the phone camera.")
    exit()

print("✅ Phone camera connected!")
print("Press Q to stop.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("❌ Could not receive camera frame.")
        break

    cv2.imshow("NETHRA - Live Phone Camera", frame)

    # Press Q to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()