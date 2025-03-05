import json
import pandas as pd
import streamlit as st
import openai
import os

# Set the API key directly on the openai module.
openai.api_key = os.getenv("OPENAI_API_KEY", "")
if not openai.api_key:
    raise ValueError("OpenAI API key not found in environment variables or Streamlit secrets")

# Function to read an Excel file into a DataFrame
def read_excel_file(uploaded_file):
    """
    Reads an Excel file into a pandas DataFrame.
    """
    return pd.read_excel(uploaded_file, engine="openpyxl")


# Function to generate a column mapping using GPT
def gpt_prompt_mapping(master_columns):
    leads_columns = [
        "Title", "First Name", "Middle Name", "Surname", "Gender", "DOB",
        "Address 1", "Address 2", "Address 3", "Address 4",
        "City", "County", "Postcode", "Tel No", "Email Address", "Mobile"
    ]
    
    prompt = f"""You are a data migration assistant with advanced semantic understanding.
I have two datasets:
1. The master dataset has the following columns:
{master_columns}

2. I need to fill in a leads import file that contains the following personal details columns:
{leads_columns}

Please provide a JSON object that maps each column from the leads import file to the best matching column from the master dataset. Use your semantic understanding to match columns even if their names differ (for example, match "Gender" with "Sex" if that is the best fit). If no appropriate master column exists for a given leads import column, assign null.
Do not include any extra explanation; output only valid JSON.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # Use the correct model identifier if needed
            messages=[
                {"role": "system", "content": "You are a helpful data mapping assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0  # Lower temperature for deterministic output
        )
        mapping_json = response.choices[0].message.content.strip()  # Use dot notation
        print("Raw GPT response:", mapping_json)  # Debug print

        # Strip out markdown code fences if present
        if mapping_json.startswith("```json"):
            mapping_json = mapping_json[len("```json"):].strip()
        if mapping_json.endswith("```"):
            mapping_json = mapping_json[:-3].strip()
        
        if not mapping_json:
            raise ValueError("Received an empty response from the GPT API.")
        
        mapping = json.loads(mapping_json)
    except Exception as e:
        raise RuntimeError(f"Error calling GPT-4o API: {e}")
    
    return mapping


# Function to update the leads import file based on mapping
def update_leads_import(master_file, leads_import_file, client_first_name="", client_surname=""):
    master_df = read_excel_file(master_file)
    leads_df_template = read_excel_file(leads_import_file)

    # Generate column mapping using GPT
    mapping = gpt_prompt_mapping(list(master_df.columns))

    # If filtering by a single client, apply the filter
    if client_first_name and client_surname:
        master_first_name_col = mapping.get("First Name")
        master_surname_col = mapping.get("Surname")
        if not master_first_name_col or not master_surname_col:
            raise ValueError("Mapping for 'First Name' or 'Surname' not found in the master file.")
        
        # Normalize user input and dataset values
        df_first_names = master_df[master_first_name_col].astype(str).str.lower().str.strip()
        df_surnames = master_df[master_surname_col].astype(str).str.lower().str.strip()
        user_first = client_first_name.strip().lower()
        user_surname = client_surname.strip().lower()

        print("DEBUG: Unique values in the master file for First Name:", df_first_names.unique())
        print("DEBUG: Unique values in the master file for Surname:", df_surnames.unique())
        print("DEBUG: User input for first name:", repr(user_first))
        print("DEBUG: User input for surname:", repr(user_surname))

        filtered_master_df = master_df[
            (df_first_names == user_first) & (df_surnames == user_surname)
        ]
        if filtered_master_df.empty:
            raise ValueError("No matching client found in the master file.")
        master_df_to_use = filtered_master_df.iloc[[0]]  # Take first match
    else:
        master_df_to_use = master_df

    # Build updated rows for the leads import file based on mapping
    updated_rows = []
    for _, row in master_df_to_use.iterrows():
        new_row = {}
        for col in leads_df_template.columns:
            if col in [
                "Title", "First Name", "Middle Name", "Surname", "Gender", "DOB",
                "Address 1", "Address 2", "Address 3", "Address 4",
                "City", "County", "Postcode", "Tel No", "Email Address", "Mobile"
            ]:
                master_col = mapping.get(col)
                new_row[col] = row.get(master_col, None) if master_col else None
            else:
                new_row[col] = None  # Default for extra columns
        updated_rows.append(new_row)

    updated_leads_df = pd.DataFrame(updated_rows, columns=leads_df_template.columns)
    return updated_leads_df, mapping
