import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from sqlalchemy import create_engine, Column, Integer, String, Text, LargeBinary
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from PIL import Image
import io
import requests
from models import image_easyocr, image_caption, facial_expression, get_object_yolo, analyze_image_information
import os
from urllib.parse import urlparse, unquote
from contextlib import contextmanager

# Set page configuration as the first Streamlit command
st.set_page_config(layout="wide", page_title="Web AI Image Part Identification")

# Define global configurations and CSS
html_content = """<div class='menu'><div class='menu-header'>Upload your pic here!</div></div>"""
css_styles = """<style>body {font-family: Arial, sans-serif;} .menu {margin-top: 20px; text-align: center;} .menu-header {font-size: 50px; font-weight: bold; color: #ffffff; margin-bottom: 20px;}</style>"""

db_host = 'Farol\\SQLEXPRESS'
db_user = 'hackathon1'
db_password = '123456'
db_name = 'image_analysis'
DATABASE_URL = f"mssql+pyodbc://{db_user}:{db_password}@{db_host}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ImageAnalysis(Base):
    __tablename__ = "image_analysis_results"
    id = Column(Integer, primary_key=True)
    file_key = Column(String(1000), unique=True)  # Adjusted length
    result = Column(Text)
    image_data = Column(LargeBinary)

Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_analysis_result(db, file_key, result, image_data):
    existing_record = db.query(ImageAnalysis).filter_by(file_key=file_key).first()
    if existing_record:
        st.info("This image already exists in the database.")
        return None
    else:
        try:
            analysis = ImageAnalysis(file_key=file_key, result=result, image_data=image_data)
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            st.success("Image analysis result saved successfully.")
            return analysis
        except Exception as e:
            db.rollback()
            st.error(f"An error occurred: {str(e)}")
            return None

def get_images_from_facebook_status(status_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(status_url)
    driver.implicitly_wait(10)
    img_elements = driver.find_elements(By.TAG_NAME, 'img')
    image_urls = [img.get_attribute('src') for img in img_elements if 'scontent' in img.get_attribute('src')]
    driver.quit()
    return image_urls

def convert_image_to_binary(image_input):
    if isinstance(image_input, str) and image_input.startswith('http'):
        response = requests.get(image_input)
        image = Image.open(io.BytesIO(response.content))
    else:
        image = Image.open(image_input)

    with io.BytesIO() as byte_io:
        image.save(byte_io, format='PNG')
        return byte_io.getvalue()

def save_uploaded_file(file_input):
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    if isinstance(file_input, str):  # URL case
        parsed_url = urlparse(file_input)
        file_name = os.path.basename(parsed_url.path)
        file_path = os.path.join(temp_dir, unquote(file_name))
        
        response = requests.get(file_input)
        with open(file_path, "wb") as f:
            f.write(response.content)
    else:  # Uploaded file case
        file_path = os.path.join(temp_dir, file_input.name)
        with open(file_path, "wb") as f:
            f.write(file_input.getbuffer())
    
    return file_path

def main():
    st.markdown("# Web AI Image Part Identification")
    st.sidebar.markdown(html_content, unsafe_allow_html=True)
    st.sidebar.markdown(css_styles, unsafe_allow_html=True)
    uploaded_files = st.sidebar.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    status_url = st.sidebar.text_input("Enter Facebook status URL:")
    fb_button_pressed = st.sidebar.button("Retrieve Images from Facebook Status")

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = save_uploaded_file(uploaded_file)
            image = Image.open(file_path).convert("RGB")
            image_binary = convert_image_to_binary(uploaded_file)
            
            # Models
            ocr_results = image_easyocr.perform_ocr(image)
            image_caption_results = image_caption.get_image_caption(image)
            facial_expression_results = facial_expression.analyze_emotion(file_path)
            yolo_results = get_object_yolo.get_object_yolo(file_path)
            
            result = analyze_image_information.analyze_image_information(image_caption_results, ocr_results, yolo_results, facial_expression_results)
            
            with get_db() as db:
                analysis = save_analysis_result(db, uploaded_file.name, result, image_binary)
            
            col1, col2 = st.columns([1, 2])  # Create two columns with specified width ratios
            with col1:
                st.image(image, caption="Uploaded Image")
            with col2:
                if analysis:
                    st.write(result)
                else:
                    st.write("This image already exists in the database.")

    if status_url and fb_button_pressed:
        images = get_images_from_facebook_status(status_url)
        if images:
            for image_url in images:
                file_path = save_uploaded_file(image_url)
                image_binary = convert_image_to_binary(image_url)
                image = Image.open(file_path).convert("RGB")

                # Models
                ocr_results = image_easyocr.perform_ocr(image)
                image_caption_results = image_caption.get_image_caption(image)
                facial_expression_results = facial_expression.analyze_emotion(file_path)
                yolo_results = get_object_yolo.get_object_yolo(file_path)

                result = analyze_image_information.analyze_image_information(image_caption_results, ocr_results, yolo_results, facial_expression_results)
                
                with get_db() as db:
                    analysis = save_analysis_result(db, image_url, result, image_binary)
                
                col1, col2 = st.columns([1, 2])  # Create two columns with specified width ratios
                with col1:
                    st.image(image, caption="Facebook Image")
                with col2:
                    if analysis:
                        st.write(f"**Analysis Result:** {result}")
                    else:
                        st.write("This image already exists in the database.")

if __name__ == "__main__":
    main()
