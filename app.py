import cloudconvert
import streamlit as st
from PIL import Image
import io
import os

# CloudConvert API Token (securely fetched from secrets)
cloudconvert_api_token = st.secrets.get("CLOUDCONVERT_API_TOKEN") or os.getenv("CLOUDCONVERT_API_TOKEN")

# Initialize CloudConvert client
cloudconvert_client = cloudconvert.ApiClient(api_key=cloudconvert_api_token)

# Function to convert PDF to images using CloudConvert API
def convert_pdf_to_images(uploaded_file):
    # Create the temporary input file
    with open("/tmp/tempfile.pdf", "wb") as f:
        f.write(uploaded_file.getvalue())

    # CloudConvert job to convert PDF to images
    job = cloudconvert_client.jobs.create({
        'tasks': {
            'import-1': {
                'operation': 'import/upload'
            },
            'convert-1': {
                'operation': 'convert',
                'input': 'import-1',
                'input_format': 'pdf',
                'output_format': 'png',  # Or 'jpeg' based on preference
                'engine': 'poppler'
            },
            'export-1': {
                'operation': 'export/url',
                'input': 'convert-1'
            }
        }
    })

    # Upload PDF file to CloudConvert
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

# Streamlit UI
st.title("Checkmate: AI-Powered Cheque Information Extraction")
st.markdown("""
    Upload a cheque image or a PDF containing multiple cheque images to extract key details like Payee Name, Bank Name, Cheque Number, and more.
    This tool uses **Google Gemini AI** to intelligently analyze the image.
""")

# File uploader for image or PDF
uploaded_file = st.file_uploader("Choose a file (PDF, JPG, PNG)...", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        st.info("Processing PDF with CloudConvert...")

        # Convert PDF to images using CloudConvert
        img_data = convert_pdf_to_images(uploaded_file)
        
        # Assuming the CloudConvert API returns images as ZIP files
        # Unzip and process each image (if it's a zip)
        # Display images or handle them accordingly
        with open("/tmp/converted_images.zip", "wb") as f:
            f.write(img_data)

        st.success("PDF converted to images successfully!")
        # Process each image in the ZIP, etc.
        # You can unzip the files and display them in Streamlit

    else:
        # If the uploaded file is an image, open it directly
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("Analyze Image"):
            with st.spinner("Processing..."):
                analysis_result = analyze_image(image)
                st.subheader("Extracted Information:")
                st.write(analysis_result)


