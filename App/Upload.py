import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Set page configuration
st.set_page_config(layout="wide")

# HTML content
html_content = """
<div class="menu">
    <div class="menu-header">Upload your pic here!</div>
</div>
"""

# CSS styles
css_styles = """
<style>
body {
    font-family: Arial, sans-serif;
}
.menu {
    margin-top: 20px;
    margin-bottom: 20px;
    text-align: center;
}
.menu-header {
    font-size: 50px;
    font-weight: bold;
    color: #fffff; 
    margin-bottom: 20px;
}
</style>
"""

def get_images_from_facebook_status(status_url):
    try:
        # Set up Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

        # Open the Facebook post URL
        driver.get(status_url)

        # Wait for the page to load
        driver.implicitly_wait(10)

        # Find all image elements
        img_elements = driver.find_elements(By.TAG_NAME, 'img')

        image_urls = []
        for img in img_elements:
            img_url = img.get_attribute('src')
            if img_url and 'scontent' in img_url:
                image_urls.append(img_url)

        driver.quit()

        if image_urls:
            return image_urls
        else:
            st.error("No images found from the Facebook status.")
            return []
    
    except Exception as e:
        st.error(f"Error retrieving images from Facebook status: {str(e)}")
        return []

def main():
    st.markdown("# Web AI Image Part Identification")

    # Initialize session state variables if not exist
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []

    if 'image_urls' not in st.session_state:
        st.session_state.image_urls = []

    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}

    if 'analysis_results_fb' not in st.session_state:
        st.session_state.analysis_results_fb = {}

    # Set up sidebar with functions
    st.sidebar.markdown(html_content, unsafe_allow_html=True)
    st.sidebar.markdown(css_styles, unsafe_allow_html=True)

    # Upload image function
    st.sidebar.markdown("<h2>Upload Images</h2>", unsafe_allow_html=True)
    uploaded_files = st.sidebar.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files

    # Retrieve images from Facebook status
    st.sidebar.markdown("<h2>Retrieve Images from Facebook Status</h2>", unsafe_allow_html=True)
    status_url = st.sidebar.text_input("Enter Facebook status URL:")

    if 'image_urls' not in st.session_state:
        st.session_state.image_urls = []

    if status_url and st.sidebar.button("Retrieve Images from Facebook Status"):
        st.session_state.image_urls = get_images_from_facebook_status(status_url)

    # Clear uploaded images button
    st.sidebar.markdown("<h2>Clear Uploaded Images</h2>", unsafe_allow_html=True)
    if st.sidebar.button("Clear Uploaded Images"):
        if 'uploaded_files' not in st.session_state or not st.session_state.uploaded_files:
            st.warning("No uploaded images to clear.")
        else:
            st.session_state.uploaded_files = []

    # Display uploaded images
    if 'uploaded_files' in st.session_state and st.session_state.uploaded_files:
        for idx, uploaded_file in enumerate(st.session_state.uploaded_files):
            st.image(uploaded_file, caption=f'Uploaded Image {idx + 1}: {uploaded_file.name}', use_column_width=True)

    # Display Facebook images
    if 'image_urls' in st.session_state and st.session_state.image_urls:
        for idx, image_url in enumerate(st.session_state.image_urls):
            st.image(image_url, caption=f'Image from Facebook status {idx + 1}', use_column_width=True)

if __name__ == "__main__":
    main()
