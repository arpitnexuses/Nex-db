import streamlit as st
import pandas as pd
import smtplib
from email.message import EmailMessage
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import base64

# Load environment variables from .env file
load_dotenv()

# Connect to MongoDB using the provided URI from .env
mongodb_uri = os.getenv("MONGODB_URI")
if mongodb_uri is None:
    st.error("MongoDB URI not found in the .env file.")
else:
    client = MongoClient(mongodb_uri)
    db = client["Nex-Whole-Data"]
    collection = db["Whole"]

    st.set_page_config(layout='wide', initial_sidebar_state='expanded')
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Function to send personalized email with "Reply-To" header and progress bar
    def send_bulk_emails(smtp_server, sender_email, password, contacts, subject, body):
        if 'Email' not in contacts.columns or 'First Name' not in contacts.columns:
            st.error("Error: 'Email' or 'First Name' column not found in the CSV file.")
            return

        with smtplib.SMTP(smtp_server, 587) as server:
            server.starttls()
            server.login(sender_email, password)

            total_emails = len(contacts)
            progress_bar = st.progress(0)

            for idx, contact in contacts.iterrows():
                receiver_email = contact['Email']
                first_name = contact['First Name']

                personalized_body = body.replace('{{first_name}}', first_name)

                message = EmailMessage()
                message['From'] = sender_email
                message['To'] = receiver_email
                message['Subject'] = subject.replace('{{first_name}}', first_name)
                message.set_content(personalized_body, subtype='html')

                message['Reply-To'] = sender_email

                server.send_message(message)

                progress_bar.progress((idx + 1) / total_emails)

    # Function to store contacts in MongoDB
    def store_contacts_in_mongodb(contacts):
        client = MongoClient(mongodb_uri)
        db = client["bulk_email_db"]
        collection = db["contacts"]
        collection.insert_many(contacts.to_dict(orient="records"))

    # Function to verify SMTP server
    def verify_smtp_server(smtp_server, sender_email, password):
        try:
            with smtplib.SMTP(smtp_server, 587) as server:
                server.starttls()
                server.login(sender_email, password)
                return True
        except Exception as e:
            return False

    # Streamlit app
    def main():
        # Your existing main function code...

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if __name__ == "__main__":
        main()

    # Close MongoDB connection when done
    client.close()
