from flask import Flask, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import threading
import time
import sys
import os

# Find NETHRA root
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from navigation.grid import grid, START, GOAL
from navigation.astar import a_star


app = Flask(__name__)
CORS(app)


# ==========================================
# YOLO
# ==========================================

model = YOLO("yolo11n.pt")

CAMERA_URL = "http://192.168.100.103:8080/video"


# ==========================================
# OBJECTS
# ==========================================

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


# ==========================================
# SYSTEM STATE
# ==========================================

rover_position = list(START)

state = "IDLE"

running = False
emergency_stop = False

obstacles_detected = 0
replans = 0
distance_travelled = 0

last_detections = []

mission_start_time = None


# ==========================================
# CAMERA → GRID
# ==========================================

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


# ==========================================
# ROVER MOVEMENT
# ==========================================

def move_rover(path):

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


# ==========================================
# VISION + NAVIGATION LOOP
# ==========================================

def vision_loop():

    global state
    global running
    global emergency_stop
    global obstacles_detected
    global replans
    global last_detections

    cap = cv2.VideoCapture(CAMERA_URL)

    while True:

        ret, frame = cap.read()

        if not ret:
            time.sleep(1)
            continue

        results = model(
            frame,
            verbose=False
        )

        height, width = frame.shape[:2]

        detections = []

        rescue_found = False
        new_obstacle = False


        # ==================================
        # YOLO DETECTIONS
        # ==================================

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


            if center_x < width / 3:
                position = "LEFT"

            elif center_x < 2 * width / 3:
                position = "CENTER"

            else:
                position = "RIGHT"


            detection = {
                "object": class_name,
                "confidence": round(confidence, 2),
                "position": position
            }

            detections.append(detection)


            # Rescue target
            if class_name == RESCUE_CLASS:

                rescue_found = True


            # Obstacle
            elif class_name in OBSTACLE_CLASSES:

                added = add_camera_obstacle(
                    position
                )

                if added:

                    obstacles_detected += 1
                    replans += 1
                    new_obstacle = True


        last_detections = detections


        # ==================================
        # MISSION LOGIC
        # ==================================

        if emergency_stop:

            state = "EMERGENCY_STOP"


        elif rescue_found and running:

            state = "TARGET_DETECTED"
            running = False


        elif running:

            path = a_star(
                tuple(rover_position),
                GOAL
            )

            if not path:

                state = "NO_SAFE_PATH"
                running = False

            else:

                if new_obstacle:
                    state = "REPLANNING"
                else:
                    state = "NAVIGATING"

                move_rover(path)

                if tuple(rover_position) == GOAL:

                    state = "MISSION_COMPLETE"
                    running = False


        time.sleep(1)


# ==========================================
# API: SYSTEM STATUS
# ==========================================

@app.route("/api/status")
def get_status():

    path = a_star(
        tuple(rover_position),
        GOAL
    )

    return jsonify({

        "state": state,

        "rover_position": rover_position,

        "goal": list(GOAL),

        "path_length": len(path) if path else 0,

        "obstacles": obstacles_detected,

        "replans": replans,

        "distance": distance_travelled,

        "camera": "IP WEBCAM",

        "vision": "LIVE / WORKING",

        "yolo": "LIVE / WORKING",

        "navigation": "LIVE / WORKING",

        "rover": "SIMULATION",

        "detections": last_detections

    })


# ==========================================
# API: GRID
# ==========================================

@app.route("/api/navigation")
def navigation():

    path = a_star(
        tuple(rover_position),
        GOAL
    )

    return jsonify({

        "grid": grid,

        "start": list(START),

        "goal": list(GOAL),

        "rover": rover_position,

        "path": path if path else []

    })


# ==========================================
# START MISSION
# ==========================================

@app.route("/api/mission/start", methods=["POST"])
def start_mission():

    global running
    global emergency_stop
    global state
    global mission_start_time

    emergency_stop = False
    running = True

    mission_start_time = time.time()

    state = "NAVIGATING"

    return jsonify({
        "success": True,
        "state": state
    })


# ==========================================
# STOP
# ==========================================

@app.route("/api/mission/stop", methods=["POST"])
def stop_mission():

    global running
    global state

    running = False
    state = "STOPPED"

    return jsonify({
        "success": True,
        "state": state
    })


# ==========================================
# EMERGENCY STOP
# ==========================================

@app.route("/api/mission/emergency-stop", methods=["POST"])
def emergency():

    global running
    global emergency_stop
    global state

    running = False
    emergency_stop = True

    state = "EMERGENCY_STOP"

    return jsonify({
        "success": True,
        "state": state
    })


# ==========================================
# RESUME
# ==========================================

@app.route("/api/mission/resume", methods=["POST"])
def resume():

    global running
    global emergency_stop
    global state

    emergency_stop = False
    running = True

    state = "NAVIGATING"

    return jsonify({
        "success": True,
        "state": state
    })


# ==========================================
# TELEMETRY
# ==========================================

@app.route("/api/telemetry")
def telemetry():

    path = a_star(
        tuple(rover_position),
        GOAL
    )

    return jsonify({

        "position": rover_position,

        "state": state,

        "distance": distance_travelled,

        "obstacles": obstacles_detected,

        "replans": replans,

        "path_length": len(path) if path else 0,

        "mission_time": (
            round(time.time() - mission_start_time, 1)
            if mission_start_time
            else 0
        )

    })


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":

    vision_thread = threading.Thread(
        target=vision_loop,
        daemon=True
    )

    vision_thread.start()

    print("====================================")
    print("🚀 NETHRA BACKEND")
    print("====================================")
    print("📱 Camera: IP Webcam")
    print("🤖 YOLO: ACTIVE")
    print("🧭 A*: ACTIVE")
    print("🌐 API: http://127.0.0.1:5000")
    print("====================================")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )