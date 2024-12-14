import time
import os
import google.generativeai as genai
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import requests
import io
import cloudconvert
import zipfile

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

# Initialize CloudConvert with API token
cloudconvert.configure(api_key=cloudconvert_api_token)

# Initialize the Generative Model
model = genai.GenerativeModel('models/gemini-1.5-pro-001')

# Function to convert PDF to Images using CloudConvert API
def convert_pdf_to_images(uploaded_file):
    with open("/tmp/tempfile.pdf", "wb") as f:
        f.write(uploaded_file.getvalue())

    try:
        # Create a job for converting PDF to images using CloudConvert API
        job = cloudconvert.Job.create({
            'tasks': {
                'import-1': {
                    'operation': 'import/upload'
                },
                'convert-1': {
                    'operation': 'convert',
                    'input': 'import-1',
                    'input_format': 'pdf',
                    'output_format': 'png',
                    'engine': 'poppler'
                },
                'export-1': {
                    'operation': 'export/url',
                    'input': 'convert-1'
                }
            }
        })

        # Debugging: Print the full job response
        print("CloudConvert Job Response:", job)

        if "tasks" not in job:
            raise KeyError("No tasks found in the job response.")

        # Upload the PDF file to CloudConvert
        upload_task = job['tasks'][0]
        upload_url = upload_task['result']['form']['url']
        file_form = upload_task['result']['form']

        # Upload the file to CloudConvert
        cloudconvert.files.upload(file_form, "/tmp/tempfile.pdf")

        # Indicating that the conversion is in progress
        st.write("Conversion in progress...")
        time.sleep(2)  # Simulate delay for progress bar

        # Poll the task to check if it's done
        while job['tasks'][1]['status'] != "finished":
            time.sleep(5)  # Wait for a while before checking again
            job = cloudconvert.Job.fetch(job['id'])  # Fetch the job status

        # Task finished, now get the export URL
        export_task = job['tasks'][2]
        download_url = export_task['result']['files'][0]['url']

        # Download the converted images (ZIP file)
        img_data = cloudconvert.files.download(download_url)

        return img_data

    except Exception as e:
        st.error(f"Error converting PDF to images: {str(e)}")
        return None

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

        # Show progress bar for PDF conversion
        progress_bar = st.progress(0)
        for percent in range(0, 101, 10):
            time.sleep(1)  # Simulate time delay for processing
            progress_bar.progress(percent)

        # Convert the PDF to images using CloudConvert
        img_data = convert_pdf_to_images(uploaded_file)

        if img_data:
            # Save the converted images as a ZIP file
            with open("/tmp/converted_images.zip", "wb") as f:
                f.write(img_data)

            st.success("PDF converted to images successfully!")

            # Extract and display the images from the ZIP file
            with zipfile.ZipFile("/tmp/converted_images.zip", "r") as zip_ref:
                zip_ref.extractall("/tmp/")  # Extract all images to /tmp/
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
            st.error("Error converting the PDF to images.")
        
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



