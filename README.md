# HackHCMC2024
# Web AI Image Part Identification

Welcome to the Web AI Image Part Identification application. This tool allows you to upload images or fetch images from a Facebook status URL, analyze them using various AI models, and save the results to a database.

## Requirements

1. Python 3.7 or higher
2. The following Python packages:
   - streamlit
   - selenium
   - sqlalchemy
   - PIL (Pillow)
   - requests
   - webdriver_manager
   - your custom models (image_easyocr, image_caption, facial_expression, get_object_yolo, analyze_image_information)

## Installation Instructions

1. Clone the repository or download the source code.

2. Navigate to the directory containing the source code.

3. Create a virtual environment and activate it:
   ```bash
   python -m venv env
   source env/bin/activate   # On Windows, use `env\Scripts\activate`
Install the required packages:

bash
pip install streamlit selenium sqlalchemy pillow requests webdriver_manager
Make sure your custom models are accessible (image_easyocr, image_caption, facial_expression, get_object_yolo, analyze_image_information).

Ensure you have access to the SQL Server database with the necessary configurations.

Database Configuration
Create a SQL Server database named image_analysis.

Run the following SQL commands to create the required table:

sql
USE image_analysis;
GO

CREATE TABLE image_analysis_results (
    id INT PRIMARY KEY IDENTITY(1,1),  
    file_key NVARCHAR(1000),    
    result TEXT,                      
    image_data VARBINARY(MAX),
    file_key_hash AS CAST(HASHBYTES('SHA2_256', file_key) AS BINARY(32)) PERSISTED
);
GO

CREATE UNIQUE INDEX UQ_file_key_hash ON image_analysis_results(file_key_hash);
GO
Update the DATABASE_URL in your Python script if needed to match your database credentials.

Running the Application
Make sure your virtual environment is activated.

Run the Streamlit application:

bash
streamlit run analyse.py
Open your web browser and go to the URL provided by Streamlit (usually http://localhost:8501).

Using the Application
Uploading Images:

In the sidebar, click on the "Browse files" button to upload one or more images (jpg, jpeg, png).
Once uploaded, the images will be displayed along with their analysis results.
Fetching Images from Facebook:

Enter the URL of a Facebook status in the text input box.
Click the "Retrieve Images from Facebook Status" button.
The images from the Facebook status will be fetched, analyzed, and displayed.
Viewing and Managing Analysis History:

You can view the analysis history by running the history.py script.
To clear the analysis history, click the "Clear All" button in the sidebar of the history.py application.
Database Management:

All image analysis results are stored in the SQL Server database.
The file_key ensures that duplicate images are not stored multiple times.

Troubleshooting
Database Connection Issues:

Ensure that the SQL Server is running and accessible.
Verify that the DATABASE_URL in the script is correct.
Package Installation Issues:

Ensure all required packages are installed in your virtual environment.
Check for any compatibility issues with your Python version.
General Errors:

Check the Streamlit logs for detailed error messages.
Verify that all custom model files are correctly imported and available.
