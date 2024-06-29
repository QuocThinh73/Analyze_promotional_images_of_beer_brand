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
st.set_page_config(layout="wide")
html_content = """<div class='menu'><div class='menu-header'>Upload your pic here!</div></div>"""
css_styles = """<style>body {font-family: Arial, sans-serif;} .menu {margin-top: 20px; text-align: center;} .menu-header {font-size: 50px; font-weight: bold; color: #ffffff; margin-bottom: 20px;}</style>"""

def analyze_image(image):
    return "Sample Analysis Result"

db_host = 'Farol\SQLEXPRESS'  # Adjust as necessary
db_user = 'hackathon1'       # Adjust as necessary
db_password = '123456'  # Adjust as necessary
db_name = 'image_analysis'  # Adjust as necessary
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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_analysis_result(db, file_key, result, image_data):
    analysis = ImageAnalysis(file_key=file_key, result=result, image_data=image_data)
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis

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
        # Xử lý đầu vào là URL
        response = requests.get(image_input)
        image = Image.open(io.BytesIO(response.content))
    else:
        # Xử lý đầu vào là file đã tải lên
        image = Image.open(image_input)

    with io.BytesIO() as byte_io:
        image.save(byte_io, format='PNG')
        return byte_io.getvalue()

def main():
    st.markdown("# Web AI Image Part Identification")
    st.sidebar.markdown(html_content, unsafe_allow_html=True)
    st.sidebar.markdown(css_styles, unsafe_allow_html=True)
    uploaded_files = st.sidebar.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            image_binary = convert_image_to_binary(uploaded_file)
            result = analyze_image(uploaded_file)
            db = next(get_db())
            save_analysis_result(db, uploaded_file.name, result, image_binary)

    status_url = st.sidebar.text_input("Enter Facebook status URL:")
    if status_url and st.sidebar.button("Retrieve Images from Facebook Status"):
        images = get_images_from_facebook_status(status_url)
        if images:
            for image_url in images:
                image_binary = convert_image_to_binary(image_url)
                result = analyze_image(image_url)
                db = next(get_db())
                save_analysis_result(db, image_url, result, image_binary)

if __name__ == "__main__":
    main()
