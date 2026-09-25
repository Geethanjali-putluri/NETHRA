import cv2
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

url = "http://192.168.100.103:8080/video"
cap = cv2.VideoCapture(url)

OBSTACLE_CLASSES = [
    "person",
    "bicycle",
    "car",
    "motorcycle",
    "bus",
    "truck",
    "chair",
    "bench",
    "suitcase"
]

while True:
    ret, frame = cap.read()

    if not ret:
        break

    results = model(frame, verbose=False)

    height, width = frame.shape[:2]

    for box in results[0].boxes:
        class_id = int(box.cls[0])
        class_name = model.names[class_id]

        if class_name not in OBSTACLE_CLASSES:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        center_x = (x1 + x2) // 2

        # Divide camera view into 3 regions
        if center_x < width / 3:
            position = "LEFT"
        elif center_x < 2 * width / 3:
            position = "CENTER"
        else:
            position = "RIGHT"

        print(f"Obstacle: {class_name} | Position: {position}")

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"{class_name} - {position}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    cv2.imshow("NETHRA - Obstacle Position", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()