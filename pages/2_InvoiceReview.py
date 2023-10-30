import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
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
    
    # Define a function to calculate the x-week lookback for a given date
    def calculate_x_week_lookback(effective_date, x):
        return effective_date - timedelta(weeks=x)
    
    # Define the Streamlit app
    st.title("Invoice Data Analysis")
    
    # Sidebar instructions
    if st.sidebar.checkbox("Show Instructions"):
        st.write("This application is a tool for tracking and analyzing data for subcontractors invoices.")
        st.write("The labor invoice data will be emailed and can be found in the group invoice email.")
        st.write("The Consolidated WSR file can be found in the following subdirectory 'Restored FMO1', 'Cross Contract Portfolio', 'Y - WSR Analysis', select the latest file.")
        st.write("The Onboarding Tracker file can be found in the following subdirectory 'Restored FMO1', 'Onboarding', select the latest tracker file.")
        st.write("Upload the Excel files.")

        st.write("After uploading the files, the application processes the data.")
        st.write("You will be prompted to add the Weekly lookback period.")
        st.write("- Extracts relevant columns from both files.")
        st.write("- Normalizes employee names by removing middle initials.")
        st.write("- Filters employees who have 'Final Approval' in the Onboarding Tracker.")
        st.write("- Determines which employees are above the 'Tripwire Rate' in the Hourly Cost file.")
        st.write("- Maps 'PLC Desc' to 'Correct LCAT Syntax' using data from the Onboarding Tracker.")
        st.write("Finally, it presents a DataFrame with processed data in a table format under the 'Processed Data' section.")

        st.write("If you want to save the processed data to an Excel file, you can:")
        st.write("- Enter a name for the Excel file in the 'Enter Excel File Name (without extension)' text field.")
        st.write("- Click the 'Save Data to Excel' button.")
        st.write("This will generate a download link for the Excel file. Click on the link to download the processed data.")
        st.write("The file will be saved to the Downloads folder by default.")


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
    if 'x_week_lookback' not in st.session_state:
        st.session_state.x_week_lookback = 4
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

    # Input field for the number of weeks lookback
    x_week_lookback = st.sidebar.number_input("Number of Weeks Lookback", min_value=1, value=st.session_state.x_week_lookback)

    # "Submit" button
    if st.sidebar.button("Submit"):
        if st.session_state.raw_invoice_copy is None:
            st.session_state.raw_invoice_copy = st.session_state.raw_invoice.copy()
            st.session_state.wsr_consolidated_copy = st.session_state.wsr_consolidated.copy()

        # Iterate through each row in the raw_invoice dataset
        for index, raw_invoice_row in st.session_state.raw_invoice_copy.iterrows():
            name = raw_invoice_row['Name']  # Extract the Name from the row
            effective_date = raw_invoice_row['Effective Bill Date']  # Extract the Effective Bill Date from the row
            start_date = effective_date - timedelta(weeks=x_week_lookback)  # Calculate the start date based on the effective date

            # Filter the WSR_consolidated_copy DataFrame for the specified date range
            filtered_wsr = st.session_state.wsr_consolidated_copy[
                (st.session_state.wsr_consolidated_copy['Contractor (Last Name, First Name)2'] == name) &
                (st.session_state.wsr_consolidated_copy['Reporting Week (MM/DD/YYYY)'] >= start_date) &
                (st.session_state.wsr_consolidated_copy['Reporting Week (MM/DD/YYYY)'] <= effective_date)  # End date is the effective date
            ]

            # Calculate the total hours for that person within the specified date range
            total_hours = filtered_wsr['Sum of Time Spent (Hours) '].sum()

            # Calculate Contract Rate: Sum of Cost Calc / Sum of Time Spent (Hours)
            contract_rate = filtered_wsr['Sum of Cost Calc'].sum() / total_hours if total_hours > 0 else 0
            contract_rate = round(contract_rate, 2)
            cost_check = contract_rate * total_hours

            st.session_state.raw_invoice_copy.at[index, 'WSR Hours'] = total_hours
            st.session_state.raw_invoice_copy.at[index, 'Contract Rate'] = contract_rate
            st.session_state.raw_invoice_copy.at[index, 'Cost Check'] = cost_check



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
