import streamlit as st
import pandas as pd
import base64
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# MongoDB connection
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client["Nex-Data"]
collection = db["Data"]

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def load_data(collection):
    data = list(collection.find({}))
    df = pd.DataFrame(data)
    return df


def main():
    if st.session_state.authenticated:
        st.title('Data Filtration')
        with st.spinner("Loading..."):
            # Load the data
            df = load_data(collection)
            st.dataframe(df)

            # Apply filters to the data
            column_names = st.multiselect("Select the columns to filter by:", df.columns)

            values = st.text_input("Enter values to filter by (comma separated):")
            values = values.split(",")

            # Remove empty values and spaces
            values = [val.strip() for val in values if val.strip()]

            # Create a boolean mask to filter the dataframe by the entered values
            if values:
                mask = None
                for column_name in column_names:
                    for val in values:
                        if mask is None:
                            mask = df[column_name].str.lower().str.contains(val, na=False)
                        else:
                            mask = mask | df[column_name].str.contains(val, na=False)

                filtered_df = df[mask]
                if filtered_df.empty:
                    st.warning("No data found that matches the entered values.")
                else:
                    # Show the filtered data
                    st.dataframe(filtered_df)
                    st.write("Number of rows in the filtered data:", filtered_df.shape[0])

                    # Download the filtered data
                    if st.button('Process filtered data'):
                        st.write("Downloading...")
                        csv = filtered_df.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        st.markdown(
                            f'<a href="data:file/csv;base64,{b64}" download="filtered_data.csv">Click here to Download</a>',
                            unsafe_allow_html=True)
                        st.balloons()
            else:
                st.warning("Please enter values to filter by.")
    else:
        st.error("Please login to access the dashboard.")


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if __name__ == '__main__':
    main()
