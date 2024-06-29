import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Set up SQLAlchemy connection to MySQL database
db_user = 'farolnguyen'
db_password = 'Nghiep123sql-'
db_host = 'localhost'
db_port = 3308
db_name = 'image_analysis'

# Connect to MySQL database
engine = create_engine(f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}')

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Define SQLAlchemy Base
Base = declarative_base()

# Define SQLAlchemy model for image analysis results table
class ImageAnalysisResult(Base):
    __tablename__ = 'image_analysis_results'
    id = Column(Integer, primary_key=True)
    file_name = Column(String)
    analysis_result = Column(String)

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Function to analyze uploaded images
def analyze_uploaded_images():
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}

    if 'uploaded_files' in st.session_state and st.session_state.uploaded_files:
        for idx, uploaded_file in enumerate(st.session_state.uploaded_files):
            file_key = f"uploaded_{uploaded_file.name}_{idx}"

            col1, col2 = st.columns([3, 1])

            with col1:
                st.image(uploaded_file, caption=f'Uploaded Image: {uploaded_file.name}', use_column_width=True)

            if file_key in st.session_state.analysis_results:
                with col2:
                    st.subheader(f"Analysis Result for: {uploaded_file.name}")
                    st.write(st.session_state.analysis_results[file_key])

            # Perform analysis (replace with your actual analysis function)
            analysis_result = perform_image_analysis(uploaded_file)

            # Save to database
            save_to_database(uploaded_file.name, analysis_result)

# Function to analyze images from Facebook
def analyze_facebook_images():
    if 'analysis_results_fb' not in st.session_state:
        st.session_state.analysis_results_fb = {}

    if 'image_urls' in st.session_state and st.session_state.image_urls:
        for idx, image_url in enumerate(st.session_state.image_urls):
            file_key = f"fb_{idx}"

            col1, col2 = st.columns([3, 1])

            with col1:
                st.image(image_url, caption=f'Image from Facebook status {idx + 1}', use_column_width=True)

            if file_key in st.session_state.analysis_results_fb:
                with col2:
                    st.subheader(f"Analysis Result for Image {idx + 1}")
                    st.write(st.session_state.analysis_results_fb[file_key])

            # Perform analysis (replace with your actual analysis function)
            analysis_result = perform_image_analysis_fb(image_url)

            # Save to database
            save_to_database(image_url, analysis_result)

# Function to analyze all images (both uploaded and from Facebook)
def analyze_all_images():
    # Check if there are no uploaded images or images retrieved from Facebook
    if ('uploaded_files' not in st.session_state or not st.session_state.uploaded_files) and \
       ('image_urls' not in st.session_state or not st.session_state.image_urls):
        st.warning("You have not added any images or retrieved images from Facebook.")
        return

    # Analyze uploaded images
    if 'uploaded_files' in st.session_state and st.session_state.uploaded_files:
        for idx, uploaded_file in enumerate(st.session_state.uploaded_files):
            file_key = f"uploaded_{uploaded_file.name}_{idx}"
            st.session_state.analysis_results[file_key] = "Analyzing uploaded image..."

            # Perform analysis (replace with your actual analysis function)
            analysis_result = perform_image_analysis(uploaded_file)

            # Save to database
            save_to_database(uploaded_file.name, analysis_result)

    # Analyze images from Facebook
    if 'image_urls' in st.session_state and st.session_state.image_urls:
        for idx, image_url in enumerate(st.session_state.image_urls):
            file_key = f"fb_{idx}"
            st.session_state.analysis_results_fb[file_key] = "Analyzing Facebook image..."

            # Perform analysis (replace with your actual analysis function)
            analysis_result = perform_image_analysis_fb(image_url)

            # Save to database
            save_to_database(image_url, analysis_result)

# Placeholder function for image analysis
def perform_image_analysis(image_data):
    return "Image analysis result placeholder."

# Placeholder function for Facebook image analysis
def perform_image_analysis_fb(image_url):
    return "Facebook image analysis result placeholder."

# Function to save analysis result to database
def save_to_database(file_name, analysis_result):
    try:
        result_entry = ImageAnalysisResult(file_name=file_name, analysis_result=analysis_result)
        session.add(result_entry)
        session.commit()
        st.success(f"Analysis result for {file_name} saved to database.")
    except IntegrityError:
        session.rollback()
        st.error(f"Error: Analysis result for {file_name} already exists in database.")

# Main function to run the Streamlit app
def main():
    st.markdown("# Analyze Images")

    # Initialize session state variables if not exist
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []

    if 'image_urls' not in st.session_state:
        st.session_state.image_urls = []

    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}

    if 'analysis_results_fb' not in st.session_state:
        st.session_state.analysis_results_fb = {}

    # Analyze all images button in the sidebar
    st.sidebar.markdown("<h2>Analyze Images</h2>", unsafe_allow_html=True)
    if st.sidebar.button("Analyze All Images"):
        analyze_all_images()

    # Display and analyze uploaded images
    analyze_uploaded_images()

    # Display and analyze Facebook images
    analyze_facebook_images()

if __name__ == "__main__":
    main()
