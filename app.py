import os
import google.generativeai as genai
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import requests
import io
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key securely
try:
    # Google Gemini API Key
    gemini_api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise KeyError("Google Gemini API Key not found in secrets or environment variables.")
except KeyError as e:
    st.error(f"Missing API credentials: {e}")
    st.stop()

# Configure Google Gemini API with the key
genai.configure(api_key=gemini_api_key)

# Initialize the Generative Model
model = genai.GenerativeModel('models/gemini-1.5-pro-001')

# List to store processed image data (image name, extracted details)
processed_images_data = []

# Function to analyze and extract key details from the image using Gemini
def analyze_image(image):
    prompt = 'Analyze and extract relevant details from the image, such as payee name, bank name, cheque number, and other general information.'
    
    try:
        result = model.generate_content([image, prompt])

        if result.text:
            return result.text
        else:
            return "No usable content returned by Gemini API."
    except Exception as e:
        return f"Error processing the image with Gemini: {e}"

# Streamlit UI with a better title and UI enhancements
st.title("Checkmate: AI-Powered Cheque Information Extraction")
st.markdown("""
    Upload an image of a cheque to extract key details like Payee Name, Bank Name, Cheque Number, and more.
    This tool uses **Google Gemini AI** to intelligently analyze the image.
""")

# File uploader for image files (JPG, PNG, JPEG)
uploaded_file = st.file_uploader("Choose an image file (JPG, PNG, JPEG)...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Open the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Analyze the image with Gemini AI when the button is clicked
    if st.button("Analyze Image"):
        with st.spinner("Processing..."):
            analysis_result = analyze_image(image)
            st.subheader("Extracted Information:")
            st.write(analysis_result)

            # Store the image data (name, extracted details)
            image_data = {
                'Image Name': uploaded_file.name,
                'Extracted Information': analysis_result
            }
            processed_images_data.append(image_data)

# Show a table with the processed image data (if any)
if processed_images_data:
    st.subheader("Processed Image Data")
    # Convert the list of dictionaries into a pandas DataFrame and display it
    df = pd.DataFrame(processed_images_data)
    st.table(df)

# Additional instructions and info
st.markdown("""
    #### How it works:
    - Upload a cheque image (JPG, PNG, JPEG) to extract key details.
    - The app uses **Google Gemini AI** to analyze the image and extract relevant information such as:
      - Payee Name
      - Bank Name
      - Account Number
      - Cheque Number
      - Amount and other details
    - The processed image data (image name and extracted information) will be displayed in a table below after processing.
""")


