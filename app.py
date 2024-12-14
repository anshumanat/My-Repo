import os
import google.generativeai as genai
import streamlit as st
from PIL import Image
from pdf2image import convert_from_path
from dotenv import load_dotenv

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
    Upload an image or PDF of a cheque to extract key details like Payee Name, Bank Name, Cheque Number, and more.
    This tool uses **Google Gemini AI** to intelligently analyze the image.
""")

# Upload image or PDF functionality
uploaded_file = st.file_uploader("Choose an image or PDF...", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file is not None:
    # Handle PDF files
    if uploaded_file.type == "application/pdf":
        st.write("PDF file detected, converting to image...")

        # Convert the first page of the PDF to an image
        images = convert_from_path(uploaded_file, first_page=1, last_page=1)
        image = images[0]  # Get the first page as an image

        # Display the image
        st.image(image, caption="First page of the uploaded PDF", use_column_width=True)

    else:
        # Read the uploaded image
        image = Image.open(uploaded_file)

        # Display the image
        st.image(image, caption="Uploaded Image", use_column_width=True)

    # Analyze the image when the user clicks the button
    if st.button("Analyze Image"):
        with st.spinner("Processing..."):
            analysis_result = analyze_image(image)
            st.subheader("Extracted Information:")
            st.write(analysis_result)

# Additional styling or info can go here
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
