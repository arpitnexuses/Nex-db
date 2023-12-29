import streamlit as st
import pymongo
from dotenv import load_dotenv
import os
import certifi


load_dotenv()  # Load variables from .env file

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

# Connect to MongoDB using environment variable
mongodb_uri = os.getenv("MONGODB_URI")

try:
    client = pymongo.MongoClient(mongodb_uri, tlsCAFile=certifi.where())
    db = client["mydatabase"]
    users_col = db["users"]
except pymongo.errors.ConnectionFailure as e:
    st.error(f"Error connecting to MongoDB: {e}")
    st.stop()  # Stop execution to avoid further issues

# Initialize the 'authenticated' attribute
if "authenticated" not in st.session_state:
    st.session_state['authenticated'] = False

# Load external CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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
""", unsafe_allow_html=True)

# Create login page
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            user = users_col.find_one({"username": username, "password": password})
            if user:
                st.session_state.authenticated = True
                st.experimental_rerun()  # Refresh the app to redirect to dashboard
            else:
                st.error("Incorrect username or password")
        except pymongo.errors.PyMongoError as e:
            st.error(f"Error querying MongoDB: {e}")

# Create register page
def register():
    if st.session_state.is_admin:
        st.write("Click the button below to register a new user.")
        if st.button("Register a new user"):
            st.session_state.show_register_form = True
    else:
        st.write("Please fill out the form to register a new user:")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        email = st.text_input("Email")
        if st.button("Register"):
            try:
                user = {"username": username, "password": password, "email": email}
                users_col.insert_one(user)
                st.session_state.show_register_form = False
                st.success("User registered successfully!")
            except pymongo.errors.PyMongoError as e:
                st.error(f"Error inserting into MongoDB: {e}")

# Create dashboard page
def dashboard():
    if st.session_state.authenticated:
        st.title("Welcome")
    else:
        st.write("Please login to access the dashboard.")
        login()

is_admin = False  # Set to True if the user is an admin

if 'authenticated' in st.session_state and st.session_state['authenticated']:
    if is_admin:
        if st.button("Register"):
            register()
    dashboard()
else:
    login()
