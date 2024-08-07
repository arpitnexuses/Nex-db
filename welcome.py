import streamlit as st
import pymongo
from dotenv import load_dotenv
import os
import certifi
import uuid
import gridfs
from pymongo import MongoClient, errors
load_dotenv()  # Load variables from .env file

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

# Connect to MongoDB using environment variable
mongodb_uri = os.getenv("MONGODB_URI")
client = pymongo.MongoClient(mongodb_uri,tlsCAFile=certifi.where())
db = client["mydatabase"]
users_col = db["users"]


# Initialize the 'authenticated' attribute
if "authenticated" not in st.session_state:
  st.session_state['authenticated'] = False

with open('styles.css') as f:
  st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
# Connect to MongoDB


# with open('styles.css') as f:
#     st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

CSS = """
h1 {
    color: #FFFFFF;
    font-size: 48px;
    font-weight: bold;
    text-align: center;
    margin-top: 100px;
}
"""


# Create login page
def login():
  st.write("<h1>Login</h1>", unsafe_allow_html=True)
  username = st.text_input("Username")
  password = st.text_input("Password", type="password")
  if st.button("Login"):
    user = users_col.find_one({"username": username, "password": password})
    if user:
      st.session_state.authenticated = True
      st.experimental_rerun()  # Refresh the app to redirect to dashboard
    else:
      st.error("Incorrect username or password")


css = """
<style>
    .login-container {
        padding: 20px;
        border: 1px solid #ccc;
        border-radius: 10px;
        background-color: #f7f7f7;
        max-width: 400px;
        margin: auto;
        margin-top: 40px;
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)


# Create register page
def register():
  if st.session_state.is_admin:
    if st.session_state.show_register_form:
      st.write("Click the button below to register a new user.")
      if st.button("Register a new user"):
        st.session_state.show_register_form = True
    else:
      st.write("Please fill out the form to register a new user:")
      username = st.text_input("Username")
      password = st.text_input("Password", type="password")
      email = st.text_input("Email")
      if st.button("Register"):
        user = {"username": username, "password": password, "email": email}
        users_col.insert_one(user)
        st.session_state.show_register_form = False
        st.success("User registered successfully!")
  else:
    st.write("You are not authorized to register a new user.")
    st.experimental_rerun()  # Refresh the app to redirect to dashboard


# Create dashboard page
def dashboard():
  if st.session_state.authenticated:
    with st.spinner("Loading..."):
      #
      st.title("Welcome")
  else:
    st.write("Please login to access the dashboard.")
    login()


def sidebar():
  # Add your sidebar elements here
  pass


is_admin = False  # Set to True if user is an admin

if 'authenticated' in st.session_state and st.session_state['authenticated']:

  if is_admin:
    if st.button("Register"):
      register()
  dashboard()
else:
  login()

# CSS styling
st.markdown("""
    <style>
    

    .login-container {
        background-color: #45b6fe;
        border-radius: 8px;
        box-shadow: 0 2px 6px 0 rgba(0, 0, 0, 0.2);
        padding: 2em;
        max-width: 500px;
        margin: 0 auto;
        margin-top: 2em;
    }
    .stButton button {
        background-color: #45b6fe;
        color: #ffffff;
        border-radius: 4px;
        padding: 0.5em 1.5em;
        border: none;
    }
    .stButton button:hover {
        background-color: #1f8bf8;
    }
    
    </style>
    """,
            unsafe_allow_html=True)
