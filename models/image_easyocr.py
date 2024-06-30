import easyocr
import numpy as np


ocr_reader = easyocr.Reader(["en"])

def perform_ocr(image):
    result = ocr_reader.readtext(np.array(image))
    ocr_texts = [line[1] for line in result]
    return ocr_texts