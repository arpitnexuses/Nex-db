import streamlit as st
import pandas as pd
from pymongo import MongoClient
import io
import base64
from dotenv import load_dotenv


st.set_page_config(layout='wide', initial_sidebar_state='expanded')
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
# Connect to MongoDB

load_dotenv()

# MongoDB connection
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client["Nex-Whole-Data"]
collection = db["Whole"]

def process_file(file):
    try:
        # Read the CSV file into a pandas DataFrame with utf-8 encoding
        df = pd.read_csv(file, encoding='utf-8')
    except UnicodeDecodeError:
        # Read the CSV file into a pandas DataFrame with ISO-8859-1 encoding
        df = pd.read_csv(file, encoding='ISO-8859-1')
    
    # Check the email column against the MongoDB data
    emails = df['email'].tolist()
    email_set = set(emails)
    db_emails = set(collection.distinct('email'))
    existing_emails = email_set.intersection(db_emails)
    existence = ['exist' if email in existing_emails else 'not exist' for email in emails]
    
    # Update the DataFrame with the result
    df['Existence'] = existence
    
    # Update the DataFrame with colored backgrounds based on the result
    styles = []
    for r in existence:
        if r == "exist":
            styles.append('background-color: #FFC7CE')
        else:
            styles.append('background-color: #C6EFCE')
    df = df.style.apply(lambda x: styles)
    
    # Return the updated DataFrame to be displayed
    return df

def main():
    if st.session_state.authenticated:
        st.title("Check if Email Exists")
        st.write("Please upload a CSV file to check email against the database.")
        
        # File upload
        file = st.file_uploader("Upload CSV", type=["csv"])
        
        # Check if file is uploaded
        if file is not None:
            # Process the uploaded file
            df = process_file(file)
            
            # Display the updated DataFrame
            st.write("Updated Data")
            st.dataframe(df)
            st.balloons()
            # Download button
            st.markdown("Download Result")
            st.write("Click below to download the updated file.")

            # Convert the DataFrame to an Excel file
            output = io.BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, index=False)
            writer.save()
            output.seek(0)

            # Generate a download link
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(output.read()).decode()}">Download</a>'
            st.markdown(href, unsafe_allow_html=True)
    else:
        st.error("Please login to access the dashboard.")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if __name__ == '__main__':
    main()
