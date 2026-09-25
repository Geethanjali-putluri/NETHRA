from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolo11n.pt")

# Test on an example image
results = model("https://ultralytics.com/images/bus.jpg")

# Show the result
results[0].show()