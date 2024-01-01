import streamlit as st
from pymongo import MongoClient
import boto3
from botocore.exceptions import NoCredentialsError
import mimetypes
from dotenv import load_dotenv
import os

st.set_page_config(layout='wide', initial_sidebar_state='expanded')
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Connect to MongoDB
load_dotenv()


# AWS S3 credentials
aws_access_key = os.getenv("AWS_ACCESS_KEY")
aws_secret_key = os.getenv("AWS_SECRET_KEY")
aws_region = os.getenv("AWS_REGION")
s3_bucket_names = ["cdn-nexlink", "voiceoc-ai", "krvauditing", "krvauditing2", "nex-digm", "blockarmour", "voiceoc2", "voiceoc-ai2", "voiceoc-ai3", "mars-solution", "mars-solution2", "mars-solution3", "mars-solution4", "nexuses", "travvir", "smiforce", "smiforce2", "cystech1", "rsm-saudi", "rsmsaudi2", "rsmsaudi3", "rsmsaudi4", "rsmsaudi5", "zainimedia", "smc-india", "smc-india3", "smc-india4", "smcindia2"]

# Create an S3 client
s3 = boto3.client('s3',
                  aws_access_key_id=aws_access_key,
                  aws_secret_access_key=aws_secret_key,
                  region_name=aws_region)

def get_object_url(file_name, bucket_name):
    try:
        url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{file_name}"
        return url
    except NoCredentialsError:
        return 'AWS credentials not available.'

def main():
    if st.session_state.authenticated:
        st.title("Upload and Get S3 Object URL")

        selected_bucket = st.selectbox("Select a S3 bucket:", s3_bucket_names)

        uploaded_file = st.file_uploader(
            "Choose a file...",
            type=["jpg", "jpeg", "png", "gif", "mp4", "avi", "mkv", "pdf"])

        if uploaded_file is not None:
            file_name = st.text_input(
                "Enter a file name (including extension):",
                value=uploaded_file.name if uploaded_file else '')

            if uploaded_file.type.startswith('image'):
                # Display image
                st.image(uploaded_file,
                         caption="Uploaded Image/Video/PDF.",
                         use_column_width=True)
            elif uploaded_file.type == 'application/pdf':
                # Display a PDF link
                st.markdown(
                    f"Uploaded PDF: [{file_name}]({get_object_url(file_name, selected_bucket)})"
                )
            else:
                st.warning("Unsupported file type. Please upload an image or a PDF.")

            if st.button("Get S3 Object URL"):
                if not file_name:
                    st.warning("Please enter a file name.")
                else:
                    # Upload the file to the selected S3 bucket with appropriate Content-Type
                    try:
                        content_type, _ = mimetypes.guess_type(file_name)
                        s3.upload_fileobj(uploaded_file,
                                          selected_bucket,
                                          file_name,
                                          ExtraArgs={'ContentType': content_type})
                        st.success("File uploaded to S3 successfully.")
                    except Exception as e:
                        st.error(f"Error uploading to S3: {str(e)}")

                    # Get the S3 object URL
                    object_url = get_object_url(file_name, selected_bucket)
                    st.write("S3 Object URL:")
                    st.write(object_url)

    else:
        st.error("Please login to access the dashboard.")


if __name__ == "__main__":
    main()
