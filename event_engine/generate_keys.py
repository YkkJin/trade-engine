import pickle
from pathlib import Path

import streamlit_authenticator as stauth

names = ["chou xiang luo", "cosmo"]
usernames = ["chouxiangluo", "rmiller"]
passwords = ["chelungungun123", "cosmo"]

hashed_passwords = stauth.Hasher(passwords).generate()
print(hashed_passwords)
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)
