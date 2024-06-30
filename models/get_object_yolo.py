from ultralytics import YOLOv10
import numpy as np
from PIL import Image

def get_object_yolo(image_path):
    # Load YOLOv10 model
    model = YOLOv10.from_pretrained('jameslahm/yolov10s')

    # Open the image using PIL
    image = Image.open(image_path).convert("RGB")

    # Convert PIL image to numpy array
    image_np = np.array(image)

    # Perform object detection
    results = model.predict(image_np)

    # Initialize a dictionary to store the count of each object type
    object_counts = {}

    # Parse results
    for result in results:
        for obj in result.boxes:
            # Get the class label (cls) for each detected object
            label = int(obj.cls.item())  # Convert tensor to int

            # Use the class label as the dictionary key
            if label in object_counts:
                object_counts[label] += 1
            else:
                object_counts[label] = 1

    return object_counts