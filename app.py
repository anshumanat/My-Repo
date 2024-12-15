import pickle
import streamlit_authenticator as stauth
from pathlib import Path

# Define user details and passwords
names = ["Prateek Agarwal", "Anubhav"]
usernames = ["Prateek", "Anubhav"]
passwords = ["abc123", "def456"]  # Example plain-text passwords

# Hash the passwords
hashed_passwords = stauth.Hasher(passwords).generate()

# Create a dictionary with usernames and their corresponding hashed passwords
credentials = {
    "usernames": {
        "Prateek": {
            "name": "Prateek Agarwal",
            "password": hashed_passwords[0],
            "email": "prateek@example.com"
        },
        "Anubhav": {
            "name": "Anubhav",
            "password": hashed_passwords[1],
            "email": "anubhav@example.com"
        }
    }
}

# Save the dictionary to a pickle file
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(credentials, file)

print("Hashed passwords and user details saved to 'hashed_pw.pkl'.")
