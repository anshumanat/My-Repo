import os
import google.generativeai as genai
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import requests
import io
from pdf2image import convert_from_path

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key and token securely
try:
    # CloudConvert API Token (securely fetched from secrets or environment variables)
    cloudconvert_api_token = st.secrets.get("CLOUDCONVERT_API_TOKEN") or os.getenv("CLOUDCONVERT_API_TOKEN")
    if not cloudconvert_api_token:
        raise KeyError("CloudConvert API Token not found in secrets or environment variables.")

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

# Function to convert PDF to Images using pdf2image library
def convert_pdf_to_images(pdf_file):
    # Convert PDF to images (one image per page)
    images = convert_from_path(pdf_file)
    return images

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
    Upload an image of a cheque or a PDF containing multiple cheque images to extract key details like Payee Name, Bank Name, Cheque Number, and more.
    This tool uses **Google Gemini AI** to intelligently analyze the image.
""")

# File uploader for image or PDF
uploaded_file = st.file_uploader("Choose a file (PDF, JPG, PNG)...", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        st.info("Processing PDF with multiple pages...")

        # Convert the PDF to images (one image per page)
        images = convert_pdf_to_images(uploaded_file)

        # Display each image and process it
        for i, image in enumerate(images):
            st.image(image, caption=f"Page {i+1} Image", use_column_width=True)

            if st.button(f"Analyze Page {i+1}"):
                with st.spinner(f"Processing Page {i+1}..."):
                    analysis_result = analyze_image(image)
                    st.subheader(f"Extracted Information from Page {i+1}:")
                    st.write(analysis_result)

    else:
        # If the uploaded file is an image, open it directly
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("Analyze Image"):
            with st.spinner("Processing..."):
                analysis_result = analyze_image(image)
                st.subheader("Extracted Information:")
                st.write(analysis_result)

# Additional instructions and info
st.markdown("""
    #### How it works:
    - Upload a cheque image or PDF to extract key details.
    - The app uses **Google Gemini AI** to analyze the image and extract relevant information such as:
      - Payee Name
      - Bank Name
      - Account Number
      - Cheque Number
      - Amount and other details
    - For PDF files, each page will be processed individually.
""")

