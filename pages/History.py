import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Text, LargeBinary
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from PIL import Image
import io
import os
import re
import hashlib
import requests
from urllib.parse import urlparse, unquote
from contextlib import contextmanager

# Database configuration
db_host = 'Farol\\SQLEXPRESS'
db_user = 'hackathon1'
db_password = '123456'
db_name = 'image_analysis'
DATABASE_URL = f"mssql+pyodbc://{db_user}:{db_password}@{db_host}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define ImageAnalysis model
class ImageAnalysis(Base):
    __tablename__ = "image_analysis_results"
    id = Column(Integer, primary_key=True)
    file_key = Column(String, unique=True)
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

def fetch_all_results(db):
    return db.query(ImageAnalysis).all()

def delete_all_results(db):
    db.query(ImageAnalysis).delete()
    db.commit()

def sanitize_filename(filename):
    sanitized = re.sub(r'[^a-zA-Z0-9_\\-\\.]', '_', filename)
    max_length = 255
    return sanitized[:max_length]

def generate_unique_filename(filename):
    file_hash = hashlib.md5(filename.encode()).hexdigest()
    _, ext = os.path.splitext(filename)
    return f"{file_hash}{ext}"

def resize_image(image, size=(800, 800)):
    return image.resize(size, Image.ANTIALIAS)

def save_images_to_folder(results, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    for result in results:
        sanitized_file_key = sanitize_filename(result.file_key)
        unique_file_key = generate_unique_filename(sanitized_file_key)
        image_path = os.path.join(folder_path, f"{unique_file_key}.png")
        text_path = os.path.join(folder_path, f"{unique_file_key}.txt")
        
        image = Image.open(io.BytesIO(result.image_data))
        image.save(image_path)
        
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(result.result)
            
    return folder_path

def display_analysis_results(folder_path):
    st.markdown(f"## Analysis Results stored in: `{folder_path}`")
    if "toggle_state" not in st.session_state:
        st.session_state.toggle_state = {}

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".png"):
            image_path = os.path.join(folder_path, file_name)
            text_path = image_path.replace(".png", ".txt")
            
            with st.container():
                st.image(image_path, caption=file_name)
                key = file_name.replace(".", "_")  # Create a unique key for each image
                with st.expander(f"Show/Hide Analysis for {file_name}"):
                    with open(text_path, 'r', encoding='utf-8') as f:
                        st.write(f.read())

def convert_image_to_binary(image_input):
    if isinstance(image_input, str) and image_input.startswith('http'):
        response = requests.get(image_input)
        image = Image.open(io.BytesIO(response.content))
    else:
        image = Image.open(image_input)

    resized_image = resize_image(image)  # Resize the image before converting to binary

    with io.BytesIO() as byte_io:
        resized_image.save(byte_io, format='PNG')
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
    st.sidebar.title("Image Analysis History")
    folder_path = "image_analysis_result"
    
    # Fetch results from database
    with get_db() as db:
        results = fetch_all_results(db)
    
    if st.sidebar.button("Clear All"):
        with get_db() as db:
            delete_all_results(db)
        st.experimental_rerun()  # Refresh the page after deletion
    
    # Fetch results again to ensure the latest state after deletion
    with get_db() as db:
        results = fetch_all_results(db)
    
    if results:
        folder_path = save_images_to_folder(results, folder_path)
        display_analysis_results(folder_path)
    else:
        st.write("No results to display.")

if __name__ == "__main__":
    main()
