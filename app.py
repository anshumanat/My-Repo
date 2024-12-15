import streamlit as st
import bcrypt
import pandas as pd
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
import os
from io import BytesIO
from streamlit_authenticator import Authenticate


# --- Load Environment Variables ---
load_dotenv()

# Fetch Gemini API key from secrets or environment variables
api_key = st.secrets.get("GEMINI", {}).get("API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API Key is missing! Please set the GEMINI_API_KEY in Streamlit Secrets or .env file.")
else:
    # Configure Gemini API
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-1.5-pro-001")

# --- Authentication Setup ---
# Define credentials
names = ["John Doe", "Jane Smith"]
usernames = ["johndoe", "janesmith"]
passwords = ["password123", "securepassword456"]

# Hash passwords manually using bcrypt
def hash_passwords(passwords):
    return [bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') for p in passwords]

# Hash the passwords
hashed_passwords = hash_passwords(passwords)

# Initialize the authenticator
from streamlit_authenticator import Authenticate
authenticator = Authenticate(
    names=names,
    usernames=usernames,
    passwords=hashed_passwords,
    cookie_name="cheque_app_cookie",
    key="some_random_signature_key",
    cookie_expiry_days=7,
)

# --- Login/Logout ---
name, authentication_status, username = authenticator.login("Login", "main")

# --- Admin Access ---
admin_password = st.secrets["general"]["password"]  # Fetch admin password from secrets

# Function to check admin password
def check_admin_password():
    input_password = st.text_input("Enter admin password:", type="password")
    if input_password == admin_password:
        st.session_state["is_admin"] = True
        st.success("Admin access granted!")
    else:
        st.session_state["is_admin"] = False
        st.warning("Incorrect password. Admin access denied.")

# --- Admin Section ---
if authentication_status:
    st.sidebar.success(f"Welcome {name}!")
    authenticator.logout("Logout", "sidebar")

    # Admin access (only for authenticated users)
    if st.session_state.get("is_admin", False):
        st.title("Admin Panel")
        st.markdown("Welcome to the Admin Panel! You can manage or view admin-level functionality here.")
        # You can add admin functionality here, e.g., data management, system settings, etc.
    else:
        # Ask for admin password only if the user is logged in
        check_admin_password()

    # --- Main App ---
    st.title("Cheque Information Extraction with Gemini AI")

    st.markdown("""**Upload a cheque image to extract key details.**
    This tool uses AI to extract:
    - Payee Name
    - Bank Name
    - Account Number
    - Date
    - Cheque Number
    - Amount  

    After extraction, download the data as a CSV file.""")

    # File uploader
    uploaded_file = st.file_uploader("Upload a cheque image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        # Display uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        # Load image function
        def load_image(image):
            try:
                return Image.open(image)
            except Exception as e:
                st.error(f"Error loading image: {e}")
                return None

        img = load_image(uploaded_file)

        if img:
            # Define the prompt for Gemini AI
            prompt = (
                "Analyze this cheque image and extract the Payee Name, Bank Name, Account Number, "
                "Date, Cheque Number, and Amount."
            )

            # Call Gemini AI
            try:
                result = model.generate_content([img, prompt])

                if result.text:
                    # Display raw extracted text
                    st.subheader("Extracted Information (Text):")
                    st.write(result.text)

                    # Parse extracted text into structured data
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

                    # Convert to DataFrame
                    df = pd.DataFrame([extracted_info])

                    # Display structured data
                    st.subheader("Extracted Information (Table):")
                    st.table(df)

                    # CSV download functionality
                    def convert_df_to_csv(df):
                        csv_buffer = BytesIO()
                        df.to_csv(csv_buffer, index=False)
                        csv_buffer.seek(0)
                        return csv_buffer.getvalue()

                    csv_data = convert_df_to_csv(df)

                    # Add download button
                    st.subheader("Download Extracted Information:")
                    st.download_button(
                        label="Download as CSV",
                        data=csv_data,
                        file_name="cheque_extracted_info.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("The AI did not return any content. Please try again.")
            except Exception as e:
                st.error(f"Error generating content: {e}")
        else:
            st.error("Failed to load the image. Please try again.")
    else:
        st.info("Please upload a cheque image to begin the analysis.")

elif authentication_status == False:
    st.error("Invalid username or password")
else:
    st.warning("Please log in to access the app.")
