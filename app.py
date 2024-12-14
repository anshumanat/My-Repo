import os
import google.generativeai as genai
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key securely
API_KEY = st.secrets["GEMINI_API_KEY"]["value"]

# Ensure the API key is set
if not API_KEY:
    st.error("API Key not found! Ensure GEMINI_API_KEY is set in your .env file.")
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

# Streamlit UI
st.title("Google Gemini AI - Image Analysis")
st.markdown("Upload an image to extract relevant details like Payee Name, Bank Name, Cheque Number, etc.")

# Upload image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
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
st.markdown(
    """
    #### How it works:
    - Upload a cheque image to extract key details.
    - The app uses **Google Gemini AI** to analyze the image and extract relevant information like:
      - Payee Name
      - Bank Name
      - Account Number
      - Cheque Number
      - Amount and other details
    """
)

