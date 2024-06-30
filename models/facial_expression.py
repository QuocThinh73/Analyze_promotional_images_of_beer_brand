import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import cv2
from deepface import DeepFace


def analyze_emotion(image_path):
    try:
        # Load image to ensure it is valid
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Image not found or invalid image format")

        print(f"Analyzing image at: {image_path}")
        analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=False)
        return analysis
    except Exception as e:
        print(f"An error occurred: {e}")
        raise