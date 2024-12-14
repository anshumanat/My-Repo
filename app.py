import os
import google.generativeai as genai
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import requests
import io
import cloudconvert  # CloudConvert SDK for conversion
import zipfile  # Import zipfile module to handle ZIP files

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

# Initialize CloudConvert client
cloudconvert_client = cloudconvert.ApiClient(api_key=cloudconvert_api_token)

# Initialize the Generative Model
model = genai.GenerativeModel('models/gemini-1.5-pro-001')

# Function to convert PDF to Images using CloudConvert API
def convert_pdf_to_images(uploaded_file):
    # Save uploaded PDF to a temporary file
    with open("/tmp/tempfile.pdf", "wb") as f:
        f.write(uploaded_file.getvalue())

    # Create a CloudConvert job to convert PDF to images
    job = cloudconvert_client.jobs.create({
        'tasks': {
            'import-1': {
                'operation': 'import/upload'
            },
            'convert-1': {
                'operation': 'convert',
                'input': 'import-1',
                'input_format': 'pdf',
                'output_format': 'png',  # You can choose 'png' or 'jpg'
                'engine': 'poppler'
            },
            'export-1': {
                'operation': 'export/url',
                'input': 'convert-1'
            }
        }
    })

    # Upload the PDF file to CloudConvert
    upload_task = job['tasks'][0]
    upload_url = upload_task['result']['form']['url']
    file_form = upload_task['result']['form']

    # Upload the PDF file
    response = cloudconvert_client.files.upload(file_form, "/tmp/tempfile.pdf")
    
    # Check if the conversion is complete
    export_task = job['tasks'][2]
    download_url = export_task['result']['files'][0]['url']
    
    # Download the converted images (as a ZIP file)
    img_data = cloudconvert_client.files.download(download_url)
    
    return img_data

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
        st.info("Processing PDF with CloudConvert...")

        # Convert the PDF to images using CloudConvert
        img_data = convert_pdf_to_images(uploaded_file)

        # Save the converted images as a ZIP file
        with open("/tmp/converted_images.zip", "wb") as f:
            f.write(img_data)

        st.success("PDF converted to images successfully!")

        # Extract and display the images from the ZIP file
        with zipfile.ZipFile("/tmp/converted_images.zip", "r") as zip_ref:
            zip_ref.extractall("/tmp/")  # Extract all images to /tmp/
            # Get all PNG files in the extracted folder
            images = [Image.open(os.path.join("/tmp/", f)) for f in os.listdir("/tmp/") if f.endswith(".png")]

        # Display each extracted image and analyze it
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

