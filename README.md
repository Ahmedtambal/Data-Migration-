# IO Migrator

This project provides a Streamlit application to handle data migration between a **master Excel file** and a **leads import Excel file**. The app uses GPT-based mapping (via `openai`) to match personal data fields, such as "First Name" or "DOB," even when the master file has different column names.

## Features

- Upload two Excel files (master file and leads import file)
- Optionally filter by a single client (First Name + Surname)
- GPT-based semantic column mapping
- Download updated leads import data as CSV

## Installation

1. **Clone** this repository:
   ```bash
   git clone https://github.com/your-username/io-migrator.git
   cd io-migrator
