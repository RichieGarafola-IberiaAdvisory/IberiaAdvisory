import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO
import base64
from openpyxl import Workbook
import pyxlsb


# Set the page configuration for the Streamlit application, including the title and icon.
st.set_page_config(
    page_title="Iberia Advisory Invoice Review",
    page_icon="📊",
    layout="wide"
)

# Display the Iberia Advisory image on the Streamlit application.
st.image("./Images/iberia-logo.png")

################
# AUTHENICATION
################

# Define a function check_password() that handles user authentication.
def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True
    
# Check the user password using the check_password() function and sets the is_logged_in flag to True if the password is correct.
if check_password():
    is_logged_in = True
    
    # Define the Streamlit app
    st.title("Invoice Data Analysis")

    # Initialize session state
    if 'raw_invoice' not in st.session_state:
        st.session_state.raw_invoice = None
    if 'wsr_consolidated' not in st.session_state:
        st.session_state.wsr_consolidated = None
    if 'onboarding_tracker' not in st.session_state:
        st.session_state.onboarding_tracker = None
    if 'raw_invoice_copy' not in st.session_state:
        st.session_state.raw_invoice_copy = None
    if 'wsr_consolidated_copy' not in st.session_state:
        st.session_state.wsr_consolidated_copy = None
    if 'date_ranges' not in st.session_state:
        st.session_state.date_ranges = {}
    if 'submit_button_pressed' not in st.session_state:
        st.session_state.submit_button_pressed = False

    # Upload files in Streamlit
    uploaded_raw_invoice = st.file_uploader("Upload Raw Invoice Excel File", type=["xlsx"])
    uploaded_wsr_consolidated = st.file_uploader("Upload WSR Consolidated Excel File", type=["xlsb"])
    uploaded_onboarding_tracker = st.file_uploader("Upload Onboarding Tracker Excel File", type=["xlsx"])

    # Check if files are uploaded and load data if necessary
    try:
        if uploaded_raw_invoice:
            st.session_state.raw_invoice = pd.read_excel(uploaded_raw_invoice, skiprows=1).drop("Unnamed: 0", axis=1)
            st.session_state.raw_invoice["Name"] = st.session_state.raw_invoice["Name"].str.replace(r' [A-Z]\b', '', regex=True)
            st.session_state.raw_invoice = st.session_state.raw_invoice[st.session_state.raw_invoice["Name"] != "Grand Total"]

        if uploaded_wsr_consolidated:
            st.session_state.wsr_consolidated = pd.read_excel(uploaded_wsr_consolidated, sheet_name="Invoice Review", skiprows=5)
            st.session_state.wsr_consolidated['Reporting Week (MM/DD/YYYY)'] = pd.to_datetime(st.session_state.wsr_consolidated['Reporting Week (MM/DD/YYYY)'], unit='D', origin='1899-12-30')
            st.session_state.wsr_consolidated["Contractor (Last Name, First Name)2"] = st.session_state.wsr_consolidated["Contractor (Last Name, First Name)2"].str.replace(r' [A-Z]\b', '', regex=True)
            st.session_state.wsr_consolidated = st.session_state.wsr_consolidated.ffill()
            st.session_state.wsr_consolidated = st.session_state.wsr_consolidated[st.session_state.wsr_consolidated["Vendor Name"] != "Grand Total"]

        if uploaded_onboarding_tracker:
            st.session_state.onboarding_tracker = pd.read_excel(uploaded_onboarding_tracker, sheet_name="Master List")
            st.session_state.onboarding_tracker["Candidate Name"] = st.session_state.onboarding_tracker["Candidate Name"].str.replace(r' [A-Z]\b', '', regex=True)
    except Exception as e:
        st.warning("An error occurred while processing the uploaded files. Please make sure you've uploaded the correct files.")

    # Display the initial DataFrame (First)
    if st.session_state.raw_invoice is not None:
        st.write(st.session_state.raw_invoice)


    # Get unique combinations of Name and Reporting Week if 'raw_invoice' is available
    if st.session_state.raw_invoice is not None:
        unique_combinations = st.session_state.raw_invoice[['Name', 'Effective Bill Date']].drop_duplicates()

        for index, row in unique_combinations.iterrows():
            name = row['Name']
            effective_date = row['Effective Bill Date']

            # Sidebar for user input
            st.sidebar.header(f"User Input for {name} ({effective_date})")
            start_date_input = st.sidebar.text_input(f"Enter Start Date (MM/DD/YYYY) for {name} ({effective_date}):", key=f"{name}_{effective_date}_start_date")
            end_date_input = st.sidebar.text_input(f"Enter End Date (MM/DD/YYYY) for {name} ({effective_date}):", key=f"{name}_{effective_date}_end_date")

            if start_date_input and end_date_input:
                st.session_state.date_ranges[(name, effective_date)] = (start_date_input, end_date_input)
    else:
        st.warning("Please upload the 'raw_invoice' Excel file before continuing.")





    # "Submit All Date Ranges" button
    if st.sidebar.button("Submit All Date Ranges"):
        st.session_state.submit_button_pressed = True

    # Perform calculations when the button is pressed
    if st.session_state.submit_button_pressed:
        if st.session_state.raw_invoice_copy is None:
            st.session_state.raw_invoice_copy = st.session_state.raw_invoice.copy()
            st.session_state.wsr_consolidated_copy = st.session_state.wsr_consolidated.copy()

        for (name, effective_date), (start_date, end_date) in st.session_state.date_ranges.items():
            start_date = pd.to_datetime(start_date, format='%m/%d/%Y')
            end_date = pd.to_datetime(end_date, format='%m/%d/%Y')

            filtered_wsr = st.session_state.wsr_consolidated_copy[st.session_state.wsr_consolidated_copy['Contractor (Last Name, First Name)2'] == name]
            filtered_wsr = filtered_wsr[(filtered_wsr['Reporting Week (MM/DD/YYYY)'] >= start_date) &
                                        (filtered_wsr['Reporting Week (MM/DD/YYYY)'] <= end_date)]

            total_hours = filtered_wsr['Sum of Time Spent (Hours) '].sum()
            contract_rate = filtered_wsr['Sum of Cost Calc'].sum() / total_hours
            contract_rate = round(contract_rate, 2)
            cost_check = contract_rate * total_hours

            st.session_state.raw_invoice_copy.loc[st.session_state.raw_invoice_copy['Name'] == name, 'WSR Hours'] = total_hours
            st.session_state.raw_invoice_copy.loc[st.session_state.raw_invoice_copy['Name'] == name, 'Contract Rate'] = contract_rate
            st.session_state.raw_invoice_copy.loc[st.session_state.raw_invoice_copy['Name'] == name, 'Cost Check'] = cost_check

        # Display the updated DataFrame in Streamlit
        st.write(st.session_state.raw_invoice_copy)  


        # Input field for Excel file name
        excel_filename = st.text_input("Enter Excel File Name (without extension)", "InvoiceReview")

        # Save to Excel button
        if st.button('Save Data to Excel'):
            # Save the filtered dataframe to an Excel file in memory
            excel_buffer = BytesIO()
            st.session_state.raw_invoice_copy.to_excel(excel_buffer, index=False)
            excel_data = excel_buffer.getvalue()

            # Generate a download link for the Excel file
            b64 = base64.b64encode(excel_data).decode('utf-8')
            excel_filename = f"{excel_filename}.xlsx"
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{excel_filename}">Download Excel File</a>'
            st.markdown(href, unsafe_allow_html=True)
