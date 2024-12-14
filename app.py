import google.generativeai as genai
import os
from tkinter import Tk, filedialog
from PIL import Image
import io
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

# Function to prompt the user to upload an image file
def upload_image():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    file_path = filedialog.askopenfilename(
        title="Select Image File",
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png")]
    )

    return file_path

# Function to analyze and extract key details from image content using Gemini
def analyze_image(image_path):
    try:
        with open(image_path, 'rb') as f:
            img_data = f.read()

        img = Image.open(io.BytesIO(img_data))
    except Exception as e:
        return f"Error loading image: {e}"

    # Refined, more general prompt to avoid triggering safety flags
    prompt = 'Analyze and extract relevant details from the image, such as payee name, bank name, cheque number, and other general information in table form.'

    try:
        # Send the image data and prompt to Gemini API for analysis
        result = model.generate_content([img, prompt])
        
        # Check if the result is valid and contains usable content
        if result.text:
            return result.text
        else:
            return "No usable content returned by Gemini API."

    except Exception as e:
        return f"Error processing the image with Gemini: {e}"

# Main function
def main():
    print("### Google Gemini AI - Image Analysis ###")

    # Prompt user to upload image
    image_path = upload_image()

    if not image_path:
        print("No image selected. Exiting.")
        return
    
    print(f"\nAnalyzing image: {image_path}...")

    # Analyze the image and get the extracted information
    analysis_result = analyze_image(image_path)

    # Display the results
    print("\n### Extracted Information ###")
    print(analysis_result)

if __name__ == "__main__":
    main()
