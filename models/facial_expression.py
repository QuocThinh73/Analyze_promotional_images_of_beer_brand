import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


from deepface import DeepFace


def analyze_emotion(image_path):
    analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'])
    emotions = []
    for face in analysis:
        emotions.append(face['dominant_emotion'])
    return emotions