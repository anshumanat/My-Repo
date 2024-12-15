# Import necessary modules
import bcrypt
import re
from datetime import datetime, timedelta
import secrets
import streamlit as st
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["auth_db"]
users_collection = db["users"]

# Helper functions for authentication
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def verify_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

def check_user_exists(email):
    user = users_collection.find_one({"email": email})
    return user is not None

def add_user(email, password):
    hashed_password = hash_password(password)
    user = {
        "email": email,
        "password": hashed_password,
        "reset_token": None,
        "reset_token_expiry": None
    }
    users_collection.insert_one(user)

def verify_user(email, password):
    user = users_collection.find_one({"email": email})
    if user and verify_password(user["password"], password):
        return True
    return False

def generate_reset_token(email):
    token = secrets.token_urlsafe(16)
    expiration_time = datetime.utcnow() + timedelta(minutes=30)  # Token expires in 30 minutes
    users_collection.update_one({"email": email}, {
        "$set": {
            "reset_token": token,
            "reset_token_expiry": expiration_time
        }
    })
    return token

def validate_reset_token(email, token):
    user = users_collection.find_one({"email": email})
    if user and user.get("reset_token") == token:
        if datetime.utcnow() < user["reset_token_expiry"]:
            return True
    return False

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Initialize session state variables
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def go_to_page(page_name):
    st.session_state.current_page = page_name

def update_title(title):
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)

# Main application logic
if st.session_state.current_page == "home":
    update_title("Gemini - User Authentication")

    # Sidebar for navigation
    option = st.sidebar.selectbox("Choose an action", ("Sign Up", "Log In"))

    # Sign Up
    if option == "Sign Up":
        st.subheader("Create an Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up"):
            if email and password:
                if not is_valid_email(email):
                    st.error("Invalid email address.")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif check_user_exists(email):
                    st.error("Email already registered.")
                else:
                    add_user(email, password)
                    st.success("Account created successfully!")
            else:
                st.error("Please fill all fields.")

    # Log In
    elif option == "Log In":
        st.subheader("Log In")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Log In"):
            if email and password:
                if verify_user(email, password):
                    st.success("Login successful!")
                    st.session_state.logged_in = True
                    st.session_state.email = email
                    go_to_page("dashboard")  # Redirect to dashboard after login
                else:
                    st.error("Invalid email or password.")
            else:
                st.error("Please fill in all fields.")

        # Forgot Password
        if st.button("Forgot Password?"):
            st.subheader("Reset Password")

            email_for_reset = st.text_input("Enter your email to request reset token")

            if st.button("Request Reset Link"):
                if email_for_reset:
                    if check_user_exists(email_for_reset):
                        token = generate_reset_token(email_for_reset)
                        st.success(f"Reset token generated! (Token: {token})")
                        st.info("Use this token to reset your password.")
                    else:
                        st.error("Email not found.")
                else:
                    st.error("Please enter your email.")

            token = st.text_input("Enter reset token")
            new_password = st.text_input("Enter new password", type="password")

            if st.button("Reset Password"):
                if email_for_reset and token and new_password:
                    if validate_reset_token(email_for_reset, token):
                        hashed_password = hash_password(new_password)
                        users_collection.update_one({"email": email_for_reset}, {
                            "$set": {
                                "password": hashed_password,
                                "reset_token": None,
                                "reset_token_expiry": None
                            }
                        })
                        st.success("Password reset successfully!")
                    else:
                        st.error("Invalid or expired token.")
                else:
                    st.error("Please fill in all fields.")

# Dashboard Page (Post-login)
elif st.session_state.current_page == "dashboard":
    update_title("Dashboard")
    st.success(f"Welcome, {st.session_state.email}!")
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.email = None
        go_to_page("home")
