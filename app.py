import streamlit as st
import os
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai  # Correct import for Google Gemini API

# Load environment variables from the .env file
load_dotenv()

# Fetch the Gemini API key from Streamlit secrets
api_key = st.secrets["GEMINI"]["API_KEY"]

# Ensure the API key is loaded correctly
if not api_key:
    st.error("API Key is missing! Please set the GEMINI_API_KEY in Streamlit Secrets.")
else:
    # Configure the Gemini API with the retrieved key
    genai.configure(api_key=api_key)

    # Initialize the Gemini model (update the model name if necessary)
    model = genai.GenerativeModel('models/gemini-1.5-pro-001')

    # Function to load and process images
    def load_image(image):
        try:
            return Image.open(image)
        except Exception as e:
            st.error(f"Error loading image: {e}")
            return None

    # Function to parse extracted text into a structured format (like a dictionary)
    def parse_extracted_info(extracted_text):
        extracted_info = {
            "Payee Name": None,
            "Bank Name": None,
            "Account Number": None,
            "Cheque Number": None,
            "Amount": None,
            "Date": None
        }

        lines = extracted_text.split("\n")
        for line in lines:
            if "Payee" in line:
                extracted_info["Payee Name"] = line.split(":")[-1].strip()
            elif "Bank" in line:
                extracted_info["Bank Name"] = line.split(":")[-1].strip()
            elif "Account Number" in line:
                extracted_info["Account Number"] = line.split(":")[-1].strip()
            elif "Cheque Number" in line:
                extracted_info["Cheque Number"] = line.split(":")[-1].strip()
            elif "Amount" in line:
                extracted_info["Amount"] = line.split(":")[-1].strip()
            elif "Date" in line:
                extracted_info["Date"] = line.split(":")[-1].strip()

        return extracted_info

    # Streamlit app UI
    st.title("Checkmate: Cheque Information Extraction with Gemini AI")

    # Instructions and welcome message right under the title
    st.markdown("""
    **Welcome to the Checkmate Cheque Information Extraction App!**  
    This app uses **Gemini AI** to analyze the image of a cheque and extract important information such as:

    - Payee Name
    - Bank Name
    - Account Number
    - Cheque Number
    - Amount
    - Date
    - And other relevant details from the cheque image.

    **How to Use**:
    1. Upload an image of a cheque.
    2. The app will analyze the image and display the extracted information on the screen.
    3. You can then view the information in the results section.

    **Supported File Types**: JPG, JPEG, PNG.
    """)

    # File uploader widget for the user to upload an image
    uploaded_file = st.file_uploader("Choose a cheque image...", type=["jpg", "jpeg", "png"])

    # Check if the file is uploaded
    if uploaded_file is not None:
        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        # Load the image
        img = load_image(uploaded_file)

        # Check if the image is loaded successfully
        if img:
            # Define the prompt for Gemini AI
            prompt = (
                "Extract the Payee Name, Bank Name, Account Number, Date, Cheque Number, and Amount from this cheque image."
            )

            # Generate response from Gemini AI
            try:
                result = model.generate_content([img, prompt])

                # Print the result to check the structure (debugging purpose)
                st.write("Full Response from Gemini:")
                st.json(result)

                # Assuming the correct way to access the content after inspecting the response:
                # We will now handle the response content based on the structure.

                # Check if result.candidates contains any response
                if result.candidates:
                    # Instead of using result.candidates[0].content["parts"][0].text
                    # Let's explore the structure of result.candidates[0].content
                    # You need to print the content to verify the correct way to access it
                    content = result.candidates[0].content  # Try printing this directly

                    st.write("Content object:", content)  # Print the content to inspect

                    # Try accessing the text field within the content object, if possible
                    if hasattr(content, 'text'):
                        content_text = content.text  # Accessing the text if it's an attribute
                    else:
                        # Handle alternative structure
                        content_text = "Content text is unavailable."

                    # Display the extracted information as text
                    st.subheader("Extracted Information (Text):")
                    st.write(content_text)

                    # Parse the extracted text into a structured format (dictionary)
                    extracted_info = parse_extracted_info(content_text)

                    # Display the extracted information as a table
                    st.subheader("Extracted Information (Table):")
                    st.table(extracted_info)

                else:
                    st.warning("No content returned. Please try again with a different image.")

            except Exception as e:
                st.error(f"Error generating content: {e}")
        else:
            st.error("Failed to load the image. Please try uploading again.")

    else:
        st.info("Please upload a cheque image to begin the analysis.")
