import os
import google.generativeai as genai
from PIL import Image
import pandas as pd
import streamlit as st
import re
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

# Function to extract relevant information using regex or string parsing
def extract_details(text):
    # Example of pattern matching - update these as per the actual output structure of the Gemini API.
    
    # Simple patterns for key fields like Amount, Payee, etc.
    details = {
        "Payee Name": re.search(r"Payee Name\s*[:\-]?\s*([A-Za-z\s]+)", text),
        "Bank Name": re.search(r"Bank Name\s*[:\-]?\s*([A-Za-z\s]+)", text),
        "Account Number": re.search(r"Account Number\s*[:\-]?\s*(\d+)", text),
        "Date": re.search(r"Date\s*[:\-]?\s*(\d{4}-\d{2}-\d{2})", text),
        "Cheque Number": re.search(r"Cheque Number\s*[:\-]?\s*(\w+)", text),
        "Amount": re.search(r"Amount\s*[:\-]?\s*\$?(\d+(\.\d{2})?)", text)
    }

    # Extract matching values or use None if no match found
    extracted_data = {
        key: match.group(1) if match else "Not Found"
        for key, match in details.items()
    }

    # Store the entire response in 'Additional Info' for reference
    extracted_data["Additional Info"] = text
    
    return extracted_data

# Function to analyze images and extract relevant details
def analyze_image(image):
    prompt = (
        "Analyze and extract all information from the image, "
        "including Payee Name, Bank Name, Account Number, Date, "
        "Cheque Number, Amount, and all other information."
    )

    try:
        # Send image and prompt to the Gemini model
        result = model.generate_content([image, prompt])
        
        # Process the result and extract details
        extracted_data = extract_details(result.text)

        return extracted_data

    except Exception as e:
        return {"Error": f"Error analyzing image: {str(e)}"}

# Streamlit app main function
def main():
    # Set up Streamlit app layout
    st.title("Google Gemini AI - Image Analysis")
    st.write("Upload an image (e.g., a cheque) for analysis.")

    # Allow user to upload one or multiple images
    uploaded_files = st.file_uploader("Upload Image(s)", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

    if uploaded_files:
        # Store extracted data for all uploaded images
        all_extracted_data = []

        for uploaded_file in uploaded_files:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption=uploaded_file.name, use_column_width=True)

            # Analyze the image using the Gemini model
            st.write("Analyzing image...")
            analysis_result = analyze_image(image)

            # Display the analysis results in table format
            st.subheader("Extracted Information (Table Format)")

            # Convert extracted data to a DataFrame
            df = pd.DataFrame([analysis_result])

            # Display the data as a table
            st.table(df)  # or st.dataframe(df) for an interactive version

            # Store the result in the list to display later (optional)
            all_extracted_data.append(analysis_result)

        # Optionally, display all results in one table
        if all_extracted_data:
            st.subheader("All Extracted Information (Summary Table)")
            all_data_df = pd.DataFrame(all_extracted_data)
            st.table(all_data_df)  # or st.dataframe(all_data_df) for an interactive version

if __name__ == "__main__":
    main()


