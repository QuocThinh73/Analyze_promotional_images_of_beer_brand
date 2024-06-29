import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Text, LargeBinary
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from PIL import Image
import io

db_host = 'Farol\SQLEXPRESS'  
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
    file_key = Column(String(1000), unique=True)
    result = Column(Text)
    image_data = Column(LargeBinary)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def fetch_all_results(db):
    return db.query(ImageAnalysis).all()

def display_analysis_results():
    db = next(get_db())
    results = fetch_all_results(db)
    if results:
        for result in results:
            image = Image.open(io.BytesIO(result.image_data))
            col1, col2, col3 = st.columns([2, 1, 3])  # Ajust the width ratios as needed
            with col1:
                st.image(image, caption=f"{result.file_key}")
            with col2:
                st.write(" ")  # This can be used for spacing if needed
            with col3:
                st.write(f"**File Key:** {result.file_key}")
                st.write(f"**Analysis Result:** {result.result}")
    else:
        st.write("No results to display.")

def main():
    st.sidebar.title("Image Analysis Dashboard")
    if st.sidebar.button("Export All Analysis Results"):
        display_analysis_results()

if __name__ == "__main__":
    main()
