import streamlit as st
import pandas as pd
from pymongo import MongoClient
import uuid
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB connection
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client["Test-trial"]
collection = db["trial"]

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def upload_to_mongodb(file):
    data = pd.read_csv(file)
    data["_id"] = [str(uuid.uuid4()) for _ in range(len(data))]  # add unique _id field
    result = collection.insert_many(data.to_dict("records"))
    return result

def main():
    if st.session_state.authenticated:
        st.title("Upload Data to Database")

        # File upload
        file = st.file_uploader("Upload CSV", type=["csv"])

        # Check if file is uploaded
        if file is not None:
            # Upload the file to MongoDB
            result = upload_to_mongodb(file)

            # Print success message and total number of documents in collection
            st.balloons()
            st.write(f"CSV file uploaded to MongoDB. Total documents in collection: {collection.count_documents({})}")

        # Add a button to refresh the page and upload another CSV file

    else:
        st.error("Please login to access the dashboard.")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    
if __name__ == '__main__':
    main()
