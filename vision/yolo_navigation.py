import cv2
from ultralytics import YOLO
import sys
import os
import time

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from navigation.grid import grid, START, GOAL
from navigation.astar import a_star


# =============================
# YOLO
# =============================

model = YOLO("yolo11n.pt")

url = "http://192.168.100.103:8080/video"
cap = cv2.VideoCapture(url)


# =============================
# OBJECTS
# =============================

OBSTACLE_CLASSES = [
    "bicycle",
    "car",
    "motorcycle",
    "bus",
    "truck",
    "chair",
    "bench",
    "suitcase"
]

RESCUE_CLASS = "person"


# =============================
# ROVER
# =============================

rover_position = list(START)

STATE = "NAVIGATING"

MOVE_DELAY = 1.0
last_move_time = time.time()

obstacles_detected = 0
replans = 0
distance_travelled = 0


# =============================
# CAMERA → GRID
# =============================

def add_camera_obstacle(position):

    if position == "LEFT":
        cell = (8, 3)

    elif position == "CENTER":
        cell = (8, 5)

    else:
        cell = (8, 7)

    row, col = cell

    if grid[row][col] == 0:
        grid[row][col] = 1
        return True

    return False


# =============================
# MOVE ROVER
# =============================

def move_rover(path):

    global rover_position
    global distance_travelled

    if not path:
        return

    current = tuple(rover_position)

    if current == GOAL:
        return

    if current in path:

        index = path.index(current)

        if index + 1 < len(path):

            next_position = path[index + 1]

            rover_position[0] = next_position[0]
            rover_position[1] = next_position[1]

            distance_travelled += 1

            print(
                f"🤖 Rover: {current} → {next_position}"
            )


# =============================
# START
# =============================

print("====================================")
print("🚀 NETHRA SEARCH & RESCUE")
print("====================================")
print("📱 Phone camera: CONNECTED")
print("🤖 YOLO: ACTIVE")
print("🧭 A*: ACTIVE")
print("🔎 Search & Rescue: ACTIVE")
print("Press Q to stop.")
print()


path = a_star(
    tuple(rover_position),
    GOAL
)


# =============================
# MAIN LOOP
# =============================

while True:

    ret, frame = cap.read()

    if not ret:
        print("❌ Camera frame unavailable")
        break


    results = model(
        frame,
        verbose=False
    )

    height, width = frame.shape[:2]

    obstacle_detected = False
    rescue_detected = False


    # =========================
    # DETECTIONS
    # =========================

    for box in results[0].boxes:

        class_id = int(box.cls[0])

        class_name = model.names[class_id]

        confidence = float(box.conf[0])


        if confidence < 0.5:
            continue


        x1, y1, x2, y2 = map(
            int,
            box.xyxy[0]
        )

        center_x = (x1 + x2) // 2


        # -------------------------
        # RESCUE PERSON
        # -------------------------

        if class_name == RESCUE_CLASS:

            rescue_detected = True

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (255, 0, 0),
                3
            )

            cv2.putText(
                frame,
                "RESCUE TARGET",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2
            )

            continue


        # -------------------------
        # OBSTACLE
        # -------------------------

        if class_name not in OBSTACLE_CLASSES:
            continue


        if center_x < width / 3:

            position = "LEFT"

        elif center_x < 2 * width / 3:

            position = "CENTER"

        else:

            position = "RIGHT"


        print(
            f"🚧 {class_name} → {position}"
        )


        added = add_camera_obstacle(
            position
        )


        if added:

            obstacle_detected = True
            obstacles_detected += 1
            replans += 1

            print(
                "🔄 Replanning route..."
            )


        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"{class_name} {confidence:.2f}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )


    # =============================
    # RESCUE FOUND
    # =============================

    if rescue_detected:

        STATE = "TARGET_DETECTED"

        cv2.putText(
            frame,
            "🚨 RESCUE TARGET FOUND",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 0, 0),
            3
        )

        print(
            "🚨 RESCUE TARGET DETECTED!"
        )

        # Stop rover
        path = []

    else:

        # =========================
        # NAVIGATION
        # =========================

        if STATE != "MISSION_COMPLETE":

            path = a_star(
                tuple(rover_position),
                GOAL
            )


            if path:

                if obstacle_detected:

                    STATE = "REPLANNING"

                else:

                    STATE = "NAVIGATING"


                current_time = time.time()


                if (
                    current_time - last_move_time
                    >= MOVE_DELAY
                ):

                    move_rover(path)

                    last_move_time = current_time


            else:

                STATE = "NO_SAFE_PATH"


    # =============================
    # GOAL
    # =============================

    if tuple(rover_position) == GOAL:

        STATE = "MISSION_COMPLETE"

        path = []

        print(
            "🎯 SEARCH AREA REACHED"
        )


    # =============================
    # DISPLAY
    # =============================

    cv2.putText(
        frame,
        f"STATE: {STATE}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"ROVER: {tuple(rover_position)}",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"OBSTACLES: {obstacles_detected}",
        (20, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"REPLANS: {replans}",
        (20, 135),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"DISTANCE: {distance_travelled}",
        (20, 165),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


    cv2.imshow(
        "NETHRA - Search & Rescue",
        frame
    )


    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# =============================
# CLEANUP
# =============================

cap.release()
cv2.destroyAllWindows()

print()
print("====================================")
print("NETHRA MISSION SUMMARY")
print("====================================")
print("Final position:", tuple(rover_position))
print("Obstacles detected:", obstacles_detected)
print("Replans:", replans)
print("Distance travelled:", distance_travelled)
print("Final state:", STATE)