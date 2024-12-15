import streamlit as st
import streamlit_authenticator as stauth
from dotenv import load_dotenv
import os
import pandas as pd
from PIL import Image
import google.generativeai as genai
from io import BytesIO

# Load environment variables
load_dotenv()

# Fetch the Gemini API key from Streamlit secrets
api_key = st.secrets["GEMINI"]["API_KEY"]

if not api_key:
    st.error("API Key is missing! Please set the GEMINI_API_KEY in Streamlit Secrets.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-1.5-pro-001")

# --- Authentication Setup ---
names = ["John Doe", "Jane Smith"]
usernames = ["johndoe", "janesmith"]
passwords = ["password123", "securepassword456"]
hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    names,
    usernames,
    hashed_passwords,
    "cheque_app_cookie",
    "some_random_signature_key",
    cookie_expiry_days=7,
)

# Login widget
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.sidebar.success(f"Welcome {name}!")
    authenticator.logout("Logout", "sidebar")

    # --- Main App: Cheque Information Extraction ---
    st.title("Cheque Information Extraction with Gemini AI")

    st.markdown("""
        **Welcome to the Cheque Information Extraction App!**  
        Upload a cheque image to extract details such as:
        - Payee Name
        - Bank Name
        - Account Number
        - Date
        - Cheque Number
        - Amount

        After extraction, you can download the results as a CSV file.
    """)

    # File uploader
    uploaded_file = st.file_uploader("Upload a cheque image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        # Load and process image
        def load_image(image):
            try:
                return Image.open(image)
            except Exception as e:
                st.error(f"Error loading image: {e}")
                return None

        img = load_image(uploaded_file)

        if img:
            # Prompt for Gemini AI
            prompt = (
                "Analyze this cheque image and extract the Payee Name, Bank Name, Account Number, Date, "
                "Cheque Number, and Amount."
            )

            try:
                result = model.generate_content([img, prompt])

                if result.text:
                    st.subheader("Extracted Information (Text):")
                    st.write(result.text)

                    # Parse extracted text
                    def parse_extracted_info(extracted_text):
                        fields = {
                            "Payee Name": None,
                            "Bank Name": None,
                            "Account Number": None,
                            "Cheque Number": None,
                            "Amount": None,
                            "Date": None,
                        }
                        lines = extracted_text.split("\n")
                        for line in lines:
                            for field in fields.keys():
                                if field in line:
                                    fields[field] = line.split(":")[-1].strip()
                        return fields

                    extracted_info = parse_extracted_info(result.text)

                    # Display parsed data as a table
                    st.subheader("Extracted Information (Table):")
                    st.table(extracted_info)

                    # Convert extracted info to a Pandas DataFrame
                    df = pd.DataFrame([extracted_info])

                    # Download as CSV
                    def convert_df_to_csv(df):
                        csv_buffer = BytesIO()
                        df.to_csv(csv_buffer, index=False)
                        csv_buffer.seek(0)
                        return csv_buffer.getvalue()

                    csv_data = convert_df_to_csv(df)

                    st.subheader("Download Extracted Information:")
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name="cheque_extracted_info.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("No valid content returned from the model. Please try again.")
            except Exception as e:
                st.error(f"Error generating content: {e}")
        else:
            st.error("Failed to load the image.")
    else:
        st.info("Please upload a cheque image to begin the analysis.")

elif authentication_status == False:
    st.error("Invalid username or password")
else:
    st.warning("Please log in to access the app.")
