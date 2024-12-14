import os
import google.generativeai as genai
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import requests
import io

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key securely from Streamlit Secrets
API_KEY = st.secrets["GEMINI_API_KEY"]["value"]

# Ensure the API key is set
if not API_KEY:
    st.error("API Key not found! Ensure GEMINI_API_KEY is set in your Streamlit Secrets.")
    st.stop()
else:
    # Configure Google Gemini API
    genai.configure(api_key=API_KEY)

# Initialize the Generative Model
model = genai.GenerativeModel('models/gemini-1.5-pro-001')

# Function to convert PDF to Image using CloudConvert API
def convert_pdf_to_image(pdf_file):
    # CloudConvert API endpoint and your API key (sign up for CloudConvert and get your API key)
    api_key = "your_cloudconvert_api_key"  # Replace with your actual API key
    url = "https://api.cloudconvert.com/v2/convert"

    # Send the PDF to CloudConvert API for conversion to image
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        files={"file": pdf_file},
    )
    
    # If the request is successful, return the image
    if response.status_code == 200:
        image_data = response.content
        return Image.open(io.BytesIO(image_data))
    else:
        return None

# Function to analyze and extract key details from the image using Gemini
def analyze_image(image):
    # Prepare the prompt for Gemini API
    prompt = 'Analyze and extract relevant details from the image, such as payee name, bank name, cheque number, and other general information.'

    try:
        # Send the image data and prompt to Gemini API for analysis
        result = model.generate_content([image, prompt])

        # Check if the result is valid and contains usable content
        if result.text:
            return result.text
        else:
            return "No usable content returned by Gemini API."

    except Exception as e:
        return f"Error processing the image with Gemini: {e}"

# Streamlit UI with a better title and UI enhancements
st.title("Checkmate: AI-Powered Cheque Information Extraction")
st.markdown("""
    Upload an image of a cheque or a PDF to extract key details like Payee Name, Bank Name, Cheque Number, and more.
    This tool uses **Google Gemini AI** to intelligently analyze the image.
""")

# File uploader for image or PDF
uploaded_file = st.file_uploader("Choose a file (PDF, JPG, PNG)...", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file is not None:
    # Check if the uploaded file is a PDF
    if uploaded_file.type == "application/pdf":
        st.info("Processing PDF...")

        # Convert the PDF to an image using CloudConvert API
        image = convert_pdf_to_image(uploaded_file)

        if image:
            # Display the converted image
            st.image(image, caption="Converted Image", use_column_width=True)
        else:
            st.error("Failed to convert PDF to image.")

    else:
        # If the uploaded file is an image, open it directly
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

    # Analyze the image when the user clicks the button
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
""")

