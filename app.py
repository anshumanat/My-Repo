# -*- coding: utf-8 -*-
"""Google Gemini AI Integration for Local Python"""

# Google Gemini AI (API)
import google.generativeai as genai

# File management
import os

# Handle images
from PIL import Image

# File upload dialog for local machine
from tkinter import Tk, filedialog

# dotenv to load environment variables
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key securely
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("API Key not found! Ensure GEMINI_API_KEY is set in your .env file.")
else:
    genai.configure(api_key=API_KEY)

# Initialize the Generative Model
model = genai.GenerativeModel('models/gemini-1.5-pro-001')

# Function to prompt the user to upload files
def upload_files():
    # Create a Tkinter root window and hide it
    root = Tk()
    root.withdraw()  # Hide the root window
    root.attributes("-topmost", True)  # Bring dialog to the front
    
    # Prompt the user to select files
    file_paths = filedialog.askopenfilenames(
        title="Select Images",
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    
    return list(file_paths)

# Function to analyze images
def analyze_image(file_path):
    # Load the image
    image = Image.open(file_path)
    prompt = ("Analyze and extract all information from the image, "
              "including Payee Name, Bank Name, Account Number, Date, "
              "Cheque Number, Amount, and all other information.")
    
    # Send image and prompt to the Gemini model
    try:
        result = model.generate_content([image, prompt])
        return result.text
    except Exception as e:
        return f"Error analyzing {os.path.basename(file_path)}: {str(e)}"

# Main function
def main():
    print("### Google Gemini AI - Image Analysis ###")
    print("Select images to analyze using the file dialog.")
    
    # Prompt user to upload files
    uploaded_files = upload_files()
    
    if not uploaded_files:
        print("No files selected. Exiting.")
        return
    
    # Create a directory to store uploaded images (if needed)
    os.makedirs("uploaded_images", exist_ok=True)

    # Process each uploaded file
    for file_path in uploaded_files:
        print(f"\nAnalyzing {file_path}...")
        
        # Save the uploaded file locally
        saved_path = os.path.join("uploaded_images", os.path.basename(file_path))
        with open(saved_path, "wb") as f:
            with open(file_path, "rb") as original_file:
                f.write(original_file.read())
        print(f"File saved to {saved_path}.")
        
        # Analyze the image
        analysis_result = analyze_image(file_path)
        
        # Display the results
        print("\n### Extracted Information ###")
        print(analysis_result)

if __name__ == "__main__":
    main()
