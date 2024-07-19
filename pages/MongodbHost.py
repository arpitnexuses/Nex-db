
import streamlit as st
from pymongo import MongoClient, errors
import gridfs
from dotenv import load_dotenv
import os
import uuid

st.set_page_config(layout='wide', initial_sidebar_state='expanded')
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Load environment variables
load_dotenv()

# MongoDB connection details
mongo_uri = ("mongodb+srv://nexuses:Nexuses@cluster0.pbrqpu9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db_name = ("Nex-Data")

# Connect to MongoDB
try:
    client = MongoClient(mongo_uri)
    db = client[db_name]
    fs = gridfs.GridFS(db)
except errors.ServerSelectionTimeoutError:
    st.error("Failed to connect to MongoDB")

def main():
    if st.session_state.authenticated:
        st.title("Upload and Get MongoDB File URL")

        uploaded_file = st.file_uploader(
            "Choose a file...",
            type=["jpg", "jpeg", "png", "gif", "mp4", "avi", "mkv", "pdf", "webp"])

        if uploaded_file is not None:
            unique_uuid = str(uuid.uuid4())
            original_name, extension = os.path.splitext(uploaded_file.name)
            original_name = original_name.replace(" ", "_")  # Remove spaces from the file name
            file_name_with_uuid = f"{original_name}_{unique_uuid}{extension}"

            original_name = st.text_input("Enter a file name (without extension):", value=original_name)
            file_name = f"{original_name}_{unique_uuid}{extension}"

            if uploaded_file.type.startswith('image'):
                st.image(uploaded_file, caption="Uploaded Image/Video/PDF.", use_column_width=True)
            elif uploaded_file.type == 'application/pdf':
                st.markdown(f"Uploaded PDF: {file_name}")
            elif uploaded_file.type.startswith('video'):
                st.video(uploaded_file)
            else:
                st.warning("Unsupported file type. Please upload an image, video, or a PDF.")

            if st.button("Get MongoDB File URL"):
                if not original_name:
                    st.warning("Please enter a file name.")
                else:
                    try:
                        file_id = fs.put(uploaded_file, filename=file_name)
                        st.success("File uploaded to MongoDB successfully.")
                        file_url = f"http://127.0.0.1:5000/file/{file_id}"
                        st.write("MongoDB File URL:")
                        st.write(file_url)
                    except Exception as e:
                        st.error(f"Error uploading to MongoDB: {str(e)}")

    else:
        st.error("Please login to access the dashboard.")

if __name__ == "__main__":
    main()
