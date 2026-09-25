import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolo11n.pt")

# Your phone camera stream
url = "http://192.168.100.103:8080/video"

cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("❌ Could not connect to phone camera.")
    exit()

print("✅ NETHRA live YOLO started!")
print("Press Q to stop.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("❌ Could not receive frame.")
        break

    # Run YOLO on the current camera frame
    results = model(frame, verbose=False)

    # Draw detections
    annotated_frame = results[0].plot()

    # Show result
    cv2.imshow("NETHRA - Live YOLO Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()