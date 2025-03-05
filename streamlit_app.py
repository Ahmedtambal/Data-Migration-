import streamlit as st
import pandas as pd
from logic import update_leads_import

# Configure the Streamlit page with a cool green theme
st.set_page_config(page_title="Data Migration App", layout="wide")
st.markdown(
    """
    <style>
    body {
        background-color: #e8f5e9;
    }
    .stApp {
        color: #1b5e20;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }
    h1, h2 {
        color: #2e7d32;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# App title and description
st.title("Data Migration Tool")
st.write(
    """
    This app helps you migrate data from a master file to a leads import file.
    You can upload the master file and the leads import file, and the app will
    update the leads import file with the latest data.
    """
)
# File upload section for the master file and the leads import file
st.header("Upload Files")
master_file = st.file_uploader("Upload Master File (Excel)", type=["xlsx", "xls"])
leads_import_file = st.file_uploader("Upload Leads Import File (Excel)", type=["xlsx", "xls"])

# Optional: Process a single client by providing unique first name and surname
st.header("Optional: Process a Single Client")
client_first_name = st.text_input("Client First Name (leave empty to process all clients)")
client_surname = st.text_input("Client Surname (leave empty to process all clients)")

# When both files are uploaded, enable the migration button
if master_file and leads_import_file:
    if st.button("Migrate Data"):
        try:
            updated_df, mapping = update_leads_import(master_file, leads_import_file, client_first_name, client_surname)
            st.success("Data migration complete!")
            st.write("**Column Mapping Used:**", mapping)
            st.write("Preview of updated data:")
            st.dataframe(updated_df.head())

            # Provide a download button for the updated leads import data as a CSV file
            csv_data = updated_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Updated Leads Import as CSV",
                data=csv_data,
                file_name="updated_leads_import.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"An error occurred during data migration: {e}")
