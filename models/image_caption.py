import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from transformers import pipeline


def get_image_caption(image):
    # Use a pre-trained image captioning model from Salesforce
    caption_pipeline = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
    return caption_pipeline(image)[0]['generated_text']