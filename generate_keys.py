import pickle
from pathlib import Path
import streamlit_authenticator as stauth

# User details
names = ["Prateek Agarwal", "Anubhav"]
usernames = ["Prateek", "Anubhav"]
passwords = ["abc123", "def456"]  

hashed_passwords = stauth.Hasher(passwords).generate()

# Define the path for the hashed_pw.pkl file
file_path = Path(__file__).parent / "hashed_pw.pkl"  # Use .parent to get the current directory

# Ensure that the directory exists
file_path.parent.mkdir(parents=True, exist_ok=True)

# Write the hashed passwords to the file
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)

print("Hashed passwords saved to 'hashed_pw.pkl'.")
